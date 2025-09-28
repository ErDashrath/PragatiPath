#!/usr/bin/env python3
"""
Test minimal submission directly in Django to bypass any API issues
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')
django.setup()

from assessment.models import AdaptiveQuestion, StudentSession, QuestionAttempt
from django.contrib.auth.models import User
import uuid

def test_minimal_submission():
    """Test the exact operation that's failing"""
    
    print("🧪 Testing Minimal Submission Components")
    print("=" * 50)
    
    # Test 1: Get the question directly
    question_id = "00a3ccb2-3391-4ebc-8c79-a0e17d72da60"
    print(f"1. Testing question lookup: {question_id}")
    
    try:
        question = AdaptiveQuestion.objects.get(id=question_id)
        print(f"   ✅ Question found: {question.question_text[:50]}...")
        print(f"   Answer: {question.answer}")
    except Exception as e:
        print(f"   ❌ Question lookup failed: {e}")
        return False
    
    # Test 2: Get or create a simple user
    print("\n2. Testing user creation...")
    try:
        user, created = User.objects.get_or_create(
            username="test_submission_user",
            defaults={'email': 'test@example.com'}
        )
        print(f"   ✅ User: {user.username} (created: {created})")
    except Exception as e:
        print(f"   ❌ User creation failed: {e}")
        return False
    
    # Test 3: Get the most recent session for this user
    print("\n3. Testing session lookup...")
    try:
        session = StudentSession.objects.filter(student=user).last()
        if session:
            print(f"   ✅ Session found: {session.id}")
        else:
            print(f"   ⚠️ No session found, this might be the issue")
            return False
    except Exception as e:
        print(f"   ❌ Session lookup failed: {e}")
        return False
    
    # Test 4: Try creating QuestionAttempt (this is where the error might be)
    print("\n4. Testing QuestionAttempt creation...")
    try:
        # This is the critical test - see if QuestionAttempt creation works
        attempt = QuestionAttempt(
            session=session,
            question=question,  # Using the real question object
            student=user,
            question_number_in_session=1,
            student_answer='A',
            correct_answer=question.answer.upper(),
            is_correct=(question.answer.upper() == 'A'),
            time_spent_seconds=25.5,
            difficulty_when_presented=question.difficulty_level,
            interaction_data={'test': True}
        )
        
        # Try to save it
        attempt.save()
        print(f"   ✅ QuestionAttempt created successfully: {attempt.id}")
        
        # Clean up
        attempt.delete()
        return True
        
    except Exception as e:
        print(f"   ❌ QuestionAttempt creation failed: {e}")
        print(f"   Error type: {type(e)}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_minimal_submission()
    if success:
        print("\n🎉 All components work! The issue must be elsewhere.")
    else:
        print("\n❌ Found the problematic component!")