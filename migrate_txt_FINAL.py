#!/usr/bin/env python3
"""
FINAL PERFECT Parser - Matches EXACT section headers from your TXT files
Section 2 headers: Detailed Company Analysis, Role-Specific Insights, etc.
"""

import sqlite3
import re
from pathlib import Path
from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def extract_text_after_header(block, header_pattern):
    """Extract text after a specific header until next header"""
    match = re.search(header_pattern, block, re.IGNORECASE)
    if not match:
        return None

    start_pos = match.end()
    remaining = block[start_pos:]

    # Find next header (starts with "- " followed by capitalized words)
    next_header = re.search(r'\n\s*-\s+[A-Z][a-z]', remaining)
    if next_header:
        text = remaining[:next_header.start()]
    else:
        text = remaining

    return text.strip()

def extract_section_2_jobs(content):
    """Extract TOP jobs from SECTION 2 with exact header matching"""

    jobs = []

    # Find SECTION 2
    section2_match = re.search(r'SECTION 2[:\s]+(STRATEGIC ANALYSIS|TOP.+MATCHES)(.+)', content, re.DOTALL | re.IGNORECASE)
    if not section2_match:
        return jobs

    section2_content = section2_match.group(2)

    # Split by "Job #1:", "Job #2:", etc.
    job_blocks = re.split(r'\n\s*Job #(\d+):', section2_content)

    # Process each job (skip first empty block)
    for i in range(1, len(job_blocks), 2):
        if i+1 >= len(job_blocks):
            break

        job_num = job_blocks[i]
        block = job_blocks[i+1]

        if len(block.strip()) < 200:
            continue

        job = {}

        # Extract title (first non-empty line)
        lines = block.strip().split('\n')
        for line in lines[:5]:
            line = line.strip().replace('**', '')
            if line and '===' not in line and 'Company:' not in line:
                job['title'] = line
                break

        if not job.get('title'):
            continue

        # Extract Company
        company_match = re.search(r'Company:?\s*(.+?)(?:\n|$)', block, re.IGNORECASE)
        if company_match:
            job['company'] = company_match.group(1).strip()

        # Map TXT sections to database fields
        # 1. Detailed Company Analysis → company_overview
        company_analysis = extract_text_after_header(block, r'-\s*Detailed Company Analysis')
        if company_analysis:
            job['company_overview'] = company_analysis

        # 2. Role-Specific Insights → full_description or why_this_role
        role_insights = extract_text_after_header(block, r'-\s*Role-Specific Insights')
        if role_insights:
            job['why_this_role'] = role_insights
            job['full_description'] = role_insights  # Use same for both

        # 3. Key requirements might be in Role-Specific section or separate
        # Look for bullet points or "Requirements" in Role-Specific
        if role_insights:
            req_bullets = re.findall(r'(?:^|\n)\s*[•-]\s*(.+)', role_insights)
            if req_bullets:
                job['key_requirements'] = '\n'.join(req_bullets)

        # 4. Interview Preparation Tips → interview_prep
        interview_prep = extract_text_after_header(block, r'-\s*Interview Preparation')
        if interview_prep:
            job['interview_prep'] = interview_prep

        # 5. Salary Negotiation Intelligence → talking_points (negotiation is a talking point)
        salary_intel = extract_text_after_header(block, r'-\s*Salary Negotiation')
        if salary_intel:
            job['talking_points'] = salary_intel

        # 6. Application Strategy → talking_points (append if exists)
        app_strategy = extract_text_after_header(block, r'-\s*Application Strategy')
        if app_strategy:
            if job.get('talking_points'):
                job['talking_points'] += '\n\n' + app_strategy
            else:
                job['talking_points'] = app_strategy

        # 7. Potential Red Flags → red_flags
        red_flags = extract_text_after_header(block, r'-\s*Potential Red Flags')
        if red_flags:
            job['red_flags'] = red_flags

        # 8. Cultural Fit Assessment → why_this_role (append if exists)
        culture_fit = extract_text_after_header(block, r'-\s*Cultural Fit')
        if culture_fit:
            if job.get('why_this_role'):
                job['why_this_role'] += '\n\n' + culture_fit
            else:
                job['why_this_role'] = culture_fit

        jobs.append(job)

    return jobs

def migrate_final(db_path='jobs.db', txt_pattern='job_search_*.txt'):
    """Final perfect migration"""

    print("🎯 FINAL PERFECT TXT Migration")
    print("=" * 60)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

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
        print(f"📄 {txt_file.name}")

        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()

        top_jobs = extract_section_2_jobs(content)
        print(f"   Found {len(top_jobs)} TOP jobs with rich data\n")

        for job in top_jobs:
            if not job.get('title'):
                continue

            # Fuzzy match
            best_match_id = None
            best_sim = 0.0

            for db_id, db_job in db_jobs.items():
                sim = similarity(job['title'], db_job['title'])
                if sim > best_sim and sim > 0.5:
                    best_sim = sim
                    best_match_id = db_id

            if best_match_id:
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
                    job.get('full_description'),
                    job.get('key_requirements'),
                    job.get('company_overview'),
                    job.get('why_this_role'),
                    job.get('interview_prep'),
                    job.get('talking_points'),
                    job.get('red_flags'),
                    best_match_id
                ))

                fields = sum([
                    bool(job.get('full_description')),
                    bool(job.get('key_requirements')),
                    bool(job.get('company_overview')),
                    bool(job.get('interview_prep')),
                    bool(job.get('talking_points')),
                    bool(job.get('red_flags'))
                ])

                print(f"   ✅ {job['title'][:50]}")
                print(f"      Match: {best_sim:.0%} | Rich fields: {fields}/6")
                total_updated += 1
            else:
                print(f"   ⏭️  No match: {job['title'][:50]}")

        print()

    conn.commit()
    conn.close()

    print("=" * 60)
    print(f"✅ Updated {total_updated} TOP jobs with rich data")
    print("=" * 60)

if __name__ == "__main__":
    migrate_final()