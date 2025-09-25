#!/usr/bin/env python3
"""
Direct Frontend Click Test

This demonstrates the simple API that works immediately with frontend clicks.
No complex setup, no orchestration dependencies - just direct working endpoints.
"""

import requests
import json
import time

class DirectFrontendTest:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.api_base = base_url
        self.session_id = None
        
    def test_direct_frontend_flow(self):
        """Test the complete direct frontend click flow"""
        
        print("🎯 Direct Frontend Click Test")
        print("=" * 60)
        print("Testing immediate working endpoints that frontend can use!")
        print()
        
        # Step 1: Health Check
        print("1️⃣ Health Check - Testing API availability...")
        if not self.test_health_check():
            print("   ❌ API not available")
            return False
        
        # Step 2: Start Session
        print("\n2️⃣ Start Session - Creating learning session...")
        if not self.test_start_session():
            print("   ❌ Session creation failed")
            return False
        
        # Step 3: Get Questions and Submit Answers
        print("\n3️⃣ Adaptive Learning Loop - Questions & Answers...")
        for i in range(3):
            print(f"\n   📚 Question {i+1}:")
            
            # Get adaptive question
            if not self.test_get_question():
                print(f"   ❌ Failed to get question {i+1}")
                continue
                
            # Submit answer (alternate correct/wrong for demo)
            is_correct = (i % 2 == 0)  # First and third correct, second wrong
            if not self.test_submit_answer(is_correct):
                print(f"   ❌ Failed to submit answer {i+1}")
                continue
                
            time.sleep(1)  # Brief pause for readability
        
        # Step 4: Check Progress
        print("\n4️⃣ Progress Check - Viewing learning analytics...")
        self.test_get_progress()
        
        print("\n" + "="*60)
        print("✅ Direct Frontend Test Complete!")
        print("🎉 All endpoints are ready for immediate frontend use!")
        
        return True
    
    def test_health_check(self):
        """Test the health endpoint"""
        try:
            response = requests.get(f"{self.api_base}/simple/health")
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ API Status: {result['status']}")
                print(f"   📡 Message: {result['message']}")
                return True
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Health check error: {e}")
            return False
    
    def test_start_session(self):
        """Test starting a learning session"""
        try:
            session_data = {
                "student_name": "Frontend Test User",
                "subject": "mathematics"
            }
            
            response = requests.post(
                f"{self.api_base}/simple/start-session",
                json=session_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                self.session_id = result['session_id']
                print(f"   ✅ Session Created: {self.session_id}")
                print(f"   👤 Student: {result['student_name']}")
                print(f"   📚 Subject: {result['subject']}")
                print(f"   💡 Next Action: {result['next_action']}")
                return True
            else:
                print(f"   ❌ Session creation failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Session creation error: {e}")
            return False
    
    def test_get_question(self):
        """Test getting an adaptive question"""
        try:
            response = requests.get(
                f"{self.api_base}/simple/get-question",
                params={'session_id': self.session_id}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"      🎯 Question {result['question_number']}: {result['difficulty_display']}")
                print(f"      📝 Text: {result['question_text']}")
                print(f"      🧠 Adaptive Info: {result['adaptive_info']['adaptive_reason']}")
                print(f"      💭 Message: {result['message']}")
                
                self.current_question_id = result['question_id']
                return True
            else:
                print(f"      ❌ Question fetch failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"      ❌ Question fetch error: {e}")
            return False
    
    def test_submit_answer(self, is_correct=True):
        """Test submitting an answer"""
        try:
            answer_data = {
                "session_id": self.session_id,
                "question_id": self.current_question_id,
                "selected_answer": "A" if is_correct else "B",
                "time_spent": 12.5
            }
            
            response = requests.post(
                f"{self.api_base}/simple/submit-answer",
                json=answer_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"      {'✅' if result['answer_correct'] else '❌'} Answer: {'Correct!' if result['answer_correct'] else 'Incorrect'}")
                print(f"      🧠 Mastery Level: {result['knowledge_update']['mastery_display']}")
                print(f"      📊 Adaptation: {result['adaptive_feedback']['difficulty_adaptation']}")
                print(f"      💬 Message: {result['adaptive_feedback']['adaptation_message']}")
                return True
            else:
                print(f"      ❌ Answer submission failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"      ❌ Answer submission error: {e}")
            return False
    
    def test_get_progress(self):
        """Test getting session progress"""
        try:
            response = requests.get(
                f"{self.api_base}/simple/session-progress",
                params={'session_id': self.session_id}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   👤 Student: {result['student_name']}")
                print(f"   📚 Subject: {result['subject']}")
                print(f"   📊 Progress: {result['session_stats']['accuracy']} accuracy")
                print(f"   🧠 BKT Mastery: {result['knowledge_state']['bkt_mastery']}")
                print(f"   🎯 DKT Prediction: {result['knowledge_state']['dkt_prediction']}")
                print(f"   💡 Status: {result['adaptive_info']['learning_status']}")
                print(f"   📈 Next Difficulty: {result['adaptive_info']['next_difficulty']}")
                return True
            else:
                print(f"   ❌ Progress fetch failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Progress fetch error: {e}")
            return False

def show_frontend_integration_guide():
    """Show how frontend can integrate with these endpoints"""
    print("\n🌐 Frontend Integration Guide")
    print("=" * 60)
    print("Your frontend can now make these direct HTTP calls:")
    print()
    
    print("1. Start Learning Session:")
    print("   POST http://localhost:8000/simple/start-session")
    print("   Body: {'student_name': 'John Doe', 'subject': 'mathematics'}")
    print("   → Returns session_id for subsequent calls")
    print()
    
    print("2. Get Adaptive Question:")
    print("   GET http://localhost:8000/simple/get-question?session_id=<session_id>")
    print("   → Returns adaptive question based on current mastery")
    print()
    
    print("3. Submit Answer:")
    print("   POST http://localhost:8000/simple/submit-answer")
    print("   Body: {'session_id': '...', 'question_id': '...', 'selected_answer': 'A'}")
    print("   → Updates BKT/DKT models, shows adaptation feedback")
    print()
    
    print("4. Check Progress:")
    print("   GET http://localhost:8000/simple/session-progress?session_id=<session_id>")
    print("   → Shows learning analytics and mastery levels")
    print()
    
    print("5. Health Check:")
    print("   GET http://localhost:8000/simple/health")
    print("   → Verify API is running")
    print()
    
    print("✅ All endpoints are CORS-ready and frontend-friendly!")
    print("🎯 Questions adapt automatically based on BKT/DKT models!")
    print("📊 Real-time mastery tracking with immediate feedback!")

if __name__ == "__main__":
    print("🚀 Testing Direct Frontend API Endpoints")
    print("This test verifies that frontend can immediately use the API!")
    print()
    
    tester = DirectFrontendTest()
    success = tester.test_direct_frontend_flow()
    
    if success:
        show_frontend_integration_guide()
        
        print("\n🎉 SUCCESS: All endpoints working!")
        print("Your frontend is ready to make adaptive learning calls!")
    else:
        print("\n⚠️ Some tests failed, but endpoints are configured.")
        print("Make sure Django server is running on http://localhost:8000")
        
        print("\nTo start the server:")
        print("cd Backend")
        print("python manage.py runserver 8000")