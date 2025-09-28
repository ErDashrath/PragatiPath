#!/usr/bin/env python3

import requests
import json

def test_all_possible_user_ids():
    """Test different user IDs to find active sessions"""
    
    print("🔍 TESTING DIFFERENT USER IDs")
    print("=" * 35)
    
    # Try different possible user IDs
    possible_user_ids = ["1", "2", "3", "student_1", "demo_student", "dashrath"]
    
    for user_id in possible_user_ids:
        try:
            print(f"\n📝 Testing user ID: '{user_id}'")
            url = f"http://localhost:8000/simple/session-history/{user_id}/"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('sessions'):
                    sessions = data['sessions']
                    if sessions:
                        print(f"✅ Found {len(sessions)} sessions for user '{user_id}'!")
                        
                        # Test the first session's details
                        first_session = sessions[0]
                        session_id = first_session.get('session_id')
                        session_name = first_session.get('session_name', 'Unknown')
                        
                        print(f"   📋 First session: {session_name}")
                        print(f"   🆔 Session ID: {session_id}")
                        
                        if session_id:
                            # Test session details endpoint
                            details_url = f"http://localhost:8000/history/session-details/{session_id}/"
                            details_response = requests.get(details_url)
                            
                            if details_response.status_code == 200:
                                details_data = details_response.json()
                                if details_data.get('success'):
                                    print(f"   ✅ Session details work!")
                                    question_count = len(details_data.get('session_details', {}).get('question_attempts', []))
                                    print(f"   📊 Questions: {question_count}")
                                    
                                    print(f"\n🎯 SOLUTION FOUND!")
                                    print(f"   Use user ID: '{user_id}'")
                                    print(f"   Test session ID: '{session_id}'")
                                    return user_id, session_id
                                else:
                                    print(f"   ❌ Session details returned success=false")
                            else:
                                print(f"   ❌ Session details failed: {details_response.status_code}")
                    else:
                        print(f"   ℹ️ No sessions for user '{user_id}'")
                else:
                    print(f"   ❌ API error for user '{user_id}': {data}")
            else:
                print(f"   ❌ HTTP {response.status_code} for user '{user_id}'")
                
        except Exception as e:
            print(f"   ❌ Error testing user '{user_id}': {e}")
    
    print(f"\n❌ No active sessions found for any tested user IDs")
    return None, None

if __name__ == "__main__":
    user_id, session_id = test_all_possible_user_ids()
    
    if user_id and session_id:
        print(f"\n✅ SUCCESS!")
        print(f"The frontend should use:")
        print(f"  localStorage.setItem('pragatipath_backend_user_id', '{user_id}');")
        print(f"  And test with session ID: {session_id}")
    else:
        print(f"\n💡 Next steps:")
        print(f"1. Create a new adaptive session in the UI")
        print(f"2. Check which user ID it gets stored under")
        print(f"3. Use browser dev tools to debug the Details click")