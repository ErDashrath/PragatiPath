#!/usr/bin/env python
"""
Final verification that the history API fix is working
"""
import requests
import json

def verify_history_fix():
    print("✅ Verifying History API Data Consistency Fix")
    print("=" * 50)
    
    username = "student_history_test_user"
    
    # Get history
    print("1. Getting session history...")
    history_resp = requests.get(f"http://localhost:8000/history/student/{username}/")
    
    if history_resp.status_code != 200:
        print(f"❌ History API failed: {history_resp.status_code}")
        return
        
    history_data = history_resp.json()
    sessions = history_data.get('adaptive_sessions', [])
    
    if not sessions:
        print("❌ No sessions found")
        return
        
    # Check the most recent session (our test session)
    recent_session = sessions[0]  # Should be most recent
    session_id = recent_session['session_id']
    
    print(f"📊 Recent Session History Results:")
    print(f"   Session ID: {session_id[:8]}...")
    print(f"   Questions Attempted: {recent_session['questions_attempted']}")
    print(f"   Questions Correct: {recent_session['questions_correct']}")
    print(f"   Accuracy: {recent_session['accuracy_percentage']}%")
    
    # Now test detailed view
    print(f"\n2. Getting detailed session view...")
    details_resp = requests.get(f"http://localhost:8000/history/session-details/{session_id}/")
    
    if details_resp.status_code != 200:
        print(f"❌ Details API failed: {details_resp.status_code}")
        return
        
    details_data = details_resp.json()
    
    if not details_data.get('success'):
        print(f"❌ Details API error: {details_data.get('error')}")
        return
        
    session_details = details_data['session_details']
    
    print(f"📋 Detailed Session Results:")
    print(f"   Questions Attempted: {session_details['questions_attempted']}")
    print(f"   Questions Correct: {session_details['questions_correct']}")
    print(f"   Accuracy: {session_details['accuracy_percentage']}%")
    print(f"   Question Attempts: {len(session_details['question_attempts'])}")
    
    # Show question breakdown
    attempts = session_details['question_attempts']
    correct_count = sum(1 for attempt in attempts if attempt['is_correct'])
    
    print(f"\n📝 Question-by-Question Breakdown:")
    for i, attempt in enumerate(attempts, 1):
        status = "✅" if attempt['is_correct'] else "❌"
        print(f"   Q{i}: {status} (answered: {attempt['student_answer']}, time: {attempt['time_spent']}s)")
    
    # Verify consistency
    history_correct = recent_session['questions_correct']
    history_total = recent_session['questions_attempted']
    details_correct = session_details['questions_correct']
    details_total = session_details['questions_attempted']
    actual_correct = correct_count
    actual_total = len(attempts)
    
    print(f"\n🔍 Data Consistency Verification:")
    print(f"   History API:    {history_correct}/{history_total} correct")
    print(f"   Details API:    {details_correct}/{details_total} correct")
    print(f"   Actual Count:   {actual_correct}/{actual_total} correct")
    
    # Check if all match
    all_consistent = (
        history_correct == details_correct == actual_correct and
        history_total == details_total == actual_total
    )
    
    if all_consistent:
        print(f"\n🎉 SUCCESS! Data Consistency Fix is Working Perfectly!")
        print(f"   ✅ All APIs return consistent data")
        print(f"   ✅ Statistics calculated from actual question attempts")
        print(f"   ✅ History view shows accurate results")
        print(f"   ✅ Detailed view shows accurate results")
    else:
        print(f"\n❌ Data inconsistency detected:")
        if history_correct != details_correct:
            print(f"   History vs Details mismatch: {history_correct} vs {details_correct}")
        if actual_correct != details_correct:
            print(f"   Details vs Actual mismatch: {details_correct} vs {actual_correct}")

if __name__ == "__main__":
    verify_history_fix()