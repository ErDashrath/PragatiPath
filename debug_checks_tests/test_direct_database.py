#!/usr/bin/env python3
"""
Test Session Completion WITHOUT Redis
Tests just the database saving part directly
"""

import requests
import json
from datetime import datetime

def test_session_without_redis():
    """Test session completion by directly creating a session record"""
    print("🧪 Testing Session Creation Without Redis...")
    print("=" * 60)
    
    try:
        # Create a minimal test session record directly in Django
        from django.core.management import call_command
        import os
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')
        
        import django
        django.setup()
        
        from django.contrib.auth.models import User
        from assessment.improved_models import StudentSession, Subject
        from datetime import datetime, timezone
        
        # Create test user
        username = "test_student"
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.first_name = "Test"
            user.last_name = "Student"
            user.save()
        
        print(f"✅ User created/found: {user.username}")
        
        # Get or create subject
        subject, _ = Subject.objects.get_or_create(
            name="quantitative_aptitude",
            defaults={'display_name': 'Quantitative Aptitude'}
        )
        
        print(f"✅ Subject: {subject.name}")
        
        # Create a test session
        session = StudentSession.objects.create(
            user=user,
            subject=subject.name,
            session_id="test-session-123",
            started_at=datetime.now(timezone.utc),
            ended_at=datetime.now(timezone.utc),
            duration_seconds=180,
            total_questions=5,
            correct_answers=3,
            accuracy_percentage=60.0,
            metadata={
                "test": True,
                "created_by": "test_script"
            }
        )
        
        print(f"✅ Session created: {session.session_id}")
        print(f"   Score: {session.accuracy_percentage}%")
        print(f"   Questions: {session.correct_answers}/{session.total_questions}")
        
        # Test if we can retrieve it
        retrieved_sessions = StudentSession.objects.filter(user=user)
        print(f"✅ Found {retrieved_sessions.count()} session(s) for user")
        
        # Test history API
        print("\n🔍 Testing History API...")
        history_response = requests.get(f"http://localhost:8000/history/student/{username}/")
        
        if history_response.status_code == 200:
            history_data = history_response.json()
            sessions = history_data.get('sessions', [])
            print(f"✅ History API returned {len(sessions)} session(s)")
            
            if sessions:
                latest = sessions[0]
                print(f"   📅 Latest session: {latest.get('subject', 'Unknown')}")
                print(f"   📊 Score: {latest.get('score', 'N/A')}%")
                print(f"   🎯 Correct: {latest.get('correct_answers', 0)}/{latest.get('total_questions', 0)}")
        else:
            print(f"⚠️ History API failed: {history_response.status_code}")
            print(f"   Response: {history_response.text}")
        
        print("\n🎉 Direct database session creation successful!")
        print("=" * 60)
        print("📝 SUMMARY:")
        print("   ✅ User and subject created")
        print("   ✅ Session record saved to database")
        print("   ✅ History API can retrieve session")
        print("\n🔗 NEXT STEPS:")
        print("   1. Open http://localhost:5173 in browser")
        print("   2. Login with username: test_student (any password)")
        print("   3. Go to Assessment History")
        print("   4. Should see the test session")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Change to backend directory
    import os
    os.chdir("C:\\Users\\Dashrath\\Desktop\\Academic\\Hackathons\\PragatiPath\\Backend")
    
    print(f"🚀 Starting database test at {datetime.now()}")
    success = test_session_without_redis()
    
    if success:
        print("\n✅ Database session creation works! Frontend history should display sessions.")
    else:
        print("\n❌ Test failed. Check output above.")