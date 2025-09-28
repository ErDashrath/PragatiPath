#!/usr/bin/env python
"""
Test script to verify that the data consistency fix is working properly.
This script will:
1. Create a test session with 10 questions
2. Answer questions with known results
3. Complete the session
4. Verify that session records match the actual question attempts
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000/simple"
TEST_USERNAME = "test_user_consistency"

def test_data_consistency():
    """Test that session completion creates consistent data"""
    print("🧪 Testing Data Consistency Fix...")
    print("=" * 60)
    
    # Step 1: Start session
    print("1️⃣ Starting session with 10 questions...")
    start_response = requests.post(f"{BASE_URL}/start-session", json={
        "student_name": TEST_USERNAME,
        "question_count": 10
    })
    
    if start_response.status_code != 200:
        print(f"❌ Failed to start session: {start_response.text}")
        return False
    
    session_data = start_response.json()
    session_id = session_data['session_id']
    print(f"✅ Session started: {session_id}")
    
    # Step 2: Answer questions with controlled pattern
    print("\n2️⃣ Answering 10 questions with known pattern...")
    correct_count = 0
    
    # Answer pattern: correct, incorrect, correct, incorrect, etc.
    answer_pattern = ['A', 'B', 'C', 'D'] * 3  # Ensure we have enough answers
    
    for i in range(10):
        # Get question
        question_response = requests.get(f"{BASE_URL}/get-question", params={
            "session_id": session_id
        })
        
        if question_response.status_code != 200:
            print(f"❌ Failed to get question {i+1}: {question_response.text}")
            break
            
        question_data = question_response.json()
        question_id = question_data['question']['id']
        correct_answer = question_data['question']['correct_answer']
        
        # Choose answer based on pattern: odd questions correct, even questions wrong
        if i % 2 == 0:  # Even index (1st, 3rd, 5th, etc.) - answer correctly
            chosen_answer = correct_answer
            correct_count += 1
            result_symbol = "✅"
        else:  # Odd index (2nd, 4th, 6th, etc.) - answer incorrectly
            # Choose a wrong answer
            wrong_options = [opt for opt in ['A', 'B', 'C', 'D'] if opt != correct_answer]
            chosen_answer = wrong_options[0] if wrong_options else 'Z'
            result_symbol = "❌"
        
        # Submit answer
        submit_response = requests.post(f"{BASE_URL}/submit-answer", json={
            "session_id": session_id,
            "question_id": question_id,
            "selected_answer": chosen_answer,
            "time_spent": 30
        })
        
        if submit_response.status_code == 200:
            submit_data = submit_response.json()
            actual_correct = submit_data.get('correct', False)
            print(f"   Q{i+1:2d}: {chosen_answer} vs {correct_answer} {result_symbol} -> {actual_correct}")
        else:
            print(f"❌ Failed to submit answer {i+1}: {submit_response.text}")
    
    expected_correct = correct_count
    print(f"\n📊 Expected pattern: {expected_correct}/10 correct answers")
    
    # Step 3: Complete session
    print("\n3️⃣ Completing session...")
    complete_response = requests.post(f"{BASE_URL}/complete-session", json={
        "session_id": session_id,
        "total_questions": 10,
        "correct_answers": 999,  # Pass wrong value intentionally - should be overridden
        "session_duration_seconds": 300,
        "final_mastery_level": 0.5,
        "student_username": TEST_USERNAME
    })
    
    if complete_response.status_code != 200:
        print(f"❌ Failed to complete session: {complete_response.text}")
        return False
        
    print("✅ Session completed successfully")
    
    # Step 4: Check session history for data consistency
    print("\n4️⃣ Verifying data consistency...")
    
    # Get session history
    history_response = requests.get(f"http://localhost:8000/history/student/{TEST_USERNAME}/")
    
    if history_response.status_code != 200:
        print(f"❌ Failed to get history: {history_response.text}")
        return False
    
    history_data = history_response.json()
    sessions = history_data.get('sessions', [])
    
    if not sessions:
        print("❌ No sessions found in history")
        return False
    
    # Find our test session (should be the most recent)
    latest_session = sessions[0]
    session_correct = latest_session.get('questions_correct', 0)
    session_total = latest_session.get('questions_attempted', 0)
    session_accuracy = latest_session.get('percentage_score', 0)
    
    print(f"📋 Session Record Summary:")
    print(f"   Questions Attempted: {session_total}")
    print(f"   Questions Correct: {session_correct}")
    print(f"   Accuracy: {session_accuracy:.1f}%")
    
    # Get detailed view
    detailed_response = requests.get(f"http://localhost:8000/history/session-details/{latest_session['id']}/")
    
    if detailed_response.status_code != 200:
        print(f"❌ Failed to get detailed view: {detailed_response.text}")
        return False
    
    detailed_data = detailed_response.json()
    attempts = detailed_data.get('question_attempts', [])
    
    if attempts:
        actual_correct = sum(1 for attempt in attempts if attempt.get('is_correct'))
        actual_total = len(attempts)
        actual_accuracy = (actual_correct / actual_total * 100) if actual_total > 0 else 0
        
        print(f"\n📊 Detailed Question Attempts:")
        print(f"   Total Attempts: {actual_total}")
        print(f"   Correct Attempts: {actual_correct}")
        print(f"   Calculated Accuracy: {actual_accuracy:.1f}%")
        
        # Verify consistency
        print(f"\n🔍 Data Consistency Check:")
        print(f"   Expected Correct: {expected_correct}")
        print(f"   Session Record:   {session_correct}")
        print(f"   Detailed View:    {actual_correct}")
        
        consistency_check = (
            session_correct == actual_correct == expected_correct and
            session_total == actual_total == 10 and
            abs(session_accuracy - actual_accuracy) < 0.1
        )
        
        if consistency_check:
            print("✅ DATA CONSISTENCY VERIFIED - All records match!")
            return True
        else:
            print("❌ DATA INCONSISTENCY DETECTED:")
            print(f"   Session vs Detailed: {session_correct} vs {actual_correct}")
            print(f"   Session vs Expected: {session_correct} vs {expected_correct}")
            return False
    else:
        print("❌ No detailed question attempts found")
        return False

if __name__ == "__main__":
    try:
        success = test_data_consistency()
        if success:
            print("\n🎉 Data consistency fix is working properly!")
        else:
            print("\n💥 Data consistency issues still exist!")
    except Exception as e:
        print(f"💥 Test failed with error: {e}")