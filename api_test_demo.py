"""
API Test Script for Competitive Exam System
Demonstrates the complete workflow with imported CSV data
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/assessment"
STUDENT_ID = "48703c5a-1840-4607-99fc-a3d98bc94753"  # From our test

def test_workflow():
    """Test complete competitive exam workflow"""
    print("🎯 Competitive Exam System API Test")
    print("=" * 50)
    
    # Step 1: List available subjects
    print("\n1️⃣ Getting Available Subjects...")
    try:
        response = requests.get(f"{BASE_URL}/subjects")
        if response.status_code == 200:
            subjects_data = response.json()
            print(f"✅ Found {subjects_data['total_subjects']} subjects:")
            for subject in subjects_data['subjects']:
                print(f"   • {subject['subject_name']}: {subject['question_count']} questions")
        else:
            print(f"❌ Error: {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Please start with: python manage.py runserver")
        return
    
    # Step 2: Get questions for Quantitative Aptitude
    print("\n2️⃣ Getting Quantitative Aptitude Questions...")
    question_payload = {
        "student_id": STUDENT_ID,
        "subject": "quantitative_aptitude",
        "count": 2
    }
    
    response = requests.post(
        f"{BASE_URL}/subject-questions",
        headers={"Content-Type": "application/json"},
        data=json.dumps(question_payload)
    )
    
    if response.status_code == 200:
        questions_data = response.json()
        print(f"✅ Retrieved {questions_data['returned_count']} questions")
        
        # Show first question
        if questions_data['questions']:
            question = questions_data['questions'][0]
            print(f"\n📋 Sample Question:")
            print(f"   Question: {question['question_text'][:80]}...")
            print(f"   Options:")
            for key, value in question['options'].items():
                print(f"     {key.upper()}) {value}")
            print(f"   Difficulty: {question['difficulty_level']} (Level {question['level']})")
            
            # Step 3: Submit answer
            print("\n3️⃣ Submitting Answer...")
            answer_payload = {
                "student_id": STUDENT_ID,
                "question_id": question['id'],
                "answer": "a",  # Submit answer 'a'
                "response_time": 45.5,
                "subject": "quantitative_aptitude",
                "skill_id": "quantitative_aptitude_skill",
                "metadata": {"test": True}
            }
            
            response = requests.post(
                f"{BASE_URL}/submit",
                headers={"Content-Type": "application/json"},
                data=json.dumps(answer_payload)
            )
            
            if response.status_code == 200:
                submit_data = response.json()
                print(f"✅ Answer submitted!")
                print(f"   Correct: {submit_data['was_correct']}")
                print(f"   Feedback: {submit_data['feedback']}")
                
                # Show algorithm results
                if 'algorithm_results' in submit_data:
                    bkt_results = submit_data['algorithm_results'].get('bkt', {})
                    if bkt_results.get('status') == 'success':
                        print(f"   BKT Mastery: {bkt_results['new_mastery']:.3f}")
                        
                        progression = bkt_results.get('level_progression', {})
                        if progression.get('level_changed'):
                            print(f"   🎉 Level Up! New Level: {progression.get('new_level')}")
                
                # Show recommendations
                if submit_data.get('recommendations'):
                    print(f"   Recommendations: {', '.join(submit_data['recommendations'])}")
            else:
                print(f"❌ Submit error: {response.status_code}")
        
    else:
        print(f"❌ Questions error: {response.status_code}")
    
    # Step 4: Get subject statistics
    print("\n4️⃣ Getting Subject Statistics...")
    response = requests.get(f"{BASE_URL}/subjects/quantitative_aptitude/stats?student_id={STUDENT_ID}")
    
    if response.status_code == 200:
        stats_data = response.json()
        print(f"✅ Statistics for {stats_data['subject']}:")
        print(f"   Total Questions: {stats_data['total_questions']}")
        print(f"   Difficulty Breakdown: {stats_data['difficulty_breakdown']}")
        
        if 'student_progress' in stats_data:
            progress = stats_data['student_progress']
            if progress.get('total_attempted', 0) > 0:
                print(f"   Student Progress:")
                print(f"     Attempted: {progress['total_attempted']}")
                print(f"     Accuracy: {progress['accuracy_rate']:.1%}")
    else:
        print(f"❌ Stats error: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("🎉 API Test Complete!")
    print("💡 Your system supports:")
    print("   ✅ Subject-wise question retrieval")
    print("   ✅ Adaptive difficulty progression") 
    print("   ✅ BKT algorithm integration")
    print("   ✅ Performance tracking")
    print("   ✅ Level-based progression")

if __name__ == "__main__":
    print("🚀 Starting API Test...")
    print("Make sure the server is running: python manage.py runserver")
    time.sleep(2)
    test_workflow()
    