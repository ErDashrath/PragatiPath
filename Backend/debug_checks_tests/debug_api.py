"""
Simple debug test for adaptive API
"""
import requests
import json

def test_simple_endpoint():
    url = "http://localhost:8000/api/v1/adaptive/next-question/"
    
    data = {
        "session_id": "debug_session",
        "user_id": 83,
        "subject_id": 9,
        "chapter_id": 52
    }
    
    try:
        print("Testing endpoint:", url)
        print("Data:", json.dumps(data, indent=2))
        
        response = requests.post(
            url,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_simple_endpoint()