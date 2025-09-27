#!/usr/bin/env python3
"""
Create a comprehensive test session for the 'dash' user with realistic mixed performance
"""
import requests
import json
import random

def create_comprehensive_test_session():
    base_url = 'http://127.0.0.1:8000/simple'
    
    print("🎯 Creating Comprehensive Test Session for 'dash' User")
    print("=" * 60)
    
    # Create session for 'dash' user (the one you're logged in as)
    session_data = {
        'student_name': 'dash',
        'subject': 'quantitative_aptitude',
        'question_count': 10  # Standard 10 questions
    }
    
    print("1. Starting session for dash user...")
    try:
        response = requests.post(f'{base_url}/start-session/', json=session_data)
        if response.status_code == 200:
            result = response.json()
            session_id = result['session_id']
            print(f"✅ Session started: {session_id}")
            
            # Simulate realistic mixed performance (70% accuracy target)
            questions_data = []
            correct_count = 0
            total_time = 0
            
            print(f"\n2. Answering 10 questions with mixed performance...")
            
            # Define realistic answer patterns
            target_correct = 7  # Target 7/10 correct (70% accuracy)
            correct_questions = random.sample(range(10), target_correct)
            
            for i in range(10):
                # Get question
                question_response = requests.get(f'{base_url}/get-question/{session_id}/')
                if question_response.status_code == 200:
                    question_data = question_response.json()
                    if question_data.get('session_complete'):
                        print(f"Session completed after {i} questions")
                        break
                        
                    questions_data.append(question_data)
                    
                    # Determine if this question should be correct
                    is_target_correct = i in correct_questions
                    
                    # Choose answer based on target
                    if is_target_correct:
                        answer_choice = 'A'  # Assume A is often correct for simplicity
                    else:
                        answer_choice = random.choice(['B', 'C', 'D'])
                    
                    # Realistic time: faster for correct answers, slower for wrong ones
                    time_spent = random.randint(20, 60) if is_target_correct else random.randint(45, 120)
                    total_time += time_spent
                    
                    # Submit answer
                    submit_response = requests.post(f'{base_url}/submit-answer/', json={
                        'session_id': session_id,
                        'question_id': question_data.get('question_id'),
                        'selected_answer': answer_choice,
                        'time_spent': time_spent
                    })
                    
                    if submit_response.status_code == 200:
                        submit_data = submit_response.json()
                        actual_correct = submit_data.get('is_correct', False)
                        if actual_correct:
                            correct_count += 1
                        
                        status_icon = "✅" if actual_correct else "❌"
                        print(f"   Q{i+1:2d}: {answer_choice} {status_icon} ({time_spent:2d}s) - {question_data.get('difficulty', 'medium')}")
                    else:
                        print(f"   Q{i+1:2d}: Failed to submit answer")
                
            # Complete the session with accurate data
            print(f"\n3. Completing session...")
            print(f"   Final Score: {correct_count}/{len(questions_data)} ({correct_count/len(questions_data)*100:.1f}%)")
            print(f"   Total Time: {total_time}s ({total_time//60}m {total_time%60}s)")
            
            completion_data = {
                'session_id': session_id,
                'total_questions': len(questions_data),
                'correct_answers': correct_count,
                'session_duration_seconds': total_time,
                'final_mastery_level': correct_count / len(questions_data) if questions_data else 0.0,
                'student_username': 'dash'  # Important: use the actual username
            }
            
            complete_response = requests.post(f'{base_url}/complete-session/', json=completion_data)
            if complete_response.status_code == 200:
                complete_result = complete_response.json()
                completed_session_id = complete_result.get('session_data', {}).get('session_id')
                print(f"✅ Session completed: {completed_session_id}")
                
                # Verify the session appears in history
                print(f"\n4. Verifying session in history...")
                history_url = f'http://127.0.0.1:8000/api/history/students/dash/history'
                history_response = requests.get(history_url)
                
                if history_response.status_code == 200:
                    history_data = history_response.json()
                    print(f"✅ History retrieved: {len(history_data)} sessions found")
                    
                    # Find our session
                    our_session = None
                    for session in history_data:
                        if session['session_id'] == completed_session_id:
                            our_session = session
                            break
                    
                    if our_session:
                        print(f"✅ Our session found in history:")
                        print(f"   Name: {our_session['session_name']}")
                        print(f"   Score: {our_session['questions_correct']}/{our_session['questions_attempted']} ({our_session['percentage_score']:.1f}%)")
                        print(f"   Grade: {our_session['grade']}")
                        print(f"   Duration: {our_session['session_duration_seconds']}s")
                        
                        # Test detailed view
                        print(f"\n5. Testing detailed assessment view...")
                        detail_url = f'http://127.0.0.1:8000/api/history/students/dash/assessment/{completed_session_id}'
                        detail_response = requests.get(detail_url)
                        
                        if detail_response.status_code == 200:
                            detail_data = detail_response.json()
                            question_attempts = detail_data.get('question_attempts', [])
                            print(f"✅ Detailed view working: {len(question_attempts)} question attempts found")
                            
                            if question_attempts:
                                actual_correct = sum(1 for q in question_attempts if q['is_correct'])
                                print(f"   Question breakdown: {actual_correct}/{len(question_attempts)} correct")
                                
                                # Show performance by topic
                                topics = detail_data.get('performance_analysis', {}).get('topics_performance', {})
                                print(f"   Topics analyzed: {len(topics)}")
                                for topic, perf in topics.items():
                                    print(f"     {topic}: {perf['correct']}/{perf['total']} ({perf['accuracy']:.1f}%)")
                            
                            print(f"\n🎉 SUCCESS! Comprehensive test session created!")
                            print(f"📱 Frontend should now show:")
                            print(f"   • History card: {our_session['questions_correct']}/{our_session['questions_attempted']} correct")
                            print(f"   • Detailed view: Full question-by-question breakdown")
                            print(f"   • Performance analysis: Topic-wise breakdown")
                            
                            return completed_session_id
                        else:
                            print(f"❌ Detailed view failed: {detail_response.status_code}")
                    else:
                        print(f"❌ Session not found in history")
                else:
                    print(f"❌ History retrieval failed: {history_response.status_code}")
            else:
                print(f"❌ Session completion failed: {complete_response.text}")
                return None
        else:
            print(f"❌ Session start failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == '__main__':
    session_id = create_comprehensive_test_session()
    if session_id:
        print(f"\n✨ Test completed successfully!")
        print(f"🔍 Session ID: {session_id}")
        print(f"💻 Now check the frontend history view!")
    else:
        print(f"\n💥 Test failed")