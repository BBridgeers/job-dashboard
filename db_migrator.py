import sqlite3
import json
import os
import glob
import re
from datetime import datetime

DB_PATH = 'jobs.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # JOBS TABLE
    c.execute("""CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        company TEXT NOT NULL,
        url TEXT UNIQUE,
        match_score INTEGER,
        tier INTEGER DEFAULT 3,
        salary_min INTEGER,
        salary_max INTEGER,
        salary_text TEXT,
        location TEXT,
        posted_date DATE,
        search_type TEXT,
        description TEXT,
        requirements TEXT,
        benefits TEXT,
        red_flags TEXT,
        company_overview TEXT,
        role_insights TEXT,
        interview_prep TEXT,
        talking_points TEXT,
        date_added DATE DEFAULT CURRENT_DATE,
        status TEXT DEFAULT 'New',
        notes TEXT
    )""")

    # APPLICATIONS TABLE
    c.execute("""CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER NOT NULL,
        applied_date DATE DEFAULT CURRENT_DATE,
        status TEXT DEFAULT 'Applied',
        notes TEXT,
        FOREIGN KEY (job_id) REFERENCES jobs (id)
    )""")

    # INTERVIEWS TABLE
    c.execute("""CREATE TABLE IF NOT EXISTS interviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        application_id INTEGER NOT NULL,
        interview_date DATETIME,
        type TEXT,
        notes TEXT,
        FOREIGN KEY (application_id) REFERENCES applications (id)
    )""")

    # STRATEGY KITS TABLE (Phase 2)
    c.execute("""CREATE TABLE IF NOT EXISTS strategy_kits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER NOT NULL,
        data JSON,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (job_id) REFERENCES jobs (id)
    )""")

    conn.commit()
    return conn

def parse_salary(salary_str):
    """Extract min and max salary from string."""
    if not salary_str:
        return None, None
    
    s = salary_str.lower().replace('k', '000').replace(',', '')
    numbers = re.findall(r'\d+', s)
    
    if not numbers:
        return None, None
    
    try:
        nums = [int(n) for n in numbers]
        nums = [n for n in nums if n > 10000] 
        
        if not nums:
            return None, None
            
        if len(nums) == 1:
            return nums[0], nums[0]
        
        return min(nums), max(nums)
    except:
        return None, None

def safe_str(value):
    """Convert value to string, handling lists and dicts."""
    if value is None:
        return ''
    if isinstance(value, (list, dict)):
        return json.dumps(value)
    return str(value)

def migrate():
    print("🚀 Starting Data Migration...")
    init_db()
    
    files = glob.glob("job_search_results/*.txt")
    print(f"📂 Found {len(files)} files to process.")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    new_count = 0
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Try to parse JSON list
            try:
                jobs = json.loads(content)
            except json.JSONDecodeError:
                # Fallback for older raw text files if needed, or skip
                continue
                
            if not isinstance(jobs, list):
                continue
                
            for j in jobs:
                # Calculate Tier
                score = int(j.get('match_score', 0))
                if score >= 90: tier = 1
                elif score >= 80: tier = 2
                else: tier = 3
                
                # Parse Salary
                salary_txt = j.get('salary_intel', '')
                min_sal, max_sal = parse_salary(salary_txt)
                
                # Determine Search Type
                search_type = 'corporate' if 'corporate' in file_path else 'nonprofit'
                
                try:
                    c.execute("""
                        INSERT INTO jobs (
                            title, company, url, match_score, tier,
                            salary_min, salary_max, salary_text, location,
                            search_type, description, requirements, red_flags,
                            company_overview, role_insights, interview_prep, talking_points,
                            date_added, status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        j.get('title'), 
                        j.get('company'), 
                        j.get('listing_url') or j.get('url'), 
                        score, 
                        tier,
                        min_sal, 
                        max_sal, 
                        safe_str(salary_txt), 
                        j.get('location'),
                        search_type, 
                        safe_str(j.get('summary_bullets')), 
                        safe_str(j.get('key_requirements')), 
                        safe_str(j.get('red_flags')),
                        safe_str(j.get('company_overview')), 
                        safe_str(j.get('role_insights')), 
                        safe_str(j.get('interview_prep')), 
                        safe_str(j.get('talking_points')),
                        datetime.now().strftime('%Y-%m-%d'), 
                        'New'
                    ))
                    new_count += 1
                except sqlite3.IntegrityError:
                    # Duplicate URL, skip
                    pass
                    
        except Exception as e:
            print(f"⚠️ Error processing {file_path}: {e}")
            
    conn.commit()
    conn.close()
    print(f"✅ Migration Complete. Added {new_count} new jobs.")

if __name__ == "__main__":
    migrate()
