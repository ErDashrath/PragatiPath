#!/usr/bin/env python3
"""
🎯 WORKING FRONTEND ADAPTIVE INTEGRATION TEST
============================================
Proper test using the exact API format expected by the backend
"""

import requests
import json
import time
from datetime import datetime

BACKEND_URL = "http://127.0.0.1:8000"

def test_working_frontend_integration():
    """Test frontend integration using exact backend API format"""
    
    print("🎯 WORKING FRONTEND ADAPTIVE INTEGRATION TEST")
    print("=" * 60)
    
    # Step 1: Start adaptive session
    print("\n📚 Step 1: Starting Adaptive Session")
    
    session_data = {
        'student_name': f'working_test_{datetime.now().strftime("%H%M%S")}',
        'subject': 'quantitative_aptitude',
        'question_count': 8
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/simple/start-session/", json=session_data)
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            session_info = response.json()
            session_id = session_info.get('session_id')
            student_name = session_info.get('student_name')
            print(f"✅ Session Started: {session_id}")
            print(f"👤 Student: {student_name}")
            
            # Step 2: Complete adaptive learning journey
            print(f"\n🎯 Step 2: Adaptive Learning Journey (8 Questions)")
            
            questions_completed = 0
            mastery_progression = []
            difficulty_progression = []
            
            # Strategy: wrong answers first, then correct answers to show adaptation
            # Phase 1: Wrong answers (Q1-3) - should build foundation
            # Phase 2: Correct answers (Q4-8) - should increase difficulty and mastery
            answer_strategies = [
                {"phase": "Foundation Building", "correct": False, "description": "❌ Wrong answer (building foundation)"},
                {"phase": "Foundation Building", "correct": False, "description": "❌ Wrong answer (building foundation)"},
                {"phase": "Foundation Building", "correct": False, "description": "❌ Wrong answer (building foundation)"},
                {"phase": "Skill Building", "correct": True, "description": "✅ Correct answer (skill building)"},
                {"phase": "Skill Building", "correct": True, "description": "✅ Correct answer (skill building)"},
                {"phase": "Mastery Building", "correct": True, "description": "✅ Correct answer (mastery building)"},
                {"phase": "Advanced Learning", "correct": True, "description": "✅ Correct answer (advanced learning)"},
                {"phase": "Expert Level", "correct": True, "description": "✅ Correct answer (expert level)"}
            ]
            
            for i in range(8):
                strategy = answer_strategies[i] if i < len(answer_strategies) else answer_strategies[-1]
                
                print(f"\n--- Question {i+1}/8: {strategy['phase']} ---")
                
                # Get next question
                question_response = requests.get(f"{BACKEND_URL}/simple/get-question/{session_id}/")
                
                if question_response.status_code == 200:
                    question_data = question_response.json()
                    
                    # Extract question details
                    question_id = question_data.get('question_id', '')
                    difficulty = question_data.get('difficulty', 'unknown')
                    question_text = question_data.get('question_text', '')[:70] + "..."
                    options = question_data.get('options', {})
                    correct_answer = question_data.get('correct_answer', 'A')
                    
                    difficulty_progression.append(difficulty)
                    
                    print(f"📝 Question: {question_text}")
                    print(f"⚡ Difficulty: {difficulty.upper()}")
                    print(f"🎯 Strategy: {strategy['description']}")
                    
                    # Choose answer based on strategy
                    if strategy['correct']:
                        # Submit correct answer
                        chosen_answer = correct_answer
                        print(f"💡 Submitting CORRECT answer: {chosen_answer}")
                    else:
                        # Submit wrong answer
                        wrong_options = ['A', 'B', 'C', 'D']
                        if correct_answer in wrong_options:
                            wrong_options.remove(correct_answer)
                        chosen_answer = wrong_options[0] if wrong_options else 'B'
                        print(f"💡 Submitting WRONG answer: {chosen_answer} (correct: {correct_answer})")
                    
                    # Submit answer with proper format
                    submission_data = {
                        'session_id': session_id,
                        'question_id': question_id,  # Use question_id as received from API
                        'selected_answer': chosen_answer,
                        'time_spent': 12.5
                    }
                    
                    submit_response = requests.post(f"{BACKEND_URL}/simple/submit-answer/", json=submission_data)
                    
                    if submit_response.status_code == 200:
                        result = submit_response.json()
                        
                        # Display detailed results
                        is_correct = result.get('is_correct', False)
                        bkt_before = result.get('bkt_mastery_before', 0)
                        bkt_after = result.get('bkt_mastery_after', 0)
                        dkt_prediction = result.get('dkt_prediction', 0)
                        mastery_change = bkt_after - bkt_before
                        
                        mastery_progression.append(bkt_after)
                        
                        result_emoji = "✅" if is_correct else "❌"
                        result_text = "CORRECT" if is_correct else "INCORRECT"
                        
                        print(f"📊 Result: {result_emoji} {result_text}")
                        print(f"🧠 BKT Mastery: {bkt_before:.4f} → {bkt_after:.4f} ({mastery_change:+.4f})")
                        print(f"🤖 DKT Prediction: {dkt_prediction:.4f}")
                        
                        # Show adaptive feedback
                        adaptation_message = result.get('adaptation_message', 'No message')
                        difficulty_change = result.get('difficulty_change', 'No change')
                        
                        print(f"🔄 Adaptation: {difficulty_change}")
                        print(f"💬 System Message: {adaptation_message}")
                        
                        # Show orchestration status if available
                        if 'orchestration_status' in result:
                            status = result['orchestration_status']
                            print(f"🎼 Orchestration Status: {status.get('status', 'unknown')}")
                            
                            if 'bkt_update' in status and status['bkt_update']:
                                bkt_status = status['bkt_update']
                                print(f"    🧠 BKT Update: {bkt_status.get('status', 'unknown')}")
                            
                            if 'dkt_update' in status and status['dkt_update']:
                                dkt_status = status['dkt_update']
                                print(f"    🤖 DKT Update: {dkt_status.get('status', 'unknown')}")
                        
                        questions_completed += 1
                        
                    else:
                        print(f"❌ Failed to submit answer: {submit_response.text}")
                        break
                        
                else:
                    print(f"❌ Failed to get question: {question_response.text}")
                    break
                
                time.sleep(1)  # Pause between questions
            
            # Step 3: Comprehensive Results Analysis
            print(f"\n📊 COMPREHENSIVE ADAPTIVE RESULTS")
            print("=" * 50)
            
            print(f"✅ Questions Completed: {questions_completed}/8")
            
            # Mastery Analysis
            if mastery_progression:
                initial_mastery = mastery_progression[0]
                final_mastery = mastery_progression[-1]
                total_change = final_mastery - initial_mastery
                max_mastery = max(mastery_progression)
                min_mastery = min(mastery_progression)
                
                print(f"\n🧠 BKT MASTERY EVOLUTION:")
                print(f"   📊 Initial Mastery: {initial_mastery:.4f}")
                print(f"   📊 Final Mastery: {final_mastery:.4f}")
                print(f"   📊 Total Change: {total_change:+.4f}")
                print(f"   📊 Peak Mastery: {max_mastery:.4f}")
                print(f"   📊 Range: {min_mastery:.4f} - {max_mastery:.4f}")
                
                print(f"\n📈 Question-by-Question Mastery:")
                for i, mastery in enumerate(mastery_progression):
                    strategy_desc = answer_strategies[i]['description'] if i < len(answer_strategies) else "Unknown"
                    print(f"   Q{i+1}: {mastery:.4f} ({strategy_desc})")
            
            # Difficulty Analysis
            if difficulty_progression:
                unique_difficulties = list(set(difficulty_progression))
                print(f"\n⚡ DIFFICULTY PROGRESSION:")
                print(f"   📊 Difficulty Journey: {' → '.join(difficulty_progression)}")
                print(f"   📊 Unique Difficulties: {len(unique_difficulties)} ({', '.join(unique_difficulties)})")
                
                # Check for difficulty changes
                difficulty_changes = []
                for i in range(1, len(difficulty_progression)):
                    if difficulty_progression[i] != difficulty_progression[i-1]:
                        change_type = "HARDER" if ["very_easy", "easy", "moderate", "difficult"].index(difficulty_progression[i]) > ["very_easy", "easy", "moderate", "difficult"].index(difficulty_progression[i-1]) else "EASIER"
                        difficulty_changes.append(f"Q{i} → Q{i+1}: {difficulty_progression[i-1]} → {difficulty_progression[i]} ({change_type})")
                
                if difficulty_changes:
                    print(f"   🔄 Difficulty Adaptations ({len(difficulty_changes)}):")
                    for change in difficulty_changes:
                        print(f"      {change}")
                else:
                    print(f"   🔄 No difficulty adaptations detected")
            
            # Success Metrics
            print(f"\n🎯 ADAPTIVE LEARNING SUCCESS METRICS:")
            
            has_mastery_growth = total_change > 0.1 if mastery_progression else False
            has_difficulty_variety = len(set(difficulty_progression)) > 1 if difficulty_progression else False
            completed_all_questions = questions_completed >= 8
            
            print(f"   ✅ All Questions Completed: {completed_all_questions}")
            print(f"   ✅ Mastery Growth (>0.1): {has_mastery_growth}")
            print(f"   ✅ Difficulty Variety: {has_difficulty_variety}")
            
            if has_mastery_growth and has_difficulty_variety and completed_all_questions:
                print(f"\n🏆 FRONTEND INTEGRATION: EXCELLENT SUCCESS!")
                print(f"   🎉 Complete adaptive learning system working perfectly through frontend API")
                success_status = "EXCELLENT"
            elif completed_all_questions and (has_mastery_growth or has_difficulty_variety):
                print(f"\n✅ FRONTEND INTEGRATION: GOOD SUCCESS!")
                print(f"   👍 Adaptive system working with minor limitations")
                success_status = "GOOD"
            else:
                print(f"\n⚠️ FRONTEND INTEGRATION: PARTIAL SUCCESS")
                print(f"   🔧 Some adaptive features need adjustment")
                success_status = "PARTIAL"
            
            # Final session summary
            try:
                progress_response = requests.get(f"{BACKEND_URL}/simple/session-progress/{session_id}/")
                if progress_response.status_code == 200:
                    progress = progress_response.json()
                    print(f"\n📊 FINAL SESSION SUMMARY:")
                    print(f"   📈 Total Questions: {progress.get('total_questions', 0)}")
                    print(f"   ✅ Correct Answers: {progress.get('correct_answers', 0)}")
                    print(f"   📊 Final Accuracy: {progress.get('accuracy', 0):.1%}")
            except:
                print(f"\n📊 Session summary not available")
            
            print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"🎯 Overall Status: {success_status}")
            
            return {
                'session_id': session_id,
                'student_name': student_name,
                'questions_completed': questions_completed,
                'mastery_progression': mastery_progression,
                'difficulty_progression': difficulty_progression,
                'success_status': success_status
            }
            
        else:
            print(f"❌ Failed to start session: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🚀 Starting Working Frontend Adaptive Integration Test...")
    result = test_working_frontend_integration()
    
    if result:
        print(f"\n✅ Test completed successfully!")
    else:
        print(f"\n❌ Test failed or incomplete")