import sqlite3
import os

def inspect_db(db_name):
    if not os.path.exists(db_name):
        print(f"❌ {db_name} does not exist.")
        return

    print(f"\n📂 Schema for {db_name}:")
    try:
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
        tables = c.fetchall()
        for name, sql in tables:
            print(f"--- Table: {name} ---")
            print(sql)
        conn.close()
    except Exception as e:
        print(f"Error reading {db_name}: {e}")

inspect_db('jobs.db')
inspect_db('applications.db')
