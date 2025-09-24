#!/usr/bin/env python3
"""
Test the comprehensive orchestration endpoint using urllib
"""

import urllib.request
import urllib.parse
import json
import sys

# Test data from the demo
payload = {
    "student_id": "fec9dc2b-f347-498e-a66f-f01a976b9cee",
    "question_id": "b80eda84-b166-4d1a-8029-8abe9e94ad0f",
    "answer": "x = 5",
    "response_time": 8.5,
    "skill_id": "algebra",
    "metadata": {
        "attempt_number": 1,
        "hint_used": False
    }
}

url = "http://127.0.0.1:8000/api/assessment/submit-answer"

print("🚀 Testing Comprehensive Orchestration Endpoint")
print("=" * 60)
print("📡 URL:", url)
print("📝 Payload:")
print(json.dumps(payload, indent=2))
print("\n🔄 Sending request...")

try:
    # Convert payload to JSON bytes
    data = json.dumps(payload).encode('utf-8')
    
    # Create request
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            'Content-Type': 'application/json',
            'Content-Length': str(len(data))
        },
        method='POST'
    )
    
    # Send request
    with urllib.request.urlopen(req, timeout=30) as response:
        status_code = response.getcode()
        response_data = response.read().decode('utf-8')
        
        print(f"📊 Response Status: {status_code}")
        
        if status_code == 200:
            print("✅ SUCCESS! Response:")
            result = json.loads(response_data)
            print(json.dumps(result, indent=2))
            
            # Highlight key results
            print("\n🎯 Key Results:")
            if 'algorithm_results' in result:
                for alg, res in result['algorithm_results'].items():
                    print(f"   {alg.upper()}: {res.get('status', 'unknown')}")
            
            if 'next_question' in result:
                print(f"   Next Question: {result['next_question'].get('question_text', 'N/A')}")
                
        else:
            print(f"❌ ERROR {status_code}:")
            print(response_data)
            
except urllib.error.HTTPError as e:
    print(f"❌ HTTP Error {e.code}:")
    error_response = e.read().decode('utf-8')
    print(error_response)
    try:
        error_json = json.loads(error_response)
        print("Error details:", json.dumps(error_json, indent=2))
    except:
        pass
        
except urllib.error.URLError as e:
    print(f"❌ Connection Error: {e.reason}")
    print("Is the Django server running on port 8000?")
    
except Exception as e:
    print(f"❌ Unexpected Error: {e}")

print("\n🏁 Test completed!")