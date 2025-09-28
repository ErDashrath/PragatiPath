#!/usr/bin/env python3
"""Debug script to check which user is currently logged in the frontend"""

import requests
import json

def test_current_user():
    """Test the current user endpoint"""
    print("Testing current user endpoint...")
    
    # Test through the Express proxy
    try:
        response = requests.get('http://localhost:5173/api/core/user', timeout=10)
        print(f"Express proxy response status: {response.status_code}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            try:
                user_data = response.json()
                print(f"Current user data: {json.dumps(user_data, indent=2)}")
                return user_data
            except json.JSONDecodeError:
                print(f"Failed to decode JSON response: {response.text}")
        else:
            print(f"Non-JSON response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Express proxy request failed: {e}")
    
    # Test direct Django endpoint
    try:
        print("\nTesting direct Django endpoint...")
        response = requests.get('http://localhost:8000/api/core/user', timeout=10)
        print(f"Direct Django response status: {response.status_code}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            try:
                user_data = response.json()
                print(f"Django user data: {json.dumps(user_data, indent=2)}")
                return user_data
            except json.JSONDecodeError:
                print(f"Failed to decode JSON response: {response.text}")
        else:
            print(f"Non-JSON response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Django direct request failed: {e}")
    
    return None

if __name__ == "__main__":
    print("=" * 60)
    print("CURRENT USER DEBUG")
    print("=" * 60)
    
    user = test_current_user()
    
    if user and 'username' in user:
        print(f"\n✅ Found current user: {user['username']}")
        print(f"   Full name: {user.get('name', 'N/A')}")
        print(f"   User type: {user.get('userType', 'N/A')}")
    else:
        print("\n❌ No current user found - user may not be logged in")