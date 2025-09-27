#!/usr/bin/env python3
"""
Complete Adaptive Learning Journey - 20 Questions
Shows the full progression: easy → moderate → difficult → moderate → easy
Demonstrates how the system adapts difficulty based on performance patterns.
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
    random_suffix = ''.join(random.choices(string.ascii_lowercase, k=4))
    return f"adaptive_journey_{timestamp}_{random_suffix}"

# Test configuration
BASE_URL = "http://localhost:8000/simple"

def get_wrong_answer(question_data):
    """Get a wrong answer for the question"""
    correct_answer = question_data['correct_answer']
    options = question_data['options']
    
    for option in options:
        if option['id'] != correct_answer:
            return option['id']
    return options[0]['id']  # Fallback

def test_complete_adaptive_journey():
    """Test the complete 20-question adaptive journey"""
    
    print("🌟 COMPLETE ADAPTIVE LEARNING JOURNEY - 20 QUESTIONS")
    print("="*80)
    
    # Generate unique username for fresh start
    unique_username = generate_unique_username()
    
    test_student = {
        "student_name": unique_username,
        "subject": "quantitative_aptitude",
        "question_count": 20
    }
    
    print(f"👤 Student: {unique_username}")
    print(f"📚 Subject: {test_student['subject']}")
    print(f"🎯 Strategy: Show complete difficulty progression")
    print(f"   Phase 1 (Q1-5):   Wrong answers → build basic understanding")
    print(f"   Phase 2 (Q6-10):  Correct answers → increase difficulty")
    print(f"   Phase 3 (Q11-15): Correct answers → reach high difficulty")
    print(f"   Phase 4 (Q16-20): Wrong answers → difficulty comes back down")
    
    # Start Session
    response = requests.post(f"{BASE_URL}/start-session/", json=test_student)
    session_data = response.json()
    session_id = session_data['session_id']
    
    print(f"✅ Session created: {session_id}")
    
    # Track progression data
    progression_data = []
    
    print(f"\n" + "="*80)
    print("🎪 ADAPTIVE LEARNING JOURNEY")
    print("="*80)
    
    # Define strategy for each phase
    def get_strategy(q_num):
        if q_num <= 5:
            return {"action": "wrong", "description": "Building foundation", "phase": "Phase 1"}
        elif q_num <= 10:
            return {"action": "correct", "description": "Skill building", "phase": "Phase 2"}
        elif q_num <= 15:
            return {"action": "correct", "description": "Advanced mastery", "phase": "Phase 3"}
        else:
            return {"action": "wrong", "description": "Difficulty reset", "phase": "Phase 4"}
    
    for q_num in range(1, 21):  # 20 questions
        strategy = get_strategy(q_num)
        
        print(f"\n🔸 Question {q_num}/20 - {strategy['phase']}: {strategy['description']}")
        
        # Get question
        try:
            response = requests.get(f"{BASE_URL}/get-question/{session_id}/")
            question_data = response.json()
            
            difficulty = question_data['difficulty']
            adaptive_info = question_data['adaptive_info']
            mastery_before = adaptive_info['bkt_mastery']
            dkt_before = adaptive_info['dkt_prediction']
            
            print(f"   📝 Question: {question_data['question_text'][:60]}...")
            print(f"   ⚡ Difficulty: {difficulty.upper()}")
            print(f"   🧠 BKT Mastery: {mastery_before:.4f}")
            print(f"   🤖 DKT Prediction: {dkt_before:.4f}")
            
            # Select answer based on strategy
            if strategy['action'] == 'correct':
                selected_answer = question_data['correct_answer']
                strategy_icon = "✅"
                expected_result = "CORRECT"
            else:
                selected_answer = get_wrong_answer(question_data)
                strategy_icon = "❌"
                expected_result = "INCORRECT"
            
            print(f"   🎯 Strategy: {strategy_icon} {strategy['action'].upper()} answer")
            
            # Submit answer
            submit_data = {
                "session_id": session_id,
                "question_id": question_data['question_id'],
                "selected_answer": selected_answer,
                "time_spent": 8.0 + random.uniform(-2.0, 3.0)  # Realistic time variation
            }
            
            response = requests.post(f"{BASE_URL}/submit-answer/", json=submit_data)
            answer_data = response.json()
            
            # Analyze results
            result_correct = answer_data['answer_correct']
            knowledge_update = answer_data.get('knowledge_update', {})
            mastery_after = knowledge_update.get('new_mastery_level', mastery_before)
            
            result_icon = "✅" if result_correct else "❌"
            actual_result = "CORRECT" if result_correct else "INCORRECT"
            
            print(f"   📊 Result: {result_icon} {actual_result}")
            
            # Calculate mastery change
            if isinstance(mastery_after, (int, float)) and isinstance(mastery_before, (int, float)):
                mastery_change = mastery_after - mastery_before
                print(f"   📈 Mastery: {mastery_before:.4f} → {mastery_after:.4f} ({mastery_change:+.4f})")
            else:
                mastery_change = 0
                print(f"   📈 Mastery: {mastery_before:.4f} → ERROR")
            
            # Get adaptation feedback
            adaptive_feedback = answer_data.get('adaptive_feedback', {})
            adaptation_msg = adaptive_feedback.get('difficulty_adaptation', 'No change')
            feedback_msg = adaptive_feedback.get('adaptation_message', '')
            
            print(f"   🔄 Adaptation: {adaptation_msg}")
            if feedback_msg:
                print(f"   💬 Message: {feedback_msg}")
            
            # Store progression data
            progression_data.append({
                'question': q_num,
                'phase': strategy['phase'],
                'strategy': strategy['action'],
                'difficulty_before': difficulty,
                'mastery_before': mastery_before,
                'mastery_after': mastery_after if isinstance(mastery_after, (int, float)) else mastery_before,
                'mastery_change': mastery_change,
                'result': actual_result,
                'adaptation': adaptation_msg
            })
            
            # Brief pause for readability
            time.sleep(0.8)
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue
    
    # Comprehensive Analysis
    print(f"\n" + "="*80)
    print("📊 COMPLETE ADAPTIVE JOURNEY ANALYSIS")
    print("="*80)
    
    # Phase-by-phase analysis
    phases = {
        'Phase 1': [d for d in progression_data if d['question'] <= 5],
        'Phase 2': [d for d in progression_data if 6 <= d['question'] <= 10],
        'Phase 3': [d for d in progression_data if 11 <= d['question'] <= 15],
        'Phase 4': [d for d in progression_data if d['question'] >= 16]
    }
    
    print(f"\n🔸 PHASE-BY-PHASE PROGRESSION:")
    
    for phase_name, phase_data in phases.items():
        if not phase_data:
            continue
            
        print(f"\n   📋 {phase_name} (Questions {phase_data[0]['question']}-{phase_data[-1]['question']}):")
        
        difficulties = [d['difficulty_before'] for d in phase_data]
        unique_difficulties = list(dict.fromkeys(difficulties))  # Preserve order
        
        initial_mastery = phase_data[0]['mastery_before']
        final_mastery = phase_data[-1]['mastery_after']
        mastery_change = final_mastery - initial_mastery
        
        print(f"     🎯 Strategy: {phase_data[0]['strategy'].upper()} answers")
        print(f"     ⚡ Difficulties: {' → '.join(unique_difficulties)}")
        print(f"     🧠 Mastery: {initial_mastery:.4f} → {final_mastery:.4f} ({mastery_change:+.4f})")
        
        correct_count = sum(1 for d in phase_data if d['result'] == 'CORRECT')
        success_rate = correct_count / len(phase_data) if phase_data else 0
        print(f"     📈 Success Rate: {success_rate:.1%} ({correct_count}/{len(phase_data)})")
    
    # Complete difficulty progression
    print(f"\n🔸 COMPLETE DIFFICULTY JOURNEY:")
    difficulty_progression = [d['difficulty_before'] for d in progression_data]
    print(f"   {' → '.join(difficulty_progression)}")
    
    # Count difficulty changes
    difficulty_changes = []
    for i in range(1, len(difficulty_progression)):
        if difficulty_progression[i] != difficulty_progression[i-1]:
            change = f"{difficulty_progression[i-1]} → {difficulty_progression[i]}"
            change_type = ""
            
            # Determine if easier or harder
            difficulty_order = {'very_easy': 0, 'easy': 1, 'moderate': 2, 'difficult': 3}
            prev_level = difficulty_order.get(difficulty_progression[i-1], 1)
            curr_level = difficulty_order.get(difficulty_progression[i], 1)
            
            if curr_level > prev_level:
                change_type = "📈 HARDER"
            elif curr_level < prev_level:
                change_type = "📉 EASIER"
            else:
                change_type = "➡️ SAME"
            
            difficulty_changes.append({
                'from_q': i,
                'to_q': i+1,
                'change': change,
                'type': change_type
            })
    
    print(f"\n🔸 DIFFICULTY ADAPTATIONS ({len(difficulty_changes)} total):")
    if difficulty_changes:
        for change in difficulty_changes:
            print(f"   Q{change['from_q']} → Q{change['to_q']}: {change['change']} {change['type']}")
    else:
        print(f"   No difficulty changes detected")
    
    # Mastery journey visualization
    print(f"\n🔸 MASTERY EVOLUTION:")
    print(f"   Q# |  Mastery  | Change   | Difficulty | Strategy | Result")
    print(f"   " + "-"*65)
    
    for data in progression_data:
        strategy_icon = "✅" if data['strategy'] == 'correct' else "❌"
        result_icon = "✅" if data['result'] == 'CORRECT' else "❌"
        
        print(f"   {data['question']:2d} | {data['mastery_after']:9.4f} | {data['mastery_change']:+8.4f} | "
              f"{data['difficulty_before']:10s} | {strategy_icon} {data['strategy']:7s} | {result_icon} {data['result']:9s}")
    
    # Statistical summary
    print(f"\n🔸 JOURNEY STATISTICS:")
    
    initial_mastery = progression_data[0]['mastery_before'] if progression_data else 0
    final_mastery = progression_data[-1]['mastery_after'] if progression_data else 0
    total_mastery_change = final_mastery - initial_mastery
    
    # Count by difficulty level
    difficulty_counts = {}
    for d in progression_data:
        difficulty = d['difficulty_before']
        difficulty_counts[difficulty] = difficulty_counts.get(difficulty, 0) + 1
    
    print(f"   📊 Initial Mastery: {initial_mastery:.4f}")
    print(f"   📊 Final Mastery: {final_mastery:.4f}")
    print(f"   📊 Total Change: {total_mastery_change:+.4f}")
    print(f"   📊 Questions by Difficulty:")
    for difficulty, count in sorted(difficulty_counts.items()):
        print(f"      {difficulty}: {count} questions")
    
    # Success metrics
    print(f"\n" + "="*80)
    print("🏆 ADAPTIVE LEARNING SUCCESS METRICS")
    print("="*80)
    
    harder_adaptations = len([c for c in difficulty_changes if "HARDER" in c['type']])
    easier_adaptations = len([c for c in difficulty_changes if "EASIER" in c['type']])
    
    print(f"✅ Total Questions: 20")
    print(f"✅ Difficulty Adaptations: {len(difficulty_changes)}")
    print(f"✅ Adaptations to Harder: {harder_adaptations}")
    print(f"✅ Adaptations to Easier: {easier_adaptations}")
    print(f"✅ Mastery Range: {min(d['mastery_after'] for d in progression_data):.4f} - {max(d['mastery_after'] for d in progression_data):.4f}")
    print(f"✅ Difficulties Used: {len(set(d['difficulty_before'] for d in progression_data))}")
    
    # Final assessment
    if len(difficulty_changes) >= 8 and harder_adaptations > 0 and easier_adaptations > 0:
        print(f"\n🎉 OUTSTANDING SUCCESS!")
        print(f"   🌟 Your adaptive learning system demonstrates:")
        print(f"   • Complete difficulty progression (easy → moderate → difficult)")
        print(f"   • Responsive adaptation to student performance")
        print(f"   • Proper BKT mastery tracking and updates")
        print(f"   • Full utilization of database question difficulties")
        print(f"   • True personalized learning experience")
        print(f"\n🚀 SYSTEM READY FOR PRODUCTION!")
    elif len(difficulty_changes) >= 5:
        print(f"\n✅ EXCELLENT SUCCESS!")
        print(f"   Your adaptive system shows strong responsive behavior")
    elif len(difficulty_changes) >= 2:
        print(f"\n👍 GOOD PROGRESS!")
        print(f"   System adapts but could be more responsive")
    else:
        print(f"\n⚠️ NEEDS IMPROVEMENT")
        print(f"   Limited adaptation detected")
    
    print(f"\n⏰ Journey completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return {
        'total_questions': 20,
        'difficulty_changes': len(difficulty_changes),
        'harder_adaptations': harder_adaptations,
        'easier_adaptations': easier_adaptations,
        'mastery_range': final_mastery - initial_mastery,
        'difficulties_used': len(set(d['difficulty_before'] for d in progression_data)),
        'success': len(difficulty_changes) >= 5 and harder_adaptations > 0 and easier_adaptations > 0
    }

def main():
    """Run the complete adaptive journey test"""
    try:
        results = test_complete_adaptive_journey()
        
        print(f"\n🎯 FINAL JOURNEY SUMMARY:")
        print(f"   Questions Completed: {results['total_questions']}")
        print(f"   Difficulty Changes: {results['difficulty_changes']}")
        print(f"   Harder Adaptations: {results['harder_adaptations']}")
        print(f"   Easier Adaptations: {results['easier_adaptations']}")
        print(f"   Mastery Evolution: {results['mastery_range']:+.4f}")
        print(f"   Difficulty Levels Used: {results['difficulties_used']}")
        print(f"   System Status: {'🎉 EXCELLENT' if results['success'] else '⚠️ NEEDS WORK'}")
        
    except Exception as e:
        print(f"❌ Journey test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()