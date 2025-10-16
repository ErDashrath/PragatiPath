#!/usr/bin/env python3
"""
Simple test to run our session fix directly through the manage.py command
"""

import subprocess
import os

# Change to Backend directory
backend_dir = r'c:\Users\Dashrath\Desktop\Academic\Hackathons\PragatiPath\Backend'
os.chdir(backend_dir)

print("🔧 Running session data fix...")

# Create a simple Python script to execute
fix_script = '''
from django.contrib.auth.models import User
from assessment.improved_models import StudentSession, QuestionAttempt

print("Finding sessions with data issues...")

# Find sessions that have QuestionAttempts but show 0 questions_attempted
problem_sessions = StudentSession.objects.filter(
    question_attempts__isnull=False,
    questions_attempted=0
).distinct()

print(f"Found {problem_sessions.count()} sessions with data issues")

fixed_count = 0
for session in problem_sessions:
    attempts = QuestionAttempt.objects.filter(session=session)
    total_attempts = attempts.count()
    correct_attempts = attempts.filter(is_correct=True).count()
    
    print(f"Session {session.id}: Has {total_attempts} attempts, {correct_attempts} correct")
    
    # Update the session
    session.questions_attempted = total_attempts
    session.questions_correct = correct_attempts
    session.questions_incorrect = total_attempts - correct_attempts
    session.percentage_score = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0.0
    session.total_score = correct_attempts
    session.max_possible_score = total_attempts
    
    try:
        session.save()
        print(f"[SUCCESS] Fixed session {session.id}")
        fixed_count += 1
    except Exception as e:
        print(f"[ERROR] Failed to fix session {session.id}: {e}")

print(f"Fixed {fixed_count} sessions")
'''

# Write the script to a temporary file
with open('temp_fix.py', 'w', encoding='utf-8') as f:
    f.write(fix_script)

try:
    # Execute through Django shell
    result = subprocess.run(
        ['python', 'manage.py', 'shell', '--command', fix_script],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    print("Output:", result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    
    if result.returncode == 0:
        print("✅ Fix completed successfully!")
    else:
        print(f"❌ Fix failed with return code {result.returncode}")

except subprocess.TimeoutExpired:
    print("❌ Command timed out")
except Exception as e:
    print(f"❌ Exception: {e}")

finally:
    # Clean up temp file
    if os.path.exists('temp_fix.py'):
        os.remove('temp_fix.py')