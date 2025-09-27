#!/usr/bin/env python3
"""
Auto-complete active sessions to fix history
"""
import requests
import json
from datetime import datetime

BACKEND_URL = "http://127.0.0.1:8000"

def auto_complete_active_sessions():
    """Auto-complete active sessions for user dashrath"""
    
    print("🔧 AUTO-COMPLETING ACTIVE SESSIONS")
    print("=" * 50)
    print("🎯 This will complete your active sessions so they appear in history")
    
    # Get the active sessions that need completion
    active_sessions = [
        "3e5ca86c-a53a-486b-802e-8fc741672c96",  # Most recent with 15 questions
        "5ca09db4-367e-430d-a4d5-8ff91a3a762d",  # Logical Reasoning with 10 questions
        "8488df09-4767-4b01-af15-e8be0798d4a4",  # Quantitative with 10 questions
    ]
    
    completed_count = 0
    
    for session_id in active_sessions:
        print(f"\n📝 Completing session: {session_id}")
        
        # Complete the session
        completion_data = {
            'session_id': session_id,
            'completion_reason': 'manual_completion'
        }
        
        try:
            response = requests.post(f"{BACKEND_URL}/simple/complete-session/", json=completion_data)
            
            if response.status_code == 200:
                result = response.json()
                completion_data = result.get('completion_data', {})
                final_mastery = completion_data.get('final_mastery', {})
                
                print(f"   ✅ Session completed successfully!")
                print(f"   🧠 Final BKT Mastery: {final_mastery.get('bkt_mastery', 'N/A')}")
                print(f"   🎯 Mastery Level: {final_mastery.get('mastery_level', 'N/A')}")
                print(f"   📊 Questions: {completion_data.get('performance_summary', {}).get('total_questions', 0)}")
                
                completed_count += 1
                
            else:
                print(f"   ❌ Failed to complete session: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error completing session: {e}")
    
    print(f"\n🎉 COMPLETION SUMMARY")
    print("=" * 30)
    print(f"   ✅ Sessions completed: {completed_count}/{len(active_sessions)}")
    
    # Now check the updated history
    if completed_count > 0:
        print(f"\n📚 Checking updated session history...")
        
        # Use user ID 69 for dashrath (from earlier check)
        user_id = 69
        
        try:
            response = requests.get(f"{BACKEND_URL}/simple/session-history/{user_id}/")
            
            if response.status_code == 200:
                history = response.json()
                
                print(f"✅ Updated history retrieved!")
                print(f"👤 Student: {history.get('student_name', 'N/A')}")
                print(f"📊 Total Sessions in History: {history.get('total_sessions', 0)}")
                
                sessions = history.get('sessions', [])
                
                if sessions:
                    print(f"\n📋 RECENT SESSIONS IN HISTORY:")
                    for i, session in enumerate(sessions[:5], 1):
                        mastery_scores = session.get('mastery_scores', {})
                        
                        print(f"   {i}. 📅 {session.get('session_date', 'N/A')}")
                        print(f"      📝 Subject: {session.get('subject', 'N/A')}")
                        print(f"      📊 Accuracy: {session.get('accuracy', 'N/A')}")
                        print(f"      🧠 BKT Mastery: {mastery_scores.get('bkt_mastery', 'N/A')}")
                        print(f"      🎯 Level: {mastery_scores.get('mastery_level', 'N/A')}")
                        print()
                else:
                    print(f"   ⚠️ No sessions found in history")
                    
            else:
                print(f"❌ Failed to get updated history: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error checking history: {e}")
    
    print(f"\n✨ SESSION COMPLETION COMPLETE!")
    print(f"🎊 Your adaptive test sessions should now appear in history!")
    
    return completed_count

if __name__ == "__main__":
    print("🚀 Starting Auto-Completion of Active Sessions...")
    result = auto_complete_active_sessions()
    
    if result > 0:
        print(f"\n🎯 SUCCESS: {result} sessions completed and added to history!")
        print(f"\n💡 NEXT STEPS:")
        print(f"   1. Check your frontend - sessions should now appear in history")
        print(f"   2. Future sessions will auto-complete when you finish tests")
        print(f"   3. Your mastery progression is now visible!")
    else:
        print(f"\n🔧 No sessions were completed - check if backend is running")