#!/usr/bin/env python
"""Find adaptive sessions with different BKT mastery levels and difficulty ranges"""
import os
import sys
import django

sys.path.append('backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')
django.setup()

from assessment.models import QuestionAttempt, StudentSession

print("🧠 Analyzing Adaptive Sessions by BKT Mastery Level")
print("=" * 60)

# Get sessions and analyze their difficulty patterns
sessions = StudentSession.objects.all()[:50]  # Sample more sessions

mastery_patterns = {}

for session in sessions:
    attempts = QuestionAttempt.objects.filter(session=session)
    if len(attempts) == 0:
        continue
        
    # Get difficulty distribution for this session
    difficulties = {}
    total_correct = 0
    
    for attempt in attempts:
        difficulty = attempt.difficulty_when_presented or attempt.difficulty or 'unknown'
        if difficulty not in difficulties:
            difficulties[difficulty] = {'total': 0, 'correct': 0}
        difficulties[difficulty]['total'] += 1
        if attempt.is_correct:
            difficulties[difficulty]['correct'] += 1
            total_correct += 1
    
    # Calculate session accuracy
    accuracy = (total_correct / len(attempts)) * 100 if len(attempts) > 0 else 0
    
    # Categorize by difficulty pattern
    difficulty_types = set(difficulties.keys())
    pattern_key = f"{len(difficulty_types)} types: {sorted(difficulty_types)}"
    
    if pattern_key not in mastery_patterns:
        mastery_patterns[pattern_key] = []
    
    mastery_patterns[pattern_key].append({
        'session_id': str(session.id),
        'questions': len(attempts),
        'accuracy': accuracy,
        'difficulties': difficulties
    })

print("📊 Adaptive Session Patterns:")
print("-" * 40)

for pattern, sessions in mastery_patterns.items():
    if len(sessions) > 0:
        print(f"\n🎯 {pattern}")
        
        # Show best examples (highest accuracy or most questions)
        best_sessions = sorted(sessions, key=lambda x: (len(x['difficulties']), x['accuracy']), reverse=True)[:2]
        
        for session in best_sessions:
            print(f"  Session: {session['session_id'][:8]}... ({session['questions']} questions, {session['accuracy']:.1f}% accuracy)")
            
            for diff, stats in session['difficulties'].items():
                ui_display = diff.replace('_', ' ').capitalize()
                diff_accuracy = (stats['correct'] / stats['total']) * 100 if stats['total'] > 0 else 0
                print(f"    {ui_display}: {stats['correct']}/{stats['total']} ({diff_accuracy:.1f}%)")

# Find sessions with very_easy and difficult specifically
print(f"\n🔍 Looking for sessions with 'very_easy' and 'difficult' questions...")

very_easy_sessions = []
difficult_sessions = []

for session in sessions:
    attempts = QuestionAttempt.objects.filter(session=session)
    difficulties = [attempt.difficulty_when_presented or attempt.difficulty for attempt in attempts]
    
    if 'very_easy' in difficulties:
        very_easy_sessions.append(str(session.id))
    if 'difficult' in difficulties:
        difficult_sessions.append(str(session.id))

print(f"\n📋 Sessions with specific difficulties:")
print(f"  Very Easy questions: {len(very_easy_sessions)} sessions")
if very_easy_sessions:
    print(f"    Example: {very_easy_sessions[0]}")

print(f"  Difficult questions: {len(difficult_sessions)} sessions") 
if difficult_sessions:
    print(f"    Example: {difficult_sessions[0]}")

print(f"\n💡 This shows how BKT adapts question difficulty based on student mastery!")