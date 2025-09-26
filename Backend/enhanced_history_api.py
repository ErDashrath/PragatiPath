#!/usr/bin/env python3
"""
Enhanced History API for Adaptive Learning Sessions

This provides comprehensive session history with adaptive learning insights
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
from django.shortcuts import get_object_or_404
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
    Get comprehensive session history for a student
    
    GET /history/student/<username>/
    
    Response includes:
    - All sessions (assessment + adaptive learning)
    - Session type categorization
    - Performance metrics
    - Adaptive learning insights
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
        
        # Categorize sessions
        assessment_sessions = []
        adaptive_sessions = []
        
        for session in sessions[:50]:  # Limit to recent 50 sessions
            attempts = QuestionAttempt.objects.filter(session=session)
            
            session_data = {
                'session_id': str(session.id),
                'session_name': session.session_name or f"{session.subject.name} Session",
                'session_type': session.session_type,
                'subject': session.subject.name if session.subject else 'Unknown',
                'chapter': session.chapter.name if session.chapter else None,
                'status': session.status,
                'created_at': session.created_at.isoformat(),
                'ended_at': session.session_end_time.isoformat() if session.session_end_time else None,
                'duration_minutes': round(session.session_duration_seconds / 60, 1) if session.session_duration_seconds > 0 else 0,
                
                # Performance metrics
                'questions_attempted': session.questions_attempted,
                'questions_correct': session.questions_correct,
                'accuracy_percentage': round(session.accuracy_percentage, 1),
                'total_score': session.total_score,
                'percentage_score': round(session.percentage_score, 1),
                
                # Question details
                'total_questions_planned': session.total_questions_planned,
                'questions_skipped': session.questions_skipped,
                'questions_timeout': session.questions_timeout,
                
                # Adaptive learning specific
                'current_difficulty': session.current_difficulty_level,
                'difficulty_adjustments': len(session.difficulty_adjustments) if session.difficulty_adjustments else 0,
                'adaptive_insights': {
                    'mastery_improvements': [],
                    'skill_progression': {},
                    'difficulty_progression': session.difficulty_adjustments[-5:] if session.difficulty_adjustments else []
                }
            }
            
            # Add attempt-level details
            attempt_details = []
            for attempt in attempts[:15]:  # Limit to recent 15 attempts per session
                attempt_details.append({
                    'question_id': str(attempt.question.id),
                    'is_correct': attempt.is_correct,
                    'selected_answer': attempt.student_answer,
                    'time_spent': attempt.time_spent_seconds,
                    'difficulty': attempt.question.difficulty_level if hasattr(attempt.question, 'difficulty_level') else 'Unknown',
                    'skill_id': attempt.question.skill_id if hasattr(attempt.question, 'skill_id') else '',
                    'timestamp': attempt.timestamp.isoformat()
                })
            
            session_data['recent_attempts'] = attempt_details
            
            # Categorize based on session characteristics
            if (session.session_type in ['ADAPTIVE', 'PRACTICE'] or 
                'adaptive' in session.session_name.lower() or
                session.difficulty_adjustments):
                adaptive_sessions.append(session_data)
            else:
                assessment_sessions.append(session_data)
        
        # Calculate overall statistics
        total_sessions = sessions.count()
        completed_sessions = sessions.filter(status='COMPLETED').count()
        total_questions = sum(s.questions_attempted for s in sessions)
        total_correct = sum(s.questions_correct for s in sessions)
        overall_accuracy = (total_correct / max(total_questions, 1)) * 100
        
        # Subject-wise breakdown
        subject_stats = {}
        for session in sessions:
            subject_name = session.subject.name if session.subject else 'Unknown'
            if subject_name not in subject_stats:
                subject_stats[subject_name] = {
                    'total_sessions': 0,
                    'total_questions': 0,
                    'total_correct': 0,
                    'accuracy': 0.0,
                    'avg_score': 0.0
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

@csrf_exempt
@require_http_methods(["GET"])
def get_adaptive_learning_analytics(request, username):
    """
    Get detailed adaptive learning analytics for a student
    
    GET /history/adaptive-analytics/<username>/
    """
    try:
        student = get_object_or_404(User, username=username)
        student_profile = get_object_or_404(StudentProfile, user=student)
        
        # Get adaptive learning sessions
        adaptive_sessions = StudentSession.objects.filter(
            student=student,
            session_type__in=['ADAPTIVE', 'PRACTICE']
        ).select_related('subject').order_by('-created_at')
        
        # Calculate BKT progression over time
        bkt_progression = []
        for session in adaptive_sessions[:20]:  # Recent 20 sessions
            attempts = QuestionAttempt.objects.filter(session=session)
            session_bkt = {
                'session_id': str(session.id),
                'date': session.created_at.date().isoformat(),
                'subject': session.subject.name if session.subject else 'Unknown',
                'skills_practiced': {},
                'mastery_improvements': [],
                'difficulty_adaptations': len(session.difficulty_adjustments) if session.difficulty_adjustments else 0
            }
            
            # Extract skill-level performance
            for attempt in attempts:
                skill = attempt.question.skill_id if hasattr(attempt.question, 'skill_id') and attempt.question.skill_id else 'general'
                if skill not in session_bkt['skills_practiced']:
                    session_bkt['skills_practiced'][skill] = {
                        'attempts': 0,
                        'correct': 0,
                        'accuracy': 0
                    }
                
                session_bkt['skills_practiced'][skill]['attempts'] += 1
                if attempt.is_correct:
                    session_bkt['skills_practiced'][skill]['correct'] += 1
            
            # Calculate skill accuracies
            for skill, data in session_bkt['skills_practiced'].items():
                if data['attempts'] > 0:
                    data['accuracy'] = round((data['correct'] / data['attempts']) * 100, 1)
            
            bkt_progression.append(session_bkt)
        
        # Get current BKT parameters
        current_bkt = student_profile.bkt_parameters
        
        # Subject mastery levels
        subject_mastery = {}
        for subject_code, progress in student_profile.subject_progress.items():
            subject_mastery[subject_code] = {
                'mastery_score': progress.get('mastery_score', 0.0),
                'current_difficulty': progress.get('current_difficulty', 'easy'),
                'level': progress.get('level', 1),
                'sessions_completed': adaptive_sessions.filter(
                    subject__code=subject_code if hasattr(adaptive_sessions.first().subject, 'code') else subject_code
                ).count() if adaptive_sessions.exists() else 0
            }
        
        response_data = {
            'success': True,
            'student_username': username,
            'adaptive_learning_analytics': {
                'bkt_progression': bkt_progression,
                'current_bkt_parameters': current_bkt,
                'subject_mastery_levels': subject_mastery,
                'total_adaptive_sessions': adaptive_sessions.count(),
                'learning_insights': {
                    'most_improved_skills': [],
                    'challenging_areas': [],
                    'recommended_focus': []
                }
            },
            'generated_at': timezone.now().isoformat()
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error fetching adaptive analytics: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Failed to fetch adaptive learning analytics'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_session_details(request, session_id):
    """
    Get detailed information about a specific session
    
    GET /history/session-details/<session_id>/
    """
    try:
        session = get_object_or_404(StudentSession, id=session_id)
        attempts = QuestionAttempt.objects.filter(session=session).select_related('question').order_by('timestamp')
        
        # Build detailed session information
        attempt_details = []
        for i, attempt in enumerate(attempts, 1):
            attempt_details.append({
                'question_number': i,
                'question_id': str(attempt.question.id),
                'question_text': attempt.question.question_text[:200] + "..." if len(attempt.question.question_text) > 200 else attempt.question.question_text,
                'difficulty': attempt.question.difficulty_level if hasattr(attempt.question, 'difficulty_level') else 'Unknown',
                'skill_id': attempt.question.skill_id if hasattr(attempt.question, 'skill_id') else '',
                'selected_answer': attempt.student_answer,
                'correct_answer': attempt.question.answer if hasattr(attempt.question, 'answer') else 'Unknown',
                'is_correct': attempt.is_correct,
                'time_spent': attempt.time_spent_seconds,
                'timestamp': attempt.timestamp.isoformat(),
                'options': {
                    'A': attempt.question.option_a if hasattr(attempt.question, 'option_a') else '',
                    'B': attempt.question.option_b if hasattr(attempt.question, 'option_b') else '',
                    'C': attempt.question.option_c if hasattr(attempt.question, 'option_c') else '',
                    'D': attempt.question.option_d if hasattr(attempt.question, 'option_d') else ''
                }
            })
        
        session_details = {
            'session_id': str(session.id),
            'session_name': session.session_name or f"{session.subject.name} Session",
            'student': session.student.get_full_name() or session.student.username,
            'subject': session.subject.name if session.subject else 'Unknown',
            'chapter': session.chapter.name if session.chapter else None,
            'session_type': session.session_type,
            'status': session.status,
            'created_at': session.created_at.isoformat(),
            'duration_minutes': round(session.session_duration_seconds / 60, 1) if session.session_duration_seconds > 0 else 0,
            
            # Performance summary
            'performance': {
                'questions_attempted': session.questions_attempted,
                'questions_correct': session.questions_correct,
                'questions_incorrect': session.questions_incorrect,
                'questions_skipped': session.questions_skipped,
                'accuracy_percentage': round(session.accuracy_percentage, 1),
                'total_score': session.total_score,
                'percentage_score': round(session.percentage_score, 1)
            },
            
            # Adaptive learning insights
            'adaptive_insights': {
                'initial_difficulty': session.current_difficulty_level,
                'difficulty_adjustments': session.difficulty_adjustments,
                'total_adaptations': len(session.difficulty_adjustments) if session.difficulty_adjustments else 0
            },
            
            # Question-by-question breakdown
            'question_attempts': attempt_details,
            'total_questions_in_session': len(attempt_details)
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

# URL patterns to be added to Django urls.py
def get_history_url_patterns():
    """Returns URL patterns for history endpoints"""
    from django.urls import path
    
    return [
        path('history/student/<str:username>/', get_student_session_history, name='student_session_history'),
        path('history/adaptive-analytics/<str:username>/', get_adaptive_learning_analytics, name='adaptive_analytics'),
        path('history/session-details/<str:session_id>/', get_session_details, name='session_details'),
    ]

if __name__ == "__main__":
    print("Enhanced History API for Adaptive Learning Sessions")
    print("==================================================")
    print("Available endpoints:")
    print("- GET /history/student/<username>/ - Complete session history")
    print("- GET /history/adaptive-analytics/<username>/ - Adaptive learning analytics") 
    print("- GET /history/session-details/<session_id>/ - Detailed session information")
    print("\nAdd these URL patterns to your Django urls.py file")