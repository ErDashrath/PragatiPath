import requests
import json

# Check for duplicate IDs in backend response
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
    questions = data['questions']
    
    ids = [q['id'] for q in questions]
    unique_ids = set(ids)
    
    print(f'Backend returned: {len(questions)} questions')
    print(f'Unique IDs: {len(unique_ids)}')
    
    if len(unique_ids) != len(questions):
        print(f'❌ DUPLICATE IDs FOUND! {len(questions) - len(unique_ids)} duplicates')
        
        # Find duplicates
        seen = set()
        duplicates = []
        for question_id in ids:
            if question_id in seen:
                duplicates.append(question_id)
            seen.add(question_id)
        
        print(f'Duplicate IDs: {duplicates}')
    else:
        print('✅ All question IDs are unique')
        
    # Check if any questions have empty or malformed fields that might cause issues
    problematic = 0
    for i, q in enumerate(questions):
        if not q.get('id') or not q.get('question_text') or not q.get('options'):
            problematic += 1
            print(f'❌ Question {i+1}: Missing required fields - ID: {bool(q.get("id"))}, Text: {bool(q.get("question_text"))}, Options: {bool(q.get("options"))}')
    
    if problematic == 0:
        print('✅ All questions have required fields')
    else:
        print(f'❌ {problematic} questions have missing fields')

else:
    print(f'Backend error: {response.status_code}')