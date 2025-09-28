#!/usr/bin/env python3
"""
Check questions properly with correct field relationships
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

from assessment.models import AdaptiveQuestion, Subject, StudentSession
from django.db.models import Count

def check_questions_properly():
    """Check questions with correct relationships"""
    print("🔍 Checking 550 Questions in Database")
    print("=" * 50)
    
    # Check total questions
    total_questions = AdaptiveQuestion.objects.count()
    print(f"Total questions: {total_questions}")
    
    # Check questions by subject using the correct relationship
    print("\n📚 Questions by Subject:")
    print("-" * 25)
    
    # Get all subjects
    subjects = Subject.objects.all()
    
    for subject in subjects:
        # Count questions for each subject
        question_count = AdaptiveQuestion.objects.filter(subject=subject).count()
        if question_count > 0:
            print(f"✅ {subject.name} ({subject.code}): {question_count} questions")
        else:
            print(f"❌ {subject.name} ({subject.code}): 0 questions")
    
    # Find subjects with questions
    subjects_with_questions = []
    for subject in subjects:
        count = AdaptiveQuestion.objects.filter(subject=subject).count()
        if count > 0:
            subjects_with_questions.append((subject, count))
    
    subjects_with_questions.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n🎯 Subjects with questions ({len(subjects_with_questions)} total):")
    print("-" * 40)
    
    for subject, count in subjects_with_questions[:5]:  # Top 5
        print(f"\n📖 {subject.name} ({count} questions)")
        
        # Get sample questions
        sample_questions = AdaptiveQuestion.objects.filter(subject=subject)[:2]
        
        for i, question in enumerate(sample_questions, 1):
            print(f"   {i}. ID: {question.id}")
            print(f"      Text: {question.question_text[:80]}...")
            print(f"      Answer: {question.answer}")
            print(f"      Difficulty: {question.difficulty_level}")
    
    # Now check our test session and fix it
    print(f"\n🔧 Fixing Test Session:")
    print("-" * 20)
    
    session_id = "81225db3-6d4d-489c-980d-b4aa7d93b3f6"
    
    try:
        session = StudentSession.objects.get(id=session_id)
        print(f"Current session subject: {session.subject}")
        
        if subjects_with_questions:
            # Use the subject with the most questions
            best_subject, best_count = subjects_with_questions[0]
            
            print(f"Updating to subject with most questions: {best_subject.name} ({best_count} questions)")
            
            session.subject = best_subject
            session.save()
            
            print(f"✅ Session updated!")
            
            # Get a sample question from this subject
            sample_question = AdaptiveQuestion.objects.filter(subject=best_subject).first()
            
            if sample_question:
                print(f"\n💡 Test with this valid question:")
                print(f"   Session ID: {session.id}")
                print(f"   Question ID: {sample_question.id}")
                print(f"   Question Text: {sample_question.question_text[:100]}...")
                
                # Create a working test file
                test_code = f'''#!/usr/bin/env python3
"""
Test submission with proper question ID from database
"""

import requests
import json

def test_working_submission():
    url = "http://localhost:8000/simple/submit-answer/"
    
    data = {{
        "session_id": "{session.id}",
        "question_id": "{sample_question.id}",
        "selected_answer": "{sample_question.answer}",  # Use correct answer for testing
        "time_spent": 25.5
    }}
    
    print("=" * 60)
    print(f"🧪 Testing with REAL database question")
    print(f"Session: {{data['session_id']}}")
    print(f"Question: {{data['question_id']}}")
    print(f"Subject: {best_subject.name}")
    print(f"Expected Answer: {{data['selected_answer']}}")
    print("=" * 60)
    
    try:
        response = requests.post(url, json=data)
        print(f"Status: {{response.status_code}}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"Response: {{json.dumps(result, indent=2)}}")
        else:
            print("❌ FAILED!")
            print(f"Response: {{response.text}}")
            
    except Exception as e:
        print(f"❌ Error: {{e}}")

if __name__ == "__main__":
    test_working_submission()
'''
                
                with open("test_working_submission.py", "w") as f:
                    f.write(test_code)
                
                print(f"\n📁 Created test_working_submission.py")
                print(f"   Run: python test_working_submission.py")
                
    except StudentSession.DoesNotExist:
        print(f"❌ Session {session_id} not found")

if __name__ == "__main__":
    check_questions_properly()