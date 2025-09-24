#!/usr/bin/env python3
"""
Test the comprehensive orchestration endpoint
"""

import requests
import json
import time

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

url = "http://127.0.0.1:8000/api/v1/assessment/submit-answer"

print("🚀 Testing Comprehensive Orchestration Endpoint")
print("=" * 60)
print("📡 URL:", url)
print("📝 Payload:")
print(json.dumps(payload, indent=2))
print("\n🔄 Sending request...")

try:
    response = requests.post(
        url, 
        json=payload, 
        headers={'Content-Type': 'application/json'},
        timeout=30
    )
    
    print(f"📊 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCCESS! Response:")
        result = response.json()
        print(json.dumps(result, indent=2))
        
        # Highlight key results
        print("\n🎯 Key Results:")
        if 'algorithm_results' in result:
            for alg, res in result['algorithm_results'].items():
                print(f"   {alg.upper()}: {res.get('status', 'unknown')}")
        
        if 'next_question' in result:
            print(f"   Next Question: {result['next_question'].get('question_text', 'N/A')}")
            
    else:
        print(f"❌ ERROR {response.status_code}:")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("❌ Connection Error: Is the Django server running on port 8000?")
except requests.exceptions.RequestException as e:
    print(f"❌ Request Error: {e}")
except Exception as e:
    print(f"❌ Unexpected Error: {e}")

print("\n🏁 Test completed!")