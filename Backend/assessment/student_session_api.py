"""
Enhanced Student Session Management API
Provides isolated session management for different students
"""
from ninja import Router
from ninja.errors import HttpError
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import uuid
import logging
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Count, Avg, Q, Sum, Max
from django.shortcuts import get_object_or_404
from django.core.cache import cache

from .models import AdaptiveQuestion
from .user_session_models import UserSession, UserQuestionHistory, UserSubjectProgress, UserDailyStats
from core.models import StudentProfile
from .user_session_schemas import (
    CreateSessionSchema, SubmitAnswerSchema, UpdateSessionSchema,
    UserSessionResponse, QuestionHistoryResponse, SubjectProgressResponse,
    DailyStatsResponse, UserDashboardResponse, SessionCreateResponse,
    AnswerSubmissionResponse, NextQuestionResponse, ErrorResponse,
    SessionListFilters, QuestionHistoryFilters, SessionStatsResponse
)

logger = logging.getLogger(__name__)
student_session_router = Router()

# ============================================================================
# Student-Specific Session Management
# ============================================================================

@student_session_router.post("/student/{student_id}/session/create", response=SessionCreateResponse, tags=["Student Sessions"])
def create_student_session(request, student_id: str, payload: CreateSessionSchema):
    """
    Create a new study session for a specific student
    Each student has isolated sessions and progress tracking
    """
    try:
        with transaction.atomic():
            # Get student profile - this ensures the student exists
            student_profile = get_object_or_404(StudentProfile, id=student_id)
            user = student_profile.user
            
            # Check for existing active session for this student and subject
            existing_session = UserSession.objects.filter(
                user=user,
                subject=payload.subject,
                status='ACTIVE'
            ).first()
            
            if existing_session:
                return SessionCreateResponse(
                    success=False,
                    message=f"Student {user.username} already has an active session for {payload.subject}",
                    session=_session_to_response(existing_session)
                )
            
            # Create new session with student-specific settings
            session = UserSession.objects.create(
                user=user,
                session_type=payload.session_type,
                subject=payload.subject,
                chapter_number=payload.chapter_number
            )
            
            # Initialize adaptive question sequence based on student's progress
            questions = _get_adaptive_questions_for_student(student_profile, session)
            session.question_ids_sequence = [str(q.id) for q in questions]
            
            # Set initial difficulty based on student's mastery level
            student_progress = _get_or_create_student_progress(student_profile, payload.subject)
            session.current_difficulty_level = student_progress.current_mastery_level
            
            session.save()
            
            # Cache session for quick access
            cache.set(f"active_session_{student_id}_{payload.subject}", str(session.id), timeout=3600)
            
            # Get first question adapted to student's level
            next_question = None
            if questions:
                next_question = _question_to_next_response(questions[0], session, student_profile)
            
            logger.info(f"Created session {session.id} for student {student_id}")
            
            return SessionCreateResponse(
                success=True,
                message=f"Session created for student {user.username}",
                session=_session_to_response(session),
                next_question=next_question
            )
            
    except StudentProfile.DoesNotExist:
        raise HttpError(404, f"Student with ID {student_id} not found")
    except Exception as e:
        logger.error(f"Error creating session for student {student_id}: {str(e)}")
        raise HttpError(500, f"Error creating session: {str(e)}")


@student_session_router.post("/student/{student_id}/session/{session_id}/submit", response=AnswerSubmissionResponse, tags=["Student Sessions"])
def submit_student_answer(request, student_id: str, session_id: str, payload: SubmitAnswerSchema):
    """
    Submit an answer for a student's session with adaptive difficulty adjustment
    """
    try:
        with transaction.atomic():
            # Verify student ownership of session
            student_profile = get_object_or_404(StudentProfile, id=student_id)
            session = get_object_or_404(
                UserSession, 
                id=session_id, 
                user=student_profile.user,
                status='ACTIVE'
            )
            question = get_object_or_404(AdaptiveQuestion, id=payload.question_id)
            
            # Verify question belongs to current session
            if payload.question_id not in session.question_ids_sequence:
                raise HttpError(400, "Question not part of current session")
            
            # Create detailed question history
            question_history = UserQuestionHistory.objects.create(
                user=student_profile.user,
                session=session,
                question=question,
                user_answer=payload.user_answer.lower().strip(),
                correct_answer=question.answer.lower().strip(),
                question_order_in_session=session.current_question_index + 1,
                difficulty_when_presented=question.difficulty_level,
                hints_requested=payload.hints_requested or 0,
                explanation_viewed=payload.explanation_viewed or False,
                confidence_level=payload.confidence_level,
                question_end_time=timezone.now(),
                time_spent_seconds=payload.time_spent_seconds or 0
            )
            
            # Update session progress
            session.questions_attempted += 1
            session.current_question_index += 1
            
            is_correct = question_history.is_correct
            if is_correct:
                session.questions_correct += 1
                session.current_score += 1
            
            # Add to answered questions
            if payload.question_id not in session.answered_question_ids:
                session.answered_question_ids.append(payload.question_id)
            
            # Adaptive difficulty adjustment based on student performance
            _adjust_difficulty_for_student(session, question_history, student_profile)
            
            # Update session timing
            if payload.time_spent_seconds:
                session.add_question_time(payload.time_spent_seconds)
            
            session.save()
            
            # Update student's learning profile
            _update_student_learning_profile(student_profile, question_history, session)
            
            # Get next adaptive question
            next_question = None
            if session.current_question_index < len(session.question_ids_sequence):
                next_question_id = session.question_ids_sequence[session.current_question_index]
                next_question_obj = AdaptiveQuestion.objects.get(id=next_question_id)
                next_question = _question_to_next_response(next_question_obj, session, student_profile)
            else:
                # Session completed - comprehensive updates
                session.complete_session()
                _complete_student_session(student_profile, session)
            
            # Update daily stats for this student
            _update_student_daily_stats(student_profile, session, question_history)
            
            # Prepare response with student-specific feedback
            explanation = _get_adaptive_explanation(question, question_history, student_profile)
            
            logger.info(f"Student {student_id} answered question {payload.question_id}: {is_correct}")
            
            return AnswerSubmissionResponse(
                success=True,
                message="Answer submitted successfully",
                is_correct=is_correct,
                correct_answer=question.answer,
                explanation=explanation,
                session_updated=_session_to_response(session),
                next_question=next_question,
                mastery_update=_get_mastery_update(student_profile, question.subject)
            )
            
    except (StudentProfile.DoesNotExist, UserSession.DoesNotExist):
        raise HttpError(404, "Student or session not found")
    except Exception as e:
        logger.error(f"Error submitting answer for student {student_id}: {str(e)}")
        raise HttpError(500, f"Error submitting answer: {str(e)}")


@student_session_router.get("/student/{student_id}/dashboard", response=UserDashboardResponse, tags=["Student Dashboard"])
def get_student_dashboard(request, student_id: str):
    """
    Get comprehensive dashboard for a specific student
    """
    try:
        student_profile = get_object_or_404(StudentProfile, id=student_id)
        user = student_profile.user
        
        # Active sessions for this student only
        active_sessions = UserSession.objects.filter(
            user=user, 
            status='ACTIVE'
        ).select_related('user')[:5]
        
        # Subject progress for this student
        subject_progress = UserSubjectProgress.objects.filter(
            user=user
        ).order_by('-updated_at')
        
        # Recent activity for this student
        recent_activity = UserQuestionHistory.objects.filter(
            user=user
        ).select_related('question', 'session').order_by('-created_at')[:10]
        
        # Today's stats for this student
        today = timezone.now().date()
        daily_stats = UserDailyStats.objects.filter(user=user, date=today).first()
        
        # Student-specific overall stats
        total_sessions = UserSession.objects.filter(user=user).count()
        total_questions = UserQuestionHistory.objects.filter(user=user).count()
        total_correct = UserQuestionHistory.objects.filter(user=user, answer_status='CORRECT').count()
        overall_accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
        
        # Student learning analytics
        subjects_studied = list(subject_progress.values_list('subject', flat=True))
        study_streak = _calculate_study_streak(student_profile)
        learning_velocity = _calculate_learning_velocity(student_profile)
        
        overall_stats = {
            'student_id': student_id,
            'student_name': user.username,
            'total_sessions': total_sessions,
            'total_questions_answered': total_questions,
            'overall_accuracy_percentage': round(overall_accuracy, 2),
            'subjects_studied': subjects_studied,
            'days_active': UserSession.objects.filter(user=user).dates('session_start_time', 'day').count(),
            'current_study_streak': study_streak,
            'learning_velocity': learning_velocity,
            'mastery_levels': {sp.subject: sp.current_mastery_level for sp in subject_progress}
        }
        
        return UserDashboardResponse(
            user_info={
                'id': user.id, 
                'username': user.username, 
                'email': user.email,
                'student_profile_id': student_id
            },
            active_sessions=[_session_to_response(s) for s in active_sessions],
            subject_progress=[_subject_progress_to_response(sp) for sp in subject_progress],
            recent_activity=[_question_history_to_response(qa) for qa in recent_activity],
            daily_stats=_daily_stats_to_response(daily_stats) if daily_stats else None,
            overall_stats=overall_stats
        )
        
    except StudentProfile.DoesNotExist:
        raise HttpError(404, f"Student with ID {student_id} not found")
    except Exception as e:
        logger.error(f"Error getting dashboard for student {student_id}: {str(e)}")
        raise HttpError(500, f"Error getting dashboard: {str(e)}")


@student_session_router.get("/student/{student_id}/sessions", response=List[UserSessionResponse], tags=["Student Sessions"])
def list_student_sessions(request, student_id: str, subject: Optional[str] = None, limit: int = 20):
    """
    List all sessions for a specific student with optional subject filter
    """
    try:
        student_profile = get_object_or_404(StudentProfile, id=student_id)
        
        sessions = UserSession.objects.filter(user=student_profile.user)
        
        if subject:
            sessions = sessions.filter(subject=subject)
        
        sessions = sessions.select_related('user').order_by('-session_start_time')[:limit]
        
        return [_session_to_response(session) for session in sessions]
        
    except StudentProfile.DoesNotExist:
        raise HttpError(404, f"Student with ID {student_id} not found")
    except Exception as e:
        logger.error(f"Error listing sessions for student {student_id}: {str(e)}")
        raise HttpError(500, f"Error listing sessions: {str(e)}")


@student_session_router.get("/student/{student_id}/progress/{subject}", response=SubjectProgressResponse, tags=["Student Progress"])
def get_student_subject_progress(request, student_id: str, subject: str):
    """
    Get detailed subject progress for a specific student
    """
    try:
        student_profile = get_object_or_404(StudentProfile, id=student_id)
        
        progress = _get_or_create_student_progress(student_profile, subject)
        
        return _subject_progress_to_response(progress)
        
    except StudentProfile.DoesNotExist:
        raise HttpError(404, f"Student with ID {student_id} not found")
    except Exception as e:
        logger.error(f"Error getting progress for student {student_id}: {str(e)}")
        raise HttpError(500, f"Error getting subject progress: {str(e)}")


# ============================================================================
# Student-Specific Helper Functions
# ============================================================================

def _get_adaptive_questions_for_student(student_profile: StudentProfile, session: UserSession) -> List[AdaptiveQuestion]:
    """
    Get adaptive question sequence based on student's learning profile
    """
    # Get student's current mastery level for the subject
    progress = _get_or_create_student_progress(student_profile, session.subject)
    
    # Start with questions at appropriate difficulty
    base_questions = AdaptiveQuestion.objects.filter(
        subject=session.subject,
        is_active=True,
        difficulty_level=progress.current_mastery_level
    )
    
    # Add some easier and harder questions for adaptive progression
    easier_questions = AdaptiveQuestion.objects.filter(
        subject=session.subject,
        is_active=True
    ).exclude(difficulty_level=progress.current_mastery_level)
    
    # Combine and shuffle based on session type
    if session.session_type == 'PRACTICE':
        questions = list(base_questions[:7]) + list(easier_questions[:3])
    elif session.session_type == 'CHAPTER_TEST':
        questions = list(base_questions[:15]) + list(easier_questions[:5])
    elif session.session_type == 'MOCK_TEST':
        questions = list(base_questions[:35]) + list(easier_questions[:15])
    else:  # FULL_TEST
        questions = list(base_questions[:70]) + list(easier_questions[:30])
    
    # Shuffle while maintaining some structure
    import random
    random.shuffle(questions)
    
    return questions


def _get_or_create_student_progress(student_profile: StudentProfile, subject: str) -> UserSubjectProgress:
    """
    Get or create subject progress for a student
    """
    progress, created = UserSubjectProgress.objects.get_or_create(
        user=student_profile.user,
        subject=subject,
        defaults={
            'current_mastery_level': 'easy',
            'chapter_progress': {},
            'topic_mastery_scores': {}
        }
    )
    
    if created:
        logger.info(f"Created new progress tracking for student {student_profile.id} in {subject}")
    
    return progress


def _adjust_difficulty_for_student(session: UserSession, question_history: UserQuestionHistory, student_profile: StudentProfile):
    """
    Adjust difficulty based on student's performance pattern
    """
    # Calculate recent accuracy for adaptive adjustment
    recent_questions = UserQuestionHistory.objects.filter(
        session=session
    ).order_by('-created_at')[:5]
    
    recent_correct = sum(1 for q in recent_questions if q.is_correct)
    recent_accuracy = recent_correct / len(recent_questions) if recent_questions else 0
    
    # Adaptive difficulty adjustment
    if recent_accuracy >= 0.8 and len(recent_questions) >= 3:
        # Student is doing well, increase difficulty
        difficulty_levels = ['very_easy', 'easy', 'moderate', 'difficult']
        current_index = difficulty_levels.index(session.current_difficulty_level)
        if current_index < len(difficulty_levels) - 1:
            session.current_difficulty_level = difficulty_levels[current_index + 1]
            
    elif recent_accuracy <= 0.4 and len(recent_questions) >= 3:
        # Student is struggling, decrease difficulty
        difficulty_levels = ['very_easy', 'easy', 'moderate', 'difficult']
        current_index = difficulty_levels.index(session.current_difficulty_level)
        if current_index > 0:
            session.current_difficulty_level = difficulty_levels[current_index - 1]


def _update_student_learning_profile(student_profile: StudentProfile, question_history: UserQuestionHistory, session: UserSession):
    """
    Update student's learning profile based on performance
    """
    # Update interaction history in student profile
    interaction_data = {
        'question_id': str(question_history.question.id),
        'timestamp': question_history.created_at.isoformat(),
        'correct': question_history.is_correct,
        'time': question_history.time_spent_seconds,
        'subject': question_history.question.subject,
        'difficulty': question_history.difficulty_when_presented,
        'session_id': str(session.id)
    }
    
    if not isinstance(student_profile.interaction_history, list):
        student_profile.interaction_history = []
    
    student_profile.interaction_history.append(interaction_data)
    
    # Keep only last 1000 interactions to prevent bloat
    if len(student_profile.interaction_history) > 1000:
        student_profile.interaction_history = student_profile.interaction_history[-1000:]
    
    student_profile.last_activity = timezone.now()
    student_profile.save()


def _complete_student_session(student_profile: StudentProfile, session: UserSession):
    """
    Handle session completion for a student
    """
    # Update subject progress
    progress = _get_or_create_student_progress(student_profile, session.subject)
    progress.update_progress_from_session(session)
    
    # Update mastery level based on session performance
    if session.accuracy_percentage >= 80:
        difficulty_levels = ['very_easy', 'easy', 'moderate', 'difficult']
        current_index = difficulty_levels.index(progress.current_mastery_level)
        if current_index < len(difficulty_levels) - 1:
            progress.current_mastery_level = difficulty_levels[current_index + 1]
            progress.save()
    
    # Clear cache
    cache.delete(f"active_session_{student_profile.id}_{session.subject}")
    
    logger.info(f"Completed session {session.id} for student {student_profile.id}")


def _update_student_daily_stats(student_profile: StudentProfile, session: UserSession, question_history: UserQuestionHistory):
    """
    Update daily statistics for a specific student
    """
    today = timezone.now().date()
    daily_stats, created = UserDailyStats.objects.get_or_create(
        user=student_profile.user,
        date=today,
        defaults={
            'subject_time_distribution': {},
            'subject_question_counts': {}
        }
    )
    
    # Update question counts
    daily_stats.questions_attempted += 1
    if question_history.is_correct:
        daily_stats.questions_correct += 1
    
    # Update subject-specific counts
    subject = session.subject
    if subject not in daily_stats.subject_question_counts:
        daily_stats.subject_question_counts[subject] = 0
    daily_stats.subject_question_counts[subject] += 1
    
    # Update time distribution
    if subject not in daily_stats.subject_time_distribution:
        daily_stats.subject_time_distribution[subject] = 0
    daily_stats.subject_time_distribution[subject] += int(question_history.time_spent_seconds)
    
    daily_stats.save()


def _get_adaptive_explanation(question: AdaptiveQuestion, question_history: UserQuestionHistory, student_profile: StudentProfile) -> str:
    """
    Generate adaptive explanation based on student's learning profile
    """
    base_explanation = f"The correct answer is '{question.answer}': {question.correct_option_text}"
    
    if not question_history.is_correct:
        # Add encouraging message for struggling students
        recent_accuracy = _get_recent_accuracy(student_profile, question.subject)
        if recent_accuracy < 0.5:
            base_explanation += "\n\nDon't worry! This topic can be challenging. Consider reviewing the fundamentals and practicing similar questions."
        else:
            base_explanation += "\n\nGood effort! You're making progress. Review this concept and try similar questions to strengthen your understanding."
    
    return base_explanation


def _get_recent_accuracy(student_profile: StudentProfile, subject: str) -> float:
    """
    Calculate recent accuracy for a student in a subject
    """
    recent_interactions = UserQuestionHistory.objects.filter(
        user=student_profile.user,
        question__subject=subject
    ).order_by('-created_at')[:10]
    
    if not recent_interactions:
        return 0.0
    
    correct_count = sum(1 for interaction in recent_interactions if interaction.is_correct)
    return correct_count / len(recent_interactions)


def _calculate_study_streak(student_profile: StudentProfile) -> int:
    """
    Calculate current study streak for a student
    """
    # Get dates when student was active
    active_dates = UserSession.objects.filter(
        user=student_profile.user
    ).dates('session_start_time', 'day').order_by('-session_start_time')
    
    if not active_dates:
        return 0
    
    streak = 0
    current_date = timezone.now().date()
    
    for active_date in active_dates:
        if (current_date - active_date).days == streak:
            streak += 1
        else:
            break
    
    return streak


def _calculate_learning_velocity(student_profile: StudentProfile) -> float:
    """
    Calculate learning velocity (questions answered per hour of study)
    """
    total_time = UserDailyStats.objects.filter(
        user=student_profile.user
    ).aggregate(
        total_time=Sum('total_study_time_seconds'),
        total_questions=Sum('questions_attempted')
    )
    
    if total_time['total_time'] and total_time['total_questions']:
        hours = total_time['total_time'] / 3600
        return round(total_time['total_questions'] / hours, 2)
    
    return 0.0


def _get_mastery_update(student_profile: StudentProfile, subject: str) -> Dict[str, float]:
    """
    Get current mastery scores for a student in a subject
    """
    progress = UserSubjectProgress.objects.filter(
        user=student_profile.user,
        subject=subject
    ).first()
    
    if progress:
        return {
            'accuracy': progress.overall_accuracy_percentage,
            'mastery_level': progress.current_mastery_level,
            'streak': progress.current_correct_streak,
            'topic_scores': progress.topic_mastery_scores
        }
    
    return {}


# Import shared helper functions from the original file
def _session_to_response(session: UserSession) -> UserSessionResponse:
    """Convert UserSession model to response schema"""
    return UserSessionResponse(
        id=str(session.id),
        user_id=session.user.id,
        username=session.user.username,
        session_type=session.session_type,
        subject=session.subject,
        chapter_number=session.chapter_number,
        status=session.status,
        current_question_index=session.current_question_index,
        session_start_time=session.session_start_time,
        session_end_time=session.session_end_time,
        total_duration_seconds=session.total_duration_seconds,
        questions_attempted=session.questions_attempted,
        questions_correct=session.questions_correct,
        current_score=session.current_score,
        accuracy_percentage=session.accuracy_percentage,
        average_time_per_question=session.average_time_per_question,
        current_difficulty_level=session.current_difficulty_level,
        is_active=session.is_active,
        created_at=session.created_at,
        updated_at=session.updated_at
    )


def _question_history_to_response(qh: UserQuestionHistory) -> QuestionHistoryResponse:
    """Convert UserQuestionHistory model to response schema"""
    return QuestionHistoryResponse(
        id=str(qh.id),
        user_id=qh.user.id,
        username=qh.user.username,
        session_id=str(qh.session.id),
        session_type=qh.session.session_type,
        question_id=str(qh.question.id),
        question_text=qh.question.question_text,
        question_subject=qh.question.subject,
        user_answer=qh.user_answer,
        correct_answer=qh.correct_answer,
        answer_status=qh.answer_status,
        is_correct=qh.is_correct,
        question_start_time=qh.question_start_time,
        question_end_time=qh.question_end_time,
        time_spent_seconds=qh.time_spent_seconds,
        question_order_in_session=qh.question_order_in_session,
        difficulty_when_presented=qh.difficulty_when_presented,
        hints_requested=qh.hints_requested,
        explanation_viewed=qh.explanation_viewed,
        confidence_level=qh.confidence_level,
        attempt_number=qh.attempt_number,
        created_at=qh.created_at
    )


def _subject_progress_to_response(sp: UserSubjectProgress) -> SubjectProgressResponse:
    """Convert UserSubjectProgress model to response schema"""
    return SubjectProgressResponse(
        id=str(sp.id),
        user_id=sp.user.id,
        username=sp.user.username,
        subject=sp.subject,
        total_questions_attempted=sp.total_questions_attempted,
        total_questions_correct=sp.total_questions_correct,
        overall_accuracy_percentage=sp.overall_accuracy_percentage,
        current_mastery_level=sp.current_mastery_level,
        total_study_time_seconds=sp.total_study_time_seconds,
        average_time_per_question=sp.average_time_per_question,
        total_sessions=sp.total_sessions,
        average_session_duration_minutes=sp.average_session_duration_minutes,
        current_correct_streak=sp.current_correct_streak,
        longest_correct_streak=sp.longest_correct_streak,
        current_study_streak_days=sp.current_study_streak_days,
        longest_study_streak_days=sp.longest_study_streak_days,
        chapter_progress=sp.chapter_progress,
        topic_mastery_scores=sp.topic_mastery_scores,
        last_session_date=sp.last_session_date,
        last_question_answered=sp.last_question_answered,
        created_at=sp.created_at,
        updated_at=sp.updated_at
    )


def _daily_stats_to_response(ds: UserDailyStats) -> DailyStatsResponse:
    """Convert UserDailyStats model to response schema"""
    return DailyStatsResponse(
        id=str(ds.id),
        user_id=ds.user.id,
        username=ds.user.username,
        date=ds.date,
        total_study_time_seconds=ds.total_study_time_seconds,
        study_time_hours=ds.study_time_hours,
        questions_attempted=ds.questions_attempted,
        questions_correct=ds.questions_correct,
        accuracy_percentage=ds.accuracy_percentage,
        sessions_completed=ds.sessions_completed,
        subject_time_distribution=ds.subject_time_distribution,
        subject_question_counts=ds.subject_question_counts,
        new_topics_attempted=ds.new_topics_attempted,
        difficulty_levels_unlocked=ds.difficulty_levels_unlocked,
        personal_bests=ds.personal_bests,
        created_at=ds.created_at,
        updated_at=ds.updated_at
    )


def _question_to_next_response(question: AdaptiveQuestion, session: UserSession, student_profile: StudentProfile) -> NextQuestionResponse:
    """Convert question to next question response with student context"""
    return NextQuestionResponse(
        question_id=str(question.id),
        question_text=question.question_text,
        options=question.formatted_options,
        difficulty_level=question.difficulty_level,
        subject=question.subject,
        chapter_name=question.topic or "General",
        question_order=session.current_question_index + 1,
        session_progress={
            'attempted': session.questions_attempted,
            'correct': session.questions_correct,
            'total_questions': len(session.question_ids_sequence),
            'accuracy': session.accuracy_percentage,
            'student_id': str(student_profile.id),
            'current_difficulty': session.current_difficulty_level
        }
    )