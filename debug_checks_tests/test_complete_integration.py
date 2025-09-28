#!/usr/bin/env python3

import requests
import json
import time

def test_complete_integration():
    """Test the complete frontend-backend integration for adaptive session details"""
    
    print("🔍 Testing Complete Frontend-Backend Integration")
    print("=" * 60)
    
    # Test 1: Verify backend endpoint returns real data
    print("\n1️⃣ Testing Backend Endpoint...")
    session_id = "dc684f75-c850-4495-b17d-7f12c4b4b31f"
    backend_url = f"http://localhost:8000/history/session-details/{session_id}/"
    
    try:
        backend_response = requests.get(backend_url)
        print(f"Backend Status: {backend_response.status_code}")
        
        if backend_response.status_code == 200:
            backend_data = backend_response.json()
            print("✅ Backend endpoint working!")
            
            session_details = backend_data.get('session_details', {})
            question_attempts = session_details.get('question_attempts', [])
            
            print(f"📊 Real Data Summary:")
            print(f"  - Session: {session_details.get('session_name')}")
            print(f"  - Questions: {session_details.get('questions_attempted')}")
            print(f"  - Correct: {session_details.get('questions_correct')}")
            print(f"  - Accuracy: {session_details.get('accuracy_percentage')}%")
            print(f"  - Real Question Attempts: {len(question_attempts)}")
            
            if question_attempts:
                print(f"\n📋 Sample Real Questions:")
                for i, attempt in enumerate(question_attempts[:3]):
                    status = "✅" if attempt.get('is_correct') else "❌"
                    print(f"  Q{attempt.get('question_number')}: {status} "
                          f"Answer: {attempt.get('student_answer')} "
                          f"(Correct: {attempt.get('correct_answer')}) "
                          f"Time: {attempt.get('time_spent')}s")
        else:
            print(f"❌ Backend endpoint failed: {backend_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False
    
    # Test 2: Check if frontend can access the endpoint through proxy
    print(f"\n2️⃣ Testing Frontend Proxy Access...")
    frontend_url = f"http://localhost:3000/history/session-details/{session_id}/"
    
    try:
        frontend_response = requests.get(frontend_url)
        print(f"Frontend Proxy Status: {frontend_response.status_code}")
        
        if frontend_response.status_code == 200:
            frontend_data = frontend_response.json()
            print("✅ Frontend proxy working!")
            
            # Compare data consistency
            if frontend_data == backend_data:
                print("✅ Data consistency verified - Frontend gets same real data as backend!")
            else:
                print("⚠️ Data mismatch between frontend and backend")
        else:
            print(f"❌ Frontend proxy failed: {frontend_response.status_code}")
            
    except Exception as e:
        print(f"❌ Frontend proxy test failed: {e}")
    
    # Test 3: Instructions for manual UI testing
    print(f"\n3️⃣ Manual UI Testing Instructions:")
    print("=" * 40)
    print(f"🌐 Open: http://localhost:3000")
    print(f"📝 Login with your credentials")
    print(f"📊 Go to Assessment History")
    print(f"🔍 Look for adaptive learning sessions")
    print(f"👁️ Click the 'Details' button/eye icon")
    print(f"📋 Verify you see REAL question attempts:")
    print(f"   - Question numbers 1-15")
    print(f"   - Real student answers (A, B, C, D)")
    print(f"   - Real correct answers")
    print(f"   - Actual time spent per question")
    print(f"   - Difficulty levels (easy, moderate, difficult)")
    print(f"   - NOT simulated 'Adaptive Question X' text")
    
    print(f"\n✅ Integration test completed!")
    print(f"📊 The system should now display REAL question data from the API!")
    
    return True

if __name__ == "__main__":
    test_complete_integration()