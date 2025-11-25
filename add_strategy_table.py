import sqlite3

DB_PATH = 'jobs.db'

def add_table():
    print("🔧 Adding 'strategy_kits' table to database...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("""CREATE TABLE IF NOT EXISTS strategy_kits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER NOT NULL,
        data JSON,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (job_id) REFERENCES jobs (id)
    )""")
    
    conn.commit()
    conn.close()
    print("✅ Table 'strategy_kits' created successfully.")

if __name__ == "__main__":
    add_table()
