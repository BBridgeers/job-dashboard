#!/usr/bin/env python3

"""
Strategic Match - 3-Tier Migration Parser
Extracts Tier 1 (full), Tier 2 (core), Tier 3 (basic) data
"""

import sqlite3
import re
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def extract_tier1_jobs(content):
    """Extract Tier 1 jobs (full 20-component analysis)"""
    jobs = []

    job_blocks = re.split(r'---START_JOB_(\d+)---', content)

    for i in range(1, len(job_blocks), 2):
        if i+1 >= len(job_blocks):
            break

        job_num = job_blocks[i]
        block = job_blocks[i+1]

        end_match = re.search(r'---END_JOB_\d+---', block)
        if end_match:
            block = block[:end_match.start()]

        job = {'tier': 1}  # Mark as Tier 1

        # Extract all 20 components
        fields = {
            'TITLE': 'title',
            'COMPANY': 'company',
            'MATCH_SCORE': 'match_score',
            'COMPANY_OVERVIEW': 'company_overview',
            'ROLE_INSIGHTS': 'why_this_role',
            'KEY_REQUIREMENTS': 'key_requirements',
            'INTERVIEW_PREP': 'interview_prep',
            'SALARY_INTEL': 'talking_points',
            'APPLICATION_STRATEGY': 'application_strategy',
            'RED_FLAGS': 'red_flags',
            'CULTURAL_FIT': 'cultural_fit',
            'SKILLS_GAP_ANALYSIS': 'skills_gap',
            'NETWORK_LEVERAGE': 'network_leverage',
            'DECISION_TIMELINE': 'decision_timeline',
            'CAREER_TRAJECTORY': 'career_trajectory',
            'WHY_THIS_ROLE': 'fit_assessment',
            'FULL_DESCRIPTION': 'full_description'
        }

        for marker, field_name in fields.items():
            pattern = f'---{marker}---\s*\n(.+?)(?=\n---|$)'
            match = re.search(pattern, block, re.DOTALL)
            if match:
                job[field_name] = match.group(1).strip()

        # Combine fields for database
        if job.get('talking_points') and job.get('application_strategy'):
            job['talking_points'] += '\n\n**Application Strategy**\n' + job['application_strategy']

        if job.get('why_this_role') and job.get('cultural_fit'):
            job['why_this_role'] += '\n\n**Cultural Fit**\n' + job['cultural_fit']

        # Add new intelligence to why_this_role
        new_insights = []
        if job.get('skills_gap'):
            new_insights.append(f"**Skills Gap**\n{job['skills_gap']}")
        if job.get('network_leverage'):
            new_insights.append(f"**Network**\n{job['network_leverage']}")
        if job.get('decision_timeline'):
            new_insights.append(f"**Timeline**\n{job['decision_timeline']}")
        if job.get('career_trajectory'):
            new_insights.append(f"**Trajectory**\n{job['career_trajectory']}")
        if job.get('fit_assessment'):
            new_insights.append(f"**Why This Role**\n{job['fit_assessment']}")

        if new_insights and job.get('why_this_role'):
            job['why_this_role'] += '\n\n' + '\n\n'.join(new_insights)

        if job.get('title'):
            jobs.append(job)

    return jobs

def extract_tier2_jobs(content):
    """Extract Tier 2 jobs (8 core data points from SECTION 1)"""
    jobs = []

    # Look for positions 6-10 in SECTION 1
    section1_match = re.search(r'SECTION 1[:\s]+(.+?)(?=SECTION 2|$)', content, re.DOTALL | re.IGNORECASE)
    if not section1_match:
        return jobs

    section1 = section1_match.group(1)

    # Find "POSITIONS 6-10" or "TIER 2" section
    tier2_match = re.search(r'(?:POSITIONS 6-10|TIER 2)(.+?)(?=TIER 3|ALL OTHER|$)', section1, re.DOTALL | re.IGNORECASE)
    if not tier2_match:
        return jobs

    tier2_section = tier2_match.group(1)

    # Parse individual jobs (6. **Title** - Company format)
    job_pattern = r'(\d+)\. \*\*(.+?)\*\* - (.+?)\n'
    matches = re.finditer(job_pattern, tier2_section)

    for match in matches:
        job_num = int(match.group(1))
        if 6 <= job_num <= 10:
            title = match.group(2).strip()
            company = match.group(3).strip()

            job = {
                'title': title,
                'company': company,
                'tier': 2
            }

            # Try to extract other core fields nearby
            job_block_start = match.end()
            job_block_end = tier2_section.find(f'{job_num+1}.', job_block_start)
            if job_block_end == -1:
                job_block_end = len(tier2_section)

            job_block = tier2_section[job_block_start:job_block_end]

            # Extract structured fields
            if 'Match Score:' in job_block:
                score_match = re.search(r'Match Score:\s*(\d+)', job_block)
                if score_match:
                    job['match_score'] = score_match.group(1)

            if 'Salary:' in job_block:
                salary_match = re.search(r'Salary:\s*(.+?)\n', job_block)
                if salary_match:
                    job['salary_range'] = salary_match.group(1).strip()

            if 'Location:' in job_block:
                loc_match = re.search(r'Location:\s*(.+?)\n', job_block)
                if loc_match:
                    job['location'] = loc_match.group(1).strip()

            jobs.append(job)

    return jobs

def extract_tier3_jobs(content):
    """Extract Tier 3 jobs (3 basic data points)"""
    jobs = []

    section1_match = re.search(r'SECTION 1[:\s]+(.+?)(?=SECTION 2|$)', content, re.DOTALL | re.IGNORECASE)
    if not section1_match:
        return jobs

    section1 = section1_match.group(1)

    # Find Tier 3 section
    tier3_match = re.search(r'(?:TIER 3|ALL OTHER MATCHES)(.+?)$', section1, re.DOTALL | re.IGNORECASE)
    if not tier3_match:
        return jobs

    tier3_section = tier3_match.group(1)

    # Parse: 11. **Title** - Company - Match: Score
    job_pattern = r'(\d+)\. \*\*(.+?)\*\* - (.+?) - Match:\s*(\d+)'
    matches = re.finditer(job_pattern, tier3_section)

    for match in matches:
        job_num = int(match.group(1))
        if job_num >= 11:
            jobs.append({
                'title': match.group(2).strip(),
                'company': match.group(3).strip(),
                'match_score': match.group(4),
                'tier': 3
            })

    return jobs

def migrate_three_tier(db_path='jobs.db', results_dir='job_search_results'):
    """Migrate 3-tier structured data to database"""
    print("🎯 Strategic Match - 3-Tier Migration")
    print("=" * 60)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get existing jobs
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
    total_inserted = 0

    for txt_file in txt_files:
        print(f"📄 {txt_file.name}")

        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Determine search type
        search_type = 'nonprofit' if 'nonprofit' in txt_file.name.lower() else 'corporate'

        # Extract all tiers
        tier1_jobs = extract_tier1_jobs(content)
        tier2_jobs = extract_tier2_jobs(content)
        tier3_jobs = extract_tier3_jobs(content)

        all_jobs = tier1_jobs + tier2_jobs + tier3_jobs

        print(f"  Tier 1: {len(tier1_jobs)} | Tier 2: {len(tier2_jobs)} | Tier 3: {len(tier3_jobs)}\n")

        for job in all_jobs:
            if not job.get('title'):
                continue

            # Fuzzy match existing jobs
            best_match_id = None
            best_sim = 0.0

            for db_id, db_job in db_jobs.items():
                sim = similarity(job['title'], db_job['title'])
                if sim > best_sim and sim > 0.5:
                    best_sim = sim
                    best_match_id = db_id

            tier = job.get('tier', 3)

            if best_match_id:
                # Update existing job
                cursor.execute("""
                    UPDATE jobs SET
                        full_description = COALESCE(?, full_description),
                        key_requirements = COALESCE(?, key_requirements),
                        company_overview = COALESCE(?, company_overview),
                        why_this_role = COALESCE(?, why_this_role),
                        interview_prep = COALESCE(?, interview_prep),
                        talking_points = COALESCE(?, talking_points),
                        red_flags = COALESCE(?, red_flags),
                        tier = ?,
                        date_added = CURRENT_DATE,
                        search_type = ?,
                        is_top_match = CASE WHEN ? = 1 THEN 1 ELSE is_top_match END
                    WHERE id = ?
                """, (
                    job.get('full_description'),
                    job.get('key_requirements'),
                    job.get('company_overview'),
                    job.get('why_this_role'),
                    job.get('interview_prep'),
                    job.get('talking_points'),
                    job.get('red_flags'),
                    tier,
                    search_type,
                    tier,
                    best_match_id
                ))

                print(f"  ✅ Updated Tier {tier}: {job['title'][:35]}")
                total_updated += 1
            else:
                # Insert new job
                cursor.execute("""
                    INSERT INTO jobs (
                        title, company, job_type, match_score, tier, date_added, search_type,
                        full_description, key_requirements, company_overview, why_this_role,
                        interview_prep, talking_points, red_flags, status, is_top_match
                    ) VALUES (?, ?, ?, ?, ?, CURRENT_DATE, ?, ?, ?, ?, ?, ?, ?, ?, 'New', ?)
                """, (
                    job.get('title'),
                    job.get('company', 'Unknown'),
                    search_type.capitalize(),
                    job.get('match_score', 0),
                    tier,
                    search_type,
                    job.get('full_description'),
                    job.get('key_requirements'),
                    job.get('company_overview'),
                    job.get('why_this_role'),
                    job.get('interview_prep'),
                    job.get('talking_points'),
                    job.get('red_flags'),
                    1 if tier == 1 else 0
                ))

                print(f"  ✨ Inserted Tier {tier}: {job['title'][:35]}")
                total_inserted += 1

        print("-" * 60)

    conn.commit()
    conn.close()

    print("\n" + "=" * 60)
    print(f"🎉 Updated: {total_updated} | Inserted: {total_inserted}")
    print("=" * 60)

if __name__ == "__main__":
    migrate_three_tier()
