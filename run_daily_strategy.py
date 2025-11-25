import sqlite3
import subprocess
import sys

DB_PATH = 'jobs.db'

def get_top_jobs(limit=5):
    """Get top N 'New' jobs sorted by match score that don't have a kit yet."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Find jobs that are New and don't have a strategy kit
    c.execute("""
        SELECT j.id, j.title, j.company, j.match_score 
        FROM jobs j
        LEFT JOIN strategy_kits s ON j.id = s.job_id
        WHERE j.status = 'New' AND s.id IS NULL
        ORDER BY j.match_score DESC
        LIMIT ?
    """, (limit,))
    
    jobs = [dict(row) for row in c.fetchall()]
    conn.close()
    return jobs

def run():
    print("🚀 Starting Daily Strategy Generation (Top 5)...")
    jobs = get_top_jobs(5)
    
    if not jobs:
        print("✅ No new high-priority jobs need strategy kits.")
        return

    print(f"🎯 Found {len(jobs)} targets:")
    for j in jobs:
        print(f"   - [{j['match_score']}] {j['title']} @ {j['company']}")
    
    print("\n⚡ Generating Kits (this may take 1-2 mins per job)...")
    for j in jobs:
        print(f"   ... Processing Job ID {j['id']} ...")
        try:
            subprocess.run([sys.executable, "generate_strategy_kit.py", str(j['id'])], check=True)
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to generate kit for Job {j['id']}")

    print("\n✅ Batch Complete! Run 'python build_dashboard_pro.py' to see updates.")

if __name__ == "__main__":
    run()
