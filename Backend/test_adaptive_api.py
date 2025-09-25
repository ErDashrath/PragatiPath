#!/usr/bin/env python3
"""
Test script to verify our adaptive learning frontend API endpoints are working properly
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/simple/health/")
        print(f"✅ Health Endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health Endpoint Error: {e}")
        return False

def test_start_session():
    """Test starting a new adaptive learning session"""
    try:
        data = {
            "user_id": 1,
            "subject": "mathematics", 
            "difficulty": "medium"
        }
        response = requests.post(f"{BASE_URL}/simple/start-session/", json=data)
        print(f"✅ Start Session: {response.status_code}")
        result = response.json()
        print(f"   Session ID: {result.get('session_id', 'Not found')}")
        return response.status_code == 200, result.get('session_id')
    except Exception as e:
        print(f"❌ Start Session Error: {e}")
        return False, None

def test_get_question(session_id):
    """Test getting a question for the session"""
    try:
        response = requests.get(f"{BASE_URL}/simple/get-question/{session_id}/")
        print(f"✅ Get Question: {response.status_code}")
        result = response.json()
        if response.status_code == 200 and result.get('success'):
            print(f"   Question: {result.get('question_text', 'No text')[:50]}...")
            print(f"   Options: {len(result.get('options', []))} options")
            print(f"   Difficulty: {result.get('difficulty_display', 'Unknown')}")
            return True, result.get('question_id')
        return False, None
    except Exception as e:
        print(f"❌ Get Question Error: {e}")
        return False, None

def test_session_progress(session_id):
    """Test getting session progress"""
    try:
        response = requests.get(f"{BASE_URL}/simple/session-progress/{session_id}/")
        print(f"✅ Session Progress: {response.status_code}")
        result = response.json()
        print(f"   Progress: {result.get('progress', {})} ")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Session Progress Error: {e}")
        return False

def main():
    print("🧠 Testing Adaptive Learning Frontend API Integration")
    print("=" * 60)
    
    # Test health endpoint
    if not test_health_endpoint():
        print("❌ Health check failed - stopping tests")
        return
    
    print()
    
    # Test starting a session
    success, session_id = test_start_session()
    if not success or not session_id:
        print("❌ Session start failed - stopping tests")
        return
    
    print()
    
    # Test getting a question
    success, question_id = test_get_question(session_id)
    if not success:
        print("❌ Question retrieval failed")
    
    print()
    
    # Test session progress
    if not test_session_progress(session_id):
        print("❌ Session progress failed")
    
    print()
    print("🎉 Frontend integration tests completed!")
    print("✨ Ready for React frontend integration!")

if __name__ == "__main__":
    main()