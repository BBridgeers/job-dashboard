#!/usr/bin/env python3
"""
TXT File to Database Migration
Parses job search TXT files and imports rich data into database
"""

import sqlite3
import re
from pathlib import Path
from datetime import datetime

def parse_txt_file(file_path):
    """Parse a job search TXT file and extract job details"""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    jobs = []

    # Split by job separators (assuming jobs are separated by "=" lines or "---")
    job_blocks = re.split(r'={50,}|\n---+\n', content)

    for block in job_blocks:
        if len(block.strip()) < 100:  # Skip small blocks
            continue

        job_data = {}

        # Extract job title (usually first bold line or after "Title:")
        title_match = re.search(r'(?:Title:|Position:|Role:)?\s*\*\*(.+?)\*\*', block, re.IGNORECASE)
        if title_match:
            job_data['title'] = title_match.group(1).strip()

        # Extract company
        company_match = re.search(r'(?:Company:|Organization:|Employer:)\s*\*\*(.+?)\*\*', block, re.IGNORECASE)
        if company_match:
            job_data['company'] = company_match.group(1).strip()

        # Extract location
        location_match = re.search(r'(?:Location:|Where:)\s*(.+?)(?:\n|$)', block, re.IGNORECASE)
        if location_match:
            job_data['location'] = location_match.group(1).strip()

        # Extract salary
        salary_match = re.search(r'(?:Salary|Compensation|Pay):?\s*(.+?)(?:\n|$)', block, re.IGNORECASE)
        if salary_match:
            job_data['salary'] = salary_match.group(1).strip()

        # Extract URLs
        url_match = re.search(r'(?:URL|Link|Apply):?\s*(https?://\S+)', block, re.IGNORECASE)
        if url_match:
            job_data['url'] = url_match.group(1).strip()

        # Extract full description (usually after "Description:" or "About:")
        desc_match = re.search(r'(?:Description|About the Role|Overview):(.+?)(?=(?:Requirements|Qualifications|Company|\n\n\*\*)|$)', block, re.DOTALL | re.IGNORECASE)
        if desc_match:
            job_data['full_description'] = desc_match.group(1).strip()

        # Extract requirements
        req_match = re.search(r'(?:Requirements|Qualifications|What we need):(.+?)(?=(?:Company|Interview|\n\n\*\*)|$)', block, re.DOTALL | re.IGNORECASE)
        if req_match:
            job_data['key_requirements'] = req_match.group(1).strip()

        # Extract company overview
        company_overview_match = re.search(r'(?:Company Overview|About the Company|Organization):(.+?)(?=(?:Why|Interview|\n\n\*\*)|$)', block, re.DOTALL | re.IGNORECASE)
        if company_overview_match:
            job_data['company_overview'] = company_overview_match.group(1).strip()

        # Extract "Why This Role"
        why_match = re.search(r'(?:Why This Role|Why Join|Fit Analysis):(.+?)(?=(?:Interview|Talking|\n\n\*\*)|$)', block, re.DOTALL | re.IGNORECASE)
        if why_match:
            job_data['why_this_role'] = why_match.group(1).strip()

        # Extract interview prep
        interview_match = re.search(r'(?:Interview Prep|Interview Tips|Preparation):(.+?)(?=(?:Talking Points|Red Flags|\n\n\*\*)|$)', block, re.DOTALL | re.IGNORECASE)
        if interview_match:
            job_data['interview_prep'] = interview_match.group(1).strip()

        # Extract talking points
        talking_match = re.search(r'(?:Talking Points|Key Points|Discussion):(.+?)(?=(?:Red Flags|Considerations|\n\n\*\*)|$)', block, re.DOTALL | re.IGNORECASE)
        if talking_match:
            job_data['talking_points'] = talking_match.group(1).strip()

        # Extract red flags
        red_flags_match = re.search(r'(?:Red Flags|Considerations|Watch Out):(.+?)(?=\n\n\*\*|$)', block, re.DOTALL | re.IGNORECASE)
        if red_flags_match:
            job_data['red_flags'] = red_flags_match.group(1).strip()

        if job_data.get('title'):  # Only add if we found at least a title
            jobs.append(job_data)

    return jobs

def migrate_txt_to_database(txt_pattern='job_search_*.txt', db_path='jobs.db'):
    """Import job data from TXT files into database"""

    print("📥 Migrating TXT Files to Database...")
    print("=" * 60)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    txt_files = sorted(Path('.').glob(txt_pattern))

    if not txt_files:
        print("⚠️  No TXT files found matching pattern:", txt_pattern)
        return

    total_imported = 0

    for txt_file in txt_files:
        print(f"\n📄 Processing: {txt_file.name}")

        jobs = parse_txt_file(txt_file)
        print(f"   Found {len(jobs)} jobs in file")

        for job in jobs:
            # Try to match existing job in DB by title + company
            cursor.execute("""
                SELECT id FROM jobs 
                WHERE title = ? AND company = ?
                LIMIT 1
            """, (job.get('title'), job.get('company')))

            existing = cursor.fetchone()

            if existing:
                # Update existing job with rich data
                job_id = existing[0]
                cursor.execute("""
                    UPDATE jobs SET
                        full_description = ?,
                        key_requirements = ?,
                        company_overview = ?,
                        why_this_role = ?,
                        interview_prep = ?,
                        talking_points = ?,
                        red_flags = ?,
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
                    job_id
                ))
                print(f"   ✅ Updated: {job.get('title')}")
                total_imported += 1
            else:
                print(f"   ⏭️  Not in DB: {job.get('title')}")

    conn.commit()
    conn.close()

    print("\n" + "=" * 60)
    print(f"✅ Migration complete! Updated {total_imported} jobs with rich data")
    print("=" * 60)

if __name__ == "__main__":
    migrate_txt_to_database()