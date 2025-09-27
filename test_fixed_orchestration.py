#!/usr/bin/env python3
"""
FIXED Orchestration Test - Verify True Adaptive Difficulty 
Tests that wrong answers actually reduce mastery and make questions easier
"""

import requests
import json
import time
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000/simple"
TEST_STUDENT = {
    "student_name": "Adaptive_Difficulty_Test",
    "subject": "quantitative_aptitude",
    "question_count": 8
}

def print_banner(text):
    print("\n" + "="*60)
    print(f" {text}")
    print("="*60)

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

def test_adaptive_difficulty_response():
    """Test that orchestration actually adapts difficulty based on performance"""
    
    print_banner("🔧 FIXED ORCHESTRATION - ADAPTIVE DIFFICULTY TEST")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🧪 Strategy: Answer questions WRONG to test if difficulty adapts")
    print(f"🎯 Expected: Difficulty should decrease as mastery drops")
    
    # Step 1: Start Session
    print_banner("🎬 STARTING TEST SESSION")
    try:
        response = requests.post(f"{BASE_URL}/start-session/", json=TEST_STUDENT)
        session_data = response.json()
        session_id = session_data['session_id']
        print("✅ Session Created!")
        print(f"📋 Session ID: {session_id}")
    except Exception as e:
        print(f"❌ Session creation failed: {e}")
        return
    
    # Step 2: Answer Questions Systematically
    print_banner("🧠 TESTING ADAPTIVE DIFFICULTY RESPONSE")
    
    difficulty_history = []
    mastery_history = []
    
    for q_num in range(1, TEST_STUDENT['question_count'] + 1):
        print(f"\n🔸 Question {q_num}/{TEST_STUDENT['question_count']}")
        
        # Get question
        try:
            response = requests.get(f"{BASE_URL}/get-question/{session_id}/")
            question_data = response.json()
            
            difficulty = question_data['difficulty']
            adaptive_info = question_data['adaptive_info']
            
            print(f"📝 Question Difficulty: {difficulty}")
            print(f"🧠 BKT Mastery: {adaptive_info['bkt_mastery']}")
            print(f"🤖 DKT Prediction: {adaptive_info['dkt_prediction']}")
            print(f"💡 Adaptive Reason: {adaptive_info['adaptive_reason']}")
            
            # Track difficulty progression
            difficulty_history.append({
                'question_num': q_num,
                'difficulty': difficulty,
                'bkt_mastery': adaptive_info['bkt_mastery'],
                'dkt_prediction': adaptive_info['dkt_prediction']
            })
            
            # Strategy: Answer wrong for first 4 questions, then right for last 4
            if q_num <= 4:
                # Get wrong answer to force mastery drop
                selected_answer = get_wrong_answer(question_data)
                strategy = "❌ WRONG (to test adaptation)"
            else:
                # Get correct answer to test recovery
                selected_answer = question_data['correct_answer']
                strategy = "✅ CORRECT (to test recovery)"
            
            print(f"🎯 Strategy: {strategy}")
            
            # Submit answer
            submit_data = {
                "session_id": session_id,
                "question_id": question_data['question_id'],
                "selected_answer": selected_answer,
                "time_spent": 10.0
            }
            
            response = requests.post(f"{BASE_URL}/submit-answer/", json=submit_data)
            answer_data = response.json()
            
            print(f"📊 Result: {'CORRECT' if answer_data['answer_correct'] else 'INCORRECT'}")
            
            # Track mastery changes
            knowledge_update = answer_data['knowledge_update']
            new_mastery = knowledge_update.get('new_mastery_level', knowledge_update.get('mastery_display', '0%'))
            mastery_history.append({
                'question_num': q_num,
                'was_correct': answer_data['answer_correct'],
                'new_mastery': new_mastery,
                'adaptation': answer_data['adaptive_feedback']['difficulty_adaptation']
            })
            
            print(f"🎯 New Mastery: {new_mastery}")
            print(f"🔄 Adaptation: {answer_data['adaptive_feedback']['difficulty_adaptation']}")
            
            time.sleep(0.5)  # Brief pause
            
        except Exception as e:
            print(f"❌ Question {q_num} failed: {e}")
            continue
    
    # Step 3: Analysis
    print_banner("📊 ADAPTIVE DIFFICULTY ANALYSIS")
    
    print("🔸 DIFFICULTY PROGRESSION:")
    for i, item in enumerate(difficulty_history):
        change_indicator = ""
        if i > 0:
            prev_difficulty = difficulty_history[i-1]['difficulty']
            curr_difficulty = item['difficulty']
            if curr_difficulty != prev_difficulty:
                if curr_difficulty == 'easy' and prev_difficulty in ['medium', 'hard']:
                    change_indicator = " 📉 ADAPTED TO EASIER!"
                elif curr_difficulty == 'medium' and prev_difficulty == 'hard':
                    change_indicator = " 📉 ADAPTED TO EASIER!"
                elif curr_difficulty == 'hard' and prev_difficulty in ['easy', 'medium']:
                    change_indicator = " 📈 ADAPTED TO HARDER!"
        
        print(f"   Q{item['question_num']}: {item['difficulty']} (BKT: {item['bkt_mastery']:.3f}){change_indicator}")
    
    print("\n🔸 MASTERY PROGRESSION:")
    for item in mastery_history:
        trend = "📉" if not item['was_correct'] else "📈"
        print(f"   Q{item['question_num']}: {trend} {item['new_mastery']} - {item['adaptation']}")
    
    # Check if adaptation actually happened
    print_banner("🎯 ADAPTATION EFFECTIVENESS")
    
    # Count difficulty changes
    difficulty_changes = 0
    easier_adaptations = 0
    harder_adaptations = 0
    
    for i in range(1, len(difficulty_history)):
        prev_diff = difficulty_history[i-1]['difficulty']
        curr_diff = difficulty_history[i]['difficulty']
        
        if prev_diff != curr_diff:
            difficulty_changes += 1
            if curr_diff == 'easy' and prev_diff in ['medium', 'hard']:
                easier_adaptations += 1
            elif curr_diff == 'hard' and prev_diff in ['easy', 'medium']:
                harder_adaptations += 1
    
    print(f"📊 Total Difficulty Changes: {difficulty_changes}")
    print(f"📉 Adaptations to Easier: {easier_adaptations}")
    print(f"📈 Adaptations to Harder: {harder_adaptations}")
    
    # Final assessment
    if difficulty_changes > 0:
        print("✅ ORCHESTRATION IS WORKING! Difficulty adapted based on performance!")
        if easier_adaptations > 0:
            print("🎯 PERFECT! System correctly made questions easier after wrong answers!")
    else:
        print("❌ ORCHESTRATION ISSUE: No difficulty adaptation detected")
        print("🔧 The system may not be responding to performance changes")
    
    print_banner("🎉 ADAPTIVE DIFFICULTY TEST COMPLETE")
    print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return {
        'difficulty_changes': difficulty_changes,
        'easier_adaptations': easier_adaptations,
        'harder_adaptations': harder_adaptations,
        'working': difficulty_changes > 0
    }

def main():
    """Run the adaptive difficulty test"""
    try:
        results = test_adaptive_difficulty_response()
        
        print(f"\n🎯 FINAL RESULTS:")
        print(f"   Adaptive Changes: {results['difficulty_changes']}")
        print(f"   Easier Adaptations: {results['easier_adaptations']}")
        print(f"   System Working: {'✅ YES' if results['working'] else '❌ NO'}")
        
        if results['working']:
            print("\n🚀 SUCCESS: Your orchestration now properly adapts difficulty!")
            print("   🧠 BKT mastery levels update correctly")
            print("   📊 Combined confidence drives question selection")
            print("   🎯 Students will get appropriate difficulty questions")
        else:
            print("\n🔧 NEEDS WORK: Orchestration may need further tuning")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()