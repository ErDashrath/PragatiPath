import requests
import json
from datetime import datetime

print('🔍 CHECKING LATEST SESSIONS FOR YOUR 7:25 AM TEST...')
print('=' * 60)

try:
    response = requests.get('http://localhost:8000/simple/session-history/69/')
    if response.status_code == 200:
        data = response.json()
        print(f'✅ Found {data.get("total_sessions", 0)} total sessions')
        
        sessions = data.get('sessions', [])
        if sessions:
            print(f'\n📅 LATEST SESSIONS (checking for 7:25 AM test):')
            for i, session in enumerate(sessions[:5]):
                session_time = session.get('session_date', 'Unknown')
                subject = session.get('subject', 'Unknown')
                status = session.get('completion_status', 'Unknown')
                questions = session.get('questions_attempted', 0)
                accuracy = session.get('accuracy_percentage', 0)
                mastery = session.get('mastery_data', {})
                
                try:
                    if 'T' in session_time:
                        dt = datetime.fromisoformat(session_time.replace('Z', '+00:00'))
                        local_time = dt.strftime('%I:%M %p')
                        print(f'  {i+1}. {local_time} - {subject} - {status} - {questions}Q - {accuracy:.1f}%')
                        if mastery and 'bkt_mastery' in mastery:
                            print(f'      🧠 BKT Mastery: {mastery["bkt_mastery"]:.1f}%')
                    else:
                        print(f'  {i+1}. {session_time} - {subject} - {status} - {questions}Q - {accuracy:.1f}%')
                except Exception as e:
                    print(f'  {i+1}. {session_time} - {subject} - {status} - {questions}Q - {accuracy:.1f}%')
        else:
            print('❌ No sessions found')
    else:
        print(f'❌ API Error: {response.status_code}')
        print(f'Response: {response.text}')
        
except Exception as e:
    print(f'❌ Connection Error: {e}')
    print('Make sure Django backend is running on port 8000')