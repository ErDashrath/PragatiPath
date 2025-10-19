#!/usr/bin/env python3
"""
Get real student UUIDs from the system and test with them
"""

import requests
import json

def get_real_student_ids():
    """Get real student IDs from the system"""
    print("🔍 Getting Real Student IDs from System")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    # Check student management endpoints
    endpoints_to_try = [
        "/api/assessment/students/list",
        "/api/students/",
        "/api/core/students/"
    ]
    
    for endpoint in endpoints_to_try:
        print(f"\nTrying: {endpoint}")
        try:
            response = requests.get(f"{base_url}{endpoint}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success! Found students")
                
                if isinstance(data, list) and len(data) > 0:
                    for i, student in enumerate(data[:3]):  # Show first 3 students
                        student_id = student.get('student_id') or student.get('id') or student.get('uuid')
                        username = student.get('username', 'Unknown')
                        print(f"   {i+1}. {username}: {student_id}")
                    
                    # Return the first student ID for testing
                    first_student_id = data[0].get('student_id') or data[0].get('id') or data[0].get('uuid')
                    if first_student_id:
                        return first_student_id
                        
                elif isinstance(data, dict) and 'students' in data:
                    students = data['students']
                    if len(students) > 0:
                        first_student_id = students[0].get('student_id') or students[0].get('id')
                        return first_student_id
                        
            else:
                print(f"   Response: {response.text[:100]}...")
        except Exception as e:
            print(f"   Error: {e}")
    
    return None

def create_test_student():
    """Create a test student using the student management API"""
    print("\n📝 Creating Test Student...")
    
    base_url = "http://localhost:8000"
    
    try:
        student_data = {
            "username": "exam_test_student",
            "email": "examtest@test.com", 
            "first_name": "Exam",
            "last_name": "Tester"
        }
        
        create_response = requests.post(
            f"{base_url}/api/assessment/students/create",
            json=student_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Create Status: {create_response.status_code}")
        
        if create_response.status_code == 200:
            created_student = create_response.json()
            student_id = created_student.get('student_id')
            print(f"   ✅ Created student: {student_id}")
            return student_id
        else:
            print(f"   Create Error: {create_response.text}")
            
    except Exception as e:
        print(f"   Create Exception: {e}")
    
    return None

def test_with_real_student_id(student_id):
    """Test orchestrated API with real student UUID"""
    print(f"\n🧪 Testing with Real Student ID: {student_id}")
    
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
            print(f"   🎉 SUCCESS!")
            print(f"   Session: {json.dumps(session_data, indent=2)}")
            return True
        else:
            print(f"   Error: {session_response.text}")
            return False
            
    except Exception as e:
        print(f"   Exception: {e}")
        return False

def main():
    """Main test flow"""
    # Try to get existing student IDs
    student_id = get_real_student_ids()
    
    if not student_id:
        # Try to create a new student
        student_id = create_test_student()
    
    if student_id:
        success = test_with_real_student_id(student_id)
        
        if success:
            print(f"\n🎉 WORKING STUDENT ID FOUND: {student_id}")
            print("✅ Update frontend to use this UUID format!")
            print(f"   Replace 'student_id: \"1\"' with 'student_id: \"{student_id}\"'")
        else:
            print(f"\n❌ Still issues with student ID: {student_id}")
    else:
        print("\n❌ Could not find or create a valid student ID")
        print("💡 Check if backend has any students or student creation endpoints")

if __name__ == "__main__":
    main()