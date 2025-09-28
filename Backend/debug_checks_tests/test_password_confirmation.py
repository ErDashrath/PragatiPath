#!/usr/bin/env python3

import requests
import json

def test_password_confirmation():
    """Test password confirmation validation in registration"""
    
    print("🔒 Testing Password Confirmation Validation")
    print("=" * 60)
    
    base_user = {
        "username": f"confirm_test_{hash('confirm_test') % 1000}",
        "email": f"confirm_test_{hash('confirm_test') % 1000}@example.com",
        "full_name": "Password Confirm Test User"
    }
    
    # Test 1: Passwords don't match
    print("1️⃣  Testing MISMATCHED passwords...")
    try:
        mismatch_user = {
            **base_user,
            "password": "password123",
            "confirm_password": "different456"
        }
        
        response = requests.post(
            "http://localhost:8000/api/core/register",
            json=mismatch_user,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            data = response.json()
            if "do not match" in data.get('detail', '').lower():
                print("✅ Mismatched passwords: PROPERLY REJECTED")
                print(f"   Error: {data.get('detail')}")
            else:
                print(f"⚠️  Wrong error message: {data.get('detail')}")
        else:
            print(f"❌ Unexpected status for mismatched passwords: {response.status_code}")
            print(f"   Response: {response.text}")
    
    except Exception as e:
        print(f"❌ Error testing mismatched passwords: {e}")
    
    # Test 2: Password too short
    print("\n2️⃣  Testing SHORT password...")
    try:
        short_pass_user = {
            **base_user,
            "username": base_user["username"] + "_short",
            "email": base_user["email"].replace("@", "_short@"),
            "password": "123",
            "confirm_password": "123"
        }
        
        response = requests.post(
            "http://localhost:8000/api/core/register",
            json=short_pass_user,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            data = response.json()
            if "8 characters" in data.get('detail', ''):
                print("✅ Short password: PROPERLY REJECTED")
                print(f"   Error: {data.get('detail')}")
            else:
                print(f"⚠️  Wrong error message: {data.get('detail')}")
        else:
            print(f"❌ Unexpected status for short password: {response.status_code}")
            print(f"   Response: {response.text}")
    
    except Exception as e:
        print(f"❌ Error testing short password: {e}")
    
    # Test 3: Valid matching passwords
    print("\n3️⃣  Testing VALID matching passwords...")
    try:
        valid_user = {
            **base_user,
            "username": base_user["username"] + "_valid",
            "email": base_user["email"].replace("@", "_valid@"),
            "password": "validpassword123",
            "confirm_password": "validpassword123"
        }
        
        response = requests.post(
            "http://localhost:8000/api/core/register",
            json=valid_user,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Valid matching passwords: REGISTRATION SUCCESS")
            print(f"   Username: {data.get('username')}")
            print(f"   User ID: {data.get('id')}")
            
            # Test login with the registered user
            print("\n4️⃣  Testing LOGIN with registered user...")
            login_response = requests.post(
                "http://localhost:8000/api/core/login",
                json={
                    "username": valid_user["username"],
                    "password": valid_user["password"]
                },
                headers={"Content-Type": "application/json"}
            )
            
            if login_response.status_code == 200:
                print("✅ Login after registration: SUCCESS")
                login_data = login_response.json()
                print(f"   Same user ID: {login_data.get('id') == data.get('id')}")
            else:
                print(f"❌ Login after registration: FAILED ({login_response.status_code})")
                print(f"   Response: {login_response.text}")
                
        else:
            print(f"❌ Valid password registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
    
    except Exception as e:
        print(f"❌ Error testing valid passwords: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Password confirmation validation tests complete!")

if __name__ == "__main__":
    test_password_confirmation()