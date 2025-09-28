import requests
import json

# Test backend API directly with 20 questions
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
    print(f'Backend API: Requested {data["requested_count"]}, Got {data["returned_count"]}')
    if data["returned_count"] != 20:
        print(f'❌ Backend API problem: Expected 20, got {data["returned_count"]}')
    else:
        print(f'✅ Backend API working correctly: Got exactly 20')
else:
    print(f'Backend API error: {response.status_code}')
    print(response.text)