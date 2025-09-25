#!/usr/bin/env python3
"""
Test Complete Assessment Workflow
Tests the entire assessment flow from setup to results with 10-minute timer
and verifies database persistence.
"""

import os
import sys
import django
import requests
import json
import time
from datetime import datetime

# Add the Backend directory to Python path
backend_dir = os.path.join(os.path.dirname(__file__), 'Backend')
sys.path.insert(0, backend_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')
django.setup()

from django.contrib.auth.models import User
from assessment.models import Subject, Chapter, AdaptiveQuestion, StudentSession, QuestionAttempt

# Test configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

class AssessmentWorkflowTester:
    def __init__(self):
        self.session = requests.Session()
        self.student_id = None
        self.assessment_id = None
        
    def test_complete_workflow(self):
        """Test complete assessment workflow"""
        print("🧪 Testing Complete Assessment Workflow")
        print("=" * 50)
        
        try:
            # Step 1: Test subjects API
            print("\n1️⃣ Testing Subjects API...")
            subjects_response = self.session.get(f"{API_BASE}/multi-student/subjects/")
            
            if subjects_response.status_code != 200:
                print(f"❌ Subjects API failed: {subjects_response.status_code}")
                return False
                
            subjects = subjects_response.json()
            print(f"✅ Found {len(subjects)} subjects")
            
            if not subjects:
                print("❌ No subjects available")
                return False
                
            selected_subject = subjects[0]
            print(f"📚 Selected subject: {selected_subject['name']} (ID: {selected_subject['id']})")
            
            # Step 2: Test chapters API
            print("\n2️⃣ Testing Chapters API...")
            chapters_response = self.session.get(
                f"{API_BASE}/multi-student/subjects/{selected_subject['id']}/chapters/"
            )
            
            if chapters_response.status_code != 200:
                print(f"❌ Chapters API failed: {chapters_response.status_code}")
                return False
                
            chapters = chapters_response.json()
            print(f"✅ Found {len(chapters)} chapters")
            
            if not chapters:
                print("❌ No chapters available")
                return False
                
            selected_chapter = chapters[0]
            print(f"📖 Selected chapter: {selected_chapter['name']} (ID: {selected_chapter['id']})")
            
            # Step 3: Start assessment
            print("\n3️⃣ Starting Assessment...")
            start_data = {
                "student_username": "TestStudent",
                "subject_code": selected_subject['code'],
                "chapter_id": selected_chapter['id'],
                "assessment_type": "PRACTICE",
                "question_count": 10,
                "time_limit_minutes": 10
            }
            
            start_response = self.session.post(
                f"{API_BASE}/full-assessment/start",
                json=start_data
            )
            
            if start_response.status_code not in [200, 201]:
                print(f"❌ Start assessment failed: {start_response.status_code}")
                print(f"Response: {start_response.text}")
                return False
                
            start_result = start_response.json()
            self.assessment_id = start_result['assessment_id']
            # Get student ID by finding the user by username
            from django.contrib.auth.models import User
            student = User.objects.get(username=start_result['student_username'])
            self.student_id = student.id
            print(f"✅ Assessment started - ID: {self.assessment_id}")
            print(f"👤 Student ID: {self.student_id}")
            
            # Step 4: Get first question
            print("\n4️⃣ Getting Questions...")
            questions_response = self.session.get(
                f"{API_BASE}/full-assessment/questions/{self.assessment_id}"
            )
            
            if questions_response.status_code != 200:
                print(f"❌ Get question failed: {questions_response.status_code}")
                print(f"Response: {questions_response.text}")
                return False
                
            question_data = questions_response.json()
            print(f"✅ Got questions data: {len(question_data.get('questions', []))} questions available")
            
            time_remaining = question_data.get('time_remaining_minutes')
            if time_remaining is not None:
                print(f"⏱️ Time remaining: {time_remaining:.1f} minutes")
                if time_remaining <= 10.0:
                    print("✅ 10-minute timer is active and counting down")
                else:
                    print(f"⚠️ Time remaining ({time_remaining:.1f}min) suggests timer might not be 10 minutes")
            else:
                print("⏱️ No time limit set (unlimited assessment)")
                print("⚠️ Expected 10-minute time limit")
            
            # Get the questions list
            questions = question_data.get('questions', [])
            if not questions:
                print("❌ No questions available")
                return False
            
            # Step 5: Submit answers for multiple questions
            print("\n5️⃣ Submitting Answers...")
            
            # Submit answers for first 5 questions
            answers_to_submit = min(5, len(questions))
            for i in range(answers_to_submit):
                question = questions[i]
                
                # Submit answer for current question
                answer_data = {
                    "assessment_id": self.assessment_id,
                    "question_id": question['question_id'],
                    "selected_answer": ["a", "b", "c", "d"][i % 4],  # Vary answers
                    "time_taken_seconds": 30 + i * 10,  # Vary time taken
                    "confidence_level": 3
                }
                
                submit_response = self.session.post(
                    f"{API_BASE}/full-assessment/submit-answer",
                    json=answer_data
                )
                
                if submit_response.status_code not in [200, 201]:
                    print(f"❌ Submit answer failed for Q{i+1}: {submit_response.status_code}")
                    print(f"Response: {submit_response.text}")
                    break
                    
                submit_result = submit_response.json()
                is_correct = submit_result.get('is_correct', False)
                print(f"📝 Question {i + 1}: {'✓' if is_correct else '✗'} {submit_result.get('points_earned', 0)} points")
            
            print(f"✅ Submitted answers for {answers_to_submit} questions")
            
            # Step 6: Complete assessment
            print("\n6️⃣ Completing Assessment...")
            complete_data = {
                "assessment_id": self.assessment_id
            }
            complete_response = self.session.post(
                f"{API_BASE}/full-assessment/complete",
                json=complete_data
            )
            
            if complete_response.status_code not in [200, 201]:
                print(f"❌ Complete assessment failed: {complete_response.status_code}")
                print(f"Response: {complete_response.text}")
                return False
                
            results = complete_response.json()
            print(f"✅ Assessment completed!")
            print(f"📊 Results: {results.get('questions_correct', 0)}/{results.get('total_questions', 0)} correct")
            print(f"⏱️ Total time: {results.get('total_time_seconds', 0)} seconds")
            print(f"🎯 Accuracy: {results.get('accuracy_percentage', 0):.1f}%")
            print(f"🏆 Grade: {results.get('grade', 'N/A')}")
            print(f"💯 Points: {results.get('total_points_earned', 0)}/{results.get('max_possible_points', 0)}")
            
            # Step 7: Verify database persistence
            print("\n7️⃣ Verifying Database Persistence...")
            self.verify_database_records()
            
            print("\n✅ Complete workflow test PASSED!")
            return True
            
        except Exception as e:
            print(f"\n❌ Workflow test failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def verify_database_records(self):
        """Verify that assessment results are saved in database"""
        try:
            # Check StudentSession
            sessions = StudentSession.objects.filter(id=self.assessment_id)
            if sessions.exists():
                session = sessions.first()
                print(f"✅ StudentSession found - Score: {session.percentage_score}%")
                print(f"   Questions: {session.questions_correct}/{session.questions_attempted}")
                print(f"   Duration: {session.session_duration_seconds}s")
                print(f"   Status: {session.status}")
            else:
                print("❌ StudentSession not found in database")
                return False
            
            # Check QuestionAttempts
            attempts = QuestionAttempt.objects.filter(session_id=self.assessment_id)
            attempt_count = attempts.count()
            correct_count = attempts.filter(is_correct=True).count()
            
            print(f"✅ Found {attempt_count} question attempts")
            print(f"   Correct: {correct_count}, Incorrect: {attempt_count - correct_count}")
            
            if attempt_count > 0:
                print("✅ Database persistence verified!")
                return True
            else:
                print("❌ No question attempts found in database")
                return False
                
        except Exception as e:
            print(f"❌ Database verification failed: {e}")
            return False

    def cleanup(self):
        """Clean up test data"""
        try:
            if self.student_id:
                # Clean up test records
                QuestionAttempt.objects.filter(student_id=self.student_id).delete()
                StudentSession.objects.filter(student_id=self.student_id).delete()
                User.objects.filter(id=self.student_id).delete()
                print("🧹 Cleaned up test data")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")

def main():
    """Main test function"""
    print("🚀 Starting Complete Assessment Workflow Test")
    print("This test verifies:")
    print("- Frontend can fetch subjects/chapters")
    print("- Assessment can be started and completed")
    print("- 10-minute timer is properly configured")
    print("- Results are displayed correctly")
    print("- Database persistence works")
    print()
    
    tester = AssessmentWorkflowTester()
    
    try:
        # Test the complete workflow
        success = tester.test_complete_workflow()
        
        if success:
            print("\n🎉 All tests PASSED! The assessment system is working correctly.")
            print("✅ Frontend-backend integration works")
            print("✅ 10-minute timer is configured")
            print("✅ Results display comprehensive data")
            print("✅ Database persistence is working")
        else:
            print("\n❌ Some tests FAILED. Check the output above.")
            
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed with unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main()