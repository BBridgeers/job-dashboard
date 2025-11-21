#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('jobs.db')
cursor = conn.cursor()

# Check jobs with tier assignments
cursor.execute("""
    SELECT id, title, company, tier, date_added, url
    FROM jobs 
    WHERE date_added = date('now')
    ORDER BY tier, id
""")

print("🔍 Today's Jobs:")
print("=" * 80)
for row in cursor.fetchall():
    print(f"ID: {row[0]} | Tier: {row[2] or 'NULL'} | {row[1][:50]}")
    print(f"   Company: {row[2]}")
    print(f"   URL: {row[5][:60] if row[5] else 'None'}")
    print()

# Check all tier assignments
cursor.execute("SELECT tier, COUNT(*) FROM jobs GROUP BY tier")
print("\n📊 Tier Distribution:")
for row in cursor.fetchall():
    print(f"  Tier {row[0] if row[0] is not None else 'NULL'}: {row[1]} jobs")

conn.close()
