#!/usr/bin/env python3
"""
FINAL WORKING Parser - Uses **Header** format (bold markdown)
"""

import sqlite3
import re
from pathlib import Path
from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def extract_section_2_jobs(content):
    """Extract TOP jobs with **Header** sections"""

    jobs = []

    # Find SECTION 2
    section2_match = re.search(r'SECTION 2[:\s]+STRATEGIC ANALYSIS(.+)', content, re.DOTALL | re.IGNORECASE)
    if not section2_match:
        return jobs

    section2_content = section2_match.group(1)

    # Split by **Job #X:**
    job_blocks = re.split(r'\*\*Job #(\d+):', section2_content)

    # Process each job
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

        print(f"   📋 Job #{job_num}: {job['title']}")

        # Extract sections using **Header** format

        # **Detailed Company Analysis**
        company_match = re.search(r'\*\*Detailed Company Analysis\*\*(.+?)(?=\n\*\*[A-Z]|$)', block, re.DOTALL | re.IGNORECASE)
        if company_match:
            job['company_overview'] = company_match.group(1).strip()
            print(f"      ✓ Company: {len(job['company_overview'])} chars")

        # **Role-Specific Insights**
        role_match = re.search(r'\*\*Role-Specific Insights\*\*(.+?)(?=\n\*\*[A-Z]|$)', block, re.DOTALL | re.IGNORECASE)
        if role_match:
            role_text = role_match.group(1).strip()
            job['why_this_role'] = role_text
            job['full_description'] = role_text

            # Extract bullet points as requirements
            bullets = re.findall(r'[-•]\s*(.+?)(?=\n|$)', role_text)
            if bullets:
                job['key_requirements'] = '\n'.join(bullets)

            print(f"      ✓ Role insights: {len(role_text)} chars")

        # **Interview Preparation Tips**
        interview_match = re.search(r'\*\*Interview Preparation Tips\*\*(.+?)(?=\n\*\*[A-Z]|$)', block, re.DOTALL | re.IGNORECASE)
        if interview_match:
            job['interview_prep'] = interview_match.group(1).strip()
            print(f"      ✓ Interview prep: {len(job['interview_prep'])} chars")

        # **Salary Negotiation Intelligence**
        salary_match = re.search(r'\*\*Salary Negotiation Intelligence\*\*(.+?)(?=\n\*\*[A-Z]|$)', block, re.DOTALL | re.IGNORECASE)
        if salary_match:
            job['talking_points'] = salary_match.group(1).strip()
            print(f"      ✓ Salary intel: {len(job['talking_points'])} chars")

        # **Application Strategy** (append to talking points)
        app_match = re.search(r'\*\*Application Strategy\*\*(.+?)(?=\n\*\*[A-Z]|$)', block, re.DOTALL | re.IGNORECASE)
        if app_match:
            app_text = app_match.group(1).strip()
            if job.get('talking_points'):
                job['talking_points'] += '\n\n**Application Strategy**\n' + app_text
            else:
                job['talking_points'] = app_text
            print(f"      ✓ App strategy: {len(app_text)} chars")

        # **Potential Red Flags**
        red_match = re.search(r'\*\*Potential Red Flags\*\*(.+?)(?=\n\*\*[A-Z]|###|$)', block, re.DOTALL | re.IGNORECASE)
        if red_match:
            job['red_flags'] = red_match.group(1).strip()
            print(f"      ✓ Red flags: {len(job['red_flags'])} chars")

        # **Cultural Fit Assessment** (append to why_this_role)
        culture_match = re.search(r'\*\*Cultural Fit Assessment\*\*(.+?)(?=\n\*\*[A-Z]|$)', block, re.DOTALL | re.IGNORECASE)
        if culture_match:
            culture_text = culture_match.group(1).strip()
            if job.get('why_this_role'):
                job['why_this_role'] += '\n\n**Cultural Fit**\n' + culture_text
            else:
                job['why_this_role'] = culture_text
            print(f"      ✓ Cultural fit: {len(culture_text)} chars")

        # Count populated fields
        fields = sum([
            bool(job.get('full_description')),
            bool(job.get('key_requirements')),
            bool(job.get('company_overview')),
            bool(job.get('interview_prep')),
            bool(job.get('talking_points')),
            bool(job.get('red_flags'))
        ])
        print(f"      📊 Total fields populated: {fields}/6\n")

        jobs.append(job)

    return jobs

def migrate_final_working(db_path='jobs.db', txt_pattern='job_search_*.txt'):
    """Final working migration"""

    print("🎯 FINAL WORKING Migration (**Header** format)")
    print("=" * 60)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, company FROM jobs")
    db_jobs = {row['id']: {'title': row['title'], 'company': row['company']} for row in cursor.fetchall()}

    print(f"📊 Database has {len(db_jobs)} jobs\n")

    txt_files = sorted(Path('.').glob(txt_pattern))
    total_updated = 0

    for txt_file in txt_files:
        print(f"📄 {txt_file.name}")

        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()

        top_jobs = extract_section_2_jobs(content)
        print(f"\n   Extracted {len(top_jobs)} jobs from SECTION 2\n")

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

                print(f"   ✅ MATCHED & UPDATED: {job['title'][:45]}")
                print(f"      DB Match: {best_sim:.0%} | Rich fields: {fields}/6\n")
                total_updated += 1
            else:
                print(f"   ⏭️  No DB match: {job['title'][:45]}\n")

        print("-" * 60)

    conn.commit()
    conn.close()

    print("\n" + "=" * 60)
    print(f"🎉 SUCCESS! Updated {total_updated} TOP jobs with full rich data")
    print("=" * 60)

if __name__ == "__main__":
    migrate_final_working()