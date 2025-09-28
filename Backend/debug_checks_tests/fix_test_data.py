#!/usr/bin/env python3
"""
Check which subjects have questions and fix our test data
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

from assessment.models import AdaptiveQuestion, StudentSession, Subject
from django.contrib.auth.models import User
from django.db.models import Count

def check_subjects_and_questions():
    """Check which subjects have questions and update test data"""
    print("🔍 Checking Subjects and Their Questions")
    print("=" * 50)
    
    # Check all subjects and their question counts
    subjects_with_counts = Subject.objects.annotate(
        question_count=Count('adaptivequestion')
    ).order_by('-question_count')
    
    print("📊 Subjects and their question counts:")
    print("-" * 40)
    
    for subject in subjects_with_counts:
        print(f"📚 {subject.name} ({subject.code}): {subject.question_count} questions")
    
    print()
    
    # Find a subject with questions
    subject_with_questions = subjects_with_counts.filter(question_count__gt=0).first()
    
    if subject_with_questions:
        print(f"🎯 Using subject with questions: {subject_with_questions.name}")
        
        # Get sample questions for this subject
        sample_questions = AdaptiveQuestion.objects.filter(
            subject=subject_with_questions
        )[:3]
        
        print(f"📋 Sample questions for {subject_with_questions.name}:")
        print("-" * 30)
        
        for i, question in enumerate(sample_questions, 1):
            print(f"{i}. ID: {question.id}")
            print(f"   Text: {question.question_text[:80]}...")
            print(f"   Answer: {question.answer}")
            print(f"   Difficulty: {question.difficulty_level}")
            print()
        
        # Update our test session to use this subject
        session_id = "81225db3-6d4d-489c-980d-b4aa7d93b3f6"
        try:
            session = StudentSession.objects.get(id=session_id)
            print(f"📝 Current session subject: {session.subject}")
            
            # Update session to use subject with questions
            session.subject = subject_with_questions
            session.save()
            
            print(f"✅ Updated session subject to: {subject_with_questions.name}")
            
            # Suggest a valid question for testing
            if sample_questions.exists():
                test_question = sample_questions.first()
                print(f"💡 Use this question ID for testing: {test_question.id}")
                
                # Create updated test script
                test_script = f'''#!/usr/bin/env python3
"""
Test submission with valid question ID
"""

import requests
import json

def test_submission_with_valid_id():
    url = "http://localhost:8000/simple/submit-answer/"
    
    data = {{
        "session_id": "{session.id}",
        "question_id": "{test_question.id}",
        "selected_answer": "A",
        "time_spent": 25.5
    }}
    
    print("=" * 60)
    print(f"Testing with VALID question ID")
    print(f"Session: {{data['session_id']}}")
    print(f"Question: {{data['question_id']}}")
    print("=" * 60)
    
    try:
        response = requests.post(url, json=data)
        print(f"Status: {{response.status_code}}")
        print(f"Headers: {{dict(response.headers)}}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"Answer correct: {{result.get('correct', 'Unknown')}}")
            print(f"Message: {{result.get('message', 'No message')}}")
        else:
            print("❌ FAILED!")
            print(f"Response text: {{response.text}}")
            try:
                error_details = response.json()
                print(f"Error details: {{json.dumps(error_details, indent=2)}}")
            except:
                pass
                
    except Exception as e:
        print(f"❌ Connection error: {{e}}")

if __name__ == "__main__":
    test_submission_with_valid_id()
'''
                
                # Save the updated test script
                with open("test_valid_submission.py", "w") as f:
                    f.write(test_script)
                
                print(f"📁 Created test_valid_submission.py with valid question ID")
                
        except StudentSession.DoesNotExist:
            print(f"❌ Session {session_id} not found")
    else:
        print("❌ No subjects with questions found in database!")

if __name__ == "__main__":
    check_subjects_and_questions()