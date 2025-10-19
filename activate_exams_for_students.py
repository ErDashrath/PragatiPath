#!/usr/bin/env python3

import requests
import json

def activate_exams_for_students():
    """Activate draft exams so students can see them"""
    
    print("🚀 Activating Exams for Student Testing")
    print("=" * 45)
    
    # List of exam IDs to activate (from the previous output)
    exam_ids_to_activate = [
        "a9d36da5-86c1-44cc-92b8-3396aef75c6a",  # Final Test Exam
        "bf99f696-2426-42b6-8a17-6da5a75405e1",  # Frontend Integration Test Exam
        "09354e99-950c-44ac-a611-303ce402e378",  # Test Exam with Valid Subject
    ]
    
    for i, exam_id in enumerate(exam_ids_to_activate, 1):
        print(f"\n{i}. Activating exam {exam_id}:")
        print("-" * 40)
        
        try:
            response = requests.post(f"http://localhost:8000/api/enhanced-exam/admin/exams/{exam_id}/activate")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"   ✅ {result.get('message', 'Activated successfully')}")
                else:
                    print(f"   ❌ {result.get('error', 'Activation failed')}")
            else:
                print(f"   ❌ HTTP Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
    
    # Now check student available exams again
    print(f"\n🎓 Checking Student Exams After Activation:")
    print("-" * 45)
    
    try:
        student_response = requests.get("http://localhost:8000/api/enhanced-exam/student/exams/available")
        print(f"Student API Status: {student_response.status_code}")
        
        if student_response.status_code == 200:
            student_data = student_response.json()
            if isinstance(student_data, dict) and 'data' in student_data:
                available_exams = student_data['data']
            elif isinstance(student_data, list):
                available_exams = student_data
            else:
                available_exams = []
            
            print(f"✅ Found {len(available_exams)} available exams for students")
            
            if available_exams:
                for i, exam in enumerate(available_exams, 1):
                    print(f"\n📝 Available Exam {i}:")
                    print(f"   ID: {exam.get('id', 'N/A')}")
                    print(f"   Name: {exam.get('exam_name', 'N/A')}")
                    print(f"   Status: {exam.get('status', 'N/A')}")
                    print(f"   Subject: {exam.get('subject_name', 'N/A')}")
                    print(f"   Start: {exam.get('scheduled_start_time', 'N/A')}")
                    print(f"   Duration: {exam.get('duration_minutes', 'N/A')} min")
            else:
                print("❌ Still no exams available for students")
        else:
            print(f"❌ Student API Error: {student_response.text}")
    
    except Exception as e:
        print(f"❌ Student API Exception: {str(e)}")

if __name__ == "__main__":
    activate_exams_for_students()