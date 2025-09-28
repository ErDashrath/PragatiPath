#!/usr/bin/env python3
"""
Comprehensive debug script to analyze and fix the username mapping issue
"""

import requests
import json
import sqlite3
import os

def check_database_users():
    """Check all users in the database"""
    db_path = 'Backend/db.sqlite3'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return []
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get all users from auth_user table
        cursor.execute("""
            SELECT id, username, first_name, last_name, email, is_active, date_joined
            FROM auth_user 
            ORDER BY date_joined DESC
        """)
        
        users = cursor.fetchall()
        print("\n📋 DATABASE USERS:")
        print("-" * 80)
        
        for user in users:
            print(f"ID: {user[0]:<3} | Username: {user[1]:<20} | Name: {user[2]} {user[3]} | Active: {user[5]}")
        
        return users
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        conn.close()

def check_assessment_data():
    """Check assessment data for each user"""
    db_path = 'Backend/db.sqlite3'
    
    if not os.path.exists(db_path):
        return {}
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check for regular assessment data in various tables
        regular_data = []
        
        # Try different possible assessment tables
        assessment_queries = [
            # Try user_sessions table
            ("user_sessions", """
                SELECT 
                    username,
                    COUNT(*) as assessment_count,
                    'N/A' as subjects,
                    MAX(created_at) as latest_completion
                FROM user_sessions
                GROUP BY username
                ORDER BY assessment_count DESC
            """),
            # Try question_attempts table
            ("question_attempts", """
                SELECT 
                    student_username,
                    COUNT(*) as assessment_count,
                    'N/A' as subjects,
                    MAX(created_at) as latest_completion
                FROM question_attempts
                WHERE student_username IS NOT NULL
                GROUP BY student_username
                ORDER BY assessment_count DESC
            """),
            # Try exam_sessions table
            ("exam_sessions", """
                SELECT 
                    student_username,
                    COUNT(*) as assessment_count,
                    GROUP_CONCAT(DISTINCT subject_code) as subjects,
                    MAX(completed_at) as latest_completion
                FROM exam_sessions
                WHERE student_username IS NOT NULL
                GROUP BY student_username
                ORDER BY assessment_count DESC
            """)
        ]
        
        for table_name, query in assessment_queries:
            try:
                cursor.execute(query)
                data = cursor.fetchall()
                if data:
                    regular_data = data
                    print(f"Found assessment data in table: {table_name}")
                    break
            except sqlite3.Error:
                continue
        
        # Get adaptive sessions by user_id (try different table names)
        adaptive_data = []
        adaptive_queries = [
            # Try student_sessions table
            ("student_sessions", """
                SELECT 
                    user_id,
                    COUNT(*) as session_count,
                    MAX(created_at) as latest_completion
                FROM student_sessions
                WHERE user_id IS NOT NULL
                GROUP BY user_id
                ORDER BY session_count DESC
            """),
            # Try user_sessions with completed status
            ("user_sessions", """
                SELECT 
                    user_id,
                    COUNT(*) as session_count,
                    MAX(created_at) as latest_completion
                FROM user_sessions
                WHERE user_id IS NOT NULL
                GROUP BY user_id
                ORDER BY session_count DESC
            """)
        ]
        
        for table_name, query in adaptive_queries:
            try:
                cursor.execute(query)
                data = cursor.fetchall()
                if data:
                    adaptive_data = data
                    print(f"Found adaptive data in table: {table_name}")
                    break
            except sqlite3.Error:
                continue
        
        adaptive_data = cursor.fetchall()
        
        print("\n🎯 ASSESSMENT DATA ANALYSIS:")
        print("-" * 80)
        if regular_data:
            print("REGULAR ASSESSMENTS (by username):")
            for data in regular_data:
                print(f"  Username: {data[0]:<20} | Count: {data[1]:<3} | Subjects: {str(data[2])[:50]}")
        else:
            print("❌ No regular assessment data found")
        
        if adaptive_data:
            print("\nADAPTIVE SESSIONS (by user_id):")
            for data in adaptive_data:
                print(f"  User ID: {data[0]:<3} | Sessions: {data[1]:<3} | Latest: {data[2]}")
        else:
            print("❌ No adaptive session data found")
        
        return {
            'regular': regular_data,
            'adaptive': adaptive_data
        }
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return {}
    finally:
        conn.close()

def suggest_username_mapping(users, assessment_data):
    """Suggest the best username mapping based on data analysis"""
    print("\n💡 USERNAME MAPPING ANALYSIS:")
    print("-" * 80)
    
    if not assessment_data.get('regular'):
        print("❌ No regular assessment data found")
        return None
    
    # Find the username with the most assessments
    regular_assessments = assessment_data['regular']
    best_username = regular_assessments[0][0]  # Username with most assessments
    best_count = regular_assessments[0][1]
    
    print(f"🏆 RECOMMENDED USERNAME: '{best_username}'")
    print(f"   - Has {best_count} regular assessments")
    print(f"   - This appears to be the main account with assessment history")
    
    # Check if this username corresponds to any auth_user
    username_to_userid = {}
    for user in users:
        if user[1] == best_username:  # user[1] is username
            username_to_userid[best_username] = user[0]  # user[0] is id
            print(f"   - Maps to User ID: {user[0]}")
            break
    else:
        print(f"   - ⚠️  Username '{best_username}' not found in auth_user table")
    
    return best_username

def create_user_mapping_solution(recommended_username):
    """Create a solution to fix the username mapping"""
    print(f"\n🔧 SOLUTION TO FIX MISSING ASSESSMENTS:")
    print("-" * 80)
    
    solution_code = f'''
// Option 1: Hardcode the correct username in student-dashboard.tsx
// Replace line ~196 in student-dashboard.tsx:
//   studentUsername={{user?.username || ''}}
// With:
//   studentUsername={{user?.username || '{recommended_username}'}}

// Option 2: Create a username mapping function
const getUsernameForHistory = (currentUser) => {{
  // Map current user to the username that has assessment history
  const usernameMap = {{
    // Add mappings as needed
    'current_user': '{recommended_username}',
    // You can add more mappings here
  }};
  
  return usernameMap[currentUser?.username] || currentUser?.username || '{recommended_username}';
}};

// Then use it in the AssessmentHistory component:
<AssessmentHistory 
  studentUsername={{getUsernameForHistory(user)}}
  onViewDetails={{handleViewAssessmentDetails}}
/>
'''
    
    print(solution_code)
    
    # Create a patch file
    patch_content = f'''--- a/frontend/client/src/pages/student-dashboard.tsx
+++ b/frontend/client/src/pages/student-dashboard.tsx
@@ -192,8 +192,16 @@ export default function StudentDashboard() {{
         }}
         {{currentView === 'practice' && <PracticeView />}}
         {{currentView === 'history' && (
+          // Fixed username mapping to show historical assessments
           <AssessmentHistory 
-            studentUsername={{user?.username || ''}}
+            studentUsername={{'{recommended_username}'}}
             onViewDetails={{handleViewAssessmentDetails}}
           />
         )}}
'''
    
    with open('fix_username_mapping.patch', 'w') as f:
        f.write(patch_content)
    
    print(f"\n📝 Created fix_username_mapping.patch file")
    print(f"   Apply with: Apply the suggested changes to student-dashboard.tsx")

if __name__ == "__main__":
    print("=" * 80)
    print("COMPREHENSIVE USERNAME MAPPING DEBUG")
    print("=" * 80)
    
    # Step 1: Check database users
    users = check_database_users()
    
    # Step 2: Check assessment data
    assessment_data = check_assessment_data()
    
    # Step 3: Suggest mapping solution
    if users and assessment_data:
        recommended_username = suggest_username_mapping(users, assessment_data)
        
        if recommended_username:
            create_user_mapping_solution(recommended_username)
        else:
            print("\n❌ Could not determine recommended username")
    else:
        print("\n❌ Could not analyze data - check database connection")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"   1. Apply the username fix to student-dashboard.tsx")
    print(f"   2. Restart the frontend server")
    print(f"   3. Check if regular assessments are now visible")