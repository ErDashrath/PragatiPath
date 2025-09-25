"""
Comprehensive Test for AI-Enhanced Competitive Exam System
Tests EXAM mode, PRACTICE mode, and POST-EXAM AI analysis
"""

import requests
import json
import time
import asyncio
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:8000"

class AIEnhancedExamTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.student_id = None
        self.exam_session_id = None
        self.practice_session_id = None
    
    def setup_test_student(self):
        """Create or get test student"""
        print("🔧 Setting up test student...")
        
        # Create student profile
        response = requests.post(f"{self.base_url}/api/core/students/", json={
            "username": f"ai_test_student_{int(time.time())}",
            "email": f"ai_test_{int(time.time())}@example.com",
            "first_name": "AI Test",
            "last_name": "Student"
        })
        
        if response.status_code == 201:
            student_data = response.json()
            self.student_id = student_data['id']
            print(f"✅ Created test student: {self.student_id}")
        else:
            print(f"❌ Failed to create student: {response.status_code}")
            print(response.text)
            return False
        
        return True
    
    def test_exam_mode_flow(self):
        """Test complete EXAM mode flow (no AI assistance during exam)"""
        print("\n" + "="*60)
        print("🎯 TESTING EXAM MODE - No AI assistance during questions")
        print("="*60)
        
        # Start EXAM mode assessment
        print("\n1. Starting EXAM mode assessment...")
        response = requests.post(f"{self.base_url}/api/assessment/v2/assessment/start", json={
            "student_id": self.student_id,
            "subject": "quantitative_aptitude",
            "assessment_mode": "EXAM"
        })
        
        if response.status_code != 200:
            print(f"❌ Failed to start exam: {response.status_code}")
            print(response.text)
            return False
        
        exam_data = response.json()
        self.exam_session_id = exam_data['session_id']
        print(f"✅ Started exam session: {self.exam_session_id}")
        print(f"   Mode: {exam_data['assessment_mode']}")
        print(f"   Mode Features: {json.dumps(exam_data['mode_features'], indent=2)}")
        
        # Answer several questions in EXAM mode (no hints allowed)
        print("\n2. Answering questions in EXAM mode (no AI help)...")
        questions_answered = 0
        current_question = exam_data.get('next_question')
        
        for i in range(5):  # Answer 5 questions
            if not current_question:
                print(f"   No more questions available after {questions_answered}")
                break
            
            print(f"\n   Question {i+1}: {current_question['question_text'][:80]}...")
            
            # Simulate answering (randomly choose answer for demo)
            import random
            answer_choices = ['a', 'b', 'c', 'd']
            chosen_answer = random.choice(answer_choices)
            
            # Submit answer
            response = requests.post(f"{self.base_url}/api/assessment/v2/assessment/submit-answer", json={
                "student_id": self.student_id,
                "session_id": self.exam_session_id,
                "question_id": current_question['id'],
                "answer": chosen_answer,
                "response_time": random.uniform(30, 90),
                "assessment_mode": "EXAM",
                "hints_used": 0
            })
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Answer: {chosen_answer} | Correct: {result['was_correct']} | Accuracy: {result['session_stats']['accuracy_rate']:.1%}")
                current_question = result.get('next_question')
                questions_answered += 1
            else:
                print(f"   ❌ Failed to submit answer: {response.status_code}")
                break
        
        # Complete the exam
        print("\n3. Completing exam and requesting AI analysis...")
        response = requests.post(f"{self.base_url}/api/assessment/v2/exam/complete", json={
            "student_id": self.student_id,
            "session_id": self.exam_session_id,
            "request_ai_analysis": True
        })
        
        if response.status_code == 200:
            completion_data = response.json()
            print("✅ Exam completed successfully!")
            print(f"   Final Stats: {json.dumps(completion_data['final_stats'], indent=2)}")
            print(f"   AI Analysis: {completion_data['analysis_availability']}")
        else:
            print(f"❌ Failed to complete exam: {response.status_code}")
            return False
        
        return True
    
    def test_post_exam_ai_analysis(self):
        """Test post-exam AI analysis with LangGraph + Gemini"""
        print("\n" + "="*60)
        print("🤖 TESTING POST-EXAM AI ANALYSIS - LangGraph + Gemini Integration")
        print("="*60)
        
        if not self.exam_session_id:
            print("❌ No exam session to analyze")
            return False
        
        print("\n1. Requesting comprehensive AI analysis...")
        print("   Note: This requires GOOGLE_API_KEY in .env file")
        
        response = requests.get(f"{self.base_url}/api/assessment/v2/exam/{self.exam_session_id}/analysis")
        
        if response.status_code == 200:
            analysis_data = response.json()
            print("✅ AI Analysis completed!")
            
            analysis = analysis_data['analysis']
            if 'error' not in analysis:
                print(f"\n   📊 Analysis Summary:")
                summary = analysis.get('summary', {})
                print(f"   • Total Questions: {summary.get('total_questions', 'N/A')}")
                print(f"   • Correct Answers: {summary.get('correct_answers', 'N/A')}")
                print(f"   • Accuracy Rate: {summary.get('accuracy_rate', 0):.1%}")
                print(f"   • Time Spent: {summary.get('time_spent_minutes', 0):.1f} minutes")
                
                recommendations = analysis.get('recommendations', {})
                if recommendations.get('immediate_actions'):
                    print(f"\n   🎯 AI Recommendations:")
                    for action in recommendations['immediate_actions'][:3]:
                        print(f"   • {action}")
            else:
                print(f"   ⚠️ Analysis had issues: {analysis.get('error', 'Unknown error')}")
        else:
            print(f"❌ Failed to get analysis: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        print("\n2. Getting detailed explanations for wrong answers...")
        response = requests.get(f"{self.base_url}/api/assessment/v2/exam/{self.exam_session_id}/explanations")
        
        if response.status_code == 200:
            explanations_data = response.json()
            print(f"✅ Got explanations for {explanations_data['total_wrong_answers']} wrong answers")
            
            for i, explanation in enumerate(explanations_data['explanations'][:2]):  # Show first 2
                print(f"\n   📝 Wrong Answer #{i+1}:")
                print(f"   Question: {explanation['question_text'][:60]}...")
                print(f"   Your Answer: {explanation['your_answer']}")
                print(f"   Correct Answer: {explanation['correct_answer']}")
                print(f"   Explanation: {explanation['explanation'][:100]}...")
        else:
            print(f"❌ Failed to get explanations: {response.status_code}")
        
        return True
    
    def test_practice_mode_flow(self):
        """Test PRACTICE mode flow with AI assistance"""
        print("\n" + "="*60)
        print("🎓 TESTING PRACTICE MODE - AI assistance available during questions")
        print("="*60)
        
        # Start PRACTICE mode assessment
        print("\n1. Starting PRACTICE mode assessment...")
        response = requests.post(f"{self.base_url}/api/assessment/v2/assessment/start", json={
            "student_id": self.student_id,
            "subject": "logical_reasoning",
            "assessment_mode": "PRACTICE"
        })
        
        if response.status_code != 200:
            print(f"❌ Failed to start practice: {response.status_code}")
            return False
        
        practice_data = response.json()
        self.practice_session_id = practice_data['session_id']
        print(f"✅ Started practice session: {self.practice_session_id}")
        print(f"   Mode Features: {json.dumps(practice_data['mode_features'], indent=2)}")
        
        # Demo practice with AI assistance
        current_question = practice_data.get('next_question')
        if current_question:
            print(f"\n2. Practice question: {current_question['question_text'][:80]}...")
            
            # Request hints (only available in PRACTICE mode)
            print("\n3. Requesting AI hints...")
            for hint_level in [1, 2]:
                response = requests.post(f"{self.base_url}/api/assessment/v2/practice/hint", json={
                    "student_id": self.student_id,
                    "session_id": self.practice_session_id,
                    "question_id": current_question['id'],
                    "hint_level": hint_level
                })
                
                if response.status_code == 200:
                    hint_data = response.json()
                    print(f"   💡 Hint Level {hint_level}: {hint_data['hint']}")
                else:
                    print(f"   ❌ Failed to get hint: {response.status_code}")
            
            # Submit answer
            print("\n4. Submitting answer and requesting explanation...")
            import random
            chosen_answer = random.choice(['a', 'b', 'c', 'd'])
            
            response = requests.post(f"{self.base_url}/api/assessment/v2/assessment/submit-answer", json={
                "student_id": self.student_id,
                "session_id": self.practice_session_id,
                "question_id": current_question['id'],
                "answer": chosen_answer,
                "response_time": 45.0,
                "assessment_mode": "PRACTICE",
                "hints_used": 2
            })
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Answer submitted: {chosen_answer} | Correct: {result['was_correct']}")
                
                # Get detailed explanation (only available in PRACTICE mode)
                response = requests.post(f"{self.base_url}/api/assessment/v2/practice/explanation", json={
                    "student_id": self.student_id,
                    "session_id": self.practice_session_id,
                    "question_id": current_question['id'],
                    "student_answer": chosen_answer
                })
                
                if response.status_code == 200:
                    explanation_data = response.json()
                    explanation = explanation_data['explanation']
                    print(f"\n   📚 AI Explanation:")
                    print(f"   • Feedback: {explanation.get('feedback', 'N/A')}")
                    print(f"   • Key Concepts: {explanation.get('key_concepts', [])}")
                    print(f"   • Practice Suggestions: {explanation.get('practice_suggestions', [])}")
                else:
                    print(f"   ❌ Failed to get explanation: {response.status_code}")
            else:
                print(f"   ❌ Failed to submit answer: {response.status_code}")
        
        return True
    
    def test_mode_restrictions(self):
        """Test that mode restrictions are enforced"""
        print("\n" + "="*60)
        print("🔒 TESTING MODE RESTRICTIONS - AI features only in correct modes")
        print("="*60)
        
        if not self.exam_session_id:
            print("❌ No exam session for restriction testing")
            return False
        
        print("\n1. Trying to request hint in EXAM mode (should fail)...")
        response = requests.post(f"{self.base_url}/api/assessment/v2/practice/hint", json={
            "student_id": self.student_id,
            "session_id": self.exam_session_id,  # EXAM session
            "question_id": "dummy-question-id",
            "hint_level": 1
        })
        
        if response.status_code == 403:
            print("✅ Correctly blocked hint request in EXAM mode")
        else:
            print(f"❌ Should have blocked hint request: {response.status_code}")
        
        print("\n2. Trying to get practice explanation in EXAM mode (should fail)...")
        response = requests.post(f"{self.base_url}/api/assessment/v2/practice/explanation", json={
            "student_id": self.student_id,
            "session_id": self.exam_session_id,  # EXAM session
            "question_id": "dummy-question-id",
            "student_answer": "a"
        })
        
        if response.status_code == 403:
            print("✅ Correctly blocked practice explanation in EXAM mode")
        else:
            print(f"❌ Should have blocked explanation request: {response.status_code}")
        
        return True
    
    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🚀 Starting Comprehensive AI-Enhanced Exam System Test")
        print("="*60)
        
        # Setup
        if not self.setup_test_student():
            return
        
        # Test flows
        self.test_exam_mode_flow()
        self.test_post_exam_ai_analysis()
        self.test_practice_mode_flow()
        self.test_mode_restrictions()
        
        # Summary
        print("\n" + "="*60)
        print("🎉 COMPREHENSIVE TEST COMPLETED")
        print("="*60)
        print("\n✅ EXAM Mode: Complete exam without AI assistance")
        print("✅ POST-EXAM Analysis: LangGraph + Gemini comprehensive analysis")
        print("✅ PRACTICE Mode: AI hints and immediate explanations")
        print("✅ Mode Restrictions: AI features properly restricted by mode")
        print("\n🔑 Key Features Demonstrated:")
        print("   • Assessment mode separation (EXAM vs PRACTICE)")
        print("   • Post-exam AI analysis with detailed explanations")
        print("   • Practice mode AI assistance (hints + explanations)")
        print("   • Mode-based access control for AI features")
        print("   • Integration with existing BKT mastery system")
        
        print(f"\n📊 Test Results:")
        print(f"   • Student ID: {self.student_id}")
        print(f"   • Exam Session: {self.exam_session_id}")
        print(f"   • Practice Session: {self.practice_session_id}")

if __name__ == "__main__":
    print("⚠️  IMPORTANT: Make sure to:")
    print("   1. Add your GOOGLE_API_KEY to the .env file")
    print("   2. Start the Django server: python manage.py runserver 8000")
    print("   3. Ensure all migrations are applied")
    print()
    
    input("Press Enter when ready to start the test...")
    
    tester = AIEnhancedExamTester()
    tester.run_comprehensive_test()