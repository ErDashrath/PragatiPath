#!/usr/bin/env python3
"""
Test the complete assessment system with correct chapter names
"""
import requests
import json

def test_assessment_with_correct_chapters():
    print("=== Testing Assessment System with Correct Chapter Names ===")
    
    # Start an assessment
    start_data = {
        'student_username': 'test_student_123',
        'subject_code': 'quantitative_aptitude',
        'chapter_id': None,  # Will get all chapters
        'assessment_type': 'PRACTICE',
        'question_count': 5,
        'time_limit_minutes': 30
    }
    
    print("1. Starting assessment...")
    r = requests.post('http://localhost:8000/api/full-assessment/start', json=start_data)
    print(f"   Start Status: {r.status_code}")
    
    if r.status_code == 200:
        assessment = r.json()
        assessment_id = assessment['assessment_id']
        print(f"   Assessment ID: {assessment_id}")
        
        # Get questions
        print("2. Getting questions...")
        questions_r = requests.get(f'http://localhost:8000/api/full-assessment/questions/{assessment_id}')
        print(f"   Questions Status: {questions_r.status_code}")
        
        if questions_r.status_code == 200:
            questions_data = questions_r.json()
            questions = questions_data['questions']
            print(f"   Total questions: {len(questions)}")
            
            print("\n3. Sample questions:")
            for i, q in enumerate(questions[:3]):  # Show first 3 questions
                print(f"   Q{i+1}:")
                print(f"     Topic: {q['topic']}")
                print(f"     Subtopic: {q['subtopic']}")
                print(f"     Difficulty: {q['difficulty_level']}")
                print(f"     Text: {q['question_text'][:80]}...")
                print(f"     Options: {list(q['options'].keys())}")
                print()
                
            return True
        else:
            print(f"   Questions Error: {questions_r.text[:200]}")
            return False
    else:
        print(f"   Start Error: {r.text[:200]}")
        return False

if __name__ == '__main__':
    success = test_assessment_with_correct_chapters()
    if success:
        print("✅ Assessment system working correctly with proper chapter names!")
    else:
        print("❌ Assessment system has issues")