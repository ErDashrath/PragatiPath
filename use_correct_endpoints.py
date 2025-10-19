#!/usr/bin/env python3
"""
Use the correct student management endpoints from the URL list
"""

import requests
import json

def use_correct_endpoints():
    """Use the correct student endpoints we found"""
    print("🎯 Using Correct Student Management Endpoints")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # 1. Try the student list endpoint that we know exists
    print("\n1. Getting existing students...")
    try:
        # From URL list: students/ [name='list_students']
        students_response = requests.get(f"{base_url}/api/students/")
        print(f"   Status: {students_response.status_code}")
        
        if students_response.status_code == 200:
            students_data = students_response.json()
            print(f"   ✅ Students found!")
            
            if isinstance(students_data, list) and len(students_data) > 0:
                for i, student in enumerate(students_data[:3]):
                    student_id = student.get('id') or student.get('student_id')
                    username = student.get('username', 'Unknown')
                    print(f"   {i+1}. {username}: {student_id}")
                
                # Use the first student for testing
                first_student_id = students_data[0].get('id') or students_data[0].get('student_id')
                if first_student_id:
                    return test_orchestrated_with_real_id(first_student_id)
            else:
                print(f"   No students in response: {students_data}")
        else:
            print(f"   Error: {students_response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # 2. Try creating a student with correct endpoint
    print("\n2. Creating student with correct endpoint...")
    try:
        # From the core API patterns, try register endpoint
        student_data = {
            "username": "test_exam_student",
            "email": "testexam@test.com",
            "password": "testpass123",
            "full_name": "Test Exam Student"
        }
        
        create_response = requests.post(
            f"{base_url}/api/register",
            json=student_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Register Status: {create_response.status_code}")
        
        if create_response.status_code == 200:
            created_student = create_response.json()
            student_id = created_student.get('id')
            print(f"   ✅ Student created: {student_id}")
            return test_orchestrated_with_real_id(student_id)
        else:
            print(f"   Register Error: {create_response.text}")
    except Exception as e:
        print(f"   Register Exception: {e}")
    
    # 3. If nothing works, let's check what student info we can get
    print("\n3. Checking student dashboard to understand format...")
    try:
        # Try the student dashboard endpoint with a simple ID
        dashboard_response = requests.get(f"{base_url}/api/frontend/dashboard/student/1")
        print(f"   Dashboard Status: {dashboard_response.status_code}")
        
        if dashboard_response.status_code == 200:
            dashboard_data = dashboard_response.json()
            print(f"   Dashboard data: {json.dumps(dashboard_data, indent=2)}")
            
            # Check if we can extract a real student ID from the dashboard
            student_id = dashboard_data.get('student_id')
            if student_id:
                return test_orchestrated_with_real_id(student_id)
        else:
            print(f"   Dashboard Error: {dashboard_response.text}")
    except Exception as e:
        print(f"   Dashboard Exception: {e}")
    
    return False

def test_orchestrated_with_real_id(student_id):
    """Test the orchestrated API with a real student ID"""
    print(f"\n🧪 Testing Orchestrated API with: {student_id}")
    
    base_url = "http://localhost:8000"
    
    exam_config = {
        "student_id": str(student_id),
        "subject": "quantitative_aptitude",
        "session_type": "exam",
        "max_questions": 5
    }
    
    try:
        session_response = requests.post(
            f"{base_url}/api/frontend-orchestration/learning-session/start",
            json=exam_config,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Session Status: {session_response.status_code}")
        
        if session_response.status_code == 200:
            session_data = session_response.json()
            print(f"   🎉 ORCHESTRATED API SUCCESS!")
            print(f"   Session: {json.dumps(session_data, indent=2)}")
            
            print(f"\n🎯 WORKING STUDENT ID: {student_id}")
            print("✅ Update frontend to use this student ID!")
            return True
        else:
            error_text = session_response.text
            print(f"   Orchestrated Error: {error_text}")
            
            # If it's a UUID error, the student ID format is wrong
            if "not a valid UUID" in error_text:
                print(f"   💡 Student ID {student_id} is not in UUID format")
                print(f"   Need to find the actual UUID for this student")
            
            return False
            
    except Exception as e:
        print(f"   Exception: {e}")
        return False

if __name__ == "__main__":
    success = use_correct_endpoints()
    
    if success:
        print(f"\n🎉 INTEGRATION WORKING!")
        print("✅ Found working student ID and tested orchestrated API")
        print("✅ Ready to update frontend with correct student ID")
    else:
        print(f"\n❌ Still debugging...")
        print("💡 May need to check StudentProfile table directly or create UUID student")