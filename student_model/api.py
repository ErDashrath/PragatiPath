from ninja import Router
from ninja import Schema
from ninja.errors import HttpError
from typing import List, Optional, Dict, Any
from datetime import datetime
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.utils import timezone
import aiohttp
import asyncio
import json
import logging
import requests

from .bkt import BKTService, BKTParameters

logger = logging.getLogger(__name__)

router = Router()

# ============================================================================
# BKT Schemas for Django Ninja API
# ============================================================================

class BKTParametersSchema(Schema):
    """Schema for BKT parameters response"""
    P_L0: float  # Initial probability of knowing the skill
    P_T: float   # Learning (transition) rate  
    P_G: float   # Guess rate
    P_S: float   # Slip rate
    P_L: float   # Current probability of knowing the skill


class BKTUpdateRequestSchema(Schema):
    """Schema for BKT update request"""
    skill_id: str
    is_correct: bool
    interaction_data: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "skill_id": "algebra_linear_equations",
                "is_correct": True,
                "interaction_data": {
                    "question_id": "q123",
                    "response_time": 15.5,
                    "hints_used": 1,
                    "timestamp": "2025-09-25T00:30:00Z"
                }
            }
        }


class BKTStateResponseSchema(Schema):
    """Schema for BKT state response"""
    student_id: int
    skill_id: str
    bkt_parameters: BKTParametersSchema
    is_mastered: bool
    mastery_threshold: float = 0.95
    updated_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "student_id": 1,
                "skill_id": "algebra_linear_equations",
                "bkt_parameters": {
                    "P_L0": 0.1,
                    "P_T": 0.3,
                    "P_G": 0.2,
                    "P_S": 0.1,
                    "P_L": 0.85
                },
                "is_mastered": False,
                "mastery_threshold": 0.95,
                "updated_at": "2025-09-25T00:30:00Z"
            }
        }


class AllBKTStatesResponseSchema(Schema):
    """Schema for all BKT states response"""
    student_id: int
    total_skills: int
    mastered_skills: int
    skill_states: Dict[str, BKTParametersSchema]
    mastered_skills_list: List[str]
    generated_at: datetime


class MasteredSkillsResponseSchema(Schema):
    """Schema for mastered skills response"""
    student_id: int
    mastered_skills: Dict[str, float]  # skill_id -> mastery_probability
    threshold: float
    total_mastered: int
    generated_at: datetime


# ============================================================================
# DKT Schemas for Django Ninja API
# ============================================================================

class DKTUpdateSchema(Schema):
    """Schema for DKT update request"""
    student_id: str
    skill_id: int
    is_correct: bool
    response_time: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "student-123",
                "skill_id": 5,
                "is_correct": True,
                "response_time": 15.5
            }
        }


class DKTResponseSchema(Schema):
    """Schema for DKT response"""
    status: str
    skill_id: int
    mastery_probability: float
    confidence: float
    hidden_state_length: Optional[int] = None
    updated_skills: Optional[int] = None
    message: Optional[str] = None


class DKTPredictionsSchema(Schema):
    """Schema for DKT predictions response"""
    status: str
    student_id: str
    skill_predictions: List[float]
    confidence: float
    sequence_length: int
    dkt_service_available: bool
    message: Optional[str] = None


# ============================================================================
# DKT Client for Microservice Communication
# ============================================================================

class DKTClient:
    """Client for communicating with DKT microservice"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
    
    async def infer_dkt(self, interaction_sequence: list, student_id: Optional[str] = None) -> Optional[Dict]:
        """Call DKT microservice for inference"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "interaction_sequence": interaction_sequence,
                    "student_id": student_id
                }
                
                async with session.post(f"{self.base_url}/dkt/infer", json=payload) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"DKT service returned status {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error calling DKT service: {e}")
            return None
    
    def infer_dkt_sync(self, interaction_sequence: list, student_id: Optional[str] = None) -> Optional[Dict]:
        """Synchronous wrapper for DKT inference"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.infer_dkt(interaction_sequence, student_id))
    
    def check_health_sync(self) -> Dict:
        """Check DKT service health synchronously"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return {
                'dkt_service_available': response.status_code == 200,
                'dkt_response': response.json() if response.status_code == 200 else None,
                'status': 'healthy' if response.status_code == 200 else 'unhealthy'
            }
        except Exception as e:
            return {
                'dkt_service_available': False,
                'error': str(e),
                'status': 'unhealthy'
            }

# Initialize DKT client
dkt_client = DKTClient()


# ============================================================================
# BKT API Endpoints
# ============================================================================

@router.post("/student/{student_id}/bkt/update", 
             response=BKTStateResponseSchema,
             tags=["BKT Algorithm"])
def update_student_bkt(request, student_id: int, payload: BKTUpdateRequestSchema):
    """
    Update BKT parameters for a student based on their interaction with a skill
    
    This endpoint implements Bayesian Knowledge Tracing to update the probability
    that a student has mastered a specific skill based on their performance.
    
    **BKT Parameters:**
    - P(L0): Initial probability of knowing the skill
    - P(T): Learning rate - probability of transitioning from unknown to known
    - P(G): Guess rate - probability of getting correct answer without knowing
    - P(S): Slip rate - probability of getting wrong answer despite knowing
    - P(L): Current probability of knowing the skill
    """
    try:
        user = get_object_or_404(User, id=student_id)
        
        # Update BKT parameters
        updated_params = BKTService.update_skill_bkt(
            user=user,
            skill_id=payload.skill_id,
            is_correct=payload.is_correct,
            interaction_data=payload.interaction_data
        )
        
        # Check if skill is mastered
        is_mastered = updated_params.P_L >= 0.95
        
        return {
            "student_id": student_id,
            "skill_id": payload.skill_id,
            "bkt_parameters": {
                "P_L0": updated_params.P_L0,
                "P_T": updated_params.P_T,
                "P_G": updated_params.P_G,
                "P_S": updated_params.P_S,
                "P_L": updated_params.P_L
            },
            "is_mastered": is_mastered,
            "mastery_threshold": 0.95,
            "updated_at": datetime.now()
        }
        
    except User.DoesNotExist:
        raise Http404(f"Student with id {student_id} not found")


@router.get("/student/{student_id}/bkt/state/{skill_id}",
            response=BKTStateResponseSchema,
            tags=["BKT Algorithm"])
def get_student_bkt_state(request, student_id: int, skill_id: str):
    """
    Get current BKT state for a specific skill for a student
    
    Returns the current Bayesian Knowledge Tracing parameters and mastery status
    for the specified skill.
    """
    try:
        user = get_object_or_404(User, id=student_id)
        
        # Get BKT parameters for the skill
        bkt_params = BKTService.get_skill_bkt_params(user, skill_id)
        
        # Check if skill is mastered
        is_mastered = bkt_params.P_L >= 0.95
        
        return {
            "student_id": student_id,
            "skill_id": skill_id,
            "bkt_parameters": {
                "P_L0": bkt_params.P_L0,
                "P_T": bkt_params.P_T,
                "P_G": bkt_params.P_G,
                "P_S": bkt_params.P_S,
                "P_L": bkt_params.P_L
            },
            "is_mastered": is_mastered,
            "mastery_threshold": 0.95,
            "updated_at": datetime.now()
        }
        
    except User.DoesNotExist:
        raise Http404(f"Student with id {student_id} not found")


@router.get("/student/{student_id}/bkt/states/all",
            response=AllBKTStatesResponseSchema,
            tags=["BKT Algorithm"])
def get_all_student_bkt_states(request, student_id: int):
    """
    Get BKT states for all skills for a student
    
    Returns comprehensive BKT information including all tracked skills,
    their current parameters, and mastery status.
    """
    try:
        user = get_object_or_404(User, id=student_id)
        
        # Get all skill states
        skill_states = BKTService.get_all_skill_states(user)
        
        # Convert to response format
        skill_states_response = {}
        mastered_skills_list = []
        
        for skill_id, params in skill_states.items():
            skill_states_response[skill_id] = {
                "P_L0": params.P_L0,
                "P_T": params.P_T,
                "P_G": params.P_G,
                "P_S": params.P_S,
                "P_L": params.P_L
            }
            
            if params.P_L >= 0.95:
                mastered_skills_list.append(skill_id)
        
        return {
            "student_id": student_id,
            "total_skills": len(skill_states),
            "mastered_skills": len(mastered_skills_list),
            "skill_states": skill_states_response,
            "mastered_skills_list": mastered_skills_list,
            "generated_at": datetime.now()
        }
        
    except User.DoesNotExist:
        raise Http404(f"Student with id {student_id} not found")


@router.get("/student/{student_id}/bkt/mastered",
            response=MasteredSkillsResponseSchema,
            tags=["BKT Algorithm"])
def get_mastered_skills(request, student_id: int, threshold: float = 0.95):
    """
    Get all mastered skills for a student
    
    Returns skills that have reached the mastery threshold (default 95% probability).
    Useful for determining what content the student has completed.
    """
    try:
        user = get_object_or_404(User, id=student_id)
        
        # Get mastered skills
        mastered_skills = BKTService.get_mastered_skills(user, threshold)
        
        return {
            "student_id": student_id,
            "mastered_skills": mastered_skills,
            "threshold": threshold,
            "total_mastered": len(mastered_skills),
            "generated_at": datetime.now()
        }
        
    except User.DoesNotExist:
        raise Http404(f"Student with id {student_id} not found")


@router.post("/student/{student_id}/bkt/reset/{skill_id}",
             response=BKTStateResponseSchema,
             tags=["BKT Algorithm"])
def reset_skill_bkt(request, student_id: int, skill_id: str):
    """
    Reset BKT parameters for a specific skill back to initial state
    
    Useful for allowing students to retake content or for testing purposes.
    Resets P(L) back to P(L0) while preserving other parameters.
    """
    try:
        user = get_object_or_404(User, id=student_id)
        
        # Reset skill parameters
        reset_params = BKTService.reset_skill(user, skill_id)
        
        return {
            "student_id": student_id,
            "skill_id": skill_id,
            "bkt_parameters": {
                "P_L0": reset_params.P_L0,
                "P_T": reset_params.P_T,
                "P_G": reset_params.P_G,
                "P_S": reset_params.P_S,
                "P_L": reset_params.P_L
            },
            "is_mastered": False,
            "mastery_threshold": 0.95,
            "updated_at": datetime.now()
        }
        
    except User.DoesNotExist:
        raise Http404(f"Student with id {student_id} not found")


# ============================================================================
# DKT API Endpoints
# ============================================================================

@router.post("/dkt/update", 
             response=DKTResponseSchema,
             tags=["DKT Algorithm"])
def update_dkt_knowledge(request, data: DKTUpdateSchema):
    """Update DKT knowledge state based on interaction"""
    try:
        from core.models import StudentProfile, Interaction
        student = get_object_or_404(StudentProfile, id=data.student_id)
        
        # Build interaction sequence from database
        interactions = list(Interaction.objects.filter(
            student=student
        ).order_by('timestamp').values(
            'skill_id', 'is_correct', 'response_time'
        ))
        
        # Convert to DKT format
        interaction_sequence = []
        for interaction in interactions:
            interaction_data = {
                "skill_id": interaction['skill_id'],
                "is_correct": interaction['is_correct']
            }
            if interaction['response_time']:
                interaction_data["response_time"] = float(interaction['response_time'])
            interaction_sequence.append(interaction_data)
        
        # Add the current interaction
        current_interaction = {
            "skill_id": data.skill_id,
            "is_correct": data.is_correct
        }
        if data.response_time:
            current_interaction["response_time"] = data.response_time
        interaction_sequence.append(current_interaction)
        
        # Call DKT microservice
        dkt_result = dkt_client.infer_dkt_sync(interaction_sequence, str(student.id))
        
        if dkt_result and dkt_result.get('status') == 'success':
            # Update student's DKT parameters
            student.dkt_hidden_state = dkt_result['hidden_state']
            
            # Update skill predictions in fundamentals
            if 'skill_predictions' in dkt_result:
                if not student.fundamentals_scores:
                    student.fundamentals_scores = {}
                
                # Update skill scores based on DKT predictions
                for skill_idx, prediction in enumerate(dkt_result['skill_predictions']):
                    skill_key = f"skill_{skill_idx}"
                    student.fundamentals_scores[skill_key] = {
                        'mastery_probability': prediction,
                        'dkt_confidence': dkt_result.get('confidence', 0.5),
                        'last_updated': timezone.now().isoformat()
                    }
            
            student.save()
            
            return {
                'status': 'success',
                'skill_id': data.skill_id,
                'mastery_probability': dkt_result['skill_predictions'][data.skill_id] if data.skill_id < len(dkt_result['skill_predictions']) else 0.5,
                'confidence': dkt_result.get('confidence', 0.5),
                'hidden_state_length': len(dkt_result['hidden_state']),
                'updated_skills': len(dkt_result['skill_predictions'])
            }
        else:
            # Fallback: use simple moving average
            recent_interactions = interaction_sequence[-10:]  # Last 10 interactions for this skill
            skill_interactions = [i for i in recent_interactions if i['skill_id'] == data.skill_id]
            
            if skill_interactions:
                correct_count = sum(1 for i in skill_interactions if i['is_correct'])
                mastery_probability = correct_count / len(skill_interactions)
            else:
                mastery_probability = 0.5
            
            # Update fundamentals scores with fallback
            if not student.fundamentals_scores:
                student.fundamentals_scores = {}
            
            skill_key = f"skill_{data.skill_id}"
            student.fundamentals_scores[skill_key] = {
                'mastery_probability': mastery_probability,
                'dkt_confidence': 0.0,  # No DKT confidence available
                'last_updated': timezone.now().isoformat(),
                'fallback_method': 'moving_average'
            }
            student.save()
            
            return {
                'status': 'success_fallback',
                'skill_id': data.skill_id,
                'mastery_probability': mastery_probability,
                'confidence': 0.0,
                'message': 'DKT service unavailable, used fallback method'
            }
        
    except Exception as e:
        logger.error(f"Error updating DKT knowledge: {e}")
        raise HttpError(500, f"Error updating DKT: {str(e)}")


@router.get("/dkt/predict/{student_id}",
            response=DKTPredictionsSchema,
            tags=["DKT Algorithm"])
def get_dkt_predictions(request, student_id: str):
    """Get current DKT predictions for a student"""
    try:
        from core.models import StudentProfile, Interaction
        student = get_object_or_404(StudentProfile, id=student_id)
        
        # Build interaction sequence
        interactions = list(Interaction.objects.filter(
            student=student
        ).order_by('timestamp').values(
            'skill_id', 'is_correct', 'response_time'
        ))
        
        # Convert to DKT format
        interaction_sequence = []
        for interaction in interactions:
            interaction_data = {
                "skill_id": interaction['skill_id'],
                "is_correct": interaction['is_correct']
            }
            if interaction['response_time']:
                interaction_data["response_time"] = float(interaction['response_time'])
            interaction_sequence.append(interaction_data)
        
        # Call DKT microservice
        dkt_result = dkt_client.infer_dkt_sync(interaction_sequence, str(student.id))
        
        if dkt_result and dkt_result.get('status') == 'success':
            return {
                'status': 'success',
                'student_id': student_id,
                'skill_predictions': dkt_result['skill_predictions'],
                'confidence': dkt_result.get('confidence', 0.5),
                'sequence_length': len(interaction_sequence),
                'dkt_service_available': True
            }
        else:
            # Return stored fundamentals scores as fallback
            fundamentals = student.fundamentals_scores or {}
            skill_predictions = []
            
            for i in range(50):  # Assume 50 skills
                skill_key = f"skill_{i}"
                if skill_key in fundamentals:
                    skill_predictions.append(fundamentals[skill_key].get('mastery_probability', 0.5))
                else:
                    skill_predictions.append(0.5)
            
            return {
                'status': 'success_fallback',
                'student_id': student_id,
                'skill_predictions': skill_predictions,
                'confidence': 0.0,
                'sequence_length': len(interaction_sequence),
                'dkt_service_available': False,
                'message': 'Using stored fundamentals scores'
            }
        
    except Exception as e:
        logger.error(f"Error getting DKT predictions: {e}")
        raise HttpError(500, f"Error getting predictions: {str(e)}")


@router.get("/dkt/health")
def check_dkt_health(request):
    """Check DKT microservice health"""
    return dkt_client.check_health_sync()


# ============================================================================
# Legacy/Mock Endpoints (for backwards compatibility)
# ============================================================================

# Pydantic schemas for DKT (placeholder for future implementation)
class KnowledgeComponentSchema(Schema):
    id: Optional[int] = None
    name: str
    subject: str
    difficulty: float  # 0.0 to 1.0

class DKTInputSchema(Schema):
    student_id: int
    interaction_sequence: List[Dict[str, Any]]

class KnowledgeStateSchema(Schema):
    student_id: int
    knowledge_states: Dict[str, float]  # KC_id -> mastery_probability
    updated_at: datetime

# Knowledge Components endpoints
@router.get("/knowledge-components", response=List[KnowledgeComponentSchema], tags=["Knowledge Components"])
def list_knowledge_components(request):
    """Get all knowledge components (placeholder endpoint)"""
    return [
        {
            "id": 1,
            "name": "Algebra Basics",
            "subject": "Mathematics",
            "difficulty": 0.3
        },
        {
            "id": 2,
            "name": "Linear Equations",
            "subject": "Mathematics", 
            "difficulty": 0.5
        }
    ]

# DKT endpoints (integrated with microservice)
@router.post("/dkt/predict", response=KnowledgeStateSchema, tags=["DKT Algorithm"])
def dkt_predict_knowledge(request, payload: DKTInputSchema):
    """Use DKT model to predict knowledge state"""
    try:
        from core.models import StudentProfile
        
        # Get student profile
        student = get_object_or_404(StudentProfile, id=str(payload.student_id))
        
        # Use the interaction sequence provided
        interaction_sequence = payload.interaction_sequence
        
        # Call DKT microservice
        dkt_result = dkt_client.infer_dkt_sync(interaction_sequence, str(payload.student_id))
        
        if dkt_result and dkt_result.get('status') == 'success':
            # Convert skill predictions to knowledge states format
            knowledge_states = {}
            for skill_idx, prediction in enumerate(dkt_result['skill_predictions'][:10]):  # First 10 skills
                knowledge_states[str(skill_idx + 1)] = prediction
        else:
            # Fallback to mock states
            knowledge_states = {
                "1": 0.75,  # KC 1 mastery probability
                "2": 0.60,  # KC 2 mastery probability
                "3": 0.85,  # KC 3 mastery probability
                "4": 0.45,  # KC 4 mastery probability
                "5": 0.70,  # KC 5 mastery probability
            }
        
        return {
            "student_id": payload.student_id,
            "knowledge_states": knowledge_states,
            "updated_at": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error in DKT predict: {e}")
        # Return mock states on error
        mock_states = {
            "1": 0.75,  # KC 1 mastery probability
            "2": 0.60,  # KC 2 mastery probability
        }
        
        return {
            "student_id": payload.student_id,
            "knowledge_states": mock_states,
            "updated_at": datetime.now()
        }

@router.get("/student/{student_id}/next-question", tags=["Recommendations"])
def get_next_recommended_question(request, student_id: int):
    """Get next recommended question based on BKT analysis"""
    return {
        "recommended_question_id": "q42",
        "skill_id": "algebra_linear_equations",
        "difficulty_level": 0.6,
        "reasoning": "Student needs more practice with linear equations (P_L = 0.75)",
        "confidence": 0.85
    }

@router.get("/algorithms/compare/{student_id}", tags=["Algorithm Comparison"])
def compare_bkt_dkt(request, student_id: int):
    """Compare BKT vs DKT predictions for a student"""
    try:
        from core.models import StudentProfile, Interaction
        from django.contrib.auth.models import User
        
        # Get Django User and StudentProfile
        user = get_object_or_404(User, id=student_id)
        student_profile = get_object_or_404(StudentProfile, user=user)
        
        # Get BKT predictions for common skills
        bkt_predictions = {}
        common_skills = ["algebra", "equations", "geometry", "statistics"]
        
        for skill in common_skills:
            try:
                bkt_params = BKTService.get_skill_bkt_params(user, skill)
                bkt_predictions[skill] = round(bkt_params.P_L, 3)
            except:
                bkt_predictions[skill] = 0.5  # Default if skill not found
        
        # Get DKT predictions
        interactions = list(Interaction.objects.filter(
            student=student_profile
        ).order_by('timestamp').values(
            'skill_id', 'is_correct', 'response_time'
        ))
        
        # Convert to DKT format
        interaction_sequence = []
        for interaction in interactions:
            interaction_data = {
                "skill_id": interaction['skill_id'],
                "is_correct": interaction['is_correct']
            }
            if interaction['response_time']:
                interaction_data["response_time"] = float(interaction['response_time'])
            interaction_sequence.append(interaction_data)
        
        # Call DKT microservice
        dkt_result = dkt_client.infer_dkt_sync(interaction_sequence, str(student_profile.id))
        
        dkt_predictions = {}
        if dkt_result and dkt_result.get('status') == 'success' and len(dkt_result['skill_predictions']) >= 4:
            # Map first 4 DKT predictions to common skills
            skill_mappings = [(0, "algebra"), (1, "equations"), (2, "geometry"), (3, "statistics")]
            for skill_idx, skill_name in skill_mappings:
                dkt_predictions[skill_name] = round(dkt_result['skill_predictions'][skill_idx], 3)
        else:
            # Fallback DKT predictions
            dkt_predictions = {"algebra": 0.75, "equations": 0.65, "geometry": 0.80, "statistics": 0.55}
        
        # Calculate recommendation based on agreement
        agreements = []
        for skill in common_skills:
            diff = abs(bkt_predictions[skill] - dkt_predictions[skill])
            agreements.append(diff)
        
        avg_disagreement = sum(agreements) / len(agreements)
        
        # Recommend algorithm based on data availability and agreement
        if len(interaction_sequence) < 5:
            recommended_algorithm = "bkt"
            reasoning = "Insufficient data for DKT, BKT better for cold start"
        elif avg_disagreement > 0.3:
            recommended_algorithm = "ensemble"
            reasoning = "High disagreement between algorithms, use ensemble"
        elif dkt_result and dkt_result.get('status') == 'success':
            recommended_algorithm = "dkt"
            reasoning = "Sufficient data available, DKT captures complex patterns"
        else:
            recommended_algorithm = "bkt"
            reasoning = "DKT service unavailable, fallback to BKT"
        
        return {
            "student_id": student_id,
            "bkt_predictions": bkt_predictions,
            "dkt_predictions": dkt_predictions,
            "recommended_algorithm": recommended_algorithm,
            "reasoning": reasoning,
            "confidence": max(0.5, 1.0 - avg_disagreement),
            "interaction_count": len(interaction_sequence),
            "dkt_service_available": dkt_result is not None and dkt_result.get('status') == 'success'
        }
        
    except Exception as e:
        logger.error(f"Error comparing algorithms: {e}")
        # Return default comparison on error
        return {
            "student_id": student_id,
            "bkt_predictions": {"algebra": 0.7, "equations": 0.6},
            "dkt_predictions": {"algebra": 0.75, "equations": 0.65},
            "recommended_algorithm": "bkt",
            "reasoning": "Error occurred, defaulting to BKT",
            "confidence": 0.5,
            "error": str(e)
        }

@router.get("/status", tags=["System"])
def student_model_status(request):
    """Student model app status endpoint"""
    # Check DKT service availability
    dkt_status = dkt_client.check_health_sync()
    
    return {
        "app": "student_model", 
        "status": "ready", 
        "description": "BKT and DKT knowledge tracing algorithms with microservice integration",
        "algorithms": {
            "bkt": {
                "status": "implemented",
                "version": "1.0",
                "features": ["bayesian_update", "mastery_tracking", "skill_reset", "django_integration"]
            },
            "dkt": {
                "status": "implemented" if dkt_status.get('dkt_service_available') else "service_unavailable",
                "version": "1.0",
                "features": ["lstm_predictions", "sequence_modeling", "microservice_integration", "fallback_handling"],
                "microservice_url": dkt_client.base_url,
                "service_health": dkt_status.get('status', 'unknown')
            }
        },
        "integration": {
            "django_ninja": "enabled",
            "microservice_architecture": "enabled",
            "fallback_mechanisms": "enabled",
            "database_models": "core.models.StudentProfile"
        }
    }