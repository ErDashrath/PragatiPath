import requests
import json

# Test the simple frontend adaptive API directly with 20 questions
session_response = requests.post(
    'http://localhost:8000/start-session',
    headers={'Content-Type': 'application/json'},
    data=json.dumps({
        'student_name': 'Test User',
        'subject': 'quantitative_aptitude', 
        'question_count': 20
    })
)

if session_response.status_code == 200:
    session_data = session_response.json()
    print(f'Session created: {session_data["success"]}')
    print(f'Session ID: {session_data["session_id"]}')
    
    # Try to get 20 questions from this session
    session_id = session_data['session_id']
    question_count = 0
    
    for i in range(25):  # Try up to 25 times to get 20 questions
        question_response = requests.get(f'http://localhost:8000/get-question/{session_id}/')
        
        if question_response.status_code == 200:
            question_data = question_response.json()
            
            if question_data['success'] and not question_data.get('session_complete'):
                question_count += 1
                if question_count <= 3:  # Show first 3 questions
                    print(f'  Question {question_count}: {question_data["question_text"][:40]}...')
            else:
                print(f'Session completed after {question_count} questions')
                if 'session_complete' in question_data:
                    print(f'Reason: {question_data.get("message", "Unknown")}')
                break
        else:
            print(f'Question {i+1} failed: {question_response.status_code}')
            break
    
    print(f'Total questions retrieved: {question_count}')
    
    if question_count == 20:
        print('✅ Adaptive system can provide 20 questions')
    else:
        print(f'❌ Adaptive system limited to {question_count} questions')
else:
    print(f'Session creation failed: {session_response.status_code}')