#!/usr/bin/env python3
"""
Test script to demonstrate BKT and DKT working together
"""

import requests
import json
import time

def test_api_endpoint(url, description):
    """Test a single API endpoint"""
    try:
        print(f"\n🧪 Testing: {description}")
        print(f"📍 URL: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Response: {json.dumps(data, indent=2)}")
            return True, data
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print(f"🚫 Connection Error: Server not running at {url}")
        return False, None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False, None

def test_post_endpoint(url, data, description):
    """Test a POST endpoint"""
    try:
        print(f"\n🧪 Testing: {description}")
        print(f"📍 URL: {url}")
        print(f"📤 Data: {json.dumps(data, indent=2)}")
        
        response = requests.post(url, json=data, timeout=10)
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            response_data = response.json()
            print(f"📊 Response: {json.dumps(response_data, indent=2)}")
            return True, response_data
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print(f"🚫 Connection Error: Server not running at {url}")
        return False, None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False, None

def main():
    """Main test function"""
    print("=" * 60)
    print("🤖 BKT + DKT Integration Test")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    
    # Test basic connectivity
    print("\n🔗 Testing Basic Connectivity...")
    success, _ = test_api_endpoint(f"{base_url}/api/docs", "API Documentation")
    if not success:
        print("\n🚫 Django server is not running!")
        print("📝 To start Django server, run:")
        print("   python manage.py runserver")
        return
    
    # Test student model status (BKT + DKT status)
    print("\n🔍 Testing Algorithm Status...")
    test_api_endpoint(f"{base_url}/api/student_model/status", "Student Model Status (BKT + DKT)")
    
    # Test DKT health check
    print("\n🏥 Testing DKT Service Health...")
    test_api_endpoint(f"{base_url}/api/student_model/dkt/health", "DKT Microservice Health Check")
    
    # Test knowledge components
    print("\n📚 Testing Knowledge Components...")
    test_api_endpoint(f"{base_url}/api/student_model/knowledge-components", "Knowledge Components List")
    
    # Test BKT endpoints (requires student creation first)
    print("\n🧠 Testing BKT Integration...")
    
    # Create test user first (this might fail if user doesn't exist)
    bkt_update_data = {
        "skill_id": "algebra_basics",
        "is_correct": True,
        "interaction_data": {
            "question_id": "q1",
            "response_time": 15.5,
            "timestamp": "2025-09-25T00:45:00Z"
        }
    }
    
    # Test BKT update (might fail without proper user setup)
    test_post_endpoint(
        f"{base_url}/api/student_model/student/1/bkt/update", 
        bkt_update_data,
        "BKT Parameter Update"
    )
    
    # Test DKT endpoints
    print("\n🧬 Testing DKT Integration...")
    
    dkt_update_data = {
        "student_id": "test-student-123",
        "skill_id": 0,
        "is_correct": True,
        "response_time": 12.3
    }
    
    test_post_endpoint(
        f"{base_url}/api/student_model/dkt/update",
        dkt_update_data,
        "DKT Knowledge State Update"
    )
    
    # Test algorithm comparison
    print("\n⚖️ Testing Algorithm Comparison...")
    test_api_endpoint(
        f"{base_url}/api/student_model/algorithms/compare/1",
        "BKT vs DKT Algorithm Comparison"
    )
    
    # Test DKT predictions
    print("\n🔮 Testing DKT Predictions...")
    test_api_endpoint(
        f"{base_url}/api/student_model/dkt/predict/test-student-123",
        "DKT Skill Predictions"
    )
    
    print("\n" + "=" * 60)
    print("✅ BKT + DKT Integration Test Complete!")
    print("=" * 60)
    print("\n📝 Summary:")
    print("• BKT Algorithm: Traditional Bayesian Knowledge Tracing")
    print("• DKT Algorithm: Deep Learning with LSTM Networks") 
    print("• Integration: Smart fallbacks and algorithm selection")
    print("• Microservice: DKT runs as separate FastAPI service")
    print("\n🚀 To start DKT microservice:")
    print("   cd dkt-service")
    print("   python start.py")

if __name__ == "__main__":
    main()