#!/usr/bin/env python3
"""
Test Frontend-Backend Integration for Adaptive Learning
This script tests if the frontend can communicate with the backend's /simple/ endpoints.
"""

import requests
import json
import time

# Test configuration
FRONTEND_URL = "http://localhost:5000"
BACKEND_URL = "http://localhost:8000"

def test_frontend_proxy():
    """Test if frontend can proxy to backend /simple/ endpoints"""
    print("🧪 Testing Frontend-Backend Integration")
    print("=" * 50)
    
    try:
        # Test 1: Health check through frontend proxy
        print("1️⃣ Testing health check through frontend proxy...")
        response = requests.get(f"{FRONTEND_URL}/simple/health/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Frontend proxy working: {data.get('message', 'OK')}")
        else:
            print(f"   ❌ Frontend proxy failed: {response.text}")
            return False
        
        # Test 2: Start session through frontend proxy
        print("\n2️⃣ Testing start session through frontend proxy...")
        session_data = {
            "student_name": "Test Student",
            "subject": "quantitative_aptitude",
            "question_count": 10
        }
        
        response = requests.post(
            f"{FRONTEND_URL}/simple/start-session/",
            headers={"Content-Type": "application/json"},
            data=json.dumps(session_data)
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            session_result = response.json()
            print(f"   ✅ Session started: {session_result.get('session_id', 'No ID')}")
            session_id = session_result.get('session_id')
            
            # Test 3: Get question through frontend proxy
            if session_id:
                print("\n3️⃣ Testing get question through frontend proxy...")
                response = requests.get(f"{FRONTEND_URL}/simple/get-question/{session_id}/")
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    question_data = response.json()
                    print(f"   ✅ Got question: {question_data.get('question_text', 'No question')[:50]}...")
                    
                    # Test 4: Submit answer through frontend proxy
                    print("\n4️⃣ Testing submit answer through frontend proxy...")
                    answer_data = {
                        "session_id": session_id,
                        "question_id": question_data.get('question_id'),
                        "selected_answer": "A",
                        "time_spent": 15.0
                    }
                    
                    response = requests.post(
                        f"{FRONTEND_URL}/simple/submit-answer/",
                        headers={"Content-Type": "application/json"},
                        data=json.dumps(answer_data)
                    )
                    
                    print(f"   Status: {response.status_code}")
                    if response.status_code == 200:
                        answer_result = response.json()
                        print(f"   ✅ Answer submitted: {answer_result.get('message', 'OK')}")
                        return True
                    else:
                        print(f"   ❌ Submit answer failed: {response.text[:100]}...")
                        return False
                else:
                    print(f"   ❌ Get question failed: {response.text[:100]}...")
                    return False
            else:
                print("   ❌ No session ID returned")
                return False
        else:
            print(f"   ❌ Start session failed: {response.text[:100]}...")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_backend_direct():
    """Test backend endpoints directly (for comparison)"""
    print("\n🔧 Testing Backend Direct Connection")
    print("=" * 50)
    
    try:
        # Test direct backend health
        response = requests.get(f"{BACKEND_URL}/simple/health/")
        print(f"Direct backend health: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend direct: {data.get('message', 'OK')}")
            return True
        else:
            print(f"❌ Backend direct failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Backend direct test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Adaptive Learning Frontend-Backend Integration")
    print(f"Frontend URL: {FRONTEND_URL}")
    print(f"Backend URL: {BACKEND_URL}")
    print()
    
    # Test backend direct first
    backend_ok = test_backend_direct()
    
    # Test frontend proxy
    frontend_ok = test_frontend_proxy()
    
    print("\n" + "=" * 50)
    print("📊 INTEGRATION TEST RESULTS")
    print("=" * 50)
    print(f"Backend Direct:  {'✅ WORKING' if backend_ok else '❌ FAILED'}")
    print(f"Frontend Proxy:  {'✅ WORKING' if frontend_ok else '❌ FAILED'}")
    
    if backend_ok and frontend_ok:
        print("\n🎉 SUCCESS: Frontend can communicate with backend!")
        print("   The adaptive learning interface should work properly.")
        print("   You can now use the Adaptive Learning feature in the frontend.")
    elif backend_ok:
        print("\n⚠️  Backend is working but frontend proxy has issues.")
        print("   Check the frontend proxy configuration in routes.ts")
    else:
        print("\n❌ Backend is not responding. Check if Django server is running on port 8000.")
        
    print(f"\n🌐 Visit: {FRONTEND_URL} to test the frontend interface")