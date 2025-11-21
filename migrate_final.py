#!/usr/bin/env python3
"""
Strategic Match - HARMONIZED MIGRATION PARSER
Aligned with 'SECTION 2' Rich Data Format
"""
import sqlite3
import re
import os
import glob
from datetime import datetime
from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def parse_rich_data(content):
    """Extract rich data blocks from SECTION 2"""
    rich_jobs = []

    # Find all "---START_JOB_X--- ... ---END_JOB_X---" blocks
    blocks = re.findall(r'---START_JOB_\d+---(.*?)---END_JOB_\d+---', content, re.DOTALL)

    for block in blocks:
        job = {}

        # Extract Title/Company for matching
        t_m = re.search(r'TITLE:\s*(.+)', block)
        c_m = re.search(r'COMPANY:\s*(.+)', block)
        if t_m: job['title'] = t_m.group(1).strip()
        if c_m: job['company'] = c_m.group(1).strip()

        # Extract Fields using exact markers
        markers = {
            'company_overview': r'---COMPANY_OVERVIEW---\s*(.*?)\s*(?=---)',
            'role_insights': r'---ROLE_INSIGHTS---\s*(.*?)\s*(?=---)',
            'key_requirements': r'---KEY_REQUIREMENTS---\s*(.*?)\s*(?=---)',
            'interview_prep': r'---INTERVIEW_PREP---\s*(.*?)\s*(?=---)',
            'talking_points': r'---WHY_THIS_ROLE---\s*(.*?)\s*(?=---)', # Mapping Why -> Talking/Why
            'red_flags': r'---RED_FLAGS---\s*(.*?)\s*(?=---)',
            'full_description': r'---FULL_DESCRIPTION---\s*(.*?)\s*(?=---)'
        }

        for field, regex in markers.items():
            match = re.search(regex, block, re.DOTALL)
            if match:
                job[field] = match.group(1).strip()
            else:
                job[field] = ""

        if 'title' in job:
            rich_jobs.append(job)

    return rich_jobs

def migrate():
    print("🚀 Starting End-to-End Harmonized Migration...")

    # Initialize DB
    conn = sqlite3.connect('jobs.db')
    cursor = conn.cursor()

    # Ensure schema exists
    cursor.execute("""CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY,
        title TEXT, company TEXT, location TEXT, salary_range TEXT, url TEXT, 
        match_score INTEGER, tier INTEGER, status TEXT, date_added TEXT,
        company_overview TEXT, why_this_role TEXT, interview_prep TEXT, 
        talking_points TEXT, red_flags TEXT, key_requirements TEXT, full_description TEXT,
        search_type TEXT
    )""")

    all_jobs = []
    files = glob.glob("job_search_results/*.txt")

    for filepath in files:
        print(f"📂 Parsing: {filepath}")
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # 1. Parse Rich Data (Section 2)
        rich_data_list = parse_rich_data(content)

        # 2. Parse Standard Jobs (Section 1 / Basic List)
        # Look for numbered list items: "1. **Title** - Company"
        matches = re.findall(r'(?:^|\n)(\d+)\.\s*\*\*([^\*]+)\*\*\s*-\s*([^\n]+)', content)

        for _, title, rest in matches:
            job = {}
            job['title'] = title.strip()

            # Parse Company & Match from "Company - Match: 95"
            if "Match:" in rest:
                parts = rest.split("Match:")
                job['company'] = parts[0].strip(" -")
                try:
                    score_str = re.search(r'(\d+)', parts[1])
                    job['match_score'] = int(score_str.group(1)) if score_str else 0
                except:
                    job['match_score'] = 0
            else:
                job['company'] = rest.strip()
                job['match_score'] = 0

            # Default fields
            job['location'] = "See details"
            job['salary_range'] = "See details"
            job['url'] = ""
            job['status'] = 'to_apply'
            job['date_added'] = datetime.now().strftime("%Y-%m-%d")

            # 3. Merge Rich Data if available
            # Find best match in rich_data_list
            best_match = None
            best_score = 0.0

            for rich in rich_data_list:
                score = similarity(job['title'], rich['title']) + similarity(job['company'], rich['company'])
                if score > 1.6: # High confidence match
                    best_match = rich
                    break

            if best_match:
                # Merge fields
                job.update(best_match)

            all_jobs.append(job)

    # 4. SORT BY MATCH SCORE (Global Ranking)
    all_jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)

    # 5. ASSIGN TIERS & INSERT
    print(f"📊 Processing {len(all_jobs)} total jobs...")

    # Clear old data to prevent duplicates/conflicts during this heavy dev phase
    # cursor.execute("DELETE FROM jobs") 

    count = 0
    for i, job in enumerate(all_jobs):
        rank = i + 1
        if rank <= 5: job['tier'] = 1
        elif rank <= 10: job['tier'] = 2
        else: job['tier'] = 3

        # Upsert based on Title+Company
        cursor.execute("SELECT id FROM jobs WHERE title = ? AND company = ?", (job['title'], job['company']))
        exists = cursor.fetchone()

        if exists:
            # Update existing
            cursor.execute("""
                UPDATE jobs SET 
                tier=?, match_score=?, company_overview=?, interview_prep=?, 
                talking_points=?, red_flags=?, key_requirements=?, full_description=?
                WHERE id=?
            """, (
                job['tier'], job['match_score'], 
                job.get('company_overview',''), job.get('interview_prep',''),
                job.get('talking_points',''), job.get('red_flags',''),
                job.get('key_requirements',''), job.get('full_description',''),
                exists[0]
            ))
        else:
            # Insert new
            cursor.execute("""
                INSERT INTO jobs (
                    title, company, location, salary_range, url, match_score, 
                    tier, status, date_added, 
                    company_overview, interview_prep, talking_points, red_flags, 
                    key_requirements, full_description
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job['title'], job['company'], job['location'], job['salary_range'], 
                job['url'], job['match_score'], job['tier'], 'to_apply', job['date_added'],
                job.get('company_overview',''), job.get('interview_prep',''),
                job.get('talking_points',''), job.get('red_flags',''),
                job.get('key_requirements',''), job.get('full_description','')
            ))
        count += 1

    conn.commit()
    conn.close()
    print(f"✅ END-TO-END MIGRATION SUCCESS: {count} jobs aligned.")

if __name__ == "__main__":
    migrate()
