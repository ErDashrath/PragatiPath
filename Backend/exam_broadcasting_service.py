"""
Industry-Standard Exam Broadcasting & Scheduling Service
Handles real-time exam notifications, automatic scheduling, and student management
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models import Q
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async

from enhanced_exam_management_models import EnhancedExam, StudentExamAttempt, ExamNotification
from core.models import StudentProfile

logger = logging.getLogger(__name__)

class ExamBroadcastingService:
    """
    Industry-standard exam broadcasting service with:
    - Automatic exam activation
    - Real-time notifications
    - Student enrollment management
    - Exam status monitoring
    """
    
    def __init__(self):
        self.active_exams: Dict[str, Dict] = {}
        self.student_connections: Dict[str, Set[str]] = {}  # student_id -> {connection_ids}
        self.admin_connections: Set[str] = set()
        self.scheduled_tasks: Dict[str, asyncio.Task] = {}
        
    async def initialize(self):
        """Initialize the broadcasting service and schedule existing exams"""
        logger.info("🚀 Initializing Exam Broadcasting Service...")
        
        # Load existing scheduled exams
        await self.load_scheduled_exams()
        
        # Start background tasks
        asyncio.create_task(self.exam_monitor_loop())
        asyncio.create_task(self.notification_cleanup_loop())
        
        logger.info("✅ Exam Broadcasting Service initialized successfully")
    
    async def load_scheduled_exams(self):
        """Load and schedule existing exams from database"""
        try:
            exams = await self.get_scheduled_exams()
            
            for exam in exams:
                await self.schedule_exam_activation(exam)
                
            logger.info(f"📅 Loaded {len(exams)} scheduled exams")
            
        except Exception as e:
            logger.error(f"❌ Error loading scheduled exams: {e}")
    
    @database_sync_to_async
    def get_scheduled_exams(self):
        """Get all scheduled exams that need activation"""
        now = timezone.now()
        
        return list(EnhancedExam.objects.filter(
            status__in=['SCHEDULED', 'DRAFT'],
            scheduled_start_time__gte=now,
            scheduled_start_time__lte=now + timedelta(days=30)  # Next 30 days
        ).select_related('subject').prefetch_related('chapters'))
    
    async def schedule_exam_activation(self, exam):
        """Schedule automatic exam activation"""
        if not exam.scheduled_start_time:
            return
            
        now = timezone.now()
        activation_time = exam.scheduled_start_time
        
        if activation_time <= now:
            # Exam should already be active
            await self.activate_exam_now(exam)
            return
        
        delay = (activation_time - now).total_seconds()
        
        # Cancel existing task if any
        task_key = f"activate_{exam.id}"
        if task_key in self.scheduled_tasks:
            self.scheduled_tasks[task_key].cancel()
        
        # Schedule new activation task
        task = asyncio.create_task(self.delayed_exam_activation(exam, delay))
        self.scheduled_tasks[task_key] = task
        
        logger.info(f"📅 Scheduled exam '{exam.exam_name}' for activation in {delay/60:.1f} minutes")
    
    async def delayed_exam_activation(self, exam, delay_seconds):
        """Delayed activation of exam after specified time"""
        try:
            await asyncio.sleep(delay_seconds)
            await self.activate_exam_now(exam)
        except asyncio.CancelledError:
            logger.info(f"📅 Exam activation cancelled for: {exam.exam_name}")
        except Exception as e:
            logger.error(f"❌ Error in delayed exam activation: {e}")
    
    async def activate_exam_now(self, exam):
        """Immediately activate an exam and notify students"""
        try:
            # Update exam status to ACTIVE
            await self.update_exam_status(exam.id, 'ACTIVE')
            
            # Get enrolled students
            enrolled_students = await self.get_enrolled_students(exam)
            
            # Create notifications
            await self.create_exam_notifications(exam, enrolled_students, 'EXAM_STARTED')
            
            # Broadcast to students
            notification_data = {
                'type': 'exam_started',
                'exam_id': str(exam.id),
                'exam_name': exam.exam_name,
                'subject_name': exam.subject.name,
                'duration_minutes': exam.duration_minutes,
                'question_count': exam.total_questions,
                'message': f"Exam '{exam.exam_name}' is now available! You have {exam.duration_minutes} minutes to complete it.",
                'timestamp': timezone.now().isoformat(),
                'priority': 'high'
            }
            
            # Broadcast to enrolled students
            for student in enrolled_students:
                await self.send_to_student(student.id, notification_data)
            
            # Broadcast to admins
            admin_notification = {
                'type': 'exam_activated',
                'exam_id': str(exam.id),
                'exam_name': exam.exam_name,
                'enrolled_count': len(enrolled_students),
                'message': f"Exam '{exam.exam_name}' has been activated for {len(enrolled_students)} students"
            }
            await self.broadcast_to_admins(admin_notification)
            
            # Add to active exams
            self.active_exams[str(exam.id)] = {
                'exam': exam,
                'activated_at': timezone.now(),
                'enrolled_students': [s.id for s in enrolled_students],
                'active_attempts': 0
            }
            
            logger.info(f"🎯 Exam '{exam.exam_name}' activated for {len(enrolled_students)} students")
            
        except Exception as e:
            logger.error(f"❌ Error activating exam: {e}")
    
    @database_sync_to_async
    def update_exam_status(self, exam_id, status):
        """Update exam status in database"""
        EnhancedExam.objects.filter(id=exam_id).update(status=status, updated_at=timezone.now())
    
    @database_sync_to_async
    def get_enrolled_students(self, exam):
        """Get students enrolled in the exam"""
        if exam.auto_assign_all_active:
            # Auto-enroll all active students
            return list(User.objects.filter(
                is_active=True,
                student_profile__isnull=False
            ).select_related('student_profile'))
        else:
            # Get manually enrolled students
            enrolled_ids = exam.metadata.get('enrolled_students', [])
            return list(User.objects.filter(
                id__in=enrolled_ids,
                is_active=True
            ).select_related('student_profile'))
    
    @database_sync_to_async
    def create_exam_notifications(self, exam, students, notification_type):
        """Create notification records in database"""
        notifications = []
        for student in students:
            notifications.append(ExamNotification(
                exam=exam,
                student=student,
                notification_type=notification_type,
                title=f"Exam Available: {exam.exam_name}",
                message=f"Your exam '{exam.exam_name}' is now available. Duration: {exam.duration_minutes} minutes.",
                is_read=False,
                created_at=timezone.now()
            ))
        
        ExamNotification.objects.bulk_create(notifications, ignore_conflicts=True)
    
    async def handle_exam_start(self, student_id: str, exam_id: str):
        """Handle when a student starts an exam"""
        try:
            # Update active attempts count
            if exam_id in self.active_exams:
                self.active_exams[exam_id]['active_attempts'] += 1
            
            # Create attempt record
            attempt = await self.create_exam_attempt(student_id, exam_id)
            
            # Notify admins
            admin_notification = {
                'type': 'student_started_exam',
                'exam_id': exam_id,
                'student_id': student_id,
                'attempt_id': str(attempt.id),
                'timestamp': timezone.now().isoformat()
            }
            await self.broadcast_to_admins(admin_notification)
            
            # Send confirmation to student
            student_notification = {
                'type': 'exam_started_confirmation',
                'exam_id': exam_id,
                'attempt_id': str(attempt.id),
                'message': "Exam started successfully. Good luck!"
            }
            await self.send_to_student(student_id, student_notification)
            
            return attempt
            
        except Exception as e:
            logger.error(f"❌ Error handling exam start: {e}")
            raise
    
    @database_sync_to_async
    def create_exam_attempt(self, student_id, exam_id):
        """Create a new exam attempt record"""
        try:
            exam = EnhancedExam.objects.get(id=exam_id)
            student = User.objects.get(id=student_id)
            student_profile, _ = StudentProfile.objects.get_or_create(user=student)
            
            # Check existing attempts
            existing_attempts = StudentExamAttempt.objects.filter(
                exam=exam, student=student
            ).count()
            
            attempt = StudentExamAttempt.objects.create(
                exam=exam,
                student=student,
                student_profile=student_profile,
                attempt_number=existing_attempts + 1,
                total_questions=exam.total_questions,
                started_at=timezone.now(),
                status='IN_PROGRESS'
            )
            
            return attempt
            
        except Exception as e:
            logger.error(f"❌ Error creating exam attempt: {e}")
            raise
    
    async def handle_exam_submission(self, student_id: str, exam_id: str, attempt_id: str, answers: Dict):
        """Handle exam submission and calculate results"""
        try:
            # Calculate results
            results = await self.calculate_exam_results(attempt_id, answers)
            
            # Update attempt status
            await self.finalize_exam_attempt(attempt_id, results)
            
            # Update active attempts count
            if exam_id in self.active_exams:
                self.active_exams[exam_id]['active_attempts'] = max(0, 
                    self.active_exams[exam_id]['active_attempts'] - 1)
            
            # Notify student of results
            student_notification = {
                'type': 'exam_completed',
                'exam_id': exam_id,
                'attempt_id': attempt_id,
                'score': results['score_percentage'],
                'grade': results['grade'],
                'passed': results['passed'],
                'message': f"Exam completed! Score: {results['score_percentage']:.1f}% ({results['grade']})"
            }
            await self.send_to_student(student_id, student_notification)
            
            # Notify admins
            admin_notification = {
                'type': 'student_completed_exam',
                'exam_id': exam_id,
                'student_id': student_id,
                'attempt_id': attempt_id,
                'score': results['score_percentage'],
                'timestamp': timezone.now().isoformat()
            }
            await self.broadcast_to_admins(admin_notification)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error handling exam submission: {e}")
            raise
    
    @database_sync_to_async
    def calculate_exam_results(self, attempt_id, answers):
        """Calculate exam results and generate analytics"""
        # Placeholder for result calculation logic
        # This would integrate with the BKT/DKT adaptive learning system
        
        total_questions = len(answers)
        correct_answers = sum(1 for answer in answers.values() if answer.get('is_correct', False))
        score_percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        # Grade assignment logic
        if score_percentage >= 90:
            grade = 'A+'
        elif score_percentage >= 80:
            grade = 'A'
        elif score_percentage >= 70:
            grade = 'B'
        elif score_percentage >= 60:
            grade = 'C'
        else:
            grade = 'F'
        
        return {
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'score_percentage': score_percentage,
            'grade': grade,
            'passed': score_percentage >= 60,
            'time_taken_minutes': 45  # Placeholder
        }
    
    @database_sync_to_async
    def finalize_exam_attempt(self, attempt_id, results):
        """Finalize exam attempt with results"""
        StudentExamAttempt.objects.filter(id=attempt_id).update(
            status='COMPLETED',
            submitted_at=timezone.now(),
            final_score_percentage=results['score_percentage'],
            grade=results['grade'],
            passed=results['passed'],
            correct_answers=results['correct_answers'],
            total_time_minutes=results['time_taken_minutes']
        )
    
    async def send_to_student(self, student_id: str, data: Dict):
        """Send notification to specific student"""
        if student_id in self.student_connections:
            for connection_id in self.student_connections[student_id].copy():
                try:
                    # This would be implemented with actual WebSocket connections
                    # For now, we'll use Django cache for demo
                    cache_key = f"student_notification_{student_id}_{connection_id}"
                    cache.set(cache_key, json.dumps(data), timeout=300)  # 5 minutes
                    logger.debug(f"📨 Sent notification to student {student_id}: {data['type']}")
                except Exception as e:
                    logger.error(f"❌ Error sending to student {student_id}: {e}")
                    self.student_connections[student_id].discard(connection_id)
    
    async def broadcast_to_admins(self, data: Dict):
        """Broadcast notification to all connected admins"""
        for connection_id in self.admin_connections.copy():
            try:
                # This would be implemented with actual WebSocket connections
                cache_key = f"admin_notification_{connection_id}"
                cache.set(cache_key, json.dumps(data), timeout=300)
                logger.debug(f"📨 Sent admin notification: {data['type']}")
            except Exception as e:
                logger.error(f"❌ Error sending to admin {connection_id}: {e}")
                self.admin_connections.discard(connection_id)
    
    async def exam_monitor_loop(self):
        """Background task to monitor exam status and handle timeouts"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                current_time = timezone.now()
                
                # Check for exams that should end
                for exam_id, exam_data in list(self.active_exams.items()):
                    exam = exam_data['exam']
                    
                    if exam.scheduled_end_time and current_time >= exam.scheduled_end_time:
                        await self.end_exam(exam_id)
                
                # Check for exam attempts that have timed out
                await self.handle_timeout_submissions()
                
            except Exception as e:
                logger.error(f"❌ Error in exam monitor loop: {e}")
    
    async def end_exam(self, exam_id: str):
        """End an exam and handle auto-submissions"""
        try:
            if exam_id not in self.active_exams:
                return
            
            exam_data = self.active_exams[exam_id]
            exam = exam_data['exam']
            
            # Update exam status
            await self.update_exam_status(exam_id, 'COMPLETED')
            
            # Handle auto-submissions for ongoing attempts
            await self.auto_submit_ongoing_attempts(exam_id)
            
            # Notify students
            notification_data = {
                'type': 'exam_ended',
                'exam_id': exam_id,
                'exam_name': exam.exam_name,
                'message': f"Exam '{exam.exam_name}' has ended. Thank you for participating!"
            }
            
            for student_id in exam_data['enrolled_students']:
                await self.send_to_student(str(student_id), notification_data)
            
            # Notify admins
            admin_notification = {
                'type': 'exam_ended',
                'exam_id': exam_id,
                'exam_name': exam.exam_name,
                'total_enrolled': len(exam_data['enrolled_students']),
                'timestamp': timezone.now().isoformat()
            }
            await self.broadcast_to_admins(admin_notification)
            
            # Remove from active exams
            del self.active_exams[exam_id]
            
            logger.info(f"🏁 Exam '{exam.exam_name}' ended automatically")
            
        except Exception as e:
            logger.error(f"❌ Error ending exam: {e}")
    
    @database_sync_to_async
    def auto_submit_ongoing_attempts(self, exam_id):
        """Auto-submit all ongoing attempts for an exam"""
        ongoing_attempts = StudentExamAttempt.objects.filter(
            exam_id=exam_id,
            status='IN_PROGRESS'
        )
        
        for attempt in ongoing_attempts:
            # Auto-submit with current progress
            attempt.status = 'AUTO_SUBMITTED'
            attempt.submitted_at = timezone.now()
            attempt.save()
    
    @database_sync_to_async
    def handle_timeout_submissions(self):
        """Handle attempts that have exceeded time limit"""
        timeout_threshold = timezone.now() - timedelta(hours=3)  # 3 hours timeout
        
        timed_out_attempts = StudentExamAttempt.objects.filter(
            status='IN_PROGRESS',
            started_at__lt=timeout_threshold
        )
        
        for attempt in timed_out_attempts:
            attempt.status = 'TIMED_OUT'
            attempt.submitted_at = timezone.now()
            attempt.save()
    
    async def notification_cleanup_loop(self):
        """Clean up old notifications periodically"""
        while True:
            try:
                await asyncio.sleep(3600)  # Clean every hour
                await self.cleanup_old_notifications()
            except Exception as e:
                logger.error(f"❌ Error in notification cleanup: {e}")
    
    @database_sync_to_async
    def cleanup_old_notifications(self):
        """Remove notifications older than 7 days"""
        cutoff_date = timezone.now() - timedelta(days=7)
        deleted_count = ExamNotification.objects.filter(
            created_at__lt=cutoff_date
        ).delete()[0]
        
        if deleted_count > 0:
            logger.info(f"🧹 Cleaned up {deleted_count} old notifications")


class ExamWebSocketConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time exam notifications"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = None
        self.user_type = None
        self.connection_id = None
        self.broadcasting_service = None
    
    async def connect(self):
        """Handle WebSocket connection"""
        try:
            # Get user from scope (assuming authentication middleware)
            user = self.scope.get('user')
            if not user or not user.is_authenticated:
                await self.close()
                return
            
            self.user_id = str(user.id)
            self.connection_id = f"{self.user_id}_{timezone.now().timestamp()}"
            
            # Determine user type
            if hasattr(user, 'student_profile'):
                self.user_type = 'student'
            else:
                self.user_type = 'admin'
            
            await self.accept()
            
            # Add to broadcasting service connections
            broadcasting_service = ExamBroadcastingService()
            if self.user_type == 'student':
                if self.user_id not in broadcasting_service.student_connections:
                    broadcasting_service.student_connections[self.user_id] = set()
                broadcasting_service.student_connections[self.user_id].add(self.connection_id)
            else:
                broadcasting_service.admin_connections.add(self.connection_id)
            
            logger.info(f"🔌 {self.user_type} {self.user_id} connected via WebSocket")
            
        except Exception as e:
            logger.error(f"❌ Error in WebSocket connection: {e}")
            await self.close()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        try:
            broadcasting_service = ExamBroadcastingService()
            
            if self.user_type == 'student' and self.user_id in broadcasting_service.student_connections:
                broadcasting_service.student_connections[self.user_id].discard(self.connection_id)
                if not broadcasting_service.student_connections[self.user_id]:
                    del broadcasting_service.student_connections[self.user_id]
            elif self.user_type == 'admin':
                broadcasting_service.admin_connections.discard(self.connection_id)
            
            logger.info(f"🔌 {self.user_type} {self.user_id} disconnected from WebSocket")
            
        except Exception as e:
            logger.error(f"❌ Error in WebSocket disconnection: {e}")
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({'type': 'pong'}))
            elif message_type == 'start_exam':
                # Handle exam start request
                exam_id = data.get('exam_id')
                broadcasting_service = ExamBroadcastingService()
                await broadcasting_service.handle_exam_start(self.user_id, exam_id)
            
        except Exception as e:
            logger.error(f"❌ Error handling WebSocket message: {e}")


# Global broadcasting service instance
broadcasting_service = ExamBroadcastingService()


async def initialize_broadcasting_service():
    """Initialize the global broadcasting service"""
    await broadcasting_service.initialize()


def get_broadcasting_service():
    """Get the global broadcasting service instance"""
    return broadcasting_service