#!/usr/bin/env python3
"""
Test submission with existing session ID
"""

import requests
import json

def test_with_existing_session():
    # Use one of the existing session IDs from the debug output
    session_id = "81225db3-6d4d-489c-980d-b4aa7d93b3f6"  # From the session list
    question_id = "real_00a3ccb2-3391-4ebc-8c79-a0e17d72da60"  # We know this question exists
    
    print(f"🧪 Testing with existing session: {session_id}")
    print("=" * 60)
    
    # Test submission directly
    submit_data = {
        'session_id': session_id,
        'question_id': question_id,
        'selected_answer': 'A',
        'time_spent': 25.5
    }
    
    print(f"Submitting: {submit_data}")
    
    try:
        response = requests.post(
            'http://localhost:8000/simple/submit-answer/',
            json=submit_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {response.headers}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"Answer correct: {result.get('answer_correct')}")
            print(f"Message: {result.get('message')}")
        else:
            print("❌ FAILED!")
            print(f"Response text: {response.text}")
            
            # Try to parse as JSON for better error details
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print("Raw response (not JSON)")
                
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_with_existing_session()