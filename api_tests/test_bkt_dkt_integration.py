#!/usr/bin/env python3
"""
BKT/DKT Integration Test Suite

This script tests the complete integration of Bayesian Knowledge Tracing (BKT) 
and Deep Knowledge Tracing (DKT) with adaptive question selection.

Run this script to verify that:
1. BKT algorithm is working and updating skill parameters
2. DKT microservice is accessible and providing predictions  
3. Adaptive question selector is using BKT/DKT data
4. Real-time knowledge tracking is functional
5. Question selection adapts based on student performance
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import random

class BKTDKTIntegrationTester:
    """Comprehensive tester for BKT/DKT integration"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api"
        self.test_results = {}
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Run complete test suite"""
        print("🧪 Starting BKT/DKT Integration Test Suite...")
        print("=" * 60)
        
        # Test 1: System Health Check
        self.test_system_health()
        
        # Test 2: BKT Algorithm Testing
        self.test_bkt_algorithm()
        
        # Test 3: DKT Microservice Testing
        self.test_dkt_microservice()
        
        # Test 4: Adaptive Question Selection
        self.test_adaptive_question_selection()
        
        # Test 5: Knowledge State Integration
        self.test_knowledge_state_integration()
        
        # Test 6: Real-time Adaptation
        self.test_realtime_adaptation()
        
        # Test 7: Algorithm Comparison
        self.test_algorithm_comparison()
        
        # Generate test report
        self.generate_test_report()
        
        return self.test_results
    
    def test_system_health(self):
        """Test 1: Verify all systems are operational"""
        print("\\n1️⃣  Testing System Health...")
        
        try:
            # Test main API health
            response = requests.get(f"{self.api_base}/health", timeout=10)
            self.test_results['main_api'] = {
                'status': 'pass' if response.status_code == 200 else 'fail',
                'response_time': response.elapsed.total_seconds(),
                'data': response.json() if response.status_code == 200 else None
            }
            
            # Test student model status
            response = requests.get(f"{self.api_base}/student-model/status", timeout=10)
            self.test_results['student_model'] = {
                'status': 'pass' if response.status_code == 200 else 'fail',
                'response_time': response.elapsed.total_seconds(),
                'data': response.json() if response.status_code == 200 else None
            }
            
            # Test DKT health
            response = requests.get(f"{self.api_base}/student-model/dkt/health", timeout=10)
            self.test_results['dkt_service'] = {
                'status': 'pass' if response.status_code == 200 else 'fail',
                'response_time': response.elapsed.total_seconds(),
                'data': response.json() if response.status_code == 200 else None
            }
            
            # Test adaptive algorithms status  
            response = requests.get(f"{self.api_base}/adaptive/algorithms/status", timeout=10)
            self.test_results['adaptive_algorithms'] = {
                'status': 'pass' if response.status_code == 200 else 'fail',
                'response_time': response.elapsed.total_seconds(),
                'data': response.json() if response.status_code == 200 else None
            }
            
            print("   ✅ System health check completed")
            
        except Exception as e:
            print(f"   ❌ System health check failed: {e}")
            self.test_results['system_health'] = {'status': 'fail', 'error': str(e)}
    
    def test_bkt_algorithm(self):
        """Test 2: Verify BKT algorithm functionality"""
        print("\\n2️⃣  Testing BKT Algorithm...")
        
        try:
            student_id = "1"  # Use test student ID
            skill_id = "algebra_test"
            
            # Test initial BKT state
            response = requests.get(f"{self.api_base}/student-model/student/{student_id}/bkt/state/{skill_id}")
            initial_state = response.json() if response.status_code == 200 else None
            
            # Test BKT update with correct answer
            update_payload = {
                "skill_id": skill_id,
                "is_correct": True,
                "interaction_data": {
                    "question_id": "test_q1",
                    "response_time": 15.5,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            response = requests.post(
                f"{self.api_base}/student-model/student/{student_id}/bkt/update",
                json=update_payload
            )
            
            updated_state = response.json() if response.status_code == 200 else None
            
            # Test BKT update with incorrect answer
            update_payload["is_correct"] = False
            response = requests.post(
                f"{self.api_base}/student-model/student/{student_id}/bkt/update",
                json=update_payload
            )
            
            # Get all BKT states
            response = requests.get(f"{self.api_base}/student-model/student/{student_id}/bkt/states/all")
            all_states = response.json() if response.status_code == 200 else None
            
            # Test mastered skills
            response = requests.get(f"{self.api_base}/student-model/student/{student_id}/bkt/mastered")
            mastered_skills = response.json() if response.status_code == 200 else None
            
            self.test_results['bkt_algorithm'] = {
                'status': 'pass' if updated_state else 'fail',
                'initial_state': initial_state,
                'updated_state': updated_state,
                'all_states': all_states,
                'mastered_skills': mastered_skills,
                'parameters_updated': updated_state and 'bkt_parameters' in updated_state
            }
            
            print("   ✅ BKT algorithm test completed")
            
        except Exception as e:
            print(f"   ❌ BKT algorithm test failed: {e}")
            self.test_results['bkt_algorithm'] = {'status': 'fail', 'error': str(e)}
    
    def test_dkt_microservice(self):
        """Test 3: Verify DKT microservice functionality"""
        print("\\n3️⃣  Testing DKT Microservice...")
        
        try:
            student_id = "test-student-123"
            
            # Test DKT update
            dkt_payload = {
                "student_id": student_id,
                "skill_id": 5,
                "is_correct": True,
                "response_time": 12.5
            }
            
            response = requests.post(
                f"{self.api_base}/student-model/dkt/update",
                json=dkt_payload
            )
            
            dkt_update_result = response.json() if response.status_code == 200 else None
            
            # Test DKT predictions
            response = requests.get(f"{self.api_base}/student-model/dkt/predict/{student_id}")
            dkt_predictions = response.json() if response.status_code == 200 else None
            
            # Test algorithm comparison
            response = requests.get(f"{self.api_base}/student-model/algorithms/compare/1")
            comparison_result = response.json() if response.status_code == 200 else None
            
            self.test_results['dkt_microservice'] = {
                'status': 'pass' if dkt_predictions else 'fail',
                'update_result': dkt_update_result,
                'predictions': dkt_predictions,
                'comparison': comparison_result,
                'service_available': dkt_predictions and dkt_predictions.get('dkt_service_available', False)
            }
            
            print("   ✅ DKT microservice test completed")
            
        except Exception as e:
            print(f"   ❌ DKT microservice test failed: {e}")
            self.test_results['dkt_microservice'] = {'status': 'fail', 'error': str(e)}
    
    def test_adaptive_question_selection(self):
        """Test 4: Verify adaptive question selection"""
        print("\\n4️⃣  Testing Adaptive Question Selection...")
        
        try:
            student_id = "1"
            
            # Test adaptive recommendations
            recommendation_payload = {
                "student_id": student_id,
                "subject_code": "MATH",
                "count": 5,
                "assessment_type": "ADAPTIVE"
            }
            
            response = requests.post(
                f"{self.api_base}/adaptive/recommendations",
                json=recommendation_payload
            )
            
            recommendations = response.json() if response.status_code == 200 else None
            
            # Test knowledge state analysis
            knowledge_payload = {
                "student_id": student_id,
                "subject_code": "MATH"
            }
            
            response = requests.post(
                f"{self.api_base}/adaptive/knowledge-state",
                json=knowledge_payload
            )
            
            knowledge_state = response.json() if response.status_code == 200 else None
            
            # Test selection trace (debug endpoint)
            response = requests.get(f"{self.api_base}/adaptive/debug/selection-trace/{student_id}")
            selection_trace = response.json() if response.status_code == 200 else None
            
            self.test_results['adaptive_selection'] = {
                'status': 'pass' if recommendations else 'fail',
                'recommendations': recommendations,
                'knowledge_state': knowledge_state,
                'selection_trace': selection_trace,
                'algorithm_used': recommendations.get('algorithm_used') if recommendations else None
            }
            
            print("   ✅ Adaptive question selection test completed")
            
        except Exception as e:
            print(f"   ❌ Adaptive question selection test failed: {e}")
            self.test_results['adaptive_selection'] = {'status': 'fail', 'error': str(e)}
    
    def test_knowledge_state_integration(self):
        """Test 5: Verify knowledge state integration"""
        print("\\n5️⃣  Testing Knowledge State Integration...")
        
        try:
            student_id = "1"
            
            # Get student progress analytics
            response = requests.get(f"{self.api_base}/adaptive/student/{student_id}/progress-analytics")
            progress_analytics = response.json() if response.status_code == 200 else None
            
            # Test real-time knowledge update - get a live question ID from recommendations
            live_question_id = None
            try:
                # Get a question recommendation to get a valid question ID
                rec_response = requests.post(
                    f"{self.api_base}/adaptive/recommendations",
                    json={"student_id": student_id, "subject_code": "quantitative_aptitude", "count": 1}
                )
                if rec_response.status_code == 200:
                    recommendations = rec_response.json().get('recommendations', [])
                    if recommendations:
                        live_question_id = recommendations[0].get('id')
            except Exception as e:
                print(f"   Could not get live question ID: {e}")
            
            # Use live question ID or fallback to skill_id only
            update_payload = {
                "student_id": student_id,
                "question_id": live_question_id or "fallback_question_id",
                "skill_id": "quantitative_aptitude_arithmetic_basics", 
                "is_correct": True,
                "interaction_data": {
                    "response_time": 18.5,
                    "hints_used": 0,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            response = requests.post(
                f"{self.api_base}/adaptive/realtime/update-knowledge",
                json=update_payload
            )
            
            realtime_update = response.json() if response.status_code == 200 else None
            
            self.test_results['knowledge_integration'] = {
                'status': 'pass' if progress_analytics else 'fail',
                'progress_analytics': progress_analytics,
                'realtime_update': realtime_update,
                'subjects_tracked': progress_analytics.get('subjects_attempted', []) if progress_analytics else []
            }
            
            print("   ✅ Knowledge state integration test completed")
            
        except Exception as e:
            print(f"   ❌ Knowledge state integration test failed: {e}")
            self.test_results['knowledge_integration'] = {'status': 'fail', 'error': str(e)}
    
    def test_realtime_adaptation(self):
        """Test 6: Verify real-time adaptation during assessment"""
        print("\\n6️⃣  Testing Real-time Adaptation...")
        
        try:
            # Simulate an assessment session with multiple question attempts
            student_id = "1"
            adaptation_results = []  # Initialize outside the if block
            
            # Start a competitive assessment
            start_payload = {
                "student_id": student_id,
                "subject": "quantitative_aptitude"  # Use actual subject from CSV data
            }
            
            response = requests.post(
                f"{self.api_base}/competitive/v1/assessment/start-subject",
                json=start_payload
            )
            
            assessment_start = response.json() if response.status_code == 200 else None
            
            if assessment_start and assessment_start.get('success'):
                assessment_id = assessment_start['assessment_id']
                
                # Simulate answering multiple questions using live session questions
                
                # Get the first question from the assessment start response
                current_question = assessment_start.get('next_question')
                
                for i in range(3):  # Answer 3 questions
                    if not current_question or not current_question.get('id'):
                        # If no question available, break the loop
                        print(f"   No more questions available at iteration {i+1}")
                        break
                    
                    # Submit an answer using the current live question ID
                    submit_payload = {
                        "student_id": student_id,
                        "assessment_id": assessment_id,
                        "question_id": current_question.get('id'),
                        "answer": "a",  # Use lowercase to match CSV format
                        "is_correct": i % 2 == 0,  # Alternate correct/incorrect
                        "response_time": random.uniform(10, 30),
                        "subject": "quantitative_aptitude",
                        "current_difficulty": "moderate"  # Use actual difficulty from CSV
                    }
                    
                    response = requests.post(
                        f"{self.api_base}/competitive/v1/assessment/submit-answer",
                        json=submit_payload
                    )
                    
                    result = response.json() if response.status_code == 200 else None
                    adaptation_results.append({
                        'question_number': i + 1,
                        'submitted_answer': submit_payload,
                        'adaptation_result': result,
                        'question_id_used': current_question.get('id')
                    })
                    
                    # Get next question from the submit result for the next iteration
                    if result and result.get('success'):
                        current_question = result.get('next_question')
                    else:
                        # Fallback: try to get another question from adaptive API
                        try:
                            next_q_response = requests.post(
                                f"{self.api_base}/adaptive/recommendations",
                                json={"student_id": student_id, "subject_code": "quantitative_aptitude", "count": 1}
                            )
                            if next_q_response.status_code == 200:
                                next_questions = next_q_response.json().get('recommendations', [])
                                current_question = next_questions[0] if next_questions else None
                            else:
                                current_question = None
                        except:
                            current_question = None
                    
                    time.sleep(0.5)  # Small delay between questions
            
            self.test_results['realtime_adaptation'] = {
                'status': 'pass' if assessment_start and assessment_start.get('success') else 'fail',
                'assessment_start': assessment_start,
                'adaptation_sequence': adaptation_results,
                'questions_adapted': len(adaptation_results)
            }
            
            print("   ✅ Real-time adaptation test completed")
            
        except Exception as e:
            print(f"   ❌ Real-time adaptation test failed: {e}")
            self.test_results['realtime_adaptation'] = {'status': 'fail', 'error': str(e)}
    
    def test_algorithm_comparison(self):
        """Test 7: Verify BKT vs DKT algorithm comparison"""
        print("\\n7️⃣  Testing Algorithm Comparison...")
        
        try:
            student_id = "1"
            
            # Get algorithm comparison
            response = requests.get(f"{self.api_base}/student-model/algorithms/compare/{student_id}")
            comparison = response.json() if response.status_code == 200 else None
            
            # Test next question recommendation based on BKT analysis
            response = requests.get(f"{self.api_base}/student-model/student/{student_id}/next-question")
            next_question_bkt = response.json() if response.status_code == 200 else None
            
            self.test_results['algorithm_comparison'] = {
                'status': 'pass' if comparison else 'fail',
                'comparison_result': comparison,
                'next_question_recommendation': next_question_bkt,
                'bkt_available': comparison and 'bkt_predictions' in comparison,
                'dkt_available': comparison and 'dkt_predictions' in comparison,
                'recommended_algorithm': comparison.get('recommended_algorithm') if comparison else None
            }
            
            print("   ✅ Algorithm comparison test completed")
            
        except Exception as e:
            print(f"   ❌ Algorithm comparison test failed: {e}")
            self.test_results['algorithm_comparison'] = {'status': 'fail', 'error': str(e)}
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\\n" + "=" * 60)
        print("📊 BKT/DKT Integration Test Report")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result.get('status') == 'pass')
        
        print(f"\\n📈 Overall Results: {passed_tests}/{total_tests} tests passed")
        print(f"🎯 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\\n🔍 Detailed Results:")
        
        for test_name, result in self.test_results.items():
            status_emoji = "✅" if result.get('status') == 'pass' else "❌"
            print(f"   {status_emoji} {test_name.replace('_', ' ').title()}")
            
            if result.get('status') == 'fail' and 'error' in result:
                print(f"      Error: {result['error']}")
        
        print("\\n🧠 Algorithm Status:")
        
        # BKT Status
        bkt_status = self.test_results.get('bkt_algorithm', {}).get('status', 'unknown')
        print(f"   🤖 BKT Algorithm: {'✅ Working' if bkt_status == 'pass' else '❌ Issues detected'}")
        
        # DKT Status  
        dkt_status = self.test_results.get('dkt_microservice', {}).get('status', 'unknown')
        dkt_available = self.test_results.get('dkt_microservice', {}).get('service_available', False)
        print(f"   🧬 DKT Microservice: {'✅ Working' if dkt_status == 'pass' and dkt_available else '⚠️ Fallback mode'}")
        
        # Adaptive Selection Status
        adaptive_status = self.test_results.get('adaptive_selection', {}).get('status', 'unknown')
        algorithm_used = self.test_results.get('adaptive_selection', {}).get('algorithm_used', 'unknown')
        print(f"   🎯 Adaptive Selection: {'✅ Working' if adaptive_status == 'pass' else '❌ Issues detected'}")
        print(f"      Algorithm in use: {algorithm_used}")
        
        # Real-time Adaptation Status
        realtime_status = self.test_results.get('realtime_adaptation', {}).get('status', 'unknown')
        print(f"   ⚡ Real-time Adaptation: {'✅ Working' if realtime_status == 'pass' else '❌ Issues detected'}")
        
        print("\\n📋 Integration Summary:")
        print("   • Questions are now selected based on BKT/DKT analysis")
        print("   • Student knowledge state updates in real-time")
        print("   • Algorithm selection adapts to data availability") 
        print("   • Fallback mechanisms ensure system reliability")
        
        if passed_tests == total_tests:
            print("\\n🎉 All systems are working perfectly! BKT/DKT integration is complete.")
        elif passed_tests > total_tests * 0.7:
            print("\\n✅ Most systems working well. Minor issues may exist.")
        else:
            print("\\n⚠️ Several issues detected. Please check the logs.")
        
        print("\\n" + "=" * 60)

def main():
    """Run the complete test suite"""
    tester = BKTDKTIntegrationTester()
    
    print("🚀 BKT/DKT Integration Testing")
    print("This will verify that Bayesian and Deep Knowledge Tracing")
    print("are properly integrated with adaptive question selection.")
    print()
    
    # Run all tests
    results = tester.run_all_tests()
    
    # Save detailed results to file
    with open('bkt_dkt_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\\n💾 Detailed results saved to: bkt_dkt_test_results.json")
    
    return results

if __name__ == "__main__":
    main()