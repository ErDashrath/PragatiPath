#!/usr/bin/env python3
"""
Debug BKT Update in API
Test the actual API endpoint to see what's happening to BKT values
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/simple"

def debug_bkt_updates():
    """Debug BKT updates through the API"""
    print("🔧 DEBUGGING BKT UPDATES IN API")
    print("="*60)
    
    # Create session
    test_student = {
        "student_name": "BKT_Debug_Test",
        "subject": "quantitative_aptitude",
        "question_count": 3
    }
    
    response = requests.post(f"{BASE_URL}/start-session/", json=test_student)
    session_data = response.json()
    session_id = session_data['session_id']
    
    print(f"✅ Session created: {session_id}")
    
    # Test sequence: wrong, correct, wrong
    test_sequence = [
        {"correct": False, "description": "First wrong answer"},
        {"correct": True, "description": "Then correct answer"},
        {"correct": False, "description": "Then wrong answer again"}
    ]
    
    for i, test_case in enumerate(test_sequence, 1):
        print(f"\n🔸 Step {i}: {test_case['description']}")
        
        # Get question
        response = requests.get(f"{BASE_URL}/get-question/{session_id}/")
        question_data = response.json()
        
        mastery_before = question_data['adaptive_info']['bkt_mastery']
        dkt_before = question_data['adaptive_info']['dkt_prediction']
        difficulty_before = question_data['difficulty']
        
        print(f"   📊 BEFORE - Mastery: {mastery_before:.6f}, DKT: {dkt_before:.6f}, Difficulty: {difficulty_before}")
        
        # Select answer based on test case
        if test_case['correct']:
            selected_answer = question_data['correct_answer']
        else:
            # Select wrong answer
            correct_answer = question_data['correct_answer']
            options = question_data['options']
            for option in options:
                if option['id'] != correct_answer:
                    selected_answer = option['id']
                    break
        
        print(f"   🎯 Selecting: {'✅ Correct' if test_case['correct'] else '❌ Wrong'} answer ({selected_answer})")
        
        # Submit answer
        submit_data = {
            "session_id": session_id,
            "question_id": question_data['question_id'],
            "selected_answer": selected_answer,
            "time_spent": 10.0
        }
        
        response = requests.post(f"{BASE_URL}/submit-answer/", json=submit_data)
        answer_data = response.json()
        
        # Check results
        result_correct = answer_data['answer_correct']
        knowledge_update = answer_data.get('knowledge_update', {})
        
        new_mastery = knowledge_update.get('new_mastery_level', 'ERROR')
        bkt_params_after = knowledge_update.get('bkt_params_after', {})
        
        print(f"   📊 AFTER  - Result: {'✅' if result_correct else '❌'}")
        print(f"   📊 AFTER  - New Mastery: {new_mastery}")
        
        if isinstance(bkt_params_after, dict) and 'P_L' in bkt_params_after:
            detailed_mastery = bkt_params_after['P_L']
            print(f"   📊 AFTER  - Detailed BKT P_L: {detailed_mastery:.6f}")
            
            if isinstance(mastery_before, (int, float)) and isinstance(detailed_mastery, (int, float)):
                change = detailed_mastery - mastery_before
                print(f"   📈 CHANGE - {change:+.6f}")
                
                if test_case['correct']:
                    if change > 0:
                        print(f"   ✅ CORRECT - Correct answer increased mastery")
                    else:
                        print(f"   ❌ BUG - Correct answer didn't increase mastery")
                else:
                    if change < 0:
                        print(f"   ✅ CORRECT - Wrong answer decreased mastery")
                    elif change == 0:
                        print(f"   ⚠️ ISSUE - Wrong answer didn't change mastery")
                    else:
                        print(f"   ❌ BUG - Wrong answer increased mastery")
            else:
                print(f"   ❌ ERROR - Cannot compare mastery values")
        else:
            print(f"   ❌ ERROR - No detailed BKT parameters in response")
        
        # Check if difficulty changed for next question
        if i < len(test_sequence):
            print(f"   ⏳ Waiting to see difficulty change...")

def main():
    try:
        debug_bkt_updates()
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()