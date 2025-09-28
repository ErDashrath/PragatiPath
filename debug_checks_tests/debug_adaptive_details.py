#!/usr/bin/env python3

import requests
import json

def debug_adaptive_details_issue():
    """Debug why adaptive learning Details button fails"""
    
    print("🔍 DEBUGGING ADAPTIVE DETAILS ISSUE")
    print("=" * 45)
    
    # From the screenshot, we can see there are adaptive sessions
    # Let's test what happens when we try to get their details
    
    print("1️⃣ Testing Backend API Endpoints...")
    
    # Test the session details endpoint we modified
    session_id = "dc684f75-c850-4495-b17d-7f12c4b4b31f"
    
    try:
        # Test the backend directly
        backend_url = f"http://localhost:8000/history/session-details/{session_id}/"
        print(f"Testing: {backend_url}")
        
        response = requests.get(backend_url)
        print(f"Backend Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend API working!")
            print(f"Session found: {data.get('session_details', {}).get('session_name', 'Unknown')}")
        else:
            print(f"❌ Backend API failed: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Backend API error: {e}")
    
    print("\n2️⃣ Checking Frontend Proxy...")
    
    try:
        # Test through frontend proxy (what the UI actually calls)
        frontend_url = f"http://localhost:5000/api/results/{session_id}/"
        print(f"Testing regular API: {frontend_url}")
        
        response = requests.get(frontend_url)
        print(f"Regular API Status: {response.status_code}")
        
        if response.status_code != 200:
            print("❌ Regular assessment API fails for adaptive sessions (expected)")
            print("This is why we need the fallback to session details endpoint")
        
    except Exception as e:
        print(f"⚠️ Regular API error (expected): {e}")
    
    print("\n3️⃣ Root Cause Analysis:")
    print("📋 The issue is likely:")
    print("   1. Frontend makes request to /api/results/{sessionId}/ first")
    print("   2. This fails for adaptive sessions (they're not regular assessments)")  
    print("   3. Frontend should fallback to /history/session-details/{sessionId}/")
    print("   4. But the fallback might not be working properly")
    
    print("\n4️⃣ Solution:")
    print("   - Check that the frontend properly handles the API fallback")
    print("   - Ensure the session-details endpoint is called correctly")
    print("   - Verify data mapping in DetailedResultView component")
    
    print("\n🔍 Let me check the DetailedResultView error handling...")
    
    return True

if __name__ == "__main__":
    debug_adaptive_details_issue()