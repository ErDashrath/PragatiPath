from django.contrib.auth.models import User
from assessment.improved_models import StudentSession

# Check all users and their sessions
print("=== ALL USERS AND THEIR SESSIONS ===")
users = User.objects.all()
for user in users:
    sessions = StudentSession.objects.filter(student=user)
    if sessions.exists():
        print(f"\n👤 User: {user.username} ({user.first_name} {user.last_name})")
        print(f"   📧 Email: {user.email}")
        for session in sessions:
            print(f"   📊 {session.id}: {session.subject} - {session.status}")
            print(f"       Score: {session.questions_correct}/{session.questions_attempted} ({session.percentage_score}%)")
            print(f"       Created: {session.created_at}")

# Update test sessions to COMPLETED status
print("\n=== UPDATING TEST SESSIONS ===")
test_sessions = StudentSession.objects.filter(
    student__username="teststudent",
    status="ACTIVE"
)

for session in test_sessions:
    session.status = "COMPLETED"
    session.save()
    print(f"✅ Updated session {session.id} to COMPLETED status")

print(f"\n📊 Updated {test_sessions.count()} sessions to COMPLETED status")