"""
Enhanced Admin API endpoints for comprehensive exam monitoring and control
Provides real-time statistics, student progress tracking, and exam lifecycle management
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from django.db.models import Q, Count, Avg, F, Case, When, IntegerField
from django.core.cache import cache
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Import your models - adjust imports based on your project structure
from core.models import StudentProfile
from assessment.models import Subject, Chapter, Question
from .enhanced_exam_management_models import (
    EnhancedExam, 
    StudentExamAttempt, 
    ExamNotification,
    ExamAnalytics
)
from .exam_broadcasting_service import ExamBroadcastingService

logger = logging.getLogger(__name__)

class AdminExamMonitoringAPI:
    """Comprehensive API for real-time exam monitoring and management"""
    
    def __init__(self):
        self.broadcasting_service = ExamBroadcastingService()
    
    def is_admin_user(self, user) -> bool:
        """Check if user has admin privileges"""
        if not user.is_authenticated:
            return False
        
        # Admin users don't have StudentProfile
        return not hasattr(user, 'studentprofile') or user.is_staff or user.is_superuser
    
    def get_exam_monitoring_data(self, request) -> JsonResponse:
        """Get comprehensive monitoring data for all exams"""
        try:
            if not self.is_admin_user(request.user):
                return JsonResponse({'error': 'Admin access required'}, status=403)
            
            # Get all exams with basic stats
            exams = EnhancedExam.objects.select_related('created_by').prefetch_related(
                'studentexamattempt_set'
            ).annotate(
                total_students=Count('studentexamattempt__user', distinct=True),
                enrolled_students=Count(
                    'studentexamattempt__user',
                    filter=Q(studentexamattempt__status__in=['not_started', 'in_progress', 'completed']),
                    distinct=True
                ),
                active_students=Count(
                    'studentexamattempt__user',
                    filter=Q(studentexamattempt__status='in_progress'),
                    distinct=True
                ),
                completed_attempts=Count(
                    'studentexamattempt__user',
                    filter=Q(studentexamattempt__status='completed'),
                    distinct=True
                )
            ).order_by('-created_at')
            
            exam_data = []
            for exam in exams:
                # Calculate additional stats
                now = timezone.now()
                time_until_start = (exam.start_time - now).total_seconds() / 60 if exam.start_time > now else 0
                time_remaining = max(0, (exam.end_time - now).total_seconds() / 60) if exam.end_time else exam.duration_minutes
                
                exam_data.append({
                    'id': exam.id,
                    'title': exam.title,
                    'status': exam.status,
                    'start_time': exam.start_time.isoformat(),
                    'end_time': exam.end_time.isoformat() if exam.end_time else None,
                    'duration_minutes': exam.duration_minutes,
                    'total_students': exam.total_students,
                    'enrolled_students': exam.enrolled_students,
                    'active_students': exam.active_students,
                    'completed_attempts': exam.completed_attempts,
                    'created_at': exam.created_at.isoformat(),
                    'created_by': exam.created_by.username if exam.created_by else 'System',
                    'time_until_start': max(0, time_until_start),
                    'time_remaining': time_remaining,
                    'subjects': list(exam.subjects.values_list('name', flat=True)),
                    'questions_count': exam.questions.count(),
                    'max_attempts': exam.max_attempts,
                    'pass_threshold': exam.pass_threshold,
                })
            
            return JsonResponse(exam_data, safe=False)
            
        except Exception as e:
            logger.error(f"Error fetching exam monitoring data: {str(e)}")
            return JsonResponse({'error': 'Failed to fetch monitoring data'}, status=500)
    
    def get_exam_live_stats(self, request, exam_id: int) -> JsonResponse:
        """Get real-time statistics for a specific exam"""
        try:
            if not self.is_admin_user(request.user):
                return JsonResponse({'error': 'Admin access required'}, status=403)
            
            try:
                exam = EnhancedExam.objects.get(id=exam_id)
            except EnhancedExam.DoesNotExist:
                return JsonResponse({'error': 'Exam not found'}, status=404)
            
            # Get all attempts for this exam
            attempts = StudentExamAttempt.objects.filter(exam=exam).select_related('user')
            
            # Calculate live statistics
            now = timezone.now()
            active_attempts = attempts.filter(status='in_progress')
            completed_attempts = attempts.filter(status='completed')
            
            # Calculate averages
            active_progress = []
            active_scores = []
            total_questions = exam.questions.count()
            
            for attempt in active_attempts:
                if attempt.current_question and total_questions > 0:
                    progress = (attempt.current_question / total_questions) * 100
                    active_progress.append(progress)
                
                if attempt.score is not None:
                    active_scores.append(attempt.score)
            
            # Time calculations
            time_remaining = 0
            if exam.status == 'active' and exam.end_time:
                time_remaining = max(0, (exam.end_time - now).total_seconds() / 60)
            
            # Get last activity time
            last_activity = attempts.filter(
                last_updated__isnull=False
            ).order_by('-last_updated').first()
            
            # Calculate questions answered
            questions_answered = sum([
                attempt.current_question or 0 for attempt in active_attempts
            ])
            
            stats = {
                'exam_id': exam.id,
                'active_students': active_attempts.count(),
                'completed_students': completed_attempts.count(),
                'avg_progress': sum(active_progress) / len(active_progress) if active_progress else 0,
                'avg_score': sum(active_scores) / len(active_scores) if active_scores else 0,
                'time_remaining': int(time_remaining),
                'questions_answered': questions_answered,
                'total_questions': total_questions * active_attempts.count(),
                'last_activity': last_activity.last_updated.isoformat() if last_activity and last_activity.last_updated else now.isoformat(),
                'peak_concurrent_students': cache.get(f'exam_{exam_id}_peak_students', active_attempts.count()),
                'total_time_spent': sum([
                    (attempt.last_updated - attempt.start_time).total_seconds() 
                    for attempt in active_attempts 
                    if attempt.start_time and attempt.last_updated
                ]),
            }
            
            # Update peak concurrent students in cache
            current_peak = cache.get(f'exam_{exam_id}_peak_students', 0)
            if active_attempts.count() > current_peak:
                cache.set(f'exam_{exam_id}_peak_students', active_attempts.count(), 3600)
            
            return JsonResponse(stats)
            
        except Exception as e:
            logger.error(f"Error fetching live stats for exam {exam_id}: {str(e)}")
            return JsonResponse({'error': 'Failed to fetch live statistics'}, status=500)
    
    def get_student_progress(self, request, exam_id: int) -> JsonResponse:
        """Get detailed progress for all students taking the exam"""
        try:
            if not self.is_admin_user(request.user):
                return JsonResponse({'error': 'Admin access required'}, status=403)
            
            try:
                exam = EnhancedExam.objects.get(id=exam_id)
            except EnhancedExam.DoesNotExist:
                return JsonResponse({'error': 'Exam not found'}, status=404)
            
            # Get all attempts with user details
            attempts = StudentExamAttempt.objects.filter(
                exam=exam
            ).select_related('user').order_by('-last_updated')
            
            progress_data = []
            total_questions = exam.questions.count()
            
            for attempt in attempts:
                # Calculate progress percentage
                progress_percentage = 0
                if attempt.current_question and total_questions > 0:
                    progress_percentage = (attempt.current_question / total_questions) * 100
                
                # Calculate time spent
                time_spent = 0
                if attempt.start_time:
                    end_time = attempt.end_time or timezone.now()
                    time_spent = int((end_time - attempt.start_time).total_seconds())
                
                # Determine connection status
                last_activity = attempt.last_updated or attempt.start_time
                now = timezone.now()
                is_disconnected = False
                
                if last_activity and attempt.status == 'in_progress':
                    # Consider disconnected if no activity for more than 5 minutes
                    is_disconnected = (now - last_activity).total_seconds() > 300
                
                status = attempt.status
                if status == 'in_progress' and is_disconnected:
                    status = 'disconnected'
                
                progress_data.append({
                    'user_id': attempt.user.id,
                    'username': attempt.user.username,
                    'email': attempt.user.email,
                    'start_time': attempt.start_time.isoformat() if attempt.start_time else None,
                    'end_time': attempt.end_time.isoformat() if attempt.end_time else None,
                    'progress_percentage': round(progress_percentage, 1),
                    'current_question': attempt.current_question or 0,
                    'total_questions': total_questions,
                    'score': attempt.score or 0,
                    'last_activity': last_activity.isoformat() if last_activity else None,
                    'time_spent': time_spent,
                    'status': status,
                    'attempt_number': attempt.attempt_number,
                    'answers_submitted': len(attempt.responses) if attempt.responses else 0,
                    'is_flagged': attempt.is_flagged,
                })
            
            return JsonResponse(progress_data, safe=False)
            
        except Exception as e:
            logger.error(f"Error fetching student progress for exam {exam_id}: {str(e)}")
            return JsonResponse({'error': 'Failed to fetch student progress'}, status=500)
    
    def activate_exam(self, request, exam_id: int) -> JsonResponse:
        """Manually activate an exam"""
        try:
            if not self.is_admin_user(request.user):
                return JsonResponse({'error': 'Admin access required'}, status=403)
            
            try:
                exam = EnhancedExam.objects.get(id=exam_id)
            except EnhancedExam.DoesNotExist:
                return JsonResponse({'error': 'Exam not found'}, status=404)
            
            if exam.status != 'scheduled':
                return JsonResponse({'error': 'Only scheduled exams can be activated'}, status=400)
            
            # Use broadcasting service to activate
            result = self.broadcasting_service.activate_exam_now(exam_id)
            
            if result['success']:
                # Log the manual activation
                logger.info(f"Exam {exam_id} manually activated by admin {request.user.username}")
                
                # Create notification
                ExamNotification.objects.create(
                    exam=exam,
                    notification_type='exam_started',
                    title='Exam Started',
                    message=f'Exam "{exam.title}" has been activated',
                    is_sent=True,
                    sent_at=timezone.now()
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Exam activated successfully',
                    'exam_id': exam_id,
                    'status': 'active'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result.get('error', 'Failed to activate exam')
                }, status=500)
                
        except Exception as e:
            logger.error(f"Error activating exam {exam_id}: {str(e)}")
            return JsonResponse({'error': 'Failed to activate exam'}, status=500)
    
    def end_exam(self, request, exam_id: int) -> JsonResponse:
        """Manually end an active exam"""
        try:
            if not self.is_admin_user(request.user):
                return JsonResponse({'error': 'Admin access required'}, status=403)
            
            try:
                exam = EnhancedExam.objects.get(id=exam_id)
            except EnhancedExam.DoesNotExist:
                return JsonResponse({'error': 'Exam not found'}, status=404)
            
            if exam.status != 'active':
                return JsonResponse({'error': 'Only active exams can be ended'}, status=400)
            
            # Use broadcasting service to end exam
            result = self.broadcasting_service.handle_exam_end(exam_id)
            
            if result['success']:
                # Log the manual ending
                logger.info(f"Exam {exam_id} manually ended by admin {request.user.username}")
                
                # Update exam status
                exam.status = 'completed'
                exam.end_time = timezone.now()
                exam.save()
                
                # Create notification
                ExamNotification.objects.create(
                    exam=exam,
                    notification_type='exam_ended',
                    title='Exam Ended',
                    message=f'Exam "{exam.title}" has been ended by administrator',
                    is_sent=True,
                    sent_at=timezone.now()
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Exam ended successfully',
                    'exam_id': exam_id,
                    'status': 'completed',
                    'ended_at': timezone.now().isoformat()
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result.get('error', 'Failed to end exam')
                }, status=500)
                
        except Exception as e:
            logger.error(f"Error ending exam {exam_id}: {str(e)}")
            return JsonResponse({'error': 'Failed to end exam'}, status=500)
    
    def get_exam_analytics(self, request, exam_id: int) -> JsonResponse:
        """Get comprehensive analytics for an exam"""
        try:
            if not self.is_admin_user(request.user):
                return JsonResponse({'error': 'Admin access required'}, status=403)
            
            try:
                exam = EnhancedExam.objects.get(id=exam_id)
            except EnhancedExam.DoesNotExist:
                return JsonResponse({'error': 'Exam not found'}, status=404)
            
            # Get or create analytics
            analytics, created = ExamAnalytics.objects.get_or_create(
                exam=exam,
                defaults={
                    'total_attempts': 0,
                    'completion_rate': 0,
                    'average_score': 0,
                    'average_time_taken': 0,
                    'question_analytics': {}
                }
            )
            
            # Calculate real-time analytics
            attempts = StudentExamAttempt.objects.filter(exam=exam)
            completed_attempts = attempts.filter(status='completed')
            
            total_attempts = attempts.count()
            completion_rate = (completed_attempts.count() / total_attempts * 100) if total_attempts > 0 else 0
            
            # Calculate averages for completed attempts
            avg_score = completed_attempts.aggregate(Avg('score'))['score__avg'] or 0
            
            # Calculate average time taken
            avg_time = 0
            if completed_attempts.exists():
                total_time = sum([
                    (attempt.end_time - attempt.start_time).total_seconds()
                    for attempt in completed_attempts
                    if attempt.start_time and attempt.end_time
                ])
                avg_time = total_time / completed_attempts.count() if completed_attempts.count() > 0 else 0
            
            # Update analytics
            analytics.total_attempts = total_attempts
            analytics.completion_rate = completion_rate
            analytics.average_score = avg_score
            analytics.average_time_taken = avg_time
            analytics.save()
            
            # Prepare response data
            analytics_data = {
                'exam_id': exam.id,
                'total_attempts': total_attempts,
                'completed_attempts': completed_attempts.count(),
                'completion_rate': round(completion_rate, 2),
                'average_score': round(avg_score, 2),
                'average_time_taken': round(avg_time, 2),
                'pass_rate': completed_attempts.filter(
                    score__gte=exam.pass_threshold
                ).count() / completed_attempts.count() * 100 if completed_attempts.count() > 0 else 0,
                'difficulty_stats': {
                    'easy_questions': exam.questions.filter(difficulty='easy').count(),
                    'medium_questions': exam.questions.filter(difficulty='medium').count(),
                    'hard_questions': exam.questions.filter(difficulty='hard').count(),
                },
                'subject_distribution': list(
                    exam.subjects.values('name').annotate(
                        question_count=Count('question', filter=Q(question__in=exam.questions.all()))
                    )
                ),
                'score_distribution': self._get_score_distribution(completed_attempts),
                'time_distribution': self._get_time_distribution(completed_attempts),
                'last_updated': analytics.last_updated.isoformat(),
            }
            
            return JsonResponse(analytics_data)
            
        except Exception as e:
            logger.error(f"Error fetching analytics for exam {exam_id}: {str(e)}")
            return JsonResponse({'error': 'Failed to fetch exam analytics'}, status=500)
    
    def _get_score_distribution(self, attempts) -> Dict[str, int]:
        """Calculate score distribution for visualization"""
        ranges = {
            '0-20': 0, '21-40': 0, '41-60': 0, '61-80': 0, '81-100': 0
        }
        
        for attempt in attempts:
            score = attempt.score or 0
            if score <= 20:
                ranges['0-20'] += 1
            elif score <= 40:
                ranges['21-40'] += 1
            elif score <= 60:
                ranges['41-60'] += 1
            elif score <= 80:
                ranges['61-80'] += 1
            else:
                ranges['81-100'] += 1
        
        return ranges
    
    def _get_time_distribution(self, attempts) -> Dict[str, int]:
        """Calculate time distribution for visualization"""
        ranges = {
            '0-15min': 0, '16-30min': 0, '31-45min': 0, '46-60min': 0, '60+min': 0
        }
        
        for attempt in attempts:
            if attempt.start_time and attempt.end_time:
                duration_minutes = (attempt.end_time - attempt.start_time).total_seconds() / 60
                
                if duration_minutes <= 15:
                    ranges['0-15min'] += 1
                elif duration_minutes <= 30:
                    ranges['16-30min'] += 1
                elif duration_minutes <= 45:
                    ranges['31-45min'] += 1
                elif duration_minutes <= 60:
                    ranges['46-60min'] += 1
                else:
                    ranges['60+min'] += 1
        
        return ranges


# Create the API instance
monitoring_api = AdminExamMonitoringAPI()

# URL Configuration Views
@login_required
@require_http_methods(["GET"])
def exam_monitoring_view(request):
    """Get comprehensive monitoring data for all exams"""
    return monitoring_api.get_exam_monitoring_data(request)

@login_required
@require_http_methods(["GET"])
def exam_live_stats_view(request, exam_id):
    """Get real-time statistics for a specific exam"""
    return monitoring_api.get_exam_live_stats(request, exam_id)

@login_required
@require_http_methods(["GET"])
def exam_student_progress_view(request, exam_id):
    """Get detailed progress for all students taking the exam"""
    return monitoring_api.get_student_progress(request, exam_id)

@login_required
@require_POST
@csrf_exempt
def activate_exam_view(request, exam_id):
    """Manually activate an exam"""
    return monitoring_api.activate_exam(request, exam_id)

@login_required
@require_POST
@csrf_exempt
def end_exam_view(request, exam_id):
    """Manually end an active exam"""
    return monitoring_api.end_exam(request, exam_id)

@login_required
@require_http_methods(["GET"])
def exam_analytics_view(request, exam_id):
    """Get comprehensive analytics for an exam"""
    return monitoring_api.get_exam_analytics(request, exam_id)

# WebSocket consumers for real-time updates (if using Django Channels)
try:
    import channels
    from channels.generic.websocket import AsyncWebsocketConsumer
    import json
    
    class ExamMonitoringConsumer(AsyncWebsocketConsumer):
        """WebSocket consumer for real-time exam monitoring updates"""
        
        async def connect(self):
            self.exam_id = self.scope['url_route']['kwargs']['exam_id']
            self.room_group_name = f'exam_monitoring_{self.exam_id}'
            
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
        
        async def disconnect(self, close_code):
            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        
        async def receive(self, text_data):
            # Handle incoming WebSocket messages if needed
            pass
        
        async def exam_update(self, event):
            # Send exam update to WebSocket
            await self.send(text_data=json.dumps({
                'type': 'exam_update',
                'data': event['data']
            }))
            
except ImportError:
    # Django Channels not installed, skip WebSocket functionality
    pass

print("✅ Enhanced admin monitoring API endpoints created successfully!")
print("📊 Features implemented:")
print("   - Real-time exam monitoring dashboard")
print("   - Live student progress tracking") 
print("   - Comprehensive exam analytics")
print("   - Manual exam activation/ending")
print("   - WebSocket support for real-time updates")
print("   - Industry-standard exam management")