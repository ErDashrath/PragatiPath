"""
User Session Management API for Django Ninja
Handles user sessions, question submission, and progress tracking
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
from django.db.models import Count, Avg, Q, Sum
from django.shortcuts import get_object_or_404

from .models import AdaptiveQuestion
from .user_session_models import UserSession, UserQuestionHistory, UserSubjectProgress, UserDailyStats
from .user_session_schemas import (
    CreateSessionSchema, SubmitAnswerSchema, UpdateSessionSchema,
    UserSessionResponse, QuestionHistoryResponse, SubjectProgressResponse,
    DailyStatsResponse, UserDashboardResponse, SessionCreateResponse,
    AnswerSubmissionResponse, NextQuestionResponse, ErrorResponse,
    SessionListFilters, QuestionHistoryFilters, SessionStatsResponse
)

logger = logging.getLogger(__name__)
user_session_router = Router()

# ============================================================================
# User Session Management Endpoints
# ============================================================================

@user_session_router.post("/sessions/create", response=SessionCreateResponse, tags=["User Sessions"])
def create_user_session(request, payload: CreateSessionSchema):
    """
    Create a new user study session
    """
    try:
        with transaction.atomic():
            # Get user
            user = get_object_or_404(User, id=payload.user_id)
            
            # Check for existing active session
            existing_session = UserSession.objects.filter(
                user=user,
                subject=payload.subject,
                status='ACTIVE'
            ).first()
            
            if existing_session:
                return SessionCreateResponse(
                    success=False,
                    message="User already has an active session for this subject",
                    session=_session_to_response(existing_session)
                )
            
            # Create new session
            session = UserSession.objects.create(
                user=user,
                session_type=payload.session_type,
                subject=payload.subject,
                chapter_number=payload.chapter_number
            )
            
            # Initialize question sequence for the session
            questions = _get_session_questions(session)
            session.question_ids_sequence = [str(q.id) for q in questions]
            session.save()
            
            # Get first question
            next_question = None
            if questions:
                next_question = _question_to_next_response(questions[0], session)
            
            return SessionCreateResponse(
                success=True,
                message="Session created successfully",
                session=_session_to_response(session),
                next_question=next_question
            )
            
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HttpError(500, f"Error creating session: {str(e)}")


@user_session_router.post("/sessions/{session_id}/submit-answer", response=AnswerSubmissionResponse, tags=["User Sessions"])
def submit_answer(request, session_id: str, payload: SubmitAnswerSchema):
    """
    Submit an answer for a question in a session
    """
    try:
        with transaction.atomic():
            # Get session
            session = get_object_or_404(UserSession, id=session_id, status='ACTIVE')
            question = get_object_or_404(AdaptiveQuestion, id=payload.question_id)
            
            # Check if question is in session sequence
            if payload.question_id not in session.question_ids_sequence:
                raise HttpError(400, "Question not part of current session")
            
            # Create question history record
            question_history = UserQuestionHistory.objects.create(
                user=session.user,
                session=session,
                question=question,
                user_answer=payload.user_answer.lower(),
                correct_answer=question.answer.lower(),
                question_order_in_session=session.current_question_index + 1,
                difficulty_when_presented=question.difficulty_level,
                hints_requested=payload.hints_requested or 0,
                explanation_viewed=payload.explanation_viewed or False,
                confidence_level=payload.confidence_level,
                question_end_time=timezone.now()
            )
            
            # Calculate time spent
            if payload.time_spent_seconds:
                question_history.time_spent_seconds = payload.time_spent_seconds
                session.add_question_time(payload.time_spent_seconds)
            
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
            
            session.save()
            question_history.save()
            
            # Get next question
            next_question = None
            if session.current_question_index < len(session.question_ids_sequence):
                next_question_id = session.question_ids_sequence[session.current_question_index]
                next_question_obj = AdaptiveQuestion.objects.get(id=next_question_id)
                next_question = _question_to_next_response(next_question_obj, session)
            else:
                # Session completed
                session.complete_session()
                _update_user_progress(session)
            
            # Update daily stats
            _update_daily_stats(session.user, session, question_history)
            
            return AnswerSubmissionResponse(
                success=True,
                message="Answer submitted successfully",
                is_correct=is_correct,
                correct_answer=question.answer,
                explanation=f"The correct answer is {question.answer}. {question.correct_option_text}",
                session_updated=_session_to_response(session),
                next_question=next_question
            )
            
    except Exception as e:
        logger.error(f"Error submitting answer: {str(e)}")
        raise HttpError(500, f"Error submitting answer: {str(e)}")


@user_session_router.get("/sessions/{session_id}", response=UserSessionResponse, tags=["User Sessions"])
def get_session(request, session_id: str):
    """
    Get details of a specific session
    """
    session = get_object_or_404(UserSession, id=session_id)
    return _session_to_response(session)


@user_session_router.put("/sessions/{session_id}", response=UserSessionResponse, tags=["User Sessions"])
def update_session(request, session_id: str, payload: UpdateSessionSchema):
    """
    Update session status or properties
    """
    try:
        session = get_object_or_404(UserSession, id=session_id)
        
        if payload.status:
            session.status = payload.status
            if payload.status == 'COMPLETED':
                session.complete_session()
                _update_user_progress(session)
        
        if payload.current_question_index is not None:
            session.current_question_index = payload.current_question_index
        
        if payload.current_score is not None:
            session.current_score = payload.current_score
            
        if payload.current_difficulty_level:
            session.current_difficulty_level = payload.current_difficulty_level
        
        session.save()
        return _session_to_response(session)
        
    except Exception as e:
        logger.error(f"Error updating session: {str(e)}")
        raise HttpError(500, f"Error updating session: {str(e)}")


@user_session_router.get("/users/{user_id}/sessions", response=List[UserSessionResponse], tags=["User Sessions"])
def list_user_sessions(request, user_id: int, filters: SessionListFilters = None):
    """
    List sessions for a specific user with optional filters
    """
    try:
        user = get_object_or_404(User, id=user_id)
        sessions = UserSession.objects.filter(user=user)
        
        if filters:
            if filters.subject:
                sessions = sessions.filter(subject=filters.subject)
            if filters.session_type:
                sessions = sessions.filter(session_type=filters.session_type)
            if filters.status:
                sessions = sessions.filter(status=filters.status)
            if filters.start_date:
                sessions = sessions.filter(session_start_time__gte=filters.start_date)
            if filters.end_date:
                sessions = sessions.filter(session_start_time__lte=filters.end_date)
        
        # Apply pagination
        offset = filters.offset if filters else 0
        limit = filters.limit if filters else 20
        sessions = sessions[offset:offset+limit]
        
        return [_session_to_response(session) for session in sessions]
        
    except Exception as e:
        logger.error(f"Error listing sessions: {str(e)}")
        raise HttpError(500, f"Error listing sessions: {str(e)}")


@user_session_router.get("/users/{user_id}/dashboard", response=UserDashboardResponse, tags=["User Dashboard"])
def get_user_dashboard(request, user_id: int):
    """
    Get comprehensive dashboard data for a user
    """
    try:
        user = get_object_or_404(User, id=user_id)
        
        # Active sessions
        active_sessions = UserSession.objects.filter(user=user, status='ACTIVE')[:5]
        
        # Subject progress
        subject_progress = UserSubjectProgress.objects.filter(user=user)
        
        # Recent activity (last 10 question interactions)
        recent_activity = UserQuestionHistory.objects.filter(user=user)[:10]
        
        # Today's stats
        today = timezone.now().date()
        daily_stats = UserDailyStats.objects.filter(user=user, date=today).first()
        
        # Overall stats
        total_sessions = UserSession.objects.filter(user=user).count()
        total_questions = UserQuestionHistory.objects.filter(user=user).count()
        total_correct = UserQuestionHistory.objects.filter(user=user, answer_status='CORRECT').count()
        overall_accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
        
        overall_stats = {
            'total_sessions': total_sessions,
            'total_questions_answered': total_questions,
            'overall_accuracy_percentage': overall_accuracy,
            'subjects_studied': list(subject_progress.values_list('subject', flat=True)),
            'days_active': UserSession.objects.filter(user=user).dates('session_start_time', 'day').count()
        }
        
        return UserDashboardResponse(
            user_info={'id': user.id, 'username': user.username, 'email': user.email},
            active_sessions=[_session_to_response(s) for s in active_sessions],
            subject_progress=[_subject_progress_to_response(sp) for sp in subject_progress],
            recent_activity=[_question_history_to_response(qa) for qa in recent_activity],
            daily_stats=_daily_stats_to_response(daily_stats) if daily_stats else None,
            overall_stats=overall_stats
        )
        
    except Exception as e:
        logger.error(f"Error getting dashboard: {str(e)}")
        raise HttpError(500, f"Error getting dashboard: {str(e)}")


@user_session_router.get("/users/{user_id}/progress/{subject}", response=SubjectProgressResponse, tags=["User Progress"])
def get_subject_progress(request, user_id: int, subject: str):
    """
    Get detailed progress for a specific subject
    """
    try:
        user = get_object_or_404(User, id=user_id)
        progress, created = UserSubjectProgress.objects.get_or_create(
            user=user,
            subject=subject,
            defaults={'current_mastery_level': 'easy'}
        )
        
        return _subject_progress_to_response(progress)
        
    except Exception as e:
        logger.error(f"Error getting subject progress: {str(e)}")
        raise HttpError(500, f"Error getting subject progress: {str(e)}")


# ============================================================================
# Helper Functions
# ============================================================================

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


def _question_to_next_response(question: AdaptiveQuestion, session: UserSession) -> NextQuestionResponse:
    """Convert question to next question response"""
    return NextQuestionResponse(
        question_id=str(question.id),
        question_text=question.question_text,
        options=question.formatted_options,
        difficulty_level=question.difficulty_level,
        subject=question.subject,
        chapter_name=question.topic,
        question_order=session.current_question_index + 1,
        session_progress={
            'attempted': session.questions_attempted,
            'correct': session.questions_correct,
            'total_questions': len(session.question_ids_sequence),
            'accuracy': session.accuracy_percentage
        }
    )


def _get_session_questions(session: UserSession) -> List[AdaptiveQuestion]:
    """Get questions for a session based on type and subject"""
    questions = AdaptiveQuestion.objects.filter(subject=session.subject, is_active=True)
    
    if session.chapter_number:
        # For chapter tests, filter by chapter (implement chapter logic)
        pass
    
    # Limit questions based on session type
    if session.session_type == 'PRACTICE':
        questions = questions.order_by('?')[:10]  # Random 10 questions
    elif session.session_type == 'CHAPTER_TEST':
        questions = questions.order_by('?')[:20]  # Random 20 questions
    elif session.session_type == 'MOCK_TEST':
        questions = questions.order_by('?')[:50]  # Random 50 questions
    elif session.session_type == 'FULL_TEST':
        questions = questions.order_by('?')[:100]  # Random 100 questions
    
    return list(questions)


def _update_user_progress(session: UserSession):
    """Update user's subject progress after session completion"""
    progress, created = UserSubjectProgress.objects.get_or_create(
        user=session.user,
        subject=session.subject,
        defaults={'current_mastery_level': 'easy'}
    )
    
    progress.update_progress_from_session(session)


def _update_daily_stats(user: User, session: UserSession, question_history: UserQuestionHistory):
    """Update user's daily statistics"""
    today = timezone.now().date()
    daily_stats, created = UserDailyStats.objects.get_or_create(
        user=user,
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
    
    # Update subject distribution
    if session.subject not in daily_stats.subject_question_counts:
        daily_stats.subject_question_counts[session.subject] = 0
    daily_stats.subject_question_counts[session.subject] += 1
    
    daily_stats.save()