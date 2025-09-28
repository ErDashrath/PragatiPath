from django.contrib.auth.models import User
from assessment.improved_models import StudentSession, Subject
from datetime import datetime, timezone

# Create sessions for the dash user
user = User.objects.get(username="dash")
print(f"Creating sessions for user: {user.username}")

# Get quantitative aptitude subject
subject = Subject.objects.get(code="quantitative_aptitude")

# Create additional completed sessions
for i, data in enumerate([
    {"total": 12, "correct": 10, "duration": 720},
    {"total": 8, "correct": 5, "duration": 480},
    {"total": 15, "correct": 11, "duration": 900}
], 1):
    session = StudentSession.objects.create(
        student=user,
        subject=subject,
        status="COMPLETED",
        session_start_time=datetime.now(timezone.utc),
        session_end_time=datetime.now(timezone.utc),
        session_duration_seconds=data["duration"],
        total_questions_planned=data["total"],
        questions_attempted=data["total"],
        questions_correct=data["correct"],
        questions_incorrect=data["total"] - data["correct"],
        percentage_score=(data["correct"] * 100.0) / data["total"]
    )
    print(f"Created session {i}: {session.questions_correct}/{session.questions_attempted} ({session.percentage_score}%)")

total = StudentSession.objects.filter(student=user, status="COMPLETED").count()
print(f"Total COMPLETED sessions for dash: {total}")

# Test API
import requests
response = requests.get("http://localhost:8000/history/student/dash/", timeout=5)
if response.status_code == 200:
    data = response.json()
    sessions = len(data.get('adaptive_sessions', []))
    print(f"History API shows {sessions} sessions for dash user")
else:
    print(f"API failed: {response.status_code}")

print("Sessions created! Now refresh your frontend history.")