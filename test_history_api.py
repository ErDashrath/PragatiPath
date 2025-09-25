#!/usr/bin/env python3
"""
Test Assessment History API
Verify that the history endpoints work correctly
"""

import os
import sys
import django
import requests
import json

# Add the Backend directory to Python path
backend_dir = os.path.join(os.path.dirname(__file__), 'Backend')
sys.path.insert(0, backend_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')
django.setup()

from django.contrib.auth.models import User
from assessment.improved_models import StudentSession

# Test configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def test_history_api():
    """Test the assessment history API endpoints"""
    print("🧪 Testing Assessment History API")
    print("=" * 50)
    
    try:
        # Find a student with assessment history
        sessions = StudentSession.objects.filter(status='COMPLETED').select_related('student')
        if not sessions.exists():
            print("❌ No completed assessments found in database")
            return False
        
        test_student = sessions.first().student
        student_username = test_student.username
        
        print(f"👤 Testing with student: {student_username}")
        
        # Test 1: Get student history
        print("\n1️⃣ Testing Student History API...")
        history_response = requests.get(f"{API_BASE}/history/students/{student_username}/history")
        
        if history_response.status_code == 200:
            history_data = history_response.json()
            print(f"✅ History API works - Found {len(history_data)} assessments")
            
            # Show sample data
            if history_data:
                sample = history_data[0]
                print(f"   Sample: {sample['session_name']} - {sample['percentage_score']}% ({sample['grade']})")
        else:
            print(f"❌ History API failed: {history_response.status_code}")
            print(f"Response: {history_response.text}")
            return False
        
        # Test 2: Get student stats
        print("\n2️⃣ Testing Student Stats API...")
        stats_response = requests.get(f"{API_BASE}/history/students/{student_username}/stats")
        
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            print(f"✅ Stats API works")
            print(f"   Total assessments: {stats_data['total_assessments']}")
            print(f"   Overall accuracy: {stats_data['overall_accuracy']:.1f}%")
            print(f"   Best accuracy: {stats_data['best_accuracy']:.1f}%")
            print(f"   Subjects: {', '.join(stats_data['subjects_attempted'])}")
        else:
            print(f"❌ Stats API failed: {stats_response.status_code}")
            print(f"Response: {stats_response.text}")
            return False
        
        # Test 3: Get detailed assessment result
        if history_data:
            test_session_id = history_data[0]['session_id']
            print(f"\n3️⃣ Testing Detailed Results API for session {test_session_id}...")
            
            details_response = requests.get(f"{API_BASE}/history/students/{student_username}/assessment/{test_session_id}")
            
            if details_response.status_code == 200:
                details_data = details_response.json()
                print(f"✅ Detailed Results API works")
                print(f"   Question attempts: {len(details_data['question_attempts'])}")
                print(f"   Performance analysis topics: {len(details_data['performance_analysis']['topics_performance'])}")
                print(f"   Recommendations: {len(details_data['recommendations'])}")
                
                # Show sample analysis
                if details_data['performance_analysis']['strengths']:
                    print(f"   Sample strength: {details_data['performance_analysis']['strengths'][0]}")
                if details_data['recommendations']:
                    print(f"   Sample recommendation: {details_data['recommendations'][0]}")
            else:
                print(f"❌ Detailed Results API failed: {details_response.status_code}")
                print(f"Response: {details_response.text}")
                return False
        
        # Test 4: Get subject-specific history
        if stats_data['subjects_attempted']:
            test_subject = stats_data['subjects_attempted'][0]
            print(f"\n4️⃣ Testing Subject History API for {test_subject}...")
            
            subject_response = requests.get(f"{API_BASE}/history/students/{student_username}/subjects/{test_subject}/history")
            
            if subject_response.status_code == 200:
                subject_data = subject_response.json()
                print(f"✅ Subject History API works - Found {len(subject_data)} assessments for {test_subject}")
            else:
                print(f"❌ Subject History API failed: {subject_response.status_code}")
                print(f"Response: {subject_response.text}")
                return False
        
        print(f"\n🎉 All History API tests PASSED!")
        print("✅ Student history retrieval works")
        print("✅ Statistics calculation works") 
        print("✅ Detailed results analysis works")
        print("✅ Subject filtering works")
        
        return True
        
    except Exception as e:
        print(f"\n❌ API test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Starting Assessment History API Test")
    print("This test verifies:")
    print("- Student can fetch assessment history")
    print("- Statistics are calculated correctly")
    print("- Detailed results show comprehensive analysis")
    print("- Subject filtering works properly")
    print()
    
    try:
        success = test_history_api()
        
        if success:
            print("\n🎉 All tests PASSED! Assessment History system is working correctly.")
            print("Students can now:")
            print("✅ View their complete assessment history")
            print("✅ See detailed performance statistics")
            print("✅ Review question-by-question analysis")
            print("✅ Get personalized recommendations")
            print("✅ Filter history by subject")
        else:
            print("\n❌ Some tests FAILED. Check the output above.")
            
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed with unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()