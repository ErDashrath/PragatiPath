#!/usr/bin/env python3

import json
import requests
import sys
import time
from datetime import datetime

def test_assessment_flow():
    """Test the complete assessment workflow"""
    
    base_url = "http://localhost:8000/simple"
    
    print("\n🚀 TESTING COMPLETE ASSESSMENT FLOW")
    print("=" * 50)
    
    # Test 1: Start Assessment Session
    print("\n📝 1. Starting Assessment Session...")
    start_data = {
        "username": f"testuser_{int(time.time())}",
        "subject": "quantitative_aptitude",
        "chapter": "percentages",
        "question_count": 3
    }
    
    try:
        response = requests.post(f"{base_url}/start-assessment/", 
                               json=start_data, 
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            session_data = response.json()
            print(f"   ✅ Session created: {session_data['session_id']}")
            print(f"   👤 Student: {session_data.get('user_id')}")
            print(f"   📚 Subject: {session_data['subject']}")
            print(f"   📖 Chapter: {session_data['chapter']}")
            print(f"   🔢 Questions: {session_data['question_count']}")
            
            session_id = session_data['session_id']
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: Get Questions and Submit Answers
    print(f"\n📋 2. Assessment Questions...")
    correct_answers = 0
    total_questions = start_data['question_count']
    
    for q_num in range(1, total_questions + 1):
        print(f"\n   Question {q_num}:")
        
        # Get question
        try:
            response = requests.get(f"{base_url}/get-assessment-question/?session_id={session_id}")
            
            if response.status_code == 200:
                question_data = response.json()
                
                if not question_data.get('success'):
                    if question_data.get('session_complete'):
                        print("   ✅ Session completed!")
                        break
                    else:
                        print(f"   ❌ Question error: {question_data.get('error', 'Unknown error')}")
                        return False
                
                question = question_data['question']
                progress = question_data['session_progress']
                
                print(f"      🔍 ID: {question['question_id']}")
                print(f"      ❓ Text: {question['question_text'][:80]}...")
                print(f"      📊 Progress: {progress['current_question']}/{progress['total_questions']}")
                print(f"      🎯 Difficulty: {question['difficulty']}")
                
                # Extract options and choose one
                options = question['options']
                available_options = list(options.keys())
                chosen_answer = available_options[0]  # Always choose first option for testing
                
                print(f"      🤔 Available options: {', '.join(available_options)}")
                print(f"      ✋ Choosing: {chosen_answer}")
                
            else:
                print(f"      ❌ Failed to get question: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"      ❌ Error getting question: {e}")
            return False
        
        # Submit answer
        time.sleep(1)  # Simulate thinking time
        
        try:
            submit_data = {
                "session_id": session_id,
                "question_id": question['question_id'],
                "selected_answer": chosen_answer,
                "time_spent": 30 + q_num * 5  # Varying time
            }
            
            response = requests.post(f"{base_url}/submit-assessment-answer/",
                                   json=submit_data,
                                   headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                answer_data = response.json()
                
                is_correct = answer_data.get('is_correct', False)
                correct_answer = answer_data.get('correct_answer', 'N/A')
                accuracy = answer_data.get('accuracy', 0)
                current_score = answer_data.get('current_score', 0)
                
                if is_correct:
                    print(f"      ✅ Correct! Answer: {chosen_answer}")
                    correct_answers += 1
                else:
                    print(f"      ❌ Wrong! Chosen: {chosen_answer}, Correct: {correct_answer}")
                
                print(f"      📊 Score: {current_score}/{answer_data.get('question_number', q_num)} ({accuracy:.1f}%)")
                
                # Check if session completed
                if answer_data.get('session_complete'):
                    print("\n   🏁 Assessment completed!")
                    final_results = answer_data.get('final_results', {})
                    if final_results:
                        print(f"      🎯 Final Results:")
                        print(f"         Total Questions: {final_results.get('total_questions', 0)}")
                        print(f"         Correct Answers: {final_results.get('correct_answers', 0)}")
                        print(f"         Final Accuracy: {final_results.get('accuracy', 0):.1f}%")
                        print(f"         Duration: {final_results.get('duration_seconds', 0):.1f} seconds")
                    break
                    
            else:
                print(f"      ❌ Failed to submit answer: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"      ❌ Error submitting answer: {e}")
            return False
    
    # Final summary
    print(f"\n🎉 ASSESSMENT FLOW TEST COMPLETED")
    print("=" * 50)
    print(f"✅ Session ID: {session_id}")
    print(f"📊 Questions answered: {q_num}")
    print(f"🎯 Correct answers: {correct_answers}")
    print(f"📈 Success rate: {(correct_answers/q_num)*100:.1f}%")
    
    return True

if __name__ == "__main__":
    print(f"🧪 Assessment Flow Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = test_assessment_flow()
    
    if success:
        print(f"\n✅ ALL TESTS PASSED! Assessment system is working perfectly! 🎉")
        sys.exit(0)
    else:
        print(f"\n❌ TESTS FAILED! Please check the errors above.")
        sys.exit(1)