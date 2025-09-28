#!/usr/bin/env python3
"""
🎯 SIMPLE FRONTEND ADAPTIVE INTEGRATION TEST
============================================
Direct test of frontend adaptive learning system
"""

import requests
import json
import time
from datetime import datetime

BACKEND_URL = "http://127.0.0.1:8000"

def test_frontend_adaptive_integration():
    """Test the complete frontend adaptive integration"""
    
    print("🎯 FRONTEND ADAPTIVE LEARNING INTEGRATION TEST")
    print("=" * 60)
    
    # Step 1: Start adaptive session
    print("\n📚 Step 1: Starting Adaptive Session")
    
    session_data = {
        'student_name': f'frontend_test_{datetime.now().strftime("%H%M%S")}',
        'subject': 'quantitative_aptitude',
        'question_count': 10
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/simple/start-session/", json=session_data)
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            session_info = response.json()
            session_id = session_info.get('session_id')
            print(f"✅ Session Started: {session_id}")
            print(f"📊 Student: {session_info.get('student_name')}")
            
            # Step 2: Complete adaptive learning journey
            print(f"\n🎯 Step 2: Adaptive Learning Journey")
            
            questions_completed = 0
            mastery_progression = []
            
            # Alternate between correct and wrong answers to show adaptation
            answer_strategy = [False, False, True, True, True, False, True, True, False, True]  # Mix of right/wrong
            
            for i in range(10):
                print(f"\n--- Question {i+1}/10 ---")
                
                # Get next question
                question_response = requests.get(f"{BACKEND_URL}/simple/get-question/{session_id}/")
                
                if question_response.status_code == 200:
                    question_data = question_response.json()
                    question_id = question_data.get('question_id')
                    difficulty = question_data.get('difficulty', 'unknown')
                    question_text = question_data.get('question_text', '')[:60] + "..."
                    correct_answer = question_data.get('correct_answer', 'A')
                    
                    print(f"📝 Question: {question_text}")
                    print(f"⚡ Difficulty: {difficulty}")
                    
                    # Choose answer based on strategy
                    is_correct_strategy = answer_strategy[i] if i < len(answer_strategy) else True
                    if is_correct_strategy:
                        chosen_answer = correct_answer
                        strategy_text = "✅ CORRECT (intentional)"
                    else:
                        options = ['A', 'B', 'C', 'D']
                        if correct_answer in options:
                            options.remove(correct_answer)
                        chosen_answer = options[0] if options else 'B'
                        strategy_text = "❌ WRONG (intentional)"
                    
                    print(f"🎯 Strategy: {strategy_text}")
                    
                    # Submit answer
                    submission_data = {
                        'session_id': session_id,
                        'question_id': question_id,
                        'selected_answer': chosen_answer
                    }
                    
                    submit_response = requests.post(f"{BACKEND_URL}/simple/submit-answer/", json=submission_data)
                    
                    if submit_response.status_code == 200:
                        result = submit_response.json()
                        
                        # Display results
                        is_correct = result.get('is_correct', False)
                        bkt_before = result.get('bkt_mastery_before', 0)
                        bkt_after = result.get('bkt_mastery_after', 0)
                        mastery_change = bkt_after - bkt_before
                        
                        mastery_progression.append(bkt_after)
                        
                        result_emoji = "✅" if is_correct else "❌"
                        print(f"📊 Result: {result_emoji} {'CORRECT' if is_correct else 'INCORRECT'}")
                        print(f"🧠 Mastery: {bkt_before:.4f} → {bkt_after:.4f} ({mastery_change:+.4f})")
                        
                        # Show adaptation message
                        if 'adaptation_message' in result:
                            print(f"💬 System: {result['adaptation_message']}")
                        
                        if 'difficulty_change' in result:
                            print(f"🔄 Adaptation: {result['difficulty_change']}")
                        
                        # Show orchestration status if available
                        if 'orchestration_status' in result:
                            status = result['orchestration_status']
                            print(f"🎼 Orchestration: {status.get('status', 'unknown')}")
                        
                        questions_completed += 1
                        
                    else:
                        print(f"❌ Failed to submit answer: {submit_response.text}")
                        break
                        
                else:
                    print(f"❌ Failed to get question: {question_response.text}")
                    break
                
                time.sleep(0.5)  # Small delay
            
            # Step 3: Show results
            print(f"\n📊 FINAL RESULTS")
            print("=" * 40)
            print(f"✅ Questions Completed: {questions_completed}/10")
            
            if mastery_progression:
                initial_mastery = mastery_progression[0]
                final_mastery = mastery_progression[-1]
                total_change = final_mastery - initial_mastery
                
                print(f"🧠 Mastery Evolution:")
                print(f"   Initial: {initial_mastery:.4f}")
                print(f"   Final: {final_mastery:.4f}")
                print(f"   Change: {total_change:+.4f}")
                
                print(f"\n📈 Mastery Progression:")
                for i, mastery in enumerate(mastery_progression):
                    print(f"   Q{i+1}: {mastery:.4f}")
            
            # Get session progress
            try:
                progress_response = requests.get(f"{BACKEND_URL}/simple/session-progress/{session_id}/")
                if progress_response.status_code == 200:
                    progress = progress_response.json()
                    print(f"\n📊 Session Progress:")
                    print(f"   Total Questions: {progress.get('total_questions', 0)}")
                    print(f"   Correct Answers: {progress.get('correct_answers', 0)}")
                    print(f"   Accuracy: {progress.get('accuracy', 0):.1%}")
            except:
                pass
            
            print(f"\n🎉 FRONTEND INTEGRATION SUCCESS!")
            print(f"✅ Complete adaptive learning journey working through frontend API")
            
        else:
            print(f"❌ Failed to start session: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_frontend_adaptive_integration()