#!/usr/bin/env python3
"""Check exam_sessions table for assessment data"""

import sqlite3
import os

def check_exam_sessions():
    """Check the exam_sessions table for assessment data"""
    db_path = 'Backend/db.sqlite3'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # First check table structure
        cursor.execute("PRAGMA table_info(exam_sessions);")
        columns = cursor.fetchall()
        
        print("📋 EXAM_SESSIONS TABLE STRUCTURE:")
        print("-" * 40)
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Check for data
        cursor.execute("SELECT COUNT(*) FROM exam_sessions;")
        total_count = cursor.fetchone()[0]
        print(f"\n📊 Total records: {total_count}")
        
        if total_count > 0:
            # Get sample data
            cursor.execute("SELECT * FROM exam_sessions LIMIT 5;")
            sample_data = cursor.fetchall()
            
            print(f"\n📋 SAMPLE DATA:")
            print("-" * 80)
            for row in sample_data:
                print(f"  {row}")
            
            # Get assessment data by student_username
            cursor.execute("""
                SELECT 
                    student_username,
                    COUNT(*) as count,
                    MAX(completed_at) as latest
                FROM exam_sessions
                WHERE student_username IS NOT NULL
                GROUP BY student_username
                ORDER BY count DESC
            """)
            
            assessment_data = cursor.fetchall()
            
            print(f"\n🎯 ASSESSMENT DATA BY USERNAME:")
            print("-" * 60)
            for data in assessment_data:
                print(f"  Username: {data[0]:<25} | Count: {data[1]:<3} | Latest: {data[2]}")
                
        else:
            print("❌ No data found in exam_sessions table")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_exam_sessions()