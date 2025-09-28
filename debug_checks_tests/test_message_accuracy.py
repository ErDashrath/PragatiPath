#!/usr/bin/env python3
"""
Test Improved Messaging System
Tests whether the feedback messages now correctly match the actual behavior
"""

import requests
import json
import time
from datetime import datetime
import random
import string

def generate_unique_username():
    """Generate a unique username"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_suffix = ''.join(random.choices(string.ascii_lowercase, k=3))
    return f"msg_test_{timestamp}_{random_suffix}"

BASE_URL = "http://localhost:8000/simple"

def test_message_accuracy():
    """Test if messages match actual behavior"""
    
    print("📢 MESSAGE ACCURACY TEST")
    print("="*50)
    
    # Create fresh user
    unique_username = generate_unique_username()
    test_student = {
        "student_name": unique_username,
        "subject": "quantitative_aptitude",
        "question_count": 10
    }
    
    response = requests.post(f"{BASE_URL}/start-session/", json=test_student)
    session_data = response.json()
    session_id = session_data['session_id']
    
    print(f"👤 Testing with: {unique_username}")
    print(f"📋 Session: {session_id}")
    
    # Test scenarios: wrong, correct, wrong, correct, correct
    test_scenarios = [
        {"answer": "wrong", "description": "Low mastery wrong answer"},
        {"answer": "correct", "description": "First correct answer (should boost)"},
        {"answer": "wrong", "description": "Medium mastery wrong answer"},
        {"answer": "correct", "description": "Building confidence"},
        {"answer": "correct", "description": "Getting to high mastery"},
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🔸 Test {i}: {scenario['description']}")
        
        # Get question
        response = requests.get(f"{BASE_URL}/get-question/{session_id}/")
        question_data = response.json()
        
        mastery_before = question_data['adaptive_info']['bkt_mastery']
        difficulty_before = question_data['difficulty']
        
        print(f"   📊 BEFORE: Mastery={mastery_before:.4f}, Difficulty={difficulty_before}")
        
        # Select answer based on scenario
        if scenario['answer'] == 'correct':
            selected_answer = question_data['correct_answer']
            expected_behavior = "Mastery should INCREASE, message should be encouraging"
        else:
            # Select wrong answer
            correct_answer = question_data['correct_answer']
            options = question_data['options']
            for option in options:
                if option['id'] != correct_answer:
                    selected_answer = option['id']
                    break
            expected_behavior = "Mastery might increase (low level) or decrease (high level), message should be supportive"
        
        print(f"   🎯 Action: {scenario['answer'].upper()} answer")
        print(f"   🤔 Expected: {expected_behavior}")
        
        # Submit answer
        submit_data = {
            "session_id": session_id,
            "question_id": question_data['question_id'],
            "selected_answer": selected_answer,
            "time_spent": 8.0
        }
        
        response = requests.post(f"{BASE_URL}/submit-answer/", json=submit_data)
        answer_data = response.json()
        
        # Analyze response
        result_correct = answer_data['answer_correct']
        knowledge_update = answer_data.get('knowledge_update', {})
        mastery_after = knowledge_update.get('new_mastery_level', mastery_before)
        
        adaptive_feedback = answer_data.get('adaptive_feedback', {})
        difficulty_adaptation = adaptive_feedback.get('difficulty_adaptation', 'No message')
        adaptation_message = adaptive_feedback.get('adaptation_message', 'No message')
        
        mastery_change = mastery_after - mastery_before if isinstance(mastery_after, (int, float)) else 0
        
        print(f"   📊 AFTER:  Mastery={mastery_after:.4f} (change: {mastery_change:+.4f})")
        print(f"   📢 System Message: \"{difficulty_adaptation}\"")
        print(f"   💬 Full Message: \"{adaptation_message}\"")
        
        # Evaluate message accuracy
        if scenario['answer'] == 'correct':
            if mastery_change > 0 and ("HARDER" in difficulty_adaptation.upper() or "GOOD" in adaptation_message.upper() or "GREAT" in adaptation_message.upper()):
                print(f"   ✅ ACCURATE: Positive result → encouraging message")
            elif mastery_change > 0:
                print(f"   ⚠️ NEEDS WORK: Positive result but neutral message")
            else:
                print(f"   ❌ ISSUE: Correct answer didn't increase mastery")
        else:  # wrong answer
            if mastery_change < 0 and ("EASIER" in difficulty_adaptation.upper() or "practice" in adaptation_message.lower()):
                print(f"   ✅ ACCURATE: Mastery drop → supportive easier message")
            elif mastery_change > 0 and ("confidence" in adaptation_message.lower() or "build" in adaptation_message.lower()):
                print(f"   ✅ ACCURATE: Learning effect → confidence building message")
            elif mastery_change == 0 and ("current" in difficulty_adaptation.lower() or "level" in adaptation_message.lower()):
                print(f"   ✅ ACCURATE: No change → maintain level message")
            else:
                print(f"   ⚠️ CHECK: Wrong answer behavior needs review")
        
        time.sleep(1)
    
    print(f"\n✅ Message accuracy test completed!")
    print(f"💡 Messages should now better reflect actual adaptive behavior")

def main():
    try:
        test_message_accuracy()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()