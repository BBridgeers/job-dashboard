#!/usr/bin/env python3
"""
FIXED Parser - Jobs are INSIDE <think> block, not after it
"""

import sqlite3
import re
from pathlib import Path
from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def extract_section_2_jobs(content):
    """Extract TOP jobs from SECTION 2 (inside <think> block)"""

    jobs = []

    # Find SECTION 2
    section2_match = re.search(r'SECTION 2[:\s]+STRATEGIC ANALYSIS(.+)', content, re.DOTALL | re.IGNORECASE)
    if not section2_match:
        return jobs

    section2_content = section2_match.group(1)

    # DON'T skip <think> block - the jobs are inside it!
    # Just use the full SECTION 2 content

    # Split by **Job #X:** format
    job_blocks = re.split(r'\*\*Job #(\d+):', section2_content)

    print(f"   DEBUG: Found {len(job_blocks)} blocks after split")

    # Process each job (blocks come in pairs: number, then content)
    for i in range(1, len(job_blocks), 2):
        if i+1 >= len(job_blocks):
            break

        job_num = job_blocks[i]
        block = job_blocks[i+1]

        if len(block.strip()) < 100:
            continue

        job = {}

        # Extract title (immediately after Job #X:, before next **)
        title_match = re.search(r'^([^\*\n]+)\*\*', block)
        if title_match:
            job['title'] = title_match.group(1).strip()

        if not job.get('title'):
            continue

        print(f"   DEBUG: Processing Job #{job_num}: {job['title'][:40]}")

        # Extract all sections - look for lines starting with "- "

        # Detailed Company Analysis
        company_match = re.search(r'-\s*Detailed [Cc]ompany [Aa]nalysis[:\s]*(.+?)(?=\n\s*-\s*[A-Z]|\*\*Job|$)', block, re.DOTALL | re.IGNORECASE)
        if company_match:
            job['company_overview'] = company_match.group(1).strip()
            print(f"      ✓ Company overview: {len(job['company_overview'])} chars")

        # Role-Specific Insights
        role_match = re.search(r'-\s*Role-[Ss]pecific [Ii]nsights[:\s]*(.+?)(?=\n\s*-\s*[A-Z]|\*\*Job|$)', block, re.DOTALL | re.IGNORECASE)
        if role_match:
            role_text = role_match.group(1).strip()
            job['why_this_role'] = role_text
            job['full_description'] = role_text
            print(f"      ✓ Role insights: {len(role_text)} chars")

            # Extract requirements from bullet points
            bullets = re.findall(r'[•●-]\s*(.+?)(?=\n|$)', role_text)
            if bullets:
                job['key_requirements'] = '\n'.join(bullets)

        # Interview Preparation
        interview_match = re.search(r'-\s*Interview [Pp]reparation[:\s]*(.+?)(?=\n\s*-\s*[A-Z]|\*\*Job|$)', block, re.DOTALL | re.IGNORECASE)
        if interview_match:
            job['interview_prep'] = interview_match.group(1).strip()
            print(f"      ✓ Interview prep: {len(job['interview_prep'])} chars")

        # Salary Negotiation
        salary_match = re.search(r'-\s*Salary [Nn]egotiation[:\s]*(.+?)(?=\n\s*-\s*[A-Z]|\*\*Job|$)', block, re.DOTALL | re.IGNORECASE)
        if salary_match:
            job['talking_points'] = salary_match.group(1).strip()
            print(f"      ✓ Salary negotiation: {len(job['talking_points'])} chars")

        # Application Strategy
        app_match = re.search(r'-\s*Application [Ss]trategy[:\s]*(.+?)(?=\n\s*-\s*[A-Z]|\*\*Job|$)', block, re.DOTALL | re.IGNORECASE)
        if app_match:
            app_text = app_match.group(1).strip()
            if job.get('talking_points'):
                job['talking_points'] += '\n\n' + app_text
            else:
                job['talking_points'] = app_text

        # Potential Red Flags
        red_match = re.search(r'-\s*Potential [Rr]ed [Ff]lags[:\s]*(.+?)(?=\n\s*-\s*[A-Z]|\*\*Job|</think>|$)', block, re.DOTALL | re.IGNORECASE)
        if red_match:
            job['red_flags'] = red_match.group(1).strip()
            print(f"      ✓ Red flags: {len(job['red_flags'])} chars")

        # Cultural Fit
        culture_match = re.search(r'-\s*Cultural [Ff]it[:\s]*(.+?)(?=\n\s*-\s*[A-Z]|\*\*Job|$)', block, re.DOTALL | re.IGNORECASE)
        if culture_match:
            culture_text = culture_match.group(1).strip()
            if job.get('why_this_role'):
                job['why_this_role'] += '\n\n' + culture_text
            else:
                job['why_this_role'] = culture_text

        jobs.append(job)

    return jobs

def migrate_fixed(db_path='jobs.db', txt_pattern='job_search_*.txt'):
    """Fixed migration - jobs are inside <think> block"""

    print("🎯 FIXED TXT Migration (jobs inside <think> block)")
    print("=" * 60)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, company FROM jobs")
    db_jobs = {row['id']: {'title': row['title'], 'company': row['company']} for row in cursor.fetchall()}

    print(f"📊 Found {len(db_jobs)} jobs in database\n")

    txt_files = sorted(Path('.').glob(txt_pattern))
    total_updated = 0

    for txt_file in txt_files:
        print(f"📄 {txt_file.name}")

        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()

        top_jobs = extract_section_2_jobs(content)
        print(f"\n   Extracted {len(top_jobs)} TOP jobs\n")

        for job in top_jobs:
            if not job.get('title'):
                continue

            # Fuzzy match to DB
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

                print(f"   ✅ MATCHED: {job['title'][:45]}")
                print(f"      Similarity: {best_sim:.0%} | Fields: {fields}/6\n")
                total_updated += 1
            else:
                print(f"   ⏭️  No DB match: {job['title'][:45]}\n")

        print()

    conn.commit()
    conn.close()

    print("=" * 60)
    print(f"✅ SUCCESS! Updated {total_updated} TOP jobs with rich data")
    print("=" * 60)

if __name__ == "__main__":
    migrate_fixed()