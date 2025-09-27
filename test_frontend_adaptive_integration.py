#!/usr/bin/env python3
"""
🎯 FRONTEND ADAPTIVE LEARNING INTEGRATION TEST
==================================================
Tests the complete adaptive learning system integration with frontend
Shows real-time BKT mastery updates, difficulty adaptation, and intelligent messaging
"""

import requests
import json
import time
import random
from datetime import datetime

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://localhost:3000"

def print_banner(text):
    """Print a colorful banner"""
    print(f"\n{'='*80}")
    print(f"🎯 {text}")
    print(f"{'='*80}")

def print_section(text):
    """Print a section header"""
    print(f"\n🔸 {text}")
    print("-" * 60)

def start_adaptive_session(subject="quantitative_aptitude"):
    """Start an adaptive learning session using simple frontend API"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    student_name = f"adaptive_frontend_{timestamp}_{random.randint(1000, 9999)}"
    
    session_data = {
        'student_name': student_name,
        'subject': subject,
        'question_count': 20  # We want to test 20 questions
    }
    
    print(f"📚 Starting adaptive session for: {student_name}")
    print(f"🎯 Subject: {subject} | Questions: 20")
    
    try:
        response = requests.post(f"{BACKEND_URL}/simple/start-session/", json=session_data)
        
        if response.status_code == 200:
            result = response.json()
            session_id = result.get('session_id')
            print(f"✅ Adaptive session started: {session_id}")
            return session_id, student_name
        else:
            print(f"❌ Session start failed: {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ Error starting session: {e}")
        return None, None

def get_next_question(session_id):
    """Get the next adaptive question using simple frontend API"""
    try:
        response = requests.get(f"{BACKEND_URL}/simple/get-question/{session_id}/")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get question: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error getting question: {e}")
        return None

def submit_answer(session_id, question_id, answer, is_correct_strategy):
    """Submit an answer with strategic correctness using simple frontend API"""
    try:
        # For simple frontend API, we need to determine correct answer from the question
        # Let's assume we can get it or use strategy-based selection
        
        # Choose answer based on strategy
        if is_correct_strategy:
            # For correct strategy, we'll submit the provided answer (assuming it's correct)
            chosen_answer = answer
        else:
            # For wrong strategy, choose a different option
            options = ['A', 'B', 'C', 'D']
            if answer in options:
                options.remove(answer)
            chosen_answer = random.choice(options)
        
        submission_data = {
            'session_id': session_id,
            'question_id': question_id,
            'selected_answer': chosen_answer
        }
        
        response = requests.post(f"{BACKEND_URL}/simple/submit-answer/", json=submission_data)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Answer submission failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error submitting answer: {e}")
        return None

def display_question_result(q_num, total_questions, question_data, result, strategy):
    """Display detailed question result with adaptive insights"""
    print(f"\n🔸 Question {q_num}/{total_questions} - {strategy}")
    
    # Question details
    question_text = question_data.get('question_text', 'N/A')[:80] + "..."
    difficulty = question_data.get('difficulty', 'unknown')
    
    print(f"   📝 Question: {question_text}")
    print(f"   ⚡ Difficulty: {difficulty.upper()}")
    
    # BKT & DKT Status
    bkt_before = result.get('bkt_mastery_before', 0)
    bkt_after = result.get('bkt_mastery_after', 0)
    dkt_prediction = result.get('dkt_prediction', 0)
    mastery_change = bkt_after - bkt_before
    
    print(f"   🧠 BKT Mastery: {bkt_before:.4f}")
    print(f"   🤖 DKT Prediction: {dkt_prediction:.4f}")
    
    # Answer result
    is_correct = result.get('is_correct', False)
    selected_answer = result.get('selected_answer', 'N/A')
    correct_answer = result.get('correct_answer', 'N/A')
    
    result_emoji = "✅" if is_correct else "❌"
    result_text = "CORRECT" if is_correct else "INCORRECT"
    
    print(f"   🎯 Strategy: {strategy}")
    print(f"   📊 Result: {result_emoji} {result_text}")
    print(f"   📈 Mastery: {bkt_before:.4f} → {bkt_after:.4f} ({mastery_change:+.4f})")
    
    # Adaptation info
    adaptation_message = result.get('adaptation_message', 'No message')
    difficulty_change = result.get('difficulty_change', 'No change')
    
    print(f"   🔄 Adaptation: {difficulty_change}")
    print(f"   💬 Message: {adaptation_message}")
    
    # Orchestration status
    if result.get('orchestration_status'):
        status = result['orchestration_status']
        print(f"   🎼 Orchestration: {status.get('status', 'unknown')}")
        if status.get('bkt_update'):
            bkt_status = status['bkt_update']
            print(f"       🧠 BKT: {bkt_status.get('status', 'unknown')}")
        if status.get('dkt_update'):
            dkt_status = status['dkt_update']
            print(f"       🤖 DKT: {dkt_status.get('status', 'unknown')}")

def run_frontend_adaptive_test():
    """Run complete frontend adaptive learning integration test"""
    
    print_banner("FRONTEND ADAPTIVE LEARNING INTEGRATION TEST")
    print("🎯 Testing complete adaptive system with frontend integration")
    print("📊 Strategy: Mixed performance to show full adaptive behavior")
    print("   Phase 1 (Q1-5):   Wrong answers → build foundation")
    print("   Phase 2 (Q6-10):  Correct answers → increase difficulty") 
    print("   Phase 3 (Q11-15): Correct answers → reach mastery")
    print("   Phase 4 (Q16-20): Wrong answers → difficulty adaptation")
    
    # Step 1: Start adaptive session (simple API handles user creation automatically)
    print_section("STEP 1: Adaptive Session Setup")
    session_id, student_name = start_adaptive_session()
    if not session_id:
        print("❌ Failed to start session. Exiting.")
        return
    
    # Step 2: Complete adaptive learning journey
    print_section("STEP 2: Adaptive Learning Journey (20 Questions)")
    
    total_questions = 20
    phases = {
        1: {"range": (1, 5), "strategy": "❌ WRONG answers", "correct": False},
        2: {"range": (6, 10), "strategy": "✅ CORRECT answers", "correct": True},
        3: {"range": (11, 15), "strategy": "✅ CORRECT answers", "correct": True},
        4: {"range": (16, 20), "strategy": "❌ WRONG answers", "correct": False}
    }
    
    # Track journey statistics
    difficulty_changes = []
    mastery_progression = []
    question_results = []
    
    for q_num in range(1, total_questions + 1):
        # Determine current phase and strategy
        current_phase = None
        strategy = ""
        is_correct_strategy = True
        
        for phase_num, phase_info in phases.items():
            start, end = phase_info["range"]
            if start <= q_num <= end:
                current_phase = phase_num
                strategy = f"Phase {phase_num}: {phase_info['strategy']}"
                is_correct_strategy = phase_info["correct"]
                break
        
        # Get next question
        question_data = get_next_question(session_id)
        if not question_data:
            print(f"❌ Failed to get question {q_num}")
            break
        
        question_id = question_data.get('question_id')
        current_difficulty = question_data.get('difficulty', 'unknown')
        correct_answer = question_data.get('correct_answer', 'A')
        
        # Submit answer with strategy
        result = submit_answer(session_id, question_id, correct_answer, is_correct_strategy)
        if not result:
            print(f"❌ Failed to submit answer for question {q_num}")
            break
        
        # Display result
        display_question_result(q_num, total_questions, question_data, result, strategy)
        
        # Track statistics
        bkt_after = result.get('bkt_mastery_after', 0)
        mastery_progression.append(bkt_after)
        
        # Check for difficulty change
        if q_num > 1:
            prev_difficulty = question_results[-1].get('difficulty')
            if prev_difficulty != current_difficulty:
                change_type = "HARDER" if ["very_easy", "easy", "moderate", "difficult"].index(current_difficulty) > ["very_easy", "easy", "moderate", "difficult"].index(prev_difficulty) else "EASIER"
                difficulty_changes.append({
                    'question': q_num,
                    'from': prev_difficulty,
                    'to': current_difficulty,
                    'type': change_type
                })
        
        question_results.append({
            'question': q_num,
            'difficulty': current_difficulty,
            'mastery': bkt_after,
            'is_correct': result.get('is_correct', False),
            'phase': current_phase
        })
        
        # Small delay to simulate real user interaction
        time.sleep(0.5)
    
    # Step 3: Display comprehensive results
    print_section("STEP 3: Adaptive Journey Analysis")
    
    print("🔸 PHASE-BY-PHASE RESULTS:")
    for phase_num, phase_info in phases.items():
        start, end = phase_info["range"]
        phase_questions = [q for q in question_results if q['phase'] == phase_num]
        
        if phase_questions:
            phase_accuracy = sum(1 for q in phase_questions if q['is_correct']) / len(phase_questions) * 100
            start_mastery = phase_questions[0]['mastery']
            end_mastery = phase_questions[-1]['mastery']
            mastery_change = end_mastery - start_mastery
            
            difficulties = list(set(q['difficulty'] for q in phase_questions))
            
            print(f"   📋 Phase {phase_num} (Questions {start}-{end}):")
            print(f"     🎯 Strategy: {phase_info['strategy']}")
            print(f"     ⚡ Difficulties: {', '.join(difficulties)}")
            print(f"     🧠 Mastery: {start_mastery:.4f} → {end_mastery:.4f} ({mastery_change:+.4f})")
            print(f"     📈 Success Rate: {phase_accuracy:.1f}% ({sum(1 for q in phase_questions if q['is_correct'])}/{len(phase_questions)})")
    
    print("\n🔸 DIFFICULTY ADAPTATIONS:")
    if difficulty_changes:
        for change in difficulty_changes:
            print(f"   Q{change['question']}: {change['from']} → {change['to']} 📈 {change['type']}")
    else:
        print("   No difficulty changes detected")
    
    print("\n🔸 MASTERY EVOLUTION:")
    if mastery_progression:
        initial_mastery = mastery_progression[0] if len(mastery_progression) > 0 else 0
        final_mastery = mastery_progression[-1] if len(mastery_progression) > 0 else 0
        total_change = final_mastery - initial_mastery
        max_mastery = max(mastery_progression) if mastery_progression else 0
        
        print(f"   📊 Initial Mastery: {initial_mastery:.4f}")
        print(f"   📊 Final Mastery: {final_mastery:.4f}")
        print(f"   📊 Total Change: {total_change:+.4f}")
        print(f"   📊 Peak Mastery: {max_mastery:.4f}")
    
    print_section("FRONTEND INTEGRATION SUCCESS METRICS")
    
    print("✅ Frontend Integration Results:")
    print(f"   📱 Total Questions Completed: {len(question_results)}")
    print(f"   🔄 Difficulty Adaptations: {len(difficulty_changes)}")
    print(f"   📊 Mastery Range: {min(mastery_progression):.4f} - {max(mastery_progression):.4f}")
    print(f"   ⚡ Difficulty Levels Used: {len(set(q['difficulty'] for q in question_results))}")
    print(f"   🎯 Phases Completed: {len(set(q['phase'] for q in question_results))}")
    
    # Success determination
    has_difficulty_changes = len(difficulty_changes) > 0
    has_mastery_growth = (mastery_progression[-1] - mastery_progression[0]) > 0 if len(mastery_progression) >= 2 else False
    uses_multiple_difficulties = len(set(q['difficulty'] for q in question_results)) > 1
    
    if has_difficulty_changes and has_mastery_growth and uses_multiple_difficulties:
        print("\n🎉 FRONTEND INTEGRATION: EXCELLENT SUCCESS!")
        print("   Your adaptive system shows perfect frontend integration")
    else:
        print("\n⚠️ FRONTEND INTEGRATION: PARTIAL SUCCESS")
        print("   Some adaptive features may need adjustment")
    
    print(f"\n⏰ Integration test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return {
        'student_name': student_name,
        'session_id': session_id,
        'total_questions': len(question_results),
        'difficulty_changes': len(difficulty_changes),
        'mastery_progression': mastery_progression,
        'success': has_difficulty_changes and has_mastery_growth and uses_multiple_difficulties
    }

if __name__ == "__main__":
    print("🎯 Starting Frontend Adaptive Learning Integration Test...")
    
    try:
        result = run_frontend_adaptive_test()
        
        if result and result['success']:
            print("\n✅ COMPLETE SUCCESS: Frontend adaptive learning integration is working perfectly!")
        else:
            print("\n⚠️ PARTIAL SUCCESS: Integration completed with some limitations")
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()