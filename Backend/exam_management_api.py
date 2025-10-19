"""
Exam Management API - Admin interface for creating and managing scheduled exams
Builds on existing adaptive learning infrastructure
"""

from ninja import Router, Schema
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg
from django.db import transaction
from django.utils import timezone
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

from assessment.models import ExamSession, AdaptiveQuestion
from assessment.improved_models import Subject, Chapter, StudentSession, QuestionAttempt

# Router setup
exam_router = Router()

# Schema definitions
class ExamCreateSchema(Schema):
    exam_name: str
    subject_code: str
    chapter_ids: Optional[List[int]] = None  # None = all chapters
    scheduled_start_time: datetime
    duration_minutes: int
    question_count: int
    difficulty_progression: str = "adaptive"  # "adaptive", "fixed", "progressive"
    auto_submit: bool = True
    allow_review: bool = True
    description: Optional[str] = None

class ScheduledExamSchema(Schema):
    id: str
    exam_name: str
    subject_name: str
    subject_code: str
    chapters: List[str]  # chapter names
    scheduled_start_time: datetime
    scheduled_end_time: datetime
    duration_minutes: int
    question_count: int
    enrolled_students_count: int
    active_sessions_count: int
    completed_sessions_count: int
    status: str  # "upcoming", "active", "completed", "cancelled"
    created_at: datetime
    created_by: str

class ExamEnrollmentSchema(Schema):
    student_id: str
    student_name: str
    email: str
    enrollment_status: str  # "enrolled", "started", "completed", "absent"
    session_id: Optional[str] = None
    start_time: Optional[datetime] = None
    completion_time: Optional[datetime] = None
    score: Optional[float] = None
    questions_attempted: Optional[int] = None

class StudentExamSchema(Schema):
    id: str
    exam_name: str
    subject_name: str
    scheduled_start_time: datetime
    scheduled_end_time: datetime
    duration_minutes: int
    question_count: int
    status: str  # "upcoming", "available", "in_progress", "completed", "missed"
    description: Optional[str] = None
    can_start: bool
    time_until_start: Optional[int] = None  # minutes until start
    session_id: Optional[str] = None

class ExamStartResponse(Schema):
    success: bool
    message: str
    session_id: Optional[str] = None
    exam_config: Optional[Dict[str, Any]] = None

# Extended ExamSession model fields (will need migration)
class ScheduledExam(Schema):
    """Represents a scheduled exam configuration"""
    id: str = None
    exam_name: str = ""
    subject_code: str = ""
    chapter_ids: List[int] = []
    scheduled_start_time: datetime = None
    duration_minutes: int = 60
    question_count: int = 10
    enrolled_students: List[str] = []
    exam_config: Dict[str, Any] = {}
    created_by: str = ""
    status: str = "upcoming"

# ============================================================================
# Admin Exam Management Endpoints  
# ============================================================================

@exam_router.post("/admin/exams/create", response=ScheduledExamSchema)
def create_scheduled_exam(request, payload: ExamCreateSchema):
    """Create a new scheduled exam using existing adaptive infrastructure"""
    
    try:
        # Validate subject exists
        subject = get_object_or_404(Subject, code=payload.subject_code)
        
        # Validate chapters if specified
        chapters = []
        if payload.chapter_ids:
            chapters = Chapter.objects.filter(
                id__in=payload.chapter_ids, 
                subject=subject,
                is_active=True
            )
            if len(chapters) != len(payload.chapter_ids):
                return {"error": "Some chapters not found or inactive"}
        
        # Calculate end time
        scheduled_end_time = payload.scheduled_start_time + timedelta(minutes=payload.duration_minutes)
        
        # Create exam configuration (stored as JSON in exam_config field)
        exam_config = {
            "exam_name": payload.exam_name,
            "subject_code": payload.subject_code,
            "chapter_ids": payload.chapter_ids or [],
            "scheduled_start_time": payload.scheduled_start_time.isoformat(),
            "scheduled_end_time": scheduled_end_time.isoformat(),
            "duration_minutes": payload.duration_minutes,
            "question_count": payload.question_count,
            "difficulty_progression": payload.difficulty_progression,
            "auto_submit": payload.auto_submit,
            "allow_review": payload.allow_review,
            "description": payload.description,
            "enrolled_students": [],
            "created_by": request.user.username if hasattr(request, 'user') else "admin",
            "status": "upcoming"
        }
        
        # For now, create a template ExamSession (will need proper ScheduledExam model later)
        exam_id = str(uuid.uuid4())
        
        # Store in a simple way for now - create inactive ExamSession as template
        template_session = ExamSession.objects.create(
            id=exam_id,
            student_id=1,  # Placeholder, will need proper ScheduledExam model
            subject=payload.subject_code,
            assessment_mode='EXAM',
            status='TEMPLATE',  # Special status for exam templates
            ai_analysis_data=exam_config  # Store config here temporarily
        )
        
        return ScheduledExamSchema(
            id=exam_id,
            exam_name=payload.exam_name,
            subject_name=subject.name,
            subject_code=payload.subject_code,
            chapters=[ch.name for ch in chapters] if chapters else ["All Chapters"],
            scheduled_start_time=payload.scheduled_start_time,
            scheduled_end_time=scheduled_end_time,
            duration_minutes=payload.duration_minutes,
            question_count=payload.question_count,
            enrolled_students_count=0,
            active_sessions_count=0,
            completed_sessions_count=0,
            status="upcoming",
            created_at=timezone.now(),
            created_by=request.user.username if hasattr(request, 'user') else "admin"
        )
        
    except Exception as e:
        return {"error": f"Failed to create exam: {str(e)}"}

@exam_router.get("/admin/exams", response=List[ScheduledExamSchema])
def list_scheduled_exams(request):
    """List all scheduled exams with current status"""
    
    try:
        # Get exam templates (status='TEMPLATE')
        exam_templates = ExamSession.objects.filter(status='TEMPLATE').order_by('-started_at')
        
        exams = []
        for template in exam_templates:
            config = template.ai_analysis_data
            
            # Count enrolled students and sessions
            enrolled_count = len(config.get('enrolled_students', []))
            
            # Count actual exam sessions for this exam
            actual_sessions = ExamSession.objects.filter(
                subject=template.subject,
                assessment_mode='EXAM',
                started_at__gte=datetime.fromisoformat(config['scheduled_start_time'].replace('Z', '+00:00')) - timedelta(hours=1)
            ).exclude(status='TEMPLATE')
            
            active_count = actual_sessions.filter(status='ACTIVE').count()
            completed_count = actual_sessions.filter(status='COMPLETED').count()
            
            # Determine current status
            now = timezone.now()
            start_time = datetime.fromisoformat(config['scheduled_start_time'].replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(config['scheduled_end_time'].replace('Z', '+00:00'))
            
            if now < start_time:
                status = "upcoming"
            elif start_time <= now <= end_time:
                status = "active"
            elif now > end_time:
                status = "completed"
            else:
                status = config.get('status', 'upcoming')
            
            subject = Subject.objects.filter(code=config['subject_code']).first()
            
            exams.append(ScheduledExamSchema(
                id=str(template.id),
                exam_name=config['exam_name'],
                subject_name=subject.name if subject else config['subject_code'],
                subject_code=config['subject_code'],
                chapters=config.get('chapters', ["All Chapters"]),
                scheduled_start_time=start_time,
                scheduled_end_time=end_time,
                duration_minutes=config['duration_minutes'],
                question_count=config['question_count'],
                enrolled_students_count=enrolled_count,
                active_sessions_count=active_count,
                completed_sessions_count=completed_count,
                status=status,
                created_at=template.started_at,
                created_by=config.get('created_by', 'admin')
            ))
        
        return exams
        
    except Exception as e:
        return []

@exam_router.post("/admin/exams/{exam_id}/students/enroll")
def enroll_students_in_exam(request, exam_id: str, student_ids: List[str]):
    """Enroll multiple students in a scheduled exam"""
    
    try:
        # Get exam template
        exam_template = get_object_or_404(ExamSession, id=exam_id, status='TEMPLATE')
        config = exam_template.ai_analysis_data
        
        # Validate students exist
        students = User.objects.filter(id__in=student_ids)
        if len(students) != len(student_ids):
            return {"error": "Some students not found"}
        
        # Add students to enrolled list
        enrolled_students = config.get('enrolled_students', [])
        new_enrollments = []
        
        for student_id in student_ids:
            if student_id not in enrolled_students:
                enrolled_students.append(student_id)
                new_enrollments.append(student_id)
        
        # Update config
        config['enrolled_students'] = enrolled_students
        exam_template.ai_analysis_data = config
        exam_template.save()
        
        return {
            "success": True,
            "message": f"Enrolled {len(new_enrollments)} new students",
            "total_enrolled": len(enrolled_students)
        }
        
    except Exception as e:
        return {"error": f"Failed to enroll students: {str(e)}"}

@exam_router.get("/admin/exams/{exam_id}/enrollments", response=List[ExamEnrollmentSchema])
def get_exam_enrollments(request, exam_id: str):
    """Get all student enrollments for an exam"""
    
    try:
        exam_template = get_object_or_404(ExamSession, id=exam_id, status='TEMPLATE')
        config = exam_template.ai_analysis_data
        
        enrolled_student_ids = config.get('enrolled_students', [])
        students = User.objects.filter(id__in=enrolled_student_ids)
        
        # Get actual exam sessions
        start_time = datetime.fromisoformat(config['scheduled_start_time'].replace('Z', '+00:00'))
        actual_sessions = ExamSession.objects.filter(
            student__in=students,
            subject=exam_template.subject,
            assessment_mode='EXAM',
            started_at__gte=start_time - timedelta(hours=1)
        ).exclude(status='TEMPLATE')
        
        enrollments = []
        for student in students:
            session = actual_sessions.filter(student=student).first()
            
            enrollments.append(ExamEnrollmentSchema(
                student_id=str(student.id),
                student_name=f"{student.first_name} {student.last_name}".strip() or student.username,
                email=student.email,
                enrollment_status="completed" if session and session.status == 'COMPLETED' else 
                                "started" if session and session.status == 'ACTIVE' else "enrolled",
                session_id=str(session.id) if session else None,
                start_time=session.started_at if session else None,
                completion_time=session.completed_at if session else None,
                score=session.accuracy_rate * 100 if session else None,
                questions_attempted=session.questions_attempted if session else None
            ))
        
        return enrollments
        
    except Exception as e:
        return []

# ============================================================================
# Student Exam Endpoints
# ============================================================================

@exam_router.get("/student/{student_id}/scheduled-exams", response=List[StudentExamSchema])
def get_student_scheduled_exams(request, student_id: str):
    """Get all scheduled exams for a student"""
    
    try:
        student = get_object_or_404(User, id=student_id)
        
        # Get all exam templates where student is enrolled
        exam_templates = ExamSession.objects.filter(status='TEMPLATE')
        
        student_exams = []
        now = timezone.now()
        
        for template in exam_templates:
            config = template.ai_analysis_data
            enrolled_students = config.get('enrolled_students', [])
            
            # Check if student is enrolled
            if student_id not in enrolled_students:
                continue
            
            start_time = datetime.fromisoformat(config['scheduled_start_time'].replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(config['scheduled_end_time'].replace('Z', '+00:00'))
            
            # Check if student has already started this exam
            existing_session = ExamSession.objects.filter(
                student=student,
                subject=template.subject,
                assessment_mode='EXAM',
                started_at__gte=start_time - timedelta(hours=1)
            ).exclude(status='TEMPLATE').first()
            
            # Determine status and availability
            if existing_session:
                if existing_session.status == 'COMPLETED':
                    status = "completed"
                    can_start = False
                else:
                    status = "in_progress"
                    can_start = True
                session_id = str(existing_session.id)
            else:
                if now < start_time:
                    status = "upcoming"
                    can_start = False
                elif start_time <= now <= end_time:
                    status = "available"
                    can_start = True
                else:
                    status = "missed"
                    can_start = False
                session_id = None
            
            # Calculate time until start (in minutes)
            time_until_start = None
            if now < start_time:
                time_until_start = int((start_time - now).total_seconds() / 60)
            
            subject = Subject.objects.filter(code=config['subject_code']).first()
            
            student_exams.append(StudentExamSchema(
                id=str(template.id),
                exam_name=config['exam_name'],
                subject_name=subject.name if subject else config['subject_code'],
                scheduled_start_time=start_time,
                scheduled_end_time=end_time,
                duration_minutes=config['duration_minutes'],
                question_count=config['question_count'],
                status=status,
                description=config.get('description'),
                can_start=can_start,
                time_until_start=time_until_start,
                session_id=session_id
            ))
        
        return student_exams
        
    except Exception as e:
        return []

@exam_router.post("/student/{student_id}/exam/{exam_id}/start", response=ExamStartResponse)
def start_student_exam(request, student_id: str, exam_id: str):
    """Start an exam session for a student"""
    
    try:
        student = get_object_or_404(User, id=student_id)
        exam_template = get_object_or_404(ExamSession, id=exam_id, status='TEMPLATE')
        config = exam_template.ai_analysis_data
        
        # Validate student is enrolled
        if student_id not in config.get('enrolled_students', []):
            return ExamStartResponse(
                success=False,
                message="Student not enrolled in this exam"
            )
        
        # Check timing
        now = timezone.now()
        start_time = datetime.fromisoformat(config['scheduled_start_time'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(config['scheduled_end_time'].replace('Z', '+00:00'))
        
        if now < start_time:
            return ExamStartResponse(
                success=False,
                message=f"Exam has not started yet. Starts at {start_time.strftime('%Y-%m-%d %H:%M')}"
            )
        
        if now > end_time:
            return ExamStartResponse(
                success=False,
                message="Exam has already ended"
            )
        
        # Check if already started
        existing_session = ExamSession.objects.filter(
            student=student,
            subject=exam_template.subject,
            assessment_mode='EXAM',
            started_at__gte=start_time - timedelta(hours=1)
        ).exclude(status='TEMPLATE').first()
        
        if existing_session:
            if existing_session.status == 'COMPLETED':
                return ExamStartResponse(
                    success=False,
                    message="Exam already completed"
                )
            else:
                return ExamStartResponse(
                    success=True,
                    message="Resuming existing exam session",
                    session_id=str(existing_session.id),
                    exam_config=config
                )
        
        # Create new exam session
        with transaction.atomic():
            exam_session = ExamSession.objects.create(
                student=student,
                subject=config['subject_code'],
                assessment_mode='EXAM',
                status='ACTIVE',
                ai_analysis_data={
                    "exam_template_id": exam_id,
                    "exam_config": config,
                    "started_at": now.isoformat()
                }
            )
        
        return ExamStartResponse(
            success=True,
            message="Exam session started successfully",
            session_id=str(exam_session.id),
            exam_config=config
        )
        
    except Exception as e:
        return ExamStartResponse(
            success=False,
            message=f"Failed to start exam: {str(e)}"
        )


# ============================================================================
# Exam Session Management Endpoints
# ============================================================================

@exam_router.get("/session/{session_id}/status")
def get_exam_session_status(request, session_id: str):
    """Get current status of an exam session"""
    try:
        # Get the exam session
        exam_session = get_object_or_404(ExamSession, id=session_id)
        
        # Get exam config from ai_analysis_data
        exam_config = exam_session.ai_analysis_data.get('exam_config', {})
        
        if not exam_config:
            return {"error": "Exam configuration not found"}
        
        now = timezone.now()
        
        scheduled_start = datetime.fromisoformat(exam_config["scheduled_start_time"].replace('Z', '+00:00'))
        scheduled_end = datetime.fromisoformat(exam_config["scheduled_end_time"].replace('Z', '+00:00'))
        
        # Calculate time remaining
        time_remaining = max(0, int((scheduled_end - now).total_seconds()))
        
        # Determine status
        status = "active"
        if now > scheduled_end or time_remaining <= 0:
            status = "expired"
        elif now < scheduled_start:
            status = "not_started"
        elif exam_session.status == 'COMPLETED':
            status = "completed"
        
        return {
            "id": session_id,
            "exam_name": exam_config.get("exam_name", ""),
            "subject_name": exam_config.get("subject_code", ""),
            "duration_minutes": exam_config.get("duration_minutes", 60),
            "question_count": exam_config.get("question_count", 10),
            "started_at": scheduled_start.isoformat(),
            "ends_at": scheduled_end.isoformat(),
            "time_remaining_seconds": time_remaining,
            "current_question_index": 0,  # Would track from session data
            "questions_answered": 0,      # Would track from session data  
            "auto_submit": True,
            "status": status
        }
        
    except Exception as e:
        return {"error": f"Error getting session status: {str(e)}"}


@exam_router.post("/session/{session_id}/submit")
def submit_exam(request, session_id: str):
    """Submit exam manually"""
    try:
        exam_session = get_object_or_404(ExamSession, id=session_id)
        
        # Mark session as completed
        exam_session.status = 'COMPLETED'
        exam_session.completed_at = timezone.now()
        exam_session.save()
        
        # Calculate results (placeholder - would use actual scoring)
        return {
            "success": True,
            "message": "Exam submitted successfully",
            "score": 85,  # Placeholder
            "total_questions": 20,
            "correct_answers": 17,
            "session_id": session_id
        }
        
    except Exception as e:
        return {"success": False, "message": f"Error submitting exam: {str(e)}"}


@exam_router.post("/session/{session_id}/auto-submit")
def auto_submit_exam(request, session_id: str):
    """Auto-submit exam when time expires"""
    try:
        exam_session = get_object_or_404(ExamSession, id=session_id)
        
        # Mark session as completed with auto-submit flag
        exam_session.status = 'COMPLETED'
        exam_session.completed_at = timezone.now()
        
        # Add auto-submit info to analysis data
        if 'exam_results' not in exam_session.ai_analysis_data:
            exam_session.ai_analysis_data['exam_results'] = {}
        exam_session.ai_analysis_data['exam_results']['auto_submitted'] = True
        exam_session.ai_analysis_data['exam_results']['submission_reason'] = 'time_expired'
        
        exam_session.save()
        
        # Calculate results (placeholder - would use actual scoring)
        return {
            "success": True,
            "message": "Exam automatically submitted due to time expiration",
            "score": 82,  # Placeholder
            "total_questions": 20,
            "correct_answers": 16,
            "auto_submitted": True,
            "session_id": session_id
        }
        
    except Exception as e:
        return {"success": False, "message": f"Error auto-submitting exam: {str(e)}"}