#!/usr/bin/env python3
"""Debug specific session details"""

import sqlite3
import os
import json

def debug_specific_session():
    """Check details for the sessions shown in the UI"""
    db_path = 'Backend/db.sqlite3'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get the specific sessions that appear in the UI for student ID 68 (dash/dashrath)
        cursor.execute("""
            SELECT 
                ss.id,
                ss.session_name,
                ss.questions_attempted,
                ss.questions_correct,
                ss.percentage_score,
                ss.session_type,
                u.username
            FROM student_sessions ss
            JOIN auth_user u ON ss.student_id = u.id
            WHERE u.username IN ('dash', 'student_dashrath', 'test_ai_student_1') 
            AND ss.status = 'COMPLETED'
            ORDER BY ss.updated_at DESC
            LIMIT 10
        """)
        
        sessions = cursor.fetchall()
        
        print("🎯 SESSIONS FOR UI USERS:")
        print("-" * 80)
        for session in sessions:
            session_id, name, attempted, correct, score, session_type, username = session
            print(f"Session ID: {session_id}")
            print(f"   User: {username} | Name: {name}")
            print(f"   Questions: {correct}/{attempted} | Score: {score:.1f}% | Type: {session_type}")
            
            # Get question attempts for this session
            cursor.execute("""
                SELECT 
                    qa.question_number_in_session,
                    qa.is_correct,
                    qa.difficulty_when_presented,
                    qa.time_spent_seconds,
                    qa.student_answer,
                    qa.correct_answer
                FROM question_attempts qa
                WHERE qa.session_id = ?
                ORDER BY qa.question_number_in_session
            """, (session_id,))
            
            attempts = cursor.fetchall()
            
            if attempts:
                print(f"   📋 Question Attempts ({len(attempts)}):")
                
                # Analyze by difficulty
                difficulty_stats = {}
                for attempt in attempts:
                    q_num, correct, difficulty, time_spent, student_ans, correct_ans = attempt
                    if difficulty not in difficulty_stats:
                        difficulty_stats[difficulty] = {'correct': 0, 'total': 0}
                    difficulty_stats[difficulty]['total'] += 1
                    if correct:
                        difficulty_stats[difficulty]['correct'] += 1
                
                for difficulty, stats in difficulty_stats.items():
                    accuracy = (stats['correct'] / stats['total']) * 100 if stats['total'] > 0 else 0
                    print(f"      {difficulty.capitalize()}: {stats['correct']}/{stats['total']} ({accuracy:.1f}%)")
                        
            else:
                print(f"   ❌ No question attempts found")
            
            print()
        
        # Check if we have sessions for the user that appears in the frontend
        print("\n🔍 CHECKING FOR FRONTEND USER DATA:")
        print("-" * 60)
        
        # The frontend seems to be showing data under user 68 (dash)
        cursor.execute("""
            SELECT username, id FROM auth_user 
            WHERE id IN (68, 69) OR username LIKE '%dash%'
        """)
        users = cursor.fetchall()
        
        for username, user_id in users:
            print(f"User ID {user_id}: {username}")
            
            # Get completed sessions for this user
            cursor.execute("""
                SELECT COUNT(*) FROM student_sessions 
                WHERE student_id = ? AND status = 'COMPLETED'
            """, (user_id,))
            
            completed_count = cursor.fetchone()[0]
            print(f"   Completed sessions: {completed_count}")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    debug_specific_session()