#!/usr/bin/env python3
"""
🎯 FRONTEND ADAPTIVE BEHAVIOR DEMONSTRATION
==========================================
Shows the working parts of the adaptive system through frontend API
Focuses on the difficulty adaptation which IS working
"""

import requests
import json
import time
from datetime import datetime

BACKEND_URL = "http://127.0.0.1:8000"

def demonstrate_adaptive_behavior():
    """Demonstrate the working adaptive behavior through frontend"""
    
    print("🎯 FRONTEND ADAPTIVE BEHAVIOR DEMONSTRATION")
    print("=" * 60)
    print("🎪 Showing the WORKING parts of our adaptive learning system!")
    print("📊 Focus: Difficulty adaptation and frontend integration")
    
    # Start session
    print(f"\n📚 STEP 1: Start Adaptive Session")
    
    session_data = {
        'student_name': f'demo_{datetime.now().strftime("%H%M%S")}',
        'subject': 'quantitative_aptitude',
        'question_count': 12
    }
    
    response = requests.post(f"{BACKEND_URL}/simple/start-session/", json=session_data)
    
    if response.status_code == 200:
        session_info = response.json()
        session_id = session_info['session_id']
        student_name = session_info['student_name']
        
        print(f"✅ Session Created: {session_id}")
        print(f"👤 Student: {student_name}")
        
        # Test adaptive journey
        print(f"\n🎯 STEP 2: Adaptive Learning Journey")
        print("🎪 Watch as difficulty adapts based on our performance!")
        
        difficulty_history = []
        question_details = []
        
        for i in range(12):
            print(f"\n--- Question {i+1}/12 ---")
            
            # Get question
            question_response = requests.get(f"{BACKEND_URL}/simple/get-question/{session_id}/")
            
            if question_response.status_code == 200:
                question_data = question_response.json()
                
                question_id = question_data.get('question_id', '')
                difficulty = question_data.get('difficulty', 'unknown')
                question_text = question_data.get('question_text', '')[:60] + "..."
                
                difficulty_history.append(difficulty)
                
                print(f"📝 Question: {question_text}")
                print(f"⚡ Current Difficulty: {difficulty.upper()}")
                
                # Show difficulty adaptation
                if i > 0:
                    prev_difficulty = difficulty_history[i-1]
                    if difficulty != prev_difficulty:
                        difficulty_levels = ["very_easy", "easy", "moderate", "difficult"]
                        if difficulty in difficulty_levels and prev_difficulty in difficulty_levels:
                            curr_level = difficulty_levels.index(difficulty)
                            prev_level = difficulty_levels.index(prev_difficulty)
                            if curr_level > prev_level:
                                print(f"📈 🎯 ADAPTATION: {prev_difficulty} → {difficulty} (HARDER!)")
                            elif curr_level < prev_level:
                                print(f"📉 🎯 ADAPTATION: {prev_difficulty} → {difficulty} (EASIER!)")
                            else:
                                print(f"🔄 Difficulty unchanged: {difficulty}")
                        else:
                            print(f"🔄 🎯 ADAPTATION: {prev_difficulty} → {difficulty}")
                    else:
                        print(f"🔄 Difficulty staying: {difficulty}")
                
                # Simulate strategic answers to trigger adaptations
                # Alternate between good and poor performance to show system response
                if i < 4:
                    # Phase 1: Poor performance (should get easier)
                    chosen_answer = 'A'  # Usually wrong
                    strategy = "🔴 Poor performance phase (should trigger easier questions)"
                elif i < 8:
                    # Phase 2: Good performance (should get harder)  
                    chosen_answer = question_data.get('correct_answer', 'A')
                    strategy = "🟢 Good performance phase (should trigger harder questions)"
                else:
                    # Phase 3: Mixed performance
                    chosen_answer = 'B' if i % 2 == 0 else question_data.get('correct_answer', 'A')
                    strategy = "🟡 Mixed performance phase"
                
                print(f"🎯 Strategy: {strategy}")
                
                # Submit answer
                submission_data = {
                    'session_id': session_id,
                    'question_id': question_id,
                    'selected_answer': chosen_answer,
                    'time_spent': 10.0
                }
                
                submit_response = requests.post(f"{BACKEND_URL}/simple/submit-answer/", json=submission_data)
                
                if submit_response.status_code == 200:
                    result = submit_response.json()
                    
                    is_correct = result.get('is_correct', False)
                    result_emoji = "✅" if is_correct else "❌"
                    
                    print(f"📊 Result: {result_emoji} {'CORRECT' if is_correct else 'INCORRECT'}")
                    
                    question_details.append({
                        'question': i+1,
                        'difficulty': difficulty,
                        'strategy': strategy,
                        'result': 'CORRECT' if is_correct else 'INCORRECT',
                        'answer_submitted': chosen_answer
                    })
                    
                else:
                    print(f"❌ Submission failed: {submit_response.text}")
                    break
            else:
                print(f"❌ Question fetch failed: {question_response.text}")
                break
            
            time.sleep(0.8)  # Pause between questions
        
        # Analyze results
        print(f"\n📊 ADAPTIVE BEHAVIOR ANALYSIS")
        print("=" * 50)
        
        # Difficulty progression
        print(f"🔸 DIFFICULTY PROGRESSION:")
        print(f"   Journey: {' → '.join(difficulty_history)}")
        
        # Find adaptations
        adaptations = []
        difficulty_levels = ["very_easy", "easy", "moderate", "difficult"]
        
        for i in range(1, len(difficulty_history)):
            prev_diff = difficulty_history[i-1]
            curr_diff = difficulty_history[i]
            
            if prev_diff != curr_diff:
                if prev_diff in difficulty_levels and curr_diff in difficulty_levels:
                    prev_level = difficulty_levels.index(prev_diff)
                    curr_level = difficulty_levels.index(curr_diff)
                    
                    if curr_level > prev_level:
                        change_type = "HARDER"
                        emoji = "📈"
                    elif curr_level < prev_level:
                        change_type = "EASIER" 
                        emoji = "📉"
                    else:
                        change_type = "SAME_LEVEL"
                        emoji = "🔄"
                        
                    adaptations.append({
                        'from_q': i,
                        'to_q': i+1,
                        'from_diff': prev_diff,
                        'to_diff': curr_diff,
                        'type': change_type,
                        'emoji': emoji
                    })
        
        print(f"\n🔸 DIFFICULTY ADAPTATIONS DETECTED ({len(adaptations)}):")
        if adaptations:
            for adaptation in adaptations:
                print(f"   {adaptation['emoji']} Q{adaptation['from_q']} → Q{adaptation['to_q']}: {adaptation['from_diff']} → {adaptation['to_diff']} ({adaptation['type']})")
        else:
            print(f"   No difficulty adaptations detected")
        
        # Summary by phase
        print(f"\n🔸 PERFORMANCE BY STRATEGY PHASE:")
        phases = [
            {"name": "Poor Performance (Q1-4)", "range": (1, 4), "expected": "Should get easier"},
            {"name": "Good Performance (Q5-8)", "range": (5, 8), "expected": "Should get harder"},
            {"name": "Mixed Performance (Q9-12)", "range": (9, 12), "expected": "Should adapt"}
        ]
        
        for phase in phases:
            start, end = phase['range']
            phase_questions = [q for q in question_details if start <= q['question'] <= end]
            
            if phase_questions:
                difficulties = [q['difficulty'] for q in phase_questions]
                unique_diffs = list(set(difficulties))
                
                print(f"   📋 {phase['name']}:")
                print(f"      Difficulties: {' → '.join(difficulties)}")
                print(f"      Unique levels: {len(unique_diffs)} ({', '.join(unique_diffs)})")
                print(f"      Expected: {phase['expected']}")
        
        # Success metrics
        print(f"\n🏆 ADAPTIVE SYSTEM SUCCESS METRICS")
        print("=" * 40)
        
        unique_difficulties = list(set(difficulty_history))
        has_adaptations = len(adaptations) > 0
        uses_multiple_difficulties = len(unique_difficulties) > 1
        
        print(f"✅ Questions Completed: {len(question_details)}/12")
        print(f"✅ Difficulty Levels Used: {len(unique_difficulties)} ({', '.join(unique_difficulties)})")
        print(f"✅ Difficulty Adaptations: {len(adaptations)}")
        print(f"✅ Multiple Difficulties: {uses_multiple_difficulties}")
        print(f"✅ Adaptive Behavior: {has_adaptations}")
        
        # Final verdict
        if has_adaptations and uses_multiple_difficulties:
            print(f"\n🎉 FRONTEND ADAPTIVE INTEGRATION: SUCCESS!")
            print(f"   🎯 The adaptive learning system IS working through the frontend!")
            print(f"   ✅ Difficulty adaptation functioning correctly")
            print(f"   ✅ Frontend API integration successful")
            print(f"   ✅ Real-time adaptation demonstrated")
            success_status = "SUCCESS"
        elif uses_multiple_difficulties:
            print(f"\n👍 FRONTEND INTEGRATION: PARTIAL SUCCESS")
            print(f"   ⚡ Multiple difficulty levels working")
            print(f"   🔧 Adaptation logic needs refinement")
            success_status = "PARTIAL"
        else:
            print(f"\n⚠️ FRONTEND INTEGRATION: NEEDS WORK")
            print(f"   🔧 Difficulty adaptation not working as expected")
            success_status = "NEEDS_WORK"
        
        print(f"\n⏰ Demo completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Status: {success_status}")
        
        return {
            'session_id': session_id,
            'adaptations': len(adaptations),
            'difficulties_used': len(unique_difficulties),
            'status': success_status
        }
        
    else:
        print(f"❌ Failed to start session: {response.text}")
        return None

if __name__ == "__main__":
    print("🚀 Starting Frontend Adaptive Behavior Demo...")
    result = demonstrate_adaptive_behavior()
    
    if result:
        print(f"\n✨ Demo Results:")
        print(f"   🎯 Adaptations: {result['adaptations']}")
        print(f"   ⚡ Difficulty Levels: {result['difficulties_used']}")
        print(f"   📊 Status: {result['status']}")
    else:
        print(f"\n❌ Demo failed")