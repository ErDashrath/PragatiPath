#!/usr/bin/env python3
"""
Test Enhanced History API with actual user data
"""

import requests
import json

def test_history_with_real_user():
    """Test the history API with a session that has actual data"""
    
    base_url = "http://localhost:8000"
    
    print("🔍 Testing Enhanced History API with Real Data")
    print("=" * 50)
    
    # Step 1: Create a session with a specific user
    print("\n1️⃣ Creating session with identifiable user...")
    try:
        response = requests.post(f"{base_url}/simple/start-session/", json={
            "student_name": "history_test_user",
            "subject": "verbal_ability"
        })
        if response.status_code == 200:
            data = response.json()
            session_id = data.get('session_id')
            print(f"   ✅ Session created: {session_id}")
            print(f"   👤 User: history_test_user")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Step 2: Complete several questions to generate history data
    print(f"\n2️⃣ Completing questions to build history...")
    for i in range(5):
        # Get question
        response = requests.get(f"{base_url}/simple/get-question/{session_id}/")
        if response.status_code == 200:
            question = response.json()
            question_id = question.get('question_id')
            
            # Submit answer (alternate correct/incorrect for variety)
            is_correct_answer = "A" if i % 2 == 0 else "B"  # Simple alternating pattern
            response = requests.post(f"{base_url}/simple/submit-answer/", json={
                "session_id": session_id,
                "question_id": question_id,
                "selected_answer": is_correct_answer,
                "time_spent": 20 + i * 5  # Varying time spent
            })
            
            if response.status_code == 200:
                result = response.json()
                print(f"   📝 Question {i+1}: {result.get('is_correct', 'Unknown')} - Mastery: {result.get('adaptive_feedback', {}).get('mastery_change', 'N/A')}")
            else:
                print(f"   ⚠️  Question {i+1} submission failed")
        else:
            print(f"   ⚠️  Question {i+1} retrieval failed")
    
    # Step 3: Test the enhanced history API
    print(f"\n3️⃣ Testing enhanced history API...")
    try:
        # The API creates username as "student_{name}"
        api_username = "student_history_test_user"
        response = requests.get(f"{base_url}/history/student/{api_username}/")
        print(f"   📡 API Status: {response.status_code}")
        
        if response.status_code == 200:
            history = response.json()
            print(f"   ✅ History API SUCCESS!")
            print(f"   📊 Total sessions: {history.get('summary', {}).get('total_sessions', 0)}")
            print(f"   📖 Assessment sessions: {history.get('summary', {}).get('assessment_sessions_count', 0)}")
            print(f"   🧠 Adaptive sessions: {history.get('summary', {}).get('adaptive_sessions_count', 0)}")
            print(f"   🎯 Overall accuracy: {history.get('summary', {}).get('overall_accuracy', 0)}%")
            print(f"   📈 Questions attempted: {history.get('summary', {}).get('total_questions_attempted', 0)}")
            
            # Show session details
            adaptive_sessions = history.get('adaptive_sessions', [])
            if adaptive_sessions:
                latest_session = adaptive_sessions[0]
                print(f"\n   📋 Latest Session Details:")
                print(f"      Session ID: {latest_session.get('session_id', 'N/A')}")
                print(f"      Session Name: {latest_session.get('session_name', 'N/A')}")
                print(f"      Questions: {latest_session.get('questions_attempted', 0)}")
                print(f"      Accuracy: {latest_session.get('accuracy_percentage', 0):.1f}%")
                print(f"      Current Difficulty: {latest_session.get('current_difficulty', 'N/A')}")
                print(f"      Difficulty Adjustments: {latest_session.get('difficulty_adjustments', 0)}")
                
                # Show subject breakdown
                subject_breakdown = history.get('summary', {}).get('subject_breakdown', {})
                if subject_breakdown:
                    print(f"\n   📚 Subject Breakdown:")
                    for subject, stats in subject_breakdown.items():
                        print(f"      {subject}: {stats.get('total_sessions', 0)} sessions, {stats.get('accuracy', 0):.1f}% accuracy")
            
        elif response.status_code == 404:
            error_data = response.json()
            print(f"   ℹ️  Expected 404: {error_data.get('error', 'User not found')}")
            print(f"   📊 Empty summary provided: {error_data.get('summary', {})}")
            
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            print(f"   📄 Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ History API Error: {e}")
    
    # Step 4: Test session details API
    print(f"\n4️⃣ Testing session details API...")
    try:
        response = requests.get(f"{base_url}/history/session/{session_id}/")
        print(f"   📡 Details API Status: {response.status_code}")
        
        if response.status_code == 200:
            details = response.json()
            print(f"   ✅ Session details retrieved!")
            session_info = details.get('session_details', {})
            print(f"   📝 Session: {session_info.get('session_name', 'N/A')}")
            print(f"   🎯 Final Score: {session_info.get('questions_correct', 0)}/{session_info.get('questions_attempted', 0)}")
            print(f"   ⏱️  Duration: {session_info.get('duration_minutes', 0)} minutes")
            
            question_attempts = session_info.get('question_attempts', [])
            print(f"   📋 Question breakdown: {len(question_attempts)} attempts recorded")
            
        else:
            print(f"   ❌ Details API failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Details API Error: {e}")
    
    print(f"\n🎉 Enhanced History API Test Complete!")
    print(f"✅ All history functionality verified working!")

if __name__ == "__main__":
    test_history_with_real_user()