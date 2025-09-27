#!/usr/bin/env python3
"""
Create a detailed test session with proper QuestionAttempts for testing the detailed view
"""
import requests
import json
import random

def create_detailed_test_session():
    base_url = 'http://127.0.0.1:8000/simple'
    
    print("🔬 Creating Detailed Test Session")
    print("=" * 50)
    
    # Start a session for the 'dash' user (who is likely logged in)
    session_data = {
        'student_name': 'dash',  # Use existing user
        'subject': 'quantitative_aptitude',
        'question_count': 8  # Create 8 questions for good test data
    }
    
    print("1. Starting detailed test session...")
    try:
        response = requests.post(f'{base_url}/start-session/', json=session_data)
        if response.status_code == 200:
            result = response.json()
            session_id = result['session_id']
            print(f"✅ Session started: {session_id}")
            
            # Answer all questions with varying performance
            questions_data = []
            correct_count = 0
            
            print("\n2. Answering questions with realistic performance...")
            
            for i in range(8):
                # Get question
                question_response = requests.get(f'{base_url}/get-question/{session_id}/')
                if question_response.status_code == 200:
                    question_data = question_response.json()
                    if question_data.get('session_complete'):
                        print(f"Session completed after {i} questions")
                        break
                        
                    questions_data.append(question_data)
                    
                    # Simulate realistic answers (70% correct rate)
                    is_correct_attempt = random.random() < 0.7
                    answer_choice = 'A' if is_correct_attempt else random.choice(['B', 'C', 'D'])
                    time_spent = random.randint(15, 120)  # 15-120 seconds per question
                    
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
                        print(f"   Q{i+1}: {answer_choice} ({'✓' if actual_correct else '✗'}) - {time_spent}s")
                    else:
                        print(f"   Q{i+1}: Failed to submit answer")
                
            # Complete the session
            print(f"\n3. Completing session with {correct_count}/{len(questions_data)} correct...")
            
            completion_data = {
                'session_id': session_id,
                'total_questions': len(questions_data),
                'correct_answers': correct_count,
                'session_duration_seconds': sum(random.randint(15, 120) for _ in range(len(questions_data))),
                'final_mastery_level': correct_count / len(questions_data) if questions_data else 0.0,
                'student_username': 'dash'
            }
            
            complete_response = requests.post(f'{base_url}/complete-session/', json=completion_data)
            if complete_response.status_code == 200:
                complete_result = complete_response.json()
                completed_session_id = complete_result.get('session_data', {}).get('session_id')
                print(f"✅ Session completed and saved: {completed_session_id}")
                
                # Test the detailed view API
                print(f"\n4. Testing detailed assessment API...")
                detail_url = f'http://127.0.0.1:8000/api/history/students/dash/assessment/{completed_session_id}'
                detail_response = requests.get(detail_url)
                
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    session_info = detail_data.get('session_info', {})
                    question_attempts = detail_data.get('question_attempts', [])
                    performance_analysis = detail_data.get('performance_analysis', {})
                    
                    print(f"✅ Detailed view data retrieved successfully!")
                    print(f"   Session: {session_info.get('session_name')} - Grade {session_info.get('grade')}")
                    print(f"   Accuracy: {session_info.get('percentage_score', 0):.1f}%")
                    print(f"   Question Details: {len(question_attempts)} attempts recorded")
                    print(f"   Performance Analysis: {len(performance_analysis.get('topics_performance', {}))} topics")
                    print(f"   Recommendations: {len(detail_data.get('recommendations', []))} suggestions")
                    
                    # Show sample question details
                    if question_attempts:
                        sample_q = question_attempts[0]
                        print(f"\n   Sample Question Detail:")
                        print(f"     Topic: {sample_q.get('topic', 'N/A')}")
                        print(f"     Difficulty: {sample_q.get('difficulty_level', 'N/A')}")
                        print(f"     Correct: {sample_q.get('is_correct', False)}")
                        print(f"     Time: {sample_q.get('time_spent_seconds', 0)}s")
                    
                    return completed_session_id
                else:
                    print(f"❌ Failed to get detailed view: {detail_response.status_code}")
                    return completed_session_id
            else:
                print(f"❌ Failed to complete session: {complete_response.text}")
                return None
        else:
            print(f"❌ Failed to start session: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == '__main__':
    session_id = create_detailed_test_session()
    if session_id:
        print(f"\n🎯 Success! Test session created: {session_id}")
        print(f"📋 You can now test the detailed view in the frontend!")
        print(f"🔗 Try clicking 'Details' button for this session in the history view.")
    else:
        print(f"\n💥 Failed to create test session.")