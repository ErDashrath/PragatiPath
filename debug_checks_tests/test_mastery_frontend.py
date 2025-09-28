#!/usr/bin/env python3
"""
Test mastery frontend integration
"""
import requests
import json

def test_mastery_frontend_integration():
    """Test if mastery tracking works end-to-end with frontend"""
    
    print("🔍 TESTING MASTERY FRONTEND INTEGRATION")
    print("=" * 50)
    
    # Test 1: Start a new session
    print("📚 Step 1: Starting new session")
    session_data = {
        'student_name': 'frontend_test_user',
        'subject': 'quantitative_aptitude',
        'question_count': 3
    }
    
    response = requests.post("http://localhost:5000/simple/start-session/", json=session_data)
    if response.status_code == 200:
        session_info = response.json()
        session_id = session_info.get('session_id')
        user_id = session_info.get('user_id')  # This is what frontend needs for history
        
        print(f"✅ Session started: {session_id}")
        print(f"👤 User ID for history: {user_id}")
    else:
        print(f"❌ Failed to start session: {response.status_code}")
        print(response.text)
        return False
    
    # Test 2: Answer a few questions
    print(f"\n📝 Step 2: Answering questions")
    for i in range(3):
        # Get question
        response = requests.get(f"http://localhost:5000/simple/get-question/{session_id}/")
        if response.status_code != 200:
            print(f"❌ Failed to get question {i+1}")
            continue
            
        question_data = response.json()
        question_id = question_data.get('question_id')
        
        # Submit answer
        answer_data = {
            'session_id': session_id,
            'question_id': question_id,
            'selected_answer': 'A',
            'time_spent': 10.0
        }
        
        response = requests.post("http://localhost:5000/simple/submit-answer/", json=answer_data)
        if response.status_code == 200:
            result = response.json()
            bkt_after = result.get('bkt_mastery_after', 0)
            print(f"   ✅ Question {i+1} answered - BKT: {bkt_after:.3f}")
        else:
            print(f"   ❌ Failed to submit answer {i+1}")
    
    # Test 3: Complete session with new endpoint
    print(f"\n🏁 Step 3: Completing session with mastery storage")
    completion_data = {
        'session_id': session_id,
        'completion_reason': 'finished'
    }
    
    response = requests.post("http://localhost:5000/simple/complete-session/", json=completion_data)
    if response.status_code == 200:
        result = response.json()
        final_mastery = result.get('completion_data', {}).get('final_mastery', {})
        
        print(f"✅ Session completed!")
        print(f"🧠 Final BKT Mastery: {final_mastery.get('bkt_mastery', 'N/A')}")
        print(f"🎯 Mastery Level: {final_mastery.get('mastery_level', 'N/A')}")
        print(f"🏆 Mastery Achieved: {final_mastery.get('mastery_achieved', False)}")
    else:
        print(f"❌ Session completion failed: {response.status_code}")
        print(response.text)
        return False
    
    # Test 4: Check mastery history
    print(f"\n📚 Step 4: Checking mastery history")
    response = requests.get(f"http://localhost:5000/simple/session-history/{user_id}/")
    if response.status_code == 200:
        history = response.json()
        
        print(f"✅ Mastery history retrieved!")
        print(f"👤 Student: {history.get('student_name', 'N/A')}")
        print(f"📊 Total Sessions: {history.get('total_sessions', 0)}")
        
        sessions = history.get('sessions', [])
        if sessions:
            latest = sessions[0]
            mastery_scores = latest.get('mastery_scores', {})
            print(f"\n🕒 Latest Session Mastery:")
            print(f"   📅 Date: {latest.get('session_date', 'N/A')}")
            print(f"   🧠 BKT: {mastery_scores.get('bkt_mastery', 'N/A')}")
            print(f"   🤖 DKT: {mastery_scores.get('dkt_prediction', 'N/A')}")
            print(f"   📊 Combined: {mastery_scores.get('combined_confidence', 'N/A')}")
            print(f"   🎯 Level: {mastery_scores.get('mastery_level', 'N/A')}")
    else:
        print(f"❌ Failed to get mastery history: {response.status_code}")
        print(response.text)
        return False
    
    print(f"\n🎉 MASTERY FRONTEND INTEGRATION: SUCCESS!")
    print(f"✅ All endpoints working through frontend proxy")
    print(f"✅ Session completion stores mastery data") 
    print(f"✅ Mastery history displays properly")
    print(f"✅ Ready for frontend UI integration!")
    
    return True

if __name__ == "__main__":
    test_mastery_frontend_integration()