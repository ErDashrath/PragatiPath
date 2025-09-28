import requests
import json

# Test frontend API with debug by checking the raw response
response = requests.get(
    'http://localhost:5000/api/assessment/questions/quantitative_aptitude/1',
    params={'count': 20}
)

if response.status_code == 200:
    questions = response.json()
    print(f'Frontend proxy: Got {len(questions)} questions')
    
    # Check if any questions are missing options
    questions_without_options = 0
    for i, q in enumerate(questions):
        options = q.get('options', [])
        if not options or len(options) == 0:
            questions_without_options += 1
            print(f'  Question {i+1}: NO OPTIONS - {q.get("questionText", "Unknown")[:30]}...')
        elif len(options) < 4:
            print(f'  Question {i+1}: PARTIAL OPTIONS ({len(options)}/4) - {q.get("questionText", "Unknown")[:30]}...')
    
    print(f'Questions without proper options: {questions_without_options}')
    
    # Check the structure of first question
    if questions:
        q = questions[0]
        print(f'Sample question options: {q.get("options", [])}')
        print(f'Sample question option count: {len(q.get("options", []))}')
        print(f'Options type: {type(q.get("options", []))}')
else:
    print(f'Frontend error: {response.status_code} - {response.text}')