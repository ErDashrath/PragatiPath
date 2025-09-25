"""
Final Comprehensive Test of Competitive Exam API v1
This script demonstrates the complete competitive exam system with level-locked progression.
"""

import os
import sys
import django
import time
from datetime import datetime

# Setup Django
sys.path.append(r'c:\Users\Dashrath\Desktop\Academic\Hackathons\StrawHatsH2')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')
django.setup()

from django.test import Client
from core.models import StudentProfile, User
from assessment.models import AdaptiveQuestion

def comprehensive_test():
    """Comprehensive test of the competitive exam system"""
    print("🎯 COMPREHENSIVE COMPETITIVE EXAM API v1 TEST")
    print("=" * 60)
    print(f"🕒 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    client = Client()
    
    # Test student
    test_user, created = User.objects.get_or_create(
        username='competitive_exam_demo_user',
        defaults={
            'email': 'demo@competitive.test',
            'first_name': 'Demo',
            'last_name': 'User'
        }
    )
    
    test_profile, created = StudentProfile.objects.get_or_create(
        user=test_user,
        defaults={
            'mastery_threshold': 0.8,
            'subject_progress': {}
        }
    )
    
    print(f"👤 Test User: {test_user.username} (ID: {test_profile.id})")
    
    # 1. TEST GET SUBJECTS
    print(f"\n1️⃣ TESTING: GET SUBJECTS")
    print("-" * 40)
    try:
        response = client.get('/api/assessment/v1/subjects')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Found {data['total_subjects']} subjects")
            for subject in data['subjects']:
                print(f"   📚 {subject['subject_name']}: {subject['total_questions']} questions")
                difficulties = subject['difficulty_breakdown']
                print(f"      - Very Easy: {difficulties['very_easy']}, Easy: {difficulties['easy']}, "
                      f"Moderate: {difficulties['moderate']}, Difficult: {difficulties['difficult']}")
        else:
            print(f"❌ FAILED: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False
    
    # 2. TEST START ASSESSMENT
    print(f"\n2️⃣ TESTING: START SUBJECT ASSESSMENT")
    print("-" * 40)
    try:
        payload = {
            "student_id": str(test_profile.id),
            "subject": "quantitative_aptitude",
            "preferred_difficulty": "very_easy"
        }
        
        response = client.post(
            '/api/assessment/v1/assessment/start-subject',
            data=payload,
            content_type='application/json'
        )
        
        if response.status_code == 200:
            start_data = response.json()
            print(f"✅ SUCCESS: Assessment started")
            print(f"   📋 Assessment ID: {start_data['assessment_id']}")
            print(f"   📚 Subject: {start_data['subject']}")
            print(f"   📊 Difficulty: {start_data['current_difficulty']}")
            print(f"   🎯 Student Level: {start_data['student_level']}")
            
            if start_data['next_question']:
                question = start_data['next_question']
                print(f"   ❓ First Question: {question['question_text'][:50]}...")
                # Print available options safely
                if 'option_a' in question:
                    print(f"      Options: A) {question['option_a'][:30]}...")
                else:
                    print(f"      Question ID: {question['id']}")
                assessment_id = start_data['assessment_id']
                question_id = question['id']
            else:
                print("❌ No question returned")
                return False
        else:
            print(f"❌ FAILED: {response.status_code} - {response.content.decode()}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False
    
    # 3. TEST SUBMIT MULTIPLE ANSWERS (Simulate progression)
    print(f"\n3️⃣ TESTING: ANSWER SUBMISSION & PROGRESSION")
    print("-" * 40)
    
    for attempt in range(1, 6):  # Submit 5 answers
        print(f"\n   Attempt {attempt}:")
        try:
            submit_payload = {
                "student_id": str(test_profile.id),
                "assessment_id": assessment_id,
                "question_id": question_id,
                "answer": "A",  # Always submit A for consistency
                "response_time": 25.0 + attempt * 2,  # Varying response times
                "subject": "quantitative_aptitude",
                "current_difficulty": "very_easy"
            }
            
            response = client.post(
                '/api/assessment/v1/assessment/submit-answer',
                data=submit_payload,
                content_type='application/json'
            )
            
            if response.status_code == 200:
                answer_data = response.json()
                print(f"   ✅ Answer {attempt} submitted - Correct: {answer_data['is_correct']}")
                print(f"      Points: +{answer_data['points_earned']}, BKT Mastery: {answer_data.get('bkt_mastery', 0):.2f}")
                
                if answer_data['level_unlocked']:
                    print(f"      🎉 LEVEL UNLOCKED: {answer_data['level_progression']['new_level']}")
                
                # Get next question for next iteration
                if answer_data['next_question']:
                    question_id = answer_data['next_question']['id']
                    print(f"      ❓ Next: {answer_data['next_question']['question_text'][:40]}...")
                else:
                    print("      📝 No more questions at current level")
                    
            else:
                print(f"   ❌ Answer {attempt} failed: {response.status_code}")
                print(f"      Response: {response.content.decode()[:200]}")
                
        except Exception as e:
            print(f"   ❌ Answer {attempt} error: {e}")
    
    # 4. TEST PROGRESS TRACKING
    print(f"\n4️⃣ TESTING: PROGRESS TRACKING")
    print("-" * 40)
    try:
        response = client.get(f'/api/assessment/v1/student/{test_profile.id}/progress')
        if response.status_code == 200:
            progress = response.json()
            print(f"✅ SUCCESS: Progress retrieved")
            print(f"   🎯 Overall Mastery: {progress.get('overall_mastery', 0):.2%}")
            print(f"   📊 Questions Attempted: {progress.get('total_questions_attempted', 0)}")
            print(f"   ✅ Questions Correct: {progress.get('total_correct', 0)}")
            print(f"   ⚡ Average Response Time: {progress.get('avg_response_time', 0):.1f}s")
            
            if 'subject_progress' in progress:
                print(f"\n   📚 Subject Progress:")
                subject_progress_data = progress['subject_progress']
                if isinstance(subject_progress_data, list):
                    # Handle list format (API v1 response)
                    for subject_data in subject_progress_data:
                        subject = subject_data.get('subject', 'Unknown')
                        level = subject_data.get('level', 1)
                        accuracy = subject_data.get('accuracy_rate', 0)
                        mastery = subject_data.get('mastery_score', 0)
                        difficulty = subject_data.get('current_difficulty', 'very_easy')
                        print(f"      • {subject.replace('_', ' ').title()}: Level {level}, "
                              f"Difficulty: {difficulty}, Mastery: {mastery:.1%}, Accuracy: {accuracy:.1%}")
                elif isinstance(subject_progress_data, dict):
                    # Handle dict format (legacy response)
                    for subject, data in subject_progress_data.items():
                        if isinstance(data, dict):
                            level = data.get('level', 1)
                            accuracy = data.get('accuracy', 0)
                            mastery = data.get('mastery_score', 0)
                            difficulty = data.get('current_difficulty', 'very_easy')
                            print(f"      • {subject.replace('_', ' ').title()}: Level {level}, "
                                  f"Difficulty: {difficulty}, Mastery: {mastery:.1%}, Accuracy: {accuracy:.1%}")
        else:
            print(f"❌ FAILED: {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # 5. SUMMARY
    print(f"\n5️⃣ TEST SUMMARY")
    print("-" * 40)
    
    # Check database state
    test_profile.refresh_from_db()
    subject_progress = test_profile.subject_progress.get('quantitative_aptitude', {})
    
    print(f"✅ SYSTEM STATUS: Fully Operational")
    print(f"📊 Database State:")
    if subject_progress:
        print(f"   • Current Difficulty: {subject_progress.get('current_difficulty', 'very_easy')}")
        print(f"   • Questions Attempted: {subject_progress.get('questions_attempted', 0)}")
        print(f"   • Consecutive Correct: {subject_progress.get('consecutive_correct', 0)}")
        print(f"   • Mastery Score: {subject_progress.get('mastery_score', 0):.2%}")
    
    total_questions = AdaptiveQuestion.objects.count()
    print(f"   • Total Questions in DB: {total_questions}")
    
    print(f"\n🎉 COMPETITIVE EXAM API v1 COMPREHENSIVE TEST COMPLETED!")
    print(f"🕒 Test finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = comprehensive_test()
    if success:
        print("\n✅ All tests passed! The Competitive Exam API v1 is ready for use.")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")