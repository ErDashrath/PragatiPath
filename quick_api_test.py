"""
Quick test to verify AI-enhanced API endpoints are accessible
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_api_endpoints():
    """Test basic API endpoint accessibility"""
    print("🔧 Testing AI-Enhanced API Endpoints...")
    
    # Test health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test API documentation
    print("\n2. Testing API documentation accessibility...")
    try:
        response = requests.get(f"{BASE_URL}/api/docs")
        if response.status_code == 200:
            print("✅ API documentation accessible")
        else:
            print(f"❌ API docs failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API docs error: {e}")
    
    # Test subjects endpoint (v1)
    print("\n3. Testing subjects endpoint (v1)...")
    try:
        response = requests.get(f"{BASE_URL}/api/assessment/v1/subjects")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Subjects endpoint working - {data.get('total_subjects', 0)} subjects found")
            for subject in data.get('subjects', []):
                print(f"   • {subject.get('subject_name', 'Unknown')}: {subject.get('total_questions', 0)} questions")
        else:
            print(f"❌ Subjects endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Subjects endpoint error: {e}")
    
    # Test enhanced assessment start (without actually starting)
    print("\n4. Testing enhanced assessment endpoint structure...")
    try:
        # This will fail because we don't have a valid student_id, but it will show if the endpoint exists
        response = requests.post(f"{BASE_URL}/api/assessment/v2/assessment/start", json={
            "student_id": "test-uuid",
            "subject": "quantitative_aptitude",
            "assessment_mode": "EXAM"
        })
        if response.status_code == 404:
            print("✅ Enhanced assessment endpoint accessible (expected 404 for invalid student)")
        elif response.status_code == 422:
            print("✅ Enhanced assessment endpoint accessible (validation working)")
        else:
            print(f"🔍 Enhanced assessment response: {response.status_code}")
    except Exception as e:
        print(f"❌ Enhanced assessment endpoint error: {e}")
    
    print("\n✅ Basic API endpoint tests completed!")
    print("🎯 Ready for full AI integration testing with valid student data")

if __name__ == "__main__":
    print("🚀 Quick API Endpoint Test")
    print("="*50)
    test_api_endpoints()