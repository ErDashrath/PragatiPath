import torch
import torch.nn as nn
import numpy as np
from typing import List, Dict, Tuple
import json

class DKTModel(nn.Module):
    """
    Deep Knowledge Tracing LSTM Model
    Input: sequence of (skill_id, correct) pairs
    Output: next skill mastery predictions + hidden state
    """
    
    def __init__(self, num_skills: int, hidden_dim: int = 128, num_layers: int = 2):
        super(DKTModel, self).__init__()
        
        self.num_skills = num_skills
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        # Input dimension: skill_id (one-hot) + correct (0/1) = num_skills * 2
        self.input_dim = num_skills * 2
        
        # LSTM layers
        self.lstm = nn.LSTM(
            input_size=self.input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2 if num_layers > 1 else 0
        )
        
        # Output layer: predict mastery probability for each skill
        self.output_layer = nn.Linear(hidden_dim, num_skills)
        self.sigmoid = nn.Sigmoid()
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        """Initialize model weights"""
        for name, param in self.named_parameters():
            if 'weight' in name:
                nn.init.xavier_uniform_(param)
            elif 'bias' in name:
                nn.init.zeros_(param)
    
    def forward(self, x: torch.Tensor, hidden: Tuple[torch.Tensor, torch.Tensor] = None):
        """
        Forward pass
        Args:
            x: Input tensor of shape (batch_size, seq_len, input_dim)
            hidden: Optional initial hidden state
        Returns:
            output: Skill mastery predictions (batch_size, seq_len, num_skills)
            hidden: Final hidden state tuple (h_n, c_n)
        """
        # LSTM forward pass
        lstm_out, hidden = self.lstm(x, hidden)
        
        # Apply output layer to each timestep
        output = self.output_layer(lstm_out)
        output = self.sigmoid(output)
        
        return output, hidden
    
    def encode_interaction(self, skill_id: int, is_correct: bool) -> np.ndarray:
        """
        Encode a single interaction as input vector
        Args:
            skill_id: Skill identifier (0 to num_skills-1)
            is_correct: Whether the answer was correct
        Returns:
            Encoded vector of size (num_skills * 2)
        """
        vector = np.zeros(self.num_skills * 2)
        
        # Set skill bit
        if 0 <= skill_id < self.num_skills:
            base_idx = skill_id * 2
            vector[base_idx] = 1.0  # Skill attempted
            if is_correct:
                vector[base_idx + 1] = 1.0  # Skill mastered
        
        return vector
    
    def predict_next_skills(self, interaction_sequence: List[Dict]) -> Dict:
        """
        Predict mastery probabilities for all skills given interaction sequence
        Args:
            interaction_sequence: List of {"skill_id": int, "is_correct": bool}
        Returns:
            Dictionary with predictions and hidden state
        """
        self.eval()
        
        if not interaction_sequence:
            # No interactions, return uniform predictions
            predictions = np.full(self.num_skills, 0.5)
            hidden_state = np.zeros(self.hidden_dim).tolist()
            return {
                "skill_predictions": predictions.tolist(),
                "hidden_state": hidden_state,
                "confidence": 0.5
            }
        
        # Encode interaction sequence
        sequence_vectors = []
        for interaction in interaction_sequence:
            skill_id = interaction.get("skill_id", 0)
            is_correct = interaction.get("is_correct", False)
            vector = self.encode_interaction(skill_id, is_correct)
            sequence_vectors.append(vector)
        
        # Convert to tensor
        x = torch.FloatTensor(sequence_vectors).unsqueeze(0)  # Add batch dimension
        
        with torch.no_grad():
            # Forward pass
            output, (h_n, c_n) = self.forward(x)
            
            # Get last timestep predictions
            last_predictions = output[0, -1, :].numpy()  # Shape: (num_skills,)
            
            # Get hidden state (last layer, last timestep)
            hidden_state = h_n[-1, 0, :].numpy()  # Shape: (hidden_dim,)
            
            # Calculate confidence as average prediction entropy
            confidence = self._calculate_confidence(last_predictions)
        
        return {
            "skill_predictions": last_predictions.tolist(),
            "hidden_state": hidden_state.tolist(),
            "confidence": float(confidence),
            "sequence_length": len(interaction_sequence)
        }
    
    def _calculate_confidence(self, predictions: np.ndarray) -> float:
        """Calculate confidence based on prediction entropy"""
        # Avoid log(0) by adding small epsilon
        epsilon = 1e-8
        predictions = np.clip(predictions, epsilon, 1 - epsilon)
        
        # Calculate entropy for each skill
        entropy = -(predictions * np.log(predictions) + 
                   (1 - predictions) * np.log(1 - predictions))
        
        # Average entropy (lower is more confident)
        avg_entropy = np.mean(entropy)
        
        # Convert to confidence (higher is more confident)
        max_entropy = -np.log(0.5)  # Maximum entropy at p=0.5
        confidence = 1.0 - (avg_entropy / max_entropy)
        
        return confidence

class DKTService:
    """Service class for DKT model operations"""
    
    def __init__(self, num_skills: int = 50, model_path: str = None):
        self.num_skills = num_skills
        self.model = DKTModel(num_skills)
        self.model_path = model_path
        
        if model_path:
            self._load_model(model_path)
        else:
            # Use pretrained weights or train on dummy data
            self._initialize_pretrained_weights()
    
    def _load_model(self, model_path: str):
        """Load model from file"""
        try:
            self.model.load_state_dict(torch.load(model_path, map_location='cpu'))
            print(f"Loaded DKT model from {model_path}")
        except Exception as e:
            print(f"Could not load model from {model_path}: {e}")
            print("Using initialized model instead")
            self._initialize_pretrained_weights()
    
    def _initialize_pretrained_weights(self):
        """Initialize with reasonable pretrained weights"""
        # This would normally be trained weights, but for demo we'll use good initialization
        print("Initializing DKT model with default weights")
        
        # Set model to eval mode
        self.model.eval()
    
    def infer(self, interaction_sequence: List[Dict]) -> Dict:
        """
        Main inference method
        Args:
            interaction_sequence: List of interactions
        Returns:
            DKT inference results
        """
        try:
            result = self.model.predict_next_skills(interaction_sequence)
            result["status"] = "success"
            return result
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "skill_predictions": [0.5] * self.num_skills,
                "hidden_state": [0.0] * self.model.hidden_dim,
                "confidence": 0.0
            }
    
    def get_model_info(self) -> Dict:
        """Get model information"""
        return {
            "num_skills": self.num_skills,
            "hidden_dim": self.model.hidden_dim,
            "num_layers": self.model.num_layers,
            "input_dim": self.model.input_dim,
            "model_parameters": sum(p.numel() for p in self.model.parameters()),
            "trainable_parameters": sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        }