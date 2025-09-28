#!/usr/bin/env python3

import requests
import json

def test_proxy_after_restart():
    """Test if the proxy is working after server restart"""
    
    print("🔍 TESTING PROXY AFTER SERVER RESTART")
    print("=" * 40)
    
    # Use the actual session ID from the console logs
    session_id = "3fe3d9c3-7a73-463f-9d98-9a8406bc334f"
    
    print("1️⃣ Testing Direct Backend:")
    backend_url = f"http://localhost:8000/history/session-details/{session_id}/"
    
    try:
        response = requests.get(backend_url)
        print(f"Backend Status: {response.status_code}")
        
        if response.status_code == 200 and response.headers.get('content-type', '').startswith('application/json'):
            data = response.json()
            print("✅ Backend returns valid JSON")
            print(f"Session: {data.get('session_details', {}).get('session_name', 'Unknown')}")
        else:
            print("❌ Backend issue")
            
    except Exception as e:
        print(f"❌ Backend error: {e}")
    
    print("\n2️⃣ Testing Frontend Proxy:")
    frontend_url = f"http://localhost:5000/history/session-details/{session_id}/"
    
    try:
        response = requests.get(frontend_url)
        print(f"Frontend Status: {response.status_code}")
        content_type = response.headers.get('content-type', '')
        print(f"Content-Type: {content_type}")
        
        if content_type.startswith('application/json'):
            try:
                data = response.json()
                print("✅ Frontend proxy returns valid JSON!")
                print(f"Session: {data.get('session_details', {}).get('session_name', 'Unknown')}")
                print("🎉 PROXY IS WORKING!")
                return True
            except:
                print("❌ JSON parsing failed")
        else:
            print("❌ Frontend still returns HTML")
            print(f"Response start: {response.text[:100]}")
            
    except Exception as e:
        print(f"❌ Frontend error: {e}")
    
    return False

if __name__ == "__main__":
    success = test_proxy_after_restart()
    
    if success:
        print("\n🎉 EXCELLENT!")
        print("The proxy is now working correctly!")
        print("The adaptive Details button should work now!")
        print("\n📝 Next step: Test the Details button in the UI")
    else:
        print("\n❌ Proxy still not working")
        print("💡 Possible issues:")
        print("1. Server needs to be restarted again")
        print("2. Code changes not applied")
        print("3. Check server logs for errors")