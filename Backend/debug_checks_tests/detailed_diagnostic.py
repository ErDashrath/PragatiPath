#!/usr/bin/env python3
"""
Detailed Diagnostic Test for 500 Errors
"""
import requests
import json

def test_endpoint_detailed(url, description):
    """Test endpoint with detailed error reporting"""
    try:
        headers = {
            'Content-Type': 'application/json',
            'Origin': 'http://localhost:5000'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ {description}: SUCCESS")
            try:
                data = response.json()
                print(f"   Data keys: {list(data.keys()) if isinstance(data, dict) else 'list'}")
            except:
                print(f"   Non-JSON response")
        else:
            print(f"❌ {description}: {response.status_code}")
            print(f"   Error: {response.text[:300]}")
            
    except Exception as e:
        print(f"❌ {description}: CONNECTION ERROR - {str(e)}")

def main():
    base_url = "http://localhost:8000"
    student_id = "9bbcc9f4-bfe8-450f-b2fa-95f567625681"
    
    print("🔍 Detailed Diagnostic Test for 500 Errors")
    print("=" * 60)
    
    # Test the problematic endpoints
    endpoints = [
        (f"{base_url}/api/core/students/{student_id}", "Core API Student by UUID"),
        (f"{base_url}/api/analytics/students/{student_id}/performance", "Analytics Performance"),
        (f"{base_url}/api/student-model/student/{student_id}/bkt/states/all", "Student Model BKT States"),
        (f"{base_url}/api/practice/api/v1/practice/{student_id}/stats", "Practice Stats"),
        (f"{base_url}/api/competitive/v1/subjects", "Competitive Subjects"),
    ]
    
    for url, desc in endpoints:
        test_endpoint_detailed(url, desc)
        print()

if __name__ == "__main__":
    main()