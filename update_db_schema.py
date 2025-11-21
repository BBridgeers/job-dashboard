#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('jobs.db')
cursor = conn.cursor()

# Get current schema
cursor.execute("PRAGMA table_info(jobs)")
existing_columns = {row[1] for row in cursor.fetchall()}

print("Current columns:", existing_columns)
print()

# Add missing columns
columns_to_add = [
    ('tier', 'INTEGER DEFAULT 3'),
    ('date_added', 'DATE'),
    ('search_type', 'TEXT DEFAULT "corporate"'),
    ('salary_range', 'TEXT'),
    ('location', 'TEXT')
]

for col_name, col_type in columns_to_add:
    if col_name not in existing_columns:
        try:
            cursor.execute(f'ALTER TABLE jobs ADD COLUMN {col_name} {col_type}')
            print(f'✅ Added {col_name} column')
        except Exception as e:
            print(f'❌ Error adding {col_name}: {e}')
    else:
        print(f'⚠️  {col_name} already exists')

# Set date_added for existing rows
cursor.execute("UPDATE jobs SET date_added = CURRENT_DATE WHERE date_added IS NULL")

conn.commit()
conn.close()

print('\n🎉 Database schema updated!')
