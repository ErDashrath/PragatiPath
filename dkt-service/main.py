from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model instance
dkt_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global dkt_service
    try:
        # Import here to handle missing dependencies gracefully
        from dkt_model import DKTService
        dkt_service = DKTService(num_skills=50)
        logger.info("DKT Service initialized successfully")
    except ImportError as e:
        logger.error(f"Could not import DKT model dependencies: {e}")
        logger.info("Running in mock mode")
        dkt_service = MockDKTService()
    except Exception as e:
        logger.error(f"Error initializing DKT service: {e}")
        dkt_service = MockDKTService()
    
    yield
    
    # Shutdown
    logger.info("DKT Service shutting down")

# Create FastAPI app with lifespan
app = FastAPI(
    title="DKT Microservice",
    description="Deep Knowledge Tracing microservice for adaptive learning",
    version="1.0.0",
    lifespan=lifespan
)

class InteractionData(BaseModel):
    skill_id: int = Field(..., description="Skill/Knowledge Component ID", ge=0, le=49)
    is_correct: bool = Field(..., description="Whether the answer was correct")
    response_time: Optional[float] = Field(None, description="Response time in seconds")
    confidence: Optional[int] = Field(None, description="Student confidence level 1-5")

class DKTInferenceRequest(BaseModel):
    interaction_sequence: List[InteractionData] = Field(
        ..., 
        description="Sequence of student interactions",
        min_length=0,
        max_length=1000
    )
    student_id: Optional[str] = Field(None, description="Student identifier for logging")

class DKTInferenceResponse(BaseModel):
    status: str = Field(..., description="Response status")
    skill_predictions: List[float] = Field(..., description="Mastery probability for each skill")
    hidden_state: List[float] = Field(..., description="Neural network hidden state vector")
    confidence: float = Field(..., description="Overall prediction confidence")
    sequence_length: int = Field(..., description="Number of interactions processed")
    error: Optional[str] = Field(None, description="Error message if any")

class ModelInfoResponse(BaseModel):
    num_skills: int = Field(..., description="Number of skills the model handles")
    hidden_dim: int = Field(..., description="Hidden dimension size")
    num_layers: int = Field(..., description="Number of LSTM layers")
    input_dim: int = Field(..., description="Input dimension size")
    model_parameters: int = Field(..., description="Total model parameters")
    trainable_parameters: int = Field(..., description="Trainable parameters")

class MockDKTService:
    """Mock DKT service for when PyTorch is not available"""
    
    def __init__(self):
        self.num_skills = 50
        self.hidden_dim = 128
        
    def infer(self, interaction_sequence: List[Dict]) -> Dict:
        """Mock inference that returns reasonable fake predictions"""
        import random
        import math
        
        # Generate realistic-looking predictions
        skill_predictions = []
        for i in range(self.num_skills):
            # Base probability around 0.5 with some variation
            base_prob = 0.5
            
            # If we have interactions, adjust based on recent performance
            if interaction_sequence:
                recent_correct = sum(1 for interaction in interaction_sequence[-5:] 
                                   if interaction.get("skill_id") == i and interaction.get("is_correct"))
                recent_attempts = sum(1 for interaction in interaction_sequence[-5:] 
                                    if interaction.get("skill_id") == i)
                
                if recent_attempts > 0:
                    recent_accuracy = recent_correct / recent_attempts
                    base_prob = 0.3 * base_prob + 0.7 * recent_accuracy
            
            # Add some randomness
            prediction = max(0.1, min(0.9, base_prob + random.gauss(0, 0.1)))
            skill_predictions.append(prediction)
        
        # Generate mock hidden state
        hidden_state = [random.gauss(0, 0.5) for _ in range(self.hidden_dim)]
        
        # Calculate confidence based on sequence length and variance
        if interaction_sequence:
            confidence = min(0.9, 0.5 + len(interaction_sequence) * 0.05)
        else:
            confidence = 0.5
        
        return {
            "status": "success",
            "skill_predictions": skill_predictions,
            "hidden_state": hidden_state,
            "confidence": confidence,
            "sequence_length": len(interaction_sequence)
        }
    
    def get_model_info(self) -> Dict:
        """Mock model info"""
        return {
            "num_skills": self.num_skills,
            "hidden_dim": self.hidden_dim,
            "num_layers": 2,
            "input_dim": self.num_skills * 2,
            "model_parameters": 50000,  # Mock number
            "trainable_parameters": 50000
        }

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "DKT Microservice is running",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    global dkt_service
    return {
        "status": "healthy",
        "service": "dkt-microservice",
        "model_loaded": dkt_service is not None,
        "mock_mode": isinstance(dkt_service, MockDKTService)
    }

@app.post("/dkt/infer", response_model=DKTInferenceResponse)
async def dkt_inference(request: DKTInferenceRequest):
    """
    Perform DKT inference on interaction sequence
    """
    global dkt_service
    
    if dkt_service is None:
        raise HTTPException(status_code=503, detail="DKT service not available")
    
    try:
        # Convert Pydantic models to dict format expected by DKT model
        interaction_sequence = []
        for interaction in request.interaction_sequence:
            interaction_dict = {
                "skill_id": interaction.skill_id,
                "is_correct": interaction.is_correct
            }
            if interaction.response_time is not None:
                interaction_dict["response_time"] = interaction.response_time
            if interaction.confidence is not None:
                interaction_dict["confidence"] = interaction.confidence
            
            interaction_sequence.append(interaction_dict)
        
        # Perform inference
        result = dkt_service.infer(interaction_sequence)
        
        # Log for monitoring
        if request.student_id:
            logger.info(f"DKT inference for student {request.student_id}: "
                       f"{len(interaction_sequence)} interactions, "
                       f"confidence: {result.get('confidence', 0):.3f}")
        
        return DKTInferenceResponse(**result)
        
    except Exception as e:
        logger.error(f"Error during DKT inference: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")

@app.get("/dkt/model-info", response_model=ModelInfoResponse)
async def get_model_info():
    """Get information about the DKT model"""
    global dkt_service
    
    if dkt_service is None:
        raise HTTPException(status_code=503, detail="DKT service not available")
    
    try:
        model_info = dkt_service.get_model_info()
        return ModelInfoResponse(**model_info)
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Model info error: {str(e)}")

@app.post("/dkt/batch-infer")
async def batch_inference(requests: List[DKTInferenceRequest]):
    """
    Perform batch DKT inference for multiple students
    """
    global dkt_service
    
    if dkt_service is None:
        raise HTTPException(status_code=503, detail="DKT service not available")
    
    if len(requests) > 100:
        raise HTTPException(status_code=400, detail="Too many requests in batch (max 100)")
    
    results = []
    for i, request in enumerate(requests):
        try:
            # Convert to dict format
            interaction_sequence = [
                {
                    "skill_id": interaction.skill_id,
                    "is_correct": interaction.is_correct,
                    **({"response_time": interaction.response_time} if interaction.response_time else {}),
                    **({"confidence": interaction.confidence} if interaction.confidence else {})
                }
                for interaction in request.interaction_sequence
            ]
            
            # Perform inference
            result = dkt_service.infer(interaction_sequence)
            result["request_index"] = i
            results.append(result)
            
        except Exception as e:
            logger.error(f"Error in batch inference for request {i}: {str(e)}")
            results.append({
                "status": "error",
                "error": str(e),
                "request_index": i,
                "skill_predictions": [0.5] * 50,
                "hidden_state": [0.0] * 128,
                "confidence": 0.0,
                "sequence_length": 0
            })
    
    return {
        "batch_size": len(requests),
        "results": results
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)