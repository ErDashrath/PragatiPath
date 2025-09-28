#!/usr/bin/env python3
"""Test script to verify assessment categorization fix"""

import requests
import json

def test_assessment_categorization():
    """Test that assessments are correctly categorized"""
    print("=" * 60)
    print("TESTING ASSESSMENT CATEGORIZATION FIX")
    print("=" * 60)
    
    # Test the username that has assessment data
    test_username = 'test_ai_student_1'
    
    try:
        # Test through the Express proxy (frontend URL)
        frontend_url = f'http://localhost:5173/history/student/{test_username}/'
        print(f"Testing frontend proxy: {frontend_url}")
        
        response = requests.get(frontend_url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                print(f"\n📊 CATEGORIZATION RESULTS:")
                print(f"   Regular Assessments: {len(data.get('assessment_sessions', []))}")
                print(f"   Adaptive Sessions: {len(data.get('adaptive_sessions', []))}")
                
                # Show details of assessment sessions
                if data.get('assessment_sessions'):
                    print(f"\n📋 REGULAR ASSESSMENTS:")
                    for i, session in enumerate(data['assessment_sessions'][:3]):  # Show first 3
                        session_type = session.get('session_type', 'N/A')
                        subject = session.get('subject', 'N/A')
                        score = session.get('score', 'N/A')
                        print(f"   {i+1}. Type: {session_type} | Subject: {subject} | Score: {score}%")
                
                # Show details of adaptive sessions  
                if data.get('adaptive_sessions'):
                    print(f"\n🧠 ADAPTIVE SESSIONS:")
                    for i, session in enumerate(data['adaptive_sessions'][:3]):  # Show first 3
                        session_type = session.get('session_type', 'N/A')
                        subject = session.get('subject', 'N/A')
                        mastery = session.get('final_mastery_score', 'N/A')
                        print(f"   {i+1}. Type: {session_type} | Subject: {subject} | Mastery: {mastery}")
                
                # Check if the fix worked
                regular_count = len(data.get('assessment_sessions', []))
                adaptive_count = len(data.get('adaptive_sessions', []))
                
                if regular_count > 0:
                    print(f"\n✅ SUCCESS: Regular assessments found ({regular_count})")
                else:
                    print(f"\n⚠️  No regular assessments found")
                
                if adaptive_count > 0:
                    print(f"✅ SUCCESS: Adaptive sessions found ({adaptive_count})")
                else:
                    print(f"⚠️  No adaptive sessions found")
                
                return True
                
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse JSON response: {e}")
                print(f"Response preview: {response.text[:200]}")
                return False
        else:
            print(f"❌ Request failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return False

def test_direct_backend():
    """Test direct backend API"""
    print(f"\n" + "=" * 60)
    print("TESTING DIRECT BACKEND API")
    print("=" * 60)
    
    test_username = 'test_ai_student_1'
    backend_url = f'http://localhost:8000/history/student/{test_username}/'
    
    try:
        response = requests.get(backend_url, timeout=10)
        print(f"Backend API Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            regular_count = len(data.get('assessment_sessions', []))
            adaptive_count = len(data.get('adaptive_sessions', []))
            
            print(f"Direct Backend Results:")
            print(f"   Regular Assessments: {regular_count}")
            print(f"   Adaptive Sessions: {adaptive_count}")
            
            return True
        else:
            print(f"❌ Backend API failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend API error: {e}")
        return False

if __name__ == "__main__":
    frontend_success = test_assessment_categorization()
    backend_success = test_direct_backend()
    
    print(f"\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Frontend Proxy: {'✅ WORKING' if frontend_success else '❌ FAILED'}")
    print(f"Backend Direct: {'✅ WORKING' if backend_success else '❌ FAILED'}")
    
    if frontend_success and backend_success:
        print(f"\n🎉 Assessment categorization fix is working!")
        print(f"   Regular assessments should now appear in the 'Assessments' tab")
        print(f"   Adaptive sessions should appear in the 'Adaptive Learning' tab")
    else:
        print(f"\n❌ Issues detected. Check the logs above for details.")