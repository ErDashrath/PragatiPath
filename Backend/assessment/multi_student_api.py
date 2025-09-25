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


# Health Check for API
@multi_student_router.get("/health/")
def health_check(request):
    """Health check endpoint for multi-student API"""
    return {
        "status": "ok",
        "message": "Multi-student API is running",
        "timestamp": timezone.now().isoformat()
    }