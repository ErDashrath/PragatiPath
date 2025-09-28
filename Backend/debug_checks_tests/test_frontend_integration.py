#!/usr/bin/env python3
"""
Test frontend-backend integration for the assessment system
Tests all API endpoints that the frontend uses
"""
import requests
import json

def test_frontend_backend_integration():
    print("=== Testing Frontend-Backend Integration ===")
    
    # Test 1: Get Subjects (frontend uses multi-student API)
    print("\n1. Testing /api/multi-student/subjects/ (used by frontend)")
    try:
        r = requests.get('http://localhost:8000/api/multi-student/subjects/')
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            subjects = r.json()
            print(f"   ✅ Found {len(subjects)} subjects")
            for subject in subjects:
                print(f"      - {subject['name']} (id: {subject['id']}, code: {subject['code']})")
            
            # Test 2: Get Chapters for each subject
            print(f"\n2. Testing /api/multi-student/subjects/{{id}}/chapters/ (used by frontend)")
            for subject in subjects:
                r = requests.get(f'http://localhost:8000/api/multi-student/subjects/{subject["id"]}/chapters/')
                if r.status_code == 200:
                    chapters = r.json()
                    print(f"   ✅ {subject['name']}: {len(chapters)} chapters")
                    for chapter in chapters[:2]:  # Show first 2 chapters
                        print(f"      - {chapter['name']} (id: {chapter['id']})")
                else:
                    print(f"   ❌ {subject['name']}: Failed to get chapters")
            
            # Test 3: Start Assessment (frontend uses full-assessment API)
            print(f"\n3. Testing /api/full-assessment/start (used by frontend)")
            assessment_data = {
                'student_username': 'frontend_test_user',
                'subject_code': subjects[0]['code'],  # Use first subject
                'chapter_id': None,  # All chapters
                'assessment_type': 'PRACTICE',
                'question_count': 3,
                'time_limit_minutes': 15
            }
            
            r = requests.post('http://localhost:8000/api/full-assessment/start', json=assessment_data)
            print(f"   Status: {r.status_code}")
            if r.status_code == 200:
                assessment = r.json()
                assessment_id = assessment['assessment_id']
                print(f"   ✅ Assessment created: {assessment_id}")
                print(f"      Subject: {assessment['subject_name']}")
                print(f"      Questions: {assessment['question_count']}")
                
                # Test 4: Get Questions (frontend uses full-assessment API)
                print(f"\n4. Testing /api/full-assessment/questions/{{id}} (used by frontend)")
                r = requests.get(f'http://localhost:8000/api/full-assessment/questions/{assessment_id}')
                print(f"   Status: {r.status_code}")
                if r.status_code == 200:
                    questions_data = r.json()
                    questions = questions_data['questions']
                    print(f"   ✅ Got {len(questions)} questions")
                    
                    # Show sample question structure
                    if questions:
                        q = questions[0]
                        print(f"   Sample Question Structure:")
                        print(f"      - ID: {q['question_id']}")
                        print(f"      - Topic: {q['topic']}")
                        print(f"      - Subtopic: {q['subtopic']}")
                        print(f"      - Difficulty: {q['difficulty_level']}")
                        print(f"      - Options: {list(q['options'].keys())}")
                        print(f"      - Text: {q['question_text'][:80]}...")
                        
                        # Test 5: Submit Answer (frontend uses full-assessment API)
                        print(f"\n5. Testing /api/full-assessment/submit-answer (used by frontend)")
                        answer_data = {
                            'assessment_id': assessment_id,
                            'question_id': q['question_id'],
                            'selected_answer': 'a',
                            'time_taken_seconds': 30
                        }
                        
                        r = requests.post('http://localhost:8000/api/full-assessment/submit-answer', json=answer_data)
                        print(f"   Status: {r.status_code}")
                        if r.status_code == 200:
                            result = r.json()
                            print(f"   ✅ Answer submitted successfully")
                            print(f"      Correct: {result.get('is_correct', 'Unknown')}")
                            print(f"      Points: {result.get('points_earned', 0)}")
                        else:
                            print(f"   ❌ Failed to submit answer: {r.text[:100]}")
                    
                    return True
                else:
                    print(f"   ❌ Failed to get questions: {r.text[:100]}")
            else:
                print(f"   ❌ Failed to start assessment: {r.text[:100]}")
        else:
            print(f"   ❌ Failed to get subjects: {r.text[:100]}")
    
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return False
    
    return False

def test_frontend_connectivity():
    """Test if frontend is accessible"""
    print("\n=== Testing Frontend Connectivity ===")
    try:
        r = requests.get('http://localhost:5000', timeout=5)
        print(f"Frontend Status: {r.status_code}")
        if r.status_code == 200:
            print("✅ Frontend is accessible on port 5000")
            return True
        else:
            print("❌ Frontend returned error")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to frontend: {e}")
        return False

if __name__ == '__main__':
    print("Testing complete assessment system integration...")
    
    # Test backend API
    backend_success = test_frontend_backend_integration()
    
    # Test frontend connectivity
    frontend_success = test_frontend_connectivity()
    
    print("\n" + "="*60)
    if backend_success and frontend_success:
        print("🎉 INTEGRATION SUCCESS!")
        print("✅ Backend APIs working correctly")
        print("✅ Frontend accessible")
        print("✅ Ready for complete assessment workflow")
    elif backend_success:
        print("⚠️  PARTIAL SUCCESS")
        print("✅ Backend APIs working correctly")
        print("❌ Frontend connectivity issues")
    else:
        print("❌ INTEGRATION FAILED")
        print("❌ Backend API issues")