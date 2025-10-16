#!/usr/bin/env python3
"""
Compare APIs to understand why practice view shows all sessions 
but detailed result view only shows limited data
"""

import requests
import json

def compare_api_responses():
    print("🔍 Comparing API Responses - Practice View vs Detailed Result View")
    print("=" * 80)
    
    username = "dashrath"
    user_id = 69
    
    # 1. Check the unified practice history API (what practice view uses)
    print("1️⃣ PRACTICE VIEW API: Unified Practice History")
    print("-" * 50)
    
    try:
        unified_url = f"http://127.0.0.1:8000/simple/practice-history/{user_id}/"
        response = requests.get(unified_url)
        
        if response.status_code == 200:
            unified_data = response.json()
            adaptive_sessions = unified_data.get('adaptive_sessions', [])
            
            print(f"✅ Status: {response.status_code}")
            print(f"📊 Total sessions: {unified_data.get('total_sessions')}")
            print(f"🧠 Adaptive sessions: {len(adaptive_sessions)}")
            
            print(f"\n📝 Sample sessions (first 5):")
            for i, session in enumerate(adaptive_sessions[:5], 1):
                session_id = session.get('session_id', 'N/A')
                questions = session.get('questions_attempted', 0)
                accuracy = session.get('accuracy', 'N/A')
                subject = session.get('subject', 'N/A')
                
                print(f"   {i}. {session_id[:8]}... | {subject} | {questions} questions | {accuracy} accuracy")
                
                # Check if this is our target session
                if session_id == "46bbeb26-7cb3-4a35-b3dc-d25acfc01d89":
                    print(f"      🎯 TARGET SESSION FOUND!")
                    print(f"         Questions: {questions}")
                    print(f"         Accuracy: {accuracy}")
                    print(f"         Duration: {session.get('duration_minutes', 'N/A')} min")
        else:
            print(f"❌ Failed: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 80)
    
    # 2. Check the regular assessment history API (what detailed result view uses)
    print("2️⃣ DETAILED RESULT VIEW API: Assessment History")
    print("-" * 50)
    
    try:
        history_url = f"http://127.0.0.1:8000/api/history/students/{username}/history"
        response = requests.get(history_url)
        
        if response.status_code == 200:
            history_data = response.json()
            
            print(f"✅ Status: {response.status_code}")
            print(f"📊 Total sessions: {len(history_data)}")
            
            print(f"\n📝 All sessions:")
            for i, session in enumerate(history_data, 1):
                session_id = session.get('session_id', 'N/A')
                questions = session.get('questions_attempted', 0)
                percentage = session.get('percentage_score', 0)
                subject = session.get('subject_name', 'N/A')
                
                print(f"   {i}. {session_id[:8]}... | {subject} | {questions} questions | {percentage}% score")
                
                # Check if this is our target session
                if session_id == "46bbeb26-7cb3-4a35-b3dc-d25acfc01d89":
                    print(f"      🎯 TARGET SESSION FOUND!")
                    print(f"         Questions: {questions}")
                    print(f"         Score: {percentage}%")
        else:
            print(f"❌ Failed: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 80)
    
    # 3. Check the simple session history API (another comparison)
    print("3️⃣ SIMPLE SESSION HISTORY API: Session History")
    print("-" * 50)
    
    try:
        simple_url = f"http://127.0.0.1:8000/simple/session-history/{user_id}/"
        response = requests.get(simple_url)
        
        if response.status_code == 200:
            simple_data = response.json()
            
            if simple_data.get('success'):
                sessions = simple_data.get('sessions', [])
                
                print(f"✅ Status: {response.status_code}")
                print(f"📊 Total sessions: {len(sessions)}")
                
                print(f"\n📝 Sample sessions (first 5):")
                for i, session in enumerate(sessions[:5], 1):
                    session_id = session.get('session_id', 'N/A')
                    questions = session.get('questions_attempted', 0)
                    accuracy = session.get('accuracy', 'N/A')
                    subject = session.get('subject', 'N/A')
                    
                    print(f"   {i}. {session_id[:8]}... | {subject} | {questions} questions | {accuracy} accuracy")
                    
                    # Check if this is our target session
                    if session_id == "46bbeb26-7cb3-4a35-b3dc-d25acfc01d89":
                        print(f"      🎯 TARGET SESSION FOUND!")
                        print(f"         Questions: {questions}")
                        print(f"         Accuracy: {accuracy}")
            else:
                print(f"❌ API returned success=False")
        else:
            print(f"❌ Failed: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 80)
    print("🎯 KEY FINDINGS:")
    print("- Practice view uses unified practice history API")
    print("- Detailed result view uses assessment history API") 
    print("- These APIs may be pulling from different data sources")
    print("- The target session might exist in one API but not the other")
    print("- Or the session data might be filtered differently")

if __name__ == "__main__":
    compare_api_responses()