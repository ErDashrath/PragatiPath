#!/usr/bin/env python3

import requests
import json

def test_password_validation():
    """Test password validation in login"""
    
    # First create a test user
    test_user = {
        "username": "password_test_user",
        "password": "correct_password_123",
        "email": "password_test@example.com",
        "full_name": "Password Test User"
    }
    
    print("🔐 Testing Password Validation")
    print("=" * 50)
    
    # Register the user first
    print("1️⃣  Registering test user...")
    try:
        reg_response = requests.post(
            "http://localhost:8000/api/core/register",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        if reg_response.status_code == 200:
            print("✅ User registered successfully")
        else:
            print("⚠️  User might already exist, continuing with login tests...")
    
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return
    
    # Test 2: Login with correct password
    print("\n2️⃣  Testing login with CORRECT password...")
    try:
        correct_login = requests.post(
            "http://localhost:8000/api/core/login",
            json={
                "username": test_user["username"],
                "password": test_user["password"]  # Correct password
            },
            headers={"Content-Type": "application/json"}
        )
        
        if correct_login.status_code == 200:
            print("✅ Login with correct password: SUCCESS")
            data = correct_login.json()
            print(f"   Username: {data.get('username')}")
            print(f"   User Type: {data.get('userType')}")
        else:
            print(f"❌ Login with correct password: FAILED ({correct_login.status_code})")
            print(f"   Response: {correct_login.text}")
    
    except Exception as e:
        print(f"❌ Error testing correct password: {e}")
    
    # Test 3: Login with WRONG password
    print("\n3️⃣  Testing login with WRONG password...")
    try:
        wrong_login = requests.post(
            "http://localhost:8000/api/core/login",
            json={
                "username": test_user["username"],
                "password": "wrong_password_123"  # Wrong password
            },
            headers={"Content-Type": "application/json"}
        )
        
        if wrong_login.status_code == 401:
            print("✅ Login with wrong password: PROPERLY REJECTED")
            try:
                error_data = wrong_login.json()
                print(f"   Error message: {error_data.get('detail')}")
            except:
                print(f"   Raw response: {wrong_login.text}")
        else:
            print(f"⚠️  Unexpected response for wrong password: {wrong_login.status_code}")
            print(f"   Response: {wrong_login.text}")
    
    except Exception as e:
        print(f"❌ Error testing wrong password: {e}")
    
    # Test 4: Login with non-existent user
    print("\n4️⃣  Testing login with NON-EXISTENT user...")
    try:
        nonexistent_login = requests.post(
            "http://localhost:8000/api/core/login",
            json={
                "username": "nonexistent_user_12345",
                "password": "any_password"
            },
            headers={"Content-Type": "application/json"}
        )
        
        if nonexistent_login.status_code == 401:
            print("✅ Login with non-existent user: PROPERLY REJECTED")
            try:
                error_data = nonexistent_login.json()
                print(f"   Error message: {error_data.get('detail')}")
            except:
                print(f"   Raw response: {nonexistent_login.text}")
        else:
            print(f"⚠️  Unexpected response for non-existent user: {nonexistent_login.status_code}")
            print(f"   Response: {nonexistent_login.text}")
    
    except Exception as e:
        print(f"❌ Error testing non-existent user: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Password validation tests complete!")

if __name__ == "__main__":
    test_password_validation()