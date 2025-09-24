from ninja import Router
from ninja import Schema
from ninja.errors import HttpError
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import logging
import uuid
from django.db import transaction
from django.utils import timezone
import json

# Import IRT components
from .irt import IRTEngine, IRTAdaptiveSelector

logger = logging.getLogger(__name__)

router = Router()

# ============================================================================
# Main Assessment Orchestration Schemas
# ============================================================================

class AssessmentSubmissionSchema(Schema):
    """Schema for submitting an answer - orchestrates all algorithms"""
    student_id: str
    question_id: str
    answer: str
    response_time: float  # Response time in seconds
    skill_id: Optional[str] = "default"
    subject: Optional[str] = None  # For subject-wise progression tracking
    metadata: Optional[Dict[str, Any]] = {}

class SubjectQuestionRequestSchema(Schema):
    """Schema for requesting subject-specific questions"""
    student_id: str
    subject: str
    difficulty_level: Optional[str] = None  # very_easy, easy, moderate, difficult
    count: Optional[int] = 1  # Number of questions to return
    level: Optional[int] = None  # Specific level if needed

class NextQuestionSchema(Schema):
    """Schema for the next recommended question"""
    question_id: Optional[str]
    question_text: Optional[str]
    question_type: Optional[str]
    difficulty: Optional[float]
    skill_id: Optional[str]
    selection_method: str  # "irt", "random", "none"
    selection_reasoning: str

class StudentStateSchema(Schema):
    """Comprehensive student state after interaction"""
    student_id: str
    bkt_parameters: Dict[str, Any]
    dkt_hidden_state: Optional[List[float]]  # DKT hidden state is a list of floats
    irt_theta: float
    fundamentals: Dict[str, float]
    srs_cards_updated: int
    total_interactions: int
    session_progress: Dict[str, Any]
    level_progression: Dict[str, Any]  # Level progression information

class AssessmentSubmissionResponseSchema(Schema):
    """Complete response for assessment submission"""
    success: bool
    interaction_id: str
    was_correct: bool
    feedback: str
    next_question: NextQuestionSchema
    updated_student_state: StudentStateSchema
    algorithm_results: Dict[str, Any]  # Detailed results from each algorithm
    performance_metrics: Dict[str, Any]
    recommendations: List[str]

class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    NUMERICAL = "numerical"

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

# Pydantic schemas for assessment
class QuestionSchema(Schema):
    id: Optional[int] = None
    title: str
    content: str
    question_type: QuestionType
    difficulty_level: DifficultyLevel
    knowledge_component_id: int
    options: Optional[List[str]] = None  # For multiple choice
    correct_answer: str
    explanation: Optional[str] = None
    created_at: Optional[datetime] = None

class QuestionCreateSchema(Schema):
    title: str
    content: str
    question_type: QuestionType
    difficulty_level: DifficultyLevel
    knowledge_component_id: int
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: Optional[str] = None

class StudentResponseSchema(Schema):
    id: Optional[int] = None
    student_id: int
    question_id: int
    answer: str
    is_correct: bool
    response_time: float  # in seconds
    timestamp: Optional[datetime] = None

class SubmitResponseSchema(Schema):
    student_id: int
    question_id: int
    answer: str
    response_time: float


# ============================================================================
# IRT (Item Response Theory) Schemas
# ============================================================================

class IRTQuestionSelectionSchema(Schema):
    """Schema for IRT question selection request"""
    student_id: str
    skill_id: Optional[str] = None
    exclude_recent: bool = True
    use_bkt_integration: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "student-123",
                "skill_id": "algebra_basics",
                "exclude_recent": True,
                "use_bkt_integration": True
            }
        }


class IRTQuestionResponseSchema(Schema):
    """Schema for IRT question selection response"""
    question_id: Optional[str] = None
    question_text: Optional[str] = None
    difficulty: float
    estimated_theta: float
    selection_reasoning: str
    irt_probability: Optional[float] = None
    bkt_integration_used: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "question_id": "q-456",
                "question_text": "What is the value of x in 2x + 5 = 15?",
                "difficulty": 0.2,
                "estimated_theta": 0.3,
                "selection_reasoning": "Question difficulty (0.2) matches student ability (0.3)",
                "irt_probability": 0.65,
                "bkt_integration_used": True
            }
        }


class IRTThetaUpdateSchema(Schema):
    """Schema for theta update request"""
    student_id: str
    question_id: str
    is_correct: bool
    response_time: Optional[float] = None
    use_question_difficulty: bool = True


class IRTThetaResponseSchema(Schema):
    """Schema for theta update response"""
    student_id: str
    previous_theta: float
    new_theta: float
    theta_change: float
    question_difficulty: Optional[float] = None
    updated_at: datetime


class IRTAnalysisSchema(Schema):
    """Schema for IRT analysis response"""
    student_id: str
    current_theta: float
    theta_source: str  # 'bkt_integration', 'interaction_history', 'default'
    ability_level: str  # 'low', 'medium', 'high'
    recommended_difficulty: float
    confidence: float
    analysis_details: Dict[str, Any]

class AssessmentSchema(Schema):
    id: Optional[int] = None
    title: str
    description: str
    question_ids: List[int]
    time_limit: Optional[int] = None  # in minutes
    is_adaptive: bool = False
    created_at: Optional[datetime] = None

class AssessmentCreateSchema(Schema):
    title: str
    description: str
    question_ids: List[int]
    time_limit: Optional[int] = None
    is_adaptive: bool = False

# Question management endpoints
@router.get("/questions", response=List[QuestionSchema])
def list_questions(request, 
                   question_type: Optional[QuestionType] = None,
                   difficulty: Optional[DifficultyLevel] = None,
                   knowledge_component_id: Optional[int] = None):
    """Get all questions with optional filtering"""
    # TODO: Implement actual database query with filters
    return [
        {
            "id": 1,
            "title": "Basic Algebra",
            "content": "What is x in the equation: 2x + 5 = 15?",
            "question_type": QuestionType.MULTIPLE_CHOICE,
            "difficulty_level": DifficultyLevel.BEGINNER,
            "knowledge_component_id": 1,
            "options": ["5", "10", "15", "20"],
            "correct_answer": "5",
            "explanation": "2x = 15 - 5 = 10, therefore x = 5",
            "created_at": datetime.now()
        }
    ]

@router.get("/questions/{question_id}", response=QuestionSchema)
def get_question(request, question_id: int):
    """Get a specific question by ID"""
    # TODO: Implement actual database query
    return {
        "id": question_id,
        "title": "Basic Algebra",
        "content": "What is x in the equation: 2x + 5 = 15?",
        "question_type": QuestionType.MULTIPLE_CHOICE,
        "difficulty_level": DifficultyLevel.BEGINNER,
        "knowledge_component_id": 1,
        "options": ["5", "10", "15", "20"],
        "correct_answer": "5",
        "explanation": "2x = 15 - 5 = 10, therefore x = 5",
        "created_at": datetime.now()
    }

@router.post("/questions", response=QuestionSchema)
def create_question(request, payload: QuestionCreateSchema):
    """Create a new question"""
    # TODO: Implement actual database creation
    return {
        "id": 1,
        "title": payload.title,
        "content": payload.content,
        "question_type": payload.question_type,
        "difficulty_level": payload.difficulty_level,
        "knowledge_component_id": payload.knowledge_component_id,
        "options": payload.options,
        "correct_answer": payload.correct_answer,
        "explanation": payload.explanation,
        "created_at": datetime.now()
    }

# Student response endpoints
@router.post("/responses", response=StudentResponseSchema)
def submit_response(request, payload: SubmitResponseSchema):
    """Submit a student response to a question"""
    # TODO: Implement actual response processing and correctness checking
    is_correct = payload.answer == "5"  # Mock correctness check
    
    response = {
        "id": 1,
        "student_id": payload.student_id,
        "question_id": payload.question_id,
        "answer": payload.answer,
        "is_correct": is_correct,
        "response_time": payload.response_time,
        "timestamp": datetime.now()
    }
    
    # TODO: Trigger BKT/DKT update via Celery task
    
    return response

@router.get("/responses/student/{student_id}", response=List[StudentResponseSchema])
def get_student_responses(request, student_id: int):
    """Get all responses for a specific student"""
    # TODO: Implement actual database query
    return [
        {
            "id": 1,
            "student_id": student_id,
            "question_id": 1,
            "answer": "5",
            "is_correct": True,
            "response_time": 12.5,
            "timestamp": datetime.now()
        }
    ]

# Assessment endpoints
@router.get("/assessments", response=List[AssessmentSchema])
def list_assessments(request):
    """Get all assessments"""
    # TODO: Implement actual database query
    return [
        {
            "id": 1,
            "title": "Algebra Basics Test",
            "description": "Test covering basic algebraic concepts",
            "question_ids": [1, 2, 3, 4, 5],
            "time_limit": 30,
            "is_adaptive": False,
            "created_at": datetime.now()
        }
    ]

@router.post("/assessments", response=AssessmentSchema)
def create_assessment(request, payload: AssessmentCreateSchema):
    """Create a new assessment"""
    # TODO: Implement actual database creation
    return {
        "id": 1,
        "title": payload.title,
        "description": payload.description,
        "question_ids": payload.question_ids,
        "time_limit": payload.time_limit,
        "is_adaptive": payload.is_adaptive,
        "created_at": datetime.now()
    }

@router.get("/assessments/{assessment_id}/adaptive-next-question/{student_id}")
def get_adaptive_next_question(request, assessment_id: int, student_id: int):
    """Get next question in adaptive assessment based on student performance"""
    # TODO: Implement adaptive question selection using BKT/DKT
    return {
        "question_id": 2,
        "reasoning": "Student mastered basic concepts, moving to intermediate level",
        "estimated_difficulty": 0.6,
        "knowledge_component": "Linear Equations"
    }

@router.get("/status")
def assessment_status(request):
    """Assessment app status endpoint"""
    return {
        "app": "assessment", 
        "status": "ready", 
        "description": "Question and assessment management with IRT integration",
        "features": [
            "Adaptive Assessment", 
            "Multiple Question Types", 
            "Response Tracking",
            "IRT Question Selection",
            "Theta Estimation",
            "BKT-IRT Integration"
        ],
        "algorithms": {
            "irt": {
                "status": "implemented",
                "version": "1.0",
                "features": ["question_selection", "theta_estimation", "bkt_integration"]
            }
        }
    }


# ============================================================================
# IRT (Item Response Theory) API Endpoints
# ============================================================================

# Initialize components
irt_engine = IRTEngine()
irt_selector = IRTAdaptiveSelector(irt_engine)

# ============================================================================
# MAIN ASSESSMENT ORCHESTRATION ENDPOINT
# ============================================================================

@router.post("/submit-answer", 
             response=AssessmentSubmissionResponseSchema,
             tags=["Assessment Orchestration"])
def submit_assessment_answer(request, payload: AssessmentSubmissionSchema):
    """
    Main assessment endpoint that orchestrates BKT, DKT, IRT, and SM-2.
    
    This is the core endpoint that ties all algorithms together:
    1. Saves interaction to database
    2. Updates BKT parameters
    3. Calls DKT service for hidden state update
    4. Updates fundamentals scores
    5. Creates/updates SRS cards if needed
    6. Selects next question via IRT
    7. Returns comprehensive state and next question
    """
    
    interaction_id = None
    
    try:
        with transaction.atomic():
            # Import models here to avoid circular imports
            from core.models import StudentProfile
            from assessment.models import AdaptiveQuestion, Interaction
            from practice.models import SRSCard
            from practice.sm2 import SM2Scheduler
            
            # Initialize results tracking
            algorithm_results = {
                "bkt": {"status": "pending"},
                "dkt": {"status": "pending"}, 
                "irt": {"status": "pending"},
                "sm2": {"status": "pending"}
            }
            
            # Step 1: Validate and get entities
            logger.info(f"Processing assessment submission for student {payload.student_id}")
            
            try:
                student_profile = StudentProfile.objects.select_for_update().get(id=payload.student_id)
            except StudentProfile.DoesNotExist:
                raise HttpError(404, f"Student {payload.student_id} not found")
            
            try:
                question = AdaptiveQuestion.objects.get(id=payload.question_id, is_active=True)
            except AdaptiveQuestion.DoesNotExist:
                raise HttpError(404, f"Question {payload.question_id} not found")
            
            # Determine if answer is correct
            is_correct = _evaluate_answer(question, payload.answer)
            
            # Step 2: Save interaction to database
            interaction = Interaction.objects.create(
                student=student_profile.user,  # Use the User, not StudentProfile
                question=question,
                student_answer=payload.answer,
                is_correct=is_correct,
                response_time=payload.response_time,
                session_id=uuid.uuid4(),  # Generate session ID
                attempt_number=payload.metadata.get('attempt_number', 1),
                hints_used=1 if payload.metadata.get('hint_used', False) else 0
            )
            interaction_id = str(interaction.id)
            logger.info(f"Created interaction {interaction_id}: correct={is_correct}")
            
            # Step 3: Update BKT parameters with level progression
            try:
                from student_model.bkt import BKTService
                
                # Use subject from payload or question for subject-specific progression
                subject = payload.subject or question.subject
                skill_id_with_subject = f"{subject}_{payload.skill_id}" if subject else payload.skill_id
                
                # Update BKT with level progression (subject-aware)
                updated_bkt_params, progression_info = BKTService.update_skill_bkt_with_progression(
                    user=student_profile.user,
                    skill_id=skill_id_with_subject,
                    is_correct=is_correct,
                    interaction_data={
                        'question_id': str(question.id),
                        'response_time': payload.response_time,
                        'timestamp': timezone.now().isoformat(),
                        'question_difficulty': question.difficulty,
                        'subject': subject,
                        'difficulty_level': question.difficulty_level,
                        'question_level': question.level
                    }
                )
                
                algorithm_results["bkt"] = {
                    "status": "success",
                    "new_mastery": updated_bkt_params.P_L,
                    "parameters": updated_bkt_params.to_dict(),
                    "level_progression": progression_info
                }
                
                # Add congratulations if level changed
                if progression_info.get('level_changed'):
                    recommendations.append(progression_info.get('congratulations_message', ''))
                elif progression_info.get('congratulations_message'):
                    recommendations.append(progression_info.get('congratulations_message'))
                
                logger.info(f"BKT updated with progression: mastery={updated_bkt_params.P_L:.3f}, "
                           f"level={progression_info.get('new_level', 'unchanged')}")
                
            except Exception as e:
                logger.error(f"BKT update failed: {e}")
                algorithm_results["bkt"] = {"status": "error", "error": str(e)}
            
            # Step 4: Call DKT service for hidden state update
            try:
                import urllib.request
                import urllib.parse
                
                # Prepare DKT request
                dkt_payload = {
                    "student_id": payload.student_id,
                    "skill_id": payload.skill_id,
                    "is_correct": is_correct,
                    "current_hidden_state": student_profile.dkt_hidden_state or [0.5] * 50
                }
                
                # Call DKT microservice using urllib
                data = json.dumps(dkt_payload).encode('utf-8')
                req = urllib.request.Request(
                    "http://localhost:8001/predict",
                    data=data,
                    headers={'Content-Type': 'application/json'},
                    method='POST'
                )
                
                with urllib.request.urlopen(req, timeout=5) as response:
                    dkt_result = json.loads(response.read().decode('utf-8'))
                
                # Update student's DKT hidden state
                student_profile.dkt_hidden_state = dkt_result.get("new_hidden_state", [0.5] * 50)
                
                algorithm_results["dkt"] = {
                    "status": "success",
                    "mastery_prediction": dkt_result.get("mastery_probability", 0.5),
                    "hidden_state_updated": True
                }
                logger.info(f"DKT updated: prediction={dkt_result.get('mastery_probability', 0.5):.3f}")
                    
            except Exception as e:
                logger.warning(f"DKT update failed (using BKT fallback): {e}")
                algorithm_results["dkt"] = {
                    "status": "fallback_to_bkt", 
                    "error": str(e),
                    "mastery_prediction": algorithm_results["bkt"].get("new_mastery", 0.5)
                }
            
            # Step 5: Update fundamentals scores
            try:
                # Update fundamentals based on question skill and correctness
                if payload.skill_id not in student_profile.fundamentals:
                    student_profile.fundamentals[payload.skill_id] = 0.5
                
                current_score = student_profile.fundamentals[payload.skill_id]
                
                # Simple exponential moving average update
                learning_rate = 0.1
                if is_correct:
                    new_score = current_score + learning_rate * (1.0 - current_score)
                else:
                    new_score = current_score - learning_rate * current_score * 0.5
                
                student_profile.fundamentals[payload.skill_id] = max(0.0, min(1.0, new_score))
                logger.info(f"Fundamentals updated: {payload.skill_id} {current_score:.3f} → {new_score:.3f}")
                
            except Exception as e:
                logger.error(f"Fundamentals update failed: {e}")
            
            # Step 6: Create/update SRS cards if needed
            srs_cards_updated = 0
            try:
                sm2_scheduler = SM2Scheduler()
                
                # Check if SRS card exists for this question
                srs_card, created = SRSCard.objects.get_or_create(
                    student=student_profile.user if hasattr(student_profile, 'user') else student_profile,
                    question=question,
                    defaults={
                        'stage': 'apprentice_1',
                        'ease_factor': 2.5,
                        'interval': 1,
                        'repetition': 0,
                        'due_date': timezone.now()
                    }
                )
                
                if created:
                    logger.info(f"Created new SRS card for question {question.id}")
                
                # Convert answer correctness to SM-2 quality score
                quality_score = 4 if is_correct else 1  # Good answer or wrong answer
                if is_correct and payload.response_time < 3.0:
                    quality_score = 5  # Perfect - fast and correct
                elif is_correct and payload.response_time > 10.0:
                    quality_score = 3  # Correct but slow
                
                # Update SRS card using SM-2
                sm2_result = sm2_scheduler.process_review(
                    card_id=str(srs_card.id),
                    quality=quality_score,
                    response_time=payload.response_time
                )
                
                if sm2_result.get('success'):
                    srs_cards_updated = 1
                    algorithm_results["sm2"] = {
                        "status": "success",
                        "card_updated": True,
                        "stage_changed": sm2_result.get('review_result', {}).get('stage_changed', False),
                        "new_interval": sm2_result.get('new_state', {}).get('interval', 1)
                    }
                    logger.info(f"SM-2 updated: quality={quality_score}, interval={sm2_result.get('new_state', {}).get('interval')}")
                
            except Exception as e:
                logger.error(f"SM-2 update failed: {e}")
                algorithm_results["sm2"] = {"status": "error", "error": str(e)}
            
            # Step 7: Select next question via IRT
            next_question_data = {
                "question_id": None,
                "question_text": None,
                "question_type": None,
                "difficulty": None,
                "skill_id": payload.skill_id,
                "selection_method": "none",
                "selection_reasoning": "No suitable questions found"
            }
            
            try:
                # Use IRT to select next question with level filtering
                selected_question = irt_selector.select_next_question(
                    student_id=payload.student_id,
                    skill_id=payload.skill_id,
                    use_bkt_integration=True,
                    level_based_filtering=True  # Enable level-based filtering
                )
                
                if selected_question:
                    next_question_data.update({
                        "question_id": str(selected_question.id),
                        "question_text": selected_question.question_text,
                        "question_type": selected_question.question_type,
                        "difficulty": getattr(selected_question, 'difficulty', 0.0),
                        "selection_method": "irt",
                        "selection_reasoning": "Selected using IRT based on current ability estimate"
                    })
                    
                    algorithm_results["irt"] = {
                        "status": "success",
                        "question_selected": True,
                        "selection_criteria": "optimal_difficulty_match"
                    }
                    logger.info(f"IRT selected next question: {selected_question.id}")
                else:
                    algorithm_results["irt"] = {
                        "status": "no_questions_available",
                        "reason": "No suitable questions found for current ability level"
                    }
                
            except Exception as e:
                logger.error(f"IRT question selection failed: {e}")
                algorithm_results["irt"] = {"status": "error", "error": str(e)}
            
            # Step 8: Save all updates to student profile
            student_profile.save()
            
            # Step 9: Calculate performance metrics
            total_interactions = Interaction.objects.filter(student=student_profile.user).count()
            recent_interactions = Interaction.objects.filter(
                student=student_profile.user,
                timestamp__gte=timezone.now() - timezone.timedelta(days=7)
            )
            recent_accuracy = (
                recent_interactions.filter(is_correct=True).count() / 
                max(1, recent_interactions.count())
            )
            
            performance_metrics = {
                "total_interactions": total_interactions,
                "recent_accuracy": recent_accuracy,
                "session_interactions": 1,  # This interaction
                "avg_response_time": payload.response_time,
                "current_streak": _calculate_current_streak(student_profile)
            }
            
            # Step 10: Generate recommendations
            recommendations = _generate_recommendations(
                student_profile, 
                algorithm_results, 
                performance_metrics
            )
            
            # Step 11: Build comprehensive response
            return {
                "success": True,
                "interaction_id": interaction_id,
                "was_correct": is_correct,
                "feedback": _generate_feedback(question, is_correct, payload.answer),
                "next_question": next_question_data,
                "updated_student_state": {
                    "student_id": payload.student_id,
                    "bkt_parameters": student_profile.bkt_parameters,
                    "dkt_hidden_state": student_profile.dkt_hidden_state,
                    "irt_theta": irt_engine.estimate_theta_from_bkt(
                        student_profile.bkt_parameters.get(payload.skill_id, {})
                    ) if student_profile.bkt_parameters.get(payload.skill_id) else 0.0,
                    "fundamentals": student_profile.fundamentals,
                    "srs_cards_updated": srs_cards_updated,
                    "total_interactions": total_interactions,
                    "session_progress": {
                        "questions_answered": 1,
                        "correct_answers": 1 if is_correct else 0,
                        "avg_response_time": payload.response_time
                    },
                    "level_progression": {
                        "current_level": student_profile.current_level.get(payload.skill_id, 0),
                        "unlocked_levels": student_profile.level_lock_status.get(payload.skill_id, [0]),
                        "consecutive_correct": student_profile.consecutive_correct_count.get(
                            f"{payload.skill_id}_level_{student_profile.current_level.get(payload.skill_id, 0)}", 0
                        ),
                        "mastery_threshold": student_profile.mastery_threshold
                    }
                },
                "algorithm_results": algorithm_results,
                "performance_metrics": performance_metrics,
                "recommendations": recommendations
            }
            
    except HttpError:
        raise
    except Exception as e:
        logger.error(f"Assessment submission failed: {e}")
        
        # Rollback will happen automatically due to transaction.atomic()
        raise HttpError(500, f"Assessment processing failed: {str(e)}")


# Helper functions for assessment orchestration

def _evaluate_answer(question, student_answer: str) -> bool:
    """Evaluate if student answer is correct"""
    correct_answer = question.correct_answer.strip().lower()
    student_answer = student_answer.strip().lower()
    
    # Simple exact match for now - can be enhanced with fuzzy matching
    return student_answer == correct_answer

def _generate_feedback(question, is_correct: bool, student_answer: str) -> str:
    """Generate feedback for the student"""
    if is_correct:
        return "Correct! Well done."
    else:
        explanation = getattr(question, 'explanation', '')
        feedback = f"Incorrect. The correct answer is: {question.correct_answer}"
        if explanation:
            feedback += f" Explanation: {explanation}"
        return feedback

def _calculate_current_streak(student_profile) -> int:
    """Calculate current correct answer streak"""
    try:
        from assessment.models import Interaction
        recent_interactions = Interaction.objects.filter(
            student=student_profile.user
        ).order_by('-timestamp')[:10]
        
        streak = 0
        for interaction in recent_interactions:
            if interaction.is_correct:
                streak += 1
            else:
                break
        return streak
    except:
        return 0

def _generate_recommendations(student_profile, algorithm_results: Dict, performance_metrics: Dict) -> List[str]:
    """Generate personalized recommendations"""
    recommendations = []
    
    # BKT-based recommendations
    bkt_result = algorithm_results.get("bkt", {})
    if bkt_result.get("status") == "success":
        mastery = bkt_result.get("new_mastery", 0.5)
        if mastery > 0.8:
            recommendations.append("Great progress! You've mastered this skill.")
        elif mastery < 0.3:
            recommendations.append("This topic needs more practice. Try some easier questions first.")
        else:
            recommendations.append("You're making good progress. Keep practicing!")
    
    # Performance-based recommendations
    if performance_metrics.get("recent_accuracy", 0) < 0.5:
        recommendations.append("Consider reviewing the fundamentals before continuing.")
    
    if performance_metrics.get("avg_response_time", 0) > 30:
        recommendations.append("Take your time to understand each question thoroughly.")
    
    # SM-2 based recommendations
    sm2_result = algorithm_results.get("sm2", {})
    if sm2_result.get("stage_changed"):
        recommendations.append("You've advanced to the next spaced repetition stage!")
    
    return recommendations[:3]  # Limit to 3 recommendations

@router.post("/irt/select-question", 
             response=IRTQuestionResponseSchema,
             tags=["IRT Algorithm"])
def irt_select_question(request, payload: IRTQuestionSelectionSchema):
    """
    Select optimal question using IRT based on student ability
    
    This endpoint uses Item Response Theory to select the best question
    for a student based on their estimated ability (theta) and question
    difficulty parameters.
    """
    try:
        # Select question using IRT
        selected_question = irt_selector.select_next_question(
            student_id=payload.student_id,
            skill_id=payload.skill_id,
            use_bkt_integration=payload.use_bkt_integration
        )
        
        if not selected_question:
            return {
                "question_id": None,
                "question_text": None,
                "difficulty": 0.0,
                "estimated_theta": 0.0,
                "selection_reasoning": "No suitable questions available",
                "irt_probability": None,
                "bkt_integration_used": payload.use_bkt_integration
            }
        
        # Estimate student's current theta
        if payload.use_bkt_integration:
            try:
                from core.models import StudentProfile
                student = StudentProfile.objects.get(id=payload.student_id)
                bkt_params = student.bkt_parameters.get(payload.skill_id, {}) if payload.skill_id else {}
                if bkt_params:
                    estimated_theta = irt_engine.estimate_theta_from_bkt(bkt_params)
                else:
                    estimated_theta = irt_selector._estimate_theta_from_history(student)
            except:
                estimated_theta = 0.0
        else:
            estimated_theta = 0.0
        
        # Calculate probability of correct response
        question_difficulty = getattr(selected_question, 'difficulty', 0.0)
        irt_probability = irt_engine.calculate_question_probability(
            estimated_theta, 
            question_difficulty
        )
        
        # Generate selection reasoning
        difficulty_distance = abs(estimated_theta - question_difficulty)
        if difficulty_distance < 0.5:
            reasoning = f"Optimal match: question difficulty ({question_difficulty:.2f}) closely matches student ability ({estimated_theta:.2f})"
        elif question_difficulty > estimated_theta:
            reasoning = f"Challenging question: difficulty ({question_difficulty:.2f}) slightly above ability ({estimated_theta:.2f})"
        else:
            reasoning = f"Confidence building: difficulty ({question_difficulty:.2f}) slightly below ability ({estimated_theta:.2f})"
        
        return {
            "question_id": str(getattr(selected_question, 'id', '')),
            "question_text": getattr(selected_question, 'question_text', '')[:100] + "...",
            "difficulty": question_difficulty,
            "estimated_theta": estimated_theta,
            "selection_reasoning": reasoning,
            "irt_probability": irt_probability,
            "bkt_integration_used": payload.use_bkt_integration
        }
        
    except Exception as e:
        logger.error(f"Error in IRT question selection: {e}")
        raise HttpError(500, f"IRT selection error: {str(e)}")


@router.post("/irt/update-theta",
             response=IRTThetaResponseSchema,
             tags=["IRT Algorithm"])
def irt_update_theta(request, payload: IRTThetaUpdateSchema):
    """
    Update student's theta (ability) based on response to question
    
    This endpoint updates the student's estimated ability using IRT
    based on their response to a question.
    """
    try:
        # Get current theta
        if payload.use_question_difficulty:
            try:
                from core.models import StudentProfile
                from assessment.models import AdaptiveQuestion
                
                student = StudentProfile.objects.get(id=payload.student_id)
                question = AdaptiveQuestion.objects.get(id=payload.question_id)
                
                # Get current theta from BKT if available
                bkt_params = student.bkt_parameters.get('default', {})
                if bkt_params:
                    current_theta = irt_engine.estimate_theta_from_bkt(bkt_params)
                else:
                    current_theta = irt_selector._estimate_theta_from_history(student)
                
                # Update theta based on response
                new_theta = irt_engine.update_theta_simple(
                    current_theta=current_theta,
                    is_correct=payload.is_correct,
                    question_difficulty=question.difficulty
                )
                
                question_difficulty = question.difficulty
                
            except Exception as e:
                logger.warning(f"Could not get question difficulty: {e}")
                current_theta = 0.0
                new_theta = irt_engine.update_theta_simple(
                    current_theta=current_theta,
                    is_correct=payload.is_correct
                )
                question_difficulty = None
        else:
            current_theta = 0.0
            new_theta = irt_engine.update_theta_simple(
                current_theta=current_theta,
                is_correct=payload.is_correct
            )
            question_difficulty = None
        
        theta_change = new_theta - current_theta
        
        return {
            "student_id": payload.student_id,
            "previous_theta": current_theta,
            "new_theta": new_theta,
            "theta_change": theta_change,
            "question_difficulty": question_difficulty,
            "updated_at": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error in theta update: {e}")
        raise HttpError(500, f"Theta update error: {str(e)}")


@router.get("/irt/analyze/{student_id}",
            response=IRTAnalysisSchema,
            tags=["IRT Algorithm"])
def irt_analyze_student(request, student_id: str, skill_id: Optional[str] = None):
    """
    Analyze student's current ability using IRT
    
    Provides comprehensive analysis of student's theta (ability) including
    source of estimation, ability level, and recommendations.
    """
    try:
        from core.models import StudentProfile
        from assessment.models import Interaction
        
        # Initialize variables
        current_theta = 0.0
        theta_source = "default"
        confidence = 0.5
        analysis_details = {}
        
        try:
            student = StudentProfile.objects.get(id=student_id)
            
            # Try BKT integration first
            bkt_params = student.bkt_parameters.get(skill_id or 'default', {})
            if bkt_params and 'P_L' in bkt_params:
                current_theta = irt_engine.estimate_theta_from_bkt(bkt_params)
                theta_source = "bkt_integration"
                confidence = bkt_params.get('P_L', 0.5)
                analysis_details['bkt_mastery_probability'] = bkt_params.get('P_L')
                analysis_details['bkt_parameters'] = bkt_params
            else:
                # Fall back to interaction history
                current_theta = irt_selector._estimate_theta_from_history(student)
                theta_source = "interaction_history"
                
                # Calculate confidence based on number of interactions
                interaction_count = Interaction.objects.filter(
                    student=student.user if hasattr(student, 'user') else student
                ).count()
                confidence = min(0.9, 0.3 + (interaction_count * 0.05))
                analysis_details['interaction_count'] = interaction_count
        
        except Exception as e:
            logger.warning(f"Could not get student data: {e}")
            analysis_details['error'] = str(e)
        
        # Determine ability level
        if current_theta < -1.0:
            ability_level = "low"
        elif current_theta > 1.0:
            ability_level = "high"
        else:
            ability_level = "medium"
        
        # Recommend question difficulty (slightly above current ability)
        recommended_difficulty = min(3.0, current_theta + 0.3)
        
        # Add probability scale conversion
        probability_equivalent = irt_engine.calculate_question_probability(
            theta=current_theta,
            question_difficulty=0.0  # Average difficulty
        )
        analysis_details['probability_equivalent'] = probability_equivalent
        analysis_details['theta_range'] = {"min": -3.0, "max": 3.0}
        
        return {
            "student_id": student_id,
            "current_theta": current_theta,
            "theta_source": theta_source,
            "ability_level": ability_level,
            "recommended_difficulty": recommended_difficulty,
            "confidence": confidence,
            "analysis_details": analysis_details
        }
        
    except Exception as e:
        logger.error(f"Error in IRT analysis: {e}")
        raise HttpError(500, f"IRT analysis error: {str(e)}")


@router.get("/irt/question-bank-analysis", tags=["IRT Algorithm"])
def irt_analyze_question_bank(request, skill_id: Optional[str] = None):
    """
    Analyze question bank difficulty distribution for IRT optimization
    
    Provides statistics about question difficulties to help optimize
    the question bank for adaptive testing.
    """
    try:
        from assessment.models import AdaptiveQuestion
        
        # Get questions
        questions = AdaptiveQuestion.objects.filter(is_active=True)
        if skill_id:
            questions = questions.filter(skill_id=skill_id)
        
        if not questions.exists():
            return {
                "total_questions": 0,
                "difficulty_distribution": {},
                "recommendations": ["Add more questions to the question bank"]
            }
        
        # Analyze difficulty distribution
        difficulties = [q.difficulty for q in questions]
        difficulty_stats = {
            "count": len(difficulties),
            "min": min(difficulties),
            "max": max(difficulties),
            "average": sum(difficulties) / len(difficulties),
            "range": max(difficulties) - min(difficulties)
        }
        
        # Count questions in difficulty bands
        difficulty_bands = {
            "very_easy": len([d for d in difficulties if d < -1.5]),
            "easy": len([d for d in difficulties if -1.5 <= d < -0.5]),
            "medium": len([d for d in difficulties if -0.5 <= d < 0.5]),
            "hard": len([d for d in difficulties if 0.5 <= d < 1.5]),
            "very_hard": len([d for d in difficulties if d >= 1.5])
        }
        
        # Generate recommendations
        recommendations = []
        total_questions = len(difficulties)
        
        if difficulty_bands["very_easy"] / total_questions < 0.1:
            recommendations.append("Add more very easy questions for struggling students")
        if difficulty_bands["medium"] / total_questions < 0.3:
            recommendations.append("Add more medium difficulty questions for balanced assessment")
        if difficulty_bands["very_hard"] / total_questions < 0.1:
            recommendations.append("Add more challenging questions for advanced students")
        if difficulty_stats["range"] < 4.0:
            recommendations.append("Expand difficulty range to cover full ability spectrum")
        
        return {
            "total_questions": total_questions,
            "skill_id": skill_id,
            "difficulty_stats": difficulty_stats,
            "difficulty_distribution": difficulty_bands,
            "recommendations": recommendations
        }
        
    except Exception as e:
        logger.error(f"Error in question bank analysis: {e}")
        raise HttpError(500, f"Question bank analysis error: {str(e)}")


@router.get("/irt/compare-algorithms/{student_id}", tags=["Algorithm Comparison"])
def irt_compare_with_bkt_dkt(request, student_id: str, skill_id: Optional[str] = None):
    """
    Compare IRT theta estimation with BKT and DKT predictions
    
    Shows how different algorithms estimate student ability and provides
    recommendations for which approach to use.
    """
    try:
        from core.models import StudentProfile
        
        # Initialize results
        results = {
            "student_id": student_id,
            "skill_id": skill_id,
            "estimations": {},
            "comparison": {},
            "recommendations": {}
        }
        
        try:
            student = StudentProfile.objects.get(id=student_id)
            
            # IRT estimation
            irt_theta = irt_selector._estimate_theta_from_history(student)
            irt_probability = irt_engine.calculate_question_probability(irt_theta, 0.0)
            results["estimations"]["irt"] = {
                "theta": irt_theta,
                "probability_equivalent": irt_probability,
                "method": "interaction_history"
            }
            
            # BKT estimation
            bkt_params = student.bkt_parameters.get(skill_id or 'default', {})
            if bkt_params:
                bkt_theta = irt_engine.estimate_theta_from_bkt(bkt_params)
                bkt_probability = bkt_params.get('P_L', 0.5)
                results["estimations"]["bkt"] = {
                    "theta": bkt_theta,
                    "probability_equivalent": bkt_probability,
                    "method": "bayesian_parameters"
                }
                
                # Compare IRT and BKT
                theta_difference = abs(irt_theta - bkt_theta)
                prob_difference = abs(irt_probability - bkt_probability)
                
                results["comparison"]["irt_vs_bkt"] = {
                    "theta_difference": theta_difference,
                    "probability_difference": prob_difference,
                    "agreement": "high" if theta_difference < 0.5 else "low"
                }
            
            # DKT estimation (if available)
            if hasattr(student, 'dkt_hidden_state') and student.dkt_hidden_state:
                # Mock DKT conversion for now
                dkt_probability = 0.6  # This would come from DKT service
                dkt_theta = irt_engine.estimate_theta_from_bkt({'P_L': dkt_probability})
                results["estimations"]["dkt"] = {
                    "theta": dkt_theta,
                    "probability_equivalent": dkt_probability,
                    "method": "neural_network"
                }
            
            # Generate recommendations
            if len(results["estimations"]) > 1:
                if results["comparison"].get("irt_vs_bkt", {}).get("agreement") == "high":
                    results["recommendations"]["algorithm"] = "irt_with_bkt"
                    results["recommendations"]["reason"] = "IRT and BKT show high agreement"
                else:
                    results["recommendations"]["algorithm"] = "ensemble"
                    results["recommendations"]["reason"] = "Algorithms disagree, use ensemble approach"
            else:
                results["recommendations"]["algorithm"] = "irt_only"
                results["recommendations"]["reason"] = "Limited data, use IRT with interaction history"
        
        except Exception as e:
            results["error"] = str(e)
        
        return results
        
    except Exception as e:
        logger.error(f"Error in algorithm comparison: {e}")
        raise HttpError(500, f"Algorithm comparison error: {str(e)}")


# ============================================================================
# Subject-Specific Question Endpoints
# ============================================================================

@router.post("/subject-questions")
def get_subject_questions(request, payload: SubjectQuestionRequestSchema):
    """
    Get questions for a specific subject with subject-wise level progression.
    Supports competitive exam dataset with proper difficulty mapping.
    """
    try:
        from core.models import StudentProfile
        from assessment.models import AdaptiveQuestion
        from django.db.models import Q
        
        # Get student profile for level-based filtering
        try:
            student_profile = StudentProfile.objects.get(id=payload.student_id)
        except StudentProfile.DoesNotExist:
            raise HttpError(404, f"Student {payload.student_id} not found")
        
        # Build query filters
        filters = Q(subject=payload.subject, is_active=True)
        
        # Add difficulty filter if specified
        if payload.difficulty_level:
            filters &= Q(difficulty_level=payload.difficulty_level)
        
        # Add level filter if specified
        if payload.level:
            filters &= Q(level=payload.level)
        else:
            # Filter by student's current level for this subject
            # For now, use general level, but this could be subject-specific
            max_level = min(student_profile.current_level + 1, 4)  # Allow one level above
            filters &= Q(level__lte=max_level)
        
        # Get questions
        questions = AdaptiveQuestion.objects.filter(filters).order_by('?')[:payload.count]
        
        # Format response
        question_list = []
        for question in questions:
            question_data = {
                "id": str(question.id),
                "question_text": question.question_text,
                "question_type": question.question_type,
                "options": question.formatted_options,
                "subject": question.subject,
                "difficulty_level": question.difficulty_level,
                "level": question.level,
                "estimated_time": question.estimated_time_seconds,
                "skill_id": question.skill_id,
                "tags": question.tags.split(',') if question.tags else []
            }
            question_list.append(question_data)
        
        return {
            "success": True,
            "subject": payload.subject,
            "student_level": student_profile.current_level,
            "requested_count": payload.count,
            "returned_count": len(question_list),
            "questions": question_list,
            "filters_applied": {
                "subject": payload.subject,
                "difficulty_level": payload.difficulty_level,
                "max_level": payload.level or max_level
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting subject questions: {e}")
        raise HttpError(500, f"Subject questions error: {str(e)}")


@router.get("/subjects/{subject}/stats")
def get_subject_stats(request, subject: str, student_id: str = None):
    """
    Get statistics for a specific subject, optionally filtered by student.
    Useful for tracking subject-wise progress.
    """
    try:
        from core.models import StudentProfile
        from assessment.models import AdaptiveQuestion, Interaction
        from django.db.models import Count, Avg, Q
        
        # Base query for subject questions
        subject_questions = AdaptiveQuestion.objects.filter(subject=subject, is_active=True)
        
        # Overall subject statistics
        stats = {
            "subject": subject,
            "total_questions": subject_questions.count(),
            "difficulty_breakdown": {},
            "level_breakdown": {},
        }
        
        # Difficulty breakdown
        difficulty_counts = subject_questions.values('difficulty_level').annotate(count=Count('id'))
        for item in difficulty_counts:
            stats["difficulty_breakdown"][item['difficulty_level']] = item['count']
        
        # Level breakdown
        level_counts = subject_questions.values('level').annotate(count=Count('id'))
        for item in level_counts:
            stats["level_breakdown"][f"level_{item['level']}"] = item['count']
        
        # Student-specific statistics if provided
        if student_id:
            try:
                student_profile = StudentProfile.objects.get(id=student_id)
                
                # Get student interactions for this subject
                student_interactions = Interaction.objects.filter(
                    student=student_profile.user,
                    question__subject=subject
                )
                
                if student_interactions.exists():
                    stats["student_progress"] = {
                        "total_attempted": student_interactions.count(),
                        "total_correct": student_interactions.filter(is_correct=True).count(),
                        "accuracy_rate": student_interactions.filter(is_correct=True).count() / student_interactions.count(),
                        "average_response_time": student_interactions.aggregate(avg_time=Avg('response_time'))['avg_time'] or 0,
                        "current_level": student_profile.current_level,
                        "mastery_threshold": student_profile.mastery_threshold
                    }
                    
                    # Difficulty-wise performance
                    difficulty_performance = {}
                    for difficulty in ['very_easy', 'easy', 'moderate', 'difficult']:
                        diff_interactions = student_interactions.filter(question__difficulty_level=difficulty)
                        if diff_interactions.exists():
                            difficulty_performance[difficulty] = {
                                "attempted": diff_interactions.count(),
                                "correct": diff_interactions.filter(is_correct=True).count(),
                                "accuracy": diff_interactions.filter(is_correct=True).count() / diff_interactions.count()
                            }
                    
                    stats["student_progress"]["difficulty_performance"] = difficulty_performance
                else:
                    stats["student_progress"] = {
                        "total_attempted": 0,
                        "message": "No interactions found for this subject"
                    }
                    
            except StudentProfile.DoesNotExist:
                stats["student_error"] = f"Student {student_id} not found"
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting subject stats: {e}")
        raise HttpError(500, f"Subject stats error: {str(e)}")


@router.get("/subjects")
def list_available_subjects(request):
    """
    List all available subjects with question counts.
    """
    try:
        from assessment.models import AdaptiveQuestion
        from django.db.models import Count
        
        # Get subject breakdown
        subjects = AdaptiveQuestion.objects.filter(is_active=True).values('subject').annotate(
            question_count=Count('id')
        ).order_by('subject')
        
        subject_list = []
        for subject_info in subjects:
            subject_list.append({
                "subject_code": subject_info['subject'],
                "subject_name": subject_info['subject'].replace('_', ' ').title(),
                "question_count": subject_info['question_count']
            })
        
        return {
            "success": True,
            "total_subjects": len(subject_list),
            "subjects": subject_list
        }
        
    except Exception as e:
        logger.error(f"Error listing subjects: {e}")
        raise HttpError(500, f"List subjects error: {str(e)}")