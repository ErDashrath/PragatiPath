#!/usr/bin/env python3
"""
Test Wrong Answers Mastery Drop
This test specifically focuses on showing how wrong answers decrease mastery
and how the system adapts difficulty downward in response.
"""

import requests
import json
import time
from datetime import datetime

# Test configuration for mastery drop testing
BASE_URL = "http://localhost:8000/simple"
TEST_STUDENT = {
    "student_name": "Mastery_Drop_Test",
    "subject": "quantitative_aptitude",
    "question_count": 8
}

def print_banner(text):
    print("\n" + "="*70)
    print(f" {text}")
    print("="*70)

def get_wrong_answer(question_data):
    """Always select the wrong answer to test mastery drop"""
    correct_answer = question_data['correct_answer']
    options = question_data['options']
    
    # Find an option that's NOT the correct answer
    for option in options:
        if option['id'] != correct_answer:
            return option['id']
    
    # Fallback
    return options[0]['id']

def test_mastery_drop_and_difficulty_adaptation():
    """Test how wrong answers decrease mastery and adapt difficulty"""
    
    print_banner("📉 MASTERY DROP & DIFFICULTY ADAPTATION TEST")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Strategy: Give ONLY wrong answers to test mastery drop")
    print(f"📊 Expected Behavior:")
    print(f"   • BKT mastery should DECREASE with each wrong answer")
    print(f"   • Difficulty should adapt DOWNWARD as mastery drops")
    print(f"   • System should recognize struggling student")
    
    # Start Session
    print_banner("🎬 STARTING MASTERY DROP SESSION")
    try:
        response = requests.post(f"{BASE_URL}/start-session/", json=TEST_STUDENT)
        session_data = response.json()
        session_id = session_data['session_id']
        print("✅ Session Created!")
        print(f"📋 Session ID: {session_id}")
        print(f"👤 Student: {session_data['student_name']}")
        print(f"🧠 Initial Setup Complete")
    except Exception as e:
        print(f"❌ Session creation failed: {e}")
        return
    
    # Track mastery progression
    mastery_progression = []
    difficulty_progression = []
    
    print_banner("❌ WRONG ANSWERS SEQUENCE")
    print("Strategy: Answer every question incorrectly to force mastery drop")
    print("Expected: Mastery probability should decrease, difficulty should adapt down")
    
    for q_num in range(1, TEST_STUDENT['question_count'] + 1):
        print(f"\n🔸 Question {q_num}/{TEST_STUDENT['question_count']} - WRONG ANSWER TEST")
        
        # Get question
        try:
            response = requests.get(f"{BASE_URL}/get-question/{session_id}/")
            question_data = response.json()
            
            difficulty = question_data['difficulty']
            adaptive_info = question_data['adaptive_info']
            current_mastery = adaptive_info['bkt_mastery']
            
            print(f"📝 Question: {question_data['question_text'][:60]}...")
            print(f"⚡ Current Difficulty: {difficulty.upper()}")
            print(f"🧠 BKT Mastery BEFORE: {current_mastery:.3f}")
            print(f"🎯 Orchestration Active: {adaptive_info['orchestration_enabled']}")
            
            # Store pre-answer state
            mastery_progression.append({
                'question': q_num,
                'mastery_before': current_mastery,
                'difficulty_before': difficulty
            })
            difficulty_progression.append(difficulty)
            
            # ALWAYS select wrong answer
            wrong_answer = get_wrong_answer(question_data)
            correct_answer = question_data['correct_answer']
            
            print(f"🔍 Correct Answer: {correct_answer}")
            print(f"❌ Selected (Wrong): {wrong_answer}")
            print(f"🧪 Testing: How does BKT respond to wrong answer?")
            
            # Submit wrong answer
            submit_data = {
                "session_id": session_id,
                "question_id": question_data['question_id'],
                "selected_answer": wrong_answer,
                "time_spent": 12.0
            }
            
            response = requests.post(f"{BASE_URL}/submit-answer/", json=submit_data)
            answer_data = response.json()
            
            # Check result
            result_correct = answer_data['answer_correct']
            result_icon = "✅" if result_correct else "❌"
            actual_result = "CORRECT" if result_correct else "INCORRECT"
            
            if result_correct:
                print(f"⚠️ UNEXPECTED: Answer marked correct! Check question logic")
            else:
                print(f"✅ EXPECTED: {result_icon} Answer marked as INCORRECT")
            
            # Get updated mastery
            knowledge_update = answer_data['knowledge_update']
            new_mastery = knowledge_update.get('new_mastery_level', 'N/A')
            
            if isinstance(new_mastery, float):
                mastery_change = new_mastery - current_mastery
                change_direction = "📉 DECREASED" if mastery_change < 0 else "📈 INCREASED" if mastery_change > 0 else "➡️ UNCHANGED"
                
                print(f"🧠 BKT Mastery AFTER: {new_mastery:.3f}")
                print(f"📊 Mastery Change: {mastery_change:+.3f} ({change_direction})")
                
                # Update progression tracking
                mastery_progression[-1]['mastery_after'] = new_mastery
                mastery_progression[-1]['mastery_change'] = mastery_change
                
                # Analyze adaptation
                adaptation_msg = answer_data['adaptive_feedback']['difficulty_adaptation']
                adaptation_full = answer_data['adaptive_feedback']['adaptation_message']
                
                print(f"🔄 System Adaptation: {adaptation_msg}")
                print(f"💬 Message: {adaptation_full}")
                
                # Check if mastery is dropping as expected
                if mastery_change < 0:
                    print("✅ CORRECT BEHAVIOR: Wrong answer decreased mastery (BKT working!)")
                elif mastery_change == 0:
                    print("⚠️ UNEXPECTED: Mastery unchanged despite wrong answer")
                else:
                    print("❌ ERROR: Mastery increased despite wrong answer!")
                    
            else:
                print(f"❌ ERROR: Could not get updated mastery: {new_mastery}")
            
            time.sleep(0.4)  # Pause for readability
            
        except Exception as e:
            print(f"❌ Question {q_num} failed: {e}")
            continue
    
    # Analysis Phase
    print_banner("📊 MASTERY DROP ANALYSIS")
    
    print("🔸 MASTERY PROGRESSION THROUGH WRONG ANSWERS:")
    print("   Q# | Difficulty | Mastery Before | Mastery After | Change   | Status")
    print("   " + "-"*75)
    
    total_mastery_drop = 0
    drops_detected = 0
    
    for data in mastery_progression:
        if 'mastery_after' in data:
            change = data['mastery_change']
            status = "📉 DROP" if change < 0 else "📈 RISE" if change > 0 else "➡️ SAME"
            
            if change < 0:
                drops_detected += 1
                total_mastery_drop += abs(change)
            
            print(f"   {data['question']:2d} | {data['difficulty_before']:10s} | "
                  f"{data['mastery_before']:13.3f} | {data['mastery_after']:12.3f} | "
                  f"{change:+8.3f} | {status}")
        else:
            print(f"   {data['question']:2d} | {data['difficulty_before']:10s} | "
                  f"{data['mastery_before']:13.3f} | {'ERROR':>12s} | {'N/A':>8s} | ❌ FAILED")
    
    # Difficulty adaptation analysis
    print("\n🔸 DIFFICULTY ADAPTATION ANALYSIS:")
    
    difficulty_levels = {'easy': 1, 'medium': 2, 'hard': 3}
    difficulty_changes = []
    
    for i in range(1, len(difficulty_progression)):
        prev_level = difficulty_levels.get(difficulty_progression[i-1], 2)
        curr_level = difficulty_levels.get(difficulty_progression[i], 2)
        
        if curr_level != prev_level:
            change_type = "📉 EASIER" if curr_level < prev_level else "📈 HARDER"
            difficulty_changes.append({
                'from_question': i,
                'to_question': i+1,
                'change': f"{difficulty_progression[i-1]} → {difficulty_progression[i]}",
                'type': change_type
            })
    
    if difficulty_changes:
        print("   Detected difficulty adaptations:")
        for change in difficulty_changes:
            print(f"     Question {change['from_question']} → {change['to_question']}: "
                  f"{change['change']} {change['type']}")
    else:
        print("   ⚠️ No difficulty changes detected")
    
    # Final Assessment
    print_banner("🎯 MASTERY DROP TEST RESULTS")
    
    initial_mastery = mastery_progression[0]['mastery_before'] if mastery_progression else 0
    final_mastery = mastery_progression[-1].get('mastery_after', initial_mastery) if mastery_progression else 0
    overall_change = final_mastery - initial_mastery
    
    print(f"📊 Initial Mastery: {initial_mastery:.3f}")
    print(f"📊 Final Mastery: {final_mastery:.3f}")
    print(f"📊 Overall Change: {overall_change:+.3f}")
    print(f"📊 Questions with Mastery Drop: {drops_detected}/{len(mastery_progression)}")
    print(f"📊 Total Mastery Lost: {total_mastery_drop:.3f}")
    print(f"📊 Difficulty Adaptations: {len(difficulty_changes)}")
    
    # Behavior Assessment
    print("\n🔸 BKT BEHAVIOR ASSESSMENT:")
    
    if drops_detected >= len(mastery_progression) * 0.7:  # 70% of questions should show drops
        print("✅ EXCELLENT: BKT correctly decreases mastery for wrong answers")
    elif drops_detected > 0:
        print("⚠️ PARTIAL: Some mastery drops detected, but not consistent")
    else:
        print("❌ ERROR: No mastery drops detected despite wrong answers")
    
    print("\n🔸 DIFFICULTY ADAPTATION ASSESSMENT:")
    
    easier_adaptations = len([c for c in difficulty_changes if "EASIER" in c['type']])
    if easier_adaptations > 0:
        print("✅ EXCELLENT: System adapts difficulty easier for struggling student")
    elif len(difficulty_changes) > 0:
        print("⚠️ PARTIAL: Some difficulty changes, but not necessarily easier")
    else:
        print("⚠️ LIMITED: No difficulty adaptations detected")
    
    # Success Criteria
    print_banner("🏆 SUCCESS CRITERIA EVALUATION")
    
    mastery_drops_working = drops_detected >= len(mastery_progression) * 0.5
    difficulty_adapts_down = easier_adaptations > 0
    overall_mastery_decreased = overall_change < -0.05  # At least 5% drop
    
    print(f"✅ Mastery Drops on Wrong Answers: {'PASS' if mastery_drops_working else 'FAIL'}")
    print(f"✅ Difficulty Adapts Downward: {'PASS' if difficulty_adapts_down else 'FAIL'}")
    print(f"✅ Overall Mastery Decreased: {'PASS' if overall_mastery_decreased else 'FAIL'}")
    
    if mastery_drops_working and difficulty_adapts_down:
        print("\n🎉 SUCCESS: Your BKT system correctly handles wrong answers!")
        print("   📉 Mastery decreases when students struggle")
        print("   🔄 Difficulty adapts to support struggling learners")
        print("   🧠 Adaptive learning is working as intended")
    elif mastery_drops_working:
        print("\n⚠️ PARTIAL SUCCESS: BKT mastery tracking works")
        print("   📉 Mastery decreases correctly")
        print("   🔧 Difficulty adaptation could be more responsive")
    else:
        print("\n❌ NEEDS WORK: BKT may not be responding to wrong answers")
        print("   🔧 Check BKT update logic and parameter tuning")
    
    print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return {
        'mastery_drops_detected': drops_detected,
        'total_questions': len(mastery_progression),
        'difficulty_changes': len(difficulty_changes),
        'easier_adaptations': easier_adaptations,
        'overall_mastery_change': overall_change,
        'bkt_working': mastery_drops_working,
        'adaptation_working': difficulty_adapts_down
    }

def main():
    """Run the mastery drop test"""
    try:
        results = test_mastery_drop_and_difficulty_adaptation()
        
        print(f"\n🎯 FINAL SUMMARY:")
        print(f"   Wrong Answers Given: {results['total_questions']}")
        print(f"   Mastery Drops Detected: {results['mastery_drops_detected']}")
        print(f"   Difficulty Adaptations: {results['difficulty_changes']}")
        print(f"   Easier Adaptations: {results['easier_adaptations']}")
        print(f"   Overall Mastery Change: {results['overall_mastery_change']:+.3f}")
        
        if results['bkt_working'] and results['adaptation_working']:
            print("\n🏆 PERFECT: BKT mastery drops work and difficulty adapts down!")
        elif results['bkt_working']:
            print("\n⚠️ BKT mastery tracking works, difficulty adaptation needs tuning")
        else:
            print("\n🔧 System needs debugging - check BKT update logic")
        
    except Exception as e:
        print(f"❌ Mastery drop test failed: {e}")

if __name__ == "__main__":
    main()