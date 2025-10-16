#!/usr/bin/env python3
"""
Fix StudentSession data inconsistency
This script will recalculate and fix questions_attempted, questions_correct, and percentage_score
based on actual QuestionAttempt records
"""

import os
import sys
import django

# Setup Django environment
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Backend')
sys.path.append(backend_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

try:
    django.setup()
except Exception as e:
    print(f"Django setup error: {e}")
    sys.exit(1)

from django.contrib.auth.models import User
from assessment.improved_models import StudentSession, QuestionAttempt
from django.db.models import Count, Q

def fix_session_statistics():
    print("🔧 Fixing StudentSession statistics based on QuestionAttempt records")
    print("=" * 70)
    
    # Get all sessions that have question attempts
    sessions_with_attempts = StudentSession.objects.filter(
        questionattempt__isnull=False
    ).distinct()
    
    print(f"📊 Found {sessions_with_attempts.count()} sessions with question attempts")
    
    fixed_count = 0
    
    for session in sessions_with_attempts:
        print(f"\n🔍 Processing session: {session.id}")
        print(f"   Student: {session.student.username}")
        print(f"   Subject: {session.subject.name}")
        print(f"   Current stats: {session.questions_attempted} attempted, {session.questions_correct} correct, {session.percentage_score}% accuracy")
        
        # Get actual question attempts for this session
        attempts = QuestionAttempt.objects.filter(session=session)
        
        # Calculate real statistics
        total_attempts = attempts.count()
        correct_attempts = attempts.filter(is_correct=True).count()
        percentage = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0.0
        
        print(f"   Actual stats: {total_attempts} attempted, {correct_attempts} correct, {percentage:.1f}% accuracy")
        
        # Check if update is needed
        needs_update = (
            session.questions_attempted != total_attempts or 
            session.questions_correct != correct_attempts or
            abs(session.percentage_score - percentage) > 0.1
        )
        
        if needs_update:
            print(f"   ✅ Updating session statistics...")
            
            # Update session fields
            session.questions_attempted = total_attempts
            session.questions_correct = correct_attempts
            session.questions_incorrect = total_attempts - correct_attempts
            session.percentage_score = percentage
            
            # Calculate total score (assuming 1 point per correct answer)
            session.total_score = correct_attempts
            session.max_possible_score = total_attempts
            
            # Save changes
            try:
                session.save()
                print(f"   ✅ Successfully updated session {session.id}")
                fixed_count += 1
                
                # Show the question attempts for verification
                if total_attempts > 0:
                    print(f"   📝 Question attempts:")
                    for i, attempt in enumerate(attempts[:3], 1):  # Show first 3
                        status = "✅ Correct" if attempt.is_correct else "❌ Incorrect"
                        print(f"      {i}. {status} - Answer: {attempt.student_answer}")
                    if total_attempts > 3:
                        print(f"      ... and {total_attempts - 3} more")
                
            except Exception as e:
                print(f"   ❌ Failed to update session: {e}")
        else:
            print(f"   ℹ️ Session statistics are already correct")
    
    print(f"\n🎯 Summary:")
    print(f"   📊 Sessions processed: {sessions_with_attempts.count()}")
    print(f"   ✅ Sessions fixed: {fixed_count}")
    print(f"   ℹ️ Sessions already correct: {sessions_with_attempts.count() - fixed_count}")
    
    return fixed_count

def verify_session_data():
    """Verify that session data is now consistent"""
    print("\n🔍 Verifying session data consistency...")
    print("-" * 50)
    
    # Check a few random sessions
    test_sessions = StudentSession.objects.filter(
        questionattempt__isnull=False
    ).distinct()[:3]
    
    for session in test_sessions:
        attempts = QuestionAttempt.objects.filter(session=session)
        
        actual_attempted = attempts.count()
        actual_correct = attempts.filter(is_correct=True).count()
        actual_percentage = (actual_correct / actual_attempted * 100) if actual_attempted > 0 else 0.0
        
        print(f"\n📋 Session {session.id}:")
        print(f"   Database: {session.questions_attempted} attempted, {session.questions_correct} correct, {session.percentage_score}%")
        print(f"   Calculated: {actual_attempted} attempted, {actual_correct} correct, {actual_percentage:.1f}%")
        
        is_consistent = (
            session.questions_attempted == actual_attempted and
            session.questions_correct == actual_correct and
            abs(session.percentage_score - actual_percentage) < 0.1
        )
        
        print(f"   Status: {'✅ Consistent' if is_consistent else '❌ Still inconsistent'}")

if __name__ == "__main__":
    try:
        print("🚀 Starting StudentSession Data Fix")
        print("=" * 50)
        
        # Show current problematic sessions
        print("📋 Current problematic sessions:")
        problem_sessions = StudentSession.objects.filter(
            questionattempt__isnull=False,
            questions_attempted=0
        ).distinct()
        
        print(f"   Found {problem_sessions.count()} sessions with attempts but questions_attempted=0")
        
        for session in problem_sessions[:3]:  # Show first 3
            attempts_count = QuestionAttempt.objects.filter(session=session).count()
            print(f"   - Session {session.id}: Has {attempts_count} attempts but questions_attempted={session.questions_attempted}")
        
        print()
        
        # Fix the data
        fixed_count = fix_session_statistics()
        
        # Verify the fix
        if fixed_count > 0:
            verify_session_data()
            
            print(f"\n🎉 Data fix completed! Fixed {fixed_count} sessions.")
            print("🔄 DetailedResultView should now show correct data.")
        else:
            print("\n📋 No sessions needed fixing.")
        
    except Exception as e:
        print(f"❌ Error during data fix: {e}")
        import traceback
        traceback.print_exc()