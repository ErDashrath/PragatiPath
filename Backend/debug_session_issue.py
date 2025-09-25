#!/usr/bin/env python3
"""
Debug session creation and lookup issue
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')
django.setup()

from assessment.models import StudentSession
from assessment.improved_models import Subject
from core.models import StudentProfile
from django.contrib.auth.models import User

def debug_session_issue():
    print("🔍 Debugging Session Creation & Lookup")
    print("=" * 50)
    
    # Step 1: Recreate the exact session creation logic from start_simple_session
    print("1. Creating user (mimicking start_simple_session)...")
    
    student_name = 'Test User Fixed'
    subject = 'quantitative_aptitude'
    
    username = f"student_{student_name.replace(' ', '_').lower()}"
    print(f"   Username will be: '{username}'")
    
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': f'{username}@example.com',
            'first_name': student_name.split()[0],
            'last_name': ' '.join(student_name.split()[1:]) if len(student_name.split()) > 1 else ''
        }
    )
    print(f"   ✅ User: {user.username} (created: {created})")
    
    # Step 2: Create profile
    print("2. Creating profile...")
    profile, created = StudentProfile.objects.get_or_create(
        user=user,
        defaults={
            'fundamentals': {
                'listening': 0.5,
                'grasping': 0.5,
                'retention': 0.5,
                'application': 0.5
            }
        }
    )
    print(f"   ✅ Profile: {profile.id} (created: {created})")
    
    # Step 3: Create subject
    print("3. Creating subject...")
    subject_code = 'quantitative_aptitude'  # This should match
    
    subject_obj, created = Subject.objects.get_or_create(
        code=subject_code,
        defaults={
            'name': subject.title(),
            'description': f'Auto-created subject for {subject}',
            'is_active': True
        }
    )
    print(f"   ✅ Subject: {subject_obj.name} ({subject_obj.code}) (created: {created})")
    
    # Step 4: Create session
    print("4. Creating session...")
    session = StudentSession.objects.create(
        student=user,
        subject=subject_obj,
        session_name=f"Debug {subject_obj.name} Session",
        total_questions_planned=5,
        session_config={
            'subject': subject,
            'subject_code': subject_code,
            'subject_name': subject_obj.name,
            'frontend_session': True,
            'simple_api': True
        }
    )
    print(f"   ✅ Session created: {session.id}")
    print(f"   Session details:")
    print(f"     Student: {session.student.username}")
    print(f"     Subject: {session.subject}")
    print(f"     Config: {session.session_config}")
    
    # Step 5: Test session lookup (mimicking submit_simple_answer)
    print("5. Testing session lookup...")
    try:
        found_session = StudentSession.objects.get(id=session.id)
        print(f"   ✅ Session found by ID: {found_session.id}")
        print(f"     Student: {found_session.student.username}")
        print(f"     Subject: {found_session.subject}")
        
        # Test the exact lookup method used in submit_simple_answer
        from django.shortcuts import get_object_or_404
        api_session = get_object_or_404(StudentSession, id=session.id)
        print(f"   ✅ Session found via get_object_or_404: {api_session.id}")
        
    except Exception as e:
        print(f"   ❌ Session lookup failed: {e}")
        return None
    
    # Step 6: List all sessions for this user
    print("6. All sessions for this user:")
    all_sessions = StudentSession.objects.filter(student=user)
    for s in all_sessions:
        print(f"   Session {s.id}: {s.session_name} (Subject: {s.subject})")
    
    return session.id

if __name__ == "__main__":
    session_id = debug_session_issue()
    if session_id:
        print(f"\n🎯 Use this session_id for testing: {session_id}")
        print("Now test submission with this session_id to see if it works!")
    else:
        print("\n❌ Session creation/lookup failed!")