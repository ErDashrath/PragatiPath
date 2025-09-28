import requests
import json

response = requests.post(
    'http://localhost:8000/api/assessment/chapter-questions',
    headers={'Content-Type': 'application/json'},
    data=json.dumps({
        'subject': 'quantitative_aptitude',
        'chapter_id': 1,
        'count': 10
    })
)

print(f'Status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    print(f'Success: {data["success"]}')
    print(f'Requested count: {data["requested_count"]}')
    print(f'Returned count: {data["returned_count"]}')
    
    if data["returned_count"] != data["requested_count"]:
        print(f'❌ MISMATCH! Requested {data["requested_count"]} but got {data["returned_count"]}')
    else:
        print(f'✅ SUCCESS! Got exactly {data["returned_count"]} questions as requested')
    
    if data['questions']:
        for i, q in enumerate(data['questions'][:3]):  # Show first 3 questions
            print(f'Question {i+1}: {q["question_text"][:30]}... Options: {len(q["options"])} choices')
else:
    print(f'Error: {response.text}')