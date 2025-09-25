#!/usr/bin/env python3
"""
Test script for Multi-Student API endpoints
Tests the improved database schema and API functionality
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def test_api_endpoint(method, endpoint, data=None, description=""):
    """Test an API endpoint and return response"""
    try:
        url = f"{BASE_URL}{endpoint}"
        
        if method.upper() == "GET":
            response = requests.get(url)
        elif method.upper() == "POST":
            response = requests.post(url, json=data)
        
        print(f"\n🔍 {description}")
        print(f"📍 {method.upper()} {endpoint}")
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                print(f"✅ Success: {json.dumps(response_data, indent=2)[:200]}...")
                return response_data
            except:
                print(f"✅ Success: {response.text[:200]}...")
                return response.text
        else:
            print(f"❌ Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Connection Error: {str(e)}")
        return None

def main():
    print("🎯 MULTI-STUDENT API TESTING SUITE")
    print("=" * 60)
    
    # Test health check
    health = test_api_endpoint("GET", "/api/multi-student/health/", 
                              description="Health Check Endpoint")
    
    if not health:
        print("❌ Server is not responding. Please check if Django server is running.")
        return
    
    # Test subjects endpoint
    subjects = test_api_endpoint("GET", "/api/multi-student/subjects/", 
                               description="Get All Subjects")
    
    # Test chapters endpoint (assuming subject ID 1 exists)
    if subjects and len(subjects) > 0:
        subject_id = subjects[0].get('id', 1)
        chapters = test_api_endpoint("GET", f"/api/multi-student/subjects/{subject_id}/chapters/", 
                                   description=f"Get Chapters for Subject {subject_id}")
    
    # Test API documentation
    docs = test_api_endpoint("GET", "/api/docs", 
                           description="API Documentation")
    
    print("\n🏁 API TESTING COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()