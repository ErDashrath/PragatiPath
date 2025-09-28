#!/usr/bin/env python3
"""Check student IDs and map to usernames"""

import sqlite3
import os

def check_student_mapping():
    """Check the mapping between student IDs and usernames"""
    db_path = 'Backend/db.sqlite3'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get assessment data by student_id and map to username
        cursor.execute("""
            SELECT 
                es.student_id,
                u.username,
                u.first_name,
                u.last_name,
                COUNT(*) as session_count,
                SUM(CASE WHEN es.completed_at IS NOT NULL THEN 1 ELSE 0 END) as completed_count,
                MAX(es.completed_at) as latest_completion,
                GROUP_CONCAT(DISTINCT es.subject) as subjects
            FROM exam_sessions es
            JOIN auth_user u ON es.student_id = u.id
            GROUP BY es.student_id, u.username, u.first_name, u.last_name
            ORDER BY session_count DESC
        """)
        
        assessment_data = cursor.fetchall()
        
        print("🎯 ASSESSMENT DATA WITH USERNAME MAPPING:")
        print("-" * 100)
        print("ID | Username              | Name               | Total | Completed | Subjects")
        print("-" * 100)
        
        for data in assessment_data:
            student_id, username, first_name, last_name, total, completed, latest, subjects = data
            name = f"{first_name or ''} {last_name or ''}".strip() or "N/A"
            print(f"{student_id:<3} | {username:<20} | {name:<18} | {total:<5} | {completed:<9} | {subjects or 'N/A'}")
        
        if assessment_data:
            # Find the best candidate for the frontend
            best_candidate = max(assessment_data, key=lambda x: x[4])  # Most completed sessions
            print(f"\n🏆 BEST CANDIDATE FOR FRONTEND:")
            print(f"   Username: {best_candidate[1]}")
            print(f"   Name: {best_candidate[2]} {best_candidate[3]}")
            print(f"   Total sessions: {best_candidate[4]}")
            print(f"   Completed: {best_candidate[5]}")
            print(f"   Subjects: {best_candidate[7]}")
            
            return best_candidate[1]  # Return username
        else:
            print("❌ No assessment data found")
            return None
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        conn.close()

if __name__ == "__main__":
    username = check_student_mapping()
    
    if username:
        print(f"\n✅ RECOMMENDED ACTION:")
        print(f"   Update student-dashboard.tsx to use username: '{username}'")
        print(f"   This will restore access to the regular assessment history.")
    else:
        print(f"\n❌ No suitable username found for assessment history")