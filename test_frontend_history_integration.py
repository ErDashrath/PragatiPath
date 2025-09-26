#!/usr/bin/env python3
"""Test frontend-backend integration for history API"""
import requests
import json

print("=== TESTING FRONTEND-BACKEND HISTORY INTEGRATION ===")

# Test the enhanced history API that the frontend should be calling
test_usernames = ['testuser', 'student_testuser', 'dashrath', 'student_dashrath']

for username in test_usernames:
    print(f"\n--- Testing username: {username} ---")
    try:
        response = requests.get(f'http://127.0.0.1:8000/history/student/{username}/')
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS - Found data for '{username}'")
            print(f"Total sessions: {data.get('summary', {}).get('total_sessions', 0)}")
            print(f"Assessment sessions: {data.get('summary', {}).get('assessment_sessions_count', 0)}")
            print(f"Adaptive sessions: {data.get('summary', {}).get('adaptive_sessions_count', 0)}")
            
            if data.get('adaptive_sessions'):
                print(f"First adaptive session: {data['adaptive_sessions'][0].get('session_name', 'N/A')}")
            
        elif response.status_code == 404:
            print(f"❌ User '{username}' not found")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection failed - Backend server not running")
        break
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n=== TESTING USER AUTHENTICATION ===")
# Check current users in the system
try:
    # Test login endpoint to see what users exist
    test_credentials = [
        {'username': 'testuser', 'password': 'password'},
        {'username': 'dashrath', 'password': 'password'},
        {'username': 'student', 'password': 'password'}
    ]
    
    for creds in test_credentials:
        print(f"\nTesting login for: {creds['username']}")
        response = requests.post('http://127.0.0.1:8000/api/core/login', 
                               json=creds,
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Login successful!")
            print(f"User ID: {user_data.get('id')}")
            print(f"Username: {user_data.get('username')}")
            print(f"Name: {user_data.get('name')}")
            print(f"User Type: {user_data.get('userType')}")
            
            # Now test history with this authenticated username
            print(f"\n🔄 Testing history API with authenticated user...")
            history_response = requests.get(f'http://127.0.0.1:8000/history/student/{user_data.get("username")}/')
            if history_response.status_code == 200:
                history_data = history_response.json()
                print(f"✅ History found: {history_data.get('summary', {}).get('total_sessions', 0)} sessions")
            else:
                print(f"❌ History not found for authenticated user")
            break
        else:
            print(f"❌ Login failed: {response.status_code}")
            
except Exception as e:
    print(f"❌ Error testing authentication: {e}")

print(f"\n=== FRONTEND INTEGRATION CHECK ===")
print("To debug frontend issues:")
print("1. Check browser Developer Tools -> Network tab")
print("2. Look for failed API calls to /history/student/{username}/")
print("3. Check if username matches what frontend is sending")
print("4. Verify authentication cookies are being sent")
print("5. Check console for JavaScript errors")