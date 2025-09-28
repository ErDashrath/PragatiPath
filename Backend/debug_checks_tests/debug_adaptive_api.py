"""
Simple debug test for adaptive API endpoints
"""
import requests
import json

def test_simple_endpoint():
    """Test a simple endpoint to debug 500 errors"""
    
    print("🔍 Debug Test for Adaptive API")
    print("=" * 40)
    
    # Test the health endpoint first
    try:
        response = requests.get("http://localhost:8000/api/health")
        print(f"Health endpoint status: {response.status_code}")
        if response.status_code == 200:
            print(f"Health response: {response.json()}")
    except Exception as e:
        print(f"Health endpoint error: {e}")
    
    print("\n" + "-" * 40)
    
    # Test imports first
    try:
        response = requests.post("http://localhost:8000/api/v1/adaptive/test-imports/", json={})
        print(f"Import test status: {response.status_code}")
        print(f"Import test response: {response.text}")
    except Exception as e:
        print(f"Import test error: {e}")
    
    print("\n" + "-" * 40)
    
    # Test simple adaptive logic
    try:
        response = requests.post("http://localhost:8000/api/v1/adaptive/test-adaptive/", 
                               json={"user_id": 83, "subject_id": "quantitative_aptitude"})
        print(f"Adaptive test status: {response.status_code}")
        print(f"Adaptive test response: {response.text}")
    except Exception as e:
        print(f"Adaptive test error: {e}")
    
    print("\n" + "-" * 40)
    
    # Test minimal endpoint
    try:
        response = requests.post("http://localhost:8000/api/v1/adaptive/minimal-question/", 
                               json={"user_id": 83, "subject_id": "quantitative_aptitude"})
        print(f"Minimal question status: {response.status_code}")
        print(f"Minimal question response: {response.text}")
    except Exception as e:
        print(f"Minimal question error: {e}")
    
    print("\n" + "-" * 40)
    
    # Test our adaptive endpoint with minimal data
    test_data = {
        "session_id": "debug_session",
        "user_id": 83,
        "subject_id": "quantitative_aptitude"  # Try with subject code instead of ID
    }
    
    print(f"Testing adaptive endpoint with data: {test_data}")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/adaptive/next-question/",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 500:
            print("🔥 Server Error - Check Django logs for details")
        
    except Exception as e:
        print(f"Request error: {e}")

if __name__ == "__main__":
    test_simple_endpoint()