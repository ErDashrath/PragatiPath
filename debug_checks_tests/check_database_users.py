#!/usr/bin/env python3
import os
import sys
import django
from pathlib import Path

# Setup Django
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))
os.chdir(str(backend_path))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')

try:
    django.setup()
    from django.contrib.auth.models import User
    from assessment.improved_models import StudentSession
    
    print("=== DATABASE USERS ===")
    users = User.objects.all()
    print(f"Total users: {users.count()}")
    
    for user in users:
        print(f"\nUser: {user.username}")
        print(f"  - Name: {user.first_name} {user.last_name}")
        print(f"  - Email: {user.email}")
        print(f"  - Active: {user.is_active}")
    
    print(f"\n=== STUDENT SESSIONS ===")
    sessions = StudentSession.objects.all()
    print(f"Total sessions: {sessions.count()}")
    
    if sessions.count() > 0:
        # Show unique usernames from sessions
        session_users = set(session.student.username for session in sessions)
        print(f"Session usernames: {list(session_users)}")
        
        # Show breakdown by username
        for username in session_users:
            user_sessions = StudentSession.objects.filter(student__username=username)
            print(f"\n'{username}': {user_sessions.count()} sessions")
            # Show session types
            session_types = user_sessions.values_list('session_type', flat=True).distinct()
            print(f"  - Session types: {list(session_types)}")
            # Show adaptive sessions
            adaptive_sessions = user_sessions.filter(session_type='ADAPTIVE_LEARNING').count()
            assessment_sessions = user_sessions.exclude(session_type='ADAPTIVE_LEARNING').count()
            print(f"  - Adaptive sessions: {adaptive_sessions}")
            print(f"  - Assessment sessions: {assessment_sessions}")
    
    print(f"\n=== RECOMMENDED ACTION ===")
    if users.count() == 0:
        print("❌ No users found! You need to:")
        print("1. Create a user through registration")
        print("2. Or create test data")
        print("3. Then login and create sessions")
    elif sessions.count() == 0:
        print("❌ No sessions found! You need to:")
        print("1. Login as an existing user") 
        print("2. Take some assessments/adaptive learning")
        print("3. Then check history")
    else:
        print("✅ Data exists! Frontend should use these usernames:")
        for username in session_users:
            print(f"  - {username}")
    
except Exception as e:
    print(f"Error: {e}")
    print("Make sure Django is properly set up and database exists")