import sqlite3

def backfill_tiers():
    print("🔄 Starting Tier Backfill...")
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    
    # Get all jobs
    c.execute("SELECT id, match_score FROM jobs")
    jobs = c.fetchall()
    
    updated_count = 0
    
    for job_id, score in jobs:
        if score is None:
            score = 0
        
        if score >= 90:
            tier = 1
        elif score >= 80:
            tier = 2
        else:
            tier = 3
            
        c.execute("UPDATE jobs SET tier = ? WHERE id = ?", (tier, job_id))
        updated_count += 1
        
    conn.commit()
    conn.close()
    print(f"✅ Backfill Complete. Updated {updated_count} jobs.")

if __name__ == "__main__":
    backfill_tiers()
