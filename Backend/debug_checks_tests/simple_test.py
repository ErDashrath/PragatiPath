from django.contrib.auth.models import User
from assessment.improved_models import StudentSession, Subject
from datetime import datetime, timezone
import requests

# Create test user
username = "teststudent"
user, created = User.objects.get_or_create(username=username)
if created:
    user.first_name = "Test"
    user.last_name = "Student"
    user.email = "test@example.com"
    user.set_password("testpass")
    user.save()
    print(f"New user created: {user.username}")
else:
    print(f"Existing user found: {user.username}")

# Get or create subject
subject, created = Subject.objects.get_or_create(
    code="quantitative_aptitude",
    defaults={'name': 'Quantitative Aptitude'}
)
print(f"Subject: {subject.name}")

# Create test sessions
sessions_data = [
    {"session_id": "test-001", "total": 10, "correct": 7, "duration": 300},
    {"session_id": "test-002", "total": 15, "correct": 9, "duration": 420}, 
    {"session_id": "test-003", "total": 5, "correct": 4, "duration": 180}
]

for data in sessions_data:
    # Don't delete by session_id since it doesn't exist, use id
    session = StudentSession.objects.create(
        student=user,  # Use student instead of user
        subject=subject,  # Use subject object, not string
        session_start_time=datetime.now(timezone.utc),
        session_end_time=datetime.now(timezone.utc),
        session_duration_seconds=data["duration"],
        total_questions_planned=data["total"],
        questions_attempted=data["total"],
        questions_correct=data["correct"],
        questions_incorrect=data["total"] - data["correct"],
        percentage_score=(data["correct"] * 100.0) / data["total"],
        session_config={"test": True, "session_name": data["session_id"]}
    )
    print(f"Session created: {session.id} ({session.percentage_score}%)")

total = StudentSession.objects.filter(student=user).count()
print(f"Total sessions for {username}: {total}")

# Test API
try:
    response = requests.get(f"http://localhost:8000/history/student/{username}/", timeout=5)
    if response.status_code == 200:
        data = response.json()
        sessions = data.get('sessions', [])
        print(f"History API returned {len(sessions)} sessions")
        for i, s in enumerate(sessions[:3]):
            print(f"  {i+1}. {s.get('subject', 'Unknown')} - {s.get('score', 'N/A')}%")
    else:
        print(f"API failed: {response.status_code}")
except Exception as e:
    print(f"API test failed: {e}")

print("\nTest complete! Login with username: teststudent, password: testpass")