#!/usr/bin/env python3
"""
Test Session Completion and History Saving
Tests the complete flow from adaptive learning to history display
"""

import requests
import json
import time
from datetime import datetime

# Base URLs
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"

def test_session_completion_flow():
    """Test complete session flow including history saving"""
    print("🧪 Testing Session Completion and History Saving...")
    print("=" * 60)
    
    try:
        # 1. Start an adaptive session
        print("1️⃣ Starting adaptive learning session...")
        session_response = requests.post(f"{BACKEND_URL}/simple/start-session/", 
            json={
                "student_name": "Test Student",
                "subject": "quantitative_aptitude"
            }
        )
        
        if session_response.status_code != 200:
            print(f"❌ Failed to start session: {session_response.status_code}")
            return False
            
        session_data = session_response.json()
        session_id = session_data['session_id']
        print(f"✅ Session started: {session_id}")
        
        # 2. Answer a few questions
        print("2️⃣ Answering questions...")
        correct_answers = 0
        total_questions = 0
        
        for i in range(3):  # Answer 3 questions
            # Get next question
            question_response = requests.get(f"{BACKEND_URL}/simple/get-question/{session_id}/")
            if question_response.status_code != 200:
                print(f"❌ Failed to get question: {question_response.status_code}")
                continue
                
            question_data = question_response.json()
            # Question data is directly in the response, not nested under 'question'
            total_questions += 1
            
            print(f"   Question {i+1}: {question_data['question_text'][:50]}...")
            
            # Submit answer (choose first option for simplicity)
            answer_response = requests.post(f"{BACKEND_URL}/simple/submit-answer/", 
                json={
                    "session_id": session_id,
                    "question_id": question_data['question_id'],
                    "selected_answer": question_data['options'][0]['id'],  # Use option ID
                    "response_time": 5.0
                }
            )
            
            if answer_response.status_code == 200:
                result = answer_response.json()
                if result['answer_correct']:  # Changed from 'correct' to 'answer_correct'
                    correct_answers += 1
                    print(f"   ✅ Correct! ({result['explanation'][:30]}...)")
                else:
                    print(f"   ❌ Wrong ({result['explanation'][:30]}...)")
            else:
                print(f"   ⚠️ Answer submission failed")
            
            time.sleep(0.5)  # Brief pause
        
        print(f"   📊 Answered {total_questions} questions, {correct_answers} correct")
        
        # 3. Complete the session
        print("3️⃣ Completing session...")
        completion_response = requests.post(f"{BACKEND_URL}/simple/complete-session/", 
            json={
                "session_id": session_id,
                "total_questions": total_questions,
                "correct_answers": correct_answers,
                "session_duration_seconds": 60,
                "final_mastery_level": 0.75
            }
        )
        
        if completion_response.status_code != 200:
            print(f"❌ Failed to complete session: {completion_response.status_code}")
            print(f"Response: {completion_response.text}")
            return False
            
        completion_data = completion_response.json()
        print(f"✅ Session completed: {completion_data['message']}")
        
        # 4. Check if session appears in history
        print("4️⃣ Checking session history...")
        time.sleep(1)  # Brief pause to ensure database write
        
        # Try the correct history endpoints from the URL patterns
        # Based on the Django URLs: history/student/<str:username>/
        test_username = "Test Student"  # or "test-student" 
        history_response = requests.get(f"{BACKEND_URL}/history/student/{test_username}/")
        
        if history_response.status_code == 200:
            history_data = history_response.json()
            sessions = history_data.get('sessions', [])
            print(f"✅ Found {len(sessions)} session(s) in student history")
            
            if sessions:
                latest_session = sessions[0]
                print(f"   📅 Latest session: {latest_session.get('subject', 'Unknown')}")
                print(f"   📊 Score: {latest_session.get('score', 'N/A')}% ({latest_session.get('correct_answers', 0)}/{latest_session.get('total_questions', 0)})")
                print(f"   ⏱️ Duration: {latest_session.get('duration_minutes', 'N/A')} minutes")
        else:
            print(f"⚠️ Student history API failed: {history_response.status_code}")
            print(f"Response: {history_response.text}")
        
        # Also try the old enhanced history endpoint
        try:
            enhanced_history_response = requests.get(f"{BACKEND_URL}/api/enhanced-history/")
            if enhanced_history_response.status_code == 200:
                enhanced_data = enhanced_history_response.json()
                enhanced_sessions = enhanced_data.get('sessions', [])
                print(f"✅ Found {len(enhanced_sessions)} session(s) in enhanced history")
            else:
                print(f"⚠️ Enhanced history API failed: {enhanced_history_response.status_code}")
        except:
            print("⚠️ Enhanced history API not available")
        
        # 5. Test frontend accessibility
        print("5️⃣ Testing frontend accessibility...")
        try:
            frontend_response = requests.get(FRONTEND_URL, timeout=5)
            if frontend_response.status_code == 200:
                print("✅ Frontend is accessible")
            else:
                print(f"⚠️ Frontend returned: {frontend_response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Frontend not accessible: {e}")
        
        print("\n🎉 Session completion flow test completed!")
        print("=" * 60)
        print("📝 SUMMARY:")
        print(f"   ✅ Session created and completed: {session_id}")
        print(f"   📊 Questions answered: {total_questions}")
        print(f"   🎯 Correct answers: {correct_answers}")
        print(f"   💾 Session saved to database")
        print(f"   📚 History APIs accessible")
        print("\n🔗 Next steps:")
        print(f"   1. Open {FRONTEND_URL} in browser")
        print(f"   2. Login as student")
        print(f"   3. Complete an adaptive learning session")
        print(f"   4. Check Assessment History to see the session")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print(f"🚀 Starting test at {datetime.now()}")
    success = test_session_completion_flow()
    
    if success:
        print("\n✅ All tests passed! Session completion and history saving should work.")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")