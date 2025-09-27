#!/usr/bin/env python3
"""
Debug the session completion issue
"""
import requests
import json

def debug_session_completion():
    base_url = 'http://127.0.0.1:8000/simple'
    
    print("🔍 Debugging Session Completion")
    print("=" * 40)
    
    # Create a simple session
    session_data = {
        'student_name': 'debug_user',
        'subject': 'quantitative_aptitude',
        'question_count': 2
    }
    
    print("1. Starting debug session...")
    response = requests.post(f'{base_url}/start-session/', json=session_data)
    if response.status_code == 200:
        result = response.json()
        session_id = result['session_id']
        print(f"✅ Session started: {session_id}")
        
        # Get and answer one question
        print("\n2. Getting and answering one question...")
        question_response = requests.get(f'{base_url}/get-question/{session_id}/')
        if question_response.status_code == 200:
            question_data = question_response.json()
            print(f"   Question received: {question_data.get('question_id')}")
            
            # Submit answer
            submit_response = requests.post(f'{base_url}/submit-answer/', json={
                'session_id': session_id,
                'question_id': question_data.get('question_id'),
                'selected_answer': 'A',
                'time_spent': 30
            })
            
            if submit_response.status_code == 200:
                print("   Answer submitted successfully")
                
                # Try to complete session
                print("\n3. Attempting to complete session...")
                completion_data = {
                    'session_id': session_id,
                    'total_questions': 1,
                    'correct_answers': 0,
                    'session_duration_seconds': 30,
                    'final_mastery_level': 0.0,
                    'student_username': 'debug_user'
                }
                
                complete_response = requests.post(f'{base_url}/complete-session/', json=completion_data)
                print(f"   Status: {complete_response.status_code}")
                print(f"   Response: {complete_response.text}")
                
                if complete_response.status_code == 200:
                    complete_result = complete_response.json()
                    print(f"✅ Completion successful!")
                    session_id = complete_result.get('session_data', {}).get('session_id')
                    print(f"   New session ID: {session_id}")
                    return session_id
                else:
                    print(f"❌ Completion failed")
                    return None
    
    return None

if __name__ == '__main__':
    session_id = debug_session_completion()
    if session_id:
        print(f"\n✅ Debug successful! Session: {session_id}")
    else:
        print(f"\n❌ Debug failed!")