#!/usr/bin/env python3
"""
Check the actual structure of AdaptiveQuestion and find where questions are
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

from assessment.models import AdaptiveQuestion, Subject, StudentSession
from django.db import connection

def check_question_structure():
    """Check the actual structure of questions in the database"""
    print("🔍 Analyzing Question Database Structure")
    print("=" * 50)
    
    # Check total questions
    total_questions = AdaptiveQuestion.objects.count()
    print(f"Total questions: {total_questions}")
    
    if total_questions > 0:
        # Get first few questions to see their structure
        print(f"\n📋 Sample Questions Structure:")
        print("-" * 30)
        
        sample_questions = AdaptiveQuestion.objects.all()[:5]
        
        for i, question in enumerate(sample_questions, 1):
            print(f"\n{i}. Question ID: {question.id}")
            print(f"   Text: {question.question_text[:100]}...")
            print(f"   Answer: {question.answer}")
            print(f"   Subject: {question.subject}")
            print(f"   Subject ID: {question.subject.id if question.subject else 'None'}")
            print(f"   Subject Name: {question.subject.name if question.subject else 'None'}")
            print(f"   Difficulty: {question.difficulty_level}")
            
            # Check if it has chapter
            if hasattr(question, 'chapter') and question.chapter:
                print(f"   Chapter: {question.chapter}")
            
            # Check all fields
            print(f"   All fields: {[field.name for field in question._meta.fields]}")
    
    # Check the raw database structure
    print(f"\n🗃️ Raw Database Structure:")
    print("-" * 30)
    
    cursor = connection.cursor()
    
    # Get the table structure
    cursor.execute("PRAGMA table_info(adaptive_questions);")
    columns = cursor.fetchall()
    
    print("Columns in adaptive_questions table:")
    for col in columns:
        print(f"   {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")
    
    # Check some raw data
    cursor.execute("SELECT id, subject_id, question_text, answer, difficulty_level FROM adaptive_questions LIMIT 5;")
    raw_data = cursor.fetchall()
    
    print(f"\n📊 Raw Question Data:")
    print("-" * 20)
    
    for row in raw_data:
        print(f"   ID: {row[0]}")
        print(f"   Subject ID: {row[1]}")
        print(f"   Text: {row[2][:80] if row[2] else 'None'}...")
        print(f"   Answer: {row[3]}")
        print(f"   Difficulty: {row[4]}")
        print()
    
    # Check if subject_id values exist in subjects table
    cursor.execute("SELECT DISTINCT subject_id FROM adaptive_questions WHERE subject_id IS NOT NULL;")
    question_subject_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id, name, code FROM subjects;")
    actual_subjects = cursor.fetchall()
    
    print(f"🔗 Subject ID Analysis:")
    print("-" * 20)
    print(f"Subject IDs in questions: {question_subject_ids}")
    print(f"Actual subjects in database:")
    for subj in actual_subjects:
        print(f"   {subj[0]}: {subj[1]} ({subj[2]})")
    
    # Check if there's a mismatch
    print(f"\n💡 Analysis:")
    print("-" * 10)
    if question_subject_ids:
        for qid in question_subject_ids:
            subject_exists = any(qid == subj[0] for subj in actual_subjects)
            if subject_exists:
                subject_name = next(subj[1] for subj in actual_subjects if subj[0] == qid)
                count_query = "SELECT COUNT(*) FROM adaptive_questions WHERE subject_id = ?"
                cursor.execute(count_query, (qid,))
                count = cursor.fetchone()[0]
                print(f"✅ Subject {qid} ({subject_name}): {count} questions")
            else:
                count_query = "SELECT COUNT(*) FROM adaptive_questions WHERE subject_id = ?"
                cursor.execute(count_query, (qid,))
                count = cursor.fetchone()[0]
                print(f"❌ Subject {qid}: {count} questions but subject doesn't exist!")
    else:
        print("❌ No questions have subject_id set!")
    
    # Check for NULL subject_ids
    cursor.execute("SELECT COUNT(*) FROM adaptive_questions WHERE subject_id IS NULL;")
    null_count = cursor.fetchone()[0]
    print(f"⚠️ Questions with NULL subject_id: {null_count}")
    
    cursor.close()
    
    # Now let's try to find a working question for our test
    print(f"\n🎯 Finding Working Question for Test:")
    print("-" * 35)
    
    # Get any question that exists
    any_question = AdaptiveQuestion.objects.first()
    if any_question:
        print(f"Found question: {any_question.id}")
        print(f"Question text: {any_question.question_text[:100]}...")
        print(f"Answer: {any_question.answer}")
        
        # Create a test that uses this question
        session_id = "81225db3-6d4d-489c-980d-b4aa7d93b3f6"
        
        test_code = f'''#!/usr/bin/env python3
"""
Test with actual question from database (bypassing subject check)
"""

import requests
import json

def test_with_existing_question():
    url = "http://localhost:8000/simple/submit-answer/"
    
    data = {{
        "session_id": "{session_id}",
        "question_id": "{any_question.id}",
        "selected_answer": "{any_question.answer}",
        "time_spent": 25.5
    }}
    
    print("=" * 60)
    print(f"🧪 Testing with EXISTING question from database")
    print(f"Session: {{data['session_id']}}")
    print(f"Question: {{data['question_id']}}")
    print(f"Expected Answer: {{data['selected_answer']}}")
    print("=" * 60)
    
    try:
        response = requests.post(url, json=data)
        print(f"Status: {{response.status_code}}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"Response: {{json.dumps(result, indent=2)}}")
        else:
            print("❌ FAILED!")
            print(f"Response: {{response.text}}")
            try:
                error_details = response.json()
                print(f"Error details: {{json.dumps(error_details, indent=2)}}")
            except:
                pass
            
    except Exception as e:
        print(f"❌ Error: {{e}}")

if __name__ == "__main__":
    test_with_existing_question()
'''
        
        with open("test_existing_question.py", "w") as f:
            f.write(test_code)
        
        print(f"\n📁 Created test_existing_question.py")
        print(f"   This uses an actual question from the database: {any_question.id}")

if __name__ == "__main__":
    check_question_structure()