#!/usr/bin/env python3
"""
Focused test for Integrated DKT Service and Real-time Adaptation
Tests the two core features with the new integrated architecture.
"""

import requests
import json
from datetime import datetime

class DKTRealtimeTest:
    def __init__(self):
        self.api_base = "http://127.0.0.1:8000/api"
        
    def test_dkt_integration(self):
        """Test DKT integrated service functionality"""
        print("\n🔍 Testing Integrated DKT Service...")
        
        try:
            # Test DKT health via backend API
            health_response = requests.get(f"{self.api_base}/student-model/dkt/health", timeout=5)
            if health_response.status_code == 200:
                health_data = health_response.json()
                if health_data.get('dkt_service_available'):
                    print("   ✅ DKT service is healthy and integrated")
                else:
                    print("   ❌ DKT service not available")
                    return False
            else:
                print(f"   ❌ DKT health check failed: {health_response.status_code}")
                return False
                
            # Create a test student to get DKT predictions
            student_data = {
                "username": f"dkt_test_{datetime.now().strftime('%H%M%S')}",
                "email": f"dkt_test_{datetime.now().strftime('%H%M%S')}@example.com",
                "full_name": f"DKT Test User {datetime.now().strftime('%H%M%S')}"
            }
            
            student_response = requests.post(f"{self.api_base}/core/students", json=student_data)
            if student_response.status_code not in [200, 201]:
                print(f"   ❌ Failed to create test student: {student_response.status_code}")
                return False
                
            student_id = student_response.json().get("id")
            
            # Test DKT prediction endpoint with the student
            prediction_payload = {
                "student_id": student_id,
                "interaction_sequence": [
                    {"skill_id": 0, "is_correct": True, "response_time": 15.5},
                    {"skill_id": 1, "is_correct": False, "response_time": 22.3},
                    {"skill_id": 0, "is_correct": True, "response_time": 18.1}
                ]
            }
            
            prediction_response = requests.post(
                f"{self.api_base}/student-model/dkt/predict",
                json=prediction_payload,
                timeout=10
            )
            
            if prediction_response.status_code == 200:
                result = prediction_response.json()
                if "knowledge_states" in result:
                    print("   ✅ DKT prediction endpoint working")
                    print(f"   📊 Knowledge states: {len(result['knowledge_states'])} skills tracked")
                    return True
                else:
                    print("   ❌ DKT response missing knowledge_states")
                    return False
            else:
                print(f"   ❌ DKT prediction failed: {prediction_response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ DKT integration error: {e}")
            return False
    
    def test_realtime_adaptation(self):
        """Test real-time adaptation functionality"""
        print("\n🔍 Testing Real-time Adaptation...")
        
        try:
            # Create a test student
            user_data = {
                "username": f"test_user_{datetime.now().strftime('%H%M%S')}",
                "email": f"test_{datetime.now().strftime('%H%M%S')}@example.com",
                "full_name": f"Test User {datetime.now().strftime('%H%M%S')}"
            }
            
            user_response = requests.post(f"{self.api_base}/core/students", json=user_data)
            if user_response.status_code not in [200, 201]:
                print(f"   ❌ Failed to create test student: {user_response.status_code}")
                try:
                    print(f"   💭 Error details: {user_response.json()}")
                except:
                    print(f"   💭 Raw response: {user_response.text}")
                return False
                
            user_id = user_response.json().get("id")
            print(f"   ✅ Created test student: {user_id}")
            
            # Start an assessment session to get live question
            assessment_data = {
                "student_id": user_id,
                "subject": "quantitative_aptitude"
            }
            
            session_response = requests.post(
                f"{self.api_base}/competitive/v1/assessment/start-subject",
                json=assessment_data
            )
            
            if session_response.status_code not in [200, 201]:
                print(f"   ❌ Failed to start assessment: {session_response.status_code}")
                return False
                
            session_data = session_response.json()
            question_id = session_data.get("next_question", {}).get("id")
            
            if not question_id:
                print("   ❌ No question ID in assessment response")
                return False
                
            print(f"   ✅ Got live question ID: {question_id}")
            
            # Test real-time knowledge update
            update_payload = {
                "student_id": user_id,
                "question_id": question_id,
                "skill_id": "quantitative_aptitude_arithmetic",
                "is_correct": True,
                "interaction_data": {
                    "response_time": 15.2,
                    "hints_used": 0,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            realtime_response = requests.post(
                f"{self.api_base}/adaptive/realtime/update-knowledge",
                json=update_payload
            )
            
            if realtime_response.status_code == 200:
                result = realtime_response.json()
                if result.get("status") == "success":
                    print("   ✅ Real-time knowledge update successful")
                    print(f"   📈 Updated knowledge state: {result.get('message', 'Updated')}")
                    
                    # Test if BKT integration works
                    if "bkt_mastery" in result or "knowledge_state" in result:
                        print("   ✅ BKT integration active in real-time updates")
                        return True
                    else:
                        print("   ⚠️  Real-time update works but BKT integration unclear")
                        return True
                else:
                    print(f"   ❌ Real-time update failed: {result}")
                    return False
            else:
                print(f"   ❌ Real-time adaptation failed: {realtime_response.status_code}")
                try:
                    error_detail = realtime_response.json()
                    print(f"   💭 Error details: {error_detail}")
                except:
                    print(f"   💭 Raw response: {realtime_response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Real-time adaptation error: {e}")
            return False
    
    def run_focused_test(self):
        """Run focused test on DKT and real-time adaptation only"""
        print("🚀 Starting Focused DKT & Real-time Adaptation Test")
        print("=" * 50)
        
        # Test results
        dkt_result = self.test_dkt_integration()
        realtime_result = self.test_realtime_adaptation()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST RESULTS SUMMARY:")
        print(f"   {'✅' if dkt_result else '❌'} Integrated DKT Service")
        print(f"   {'✅' if realtime_result else '❌'} Real-time Adaptation")
        
        if dkt_result and realtime_result:
            print("\n🎉 ALL CORE FEATURES WORKING! 🎉")
            return True
        else:
            print("\n⚠️  Some core features need attention")
            return False

if __name__ == "__main__":
    tester = DKTRealtimeTest()
    success = tester.run_focused_test()
    exit(0 if success else 1)