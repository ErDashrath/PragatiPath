#!/usr/bin/env python3
"""
Assessment Minimum Questions Verification
Ensures assessments have at least 15 questions and adaptive learning works correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')
django.setup()

from core.models import Question, Subject, Chapter
from assessment.models import StudentSession, QuestionAttempt
from django.contrib.auth import get_user_model
import json

User = get_user_model()

def check_questions_per_subject():
    """Check if each subject has at least 15 questions available"""
    print("=== Subject Question Availability Check ===")
    
    subjects = Subject.objects.all()
    issues = []
    
    for subject in subjects:
        question_count = Question.objects.filter(subject=subject).count()
        
        if question_count < 15:
            issues.append({
                'subject': subject.name,
                'available_questions': question_count,
                'required': 15,
                'deficit': 15 - question_count
            })
            print(f"❌ {subject.name}: Only {question_count} questions (need {15 - question_count} more)")
        else:
            print(f"✅ {subject.name}: {question_count} questions available")
    
    return issues

def check_assessment_session_questions():
    """Check actual assessment sessions for minimum question requirement"""
    print("\n=== Assessment Session Question Count Check ===")
    
    sessions = StudentSession.objects.filter(
        session_type__in=['COMPETITIVE_EXAM', 'PRACTICE_TEST', 'ASSESSMENT']
    ).order_by('-created_at')[:10]  # Check latest 10 sessions
    
    issues = []
    
    for session in sessions:
        attempt_count = QuestionAttempt.objects.filter(session=session).count()
        
        if attempt_count < 15:
            issues.append({
                'session_id': session.session_id,
                'session_name': session.session_name,
                'session_type': session.session_type,
                'questions_attempted': attempt_count,
                'student': session.student.username,
                'subject': session.subject.name if session.subject else 'Unknown'
            })
            print(f"❌ Session {session.session_id}: Only {attempt_count} questions")
        else:
            print(f"✅ Session {session.session_id}: {attempt_count} questions")
    
    return issues

def check_adaptive_learning_orchestration():
    """Check if adaptive learning sessions have orchestration data"""
    print("\n=== Adaptive Learning Orchestration Check ===")
    
    adaptive_sessions = StudentSession.objects.filter(
        session_type='ADAPTIVE_LEARNING'
    ).order_by('-created_at')[:5]  # Check latest 5 adaptive sessions
    
    issues = []
    orchestration_found = False
    
    for session in adaptive_sessions:
        attempts = QuestionAttempt.objects.filter(session=session)
        
        # Check if attempts have BKT/DKT data
        has_bkt_data = any(attempt.metadata and ('bkt_mastery' in attempt.metadata or 'mastery_level' in attempt.metadata) 
                          for attempt in attempts)
        
        if has_bkt_data:
            orchestration_found = True
            print(f"✅ Session {session.session_id}: Has BKT/DKT orchestration data")
        else:
            issues.append({
                'session_id': session.session_id,
                'session_name': session.session_name,
                'questions_attempted': attempts.count(),
                'student': session.student.username
            })
            print(f"❌ Session {session.session_id}: No BKT/DKT orchestration data found")
    
    if not adaptive_sessions.exists():
        print("ℹ️  No adaptive learning sessions found")
    
    return issues, orchestration_found

def check_database_consistency():
    """Check overall database consistency"""
    print("\n=== Database Consistency Check ===")
    
    issues = []
    
    # Check for orphaned question attempts
    orphaned_attempts = QuestionAttempt.objects.filter(session__isnull=True).count()
    if orphaned_attempts > 0:
        issues.append(f"Found {orphaned_attempts} orphaned question attempts")
        print(f"❌ {orphaned_attempts} question attempts without sessions")
    else:
        print("✅ No orphaned question attempts")
    
    # Check for sessions without attempts
    empty_sessions = StudentSession.objects.filter(questionattempt__isnull=True).count()
    if empty_sessions > 0:
        issues.append(f"Found {empty_sessions} sessions without question attempts")
        print(f"⚠️  {empty_sessions} sessions without question attempts")
    else:
        print("✅ All sessions have question attempts")
    
    # Check user-session relationships
    users_with_sessions = User.objects.filter(studentsession__isnull=False).distinct().count()
    total_users = User.objects.count()
    print(f"ℹ️  {users_with_sessions}/{total_users} users have session data")
    
    return issues

def generate_data_insights():
    """Generate insights about the current data"""
    print("\n=== Data Insights ===")
    
    insights = {
        'total_subjects': Subject.objects.count(),
        'total_questions': Question.objects.count(),
        'total_sessions': StudentSession.objects.count(),
        'total_attempts': QuestionAttempt.objects.count(),
        'assessment_sessions': StudentSession.objects.filter(
            session_type__in=['COMPETITIVE_EXAM', 'PRACTICE_TEST', 'ASSESSMENT']
        ).count(),
        'adaptive_sessions': StudentSession.objects.filter(
            session_type='ADAPTIVE_LEARNING'
        ).count(),
        'active_users': User.objects.filter(studentsession__isnull=False).distinct().count(),
    }
    
    for key, value in insights.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    
    return insights

def main():
    """Main verification process"""
    print("Assessment & Adaptive Learning Verification")
    print("=" * 50)
    
    # Run all checks
    subject_issues = check_questions_per_subject()
    session_issues = check_assessment_session_questions() 
    orchestration_issues, has_orchestration = check_adaptive_learning_orchestration()
    db_issues = check_database_consistency()
    insights = generate_data_insights()
    
    # Generate summary report
    print("\n" + "=" * 50)
    print("VERIFICATION SUMMARY")
    print("=" * 50)
    
    total_issues = len(subject_issues) + len(session_issues) + len(orchestration_issues) + len(db_issues)
    
    if total_issues == 0:
        print("✅ All checks passed successfully!")
        success = True
    else:
        print(f"❌ Found {total_issues} issues that need attention:")
        success = False
        
        if subject_issues:
            print(f"\n📊 Subjects with insufficient questions ({len(subject_issues)}):")
            for issue in subject_issues:
                print(f"  - {issue['subject']}: Need {issue['deficit']} more questions")
        
        if session_issues:
            print(f"\n📝 Sessions with < 15 questions ({len(session_issues)}):")
            for issue in session_issues:
                print(f"  - {issue['session_name']}: {issue['questions_attempted']} questions")
        
        if orchestration_issues:
            print(f"\n🧠 Adaptive sessions missing orchestration ({len(orchestration_issues)}):")
            for issue in orchestration_issues:
                print(f"  - {issue['session_name']}: No BKT/DKT data")
        
        if db_issues:
            print(f"\n💾 Database consistency issues ({len(db_issues)}):")
            for issue in db_issues:
                print(f"  - {issue}")
    
    # Save detailed report
    report_data = {
        'timestamp': django.utils.timezone.now().isoformat(),
        'summary': {
            'total_issues': total_issues,
            'success': success,
            'has_orchestration': has_orchestration
        },
        'subject_issues': subject_issues,
        'session_issues': session_issues,
        'orchestration_issues': orchestration_issues,
        'db_issues': db_issues,
        'insights': insights
    }
    
    with open('assessment_verification_report.json', 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: assessment_verification_report.json")
    
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())