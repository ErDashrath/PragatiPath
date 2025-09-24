#!/usr/bin/env python3
"""
Test Level Progression System
Tests multiple correct answers to trigger level-up
"""

import urllib.request
import urllib.parse
import json

def test_level_progression():
    """Test level progression with multiple correct answers"""
    
    base_url = "http://127.0.0.1:8000/api/assessment/submit-answer"
    student_id = "fec9dc2b-f347-498e-a66f-f01a976b9cee"
    
    # Test sequence: 3+ correct answers to trigger level progression
    test_sequence = [
        {
            "question_id": "b80eda84-b166-4d1a-8029-8abe9e94ad0f",  # Level 0 question
            "answer": "x = 5",
            "description": "First correct answer (Level 0)"
        },
        {
            "question_id": "63629016-6ea3-463e-a330-0d4dd5f4b02b",  # Level 0 question  
            "answer": "12",
            "description": "Second correct answer (Level 0)"
        },
        {
            "question_id": "b80eda84-b166-4d1a-8029-8abe9e94ad0f",  # Level 0 question
            "answer": "x = 5",
            "description": "Third correct answer (should trigger level progression!)"
        }
    ]
    
    print("🎯 TESTING LEVEL PROGRESSION SYSTEM")
    print("=" * 50)
    print(f"Student ID: {student_id}")
    print(f"Goal: Get 3+ consecutive correct + BKT mastery ≥ 0.8 to unlock next level")
    print()
    
    for i, test_case in enumerate(test_sequence, 1):
        print(f"📝 Test {i}: {test_case['description']}")
        
        payload = {
            "student_id": student_id,
            "question_id": test_case["question_id"],
            "answer": test_case["answer"],
            "response_time": 5.0 + i,  # Vary response time
            "skill_id": "algebra",
            "metadata": {
                "attempt_number": i,
                "hint_used": False
            }
        }
        
        try:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                base_url,
                data=data,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                print(f"   ✅ Answer: {payload['answer']}")
                print(f"   📊 Correct: {result['was_correct']}")
                
                # Check level progression info
                if 'algorithm_results' in result and 'bkt' in result['algorithm_results']:
                    bkt_result = result['algorithm_results']['bkt']
                    if 'level_progression' in bkt_result:
                        prog = bkt_result['level_progression']
                        print(f"   🎯 Level: {prog.get('new_level', 'unchanged')}")
                        print(f"   🔥 Consecutive: {prog.get('consecutive_count', 0)}")
                        print(f"   🧠 Mastery: {bkt_result.get('new_mastery', 0.5):.3f}")
                        
                        if prog.get('level_changed'):
                            print(f"   🎉 LEVEL UP! {prog.get('congratulations_message', '')}")
                        elif prog.get('congratulations_message'):
                            print(f"   💪 Progress: {prog.get('congratulations_message', '')}")
                
                # Show level progression state
                if 'updated_student_state' in result and 'level_progression' in result['updated_student_state']:
                    level_state = result['updated_student_state']['level_progression']
                    print(f"   📚 Current Level: {level_state.get('current_level', 0)}")
                    print(f"   🔓 Unlocked Levels: {level_state.get('unlocked_levels', [])}")
                    print(f"   ⭐ Threshold: {level_state.get('mastery_threshold', 0.8)}")
                
                print()
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            print()

if __name__ == "__main__":
    test_level_progression()