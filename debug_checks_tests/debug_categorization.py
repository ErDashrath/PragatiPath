#!/usr/bin/env python3
"""Debug the assessment data and categorization"""

import sqlite3
import os

def debug_assessment_data():
    """Debug the actual assessment data in the database"""
    print("=" * 60)
    print("DEBUGGING ASSESSMENT DATA")
    print("=" * 60)
    
    db_path = 'Backend/db.sqlite3'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check exam_sessions for user ID 5 (test_ai_student_1)
        cursor.execute("""
            SELECT 
                es.id,
                es.subject,
                es.assessment_mode,
                es.status,
                es.questions_correct,
                es.questions_attempted,
                es.started_at,
                es.completed_at,
                u.username
            FROM exam_sessions es
            JOIN auth_user u ON es.student_id = u.id
            WHERE u.username = 'test_ai_student_1'
            ORDER BY es.started_at DESC
        """)
        
        exam_sessions = cursor.fetchall()
        
        print(f"📋 EXAM SESSIONS for test_ai_student_1:")
        print(f"   Total sessions: {len(exam_sessions)}")
        
        for session in exam_sessions[:5]:  # Show first 5
            session_id, subject, mode, status, correct, attempted, started, completed, username = session
            print(f"   ID: {session_id} | Subject: {subject} | Mode: {mode} | Status: {status}")
            print(f"      Score: {correct}/{attempted} | Started: {started} | Completed: {completed}")
        
        # Check student_sessions for adaptive learning
        cursor.execute("""
            SELECT 
                ss.id,
                ss.session_type,
                ss.created_at,
                ss.final_mastery_score,
                u.username
            FROM student_sessions ss
            JOIN auth_user u ON ss.user_id = u.id
            WHERE u.username = 'test_ai_student_1'
            ORDER BY ss.created_at DESC
        """)
        
        student_sessions = cursor.fetchall()
        
        print(f"\n🧠 STUDENT SESSIONS for test_ai_student_1:")
        print(f"   Total sessions: {len(student_sessions)}")
        
        for session in student_sessions[:3]:  # Show first 3
            session_id, session_type, completed, mastery, username = session
            print(f"   ID: {session_id} | Type: {session_type} | Completed: {completed} | Mastery: {mastery}")
        
        # Test the categorization logic manually
        print(f"\n🔍 CATEGORIZATION TEST:")
        regular_count = 0
        adaptive_count = 0
        
        for session in exam_sessions:
            mode = session[2]  # assessment_mode
            if mode in ['PRACTICE', 'EXAM']:
                regular_count += 1
            print(f"   ExamSession mode '{mode}' → Regular Assessment")
        
        for session in student_sessions:
            session_type = session[1]  # session_type  
            if session_type == 'adaptive_learning':
                adaptive_count += 1
            print(f"   StudentSession type '{session_type}' → Adaptive Learning")
        
        print(f"\n📊 EXPECTED CATEGORIZATION:")
        print(f"   Regular Assessments: {regular_count}")
        print(f"   Adaptive Sessions: {adaptive_count}")
        
        return regular_count, adaptive_count
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return 0, 0
    finally:
        conn.close()

if __name__ == "__main__":
    debug_assessment_data()