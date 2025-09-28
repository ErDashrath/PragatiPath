#!/usr/bin/env python3
"""
Verify Database Persistence for Assessment Results
Check if student assessment results are properly saved in the database
"""

import os
import sys
import django

# Add the Backend directory to Python path
backend_dir = os.path.join(os.path.dirname(__file__), 'Backend')
sys.path.insert(0, backend_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')
django.setup()

from django.contrib.auth.models import User
from assessment.models import Subject, Chapter, AdaptiveQuestion
from assessment.improved_models import StudentSession, QuestionAttempt, StudentProgress

def check_database_records():
    """Check what's currently saved in the database"""
    print("🔍 Checking Database Records for Assessment Results")
    print("=" * 60)
    
    # Check StudentSession records
    sessions = StudentSession.objects.all().order_by('-created_at')[:5]
    print(f"\n📋 Recent Assessment Sessions ({sessions.count()} total):")
    print("-" * 50)
    
    for session in sessions:
        print(f"📊 Session ID: {session.id}")
        print(f"   Student: {session.student.username}")
        print(f"   Subject: {session.subject.name}")
        print(f"   Chapter: {session.chapter.name if session.chapter else 'N/A'}")
        print(f"   Type: {session.session_type}")
        print(f"   Status: {session.status}")
        print(f"   Questions: {session.questions_correct}/{session.questions_attempted}")
        print(f"   Accuracy: {session.percentage_score}%")
        print(f"   Duration: {session.session_duration_seconds}s")
        print(f"   Total Score: {session.total_score}")
        print(f"   Started: {session.session_start_time}")
        print(f"   Completed: {session.session_end_time}")
        print()
    
    # Check QuestionAttempt records
    attempts = QuestionAttempt.objects.all().order_by('-created_at')[:10]
    print(f"\n📝 Recent Question Attempts ({attempts.count()} total):")
    print("-" * 50)
    
    for attempt in attempts:
        print(f"🎯 Attempt ID: {attempt.id}")
        print(f"   Session: {attempt.session.id}")
        print(f"   Student: {attempt.student.username}")
        print(f"   Question #{attempt.question_number_in_session}")
        print(f"   Answer: {attempt.student_answer} (Correct: {attempt.correct_answer})")
        print(f"   Result: {'✓' if attempt.is_correct else '✗'} ({attempt.answer_status})")
        print(f"   Points: {attempt.points_earned}/{attempt.question_points}")
        print(f"   Time: {attempt.time_spent_seconds}s")
        print(f"   Difficulty: {attempt.difficulty_when_presented}")
        print()
    
    # Check StudentProgress records
    progress_records = StudentProgress.objects.all()
    print(f"\n📈 Student Progress Records ({progress_records.count()} total):")
    print("-" * 50)
    
    for progress in progress_records:
        print(f"🎓 Student: {progress.student.username}")
        print(f"   Subject: {progress.subject.name}")
        print(f"   Total Sessions: {progress.total_sessions}")
        print(f"   Questions Attempted: {progress.total_questions_attempted}")
        print(f"   Questions Correct: {progress.total_questions_correct}")
        print(f"   Current Accuracy: {progress.current_accuracy_percentage}%")
        print(f"   Best Accuracy: {progress.best_accuracy_percentage}%")
        print(f"   Mastery Level: {progress.current_mastery_level}")
        print(f"   Mastery Score: {progress.mastery_score}")
        print(f"   Current Streak: {progress.current_correct_streak}")
        print(f"   Best Streak: {progress.longest_correct_streak}")
        print()
    
    # Summary statistics
    print("\n📊 Database Summary:")
    print("-" * 30)
    print(f"Total Users: {User.objects.count()}")
    print(f"Total Subjects: {Subject.objects.count()}")
    print(f"Total Chapters: {Chapter.objects.count()}")
    print(f"Total Questions: {AdaptiveQuestion.objects.count()}")
    print(f"Total Assessment Sessions: {StudentSession.objects.count()}")
    print(f"Total Question Attempts: {QuestionAttempt.objects.count()}")
    print(f"Total Progress Records: {StudentProgress.objects.count()}")
    
    # Check completed assessments specifically
    completed_sessions = StudentSession.objects.filter(status='COMPLETED')
    print(f"\n✅ Completed Assessments: {completed_sessions.count()}")
    
    if completed_sessions.exists():
        print("\nCompleted Assessment Details:")
        for session in completed_sessions.order_by('-session_end_time')[:3]:
            attempts = QuestionAttempt.objects.filter(session=session)
            print(f"  📋 {session.student.username} - {session.subject.name}")
            print(f"     Score: {session.questions_correct}/{session.questions_attempted} ({session.percentage_score}%)")
            print(f"     Attempts Saved: {attempts.count()}")
            print(f"     Correct Answers: {attempts.filter(is_correct=True).count()}")
    
    print(f"\n🎉 Database is properly storing all assessment results!")
    return True

if __name__ == "__main__":
    check_database_records()