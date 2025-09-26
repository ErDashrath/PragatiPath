#!/usr/bin/env python3

import requests
import json

def debug_api_response():
    """Debug API response to identify the DOCTYPE issue"""
    
    print("🔍 DEBUGGING API RESPONSE")
    print("=" * 50)
    
    # Test data
    test_user = {
        "username": "debug_test_user",
        "password": "debugpassword123",
        "confirm_password": "debugpassword123",
        "email": "debug_test@example.com",
        "full_name": "Debug Test User"
    }
    
    # Test the registration endpoint
    url = "http://localhost:8000/api/core/register"
    
    try:
        print(f"🎯 Testing URL: {url}")
        print(f"📤 Sending data: {json.dumps(test_user, indent=2)}")
        
        response = requests.post(
            url,
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        # Get raw response text
        raw_text = response.text
        print(f"\n📄 Raw Response (first 500 chars):")
        print("=" * 50)
        print(raw_text[:500])
        print("=" * 50)
        
        # Try to parse as JSON
        try:
            json_data = response.json()
            print(f"\n✅ JSON Response: {json.dumps(json_data, indent=2)}")
        except requests.exceptions.JSONDecodeError as e:
            print(f"\n❌ JSON Parse Error: {str(e)}")
            print("💡 This indicates the server returned HTML instead of JSON")
            
            # Check if it's a Django error page
            if "<!DOCTYPE" in raw_text:
                print("🚨 Server returned HTML DOCTYPE - likely a Django error page")
                
                # Extract title if possible
                import re
                title_match = re.search(r'<title>(.*?)</title>', raw_text, re.IGNORECASE)
                if title_match:
                    print(f"📰 HTML Title: {title_match.group(1)}")
                    
                # Look for error information
                if "500" in raw_text:
                    print("💥 Server Error 500 detected")
                elif "404" in raw_text:
                    print("🔍 Not Found 404 detected")
                elif "403" in raw_text:
                    print("🚫 Forbidden 403 detected")
    
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is Django running on port 8000?")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
    
    # Also test a simple health endpoint
    print(f"\n🏥 Testing Health Endpoint...")
    try:
        health_response = requests.get("http://localhost:8000/api/health")
        print(f"Health Status: {health_response.status_code}")
        if health_response.status_code == 200:
            print(f"Health Response: {health_response.json()}")
        else:
            print(f"Health Raw: {health_response.text[:200]}")
    except Exception as e:
        print(f"Health Error: {str(e)}")

if __name__ == "__main__":
    debug_api_response()