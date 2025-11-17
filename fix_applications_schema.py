#!/usr/bin/env python3
# fix_applications_schema.py
"""
Quick fix to add missing 'status' column to applications table
"""

import sqlite3

def fix_schema():
    conn = sqlite3.connect('master_jobs.db')
    cursor = conn.cursor()

    # Check if applications table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='applications'")
    if not cursor.fetchone():
        print("❌ Applications table doesn't exist yet. Run application_tracker.py first!")
        return False

    # Check if 'status' column exists
    cursor.execute("PRAGMA table_info(applications)")
    columns = [row[1] for row in cursor.fetchall()]

    if 'status' not in columns:
        print("🔧 Adding 'status' column to applications table...")
        try:
            cursor.execute("ALTER TABLE applications ADD COLUMN status TEXT DEFAULT 'applied'")
            conn.commit()
            print("✅ Schema fixed! 'status' column added.")
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    else:
        print("✅ Schema is already correct - 'status' column exists!")

    conn.close()
    return True

if __name__ == "__main__":
    print("\n🔧 FIXING DATABASE SCHEMA...\n")
    if fix_schema():
        print("\n✅ Database ready! You can now run:")
        print("   python3 build_dashboard.py")
    else:
        print("\n⚠️  Please run application_tracker.py first to create tables")
