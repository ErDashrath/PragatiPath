#!/usr/bin/env python3
"""Test the correct session details endpoint"""

import requests
import json

def test_correct_endpoint():
    """Test the correct session details endpoint"""
    print("=" * 60)
    print("TESTING CORRECT SESSION DETAILS ENDPOINT")
    print("=" * 60)
    
    # Use a completed session ID from our database analysis
    test_session_id = 'f1831253a2b24bf6931ecb59be88292a'  # Data Interpretation session for user 'dash'
    
    # Test the correct endpoint
    backend_url = f'http://localhost:8000/history/session-details/{test_session_id}/'
    print(f"Testing: {backend_url}")
    
    try:
        response = requests.get(backend_url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n✅ SUCCESS! Response data:")
            print(f"   Success: {data.get('success', False)}")
            
            if data.get('session_details'):
                session = data['session_details']
                print(f"   Session ID: {session.get('session_id')}")
                print(f"   Session Name: {session.get('session_name')}")
                print(f"   Questions: {session.get('questions_correct')}/{session.get('questions_attempted')}")
                print(f"   Accuracy: {session.get('accuracy_percentage')}%")
                
                attempts = session.get('question_attempts', [])
                print(f"   Question Attempts: {len(attempts)}")
                
                if attempts:
                    print(f"\n📊 Sample attempts:")
                    for i, attempt in enumerate(attempts[:3]):
                        print(f"      {i+1}. Difficulty: {attempt.get('difficulty')} | Correct: {attempt.get('is_correct')}")
                
                return True
            else:
                print(f"   ❌ No session_details found")
                return False
        else:
            print(f"❌ Failed with status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_correct_endpoint()