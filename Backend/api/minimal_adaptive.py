"""
Minimal working adaptive API for testing
"""
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from assessment.improved_models import Subject, Chapter, StudentSession
from assessment.models import AdaptiveQuestion
from django.utils import timezone

@csrf_exempt
@require_http_methods(["POST"])
def minimal_next_question(request):
    """Minimal version that just returns a question"""
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        subject_id = data.get('subject_id')
        
        # Get user and subject
        user = User.objects.get(id=user_id)
        if str(subject_id).isdigit():
            subject = Subject.objects.get(id=subject_id)
        else:
            subject = Subject.objects.get(code=subject_id)
        
        # Get a question
        question = AdaptiveQuestion.objects.filter(
            subject=subject.code,
            is_active=True
        ).first()
        
        if question:
            return JsonResponse({
                'success': True,
                'question': {
                    'id': str(question.id),
                    'question_text': question.question_text,
                    'options': question.formatted_options,
                    'difficulty': question.difficulty_level,
                    'subject': question.subject
                },
                'mastery_status': {
                    'current_score': 0.5,
                    'mastery_achieved': False,
                    'mastery_level': 'developing',
                    'confidence': 0.6,
                    'questions_remaining': 5
                },
                'session_info': {
                    'session_id': 'temp_session',
                    'questions_attempted': 0,
                    'current_streak': 0,
                    'session_duration': 0
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'No questions found'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error: {str(e)}',
            'details': type(e).__name__
        }, status=500)