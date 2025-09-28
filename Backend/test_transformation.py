import requests
import json

# Test the exact transformation logic from frontend
def test_transformation(questions):
    transformed = []
    
    for i, q in enumerate(questions):
        try:
            # This is the exact logic from frontend routes.ts
            options = q.get('options', {})
            if isinstance(options, list):
                transformed_options = options
            else:
                transformed_options = list(options.values()) if options else []
            
            if len(transformed_options) != 4:
                print(f"❌ Question {i+1}: Bad options - Original: {options}, Transformed: {transformed_options}")
                continue  # Skip this question
                
            transformed_question = {
                'id': q['id'],
                'moduleId': q['subject'],
                'chapterId': 1,
                'questionText': q['question_text'],
                'options': transformed_options,
                'correctAnswer': 0,
                'difficulty': 3,  # Default
                'fundamentalType': "application",
                'questionType': q.get('question_type', 'multiple-choice')
            }
            
            transformed.append(transformed_question)
            
        except Exception as e:
            print(f"❌ Question {i+1}: Exception during transformation: {e}")
            continue
    
    return transformed

# Get backend data
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
    backend_questions = data['questions']
    
    print(f'Backend questions: {len(backend_questions)}')
    
    # Test transformation
    transformed = test_transformation(backend_questions)
    
    print(f'Transformed questions: {len(transformed)}')
    print(f'Lost in transformation: {len(backend_questions) - len(transformed)}')
    
    if len(transformed) == len(backend_questions):
        print('✅ No questions lost in transformation!')
    else:
        print('❌ Questions lost in transformation!')
        
else:
    print(f'Backend error: {response.status_code}')