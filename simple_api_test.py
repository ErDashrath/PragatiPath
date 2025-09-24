"""
Simple test script for competitive exam API v1 endpoints
Tests against     # Test 3: Submit answer
    print(f"\n3️⃣ Testing POST /api/assessment/v1/assessment/submit-answer")
    try:
        payload = {
            "student_id": student_id,
            "assessment_id": assessment_id,
            "question_id": question_id,
            "answer": "A",
            "response_time": 30.5,
            "subject": first_subject,
            "current_difficulty": "very_easy"
        }g Django server
"""

import requests
import json
import uuid

BASE_URL = 'http://localhost:8000'

def test_competitive_exam_api():
    """Test the new competitive exam API v1 endpoints"""
    print("🚀 Simple Competitive Exam API v1 Test")
    print("=" * 60)
    
    session = requests.Session()
    
    # Use an existing student ID
    student_id = "48703c5a-1840-4607-99fc-a3d98bc94753"  # test_competitive_student
    print(f"👤 Using existing student ID: {student_id}")
    
    # Test 1: Get subjects v1
    print(f"\n1️⃣ Testing GET /api/assessment/v1/subjects")
    try:
        response = session.get(f"{BASE_URL}/api/assessment/v1/subjects")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            response_data = response.json()
            subjects = response_data['subjects']
            print(f"   ✅ SUCCESS: Found {len(subjects)} subjects")
            for subject in subjects:
                print(f"      • {subject['subject_name']}: {subject['total_questions']} questions")
        else:
            print(f"   ❌ ERROR: {response.status_code} - {response.text[:200]}")
            return
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return
    
    if not subjects:
        print("   ❌ No subjects found - skipping remaining tests")
        return
    
    # Test 2: Start subject assessment
    print(f"\n2️⃣ Testing POST /api/assessment/v1/assessment/start-subject")
    try:
        first_subject = subjects[0]['subject_code']  # Use subject_code not subject_name
        payload = {
            "student_id": student_id,
            "subject": first_subject,
            "preferred_difficulty": "very_easy"
        }
        response = session.post(
            f"{BASE_URL}/api/assessment/v1/assessment/start-subject",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            start_data = response.json()
            print(f"   ✅ SUCCESS: Started {first_subject} assessment")
            print(f"      • Assessment ID: {start_data['assessment_id']}")
            print(f"      • Subject: {start_data['subject']}")
            print(f"      • Current difficulty: {start_data['current_difficulty']}")
            print(f"      • Student level: {start_data['student_level']}")
            if start_data['next_question']:
                print(f"      • Question: {start_data['next_question']['question_text'][:50]}...")
                assessment_id = start_data['assessment_id']
                question_id = start_data['next_question']['id']
                current_difficulty = start_data['current_difficulty']
        else:
            print(f"   ❌ ERROR: {response.status_code} - {response.text[:400]}")
            return
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return
    
    # Test 3: Submit answer
    print(f"\n3️⃣ Testing POST /api/assessment/v1/assessment/submit-answer")
    try:
        payload = {
            "student_id": student_id,
            "assessment_id": assessment_id,
            "question_id": question_id,
            "answer": "A",
            "response_time": 30.0,
            "subject": first_subject,
            "current_difficulty": current_difficulty
        }
        response = session.post(
            f"{BASE_URL}/api/assessment/v1/assessment/submit-answer",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            answer_data = response.json()
            print(f"   ✅ SUCCESS: Answer submitted")
            print(f"      • Correct: {answer_data['is_correct']}")
            print(f"      • Points earned: {answer_data['points_earned']}")
            print(f"      • Level unlocked: {answer_data['level_unlocked']}")
            if answer_data['next_question']:
                print(f"      • Next question: {answer_data['next_question']['question_text'][:50]}...")
        else:
            print(f"   ❌ ERROR: {response.status_code} - {response.text[:400]}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test 4: Get student progress
    print(f"\n4️⃣ Testing GET /api/assessment/v1/student/{student_id}/progress")
    try:
        response = session.get(f"{BASE_URL}/api/assessment/v1/student/{student_id}/progress")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            progress_data = response.json()
            print(f"   ✅ SUCCESS: Progress retrieved")
            print(f"      • Overall mastery: {progress_data.get('overall_mastery', 0):.2f}")
            if 'subject_progress' in progress_data:
                subject_progress = progress_data['subject_progress']
                if isinstance(subject_progress, dict):
                    for subject, data in subject_progress.items():
                        print(f"      • {subject}: Level {data.get('level', 1)}, Mastery {data.get('mastery', 0):.2f}")
                elif isinstance(subject_progress, list):
                    for subject_data in subject_progress:
                        if isinstance(subject_data, dict):
                            subject_name = subject_data.get('subject', 'Unknown')
                            level = subject_data.get('level', 1)
                            accuracy = subject_data.get('accuracy_rate', 0)
                            print(f"      • {subject_name}: Level {level}, Accuracy {accuracy:.2f}")
                else:
                    print(f"      • Subject progress format: {type(subject_progress)}")
        else:
            print(f"   ❌ ERROR: {response.status_code} - {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Simple Test Completed!")

if __name__ == "__main__":
    test_competitive_exam_api()