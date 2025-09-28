"""
Test script for enhanced adaptive learning API with mastery tracking
Run: python test_adaptive_mastery_api.py
"""

import requests
import json
import time
from datetime import datetime

# Configuration - Using your actual quantitative aptitude subject
BASE_URL = "http://localhost:8000/api/v1/adaptive"
SESSION_ID = f"test_session_{int(time.time())}"
USER_ID = 83  # Test user from initialization
SUBJECT_ID = 5  # Quantitative Aptitude from your system
CHAPTER_ID = None  # Will test without specific chapter first

def test_adaptive_api():
    """Test the complete adaptive learning workflow"""
    
    print("🚀 Testing Enhanced Adaptive Learning API with Mastery Tracking")
    print("=" * 60)
    
    # Test 1: Get Next Question
    print("\n📝 Test 1: Getting Next Adaptive Question")
    
    question_data = {
        "session_id": SESSION_ID,
        "user_id": USER_ID,
        "subject_id": SUBJECT_ID,
        "chapter_id": CHAPTER_ID
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/next-question/",
            json=question_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Successfully got next question!")
            print(f"Question: {data.get('question', {}).get('question_text', 'N/A')}")
            print(f"Difficulty: {data.get('question', {}).get('difficulty', 'N/A')}")
            print(f"Current Mastery: {data.get('mastery_status', {}).get('current_score', 0):.2%}")
            print(f"Mastery Level: {data.get('mastery_status', {}).get('mastery_level', 'N/A')}")
            
            # Store question for answer submission
            question_id = data.get('question', {}).get('id')
            correct_answer = "Paris"  # Mock answer
            
            if question_id:
                # Test 2: Submit Answer
                print(f"\n✍️ Test 2: Submitting Answer for Question {question_id}")
                
                answer_data = {
                    "session_id": SESSION_ID,
                    "question_id": question_id,
                    "answer": correct_answer,
                    "response_time": 15.5
                }
                
                answer_response = requests.post(
                    f"{BASE_URL}/submit-answer/",
                    json=answer_data,
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"Status Code: {answer_response.status_code}")
                
                if answer_response.status_code == 200:
                    answer_data = answer_response.json()
                    print("✅ Successfully submitted answer!")
                    print(f"Correct: {answer_data.get('result', {}).get('correct', False)}")
                    print(f"Points: {answer_data.get('result', {}).get('points_earned', 0)}")
                    print(f"Updated Mastery: {answer_data.get('mastery_update', {}).get('overall_mastery', 0):.2%}")
                    print(f"Questions Attempted: {answer_data.get('session_stats', {}).get('questions_attempted', 0)}")
                    print(f"Current Streak: {answer_data.get('session_stats', {}).get('current_streak', 0)}")
                else:
                    print(f"❌ Error submitting answer: {answer_response.text}")
            
        else:
            print(f"❌ Error getting question: {response.text}")
    
    except requests.ConnectionError:
        print("❌ Connection Error: Make sure Django server is running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False
    
    # Test 3: Real-time Mastery Status
    print(f"\n📊 Test 3: Getting Real-time Mastery Status")
    
    try:
        mastery_response = requests.get(
            f"{BASE_URL}/mastery/status/",
            params={"session_id": SESSION_ID}
        )
        
        print(f"Status Code: {mastery_response.status_code}")
        
        if mastery_response.status_code == 200:
            mastery_data = mastery_response.json()
            print("✅ Successfully retrieved mastery status!")
            print(f"Overall Mastery: {mastery_data.get('mastery_status', {}).get('overall_mastery', 0):.2%}")
            print(f"Mastery Achieved: {mastery_data.get('mastery_status', {}).get('mastery_achieved', False)}")
            print(f"Session Duration: {mastery_data.get('session_summary', {}).get('duration_minutes', 0)} minutes")
            print(f"Learning Velocity: {mastery_data.get('session_summary', {}).get('learning_velocity', 0)} q/min")
        else:
            print(f"❌ Error getting mastery status: {mastery_response.text}")
    
    except Exception as e:
        print(f"❌ Error getting mastery status: {str(e)}")
    
    # Test 4: Mastery Dashboard
    print(f"\n📈 Test 4: Getting Mastery Dashboard")
    
    try:
        dashboard_response = requests.get(
            f"{BASE_URL}/mastery/dashboard/",
            params={
                "user_id": USER_ID,
                "subject_id": SUBJECT_ID,
                "time_range": 7
            }
        )
        
        print(f"Status Code: {dashboard_response.status_code}")
        
        if dashboard_response.status_code == 200:
            dashboard_data = dashboard_response.json()
            print("✅ Successfully retrieved mastery dashboard!")
            
            student_summary = dashboard_data.get('dashboard', {}).get('student_summary', {})
            print(f"Total Sessions: {student_summary.get('total_sessions', 0)}")
            print(f"Subjects Studied: {student_summary.get('subjects_studied', 0)}")
            print(f"Average Mastery: {student_summary.get('average_mastery', 0):.2%}")
            
            metadata = dashboard_data.get('metadata', {})
            print(f"Mastery Records: {metadata.get('total_mastery_records', 0)}")
        else:
            print(f"❌ Error getting dashboard: {dashboard_response.text}")
    
    except Exception as e:
        print(f"❌ Error getting dashboard: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎯 Test Summary:")
    print(f"Session ID: {SESSION_ID}")
    print(f"User ID: {USER_ID}")
    print(f"Subject ID: {SUBJECT_ID}")
    print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n✨ Enhanced Adaptive Learning API Test Complete!")
    
    return True


def test_error_handling():
    """Test API error handling"""
    
    print("\n🔍 Testing Error Handling")
    
    # Test invalid session
    invalid_data = {
        "session_id": "invalid_session",
        "user_id": 999999,
        "subject_id": 999999
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/next-question/",
            json=invalid_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 404:
            print("✅ Proper error handling for invalid references")
        else:
            print(f"⚠️ Unexpected response for invalid data: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error testing error handling: {str(e)}")


def generate_integration_example():
    """Generate integration example for developers"""
    
    print("\n📚 Generating Frontend Integration Example")
    
    js_example = f'''
// Frontend Integration Example
const adaptiveLearning = {{
  sessionId: "{SESSION_ID}",
  userId: {USER_ID},
  subjectId: {SUBJECT_ID},
  
  async getNextQuestion() {{
    const response = await fetch('/api/v1/adaptive/next-question/', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify({{
        session_id: this.sessionId,
        user_id: this.userId,
        subject_id: this.subjectId
      }})
    }});
    
    const data = await response.json();
    this.displayQuestion(data.question);
    this.updateMastery(data.mastery_status);
  }},
  
  async submitAnswer(questionId, answer, responseTime) {{
    const response = await fetch('/api/v1/adaptive/submit-answer/', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify({{
        session_id: this.sessionId,
        question_id: questionId,
        answer: answer,
        response_time: responseTime
      }})
    }});
    
    const data = await response.json();
    this.showResult(data.result);
    this.updateMastery(data.mastery_update);
  }}
}};

// Start adaptive learning
adaptiveLearning.getNextQuestion();
'''
    
    print("💻 JavaScript Integration Example:")
    print(js_example)


if __name__ == "__main__":
    # Run comprehensive API tests
    success = test_adaptive_api()
    
    if success:
        test_error_handling()
        generate_integration_example()
    
    print("\n🎉 All tests completed!")
    print("📋 Next Steps:")
    print("1. Integrate these endpoints with your frontend")
    print("2. Run database migrations: python manage.py migrate")
    print("3. Test with real user sessions")
    print("4. Monitor mastery progression in real-time")
    print("5. Use analytics for educational insights")