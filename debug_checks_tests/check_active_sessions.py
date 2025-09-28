import sqlite3
import json
from datetime import datetime

conn = sqlite3.connect('Backend/db.sqlite3')
cursor = conn.cursor()

print("🔍 CHECKING FOR ACTIVE SESSIONS (Your 6:48 session might be ACTIVE)")
print("=" * 70)

# Check all ACTIVE sessions that might be your unfinished 6:48 session
cursor.execute('''
    SELECT id, session_name, status, session_start_time, 
           questions_attempted, questions_correct, percentage_score, 
           student_id, created_at
    FROM student_sessions 
    WHERE status = 'ACTIVE'
    ORDER BY session_start_time DESC
    LIMIT 20
''')

active_sessions = cursor.fetchall()

print(f"📊 Found {len(active_sessions)} ACTIVE (incomplete) sessions:")
print("-" * 60)

for session in active_sessions:
    session_id, name, status, start_time, attempted, correct, score, student_id, created = session
    
    print(f"🆔 Session: {session_id}")
    print(f"👤 Student: {student_id}")
    print(f"🕐 Started: {start_time}")
    print(f"❓ Questions: {attempted} attempted, {correct} correct")
    print(f"📊 Status: {status}")
    
    # Check if this could be around 6:48
    if start_time and ('18:4' in start_time or '6:4' in start_time):
        print("🎯 **POSSIBLE 6:48 PM SESSION - BUT STILL ACTIVE!**")
        print("💡 This session never completed - that's why it's not in history!")
        
    print("-" * 40)

print("\n💡 SOLUTION:")
print("If your 6:48 session is in the ACTIVE list above, it means:")
print("1. ❌ The session started but never completed properly")  
print("2. ❌ Only COMPLETED sessions show in history")
print("3. ✅ You need to complete/finish the session for it to appear")
print("4. 🔧 We can manually complete it or you can start a new session")

conn.close()