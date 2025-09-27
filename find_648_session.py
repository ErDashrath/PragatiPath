import sqlite3
import json
from datetime import datetime, timedelta

conn = sqlite3.connect('Backend/db.sqlite3')
cursor = conn.cursor()

print("🔍 SEARCHING FOR YOUR 6:48 PM SESSION TODAY")
print("=" * 60)

# Get today's date
today = datetime.now().date()
print(f"📅 Today's date: {today}")

# Check all sessions from today around 6:48 PM (18:48)
cursor.execute('''
    SELECT id, session_name, status, session_start_time, session_end_time, 
           questions_attempted, questions_correct, percentage_score, 
           session_config, student_id, created_at, updated_at
    FROM student_sessions 
    WHERE DATE(session_start_time) = ? OR DATE(created_at) = ?
    ORDER BY session_start_time DESC
''', (today, today))

sessions = cursor.fetchall()

print(f"📊 Found {len(sessions)} sessions from today:")
print("-" * 50)

for session in sessions:
    session_id, name, status, start_time, end_time, attempted, correct, score, config, student_id, created, updated = session
    
    # Parse the timestamps to check for 6:48 PM time
    if start_time:
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00').replace('+00:00', ''))
        start_time_str = start_dt.strftime('%H:%M:%S')  # Get time part
    else:
        start_dt = None
        start_time_str = "Unknown"
    
    print(f"🆔 Session ID: {session_id}")
    print(f"👤 Student ID: {student_id}")
    print(f"📛 Name: {name}")
    print(f"📊 Status: {status}")
    print(f"🕐 Start Time: {start_time_str} ({start_time})")
    print(f"❓ Questions: {attempted} attempted, {correct} correct")
    print(f"📈 Score: {score}%")
    
    # Check if this is around 6:48 PM
    if start_dt and start_dt.hour == 18 and 45 <= start_dt.minute <= 50:
        print("🎯 **THIS MIGHT BE YOUR 6:48 PM SESSION!**")
        
        # Check mastery data
        if config:
            try:
                config_data = json.loads(config)
                final_mastery = config_data.get('final_mastery', {})
                if final_mastery:
                    print(f"🧠 Mastery Data Found:")
                    print(f"   BKT: {final_mastery.get('bkt_mastery', 'N/A')}%")
                    print(f"   DKT: {final_mastery.get('dkt_mastery', 'N/A')}%")
                    print(f"   Combined: {final_mastery.get('combined_confidence', 'N/A')}%")
            except:
                print("⚠️ Could not parse session config")
    
    print("-" * 50)

# Also check for any sessions with similar timing patterns
print(f"\n🔍 Checking for sessions around 18:48 (6:48 PM) timing...")
cursor.execute('''
    SELECT id, session_start_time, student_id, questions_attempted, percentage_score, status
    FROM student_sessions 
    WHERE session_start_time LIKE '%18:4%' OR session_start_time LIKE '%6:4%'
    ORDER BY session_start_time DESC
    LIMIT 10
''')

evening_sessions = cursor.fetchall()
for session in evening_sessions:
    print(f"🕐 {session[1]} - Student {session[2]} - {session[3]} questions - {session[4]}% - {session[5]}")

conn.close()