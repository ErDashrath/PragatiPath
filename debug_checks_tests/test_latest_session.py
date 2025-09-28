#!/usr/bin/env python3
"""
Test the detailed API with the latest session that has question attempts
"""
import requests
import json

def test_latest_session_with_attempts():
    # Use the session ID from our recent test
    session_id = '760378ee-8a57-448c-ae17-c5e0eb8c818a'  # From the last successful test
    username = 'student_dash'  # The user we created the session for
    url = f'http://127.0.0.1:8000/api/history/students/{username}/assessment/{session_id}'
    print(f'Testing URL: {url}')

    try:
        response = requests.get(url)
        print(f'Status Code: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print('✅ Response received successfully!')
            
            session_info = data['session_info']
            question_attempts = data['question_attempts']
            performance_analysis = data['performance_analysis']
            recommendations = data['recommendations']
            
            print(f"📊 Session: {session_info['session_name']} - Grade {session_info['grade']}")
            print(f"🎯 Accuracy: {session_info['percentage_score']:.1f}% ({session_info['questions_correct']}/{session_info['questions_attempted']})")
            print(f"⏱️  Duration: {session_info['session_duration_seconds']}s")
            print(f"❓ Questions: {len(question_attempts)} attempts")
            print(f"📈 Analysis: {len(performance_analysis['topics_performance'])} topics analyzed")
            print(f"💡 Recommendations: {len(recommendations)} suggestions")
            
            if question_attempts:
                correct_count = sum(1 for q in question_attempts if q['is_correct'])
                print(f"\n🔍 Question Breakdown:")
                print(f"   Correct Answers: {correct_count}/{len(question_attempts)}")
                
                # Show first few questions
                for i, q in enumerate(question_attempts[:3]):
                    status = "✓" if q['is_correct'] else "✗"
                    print(f"   Q{q['question_number']}: {status} {q['topic']} ({q['difficulty_level']}) - {q['time_spent_seconds']}s")
                
                # Show topics performance
                print(f"\n📊 Topics Performance:")
                for topic, perf in performance_analysis['topics_performance'].items():
                    print(f"   {topic}: {perf['correct']}/{perf['total']} ({perf['accuracy']:.1f}%)")
            
            return True
        else:
            print(f'❌ Error: {response.text}')
            return False
    except Exception as e:
        print(f'❌ Exception: {e}')
        return False

if __name__ == '__main__':
    test_latest_session_with_attempts()