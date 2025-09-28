#!/usr/bin/env python3
"""
Check database status for submissions
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')
django.setup()

from assessment.models import QuestionAttempt, StudentSession, AdaptiveQuestion
from django.contrib.auth.models import User

def check_database_status():
    print('=== DATABASE STATUS ===')
    print(f'Users: {User.objects.count()}')
    print(f'Sessions: {StudentSession.objects.count()}')  
    print(f'Questions: {AdaptiveQuestion.objects.count()}')
    print(f'Question Attempts: {QuestionAttempt.objects.count()}')

    print('\n=== RECENT SESSIONS ===')
    for session in StudentSession.objects.all().order_by('-created_at')[:3]:
        print(f'Session: {session.id} - Student: {session.student.username} - Subject: {session.subject}')

    print('\n=== RECENT ATTEMPTS ===')
    for attempt in QuestionAttempt.objects.all().order_by('-created_at')[:5]:
        print(f'Attempt: {attempt.id} - Student: {attempt.student.username} - Correct: {attempt.is_correct} - Question: {attempt.question_id}')

    print('\n=== ADAPTIVE QUESTIONS ===')
    for q in AdaptiveQuestion.objects.all()[:5]:
        print(f'Question: {q.id} - Subject: {getattr(q, "subject_fk", "None")} - Difficulty: {q.difficulty_level}')
        
    # Check if AdaptiveSubmission model exists
    try:
        from assessment.adaptive_submission_models import AdaptiveSubmission
        print(f'\n=== ADAPTIVE SUBMISSIONS ===')
        print(f'Adaptive Submissions: {AdaptiveSubmission.objects.count()}')
        for submission in AdaptiveSubmission.objects.all().order_by('-created_at')[:3]:
            print(f'Submission: {submission.id} - Student: {submission.student.username} - Correct: {submission.is_correct}')
    except Exception as e:
        print(f'\n=== ADAPTIVE SUBMISSIONS ===')
        print(f'AdaptiveSubmission model not available: {e}')

if __name__ == "__main__":
    check_database_status()