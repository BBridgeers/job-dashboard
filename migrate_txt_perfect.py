#!/usr/bin/env python3
"""
PERFECT TXT Parser - Handles SECTION 1 (brief) and SECTION 2 (rich data)
Matches your exact job search TXT file format
"""

import sqlite3
import re
from pathlib import Path
from difflib import SequenceMatcher

def similarity(a, b):
    """Calculate similarity between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def extract_section_2_jobs(content):
    """Extract TOP 3 jobs with rich 11-component data from SECTION 2"""

    jobs = []

    # Find SECTION 2
    section2_match = re.search(r'SECTION 2[:\s]+STRATEGIC ANALYSIS(.+)', content, re.DOTALL | re.IGNORECASE)
    if not section2_match:
        print("  ⚠️  No SECTION 2 found in file")
        return jobs

    section2_content = section2_match.group(1)

    # Split by "Job #1:", "Job #2:", "Job #3:"
    job_blocks = re.split(r'Job #\d+:', section2_content)

    for block in job_blocks[1:]:  # Skip first empty block
        if len(block.strip()) < 200:
            continue

        job = {}
        lines = block.strip().split('\n')

        # Extract title (first line after "Job #X:")
        for line in lines[:5]:
            if line.strip() and '===' not in line:
                job['title'] = line.strip().replace('**', '')
                break

        if not job.get('title'):
            continue

        # Extract company
        company_match = re.search(r'Company:?\s*\*\*?(.+?)\*\*?', block, re.IGNORECASE)
        if company_match:
            job['company'] = company_match.group(1).strip()

        # Extract Description / Why This Role
        desc_match = re.search(r'(?:Description|Why This Role|Overview):(.+?)(?=Key Requirements|Qualifications|Company Overview|$)', block, re.DOTALL | re.IGNORECASE)
        if desc_match:
            job['full_description'] = desc_match.group(1).strip()

        # Extract Requirements
        req_match = re.search(r'(?:Key Requirements|Qualifications):(.+?)(?=Company Overview|Why This Role|Interview Prep|$)', block, re.DOTALL | re.IGNORECASE)
        if req_match:
            job['key_requirements'] = req_match.group(1).strip()

        # Extract Company Overview
        company_match = re.search(r'Company Overview:(.+?)(?=Why This Role|Interview Prep|Talking Points|$)', block, re.DOTALL | re.IGNORECASE)
        if company_match:
            job['company_overview'] = company_match.group(1).strip()

        # Extract Why This Role (alternative location)
        if not job.get('full_description'):
            why_match = re.search(r'Why This Role:(.+?)(?=Key Requirements|Interview Prep|$)', block, re.DOTALL | re.IGNORECASE)
            if why_match:
                job['why_this_role'] = why_match.group(1).strip()

        # Extract Interview Prep
        interview_match = re.search(r'Interview Prep(?:aration)?:(.+?)(?=Talking Points|Red Flags|Job #|$)', block, re.DOTALL | re.IGNORECASE)
        if interview_match:
            job['interview_prep'] = interview_match.group(1).strip()

        # Extract Talking Points
        talking_match = re.search(r'Talking Points:(.+?)(?=Red Flags|Considerations|Job #|$)', block, re.DOTALL | re.IGNORECASE)
        if talking_match:
            job['talking_points'] = talking_match.group(1).strip()

        # Extract Red Flags
        red_match = re.search(r'(?:Red Flags|Considerations):(.+?)(?=Job #|==|$)', block, re.DOTALL | re.IGNORECASE)
        if red_match:
            job['red_flags'] = red_match.group(1).strip()

        jobs.append(job)

    return jobs

def migrate_perfect(db_path='jobs.db', txt_pattern='job_search_*.txt'):
    """Perfect migration with exact format parsing"""

    print("🎯 PERFECT TXT Migration (Section 1 + Section 2)")
    print("=" * 60)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all jobs from DB
    cursor.execute("SELECT id, title, company FROM jobs")
    db_jobs = {row['id']: {'title': row['title'], 'company': row['company']} for row in cursor.fetchall()}

    print(f"📊 Found {len(db_jobs)} jobs in database\n")

    txt_files = sorted(Path('.').glob(txt_pattern))

    if not txt_files:
        print("⚠️  No TXT files found")
        conn.close()
        return

    total_updated = 0

    for txt_file in txt_files:
        print(f"📄 Processing: {txt_file.name}")

        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract TOP 3 jobs with rich data from SECTION 2
        top_jobs = extract_section_2_jobs(content)

        print(f"   Found {len(top_jobs)} TOP jobs with rich data\n")

        for job in top_jobs:
            if not job.get('title'):
                continue

            # Fuzzy match to DB
            best_match_id = None
            best_similarity = 0.0

            for db_id, db_job in db_jobs.items():
                title_sim = similarity(job['title'], db_job['title'])
                if title_sim > best_similarity and title_sim > 0.5:  # 50% threshold
                    best_similarity = title_sim
                    best_match_id = db_id

            if best_match_id:
                # Update with ALL available data
                cursor.execute("""
                    UPDATE jobs SET
                        full_description = COALESCE(?, full_description),
                        key_requirements = COALESCE(?, key_requirements),
                        company_overview = COALESCE(?, company_overview),
                        why_this_role = COALESCE(?, why_this_role),
                        interview_prep = COALESCE(?, interview_prep),
                        talking_points = COALESCE(?, talking_points),
                        red_flags = COALESCE(?, red_flags),
                        is_top_match = 1
                    WHERE id = ?
                """, (
                    job.get('full_description') or job.get('why_this_role'),
                    job.get('key_requirements'),
                    job.get('company_overview'),
                    job.get('why_this_role'),
                    job.get('interview_prep'),
                    job.get('talking_points'),
                    job.get('red_flags'),
                    best_match_id
                ))

                # Count how many fields were populated
                fields_added = sum([
                    bool(job.get('full_description') or job.get('why_this_role')),
                    bool(job.get('key_requirements')),
                    bool(job.get('company_overview')),
                    bool(job.get('interview_prep')),
                    bool(job.get('talking_points')),
                    bool(job.get('red_flags'))
                ])

                print(f"   ✅ {job['title'][:55]}")
                print(f"      Match: {best_similarity:.0%} | Added {fields_added}/6 rich fields")
                total_updated += 1
            else:
                print(f"   ⏭️  No DB match: {job['title'][:50]}")

        print()

    conn.commit()
    conn.close()

    print("=" * 60)
    print(f"✅ Migration complete! Updated {total_updated} TOP jobs with rich data")
    print("=" * 60)

if __name__ == "__main__":
    migrate_perfect()