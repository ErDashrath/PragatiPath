#!/usr/bin/env python
"""
Test the history API to verify data consistency fix is working
"""
import requests
import json

def test_history_api_fix():
    print("🔍 Testing History API Data Consistency Fix")
    print("=" * 50)
    
    # First, create a test session to ensure we have data
    print("1. Creating test session...")
    try:
        # Start session
        start_resp = requests.post("http://localhost:8000/simple/start-session/", 
                                 json={"student_name": "history_test_user", "question_count": 5})
        if start_resp.status_code != 200:
            print(f"❌ Failed to start session: {start_resp.status_code}")
            return
            
        session_data = start_resp.json()
        session_id = session_data['session_id']
        print(f"✅ Session created: {session_id[:8]}...")
        
        # Answer 2 questions correctly, 3 incorrectly
        expected_correct = 0
        for i in range(5):
            # Get question
            q_resp = requests.get(f"http://localhost:8000/simple/get-question/{session_id}/")
            if q_resp.status_code != 200:
                print(f"❌ Failed to get question {i+1}")
                continue
                
            q_data = q_resp.json()
            question_id = q_data['question_id']
            correct_answer = q_data['correct_answer']
            
            # Answer first 2 correctly, rest incorrectly
            if i < 2:
                chosen_answer = correct_answer
                expected_correct += 1
                result_symbol = "✅"
            else:
                wrong_options = ['A', 'B', 'C', 'D']
                wrong_options.remove(correct_answer)
                chosen_answer = wrong_options[0]
                result_symbol = "❌"
            
            # Submit answer
            submit_resp = requests.post("http://localhost:8000/simple/submit-answer/", 
                                      json={"session_id": session_id, 
                                           "question_id": question_id, 
                                           "selected_answer": chosen_answer,
                                           "time_spent": 15})
            
            if submit_resp.status_code == 200:
                print(f"   Q{i+1}: {result_symbol}")
            else:
                print(f"❌ Failed to submit answer {i+1}")
        
        # Complete session with wrong data
        print(f"\n2. Completing session (passing wrong data intentionally)...")
        complete_resp = requests.post("http://localhost:8000/simple/complete-session/", 
                                    json={
                                        "session_id": session_id,
                                        "total_questions": 5,
                                        "correct_answers": 0,  # Wrong data - should be overridden
                                        "session_duration_seconds": 120,
                                        "final_mastery_level": 0.4,
                                        "student_username": "history_test_user"
                                    })
        
        if complete_resp.status_code != 200:
            print(f"❌ Failed to complete session: {complete_resp.status_code}")
            return
            
        print("✅ Session completed")
        print(f"Expected result: {expected_correct}/5 correct answers")
        
        # Test history API
        print(f"\n3. Testing history API...")
        history_resp = requests.get("http://localhost:8000/history/student/history_test_user/")
        
        if history_resp.status_code != 200:
            print(f"❌ History API failed: {history_resp.status_code}")
            return
            
        history_data = history_resp.json()
        
        if not history_data.get('success'):
            print(f"❌ History API returned error: {history_data.get('error')}")
            return
            
        sessions = history_data.get('adaptive_sessions', []) + history_data.get('assessment_sessions', [])
        if not sessions:
            print("❌ No sessions found in history")
            return
            
        # Find our test session
        test_session = None
        for session in sessions:
            if session['session_id'] == session_id:
                test_session = session
                break
                
        if not test_session:
            print("❌ Test session not found in history")
            return
            
        print(f"📊 History API Results:")
        print(f"   Questions Attempted: {test_session['questions_attempted']}")
        print(f"   Questions Correct: {test_session['questions_correct']}")
        print(f"   Accuracy: {test_session['accuracy_percentage']}%")
        
        # Test detailed view
        print(f"\n4. Testing detailed session API...")
        details_resp = requests.get(f"http://localhost:8000/history/session-details/{session_id}/")
        
        if details_resp.status_code != 200:
            print(f"❌ Details API failed: {details_resp.status_code}")
            return
            
        details_data = details_resp.json()
        
        if not details_data.get('success'):
            print(f"❌ Details API returned error: {details_data.get('error')}")
            return
            
        session_details = details_data['session_details']
        print(f"📋 Detailed View Results:")
        print(f"   Questions Attempted: {session_details['questions_attempted']}")
        print(f"   Questions Correct: {session_details['questions_correct']}")
        print(f"   Accuracy: {session_details['accuracy_percentage']}%")
        print(f"   Question Attempts Count: {len(session_details['question_attempts'])}")
        
        # Verify consistency
        history_correct = test_session['questions_correct']
        details_correct = session_details['questions_correct']
        attempts_correct = sum(1 for attempt in session_details['question_attempts'] if attempt['is_correct'])
        
        print(f"\n🔍 Consistency Check:")
        print(f"   Expected Correct: {expected_correct}")
        print(f"   History API: {history_correct}")
        print(f"   Details API: {details_correct}")  
        print(f"   Actual Attempts: {attempts_correct}")
        
        if history_correct == details_correct == attempts_correct == expected_correct:
            print(f"\n✅ DATA CONSISTENCY FIX SUCCESSFUL!")
            print(f"   All APIs now return consistent, accurate data!")
        else:
            print(f"\n❌ Data inconsistency still exists:")
            print(f"   History vs Details: {history_correct} vs {details_correct}")
            print(f"   Expected vs Actual: {expected_correct} vs {attempts_correct}")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_history_api_fix()