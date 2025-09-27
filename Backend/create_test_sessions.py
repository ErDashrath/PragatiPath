#!/usr/bin/env python3
"""
Django Shell Script - Create test session directly
"""

from django.contrib.auth.models import User
from assessment.improved_models import StudentSession, Subject
from datetime import datetime, timezone
import requests

def create_test_session():
    """Create a test session in the database"""
    print("🧪 Creating test session directly in database...")
    
    # Create test user
    username = "teststudent"
    user, created = User.objects.get_or_create(username=username)
    if created:
        user.first_name = "Test"
        user.last_name = "Student"
        user.email = "test@example.com"
        user.set_password("testpass")
        user.save()
        print(f"✅ New user created: {user.username}")
    else:
        print(f"✅ Existing user found: {user.username}")
    
    # Get or create subject
    subject, created = Subject.objects.get_or_create(
        name="quantitative_aptitude",
        defaults={'display_name': 'Quantitative Aptitude'}
    )
    print(f"✅ Subject: {subject.name}")
    
    # Create test sessions
    sessions_data = [
        {
            "session_id": "test-session-001",
            "duration_seconds": 300,
            "total_questions": 10,
            "correct_answers": 7,
            "accuracy_percentage": 70.0
        },
        {
            "session_id": "test-session-002", 
            "duration_seconds": 420,
            "total_questions": 15,
            "correct_answers": 9,
            "accuracy_percentage": 60.0
        },
        {
            "session_id": "test-session-003",
            "duration_seconds": 180,
            "total_questions": 5,
            "correct_answers": 4,
            "accuracy_percentage": 80.0
        }
    ]
    
    created_sessions = []
    for session_data in sessions_data:
        # Delete existing session with same ID
        StudentSession.objects.filter(session_id=session_data["session_id"]).delete()
        
        # Create new session
        session = StudentSession.objects.create(
            user=user,
            subject=subject.name,
            session_id=session_data["session_id"],
            started_at=datetime.now(timezone.utc),
            ended_at=datetime.now(timezone.utc),
            duration_seconds=session_data["duration_seconds"],
            total_questions=session_data["total_questions"],
            correct_answers=session_data["correct_answers"],
            accuracy_percentage=session_data["accuracy_percentage"],
            metadata={
                "test": True,
                "created_by": "direct_database_test"
            }
        )
        created_sessions.append(session)
        print(f"✅ Session created: {session.session_id} ({session.accuracy_percentage}%)")
    
    # Verify sessions exist
    total_sessions = StudentSession.objects.filter(user=user).count()
    print(f"✅ Total sessions for {username}: {total_sessions}")
    
    # Test history API
    print("\n🔍 Testing History API...")
    try:
        response = requests.get(f"http://localhost:8000/history/student/{username}/", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            api_sessions = data.get('sessions', [])
            print(f"✅ History API returned {len(api_sessions)} session(s)")
            
            for i, session in enumerate(api_sessions[:3]):  # Show first 3
                print(f"   {i+1}. {session.get('subject', 'Unknown')} - {session.get('score', 'N/A')}% ({session.get('correct_answers', 0)}/{session.get('total_questions', 0)})")
        else:
            print(f"⚠️ History API failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"⚠️ API test failed: {e}")
    
    print("\n🎉 Test sessions created successfully!")
    print("=" * 50)
    print("🔗 NEXT STEPS:")
    print(f"   1. Open http://localhost:5173 in browser")
    print(f"   2. Login with username: {username} password: testpass")
    print(f"   3. Go to Assessment History") 
    print(f"   4. Should see {len(created_sessions)} test session(s)")
    
    return True

if __name__ == "__main__":
    create_test_session()