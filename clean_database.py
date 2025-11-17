import sqlite3

conn = sqlite3.connect('jobs.db')
cursor = conn.cursor()

cursor.execute("""
DELETE FROM jobs WHERE 
    title LIKE '%Prioritize%' OR 
    title LIKE '%Leverage%' OR 
    title LIKE '%Target%' OR 
    title LIKE '%Consider%' OR 
    title LIKE '%Prepare%' OR 
    title LIKE '%Salary%' OR 
    title LIKE '%Network%' OR
    title LIKE '%**%' OR
    url IS NULL OR
    url = ''
""")

conn.commit()
print(f"✅ Deleted {cursor.rowcount} garbage entries")

cursor.execute("SELECT COUNT(*) FROM jobs")
print(f"📊 {cursor.fetchone()[0]} valid jobs remaining")

conn.close()
