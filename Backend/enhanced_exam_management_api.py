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

@enhanced_exam_router.post("/admin/exams/create")
def create_enhanced_exam(request, payload: EnhancedExamCreateSchema):
    """Create a new exam with enhanced subject/chapter selection"""
    
    try:
        with transaction.atomic():
            # Handle authentication - get a valid user
            if hasattr(request, 'user') and request.user.is_authenticated:
                creator = request.user
            else:
                # For testing purposes, use the first available user
                creator = User.objects.first()
                if not creator:
                    return {"error": "No users available. Please create a user first."}
            
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
            unique_code = f"EXAM_{uuid.uuid4().hex[:8].upper()}"
            # Ensure unique exam code
            while EnhancedExam.objects.filter(exam_code=unique_code).exists():
                unique_code = f"EXAM_{uuid.uuid4().hex[:8].upper()}"
            
            enhanced_exam = EnhancedExam.objects.create(
                exam_name=payload.exam_name,
                exam_code=payload.exam_code or unique_code,
                description=payload.description,
                created_by=creator,
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
            
            return {
                "success": True,
                "exam": {
                    "id": str(enhanced_exam.id),
                    "exam_name": enhanced_exam.exam_name,
                    "exam_code": enhanced_exam.exam_code,
                    "subject_name": subject.name,
                    "subject_code": subject.code,
                    "chapters": [chapter.name for chapter in chapters],
                    "scheduled_start_time": enhanced_exam.scheduled_start_time.isoformat() if enhanced_exam.scheduled_start_time else None,
                    "scheduled_end_time": enhanced_exam.scheduled_end_time.isoformat() if enhanced_exam.scheduled_end_time else None,
                    "duration_minutes": enhanced_exam.duration_minutes,
                    "question_count": enhanced_exam.total_questions,
                    "status": enhanced_exam.status.lower(),
                    "created_at": enhanced_exam.created_at.isoformat(),
                    "created_by": creator.username
                },
                "question_pool": {
                    "total_available": available_questions,
                    "selected_count": payload.question_count,
                    "difficulty_breakdown": difficulty_breakdown,
                    "estimated_duration": payload.duration_minutes
                },
                "message": f"Enhanced exam '{enhanced_exam.exam_name}' created successfully"
            }
            
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
            status__in=['DRAFT', 'SCHEDULED', 'ACTIVE'],  # Include DRAFT for testing
        ).filter(
            Q(scheduled_start_time__isnull=True) | Q(scheduled_start_time__lte=now + timedelta(hours=24))  # Include exams starting within 24 hours
        ).filter(
            Q(scheduled_end_time__isnull=True) | Q(scheduled_end_time__gte=now - timedelta(hours=1))  # Include exams that ended within 1 hour
        ).select_related('subject').prefetch_related('chapters')
        
        result = []
        for exam in available_exams:
            # Check if student has already taken this exam (only if authenticated)
            can_attempt = True
            if hasattr(request, 'user') and request.user.is_authenticated:
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

@enhanced_exam_router.get("/student/{student_id}/attempts")
def get_student_exam_attempts(request, student_id: str):
    """Get all exam attempts for a specific student"""
    
    try:
        # Get student attempts
        attempts = StudentExamAttempt.objects.filter(
            student__id=student_id
        ).select_related('exam', 'student').order_by('-started_at')
        
        result = []
        for attempt in attempts:
            result.append({
                "id": str(attempt.id),
                "exam_id": str(attempt.exam.id),
                "exam_name": attempt.exam.exam_name,
                "attempt_number": attempt.attempt_number,
                "status": attempt.status.lower(),
                "started_at": attempt.started_at.isoformat() if attempt.started_at else None,
                "submitted_at": attempt.submitted_at.isoformat() if attempt.submitted_at else None,
                "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None,
                "total_time_minutes": attempt.duration_minutes,
                "questions_attempted": attempt.questions_attempted,
                "questions_answered": attempt.questions_answered,
                "correct_answers": attempt.correct_answers,
                "final_score_percentage": float(attempt.final_score_percentage),
                "passed": attempt.passed,
                "grade": attempt.grade
            })
        
        return {"success": True, "data": result}
        
    except Exception as e:
        return {"error": f"Failed to fetch student attempts: {str(e)}"}

@enhanced_exam_router.get("/student/attempts/{attempt_id}")
def get_exam_attempt_details(request, attempt_id: str):
    """Get detailed information about a specific exam attempt"""
    
    try:
        attempt = StudentExamAttempt.objects.select_related('exam', 'student').get(id=attempt_id)
        
        # Get question attempts for this exam attempt
        question_attempts = ExamQuestionAttempt.objects.filter(
            exam_attempt=attempt
        ).select_related('question').order_by('question_number')
        
        questions = []
        for qa in question_attempts:
            questions.append({
                "question_id": str(qa.question.id),
                "question_number": qa.question_number,
                "question_text": qa.question.question_text,
                "correct_answer": qa.question.correct_answer,
                "selected_answer": qa.selected_answer,
                "is_correct": qa.is_correct,
                "time_spent_seconds": qa.time_spent_seconds,
                "answered_at": qa.answered_at.isoformat() if qa.answered_at else None
            })
        
        result = {
            "id": str(attempt.id),
            "exam": {
                "id": str(attempt.exam.id),
                "name": attempt.exam.exam_name,
                "description": attempt.exam.description,
                "total_questions": attempt.exam.total_questions,
                "duration_minutes": attempt.exam.duration_minutes
            },
            "attempt_number": attempt.attempt_number,
            "status": attempt.status.lower(),
            "started_at": attempt.started_at.isoformat() if attempt.started_at else None,
            "submitted_at": attempt.submitted_at.isoformat() if attempt.submitted_at else None,
            "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None,
            "duration_minutes": attempt.duration_minutes,
            "questions_attempted": attempt.questions_attempted,
            "questions_answered": attempt.questions_answered,
            "correct_answers": attempt.correct_answers,
            "final_score_percentage": float(attempt.final_score_percentage),
            "passed": attempt.passed,
            "grade": attempt.grade,
            "questions": questions
        }
        
        return {"success": True, "data": result}
        
    except StudentExamAttempt.DoesNotExist:
        return {"error": "Exam attempt not found"}
    except Exception as e:
        return {"error": f"Failed to fetch attempt details: {str(e)}"}

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

# ============================================================================
# Additional CRUD Operations for Admin
# ============================================================================

@enhanced_exam_router.put("/admin/exams/{exam_id}/update", response=EnhancedScheduledExamSchema)
def update_enhanced_exam(request, exam_id: str, payload: EnhancedExamCreateSchema):
    """Update an existing enhanced exam"""
    
    try:
        with transaction.atomic():
            exam = get_object_or_404(EnhancedExam, id=exam_id)
            
            # Check if user has permission to update
            if exam.created_by != request.user and not request.user.is_superuser:
                return {"error": "Permission denied. You can only update your own exams."}
            
            # Validate subject
            subject = get_object_or_404(Subject, id=payload.content_selection.subject_id, is_active=True)
            
            # Update exam fields
            exam.exam_name = payload.exam_name
            exam.description = payload.description
            exam.exam_type = 'PRACTICE' if payload.exam_type == 'practice' else 'MOCK_TEST'
            exam.difficulty_level = payload.difficulty_level or 'mixed'
            exam.total_questions = payload.question_count
            exam.duration_minutes = payload.duration_minutes
            exam.scheduled_start_time = payload.scheduled_start_time
            exam.scheduled_end_time = payload.scheduled_end_time
            exam.adaptive_mode = payload.adaptive_config.get('enabled', False) if payload.adaptive_config else False
            exam.shuffle_questions = payload.randomize_questions
            exam.allow_review = payload.allow_question_review
            exam.show_results_immediately = not payload.proctoring_enabled
            exam.passing_score_percentage = payload.passing_score or 60.0
            exam.subject = subject
            
            # Update chapters
            chapters = []
            if payload.content_selection.selection_type == "specific_chapters":
                if payload.content_selection.chapter_ids:
                    chapters = Chapter.objects.filter(
                        id__in=payload.content_selection.chapter_ids,
                        subject=subject,
                        is_active=True
                    )
            else:
                chapters = Chapter.objects.filter(subject=subject, is_active=True)
            
            exam.chapters.set(chapters)
            
            # Update metadata
            exam.metadata.update({
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
            })
            
            exam.save()
            
            return EnhancedScheduledExamSchema(
                id=str(exam.id),
                exam_name=exam.exam_name,
                subject_name=subject.name,
                subject_code=subject.code,
                chapters=[chapter.name for chapter in chapters],
                scheduled_start_time=exam.scheduled_start_time,
                scheduled_end_time=exam.scheduled_end_time,
                duration_minutes=exam.duration_minutes,
                question_count=exam.total_questions,
                content_selection=payload.content_selection.dict(),
                question_pool=ExamQuestionPoolSchema(
                    total_available=exam.total_questions,
                    selected_count=exam.total_questions,
                    difficulty_breakdown=exam.question_distribution,
                    chapter_breakdown={},
                    estimated_duration=exam.duration_minutes
                ),
                enrolled_students_count=len(exam.metadata.get('enrolled_students', [])),
                active_sessions_count=exam.student_attempts.filter(status='IN_PROGRESS').count(),
                completed_sessions_count=exam.student_attempts.filter(status='COMPLETED').count(),
                status=exam.status.lower(),
                created_at=exam.created_at,
                created_by=exam.created_by.username
            )
            
    except Exception as e:
        return {"error": f"Failed to update exam: {str(e)}"}

@enhanced_exam_router.delete("/admin/exams/{exam_id}/delete")
def delete_enhanced_exam(request, exam_id: str):
    """Delete an enhanced exam (soft delete if has attempts)"""
    
    try:
        exam = get_object_or_404(EnhancedExam, id=exam_id)
        
        # Check if user has permission to delete
        if exam.created_by != request.user and not request.user.is_superuser:
            return {"error": "Permission denied. You can only delete your own exams."}
        
        # Check if exam has student attempts
        has_attempts = exam.student_attempts.exists()
        
        if has_attempts:
            # Soft delete - mark as cancelled instead of actual deletion
            exam.status = 'CANCELLED'
            exam.save()
            message = f"Exam '{exam.exam_name}' has been cancelled (soft delete due to existing attempts)"
        else:
            # Hard delete - safe to remove completely
            exam_name = exam.exam_name
            exam.delete()
            message = f"Exam '{exam_name}' has been permanently deleted"
        
        return {
            "success": True,
            "message": message,
            "soft_delete": has_attempts
        }
        
    except Exception as e:
        return {"error": f"Failed to delete exam: {str(e)}"}

@enhanced_exam_router.get("/admin/exams/{exam_id}/details", response=EnhancedScheduledExamSchema)
def get_exam_details(request, exam_id: str):
    """Get detailed information about a specific exam"""
    
    try:
        exam = get_object_or_404(EnhancedExam, id=exam_id)
        
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
        
        return EnhancedScheduledExamSchema(
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
        )
        
    except Exception as e:
        return {"error": f"Failed to fetch exam details: {str(e)}"}

@enhanced_exam_router.post("/admin/exams/{exam_id}/activate")
def activate_exam(request, exam_id: str):
    """Activate a draft exam"""
    
    try:
        exam = get_object_or_404(EnhancedExam, id=exam_id)
        
        if exam.created_by != request.user and not request.user.is_superuser:
            return {"error": "Permission denied"}
        
        if exam.status != 'DRAFT':
            return {"error": f"Can only activate draft exams. Current status: {exam.status}"}
        
        exam.status = 'SCHEDULED'
        exam.save()
        
        return {
            "success": True,
            "message": f"Exam '{exam.exam_name}' has been activated",
            "exam_id": str(exam.id),
            "new_status": exam.status
        }
        
    except Exception as e:
        return {"error": f"Failed to activate exam: {str(e)}"}

# ============================================================================
# Additional Student Endpoints for Complete Exam Flow
# ============================================================================

@enhanced_exam_router.post("/student/attempts/{attempt_id}/submit")
def submit_exam_attempt(request, attempt_id: str):
    """Submit an exam attempt and calculate final score"""
    
    try:
        # Parse request body
        data = json.loads(request.body)
        answers = data.get('answers', [])  # List of {question_id, selected_answer}
        
        attempt = StudentExamAttempt.objects.get(id=attempt_id)
        
        if attempt.status != 'IN_PROGRESS':
            return {"error": "Cannot submit exam that is not in progress"}
        
        # Update question attempts with answers
        correct_count = 0
        answered_count = 0
        
        for answer_data in answers:
            question_id = answer_data.get('question_id')
            selected_answer = answer_data.get('selected_answer')
            
            if question_id and selected_answer:
                try:
                    question_attempt = ExamQuestionAttempt.objects.get(
                        exam_attempt=attempt,
                        question_id=question_id
                    )
                    
                    question_attempt.selected_answer = selected_answer
                    question_attempt.answered_at = timezone.now()
                    
                    # Check if answer is correct
                    if question_attempt.question.correct_answer == selected_answer:
                        question_attempt.is_correct = True
                        correct_count += 1
                    
                    question_attempt.save()
                    answered_count += 1
                    
                except ExamQuestionAttempt.DoesNotExist:
                    continue
        
        # Calculate final score
        total_questions = attempt.exam.total_questions
        score_percentage = (correct_count / total_questions * 100) if total_questions > 0 else 0
        
        # Update attempt
        attempt.status = 'COMPLETED'
        attempt.completed_at = timezone.now()
        attempt.submitted_at = timezone.now()
        attempt.questions_answered = answered_count
        attempt.correct_answers = correct_count
        attempt.final_score_percentage = score_percentage
        attempt.passed = score_percentage >= attempt.exam.passing_score_percentage
        
        # Assign grade based on score
        if score_percentage >= 90:
            attempt.grade = 'A'
        elif score_percentage >= 80:
            attempt.grade = 'B'
        elif score_percentage >= 70:
            attempt.grade = 'C'
        elif score_percentage >= 60:
            attempt.grade = 'D'
        else:
            attempt.grade = 'F'
        
        attempt.save()
        
        return {
            "success": True,
            "data": {
                "attempt_id": str(attempt.id),
                "status": "completed",
                "final_score_percentage": float(score_percentage),
                "correct_answers": correct_count,
                "total_questions": total_questions,
                "passed": attempt.passed,
                "grade": attempt.grade
            }
        }
        
    except StudentExamAttempt.DoesNotExist:
        return {"error": "Exam attempt not found"}
    except Exception as e:
        return {"error": f"Failed to submit exam: {str(e)}"}

@enhanced_exam_router.post("/student/attempts/{attempt_id}/answer")
def save_exam_answer(request, attempt_id: str):
    """Save a single answer during exam (for auto-save functionality)"""
    
    try:
        data = json.loads(request.body)
        question_id = data.get('question_id')
        selected_answer = data.get('selected_answer')
        time_spent = data.get('time_spent_seconds', 0)
        
        attempt = StudentExamAttempt.objects.get(id=attempt_id)
        
        if attempt.status != 'IN_PROGRESS':
            return {"error": "Cannot save answer for exam that is not in progress"}
        
        # Update question attempt
        question_attempt = ExamQuestionAttempt.objects.get(
            exam_attempt=attempt,
            question_id=question_id
        )
        
        question_attempt.selected_answer = selected_answer
        question_attempt.time_spent_seconds = time_spent
        question_attempt.answered_at = timezone.now()
        
        # Check if answer is correct
        question_attempt.is_correct = (
            question_attempt.question.correct_answer == selected_answer
        )
        
        question_attempt.save()
        
        return {"success": True, "message": "Answer saved successfully"}
        
    except (StudentExamAttempt.DoesNotExist, ExamQuestionAttempt.DoesNotExist):
        return {"error": "Exam attempt or question not found"}
    except Exception as e:
        return {"error": f"Failed to save answer: {str(e)}"}

@enhanced_exam_router.get("/admin/exams/analytics")
def get_enhanced_exam_analytics(request):
    """Get comprehensive analytics for all enhanced exams"""
    
    try:
        # Basic exam statistics
        total_exams = EnhancedExam.objects.count()
        active_exams = EnhancedExam.objects.filter(status='SCHEDULED').count()
        draft_exams = EnhancedExam.objects.filter(status='DRAFT').count()
        cancelled_exams = EnhancedExam.objects.filter(status='CANCELLED').count()
        
        # Attempt statistics
        total_attempts = StudentExamAttempt.objects.count()
        completed_attempts = StudentExamAttempt.objects.filter(status='COMPLETED').count()
        in_progress_attempts = StudentExamAttempt.objects.filter(status='IN_PROGRESS').count()
        
        # Performance statistics
        if completed_attempts > 0:
            avg_score = StudentExamAttempt.objects.filter(
                status='COMPLETED'
            ).aggregate(avg_score=Avg('final_score_percentage'))['avg_score']
            
            passed_attempts = StudentExamAttempt.objects.filter(
                status='COMPLETED',
                passed=True
            ).count()
            
            pass_rate = (passed_attempts / completed_attempts) * 100
        else:
            avg_score = 0
            pass_rate = 0
        
        # Recent activity (last 7 days)
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_exams = EnhancedExam.objects.filter(created_at__gte=seven_days_ago).count()
        recent_attempts = StudentExamAttempt.objects.filter(started_at__gte=seven_days_ago).count()
        
        # Subject-wise breakdown
        subject_stats = []
        subjects_with_exams = Subject.objects.filter(
            enhanced_exams__isnull=False
        ).distinct()
        
        for subject in subjects_with_exams:
            subject_exam_count = subject.enhanced_exams.count()
            subject_attempts = StudentExamAttempt.objects.filter(
                exam__subject=subject
            ).count()
            
            subject_stats.append({
                "subject_name": subject.name,
                "subject_code": subject.code,
                "exam_count": subject_exam_count,
                "total_attempts": subject_attempts
            })
        
        return {
            "success": True,
            "data": {
                "exam_statistics": {
                    "total_exams": total_exams,
                    "active_exams": active_exams,
                    "draft_exams": draft_exams,
                    "cancelled_exams": cancelled_exams
                },
                "attempt_statistics": {
                    "total_attempts": total_attempts,
                    "completed_attempts": completed_attempts,
                    "in_progress_attempts": in_progress_attempts
                },
                "performance_statistics": {
                    "average_score_percentage": round(float(avg_score or 0), 2),
                    "pass_rate_percentage": round(pass_rate, 2),
                    "total_passed": StudentExamAttempt.objects.filter(
                        status='COMPLETED',
                        passed=True
                    ).count()
                },
                "recent_activity": {
                    "new_exams_last_7_days": recent_exams,
                    "new_attempts_last_7_days": recent_attempts
                },
                "subject_breakdown": subject_stats,
                "generated_at": timezone.now().isoformat()
            }
        }
        
    except Exception as e:
        return {"error": f"Failed to generate analytics: {str(e)}"}