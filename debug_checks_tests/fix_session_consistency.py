#!/usr/bin/env python3
"""
Fix data consistency between session records and question attempts
"""
import os
import sys
import django

# Set up Django - must run from Backend directory
os.chdir('Backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')
django.setup()

from assessment.improved_models import StudentSession, QuestionAttempt
from django.contrib.auth.models import User

def fix_session_data_consistency():
    print("🔧 Fixing Session Data Consistency")
    print("=" * 40)
    
    # Find the dash user
    try:
        user = User.objects.get(username='dash')
        print(f"✅ Found user: {user.username}")
    except User.DoesNotExist:
        print("❌ User 'dash' not found")
        return False
    
    # Get recent sessions for dash user
    recent_sessions = StudentSession.objects.filter(
        student=user,
        session_name__contains='Adaptive Learning'
    ).order_by('-created_at')[:5]
    
    print(f"\n📊 Found {recent_sessions.count()} recent adaptive learning sessions:")
    
    fixed_count = 0
    for session in recent_sessions:
        print(f"\n🔍 Session: {session.id}")
        print(f"   Name: {session.session_name}")
        print(f"   Current record: {session.questions_correct}/{session.questions_attempted}")
        
        # Get actual question attempts
        attempts = QuestionAttempt.objects.filter(session=session)
        actual_correct = attempts.filter(is_correct=True).count()
        actual_total = attempts.count()
        
        print(f"   Actual attempts: {actual_correct}/{actual_total}")
        
        # Check for discrepancy
        if session.questions_correct != actual_correct or session.questions_attempted != actual_total:
            print(f"   ❌ MISMATCH FOUND!")
            
            # Fix the session record
            old_percentage = session.percentage_score
            new_percentage = (actual_correct / actual_total * 100) if actual_total > 0 else 0
            
            session.questions_correct = actual_correct
            session.questions_attempted = actual_total
            session.questions_incorrect = actual_total - actual_correct
            session.percentage_score = new_percentage
            
            # Update grade
            if new_percentage >= 90:
                session.grade = 'A+'
            elif new_percentage >= 80:
                session.grade = 'A'
            elif new_percentage >= 70:
                session.grade = 'B'
            elif new_percentage >= 60:
                session.grade = 'C'
            elif new_percentage >= 50:
                session.grade = 'D'
            else:
                session.grade = 'F'
            
            session.save()
            
            print(f"   ✅ FIXED!")
            print(f"      Score: {session.questions_correct}/{session.questions_attempted} ({session.percentage_score:.1f}%)")
            print(f"      Grade: {session.grade}")
            
            fixed_count += 1
        else:
            print(f"   ✅ Data consistent")
    
    print(f"\n📈 Summary:")
    print(f"   Sessions checked: {recent_sessions.count()}")
    print(f"   Sessions fixed: {fixed_count}")
    
    if fixed_count > 0:
        print(f"\n🎉 Data consistency fixed! Frontend should now show correct scores.")
    else:
        print(f"\n✅ All sessions were already consistent.")
    
    return True

if __name__ == '__main__':
    fix_session_data_consistency()