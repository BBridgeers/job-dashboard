#!/usr/bin/env python3
"""
Database Schema Update - Adds Rich Job Detail Fields
Expands jobs table to store all 11 components from TXT files
"""

import sqlite3
from datetime import datetime

def update_database_schema(db_path='jobs.db'):
    """Add new columns for rich job details"""

    print("🔧 Updating Database Schema...")
    print("=" * 60)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # New columns to add
    new_columns = [
        ("full_description", "TEXT"),
        ("key_requirements", "TEXT"),
        ("company_overview", "TEXT"),
        ("why_this_role", "TEXT"),
        ("interview_prep", "TEXT"),
        ("talking_points", "TEXT"),
        ("red_flags", "TEXT"),
        ("application_url", "TEXT"),
        ("viewed_date", "TIMESTAMP"),
        ("applied_date", "TIMESTAMP"),
        ("is_top_match", "INTEGER DEFAULT 0"),
    ]

    for col_name, col_type in new_columns:
        try:
            cursor.execute(f"ALTER TABLE jobs ADD COLUMN {col_name} {col_type}")
            print(f"✅ Added column: {col_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print(f"⏭️  Column exists: {col_name}")
            else:
                print(f"⚠️  Error adding {col_name}: {e}")

    conn.commit()

    # Verify schema
    cursor.execute("PRAGMA table_info(jobs)")
    columns = cursor.fetchall()

    print("\n📋 Current Database Schema:")
    print("-" * 60)
    for col in columns:
        print(f"  {col[1]} ({col[2]})")

    conn.close()

    print("\n✅ Database schema updated successfully!")
    print("=" * 60)

if __name__ == "__main__":
    update_database_schema()