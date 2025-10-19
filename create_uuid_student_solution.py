#!/usr/bin/env python3
"""
Create a proper student using Django management command approach
"""

import requests
import json
import uuid

def create_uuid_student():
    """Try to understand and create UUID students"""
    print("🔧 Creating UUID Student for Orchestrated API")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # First, let's check what the frontend-orchestration health says about students
    print("\n1. Checking orchestration system health...")
    try:
        health_response = requests.get(f"{base_url}/api/frontend-orchestration/system/health")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"   Health: {json.dumps(health_data, indent=2)}")
        else:
            print(f"   Health check failed: {health_response.status_code}")
    except Exception as e:
        print(f"   Health error: {e}")
    
    # Since the system expects UUIDs, let's try some simple approaches
    print("\n2. Testing with different student ID approaches...")
    
    # List of approaches to try
    test_cases = [
        ("Integer as string", "1"),
        ("Different integer", "69"),  # From earlier logs
        ("Mock UUID", str(uuid.uuid4())),
        ("Test pattern", "test-student-uuid")
    ]
    
    for desc, student_id in test_cases:
        print(f"\n   Testing {desc}: {student_id}")
        
        exam_config = {
            "student_id": student_id,
            "subject": "quantitative_aptitude",
            "session_type": "exam",
            "max_questions": 3
        }
        
        try:
            session_response = requests.post(
                f"{base_url}/api/frontend-orchestration/learning-session/start",
                json=exam_config,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"      Status: {session_response.status_code}")
            
            if session_response.status_code == 200:
                session_data = session_response.json()
                print(f"      🎉 SUCCESS with {desc}!")
                print(f"      Working student_id: {student_id}")
                print(f"      Session: {json.dumps(session_data, indent=2)}")
                return student_id  # Return the working ID
            else:
                error_text = session_response.text
                print(f"      Error: {error_text[:100]}...")
                
        except Exception as e:
            print(f"      Exception: {e}")
    
    # If none work, try the original non-orchestrated adaptive session
    print("\n3. Testing non-orchestrated adaptive session for comparison...")
    try:
        adaptive_config = {
            "student_username": "test_student",
            "subject_code": "MATH",
            "chapter_id": "basic_arithmetic",
            "question_count": 5,
            "assessment_type": "ADAPTIVE"
        }
        
        adaptive_response = requests.post(
            f"{base_url}/api/full-assessment/start",
            json=adaptive_config,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Non-orchestrated Status: {adaptive_response.status_code}")
        if adaptive_response.status_code == 200:
            print(f"   ✅ Non-orchestrated works!")
            print(f"   Response: {adaptive_response.json()}")
        else:
            print(f"   Non-orchestrated Error: {adaptive_response.text[:100]}...")
            
    except Exception as e:
        print(f"   Non-orchestrated Exception: {e}")
    
    return None

def create_manual_solution():
    """Create a manual solution suggestion"""
    print("\n" + "=" * 60)
    print("🔧 MANUAL SOLUTION APPROACH")
    print("=" * 60)
    
    working_student_id = create_uuid_student()
    
    if working_student_id:
        print(f"\n✅ FOUND WORKING STUDENT ID: {working_student_id}")
        print("\n📝 UPDATE FRONTEND:")
        print(f"   Replace in timed-exam-interface.tsx:")
        print(f"   student_id: \"1\"")
        print(f"   →")
        print(f"   student_id: \"{working_student_id}\"")
        return True
    else:
        print("\n💡 ALTERNATIVE APPROACHES:")
        print("1. Check if Django admin has StudentProfile entries")
        print("2. Create StudentProfile manually via Django shell")
        print("3. Use non-orchestrated adaptive APIs instead")
        print("4. Modify orchestrated API to create student if not exists")
        
        print("\n🛠️  QUICK FIX OPTIONS:")
        print("A. Modify frontend to use non-orchestrated adaptive APIs")
        print("B. Create a student via Django admin panel")
        print("C. Add fallback student creation to orchestrated API")
        
        return False

if __name__ == "__main__":
    success = create_manual_solution()
    
    if success:
        print(f"\n🎉 READY FOR PRODUCTION!")
        print("✅ Frontend can now use orchestrated BKT+DKT APIs")
    else:
        print(f"\n🔧 NEEDS MANUAL INTERVENTION")
        print("Choose one of the suggested approaches to resolve student ID issue")