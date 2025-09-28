#!/usr/bin/env python3
"""
🎯 PROPER FRONTEND ADAPTIVE INTEGRATION TEST
===========================================
Uses the correct adaptive-session endpoints that include proper BKT/orchestration
This should show our REAL adaptive system working through frontend API
"""

import requests
import json
import time
from datetime import datetime

BACKEND_URL = "http://127.0.0.1:8000"

def test_proper_frontend_integration():
    """Test frontend integration using the PROPER adaptive session endpoints"""
    
    print("🎯 PROPER FRONTEND ADAPTIVE INTEGRATION TEST")
    print("=" * 60)
    print("🧠 Using REAL adaptive-session endpoints with full BKT/orchestration!")
    print("📊 This should show our sophisticated adaptive system working")
    
    # Step 1: Start proper adaptive session
    print(f"\n📚 STEP 1: Start Proper Adaptive Session")
    
    session_data = {
        'student_name': f'proper_test_{datetime.now().strftime("%H%M%S")}',
        'subject': 'quantitative_aptitude'
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/adaptive-session/start/", json=session_data)
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            session_info = response.json()
            session_id = session_info.get('session_id')
            student_name = session_info.get('student_name')
            
            print(f"✅ Proper Adaptive Session Started: {session_id}")
            print(f"👤 Student: {student_name}")
            
            # Show session initialization info
            if 'bkt_initial_state' in session_info:
                bkt_state = session_info['bkt_initial_state']
                print(f"🧠 Initial BKT Mastery: {bkt_state.get('mastery', 'N/A')}")
            
            if 'dkt_initial_state' in session_info:
                dkt_state = session_info['dkt_initial_state']
                print(f"🤖 Initial DKT Prediction: {dkt_state.get('prediction', 'N/A')}")
            
            # Step 2: Complete adaptive learning journey with proper orchestration
            print(f"\n🎯 STEP 2: Proper Adaptive Learning Journey")
            print("🎪 This should show REAL BKT mastery updates and orchestration messages!")
            
            mastery_progression = []
            difficulty_progression = []
            orchestration_messages = []
            
            # Strategy: Show the full adaptive journey like our working tests
            # Phase 1: Wrong answers (Q1-3) - should build mastery gradually
            # Phase 2: Correct answers (Q4-8) - should increase mastery significantly  
            # Phase 3: Mixed performance (Q9-12) - should adapt difficulty
            
            answer_phases = [
                {"q_range": (1, 3), "correct": False, "description": "Foundation Building (wrong answers)"},
                {"q_range": (4, 8), "correct": True, "description": "Skill Building (correct answers)"},
                {"q_range": (9, 12), "correct": "mixed", "description": "Advanced Adaptation (mixed performance)"}
            ]
            
            for i in range(12):
                print(f"\n--- Question {i+1}/12 ---")
                
                # Determine strategy for this question
                current_strategy = None
                for phase in answer_phases:
                    start, end = phase["q_range"]
                    if start <= (i+1) <= end:
                        current_strategy = phase
                        break
                
                if not current_strategy:
                    current_strategy = {"correct": True, "description": "Default (correct)"}
                
                print(f"🎯 Phase: {current_strategy['description']}")
                
                # Get next adaptive question
                question_response = requests.get(f"{BACKEND_URL}/adaptive-session/next-question/{session_id}/")
                
                if question_response.status_code == 200:
                    question_data = question_response.json()
                    
                    question_id = question_data.get('question_id', '')
                    difficulty = question_data.get('difficulty', 'unknown')
                    question_text = question_data.get('question_text', '')[:70] + "..."
                    correct_answer = question_data.get('correct_answer', 'A')
                    
                    # Show current BKT state if available
                    if 'current_bkt_mastery' in question_data:
                        current_mastery = question_data['current_bkt_mastery']
                        print(f"🧠 Current BKT Mastery: {current_mastery:.4f}")
                    
                    difficulty_progression.append(difficulty)
                    
                    print(f"📝 Question: {question_text}")
                    print(f"⚡ Difficulty: {difficulty.upper()}")
                    
                    # Show difficulty adaptation
                    if i > 0:
                        prev_difficulty = difficulty_progression[i-1]
                        if difficulty != prev_difficulty:
                            print(f"🔄 🎯 ADAPTATION: {prev_difficulty} → {difficulty}")
                        else:
                            print(f"🔄 Difficulty unchanged: {difficulty}")
                    
                    # Choose answer based on strategy
                    if current_strategy['correct'] == "mixed":
                        # Mixed performance: alternate
                        is_correct_strategy = (i % 2 == 0)
                    else:
                        is_correct_strategy = current_strategy['correct']
                    
                    if is_correct_strategy:
                        chosen_answer = correct_answer
                        strategy_text = "✅ CORRECT (intentional)"
                    else:
                        wrong_options = ['A', 'B', 'C', 'D']
                        if correct_answer in wrong_options:
                            wrong_options.remove(correct_answer)
                        chosen_answer = wrong_options[0] if wrong_options else 'B'
                        strategy_text = "❌ WRONG (intentional)"
                    
                    print(f"💡 Strategy: {strategy_text}")
                    
                    # Submit answer to proper adaptive endpoint
                    submission_data = {
                        'session_id': session_id,
                        'question_id': question_id,
                        'selected_answer': chosen_answer,
                        'time_spent': 15.0
                    }
                    
                    submit_response = requests.post(f"{BACKEND_URL}/adaptive-session/submit-answer/", json=submission_data)
                    
                    if submit_response.status_code == 200:
                        result = submit_response.json()
                        
                        # Display comprehensive adaptive results
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
                        
                        # Show orchestration feedback (this is what was missing!)
                        adaptation_message = result.get('adaptation_message', '')
                        difficulty_change = result.get('difficulty_change', '')
                        
                        if adaptation_message:
                            print(f"💬 Orchestration Message: {adaptation_message}")
                            orchestration_messages.append(adaptation_message)
                        
                        if difficulty_change:
                            print(f"🔄 Difficulty Adaptation: {difficulty_change}")
                        
                        # Show orchestration status details
                        if 'orchestration_status' in result:
                            status = result['orchestration_status']
                            print(f"🎼 Orchestration Status: {status.get('status', 'unknown')}")
                            
                            # Show detailed BKT/DKT updates
                            if 'bkt_update' in status and status['bkt_update']:
                                bkt_update = status['bkt_update']
                                print(f"    🧠 BKT Update: {bkt_update.get('status', 'unknown')}")
                                if 'params_update' in bkt_update:
                                    params = bkt_update['params_update']
                                    print(f"        P_L: {params.get('P_L', 'N/A'):.4f}")
                                    print(f"        P_T: {params.get('P_T', 'N/A'):.4f}")
                            
                            if 'dkt_update' in status and status['dkt_update']:
                                dkt_update = status['dkt_update']
                                print(f"    🤖 DKT Update: {dkt_update.get('status', 'unknown')}")
                        
                    else:
                        print(f"❌ Submission failed: {submit_response.text}")
                        break
                        
                else:
                    print(f"❌ Question fetch failed: {question_response.text}")
                    break
                
                time.sleep(1)  # Pause between questions
            
            # Step 3: Get comprehensive session summary
            print(f"\n📊 STEP 3: Comprehensive Adaptive Session Analysis")
            
            try:
                summary_response = requests.get(f"{BACKEND_URL}/adaptive-session/session-summary/{session_id}/")
                if summary_response.status_code == 200:
                    summary = summary_response.json()
                    
                    print("=" * 60)
                    print("🏆 COMPREHENSIVE SESSION SUMMARY")
                    print("=" * 60)
                    
                    # Basic metrics
                    print(f"✅ Questions Completed: {summary.get('total_questions', 0)}")
                    print(f"✅ Correct Answers: {summary.get('correct_answers', 0)}")
                    print(f"📊 Final Accuracy: {summary.get('accuracy', 0):.1%}")
                    
                    # BKT Analysis
                    if 'bkt_analysis' in summary:
                        bkt_data = summary['bkt_analysis']
                        print(f"\n🧠 BKT MASTERY ANALYSIS:")
                        print(f"   📊 Initial Mastery: {bkt_data.get('initial_mastery', 0):.4f}")
                        print(f"   📊 Final Mastery: {bkt_data.get('final_mastery', 0):.4f}")
                        print(f"   📊 Total Change: {bkt_data.get('mastery_change', 0):+.4f}")
                        print(f"   📊 Peak Mastery: {bkt_data.get('peak_mastery', 0):.4f}")
                    
                    # Difficulty Analysis
                    if 'difficulty_analysis' in summary:
                        diff_data = summary['difficulty_analysis']
                        print(f"\n⚡ DIFFICULTY ADAPTATION ANALYSIS:")
                        print(f"   📊 Difficulty Levels Used: {diff_data.get('levels_used', 0)}")
                        print(f"   🔄 Total Adaptations: {diff_data.get('adaptations_count', 0)}")
                        
                        if 'adaptation_history' in diff_data:
                            adaptations = diff_data['adaptation_history']
                            for adaptation in adaptations:
                                print(f"      {adaptation}")
                    
                    # Orchestration Messages
                    if orchestration_messages:
                        print(f"\n💬 ORCHESTRATION MESSAGES ({len(orchestration_messages)}):")
                        for i, msg in enumerate(orchestration_messages):
                            print(f"   {i+1}. {msg}")
                    
            except Exception as e:
                print(f"⚠️ Could not get session summary: {e}")
            
            # Final Analysis
            print(f"\n🎯 PROPER FRONTEND INTEGRATION ANALYSIS")
            print("=" * 50)
            
            # Success metrics
            has_mastery_updates = len([m for m in mastery_progression if m > 0]) > 0
            has_difficulty_variety = len(set(difficulty_progression)) > 1
            has_orchestration_messages = len(orchestration_messages) > 0
            completed_all_questions = len(mastery_progression) >= 10
            
            print(f"✅ Questions Completed: {completed_all_questions}")
            print(f"✅ BKT Mastery Updates: {has_mastery_updates}")
            print(f"✅ Difficulty Variety: {has_difficulty_variety}")
            print(f"✅ Orchestration Messages: {has_orchestration_messages}")
            
            if mastery_progression:
                initial_mastery = mastery_progression[0] if mastery_progression else 0
                final_mastery = mastery_progression[-1] if mastery_progression else 0
                total_change = final_mastery - initial_mastery
                
                print(f"\n📈 MASTERY PROGRESSION:")
                print(f"   Initial: {initial_mastery:.4f}")
                print(f"   Final: {final_mastery:.4f}")
                print(f"   Change: {total_change:+.4f}")
            
            # Final verdict
            if has_mastery_updates and has_difficulty_variety and has_orchestration_messages:
                print(f"\n🎉 PROPER FRONTEND INTEGRATION: EXCELLENT SUCCESS!")
                print(f"   🧠 Real BKT mastery updates working!")
                print(f"   🎼 Orchestration messages working!")
                print(f"   ⚡ Difficulty adaptation working!")
                print(f"   🎯 Complete adaptive learning system integrated!")
                success_status = "EXCELLENT"
            elif has_mastery_updates or has_orchestration_messages:
                print(f"\n👍 PROPER FRONTEND INTEGRATION: GOOD SUCCESS!")
                print(f"   ✅ Some advanced features working")
                success_status = "GOOD"
            else:
                print(f"\n⚠️ PROPER FRONTEND INTEGRATION: STILL ISSUES")
                print(f"   🔧 Advanced features not fully working")
                success_status = "ISSUES"
            
            print(f"\n⏰ Proper test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"🎯 Status: {success_status}")
            
            return {
                'session_id': session_id,
                'mastery_updates': has_mastery_updates,
                'orchestration_messages': len(orchestration_messages),
                'difficulty_adaptations': len(set(difficulty_progression)),
                'status': success_status
            }
            
        else:
            print(f"❌ Failed to start proper adaptive session: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🚀 Starting PROPER Frontend Adaptive Integration Test...")
    result = test_proper_frontend_integration()
    
    if result:
        print(f"\n✨ PROPER Integration Results:")
        print(f"   🧠 BKT Updates: {result['mastery_updates']}")
        print(f"   💬 Orchestration Messages: {result['orchestration_messages']}")
        print(f"   ⚡ Difficulty Levels: {result['difficulty_adaptations']}")
        print(f"   📊 Status: {result['status']}")
        
        if result['status'] == 'EXCELLENT':
            print(f"\n🎉 SUCCESS! Your sophisticated adaptive learning system is working through the frontend!")
        else:
            print(f"\n🔧 The proper endpoints may need some adjustment")
    else:
        print(f"\n❌ Proper test failed")