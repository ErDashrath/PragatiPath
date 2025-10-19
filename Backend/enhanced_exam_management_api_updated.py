"""
Enhanced Exam Management API - Updated for New Enhanced Exam Schema
Uses the new EnhancedExam, StudentExamAttempt, ExamQuestionAttempt models
"""

from ninja import Router, Schema
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg, Sum, Case, When, IntegerField
from django.db import transaction
from django.utils import timezone
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

# Import NEW Enhanced Exam Models
from assessment.models import (
    EnhancedExam, 
    StudentExamAttempt, 
    ExamQuestionAttempt, 
    EnhancedExamAnalytics,
    AdaptiveQuestion
)
from assessment.improved_models import Subject, Chapter, StudentSession, QuestionAttempt
from core.models import StudentProfile

# Router setup
enhanced_exam_router = Router()

# ============================================================================
# Enhanced Schemas for Dynamic Subject/Chapter Selection
# ============================================================================

class ChapterInfoSchema(Schema):
    """Detailed chapter information for exam creation"""
    id: int
    name: str
    chapter_number: int
    description: str
    question_count: int = 0
    difficulty_distribution: Dict[str, int] = {}
    avg_difficulty: float = 0.0
    estimated_time_minutes: int = 0

class SubjectDetailsSchema(Schema):
    """Comprehensive subject information with analytics"""
    id: int
    code: str
    name: str
    description: str
    total_questions: int = 0
    chapters: List[ChapterInfoSchema] = []
    difficulty_distribution: Dict[str, int] = {}
    question_types: List[str] = []
    avg_response_time: float = 0.0
    success_rate: float = 0.0

class ExamContentSelection(Schema):
    """Defines what content to include in the exam"""
    subject_id: int
    selection_type: str  # "full_subject", "specific_chapters"
    chapter_ids: Optional[List[int]] = None
    difficulty_levels: Optional[List[str]] = None
    question_types: Optional[List[str]] = None
    include_adaptive: bool = False

class ExamQuestionPoolSchema(Schema):
    """Information about the question pool for the exam"""
    total_available: int = 0
    selected_count: int = 0
    difficulty_breakdown: Dict[str, int] = {}
    chapter_breakdown: Dict[str, int] = {}
    estimated_duration: int = 0

class EnhancedExamCreateSchema(Schema):
    """Schema for creating enhanced exams"""
    exam_name: str
    exam_code: Optional[str] = None
    description: str = ""
    exam_type: str = "practice"  # practice, mock_test, chapter_test, full_test
    difficulty_level: Optional[str] = "mixed"
    duration_minutes: int = 60
    question_count: int = 10
    content_selection: ExamContentSelection
    adaptive_config: Optional[Dict[str, Any]] = None
    randomize_questions: bool = True
    allow_question_navigation: bool = True
    show_question_feedback: bool = False
    allow_question_review: bool = True
    auto_submit_on_expiry: bool = True
    proctoring_enabled: bool = False
    detailed_analytics: bool = True
    passing_score: Optional[float] = 60.0
    scheduled_start_time: Optional[datetime] = None
    scheduled_end_time: Optional[datetime] = None

class EnhancedScheduledExamSchema(Schema):
    """Response schema for scheduled exams"""
    id: str
    exam_name: str
    subject_name: str
    subject_code: str
    chapters: List[str] = []
    scheduled_start_time: Optional[datetime] = None
    scheduled_end_time: Optional[datetime] = None
    duration_minutes: int
    question_count: int
    content_selection: Optional[Dict[str, Any]] = {}
    question_pool: ExamQuestionPoolSchema
    enrolled_students_count: int = 0
    active_sessions_count: int = 0
    completed_sessions_count: int = 0
    status: str = "draft"
    created_at: datetime
    created_by: str

class StudentExamAttemptSchema(Schema):
    """Schema for student exam attempts"""
    id: str
    student_name: str
    student_username: str
    attempt_number: int
    status: str
    started_at: Optional[datetime]
    submitted_at: Optional[datetime]
    total_time_minutes: float = 0.0
    questions_attempted: int = 0
    questions_answered: int = 0
    correct_answers: int = 0
    final_score_percentage: float = 0.0
    passed: bool = False
    grade: str = ""

class ExamAnalyticsSchema(Schema):
    """Schema for exam analytics"""
    total_attempts: int = 0
    completed_attempts: int = 0
    average_score: float = 0.0
    pass_rate: float = 0.0
    average_time_minutes: float = 0.0
    difficulty_performance: Dict[str, float] = {}
    question_analytics: List[Dict[str, Any]] = []

# ============================================================================
# Admin Endpoints - Enhanced Exam Management
# ============================================================================

@enhanced_exam_router.get("/admin/subjects/details", response=List[SubjectDetailsSchema])
def get_subjects_with_details(request):
    """Get all subjects with detailed analytics for exam creation"""
    
    try:
        subjects = Subject.objects.filter(is_active=True).prefetch_related('chapters')
        result = []
        
        for subject in subjects:
            # Get chapters with question counts
            chapters_data = []
            for chapter in subject.chapters.filter(is_active=True):
                # Count questions for this chapter
                question_count = AdaptiveQuestion.objects.filter(
                    Q(chapter=chapter) | Q(chapter_id=chapter.id),
                    is_active=True
                ).count()
                
                # Get difficulty distribution
                difficulty_dist = AdaptiveQuestion.objects.filter(
                    Q(chapter=chapter) | Q(chapter_id=chapter.id),
                    is_active=True
                ).values('difficulty_level').annotate(count=Count('id'))
                
                diff_breakdown = {}
                for item in difficulty_dist:
                    diff_breakdown[item['difficulty_level']] = item['count']
                
                chapters_data.append(ChapterInfoSchema(
                    id=chapter.id,
                    name=chapter.name,
                    chapter_number=chapter.chapter_number,
                    description=chapter.description or "",
                    question_count=question_count,
                    difficulty_distribution=diff_breakdown,
                    estimated_time_minutes=question_count * 2  # Rough estimate
                ))
            
            # Subject-level analytics
            total_questions = AdaptiveQuestion.objects.filter(
                Q(subject_fk=subject) | Q(subject=subject.code),
                is_active=True
            ).count()
            
            # Difficulty distribution for subject
            subject_difficulty_dist = AdaptiveQuestion.objects.filter(
                Q(subject_fk=subject) | Q(subject=subject.code),
                is_active=True
            ).values('difficulty_level').annotate(count=Count('id'))
            
            subject_diff_breakdown = {}
            for item in subject_difficulty_dist:
                subject_diff_breakdown[item['difficulty_level']] = item['count']
            
            # Question types
            question_types = list(AdaptiveQuestion.objects.filter(
                Q(subject_fk=subject) | Q(subject=subject.code),
                is_active=True
            ).values_list('question_type', flat=True).distinct())
            
            result.append(SubjectDetailsSchema(
                id=subject.id,
                code=subject.code,
                name=subject.name,
                description=subject.description or "",
                total_questions=total_questions,
                chapters=chapters_data,
                difficulty_distribution=subject_diff_breakdown,
                question_types=question_types,
                avg_response_time=0.0,  # Would need historical data
                success_rate=0.0  # Would need historical data
            ))
        
        return result
        
    except Exception as e:
        return {"error": f"Failed to fetch subjects: {str(e)}"}

@enhanced_exam_router.post("/admin/exams/create", response=EnhancedScheduledExamSchema)
def create_enhanced_exam(request, payload: EnhancedExamCreateSchema):
    """Create a new exam with enhanced subject/chapter selection"""
    
    try:
        with transaction.atomic():
            # Validate subject
            subject = get_object_or_404(Subject, id=payload.content_selection.subject_id, is_active=True)
            
            # Validate and get chapters
            chapters = []
            if payload.content_selection.selection_type == "specific_chapters":
                if not payload.content_selection.chapter_ids:
                    return {"error": "Chapter IDs required for specific_chapters selection"}
                
                chapters = Chapter.objects.filter(
                    id__in=payload.content_selection.chapter_ids,
                    subject=subject,
                    is_active=True
                )
                if len(chapters) != len(payload.content_selection.chapter_ids):
                    return {"error": "Some specified chapters not found or inactive"}
            else:
                # Get all chapters for the subject
                chapters = Chapter.objects.filter(subject=subject, is_active=True)
            
            # Validate question availability
            questions_filter = Q(is_active=True) & (Q(subject_fk=subject) | Q(subject=subject.code))
            
            if payload.content_selection.selection_type == "specific_chapters":
                questions_filter &= Q(chapter__in=chapters)
            
            if payload.content_selection.difficulty_levels:
                questions_filter &= Q(difficulty_level__in=payload.content_selection.difficulty_levels)
            
            if payload.content_selection.question_types:
                questions_filter &= Q(question_type__in=payload.content_selection.question_types)
            
            available_questions = AdaptiveQuestion.objects.filter(questions_filter).count()
            
            if available_questions < payload.question_count:
                return {"error": f"Only {available_questions} questions available with current selection criteria. Requested: {payload.question_count}"}
            
            # Calculate difficulty breakdown
            difficulty_breakdown = {}
            diff_dist = AdaptiveQuestion.objects.filter(questions_filter).values('difficulty_level').annotate(count=Count('id'))
            for item in diff_dist:
                difficulty_breakdown[item['difficulty_level']] = item['count']
            
            # Create enhanced exam using NEW schema
            enhanced_exam = EnhancedExam.objects.create(
                exam_name=payload.exam_name,
                exam_code=payload.exam_code or f"EXAM_{uuid.uuid4().hex[:8].upper()}",
                description=payload.description,
                created_by=request.user,
                subject=subject,
                exam_type='PRACTICE' if payload.exam_type == 'practice' else 'MOCK_TEST',
                difficulty_level=payload.difficulty_level or 'mixed',
                total_questions=payload.question_count,
                duration_minutes=payload.duration_minutes,
                scheduled_start_time=payload.scheduled_start_time,
                scheduled_end_time=payload.scheduled_end_time,
                adaptive_mode=payload.adaptive_config.get('enabled', False) if payload.adaptive_config else False,
                shuffle_questions=payload.randomize_questions,
                allow_review=payload.allow_question_review,
                show_results_immediately=not payload.proctoring_enabled,
                max_attempts_per_student=1,
                passing_score_percentage=payload.passing_score or 60.0,
                question_distribution=difficulty_breakdown,
                content_selection={
                    "chapters": [ch.id for ch in chapters] if chapters else [],
                    "difficulty_distribution": difficulty_breakdown,
                    "selection_criteria": payload.content_selection.dict()
                },
                metadata={
                    "exam_settings": {
                        "randomize_questions": payload.randomize_questions,
                        "allow_question_navigation": payload.allow_question_navigation,
                        "show_question_feedback": payload.show_question_feedback,
                        "allow_question_review": payload.allow_question_review,
                        "auto_submit_on_expiry": payload.auto_submit_on_expiry,
                        "proctoring_enabled": payload.proctoring_enabled,
                        "detailed_analytics": payload.detailed_analytics
                    },
                    "adaptive_settings": payload.adaptive_config or {}
                }
            )
            
            # Add selected chapters to the exam
            if chapters:
                enhanced_exam.chapters.set(chapters)
            
            # Calculate question pool for response
            question_pool = ExamQuestionPoolSchema(
                total_available=available_questions,
                selected_count=payload.question_count,
                difficulty_breakdown=difficulty_breakdown,
                chapter_breakdown={},
                estimated_duration=payload.duration_minutes
            )
            
            return EnhancedScheduledExamSchema(
                id=str(enhanced_exam.id),
                exam_name=enhanced_exam.exam_name,
                subject_name=subject.name,
                subject_code=subject.code,
                chapters=[chapter.name for chapter in chapters],
                scheduled_start_time=enhanced_exam.scheduled_start_time,
                scheduled_end_time=enhanced_exam.scheduled_end_time,
                duration_minutes=enhanced_exam.duration_minutes,
                question_count=enhanced_exam.total_questions,
                content_selection=payload.content_selection.dict(),
                question_pool=question_pool,
                enrolled_students_count=0,
                active_sessions_count=0,
                completed_sessions_count=0,
                status=enhanced_exam.status.lower(),
                created_at=enhanced_exam.created_at,
                created_by=enhanced_exam.created_by.username
            )
            
    except Exception as e:
        return {"error": f"Failed to create exam: {str(e)}"}

@enhanced_exam_router.get("/admin/exams/list", response=List[EnhancedScheduledExamSchema])
def list_enhanced_exams(request):
    """List all enhanced scheduled exams with analytics"""
    
    try:
        enhanced_exams = EnhancedExam.objects.select_related(
            'subject', 'created_by'
        ).prefetch_related(
            'chapters', 'student_attempts'
        ).order_by('-created_at')
        
        result = []
        for exam in enhanced_exams:
            # Calculate current statistics
            active_sessions = exam.student_attempts.filter(status='IN_PROGRESS').count()
            completed_sessions = exam.student_attempts.filter(status='COMPLETED').count()
            
            # Determine status
            now = timezone.now()
            if exam.status == 'DRAFT':
                status = 'draft'
            elif exam.status == 'SCHEDULED':
                if exam.scheduled_start_time and now < exam.scheduled_start_time:
                    status = 'upcoming'
                elif exam.scheduled_end_time and now > exam.scheduled_end_time:
                    status = 'expired'
                else:
                    status = 'active'
            else:
                status = exam.status.lower()
            
            result.append(EnhancedScheduledExamSchema(
                id=str(exam.id),
                exam_name=exam.exam_name,
                subject_name=exam.subject.name,
                subject_code=exam.subject.code,
                chapters=[chapter.name for chapter in exam.chapters.all()],
                scheduled_start_time=exam.scheduled_start_time,
                scheduled_end_time=exam.scheduled_end_time,
                duration_minutes=exam.duration_minutes,
                question_count=exam.total_questions,
                content_selection=exam.content_selection,
                question_pool=ExamQuestionPoolSchema(
                    total_available=exam.total_questions,
                    selected_count=exam.total_questions,
                    difficulty_breakdown=exam.question_distribution,
                    chapter_breakdown={},
                    estimated_duration=exam.duration_minutes
                ),
                enrolled_students_count=len(exam.metadata.get('enrolled_students', [])),
                active_sessions_count=active_sessions,
                completed_sessions_count=completed_sessions,
                status=status,
                created_at=exam.created_at,
                created_by=exam.created_by.username
            ))
        
        return result
        
    except Exception as e:
        return {"error": f"Failed to list exams: {str(e)}"}

@enhanced_exam_router.get("/admin/exams/{exam_id}/attempts", response=List[StudentExamAttemptSchema])
def get_exam_attempts(request, exam_id: str):
    """Get all student attempts for a specific exam"""
    
    try:
        exam = get_object_or_404(EnhancedExam, id=exam_id)
        attempts = exam.student_attempts.select_related('student', 'student_profile').order_by('-started_at')
        
        result = []
        for attempt in attempts:
            result.append(StudentExamAttemptSchema(
                id=str(attempt.id),
                student_name=f"{attempt.student.first_name} {attempt.student.last_name}".strip() or attempt.student.username,
                student_username=attempt.student.username,
                attempt_number=attempt.attempt_number,
                status=attempt.status.lower(),
                started_at=attempt.started_at,
                submitted_at=attempt.submitted_at,
                total_time_minutes=attempt.duration_minutes,
                questions_attempted=attempt.questions_attempted,
                questions_answered=attempt.questions_answered,
                correct_answers=attempt.correct_answers,
                final_score_percentage=float(attempt.final_score_percentage),
                passed=attempt.passed,
                grade=attempt.grade
            ))
        
        return result
        
    except Exception as e:
        return {"error": f"Failed to fetch exam attempts: {str(e)}"}

@enhanced_exam_router.get("/admin/exams/{exam_id}/analytics", response=ExamAnalyticsSchema)
def get_exam_analytics(request, exam_id: str):
    """Get comprehensive analytics for a specific exam"""
    
    try:
        exam = get_object_or_404(EnhancedExam, id=exam_id)
        attempts = exam.student_attempts.filter(status='COMPLETED')
        
        if not attempts.exists():
            return ExamAnalyticsSchema()
        
        # Basic statistics
        total_attempts = exam.student_attempts.count()
        completed_attempts = attempts.count()
        average_score = attempts.aggregate(avg=Avg('final_score_percentage'))['avg'] or 0.0
        pass_rate = (attempts.filter(passed=True).count() / completed_attempts * 100) if completed_attempts > 0 else 0.0
        average_time = attempts.aggregate(avg=Avg('total_time_spent_seconds'))['avg'] or 0.0
        average_time_minutes = average_time / 60 if average_time else 0.0
        
        # Question-level analytics
        question_attempts = ExamQuestionAttempt.objects.filter(
            exam_attempt__exam=exam,
            exam_attempt__status='COMPLETED'
        ).select_related('question')
        
        question_analytics = []
        question_stats = question_attempts.values(
            'question_id', 'question__question_text'
        ).annotate(
            total_attempts=Count('id'),
            correct_count=Count(Case(When(is_correct=True, then=1))),
            avg_time=Avg('total_time_spent_seconds')
        )
        
        for stat in question_stats:
            accuracy = (stat['correct_count'] / stat['total_attempts'] * 100) if stat['total_attempts'] > 0 else 0.0
            question_analytics.append({
                'question_id': stat['question_id'],
                'question_text': stat['question__question_text'][:100] + '...' if len(stat['question__question_text']) > 100 else stat['question__question_text'],
                'total_attempts': stat['total_attempts'],
                'accuracy_percentage': round(accuracy, 2),
                'average_time_seconds': round(stat['avg_time'] or 0, 2)
            })
        
        return ExamAnalyticsSchema(
            total_attempts=total_attempts,
            completed_attempts=completed_attempts,
            average_score=round(average_score, 2),
            pass_rate=round(pass_rate, 2),
            average_time_minutes=round(average_time_minutes, 2),
            difficulty_performance={},  # Could be enhanced with difficulty analysis
            question_analytics=question_analytics
        )
        
    except Exception as e:
        return {"error": f"Failed to fetch exam analytics: {str(e)}"}

# ============================================================================
# Student Endpoints - Taking Exams
# ============================================================================

@enhanced_exam_router.get("/student/exams/available", response=List[EnhancedScheduledExamSchema])
def get_available_exams(request):
    """Get all available exams for students"""
    
    try:
        now = timezone.now()
        available_exams = EnhancedExam.objects.filter(
            status__in=['SCHEDULED', 'ACTIVE'],
        ).filter(
            Q(scheduled_start_time__isnull=True) | Q(scheduled_start_time__lte=now)
        ).filter(
            Q(scheduled_end_time__isnull=True) | Q(scheduled_end_time__gte=now)
        ).select_related('subject').prefetch_related('chapters')
        
        result = []
        for exam in available_exams:
            # Check if student has already taken this exam
            attempts_count = exam.student_attempts.filter(student=request.user).count()
            can_attempt = attempts_count < exam.max_attempts_per_student
            
            if can_attempt:
                result.append(EnhancedScheduledExamSchema(
                    id=str(exam.id),
                    exam_name=exam.exam_name,
                    subject_name=exam.subject.name,
                    subject_code=exam.subject.code,
                    chapters=[chapter.name for chapter in exam.chapters.all()],
                    scheduled_start_time=exam.scheduled_start_time,
                    scheduled_end_time=exam.scheduled_end_time,
                    duration_minutes=exam.duration_minutes,
                    question_count=exam.total_questions,
                    content_selection=exam.content_selection,
                    question_pool=ExamQuestionPoolSchema(
                        total_available=exam.total_questions,
                        selected_count=exam.total_questions,
                        difficulty_breakdown=exam.question_distribution,
                        chapter_breakdown={},
                        estimated_duration=exam.duration_minutes
                    ),
                    enrolled_students_count=0,
                    active_sessions_count=0,
                    completed_sessions_count=0,
                    status='available',
                    created_at=exam.created_at,
                    created_by=exam.created_by.username
                ))
        
        return result
        
    except Exception as e:
        return {"error": f"Failed to fetch available exams: {str(e)}"}

@enhanced_exam_router.post("/student/exams/{exam_id}/start")
def start_exam_attempt(request, exam_id: str):
    """Start a new exam attempt for the student"""
    
    try:
        exam = get_object_or_404(EnhancedExam, id=exam_id)
        
        # Check if exam is available
        now = timezone.now()
        if exam.scheduled_start_time and now < exam.scheduled_start_time:
            return {"error": "Exam has not started yet"}
        
        if exam.scheduled_end_time and now > exam.scheduled_end_time:
            return {"error": "Exam has ended"}
        
        # Check attempt limits
        existing_attempts = exam.student_attempts.filter(student=request.user).count()
        if existing_attempts >= exam.max_attempts_per_student:
            return {"error": f"Maximum attempts ({exam.max_attempts_per_student}) reached"}
        
        # Get or create student profile
        student_profile, created = StudentProfile.objects.get_or_create(user=request.user)
        
        # Create new attempt
        with transaction.atomic():
            attempt = StudentExamAttempt.objects.create(
                student_profile=student_profile,
                student=request.user,
                exam=exam,
                attempt_number=existing_attempts + 1,
                total_questions=exam.total_questions,
                started_at=now,
                status='IN_PROGRESS'
            )
        
        return {
            "success": True,
            "attempt_id": str(attempt.id),
            "exam_name": exam.exam_name,
            "duration_minutes": exam.duration_minutes,
            "total_questions": exam.total_questions,
            "message": f"Exam attempt started successfully. You have {exam.duration_minutes} minutes to complete."
        }
        
    except Exception as e:
        return {"error": f"Failed to start exam: {str(e)}"}