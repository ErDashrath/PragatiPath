#!/usr/bin/env python3
"""Check for completed sessions and question attempts"""

import sqlite3
import os

def check_completed_sessions():
    """Check for completed sessions with actual data"""
    db_path = 'Backend/db.sqlite3'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check for completed student_sessions
        cursor.execute("""
            SELECT 
                ss.id,
                ss.session_type,
                ss.session_name,
                ss.status,
                ss.questions_attempted,
                ss.questions_correct,
                ss.percentage_score,
                ss.session_end_time,
                ss.student_id
            FROM student_sessions ss
            WHERE ss.status = 'COMPLETED'
            ORDER BY ss.updated_at DESC
            LIMIT 10
        """)
        
        completed_sessions = cursor.fetchall()
        
        print("📊 COMPLETED STUDENT SESSIONS:")
        print("-" * 80)
        if completed_sessions:
            for session in completed_sessions:
                session_id, session_type, name, status, attempted, correct, score, end_time, student_id = session
                print(f"  ID: {session_id}")
                print(f"     Name: {name} | Type: {session_type} | Status: {status}")
                print(f"     Questions: {correct}/{attempted} | Score: {score}% | Student: {student_id}")
                print(f"     Completed: {end_time}")
                print()
        else:
            print("  ❌ No completed sessions found")
        
        # Check question_attempts table structure
        print("\n📋 QUESTION_ATTEMPTS TABLE STRUCTURE:")
        print("-" * 40)
        cursor.execute("PRAGMA table_info(question_attempts);")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Check for question attempts data
        cursor.execute("SELECT COUNT(*) FROM question_attempts;")
        attempts_count = cursor.fetchone()[0]
        print(f"\n📊 Total question attempts: {attempts_count}")
        
        if attempts_count > 0:
            # Get sample question attempts
            cursor.execute("""
                SELECT 
                    qa.id,
                    qa.session_id,
                    qa.question_number,
                    qa.is_correct,
                    qa.difficulty_level,
                    qa.student_username
                FROM question_attempts qa
                LIMIT 5
            """)
            
            sample_attempts = cursor.fetchall()
            
            print(f"\n📋 SAMPLE QUESTION ATTEMPTS:")
            print("-" * 60)
            for attempt in sample_attempts:
                attempt_id, session_id, q_num, correct, difficulty, username = attempt
                print(f"  Session: {session_id} | Q{q_num} | {'✅' if correct else '❌'} | {difficulty} | {username}")
        
        return completed_sessions
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        conn.close()

if __name__ == "__main__":
    check_completed_sessions()