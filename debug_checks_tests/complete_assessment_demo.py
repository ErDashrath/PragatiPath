#!/usr/bin/env python3
"""
Complete Assessment System Demo
Tests the full assessment workflow: start assessment, get questions, submit answers, generate results
"""

import requests
import json
import time
import random
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

class AssessmentDemo:
    def __init__(self):
        self.session = requests.Session()
        self.assessment_id = None
        
    def test_endpoint(self, method, endpoint, data=None, description=""):
        """Test an API endpoint"""
        try:
            url = f"{BASE_URL}{endpoint}"
            
            print(f"\n🔍 {description}")
            print(f"📍 {method.upper()} {endpoint}")
            
            if method.upper() == "GET":
                response = self.session.get(url)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) > 300:
                        print(f"✅ Success: {json.dumps(response_data, indent=2)[:300]}...")
                    else:
                        print(f"✅ Success: {json.dumps(response_data, indent=2)}")
                    return response_data
                except:
                    print(f"✅ Success: {response.text[:200]}...")
                    return response.text
            else:
                print(f"❌ Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Connection Error: {str(e)}")
            return None
    
    def start_assessment(self, student_username="alice_johnson", subject_code="quantitative_aptitude"):
        """Start a new assessment"""
        data = {
            "student_username": student_username,
            "subject_code": subject_code,
            "assessment_type": "PRACTICE",
            "question_count": 5,
            "time_limit_minutes": 30
        }
        
        result = self.test_endpoint("POST", "/api/full-assessment/start", data, 
                                  f"Starting Assessment for {student_username}")
        
        if result and 'assessment_id' in result:
            self.assessment_id = result['assessment_id']
            print(f"🎯 Assessment ID: {self.assessment_id}")
            return True
        return False
    
    def get_questions(self):
        """Get all questions for the assessment"""
        if not self.assessment_id:
            print("❌ No active assessment. Start assessment first.")
            return None
            
        result = self.test_endpoint("GET", f"/api/full-assessment/questions/{self.assessment_id}",
                                  description="Getting Assessment Questions")
        return result
    
    def submit_answer(self, question_id, selected_answer="a", time_taken=45):
        """Submit an answer for a question"""
        if not self.assessment_id:
            print("❌ No active assessment. Start assessment first.")
            return None
            
        data = {
            "assessment_id": self.assessment_id,
            "question_id": question_id,
            "selected_answer": selected_answer,
            "time_taken_seconds": time_taken,
            "confidence_level": random.randint(3, 5)
        }
        
        result = self.test_endpoint("POST", "/api/full-assessment/submit-answer", data,
                                  f"Submitting Answer: {selected_answer} for Question {question_id[:8]}...")
        return result
    
    def complete_assessment(self):
        """Complete the assessment and get results"""
        if not self.assessment_id:
            print("❌ No active assessment. Start assessment first.")
            return None
            
        data = {
            "assessment_id": self.assessment_id
        }
        
        result = self.test_endpoint("POST", "/api/full-assessment/complete", data,
                                  "Completing Assessment and Generating Results")
        return result
    
    def get_student_results(self, username="alice_johnson"):
        """Get past results for a student"""
        result = self.test_endpoint("GET", f"/api/full-assessment/student-results/{username}",
                                  description=f"Getting Past Results for {username}")
        return result
    
    def run_complete_demo(self):
        """Run the complete assessment demo workflow"""
        print("🎯 COMPLETE ASSESSMENT SYSTEM DEMO")
        print("=" * 80)
        print("Testing end-to-end assessment workflow:")
        print("1. Start Assessment → 2. Get Questions → 3. Submit Answers → 4. Generate Results")
        print("=" * 80)
        
        # Step 1: Health check
        self.test_endpoint("GET", "/api/full-assessment/health", 
                          description="Health Check - Assessment API")
        
        # Step 2: Start assessment for Alice
        print(f"\n{'='*60}")
        print("📚 STEP 1: STARTING ASSESSMENT")
        print(f"{'='*60}")
        
        if not self.start_assessment("alice_johnson", "quantitative_aptitude"):
            print("❌ Failed to start assessment")
            return
        
        # Step 3: Get questions
        print(f"\n{'='*60}")
        print("📝 STEP 2: GETTING QUESTIONS")
        print(f"{'='*60}")
        
        questions_data = self.get_questions()
        if not questions_data or 'questions' not in questions_data:
            print("❌ Failed to get questions")
            return
        
        questions = questions_data['questions']
        print(f"📊 Retrieved {len(questions)} questions")
        
        # Step 4: Submit answers for each question
        print(f"\n{'='*60}")
        print("✍️ STEP 3: SUBMITTING ANSWERS")
        print(f"{'='*60}")
        
        answers = ['a', 'b', 'a', 'c', 'a']  # Mix of correct and incorrect
        times = [45, 60, 55, 70, 50]  # Different time taken for each question
        
        for i, question in enumerate(questions):
            selected_answer = answers[i] if i < len(answers) else 'a'
            time_taken = times[i] if i < len(times) else 60
            
            print(f"\n📝 Question {i+1}: {question['question_text'][:80]}...")
            print(f"   Options: {question['options']}")
            print(f"   Selected: {selected_answer}, Time: {time_taken}s")
            
            result = self.submit_answer(question['question_id'], selected_answer, time_taken)
            
            if result:
                status = "✅ CORRECT" if result.get('is_correct') else "❌ INCORRECT"
                correct_ans = result.get('correct_answer', 'Unknown')
                points = result.get('points_earned', 0)
                print(f"   Result: {status} | Correct Answer: {correct_ans} | Points: {points}")
        
        # Step 5: Complete assessment and get results
        print(f"\n{'='*60}")
        print("📊 STEP 4: GENERATING FINAL RESULTS")
        print(f"{'='*60}")
        
        results = self.complete_assessment()
        
        if results:
            self.display_results(results)
        
        # Step 6: Get student's assessment history
        print(f"\n{'='*60}")
        print("📈 STEP 5: STUDENT ASSESSMENT HISTORY")
        print(f"{'='*60}")
        
        history = self.get_student_results("alice_johnson")
        if history:
            print(f"📚 Found {len(history)} past assessments for Alice Johnson")
        
        print(f"\n{'='*80}")
        print("🎉 COMPLETE ASSESSMENT DEMO FINISHED!")
        print(f"{'='*80}")
    
    def display_results(self, results):
        """Display assessment results in a formatted way"""
        print(f"\n🎯 ASSESSMENT RESULTS SUMMARY")
        print(f"├─ Student: {results.get('student_username', 'Unknown')}")
        print(f"├─ Subject: {results.get('subject_name', 'Unknown')}")
        print(f"├─ Questions: {results.get('questions_attempted', 0)}/{results.get('total_questions', 0)}")
        print(f"├─ Accuracy: {results.get('accuracy_percentage', 0)}%")
        print(f"├─ Grade: {results.get('grade', 'N/A')}")
        print(f"├─ Points: {results.get('total_points_earned', 0)}/{results.get('max_possible_points', 0)}")
        print(f"└─ Time: {results.get('total_time_seconds', 0)}s")
        
        # Performance Analysis
        analysis = results.get('performance_analysis', {})
        if analysis:
            print(f"\n📊 PERFORMANCE ANALYSIS")
            
            # Difficulty breakdown
            difficulty_stats = analysis.get('difficulty_breakdown', {})
            if difficulty_stats:
                print("   Difficulty Performance:")
                for difficulty, stats in difficulty_stats.items():
                    accuracy = stats.get('accuracy', 0)
                    total = stats.get('total', 0)
                    print(f"   ├─ {difficulty.title()}: {accuracy:.1f}% ({stats.get('correct', 0)}/{total})")
            
            # Topic breakdown
            topic_stats = analysis.get('topic_breakdown', {})
            if topic_stats:
                print("   Topic Performance:")
                for topic, stats in topic_stats.items():
                    if topic:  # Skip empty topics
                        accuracy = stats.get('accuracy', 0)
                        total = stats.get('total', 0)
                        print(f"   ├─ {topic}: {accuracy:.1f}% ({stats.get('correct', 0)}/{total})")
            
            # Strengths and improvement areas
            strengths = analysis.get('strengths', [])
            improvements = analysis.get('improvement_areas', [])
            
            if strengths:
                print(f"   💪 Strengths: {', '.join(strengths)}")
            if improvements:
                print(f"   📈 Needs Improvement: {', '.join(improvements)}")
        
        # Question-by-question results
        question_results = results.get('question_results', [])
        if question_results:
            print(f"\n📝 QUESTION-BY-QUESTION RESULTS")
            for i, q_result in enumerate(question_results, 1):
                status = "✅" if q_result.get('is_correct') else "❌"
                selected = q_result.get('selected_answer', 'N/A')
                correct = q_result.get('correct_answer', 'N/A')
                time_taken = q_result.get('time_taken_seconds', 0)
                points = q_result.get('points_earned', 0)
                
                print(f"   Q{i}: {status} Selected: {selected} | Correct: {correct} | Time: {time_taken}s | Points: {points}")

def main():
    """Main demo function"""
    demo = AssessmentDemo()
    demo.run_complete_demo()

if __name__ == "__main__":
    main()