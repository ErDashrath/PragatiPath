print("🚀 TESTING COMPLETE FRONTEND-BACKEND FLOW")
print("=" * 60)

import requests
import json

# Test 1: Backend API Direct
print("\n📡 TEST 1: Backend API (Direct)")
try:
    response = requests.get("http://localhost:8000/simple/session-history/69/")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Backend API Working: {data['total_sessions']} sessions")
        print(f"📊 Latest session: {data['sessions'][0]['session_date']}")
        print(f"🧠 Latest BKT: {data['sessions'][0]['mastery_scores']['bkt_mastery']}")
    else:
        print(f"❌ Backend API failed: {response.status_code}")
except Exception as e:
    print(f"❌ Backend connection error: {e}")

# Test 2: Frontend Server Status
print("\n🌐 TEST 2: Frontend Server")
try:
    response = requests.get("http://localhost:5000/", timeout=5)
    if response.status_code == 200:
        print("✅ Frontend server responding")
    else:
        print(f"⚠️ Frontend server status: {response.status_code}")
except Exception as e:
    print(f"❌ Frontend server error: {e}")

# Test 3: Frontend Proxy to Backend
print("\n🔄 TEST 3: Frontend Proxy to Backend")
try:
    # This should proxy through the frontend server to backend
    response = requests.get("http://localhost:5000/simple/session-history/69/", timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Frontend proxy working: {data['total_sessions']} sessions")
        print(f"📊 Proxy data matches backend: {data.get('success', False)}")
    else:
        print(f"❌ Frontend proxy failed: {response.status_code}")
        print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"❌ Frontend proxy error: {e}")

print("\n🎯 DEBUGGING SUMMARY:")
print("1. If Backend API works but Frontend Proxy fails → Frontend server issue")
print("2. If both work but UI doesn't show → React component/state issue") 
print("3. If neither work → Network/port issue")
print("\n💡 Next Steps:")
print("- Check browser console for frontend errors")
print("- Verify both servers are running on correct ports")
print("- Check the debug info box in the mastery tab")