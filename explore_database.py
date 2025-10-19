#!/usr/bin/env python3
"""
Explore database structure to find where users are stored
"""

import sqlite3

def explore_database():
    try:
        # Connect to the database
        conn = sqlite3.connect('db.sqlite')
        cursor = conn.cursor()
        
        # Get all tables
        print("📊 All tables in database:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("   No tables found!")
            return
        
        for table in tables:
            table_name = table[0]
            print(f"   📋 {table_name}")
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            for col in columns:
                col_id, col_name, col_type, not_null, default, pk = col
                pk_marker = " (PK)" if pk else ""
                print(f"      - {col_name}: {col_type}{pk_marker}")
            
            # Show sample data
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"      Records: {count}")
            
            if count > 0 and count < 20:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                sample_data = cursor.fetchall()
                for row in sample_data:
                    print(f"      Sample: {row}")
            
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    print("🔍 Exploring Database Structure\n")
    explore_database()
    print("✨ Exploration completed!")