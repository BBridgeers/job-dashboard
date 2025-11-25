#!/usr/bin/env python3
"""
Improved TXT to Database Migration
Better parsing and fuzzy matching for job titles
"""

import sqlite3
import re
from pathlib import Path
from difflib import SequenceMatcher

def similarity(a, b):
    """Calculate similarity ratio between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def parse_job_block(block):
    """Parse a single job block from TXT file"""

    job_data = {}
    lines = block.strip().split('\n')

    # Look for the actual job title (usually has ** markers or is first bold line)
    for i, line in enumerate(lines):
        # Try to find title with ** markers
        title_match = re.search(r'\*\*(.+?)\*\*', line)
        if title_match and not any(x in line.lower() for x in ['match score', 'note:', 'industry', 'key responsibilities']):
            job_data['title'] = title_match.group(1).strip()
            break
        # Or look for patterns like "Job #1: Title"
        job_num_match = re.search(r'Job #\d+:?\s*(.+)', line, re.IGNORECASE)
        if job_num_match:
            job_data['title'] = job_num_match.group(1).strip()
            break

    if not job_data.get('title'):
        return None

    # Extract company
    for line in lines:
        if 'company:' in line.lower() or 'organization:' in line.lower():
            company_match = re.search(r'(?:Company|Organization):?\s*\*\*?(.+?)\*\*?', line, re.IGNORECASE)
            if company_match:
                job_data['company'] = company_match.group(1).strip()
                break

    # Extract full description
    desc_start = None
    for i, line in enumerate(lines):
        if any(x in line.lower() for x in ['description:', 'about the role:', 'overview:', 'responsibilities:']):
            desc_start = i
            break

    if desc_start:
        desc_lines = []
        for line in lines[desc_start+1:]:
            if line.strip() and not any(x in line.lower() for x in ['requirements:', 'qualifications:', 'company overview:']):
                desc_lines.append(line.strip())
            elif any(x in line.lower() for x in ['requirements:', 'qualifications:']):
                break
        if desc_lines:
            job_data['full_description'] = ' '.join(desc_lines)

    # Extract requirements
    req_start = None
    for i, line in enumerate(lines):
        if any(x in line.lower() for x in ['requirements:', 'qualifications:', 'what we need:']):
            req_start = i
            break

    if req_start:
        req_lines = []
        for line in lines[req_start+1:]:
            if line.strip() and not any(x in line.lower() for x in ['company overview:', 'why this role:', 'interview prep:']):
                req_lines.append(line.strip())
            elif 'company overview:' in line.lower():
                break
        if req_lines:
            job_data['key_requirements'] = ' '.join(req_lines)

    # Extract company overview
    company_start = None
    for i, line in enumerate(lines):
        if 'company overview:' in line.lower() or 'about the company:' in line.lower():
            company_start = i
            break

    if company_start:
        company_lines = []
        for line in lines[company_start+1:]:
            if line.strip() and not any(x in line.lower() for x in ['why this role:', 'interview prep:', 'talking points:']):
                company_lines.append(line.strip())
            elif 'why this role:' in line.lower():
                break
        if company_lines:
            job_data['company_overview'] = ' '.join(company_lines)

    # Extract "Why This Role"
    why_start = None
    for i, line in enumerate(lines):
        if 'why this role:' in line.lower() or 'why join:' in line.lower():
            why_start = i
            break

    if why_start:
        why_lines = []
        for line in lines[why_start+1:]:
            if line.strip() and not any(x in line.lower() for x in ['interview prep:', 'talking points:', 'red flags:']):
                why_lines.append(line.strip())
            elif 'interview prep:' in line.lower():
                break
        if why_lines:
            job_data['why_this_role'] = ' '.join(why_lines)

    # Extract interview prep
    interview_start = None
    for i, line in enumerate(lines):
        if 'interview prep:' in line.lower() or 'interview tips:' in line.lower():
            interview_start = i
            break

    if interview_start:
        interview_lines = []
        for line in lines[interview_start+1:]:
            if line.strip() and not any(x in line.lower() for x in ['talking points:', 'red flags:', 'considerations:']):
                interview_lines.append(line.strip())
            elif 'talking points:' in line.lower():
                break
        if interview_lines:
            job_data['interview_prep'] = ' '.join(interview_lines)

    # Extract talking points
    talking_start = None
    for i, line in enumerate(lines):
        if 'talking points:' in line.lower() or 'key points:' in line.lower():
            talking_start = i
            break

    if talking_start:
        talking_lines = []
        for line in lines[talking_start+1:]:
            if line.strip() and not any(x in line.lower() for x in ['red flags:', 'considerations:', 'note:']):
                talking_lines.append(line.strip())
            elif 'red flags:' in line.lower():
                break
        if talking_lines:
            job_data['talking_points'] = ' '.join(talking_lines)

    # Extract red flags
    red_start = None
    for i, line in enumerate(lines):
        if 'red flags:' in line.lower() or 'considerations:' in line.lower():
            red_start = i
            break

    if red_start:
        red_lines = []
        for line in lines[red_start+1:]:
            if line.strip() and 'job #' not in line.lower() and '===' not in line:
                red_lines.append(line.strip())
            else:
                break
        if red_lines:
            job_data['red_flags'] = ' '.join(red_lines)

    return job_data

def migrate_with_fuzzy_matching(db_path='jobs.db', txt_pattern='job_search_*.txt'):
    """Migrate with fuzzy title matching"""

    print("📥 Migrating TXT Files to Database (Fuzzy Matching)...")
    print("=" * 60)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all jobs from DB
    cursor.execute("SELECT id, title, company FROM jobs")
    db_jobs = {row['id']: {'title': row['title'], 'company': row['company']} for row in cursor.fetchall()}

    print(f"Found {len(db_jobs)} jobs in database")

    txt_files = sorted(Path('.').glob(txt_pattern))

    if not txt_files:
        print("⚠️  No TXT files found")
        conn.close()
        return

    total_updated = 0

    for txt_file in txt_files:
        print(f"\n📄 Processing: {txt_file.name}")

        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split by job separators
        jobs = re.split(r'={50,}|Job #\d+:', content)

        parsed_count = 0
        for block in jobs:
            if len(block.strip()) < 100:
                continue

            job_data = parse_job_block(block)
            if not job_data or not job_data.get('title'):
                continue

            parsed_count += 1

            # Fuzzy match to DB
            best_match_id = None
            best_similarity = 0.0

            for db_id, db_job in db_jobs.items():
                title_sim = similarity(job_data['title'], db_job['title'])
                if title_sim > best_similarity and title_sim > 0.6:  # 60% similarity threshold
                    best_similarity = title_sim
                    best_match_id = db_id

            if best_match_id:
                # Update the matched job
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
                    job_data.get('full_description'),
                    job_data.get('key_requirements'),
                    job_data.get('company_overview'),
                    job_data.get('why_this_role'),
                    job_data.get('interview_prep'),
                    job_data.get('talking_points'),
                    job_data.get('red_flags'),
                    best_match_id
                ))
                print(f"   ✅ Matched & Updated: {job_data['title'][:50]} (similarity: {best_similarity:.0%})")
                total_updated += 1
            else:
                print(f"   ⏭️  No match: {job_data['title'][:50]}")

        print(f"   Parsed {parsed_count} jobs from file")

    conn.commit()
    conn.close()

    print("\n" + "=" * 60)
    print(f"✅ Migration complete! Updated {total_updated} jobs with rich data")
    print("=" * 60)

if __name__ == "__main__":
    migrate_with_fuzzy_matching()