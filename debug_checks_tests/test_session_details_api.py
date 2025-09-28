#!/usr/bin/env python3
"""
Test the new session-details API endpoint to get real question attempts
for adaptive learning sessions
"""

import requests
import json

def test_session_details_api():
    print("🧪 TESTING NEW SESSION-DETAILS API ENDPOINT")
    print("=" * 55)
    
    # Get a sample session ID from the session history first
    print("\n📋 Step 1: Getting recent session ID...")
    try:
        response = requests.get("http://localhost:8000/simple/session-history/69/")
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('sessions'):
                latest_session = data['sessions'][0]
                session_id = latest_session['session_id']
                subject = latest_session['subject']
                print(f"✅ Found session: {session_id}")
                print(f"📚 Subject: {subject}")
                print(f"❓ Questions: {latest_session['questions_attempted']}")
                
                # Now test the new session-details endpoint
                print(f"\n📋 Step 2: Getting detailed session data...")
                detail_response = requests.get(f"http://localhost:8000/simple/session-details/{session_id}/")
                
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    if detail_data.get('success'):
                        print("✅ Session details API working!")
                        
                        session_info = detail_data.get('session_info', {})
                        question_attempts = detail_data.get('question_attempts', [])
                        performance_analysis = detail_data.get('performance_analysis', {})
                        
                        print(f"\n📊 SESSION INFO:")
                        print(f"  🎯 Session Name: {session_info.get('session_name')}")
                        print(f"  📚 Subject: {session_info.get('subject_name')}")
                        print(f"  ✅ Questions Correct: {session_info.get('questions_correct')}/{session_info.get('questions_attempted')}")
                        print(f"  📈 Accuracy: {session_info.get('percentage_score', 0):.1f}%")
                        print(f"  🏆 Grade: {session_info.get('grade')}")
                        
                        print(f"\n❓ QUESTION ATTEMPTS ({len(question_attempts)} questions):")
                        for i, attempt in enumerate(question_attempts[:3]):  # Show first 3
                            print(f"  Q{attempt.get('question_number', i+1)}: {attempt.get('question_text', '')[:50]}...")
                            print(f"    Student Answer: {attempt.get('student_answer')} | Correct: {attempt.get('correct_answer')}")
                            print(f"    ✅ Correct: {attempt.get('is_correct')} | Time: {attempt.get('time_spent_seconds')}s")
                            print()
                        
                        if len(question_attempts) > 3:
                            print(f"  ... and {len(question_attempts) - 3} more questions")
                        
                        print(f"\n📈 PERFORMANCE ANALYSIS:")
                        strengths = performance_analysis.get('strengths', [])
                        improvement_areas = performance_analysis.get('improvement_areas', [])
                        print(f"  💪 Strengths: {', '.join(strengths)}")
                        print(f"  📚 Improvement Areas: {', '.join(improvement_areas) if improvement_areas else 'None - Great job!'}")
                        
                        mastery_data = detail_data.get('mastery_data', {})
                        print(f"\n🧠 MASTERY DATA:")
                        print(f"  🎯 BKT Mastery: {mastery_data.get('bkt_mastery', 0):.1f}%")
                        print(f"  🏆 Mastery Level: {mastery_data.get('mastery_level')}")
                        print(f"  ✅ Mastery Achieved: {mastery_data.get('mastery_achieved')}")
                        
                        print(f"\n🎉 SUCCESS! Real question data available for adaptive sessions!")
                        return True
                        
                    else:
                        print(f"❌ Session details API returned failure: {detail_data}")
                        return False
                else:
                    print(f"❌ Session details API failed: {detail_response.status_code}")
                    print(f"Response: {detail_response.text}")
                    return False
            else:
                print("❌ No sessions found in history")
                return False
        else:
            print(f"❌ Session history API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_session_details_api()
    if success:
        print(f"\n🚀 READY! Frontend will now show REAL question attempts for adaptive sessions!")
        print(f"💡 Click Details button on any adaptive session to see actual questions answered!")
    else:
        print(f"\n⚠️ Issue with session details API - check backend is running on port 8000")