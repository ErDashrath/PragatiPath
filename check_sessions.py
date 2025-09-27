import sqlite3
import json
from datetime import datetime

conn = sqlite3.connect('Backend/db.sqlite3')
cursor = conn.cursor()

# Check what tables exist
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Database Tables:')
for table in tables:
    print(f'- {table[0]}')

print('\n' + '='*50)

# Find session-related tables
session_tables = [t[0] for t in tables if 'session' in t[0].lower()]
print(f'Session-related tables: {session_tables}')

# Check different session tables
for table_name in ['student_sessions', 'user_sessions', 'exam_sessions']:
    if table_name in [t[0] for t in tables]:
        print(f'\nChecking recent sessions in {table_name}:')
        print('='*50)
        
        try:
            cursor.execute(f"SELECT * FROM {table_name} ORDER BY rowid DESC LIMIT 5")
            
            # Get column names
            columns = [description[0] for description in cursor.description]
            print(f'Columns: {columns}')
            
            sessions = cursor.fetchall()
            for session in sessions:
                print('\nSession:')
                for i, col in enumerate(columns):
                    value = session[i]
                    if col == 'session_config' and value:
                        try:
                            config = json.loads(value)
                            print(f'  {col}: {json.dumps(config, indent=2)[:200]}...')
                        except:
                            print(f'  {col}: {value}')
                    else:
                        print(f'  {col}: {value}')
                print('-' * 30)
        except Exception as e:
            print(f'Error checking {table_name}: {e}')
            
        print('\n' + '='*50)

conn.close()