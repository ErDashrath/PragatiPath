#!/usr/bin/env python3

import requests
import json

def test_frontend_proxy():
    """Test if frontend proxy is working correctly"""
    
    print("🔗 TESTING FRONTEND PROXY CONFIGURATION")
    print("=" * 60)
    
    # Test endpoints that frontend should access
    test_cases = [
        {
            "name": "Direct Backend",
            "url": "http://localhost:8000/api/core/register",
            "description": "Direct access to Django backend"
        },
        {
            "name": "Through Vite Proxy", 
            "url": "http://localhost:5173/api/core/register",
            "description": "Access through Vite dev server proxy"
        }
    ]
    
    test_payload = {
        "username": f"proxy_test_{hash('proxy') % 1000}",
        "password": "proxytest123",
        "confirm_password": "proxytest123",
        "email": f"proxy_test_{hash('proxy') % 1000}@example.com",
        "full_name": "Proxy Test User"
    }
    
    for test_case in test_cases:
        print(f"\n🎯 Testing: {test_case['name']}")
        print(f"📝 {test_case['description']}")
        print(f"🔗 URL: {test_case['url']}")
        
        try:
            response = requests.post(
                test_case['url'],
                json=test_payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"📊 Status: {response.status_code}")
            print(f"🔍 Content-Type: {response.headers.get('content-type', 'N/A')}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ SUCCESS - JSON Response received")
                    print(f"👤 Username: {data.get('username', 'N/A')}")
                    print(f"📧 Email: {data.get('email', 'N/A')}")
                except:
                    print(f"⚠️ SUCCESS but invalid JSON")
                    
            elif 'application/json' in response.headers.get('content-type', ''):
                try:
                    error_data = response.json()
                    print(f"❌ ERROR - JSON Error Response:")
                    print(f"   Detail: {error_data.get('detail', 'N/A')}")
                except:
                    print(f"❌ ERROR - Could not parse JSON error")
            else:
                print(f"❌ ERROR - HTML/Text Response (DOCTYPE issue)")
                if '<!DOCTYPE' in response.text[:100]:
                    print("🚨 HTML DOCTYPE detected - this causes frontend JSON parse errors")
                    
        except requests.exceptions.ConnectionError:
            print(f"❌ CONNECTION FAILED - Server not running or proxy not working")
        except requests.exceptions.Timeout:
            print(f"❌ TIMEOUT - Server took too long to respond")
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
    
    print(f"\n" + "=" * 60)
    print("📋 PROXY TEST SUMMARY:")
    print("✅ If Direct Backend works: Django server is fine")
    print("✅ If Vite Proxy works: Frontend proxy is configured correctly")
    print("❌ If Vite Proxy fails: Need to restart Vite dev server after config change")

if __name__ == "__main__":
    test_frontend_proxy()