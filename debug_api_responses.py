#!/usr/bin/env python
"""
Debug script to see API responses
"""
import requests
import json

def debug_api():
    print("🔍 API Response Debug")
    print("=" * 30)
    
    # Start session
    print("1. Starting session...")
    try:
        response = requests.post("http://localhost:8000/simple/start-session/", 
                                json={"student_name": "debuguser", "question_count": 3})
        print(f"Start Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Start Response: {response.text}")
            return
            
        session_data = response.json()
        session_id = session_data['session_id']
        print(f"Session ID: {session_id}")
        print(f"Full Start Response: {json.dumps(session_data, indent=2)}")
        
        # Get question
        print(f"\n2. Getting question...")
        q_resp = requests.get(f"http://localhost:8000/simple/get-question/{session_id}/")
        print(f"Question Status: {q_resp.status_code}")
        print(f"Question Response: {q_resp.text}")
        
        if q_resp.status_code == 200:
            try:
                q_data = q_resp.json()
                print(f"Question JSON: {json.dumps(q_data, indent=2)}")
            except Exception as e:
                print(f"JSON Parse Error: {e}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_api()