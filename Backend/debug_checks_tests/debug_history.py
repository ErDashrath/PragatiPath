from django.contrib.auth.models import User
from assessment.improved_models import StudentSession

username = "teststudent"
try:
    student = User.objects.get(username=username)
    print(f"Found user: {student.username}")
    
    sessions = StudentSession.objects.filter(student=student)
    print(f"Found {sessions.count()} sessions")
    
    for session in sessions[:5]:
        print(f"  - {session.id}: {session.subject} ({session.questions_correct}/{session.questions_attempted})")
        print(f"    Status: {session.status}")
        print(f"    Created: {session.created_at}")
        print(f"    Subject object: {session.subject}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()