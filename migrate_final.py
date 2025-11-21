#!/usr/bin/env python3
"""
Strategic Match - ROBUST MIGRATION PARSER
Fixed to catch data even if formatting is slightly off.
"""
import sqlite3
import re
import glob
from datetime import datetime

def clean_text(text):
    if not text: return ""
    return text.strip().strip('[]').strip()

def parse_file(content):
    jobs = []

    # SPLIT BY JOB BLOCKS (Robust splitting)
    # We look for "1. **Title**" pattern or "---START_JOB"

    # STRATEGY: First, try to extract the "SECTION 2" rich blocks because they have the ID mapping
    rich_blocks = re.split(r'---START_JOB_\d+---', content)

    rich_data_map = {}
    for block in rich_blocks[1:]: # Skip preamble
        # Extract Title to link back
        title_match = re.search(r'TITLE:\s*(.+)', block)
        if title_match:
            title_key = title_match.group(1).strip().lower()[:20] # First 20 chars of title as key

            rich_data = {}
            # Extract all fields using loose matching
            patterns = {
                'company_overview': r'---COMPANY_OVERVIEW---\s*(.*?)(?=\n---|---ROLE|\Z)',
                'role_insights': r'---ROLE_INSIGHTS---\s*(.*?)(?=\n---|---KEY|\Z)',
                'key_requirements': r'---KEY_REQUIREMENTS---\s*(.*?)(?=\n---|---INT|\Z)',
                'interview_prep': r'---INTERVIEW_PREP---\s*(.*?)(?=\n---|---SAL|\Z)',
                'talking_points': r'---WHY_THIS_ROLE---\s*(.*?)(?=\n---|---FUL|\Z)', # Mapping Why -> Talk
                'red_flags': r'---RED_FLAGS---\s*(.*?)(?=\n---|---CUL|\Z)',
                'full_description': r'---FULL_DESCRIPTION---\s*(.*?)(?=\n---|---END|\Z)'
            }

            for field, pat in patterns.items():
                m = re.search(pat, block, re.DOTALL)
                if m: rich_data[field] = m.group(1).strip()

            rich_data_map[title_key] = rich_data

    # NOW PARSE THE LISTINGS (Section 1)
    # Pattern: "1. **Title** - Company"
    listing_pattern = r'(\d+)\.\s*\*\*([^\*]+)\*\*\s*-\s*([^\n]+)'
    matches = re.findall(listing_pattern, content)

    for rank, title, rest in matches:
        job = {}
        job['title'] = title.strip()

        # Parse Company, Match, Location, URL from the lines following the title
        # We need to find where this listing starts in the text to look ahead
        start_idx = content.find(f"{rank}. **{title}**")
        end_idx = content.find(f"{int(rank)+1}. **", start_idx)
        if end_idx == -1: end_idx = len(content)

        job_block = content[start_idx:end_idx]

        # Company
        if "Match:" in rest:
            job['company'] = rest.split("Match:")[0].strip(" -")
            ms = re.search(r'Match:.*?(\d+)', rest)
            job['match_score'] = int(ms.group(1)) if ms else 0
        else:
            job['company'] = rest.strip()
            job['match_score'] = 0

        # Location
        loc_m = re.search(r'Location:\s*([^\n]+)', job_block)
        job['location'] = loc_m.group(1).strip() if loc_m else "See details"

        # URL (CRITICAL)
        url_m = re.search(r'URL:\s*([^\n]+)', job_block)
        # Clean URL (remove brackets or markdown links)
        raw_url = url_m.group(1).strip() if url_m else "#"
        if "(" in raw_url and ")" in raw_url:
            raw_url = raw_url.split("(")[-1].strip(")")
        job['url'] = raw_url

        # Salary
        sal_m = re.search(r'Salary:\s*([^\n]+)', job_block)
        job['salary'] = sal_m.group(1).strip() if sal_m else "Not listed"

        # MERGE RICH DATA
        t_key = job['title'].lower()[:20]
        if t_key in rich_data_map:
            job.update(rich_data_map[t_key])
            job['tier'] = 1 # If it has rich data, it's tier 1
        else:
            job['tier'] = 3 if int(rank) > 10 else 2

        jobs.append(job)

    return jobs

def migrate():
    print("🚀 STARTING ROBUST DATA MIGRATION...")
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()

    # Create table
    c.execute("""CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY,
        title TEXT, company TEXT, location TEXT, url TEXT,
        match_score INTEGER, tier INTEGER, status TEXT, date_added TEXT,
        company_overview TEXT, role_insights TEXT, key_requirements TEXT,
        interview_prep TEXT, talking_points TEXT, red_flags TEXT, full_description TEXT,
        notes TEXT, application_url TEXT, search_type TEXT
    )""")

    # Process files
    files = sorted(glob.glob("job_search_results/*.txt"))
    total_imported = 0

    for fpath in files:
        print(f"📂 Reading {fpath}...")
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        jobs = parse_file(content)
        search_type = 'Corporate' if 'corporate' in fpath.lower() else 'Nonprofit'

        for j in jobs:
            # Upsert
            c.execute("SELECT id FROM jobs WHERE title = ? AND company = ?", (j['title'], j['company']))
            exists = c.fetchone()

            if exists:
                # Update rich fields if present
                if j.get('company_overview'):
                    c.execute("""UPDATE jobs SET 
                        tier=1, company_overview=?, role_insights=?, key_requirements=?,
                        interview_prep=?, talking_points=?, red_flags=?, full_description=?, url=?
                        WHERE id=?""", (
                        j.get('company_overview'), j.get('role_insights'), j.get('key_requirements'),
                        j.get('interview_prep'), j.get('talking_points'), j.get('red_flags'),
                        j.get('full_description'), j.get('url'), exists[0]
                    ))
            else:
                c.execute("""INSERT INTO jobs (
                    title, company, location, url, match_score, tier, status, date_added,
                    company_overview, role_insights, key_requirements, interview_prep,
                    talking_points, red_flags, full_description, search_type
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
                    j['title'], j['company'], j['location'], j['url'], j['match_score'],
                    j['tier'], 'New', datetime.now().strftime("%Y-%m-%d"),
                    j.get('company_overview'), j.get('role_insights'), j.get('key_requirements'),
                    j.get('interview_prep'), j.get('talking_points'), j.get('red_flags'),
                    j.get('full_description'), search_type
                ))
                total_imported += 1

    conn.commit()
    conn.close()
    print(f"✅ Migration Complete. Imported/Updated {total_imported} jobs.")

if __name__ == "__main__":
    migrate()
