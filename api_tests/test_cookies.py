#!/usr/bin/env python3
"""
Debug cookie forwarding in the proxy
"""
import requests
import json

def test_cookies():
    print("🍪 Testing Cookie Forwarding")
    print("=" * 50)
    
    session = requests.Session()
    
    # Test login and inspect all headers/cookies
    login_data = {
        "username": "testuser123",
        "password": "testpassword123"
    }
    
    print("\n1. Login via Proxy - Detailed Headers...")
    response = session.post("http://localhost:5000/api/core/login", json=login_data)
    print(f"   Status: {response.status_code}")
    print(f"   Response Headers: {dict(response.headers)}")
    print(f"   Response Cookies: {dict(response.cookies)}")
    print(f"   Session Cookies After: {dict(session.cookies)}")
    
    print("\n2. Get User via Proxy - With Session...")
    response = session.get("http://localhost:5000/api/user")
    print(f"   Status: {response.status_code}")
    print(f"   Request Headers: {dict(session.headers)}")
    print(f"   Session Cookies: {dict(session.cookies)}")
    if response.status_code != 200:
        print(f"   Error: {response.text}")
    
    print("\n3. Direct Django Login - For Comparison...")
    django_session = requests.Session()
    response = django_session.post("http://localhost:8000/api/core/login", json=login_data)
    print(f"   Status: {response.status_code}")
    print(f"   Response Headers: {dict(response.headers)}")
    print(f"   Response Cookies: {dict(response.cookies)}")
    print(f"   Session Cookies After: {dict(django_session.cookies)}")
    
    print("\n4. Direct Django Get User...")
    response = django_session.get("http://localhost:8000/api/core/user")
    print(f"   Status: {response.status_code}")
    print(f"   Session Cookies: {dict(django_session.cookies)}")

if __name__ == "__main__":
    test_cookies()