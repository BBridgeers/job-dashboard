import sqlite3
import json
import glob
import os
import re

DB_PATH = 'jobs.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        company TEXT,
        url TEXT UNIQUE,
        match_score INTEGER,
        tier INTEGER,
        status TEXT DEFAULT 'New',
        notes TEXT,
        company_overview TEXT,
        role_insights TEXT,
        key_requirements TEXT,
        interview_prep TEXT,
        talking_points TEXT,
        red_flags TEXT,
        full_description TEXT,
        search_type TEXT,
        application_url TEXT,
        date_added TEXT
    )""")
    conn.commit()
    return conn

def clean_text(text):
    """Clean and normalize text data"""
    if not text:
        return ""
    # Remove excessive whitespace and normalize
    text = re.sub(r'\s+', ' ', str(text).strip())
    return text

def parse_txt_file(filepath):
    jobs = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        raw_entries = content.split("--------------------------------------------------")

        for entry in raw_entries:
            if not entry.strip(): 
                continue

            job = {}
            title_match = re.search(r"Role: (.+)", entry)
            company_match = re.search(r"Company: (.+)", entry)
            url_match = re.search(r"URL: (.+)", entry)
            score_match = re.search(r"Match Score: (\d+)", entry)
            tier_match = re.search(r"Tier: (\d+)", entry)

            if title_match: job['title'] = clean_text(title_match.group(1))
            if company_match: job['company'] = clean_text(company_match.group(1))
            if url_match: job['url'] = clean_text(url_match.group(1))
            if score_match: job['match_score'] = int(score_match.group(1))
            if tier_match: job['tier'] = int(tier_match.group(1))

            sections = [
                ('Company Overview', 'company_overview'),
                ('Role Insights', 'role_insights'),
                ('Key Requirements', 'key_requirements'),
                ('Interview Prep', 'interview_prep'),
                ('Talking Points', 'talking_points'),
                ('Red Flags', 'red_flags')
            ]

            for label, key in sections:
                pattern = fr"\*\*?{label}:?\*\*?\s*(.*?)(?=\n\*\*|$)"
                match = re.search(pattern, entry, re.DOTALL)
                if match:
                    job[key] = clean_text(match.group(1))
                else:
                    job[key] = ""

            # Only add jobs with valid URLs
            if job.get('url') and job['url'].strip() != '#':
                jobs.append(job)

    except Exception as e:
        print(f"⚠️ Error reading {filepath}: {e}")

    return jobs

def migrate():
    print("🚀 STARTING ROBUST MIGRATION...")
    conn = init_db()
    c = conn.cursor()

    files = glob.glob("job_search_results/*.txt")
    if not files:
        files = glob.glob("job_search_*sonar*.txt")

    print(f"📂 Found {len(files)} result files.")

    new_count = 0
    updated_count = 0

    for fpath in files:
        print(f"   Processing {fpath}...")
        jobs = parse_txt_file(fpath)
        search_type = "Corporate" if "corporate" in fpath.lower() else "Nonprofit"

        for j in jobs:
            try:
                # Ensure values are strings (handles lists gracefully)
                vals = (
                    j.get('title', 'Unknown Role'),
                    j.get('company', 'Unknown Co'),
                    j.get('url', '#'),
                    j.get('match_score', 0),
                    j.get('tier', 3),
                    str(j.get('company_overview', '')),
                    str(j.get('role_insights', '')),
                    str(j.get('key_requirements', '')),
                    str(j.get('interview_prep', '')),
                    str(j.get('talking_points', '')),
                    str(j.get('red_flags', '')),
                    search_type,
                    j.get('url', '#')  # application_url same as listing url by default
                )

                # Try to insert, if duplicate update existing
                c.execute("""
                    INSERT OR IGNORE INTO jobs (
                        title, company, url, match_score, tier, 
                        company_overview, role_insights, key_requirements,
                        interview_prep, talking_points, red_flags,
                        search_type, application_url, date_added
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, date('now'))
                """, vals)

                if c.rowcount > 0:
                    new_count += 1
                else:
                    # Update existing job with new data
                    c.execute("""
                        UPDATE jobs SET
                            title = ?, company = ?, match_score = ?, tier = ?,
                            company_overview = ?, role_insights = ?, key_requirements = ?,
                            interview_prep = ?, talking_points = ?, red_flags = ?,
                            search_type = ?, application_url = ?
                        WHERE url = ?
                    """, vals)
                    updated_count += 1

            except Exception as e:
                print(f"❌ Error processing job {j.get('company', 'Unknown')}: {e}")

    conn.commit()
    conn.close()
    print(f"✅ Migration Complete. Added {new_count} new jobs, updated {updated_count} existing jobs.")

if __name__ == '__main__':
    migrate()
