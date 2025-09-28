#!/usr/bin/env python3
"""
Test the fixed submission system
"""

import requests
import json

def test_submission_fix():
    print("🧪 Testing Fixed Submission System...")
    print("=" * 50)
    
    try:
        # Start session
        print("1. Starting session...")
        session_response = requests.post('http://localhost:8000/simple/start-session/', json={
            'student_name': 'Test User Fixed', 
            'subject': 'quantitative_aptitude'
        })
        
        print(f"   Status: {session_response.status_code}")
        if session_response.status_code != 200:
            print(f"   Error: {session_response.text}")
            return
            
        session_data = session_response.json()
        session_id = session_data['session_id']
        print(f"   ✅ Session: {session_id}")
        
        # Get question
        print("2. Getting question...")
        question_response = requests.get(f'http://localhost:8000/simple/get-question/{session_id}/')
        print(f"   Status: {question_response.status_code}")
        if question_response.status_code != 200:
            print(f"   Error: {question_response.text}")
            return
            
        question_data = question_response.json()
        question_id = question_data['question_id']
        print(f"   ✅ Question: {question_id}")
        print(f"   Subject: {question_data.get('subject_display', 'Unknown')}")
        print(f"   Difficulty: {question_data.get('difficulty_display', 'Unknown')}")
        
        # Submit answer - THIS IS WHERE THE ERROR WAS HAPPENING
        print("3. Submitting answer...")
        submit_data = {
            'session_id': session_id,
            'question_id': question_id,
            'selected_answer': 'A',
            'time_spent': 25.5
        }
        
        print(f"   Sending: {submit_data}")
        submit_response = requests.post('http://localhost:8000/simple/submit-answer/', 
                                     json=submit_data)
        print(f"   Status: {submit_response.status_code}")
        
        if submit_response.status_code == 200:
            submit_result = submit_response.json()
            print(f"   ✅ Submission successful!")
            print(f"   Answer Correct: {submit_result.get('answer_correct', False)}")
            print(f"   Mastery Level: {submit_result.get('knowledge_update', {}).get('mastery_display', 'Unknown')}")
            print(f"   Session Accuracy: {submit_result.get('session_progress', {}).get('accuracy', 'Unknown')}")
            print(f"   Adaptation: {submit_result.get('adaptive_feedback', {}).get('difficulty_adaptation', 'Unknown')}")
            
            print("\n🎉 SUBMISSION ISSUE FIXED! ✅")
            
        else:
            print(f"   ❌ Submission failed!")
            print(f"   Response: {submit_response.text}")
            
            # Let's see the full response for debugging
            try:
                error_data = submit_response.json()
                print(f"   Error details: {error_data}")
            except:
                print(f"   Raw response: {submit_response.text}")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")

if __name__ == "__main__":
    test_submission_fix()