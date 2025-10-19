"""
Enhanced Exam Management API with Industry-Standard Broadcasting
Provides comprehensive exam scheduling, real-time notifications, and student management
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from ninja import Router, Schema
from ninja.errors import HttpError
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg
from django.core.cache import cache

from enhanced_exam_management_models import (
    EnhancedExam, StudentExamAttempt, ExamNotification, 
    ExamAnalytics, ExamSession, ExamStatus, NotificationType
)
from exam_broadcasting_service import get_broadcasting_service
from core.models import StudentProfile
from assessment.models import Subject, Chapter

logger = logging.getLogger(__name__)

# Router setup
enhanced_router = Router()

# ============================================================================
# Request/Response Schemas
# ============================================================================

class ExamScheduleSchema(Schema):
    """Schema for creating scheduled exams"""
    exam_name: str
    description: Optional[str] = ""
    subject_id: int
    chapter_ids: Optional[List[int]] = []
    
    # Scheduling
    scheduled_start_time: datetime
    duration_minutes: int
    
    # Question Configuration
    question_count: int
    difficulty_levels: Optional[List[str]] = ["easy", "medium", "hard"]
    
    # Enrollment
    auto_assign_all_active: bool = True
    enrolled_student_ids: Optional[List[str]] = []
    max_attempts_per_student: int = 1
    
    # Exam Settings
    randomize_questions: bool = True
    allow_question_navigation: bool = True
    show_question_feedback: bool = False
    auto_submit_on_expiry: bool = True
    passing_score: float = 60.0
    
    # Notifications
    send_notifications: bool = True
    reminder_times: Optional[List[int]] = [60, 30, 10]  # Minutes before start


class ExamResponseSchema(Schema):
    """Response schema for exam creation/updates"""
    id: str
    exam_name: str
    exam_code: str
    subject_name: str
    status: str
    scheduled_start_time: Optional[datetime]
    scheduled_end_time: Optional[datetime]
    duration_minutes: int
    question_count: int
    enrolled_count: int
    created_at: datetime


class ExamListSchema(Schema):
    """Schema for exam list view"""
    id: str
    exam_name: str
    subject_name: str
    status: str
    scheduled_start_time: Optional[datetime]
    duration_minutes: int
    enrolled_count: int
    active_attempts: int
    completed_attempts: int


class StudentExamSchema(Schema):
    """Schema for student exam view"""
    id: str
    exam_name: str
    subject_name: str
    description: Optional[str]
    scheduled_start_time: Optional[datetime]
    scheduled_end_time: Optional[datetime]
    duration_minutes: int
    question_count: int
    status: str
    can_attempt: bool
    attempts_used: int
    max_attempts: int
    time_remaining: Optional[int]


class ExamAttemptResponseSchema(Schema):
    """Response for exam attempt start"""
    success: bool
    attempt_id: str
    exam_name: str
    duration_minutes: int
    question_count: int
    message: str


class ExamStatsSchema(Schema):
    """Exam statistics schema"""
    total_exams: int
    active_exams: int
    scheduled_exams: int
    completed_exams: int
    total_attempts: int
    active_attempts: int


class NotificationSchema(Schema):
    """Notification schema"""
    id: str
    title: str
    message: str
    type: str
    priority: str
    is_read: bool
    created_at: datetime


# ============================================================================
# Admin Exam Management Endpoints
# ============================================================================

@enhanced_router.post("/admin/exams/schedule", response=ExamResponseSchema)
def schedule_exam(request, payload: ExamScheduleSchema):
    """
    Create and schedule a new exam with automatic broadcasting
    Industry-standard exam scheduling with comprehensive notifications
    """
    
    try:
        with transaction.atomic():
            # Validate subject and chapters
            subject = get_object_or_404(Subject, id=payload.subject_id)
            
            chapters = []
            if payload.chapter_ids:
                chapters = list(Chapter.objects.filter(
                    id__in=payload.chapter_ids,
                    subject=subject
                ))
                
                if len(chapters) != len(payload.chapter_ids):
                    raise HttpError(400, "Some chapters not found or don't belong to the subject")
            
            # Calculate end time
            scheduled_end_time = payload.scheduled_start_time + timedelta(minutes=payload.duration_minutes)
            
            # Generate unique exam code
            exam_code = f"{subject.code}_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create exam
            exam = EnhancedExam.objects.create(
                exam_code=exam_code,
                exam_name=payload.exam_name,
                description=payload.description,
                subject=subject,
                scheduled_start_time=payload.scheduled_start_time,
                scheduled_end_time=scheduled_end_time,
                duration_minutes=payload.duration_minutes,
                total_questions=payload.question_count,
                auto_assign_all_active=payload.auto_assign_all_active,
                max_attempts_per_student=payload.max_attempts_per_student,
                randomize_questions=payload.randomize_questions,
                allow_question_navigation=payload.allow_question_navigation,
                show_question_feedback=payload.show_question_feedback,
                auto_submit_on_expiry=payload.auto_submit_on_expiry,
                passing_score=payload.passing_score,
                status=ExamStatus.SCHEDULED,
                created_by=request.user,
                metadata={
                    'enrolled_students': payload.enrolled_student_ids or [],
                    'difficulty_levels': payload.difficulty_levels,
                    'reminder_times': payload.reminder_times,
                    'send_notifications': payload.send_notifications
                },
                content_selection={
                    'subject_id': payload.subject_id,
                    'chapter_ids': payload.chapter_ids,
                    'difficulty_levels': payload.difficulty_levels
                }
            )
            
            # Add chapters
            if chapters:
                exam.chapters.set(chapters)
            
            # Schedule with broadcasting service
            broadcasting_service = get_broadcasting_service()
            asyncio.create_task(broadcasting_service.schedule_exam_activation(exam))
            
            # Create initial analytics record
            ExamAnalytics.objects.create(exam=exam)
            
            # Send notifications if enabled
            if payload.send_notifications:
                asyncio.create_task(send_exam_scheduled_notifications(exam))
            
            logger.info(f"✅ Exam '{exam.exam_name}' scheduled successfully for {payload.scheduled_start_time}")
            
            return ExamResponseSchema(
                id=str(exam.id),
                exam_name=exam.exam_name,
                exam_code=exam.exam_code,
                subject_name=subject.name,
                status=exam.status,
                scheduled_start_time=exam.scheduled_start_time,
                scheduled_end_time=exam.scheduled_end_time,
                duration_minutes=exam.duration_minutes,
                question_count=exam.total_questions,
                enrolled_count=exam.enrolled_students_count,
                created_at=exam.created_at
            )
            
    except Exception as e:
        logger.error(f"❌ Error scheduling exam: {e}")
        raise HttpError(500, f"Failed to schedule exam: {str(e)}")


@enhanced_router.get("/admin/exams/list", response=List[ExamListSchema])
def list_all_exams(request):
    """
    List all exams with real-time statistics
    Provides comprehensive exam overview for admin dashboard
    """
    
    try:
        exams = EnhancedExam.objects.select_related('subject').prefetch_related(
            'student_attempts'
        ).order_by('-created_at')
        
        result = []
        for exam in exams:
            # Calculate real-time statistics
            total_attempts = exam.student_attempts.count()
            active_attempts = exam.student_attempts.filter(status='IN_PROGRESS').count()
            completed_attempts = exam.student_attempts.filter(status='COMPLETED').count()
            
            result.append(ExamListSchema(
                id=str(exam.id),
                exam_name=exam.exam_name,
                subject_name=exam.subject.name,
                status=exam.status,
                scheduled_start_time=exam.scheduled_start_time,
                duration_minutes=exam.duration_minutes,
                enrolled_count=exam.enrolled_students_count,
                active_attempts=active_attempts,
                completed_attempts=completed_attempts
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Error listing exams: {e}")
        raise HttpError(500, f"Failed to list exams: {str(e)}")


@enhanced_router.post("/admin/exams/{exam_id}/activate")
def activate_exam_manually(request, exam_id: str):
    """
    Manually activate an exam (for immediate start)
    Triggers broadcasting and notifications
    """
    
    try:
        exam = get_object_or_404(EnhancedExam, id=exam_id)
        
        if exam.status not in [ExamStatus.DRAFT, ExamStatus.SCHEDULED]:
            raise HttpError(400, f"Cannot activate exam with status: {exam.status}")
        
        # Update status
        exam.status = ExamStatus.ACTIVE
        exam.save(update_fields=['status', 'updated_at'])
        
        # Trigger broadcasting
        broadcasting_service = get_broadcasting_service()
        asyncio.create_task(broadcasting_service.activate_exam_now(exam))
        
        logger.info(f"✅ Exam '{exam.exam_name}' manually activated")
        
        return {"success": True, "message": f"Exam '{exam.exam_name}' activated successfully"}
        
    except Exception as e:
        logger.error(f"❌ Error activating exam: {e}")
        raise HttpError(500, f"Failed to activate exam: {str(e)}")


@enhanced_router.post("/admin/exams/{exam_id}/end")
def end_exam_manually(request, exam_id: str):
    """
    Manually end an active exam
    Handles auto-submission and final notifications
    """
    
    try:
        exam = get_object_or_404(EnhancedExam, id=exam_id)
        
        if exam.status != ExamStatus.ACTIVE:
            raise HttpError(400, f"Cannot end exam with status: {exam.status}")
        
        # Trigger broadcasting service to end exam
        broadcasting_service = get_broadcasting_service()
        asyncio.create_task(broadcasting_service.end_exam(str(exam.id)))
        
        logger.info(f"✅ Exam '{exam.exam_name}' manually ended")
        
        return {"success": True, "message": f"Exam '{exam.exam_name}' ended successfully"}
        
    except Exception as e:
        logger.error(f"❌ Error ending exam: {e}")
        raise HttpError(500, f"Failed to end exam: {str(e)}")


@enhanced_router.get("/admin/exams/{exam_id}/live-stats")
def get_live_exam_stats(request, exam_id: str):
    """
    Get real-time statistics for an active exam
    Used by admin dashboard for live monitoring
    """
    
    try:
        exam = get_object_or_404(EnhancedExam, id=exam_id)
        
        # Get real-time statistics
        total_enrolled = exam.enrolled_students_count
        attempts = exam.student_attempts.all()
        
        active_attempts = attempts.filter(status='IN_PROGRESS').count()
        completed_attempts = attempts.filter(status='COMPLETED').count()
        auto_submitted = attempts.filter(status='AUTO_SUBMITTED').count()
        
        # Calculate participation rate
        participation_rate = ((active_attempts + completed_attempts) / total_enrolled * 100) if total_enrolled > 0 else 0
        
        # Get average progress for active attempts
        active_progress = []
        for attempt in attempts.filter(status='IN_PROGRESS'):
            progress = (attempt.questions_answered / attempt.total_questions * 100) if attempt.total_questions > 0 else 0
            active_progress.append(progress)
        
        avg_progress = sum(active_progress) / len(active_progress) if active_progress else 0
        
        # Time remaining
        time_remaining = exam.get_time_remaining()
        
        stats = {
            "exam_id": str(exam.id),
            "exam_name": exam.exam_name,
            "status": exam.status,
            "total_enrolled": total_enrolled,
            "active_attempts": active_attempts,
            "completed_attempts": completed_attempts,
            "auto_submitted": auto_submitted,
            "participation_rate": round(participation_rate, 1),
            "average_progress": round(avg_progress, 1),
            "time_remaining_minutes": time_remaining,
            "last_updated": timezone.now().isoformat()
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"❌ Error getting live stats: {e}")
        raise HttpError(500, f"Failed to get live stats: {str(e)}")


@enhanced_router.get("/admin/dashboard/stats", response=ExamStatsSchema)
def get_admin_dashboard_stats(request):
    """
    Get overall system statistics for admin dashboard
    """
    
    try:
        now = timezone.now()
        
        # Exam counts
        total_exams = EnhancedExam.objects.count()
        active_exams = EnhancedExam.objects.filter(status=ExamStatus.ACTIVE).count()
        scheduled_exams = EnhancedExam.objects.filter(
            status=ExamStatus.SCHEDULED,
            scheduled_start_time__gte=now
        ).count()
        completed_exams = EnhancedExam.objects.filter(status=ExamStatus.COMPLETED).count()
        
        # Attempt counts
        total_attempts = StudentExamAttempt.objects.count()
        active_attempts = StudentExamAttempt.objects.filter(status='IN_PROGRESS').count()
        
        return ExamStatsSchema(
            total_exams=total_exams,
            active_exams=active_exams,
            scheduled_exams=scheduled_exams,
            completed_exams=completed_exams,
            total_attempts=total_attempts,
            active_attempts=active_attempts
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting dashboard stats: {e}")
        raise HttpError(500, f"Failed to get dashboard stats: {str(e)}")


# ============================================================================
# Student Exam Endpoints
# ============================================================================

@enhanced_router.get("/student/exams/available", response=List[StudentExamSchema])
def get_available_exams_for_student(request):
    """
    Get available exams for the current student
    Shows scheduled, active, and upcoming exams with real-time status
    """
    
    try:
        if not hasattr(request.user, 'student_profile'):
            raise HttpError(403, "Only students can access this endpoint")
        
        now = timezone.now()
        
        # Get exams that are available or upcoming
        available_exams = EnhancedExam.objects.filter(
            Q(status__in=[ExamStatus.SCHEDULED, ExamStatus.ACTIVE]) &
            (Q(scheduled_end_time__isnull=True) | Q(scheduled_end_time__gte=now))
        ).select_related('subject').prefetch_related('student_attempts')
        
        result = []
        for exam in available_exams:
            # Check if student can attempt
            can_attempt, reason = exam.can_student_attempt(request.user)
            
            # Get student's attempts for this exam
            student_attempts = exam.student_attempts.filter(student=request.user)
            attempts_used = student_attempts.count()
            
            # Determine status for student
            if exam.status == ExamStatus.SCHEDULED and exam.scheduled_start_time and exam.scheduled_start_time > now:
                status = "upcoming"
            elif exam.status == ExamStatus.ACTIVE:
                status = "available"
            elif exam.scheduled_end_time and exam.scheduled_end_time < now:
                status = "expired"
            else:
                status = exam.status.lower()
            
            result.append(StudentExamSchema(
                id=str(exam.id),
                exam_name=exam.exam_name,
                subject_name=exam.subject.name,
                description=exam.description,
                scheduled_start_time=exam.scheduled_start_time,
                scheduled_end_time=exam.scheduled_end_time,
                duration_minutes=exam.duration_minutes,
                question_count=exam.total_questions,
                status=status,
                can_attempt=can_attempt,
                attempts_used=attempts_used,
                max_attempts=exam.max_attempts_per_student,
                time_remaining=exam.get_time_remaining()
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Error getting available exams: {e}")
        raise HttpError(500, f"Failed to get available exams: {str(e)}")


@enhanced_router.post("/student/exams/{exam_id}/start", response=ExamAttemptResponseSchema)
def start_exam_attempt(request, exam_id: str):
    """
    Start a new exam attempt for the student
    Integrates with broadcasting service for real-time tracking
    """
    
    try:
        if not hasattr(request.user, 'student_profile'):
            raise HttpError(403, "Only students can start exams")
        
        exam = get_object_or_404(EnhancedExam, id=exam_id)
        
        # Validate exam can be attempted
        can_attempt, reason = exam.can_student_attempt(request.user)
        if not can_attempt:
            raise HttpError(400, reason)
        
        # Use broadcasting service to handle exam start
        broadcasting_service = get_broadcasting_service()
        attempt = asyncio.run(broadcasting_service.handle_exam_start(
            str(request.user.id), 
            exam_id
        ))
        
        return ExamAttemptResponseSchema(
            success=True,
            attempt_id=str(attempt.id),
            exam_name=exam.exam_name,
            duration_minutes=exam.duration_minutes,
            question_count=exam.total_questions,
            message=f"Exam started successfully! You have {exam.duration_minutes} minutes to complete it."
        )
        
    except Exception as e:
        logger.error(f"❌ Error starting exam attempt: {e}")
        raise HttpError(500, f"Failed to start exam: {str(e)}")


@enhanced_router.get("/student/notifications", response=List[NotificationSchema])
def get_student_notifications(request):
    """
    Get exam notifications for the current student
    """
    
    try:
        if not hasattr(request.user, 'student_profile'):
            raise HttpError(403, "Only students can access notifications")
        
        notifications = ExamNotification.objects.filter(
            student=request.user
        ).order_by('-created_at')[:20]  # Last 20 notifications
        
        result = []
        for notification in notifications:
            result.append(NotificationSchema(
                id=str(notification.id),
                title=notification.title,
                message=notification.message,
                type=notification.notification_type,
                priority=notification.priority,
                is_read=notification.is_read,
                created_at=notification.created_at
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Error getting notifications: {e}")
        raise HttpError(500, f"Failed to get notifications: {str(e)}")


@enhanced_router.post("/student/notifications/{notification_id}/read")
def mark_notification_read(request, notification_id: str):
    """
    Mark a notification as read
    """
    
    try:
        notification = get_object_or_404(
            ExamNotification, 
            id=notification_id, 
            student=request.user
        )
        
        notification.mark_as_read()
        
        return {"success": True, "message": "Notification marked as read"}
        
    except Exception as e:
        logger.error(f"❌ Error marking notification as read: {e}")
        raise HttpError(500, f"Failed to mark notification as read: {str(e)}")


# ============================================================================
# Utility Functions
# ============================================================================

async def send_exam_scheduled_notifications(exam):
    """
    Send notifications when an exam is scheduled
    """
    try:
        # Get enrolled students
        if exam.auto_assign_all_active:
            students = User.objects.filter(
                is_active=True,
                student_profile__isnull=False
            )
        else:
            enrolled_ids = exam.metadata.get('enrolled_students', [])
            students = User.objects.filter(id__in=enrolled_ids)
        
        # Create notifications
        notifications = []
        for student in students:
            notifications.append(ExamNotification(
                exam=exam,
                student=student,
                notification_type=NotificationType.EXAM_SCHEDULED,
                title=f"New Exam Scheduled: {exam.exam_name}",
                message=f"A new exam '{exam.exam_name}' has been scheduled for {exam.scheduled_start_time.strftime('%B %d, %Y at %I:%M %p')}. Duration: {exam.duration_minutes} minutes.",
                priority='medium'
            ))
        
        # Bulk create notifications
        ExamNotification.objects.bulk_create(notifications, batch_size=100)
        
        logger.info(f"📧 Sent scheduled notifications to {len(notifications)} students")
        
    except Exception as e:
        logger.error(f"❌ Error sending scheduled notifications: {e}")


def schedule_exam_reminders(exam):
    """
    Schedule reminder notifications for an exam
    """
    try:
        reminder_times = exam.metadata.get('reminder_times', [60, 30, 10])
        
        for minutes_before in reminder_times:
            reminder_time = exam.scheduled_start_time - timedelta(minutes=minutes_before)
            
            # Use Django's task scheduler or Celery for production
            # For now, we'll use the broadcasting service
            broadcasting_service = get_broadcasting_service()
            
            # Schedule reminder (simplified implementation)
            # In production, use Celery beat or similar
            asyncio.create_task(
                schedule_reminder_task(exam, minutes_before, reminder_time)
            )
        
    except Exception as e:
        logger.error(f"❌ Error scheduling reminders: {e}")


async def schedule_reminder_task(exam, minutes_before, reminder_time):
    """
    Schedule a reminder task
    """
    try:
        now = timezone.now()
        delay = (reminder_time - now).total_seconds()
        
        if delay > 0:
            await asyncio.sleep(delay)
            await send_exam_reminder(exam, minutes_before)
        
    except Exception as e:
        logger.error(f"❌ Error in reminder task: {e}")


async def send_exam_reminder(exam, minutes_before):
    """
    Send exam reminder notifications
    """
    try:
        # Get enrolled students
        if exam.auto_assign_all_active:
            students = await get_active_students()
        else:
            enrolled_ids = exam.metadata.get('enrolled_students', [])
            students = await get_students_by_ids(enrolled_ids)
        
        # Send reminder notifications
        broadcasting_service = get_broadcasting_service()
        
        for student in students:
            notification_data = {
                'type': 'exam_reminder',
                'exam_id': str(exam.id),
                'exam_name': exam.exam_name,
                'minutes_until_start': minutes_before,
                'message': f"Reminder: Exam '{exam.exam_name}' starts in {minutes_before} minutes!",
                'priority': 'high' if minutes_before <= 10 else 'medium'
            }
            
            await broadcasting_service.send_to_student(str(student.id), notification_data)
        
        logger.info(f"⏰ Sent {minutes_before}-minute reminders to {len(students)} students")
        
    except Exception as e:
        logger.error(f"❌ Error sending reminders: {e}")


async def get_active_students():
    """Get all active students (async)"""
    from asgiref.sync import sync_to_async
    
    @sync_to_async
    def _get_students():
        return list(User.objects.filter(
            is_active=True,
            student_profile__isnull=False
        ))
    
    return await _get_students()


async def get_students_by_ids(student_ids):
    """Get students by IDs (async)"""
    from asgiref.sync import sync_to_async
    
    @sync_to_async
    def _get_students():
        return list(User.objects.filter(id__in=student_ids))
    
    return await _get_students()