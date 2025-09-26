#!/usr/bin/env python3
"""
Frontend-Backend Endpoint Verification Script
Tests if frontend endpoints correctly map to backend endpoints.
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, List

# Configuration
BACKEND_BASE = "http://127.0.0.1:8000"
FRONTEND_BASE = "http://127.0.0.1:5000"

class EndpointVerifier:
    def __init__(self):
        self.results = []
        self.session = requests.Session()
        
    def log_result(self, endpoint: str, status: str, details: str, response_data: Any = None):
        """Log verification result"""
        result = {
            "endpoint": endpoint,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.results.append(result)
        print(f"[{status.upper()}] {endpoint}: {details}")
    
    def test_endpoint_availability(self, endpoint: str, base_url: str, expected_status: int = 200) -> Dict[str, Any]:
        """Test if an endpoint is available and returns expected status"""
        try:
            response = self.session.get(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == expected_status:
                return {
                    "available": True,
                    "status_code": response.status_code,
                    "response_data": response.json() if response.content else None,
                    "error": None
                }
            else:
                return {
                    "available": False,
                    "status_code": response.status_code,
                    "response_data": None,
                    "error": f"Expected {expected_status}, got {response.status_code}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "available": False,
                "status_code": None,
                "response_data": None,
                "error": str(e)
            }
    
    def verify_frontend_proxy(self):
        """Verify frontend proxy is correctly forwarding requests"""
        print("\n=== Frontend Proxy Verification ===")
        
        # Test direct backend endpoint
        backend_result = self.test_endpoint_availability("/simple/subjects/", BACKEND_BASE)
        
        # Test frontend proxy endpoint
        frontend_result = self.test_endpoint_availability("/simple/subjects/", FRONTEND_BASE)
        
        if backend_result["available"] and frontend_result["available"]:
            # Compare responses
            backend_data = backend_result["response_data"]
            frontend_data = frontend_result["response_data"]
            
            if backend_data == frontend_data:
                self.log_result(
                    "/simple/subjects/",
                    "PASS",
                    "Frontend proxy correctly forwards to backend",
                    {"backend_subjects": len(backend_data.get("subjects", [])) if backend_data else 0}
                )
            else:
                self.log_result(
                    "/simple/subjects/",
                    "FAIL",
                    "Frontend proxy returns different data than backend",
                    {"backend_response": backend_data, "frontend_response": frontend_data}
                )
        else:
            if not backend_result["available"]:
                self.log_result("/simple/subjects/", "FAIL", f"Backend unavailable: {backend_result['error']}")
            if not frontend_result["available"]:
                self.log_result("/simple/subjects/", "FAIL", f"Frontend proxy unavailable: {frontend_result['error']}")
    
    def verify_assessment_history_endpoints(self):
        """Verify assessment history endpoints"""
        print("\n=== Assessment History Endpoints ===")
        
        # Test student username (using 'admin' as test user)
        test_username = "admin"
        
        endpoints_to_test = [
            f"/history/student/{test_username}/",
            f"/history/adaptive-analytics/{test_username}/",
            f"/api/assessment-history/{test_username}/",
            f"/api/student-stats/{test_username}/",
        ]
        
        for endpoint in endpoints_to_test:
            # Test backend directly
            backend_result = self.test_endpoint_availability(endpoint, BACKEND_BASE, expected_status=200)
            
            # Test through frontend proxy  
            frontend_result = self.test_endpoint_availability(endpoint, FRONTEND_BASE, expected_status=200)
            
            if backend_result["available"]:
                if frontend_result["available"]:
                    self.log_result(
                        endpoint,
                        "PASS",
                        "Both backend and frontend accessible",
                        {"backend_status": backend_result["status_code"], "frontend_status": frontend_result["status_code"]}
                    )
                else:
                    self.log_result(
                        endpoint,
                        "WARN",
                        f"Backend accessible but frontend proxy failed: {frontend_result['error']}",
                        {"backend_data_size": len(str(backend_result["response_data"])) if backend_result["response_data"] else 0}
                    )
            else:
                self.log_result(
                    endpoint,
                    "FAIL",
                    f"Backend not accessible: {backend_result['error']}"
                )
    
    def verify_adaptive_learning_endpoints(self):
        """Verify adaptive learning API endpoints"""
        print("\n=== Adaptive Learning Endpoints ===")
        
        endpoints_to_test = [
            "/simple/subjects/",
            "/simple/question/",
            "/simple/session-progress/",
            "/simple/chapters/",
        ]
        
        for endpoint in endpoints_to_test:
            # Test backend
            backend_result = self.test_endpoint_availability(endpoint, BACKEND_BASE)
            
            # Test frontend proxy
            frontend_result = self.test_endpoint_availability(endpoint, FRONTEND_BASE)
            
            if backend_result["available"] and frontend_result["available"]:
                self.log_result(
                    endpoint,
                    "PASS", 
                    "Endpoint accessible via both backend and frontend",
                    {"response_keys": list(backend_result["response_data"].keys()) if backend_result["response_data"] else []}
                )
            elif backend_result["available"]:
                self.log_result(
                    endpoint,
                    "WARN",
                    f"Backend works but frontend proxy fails: {frontend_result['error']}"
                )
            else:
                self.log_result(
                    endpoint,
                    "FAIL",
                    f"Backend endpoint failed: {backend_result['error']}"
                )
    
    def verify_database_consistency(self):
        """Check database consistency for sessions and questions"""
        print("\n=== Database Consistency Check ===")
        
        try:
            # Get session progress to check if orchestration is working
            response = self.session.get(f"{BACKEND_BASE}/simple/session-progress/")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for minimum requirements
                questions_answered = data.get("questions_answered", 0)
                session_active = data.get("session_active", False)
                
                if questions_answered >= 15:
                    self.log_result(
                        "minimum_questions",
                        "PASS",
                        f"Session has {questions_answered} questions (≥15 requirement met)",
                        {"questions_answered": questions_answered, "session_active": session_active}
                    )
                elif questions_answered > 0:
                    self.log_result(
                        "minimum_questions",
                        "WARN", 
                        f"Session has only {questions_answered} questions (< 15 minimum)",
                        {"questions_answered": questions_answered, "session_active": session_active}
                    )
                else:
                    self.log_result(
                        "minimum_questions",
                        "INFO",
                        "No active session to check question count",
                        {"session_active": session_active}
                    )
                    
                # Check if BKT/DKT orchestration data is present
                if "bkt_mastery" in data or "dkt_mastery" in data:
                    self.log_result(
                        "orchestration_data",
                        "PASS",
                        "BKT/DKT orchestration data found in session progress",
                        {"has_bkt": "bkt_mastery" in data, "has_dkt": "dkt_mastery" in data}
                    )
                else:
                    self.log_result(
                        "orchestration_data",
                        "WARN",
                        "No BKT/DKT orchestration data found in session progress"
                    )
            else:
                self.log_result(
                    "session_progress",
                    "FAIL",
                    f"Cannot get session progress: HTTP {response.status_code}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "database_consistency",
                "FAIL",
                f"Database consistency check failed: {str(e)}"
            )
    
    def verify_json_response_format(self):
        """Verify all endpoints return valid JSON"""
        print("\n=== JSON Response Format Verification ===")
        
        test_endpoints = [
            "/simple/subjects/",
            "/simple/session-progress/",
            "/history/student/admin/",
        ]
        
        for endpoint in test_endpoints:
            try:
                response = self.session.get(f"{BACKEND_BASE}{endpoint}")
                
                if response.status_code == 200:
                    try:
                        json_data = response.json()
                        self.log_result(
                            f"{endpoint}_json",
                            "PASS",
                            "Valid JSON response",
                            {"json_keys": list(json_data.keys()) if isinstance(json_data, dict) else "non_dict"}
                        )
                    except json.JSONDecodeError as e:
                        self.log_result(
                            f"{endpoint}_json",
                            "FAIL",
                            f"Invalid JSON response: {str(e)}",
                            {"raw_response": response.text[:200]}
                        )
                else:
                    self.log_result(
                        f"{endpoint}_json",
                        "INFO",
                        f"Non-200 status code: {response.status_code}"
                    )
                    
            except requests.exceptions.RequestException as e:
                self.log_result(
                    f"{endpoint}_json",
                    "FAIL",
                    f"Request failed: {str(e)}"
                )
    
    def generate_report(self):
        """Generate comprehensive verification report"""
        print("\n" + "="*60)
        print("COMPREHENSIVE ENDPOINT VERIFICATION REPORT")
        print("="*60)
        
        # Count results by status
        status_counts = {}
        for result in self.results:
            status = result["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"\nSUMMARY:")
        for status, count in status_counts.items():
            print(f"  {status}: {count}")
        
        # Critical issues
        critical_issues = [r for r in self.results if r["status"] == "FAIL"]
        if critical_issues:
            print(f"\nCRITICAL ISSUES ({len(critical_issues)}):")
            for issue in critical_issues:
                print(f"  - {issue['endpoint']}: {issue['details']}")
        
        # Warnings
        warnings = [r for r in self.results if r["status"] == "WARN"]
        if warnings:
            print(f"\nWARNINGS ({len(warnings)}):")
            for warning in warnings:
                print(f"  - {warning['endpoint']}: {warning['details']}")
        
        # Save detailed report
        with open("endpoint_verification_report.json", "w") as f:
            json.dump({
                "verification_time": datetime.now().isoformat(),
                "summary": status_counts,
                "results": self.results
            }, f, indent=2)
        
        print(f"\nDetailed report saved to: endpoint_verification_report.json")
        return status_counts.get("FAIL", 0) == 0

def main():
    """Main verification process"""
    print("Starting Frontend-Backend Endpoint Verification...")
    print("="*60)
    
    verifier = EndpointVerifier()
    
    # Run all verification tests
    verifier.verify_frontend_proxy()
    verifier.verify_assessment_history_endpoints() 
    verifier.verify_adaptive_learning_endpoints()
    verifier.verify_database_consistency()
    verifier.verify_json_response_format()
    
    # Generate final report
    success = verifier.generate_report()
    
    if success:
        print("\n✅ All critical tests passed!")
        return 0
    else:
        print("\n❌ Some critical tests failed!")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())