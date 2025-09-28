#!/usr/bin/env python3
import requests
import json

# Test the detailed assessment API
session_id = '26c48895-cf65-4a80-8920-1899d95e9984'
username = 'student'
url = f'http://127.0.0.1:8000/api/history/students/{username}/assessment/{session_id}'
print(f'Testing URL: {url}')

try:
    response = requests.get(url)
    print(f'Status Code: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print('✅ Response received successfully!')
        
        session_name = data['session_info']['session_name']
        grade = data['session_info']['grade']
        accuracy = data['session_info']['percentage_score']
        print(f'📊 Session: {session_name} - Grade {grade} ({accuracy:.1f}%)')
        
        questions_count = len(data['question_attempts'])
        print(f'❓ Questions: {questions_count} attempts')
        
        topics_count = len(data['performance_analysis']['topics_performance'])
        print(f'📈 Analysis: {topics_count} topics analyzed')
        
        recommendations_count = len(data['recommendations'])
        print(f'💡 Recommendations: {recommendations_count} suggestions')
        
        # Show first question details
        if questions_count > 0:
            first_q = data['question_attempts'][0]
            print(f"\n🔍 First Question Example:")
            print(f"   Topic: {first_q['topic']}")
            print(f"   Difficulty: {first_q['difficulty_level']}")
            print(f"   Correct: {first_q['is_correct']}")
            print(f"   Time: {first_q['time_spent_seconds']}s")
        
        # Show performance breakdown
        print(f"\n📊 Performance Analysis:")
        for topic, perf in data['performance_analysis']['topics_performance'].items():
            print(f"   {topic}: {perf['correct']}/{perf['total']} ({perf['accuracy']:.1f}%)")
            
    else:
        print(f'❌ Error: {response.text}')
except Exception as e:
    print(f'❌ Exception: {e}')