#!/usr/bin/env python3
"""
Quick test to check database questions and fix API issues
"""
import os
import sys
import django

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')
django.setup()

from assessment.improved_models import Question, Subject

def check_database():
    """Check what's in the database"""
    print("=== Database Check ===")
    
    # Check subjects
    subjects = Subject.objects.all()
    print(f"Subjects in database: {subjects.count()}")
    for subject in subjects:
        print(f"  - {subject.code}: {subject.name}")
    
    # Check questions
    questions = Question.objects.all()
    print(f"\nQuestions in database: {questions.count()}")
    
    if questions.exists():
        sample = questions.first()
        print(f"Sample question fields: {[field.name for field in sample._meta.fields]}")
        print(f"Sample question text: {getattr(sample, 'question_text', 'No question_text field')}")
        print(f"Sample question: {getattr(sample, 'text', 'No text field')}")
    
    return subjects.count(), questions.count()

def test_api_response():
    """Test what the API is actually returning"""
    print("\n=== API Response Test ===")
    import requests
    
    try:
        # Start session
        session_response = requests.post('http://localhost:8000/simple/start-session/', json={
            'user_id': 1, 
            'subject': 'quantitative_aptitude'
        })
        
        if session_response.status_code == 200:
            session_data = session_response.json()
            session_id = session_data['session_id']
            print(f"Session created: {session_id}")
            
            # Get question
            question_response = requests.get(f'http://localhost:8000/simple/get-question/{session_id}/')
            if question_response.status_code == 200:
                question_data = question_response.json()
                print(f"Question response keys: {list(question_data.keys())}")
                print(f"Question text field: {question_data.get('question_text', 'MISSING')}")
                return True
            else:
                print(f"Question request failed: {question_response.status_code}")
                print(f"Response: {question_response.text}")
        else:
            print(f"Session request failed: {session_response.status_code}")
            
    except Exception as e:
        print(f"API test error: {e}")
    
    return False

if __name__ == "__main__":
    subject_count, question_count = check_database()
    api_success = test_api_response()
    
    print(f"\n=== Summary ===")
    print(f"Subjects: {subject_count}")
    print(f"Questions: {question_count}")
    print(f"API working: {api_success}")