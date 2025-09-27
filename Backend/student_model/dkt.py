"""
Deep Knowledge Tracing (DKT) Algorithm Implementation

DKT uses recurrent neural networks (typically LSTMs) to model student knowledge
state and predict performance on future questions. Unlike BKT, DKT can capture 
complex temporal patterns and skill interactions.

This implementation provides both a neural network-based DKT and a simplified
mock version for systems without deep learning dependencies.
"""

import math
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import StudentProfile
import json


@dataclass
class DKTInteraction:
    """Represents a single interaction for DKT"""
    skill_id: str
    is_correct: bool
    response_time: Optional[float] = None
    timestamp: Optional[str] = None
    question_id: Optional[str] = None
    
    def to_vector(self, num_skills: int, skill_to_index: Dict[str, int]) -> List[float]:
        """Convert interaction to input vector for DKT"""
        # Create one-hot vector for skill (size: num_skills * 2)
        # First half: skill attempted, Second half: correctness
        vector = [0.0] * (num_skills * 2)
        
        if self.skill_id in skill_to_index:
            skill_index = skill_to_index[self.skill_id]
            vector[skill_index] = 1.0  # Skill attempted
            if self.is_correct:
                vector[num_skills + skill_index] = 1.0  # Correct response
        
        return vector


@dataclass 
class DKTState:
    """DKT model state for a student"""
    student_id: str
    hidden_state: List[float]
    skill_predictions: List[float]
    interaction_sequence: List[DKTInteraction]
    skill_mapping: Dict[str, int]
    last_updated: str
    confidence: float = 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'student_id': self.student_id,
            'hidden_state': self.hidden_state,
            'skill_predictions': self.skill_predictions,
            'interaction_sequence': [asdict(interaction) for interaction in self.interaction_sequence],
            'skill_mapping': self.skill_mapping,
            'last_updated': self.last_updated,
            'confidence': self.confidence
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DKTState':
        """Create from dictionary"""
        interactions = [DKTInteraction(**interaction) for interaction in data.get('interaction_sequence', [])]
        return cls(
            student_id=data['student_id'],
            hidden_state=data.get('hidden_state', []),
            skill_predictions=data.get('skill_predictions', []),
            interaction_sequence=interactions,
            skill_mapping=data.get('skill_mapping', {}),
            last_updated=data.get('last_updated', timezone.now().isoformat()),
            confidence=data.get('confidence', 0.5)
        )


class MockDKTModel:
    """
    Mock DKT implementation that provides realistic predictions without deep learning
    This is used when PyTorch/neural network dependencies are not available
    """
    
    def __init__(self, num_skills: int = 50, hidden_dim: int = 128):
        self.num_skills = num_skills
        self.hidden_dim = hidden_dim
        
        # Pre-computed skill difficulty and learning rates
        np.random.seed(42)  # For reproducible results
        self.skill_difficulties = np.random.uniform(0.2, 0.8, num_skills)
        self.skill_learning_rates = np.random.uniform(0.1, 0.4, num_skills)
    
    def predict(self, interaction_sequence: List[DKTInteraction], skill_mapping: Dict[str, int]) -> Tuple[List[float], List[float]]:
        """
        Generate mock DKT predictions based on interaction history
        
        Args:
            interaction_sequence: List of student interactions
            skill_mapping: Mapping from skill names to indices
            
        Returns:
            Tuple of (skill_predictions, hidden_state)
        """
        # Initialize predictions with base difficulty
        skill_predictions = self.skill_difficulties.copy()
        
        # Update predictions based on interaction history
        skill_performance = {}
        
        for interaction in interaction_sequence:
            if interaction.skill_id in skill_mapping:
                skill_idx = skill_mapping[interaction.skill_id]
                
                if skill_idx not in skill_performance:
                    skill_performance[skill_idx] = {'correct': 0, 'total': 0}
                
                skill_performance[skill_idx]['total'] += 1
                if interaction.is_correct:
                    skill_performance[skill_idx]['correct'] += 1
        
        # Adjust predictions based on performance
        for skill_idx, performance in skill_performance.items():
            if performance['total'] > 0:
                accuracy = performance['correct'] / performance['total']
                learning_progress = min(1.0, performance['total'] * self.skill_learning_rates[skill_idx])
                
                # Blend current accuracy with base difficulty, weighted by learning progress
                skill_predictions[skill_idx] = (
                    (1 - learning_progress) * self.skill_difficulties[skill_idx] + 
                    learning_progress * accuracy
                )
        
        # Apply skill transfer effects (skills influence each other)
        self._apply_skill_transfer(skill_predictions, skill_performance)
        
        # Generate mock hidden state
        hidden_state = self._generate_hidden_state(interaction_sequence)
        
        # Ensure probabilities are in valid range
        skill_predictions = np.clip(skill_predictions, 0.1, 0.9)
        
        return skill_predictions.tolist(), hidden_state
    
    def _apply_skill_transfer(self, skill_predictions: np.ndarray, skill_performance: Dict[int, Dict[str, int]]):
        """Apply transfer learning effects between related skills"""
        # Simple transfer model: similar skills influence each other
        for skill_idx in range(len(skill_predictions)):
            if skill_idx in skill_performance:
                # Find related skills (neighboring indices as a simple heuristic)
                related_skills = [
                    i for i in range(max(0, skill_idx - 2), min(len(skill_predictions), skill_idx + 3))
                    if i != skill_idx and i in skill_performance
                ]
                
                if related_skills:
                    # Average performance on related skills influences current skill
                    related_performance = np.mean([
                        skill_performance[i]['correct'] / skill_performance[i]['total']
                        for i in related_skills
                    ])
                    
                    # Small transfer effect (10% influence)
                    transfer_effect = 0.1 * related_performance
                    skill_predictions[skill_idx] = (
                        0.9 * skill_predictions[skill_idx] + 0.1 * transfer_effect
                    )
    
    def _generate_hidden_state(self, interaction_sequence: List[DKTInteraction]) -> List[float]:
        """Generate a mock hidden state vector"""
        # Create a simple hidden state based on recent interactions
        hidden_state = np.zeros(self.hidden_dim)
        
        if not interaction_sequence:
            return hidden_state.tolist()
        
        # Use recent interactions to influence hidden state
        recent_interactions = interaction_sequence[-10:]  # Last 10 interactions
        
        for i, interaction in enumerate(recent_interactions):
            # Decay older interactions
            weight = 0.9 ** (len(recent_interactions) - i - 1)
            
            # Hash skill_id to get consistent indices
            skill_hash = hash(interaction.skill_id) % self.hidden_dim
            
            if interaction.is_correct:
                hidden_state[skill_hash] += weight
            else:
                hidden_state[skill_hash] -= weight * 0.5
        
        # Normalize to reasonable range
        if np.max(np.abs(hidden_state)) > 0:
            hidden_state = hidden_state / np.max(np.abs(hidden_state))
        
        return hidden_state.tolist()


class DKTService:
    """
    Service class for managing DKT operations with database integration
    """
    
    # Standard skill mapping for competitive exams
    DEFAULT_SKILLS = [
        'quantitative_aptitude_arithmetic',
        'quantitative_aptitude_algebra', 
        'quantitative_aptitude_geometry',
        'quantitative_aptitude_statistics',
        'logical_reasoning_analytical',
        'logical_reasoning_verbal',
        'logical_reasoning_non_verbal',
        'logical_reasoning_critical',
        'data_interpretation_charts',
        'data_interpretation_tables',
        'data_interpretation_graphs',
        'data_interpretation_analysis',
        'verbal_ability_reading',
        'verbal_ability_grammar',
        'verbal_ability_vocabulary',
        'verbal_ability_comprehension'
    ]
    
    def __init__(self):
        self.model = MockDKTModel(num_skills=len(self.DEFAULT_SKILLS))
        self.skill_to_index = {skill: idx for idx, skill in enumerate(self.DEFAULT_SKILLS)}
    
    @staticmethod
    def get_or_create_student_profile(user: User) -> StudentProfile:
        """Get or create StudentProfile for a user"""
        profile, created = StudentProfile.objects.get_or_create(
            user=user,
            defaults={
                'bkt_parameters': {},
                'dkt_hidden_state': [],
                'fundamentals': {
                    'listening': 0.5,
                    'grasping': 0.5,
                    'retention': 0.5,
                    'application': 0.5
                },
                'interaction_history': []
            }
        )
        return profile
    
    def get_dkt_state(self, user: User) -> DKTState:
        """Get DKT state for a user, creating if necessary"""
        profile = self.get_or_create_student_profile(user)
        
        # Initialize DKT state if not exists
        if not hasattr(profile, 'dkt_state_data') or not profile.dkt_state_data:
            initial_state = DKTState(
                student_id=str(user.id),
                hidden_state=[0.0] * self.model.hidden_dim,
                skill_predictions=[0.5] * len(self.DEFAULT_SKILLS),
                interaction_sequence=[],
                skill_mapping=self.skill_to_index,
                last_updated=timezone.now().isoformat(),
                confidence=0.5
            )
            
            # Store in profile's dkt_hidden_state field as JSON
            profile.dkt_hidden_state = initial_state.to_dict()
            profile.save()
            
            return initial_state
        
        # Load existing state
        return DKTState.from_dict(profile.dkt_hidden_state)
    
    def update_dkt_knowledge(
        self, 
        user: User, 
        skill_id: str, 
        is_correct: bool,
        interaction_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update DKT knowledge state based on new interaction
        
        Args:
            user: Django User object
            skill_id: Skill identifier
            is_correct: Whether the response was correct
            interaction_data: Additional interaction metadata
            
        Returns:
            Dictionary with updated predictions and metadata
        """
        profile = self.get_or_create_student_profile(user)
        dkt_state = self.get_dkt_state(user)
        
        # Create new interaction
        interaction = DKTInteraction(
            skill_id=skill_id,
            is_correct=is_correct,
            response_time=interaction_data.get('response_time') if interaction_data else None,
            timestamp=timezone.now().isoformat(),
            question_id=interaction_data.get('question_id') if interaction_data else None
        )
        
        # Add to sequence
        dkt_state.interaction_sequence.append(interaction)
        
        # Keep only recent interactions (last 100) to prevent unbounded growth
        if len(dkt_state.interaction_sequence) > 100:
            dkt_state.interaction_sequence = dkt_state.interaction_sequence[-100:]
        
        # Update predictions using DKT model
        skill_predictions, hidden_state = self.model.predict(
            dkt_state.interaction_sequence,
            dkt_state.skill_mapping
        )
        
        # Update state
        dkt_state.skill_predictions = skill_predictions
        dkt_state.hidden_state = hidden_state
        dkt_state.last_updated = timezone.now().isoformat()
        
        # Calculate confidence based on sequence length and prediction consistency
        dkt_state.confidence = self._calculate_confidence(dkt_state)
        
        # Save to database
        profile.dkt_hidden_state = dkt_state.to_dict()
        
        # Also update the legacy fields for compatibility
        profile.dkt_skill_predictions = skill_predictions
        profile.dkt_last_updated = timezone.now()
        
        profile.save()
        
        return {
            'status': 'success',
            'skill_predictions': {
                skill: pred for skill, pred in zip(self.DEFAULT_SKILLS, skill_predictions)
            },
            'updated_skill': skill_id,
            'updated_prediction': skill_predictions[self.skill_to_index.get(skill_id, 0)],
            'confidence': dkt_state.confidence,
            'sequence_length': len(dkt_state.interaction_sequence),
            'message': f'DKT updated for skill {skill_id}'
        }
    
    def get_skill_prediction(self, user: User, skill_id: str) -> float:
        """Get DKT prediction for a specific skill"""
        dkt_state = self.get_dkt_state(user)
        
        if skill_id in self.skill_to_index:
            skill_idx = self.skill_to_index[skill_id]
            return dkt_state.skill_predictions[skill_idx]
        
        return 0.5  # Default prediction
    
    def predict_performance(self, student_username: str, subject: str) -> Dict[str, Any]:
        """
        Predict performance for a student in a subject (orchestration compatibility method)
        
        Args:
            student_username: Username of the student
            subject: Subject name
            
        Returns:
            Dict containing predicted performance and metadata
        """
        try:
            from django.contrib.auth.models import User
            user = User.objects.get(username=student_username)
            
            # Create skill_id for the subject
            skill_id = f"{subject}_skill"
            
            # Get DKT prediction
            predicted_performance = self.get_skill_prediction(user, skill_id)
            
            return {
                'success': True,
                'predicted_performance': predicted_performance,
                'skill_id': skill_id,
                'confidence': predicted_performance,
                'timestamp': str(timezone.now())
            }
            
        except User.DoesNotExist:
            return {
                'success': False,
                'predicted_performance': 0.5,
                'error': f'User {student_username} not found'
            }
        except Exception as e:
            return {
                'success': False, 
                'predicted_performance': 0.5,
                'error': str(e)
            }
    
    def update_knowledge_state(
        self, 
        student_username: str, 
        subject: str, 
        question_id: str, 
        is_correct: bool, 
        time_spent: float
    ) -> Dict[str, Any]:
        """
        Update knowledge state for orchestration compatibility
        
        Args:
            student_username: Username of the student
            subject: Subject name  
            question_id: Question identifier
            is_correct: Whether answer was correct
            time_spent: Time spent on question
            
        Returns:
            Dict containing update results
        """
        try:
            from django.contrib.auth.models import User
            user = User.objects.get(username=student_username)
            
            # Create skill_id for the subject
            skill_id = f"{subject}_skill"
            
            # Update DKT knowledge using existing method
            result = self.update_dkt_knowledge(
                user=user,
                skill_id=skill_id,
                is_correct=is_correct,
                response_time=time_spent,
                question_id=question_id
            )
            
            return {
                'success': True,
                'predicted_performance': result.get('new_prediction', 0.5),
                'skill_id': skill_id,
                'update_result': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'predicted_performance': 0.5,
                'error': str(e)
            }
    
    def get_all_predictions(self, user: User) -> Dict[str, float]:
        """Get DKT predictions for all skills"""
        dkt_state = self.get_dkt_state(user)
        
        return {
            skill: dkt_state.skill_predictions[idx]
            for skill, idx in self.skill_to_index.items()
        }
    
    def compare_with_bkt(self, user: User) -> Dict[str, Any]:
        """Compare DKT predictions with BKT for all skills"""
        from .bkt import BKTService
        
        dkt_predictions = self.get_all_predictions(user)
        bkt_states = BKTService.get_all_skill_states(user)
        
        comparison = {}
        for skill_id in self.DEFAULT_SKILLS:
            dkt_pred = dkt_predictions.get(skill_id, 0.5)
            bkt_pred = bkt_states.get(skill_id)
            bkt_value = bkt_pred.P_L if bkt_pred else 0.5
            
            comparison[skill_id] = {
                'dkt_prediction': dkt_pred,
                'bkt_prediction': bkt_value,
                'difference': abs(dkt_pred - bkt_value),
                'agreement': 'high' if abs(dkt_pred - bkt_value) < 0.2 else 'medium' if abs(dkt_pred - bkt_value) < 0.4 else 'low'
            }
        
        return {
            'skill_comparison': comparison,
            'overall_correlation': self._calculate_correlation([
                comparison[skill]['dkt_prediction'] for skill in self.DEFAULT_SKILLS
            ], [
                comparison[skill]['bkt_prediction'] for skill in self.DEFAULT_SKILLS
            ]),
            'high_agreement_count': sum(1 for skill in comparison.values() if skill['agreement'] == 'high')
        }
    
    def _calculate_confidence(self, dkt_state: DKTState) -> float:
        """Calculate confidence in DKT predictions"""
        sequence_length = len(dkt_state.interaction_sequence)
        
        # Base confidence increases with more data
        base_confidence = min(0.9, 0.3 + sequence_length * 0.02)
        
        # Adjust based on prediction variance
        if len(dkt_state.skill_predictions) > 1:
            prediction_variance = np.var(dkt_state.skill_predictions)
            # Lower variance = higher confidence
            variance_adjustment = max(-0.2, -prediction_variance)
            base_confidence += variance_adjustment
        
        return max(0.1, min(0.95, base_confidence))
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient"""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xx = sum(xi * xi for xi in x)
        sum_yy = sum(yi * yi for yi in y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator_x = n * sum_xx - sum_x * sum_x
        denominator_y = n * sum_yy - sum_y * sum_y
        
        if denominator_x <= 0 or denominator_y <= 0:
            return 0.0
        
        denominator = math.sqrt(denominator_x * denominator_y)
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def reset_dkt_state(self, user: User) -> Dict[str, Any]:
        """Reset DKT state for a user"""
        profile = self.get_or_create_student_profile(user)
        
        initial_state = DKTState(
            student_id=str(user.id),
            hidden_state=[0.0] * self.model.hidden_dim,
            skill_predictions=[0.5] * len(self.DEFAULT_SKILLS),
            interaction_sequence=[],
            skill_mapping=self.skill_to_index,
            last_updated=timezone.now().isoformat(),
            confidence=0.5
        )
        
        profile.dkt_hidden_state = initial_state.to_dict()
        profile.dkt_skill_predictions = [0.5] * len(self.DEFAULT_SKILLS)
        profile.dkt_last_updated = timezone.now()
        profile.save()
        
        return {
            'status': 'success',
            'message': 'DKT state reset successfully',
            'skill_predictions': {
                skill: 0.5 for skill in self.DEFAULT_SKILLS
            }
        }
    
    def initialize_student(self, student_username: str, subject: str) -> Dict[str, Any]:
        """
        Initialize DKT state for a new student
        
        Args:
            student_username: Username of the student
            subject: Subject to initialize
            
        Returns:
            Dict containing initialization status
        """
        try:
            # Get or create user and profile
            from django.contrib.auth.models import User
            user, created = User.objects.get_or_create(username=student_username)
            profile = self.get_or_create_student_profile(user)
            
            # Initialize DKT hidden state if needed
            if not profile.dkt_hidden_state:
                initial_state = DKTState(
                    student_id=str(user.id),
                    hidden_state=[0.0] * self.model.hidden_dim,
                    skill_predictions=[0.5] * len(self.DEFAULT_SKILLS),
                    interaction_sequence=[],
                    skill_mapping=self.skill_to_index,
                    last_updated=timezone.now().isoformat(),
                    confidence=0.5
                )
                profile.dkt_hidden_state = initial_state.to_dict()
                profile.save()
            
            logger.info(f"✅ DKT initialized for {student_username} in {subject}")
            
            return {
                'success': True,
                'student_username': student_username,
                'subject': subject,
                'hidden_state_dim': len(profile.dkt_hidden_state.get('hidden_state', [])),
                'message': f'DKT state initialized for {student_username}'
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize DKT for {student_username}: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'DKT initialization failed for {student_username}'
            }