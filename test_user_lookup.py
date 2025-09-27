#!/usr/bin/env python
"""
Check what users exist and test with the right username
"""
import requests
import json

def test_user_lookup():
    print("🔍 Testing User Lookup")
    print("=" * 30)
    
    # Test different username variations
    test_usernames = [
        "history_test_user",
        "student_history_test_user", 
        "student_testuser",
        "testuser"
    ]
    
    for username in test_usernames:
        print(f"\n Testing username: {username}")
        resp = requests.get(f"http://localhost:8000/history/student/{username}/")
        print(f"   Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get('success'):
                sessions_count = len(data.get('adaptive_sessions', [])) + len(data.get('assessment_sessions', []))
                print(f"   ✅ Found user with {sessions_count} sessions")
                
                if sessions_count > 0:
                    # Show recent session
                    recent = data.get('adaptive_sessions', data.get('assessment_sessions', [{}]))[0]
                    if recent:
                        print(f"   Recent session: {recent.get('questions_correct', 0)}/{recent.get('questions_attempted', 0)} correct")
                        return username
            else:
                print(f"   ❌ API error: {data.get('error', 'Unknown')}")
        elif resp.status_code == 404:
            print(f"   ❌ User not found")
        else:
            print(f"   ❌ API error: {resp.status_code}")
    
    return None

if __name__ == "__main__":
    found_user = test_user_lookup()
    if found_user:
        print(f"\n✅ Working username found: {found_user}")
    else:
        print(f"\n❌ No working username found")