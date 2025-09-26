#!/usr/bin/env python3
"""
Test the subject mapping fix for adaptive learning
"""
import requests
import json

def test_verbal_subject_mapping():
    print("🧪 Testing Subject Mapping Fix")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Start session with verbal_ability
    print("\n1. Testing session start with 'verbal_ability'...")
    session_data = {
        "student_name": "Test Student",
        "subject": "verbal_ability"
    }
    
    try:
        response = requests.post(
            f"{base_url}/simple/start-session/",
            json=session_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            session = response.json()
            print(f"   Session created successfully!")
            print(f"   Session ID: {session.get('session_id')}")
            print(f"   Subject: {session.get('subject')}")
            print(f"   Subject Display: {session.get('subject_display')}")
            
            # Test 2: Get a question from this session
            print("\n2. Testing question retrieval...")
            session_id = session.get('session_id')
            
            question_response = requests.get(
                f"{base_url}/simple/get-question/{session_id}/"
            )
            
            print(f"   Question Status: {question_response.status_code}")
            if question_response.status_code == 200:
                question = question_response.json()
                print(f"   Question Subject: {question.get('subject')}")
                print(f"   Question Subject Display: {question.get('subject_display')}")
                print(f"   Question Text: {question.get('question_text', 'N/A')[:100]}...")
                
                # Check if we're getting the right subject
                if question.get('subject_display') == 'Verbal Ability':
                    print("   ✅ SUCCESS: Getting verbal ability questions!")
                else:
                    print(f"   ❌ FAIL: Expected 'Verbal Ability', got '{question.get('subject_display')}'")
            else:
                print(f"   Question Error: {question_response.text}")
        else:
            print(f"   Session Error: {response.text}")
            
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 3: Also test quantitative_aptitude direct mapping
    print("\n3. Testing session start with 'quantitative_aptitude'...")
    session_data = {
        "student_name": "Test Student 2",
        "subject": "quantitative_aptitude"
    }
    
    try:
        response = requests.post(
            f"{base_url}/simple/start-session/",
            json=session_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            session = response.json()
            print(f"   Subject Display: {session.get('subject_display')}")
            
            if session.get('subject_display') == 'Quantitative Aptitude':
                print("   ✅ SUCCESS: Quantitative mapping also works!")
            else:
                print(f"   ❌ FAIL: Expected 'Quantitative Aptitude', got '{session.get('subject_display')}'")
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"   Exception: {e}")

if __name__ == "__main__":
    test_verbal_subject_mapping()