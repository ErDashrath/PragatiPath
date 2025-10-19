#!/usr/bin/env python3
"""
Quick API Endpoint Test
Tests if the enhanced exam API endpoints are now accessible
"""

import requests

def test_api_endpoints():
    """Test the enhanced exam API endpoints"""
    print("🔍 TESTING ENHANCED EXAM API ENDPOINTS")
    print("=" * 40)
    
    base_url = "http://localhost:8000/api"
    
    endpoints_to_test = [
        ("subjects", f"{base_url}/enhanced-exam/admin/subjects/details"),
        ("exam list", f"{base_url}/enhanced-exam/admin/exams/list"),
        ("student exams", f"{base_url}/enhanced-exam/student/exams/available"),
    ]
    
    for endpoint_name, url in endpoints_to_test:
        try:
            print(f"Testing {endpoint_name}: {url}")
            response = requests.get(url, timeout=5)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Success")
                data = response.json()
                if isinstance(data, list):
                    print(f"   📊 Returned {len(data)} items")
                elif isinstance(data, dict):
                    print(f"   📊 Returned data with keys: {list(data.keys())}")
            else:
                print(f"   ❌ Failed")
                
        except requests.exceptions.ConnectionError:
            print(f"   ⚠️  Server not running on localhost:8000")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()

if __name__ == "__main__":
    test_api_endpoints()