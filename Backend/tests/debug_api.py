"""
Debug script to inspect API responses
"""

import requests
import json

BASE_URL = 'http://localhost:8000'

def debug_subjects_endpoint():
    """Debug the subjects endpoint"""
    print("🔍 Debugging GET /api/assessment/v1/subjects")
    
    try:
        response = requests.get(f"{BASE_URL}/api/assessment/v1/subjects")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response type: {type(data)}")
            print(f"Response data: {json.dumps(data, indent=2)}")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_subjects_endpoint()