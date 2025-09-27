"""
Adaptive Learning Session API

This module provides REST API endpoints for the adaptive learning system
with industry-standard BKT/DKT integration and mastery tracking.

Endpoints:
- POST /adaptive/start/ - Start new adaptive session
- GET /adaptive/next-question/<session_id>/ - Get next adaptive question
- POST /adaptive/submit-answer/ - Submit answer and update knowledge
- GET /adaptive/session-summary/<session_id>/ - Get session analytics
- GET /adaptive/student-mastery/<student_id>/ - Get student mastery levels

Author: AI Assistant
Date: 2024-12-26
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.db import transaction
import json
import logging

from assessment.adaptive_session_manager import adaptive_session_manager
from assessment.improved_models import StudentSession

logger = logging.getLogger(__name__)

@api_view(['POST'])
@csrf_exempt
def start_adaptive_session(request):
    """
    Start a new adaptive learning session
    
    Body parameters:
    - student_id (int): Student's user ID
    - subject_code (str): Subject code (quantitative_aptitude, logical_reasoning, etc.)
    - chapter_id (int, optional): Specific chapter ID
    - max_questions (int, optional): Maximum questions in session (default: 15)
    
    Returns:
    - success: Session initialization result
    - session_id: New session ID
    - initial_state: Complete session state
    - starting_difficulty: Initial difficulty level
    - initial_mastery: Starting mastery score
    """
    
    try:
        data = json.loads(request.body) if request.body else {}
        
        # Validate required parameters
        student_id = data.get('student_id')
        subject_code = data.get('subject_code')
        
        if not student_id or not subject_code:
            return JsonResponse({
                'success': False,
                'error': 'Missing required parameters: student_id, subject_code'
            }, status=400)
        
        # Optional parameters
        chapter_id = data.get('chapter_id')
        max_questions = data.get('max_questions', 15)
        
        # Start adaptive session
        result = adaptive_session_manager.start_adaptive_session(
            student_id=int(student_id),
            subject_code=subject_code,
            chapter_id=int(chapter_id) if chapter_id else None,
            max_questions=max_questions
        )
        
        if result['success']:
            logger.info(f"🎯 Adaptive session started - Session: {result['session_id']}, Student: {student_id}")
            return JsonResponse(result, status=201)
        else:
            return JsonResponse(result, status=400)
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    
    except Exception as e:
        logger.error(f"❌ Start session API error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['GET'])
def get_next_question(request, session_id):
    """
    Get next adaptive question for session
    
    URL Parameters:
    - session_id: Active session ID
    
    Returns:
    - success: Operation result
    - question: Next question data with options
    - current_difficulty: Current difficulty level
    - questions_attempted: Progress counter
    - current_mastery: Current mastery level
    """
    
    try:
        result = adaptive_session_manager.get_next_question(session_id)
        
        if result['success']:
            return JsonResponse(result, status=200)
        else:
            return JsonResponse(result, status=400)
    
    except Exception as e:
        logger.error(f"❌ Get next question API error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['POST'])
@csrf_exempt
def submit_answer(request):
    """
    Submit student answer and update knowledge models
    
    Body parameters:
    - session_id (str): Active session ID
    - question_id (str): Question that was answered
    - student_answer (str): Student's answer (a, b, c, d)
    - response_time (float): Time taken in seconds
    
    Returns:
    - success: Submission result
    - is_correct: Whether answer was correct
    - new_mastery: Updated mastery score
    - mastery_level: Current mastery level
    - next_difficulty: Next question difficulty
    - bkt_progression: BKT knowledge progression
    """
    
    try:
        data = json.loads(request.body) if request.body else {}
        
        # Validate required parameters
        session_id = data.get('session_id')
        question_id = data.get('question_id')
        student_answer = data.get('student_answer')
        response_time = data.get('response_time', 30.0)
        
        if not all([session_id, question_id, student_answer]):
            return JsonResponse({
                'success': False,
                'error': 'Missing required parameters: session_id, question_id, student_answer'
            }, status=400)
        
        # Submit answer
        result = adaptive_session_manager.submit_answer(
            session_id=session_id,
            question_id=question_id,
            student_answer=student_answer,
            response_time=float(response_time)
        )
        
        if result['success']:
            logger.info(f"✅ Answer submitted - Session: {session_id}, Correct: {result['is_correct']}")
            return JsonResponse(result, status=200)
        else:
            return JsonResponse(result, status=400)
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    
    except Exception as e:
        logger.error(f"❌ Submit answer API error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['GET'])
def get_session_summary(request, session_id):
    """
    Get comprehensive session analytics
    
    URL Parameters:
    - session_id: Session ID to analyze
    
    Returns:
    - success: Operation result
    - summary: Complete session analytics
      - mastery_progression: Mastery scores over time
      - difficulty_progression: Difficulty changes
      - performance_history: Question-by-question results
      - recommendations: Personalized learning recommendations
      - final_mastery_level: Industry-standard mastery category
    """
    
    try:
        result = adaptive_session_manager.get_session_summary(session_id)
        
        if result['success']:
            return JsonResponse(result, status=200)
        else:
            return JsonResponse(result, status=400)
    
    except Exception as e:
        logger.error(f"❌ Get session summary API error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['GET'])
def get_student_mastery(request, student_id):
    """
    Get student's current mastery levels across all subjects/chapters
    
    URL Parameters:
    - student_id: Student's user ID
    
    Returns:
    - success: Operation result
    - mastery_data: Student's mastery levels by skill
    - overall_statistics: Cross-subject performance summary
    """
    
    try:
        user = User.objects.get(id=student_id)
        profile = user.student_profile
        
        # Get mastery levels
        mastery_levels = getattr(profile, 'mastery_levels', {})
        
        # Calculate overall statistics
        if mastery_levels:
            mastery_scores = [data['mastery_score'] for data in mastery_levels.values()]
            overall_mastery = sum(mastery_scores) / len(mastery_scores)
            
            # Count mastery levels
            level_counts = {}
            for data in mastery_levels.values():
                level = data['mastery_level']
                level_counts[level] = level_counts.get(level, 0) + 1
        else:
            overall_mastery = 0.0
            level_counts = {}
        
        # Get recent sessions
        recent_sessions = StudentSession.objects.filter(
            student=user,
            status='COMPLETED'
        ).order_by('-session_end_time')[:5]
        
        session_history = []
        for session in recent_sessions:
            session_history.append({
                'session_id': str(session.id),
                'subject': session.subject.code,
                'chapter': session.chapter.name if session.chapter else None,
                'questions_attempted': session.questions_attempted,
                'accuracy': round(session.percentage_score, 1),
                'date': session.session_end_time.isoformat() if session.session_end_time else None
            })
        
        result = {
            'success': True,
            'student_id': student_id,
            'mastery_data': mastery_levels,
            'overall_statistics': {
                'overall_mastery': round(overall_mastery, 3),
                'skills_tracked': len(mastery_levels),
                'mastery_level_distribution': level_counts,
                'recent_sessions': session_history
            }
        }
        
        return JsonResponse(result, status=200)
    
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': f'Student with ID {student_id} not found'
        }, status=404)
    
    except Exception as e:
        logger.error(f"❌ Get student mastery API error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['GET'])
def get_available_subjects(request):
    """
    Get all available subjects and chapters for adaptive learning
    
    Returns:
    - success: Operation result
    - subjects: List of subjects with chapters
    """
    
    try:
        from assessment.improved_models import Subject
        
        subjects_data = []
        subjects = Subject.objects.filter(is_active=True)
        
        for subject in subjects:
            chapters = subject.chapters.filter(is_active=True)
            chapter_list = []
            
            for chapter in chapters:
                chapter_list.append({
                    'id': chapter.id,
                    'name': chapter.name,
                    'chapter_number': chapter.chapter_number,
                    'description': chapter.description
                })
            
            subjects_data.append({
                'code': subject.code,
                'name': subject.name,
                'description': subject.description,
                'chapters': chapter_list
            })
        
        return JsonResponse({
            'success': True,
            'subjects': subjects_data
        }, status=200)
    
    except Exception as e:
        logger.error(f"❌ Get available subjects API error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['POST'])
@csrf_exempt
def end_session(request, session_id):
    """
    Manually end an adaptive session before completion
    
    URL Parameters:
    - session_id: Session to end
    
    Returns:
    - success: Operation result
    - session_summary: Final session analytics
    """
    
    try:
        session = StudentSession.objects.get(id=session_id, status='ACTIVE')
        
        # Mark session as completed
        session.status = 'COMPLETED'
        session.save()
        
        # Get final summary
        summary_result = adaptive_session_manager.get_session_summary(session_id)
        
        logger.info(f"🏁 Session manually ended - ID: {session_id}")
        
        return JsonResponse({
            'success': True,
            'message': 'Session ended successfully',
            'session_summary': summary_result.get('summary', {})
        }, status=200)
    
    except StudentSession.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': f'Active session with ID {session_id} not found'
        }, status=404)
    
    except Exception as e:
        logger.error(f"❌ End session API error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)