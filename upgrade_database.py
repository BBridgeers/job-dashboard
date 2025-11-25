import sqlite3
import shutil
import os
import re
from datetime import datetime

DB_PATH = 'jobs.db'
BACKUP_PATH = 'jobs.db.backup'

def backup_db():
    if os.path.exists(DB_PATH):
        shutil.copy2(DB_PATH, BACKUP_PATH)
        print(f"✅ Backup created at {BACKUP_PATH}")
    else:
        print("⚠️ No existing database found to backup.")

def parse_salary(salary_str):
    """Extract min and max salary from string."""
    if not salary_str:
        return None, None
    
    # Remove k/K and replace with 000 for easier parsing
    s = salary_str.lower().replace('k', '000').replace(',', '')
    numbers = re.findall(r'\d+', s)
    
    if not numbers:
        return None, None
    
    try:
        nums = [int(n) for n in numbers]
        # Filter out unlikely salary numbers (e.g. years like 2024)
        nums = [n for n in nums if n > 10000] 
        
        if not nums:
            return None, None
            
        if len(nums) == 1:
            return nums[0], nums[0]
        
        return min(nums), max(nums)
    except:
        return None, None

def upgrade_schema():
    print("🚀 Starting Database Upgrade...")
    
    # 1. Connect to old DB to get data
    old_jobs = []
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            # Check if table exists
            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='jobs'")
            if c.fetchone():
                c.execute("SELECT * FROM jobs")
                old_jobs = [dict(row) for row in c.fetchall()]
            conn.close()
        except Exception as e:
            print(f"⚠️ Error reading old DB: {e}")

    # 2. Delete old DB file (since we have backup) and create fresh
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 3. Create New Tables
    print("🔧 Creating new schema...")
    
    # JOBS TABLE
    c.execute("""
        CREATE TABLE jobs (
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
        )
    """)
    
    # APPLICATIONS TABLE
    c.execute("""
        CREATE TABLE applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            applied_date DATE DEFAULT CURRENT_DATE,
            status TEXT DEFAULT 'Applied',
            notes TEXT,
            FOREIGN KEY (job_id) REFERENCES jobs (id)
        )
    """)
    
    # INTERVIEWS TABLE
    c.execute("""
        CREATE TABLE interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER NOT NULL,
            interview_date DATETIME,
            type TEXT,
            notes TEXT,
            FOREIGN KEY (application_id) REFERENCES applications (id)
        )
    """)
    
    # 4. Migrate Data
    print(f"📦 Migrating {len(old_jobs)} jobs...")
    count = 0
    app_count = 0
    
    for j in old_jobs:
        try:
            # Parse Salary
            salary_txt = j.get('salary', '') or j.get('salary_range', '')
            min_sal, max_sal = parse_salary(salary_txt)
            
            # Insert Job
            c.execute("""
                INSERT INTO jobs (
                    title, company, url, match_score, tier,
                    salary_min, salary_max, salary_text, location,
                    search_type, description, requirements, red_flags,
                    company_overview, role_insights, interview_prep, talking_points,
                    date_added, status, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                j.get('title'), j.get('company'), j.get('url'), j.get('match_score'), j.get('tier', 3),
                min_sal, max_sal, salary_txt, j.get('location'),
                j.get('search_type', 'corporate'), j.get('full_description') or j.get('description'), 
                j.get('key_requirements') or j.get('requirements'), j.get('red_flags'),
                j.get('company_overview'), j.get('role_insights'), j.get('interview_prep'), j.get('talking_points'),
                j.get('date_added') or j.get('first_seen', datetime.now().strftime('%Y-%m-%d')),
                j.get('status', 'New'), j.get('notes')
            ))
            
            job_id = c.lastrowid
            
            # Create Application if needed
            status = j.get('status', 'New').lower()
            if status in ['applied', 'interview', 'offer', 'rejected']:
                c.execute("""
                    INSERT INTO applications (job_id, status, applied_date)
                    VALUES (?, ?, ?)
                """, (job_id, j.get('status'), datetime.now().strftime('%Y-%m-%d')))
                app_count += 1
                
            count += 1
            
        except Exception as e:
            print(f"❌ Failed to migrate {j.get('company')}: {e}")
            
    conn.commit()
    conn.close()
    print(f"✅ Upgrade Complete!")
    print(f"   - Jobs Migrated: {count}")
    print(f"   - Applications Created: {app_count}")

if __name__ == "__main__":
    backup_db()
    upgrade_schema()
