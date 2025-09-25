#!/usr/bin/env python3
"""
Check actual question IDs in the database to understand the format
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

from assessment.models import AdaptiveQuestion, StudentSession
from django.contrib.auth.models import User

def check_question_ids():
    """Check what question IDs actually exist in the database"""
    print("🔍 Checking AdaptiveQuestion IDs in Database")
    print("=" * 50)
    
    # Get all questions
    questions = AdaptiveQuestion.objects.all()[:10]  # First 10 for debugging
    
    print(f"Total questions in database: {AdaptiveQuestion.objects.count()}")
    print()
    
    print("📋 Sample Question IDs:")
    print("-" * 30)
    
    for i, question in enumerate(questions, 1):
        print(f"{i:2}. ID: {question.id}")
        print(f"     Type: {type(question.id)}")
        print(f"     Text: {question.question_text[:60]}...")
        print(f"     Answer: {question.answer}")
        print()
    
    # Check the specific session and see what questions are available for it
    session_id = "81225db3-6d4d-489c-980d-b4aa7d93b3f6"
    
    try:
        session = StudentSession.objects.get(id=session_id)
        print(f"🎯 Session Subject: {session.subject}")
        
        # Get questions for this subject
        subject_questions = AdaptiveQuestion.objects.filter(
            subject=session.subject
        )[:5]  # First 5 for this subject
        
        print(f"📚 Questions available for {session.subject} ({subject_questions.count()} total):")
        print("-" * 30)
        
        for i, question in enumerate(subject_questions, 1):
            print(f"{i:2}. ID: {question.id}")
            print(f"     Text: {question.question_text[:60]}...")
            print(f"     Difficulty: {question.difficulty_level}")
            print(f"     Answer: {question.answer}")
            print()
        
        # Suggest a valid question ID for testing
        if subject_questions.exists():
            test_question = subject_questions.first()
            print(f"💡 Suggested question ID for testing: {test_question.id}")
            
    except StudentSession.DoesNotExist:
        print(f"❌ Session {session_id} not found")

if __name__ == "__main__":
    check_question_ids()