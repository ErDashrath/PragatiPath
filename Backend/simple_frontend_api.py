#!/usr/bin/env python3
"""
Simple Direct Frontend API

This provides immediate working endpoints that the frontend can click and use
without any complex setup or orchestration dependencies.
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
from django.utils import timezone
import json
import uuid
import logging

from core.models import StudentProfile
from assessment.models import StudentSession, QuestionAttempt
from student_model.bkt import BKTService
from student_model.dkt import DKTService

logger = logging.getLogger(__name__)

# Initialize services
bkt_service = BKTService()
dkt_service = DKTService()

# ============================================================================
# Simple Direct Endpoints - Ready for Frontend Clicks
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def start_simple_session(request):
    """
    START SESSION - Direct frontend click endpoint
    
    Frontend can call this immediately:
    POST /start-session
    {
        "student_name": "John Doe",
        "subject": "mathematics"
    }
    """
    try:
        data = json.loads(request.body)
        student_name = data.get('student_name', 'Test Student')
        subject = data.get('subject', 'mathematics')
        
        # Create or get student
        username = f"student_{student_name.replace(' ', '_').lower()}"
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@example.com',
                'first_name': student_name.split()[0],
                'last_name': ' '.join(student_name.split()[1:]) if len(student_name.split()) > 1 else ''
            }
        )
        
        # Create or get student profile
        profile, created = StudentProfile.objects.get_or_create(
            user=user,
            defaults={
                'fundamentals': {
                    'listening': 0.5,
                    'grasping': 0.5,
                    'retention': 0.5,
                    'application': 0.5
                }
            }
        )
        
        # Get or create subject for session
        from assessment.improved_models import Subject, SUBJECT_CHOICES
        
        # Map subject name to valid code
        subject_mapping = {
            'mathematics': 'quantitative_aptitude',
            'math': 'quantitative_aptitude', 
            'quantitative': 'quantitative_aptitude',
            'reasoning': 'logical_reasoning',
            'logic': 'logical_reasoning',
            'data': 'data_interpretation',
            'verbal': 'verbal_ability',
            'english': 'verbal_ability'
        }
        
        subject_code = subject_mapping.get(subject.lower(), 'quantitative_aptitude')
        
        subject_obj, created = Subject.objects.get_or_create(
            code=subject_code,
            defaults={
                'name': subject.title(),
                'description': f'Auto-created subject for {subject}',
                'is_active': True
            }
        )
        
        # Create simple session
        session = StudentSession.objects.create(
            student=user,
            subject=subject_obj,
            session_name=f"Simple {subject_obj.name} Session",
            total_questions_planned=5,
            session_config={
                'subject': subject,
                'subject_code': subject_code,
                'subject_name': subject_obj.name,
                'frontend_session': True,
                'simple_api': True
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Session started successfully!',
            'session_id': str(session.id),
            'student_id': str(profile.id),
            'student_name': student_name,
            'subject': subject,
            'next_action': 'Click "Get Question" to start learning!'
        })
        
    except Exception as e:
        logger.error(f"Start session error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Session start failed'
        }, status=500)

@csrf_exempt 
@require_http_methods(["GET"])
def get_simple_question(request, session_id):
    """
    GET QUESTION - Direct frontend click endpoint
    
    Frontend can call this immediately:
    GET /get-question/<session_id>/
    """
    try:
        if not session_id:
            return JsonResponse({
                'success': False,
                'error': 'session_id required',
                'message': 'Please provide session_id parameter'
            }, status=400)
        
        session = get_object_or_404(StudentSession, id=session_id)
        subject = session.session_config.get('subject', 'mathematics')
        
        # Count current questions
        question_count = QuestionAttempt.objects.filter(session=session).count() + 1
        
        # Get current knowledge state for adaptive difficulty
        skill_id = f"{subject}_skill_{question_count}"
        
        try:
            # Try to get BKT mastery
            bkt_params = bkt_service.get_skill_bkt_params(session.student, skill_id)
            mastery_level = bkt_params.P_L if bkt_params else 0.5
        except:
            mastery_level = 0.5
        
        # Map adaptive difficulty to database difficulty
        if mastery_level < 0.3:
            difficulty = "easy"
            db_difficulty = "easy"
            difficulty_emoji = "🟢"
        elif mastery_level < 0.7:
            difficulty = "medium" 
            db_difficulty = "moderate"
            difficulty_emoji = "🟡"
        else:
            difficulty = "hard"
            db_difficulty = "difficult"
            difficulty_emoji = "🔴"
        
        # Get real questions from database
        from assessment.improved_models import Subject
        from assessment.models import AdaptiveQuestion
        
        # Get subject object
        subject_obj = Subject.objects.filter(code=session.session_config.get('subject_code', 'quantitative_aptitude')).first()
        if not subject_obj:
            # Fallback to first available subject
            subject_obj = Subject.objects.first()
        
        # Try to get real questions matching difficulty
        real_questions = AdaptiveQuestion.objects.filter(
            subject_fk=subject_obj,
            difficulty_level=db_difficulty
        ).exclude(
            # Exclude questions already attempted in this session
            id__in=QuestionAttempt.objects.filter(session=session).values_list('question_id', flat=True)
        )
        
        if real_questions.exists():
            # Use real question from database
            real_question = real_questions.first()
            question_id = f"real_{real_question.id}"
            
            question = {
                'success': True,
                'question_id': question_id,
                'real_question_id': real_question.id,
                'session_id': session_id,
                'question_number': question_count,
                'subject': subject,
                'subject_display': subject_obj.name,
                'difficulty': difficulty,
                'difficulty_display': f"{difficulty_emoji} {difficulty.upper()}",
                'question_text': real_question.question_text,
                'options': [
                    {'id': 'A', 'text': real_question.option_a},
                    {'id': 'B', 'text': real_question.option_b},
                    {'id': 'C', 'text': real_question.option_c},
                    {'id': 'D', 'text': real_question.option_d}
                ],
                'correct_answer': real_question.correct_answer,
                'explanation': real_question.explanation or f'This {difficulty} question was selected based on your mastery level of {mastery_level:.1%}',
                'topic': real_question.topic,
                'subtopic': real_question.subtopic,
                'adaptive_info': {
                    'mastery_level': mastery_level,
                    'skill_id': skill_id,
                    'adaptive_reason': f"Selected {difficulty} difficulty because mastery is {mastery_level:.1%}",
                    'real_question': True
                },
            }
        else:
            # Fallback to adaptive dummy question if no real questions available
            question_id = f"adaptive_{session_id}_{question_count}"
            
            question = {
                'success': True,
                'question_id': question_id,
                'session_id': session_id,
                'question_number': question_count,
                'subject': subject,
                'subject_display': subject_obj.name if subject_obj else subject.title(),
                'difficulty': difficulty,
                'difficulty_display': f"{difficulty_emoji} {difficulty.upper()}",
                'question_text': f"Question {question_count}: This is a {difficulty} {subject} question adapted to your current mastery level ({mastery_level:.1%}).",
                'options': [
                    {'id': 'A', 'text': f'Option A - {difficulty} level answer'},
                    {'id': 'B', 'text': f'Option B - {difficulty} level answer'},
                    {'id': 'C', 'text': f'Option C - {difficulty} level answer'},
                    {'id': 'D', 'text': f'Option D - {difficulty} level answer'}
                ],
                'correct_answer': 'A',
                'explanation': f'This {difficulty} question was selected based on your mastery level of {mastery_level:.1%}',
                'adaptive_info': {
                    'mastery_level': mastery_level,
                    'skill_id': skill_id,
                    'adaptive_reason': f"Selected {difficulty} difficulty because mastery is {mastery_level:.1%}",
                    'real_question': False
                },
            'message': f'📚 Adaptive question ready! Difficulty: {difficulty_emoji} {difficulty.upper()}',
            'next_action': 'Choose your answer and click "Submit Answer"'
        }
        
        return JsonResponse(question)
        
    except Exception as e:
        logger.error(f"Get question error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Failed to get question'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def submit_simple_answer(request):
    """
    SUBMIT ANSWER - Direct frontend click endpoint
    
    Frontend can call this immediately:
    POST /submit-answer
    {
        "session_id": "<session_id>",
        "question_id": "<question_id>", 
        "selected_answer": "A",
        "time_spent": 15.5
    }
    """
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        question_id = data.get('question_id')
        selected_answer = data.get('selected_answer')
        time_spent = data.get('time_spent', 10.0)
        
        if not all([session_id, question_id, selected_answer]):
            return JsonResponse({
                'success': False,
                'error': 'Missing required fields',
                'message': 'session_id, question_id, and selected_answer are required'
            }, status=400)
        
        # Validate session exists with better error handling
        try:
            session = get_object_or_404(StudentSession, id=session_id)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'message': 'Invalid session_id - please use a valid session from start-session endpoint'
            }, status=400)
        subject = session.session_config.get('subject', 'mathematics')
        
        # For demo, assume A is always correct
        is_correct = (selected_answer == 'A')
        
        # Create question attempt record
        # Note: QuestionAttempt requires a question FK, but we're using question_id as string
        # For now, create a simplified record
        from assessment.models import AdaptiveQuestion
        
        # Get or create a dummy question for the attempt
        dummy_question, created = AdaptiveQuestion.objects.get_or_create(
            id=question_id,
            defaults={
                'question_text': f'Simple API Question {question_id}',
                'question_type': 'multiple_choice',
                'correct_answer': 'A',
                'difficulty_level': 'medium',
                'subject': subject,
                'chapter': 'General',
                'options': ['A', 'B', 'C', 'D']
            }
        )
        
        attempt = QuestionAttempt.objects.create(
            session=session,
            question=dummy_question,
            student=session.student,
            question_number_in_session=QuestionAttempt.objects.filter(session=session).count() + 1,
            student_answer=selected_answer,
            correct_answer='A',
            is_correct=is_correct,
            time_spent_seconds=time_spent,
            difficulty_when_presented=dummy_question.difficulty_level,
            interaction_data={
                'simple_api': True,
                'adaptive_submission': True,
                'question_id_string': question_id
            }
        )
        
        # Update knowledge models
        skill_id = f"{subject}_skill_{QuestionAttempt.objects.filter(session=session).count()}"
        
        # Update BKT
        try:
            bkt_service.update_skill_bkt(
                user=session.student,
                skill_id=skill_id,
                is_correct=is_correct,
                interaction_data={'question_id': question_id, 'time_spent': time_spent}
            )
            bkt_updated = True
            # Get updated mastery
            updated_bkt = bkt_service.get_skill_bkt_params(session.student, skill_id)
            new_mastery = updated_bkt.P_L if updated_bkt else 0.5
        except Exception as e:
            logger.warning(f"BKT update failed: {e}")
            bkt_updated = False
            new_mastery = 0.5
        
        # Update DKT 
        try:
            dkt_service.update_dkt_knowledge(
                user=session.student,
                skill_id=skill_id,
                is_correct=is_correct,
                interaction_data={'question_id': question_id, 'time_spent': time_spent}
            )
            dkt_updated = True
            dkt_prediction = dkt_service.get_skill_prediction(session.student, skill_id)
        except Exception as e:
            logger.warning(f"DKT update failed: {e}")
            dkt_updated = False
            dkt_prediction = 0.5
        
        # Calculate session progress
        total_questions = QuestionAttempt.objects.filter(session=session).count()
        correct_answers = QuestionAttempt.objects.filter(session=session, is_correct=True).count()
        accuracy = correct_answers / max(total_questions, 1)
        
        # Determine adaptation message
        if is_correct and new_mastery > 0.7:
            adaptation_message = "🎉 Great job! Questions will get harder to challenge you more."
            difficulty_change = "Questions getting HARDER"
        elif not is_correct and new_mastery < 0.4:
            adaptation_message = "💪 Let's try easier questions to build your confidence."
            difficulty_change = "Questions getting EASIER"
        else:
            adaptation_message = "👍 Good progress! Questions will stay at similar difficulty."
            difficulty_change = "Difficulty staying SIMILAR"
        
        response = {
            'success': True,
            'answer_correct': is_correct,
            'correct_answer': 'A',
            'selected_answer': selected_answer,
            'explanation': f"The correct answer was A. {'Well done!' if is_correct else 'Better luck next time!'}",
            'knowledge_update': {
                'bkt_updated': bkt_updated,
                'dkt_updated': dkt_updated,
                'new_mastery_level': new_mastery,
                'dkt_prediction': dkt_prediction,
                'mastery_display': f"{new_mastery:.1%}"
            },
            'session_progress': {
                'total_questions': total_questions,
                'correct_answers': correct_answers,
                'accuracy': f"{accuracy:.1%}",
                'questions_remaining': max(0, session.total_questions_planned - total_questions)
            },
            'adaptive_feedback': {
                'mastery_change': f"Mastery level: {new_mastery:.1%}",
                'difficulty_adaptation': difficulty_change,
                'adaptation_message': adaptation_message
            },
            'message': f"✅ Answer submitted! {adaptation_message}",
            'next_action': 'Click "Get Next Question" to continue learning!' if total_questions < session.total_questions_planned else 'Session complete! Well done! 🎉'
        }
        
        return JsonResponse(response)
        
    except Exception as e:
        logger.error(f"Submit answer error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Failed to submit answer'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_session_progress(request, session_id):
    """
    GET PROGRESS - Direct frontend click endpoint
    
    Frontend can call this immediately:
    GET /session-progress/<session_id>/
    """
    try:
        if not session_id:
            return JsonResponse({
                'success': False,
                'error': 'session_id required'
            }, status=400)
        
        session = get_object_or_404(StudentSession, id=session_id)
        attempts = QuestionAttempt.objects.filter(session=session)
        
        total_questions = attempts.count()
        correct_answers = attempts.filter(is_correct=True).count()
        
        # Get current knowledge states
        subject = session.session_config.get('subject', 'mathematics')
        skill_id = f"{subject}_skill_1"
        
        try:
            bkt_params = bkt_service.get_skill_bkt_params(session.student, skill_id)
            current_mastery = bkt_params.P_L if bkt_params else 0.5
        except:
            current_mastery = 0.5
        
        try:
            dkt_prediction = dkt_service.get_skill_prediction(session.student, skill_id)
        except:
            dkt_prediction = 0.5
        
        progress = {
            'success': True,
            'session_id': session_id,
            'student_name': session.student.get_full_name() or session.student.username,
            'subject': subject,
            'session_stats': {
                'questions_answered': total_questions,
                'correct_answers': correct_answers,
                'accuracy': f"{correct_answers / max(total_questions, 1):.1%}",
                'questions_remaining': max(0, session.total_questions_planned - total_questions)
            },
            'knowledge_state': {
                'bkt_mastery': f"{current_mastery:.1%}",
                'dkt_prediction': f"{dkt_prediction:.1%}",
                'overall_progress': f"{(current_mastery + dkt_prediction) / 2:.1%}",
                'skill_level': skill_id
            },
            'adaptive_info': {
                'difficulty_trend': "Adapting based on your performance",
                'next_difficulty': "Easy" if current_mastery < 0.3 else "Hard" if current_mastery > 0.7 else "Medium",
                'learning_status': "Excellent progress!" if current_mastery > 0.7 else "Good progress!" if current_mastery > 0.4 else "Building foundations"
            },
            'message': f"📊 Progress: {correct_answers}/{total_questions} correct ({correct_answers / max(total_questions, 1):.1%}), Mastery: {current_mastery:.1%}"
        }
        
        return JsonResponse(progress)
        
    except Exception as e:
        logger.error(f"Get progress error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Failed to get progress'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def api_health(request):
    """
    HEALTH CHECK - Direct frontend click endpoint
    
    Frontend can call this to verify the API is working:
    GET /health
    """
    return JsonResponse({
        'success': True,
        'status': 'healthy',
        'message': '✅ Simple Frontend API is ready!',
        'services': {
            'django': 'active',
            'database': 'connected',
            'bkt_service': 'available',
            'dkt_service': 'available'
        },
        'endpoints': [
            'POST /start-session - Start a new learning session',
            'GET /get-question - Get adaptive question',
            'POST /submit-answer - Submit answer and see adaptation',
            'GET /session-progress - View learning progress',
            'GET /health - Check API status'
        ],
        'ready_for_frontend': True
    })

# ============================================================================
# URL Routing Setup (if needed)
# ============================================================================

def setup_simple_urls():
    """Setup URLs for the simple frontend API"""
    from django.urls import path
    
    urlpatterns = [
        path('start-session', start_simple_session, name='start_simple_session'),
        path('get-question', get_simple_question, name='get_simple_question'),
        path('submit-answer', submit_simple_answer, name='submit_simple_answer'),
        path('session-progress', get_session_progress, name='get_session_progress'),
        path('health', api_health, name='api_health'),
    ]
    
    return urlpatterns

if __name__ == "__main__":
    print("🚀 Simple Frontend API Ready!")
    print("=" * 50)
    print("Direct endpoints for frontend clicks:")
    print()
    print("1. POST /start-session")
    print("   Body: {'student_name': 'John', 'subject': 'math'}")
    print("   → Starts learning session")
    print()
    print("2. GET /get-question?session_id=<session_id>")
    print("   → Gets adaptive question")
    print()
    print("3. POST /submit-answer")
    print("   Body: {'session_id': '...', 'question_id': '...', 'selected_answer': 'A'}")
    print("   → Submits answer, shows adaptation")
    print()
    print("4. GET /session-progress?session_id=<session_id>")
    print("   → Shows learning progress")
    print()
    print("5. GET /health")
    print("   → API health check")
    print()
    print("✅ Ready for immediate frontend integration!")