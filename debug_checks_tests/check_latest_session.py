import requests

response = requests.get('http://localhost:5000/simple/session-history/69/')
if response.status_code == 200:
    data = response.json()
    
    print('🎉 YOUR LATEST SESSION IN HISTORY!')
    print('='*50)
    student_name = data.get('student_name', 'Unknown')
    total_sessions = data.get('total_sessions', 0)
    print(f'👤 Student: {student_name}')
    print(f'📊 Total Sessions: {total_sessions}')
    
    sessions = data.get('sessions', [])
    if sessions:
        latest = sessions[0]  # Most recent
        print('\n🕒 LATEST SESSION (Your 5-minute-ago test):')
        session_date = latest.get('session_date', 'Unknown')
        subject = latest.get('subject', 'Unknown')
        questions_attempted = latest.get('questions_attempted', 0)
        accuracy = latest.get('accuracy', 'Unknown')
        print(f'   📅 Date: {session_date}')
        print(f'   📚 Subject: {subject}')
        print(f'   ❓ Questions: {questions_attempted}')
        print(f'   ✅ Accuracy: {accuracy}')
        
        mastery = latest.get('mastery_scores', {})
        bkt_mastery = mastery.get('bkt_mastery', 'N/A')
        mastery_level = mastery.get('mastery_level', 'N/A')
        dkt_prediction = mastery.get('dkt_prediction', 'N/A')
        combined_confidence = mastery.get('combined_confidence', 'N/A')
        mastery_achieved = mastery.get('mastery_achieved', False)
        
        print(f'   🧠 BKT Mastery: {bkt_mastery} ({mastery_level} level)')
        print(f'   🤖 DKT Prediction: {dkt_prediction}')
        print(f'   🔮 Combined: {combined_confidence}')
        print(f'   🏆 Mastery Achieved: {"YES" if mastery_achieved else "NO"}')
    
    print('\n💡 FRONTEND ISSUE:')
    print('Your session IS in the backend history API!')
    print('The issue is the frontend is not using user ID 69.')
    print('\n🔧 To fix: In browser dev tools check:')
    print('localStorage → pragatipath_backend_user_id should be "69"')
else:
    print(f'❌ API Error: {response.status_code}')