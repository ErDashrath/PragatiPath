#!/usr/bin/env python3
"""
Quick API Test - Check what the simple API returns
"""

import requests
import json

def test_simple_api():
    base_url = "http://localhost:8000"
    
    print("🔍 Testing Simple API Endpoints...")
    
    # 1. Start session
    print("\n1. Testing start-session...")
    try:
        response = requests.post(f"{base_url}/simple/start-session/", 
            json={"student_name": "Test", "subject": "quantitative_aptitude"})
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            session_id = data.get('session_id')
            print(f"Session ID: {session_id}")
            
            # 2. Get question
            if session_id:
                print(f"\n2. Testing get-question/{session_id}...")
                q_response = requests.get(f"{base_url}/simple/get-question/{session_id}/")
                print(f"Status: {q_response.status_code}")
                if q_response.status_code == 200:
                    q_data = q_response.json()
                    print(f"Question response keys: {list(q_data.keys())}")
                    print(f"Question data structure:")
                    print(json.dumps(q_data, indent=2)[:500])
                else:
                    print(f"Error: {q_response.text}")
                
                # 3. Test submit answer
                if q_response.status_code == 200:
                    print(f"\n3. Testing submit-answer...")
                    submit_data = {
                        "session_id": session_id,
                        "question_id": q_data['question_id'],
                        "selected_answer": q_data['options'][0]['id'],
                        "response_time": 5.0
                    }
                    s_response = requests.post(f"{base_url}/simple/submit-answer/", json=submit_data)
                    print(f"Status: {s_response.status_code}")
                    if s_response.status_code == 200:
                        s_data = s_response.json()
                        print(f"Submit response keys: {list(s_data.keys())}")
                        print(f"Submit response:")
                        print(json.dumps(s_data, indent=2)[:500])
                    else:
                        print(f"Error: {s_response.text}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_simple_api()