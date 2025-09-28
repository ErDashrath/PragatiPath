import requests
import json

print("🔍 CHECKING API RESPONSE FORMAT")
print("=" * 50)

try:
    response = requests.get("http://localhost:8000/simple/session-history/69/")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ API Response Status: 200 OK")
        print(f"📊 Response Keys: {list(data.keys())}")
        print(f"🔑 Has 'success' field: {'success' in data}")
        print(f"📈 Total Sessions: {data.get('total_sessions', 'N/A')}")
        
        if 'sessions' in data:
            print(f"📋 Number of Sessions: {len(data['sessions'])}")
            if data['sessions']:
                latest = data['sessions'][0]
                print(f"📅 Latest Session Date: {latest.get('session_date', 'N/A')}")
                print(f"📝 Latest Subject: {latest.get('subject_name', 'N/A')}")
        
        print("\n🔍 FULL API RESPONSE:")
        print(json.dumps(data, indent=2))
        
    else:
        print(f"❌ API Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Connection Error: {e}")
    print("🔧 Make sure Django backend is running on port 8000")