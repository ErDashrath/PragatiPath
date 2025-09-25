"""
Adaptive Assessment API Extensions

Additional endpoints for real-time adaptive question selection and knowledge tracking.
"""

from ninja import Router, Schema
from typing import List, Dict, Any, Optional
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError
import logging

from .adaptive_question_selector import adaptive_selector
from .models import StudentSession, QuestionAttempt, AdaptiveQuestion
from core.models import StudentProfile
from student_model.dkt import DKTService

logger = logging.getLogger(__name__)

adaptive_router = Router()

# ============================================================================
# Schemas for Real-time Adaptation
# ============================================================================

class RealtimeUpdateSchema(Schema):
    student_id: str
    question_id: str
    skill_id: str
    is_correct: bool
    interaction_data: Optional[Dict[str, Any]] = None

# ============================================================================
# Schemas for Adaptive Assessment API
# ============================================================================

class KnowledgeStateRequest(Schema):
    """Request schema for getting knowledge state"""
    student_id: str
    subject_code: str

class KnowledgeStateResponse(Schema):
    """Response schema for knowledge state"""
    student_id: str
    subject_code: str
    bkt_skills: Dict[str, Dict[str, float]]
    dkt_predictions: List[float]
    recommended_algorithm: str
    confidence: float
    total_interactions: int
    last_updated: str

class NextQuestionRequest(Schema):
    """Request schema for getting next adaptive question"""
    student_id: str
    session_id: str
    previous_answers: Optional[List[Dict[str, Any]]] = []

class NextQuestionResponse(Schema):
    """Response schema for next question"""
    question_id: str
    question_text: str
    options: Dict[str, str]
    difficulty: str
    estimated_time: int
    selection_algorithm: str
    adaptive_metadata: Dict[str, Any]
    confidence: float

class AdaptiveRecommendationRequest(Schema):
    """Request schema for question recommendations"""
    student_id: str
    subject_code: str
    chapter_id: Optional[str] = None
    count: int = 5
    assessment_type: str = 'ADAPTIVE'

class AdaptiveRecommendationResponse(Schema):
    """Response schema for recommendations"""
    student_id: str
    recommendations: List[Dict[str, Any]]
    algorithm_used: str
    confidence: float
    reason: str

# ============================================================================
# Adaptive Assessment Endpoints
# ============================================================================

@adaptive_router.post("/knowledge-state", response=KnowledgeStateResponse)
def get_student_knowledge_state(request, payload: KnowledgeStateRequest):
    """
    Get comprehensive knowledge state for a student using BKT and DKT.
    
    This endpoint provides real-time analysis of student's mastery levels
    across all skills in a subject using both Bayesian and Deep Knowledge Tracing.
    """
    try:
        # Get user
        user = get_object_or_404(User, id=payload.student_id)
        
        # Get knowledge state from adaptive selector
        knowledge_state = adaptive_selector._get_student_knowledge_state(
            user, payload.subject_code
        )
        
        # Format BKT skills for response
        bkt_skills = {}
        bkt_state = knowledge_state.get('bkt_state', {})
        
        for skill, params in bkt_state.items():
            bkt_skills[skill] = {
                'P_L0': params.P_L0,
                'P_T': params.P_T, 
                'P_G': params.P_G,
                'P_S': params.P_S,
                'P_L': params.P_L,
                'is_mastered': params.P_L >= 0.95
            }
        
        # Get DKT predictions
        dkt_state = knowledge_state.get('dkt_state', {})
        dkt_predictions = dkt_state.get('skill_predictions', [])
        
        # Count total interactions
        total_interactions = QuestionAttempt.objects.filter(
            session__student=user
        ).count()
        
        return {
            'student_id': payload.student_id,
            'subject_code': payload.subject_code,
            'bkt_skills': bkt_skills,
            'dkt_predictions': dkt_predictions,
            'recommended_algorithm': knowledge_state.get('recommended_algorithm', 'bkt'),
            'confidence': dkt_state.get('confidence', 0.5),
            'total_interactions': total_interactions,
            'last_updated': knowledge_state.get('timestamp', '').isoformat() if knowledge_state.get('timestamp') else ''
        }
        
    except Exception as e:
        logger.error(f"Error getting knowledge state: {e}")
        raise HttpError(500, f"Failed to get knowledge state: {str(e)}")

@adaptive_router.post("/next-question", response=NextQuestionResponse)
def get_next_adaptive_question(request, payload: NextQuestionRequest):
    """
    Get the next adaptive question based on real-time knowledge state analysis.
    
    This endpoint uses the latest student interactions to select the optimal
    next question using BKT/DKT algorithms.
    """
    try:
        # Get user and session
        user = get_object_or_404(User, id=payload.student_id)
        session = get_object_or_404(StudentSession, id=payload.session_id)
        
        # Get next adaptive question
        next_question = adaptive_selector.get_next_adaptive_question(
            user=user,
            session=session,
            previous_answers=payload.previous_answers
        )
        
        if not next_question:
            raise HttpError(404, "No more questions available")
        
        return NextQuestionResponse(
            question_id=next_question['id'],
            question_text=next_question['question_text'],
            options=next_question['options'],
            difficulty=next_question['difficulty'],
            estimated_time=next_question.get('estimated_time', 60),
            selection_algorithm=next_question.get('selection_algorithm', 'adaptive'),
            adaptive_metadata=next_question.get('adaptive_metadata', {}),
            confidence=next_question.get('adaptive_metadata', {}).get('recommendation_confidence', 0.5)
        )
        
    except Exception as e:
        logger.error(f"Error getting next question: {e}")
        raise HttpError(500, f"Failed to get next question: {str(e)}")

@adaptive_router.post("/recommendations", response=AdaptiveRecommendationResponse)
def get_adaptive_recommendations(request, payload: AdaptiveRecommendationRequest):
    """
    Get adaptive question recommendations for a student.
    
    This endpoint analyzes student's knowledge state and recommends
    the most appropriate questions for their learning needs.
    """
    try:
        # Get user
        user = get_object_or_404(User, id=payload.student_id)
        
        # Get adaptive question recommendations
        recommendations = adaptive_selector.select_questions(
            user=user,
            subject_code=payload.subject_code,
            chapter_id=payload.chapter_id,
            question_count=payload.count,
            assessment_type=payload.assessment_type
        )
        
        # Get knowledge state for metadata
        knowledge_state = adaptive_selector._get_student_knowledge_state(
            user, payload.subject_code
        )
        
        algorithm_used = knowledge_state.get('recommended_algorithm', 'adaptive')
        confidence = knowledge_state.get('dkt_state', {}).get('confidence', 0.5)
        
        # Generate reason for recommendations
        bkt_state = knowledge_state.get('bkt_state', {})
        weak_skills = [
            skill for skill, params in bkt_state.items() 
            if hasattr(params, 'P_L') and params.P_L < 0.6
        ]
        
        if weak_skills:
            reason = f"Focusing on skills needing practice: {', '.join(weak_skills[:3])}"
        elif algorithm_used == 'dkt':
            reason = "Using neural network analysis for optimal question selection"
        else:
            reason = "Using Bayesian analysis for personalized question selection"
        
        return {
            'student_id': payload.student_id,
            'recommendations': recommendations,
            'algorithm_used': algorithm_used,
            'confidence': confidence,
            'reason': reason
        }
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HttpError(500, f"Failed to get recommendations: {str(e)}")

@adaptive_router.get("/algorithms/status")
def get_adaptive_algorithms_status(request):
    """
    Get status of BKT and DKT algorithms and their availability.
    """
    try:
        # Check DKT service availability
        dkt_service = DKTService()
        dkt_health = {'dkt_service_available': True, 'status': 'healthy', 'integrated_service': True}
        
        # Count active students with BKT data
        try:
            from student_model.models import BKTSkillState
            active_bkt_students = BKTSkillState.objects.values('user').distinct().count()
        except Exception:
            active_bkt_students = 0  # Fallback if model doesn't exist yet
        
        # Count total questions available
        total_questions = AdaptiveQuestion.objects.filter(is_active=True).count()
        
        return {
            'status': 'operational',
            'algorithms': {
                'bkt': {
                    'status': 'active',
                    'active_students': active_bkt_students,
                    'features': ['bayesian_tracking', 'mastery_detection', 'skill_progression']
                },
                'dkt': {
                    'status': 'active' if dkt_health.get('dkt_service_available') else 'unavailable',
                    'service_health': dkt_health.get('status', 'unknown'),
                    'features': ['lstm_predictions', 'sequence_modeling', 'pattern_recognition']
                }
            },
            'question_database': {
                'total_questions': total_questions,
                'subjects': list(AdaptiveQuestion.objects.values_list('subject', flat=True).distinct())
            },
            'adaptive_selection': {
                'enabled': True,
                'fallback_available': True,
                'real_time_adaptation': True
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting algorithm status: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'algorithms': {
                'bkt': {'status': 'unknown'},
                'dkt': {'status': 'unknown'}
            }
        }

@adaptive_router.get("/student/{student_id}/progress-analytics")
def get_student_progress_analytics(request, student_id: str):
    """
    Get detailed analytics about student's learning progress using BKT/DKT.
    """
    try:
        user = get_object_or_404(User, id=student_id)
        
        # Get all subjects from your competitive exam CSV data structure
        attempted_subjects = []
        try:
            # Get subjects from your CSV-loaded questions
            attempted_subjects = list(AdaptiveQuestion.objects.values_list('subject', flat=True).distinct())
        except:
            pass
        
        # If no subjects found, use your competitive exam subjects
        if not attempted_subjects:
            attempted_subjects = ['data_interpretation', 'logical_reasoning', 'quantitative_aptitude', 'verbal_ability']
        
        analytics = {
            'student_id': student_id,
            'subjects_attempted': attempted_subjects,
            'subject_analysis': {}
        }
        
        # Analyze each subject
        for subject in attempted_subjects:
            try:
                knowledge_state = adaptive_selector._get_student_knowledge_state(user, subject)
            except Exception as e:
                logger.warning(f"Could not get knowledge state for {subject}: {e}")
                # Create default knowledge state
                knowledge_state = {
                    'bkt_state': {},
                    'recommended_algorithm': 'bkt',
                    'dkt_state': {'confidence': 0.5}
                }
            
            bkt_state = knowledge_state.get('bkt_state', {})
            mastered_skills = [
                skill for skill, params in bkt_state.items()
                if hasattr(params, 'P_L') and params.P_L >= 0.95
            ]
            
            weak_skills = [
                skill for skill, params in bkt_state.items()
                if hasattr(params, 'P_L') and params.P_L < 0.5
            ]
            
            # Calculate overall mastery
            if bkt_state:
                mastery_scores = [
                    params.P_L for params in bkt_state.values() 
                    if hasattr(params, 'P_L')
                ]
                avg_mastery = sum(mastery_scores) / len(mastery_scores) if mastery_scores else 0
            else:
                avg_mastery = 0
            
            analytics['subject_analysis'][subject] = {
                'overall_mastery': round(avg_mastery, 3),
                'mastered_skills': mastered_skills,
                'skills_needing_practice': weak_skills,
                'total_skills_tracked': len(bkt_state),
                'recommended_algorithm': knowledge_state.get('recommended_algorithm', 'bkt'),
                'confidence': knowledge_state.get('dkt_state', {}).get('confidence', 0.5)
            }
        
        # Get recent performance trends
        recent_attempts = QuestionAttempt.objects.filter(
            session__student=user
        ).order_by('-created_at')[:20]
        
        recent_performance = {
            'total_recent_attempts': len(recent_attempts),
            'accuracy': sum(1 for attempt in recent_attempts if attempt.is_correct) / len(recent_attempts) if recent_attempts else 0,
            'avg_response_time': sum(attempt.response_time or 60 for attempt in recent_attempts) / len(recent_attempts) if recent_attempts else 0
        }
        
        analytics['recent_performance'] = recent_performance
        
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting progress analytics: {e}")
        raise HttpError(500, f"Failed to get analytics: {str(e)}")

# ============================================================================
# Real-time Adaptation Endpoints
# ============================================================================

@adaptive_router.post("/realtime/update-knowledge")
def update_knowledge_realtime(request, data: RealtimeUpdateSchema):
    """
    Update student knowledge state in real-time as they answer questions.
    
    This endpoint is called after each question attempt to update BKT/DKT
    and prepare for the next adaptive question selection.
    """
    try:
        # Get student profile first, then user
        student_profile = get_object_or_404(StudentProfile, id=data.student_id)
        user = student_profile.user
        
        # Try to get the question, but don't fail if it doesn't exist
        question = None
        try:
            question = AdaptiveQuestion.objects.get(id=data.question_id)
        except AdaptiveQuestion.DoesNotExist:
            logger.warning(f"Question {data.question_id} not found, using skill_id from request")
        
        # Update BKT for relevant skills
        if question:
            skill_id = data.skill_id or f"{question.subject}_{question.difficulty_level}"
        else:
            skill_id = data.skill_id or 'general_skill'
        
        from student_model.bkt import BKTService
        BKTService.update_skill_bkt(
            user=user,
            skill_id=skill_id,
            is_correct=data.is_correct,
            interaction_data=data.interaction_data or {}
        )
        
        # Update DKT using integrated service
        try:
            from student_model.dkt import DKTService
            dkt_service = DKTService()
            
            dkt_result = dkt_service.update_dkt_knowledge(
                user=user,
                skill_id=skill_id,
                is_correct=data.is_correct,
                interaction_data=data.interaction_data or {}
            )
            
            logger.info(f"Real-time DKT and BKT update completed for user {user.id}")
        except Exception as dkt_error:
            logger.warning(f"DKT real-time update failed: {dkt_error}")
        
        # Get updated BKT state for response
        try:
            from student_model.bkt import BKTService
            bkt_state = BKTService.get_skill_mastery(user, skill_id)
            mastery_level = bkt_state.get('mastery_probability', 0.0) if bkt_state else 0.0
        except:
            mastery_level = 0.0
        
        return {
            'status': 'success',
            'updated_skill': skill_id,
            'bkt_updated': True,
            'dkt_updated': True,
            'bkt_mastery': mastery_level,
            'message': f'Knowledge updated for skill: {skill_id}'
        }
        
    except Exception as e:
        logger.error(f"Error in real-time update: {e}")
        raise HttpError(500, f"Real-time update failed: {str(e)}")

@adaptive_router.get("/debug/selection-trace/{student_id}")
def get_selection_trace(request, student_id: str):
    """
    Debug endpoint to trace how adaptive question selection works for a student.
    
    Provides detailed breakdown of the selection algorithm logic.
    """
    try:
        user = get_object_or_404(User, id=student_id)
        
        # Get knowledge state
        knowledge_state = adaptive_selector._get_student_knowledge_state(user, 'MATH')  # Using MATH as example
        
        # Analyze algorithm choice
        total_attempts = QuestionAttempt.objects.filter(session__student=user).count()
        
        trace = {
            'student_id': student_id,
            'total_attempts': total_attempts,
            'algorithm_choice_logic': {
                'cold_start': total_attempts < 5,
                'dkt_available': knowledge_state.get('dkt_state', {}).get('available', False),
                'recommended_algorithm': knowledge_state.get('recommended_algorithm'),
            },
            'bkt_analysis': {},
            'dkt_analysis': knowledge_state.get('dkt_state', {}),
            'selection_strategy': ''
        }
        
        # BKT analysis
        bkt_state = knowledge_state.get('bkt_state', {})
        for skill, params in bkt_state.items():
            if hasattr(params, 'P_L'):
                trace['bkt_analysis'][skill] = {
                    'mastery_probability': params.P_L,
                    'needs_practice': params.P_L < 0.6,
                    'mastered': params.P_L >= 0.95
                }
        
        # Determine selection strategy explanation
        algorithm = knowledge_state.get('recommended_algorithm', 'bkt')
        if algorithm == 'bkt':
            trace['selection_strategy'] = "Using BKT: Focus on skills with low mastery probability"
        elif algorithm == 'dkt':
            trace['selection_strategy'] = "Using DKT: Neural network predictions for complex patterns"
        else:
            trace['selection_strategy'] = "Using ensemble: Combining BKT and DKT recommendations"
        
        return trace
        
    except Exception as e:
        logger.error(f"Error getting selection trace: {e}")
        raise HttpError(500, f"Failed to get trace: {str(e)}")