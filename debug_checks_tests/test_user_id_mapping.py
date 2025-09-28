import requests
import json

print("🔍 TESTING SESSION CREATION AND USER ID MAPPING")
print("=" * 60)

# Test creating a new session to see what user ID gets returned
session_data = {
    "student_name": "Debug User ID Test", 
    "subject": "quantitative_aptitude"
}

print("🚀 Creating test session...")
response = requests.post("http://localhost:5000/simple/start-session/", 
                        json=session_data,
                        headers={"Content-Type": "application/json"})

if response.status_code == 200:
    data = response.json()
    print("✅ Session created successfully!")
    print(f"📝 Response data:")
    print(json.dumps(data, indent=2))
    
    user_id = data.get('user_id')
    student_id = data.get('student_id')
    
    print(f"\n🔧 Key Information:")
    print(f"   user_id: {user_id} (type: {type(user_id)})")
    print(f"   student_id: {student_id} (type: {type(student_id)})")
    
    # Test the history endpoint with the user_id
    print(f"\n🔍 Testing history with user_id {user_id}:")
    history_response = requests.get(f"http://localhost:5000/simple/session-history/{user_id}/")
    if history_response.status_code == 200:
        history_data = history_response.json()
        print(f"✅ History found: {history_data.get('total_sessions', 0)} sessions")
    else:
        print(f"❌ History failed: {history_response.status_code}")
        
else:
    print(f"❌ Session creation failed: {response.status_code}")
    print(response.text[:200])

print(f"\n💡 SOLUTION:")
print("The frontend should store and use the 'user_id' returned from session creation")
print("This user_id should be used for all subsequent history API calls")