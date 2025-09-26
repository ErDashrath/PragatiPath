#!/usr/bin/env python3
"""
Comprehensive API Test Suite for PragatiPathLearn Backend
Tests all API endpoints to verify frontend integration
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, List

class PragatiPathLearnAPITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.test_student_id = "9bbcc9f4-bfe8-450f-b2fa-95f567625681"
        self.results = []
        
    def test_endpoint(self, method: str, endpoint: str, data=None, description="", expected_status=200):
        """Test a single API endpoint"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Content-Type': 'application/json',
            'Origin': 'http://localhost:5000',
            'Accept': 'application/json'
        }
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            success = response.status_code == expected_status
            
            test_result = {
                'endpoint': endpoint,
                'method': method,
                'description': description,
                'status_code': response.status_code,
                'expected_status': expected_status,
                'success': success,
                'response_time': response.elapsed.total_seconds(),
                'has_cors': 'Access-Control-Allow-Origin' in response.headers,
                'cors_origin': response.headers.get('Access-Control-Allow-Origin', 'N/A'),
                'timestamp': datetime.now().isoformat()
            }
            
            if success and response.content:
                try:
                    json_data = response.json()
                    test_result['response_keys'] = list(json_data.keys()) if isinstance(json_data, dict) else []
                    test_result['response_type'] = type(json_data).__name__
                    test_result['data_sample'] = str(json_data)[:200] + "..." if len(str(json_data)) > 200 else str(json_data)
                except:
                    test_result['response_keys'] = []
                    test_result['response_type'] = 'non-json'
                    test_result['data_sample'] = response.text[:200]
            else:
                test_result['error_message'] = response.text[:500] if response.text else "No error message"
                
        except requests.RequestException as e:
            test_result = {
                'endpoint': endpoint,
                'method': method,
                'description': description,
                'status_code': 0,
                'expected_status': expected_status,
                'success': False,
                'response_time': 0,
                'has_cors': False,
                'cors_origin': 'N/A',
                'error_message': str(e),
                'timestamp': datetime.now().isoformat()
            }
        
        self.results.append(test_result)
        return test_result
    
    def run_all_tests(self):
        """Run comprehensive tests for all API endpoints"""
        print("🚀 Starting Comprehensive PragatiPathLearn API Test Suite")
        print("=" * 80)
        
        # 1. Health Check
        print("\n1️⃣ HEALTH & SYSTEM ENDPOINTS")
        self.test_endpoint('GET', '/api/health', description='System Health Check')
        
        # 2. Frontend-Specific API Endpoints
        print("\n2️⃣ FRONTEND API ENDPOINTS")
        self.test_endpoint('GET', f'/api/frontend/dashboard/student/{self.test_student_id}', 
                          description='Student Dashboard Data')
        self.test_endpoint('GET', '/api/frontend/dashboard/admin', 
                          description='Admin Dashboard Data')
        self.test_endpoint('GET', '/api/frontend/subjects/available', 
                          description='Available Subjects for Frontend')
        self.test_endpoint('GET', f'/api/frontend/analytics/student/{self.test_student_id}/charts?days=30', 
                          description='Student Analytics Charts')
        self.test_endpoint('GET', '/api/frontend/status/all', 
                          description='Frontend System Status')
        self.test_endpoint('GET', '/api/frontend/config/frontend', 
                          description='Frontend Configuration')
        
        # 3. Core API Endpoints
        print("\n3️⃣ CORE API ENDPOINTS")
        self.test_endpoint('GET', '/api/core/students', description='List All Students')
        self.test_endpoint('GET', f'/api/core/students/{self.test_student_id}', description='Get Specific Student')
        self.test_endpoint('GET', '/api/core/status', description='Core System Status')
        
        # 4. Assessment API Endpoints
        print("\n4️⃣ ASSESSMENT API ENDPOINTS")
        self.test_endpoint('GET', '/api/assessment/questions', description='List Assessment Questions')
        self.test_endpoint('GET', '/api/assessment/assessments', description='List Assessments')
        self.test_endpoint('GET', '/api/assessment/subjects', description='Assessment Subjects')
        self.test_endpoint('GET', '/api/assessment/status', description='Assessment System Status')
        
        # 5. Student Model API Endpoints  
        print("\n5️⃣ STUDENT MODEL API ENDPOINTS")
        self.test_endpoint('GET', f'/api/student-model/student/{self.test_student_id}/bkt/states/all', 
                          description='BKT All States')
        self.test_endpoint('GET', f'/api/student-model/student/{self.test_student_id}/bkt/mastered', 
                          description='BKT Mastered Skills')
        self.test_endpoint('GET', '/api/student-model/dkt/health', description='DKT Health Check')
        self.test_endpoint('GET', '/api/student-model/knowledge-components', description='Knowledge Components')
        self.test_endpoint('GET', '/api/student-model/status', description='Student Model Status')
        
        # 6. Analytics API Endpoints
        print("\n6️⃣ ANALYTICS API ENDPOINTS")
        self.test_endpoint('GET', f'/api/analytics/students/{self.test_student_id}/performance', 
                          description='Student Performance Analytics')
        self.test_endpoint('GET', f'/api/analytics/students/{self.test_student_id}/learning-analytics', 
                          description='Learning Analytics')
        self.test_endpoint('GET', f'/api/analytics/students/{self.test_student_id}/progress-tracking', 
                          description='Progress Tracking')
        self.test_endpoint('GET', f'/api/analytics/students/{self.test_student_id}/recommendations', 
                          description='Recommendations')
        self.test_endpoint('GET', '/api/analytics/system/metrics', description='System Metrics')
        self.test_endpoint('GET', '/api/analytics/status', description='Analytics Status')
        
        # 7. Practice API Endpoints (SM-2 Algorithm)
        print("\n7️⃣ PRACTICE API ENDPOINTS (SM-2)")
        self.test_endpoint('GET', f'/api/practice/api/v1/practice/{self.test_student_id}/due-cards', 
                          description='Due Practice Cards')
        self.test_endpoint('GET', f'/api/practice/api/v1/practice/{self.test_student_id}/stats', 
                          description='Practice Statistics')
        self.test_endpoint('GET', f'/api/practice/api/v1/practice/{self.test_student_id}/optimal-study-set', 
                          description='Optimal Study Set')
        self.test_endpoint('GET', '/api/practice/status', description='Practice System Status')
        
        # 8. Competitive Exam API (V1)
        print("\n8️⃣ COMPETITIVE EXAM API V1")
        self.test_endpoint('GET', '/api/competitive/v1/subjects', description='Competitive Subjects')
        self.test_endpoint('GET', f'/api/competitive/v1/student/{self.test_student_id}/progress', 
                          description='Competitive Progress')
        
        # 9. Enhanced API (V2) - AI Integration
        print("\n9️⃣ ENHANCED API V2 (AI INTEGRATION)")
        # Note: These endpoints might require specific data or sessions
        
        print("\n" + "=" * 80)
        print("✅ API Test Suite Completed!")
        
        return self.results
    
    def print_summary(self):
        """Print a detailed summary of all test results"""
        successful_tests = [r for r in self.results if r['success']]
        failed_tests = [r for r in self.results if not r['success']]
        
        print(f"\n📊 TEST RESULTS SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {len(self.results)}")
        print(f"✅ Successful: {len(successful_tests)} ({len(successful_tests)/len(self.results)*100:.1f}%)")
        print(f"❌ Failed: {len(failed_tests)} ({len(failed_tests)/len(self.results)*100:.1f}%)")
        
        # CORS Analysis
        cors_enabled = [r for r in self.results if r.get('has_cors', False)]
        print(f"🌐 CORS Enabled: {len(cors_enabled)} endpoints")
        
        # Performance Analysis
        avg_response_time = sum(r.get('response_time', 0) for r in successful_tests) / len(successful_tests) if successful_tests else 0
        print(f"⚡ Average Response Time: {avg_response_time:.3f}s")
        
        print(f"\n🎯 SUCCESSFUL ENDPOINTS:")
        for test in successful_tests:
            cors_status = "🌐" if test.get('has_cors') else "🚫"
            print(f"  {cors_status} {test['method']} {test['endpoint']} - {test['description']} ({test['response_time']:.3f}s)")
        
        if failed_tests:
            print(f"\n❌ FAILED ENDPOINTS:")
            for test in failed_tests:
                print(f"  ❌ {test['method']} {test['endpoint']} - {test['description']}")
                print(f"     Status: {test['status_code']}, Error: {test.get('error_message', 'Unknown')[:100]}")
        
        print("\n" + "=" * 80)
        
        # Frontend Integration Status
        frontend_endpoints = [r for r in self.results if '/api/frontend/' in r['endpoint']]
        frontend_success = [r for r in frontend_endpoints if r['success']]
        
        print(f"🎨 FRONTEND INTEGRATION STATUS:")
        print(f"Frontend-specific endpoints: {len(frontend_endpoints)}")
        print(f"Frontend endpoints working: {len(frontend_success)}/{len(frontend_endpoints)}")
        
        if len(frontend_success) == len(frontend_endpoints):
            print("🎉 ALL FRONTEND ENDPOINTS WORKING! React integration ready!")
        else:
            print("⚠️  Some frontend endpoints need attention")
            
        return {
            'total_tests': len(self.results),
            'successful_tests': len(successful_tests),
            'failed_tests': len(failed_tests),
            'success_rate': len(successful_tests)/len(self.results)*100,
            'frontend_ready': len(frontend_success) == len(frontend_endpoints),
            'cors_enabled': len(cors_enabled),
            'average_response_time': avg_response_time
        }
    
    def save_results(self, filename="api_test_results.json"):
        """Save test results to JSON file"""
        with open(filename, 'w') as f:
            json.dump({
                'test_metadata': {
                    'total_tests': len(self.results),
                    'timestamp': datetime.now().isoformat(),
                    'base_url': self.base_url,
                    'test_student_id': self.test_student_id
                },
                'test_results': self.results
            }, f, indent=2)
        print(f"💾 Results saved to {filename}")

def main():
    """Main function to run the comprehensive API test"""
    print("🔥 PragatiPathLearn API Comprehensive Test Suite")
    print("Testing all backend endpoints for frontend integration")
    print("-" * 80)
    
    # Initialize the tester
    tester = PragatiPathLearnAPITester()
    
    # Run all tests
    results = tester.run_all_tests()
    
    # Print summary
    summary = tester.print_summary()
    
    # Save results
    tester.save_results()
    
    print(f"\n🏁 Testing Complete!")
    print(f"📈 Success Rate: {summary['success_rate']:.1f}%")
    print(f"🌐 CORS Endpoints: {summary['cors_enabled']}")
    print(f"⚡ Avg Response: {summary['average_response_time']:.3f}s")
    
    if summary['frontend_ready']:
        print("🎉 FRONTEND INTEGRATION: READY!")
    else:
        print("⚠️  FRONTEND INTEGRATION: Needs attention")

if __name__ == "__main__":
    main()