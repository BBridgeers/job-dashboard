import sqlite3
import os
import glob
import json
import datetime

DB_NAME = "jobs.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Create table with ALL 30 columns if not exists
    # Fixed the triple-quote syntax error here
    sql = """CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT, company TEXT, location TEXT, match_score INTEGER,
        url TEXT, application_url TEXT,
        summary_bullets TEXT, company_overview TEXT, role_insights TEXT,
        key_requirements TEXT, salary_intel TEXT, application_strategy TEXT,
        red_flags TEXT, cultural_fit TEXT, competitive_landscape TEXT,
        skills_gap TEXT, network_leverage TEXT, decision_timeline TEXT,
        career_trajectory TEXT, resume_keywords TEXT, resume_summary TEXT,
        cover_letter TEXT, why_me_bullets TEXT, why_them_bullets TEXT,
        interview_prep TEXT, star_hooks TEXT, talking_points TEXT,
        questions_to_ask TEXT, recruiter_email TEXT, plan_30_60_90 TEXT,
        status TEXT DEFAULT 'New', tier INTEGER DEFAULT 3,
        search_type TEXT, date_added DATE
    )"""
    c.execute(sql)
    conn.commit()
    conn.close()

def run_migration():
    print("🚀 STARTING JSON MIGRATION...")
    init_db()

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Find all result files
    files = glob.glob("job_search_results/*.txt")
    new_count = 0

    for f in files:
        try:
            with open(f, 'r', encoding='utf-8') as file:
                content = file.read().strip()

            # Try parsing as JSON
            try:
                data = json.loads(content)
            except:
                print(f"⚠️ Skipping {f} (Not valid JSON)")
                continue

            if not isinstance(data, list): data = [data]

            # Identify type based on filename
            s_type = "Corporate" if "corporate" in f else "Nonprofit"

            for job in data:
                # Check dupe
                title = job.get('title', '')
                company = job.get('company', '')
                c.execute("SELECT id FROM jobs WHERE title=? AND company=?", (title, company))
                if c.fetchone():
                    continue

                # Insert
                cols = [
                    'title', 'company', 'location', 'match_score', 'url', 'application_url',
                    'summary_bullets', 'company_overview', 'role_insights', 'key_requirements',
                    'salary_intel', 'application_strategy', 'red_flags', 'cultural_fit',
                    'competitive_landscape', 'skills_gap', 'network_leverage', 'decision_timeline',
                    'career_trajectory', 'resume_keywords', 'resume_summary', 'cover_letter',
                    'why_me_bullets', 'why_them_bullets', 'interview_prep', 'star_hooks',
                    'talking_points', 'questions_to_ask', 'recruiter_email', 'plan_30_60_90'
                ]

                # Map specific keys from JSON to DB columns
                # Note: JSON key 'listing_url' maps to DB column 'url'
                vals = []
                for k in cols:
                    if k == 'url':
                        vals.append(job.get('listing_url', ''))
                    else:
                        vals.append(job.get(k, ''))

                vals.append('New') # status

                # Tier Logic
                score = int(job.get('match_score', 0))
                tier = 1 if score >= 90 else 2 if score >= 80 else 3
                vals.append(tier)

                vals.append(s_type) # search_type
                vals.append(datetime.date.today()) # date_added

                placeholders = ','.join(['?'] * len(vals))
                c.execute(f"INSERT INTO jobs ({','.join(cols + ['status', 'tier', 'search_type', 'date_added'])}) VALUES ({placeholders})", vals)
                new_count += 1

        except Exception as e:
            print(f"❌ Error processing {f}: {e}")

    conn.commit()
    conn.close()
    print(f"✅ Migration Complete. Added {new_count} new jobs.")

if __name__ == "__main__":
    run_migration()
