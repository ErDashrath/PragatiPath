#!/usr/bin/env python3

import requests
import json

def debug_actual_sessions():
    """Get the actual session IDs from the current adaptive sessions"""
    
    print("🔍 DEBUGGING ACTUAL ADAPTIVE SESSIONS")
    print("=" * 40)
    
    # Get the student ID from backend
    backend_user_id = "1"  # Assuming this is the backend user ID
    
    try:
        print("1️⃣ Getting current adaptive sessions...")
        session_history_url = f"http://localhost:8000/simple/session-history/{backend_user_id}/"
        
        response = requests.get(session_history_url)
        print(f"Session history status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('sessions'):
                sessions = data['sessions']
                print(f"✅ Found {len(sessions)} sessions")
                
                print("\n📋 Current Adaptive Sessions:")
                for i, session in enumerate(sessions[:3]):  # Show first 3
                    print(f"\n{i+1}. Session: {session.get('session_name', 'Unknown')}")
                    print(f"   ID: {session.get('session_id')}")
                    print(f"   Subject: {session.get('subject')}")
                    print(f"   Status: {session.get('status')}")
                    print(f"   Questions: {session.get('questions_attempted')}")
                    print(f"   Accuracy: {session.get('accuracy')}%")
                    
                    # Test this specific session's details
                    session_id = session.get('session_id')
                    if session_id:
                        print(f"   Testing details for this session...")
                        
                        try:
                            # Test the session details endpoint
                            details_url = f"http://localhost:8000/history/session-details/{session_id}/"
                            details_response = requests.get(details_url)
                            
                            if details_response.status_code == 200:
                                details_data = details_response.json()
                                if details_data.get('success'):
                                    session_details = details_data.get('session_details', {})
                                    question_attempts = session_details.get('question_attempts', [])
                                    print(f"   ✅ Details API works: {len(question_attempts)} questions")
                                else:
                                    print(f"   ❌ Details API returned success=false")
                            else:
                                print(f"   ❌ Details API failed: {details_response.status_code}")
                                
                            # Test the regular assessment API
                            regular_url = f"http://localhost:8000/api/results/{session_id}/"
                            regular_response = requests.get(regular_url)
                            print(f"   Regular API status: {regular_response.status_code}")
                            
                        except Exception as e:
                            print(f"   ❌ Error testing session {session_id}: {e}")
                            
            else:
                print("❌ No sessions found or API error")
                print(data)
                
    except Exception as e:
        print(f"❌ Error getting sessions: {e}")
        
    print("\n🎯 The issue might be:")
    print("1. Frontend is using wrong session IDs")
    print("2. Data mapping in DetailedResultView has errors")
    print("3. Console errors in browser dev tools")
    print("4. Network request failing silently")
    
    return True

if __name__ == "__main__":
    debug_actual_sessions()