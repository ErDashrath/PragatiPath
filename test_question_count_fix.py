#!/usr/bin/env python3
"""
Test the fixed question count functionality
"""
import requests
import json
import time

def test_question_count_fix():
    base_url = 'http://127.0.0.1:8000/simple'
    
    print("🧪 Testing Question Count Fix")
    print("=" * 50)
    
    # Test 1: Start session with 10 questions
    print("\n1. Starting session with 10 questions...")
    
    session_data = {
        'student_name': 'Test Student Question Count',
        'subject': 'quantitative_aptitude',
        'question_count': 10
    }
    
    try:
        response = requests.post(f'{base_url}/start-session/', json=session_data)
        if response.status_code == 200:
            result = response.json()
            session_id = result['session_id']
            print(f"✅ Session started: {session_id}")
            print(f"   Subject: {result['subject']}")
            
            # Test 2: Verify session has correct question count in database
            # We can't directly check the database here, so let's test by getting questions
            print(f"\n2. Testing question retrieval (should get exactly 10 questions)...")
            
            questions_received = 0
            for i in range(15):  # Try to get 15 questions but should stop at 10
                try:
                    question_response = requests.get(f'{base_url}/get-question/{session_id}/')
                    if question_response.status_code == 200:
                        question_data = question_response.json()
                        if question_data.get('session_complete'):
                            print(f"🎯 Session completed after {questions_received} questions!")
                            print(f"   Message: {question_data.get('message')}")
                            break
                        else:
                            questions_received += 1
                            print(f"   Question {questions_received}: {question_data.get('question_text', 'N/A')[:50]}...")
                            
                            # Submit a dummy answer to move to next question
                            submit_response = requests.post(f'{base_url}/submit-answer/', json={
                                'session_id': session_id,
                                'question_id': question_data.get('question_id'),
                                'selected_answer': 'A',
                                'time_spent': 5
                            })
                            
                            if submit_response.status_code == 200:
                                submit_data = submit_response.json()
                                print(f"     Answer submitted - Correct: {submit_data.get('is_correct', False)}")
                            
                    else:
                        print(f"❌ Failed to get question {i+1}: {question_response.status_code}")
                        break
                        
                except Exception as e:
                    print(f"❌ Error getting question {i+1}: {e}")
                    break
                    
                # Small delay between questions
                time.sleep(0.1)
            
            print(f"\n3. Testing Results:")
            print(f"   Questions requested: 10")
            print(f"   Questions received: {questions_received}")
            
            if questions_received == 10:
                print("✅ SUCCESS: Correct number of questions delivered!")
            else:
                print(f"❌ FAILURE: Expected 10 questions but got {questions_received}")
                
            return questions_received == 10
                
        else:
            print(f"❌ Failed to start session: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

if __name__ == '__main__':
    success = test_question_count_fix()
    if success:
        print("\n🎉 All tests passed! Question count fix is working correctly.")
    else:
        print("\n💥 Tests failed! Question count fix needs more work.")