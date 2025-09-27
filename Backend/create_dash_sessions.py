from django.contrib.auth.models import User
from assessment.improved_models import StudentSession, Subject
from datetime import datetime, timezone

# Create sessions for the "dash" user (the one you're logged in as)
username = "dash"
user = User.objects.get(username=username)
print(f"Creating sessions for user: {user.username} ({user.first_name})")

# Get subjects
subjects_data = [
    ("quantitative_aptitude", "Quantitative Aptitude"),
    ("verbal_ability", "Verbal Ability"), 
    ("data_interpretation", "Data Interpretation")
]

# Create test sessions for dash user
sessions_data = [
    {"subject": "quantitative_aptitude", "total": 10, "correct": 8, "duration": 600},
    {"subject": "verbal_ability", "total": 8, "correct": 6, "duration": 480},
    {"subject": "data_interpretation", "total": 12, "correct": 9, "duration": 720},
    {"subject": "quantitative_aptitude", "total": 15, "correct": 12, "duration": 900},
]

for session_data in sessions_data:
    subject = Subject.objects.get(code=session_data["subject"])
    
    session = StudentSession.objects.create(
        student=user,
        subject=subject,
        status="COMPLETED",  # Set as completed so they show in history
        session_start_time=datetime.now(timezone.utc),
        session_end_time=datetime.now(timezone.utc),
        session_duration_seconds=session_data["duration"],
        total_questions_planned=session_data["total"],
        questions_attempted=session_data["total"],
        questions_correct=session_data["correct"],
        questions_incorrect=session_data["total"] - session_data["correct"],
        percentage_score=(session_data["correct"] * 100.0) / session_data["total"],
        session_config={"test": True, "created_by": "manual_test"}
    )
    print(f"✅ Created session: {subject.name} - {session.questions_correct}/{session.questions_attempted} ({session.percentage_score}%)")

# Check total sessions for dash user
total = StudentSession.objects.filter(student=user, status="COMPLETED").count()
print(f"\n📊 Total COMPLETED sessions for {username}: {total}")

# Test the API
import requests
try:
    response = requests.get(f"http://localhost:8000/history/student/{username}/", timeout=5)
    if response.status_code == 200:
        data = response.json()
        assessment_sessions = len(data.get('assessment_sessions', []))
        adaptive_sessions = len(data.get('adaptive_sessions', []))
        print(f"✅ History API: {assessment_sessions} assessment + {adaptive_sessions} adaptive sessions")
    else:
        print(f"⚠️ API failed: {response.status_code}")
except Exception as e:
    print(f"⚠️ API test failed: {e}")

print(f"\n🎉 Test sessions created for user '{username}'!")
print("Now refresh your frontend history page to see the new sessions.")