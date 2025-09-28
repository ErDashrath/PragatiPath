#!/usr/bin/env python3
"""
Fixed Enhanced History API - Using actual model fields
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
        
        # Summary statistics
        total_sessions = sessions.count()
        completed_sessions = sessions.filter(status='COMPLETED').count()
        total_questions = sum(s.questions_attempted for s in sessions)
        total_correct = sum(s.questions_correct for s in sessions)
        overall_accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
        
        # Subject breakdown
        subject_stats = {}
        
        for session in sessions:
            # Basic session data
            session_data = {
                'session_id': str(session.session_id),
                'session_name': session.session_name or f"Session {session.session_id}",
                'session_type': session.session_type,
                'subject': session.subject.name if session.subject else 'Unknown',
                'chapter': session.chapter.name if session.chapter else None,
                'status': session.status,
                'created_at': session.created_at.isoformat(),
                'ended_at': session.session_end_time.isoformat() if session.session_end_time else None,
                'duration_minutes': int(session.session_duration_seconds / 60) if session.session_duration_seconds else 0,
                'questions_attempted': session.questions_attempted,
                'questions_correct': session.questions_correct,
                'accuracy_percentage': session.accuracy_percentage,
                'total_score': session.total_score,
                'percentage_score': session.percentage_score,
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
                    'skill_id': attempt.question.subject.name if attempt.question.subject else 'unknown',
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
            subject_name = session.subject.name if session.subject else 'Unknown'
            if subject_name not in subject_stats:
                subject_stats[subject_name] = {
                    'total_sessions': 0,
                    'total_questions': 0,
                    'total_correct': 0,
                    'accuracy': 0.0
                }
            
            subject_stats[subject_name]['total_sessions'] += 1
            subject_stats[subject_name]['total_questions'] += session.questions_attempted
            subject_stats[subject_name]['total_correct'] += session.questions_correct
        
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

if __name__ == "__main__":
    print("Fixed Enhanced History API - using actual model fields")