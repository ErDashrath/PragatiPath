#!/usr/bin/env python3
"""
Quick test to isolate the exam completion issue
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_complete_exam():
    print("🔍 Testing Exam Completion Issue...")
    
    # Use existing student ID
    student_id = "52938de0-cf62-4794-99ff-73cf75becf79"
    
    # Start an EXAM session
    print("1. Starting EXAM session...")
    exam_response = requests.post(f"{BASE_URL}/api/assessment/v2/assessment/start", json={
        "student_id": student_id,
        "subject": "quantitative_aptitude", 
        "assessment_mode": "EXAM"
    })
    
    print(f"   Status: {exam_response.status_code}")
    if exam_response.status_code != 200:
        print(f"   Error: {exam_response.text}")
        return
    
    exam_data = exam_response.json()
    session_id = exam_data['session_id']
    print(f"   Session: {session_id[:8]}...")
    
    # Try to complete the exam
    print("2. Completing exam...")
    complete_response = requests.post(f"{BASE_URL}/api/assessment/v2/exam/complete", json={
        "student_id": student_id,
        "session_id": session_id,
        "request_ai_analysis": True
    })
    
    print(f"   Status: {complete_response.status_code}")
    if complete_response.status_code == 200:
        complete_data = complete_response.json()
        print(f"   ✅ Success: {complete_data['success']}")
        print(f"   AI Analysis: {complete_data['ai_analysis_requested']}")
    else:
        print(f"   ❌ Error: {complete_response.text}")

if __name__ == "__main__":
    test_complete_exam()