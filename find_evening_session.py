import sqlite3
import json
from datetime import datetime

conn = sqlite3.connect('Backend/db.sqlite3')
cursor = conn.cursor()

print("🔍 SEARCHING FOR EVENING SESSIONS TODAY (6:48 PM)")
print("=" * 60)

# Search for any sessions today between 6 PM and 7 PM
cursor.execute('''
    SELECT id, session_name, status, session_start_time, session_end_time,
           questions_attempted, questions_correct, percentage_score, 
           student_id, created_at, updated_at
    FROM student_sessions 
    WHERE (session_start_time LIKE '2025-09-27 18:%' OR 
           session_start_time LIKE '2025-09-27 6:%' OR
           created_at LIKE '2025-09-27 18:%' OR
           created_at LIKE '2025-09-27 6:%')
    ORDER BY session_start_time DESC
''')

evening_sessions = cursor.fetchall()

if evening_sessions:
    print(f"📊 Found {len(evening_sessions)} evening sessions today:")
    print("-" * 50)
    
    for session in evening_sessions:
        session_id, name, status, start_time, end_time, attempted, correct, score, student_id, created, updated = session
        
        print(f"🆔 Session: {session_id}")
        print(f"👤 Student: {student_id}")
        print(f"🕐 Start: {start_time}")
        print(f"🏁 End: {end_time}")
        print(f"❓ Questions: {attempted} attempted, {correct} correct")
        print(f"📊 Status: {status}")
        print(f"📈 Score: {score}%")
        
        if '18:48' in str(start_time) or '6:48' in str(start_time):
            print("🎯 **THIS IS YOUR 6:48 PM SESSION!**")
        
        print("-" * 50)
else:
    print("❌ No evening sessions found for today")

# Check what student IDs you might be using
print("\n🔍 Let's see which student ID you should check:")
cursor.execute('''
    SELECT DISTINCT student_id, COUNT(*) as session_count
    FROM student_sessions 
    WHERE DATE(session_start_time) = '2025-09-27'
    GROUP BY student_id
    ORDER BY session_count DESC
    LIMIT 10
''')

student_activity = cursor.fetchall()
print("👥 Most active students today:")
for student_id, count in student_activity:
    print(f"   Student {student_id}: {count} sessions")

print(f"\n💡 Try checking history for these student IDs in the frontend!")

conn.close()