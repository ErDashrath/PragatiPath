#!/usr/bin/env python3

import requests
import json

def debug_missing_assessments():
    """Debug why regular module assessments are missing"""
    
    print("🔍 DEBUGGING MISSING REGULAR ASSESSMENTS")
    print("=" * 45)
    
    # Test different user IDs to find regular assessments
    possible_user_ids = ["1", "69", "dash", "demo", "student_dashrath"]
    
    print("1️⃣ Checking for regular assessment sessions...")
    
    for user_id in possible_user_ids:
        try:
            print(f"\n📝 Testing user ID: '{user_id}'")
            
            # Check regular assessment history API
            regular_url = f"http://localhost:8000/api/history/students/{user_id}/history"
            response = requests.get(regular_url)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and data:
                    print(f"   ✅ Found {len(data)} regular assessments!")
                    
                    # Show sample assessments
                    for i, assessment in enumerate(data[:3]):
                        print(f"   {i+1}. {assessment.get('session_name', 'Unknown')}")
                        print(f"      Subject: {assessment.get('subject_name', 'Unknown')}")
                        print(f"      Score: {assessment.get('percentage_score', 0)}%")
                        print(f"      Date: {assessment.get('session_start_time', 'Unknown')}")
                elif isinstance(data, list):
                    print(f"   ℹ️ No regular assessments found for '{user_id}'")
                else:
                    print(f"   ❌ Unexpected response format: {type(data)}")
            else:
                print(f"   ❌ API error {response.status_code} for user '{user_id}'")
                
        except Exception as e:
            print(f"   ❌ Error testing user '{user_id}': {e}")
    
    print(f"\n2️⃣ Checking adaptive sessions for comparison...")
    
    # Check adaptive sessions for user 69 (we know this works)
    try:
        adaptive_url = "http://localhost:8000/simple/session-history/69/"
        response = requests.get(adaptive_url)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('sessions'):
                sessions = data['sessions']
                print(f"   ✅ Found {len(sessions)} adaptive sessions for user '69'")
                
                for session in sessions[:2]:
                    print(f"   - {session.get('session_name', 'Unknown')}")
                    print(f"     Accuracy: {session.get('accuracy')}%")
            else:
                print(f"   ❌ No adaptive sessions found")
        else:
            print(f"   ❌ Adaptive API error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Adaptive API error: {e}")
    
    print(f"\n3️⃣ Checking assessment history component...")
    print(f"The issue might be:")
    print(f"   1. Regular assessments stored under different user ID")
    print(f"   2. Assessment history component not loading regular data")
    print(f"   3. Database migration or data loss")
    print(f"   4. API endpoint changes")
    
    print(f"\n💡 Next steps:")
    print(f"   1. Check the assessment-history.tsx component")
    print(f"   2. Verify which user ID the frontend is using")
    print(f"   3. Check if regular assessments are in different database")
    print(f"   4. Look at browser network tab for failed requests")

if __name__ == "__main__":
    debug_missing_assessments()