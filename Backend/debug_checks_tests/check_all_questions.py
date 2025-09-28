#!/usr/bin/env python3
"""
Check all database tables and find where questions are stored
"""

import os
import sys
import django

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')
django.setup()

from django.db import connection
from assessment.models import AdaptiveQuestion, Subject
from django.db.models import Count

def check_all_tables_and_questions():
    """Check all database tables and find questions"""
    print("🔍 Checking All Database Tables and Questions")
    print("=" * 60)
    
    # Check all tables in database
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    print("📋 All tables in database:")
    print("-" * 30)
    for i, table in enumerate(tables, 1):
        print(f"{i:2}. {table}")
    
    print()
    
    # Check for question-related tables
    question_tables = [table for table in tables if 'question' in table.lower()]
    print(f"🎯 Question-related tables: {question_tables}")
    print()
    
    # Check AdaptiveQuestion table specifically
    print("📊 AdaptiveQuestion Analysis:")
    print("-" * 30)
    
    total_questions = AdaptiveQuestion.objects.count()
    print(f"Total AdaptiveQuestion records: {total_questions}")
    
    if total_questions > 0:
        # Check questions by subject
        subjects_with_counts = Subject.objects.annotate(
            question_count=Count('adaptivequestion')
        ).order_by('-question_count')
        
        print("\n📚 Questions by Subject:")
        print("-" * 25)
        
        for subject in subjects_with_counts:
            count = subject.question_count
            if count > 0:
                print(f"✅ {subject.name} ({subject.code}): {count} questions")
            else:
                print(f"❌ {subject.name} ({subject.code}): 0 questions")
        
        # Get sample questions from each subject that has questions
        print("\n🎯 Sample Questions from Each Subject:")
        print("-" * 40)
        
        subjects_with_questions = subjects_with_counts.filter(question_count__gt=0)
        
        for subject in subjects_with_questions:
            sample_question = AdaptiveQuestion.objects.filter(subject=subject).first()
            if sample_question:
                print(f"\n📖 {subject.name}:")
                print(f"   Sample Question ID: {sample_question.id}")
                print(f"   Text: {sample_question.question_text[:100]}...")
                print(f"   Answer: {sample_question.answer}")
                print(f"   Difficulty: {sample_question.difficulty_level}")
    
    # Check other potential question tables using raw SQL
    print("\n🔍 Checking Other Potential Question Tables:")
    print("-" * 45)
    
    for table in question_tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            count = cursor.fetchone()[0]
            print(f"📊 {table}: {count} records")
            
            if count > 0 and count < 20:  # Show sample if not too many
                cursor.execute(f"SELECT * FROM {table} LIMIT 3;")
                rows = cursor.fetchall()
                
                # Get column names
                cursor.execute(f"PRAGMA table_info({table});")
                columns = [col[1] for col in cursor.fetchall()]
                
                print(f"   Sample records:")
                for row in rows:
                    row_data = dict(zip(columns, row))
                    print(f"   - {row_data}")
                    
        except Exception as e:
            print(f"❌ Error checking {table}: {e}")
    
    # Also check if there are other question models not in AdaptiveQuestion
    print("\n🔎 Checking for Other Question Models:")
    print("-" * 35)
    
    # Check if there's a basic Question model
    try:
        from assessment.models import Question
        question_count = Question.objects.count()
        print(f"📊 Question model: {question_count} records")
        
        if question_count > 0:
            sample = Question.objects.first()
            print(f"   Sample ID: {sample.id}")
            print(f"   Text: {sample.question_text[:100] if hasattr(sample, 'question_text') else 'N/A'}")
            
    except ImportError:
        print("❌ No basic Question model found")
    
    cursor.close()

if __name__ == "__main__":
    check_all_tables_and_questions()