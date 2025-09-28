#!/usr/bin/env python3
"""
Test script to verify admin frontend integration with backend endpoints
"""

import requests
import json
from datetime import datetime

BACKEND_URL = "http://127.0.0.1:8000"

def test_admin_endpoints():
    """Test all admin endpoints that the frontend uses"""
    
    print("🔍 Testing Admin Frontend Integration")
    print("=" * 50)
    
    endpoints_to_test = [
        {
            "url": f"{BACKEND_URL}/api/admin/class-overview",
            "name": "Class Overview",
            "expected_keys": ["totalStudents", "activeThisWeek", "totalSessions", "averageAccuracy"]
        },
        {
            "url": f"{BACKEND_URL}/api/admin/students", 
            "name": "Students List",
            "expected_keys": ["id", "username", "full_name", "total_sessions", "accuracy"]
        },
        {
            "url": f"{BACKEND_URL}/api/admin/system-stats",
            "name": "System Statistics", 
            "expected_keys": ["users", "sessions", "questions", "subjects"]
        },
        {
            "url": f"{BACKEND_URL}/api/frontend/dashboard/admin",
            "name": "Frontend Admin Dashboard",
            "expected_keys": ["system_stats", "student_count", "question_bank_stats"]
        },
        {
            "url": f"{BACKEND_URL}/api/core/students",
            "name": "Core Students (Fallback)",
            "expected_keys": []  # Fallback endpoint structure may vary
        }
    ]
    
    results = []
    
    for endpoint in endpoints_to_test:
        print(f"\n📊 Testing: {endpoint['name']}")
        print(f"URL: {endpoint['url']}")
        
        try:
            response = requests.get(endpoint['url'], timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Status: {response.status_code} OK")
                
                # Check for expected keys if specified
                if endpoint['expected_keys']:
                    missing_keys = []
                    if isinstance(data, list) and len(data) > 0:
                        # For list responses, check first item
                        sample_item = data[0]
                        for key in endpoint['expected_keys']:
                            if key not in sample_item:
                                missing_keys.append(key)
                    elif isinstance(data, dict):
                        # For dict responses, check directly
                        for key in endpoint['expected_keys']:
                            if key not in data:
                                missing_keys.append(key)
                    
                    if missing_keys:
                        print(f"⚠️  Missing keys: {missing_keys}")
                    else:
                        print("✅ All expected keys present")
                
                # Show data summary
                if isinstance(data, list):
                    print(f"📊 Response: List with {len(data)} items")
                    if len(data) > 0:
                        print(f"Sample item keys: {list(data[0].keys())}")
                elif isinstance(data, dict):
                    print(f"📊 Response: Dict with {len(data)} keys")
                    print(f"Keys: {list(data.keys())}")
                    
                    # Show some sample values for key metrics
                    if 'totalStudents' in data:
                        print(f"   • Total Students: {data['totalStudents']}")
                    if 'total_students' in data:
                        print(f"   • Total Students: {data['total_students']}")
                    if 'system_stats' in data and isinstance(data['system_stats'], dict):
                        stats = data['system_stats']
                        print(f"   • System Stats: {len(stats)} metrics")
                        if 'total_students' in stats:
                            print(f"     - Students: {stats['total_students']}")
                        if 'total_questions' in stats:
                            print(f"     - Questions: {stats['total_questions']}")
                
                results.append({
                    "endpoint": endpoint['name'],
                    "status": "SUCCESS",
                    "data_type": type(data).__name__,
                    "data_size": len(data) if isinstance(data, (list, dict)) else 0
                })
                
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                results.append({
                    "endpoint": endpoint['name'],
                    "status": f"ERROR_{response.status_code}",
                    "data_type": "none",
                    "data_size": 0
                })
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            results.append({
                "endpoint": endpoint['name'],
                "status": "CONNECTION_ERROR",
                "data_type": "none", 
                "data_size": 0
            })
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            results.append({
                "endpoint": endpoint['name'],
                "status": "PARSE_ERROR",
                "data_type": "none",
                "data_size": 0
            })
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 50)
    
    success_count = len([r for r in results if r['status'] == 'SUCCESS'])
    total_count = len(results)
    
    for result in results:
        status_icon = "✅" if result['status'] == 'SUCCESS' else "❌"
        print(f"{status_icon} {result['endpoint']:25} {result['status']:15} {result['data_type']:10}")
    
    print(f"\n🎯 Success Rate: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    if success_count >= 3:  # At least 3 endpoints working
        print("\n✅ FRONTEND READY: Admin dashboard should display real data")
        print("💡 Next Steps:")
        print("   1. Start React frontend development server")
        print("   2. Login as admin (admin/admin123)")
        print("   3. Navigate to admin dashboard")
        print("   4. Verify real data is displayed in UI components")
    else:
        print("\n❌ ISSUES DETECTED: Some admin endpoints are not working")
        print("💡 Troubleshooting:")
        print("   1. Ensure Django server is running on port 8000")
        print("   2. Check database has student/session data")
        print("   3. Verify admin_api.py is properly imported in urls.py")
        print("   4. Check for any Django server errors")

if __name__ == "__main__":
    print(f"🚀 Admin Frontend Integration Test")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_admin_endpoints()
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")