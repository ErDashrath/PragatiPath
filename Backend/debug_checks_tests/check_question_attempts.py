#!/usr/bin/env python3
"""
Check existing question attempts to understand the constraint violation
"""

import os
import sys
import django

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')
django.setup()

from assessment.models import QuestionAttempt, StudentSession, AdaptiveQuestion
from django.contrib.auth.models import User

def check_attempts():
    """Check existing attempts for the session and question we're testing"""
    print("🔍 Checking Question Attempts Database")
    print("=" * 50)
    
    # Test session ID from our test
    session_id = "81225db3-6d4d-489c-980d-b4aa7d93b3f6"
    question_id = "real_00a3ccb2-3391-4ebc-8c79-a0e17d72da60"
    
    print(f"Looking for existing attempts:")
    print(f"   Session ID: {session_id}")
    print(f"   Question ID: {question_id}")
    print()
    
    # Check if session exists
    try:
        session = StudentSession.objects.get(id=session_id)
        print(f"✅ Session found: {session.id}")
        print(f"   Student: {session.student.username}")
        print(f"   Subject: {session.subject}")
        print(f"   Status: {session.status}")
    except StudentSession.DoesNotExist:
        print(f"❌ Session not found!")
        return
    
    # Check if question exists
    try:
        question = AdaptiveQuestion.objects.get(id=question_id)
        print(f"✅ Question found: {question.id}")
        print(f"   Text: {question.question_text[:100]}...")
        print(f"   Answer: {question.answer}")
    except AdaptiveQuestion.DoesNotExist:
        print(f"❌ Question not found!")
        return
    
    print()
    
    # Check existing attempts for this session + question combination
    existing_attempts = QuestionAttempt.objects.filter(
        session=session,
        question=question
    ).order_by('attempt_number')
    
    print(f"🎯 Existing attempts for this session + question: {existing_attempts.count()}")
    print("-" * 30)
    
    for attempt in existing_attempts:
        print(f"📝 Attempt #{attempt.attempt_number}")
        print(f"   ID: {attempt.id}")
        print(f"   Student Answer: {attempt.student_answer}")
        print(f"   Correct: {attempt.is_correct}")
        print(f"   Status: {attempt.answer_status}")
        print(f"   Created: {attempt.created_at}")
        print()
    
    # Check what the next attempt number should be
    if existing_attempts:
        max_attempt = existing_attempts.aggregate(
            max_attempt=django.db.models.Max('attempt_number')
        )['max_attempt']
        next_attempt = max_attempt + 1
        print(f"💡 Next attempt number should be: {next_attempt}")
    else:
        print(f"💡 This would be the first attempt (attempt_number=1)")
    
    print()
    
    # Check all attempts for this session
    all_session_attempts = QuestionAttempt.objects.filter(
        session=session
    ).order_by('question_number_in_session', 'attempt_number')
    
    print(f"📊 All attempts in this session: {all_session_attempts.count()}")
    print("-" * 30)
    
    for attempt in all_session_attempts:
        print(f"Q{attempt.question_number_in_session}.{attempt.attempt_number}: "
              f"{attempt.question.id[:8]}... -> {attempt.student_answer} "
              f"({'✓' if attempt.is_correct else '✗'})")

if __name__ == "__main__":
    check_attempts()