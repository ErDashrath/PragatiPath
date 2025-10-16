#!/usr/bin/env python3
"""
Deep dive to find all question attempts for user dashrath
Check if there are 15 questions somewhere that we're missing
"""

import requests
import json

def find_all_questions_for_user():
    print("🕵️ Deep dive: Finding all question data for user 'dashrath'")
    print("=" * 70)
    
    username = "dashrath"
    
    # 1. Get all sessions for this user
    print("1️⃣ Getting all sessions for user...")
    history_url = f"http://127.0.0.1:8000/api/history/students/{username}/history"
    
    try:
        response = requests.get(history_url)
        if response.status_code == 200:
            sessions = response.json()
            print(f"   Found {len(sessions)} sessions")
            
            for i, session in enumerate(sessions, 1):
                session_id = session.get('session_id')
                attempted = session.get('questions_attempted', 0)
                correct = session.get('questions_correct', 0)
                percentage = session.get('percentage_score', 0)
                subject = session.get('subject_name', 'Unknown')
                session_type = session.get('session_type', 'Unknown')
                
                print(f"   Session {i}: {session_id}")
                print(f"      Subject: {subject} | Type: {session_type}")
                print(f"      Questions: {attempted} attempted, {correct} correct ({percentage}%)")
                print()
        else:
            print(f"   ❌ Failed to get sessions: {response.status_code}")
            return
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # 2. Check simple frontend API
    print("2️⃣ Checking simple frontend API...")
    
    # Try different user IDs to find the right backend user ID for dashrath
    for backend_user_id in range(1, 10):
        try:
            simple_url = f"http://127.0.0.1:8000/simple/session-history/{backend_user_id}/"
            response = requests.get(simple_url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('sessions'):
                    sessions = data['sessions']
                    student_name = data.get('student_name', 'Unknown')
                    
                    print(f"   Backend User ID {backend_user_id}: {student_name}")
                    print(f"   Found {len(sessions)} sessions")
                    
                    for j, session in enumerate(sessions, 1):
                        session_id = session.get('session_id')
                        attempted = session.get('questions_attempted', 0)
                        accuracy = session.get('accuracy', 'N/A')
                        subject = session.get('subject', 'Unknown')
                        
                        print(f"      Session {j}: {session_id[:8]}...")
                        print(f"         Subject: {subject} | Attempted: {attempted} | Accuracy: {accuracy}")
                        
                        # Check if this matches our target session
                        if session_id == "46bbeb26-7cb3-4a35-b3dc-d25acfc01d89":
                            print(f"         🎯 THIS IS OUR TARGET SESSION!")
                            print(f"         📊 Shows {attempted} questions attempted")
                            
                            # Check if there are 15 questions in mastery_scores or other fields
                            mastery = session.get('mastery_scores', {})
                            performance = session.get('performance', {})
                            
                            if mastery:
                                print(f"         📈 Mastery data: {mastery}")
                            if performance:
                                print(f"         📈 Performance data: {performance}")
                    
                    print()
        
        except Exception as e:
            continue
    
    # 3. Check if there are other sessions with 15 questions
    print("3️⃣ Looking for any sessions with 15+ questions...")
    
    # Check all sessions again to see if any have 15 questions
    for session in sessions:
        session_id = session.get('session_id')
        attempted = session.get('questions_attempted', 0)
        
        if attempted >= 15:
            print(f"   🎯 Found session with 15+ questions: {session_id}")
            print(f"      Attempted: {attempted}")
        elif attempted >= 10:
            print(f"   📋 Found session with 10+ questions: {session_id}")
            print(f"      Attempted: {attempted}")
    
    # 4. Direct database-style query simulation
    print("4️⃣ Checking if the target session should have more questions...")
    
    target_session_id = "46bbeb26-7cb3-4a35-b3dc-d25acfc01d89"
    
    # Check detailed result again but look more carefully at the response
    detail_url = f"http://127.0.0.1:8000/api/history/students/{username}/assessment/{target_session_id}"
    
    try:
        response = requests.get(detail_url)
        if response.status_code == 200:
            data = response.json()
            
            print(f"   Target session detailed analysis:")
            session_info = data.get('session_info', {})
            question_attempts = data.get('question_attempts', [])
            
            print(f"   📊 Session info shows: {session_info.get('questions_attempted')} questions")
            print(f"   📝 Question attempts array: {len(question_attempts)} items")
            
            # Check if there might be a pagination issue or data filtering
            print(f"   🔍 Checking for any hints of more data...")
            
            performance = data.get('performance_analysis', {})
            if performance:
                topics = performance.get('topics_performance', {})
                difficulties = performance.get('difficulty_performance', {})
                
                print(f"   📈 Topics analyzed: {list(topics.keys())}")
                print(f"   📈 Difficulties analyzed: {list(difficulties.keys())}")
    
    except Exception as e:
        print(f"   ❌ Error checking detailed result: {e}")

if __name__ == "__main__":
    find_all_questions_for_user()