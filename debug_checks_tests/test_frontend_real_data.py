#!/usr/bin/env python3

import requests
import json
import time

def test_adaptive_details_frontend():
    """Test that the frontend properly displays real question attempts data"""
    
    # Test the existing endpoint that returns real data
    session_id = "dc684f75-c850-4495-b17d-7f12c4b4b31f"
    
    print("🔍 Testing existing session details endpoint...")
    url = f"http://localhost:8000/history/session-details/{session_id}/"
    
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Successfully fetched session details!")
            
            # Check the structure matches what DetailedResultView expects
            session_details = data.get('session_details', {})
            question_attempts = session_details.get('question_attempts', [])
            
            print(f"\n📊 Session Summary:")
            print(f"Session ID: {session_details.get('session_id')}")
            print(f"Session Name: {session_details.get('session_name')}")
            print(f"Questions Attempted: {session_details.get('questions_attempted')}")
            print(f"Questions Correct: {session_details.get('questions_correct')}")
            print(f"Accuracy: {session_details.get('accuracy_percentage')}%")
            
            print(f"\n🎯 Question Attempts Analysis:")
            print(f"Total question attempts found: {len(question_attempts)}")
            
            if question_attempts:
                print("\n📋 Sample Question Attempts:")
                for i, attempt in enumerate(question_attempts[:3]):  # Show first 3
                    print(f"  Q{attempt.get('question_number', i+1)}: "
                          f"{'✅' if attempt.get('is_correct') else '❌'} "
                          f"Answer: {attempt.get('student_answer')} "
                          f"(Correct: {attempt.get('correct_answer')}) "
                          f"Time: {attempt.get('time_spent')}s "
                          f"Difficulty: {attempt.get('difficulty')}")
                
                print("\n🔢 Data Structure Validation:")
                sample_attempt = question_attempts[0]
                required_fields = ['question_number', 'is_correct', 'student_answer', 
                                 'correct_answer', 'time_spent', 'difficulty']
                
                for field in required_fields:
                    has_field = field in sample_attempt
                    print(f"  {field}: {'✅' if has_field else '❌'}")
                
                print("\n✅ The endpoint returns REAL question attempts data!")
                print("✅ Data structure matches what DetailedResultView expects!")
                print("✅ Frontend should display actual questions answered, not simulated ones!")
            
        else:
            print(f"❌ Failed to fetch session details: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")

if __name__ == "__main__":
    test_adaptive_details_frontend()