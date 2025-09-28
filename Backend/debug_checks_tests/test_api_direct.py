import requests
import json

try:
    response = requests.get("http://localhost:8000/history/student/teststudent/")
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response keys: {list(data.keys())}")
        
        if 'assessment_sessions' in data:
            print(f"Assessment sessions: {len(data['assessment_sessions'])}")
        if 'adaptive_sessions' in data:
            print(f"Adaptive sessions: {len(data['adaptive_sessions'])}")
        if 'sessions' in data:
            print(f"Sessions: {len(data['sessions'])}")
            
        print("\nFull response:")
        print(json.dumps(data, indent=2)[:1000] + "..." if len(str(data)) > 1000 else json.dumps(data, indent=2))
    else:
        print(f"Error response: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()