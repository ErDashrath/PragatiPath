"""
Debug the enhanced API v2 endpoint to identify the 500 error
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def debug_enhanced_api():
    """Debug the enhanced API endpoint"""
    print("🔍 Debugging Enhanced API v2 Endpoint")
    print("="*50)
    
    # First, let's create a test student
    print("\n1. Creating test student...")
    response = requests.post(f"{BASE_URL}/api/core/students/", json={
        "username": f"debug_student_{int(time.time())}",
        "email": f"debug_{int(time.time())}@example.com",
        "first_name": "Debug",
        "last_name": "Student"
    })
    
    if response.status_code == 201:
        student_data = response.json()
        student_id = student_data['id']
        print(f"✅ Created student: {student_id}")
        
        # Now test the enhanced assessment endpoint
        print("\n2. Testing enhanced assessment start...")
        response = requests.post(f"{BASE_URL}/api/assessment/v2/assessment/start", json={
            "student_id": student_id,
            "subject": "quantitative_aptitude",
            "assessment_mode": "EXAM"
        })
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Enhanced API working correctly!")
        else:
            print(f"❌ Enhanced API error: {response.status_code}")
            
    else:
        print(f"❌ Failed to create student: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    import time
    debug_enhanced_api()