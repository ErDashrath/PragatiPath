#!/usr/bin/env python3
"""
Check Database Difficulty Levels
"""
import os
import sys
import django

# Setup Django
backend_path = os.path.join(os.path.dirname(__file__), 'Backend')
sys.path.insert(0, backend_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')
django.setup()

from assessment.models import AdaptiveQuestion
from assessment.improved_models import Subject
from django.db.models import Count

def check_difficulty_levels():
    print("🔍 CHECKING DATABASE DIFFICULTY LEVELS")
    print("="*60)
    
    # Check all difficulty levels in the database
    difficulty_counts = AdaptiveQuestion.objects.values('difficulty_level').annotate(count=Count('id')).order_by('difficulty_level')
    
    print("📊 Available Difficulty Levels in Database:")
    total_questions = 0
    
    for item in difficulty_counts:
        difficulty = item['difficulty_level']
        count = item['count']
        total_questions += count
        print(f"   {difficulty}: {count} questions")
    
    print(f"\nTotal Questions: {total_questions}")
    
    # Check subjects
    subjects = Subject.objects.all()
    print(f"\n📚 Available Subjects: {subjects.count()}")
    for subject in subjects:
        print(f"   {subject.code}: {subject.name}")
    
    # Check questions by subject and difficulty
    print("\n📈 Questions by Subject and Difficulty:")
    
    for subject in subjects:
        print(f"\n  📖 {subject.name} ({subject.code}):")
        subject_difficulties = AdaptiveQuestion.objects.filter(
            subject_fk=subject
        ).values('difficulty_level').annotate(count=Count('id')).order_by('difficulty_level')
        
        if subject_difficulties:
            for item in subject_difficulties:
                print(f"     {item['difficulty_level']}: {item['count']} questions")
        else:
            print(f"     No questions found for {subject.name}")
    
    # Sample a few questions to see their actual difficulty values
    print("\n🔍 Sample Questions and Their Difficulties:")
    sample_questions = AdaptiveQuestion.objects.all()[:10]
    
    for q in sample_questions:
        print(f"   ID: {q.id}, Difficulty: '{q.difficulty_level}', Subject: {q.subject_fk.name if q.subject_fk else 'None'}")
        print(f"      Question: {q.question_text[:60]}...")
        print()

if __name__ == "__main__":
    try:
        check_difficulty_levels()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()