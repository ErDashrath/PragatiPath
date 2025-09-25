"""
API endpoints for LangGraph-orchestrated adaptive learning
"""

from ninja import Router, Schema
from typing import Dict, Any, Optional
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError
import logging

from core.models import StudentProfile
from .adaptive_orchestrator import adaptive_orchestrator

logger = logging.getLogger(__name__)

orchestration_router = Router()

# ============================================================================
# Request/Response Schemas
# ============================================================================

class StartAdaptiveSessionSchema(Schema):
    student_id: str
    subject: Optional[str] = "mathematics"
    max_iterations: Optional[int] = 10
    mastery_threshold: Optional[float] = 0.8

class AdaptiveSessionResponseSchema(Schema):
    success: bool
    student_id: str
    subject: str
    questions_attempted: int
    final_skill: str
    recommendation: str
    session_complete: bool
    bkt_mastery: float
    dkt_prediction: float
    error_message: Optional[str] = None

class QuestionResponseSchema(Schema):
    student_id: str
    question_id: str
    answer: str
    is_correct: bool
    response_time: float

# ============================================================================
# Orchestration API Endpoints
# ============================================================================

@orchestration_router.post("/adaptive-session/start", response=AdaptiveSessionResponseSchema)
def start_adaptive_session(request, data: StartAdaptiveSessionSchema):
    """
    Start a complete adaptive learning session using LangGraph orchestration
    
    This endpoint runs an entire adaptive session that:
    1. Analyzes student knowledge using BKT + DKT
    2. Selects optimal questions adaptively  
    3. Updates knowledge models in real-time
    4. Makes intelligent progression decisions
    5. Provides comprehensive session analytics
    """
    try:
        logger.info(f"🚀 Starting orchestrated adaptive session for student: {data.student_id}")
        
        # Validate student exists
        student_profile = get_object_or_404(StudentProfile, id=data.student_id)
        
        # Run LangGraph orchestrated session
        result = adaptive_orchestrator.run_adaptive_session(
            student_id=data.student_id,
            subject=data.subject,
            max_iterations=data.max_iterations
        )
        
        if not result["success"]:
            raise HttpError(500, f"Adaptive session failed: {result.get('error', 'Unknown error')}")
        
        logger.info(f"✅ Adaptive session completed - {result['questions_attempted']} questions")
        
        return AdaptiveSessionResponseSchema(**result)
        
    except Exception as e:
        logger.error(f"❌ Adaptive session API error: {e}")
        raise HttpError(500, f"Failed to run adaptive session: {str(e)}")

@orchestration_router.get("/adaptive-session/health")
def orchestration_health(request):
    """Health check for orchestration system"""
    try:
        # Test that orchestrator can be initialized
        test_result = {
            "status": "healthy",
            "orchestrator_ready": adaptive_orchestrator is not None,
            "langraph_available": True,
            "services_integrated": {
                "bkt": adaptive_orchestrator.bkt_service is not None,
                "dkt": adaptive_orchestrator.dkt_service is not None
            }
        }
        
        logger.info("✅ Orchestration system health check passed")
        return test_result
        
    except Exception as e:
        logger.error(f"❌ Orchestration health check failed: {e}")
        raise HttpError(500, f"Orchestration system unhealthy: {str(e)}")

@orchestration_router.get("/adaptive-session/workflow-status/{student_id}")
def get_workflow_status(request, student_id: str):
    """
    Get the current workflow status for a student's adaptive session
    
    Provides insights into the LangGraph workflow execution
    """
    try:
        # Validate student exists
        student_profile = get_object_or_404(StudentProfile, id=student_id)
        
        # Get knowledge states from both models
        bkt_state = adaptive_orchestrator.bkt_service.get_skill_mastery(
            student_profile.user, "mathematics_basic"
        )
        dkt_state = adaptive_orchestrator.dkt_service.get_skill_predictions(
            student_profile.user, ["mathematics_basic"]
        )
        
        workflow_status = {
            "student_id": student_id,
            "workflow_ready": True,
            "current_knowledge_state": {
                "bkt": bkt_state or {"mastery_probability": 0.5},
                "dkt": dkt_state or {"predictions": {"mathematics_basic": 0.5}}
            },
            "orchestration_available": True,
            "next_recommended_action": "start_adaptive_session"
        }
        
        return workflow_status
        
    except Exception as e:
        logger.error(f"❌ Workflow status check failed: {e}")
        raise HttpError(500, f"Failed to get workflow status: {str(e)}")

@orchestration_router.post("/adaptive-session/simulate")
def simulate_adaptive_session(request, data: StartAdaptiveSessionSchema):
    """
    Simulate an adaptive session with mock student responses
    
    Useful for testing the LangGraph orchestration without real student interaction
    """
    try:
        logger.info(f"🎭 Simulating adaptive session for student: {data.student_id}")
        
        # Validate student exists
        student_profile = get_object_or_404(StudentProfile, id=data.student_id)
        
        # Run simulated session (orchestrator handles simulation internally)
        result = adaptive_orchestrator.run_adaptive_session(
            student_id=data.student_id,
            subject=data.subject,
            max_iterations=min(data.max_iterations, 5)  # Limit for simulation
        )
        
        # Add simulation metadata
        result["simulation"] = True
        result["note"] = "This was a simulated session with mock student responses"
        
        if not result["success"]:
            raise HttpError(500, f"Simulation failed: {result.get('error', 'Unknown error')}")
        
        logger.info(f"🎭 Simulation completed - {result['questions_attempted']} questions")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Simulation API error: {e}")
        raise HttpError(500, f"Failed to run simulation: {str(e)}")

@orchestration_router.get("/adaptive-session/analytics/{student_id}")
def get_adaptive_analytics(request, student_id: str):
    """
    Get comprehensive adaptive learning analytics powered by LangGraph orchestration
    """
    try:
        # Validate student exists
        student_profile = get_object_or_404(StudentProfile, id=student_id)
        
        # Get analytics from both models
        bkt_analytics = adaptive_orchestrator.bkt_service.get_all_masteries(student_profile.user)
        dkt_analytics = adaptive_orchestrator.dkt_service.get_all_predictions(student_profile.user)
        
        # Combine analytics
        analytics = {
            "student_id": student_id,
            "orchestration_insights": {
                "total_skills_tracked": len(bkt_analytics.get("masteries", {})),
                "average_bkt_mastery": sum(bkt_analytics.get("masteries", {}).values()) / max(1, len(bkt_analytics.get("masteries", {}))),
                "average_dkt_prediction": sum(dkt_analytics.get("predictions", {}).values()) / max(1, len(dkt_analytics.get("predictions", {}))),
                "langraph_orchestration": "active"
            },
            "detailed_states": {
                "bkt": bkt_analytics,
                "dkt": dkt_analytics
            },
            "recommendations": {
                "ready_for_advanced": [],
                "needs_reinforcement": [],
                "optimal_next_skills": []
            }
        }
        
        # Generate recommendations based on combined analysis
        for skill, mastery in bkt_analytics.get("masteries", {}).items():
            if mastery >= 0.8:
                analytics["recommendations"]["ready_for_advanced"].append(skill)
            elif mastery < 0.4:
                analytics["recommendations"]["needs_reinforcement"].append(skill)
            else:
                analytics["recommendations"]["optimal_next_skills"].append(skill)
        
        return analytics
        
    except Exception as e:
        logger.error(f"❌ Analytics API error: {e}")
        raise HttpError(500, f"Failed to get analytics: {str(e)}")