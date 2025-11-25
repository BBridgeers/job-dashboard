#!/usr/bin/env python3

"""
UNIVERSAL Parser - Handles ALL file formats (Nov 13, 14, 17+)
"""

import sqlite3
import re
from pathlib import Path
from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def extract_jobs_format_new(content):
    """Format: ## 1. Job Title (Match Score: 98)"""
    jobs = []

    section2_match = re.search(r'SECTION 2[:\s]+STRATEGIC ANALYSIS(.+)', content, re.DOTALL | re.IGNORECASE)
    if not section2_match:
        return jobs

    section2_content = section2_match.group(1)
    job_blocks = re.split(r'##\s+(\d+)\.\s+(.+?)\s+\(Match Score:\s+(\d+)\)', section2_content)

    for i in range(1, len(job_blocks), 4):
        if i+3 >= len(job_blocks):
            break

        job_num = job_blocks[i]
        job_title = job_blocks[i+1].strip()
        match_score = job_blocks[i+2]
        block = job_blocks[i+3]

        if len(block.strip()) < 100:
            continue

        job = {'title': job_title}
        end_pattern = r'(?=\n\*\*[A-Z]|\n##\s+\d+\.|</think>|\Z)'

        # Extract all sections
        company_match = re.search(r'\*\*Detailed Company Analysis\*\*\s*\n(.+?)' + end_pattern, block, re.DOTALL | re.IGNORECASE)
        if company_match:
            job['company_overview'] = company_match.group(1).strip()

        role_match = re.search(r'\*\*Role-Specific Insights\*\*\s*\n(.+?)' + end_pattern, block, re.DOTALL | re.IGNORECASE)
        if role_match:
            role_text = role_match.group(1).strip()
            job['why_this_role'] = role_text
            job['full_description'] = role_text
            bullets = re.findall(r'[-•]\s*(.+?)(?=\n|$)', role_text)
            if bullets:
                job['key_requirements'] = '\n'.join(bullets)

        interview_match = re.search(r'\*\*Interview Preparation Tips\*\*\s*\n(.+?)' + end_pattern, block, re.DOTALL | re.IGNORECASE)
        if interview_match:
            job['interview_prep'] = interview_match.group(1).strip()

        salary_match = re.search(r'\*\*Salary Negotiation Intelligence\*\*\s*\n(.+?)' + end_pattern, block, re.DOTALL | re.IGNORECASE)
        if salary_match:
            job['talking_points'] = salary_match.group(1).strip()

        app_match = re.search(r'\*\*Application Strategy\*\*\s*\n(.+?)' + end_pattern, block, re.DOTALL | re.IGNORECASE)
        if app_match:
            app_text = app_match.group(1).strip()
            if job.get('talking_points'):
                job['talking_points'] += '\n\n**Application Strategy**\n' + app_text
            else:
                job['talking_points'] = app_text

        red_match = re.search(r'\*\*Potential Red Flags\*\*\s*\n(.+?)' + end_pattern, block, re.DOTALL | re.IGNORECASE)
        if red_match:
            job['red_flags'] = red_match.group(1).strip()

        culture_match = re.search(r'\*\*Cultural Fit Assessment\*\*\s*\n(.+?)' + end_pattern, block, re.DOTALL | re.IGNORECASE)
        if culture_match:
            culture_text = culture_match.group(1).strip()
            if job.get('why_this_role'):
                job['why_this_role'] += '\n\n**Cultural Fit**\n' + culture_text
            else:
                job['why_this_role'] = culture_text

        jobs.append(job)

    return jobs

def extract_jobs_format_old(content):
    """Format: ## JOB 3: Job Title"""
    jobs = []

    section2_match = re.search(r'SECTION 2[:\s]+(.+)', content, re.DOTALL | re.IGNORECASE)
    if not section2_match:
        return jobs

    section2_content = section2_match.group(1)
    job_blocks = re.split(r'##\s+JOB\s+(\d+):\s+(.+?)\n', section2_content)

    for i in range(1, len(job_blocks), 3):
        if i+2 >= len(job_blocks):
            break

        job_num = job_blocks[i]
        job_title = job_blocks[i+1].strip()
        block = job_blocks[i+2]

        if len(block.strip()) < 100:
            continue

        job = {'title': job_title}

        # Extract basic info from ## JOB format
        brief_match = re.search(r'\*\*Brief:\*\*(.+?)(?=\n\*\*|$)', block, re.DOTALL)
        if brief_match:
            job['full_description'] = brief_match.group(1).strip()

        jobs.append(job)

    return jobs

def migrate_universal(db_path='jobs.db', results_dir='job_search_results'):
    """Universal migration - handles all file formats"""
    print("🎯 UNIVERSAL Migration (ALL formats supported)")
    print("=" * 60)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, company FROM jobs")
    db_jobs = {row['id']: {'title': row['title'], 'company': row['company']} for row in cursor.fetchall()}

    print(f"📊 Database has {len(db_jobs)} jobs\n")

    results_path = Path(results_dir)
    if not results_path.exists():
        print(f"❌ Directory not found: {results_dir}")
        return

    txt_files = sorted(results_path.glob('job_search_*.txt'))
    print(f"Found {len(txt_files)} TXT files\n")

    total_updated = 0

    for txt_file in txt_files:
        print(f"📄 {txt_file.name}")

        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Try new format first
        top_jobs = extract_jobs_format_new(content)
        if not top_jobs:
            # Try old format
            top_jobs = extract_jobs_format_old(content)

        print(f"  Extracted {len(top_jobs)} jobs\n")

        for job in top_jobs:
            if not job.get('title'):
                continue

            # Count fields
            fields = sum([
                bool(job.get('full_description')),
                bool(job.get('key_requirements')),
                bool(job.get('company_overview')),
                bool(job.get('interview_prep')),
                bool(job.get('talking_points')),
                bool(job.get('red_flags'))
            ])

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

                print(f"  ✅ {job['title'][:40]} | Match: {best_sim:.0%} | Fields: {fields}/6")
                total_updated += 1
            else:
                print(f"  ⏭️  {job['title'][:40]} | Fields: {fields}/6")

        print("-" * 60)

    conn.commit()
    conn.close()

    print("\n" + "=" * 60)
    print(f"🎉 Updated {total_updated} jobs")
    print("=" * 60)

if __name__ == "__main__":
    migrate_universal()
