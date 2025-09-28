#!/usr/bin/env python3

import requests

def test_endpoint_routing():
    """Test the exact routing issue"""
    
    print("🔍 TESTING ENDPOINT ROUTING ISSUE")
    print("=" * 40)
    
    session_id = "dc684f75-c850-4495-b17d-7f12c4b4b31f"
    
    print("1️⃣ Testing Backend Direct:")
    backend_url = f"http://localhost:8000/history/session-details/{session_id}/"
    try:
        response = requests.get(backend_url)
        print(f"Backend Status: {response.status_code}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            print("✅ Backend returns JSON")
            data = response.json()
            print(f"Success: {data.get('success')}")
        else:
            print("❌ Backend returns HTML!")
            print(f"Content-Type: {response.headers.get('content-type')}")
            print(f"Response start: {response.text[:100]}")
    except Exception as e:
        print(f"Backend error: {e}")
    
    print("\n2️⃣ Testing Frontend Proxy:")
    frontend_url = f"http://localhost:5000/history/session-details/{session_id}/"
    try:
        response = requests.get(frontend_url)
        print(f"Frontend Status: {response.status_code}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            print("✅ Frontend returns JSON")
        else:
            print("❌ Frontend returns HTML!")
            print(f"Content-Type: {response.headers.get('content-type')}")
            print(f"Response start: {response.text[:100]}")
    except Exception as e:
        print(f"Frontend error: {e}")
    
    print("\n🎯 SOLUTION:")
    print("The frontend request is not being proxied correctly.")
    print("Need to check the Vite proxy configuration.")

if __name__ == "__main__":
    test_endpoint_routing()