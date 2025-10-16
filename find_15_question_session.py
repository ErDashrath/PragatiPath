#!/usr/bin/env python3
"""
Find the session with 15 questions in the practice API
and see if we can get its detailed results
"""

import requests
import json

def find_session_with_15_questions():
    print("🔍 Finding session with 15 questions in practice API")
    print("=" * 60)
    
    user_id = 69
    target_questions = 15
    
    # Get all sessions from practice API
    try:
        unified_url = f"http://127.0.0.1:8000/simple/practice-history/{user_id}/"
        response = requests.get(unified_url)
        
        if response.status_code == 200:
            data = response.json()
            adaptive_sessions = data.get('adaptive_sessions', [])
            
            print(f"📊 Found {len(adaptive_sessions)} adaptive sessions")
            print()
            
            sessions_with_15 = []
            
            for session in adaptive_sessions:
                questions = session.get('questions_attempted', 0)
                if questions == target_questions:
                    sessions_with_15.append(session)
            
            print(f"🎯 Sessions with {target_questions} questions: {len(sessions_with_15)}")
            
            if sessions_with_15:
                print(f"\n📋 Sessions with {target_questions} questions:")
                
                for i, session in enumerate(sessions_with_15, 1):
                    session_id = session.get('session_id')
                    subject = session.get('subject', 'N/A')
                    accuracy = session.get('accuracy', 'N/A')
                    duration = session.get('duration_minutes', 'N/A')
                    
                    print(f"   {i}. Session: {session_id}")
                    print(f"      Subject: {subject}")
                    print(f"      Questions: {questions}")
                    print(f"      Accuracy: {accuracy}")
                    print(f"      Duration: {duration} minutes")
                    print()
                    
                    # Test if this session works with detailed result API
                    print(f"      🧪 Testing detailed result API for this session...")
                    test_detailed_api(session_id, "dashrath")
                    print()
            
            else:
                print(f"❌ No sessions found with {target_questions} questions")
                print("📝 Available question counts:")
                
                question_counts = {}
                for session in adaptive_sessions:
                    questions = session.get('questions_attempted', 0)
                    if questions in question_counts:
                        question_counts[questions] += 1
                    else:
                        question_counts[questions] = 1
                
                for questions, count in sorted(question_counts.items()):
                    print(f"   {questions} questions: {count} sessions")
        
        else:
            print(f"❌ Failed to get practice API data: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

def test_detailed_api(session_id, username):
    """Test if a session works with the detailed result API"""
    try:
        detail_url = f"http://127.0.0.1:8000/api/history/students/{username}/assessment/{session_id}"
        response = requests.get(detail_url)
        
        if response.status_code == 200:
            data = response.json()
            session_info = data.get('session_info', {})
            question_attempts = data.get('question_attempts', [])
            
            attempted = session_info.get('questions_attempted', 0)
            correct = session_info.get('questions_correct', 0)
            percentage = session_info.get('percentage_score', 0)
            
            print(f"         ✅ Detailed API works!")
            print(f"         📊 Shows: {attempted} attempted, {correct} correct, {percentage}% accuracy")
            print(f"         📝 Question attempts: {len(question_attempts)} items")
            
            if attempted == 15:
                print(f"         🎉 FOUND IT! This session has 15 questions in detailed API!")
                return True
            else:
                print(f"         ⚠️  Detailed API shows {attempted} questions (not 15)")
        
        else:
            print(f"         ❌ Detailed API failed: {response.status_code}")
    
    except Exception as e:
        print(f"         ❌ Detailed API error: {e}")
    
    return False

if __name__ == "__main__":
    find_session_with_15_questions()