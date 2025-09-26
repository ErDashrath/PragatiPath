#!/usr/bin/env python3

import requests
import json

def test_frontend_registration_error():
    """Test to reproduce the exact frontend registration error"""
    
    print("🔍 DEBUGGING FRONTEND REGISTRATION ERROR")
    print("=" * 60)
    
    # Test with the exact same payload the frontend would send
    frontend_payload = {
        "username": "frontend_test_user",
        "password": "testpassword123",
        "confirm_password": "testpassword123", 
        "email": "frontend_test@example.com",
        "full_name": "Frontend Test User"
    }
    
    print(f"🎯 Testing Frontend Registration Flow")
    print(f"📤 Payload: {json.dumps(frontend_payload, indent=2)}")
    
    try:
        # Test the exact endpoint the frontend uses
        response = requests.post(
            "http://localhost:8000/api/core/register",
            json=frontend_payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Frontend Test)"
            }
        )
        
        print(f"\n📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        # Check content type
        content_type = response.headers.get('content-type', '')
        print(f"🔍 Content-Type: {content_type}")
        
        # Get raw response
        raw_response = response.text
        print(f"\n📄 Raw Response (first 1000 chars):")
        print("=" * 50)
        print(raw_response[:1000])
        print("=" * 50)
        
        # Try to determine the issue
        if response.status_code == 200:
            if 'application/json' in content_type:
                data = response.json()
                print(f"✅ SUCCESS - JSON Response:")
                print(json.dumps(data, indent=2))
            else:
                print(f"⚠️ SUCCESS but wrong content type: {content_type}")
                
        elif response.status_code >= 400:
            if 'application/json' in content_type:
                try:
                    error_data = response.json()
                    print(f"❌ ERROR - JSON Response:")
                    print(json.dumps(error_data, indent=2))
                except:
                    print(f"❌ ERROR - Could not parse JSON")
            else:
                print(f"❌ ERROR - HTML/Text Response (this causes DOCTYPE error)")
                
                # Check if it's a Django error page
                if '<!DOCTYPE' in raw_response:
                    print("🚨 FOUND: HTML DOCTYPE in response!")
                    
                    # Extract error details from Django error page
                    import re
                    
                    # Look for exception info
                    exception_match = re.search(r'<h1>(.*?)</h1>', raw_response)
                    if exception_match:
                        print(f"💥 Exception: {exception_match.group(1)}")
                    
                    # Look for traceback
                    traceback_match = re.search(r'<div class="traceback">(.*?)</div>', raw_response, re.DOTALL)
                    if traceback_match:
                        print(f"🔍 Found traceback section")
                    
                    # Look for specific error patterns
                    if 'IntegrityError' in raw_response:
                        print("🔍 Database integrity error detected")
                    if 'ValidationError' in raw_response:
                        print("🔍 Validation error detected")
                    if 'KeyError' in raw_response:
                        print("🔍 Missing key error detected")
                        
        else:
            print(f"⚠️ Unexpected status code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - is Django server running on port 8000?")
    except Exception as e:
        print(f"❌ Test error: {str(e)}")
    
    print(f"\n" + "=" * 60)
    print("🔍 Frontend registration error analysis complete!")

if __name__ == "__main__":
    test_frontend_registration_error()