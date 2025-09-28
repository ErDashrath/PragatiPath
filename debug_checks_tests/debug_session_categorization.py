#!/usr/bin/env python3
"""Debug script to check session types and categorization"""

import sqlite3
import os

def check_session_types():
    """Check session types in the database"""
    db_path = 'Backend/db.sqlite3'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check exam_sessions table for session types
        cursor.execute("""
            SELECT 
                subject,
                assessment_mode,
                status,
                questions_attempted,
                questions_correct,
                started_at,
                completed_at,
                student_id
            FROM exam_sessions
            WHERE completed_at IS NOT NULL
            ORDER BY completed_at DESC
            LIMIT 10
        """)
        
        sessions = cursor.fetchall()
        
        print("🎯 RECENT COMPLETED SESSIONS:")
        print("-" * 100)
        print("Subject               | Mode      | Status  | Q.Att | Q.Cor | Started             | Completed           | StudentID")
        print("-" * 100)
        
        for session in sessions:
            subject, mode, status, q_att, q_cor, started, completed, student_id = session
            print(f"{subject:<20} | {mode:<8} | {status:<6} | {q_att:<5} | {q_cor:<5} | {started:<18} | {completed:<18} | {student_id}")
        
        # Check session type distribution
        cursor.execute("""
            SELECT assessment_mode, COUNT(*) as count
            FROM exam_sessions
            GROUP BY assessment_mode
            ORDER BY count DESC
        """)
        
        mode_distribution = cursor.fetchall()
        
        print(f"\n📊 SESSION MODE DISTRIBUTION:")
        print("-" * 40)
        for mode, count in mode_distribution:
            print(f"  {mode:<15}: {count} sessions")
        
        # Check which sessions would be categorized as adaptive vs assessment
        print(f"\n🔍 CATEGORIZATION ANALYSIS:")
        print("-" * 50)
        
        assessment_types = ['COMPETITIVE_EXAM', 'PRACTICE_TEST', 'ASSESSMENT']
        adaptive_types = ['PRACTICE', 'EXAM', 'ADAPTIVE_LEARNING']
        
        for mode, count in mode_distribution:
            if mode in assessment_types:
                category = "ASSESSMENT TAB"
            elif mode in adaptive_types:
                category = "ADAPTIVE TAB"
            else:
                category = "OTHER/UNKNOWN"
            
            print(f"  {mode:<15} → {category} ({count} sessions)")
            
        return mode_distribution
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 80)
    print("SESSION TYPE CATEGORIZATION DEBUG")
    print("=" * 80)
    
    mode_distribution = check_session_types()
    
    if mode_distribution:
        print(f"\n💡 ISSUE IDENTIFIED:")
        print(f"   Sessions with 'PRACTICE' and 'EXAM' modes are being categorized")
        print(f"   as ADAPTIVE LEARNING instead of regular ASSESSMENTS.")
        print(f"   ")
        print(f"   SOLUTION: Update the categorization logic in enhanced_history_api_fixed.py")
        print(f"   to treat 'PRACTICE' and 'EXAM' as regular assessment types.")
    else:
        print(f"\n❌ Could not analyze session categorization")