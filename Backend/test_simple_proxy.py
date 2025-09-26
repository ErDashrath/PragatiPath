#!/usr/bin/env python3

import requests
import json

def test_simple_api_proxy():
    """Test the /simple/ API proxy for adaptive learning"""
    
    print("🔗 TESTING SIMPLE API PROXY")
    print("=" * 60)
    
    # Test health endpoint
    print("1️⃣  Testing Simple API Health Check")
    try:
        # Direct backend
        direct_health = requests.get("http://localhost:8000/simple/health/")
        print(f"Direct Backend Health: {direct_health.status_code}")
        if direct_health.status_code == 200:
            health_data = direct_health.json()
            print(f"   Status: {health_data.get('status')}")
            print(f"   Ready: {health_data.get('ready_for_frontend')}")
        
        # Through proxy
        proxy_health = requests.get("http://localhost:5000/simple/health/")
        print(f"Through Proxy Health: {proxy_health.status_code}")
        if proxy_health.status_code == 200:
            proxy_health_data = proxy_health.json()
            print(f"   Status: {proxy_health_data.get('status')}")
            print(f"   Ready: {proxy_health_data.get('ready_for_frontend')}")
        else:
            print(f"   Error: {proxy_health.text[:200]}")
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test start session
    print(f"\n2️⃣  Testing Start Session")
    session_data = {
        "student_name": "proxy_test_student",
        "subject": "verbal_ability"
    }
    
    try:
        # Direct backend
        direct_session = requests.post(
            "http://localhost:8000/simple/start-session/",
            json=session_data
        )
        print(f"Direct Backend Session: {direct_session.status_code}")
        if direct_session.status_code == 200:
            session_result = direct_session.json()
            print(f"   Session ID: {session_result.get('session_id')}")
            print(f"   Subject: {session_result.get('subject')}")
        
        # Through proxy  
        proxy_session = requests.post(
            "http://localhost:5000/simple/start-session/",
            json=session_data
        )
        print(f"Through Proxy Session: {proxy_session.status_code}")
        if proxy_session.status_code == 200:
            proxy_session_result = proxy_session.json()
            print(f"   Session ID: {proxy_session_result.get('session_id')}")
            print(f"   Subject: {proxy_session_result.get('subject')}")
        else:
            print(f"   Error: {proxy_session.text[:200]}")
            
    except Exception as e:
        print(f"❌ Session start error: {e}")
    
    print(f"\n" + "=" * 60)
    print("📋 SIMPLE API PROXY TEST COMPLETE")

if __name__ == "__main__":
    test_simple_api_proxy()