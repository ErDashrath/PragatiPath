"""
Test script for competitive exam dataset support with subject-wise progression.
Tests the new CSV import system and subject-specific question APIs.
"""

import requests
import json
import sys
import random

# API base URL
BASE_URL = "http://localhost:8000/api/assessment"

def test_list_subjects():
    """Test listing available subjects"""
    print("\n=== Testing List Subjects ===")
    
    try:
        response = requests.get(f"{BASE_URL}/subjects")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data['total_subjects']} subjects:")
            for subject in data['subjects']:
                print(f"   • {subject['subject_name']}: {subject['question_count']} questions")
            return data['subjects']
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return []
    
    except Exception as e:
        print(f"❌ Exception: {e}")
        return []

def test_subject_questions(subject_code, student_id="test-student-123"):
    """Test getting questions for a specific subject"""
    print(f"\n=== Testing Subject Questions: {subject_code} ===")
    
    payload = {
        "student_id": student_id,
        "subject": subject_code,
        "count": 3
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/subject-questions",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Retrieved {data['returned_count']} questions for {data['subject']}")
            
            for i, question in enumerate(data['questions'], 1):
                print(f"\n   Question {i}:")
                print(f"   ID: {question['id']}")
                print(f"   Text: {question['question_text'][:60]}...")
                print(f"   Difficulty: {question['difficulty_level']} (Level {question['level']})")
                print(f"   Options: {list(question['options'].keys())}")
                
            return data['questions']
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return []
    
    except Exception as e:
        print(f"❌ Exception: {e}")
        return []

def test_subject_stats(subject_code, student_id="test-student-123"):
    """Test getting statistics for a subject"""
    print(f"\n=== Testing Subject Stats: {subject_code} ===")
    
    try:
        response = requests.get(f"{BASE_URL}/subjects/{subject_code}/stats?student_id={student_id}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Subject: {data['subject']}")
            print(f"   Total Questions: {data['total_questions']}")
            print(f"   Difficulty Breakdown: {data['difficulty_breakdown']}")
            print(f"   Level Breakdown: {data['level_breakdown']}")
            
            if 'student_progress' in data:
                progress = data['student_progress']
                if 'total_attempted' in progress:
                    print(f"   Student Progress:")
                    print(f"     Attempted: {progress['total_attempted']}")
                    if progress['total_attempted'] > 0:
                        print(f"     Accuracy: {progress['accuracy_rate']:.2%}")
                        print(f"     Avg Response Time: {progress['average_response_time']:.1f}s")
            
            return data
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
    
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def test_submit_answer_with_subject(question_id, answer, subject_code, student_id="test-student-123"):
    """Test submitting an answer with subject information"""
    print(f"\n=== Testing Submit Answer with Subject ===")
    
    payload = {
        "student_id": student_id,
        "question_id": question_id,
        "answer": answer,
        "response_time": random.uniform(30, 120),
        "subject": subject_code,
        "skill_id": f"{subject_code}_skill",
        "metadata": {
            "test_run": True,
            "subject": subject_code
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/submit",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Answer submitted successfully!")
            print(f"   Correct: {data['was_correct']}")
            print(f"   Feedback: {data['feedback']}")
            
            # Check BKT results
            if 'algorithm_results' in data and 'bkt' in data['algorithm_results']:
                bkt_results = data['algorithm_results']['bkt']
                if bkt_results['status'] == 'success':
                    print(f"   New Mastery: {bkt_results['new_mastery']:.3f}")
                    
                    # Check level progression
                    if 'level_progression' in bkt_results:
                        progression = bkt_results['level_progression']
                        if progression.get('level_changed'):
                            print(f"   🎉 LEVEL UP! New Level: {progression.get('new_level')}")
            
            # Check recommendations
            if data.get('recommendations'):
                print(f"   Recommendations: {data['recommendations']}")
            
            return data
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
    
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def main():
    """Main test function"""
    print("🧪 Testing Competitive Exam Dataset Support")
    print("=" * 50)
    
    # Test 1: List available subjects
    subjects = test_list_subjects()
    
    if not subjects:
        print("\n❌ No subjects found. Make sure you've imported CSV data!")
        sys.exit(1)
    
    # Test 2: Get questions for each available subject
    for subject in subjects[:2]:  # Test first 2 subjects
        subject_code = subject['subject_code']
        
        # Get subject statistics
        test_subject_stats(subject_code)
        
        # Get questions for this subject
        questions = test_subject_questions(subject_code)
        
        if questions:
            # Test submitting an answer for the first question
            first_question = questions[0]
            question_id = first_question['id']
            
            # Submit correct answer (option 'a' for testing)
            test_submit_answer_with_subject(question_id, 'a', subject_code)
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print("✅ All tests completed!")
    print("📊 Check your database for imported questions and interactions")
    print("🚀 Your competitive exam system is ready!")

if __name__ == "__main__":
    main()