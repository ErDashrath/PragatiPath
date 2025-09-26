#!/usr/bin/env python3

import requests
import json

def test_complete_registration_flow():
    """Test the complete registration and login flow"""
    
    # Test data
    test_user = {
        "username": f"testuser_{hash('test') % 1000}",
        "password": "securepassword123",
        "email": f"testuser_{hash('test') % 1000}@example.com",
        "full_name": "John Doe Test"
    }
    
    print("🧪 Testing Registration & Login Flow")
    print("=" * 50)
    
    # Test 1: Registration
    print("\n1️⃣  Testing Registration...")
    try:
        response = requests.post(
            "http://localhost:8000/api/core/register",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Registration successful!")
            print(f"   User ID: {data.get('id')}")
            print(f"   Username: {data.get('username')}")
            print(f"   Email: {data.get('email')}")
            print(f"   User Type: {data.get('userType')}")
            
            # Test 2: Login with same credentials
            print("\n2️⃣  Testing Login...")
            login_response = requests.post(
                "http://localhost:8000/api/core/login",
                json={
                    "username": test_user["username"],
                    "password": test_user["password"]
                },
                headers={"Content-Type": "application/json"}
            )
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                print(f"✅ Login successful!")
                print(f"   Same User ID: {login_data.get('id') == data.get('id')}")
                print(f"   Username: {login_data.get('username')}")
            else:
                print(f"❌ Login failed: {login_response.status_code}")
                print(f"   Response: {login_response.text}")
                
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure Django server is running on port 8000.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 3: Duplicate registration
    print("\n3️⃣  Testing Duplicate Registration...")
    try:
        dup_response = requests.post(
            "http://localhost:8000/api/core/register",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        if dup_response.status_code == 400:
            print("✅ Duplicate registration properly rejected!")
            print(f"   Error: {dup_response.json().get('detail')}")
        else:
            print(f"⚠️  Unexpected response for duplicate: {dup_response.status_code}")
            print(f"   Response: {dup_response.text}")
            try:
                error_data = dup_response.json()
                print(f"   Error detail: {error_data.get('detail')}")
            except:
                pass
            
    except Exception as e:
        print(f"❌ Error testing duplicate: {str(e)}")
    
    print("\n" + "=" * 50)
    print("✅ Registration flow validation complete!")

if __name__ == "__main__":
    test_complete_registration_flow()