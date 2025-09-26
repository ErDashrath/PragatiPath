#!/usr/bin/env python3
"""Debug user session to check what username is actually saved"""
import os
import django
import sys

# Add the project directory to Python path
sys.path.insert(0, 'c:\\Users\\Dashrath\\Desktop\\Academic\\Hackathons\\StrawHatsH2')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')
os.chdir('c:\\Users\\Dashrath\\Desktop\\Academic\\Hackathons\\StrawHatsH2')

django.setup()

from core.models import User

print("\n=== DEBUG USER SESSION ===")

# List all users
users = User.objects.all()
print(f"Total users found: {users.count()}")

for user in users:
    print(f"\nUser ID: {user.id}")
    print(f"Username: {user.username}")
    print(f"Name: {user.name}")
    print(f"Email: {user.email}")
    print(f"User Type: {user.userType}")
    print(f"Is Active: {user.is_active}")

# Let's see if there are student sessions
from core.models import StudentSession
sessions = StudentSession.objects.all()
print(f"\n=== STUDENT SESSIONS ===")
print(f"Total sessions: {sessions.count()}")

if sessions.count() > 0:
    session_usernames = set(session.student_username for session in sessions)
    print(f"Unique session usernames: {list(session_usernames)}")

print("\n=== USER-SESSION MAPPING ===")
for user in users:
    user_sessions = StudentSession.objects.filter(student_username=user.username).count()
    prefixed_sessions = StudentSession.objects.filter(student_username=f'student_{user.username}').count()
    print(f"User '{user.username}' has:")
    print(f"  - {user_sessions} sessions with direct username")
    print(f"  - {prefixed_sessions} sessions with 'student_{user.username}' prefix")