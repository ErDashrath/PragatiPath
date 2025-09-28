#!/usr/bin/env python3

import requests
import json

# Test registration endpoint
def test_registration():
    url = "http://localhost:8000/api/core/register"
    
    test_user = {
        "username": "testuser123",
        "password": "testpassword123",
        "email": "testuser123@example.com",
        "full_name": "Test User"
    }
    
    try:
        response = requests.post(
            url,
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Registration successful!")
            data = response.json()
            print(f"User ID: {data.get('id')}")
            print(f"Username: {data.get('username')}")
            print(f"Email: {data.get('email')}")
        else:
            print("❌ Registration failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure Django server is running on port 8000.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

# Test login endpoint
def test_login():
    url = "http://localhost:8000/api/core/login"
    
    login_data = {
        "username": "testuser123",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(
            url,
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nLogin Status Code: {response.status_code}")
        print(f"Login Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
        else:
            print("❌ Login failed!")
            
    except Exception as e:
        print(f"❌ Login Error: {str(e)}")

if __name__ == "__main__":
    print("Testing Registration API...")
    test_registration()
    test_login()