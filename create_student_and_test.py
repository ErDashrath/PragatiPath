#!/usr/bin/env python3
"""
Create a student and test the orchestrated API
"""

import requests
import json
import uuid

def create_student_and_test():
    """Create a student first, then test the orchestrated API"""
    print("👤 Creating Student and Testing Orchestrated API")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # First, let's try to create a student or check existing students
    print("\n1. Checking for existing students...")
    
    try:
        # Try to get students list
        students_response = requests.get(f"{base_url}/api/students/")
        
        if students_response.status_code == 200:
            students_data = students_response.json()
            print(f"   Existing students: {students_data}")
            
            if students_data and len(students_data) > 0:
                # Use the first existing student
                student_id = students_data[0].get('id') or students_data[0].get('student_id')
                print(f"   Using existing student: {student_id}")
                return test_with_student_id(student_id)
        else:
            print(f"   Students endpoint not available: {students_response.status_code}")
    except Exception as e:
        print(f"   Error getting students: {e}")
    
    # Try creating a student
    print("\n2. Creating a new student...")
    
    try:
        student_data = {
            "username": "test_student_orchestrated",
            "email": "test@example.com",
            "name": "Test Student",
            "phone": "1234567890"
        }
        
        create_response = requests.post(
            f"{base_url}/api/students/create/",
            json=student_data,
            headers={"Content-Type": "application/json"}
        )
        
        if create_response.status_code == 201:
            created_student = create_response.json()
            student_id = created_student.get('id') or created_student.get('student_id')
            print(f"   ✅ Created student: {student_id}")
            return test_with_student_id(student_id)
        else:
            print(f"   Student creation failed: {create_response.status_code}")
            print(f"   Response: {create_response.text}")
    except Exception as e:
        print(f"   Error creating student: {e}")
    
    # If all else fails, try with a known working approach
    print("\n3. Trying alternative approaches...")
    
    # Let's check what student IDs are actually in the system
    try:
        # Try to use a UUID format
        test_uuid = str(uuid.uuid4())
        print(f"   Generated UUID: {test_uuid}")
        return test_with_student_id(test_uuid)
    except Exception as e:
        print(f"   UUID approach failed: {e}")
    
    # Last resort - check if there's a simple ID format that works
    simple_ids_to_try = ["student_1", "1", "test_student"]
    
    for student_id in simple_ids_to_try:
        print(f"\n   Trying student_id: {student_id}")
        success = test_with_student_id(student_id)
        if success:
            return True
    
    return False

def test_with_student_id(student_id):
    """Test the orchestrated API with a specific student ID"""
    print(f"\n🧪 Testing with student_id: {student_id}")
    
    base_url = "http://localhost:8000"
    
    exam_config = {
        "student_id": str(student_id),
        "subject": "quantitative_aptitude",
        "session_type": "timed_exam",
        "max_questions": 3
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
            print(f"   🎉 Session Success!")
            print(f"   Session Data: {json.dumps(session_data, indent=2)}")
            
            if session_data.get('success'):
                return True
        else:
            print(f"   Session Error: {session_response.text}")
            
    except Exception as e:
        print(f"   Exception: {e}")
    
    return False

if __name__ == "__main__":
    success = create_student_and_test()
    
    if success:
        print("\n🎉 SUCCESS! Found working student ID format")
        print("✅ Ready to update frontend with correct student ID!")
    else:
        print("\n❌ Still need to resolve student ID format")