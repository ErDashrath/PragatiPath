#!/usr/bin/env python3
"""Check student_sessions table structure"""

import sqlite3
import os

def check_student_sessions_schema():
    """Check the student_sessions table structure"""
    db_path = 'Backend/db.sqlite3'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check table structure
        cursor.execute("PRAGMA table_info(student_sessions);")
        columns = cursor.fetchall()
        
        print("📋 STUDENT_SESSIONS TABLE STRUCTURE:")
        print("-" * 40)
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Check for data
        cursor.execute("SELECT COUNT(*) FROM student_sessions;")
        total_count = cursor.fetchone()[0]
        print(f"\n📊 Total records: {total_count}")
        
        if total_count > 0:
            # Get sample data
            cursor.execute("SELECT * FROM student_sessions LIMIT 3;")
            sample_data = cursor.fetchall()
            
            print(f"\n📋 SAMPLE DATA:")
            print("-" * 80)
            for i, row in enumerate(sample_data):
                print(f"  Row {i+1}: {row}")
                
        else:
            print("❌ No data found in student_sessions table")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_student_sessions_schema()