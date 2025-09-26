#!/usr/bin/env python3
"""
Comprehensive Frontend-Compatible LangGraph Orchestration Test

Tests complete integration between frontend API calls, LangGraph orchestration,
and database consistency across the entire adaptive learning workflow.
"""

import requests
import json
from datetime import datetime
import time

class FrontendOrchestrationTester:
    def __init__(self, base_url="http://127.0.0.1:8000/api"):
        self.api_base = base_url
        self.test_student_id = None
        self.test_session_id = None

    def run_comprehensive_frontend_test(self):
        """Run complete frontend-compatible orchestration test"""
        
        print("🌐 Frontend-Compatible LangGraph Orchestration Test")
        print("=" * 70)
        
        success_count = 0
        total_tests = 7
        
        # Test 1: System Health Check
        if self.test_system_health():
            success_count += 1
        
        # Test 2: Create Student (Database Consistency)
        if self.create_test_student():
            success_count += 1
            
            # Test 3: Start Learning Session
            if self.start_learning_session():
                success_count += 1
                
                # Test 4: Get Adaptive Question
                if self.get_adaptive_question():
                    success_count += 1
                    
                    # Test 5: Submit Answer with Orchestration
                    if self.submit_answer_with_orchestration():
                        success_count += 1
                        
                        # Test 6: Complete Session
                        if self.complete_learning_session():
                            success_count += 1
                            
                            # Test 7: Get Analytics
                            if self.get_learning_analytics():
                                success_count += 1
        
        # Summary
        print("\n" + "=" * 70)
        print("🏁 FRONTEND ORCHESTRATION TEST SUMMARY:")
        print(f"   ✅ Passed: {success_count}/{total_tests}")
        print(f"   📊 Success Rate: {(success_count/total_tests)*100:.1f}%")
        
        if success_count == total_tests:
            print("   🎉 ALL TESTS PASSED - Frontend-compatible orchestration working perfectly!")
            print("   🌐 Database consistency maintained across all operations!")
            print("   🤖 LangGraph orchestration seamlessly integrated with frontend!")
        else:
            print(f"   ⚠️  {total_tests - success_count} tests failed - Check logs above")
        
        return success_count == total_tests

    def test_system_health(self):
        """Test system health with database and orchestration verification"""
        print("\n🔍 Testing Frontend Orchestration System Health...")
        
        try:
            response = requests.get(f"{self.api_base}/frontend-orchestration/system/health")
            
            if response.status_code == 200:
                result = response.json()
                
                print("   ✅ System health check passed")
                print(f"   🤖 LangGraph: {result.get('langraph_orchestration', 'unknown')}")
                print(f"   🗄️ Database models: {list(result.get('database_models', {}).keys())}")
                print(f"   🧠 BKT service: {result.get('knowledge_services', {}).get('bkt_service', False)}")
                print(f"   🎯 DKT service: {result.get('knowledge_services', {}).get('dkt_service', False)}")
                print(f"   🌐 Frontend compatibility: {result.get('frontend_compatibility', 'unknown')}")
                print(f"   📊 Field consistency: {result.get('field_consistency', 'unknown')}")
                
                return (result.get('status') == 'healthy' and 
                       result.get('langraph_orchestration') == 'active' and
                       result.get('frontend_compatibility') == 'ensured')
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Health check error: {e}")
            return False

    def create_test_student(self):
        """Create test student with proper database consistency"""
        print("\n👤 Creating Test Student...")
        
        try:
            student_data = {
                "username": f"frontend_test_{datetime.now().strftime('%H%M%S')}",
                "email": f"frontend_test_{datetime.now().strftime('%H%M%S')}@test.com",
                "full_name": f"Frontend Test User {datetime.now().strftime('%H%M%S')}"
            }
            
            response = requests.post(f"{self.api_base}/core/students", json=student_data)
            
            if response.status_code in [200, 201]:
                student = response.json()
                self.test_student_id = student['id']
                print(f"   ✅ Student created: {self.test_student_id}")
                print(f"   👤 Username: {student.get('username', 'N/A')}")
                print(f"   📧 Email: {student.get('email', 'N/A')}")
                print(f"   🆔 UUID Format: {len(self.test_student_id) > 30}")  # UUID check
                return True
            else:
                print(f"   ❌ Student creation failed: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   💭 Error: {error_detail}")
                except:
                    pass
                return False
                
        except Exception as e:
            print(f"   ❌ Student creation error: {e}")
            return False

    def start_learning_session(self):
        """Start orchestrated learning session with frontend-compatible API"""
        print("\n🚀 Starting Learning Session...")
        
        try:
            session_data = {
                "student_id": self.test_student_id,
                "subject": "mathematics",
                "difficulty_level": "medium",
                "max_questions": 5,
                "session_type": "adaptive"
            }
            
            response = requests.post(
                f"{self.api_base}/frontend-orchestration/learning-session/start",
                json=session_data
            )
            
            if response.status_code == 200:
                result = response.json()
                
                self.test_session_id = result['session_id']
                print("   ✅ Learning session started successfully")
                print(f"   🆔 Session ID: {self.test_session_id}")
                print(f"   📚 Subject: {result.get('subject', 'N/A')}")
                print(f"   📊 Initial BKT mastery: {result.get('initial_knowledge_state', {}).get('bkt_mastery', 0):.3f}")
                print(f"   🎯 Initial DKT prediction: {result.get('initial_knowledge_state', {}).get('dkt_prediction', 0):.3f}")
                print(f"   🤖 Orchestration ready: {result.get('orchestration_ready', False)}")
                print(f"   🌐 Session type: {result.get('session_type', 'unknown')}")
                
                return (result.get('success', False) and 
                       result.get('orchestration_ready', False) and
                       self.test_session_id is not None)
            else:
                print(f"   ❌ Session start failed: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   💭 Error: {error_detail}")
                except:
                    pass
                return False
                
        except Exception as e:
            print(f"   ❌ Session start error: {e}")
            return False

    def get_adaptive_question(self):
        """Get adaptive question using LangGraph orchestration"""
        print("\n🎯 Getting Adaptive Question...")
        
        try:
            response = requests.get(
                f"{self.api_base}/frontend-orchestration/learning-session/{self.test_session_id}/next-question"
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print("   ✅ Adaptive question retrieved successfully")
                print(f"   🆔 Question ID: {result.get('id', 'N/A')}")
                print(f"   📝 Question type: {result.get('question_type', 'N/A')}")
                print(f"   📊 Difficulty: {result.get('difficulty_level', 'N/A')}")
                print(f"   🎯 Skill ID: {result.get('skill_id', 'N/A')}")
                print(f"   🤖 Selection algorithm: {result.get('orchestration_metadata', {}).get('selection_algorithm', 'N/A')}")
                
                # Store for next test
                self.test_question_id = result.get('id')
                self.correct_answer = result.get('correct_answer', 'A')
                
                return (result.get('id') is not None and
                       result.get('difficulty_level') is not None and
                       'orchestration_metadata' in result)
            else:
                print(f"   ❌ Question retrieval failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Question retrieval error: {e}")
            return False

    def submit_answer_with_orchestration(self):
        """Submit answer and trigger orchestrated knowledge update"""
        print("\n📝 Submitting Answer with Orchestration...")
        
        try:
            # Submit a correct answer
            answer_data = {
                "session_id": self.test_session_id,
                "student_id": self.test_student_id,
                "question_id": self.test_question_id,
                "selected_answer": self.correct_answer,
                "is_correct": True,
                "time_spent": 25.5,
                "hint_count": 0,
                "attempt_number": 1
            }
            
            response = requests.post(
                f"{self.api_base}/frontend-orchestration/learning-session/submit-answer",
                json=answer_data
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print("   ✅ Answer submitted and processed successfully")
                print(f"   🆔 Attempt ID: {result.get('attempt_id', 'N/A')}")
                print(f"   🤖 Orchestration complete: {result.get('orchestration_complete', False)}")
                print(f"   📊 Updated BKT mastery: {result.get('knowledge_updated', {}).get('bkt_mastery', 0):.3f}")
                print(f"   🎯 Updated DKT prediction: {result.get('knowledge_updated', {}).get('dkt_prediction', 0):.3f}")
                print(f"   📈 Session accuracy: {result.get('session_progress', {}).get('accuracy', 0):.3f}")
                print(f"   💡 Recommendation: {result.get('session_progress', {}).get('recommendation', 'N/A')}")
                print(f"   🔄 Continue session: {result.get('continue_session', False)}")
                
                return (result.get('success', False) and
                       result.get('orchestration_complete', False) and
                       'knowledge_updated' in result)
            else:
                print(f"   ❌ Answer submission failed: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   💭 Error: {error_detail}")
                except:
                    pass
                return False
                
        except Exception as e:
            print(f"   ❌ Answer submission error: {e}")
            return False

    def complete_learning_session(self):
        """Complete the learning session with comprehensive analytics"""
        print("\n🏁 Completing Learning Session...")
        
        try:
            response = requests.post(
                f"{self.api_base}/frontend-orchestration/learning-session/{self.test_session_id}/complete"
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print("   ✅ Learning session completed successfully")
                print(f"   📊 Total questions: {result.get('orchestration_summary', {}).get('total_questions', 0)}")
                print(f"   ✅ Correct answers: {result.get('orchestration_summary', {}).get('correct_answers', 0)}")
                print(f"   📈 Final accuracy: {result.get('orchestration_summary', {}).get('accuracy', 0):.3f}")
                print(f"   🧠 Final BKT mastery: {result.get('final_knowledge_state', {}).get('bkt_mastery', 0):.3f}")
                print(f"   🎯 Final DKT prediction: {result.get('final_knowledge_state', {}).get('dkt_prediction', 0):.3f}")
                print(f"   🏆 Mastery achieved: {result.get('final_knowledge_state', {}).get('mastery_achieved', False)}")
                print(f"   💡 Next focus: {result.get('recommendations', {}).get('next_session_focus', 'N/A')}")
                print(f"   🗄️ DB consistency: {result.get('database_consistency', 'unknown')}")
                
                return (result.get('success', False) and
                       result.get('session_complete', False) and
                       result.get('database_consistency') == 'maintained')
            else:
                print(f"   ❌ Session completion failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Session completion error: {e}")
            return False

    def get_learning_analytics(self):
        """Get comprehensive learning analytics with database consistency"""
        print("\n📊 Getting Learning Analytics...")
        
        try:
            response = requests.get(
                f"{self.api_base}/frontend-orchestration/student/{self.test_student_id}/learning-analytics"
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print("   ✅ Learning analytics retrieved successfully")
                print(f"   👤 Student: {result.get('username', 'N/A')} ({result.get('email', 'N/A')})")
                
                analytics = result.get('learning_analytics', {})
                bkt_data = analytics.get('knowledge_models', {}).get('bkt', {})
                dkt_data = analytics.get('knowledge_models', {}).get('dkt', {})
                progress = analytics.get('overall_progress', {})
                integration = analytics.get('langraph_integration', {})
                
                print(f"   🧠 BKT skills tracked: {len(bkt_data.get('masteries', {}))}")
                print(f"   🎯 DKT predictions: {len(dkt_data.get('predictions', {}))}")
                print(f"   📚 Total sessions: {progress.get('total_sessions', 0)}")
                print(f"   🤖 Orchestrated sessions: {progress.get('orchestrated_sessions', 0)}")
                print(f"   📈 Average accuracy: {progress.get('average_accuracy', 0):.3f}")
                print(f"   🔄 Orchestration active: {integration.get('orchestration_active', False)}")
                print(f"   🗄️ DB consistency: {integration.get('database_consistency', 'unknown')}")
                
                return (result.get('student_id') == self.test_student_id and
                       integration.get('orchestration_active', False) and
                       integration.get('database_consistency') == 'verified')
            else:
                print(f"   ❌ Analytics retrieval failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Analytics retrieval error: {e}")
            return False

if __name__ == "__main__":
    tester = FrontendOrchestrationTester()
    success = tester.run_comprehensive_frontend_test()
    
    if success:
        print("\n🎉 Frontend-compatible LangGraph orchestration is fully functional!")
        print("🌐 Database consistency maintained across all operations!")
        print("🤖 Ready for production frontend integration!")
    else:
        print("\n⚠️ Some frontend orchestration tests failed. Check the logs above.")
    
    exit(0 if success else 1)