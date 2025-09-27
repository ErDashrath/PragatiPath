#!/usr/bin/env python3
"""Test history saving and retrieval issues"""

import requests
import json

print("Testing history API and session saving issues...")
print("="*60)

# Test 1: Check if the history API endpoints exist and work
print("1. Testing backend history API endpoints...")

try:
    # Try different possible usernames that might exist
    test_usernames = ['admin', 'student', 'student_1', 'test_user']
    
    for username in test_usernames:
        print(f"\n   Testing username: {username}")
        
        # Test the enhanced history endpoint (the one used in frontend)
        enhanced_url = f"http://localhost:8000/history/student/{username}/"
        print(f"   📍 Enhanced API URL: {enhanced_url}")
        
        try:
            response = requests.get(enhanced_url, timeout=5)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Enhanced API works for {username}")
                print(f"   Sessions found: {data.get('summary', {}).get('total_sessions', 0)}")
                break
            elif response.status_code == 404:
                print(f"   ❌ User {username} not found")
            else:
                print(f"   ⚠️ Unexpected status: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Connection error: {e}")
    
    # Test the legacy history API
    print(f"\n   Testing legacy history API...")
    legacy_url = f"http://localhost:8000/api/history/students/admin/history"
    print(f"   📍 Legacy API URL: {legacy_url}")
    
    try:
        response = requests.get(legacy_url, timeout=5)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Legacy API works")
            print(f"   Sessions found: {len(data) if isinstance(data, list) else 0}")
        else:
            print(f"   Response: {response.text[:200]}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
        
except Exception as e:
    print(f"❌ Error testing APIs: {e}")

print("\n" + "="*60)
print("2. Analyzing potential history issues...")
print("")

issues_and_solutions = [
    {
        "issue": "Sessions not being saved to database",
        "causes": [
            "Adaptive learning API not saving sessions properly",
            "Session completion not triggering save",
            "Database connection issues",
            "Session model not being created"
        ],
        "solutions": [
            "Add explicit session saving after completion",
            "Check database for session records",
            "Add session save API endpoint",
            "Verify database models and migrations"
        ]
    },
    {
        "issue": "Username mismatch in API calls",
        "causes": [
            "Frontend using wrong username format",
            "User authentication returning different username",
            "API expecting different username format"
        ],
        "solutions": [
            "Check user.username in frontend",
            "Add username debugging in history component",
            "Verify API endpoint username format",
            "Add fallback username attempts"
        ]
    },
    {
        "issue": "API endpoints not working",
        "causes": [
            "Backend not running",
            "URL routing issues",
            "CORS problems",
            "API endpoint bugs"
        ],
        "solutions": [
            "Verify backend server status",
            "Check URL configuration",
            "Add API debugging",
            "Test endpoints manually"
        ]
    }
]

for i, item in enumerate(issues_and_solutions, 1):
    print(f"{i}. {item['issue']}")
    print("   Possible causes:")
    for cause in item['causes']:
        print(f"   • {cause}")
    print("   Solutions:")
    for solution in item['solutions']:
        print(f"   ✓ {solution}")
    print()

print("="*60)
print("3. Next steps to fix history issues:")
print("")
print("✅ 1. Check current user authentication and username")
print("✅ 2. Add session saving mechanism to adaptive learning")
print("✅ 3. Test API endpoints with correct usernames")
print("✅ 4. Add debugging to history component")
print("✅ 5. Verify database has session records")
print("")
print("🎯 Most likely fix: Add proper session saving when adaptive learning completes!")