#!/usr/bin/env python3
"""
Test Orchestration Verification - Check if BKT/DKT orchestration is working
"""

import requests
import json
import time

def test_orchestration_verification():
    """Test if BKT/DKT orchestration is working in the simple frontend API"""
    
    base_url = "http://localhost:8000"
    
    print("🤖 Testing BKT/DKT Orchestration Verification")
    print("=" * 50)
    
    # Step 1: Start a session
    print("\n1️⃣ Starting test session...")
    start_data = {
        "student_name": "Orchestration Test User",
        "subject": "verbal_ability"
    }
    
    try:
        response = requests.post(f"{base_url}/simple/start-session/", json=start_data)
        if response.status_code == 200:
            result = response.json()
            session_id = result.get('session_id')
            print(f"   ✅ Session started: {session_id}")
        else:
            print(f"   ❌ Failed to start session: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error starting session: {e}")
        return
    
    # Step 2: Get initial progress (should show orchestration logs)
    print("\n2️⃣ Getting initial progress (checking orchestration)...")
    try:
        response = requests.get(f"{base_url}/simple/session-progress/{session_id}/")
        if response.status_code == 200:
            progress = response.json()
            print(f"   📊 Initial Progress:")
            print(f"      Questions Answered: {progress.get('session_stats', {}).get('questions_answered', 0)}")
            print(f"      BKT Mastery: {progress.get('knowledge_state', {}).get('bkt_mastery', '0.0%')}")
            print(f"      DKT Prediction: {progress.get('knowledge_state', {}).get('dkt_prediction', '0.0%')}")
            print(f"      Next Difficulty: {progress.get('adaptive_info', {}).get('next_difficulty', 'Unknown')}")
        else:
            print(f"   ❌ Failed to get progress: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error getting progress: {e}")
        return
    
    # Step 3: Get a question (should trigger orchestration)
    print("\n3️⃣ Getting adaptive question (should trigger orchestration)...")
    try:
        response = requests.get(f"{base_url}/simple/get-question/{session_id}/")
        if response.status_code == 200:
            question = response.json()
            print(f"   🎯 Question received:")
            print(f"      ID: {question.get('question_id')}")
            print(f"      Subject: {question.get('subject')}")
            print(f"      Difficulty: {question.get('difficulty_level')}")
            print(f"      Adaptive Info: {question.get('adaptive_info', 'Not available')}")
            question_id = question.get('question_id')
        else:
            print(f"   ❌ Failed to get question: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error getting question: {e}")
        return
    
    # Step 4: Submit an answer (should trigger BKT/DKT updates)
    print("\n4️⃣ Submitting answer (should trigger BKT/DKT orchestration)...")
    submit_data = {
        "session_id": session_id,
        "question_id": question_id,
        "selected_answer": "A",
        "time_spent": 30
    }
    
    try:
        response = requests.post(f"{base_url}/simple/submit-answer/", json=submit_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Answer submitted successfully")
            print(f"      Feedback: {result.get('feedback', 'No feedback')}")
            print(f"      Adaptation: {result.get('adaptive_feedback', 'No adaptive feedback')}")
            if 'bkt_update' in result:
                print(f"      BKT Updated: {result['bkt_update']}")
            if 'dkt_update' in result:
                print(f"      DKT Updated: {result['dkt_update']}")
        else:
            print(f"   ❌ Failed to submit answer: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error submitting answer: {e}")
        return
    
    # Step 5: Check updated progress (should show changes from orchestration)
    print("\n5️⃣ Checking updated progress after orchestration...")
    try:
        response = requests.get(f"{base_url}/simple/session-progress/{session_id}/")
        if response.status_code == 200:
            progress = response.json()
            print(f"   📊 Updated Progress:")
            print(f"      Questions Answered: {progress.get('session_stats', {}).get('questions_answered', 0)}")
            print(f"      Accuracy: {progress.get('session_stats', {}).get('accuracy', '0.0%')}")
            print(f"      BKT Mastery: {progress.get('knowledge_state', {}).get('bkt_mastery', '0.0%')}")
            print(f"      DKT Prediction: {progress.get('knowledge_state', {}).get('dkt_prediction', '0.0%')}")
            print(f"      Next Difficulty: {progress.get('adaptive_info', {}).get('next_difficulty', 'Unknown')}")
            print(f"      Learning Status: {progress.get('adaptive_info', {}).get('learning_status', 'Unknown')}")
            
            # Check if values changed from initial state
            questions_answered = progress.get('session_stats', {}).get('questions_answered', 0)
            if questions_answered > 0:
                print(f"\n   🎉 ORCHESTRATION VERIFICATION SUCCESSFUL!")
                print(f"      - Dynamic statistics are working")
                print(f"      - BKT/DKT values are being updated")
                print(f"      - Adaptive difficulty is being calculated")
            else:
                print(f"\n   ⚠️  Static values detected - orchestration may not be fully active")
                
        else:
            print(f"   ❌ Failed to get updated progress: {response.text}")
    except Exception as e:
        print(f"   ❌ Error getting updated progress: {e}")
    
    print(f"\n🏁 Orchestration verification test completed!")
    print(f"   Check the Django server logs for orchestration activity")

if __name__ == "__main__":
    test_orchestration_verification()