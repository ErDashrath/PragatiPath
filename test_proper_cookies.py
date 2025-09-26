#!/usr/bin/env python3
"""
Test auth flow with proper cookie jar that handles HttpOnly cookies
"""
import requests
from http.cookiejar import CookieJar
import json

def test_with_proper_cookies():
    print("🍪 Testing With Proper Cookie Handling")
    print("=" * 50)
    
    # Use a proper cookie jar that handles HttpOnly cookies
    session = requests.Session()
    session.cookies = CookieJar()
    
    login_data = {
        "username": "testuser123", 
        "password": "testpassword123"
    }
    
    print("\n1. Login via Proxy...")
    response = session.post("http://localhost:5000/api/core/login", json=login_data)
    print(f"   Status: {response.status_code}")
    
    # Print all cookies including HttpOnly ones
    print("   All cookies in jar:")
    for cookie in session.cookies:
        print(f"     {cookie.name}={cookie.value} (HttpOnly: {cookie._rest.get('HttpOnly', False)})")
    
    if response.status_code == 200:
        print(f"   Login Success: {response.json()}")
        
        print("\n2. Get User via Proxy...")
        response = session.get("http://localhost:5000/api/user")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   User Success: {response.json()}")
        else:
            print(f"   User Error: {response.text}")
            
        # Also test with manual cookie setting
        print("\n3. Test Manual Cookie Forward...")
        cookies_header = "; ".join([f"{c.name}={c.value}" for c in session.cookies])
        print(f"   Manual cookies header: {cookies_header}")
        
        manual_response = requests.get(
            "http://localhost:5000/api/user",
            headers={"Cookie": cookies_header}
        )
        print(f"   Manual Status: {manual_response.status_code}")
        if manual_response.status_code != 200:
            print(f"   Manual Error: {manual_response.text}")

if __name__ == "__main__":
    test_with_proper_cookies()