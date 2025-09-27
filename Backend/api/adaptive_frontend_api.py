"""
Enhanced Adaptive Learning Frontend API
Integrates BKT/DKT orchestration with mastery tracking for real-time frontend updates
"""

import json
import logging
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction, models
from django.utils import timezone
from django.db.models import Q, F, Avg, Count, Case, When

from django.contrib.auth.models import User
from assessment.improved_models import (
    StudentSession, Subject, Chapter,
    QuestionAttempt, StudentMastery
)
from assessment.models import AdaptiveQuestion

logger = logging.getLogger(__name__)

# Mock adaptive manager for now - will integrate with your existing one
class AdaptiveSessionManager:
    def get_next_question(self, **kwargs):
        # Integration with your existing adaptive system
        try:
            subject_id = kwargs.get('subject_id')
            chapter_id = kwargs.get('chapter_id') 
            current_mastery = kwargs.get('current_mastery', 0.0)
            
            # Map mastery level to your difficulty levels
            difficulty_map = {
                0.0: 'very_easy',
                0.3: 'easy', 
                0.6: 'moderate',
                0.8: 'difficult'
            }
            
            target_difficulty = 'very_easy'
            for threshold, diff in difficulty_map.items():
                if current_mastery >= threshold:
                    target_difficulty = diff
            
            # Query questions using your actual field structure
            questions = AdaptiveQuestion.objects.filter(
                difficulty_level=target_difficulty,
                is_active=True
            )
            
            # Filter by subject using the subject field (not subject_fk)
            if subject_id:
                try:
                    # Get subject by ID if it's numeric, or by code if it's string
                    if str(subject_id).isdigit():
                        subject_obj = Subject.objects.get(id=subject_id)
                        questions = questions.filter(subject=subject_obj.code)
                    else:
                        # Direct subject code filtering
                        questions = questions.filter(subject=subject_id)
                except Subject.DoesNotExist:
                    logger.warning(f"Subject with ID {subject_id} not found")
            
            if chapter_id:
                questions = questions.filter(chapter_id=chapter_id)
            
            question = questions.first()
            
            if question:
                return {
                    'id': str(question.id),
                    'question_text': question.question_text,
                    'options': question.formatted_options,
                    'difficulty': question.difficulty_level,
                    'subject': question.subject,
                    'chapter_name': question.chapter.name if question.chapter else None
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting next question: {e}")
            return None
    
    def process_answer(self, **kwargs):
        # Integration with your BKT/DKT system
        question_id = kwargs.get('question_id')
        user_answer = kwargs.get('user_answer')
        
        try:
            question = AdaptiveQuestion.objects.get(id=question_id)
            is_correct = str(user_answer).strip().lower() == str(question.answer).strip().lower()
            
            # Mock BKT/DKT probabilities - integrate with your actual system
            bkt_probability = min(0.9, 0.5 + (0.1 if is_correct else -0.1))
            dkt_prediction = min(0.9, 0.6 + (0.1 if is_correct else -0.1))
            
            return {
                'is_correct': is_correct,
                'bkt_probability': bkt_probability,
                'dkt_prediction': dkt_prediction,
                'has_next_question': True
            }
        except AdaptiveQuestion.DoesNotExist:
            return {
                'is_correct': False,
                'bkt_probability': 0.0,
                'dkt_prediction': 0.0,
                'has_next_question': False
            }

adaptive_manager = AdaptiveSessionManager()

@csrf_exempt
@require_http_methods(["POST"])
def get_next_adaptive_question(request):
    """
    Get next adaptive question based on current mastery and performance
    Enhanced with real-time mastery tracking
    """
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        user_id = data.get('user_id') 
        subject_id = data.get('subject_id')
        chapter_id = data.get('chapter_id', None)
        
        if not all([session_id, user_id, subject_id]):
            return JsonResponse({
                'success': False,
                'error': 'Missing required fields: session_id, user_id, subject_id'
            }, status=400)
        
        # Get or create basic session (simplified)
        try:
            user = User.objects.get(id=user_id)
            
            # Handle subject - could be ID or code
            if str(subject_id).isdigit():
                subject = Subject.objects.get(id=subject_id)
            else:
                subject = Subject.objects.get(code=subject_id)
            
            chapter = None
            if chapter_id:
                chapter = Chapter.objects.get(id=chapter_id)
            
            # Get or create session using existing session or create new one
            # Since StudentSession doesn't have session_id field, we'll use a different approach
            session = StudentSession.objects.filter(
                student=user,
                subject=subject,
                status='ACTIVE'
            ).first()
            
            if not session:
                # Create new session
                session = StudentSession.objects.create(
                    student=user,
                    subject=subject,
                    chapter=chapter,
                    session_type='PRACTICE',
                    status='ACTIVE'
                )
                created = True
            else:
                created = False
            
        except (User.DoesNotExist, Subject.DoesNotExist, Chapter.DoesNotExist) as e:
            return JsonResponse({
                'success': False,
                'error': f'Invalid reference: {str(e)}'
            }, status=404)
        
        # Get current mastery (simplified)
        current_mastery = session.current_mastery_score if hasattr(session, 'current_mastery_score') else 0.0
        
        # Use adaptive manager to get next question
        next_question = adaptive_manager.get_next_question(
            user_id=user_id,
            subject_id=subject.code,  # Use subject code
            chapter_id=chapter_id,
            current_mastery=current_mastery,
            performance_history=[]
        )
        
        if not next_question:
            return JsonResponse({
                'success': False,
                'message': 'No more questions available for current mastery level',
                'mastery_achieved': current_mastery >= 0.8
            }, status=200)
        
        return JsonResponse({
            'success': True,
            'question': next_question,
            'mastery_status': {
                'current_score': current_mastery,
                'mastery_achieved': current_mastery >= 0.8,
                'mastery_level': get_mastery_level(current_mastery),
                'confidence': 0.5,  # Default confidence
                'questions_remaining': 5  # Default estimate
            },
            'session_info': {
                'session_id': str(session.id),  # Use the actual session UUID
                'questions_attempted': session.questions_attempted if hasattr(session, 'questions_attempted') else 0,
                'current_streak': getattr(session, 'current_streak', 0),
                'session_duration': 0  # Will calculate properly later
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error getting next question: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)


@csrf_exempt 
@require_http_methods(["POST"])
def submit_answer_with_mastery_update(request):
    """
    Submit answer and update mastery in real-time
    Returns updated mastery status for frontend
    """
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        question_id = data.get('question_id')
        user_answer = data.get('answer')
        response_time = data.get('response_time', 0)
        
        if not all([session_id, question_id, user_answer is not None]):
            return JsonResponse({
                'success': False,
                'error': 'Missing required fields: session_id, question_id, answer'
            }, status=400)
        
        # Get session and question
        try:
            session = StudentSession.objects.get(session_id=session_id)
            question = AdaptiveQuestion.objects.get(id=question_id)
        except (StudentSession.DoesNotExist, AdaptiveQuestion.DoesNotExist) as e:
            return JsonResponse({
                'success': False,
                'error': f'Invalid reference: {str(e)}'
            }, status=404)
        
        # Process answer with adaptive manager
        result = adaptive_manager.process_answer(
            session_id=session_id,
            question_id=question_id,
            user_answer=user_answer,
            response_time=response_time
        )
        
        # Create question attempt record
        with transaction.atomic():
            attempt = QuestionAttempt.objects.create(
                session=session,
                question=question,
                student_answer=str(user_answer),
                is_correct=result['is_correct'],
                response_time_seconds=response_time,
                bkt_knowledge_probability=result.get('bkt_probability', 0.0),
                dkt_prediction=result.get('dkt_prediction', 0.0)
            )
            
            # Update session statistics
            session.questions_attempted = F('questions_attempted') + 1
            if result['is_correct']:
                session.questions_correct = F('questions_correct') + 1
                session.current_streak = F('current_streak') + 1
                session.best_streak = models.Case(
                    models.When(current_streak__gt=F('best_streak'), then=F('current_streak')),
                    default=F('best_streak')
                )
            else:
                session.current_streak = 0
            
            session.save()
            session.refresh_from_db()
            
            # Update mastery records
            updated_mastery = update_mastery_tracking(
                session, question, result['is_correct'], 
                result.get('bkt_probability', 0.0),
                result.get('dkt_prediction', 0.0)
            )
            
            # Update overall session mastery
            overall_mastery = calculate_overall_mastery(session)
            mastery_achieved = session.update_mastery_score(overall_mastery)
        
        return JsonResponse({
            'success': True,
            'result': {
                'correct': result['is_correct'],
                'correct_answer': question.answer,
                'explanation': getattr(question, 'explanation', 'No explanation available'),
                'points_earned': 10 if result['is_correct'] else 0
            },
            'mastery_update': {
                'overall_mastery': overall_mastery,
                'mastery_achieved': mastery_achieved,
                'mastery_level': get_mastery_level(overall_mastery),
                'subject_mastery': updated_mastery.get('subject_mastery', 0.0),
                'chapter_mastery': updated_mastery.get('chapter_mastery', 0.0),
                'confidence': updated_mastery.get('confidence', 0.0)
            },
            'session_stats': {
                'questions_attempted': session.questions_attempted,
                'questions_correct': session.questions_correct,
                'accuracy': session.questions_correct / session.questions_attempted if session.questions_attempted > 0 else 0,
                'current_streak': session.current_streak,
                'best_streak': session.best_streak
            },
            'next_question_available': result.get('has_next_question', True)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error submitting answer: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_real_time_mastery(request):
    """
    Get real-time mastery status for frontend updates
    """
    try:
        session_id = request.GET.get('session_id')
        if not session_id:
            return JsonResponse({
                'success': False,
                'error': 'Missing session_id parameter'
            }, status=400)
        
        try:
            session = StudentSession.objects.get(session_id=session_id)
        except StudentSession.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Session not found'
            }, status=404)
        
        # Get comprehensive mastery analytics
        mastery_analytics = session.get_mastery_analytics()
        
        # Get recent performance trend
        recent_attempts = QuestionAttempt.objects.filter(
            session=session
        ).order_by('-timestamp')[:10]
        
        performance_trend = [
            {
                'timestamp': attempt.timestamp.isoformat(),
                'correct': attempt.is_correct,
                'difficulty': attempt.question.difficulty_level,
                'response_time': attempt.response_time_seconds,
                'mastery_at_time': attempt.bkt_knowledge_probability
            }
            for attempt in recent_attempts
        ]
        
        return JsonResponse({
            'success': True,
            'mastery_status': {
                'overall_mastery': session.current_mastery_score,
                'mastery_achieved': session.mastery_achieved,
                'mastery_threshold': session.mastery_threshold,
                'mastery_achieved_at': session.mastery_achieved_at.isoformat() if session.mastery_achieved_at else None
            },
            'detailed_analytics': mastery_analytics,
            'performance_trend': performance_trend,
            'session_summary': {
                'duration_minutes': get_session_duration_minutes(session),
                'questions_attempted': session.questions_attempted,
                'accuracy': session.questions_correct / session.questions_attempted if session.questions_attempted > 0 else 0,
                'learning_velocity': calculate_learning_velocity(session),
                'estimated_time_to_mastery': estimate_time_to_mastery(session)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting mastery status: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_mastery_dashboard(request):
    """
    Comprehensive mastery dashboard for analytics and reporting
    """
    try:
        user_id = request.GET.get('user_id')
        subject_id = request.GET.get('subject_id', None)
        time_range = request.GET.get('time_range', '7')  # days
        
        if not user_id:
            return JsonResponse({
                'success': False,
                'error': 'Missing user_id parameter'
            }, status=400)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Student not found'
            }, status=404)
        
        # Base query for time range
        cutoff_date = timezone.now() - timedelta(days=int(time_range))
        
        # Get sessions with mastery data
        sessions_query = StudentSession.objects.filter(
            user=user,
            updated_at__gte=cutoff_date
        ).select_related('subject', 'chapter')
        
        if subject_id:
            sessions_query = sessions_query.filter(subject_id=subject_id)
        
        sessions = sessions_query.order_by('-updated_at')
        
        # Aggregate mastery analytics
        dashboard_data = {
            'student_summary': {
                'student_id': user.id,
                'username': user.username,
                'total_sessions': sessions.count(),
                'subjects_studied': sessions.values('subject').distinct().count(),
                'average_mastery': sessions.aggregate(avg_mastery=Avg('current_mastery_score'))['avg_mastery'] or 0.0
            },
            'mastery_progression': [],
            'subject_masteries': {},
            'chapter_masteries': {},
            'learning_insights': {}
        }
        
        # Process each session for detailed analytics
        for session in sessions:
            # Mastery progression
            dashboard_data['mastery_progression'].append({
                'date': session.updated_at.date().isoformat(),
                'mastery_score': session.current_mastery_score,
                'subject': session.subject.name,
                'chapter': session.chapter.name if session.chapter else 'Overall',
                'questions_attempted': session.questions_attempted,
                'accuracy': session.questions_correct / session.questions_attempted if session.questions_attempted > 0 else 0
            })
            
            # Subject-level aggregation
            subject_name = session.subject.name
            if subject_name not in dashboard_data['subject_masteries']:
                dashboard_data['subject_masteries'][subject_name] = {
                    'subject_id': session.subject.id,
                    'current_mastery': 0.0,
                    'sessions_count': 0,
                    'total_questions': 0,
                    'mastery_achieved': False
                }
            
            dashboard_data['subject_masteries'][subject_name]['current_mastery'] = max(
                dashboard_data['subject_masteries'][subject_name]['current_mastery'],
                session.current_mastery_score
            )
            dashboard_data['subject_masteries'][subject_name]['sessions_count'] += 1
            dashboard_data['subject_masteries'][subject_name]['total_questions'] += session.questions_attempted
            dashboard_data['subject_masteries'][subject_name]['mastery_achieved'] = dashboard_data['subject_masteries'][subject_name]['mastery_achieved'] or session.mastery_achieved
        
        # Get detailed mastery records
        mastery_records = StudentMastery.objects.filter(
            student_session__user=user,
            last_updated__gte=cutoff_date
        ).select_related('subject', 'chapter', 'student_session')
        
        if subject_id:
            mastery_records = mastery_records.filter(subject_id=subject_id)
        
        # Process mastery records
        for record in mastery_records:
            chapter_key = f"{record.subject.name}_{record.chapter.name}"
            dashboard_data['chapter_masteries'][chapter_key] = {
                'subject_name': record.subject.name,
                'chapter_name': record.chapter.name,
                'mastery_score': record.mastery_score,
                'mastery_level': record.mastery_level,
                'confidence': record.confidence_score,
                'questions_attempted': record.questions_attempted,
                'accuracy': record.accuracy_rate,
                'bkt_probability': record.bkt_knowledge_probability,
                'dkt_confidence': record.dkt_prediction_confidence,
                'last_updated': record.last_updated.isoformat()
            }
        
        return JsonResponse({
            'success': True,
            'dashboard': dashboard_data,
            'metadata': {
                'time_range_days': int(time_range),
                'generated_at': timezone.now().isoformat(),
                'total_mastery_records': len(dashboard_data['chapter_masteries']),
                'subjects_with_mastery': len(dashboard_data['subject_masteries'])
            }
        })
        
    except Exception as e:
        logger.error(f"Error generating mastery dashboard: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)


# Helper Functions

def get_current_mastery_state(session, subject, chapter=None):
    """Get current mastery state for session"""
    mastery_records = StudentMastery.objects.filter(
        student_session=session,
        subject=subject
    )
    
    if chapter:
        mastery_records = mastery_records.filter(chapter=chapter)
    
    if mastery_records.exists():
        latest_record = mastery_records.order_by('-last_updated').first()
        return {
            'overall_mastery': session.current_mastery_score,
            'subject_mastery': latest_record.mastery_score,
            'mastery_level': latest_record.mastery_level,
            'confidence': latest_record.confidence_score,
            'mastery_achieved': session.mastery_achieved,
            'recent_performance': get_recent_performance(session)
        }
    
    return {
        'overall_mastery': 0.0,
        'subject_mastery': 0.0,
        'mastery_level': 'novice',
        'confidence': 0.0,
        'mastery_achieved': False,
        'recent_performance': []
    }


def get_recent_performance(session, limit=5):
    """Get recent performance data"""
    attempts = QuestionAttempt.objects.filter(
        session=session
    ).order_by('-timestamp')[:limit]
    
    return [
        {
            'correct': attempt.is_correct,
            'difficulty': attempt.question.difficulty_level,
            'timestamp': attempt.timestamp.isoformat()
        }
        for attempt in attempts
    ]


def update_mastery_tracking(session, question, is_correct, bkt_probability, dkt_prediction):
    """Update mastery tracking records"""
    mastery_record, created = StudentMastery.objects.get_or_create(
        student_session=session,
        subject=session.subject,
        chapter=session.chapter or question.chapter,
        defaults={
            'mastery_score': 0.0,
            'confidence_score': 0.0
        }
    )
    
    # Update metrics
    mastery_record.questions_attempted += 1
    if is_correct:
        mastery_record.questions_correct += 1
    
    # Update BKT/DKT metrics
    mastery_record.bkt_knowledge_probability = bkt_probability
    mastery_record.dkt_prediction_confidence = dkt_prediction
    
    # Recalculate mastery score (weighted average of BKT and DKT)
    mastery_record.mastery_score = (bkt_probability + dkt_prediction) / 2
    mastery_record.confidence_score = min(bkt_probability, dkt_prediction)
    
    # Update mastery level
    mastery_record.update_mastery_level()
    
    return {
        'subject_mastery': mastery_record.mastery_score,
        'chapter_mastery': mastery_record.mastery_score,
        'confidence': mastery_record.confidence_score
    }


def calculate_overall_mastery(session):
    """Calculate overall session mastery"""
    mastery_records = session.mastery_records.all()
    if not mastery_records.exists():
        return 0.0
    
    total_score = sum(record.mastery_score for record in mastery_records)
    return total_score / mastery_records.count()


def get_mastery_level(score):
    """Get mastery level from score"""
    if score >= 0.85:
        return 'expert'
    elif score >= 0.70:
        return 'advanced'
    elif score >= 0.50:
        return 'proficient'
    elif score >= 0.30:
        return 'developing'
    else:
        return 'novice'


def estimate_questions_to_mastery(mastery_data):
    """Estimate questions remaining to achieve mastery"""
    current_score = mastery_data['overall_mastery']
    if current_score >= 0.8:
        return 0
    
    # Simple estimation based on current progress
    progress_needed = 0.8 - current_score
    questions_per_point = 5  # Estimated questions per mastery point
    return int(progress_needed * 100 * questions_per_point)


def estimate_time_to_mastery(session):
    """Estimate time to mastery in minutes"""
    if session.mastery_achieved:
        return 0
    
    questions_remaining = estimate_questions_to_mastery({
        'overall_mastery': session.current_mastery_score
    })
    
    # Average 2 minutes per question
    return questions_remaining * 2


def get_session_duration_minutes(session):
    """Get session duration in minutes"""
    if not session.session_start_time:
        return 0
    
    end_time = session.session_end_time or timezone.now()
    duration = end_time - session.session_start_time
    return round(duration.total_seconds() / 60, 2)


def calculate_learning_velocity(session):
    """Calculate learning velocity (questions per minute)"""
    duration_minutes = get_session_duration_minutes(session)
    if duration_minutes == 0:
        return 0.0
    
    return round(session.questions_attempted / duration_minutes, 2)


def update_session_analytics(session, new_data):
    """Update session analytics with new data"""
    analytics = session.session_analytics or {}
    analytics.update(new_data)
    session.session_analytics = analytics
    session.save(update_fields=['session_analytics'])