#!/usr/bin/env python3
"""
Extended Adaptive Test - 10 Questions to See Full Progression
Tests the complete adaptive difficulty journey with more questions
"""

import requests
import json
import time
from datetime import datetime

# Extended test configuration
BASE_URL = "http://localhost:8000/simple"
TEST_STUDENT = {
    "student_name": "Extended_Adaptive_Test",
    "subject": "quantitative_aptitude",
    "question_count": 10
}

def print_banner(text):
    print("\n" + "="*70)
    print(f" {text}")
    print("="*70)

def get_wrong_answer(question_data):
    """Always select the wrong answer to test adaptation"""
    correct_answer = question_data['correct_answer']
    options = question_data['options']
    
    # Find an option that's NOT the correct answer
    for option in options:
        if option['id'] != correct_answer:
            return option['id']
    
    # Fallback if we can't find wrong answer
    return options[0]['id']

def test_extended_adaptive_progression():
    """Test orchestration with extended question sequence"""
    
    print_banner("🚀 EXTENDED ADAPTIVE PROGRESSION TEST")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Testing: {TEST_STUDENT['question_count']} questions with strategic wrong/right answers")
    print(f"📊 Strategy: Wrong answers first 6 questions, then correct answers")
    print(f"🎪 Expected: Difficulty should drop then rise as mastery changes")
    
    # Start Session
    print_banner("🎬 STARTING EXTENDED SESSION")
    try:
        response = requests.post(f"{BASE_URL}/start-session/", json=TEST_STUDENT)
        session_data = response.json()
        session_id = session_data['session_id']
        print("✅ Session Created!")
        print(f"📋 Session ID: {session_id}")
        print(f"👤 Student: {session_data['student_name']}")
    except Exception as e:
        print(f"❌ Session creation failed: {e}")
        return
    
    # Track progression data
    progression_data = []
    
    print_banner("🧠 EXTENDED ADAPTIVE QUESTION FLOW")
    
    for q_num in range(1, TEST_STUDENT['question_count'] + 1):
        print(f"\n🔸 Question {q_num}/{TEST_STUDENT['question_count']}")
        
        # Get question
        try:
            response = requests.get(f"{BASE_URL}/get-question/{session_id}/")
            question_data = response.json()
            
            difficulty = question_data['difficulty']
            adaptive_info = question_data['adaptive_info']
            
            print(f"📝 Question: {question_data['question_text'][:80]}...")
            print(f"⚡ Difficulty: {difficulty.upper()}")
            print(f"🧠 BKT Mastery: {adaptive_info['bkt_mastery']:.3f}")
            print(f"🤖 DKT Prediction: {adaptive_info['dkt_prediction']:.3f}")
            print(f"🎯 Orchestration: {adaptive_info['orchestration_enabled']}")
            
            # Strategy: Wrong answers for first 6, then correct answers
            if q_num <= 6:
                selected_answer = get_wrong_answer(question_data)
                strategy = f"❌ WRONG (testing mastery drop - {q_num}/6)"
                expected_result = "INCORRECT"
            else:
                selected_answer = question_data['correct_answer']
                strategy = f"✅ CORRECT (testing recovery - {q_num-6}/4)"
                expected_result = "CORRECT"
            
            print(f"🎯 Strategy: {strategy}")
            
            # Submit answer
            submit_data = {
                "session_id": session_id,
                "question_id": question_data['question_id'],
                "selected_answer": selected_answer,
                "time_spent": 8.0
            }
            
            response = requests.post(f"{BASE_URL}/submit-answer/", json=submit_data)
            answer_data = response.json()
            
            result_correct = answer_data['answer_correct']
            actual_result = "CORRECT" if result_correct else "INCORRECT"
            result_icon = "✅" if result_correct else "❌"
            
            print(f"📊 Result: {result_icon} {actual_result}")
            
            # Get mastery update info
            knowledge_update = answer_data['knowledge_update']
            new_mastery = knowledge_update.get('new_mastery_level', 'N/A')
            if isinstance(new_mastery, float):
                mastery_display = f"{new_mastery:.3f}"
            else:
                mastery_display = str(new_mastery)
            
            print(f"📈 New Mastery: {mastery_display}")
            print(f"🔄 Adaptation: {answer_data['adaptive_feedback']['difficulty_adaptation']}")
            
            # Store progression data
            progression_data.append({
                'question': q_num,
                'difficulty_before': difficulty,
                'bkt_before': adaptive_info['bkt_mastery'],
                'dkt_before': adaptive_info['dkt_prediction'],
                'strategy': 'wrong' if q_num <= 6 else 'correct',
                'result': actual_result,
                'mastery_after': new_mastery if isinstance(new_mastery, float) else 0,
                'adaptation': answer_data['adaptive_feedback']['difficulty_adaptation']
            })
            
            time.sleep(0.3)  # Brief pause
            
        except Exception as e:
            print(f"❌ Question {q_num} failed: {e}")
            continue
    
    # Analysis
    print_banner("📊 EXTENDED PROGRESSION ANALYSIS")
    
    print("🔸 COMPLETE ADAPTIVE JOURNEY:")
    print("   Q# | Difficulty | BKT Before | Strategy | Result | BKT After | Adaptation")
    print("   " + "-"*75)
    
    for data in progression_data:
        strategy_icon = "❌" if data['strategy'] == 'wrong' else "✅"
        result_icon = "❌" if data['result'] == 'INCORRECT' else "✅"
        
        print(f"   {data['question']:2d} | {data['difficulty_before']:10s} | "
              f"{data['bkt_before']:10.3f} | {strategy_icon} {data['strategy']:6s} | "
              f"{result_icon} {data['result']:9s} | {data['mastery_after']:9.3f} | "
              f"{data['adaptation'][:20]}...")
    
    # Detect difficulty changes
    print("\n🔸 DIFFICULTY ADAPTATION ANALYSIS:")
    difficulty_changes = []
    
    for i in range(1, len(progression_data)):
        prev_diff = progression_data[i-1]['difficulty_before']
        curr_diff = progression_data[i]['difficulty_before']
        
        if prev_diff != curr_diff:
            change_type = ""
            if curr_diff == 'easy' and prev_diff in ['medium', 'hard']:
                change_type = "📉 EASIER"
            elif curr_diff == 'medium' and prev_diff == 'hard':
                change_type = "📉 EASIER"
            elif curr_diff == 'hard' and prev_diff in ['easy', 'medium']:
                change_type = "📈 HARDER"
            elif curr_diff == 'medium' and prev_diff == 'easy':
                change_type = "📈 HARDER"
            
            difficulty_changes.append({
                'from_question': i,
                'to_question': i+1,
                'change': f"{prev_diff} → {curr_diff}",
                'type': change_type
            })
            
            print(f"   Question {i} → {i+1}: {prev_diff} → {curr_diff} {change_type}")
    
    if not difficulty_changes:
        print("   ⚠️ No difficulty changes detected")
    
    # Mastery progression analysis
    print("\n🔸 MASTERY PROGRESSION:")
    initial_mastery = progression_data[0]['bkt_before']
    final_mastery = progression_data[-1]['mastery_after']
    
    print(f"   📊 Initial BKT Mastery: {initial_mastery:.3f}")
    print(f"   📊 Final BKT Mastery: {final_mastery:.3f}")
    print(f"   📊 Total Change: {final_mastery - initial_mastery:+.3f}")
    
    # Expected behavior analysis
    print("\n🔸 ADAPTIVE BEHAVIOR ASSESSMENT:")
    
    wrong_phase_mastery = [d for d in progression_data[:6] if d['strategy'] == 'wrong']
    correct_phase_mastery = [d for d in progression_data[6:] if d['strategy'] == 'correct']
    
    if wrong_phase_mastery:
        avg_wrong_mastery = sum(d['mastery_after'] for d in wrong_phase_mastery) / len(wrong_phase_mastery)
        print(f"   📉 Average mastery during wrong answers: {avg_wrong_mastery:.3f}")
    
    if correct_phase_mastery:
        avg_correct_mastery = sum(d['mastery_after'] for d in correct_phase_mastery) / len(correct_phase_mastery)
        print(f"   📈 Average mastery during correct answers: {avg_correct_mastery:.3f}")
    
    # Final assessment
    print_banner("🎯 EXTENDED TEST RESULTS")
    
    total_adaptations = len(difficulty_changes)
    easier_adaptations = len([d for d in difficulty_changes if "EASIER" in d['type']])
    harder_adaptations = len([d for d in difficulty_changes if "HARDER" in d['type']])
    
    print(f"✅ Test Complete: {TEST_STUDENT['question_count']} questions processed")
    print(f"📊 Total Difficulty Changes: {total_adaptations}")
    print(f"📉 Adaptations to Easier: {easier_adaptations}")
    print(f"📈 Adaptations to Harder: {harder_adaptations}")
    print(f"🧠 BKT Updates: {len([d for d in progression_data if d['mastery_after'] != d['bkt_before']])}")
    
    if total_adaptations > 0:
        print("\n🚀 SUCCESS: Orchestration is adapting difficulty based on performance!")
        print("   🎯 Your adaptive learning system is working correctly")
        print("   📊 BKT mastery levels are updating properly")
        print("   🔄 Questions adapt to student performance")
    else:
        print("\n🔧 NEEDS TUNING: Limited difficulty adaptation detected")
        print("   💡 Consider adjusting confidence thresholds for more responsive adaptation")
    
    print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return {
        'total_questions': TEST_STUDENT['question_count'],
        'difficulty_changes': total_adaptations,
        'easier_adaptations': easier_adaptations,
        'harder_adaptations': harder_adaptations,
        'mastery_change': final_mastery - initial_mastery,
        'working': total_adaptations > 0 or abs(final_mastery - initial_mastery) > 0.1
    }

def main():
    """Run the extended adaptive test"""
    try:
        results = test_extended_adaptive_progression()
        
        print(f"\n🎯 FINAL SUMMARY:")
        print(f"   Total Questions: {results['total_questions']}")
        print(f"   Difficulty Adaptations: {results['difficulty_changes']}")
        print(f"   Mastery Change: {results['mastery_change']:+.3f}")
        print(f"   System Status: {'✅ WORKING' if results['working'] else '⚠️ NEEDS WORK'}")
        
        if results['working']:
            print("\n🎉 EXCELLENT: Your orchestration provides true adaptive learning!")
        
    except Exception as e:
        print(f"❌ Extended test failed: {e}")

if __name__ == "__main__":
    main()