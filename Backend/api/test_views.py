"""
Simple test view to check imports and basic functionality
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

@csrf_exempt
@require_http_methods(["POST"])
def test_imports(request):
    """Test if all imports work correctly"""
    try:
        # Test imports step by step
        from django.contrib.auth.models import User
        from assessment.improved_models import Subject, StudentSession
        from assessment.models import AdaptiveQuestion
        
        # Test basic database queries
        user_count = User.objects.count()
        subject_count = Subject.objects.count()
        question_count = AdaptiveQuestion.objects.count()
        
        return JsonResponse({
            'success': True,
            'message': 'All imports successful',
            'counts': {
                'users': user_count,
                'subjects': subject_count,
                'questions': question_count
            }
        })
        
    except ImportError as e:
        return JsonResponse({
            'success': False,
            'error': f'Import error: {str(e)}'
        }, status=500)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'General error: {str(e)}'
        }, status=500)

@csrf_exempt  
@require_http_methods(["POST"])
def test_simple_adaptive(request):
    """Test adaptive logic without session creation"""
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id', 83)
        subject_id = data.get('subject_id', 'quantitative_aptitude')
        
        # Test getting user
        from django.contrib.auth.models import User
        user = User.objects.get(id=user_id)
        
        # Test getting subject
        from assessment.improved_models import Subject
        if str(subject_id).isdigit():
            subject = Subject.objects.get(id=subject_id)
        else:
            subject = Subject.objects.get(code=subject_id)
        
        # Test getting question directly
        from assessment.models import AdaptiveQuestion
        question = AdaptiveQuestion.objects.filter(
            subject=subject.code,
            is_active=True
        ).first()
        
        if question:
            return JsonResponse({
                'success': True,
                'user': user.username,
                'subject': subject.name,
                'question': {
                    'id': str(question.id),
                    'text': question.question_text[:100] + '...',
                    'subject': question.subject,
                    'difficulty': question.difficulty_level
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'No questions found for subject {subject.code}'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error: {str(e)}',
            'type': type(e).__name__
        }, status=500)