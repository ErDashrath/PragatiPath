"""
Complete Assessment Orchestration Demo
Tests the main endpoint that ties BKT, DKT, IRT, and SM-2 together
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')
sys.path.append('.')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import json
import uuid

def create_comprehensive_demo():
    """Create comprehensive demo showing full orchestration"""
    print("🚀 COMPREHENSIVE ASSESSMENT ORCHESTRATION DEMO")
    print("=" * 60)
    
    # Import models
    from core.models import StudentProfile
    from assessment.models import AdaptiveQuestion, Interaction
    from practice.models import SRSCard
    
    # Create or get demo student with full profile
    user, created = User.objects.get_or_create(
        username='orchestration_student',
        defaults={
            'email': 'orchestration@example.com',
            'first_name': 'Demo',
            'last_name': 'Student'
        }
    )
    
    student_profile, created = StudentProfile.objects.get_or_create(
        user=user,
        defaults={
            'bkt_parameters': {
                'algebra': {
                    'P_L': 0.4,  # Current mastery probability
                    'P_T': 0.1,  # Probability of transition
                    'P_S': 0.2,  # Probability of slip
                    'P_G': 0.1   # Probability of guess
                }
            },
            'dkt_hidden_state': [0.3] * 50,  # DKT hidden state
            'fundamentals': {
                'algebra': 0.45,
                'geometry': 0.60
            }
        }
    )
    
    if created or not student_profile.bkt_parameters:
        student_profile.bkt_parameters = {
            'algebra': {
                'P_L': 0.4,
                'P_T': 0.1,
                'P_S': 0.2,
                'P_G': 0.1
            }
        }
        student_profile.dkt_hidden_state = [0.3] * 50
        student_profile.fundamentals = {
            'algebra': 0.45,
            'geometry': 0.60
        }
        student_profile.save()
    
    # Create demo questions with IRT parameters and levels
    demo_questions = [
        {
            'question_text': 'Solve for x: 3x + 7 = 22',
            'correct_answer': 'x = 5',
            'question_type': 'short_answer',
            'skill_id': 'algebra',
            'difficulty': 0.2,  # Easy question
            'discrimination': 1.5,
            'guessing': 0.1,
            'level': 0  # Beginner level
        },
        {
            'question_text': 'Factor: x² - 16',
            'correct_answer': '(x+4)(x-4)',
            'question_type': 'short_answer', 
            'skill_id': 'algebra',
            'difficulty': 0.6,  # Medium question
            'discrimination': 1.8,
            'guessing': 0.1,
            'level': 1  # Intermediate level
        },
        {
            'question_text': 'Simplify: √(144)',
            'correct_answer': '12',
            'question_type': 'numerical',
            'skill_id': 'algebra',
            'difficulty': -0.3,  # Very easy
            'discrimination': 1.2,
            'guessing': 0.2,
            'level': 0  # Beginner level
        },
        {
            'question_text': 'Solve quadratic: x² + 5x + 6 = 0',
            'correct_answer': 'x = -2 or x = -3',
            'question_type': 'short_answer',
            'skill_id': 'algebra',
            'difficulty': 1.2,  # Hard question
            'discrimination': 2.0,
            'guessing': 0.05,
            'level': 2  # Advanced level
        }
    ]
    
    questions = []
    for q_data in demo_questions:
        question, created = AdaptiveQuestion.objects.get_or_create(
            question_text=q_data['question_text'],
            defaults={
                'correct_answer': q_data['correct_answer'],
                'question_type': q_data['question_type'],
                'skill_id': q_data['skill_id'],
                'difficulty': q_data['difficulty'],
                'discrimination': q_data['discrimination'],
                'guessing': q_data['guessing'],
                'level': q_data['level'],  # Add level
                'is_active': True
            }
        )
        questions.append(question)
        if created:
            print(f"✅ Created question: {question.question_text}")
    
    print(f"\n👤 Demo Student Profile Created:")
    print(f"   Student ID: {student_profile.id}")
    print(f"   Username: {user.username}")
    print(f"   Initial BKT Mastery (algebra): {student_profile.bkt_parameters['algebra']['P_L']:.3f}")
    print(f"   Fundamentals Score (algebra): {student_profile.fundamentals['algebra']:.3f}")
    print(f"   DKT Hidden State Length: {len(student_profile.dkt_hidden_state or [])}")
    
    # Create a sample assessment submission
    test_question = questions[0]  # Easy question
    
    print(f"\n📝 Sample Assessment Submission:")
    print(f"   Question: {test_question.question_text}")
    print(f"   Correct Answer: {test_question.correct_answer}")
    print(f"   Difficulty: {test_question.difficulty}")
    
    # Create payload that would be sent to the API
    api_payload = {
        "student_id": str(student_profile.id),
        "question_id": str(test_question.id),
        "answer": "x = 5",  # Correct answer
        "response_time": 8.5,
        "skill_id": "algebra",
        "metadata": {
            "attempt_number": 1,
            "hint_used": False
        }
    }
    
    print(f"\n📡 API Payload:")
    print(f"   {json.dumps(api_payload, indent=2)}")
    
    print(f"\n🔗 Test this endpoint:")
    print(f"   POST /api/v1/assessment/submit-answer")
    print(f"   Content-Type: application/json")
    print(f"   Body: {json.dumps(api_payload)}")
    
    # Show what the response would contain
    print(f"\n📊 Expected Response Structure:")
    expected_response = {
        "success": True,
        "interaction_id": "uuid-here",
        "was_correct": True,
        "feedback": "Correct! Well done.",
        "next_question": {
            "question_id": "next-question-uuid",
            "question_text": "Next question selected by IRT...",
            "question_type": "short_answer",
            "difficulty": 0.4,
            "skill_id": "algebra",
            "selection_method": "irt",
            "selection_reasoning": "Selected using IRT based on current ability estimate"
        },
        "updated_student_state": {
            "student_id": str(student_profile.id),
            "bkt_parameters": "Updated BKT parameters...",
            "dkt_hidden_state": "Updated DKT hidden state...",
            "irt_theta": "Estimated ability level...",
            "fundamentals": "Updated fundamentals...",
            "srs_cards_updated": 1,
            "total_interactions": "Count of interactions...",
            "session_progress": "Session statistics..."
        },
        "algorithm_results": {
            "bkt": {"status": "success", "mastery_change": "0.400 → 0.450"},
            "dkt": {"status": "success", "prediction": 0.55},
            "irt": {"status": "success", "question_selected": True},
            "sm2": {"status": "success", "card_updated": True}
        },
        "performance_metrics": {
            "total_interactions": "Updated count",
            "recent_accuracy": "7-day accuracy rate",
            "current_streak": "Consecutive correct answers"
        },
        "recommendations": [
            "Great progress! You're improving in algebra.",
            "Keep practicing to maintain your streak.",
            "Try some harder questions to challenge yourself."
        ]
    }
    
    print(f"   {json.dumps(expected_response, indent=2)}")
    
    print(f"\n🎯 Orchestration Flow:")
    print(f"   1. ✅ Save interaction to database")
    print(f"   2. 🧠 Update BKT parameters (Bayesian Knowledge Tracing)")
    print(f"   3. 🤖 Call DKT service (Deep Knowledge Tracing)")
    print(f"   4. 📈 Update fundamentals scores")
    print(f"   5. 🔄 Create/update SRS cards (SM-2 Spaced Repetition)")
    print(f"   6. 🎲 Select next question via IRT (Item Response Theory)")
    print(f"   7. 📊 Return comprehensive state and next question")
    
    print(f"\n🧪 Test Commands:")
    print(f"# Start Django server")
    print(f"python manage.py runserver 8000")
    print(f"")
    print(f"# Test the orchestration endpoint")
    print(f"$payload = @{{")
    print(f"    student_id = '{student_profile.id}'")
    print(f"    question_id = '{test_question.id}'")
    print(f"    answer = 'x = 5'")
    print(f"    response_time = 8.5")
    print(f"    skill_id = 'algebra'")
    print(f"    metadata = @{{attempt_number = 1; hint_used = $false}}")
    print(f"}} | ConvertTo-Json -Depth 3")
    print(f"")
    print(f"Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/assessment/submit-answer' -Method POST -Body $payload -ContentType 'application/json'")
    
    return student_profile.id, test_question.id

if __name__ == "__main__":
    try:
        student_id, question_id = create_comprehensive_demo()
        print(f"\n✨ Comprehensive orchestration demo ready!")
        print(f"🎊 All four algorithms (BKT, DKT, IRT, SM-2) integrated in single endpoint!")
        print(f"📚 Student ID: {student_id}")
        print(f"❓ Question ID: {question_id}")
    except Exception as e:
        print(f"❌ Demo setup failed: {e}")
        import traceback
        traceback.print_exc()