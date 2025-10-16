"""
Fix StudentSession data inconsistency using Django shell
Run this in Django shell: python manage.py shell < fix_session_data.py
"""

from django.contrib.auth.models import User
from assessment.improved_models import StudentSession, QuestionAttempt

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
            
        except Exception as e:
            print(f"   ❌ Failed to update session: {e}")
    else:
        print(f"   ℹ️ Session statistics are already correct")

print(f"\n🎯 Summary:")
print(f"   📊 Sessions processed: {sessions_with_attempts.count()}")
print(f"   ✅ Sessions fixed: {fixed_count}")
print(f"   ℹ️ Sessions already correct: {sessions_with_attempts.count() - fixed_count}")

print("\n🔄 Fix completed! DetailedResultView should now show correct data.")