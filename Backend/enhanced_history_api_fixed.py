

#!/usr/bin/env python3
"""
Enhanced History API for Adaptive Learning Sessions - FIXED VERSION

This provides comprehensive session history with adaptive learning insights
Fixed to use actual model field names.
"""

import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')
django.setup()

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.db.models import Count, Avg, Q
from django.utils import timezone
import json
import logging

from assessment.models import StudentSession, QuestionAttempt
from core.models import StudentProfile

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET"])
def get_student_session_history(request, username):
    """
    Get comprehensive session history for a student - FIXED VERSION
    """
    try:
        # Check if student user exists
        try:
            student = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'User "{username}" not found',
                'student_username': username,
                'summary': {
                    'total_sessions': 0,
                    'completed_sessions': 0,
                    'total_questions_attempted': 0,
                    'overall_accuracy': 0.0,
                    'assessment_sessions_count': 0,
                    'adaptive_sessions_count': 0,
                    'subject_breakdown': {}
                },
                'assessment_sessions': [],
                'adaptive_sessions': [],
                'generated_at': timezone.now().isoformat()
            }, status=404)
        
        # Get all sessions with related data
        sessions = StudentSession.objects.filter(student=student).select_related('subject', 'chapter').order_by('-created_at')
        
        if not sessions.exists():
            return JsonResponse({
                'success': True,
                'student_username': username,
                'summary': {
                    'total_sessions': 0,
                    'completed_sessions': 0,
                    'total_questions_attempted': 0,
                    'overall_accuracy': 0.0,
                    'assessment_sessions_count': 0,
                    'adaptive_sessions_count': 0,
                    'subject_breakdown': {}
                },
                'assessment_sessions': [],
                'adaptive_sessions': [],
                'generated_at': timezone.now().isoformat()
            })
        
        # Categorize sessions
        assessment_sessions = []
        adaptive_sessions = []
        
        # Summary statistics - calculate from actual question attempts
        total_sessions = sessions.count()
        completed_sessions = sessions.filter(status='COMPLETED').count()
        
        # Calculate accurate totals from QuestionAttempt records
        total_questions = 0
        total_correct = 0
        
        for session in sessions:
            session_attempts = QuestionAttempt.objects.filter(session=session)
            session_total = session_attempts.count()
            session_correct = session_attempts.filter(is_correct=True).count()
            
            total_questions += session_total
            total_correct += session_correct
        
        overall_accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
        
        # Subject breakdown
        subject_stats = {}
        
        for session in sessions:
            # Calculate actual statistics from question attempts
            session_attempts = QuestionAttempt.objects.filter(session=session)
            actual_attempted = session_attempts.count()
            actual_correct = session_attempts.filter(is_correct=True).count()
            actual_accuracy = (actual_correct / actual_attempted * 100) if actual_attempted > 0 else 0
            
            # Basic session data
            session_data = {
                'session_id': str(session.id),
                'session_name': session.session_name or f"Session {session.id}",
                'session_type': session.session_type,
                'subject': session.subject.name if hasattr(session.subject, 'name') else str(session.subject),
                'chapter': session.chapter.name if session.chapter else None,
                'status': session.status,
                'created_at': session.created_at.isoformat(),
                'ended_at': session.session_end_time.isoformat() if session.session_end_time else None,
                'duration_minutes': int(session.session_duration_seconds / 60) if session.session_duration_seconds else 0,
                'questions_attempted': actual_attempted,      # Use actual count
                'questions_correct': actual_correct,          # Use actual count
                'accuracy_percentage': round(actual_accuracy, 1),  # Use calculated accuracy
                'total_score': session.total_score,
                'percentage_score': round(actual_accuracy, 1),     # Use calculated accuracy
                # Keep original for reference
                'original_stats': {
                    'recorded_attempted': session.questions_attempted,
                    'recorded_correct': session.questions_correct,
                    'recorded_accuracy': session.accuracy_percentage
                }
            }
            
            # Get recent question attempts (simplified)
            recent_attempts = QuestionAttempt.objects.filter(
                session=session
            ).select_related('question').order_by('-question_displayed_at')[:10]
            
            attempt_details = []
            for attempt in recent_attempts:
                attempt_details.append({
                    'question_id': str(attempt.question.id),
                    'is_correct': attempt.is_correct,
                    'selected_answer': attempt.student_answer or '',
                    'time_spent': attempt.time_spent_seconds,
                    'difficulty': attempt.difficulty_when_presented,
                    'skill_id': attempt.question.subject.name if hasattr(attempt.question.subject, 'name') else str(attempt.question.subject) if attempt.question.subject else 'unknown',
                    'timestamp': attempt.question_displayed_at.isoformat(),
                })
            
            session_data['recent_attempts'] = attempt_details
            
            # Categorize based on session type
            if session.session_type in ['COMPETITIVE_EXAM', 'PRACTICE_TEST', 'ASSESSMENT']:
                assessment_sessions.append(session_data)
            else:  # ADAPTIVE_LEARNING or others
                # Add adaptive-specific data
                session_data.update({
                    'current_difficulty': session.current_difficulty_level,
                    'difficulty_adjustments': len(session.difficulty_adjustments) if session.difficulty_adjustments else 0,
                })
                adaptive_sessions.append(session_data)
            
            # Update subject statistics
            subject_name = session.subject.name if hasattr(session.subject, 'name') else str(session.subject) if session.subject else 'Unknown'
            if subject_name not in subject_stats:
                subject_stats[subject_name] = {
                    'total_sessions': 0,
                    'total_questions': 0,
                    'total_correct': 0,
                    'accuracy': 0.0
                }
            
            subject_stats[subject_name]['total_sessions'] += 1
            subject_stats[subject_name]['total_questions'] += actual_attempted  # Use actual count
            subject_stats[subject_name]['total_correct'] += actual_correct      # Use actual count
        
        # Calculate subject accuracies
        for subject, stats in subject_stats.items():
            if stats['total_questions'] > 0:
                stats['accuracy'] = round((stats['total_correct'] / stats['total_questions']) * 100, 1)
        
        response_data = {
            'success': True,
            'student_username': username,
            'summary': {
                'total_sessions': total_sessions,
                'completed_sessions': completed_sessions,
                'total_questions_attempted': total_questions,
                'overall_accuracy': round(overall_accuracy, 1),
                'assessment_sessions_count': len(assessment_sessions),
                'adaptive_sessions_count': len(adaptive_sessions),
                'subject_breakdown': subject_stats
            },
            'assessment_sessions': assessment_sessions,
            'adaptive_sessions': adaptive_sessions,
            'generated_at': timezone.now().isoformat()
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error fetching session history: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Failed to fetch session history'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_adaptive_learning_analytics(request, username):
    """
    Get adaptive learning specific analytics - SIMPLIFIED VERSION
    """
    try:
        try:
            student = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'User "{username}" not found'
            }, status=404)
        
        # Get adaptive learning sessions
        adaptive_sessions = StudentSession.objects.filter(
            student=student,
            session_type='ADAPTIVE_LEARNING'
        ).order_by('-created_at')
        
        if not adaptive_sessions.exists():
            return JsonResponse({
                'success': True,
                'student_username': username,
                'analytics': {
                    'total_adaptive_sessions': 0,
                    'avg_mastery_improvement': 0,
                    'subjects_studied': [],
                    'difficulty_trends': []
                }
            })
        
        # Simple analytics
        analytics = {
            'total_adaptive_sessions': adaptive_sessions.count(),
            'subjects_studied': list(set(s.subject.name if hasattr(s.subject, 'name') else str(s.subject) for s in adaptive_sessions if s.subject)),
            'avg_accuracy': sum(s.accuracy_percentage for s in adaptive_sessions) / adaptive_sessions.count(),
            'total_questions': sum(s.questions_attempted for s in adaptive_sessions),
            'difficulty_trends': []  # Simplified - could be enhanced
        }
        
        return JsonResponse({
            'success': True,
            'student_username': username,
            'analytics': analytics
        })
        
    except Exception as e:
        logger.error(f"Error fetching adaptive analytics: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_session_details(request, session_id):
    """
    Get detailed information about a specific session - SIMPLIFIED VERSION
    """
    try:
        try:
            session = StudentSession.objects.get(id=session_id)
        except StudentSession.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'Session "{session_id}" not found'
            }, status=404)
        
        # Get question attempts
        attempts = QuestionAttempt.objects.filter(
            session=session
        ).select_related('question').order_by('question_number_in_session')
        
        # Calculate actual statistics from question attempts
        actual_total_questions = attempts.count()
        actual_correct_answers = attempts.filter(is_correct=True).count()
        actual_accuracy = (actual_correct_answers / actual_total_questions * 100) if actual_total_questions > 0 else 0
        
        attempt_details = []
        for attempt in attempts:
            attempt_details.append({
                'question_number': attempt.question_number_in_session,
                'question_id': str(attempt.question.id),
                'is_correct': attempt.is_correct,
                'student_answer': attempt.student_answer or '',
                'correct_answer': attempt.correct_answer or '',
                'time_spent': attempt.time_spent_seconds,
                'difficulty': attempt.difficulty_when_presented,
                'points_earned': attempt.points_earned,
                'timestamp': attempt.question_displayed_at.isoformat() if attempt.question_displayed_at else attempt.created_at.isoformat()
            })
        
        session_details = {
            'session_id': str(session.id),
            'session_name': session.session_name or f"Session {session.id}",
            'session_type': session.session_type,
            'student_username': session.student.username,
            'subject': session.subject.name if hasattr(session.subject, 'name') else str(session.subject) if session.subject else 'Unknown',
            'status': session.status,
            'created_at': session.created_at.isoformat(),
            'duration_minutes': int(session.session_duration_seconds / 60) if session.session_duration_seconds else 0,
            'questions_attempted': actual_total_questions,  # Use actual count from attempts
            'questions_correct': actual_correct_answers,    # Use actual count from attempts
            'accuracy_percentage': round(actual_accuracy, 1),  # Use calculated accuracy
            'question_attempts': attempt_details,
            'total_questions_in_session': len(attempt_details),
            # Keep original session record for reference (in case needed for debugging)
            'session_record_stats': {
                'recorded_attempted': session.questions_attempted,
                'recorded_correct': session.questions_correct,
                'recorded_accuracy': session.accuracy_percentage
            }
        }
        
        return JsonResponse({
            'success': True,
            'session_details': session_details
        })
        
    except Exception as e:
        logger.error(f"Error fetching session details: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Failed to fetch session details'
        }, status=500)