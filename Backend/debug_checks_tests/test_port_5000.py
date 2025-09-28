#!/usr/bin/env python3

import requests
import json

def test_frontend_port_5000():
    """Test frontend on port 5000 with proxy"""
    
    print("🔗 TESTING FRONTEND ON PORT 5000")
    print("=" * 60)
    
    # Test endpoints
    test_cases = [
        {
            "name": "Direct Backend",
            "url": "http://localhost:8000/api/core/register",
            "description": "Direct access to Django backend"
        },
        {
            "name": "Through Frontend Proxy (Port 5000)", 
            "url": "http://localhost:5000/api/core/register",
            "description": "Access through frontend dev server proxy"
        }
    ]
    
    test_payload = {
        "username": f"port5000_test_{hash('port5000') % 1000}",
        "password": "port5000test123",
        "confirm_password": "port5000test123",
        "email": f"port5000_test_{hash('port5000') % 1000}@example.com",
        "full_name": "Port 5000 Test User"
    }
    
    for test_case in test_cases:
        print(f"\n🎯 Testing: {test_case['name']}")
        print(f"📝 {test_case['description']}")
        print(f"🔗 URL: {test_case['url']}")
        
        try:
            response = requests.post(
                test_case['url'],
                json=test_payload,
                headers={
                    "Content-Type": "application/json",
                    "Origin": "http://localhost:5000"  # Add origin header
                },
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
                except Exception as e:
                    print(f"⚠️ SUCCESS but invalid JSON: {str(e)}")
                    
            elif response.status_code >= 400 and 'application/json' in response.headers.get('content-type', ''):
                try:
                    error_data = response.json()
                    print(f"❌ ERROR - JSON Error Response:")
                    print(f"   Detail: {error_data.get('detail', 'N/A')}")
                except Exception as e:
                    print(f"❌ ERROR - Could not parse JSON error: {str(e)}")
            else:
                print(f"❌ ERROR - HTML/Text Response (DOCTYPE issue)")
                response_preview = response.text[:200].replace('\n', ' ')
                print(f"   Preview: {response_preview}")
                
                if '<!DOCTYPE' in response.text[:100]:
                    print("🚨 HTML DOCTYPE detected - this is the source of your frontend error!")
                    
                    # Try to extract meaningful error info
                    if 'Internal Server Error' in response.text:
                        print("💥 Internal Server Error detected")
                    if 'Bad Request' in response.text:
                        print("💥 Bad Request detected")
                    if 'Not Found' in response.text:
                        print("💥 Not Found detected")
                        
        except requests.exceptions.ConnectionError:
            print(f"❌ CONNECTION FAILED - Server not running on this port")
        except requests.exceptions.Timeout:
            print(f"❌ TIMEOUT - Server took too long to respond")
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
    
    # Also test a simple GET request to see if the server is responding
    print(f"\n🏥 Testing simple GET request to port 5000...")
    try:
        health_response = requests.get("http://localhost:5000/", timeout=5)
        print(f"GET Status: {health_response.status_code}")
        print(f"GET Content-Type: {health_response.headers.get('content-type', 'N/A')}")
        if health_response.status_code == 200:
            print("✅ Frontend server is responding to GET requests")
        else:
            print("⚠️ Frontend server returned non-200 for GET request")
    except Exception as e:
        print(f"❌ GET request failed: {str(e)}")
    
    print(f"\n" + "=" * 60)
    print("📋 PORT 5000 TEST RESULTS:")
    print("✅ If Direct Backend works: Django server is fine")
    print("✅ If Port 5000 Proxy works: Frontend proxy is configured correctly")
    print("❌ If Port 5000 returns HTML: Frontend server has an error or no proxy")

if __name__ == "__main__":
    test_frontend_port_5000()