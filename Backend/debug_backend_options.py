import requests
import json

# Test backend API directly with 20 questions and check all options
response = requests.post(
    'http://localhost:8000/api/assessment/chapter-questions',
    headers={'Content-Type': 'application/json'},
    data=json.dumps({
        'subject': 'quantitative_aptitude',
        'chapter_id': 1,
        'count': 20
    })
)

if response.status_code == 200:
    data = response.json()
    print(f'Backend: Requested {data["requested_count"]}, Got {data["returned_count"]}')
    
    questions_with_bad_options = 0
    for i, q in enumerate(data['questions']):
        options = q.get('options', {})
        if not options:
            questions_with_bad_options += 1
            print(f'  Question {i+1}: NO OPTIONS - {q.get("question_text", "Unknown")[:30]}...')
        elif len(options) != 4:
            questions_with_bad_options += 1
            print(f'  Question {i+1}: BAD OPTIONS ({len(options)} keys) - {q.get("question_text", "Unknown")[:30]}...')
            print(f'    Options: {options}')
    
    print(f'Backend questions with bad options: {questions_with_bad_options}/20')
    
    if questions_with_bad_options == 0:
        print('✅ All backend questions have proper options')
    else:
        print('❌ Some backend questions have malformed options')
else:
    print(f'Backend error: {response.status_code} - {response.text}')