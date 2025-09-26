#!/usr/bin/env python3
"""
Test the complete authentication flow through the proxy
"""
import requests
import json

# Base URLs
FRONTEND_URL = "http://localhost:5000"
BACKEND_URL = "http://localhost:8000"

def test_auth_flow():
    print("🧪 Testing Authentication Flow")
    print("=" * 50)
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Test 1: Register a user via proxy
    print("\n1. Testing Registration via Proxy...")
    register_data = {
        "username": "testuser123",
        "password": "testpassword123",
        "confirm_password": "testpassword123",
        "email": "test@example.com",
        "full_name": "Test User"
    }
    
    try:
        response = session.post(f"{FRONTEND_URL}/api/core/register", json=register_data)
        print(f"   Registration Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Registration Success: {response.json()}")
        else:
            print(f"   Registration Error: {response.text}")
    except Exception as e:
        print(f"   Registration Exception: {e}")
    
    # Test 2: Login via proxy
    print("\n2. Testing Login via Proxy...")
    login_data = {
        "username": "testuser123",
        "password": "testpassword123"
    }
    
    try:
        response = session.post(f"{FRONTEND_URL}/api/core/login", json=login_data)
        print(f"   Login Status: {response.status_code}")
        print(f"   Login Cookies: {dict(response.cookies)}")
        if response.status_code == 200:
            user_data = response.json()
            print(f"   Login Success: {user_data}")
        else:
            print(f"   Login Error: {response.text}")
    except Exception as e:
        print(f"   Login Exception: {e}")
    
    # Test 3: Get current user via proxy
    print("\n3. Testing Get Current User via Proxy...")
    try:
        response = session.get(f"{FRONTEND_URL}/api/user")
        print(f"   User Status: {response.status_code}")
        print(f"   User Cookies: {dict(session.cookies)}")
        if response.status_code == 200:
            user_data = response.json()
            print(f"   User Success: {user_data}")
        else:
            print(f"   User Error: {response.text}")
    except Exception as e:
        print(f"   User Exception: {e}")
    
    # Test 4: Direct Django backend test
    print("\n4. Testing Direct Django Backend...")
    backend_session = requests.Session()
    try:
        # Direct login to Django
        response = backend_session.post(f"{BACKEND_URL}/api/core/login", json=login_data)
        print(f"   Direct Login Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Direct Login Success: {response.json()}")
            
            # Test direct user endpoint
            response = backend_session.get(f"{BACKEND_URL}/api/core/user")
            print(f"   Direct User Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Direct User Success: {response.json()}")
            else:
                print(f"   Direct User Error: {response.text}")
        else:
            print(f"   Direct Login Error: {response.text}")
    except Exception as e:
        print(f"   Direct Backend Exception: {e}")

if __name__ == "__main__":
    test_auth_flow()