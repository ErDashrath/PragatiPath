#!/usr/bin/env python3
"""Check ExamSession table schema"""

import sqlite3
import os

def check_exam_session_schema():
    """Check the schema of exam_sessions table"""
    db_path = 'Backend/db.sqlite3'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get table schema
        cursor.execute("PRAGMA table_info(exam_sessions);")
        columns = cursor.fetchall()
        
        print("📋 EXAM_SESSIONS TABLE SCHEMA:")
        print("-" * 60)
        print("Column Name          | Type        | Null | Default | Primary")
        print("-" * 60)
        
        for col in columns:
            cid, name, data_type, notnull, default_value, pk = col
            null_str = "NO" if notnull else "YES"
            pk_str = "YES" if pk else "NO"
            default_str = str(default_value) if default_value is not None else "NULL"
            
            print(f"{name:<20} | {data_type:<10} | {null_str:<4} | {default_str:<7} | {pk_str}")
        
        # Check sample data to see the actual field values
        cursor.execute("SELECT assessment_mode, subject, questions_attempted FROM exam_sessions LIMIT 5;")
        samples = cursor.fetchall()
        
        print(f"\n📋 SAMPLE DATA:")
        print("-" * 60)
        print("Assessment Mode | Subject               | Questions")
        print("-" * 60)
        
        for sample in samples:
            mode, subject, questions = sample
            print(f"{mode:<15} | {subject:<20} | {questions}")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_exam_session_schema()