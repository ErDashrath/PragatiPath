#!/usr/bin/env python3

import requests
import json

def debug_module_mapping():
    """Debug the module/subject mapping issue"""
    
    print("🔍 DEBUGGING MODULE/SUBJECT MAPPING")
    print("=" * 60)
    
    # Test 1: Check what modules the frontend returns
    print("1️⃣  Testing Frontend Modules Endpoint")
    try:
        frontend_modules = requests.get("http://localhost:5000/api/modules")
        if frontend_modules.status_code == 200:
            modules_data = frontend_modules.json()
            print("✅ Frontend Modules:")
            for module in modules_data:
                print(f"   ID: {module.get('id')} | Title: {module.get('title')}")
        else:
            print(f"❌ Frontend modules failed: {frontend_modules.status_code}")
    except Exception as e:
        print(f"❌ Error fetching frontend modules: {e}")
    
    # Test 2: Check what subjects the Django backend has
    print(f"\n2️⃣  Testing Django Backend Subjects")
    try:
        backend_subjects = requests.get("http://localhost:8000/api/assessment/subjects-with-chapters")
        if backend_subjects.status_code == 200:
            subjects_data = backend_subjects.json()
            print("✅ Django Backend Subjects:")
            if subjects_data.get('success') and subjects_data.get('subjects'):
                for subject in subjects_data['subjects']:
                    print(f"   Code: {subject.get('subject_code')} | Name: {subject.get('subject_name')}")
                    for chapter in subject.get('chapters', []):
                        print(f"      Chapter {chapter.get('id')}: {chapter.get('name')}")
            else:
                print("⚠️  Invalid backend response structure")
        else:
            print(f"❌ Django backend subjects failed: {backend_subjects.status_code}")
    except Exception as e:
        print(f"❌ Error fetching backend subjects: {e}")
    
    # Test 3: Test specific question requests
    test_subjects = ['verbal_ability', 'quantitative_aptitude', 'logical_reasoning']
    
    print(f"\n3️⃣  Testing Question Requests for Different Subjects")
    for subject in test_subjects:
        print(f"\n📚 Testing Subject: {subject}")
        
        # Test frontend endpoint
        try:
            frontend_questions = requests.get(f"http://localhost:5000/api/assessment/questions/{subject}/1?count=5")
            if frontend_questions.status_code == 200:
                questions_data = frontend_questions.json()
                print(f"✅ Frontend returned {len(questions_data)} questions")
                if questions_data:
                    first_q = questions_data[0]
                    print(f"   First question module: {first_q.get('moduleId')}")
                    print(f"   Question preview: {first_q.get('questionText', '')[:50]}...")
            else:
                print(f"❌ Frontend questions failed: {frontend_questions.status_code}")
        except Exception as e:
            print(f"❌ Frontend questions error: {e}")
        
        # Test direct backend endpoint
        try:
            backend_request = {
                "student_id": "debug-student",
                "subject": subject,
                "chapter_id": 1,
                "difficulty_level": "moderate",
                "count": 5
            }
            backend_questions = requests.post(
                "http://localhost:8000/api/assessment/chapter-questions",
                json=backend_request
            )
            if backend_questions.status_code == 200:
                backend_data = backend_questions.json()
                if backend_data.get('success') and backend_data.get('questions'):
                    questions = backend_data['questions']
                    print(f"✅ Backend returned {len(questions)} questions")
                    if questions:
                        first_q = questions[0]
                        print(f"   First question subject: {first_q.get('subject')}")
                        print(f"   Question preview: {first_q.get('question_text', '')[:50]}...")
                else:
                    print(f"⚠️  Backend success but no questions: {backend_data}")
            else:
                print(f"❌ Backend questions failed: {backend_questions.status_code}")
                print(f"   Response: {backend_questions.text[:200]}")
        except Exception as e:
            print(f"❌ Backend questions error: {e}")
    
    print(f"\n" + "=" * 60)
    print("📋 MAPPING ANALYSIS COMPLETE")

if __name__ == "__main__":
    debug_module_mapping()