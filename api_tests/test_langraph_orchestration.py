#!/usr/bin/env python3
"""
LangGraph Orchestration Test Suite

Test the complete LangGraph-orchestrated adaptive learning workflow
that coordinates BKT and DKT services for intelligent adaptation.
"""

import requests
import json
from datetime import datetime

class LangGraphOrchestrationTester:
    def __init__(self, base_url="http://127.0.0.1:8000/api"):
        self.api_base = base_url
        self.test_student_id = None

    def run_comprehensive_test(self):
        """Run complete LangGraph orchestration test suite"""
        
        print("🤖 LangGraph Adaptive Learning Orchestration Test")
        print("=" * 60)
        
        success_count = 0
        total_tests = 5
        
        # Test 1: System Health
        if self.test_orchestration_health():
            success_count += 1
        
        # Test 2: Create Test Student  
        if self.create_test_student():
            success_count += 1
            
            # Test 3: Workflow Status
            if self.test_workflow_status():
                success_count += 1
            
            # Test 4: Simulate Adaptive Session
            if self.test_adaptive_simulation():
                success_count += 1
            
            # Test 5: Run Real Orchestrated Session
            if self.test_full_orchestration():
                success_count += 1
        
        # Summary
        print("\n" + "=" * 60)
        print("🏁 LANGRAPH ORCHESTRATION TEST SUMMARY:")
        print(f"   ✅ Passed: {success_count}/{total_tests}")
        print(f"   📊 Success Rate: {(success_count/total_tests)*100:.1f}%")
        
        if success_count == total_tests:
            print("   🎉 ALL TESTS PASSED - LangGraph orchestration is working perfectly!")
        else:
            print(f"   ⚠️  {total_tests - success_count} tests failed - Check logs above")
        
        return success_count == total_tests

    def test_orchestration_health(self):
        """Test orchestration system health"""
        print("\n🔍 Testing LangGraph Orchestration Health...")
        
        try:
            response = requests.get(f"{self.api_base}/orchestration/adaptive-session/health")
            
            if response.status_code == 200:
                result = response.json()
                
                print("   ✅ Orchestration system is healthy")
                print(f"   🤖 LangGraph ready: {result.get('langraph_available', False)}")
                print(f"   🧠 BKT integrated: {result.get('services_integrated', {}).get('bkt', False)}")
                print(f"   🎯 DKT integrated: {result.get('services_integrated', {}).get('dkt', False)}")
                
                return (result.get('status') == 'healthy' and 
                       result.get('orchestrator_ready', False) and
                       result.get('langraph_available', False))
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Health check error: {e}")
            return False

    def create_test_student(self):
        """Create a test student for orchestration testing"""
        print("\n👤 Creating Test Student...")
        
        try:
            student_data = {
                "username": f"langraph_test_{datetime.now().strftime('%H%M%S')}",
                "email": f"langraph_test_{datetime.now().strftime('%H%M%S')}@test.com",
                "full_name": f"LangGraph Test User {datetime.now().strftime('%H%M%S')}"
            }
            
            response = requests.post(f"{self.api_base}/core/students", json=student_data)
            
            if response.status_code in [200, 201]:
                student = response.json()
                self.test_student_id = student['id']
                print(f"   ✅ Test student created: {self.test_student_id}")
                return True
            else:
                print(f"   ❌ Student creation failed: {response.status_code}")
                try:
                    print(f"   💭 Error: {response.json()}")
                except:
                    pass
                return False
                
        except Exception as e:
            print(f"   ❌ Student creation error: {e}")
            return False

    def test_workflow_status(self):
        """Test workflow status endpoint"""
        print("\n📊 Testing Workflow Status...")
        
        try:
            response = requests.get(
                f"{self.api_base}/orchestration/adaptive-session/workflow-status/{self.test_student_id}"
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print("   ✅ Workflow status retrieved successfully")
                print(f"   🎯 Workflow ready: {result.get('workflow_ready', False)}")
                print(f"   🧠 BKT state available: {'bkt' in result.get('current_knowledge_state', {})}")
                print(f"   🎯 DKT state available: {'dkt' in result.get('current_knowledge_state', {})}")
                print(f"   🔄 Next action: {result.get('next_recommended_action', 'unknown')}")
                
                return result.get('workflow_ready', False)
            else:
                print(f"   ❌ Workflow status failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Workflow status error: {e}")
            return False

    def test_adaptive_simulation(self):
        """Test simulated adaptive session"""
        print("\n🎭 Testing Adaptive Session Simulation...")
        
        try:
            simulation_data = {
                "student_id": self.test_student_id,
                "subject": "mathematics",
                "max_iterations": 3,  # Short simulation
                "mastery_threshold": 0.7
            }
            
            response = requests.post(
                f"{self.api_base}/orchestration/adaptive-session/simulate",
                json=simulation_data
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print("   ✅ Simulation completed successfully")
                print(f"   📝 Questions attempted: {result.get('questions_attempted', 0)}")
                print(f"   🎯 Final skill: {result.get('final_skill', 'unknown')}")
                print(f"   📊 BKT mastery: {result.get('bkt_mastery', 0):.3f}")
                print(f"   🎯 DKT prediction: {result.get('dkt_prediction', 0):.3f}")
                print(f"   💡 Recommendation: {result.get('recommendation', 'none')}")
                
                return result.get('success', False) and result.get('questions_attempted', 0) > 0
            else:
                print(f"   ❌ Simulation failed: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   💭 Error: {error_detail}")
                except:
                    pass
                return False
                
        except Exception as e:
            print(f"   ❌ Simulation error: {e}")
            return False

    def test_full_orchestration(self):
        """Test full LangGraph orchestrated adaptive session"""
        print("\n🤖 Testing Full LangGraph Orchestration...")
        
        try:
            session_data = {
                "student_id": self.test_student_id,
                "subject": "mathematics",
                "max_iterations": 5,
                "mastery_threshold": 0.8
            }
            
            print("   🚀 Starting orchestrated adaptive session...")
            
            response = requests.post(
                f"{self.api_base}/orchestration/adaptive-session/start",
                json=session_data
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print("   ✅ LangGraph orchestration completed successfully!")
                print(f"   📚 Subject: {result.get('subject', 'unknown')}")
                print(f"   📝 Questions processed: {result.get('questions_attempted', 0)}")
                print(f"   🎯 Final skill level: {result.get('final_skill', 'unknown')}")
                print(f"   📈 BKT final mastery: {result.get('bkt_mastery', 0):.3f}")
                print(f"   🎯 DKT final prediction: {result.get('dkt_prediction', 0):.3f}")
                print(f"   💡 Final recommendation: {result.get('recommendation', 'none')}")
                print(f"   ✅ Session complete: {result.get('session_complete', False)}")
                
                # Test analytics endpoint
                analytics_response = requests.get(
                    f"{self.api_base}/orchestration/adaptive-session/analytics/{self.test_student_id}"
                )
                
                if analytics_response.status_code == 200:
                    analytics = analytics_response.json()
                    print(f"   📊 Skills tracked: {analytics.get('orchestration_insights', {}).get('total_skills_tracked', 0)}")
                    print(f"   🎯 Avg BKT mastery: {analytics.get('orchestration_insights', {}).get('average_bkt_mastery', 0):.3f}")
                    print(f"   📈 LangGraph status: {analytics.get('orchestration_insights', {}).get('langraph_orchestration', 'inactive')}")
                
                return (result.get('success', False) and 
                       result.get('questions_attempted', 0) > 0 and
                       result.get('session_complete', False))
            else:
                print(f"   ❌ Orchestration failed: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   💭 Error: {error_detail}")
                except:
                    pass
                return False
                
        except Exception as e:
            print(f"   ❌ Orchestration error: {e}")
            return False

if __name__ == "__main__":
    tester = LangGraphOrchestrationTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 LangGraph orchestration is fully functional!")
        print("🤖 Ready for production adaptive learning workflows!")
    else:
        print("\n⚠️ Some orchestration tests failed. Check the logs above.")
    
    exit(0 if success else 1)