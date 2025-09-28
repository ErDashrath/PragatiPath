#!/usr/bin/env python3
"""
Check user sessions to debug history issue
"""
import os
import sys
import django

# Setup Django
backend_path = r'C:\Users\Dashrath\Desktop\Academic\Hackathons\PragatiPath\Backend'
sys.path.insert(0, backend_path)
os.chdir(backend_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')
django.setup()

from assessment.improved_models import StudentSession
from django.contrib.auth.models import User

def check_user_sessions():
    print("🔍 Checking User Sessions for History Issue")
    print("=" * 50)
    
    # Find users with 'dashrath' in username
    users = User.objects.filter(username__icontains='dashrath')
    print(f"📋 Users found with 'dashrath': {users.count()}")
    
    for user in users:
        print(f"\n👤 User: {user.username} (ID: {user.id})")
        
        # Get all sessions for this user
        all_sessions = StudentSession.objects.filter(student=user).order_by('-session_start_time')
        active_sessions = all_sessions.filter(status='ACTIVE')
        completed_sessions = all_sessions.filter(status='COMPLETED')
        
        print(f"   📊 Total Sessions: {all_sessions.count()}")
        print(f"   🟢 Active Sessions: {active_sessions.count()}")
        print(f"   ✅ Completed Sessions: {completed_sessions.count()}")
        
        if active_sessions.exists():
            print(f"\n   🟢 ACTIVE SESSIONS (Not in history):")
            for session in active_sessions[:3]:
                questions = session.question_attempts.count()
                print(f"      🔄 {session.id}")
                print(f"         Started: {session.session_start_time}")
                print(f"         Subject: {session.subject.name}")
                print(f"         Questions: {questions}")
                print(f"         Status: {session.status}")
        
        if completed_sessions.exists():
            print(f"\n   ✅ COMPLETED SESSIONS (In history):")
            for session in completed_sessions[:3]:
                questions = session.question_attempts.count()
                mastery_config = session.session_config or {}
                final_mastery = mastery_config.get('final_bkt_mastery', 'No mastery data')
                print(f"      ✅ {session.id}")
                print(f"         Ended: {session.session_end_time}")
                print(f"         Subject: {session.subject.name}")
                print(f"         Questions: {questions}")
                print(f"         Final Mastery: {final_mastery}")
    
    print(f"\n🎯 DIAGNOSIS:")
    if active_sessions.exists():
        print(f"❌ ISSUE FOUND: You have {active_sessions.count()} ACTIVE sessions")
        print(f"💡 SOLUTION: These sessions need to be COMPLETED to appear in history")
        print(f"🔧 FIX: Call POST /simple/complete-session/ for each session")
    else:
        print(f"✅ No active sessions found - all sessions should be in history")

if __name__ == "__main__":
    check_user_sessions()