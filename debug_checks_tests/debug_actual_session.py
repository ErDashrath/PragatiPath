#!/usr/bin/env python3

import requests
import json

def debug_actual_session():
    """Debug the actual session being used in the UI"""
    
    print("🔍 DEBUGGING ACTUAL SESSION FROM CONSOLE LOGS")
    print("=" * 50)
    
    # From the console logs, the actual session ID being used
    session_id = "3fe3d9c3-7a73-463f-9d98-9a8406bc334f"
    
    print(f"📝 Testing session ID from console: {session_id}")
    
    # Test all the endpoints that are failing
    endpoints_to_test = [
        f"http://localhost:8000/history/session-details/{session_id}/",
        f"http://localhost:8000/api/history/students/dash/assessment/{session_id}",
        f"http://localhost:5000/history/session-details/{session_id}/",
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\n🔍 Testing: {endpoint}")
        
        try:
            response = requests.get(endpoint)
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
            
            if response.headers.get('content-type', '').startswith('application/json'):
                try:
                    data = response.json()
                    print(f"   ✅ Valid JSON response")
                    if 'success' in data:
                        print(f"   Success: {data.get('success')}")
                    if 'session_details' in data:
                        session_details = data['session_details']
                        print(f"   Session: {session_details.get('session_name', 'Unknown')}")
                except Exception as json_error:
                    print(f"   ❌ JSON parsing failed: {json_error}")
            else:
                print(f"   ❌ HTML response: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
    
    # Check what user IDs have sessions
    print(f"\n🔍 Looking for user with this session...")
    for user_id in ["69", "1", "2", "demo", "student_dashrath"]:
        try:
            url = f"http://localhost:8000/simple/session-history/{user_id}/"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('sessions'):
                    sessions = data['sessions']
                    matching_session = next((s for s in sessions if s.get('session_id') == session_id), None)
                    
                    if matching_session:
                        print(f"✅ Found session for user ID '{user_id}'!")
                        print(f"   Session: {matching_session.get('session_name')}")
                        print(f"   Questions: {matching_session.get('questions_attempted')}")
                        print(f"   Accuracy: {matching_session.get('accuracy')}%")
                        return user_id
                        
        except Exception as e:
            continue
    
    print(f"\n❌ Session {session_id} not found for any user ID tested")
    return None

if __name__ == "__main__":
    user_id = debug_actual_session()
    
    if user_id:
        print(f"\n💡 The localStorage should have:")
        print(f"   'pragatipath_backend_user_id': '{user_id}'")
    else:
        print(f"\n💡 Next steps:")
        print(f"1. Check localStorage for 'pragatipath_backend_user_id'")
        print(f"2. Create a fresh adaptive session")
        print(f"3. Note which user ID it gets stored under")