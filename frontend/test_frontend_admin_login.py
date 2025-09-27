#!/usr/bin/env python3
"""Test admin login from frontend perspective"""

import requests
import json

# Test frontend admin login
print("Testing admin login from frontend perspective...")
print("="*50)

# Login with admin credentials
login_data = {
    "username": "admin",
    "password": "admin123"
}

try:
    response = requests.post(
        "http://localhost:8000/api/core/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    if response.headers.get('content-type', '').startswith('application/json'):
        data = response.json()
        print(f"Response Data: {json.dumps(data, indent=2)}")
        
        # Check if userType is admin
        if data.get('userType') == 'admin':
            print("✅ Backend correctly returns userType: admin")
        else:
            print("❌ Backend NOT returning userType as admin")
            
    else:
        print("❌ Response is not JSON:")
        print(response.text[:500])
        
except Exception as e:
    print(f"❌ Error testing admin login: {e}")

# Test the user endpoint that frontend calls after login
print("\n" + "="*50)
print("Testing /api/user endpoint (what frontend calls after login)...")

try:
    # First login to get session
    session = requests.Session()
    login_response = session.post(
        "http://localhost:8000/api/core/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if login_response.status_code == 200:
        # Now test the user endpoint
        user_response = session.get("http://localhost:8000/api/user")
        
        print(f"Status Code: {user_response.status_code}")
        
        if user_response.headers.get('content-type', '').startswith('application/json'):
            user_data = user_response.json()
            print(f"User Data: {json.dumps(user_data, indent=2)}")
            
            if user_data.get('userType') == 'admin':
                print("✅ /api/user correctly returns userType: admin")
            else:
                print("❌ /api/user NOT returning userType as admin")
                
        else:
            print("❌ /api/user response is not JSON:")
            print(user_response.text[:500])
    else:
        print(f"❌ Login failed with status {login_response.status_code}")
        
except Exception as e:
    print(f"❌ Error testing /api/user endpoint: {e}")