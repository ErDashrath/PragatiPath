import requests
import json

# Test the frontend proxy endpoint that the assessment interface uses
response = requests.get(
    'http://localhost:5000/api/assessment/questions/quantitative_aptitude/1',
    params={'count': 15}  # Request exactly 15 questions
)

print(f'Frontend Proxy Status: {response.status_code}')
if response.status_code == 200:
    questions = response.json()
    print(f'✅ SUCCESS! Frontend returned {len(questions)} questions')
    
    if len(questions) == 15:
        print(f'🎉 PERFECT! Got exactly 15 questions as requested')
    else:
        print(f'❌ MISMATCH! Requested 15 but got {len(questions)} questions')
    
    # Check if questions have proper structure
    if questions:
        q = questions[0]
        print(f'Sample question structure:')
        print(f'  - ID: {q.get("id", "missing")}')
        print(f'  - Text: {q.get("questionText", "missing")[:40]}...')
        print(f'  - Options: {len(q.get("options", []))} choices')
        print(f'  - Difficulty: {q.get("difficulty", "missing")}')
        
        # Count questions with proper options
        questions_with_options = sum(1 for q in questions if q.get("options") and len(q.get("options", [])) > 0)
        print(f'  - Questions with options: {questions_with_options}/{len(questions)}')
        
        if questions_with_options != len(questions):
            print(f'❌ WARNING: {len(questions) - questions_with_options} questions missing options!')
        else:
            print(f'✅ All questions have proper options')
            
else:
    print(f'Error: {response.text}')

# Test with different counts
for count in [10, 15, 20]:
    response = requests.get(
        'http://localhost:5000/api/assessment/questions/quantitative_aptitude/1',
        params={'count': count}
    )
    
    if response.status_code == 200:
        questions = response.json()
        result = "✅" if len(questions) == count else "❌"
        print(f'{result} Count {count}: Got {len(questions)} questions')
    else:
        print(f'❌ Count {count}: Error {response.status_code}')