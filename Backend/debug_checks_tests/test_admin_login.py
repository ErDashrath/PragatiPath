#!/usr/bin/env python3
"""
Test admin login functionality
"""

import requests
import json

def test_admin_login():
    # Test admin login
    login_url = "http://localhost:8000/api/core/login"
    
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        print("Testing admin login...")
        response = requests.post(
            login_url,
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Admin login successful!")
            print(f"User ID: {data.get('id')}")
            print(f"Username: {data.get('username')}")
            print(f"Name: {data.get('name')}")
            print(f"User Type: {data.get('userType')}")
            print(f"Email: {data.get('email')}")
        else:
            print("❌ Admin login failed!")
            
    except Exception as e:
        print(f"❌ Login Error: {str(e)}")

if __name__ == "__main__":
    test_admin_login()