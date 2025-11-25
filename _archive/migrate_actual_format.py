#!/usr/bin/env python3

"""
Strategic Match - Parser for Actual Perplexity Format (FIXED)
Handles first_seen column requirement
"""

import sqlite3
import re
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def extract_tier1_jobs(content):
    """Extract Tier 1 jobs from bullet format"""
    jobs = []

    # Find TOP 5 MATCHES section
    tier1_match = re.search(r'TOP 5 MATCHES.*?POSITIONS 6-10', content, re.DOTALL | re.IGNORECASE)
    if not tier1_match:
        return jobs

    tier1_section = tier1_match.group(0)

    # Split by job number (1., 2., 3., etc.)
    job_pattern = r'\n(\d+)\. (.+?)\n'
    job_matches = list(re.finditer(job_pattern, tier1_section))

    for i, match in enumerate(job_matches):
        job_num = match.group(1)
        title = match.group(2).strip()

        # Get content until next job or section end
        start_pos = match.end()
        if i < len(job_matches) - 1:
            end_pos = job_matches[i+1].start()
        else:
            end_pos = len(tier1_section)

        block = tier1_section[start_pos:end_pos]

        job = {
            'title': title,
            'tier': 1
        }

        # Extract match score
        score_match = re.search(r'Match Score:\s*(\d+)', block)
        if score_match:
            job['match_score'] = score_match.group(1)

        # Extract salary
        salary_match = re.search(r'Salary:\s*(.+?)\n', block)
        if salary_match:
            job['salary_range'] = salary_match.group(1).strip()

        # Extract location
        loc_match = re.search(r'Location:\s*(.+?)\n', block)
        if loc_match:
            job['location'] = loc_match.group(1).strip()

        # Extract company overview
        overview_match = re.search(r'Company Overview:\s*(.+?)\n\s*-\s*Role', block, re.DOTALL)
        if overview_match:
            job['company_overview'] = overview_match.group(1).strip()

        # Extract role insights
        role_match = re.search(r'Role Insights:\s*(.+?)\n\s*-\s*Key', block, re.DOTALL)
        if role_match:
            job['why_this_role'] = role_match.group(1).strip()
            job['full_description'] = role_match.group(1).strip()

        # Extract key requirements
        req_match = re.search(r'Key Requirements:\s*(.+?)\n\s*-\s*URL', block, re.DOTALL)
        if req_match:
            job['key_requirements'] = req_match.group(1).strip()

        # Extract URL
        url_match = re.search(r'URL:\s*(.+?)(?:\n|$)', block)
        if url_match:
            job['url'] = url_match.group(1).strip()

        jobs.append(job)

    return jobs

def extract_tier2_jobs(content):
    """Extract Tier 2 jobs from bullet format"""
    jobs = []

    # Find POSITIONS 6-10 section
    tier2_match = re.search(r'POSITIONS 6-10.*?(?:ALL OTHER|SECTION 2|$)', content, re.DOTALL | re.IGNORECASE)
    if not tier2_match:
        return jobs

    tier2_section = tier2_match.group(0)

    # Split by job number
    job_pattern = r'\n(\d+)\. (.+?)\n'
    job_matches = list(re.finditer(job_pattern, tier2_section))

    for i, match in enumerate(job_matches):
        job_num = int(match.group(1))
        if job_num < 6 or job_num > 10:
            continue

        title = match.group(2).strip()

        start_pos = match.end()
        if i < len(job_matches) - 1:
            end_pos = job_matches[i+1].start()
        else:
            end_pos = len(tier2_section)

        block = tier2_section[start_pos:end_pos]

        job = {
            'title': title,
            'tier': 2
        }

        # Extract fields same as Tier 1
        score_match = re.search(r'Match Score:\s*(\d+)', block)
        if score_match:
            job['match_score'] = score_match.group(1)

        salary_match = re.search(r'Salary:\s*(.+?)\n', block)
        if salary_match:
            job['salary_range'] = salary_match.group(1).strip()

        loc_match = re.search(r'Location:\s*(.+?)\n', block)
        if loc_match:
            job['location'] = loc_match.group(1).strip()

        overview_match = re.search(r'Company Overview:\s*(.+?)\n\s*-\s*Role', block, re.DOTALL)
        if overview_match:
            job['company_overview'] = overview_match.group(1).strip()

        role_match = re.search(r'Role Insights:\s*(.+?)\n\s*-\s*Key', block, re.DOTALL)
        if role_match:
            job['why_this_role'] = role_match.group(1).strip()

        req_match = re.search(r'Key Requirements:\s*(.+?)\n\s*-\s*URL', block, re.DOTALL)
        if req_match:
            job['key_requirements'] = req_match.group(1).strip()

        url_match = re.search(r'URL:\s*(.+?)(?:\n|$)', block)
        if url_match:
            job['url'] = url_match.group(1).strip()

        jobs.append(job)

    return jobs

def extract_tier3_jobs(content):
    """Extract Tier 3 jobs (basic list)"""
    jobs = []

    tier3_match = re.search(r'ALL OTHER MATCHES.*?(?:SECTION 2|$)', content, re.DOTALL | re.IGNORECASE)
    if not tier3_match:
        return jobs

    tier3_section = tier3_match.group(0)

    # Pattern: 11. Title - Company - Match: Score
    job_pattern = r'(\d+)\. (.+?) - (.+?) - Match: (\d+)'
    matches = re.finditer(job_pattern, tier3_section)

    for match in matches:
        job_num = int(match.group(1))
        if job_num < 11:
            continue

        jobs.append({
            'title': match.group(2).strip(),
            'company': match.group(3).strip(),
            'match_score': match.group(4),
            'tier': 3
        })

    return jobs

def migrate_actual_format(db_path='jobs.db', results_dir='job_search_results'):
    """Migrate actual Perplexity output format"""
    print("🎯 Strategic Match - Actual Format Parser")
    print("=" * 60)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, company FROM jobs")
    db_jobs = {row['id']: {'title': row['title'], 'company': row['company']} for row in cursor.fetchall()}

    print(f"📊 Database has {len(db_jobs)} jobs\n")

    results_path = Path(results_dir)
    txt_files = sorted(results_path.glob('job_search_*_2025-11-18.txt'))
    print(f"Found {len(txt_files)} TXT files from today\n")

    total_updated = 0
    total_inserted = 0

    for txt_file in txt_files:
        print(f"📄 {txt_file.name}")

        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()

        search_type = 'nonprofit' if 'nonprofit' in txt_file.name.lower() else 'corporate'

        tier1_jobs = extract_tier1_jobs(content)
        tier2_jobs = extract_tier2_jobs(content)
        tier3_jobs = extract_tier3_jobs(content)

        all_jobs = tier1_jobs + tier2_jobs + tier3_jobs

        print(f"  Tier 1: {len(tier1_jobs)} | Tier 2: {len(tier2_jobs)} | Tier 3: {len(tier3_jobs)}\n")

        for job in all_jobs:
            if not job.get('title'):
                continue

            # Extract company from title if not present
            if not job.get('company'):
                title_parts = job['title'].split('–')
                if len(title_parts) >= 2:
                    job['company'] = title_parts[-1].strip()

            # Fuzzy match
            best_match_id = None
            best_sim = 0.0

            for db_id, db_job in db_jobs.items():
                sim = similarity(job['title'], db_job['title'])
                if sim > best_sim and sim > 0.5:
                    best_sim = sim
                    best_match_id = db_id

            tier = job.get('tier', 3)
            today = datetime.now().strftime('%Y-%m-%d')

            if best_match_id:
                # Update existing
                cursor.execute("""
                    UPDATE jobs SET
                        salary_range = COALESCE(?, salary_range),
                        location = COALESCE(?, location),
                        company_overview = COALESCE(?, company_overview),
                        why_this_role = COALESCE(?, why_this_role),
                        key_requirements = COALESCE(?, key_requirements),
                        full_description = COALESCE(?, full_description),
                        url = COALESCE(?, url),
                        tier = ?,
                        date_added = ?,
                        last_seen = ?,
                        search_type = ?,
                        is_top_match = CASE WHEN ? = 1 THEN 1 ELSE is_top_match END
                    WHERE id = ?
                """, (
                    job.get('salary_range'),
                    job.get('location'),
                    job.get('company_overview'),
                    job.get('why_this_role'),
                    job.get('key_requirements'),
                    job.get('full_description'),
                    job.get('url'),
                    tier,
                    today,
                    today,
                    search_type,
                    tier,
                    best_match_id
                ))

                print(f"  ✅ Updated Tier {tier}: {job['title'][:40]}")
                total_updated += 1
            else:
                # Insert new - include first_seen
                cursor.execute("""
                    INSERT INTO jobs (
                        title, company, job_type, match_score, tier, date_added, 
                        first_seen, last_seen, search_type, salary_range, location, 
                        company_overview, why_this_role, key_requirements, full_description, 
                        url, status, is_top_match
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'New', ?)
                """, (
                    job.get('title'),
                    job.get('company', 'Unknown'),
                    search_type.capitalize(),
                    job.get('match_score', 0),
                    tier,
                    today,
                    today,  # first_seen
                    today,  # last_seen
                    search_type,
                    job.get('salary_range'),
                    job.get('location'),
                    job.get('company_overview'),
                    job.get('why_this_role'),
                    job.get('key_requirements'),
                    job.get('full_description'),
                    job.get('url'),
                    1 if tier == 1 else 0
                ))

                print(f"  ✨ Inserted Tier {tier}: {job['title'][:40]}")
                total_inserted += 1

        print("-" * 60)

    conn.commit()
    conn.close()

    print("\n" + "=" * 60)
    print(f"🎉 Updated: {total_updated} | Inserted: {total_inserted}")
    print("=" * 60)

if __name__ == "__main__":
    migrate_actual_format()
