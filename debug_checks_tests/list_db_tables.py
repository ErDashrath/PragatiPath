#!/usr/bin/env python3
"""Simple script to check database tables"""

import sqlite3
import os

def list_tables():
    """List all tables in the database"""
    db_path = 'Backend/db.sqlite3'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("Database Tables:")
        print("-" * 40)
        for table in tables:
            print(f"  {table[0]}")
            
        print(f"\n📊 Total tables: {len(tables)}")
        
        # Find assessment-related tables
        assessment_tables = [t[0] for t in tables if 'assessment' in t[0].lower()]
        if assessment_tables:
            print(f"\n🎯 Assessment-related tables:")
            for table in assessment_tables:
                print(f"  {table}")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    list_tables()