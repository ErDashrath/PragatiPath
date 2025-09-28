#!/usr/bin/env python
"""
Quick test to verify the endpoints are working correctly.
"""
import requests
import json

def test_endpoints():
    """Test API endpoints directly"""
    print("Testing API Endpoints...")
    
    # Test start session
    print("\n1. Testing start session...")
    try:
        response = requests.post("http://localhost:8000/simple/start-session/", json={
            "student_name": "test_user_direct",
            "question_count": 10
        })
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            session_id = data['session_id']
            print(f"✅ Session started: {session_id}")
            
            # Test get question
            print("\n2. Testing get question...")
            q_response = requests.get(f"http://localhost:8000/simple/get-question/{session_id}/")
            print(f"Question Status: {q_response.status_code}")
            if q_response.status_code == 200:
                q_data = q_response.json()
                print(f"✅ Question retrieved: {q_data['question']['id']}")
            else:
                print(f"❌ Question failed: {q_response.text[:200]}")
                
        else:
            print(f"❌ Start session failed: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test history endpoint
    print("\n3. Testing history endpoint...")
    try:
        h_response = requests.get("http://localhost:8000/history/student/test_user_direct/")
        print(f"History Status: {h_response.status_code}")
        if h_response.status_code == 200:
            h_data = h_response.json()
            print(f"✅ History retrieved: {len(h_data.get('sessions', []))} sessions")
        else:
            print(f"❌ History failed: {h_response.text[:200]}")
    except Exception as e:
        print(f"❌ History error: {e}")

if __name__ == "__main__":
    test_endpoints()