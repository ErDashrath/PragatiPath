"""
Enhanced Competitive Exam API v2 - With AI Integration
Supports EXAM/PRACTICE modes and post-exam analysis via LangGraph + Gemini
"""

from ninja import Router
from ninja import Schema
from ninja.errors import HttpError
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import logging
import uuid
import asyncio
from django.db import transaction
from django.utils import timezone
from asgiref.sync import sync_to_async
import json

# AI Integration
from .working_ai_service import get_working_ai_service

logger = logging.getLogger(__name__)

router = Router()

# ============================================================================
# Enhanced API v2 Schemas with Assessment Modes
# ============================================================================

class AssessmentModeEnum(str, Enum):
    EXAM = "EXAM"
    PRACTICE = "PRACTICE"

class StartEnhancedAssessmentSchema(Schema):
    """Schema for starting assessment with mode selection"""
    student_id: str
    subject: str
    assessment_mode: AssessmentModeEnum = AssessmentModeEnum.EXAM
    preferred_difficulty: Optional[str] = None

class StartEnhancedAssessmentResponseSchema(Schema):
    """Enhanced response with mode-specific features"""
    success: bool
    session_id: str
    assessment_mode: str
    subject: str
    current_difficulty: str
    student_level: int
    next_question: Optional[Dict[str, Any]]
    mode_features: Dict[str, Any]  # Different features per mode

class EnhancedSubmitAnswerSchema(Schema):
    """Enhanced answer submission with mode tracking"""
    student_id: str
    session_id: str
    question_id: str
    answer: str
    response_time: float
    assessment_mode: AssessmentModeEnum
    hints_used: int = 0

class CompleteExamSchema(Schema):
    """Schema for marking exam as complete"""
    student_id: str
    session_id: str
    request_ai_analysis: bool = True

class CompleteExamResponseSchema(Schema):
    """Response for exam completion"""
    success: bool
    session_id: str
    final_stats: Dict[str, Any]
    ai_analysis_requested: bool
    analysis_availability: str

class HintRequestSchema(Schema):
    """Schema for requesting hints in practice mode"""
    student_id: str
    session_id: str
    question_id: str
    hint_level: int = 1  # 1=subtle, 2=specific, 3=detailed

class HintResponseSchema(Schema):
    """Response with hint for practice mode"""
    success: bool
    hint: str
    hint_level: int
    remaining_hints: int
    can_request_more_hints: bool

class PracticeExplanationSchema(Schema):
    """Schema for requesting explanation in practice mode"""
    student_id: str
    session_id: str
    question_id: str
    student_answer: str

class PracticeExplanationResponseSchema(Schema):
    """Response with detailed explanation"""
    success: bool
    explanation: str  # Simple string explanation for compatibility
    detailed_explanation: Dict[str, Any]  # Full AI response
    is_correct: bool
    next_question: Optional[Dict[str, Any]]

class AIAnalysisResponseSchema(Schema):
    """Response schema for AI analysis"""
    success: bool
    session_id: str
    analysis: Dict[str, Any]
    generated_at: str

class ExplanationsResponseSchema(Schema):
    """Response for getting explanations of all wrong answers"""
    success: bool
    session_id: str
    explanations: List[Dict[str, Any]]
    total_wrong_answers: int

# ============================================================================
# Enhanced API v2 Endpoints - With Assessment Modes
# ============================================================================

@router.post("/v2/assessment/start", response=StartEnhancedAssessmentResponseSchema)
def start_enhanced_assessment(request, payload: StartEnhancedAssessmentSchema):
    """
    Start assessment with mode selection (EXAM or PRACTICE)
    EXAM mode: No hints, no AI help during questions
    PRACTICE mode: Hints available, explanations after each question
    """
    try:
        from core.models import StudentProfile
        from assessment.models import AdaptiveQuestion, ExamSession
        
        # Get student profile
        try:
            student_profile = StudentProfile.objects.get(id=payload.student_id)
        except StudentProfile.DoesNotExist:
            raise HttpError(404, f"Student {payload.student_id} not found")
        
        # Get subject progress
        subject_progress = student_profile.subject_progress.get(payload.subject, {
            'current_difficulty': 'very_easy',
            'level': 1,
            'mastery_score': 0.0,
            'consecutive_correct': 0,
            'questions_attempted': 0,
            'questions_correct': 0,
            'unlocked_difficulties': ['very_easy']
        })
        
        # Determine current difficulty
        current_difficulty = payload.preferred_difficulty or subject_progress['current_difficulty']
        if current_difficulty not in subject_progress['unlocked_difficulties']:
            current_difficulty = subject_progress['current_difficulty']
        
        with transaction.atomic():
            # Create exam session
            exam_session = ExamSession.objects.create(
                student=student_profile.user,
                subject=payload.subject,
                assessment_mode=payload.assessment_mode,
                current_difficulty=current_difficulty,
                initial_mastery_score=subject_progress['mastery_score']
            )
            
            # Get first question
            available_questions = AdaptiveQuestion.objects.filter(
                subject=payload.subject,
                difficulty_level=current_difficulty,
                is_active=True
            ).order_by('?')[:1]
            
            next_question = None
            if available_questions:
                question = available_questions[0]
                next_question = {
                    "id": str(question.id),
                    "question_text": question.question_text,
                    "options": question.formatted_options,
                    "difficulty": current_difficulty,
                    "estimated_time": question.estimated_time_seconds,
                    "question_number": 1
                }
            
            # Mode-specific features
            mode_features = {
                "hints_available": payload.assessment_mode == AssessmentModeEnum.PRACTICE,
                "immediate_explanations": payload.assessment_mode == AssessmentModeEnum.PRACTICE,
                "ai_assistance": payload.assessment_mode == AssessmentModeEnum.PRACTICE,
                "post_exam_analysis": True,  # Available for both modes after completion
                "mode_description": get_mode_description(payload.assessment_mode)
            }
            
            return StartEnhancedAssessmentResponseSchema(
                success=True,
                session_id=str(exam_session.id),
                assessment_mode=payload.assessment_mode,
                subject=payload.subject,
                current_difficulty=current_difficulty,
                student_level=subject_progress['level'],
                next_question=next_question,
                mode_features=mode_features
            )
            
    except Exception as e:
        logger.error(f"Error starting enhanced assessment: {e}")
        raise HttpError(500, f"Failed to start assessment: {str(e)}")

@router.post("/v2/assessment/submit-answer")
def submit_enhanced_answer(request, payload: EnhancedSubmitAnswerSchema):
    """
    Submit answer with mode-aware processing
    EXAM mode: Standard processing, no AI feedback
    PRACTICE mode: Immediate AI feedback available
    """
    try:
        from core.models import StudentProfile
        from assessment.models import AdaptiveQuestion, Interaction, ExamSession
        from student_model.bkt import BKTService
        
        with transaction.atomic():
            # Get required objects
            try:
                student_profile = StudentProfile.objects.get(id=payload.student_id)
                question = AdaptiveQuestion.objects.get(id=payload.question_id)
                exam_session = ExamSession.objects.get(id=payload.session_id)
            except (StudentProfile.DoesNotExist, AdaptiveQuestion.DoesNotExist, ExamSession.DoesNotExist) as e:
                raise HttpError(404, str(e))
            
            # Validate session is active
            if exam_session.status != 'ACTIVE':
                raise HttpError(400, "Session is not active")
            
            # Check if answer is correct
            is_correct = payload.answer.lower() == question.answer.lower()
            correct_answer = f"{question.answer.upper()}: {question.formatted_options[question.answer]}"
            
            # Create interaction record
            interaction = Interaction.objects.create(
                student=student_profile.user,
                question=question,
                student_answer=payload.answer,
                is_correct=is_correct,
                response_time=payload.response_time,
                session_id=payload.session_id,
                assessment_mode=payload.assessment_mode,
                hints_used=payload.hints_used,
                attempt_number=1
            )
            
            # Update BKT
            skill_id = f"{exam_session.subject}_{exam_session.current_difficulty}"
            updated_bkt_params, bkt_progression = BKTService.update_skill_bkt_with_progression(
                user=student_profile.user,
                skill_id=skill_id,
                is_correct=is_correct,
                interaction_data={
                    'question_id': str(question.id),
                    'response_time': payload.response_time,
                    'subject': exam_session.subject,
                    'difficulty': exam_session.current_difficulty,
                    'timestamp': timezone.now().isoformat()
                }
            )
            
            # Update exam session stats
            exam_session.questions_attempted += 1
            if is_correct:
                exam_session.questions_correct += 1
            exam_session.total_time_spent += payload.response_time
            exam_session.final_mastery_score = updated_bkt_params.P_L
            exam_session.save()
            
            # Get next question if available
            next_question = get_next_question_for_session(exam_session)
            
            # Mode-specific response
            response_data = {
                "success": True,
                "was_correct": is_correct,
                "correct_answer": correct_answer,
                "mastery_score": updated_bkt_params.P_L,
                "session_stats": {
                    "questions_attempted": exam_session.questions_attempted,
                    "questions_correct": exam_session.questions_correct,
                    "accuracy_rate": exam_session.accuracy_rate,
                    "time_spent_minutes": exam_session.duration_minutes
                },
                "next_question": next_question
            }
            
            # For PRACTICE mode, add immediate feedback option
            if payload.assessment_mode == AssessmentModeEnum.PRACTICE:
                response_data["immediate_explanation_available"] = True
                response_data["hint_usage"] = {
                    "hints_used": payload.hints_used,
                    "explanation_recommended": not is_correct
                }
            
            return response_data
            
    except Exception as e:
        logger.error(f"Error submitting enhanced answer: {e}")
        raise HttpError(500, f"Failed to submit answer: {str(e)}")

# ============================================================================
# Post-Exam Analysis Endpoints
# ============================================================================

@router.post("/v2/exam/complete", response=CompleteExamResponseSchema)
def complete_exam(request, payload: CompleteExamSchema):
    """
    Mark exam as complete and optionally request AI analysis
    Only available for completed exams - triggers post-exam analysis
    """
    try:
        from assessment.models import ExamSession
        
        try:
            exam_session = ExamSession.objects.get(id=payload.session_id)
        except ExamSession.DoesNotExist:
            raise HttpError(404, "Exam session not found")
        
        # Validate session belongs to student via StudentProfile
        try:
            from core.models import StudentProfile
            student_profile = StudentProfile.objects.get(id=payload.student_id)
            if exam_session.student != student_profile.user:
                logger.warning(f"Unauthorized access - session user: {exam_session.student.id}, profile user: {student_profile.user.id}")
                raise HttpError(403, "Unauthorized access to exam session")
        except StudentProfile.DoesNotExist:
            logger.warning(f"Student profile not found: {payload.student_id}")
            raise HttpError(404, f"Student {payload.student_id} not found")
        
        # Mark as completed
        exam_session.mark_completed()
        
        # Request AI analysis if requested
        if payload.request_ai_analysis:
            exam_session.ai_analysis_requested = True
            exam_session.save()
        
        # Calculate final statistics
        final_stats = {
            "questions_attempted": exam_session.questions_attempted,
            "questions_correct": exam_session.questions_correct,
            "accuracy_rate": exam_session.accuracy_rate,
            "time_spent_minutes": exam_session.duration_minutes,
            "subject": exam_session.subject,
            "final_mastery_score": exam_session.final_mastery_score,
            "mastery_improvement": exam_session.final_mastery_score - exam_session.initial_mastery_score
        }
        
        return CompleteExamResponseSchema(
            success=True,
            session_id=payload.session_id,
            final_stats=final_stats,
            ai_analysis_requested=payload.request_ai_analysis,
            analysis_availability="Available in a few minutes" if payload.request_ai_analysis else "Not requested"
        )
        
    except Exception as e:
        logger.error(f"Error completing exam: {e}")
        raise HttpError(500, f"Failed to complete exam: {str(e)}")

@router.get("/v2/exam/{session_id}/analysis", response=AIAnalysisResponseSchema)
def get_exam_analysis(request, session_id: str):
    """
    Get comprehensive AI analysis for completed exam
    Uses LangGraph + Gemini for detailed analysis
    """
    try:
        from assessment.models import ExamSession, Interaction, AdaptiveQuestion
        
        try:
            exam_session = ExamSession.objects.get(id=session_id)
        except ExamSession.DoesNotExist:
            raise HttpError(404, "Exam session not found")
        
        # Check if session is completed
        if exam_session.status != 'COMPLETED':
            raise HttpError(400, "Analysis only available for completed exams")
        
        # Check if analysis already exists
        if exam_session.ai_analysis_completed and exam_session.ai_analysis_data:
            return AIAnalysisResponseSchema(
                success=True,
                session_id=session_id,
                analysis=exam_session.ai_analysis_data,
                generated_at=exam_session.updated_at.isoformat()
            )
        
        # Generate new analysis using working AI service
        ai_service = get_working_ai_service()
        
        # Prepare exam session data
        interactions = Interaction.objects.filter(session_id=session_id).select_related('question')
        questions_data = []
        
        for interaction in interactions:
            questions_data.append({
                'question_id': str(interaction.question.id),
                'question_text': interaction.question.question_text,
                'options': interaction.question.formatted_options,
                'student_answer': interaction.student_answer,
                'correct_answer': interaction.question.answer,
                'is_correct': interaction.is_correct,
                'difficulty': interaction.question.difficulty_level,
                'subject': interaction.question.subject,
                'response_time': interaction.response_time,
                'hints_used': interaction.hints_used
            })
        
        exam_session_data = {
            'session_id': session_id,
            'student_id': str(exam_session.student.id),
            'subject': exam_session.subject,
            'questions_data': questions_data,
            'overall_score': exam_session.accuracy_rate,
            'time_spent': exam_session.duration_minutes,
            'mastery_score': exam_session.final_mastery_score,
            'assessment_mode': exam_session.assessment_mode,
            'bkt_data': {
                'initial_mastery': exam_session.initial_mastery_score,
                'final_mastery': exam_session.final_mastery_score,
                'improvement': exam_session.final_mastery_score - exam_session.initial_mastery_score
            }
        }
        
        # Run AI analysis using working service
        analysis_result = ai_service.analyze_exam_session(exam_session_data)
        
        # Store analysis results
        exam_session.ai_analysis_data = analysis_result
        exam_session.ai_analysis_completed = True
        exam_session.save()
        
        return AIAnalysisResponseSchema(
            success=True,
            session_id=session_id,
            analysis=analysis_result,
            generated_at=timezone.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error generating exam analysis: {e}")
        raise HttpError(500, f"Failed to generate analysis: {str(e)}")

@router.get("/v2/exam/{session_id}/explanations", response=ExplanationsResponseSchema)
async def get_exam_explanations(request, session_id: str):
    """
    Get detailed explanations for all incorrect answers
    Provides comprehensive explanations via Gemini AI
    """
    try:
        from assessment.models import ExamSession, Interaction
        from .ai_analysis import GeminiAIService
        
        try:
            exam_session = ExamSession.objects.get(id=session_id)
        except ExamSession.DoesNotExist:
            raise HttpError(404, "Exam session not found")
        
        # Check if session is completed
        if exam_session.status != 'COMPLETED':
            raise HttpError(400, "Explanations only available for completed exams")
        
        # Get all incorrect interactions
        incorrect_interactions = Interaction.objects.filter(
            session_id=session_id,
            is_correct=False
        ).select_related('question')
        
        if not incorrect_interactions.exists():
            return ExplanationsResponseSchema(
                success=True,
                session_id=session_id,
                explanations=[],
                total_wrong_answers=0
            )
        
        # Generate explanations for each incorrect answer
        gemini_service = GeminiAIService()
        explanations = []
        
        for interaction in incorrect_interactions:
            question_data = {
                'question_text': interaction.question.question_text,
                'options': interaction.question.formatted_options,
                'student_answer': interaction.student_answer,
                'correct_answer': interaction.question.answer,
                'is_correct': interaction.is_correct,
                'difficulty': interaction.question.difficulty_level,
                'subject': interaction.question.subject
            }
            
            analysis = await gemini_service.analyze_question(question_data)
            
            explanations.append({
                'question_id': str(interaction.question.id),
                'question_text': interaction.question.question_text,
                'your_answer': interaction.student_answer,
                'correct_answer': f"{interaction.question.answer.upper()}: {interaction.question.formatted_options[interaction.question.answer]}",
                'explanation': analysis.get('explanation', 'Explanation not available'),
                'why_wrong': analysis.get('why_wrong', 'Review the concepts involved'),
                'improvement_tips': analysis.get('improvement_tips', []),
                'concepts_tested': analysis.get('concepts_tested', []),
                'difficulty': interaction.question.difficulty_level,
                'subject': interaction.question.subject
            })
        
        return ExplanationsResponseSchema(
            success=True,
            session_id=session_id,
            explanations=explanations,
            total_wrong_answers=len(explanations)
        )
        
    except Exception as e:
        logger.error(f"Error getting explanations: {e}")
        raise HttpError(500, f"Failed to get explanations: {str(e)}")

# ============================================================================
# Practice Mode AI Assistance Endpoints  
# ============================================================================

@router.post("/v2/practice/hint", response=HintResponseSchema)
def request_hint(request, payload: HintRequestSchema):
    """
    Request hint for practice mode (not available in exam mode)
    Provides graduated hints using Gemini AI
    """
    try:
        from assessment.models import ExamSession, AdaptiveQuestion
        
        try:
            exam_session = ExamSession.objects.get(id=payload.session_id)
            question = AdaptiveQuestion.objects.get(id=payload.question_id)
        except (ExamSession.DoesNotExist, AdaptiveQuestion.DoesNotExist) as e:
            raise HttpError(404, str(e))
        
        # Check if session is in practice mode
        if exam_session.assessment_mode != 'PRACTICE':
            raise HttpError(403, "Hints are only available in practice mode")
        
        # Check if session is active
        if exam_session.status != 'ACTIVE':
            raise HttpError(400, "Session is not active")
        
        # Generate hint using AI
        ai_service = get_working_ai_service()
        
        question_data = {
            'question_text': question.question_text,
            'options': question.formatted_options,
            'correct_answer': question.answer,
            'subject': question.subject,
            'difficulty': question.difficulty_level
        }
        
        hint = ai_service.get_hint(question_data, payload.hint_level)
        
        return HintResponseSchema(
            success=True,
            hint=hint,
            hint_level=payload.hint_level,
            remaining_hints=3 - payload.hint_level,  # Max 3 hint levels
            can_request_more_hints=payload.hint_level < 3
        )
        
    except Exception as e:
        logger.error(f"Error requesting hint: {e}")
        raise HttpError(500, f"Failed to get hint: {str(e)}")

@router.post("/v2/practice/explanation", response=PracticeExplanationResponseSchema)
def get_practice_explanation(request, payload: PracticeExplanationSchema):
    """
    Get detailed explanation after answering in practice mode
    Provides immediate feedback and learning guidance
    """
    try:
        from assessment.models import ExamSession, AdaptiveQuestion
        
        try:
            exam_session = ExamSession.objects.get(id=payload.session_id)
            question = AdaptiveQuestion.objects.get(id=payload.question_id)
        except (ExamSession.DoesNotExist, AdaptiveQuestion.DoesNotExist) as e:
            raise HttpError(404, str(e))
        
        # Check if session is in practice mode
        if exam_session.assessment_mode != 'PRACTICE':
            raise HttpError(403, "Detailed explanations are only available in practice mode")
        
        # Generate explanation using AI
        ai_service = get_working_ai_service()
        
        question_data = {
            'question_text': question.question_text,
            'options': question.formatted_options,
            'correct_answer': question.answer,
            'subject': question.subject,
            'difficulty': question.difficulty_level
        }
        
        explanation = ai_service.get_explanation(question_data, payload.student_answer)
        
        # Get next question for continuous practice
        next_question = get_next_question_for_session(exam_session)
        
        return PracticeExplanationResponseSchema(
            success=True,
            explanation=explanation.get('detailed_explanation', 'AI explanation generated successfully'),
            detailed_explanation=explanation,
            is_correct=payload.student_answer.lower() == question.answer.lower(),
            next_question=next_question
        )
        
    except Exception as e:
        logger.error(f"Error getting practice explanation: {e}")
        raise HttpError(500, f"Failed to get explanation: {str(e)}")

# ============================================================================
# Helper Functions
# ============================================================================

def get_mode_description(mode: AssessmentModeEnum) -> str:
    """Get description for assessment mode"""
    if mode == AssessmentModeEnum.EXAM:
        return "Exam Mode: Complete exam without AI assistance. Comprehensive analysis available after completion."
    else:
        return "Practice Mode: AI hints available during questions, immediate explanations after each answer."

def get_next_question_for_session(exam_session) -> Optional[Dict[str, Any]]:
    """Get next question for the exam session"""
    from assessment.models import AdaptiveQuestion, Interaction
    
    # Get questions already answered in this session
    answered_questions = Interaction.objects.filter(
        session_id=exam_session.id
    ).values_list('question_id', flat=True)
    
    # Get next question
    available_questions = AdaptiveQuestion.objects.filter(
        subject=exam_session.subject,
        difficulty_level=exam_session.current_difficulty,
        is_active=True
    ).exclude(id__in=answered_questions).order_by('?')[:1]
    
    if available_questions:
        question = available_questions[0]
        return {
            "id": str(question.id),
            "question_text": question.question_text,
            "options": question.formatted_options,
            "difficulty": exam_session.current_difficulty,
            "estimated_time": question.estimated_time_seconds,
            "question_number": exam_session.questions_attempted + 1
        }
    
    return None