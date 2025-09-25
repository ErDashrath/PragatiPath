"""
Comprehensive API for Multi-Student Session Management
Handles all student interactions with proper database relationships
"""

from ninja import Router, Schema
from ninja.pagination import paginate, PageNumberPagination
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg, Sum
from django.db import transaction
from django.utils import timezone
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, date

# Import our improved models
from .improved_models import (
    Subject, Chapter, StudentSession, QuestionAttempt, 
    StudentProgress, DailyStudyStats
)
from .models import AdaptiveQuestion

# Router setup
multi_student_router = Router()

# Schema definitions for proper API structure
class SubjectSchema(Schema):
    id: int
    code: str
    name: str
    description: str
    is_active: bool
    created_at: datetime

class ChapterSchema(Schema):
    id: int
    subject_id: int
    name: str
    description: str
    chapter_number: int
    is_active: bool

class StudentSessionCreateSchema(Schema):
    subject_id: int
    chapter_id: Optional[int] = None
    session_type: str = 'PRACTICE'
    session_name: Optional[str] = None
    total_questions_planned: int = 10
    time_limit_minutes: Optional[int] = None

class StudentSessionSchema(Schema):
    id: str
    student_username: str
    subject_name: str
    chapter_name: Optional[str] = None
    session_type: str
    session_name: str
    status: str
    current_question_number: int
    total_questions_planned: int
    session_start_time: datetime
    session_end_time: Optional[datetime] = None
    questions_attempted: int
    questions_correct: int
    questions_incorrect: int
    percentage_score: float
    current_difficulty_level: str

class QuestionAttemptSchema(Schema):
    id: int
    session_id: str
    question_id: int
    student_username: str
    question_number_in_session: int
    student_answer: str
    correct_answer: str
    answer_status: str
    is_correct: bool
    time_spent_seconds: float
    difficulty_when_presented: str
    points_earned: float

class StudentProgressSchema(Schema):
    id: int
    student_username: str
    subject_name: str
    total_sessions: int
    total_questions_attempted: int
    total_questions_correct: int
    current_accuracy_percentage: float
    best_accuracy_percentage: float
    current_mastery_level: str
    mastery_score: float
    current_correct_streak: int
    longest_correct_streak: int

class DailyStatsSchema(Schema):
    id: int
    student_username: str
    study_date: date
    total_sessions: int
    total_study_time_seconds: int
    questions_attempted: int
    questions_correct: int
    daily_accuracy_percentage: float

class AnswerSubmissionSchema(Schema):
    session_id: str
    question_id: int
    student_answer: str
    time_spent_seconds: float
    confidence_level: Optional[int] = None


# Subject Management APIs
@multi_student_router.get("/subjects/", response=List[SubjectSchema])
def list_subjects(request):
    """Get all active subjects"""
    return Subject.objects.filter(is_active=True)

@multi_student_router.get("/subjects/{subject_id}/chapters/", response=List[ChapterSchema])
def list_chapters(request, subject_id: int):
    """Get all chapters for a subject"""
    return Chapter.objects.filter(subject_id=subject_id, is_active=True).order_by('chapter_number')


# Student Session Management APIs
@multi_student_router.post("/sessions/create/", response=StudentSessionSchema)
def create_student_session(request, data: StudentSessionCreateSchema):
    """Create a new study session for authenticated student"""
    if not request.user.is_authenticated:
        return {"error": "Authentication required"}
    
    subject = get_object_or_404(Subject, id=data.subject_id)
    chapter = None
    if data.chapter_id:
        chapter = get_object_or_404(Chapter, id=data.chapter_id, subject=subject)
    
    # Create new session with proper relationships
    session = StudentSession.objects.create(
        student=request.user,
        subject=subject,
        chapter=chapter,
        session_type=data.session_type,
        session_name=data.session_name or f"{subject.name} {data.session_type}",
        total_questions_planned=data.total_questions_planned,
        time_limit_minutes=data.time_limit_minutes,
        status='ACTIVE'
    )
    
    return {
        "id": str(session.id),
        "student_username": session.student.username,
        "subject_name": session.subject.name,
        "chapter_name": session.chapter.name if session.chapter else None,
        "session_type": session.session_type,
        "session_name": session.session_name,
        "status": session.status,
        "current_question_number": session.current_question_number,
        "total_questions_planned": session.total_questions_planned,
        "session_start_time": session.session_start_time,
        "session_end_time": session.session_end_time,
        "questions_attempted": session.questions_attempted,
        "questions_correct": session.questions_correct,
        "questions_incorrect": session.questions_incorrect,
        "percentage_score": session.percentage_score,
        "current_difficulty_level": session.current_difficulty_level,
    }

@multi_student_router.get("/sessions/", response=List[StudentSessionSchema])
@paginate(PageNumberPagination, page_size=20)
def list_student_sessions(request, status: Optional[str] = None):
    """List sessions for authenticated student with optional status filter"""
    if not request.user.is_authenticated:
        return {"error": "Authentication required"}
    
    sessions = StudentSession.objects.filter(student=request.user)
    
    if status:
        sessions = sessions.filter(status=status.upper())
    
    sessions = sessions.select_related('subject', 'chapter', 'student').order_by('-session_start_time')
    
    result = []
    for session in sessions:
        result.append({
            "id": str(session.id),
            "student_username": session.student.username,
            "subject_name": session.subject.name,
            "chapter_name": session.chapter.name if session.chapter else None,
            "session_type": session.session_type,
            "session_name": session.session_name,
            "status": session.status,
            "current_question_number": session.current_question_number,
            "total_questions_planned": session.total_questions_planned,
            "session_start_time": session.session_start_time,
            "session_end_time": session.session_end_time,
            "questions_attempted": session.questions_attempted,
            "questions_correct": session.questions_correct,
            "questions_incorrect": session.questions_incorrect,
            "percentage_score": session.percentage_score,
            "current_difficulty_level": session.current_difficulty_level,
        })
    
    return result

@multi_student_router.get("/sessions/{session_id}/", response=StudentSessionSchema)
def get_student_session(request, session_id: str):
    """Get specific session details for authenticated student"""
    if not request.user.is_authenticated:
        return {"error": "Authentication required"}
    
    session = get_object_or_404(
        StudentSession.objects.select_related('subject', 'chapter', 'student'),
        id=session_id,
        student=request.user
    )
    
    return {
        "id": str(session.id),
        "student_username": session.student.username,
        "subject_name": session.subject.name,
        "chapter_name": session.chapter.name if session.chapter else None,
        "session_type": session.session_type,
        "session_name": session.session_name,
        "status": session.status,
        "current_question_number": session.current_question_number,
        "total_questions_planned": session.total_questions_planned,
        "session_start_time": session.session_start_time,
        "session_end_time": session.session_end_time,
        "questions_attempted": session.questions_attempted,
        "questions_correct": session.questions_correct,
        "questions_incorrect": session.questions_incorrect,
        "percentage_score": session.percentage_score,
        "current_difficulty_level": session.current_difficulty_level,
    }


# Question and Answer Management APIs
@multi_student_router.get("/sessions/{session_id}/next-question/")
def get_next_question(request, session_id: str):
    """Get next question for student session"""
    if not request.user.is_authenticated:
        return {"error": "Authentication required"}
    
    session = get_object_or_404(StudentSession, id=session_id, student=request.user, status='ACTIVE')
    
    # Get questions for this subject that haven't been attempted in this session
    attempted_questions = QuestionAttempt.objects.filter(
        session=session
    ).values_list('question_id', flat=True)
    
    available_questions = AdaptiveQuestion.objects.filter(
        subject=session.subject.code
    ).exclude(id__in=attempted_questions)
    
    if not available_questions.exists():
        return {"error": "No more questions available"}
    
    # Get next question based on current difficulty level
    question = available_questions.filter(
        difficulty_level=session.current_difficulty_level
    ).first()
    
    if not question:
        question = available_questions.first()
    
    # Update session progress
    session.current_question_number += 1
    session.save(update_fields=['current_question_number'])
    
    return {
        "question_id": question.id,
        "question_number": session.current_question_number,
        "question_text": question.question_text,
        "option_a": question.option_a,
        "option_b": question.option_b,
        "option_c": question.option_c,
        "option_d": question.option_d,
        "difficulty_level": question.difficulty_level,
        "subject": question.subject,
        "topic": question.topic,
        "chapter": question.chapter
    }

@multi_student_router.post("/sessions/{session_id}/submit-answer/", response=QuestionAttemptSchema)
def submit_answer(request, session_id: str, data: AnswerSubmissionSchema):
    """Submit answer for current question"""
    if not request.user.is_authenticated:
        return {"error": "Authentication required"}
    
    session = get_object_or_404(StudentSession, id=session_id, student=request.user, status='ACTIVE')
    question = get_object_or_404(AdaptiveQuestion, id=data.question_id)
    
    # Check if answer is correct
    is_correct = data.student_answer.upper() == question.correct_answer.upper()
    
    # Calculate points earned
    points_earned = 1.0 if is_correct else 0.0
    
    # Determine answer status
    answer_status = 'CORRECT' if is_correct else 'INCORRECT'
    if not data.student_answer:
        answer_status = 'SKIPPED'
    
    # Create question attempt record
    with transaction.atomic():
        attempt = QuestionAttempt.objects.create(
            session=session,
            question=question,
            student=request.user,
            question_number_in_session=session.current_question_number,
            student_answer=data.student_answer,
            correct_answer=question.correct_answer,
            answer_status=answer_status,
            is_correct=is_correct,
            time_spent_seconds=data.time_spent_seconds,
            difficulty_when_presented=session.current_difficulty_level,
            question_points=1.0,
            points_earned=points_earned,
            confidence_level=data.confidence_level,
            answer_submitted_at=timezone.now()
        )
        
        # Update session statistics
        session.questions_attempted += 1
        if is_correct:
            session.questions_correct += 1
        else:
            session.questions_incorrect += 1
        
        session.total_score += points_earned
        session.max_possible_score += 1.0
        session.percentage_score = (session.total_score / session.max_possible_score) * 100 if session.max_possible_score > 0 else 0
        
        session.save(update_fields=[
            'questions_attempted', 'questions_correct', 'questions_incorrect',
            'total_score', 'max_possible_score', 'percentage_score'
        ])
        
        # Update or create student progress
        progress, created = StudentProgress.objects.get_or_create(
            student=request.user,
            subject=session.subject,
            defaults={
                'total_sessions': 1,
                'total_questions_attempted': 1,
                'total_questions_correct': 1 if is_correct else 0,
                'current_accuracy_percentage': 100.0 if is_correct else 0.0,
                'best_accuracy_percentage': 100.0 if is_correct else 0.0,
                'last_session_date': timezone.now().date(),
                'last_question_answered_at': timezone.now(),
            }
        )
        
        if not created:
            progress.total_questions_attempted += 1
            if is_correct:
                progress.total_questions_correct += 1
            
            # Update accuracy percentage
            progress.current_accuracy_percentage = (
                progress.total_questions_correct / progress.total_questions_attempted
            ) * 100
            
            if progress.current_accuracy_percentage > progress.best_accuracy_percentage:
                progress.best_accuracy_percentage = progress.current_accuracy_percentage
            
            progress.last_question_answered_at = timezone.now()
            progress.save(update_fields=[
                'total_questions_attempted', 'total_questions_correct',
                'current_accuracy_percentage', 'best_accuracy_percentage',
                'last_question_answered_at'
            ])
        
        # Update daily stats
        today = timezone.now().date()
        daily_stats, created = DailyStudyStats.objects.get_or_create(
            student=request.user,
            study_date=today,
            defaults={
                'total_sessions': 1,
                'questions_attempted': 1,
                'questions_correct': 1 if is_correct else 0,
                'daily_accuracy_percentage': 100.0 if is_correct else 0.0,
            }
        )
        
        if not created:
            daily_stats.questions_attempted += 1
            if is_correct:
                daily_stats.questions_correct += 1
            
            daily_stats.daily_accuracy_percentage = (
                daily_stats.questions_correct / daily_stats.questions_attempted
            ) * 100
            
            daily_stats.save(update_fields=[
                'questions_attempted', 'questions_correct', 'daily_accuracy_percentage'
            ])
    
    return {
        "id": attempt.id,
        "session_id": str(attempt.session.id),
        "question_id": attempt.question.id,
        "student_username": attempt.student.username,
        "question_number_in_session": attempt.question_number_in_session,
        "student_answer": attempt.student_answer,
        "correct_answer": attempt.correct_answer,
        "answer_status": attempt.answer_status,
        "is_correct": attempt.is_correct,
        "time_spent_seconds": attempt.time_spent_seconds,
        "difficulty_when_presented": attempt.difficulty_when_presented,
        "points_earned": attempt.points_earned,
    }


# Progress Tracking APIs
@multi_student_router.get("/progress/", response=List[StudentProgressSchema])
def get_student_progress(request):
    """Get progress for all subjects for authenticated student"""
    if not request.user.is_authenticated:
        return {"error": "Authentication required"}
    
    progress_records = StudentProgress.objects.filter(
        student=request.user
    ).select_related('subject', 'student')
    
    result = []
    for progress in progress_records:
        result.append({
            "id": progress.id,
            "student_username": progress.student.username,
            "subject_name": progress.subject.name,
            "total_sessions": progress.total_sessions,
            "total_questions_attempted": progress.total_questions_attempted,
            "total_questions_correct": progress.total_questions_correct,
            "current_accuracy_percentage": progress.current_accuracy_percentage,
            "best_accuracy_percentage": progress.best_accuracy_percentage,
            "current_mastery_level": progress.current_mastery_level,
            "mastery_score": progress.mastery_score,
            "current_correct_streak": progress.current_correct_streak,
            "longest_correct_streak": progress.longest_correct_streak,
        })
    
    return result

@multi_student_router.get("/progress/{subject_id}/", response=StudentProgressSchema)
def get_subject_progress(request, subject_id: int):
    """Get progress for specific subject for authenticated student"""
    if not request.user.is_authenticated:
        return {"error": "Authentication required"}
    
    subject = get_object_or_404(Subject, id=subject_id)
    progress = get_object_or_404(StudentProgress, student=request.user, subject=subject)
    
    return {
        "id": progress.id,
        "student_username": progress.student.username,
        "subject_name": progress.subject.name,
        "total_sessions": progress.total_sessions,
        "total_questions_attempted": progress.total_questions_attempted,
        "total_questions_correct": progress.total_questions_correct,
        "current_accuracy_percentage": progress.current_accuracy_percentage,
        "best_accuracy_percentage": progress.best_accuracy_percentage,
        "current_mastery_level": progress.current_mastery_level,
        "mastery_score": progress.mastery_score,
        "current_correct_streak": progress.current_correct_streak,
        "longest_correct_streak": progress.longest_correct_streak,
    }

@multi_student_router.get("/daily-stats/", response=List[DailyStatsSchema])
def get_daily_stats(request, days: int = 7):
    """Get daily study statistics for authenticated student"""
    if not request.user.is_authenticated:
        return {"error": "Authentication required"}
    
    from datetime import timedelta
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days-1)
    
    daily_stats = DailyStudyStats.objects.filter(
        student=request.user,
        study_date__range=[start_date, end_date]
    ).select_related('student').order_by('-study_date')
    
    result = []
    for stats in daily_stats:
        result.append({
            "id": stats.id,
            "student_username": stats.student.username,
            "study_date": stats.study_date,
            "total_sessions": stats.total_sessions,
            "total_study_time_seconds": stats.total_study_time_seconds,
            "questions_attempted": stats.questions_attempted,
            "questions_correct": stats.questions_correct,
            "daily_accuracy_percentage": stats.daily_accuracy_percentage,
        })
    
    return result

@multi_student_router.post("/sessions/{session_id}/end/")
def end_session(request, session_id: str):
    """End current session for authenticated student"""
    if not request.user.is_authenticated:
        return {"error": "Authentication required"}
    
    session = get_object_or_404(StudentSession, id=session_id, student=request.user, status='ACTIVE')
    
    # Calculate session duration
    session.session_end_time = timezone.now()
    duration = session.session_end_time - session.session_start_time
    session.session_duration_seconds = int(duration.total_seconds())
    session.status = 'COMPLETED'
    
    session.save(update_fields=['session_end_time', 'session_duration_seconds', 'status'])
    
    # Update progress records
    progress = StudentProgress.objects.get(student=request.user, subject=session.subject)
    progress.total_sessions += 1
    progress.total_study_time_seconds += session.session_duration_seconds
    progress.last_session_date = timezone.now().date()
    progress.save(update_fields=['total_sessions', 'total_study_time_seconds', 'last_session_date'])
    
    # Update daily stats
    today = timezone.now().date()
    daily_stats = DailyStudyStats.objects.get(student=request.user, study_date=today)
    daily_stats.total_study_time_seconds += session.session_duration_seconds
    daily_stats.sessions_completed += 1
    daily_stats.save(update_fields=['total_study_time_seconds', 'sessions_completed'])
    
    return {
        "message": "Session ended successfully",
        "session_id": str(session.id),
        "duration_seconds": session.session_duration_seconds,
        "questions_attempted": session.questions_attempted,
        "questions_correct": session.questions_correct,
        "final_score": session.percentage_score
    }