#!/usr/bin/env python3

import requests
import webbrowser
import time

def test_frontend_display():
    """Test if the frontend is properly displaying the data"""
    
    print("🔍 Frontend Display Test")
    print("=" * 30)
    
    # Check backend API first
    session_id = "dc684f75-c850-4495-b17d-7f12c4b4b31f"
    backend_url = f"http://localhost:8000/history/session-details/{session_id}/"
    
    try:
        print("1️⃣ Testing backend API...")
        response = requests.get(backend_url)
        
        if response.status_code == 200:
            data = response.json()
            session_details = data.get('session_details', {})
            
            print("✅ Backend API working!")
            print(f"   - Session: {session_details.get('session_name')}")
            print(f"   - Questions: {session_details.get('questions_attempted')}")
            print(f"   - Accuracy: {session_details.get('accuracy_percentage')}%")
            print(f"   - Real question attempts: {len(session_details.get('question_attempts', []))}")
            
        else:
            print(f"❌ Backend API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend API error: {e}")
        return False
    
    # Check frontend server
    print("\n2️⃣ Testing frontend server...")
    try:
        frontend_response = requests.get("http://localhost:5000", timeout=5)
        if frontend_response.status_code == 200:
            print("✅ Frontend server responding!")
        else:
            print(f"❌ Frontend server issue: {frontend_response.status_code}")
    except Exception as e:
        print(f"❌ Frontend server error: {e}")
        print("💡 Make sure frontend is running on port 5000")
        return False
    
    print("\n3️⃣ Manual Testing Instructions:")
    print("=" * 40)
    print("🌐 Frontend URL: http://localhost:5000")
    print("📝 Login with your student credentials")
    print("📊 Navigate to: Assessment History")
    print("🔍 Look for: 'Adaptive Verbal Ability Session'")
    print("👁️ Click: Details button (eye icon)")
    print("📋 Verify you see:")
    print("   ✅ Session name and metrics")
    print("   ✅ Real question attempts (15 questions)")
    print("   ✅ Actual answers (A, B, C, D)")
    print("   ✅ Real time spent per question") 
    print("   ✅ Difficulty levels (easy, moderate, difficult)")
    print("   ✅ Mastery progression section")
    print("   ❌ NO 'Adaptive Question X' simulated text")
    
    # Open browser automatically
    print(f"\n🚀 Opening browser...")
    try:
        webbrowser.open('http://localhost:5000')
        print("✅ Browser opened! Please test the Details view manually.")
    except Exception as e:
        print(f"⚠️ Could not open browser automatically: {e}")
        print("📱 Please manually open: http://localhost:5000")
    
    return True

if __name__ == "__main__":
    print("🎯 Testing Frontend Display Integration")
    print("=" * 50)
    
    success = test_frontend_display()
    
    if success:
        print(f"\n🎉 TEST COMPLETE!")
        print(f"📱 Please test the UI manually to verify real data display")
        print(f"🔍 Look for actual question attempts instead of simulated ones")
    else:
        print(f"\n❌ Test failed - check server status")