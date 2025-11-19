#!/usr/bin/env python3

"""
Strategic Match - Dashboard Builder
Generates index.html with data from jobs.db including tier system
"""

import sqlite3
import json
from datetime import datetime

def build_dashboard():
    """Build Strategic Match dashboard from database"""
    print("🎯 Building Strategic Match Dashboard")
    print("=" * 60)

    # Connect to database
    conn = sqlite3.connect('jobs.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Fetch all jobs
    cursor.execute("""
        SELECT 
            id, title, company, job_type, salary_range, location, match_score,
            company_overview, why_this_role, interview_prep, talking_points,
            red_flags, url, status, date_added, tier, search_type
        FROM jobs
        ORDER BY date_added DESC, tier ASC, match_score DESC
    """)

    rows = cursor.fetchall()

    # Convert to list of dicts
    jobs = []
    for row in rows:
        job = dict(row)
        # Ensure tier exists (default to 3 for old jobs)
        if not job.get('tier'):
            job['tier'] = 3
        # Convert date to string
        if job.get('date_added'):
            job['date_added'] = str(job['date_added'])
        jobs.append(job)

    conn.close()

    print(f"📊 Loaded {len(jobs)} jobs from database")

    # Count by tier
    tier1 = len([j for j in jobs if j['tier'] == 1])
    tier2 = len([j for j in jobs if j['tier'] == 2])
    tier3 = len([j for j in jobs if j['tier'] == 3])

    print(f"   Tier 1: {tier1} | Tier 2: {tier2} | Tier 3: {tier3}")

    # Read HTML template
    with open('index.html', 'r', encoding='utf-8') as f:
        html_template = f.read()

    # Replace placeholder with actual data
    jobs_json = json.dumps(jobs, ensure_ascii=False)
    html_final = html_template.replace("'{{JOBS_JSON}}'", jobs_json)

    # Save final dashboard
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_final)

    print("\n✅ Dashboard built successfully!")
    print(f"   File: index.html")
    print(f"   Total jobs: {len(jobs)}")
    print("=" * 60)

if __name__ == "__main__":
    build_dashboard()
