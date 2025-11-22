#!/usr/bin/env python3
"""
Strategic Match - ROBUST MIGRATION PARSER (FINAL SPEC)
"""
import sqlite3
import re
import glob
from datetime import datetime

def clean_bullets(text):
    if not text: return ""
    # Format as HTML list if it looks like bullets
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if not lines: return ""
    html = "<ul>"
    for l in lines:
        clean_l = l.lstrip('-*•').strip()
        html += f"<li>{clean_l}</li>"
    html += "</ul>"
    return html

def parse_file(content):
    jobs = []

    # --- SPLIT BY JOB BLOCKS (SECTION 2) ---
    rich_blocks = re.split(r'---START_JOB_\d+---', content)
    rich_data_map = {}

    for block in rich_blocks[1:]: 
        title_match = re.search(r'TITLE:\s*(.+)', block)
        if title_match:
            title_key = title_match.group(1).strip().lower()[:20]

            rich_data = {}
            # 12 APPLIED RESEARCH FIELDS
            research_pats = {
                'company_overview': r'---COMPANY_OVERVIEW---\s*(.*?)(?=\n---|---ROLE|\Z)',
                'role_insights': r'---ROLE_INSIGHTS---\s*(.*?)(?=\n---|---KEY|\Z)',
                'key_requirements': r'---KEY_REQUIREMENTS---\s*(.*?)(?=\n---|---SAL|\Z)',
                'salary_intel': r'---SALARY_INTEL---\s*(.*?)(?=\n---|---APP|\Z)',
                'application_strategy': r'---APPLICATION_STRATEGY---\s*(.*?)(?=\n---|---RED|\Z)',
                'red_flags': r'---RED_FLAGS---\s*(.*?)(?=\n---|---CUL|\Z)',
                'cultural_fit': r'---CULTURAL_FIT---\s*(.*?)(?=\n---|---COM|\Z)',
                'competitive_landscape': r'---COMPETITIVE_LANDSCAPE---\s*(.*?)(?=\n---|---SKI|\Z)',
                'skills_gap': r'---SKILLS_GAP_ANALYSIS---\s*(.*?)(?=\n---|---NET|\Z)',
                'network_leverage': r'---NETWORK_LEVERAGE---\s*(.*?)(?=\n---|---DEC|\Z)',
                'decision_timeline': r'---DECISION_TIMELINE---\s*(.*?)(?=\n---|---CAR|\Z)',
                'career_trajectory': r'---CAREER_TRAJECTORY---\s*(.*?)(?=\n---|---RES|\Z)',
            }

            # 12 APPLICATION PACK FIELDS
            pack_pats = {
                'resume_keywords': r'---RESUME_KEYWORDS---\s*(.*?)(?=\n---|---RES|\Z)',
                'resume_summary': r'---RESUME_SUMMARY---\s*(.*?)(?=\n---|---COV|\Z)',
                'cover_letter': r'---COVER_LETTER_DRAFT---\s*(.*?)(?=\n---|---WHY|\Z)',
                'why_me_bullets': r'---WHY_ME_BULLETS---\s*(.*?)(?=\n---|---WHY|\Z)',
                'why_them_bullets': r'---WHY_THEM_BULLETS---\s*(.*?)(?=\n---|---INT|\Z)',
                'interview_prep': r'---INTERVIEW_PREP---\s*(.*?)(?=\n---|---STA|\Z)',
                'star_hooks': r'---STAR_HOOKS---\s*(.*?)(?=\n---|---TAL|\Z)',
                'talking_points': r'---TALKING_POINTS---\s*(.*?)(?=\n---|---QUE|\Z)',
                'questions_to_ask': r'---QUESTIONS_TO_ASK---\s*(.*?)(?=\n---|---REC|\Z)',
                'recruiter_email': r'---RECRUITER_EMAIL---\s*(.*?)(?=\n---|---THA|\Z)',
                'thank_you_email': r'---THANK_YOU_EMAIL---\s*(.*?)(?=\n---|---30_|\Z)',
                'plan_30_60_90': r'---30_60_90_PLAN---\s*(.*?)(?=\n---|---END|\Z)'
            }

            # Combine and Parse
            all_pats = {**research_pats, **pack_pats}
            for field, pat in all_pats.items():
                m = re.search(pat, block, re.DOTALL)
                if m: rich_data[field] = m.group(1).strip()

            rich_data_map[title_key] = rich_data

    # --- LISTING PARSER (SECTION 1) ---
    # Now catches SUMMARY_BULLETS and FIT_BULLETS
    listing_pattern = r'(\d+)\.\s*\*\*([^\*]+)\*\*\s*-\s*([^\n]+)'
    matches = re.findall(listing_pattern, content)

    for rank, title, rest in matches:
        job = {}
        job['title'] = title.strip()

        # Isolate block
        start_idx = content.find(f"{rank}. **{title}**")
        end_idx = content.find(f"{int(rank)+1}. **", start_idx)
        if end_idx == -1: end_idx = len(content)
        job_block = content[start_idx:end_idx]

        # Basic Fields
        if "Match:" in rest:
            job['company'] = rest.split("Match:")[0].strip(" -")
            ms = re.search(r'Match:.*?(\d+)', rest)
            job['match_score'] = int(ms.group(1)) if ms else 0
        else:
            job['company'] = rest.strip()
            job['match_score'] = 0

        loc_m = re.search(r'Location:\s*([^\n]+)', job_block)
        job['location'] = loc_m.group(1).strip() if loc_m else "See details"

        url_m = re.search(r'URL:\s*([^\n]+)', job_block)
        raw_url = url_m.group(1).strip() if url_m else "#"
        if "(" in raw_url and ")" in raw_url: raw_url = raw_url.split("(")[-1].strip(")")
        job['url'] = raw_url

        # NEW: Capture Summary/Fit Bullets
        sum_m = re.search(r'SUMMARY_BULLETS:\s*(.*?)(?=\n\s*[A-Z]|\Z)', job_block, re.DOTALL)
        job['summary_bullets'] = clean_bullets(sum_m.group(1)) if sum_m else ""

        fit_m = re.search(r'FIT_BULLETS:\s*(.*?)(?=\n\s*[A-Z]|\Z)', job_block, re.DOTALL)
        job['fit_bullets'] = clean_bullets(fit_m.group(1)) if fit_m else ""

        # Merge Rich Data
        t_key = job['title'].lower()[:20]
        if t_key in rich_data_map:
            job.update(rich_data_map[t_key])
            job['tier'] = 1 
        else:
            job['tier'] = 3 if int(rank) > 10 else 2

        jobs.append(job)

    return jobs

def migrate():
    print("🚀 STARTING FINAL SPEC MIGRATION...")
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()

    # FULL SCHEMA - 30+ COLUMNS
    c.execute("""CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY,
        title TEXT, company TEXT, location TEXT, url TEXT,
        match_score INTEGER, tier INTEGER, status TEXT, date_added TEXT,
        summary_bullets TEXT, fit_bullets TEXT,

        -- APPLIED RESEARCH
        company_overview TEXT, role_insights TEXT, key_requirements TEXT,
        salary_intel TEXT, application_strategy TEXT, red_flags TEXT,
        cultural_fit TEXT, competitive_landscape TEXT, skills_gap TEXT,
        network_leverage TEXT, decision_timeline TEXT, career_trajectory TEXT,

        -- APPLICATION PACK
        resume_keywords TEXT, resume_summary TEXT, cover_letter TEXT,
        why_me_bullets TEXT, why_them_bullets TEXT, interview_prep TEXT,
        star_hooks TEXT, talking_points TEXT, questions_to_ask TEXT,
        recruiter_email TEXT, thank_you_email TEXT, plan_30_60_90 TEXT,

        notes TEXT, application_url TEXT, search_type TEXT
    )""")

    # Schema Migration Check
    existing_cols = [row[1] for row in c.execute("PRAGMA table_info(jobs)")]
    new_cols = [
        'summary_bullets', 'fit_bullets', 'salary_intel', 'application_strategy',
        'why_me_bullets', 'why_them_bullets', 'thank_you_email', 'plan_30_60_90'
    ]
    for col in new_cols:
        if col not in existing_cols:
            try: c.execute(f"ALTER TABLE jobs ADD COLUMN {col} TEXT"); print(f"🔧 Added {col}")
            except: pass

    files = sorted(glob.glob("job_search_results/*.txt"))
    total_imported = 0

    for fpath in files:
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f: content = f.read()
        jobs = parse_file(content)
        search_type = 'Corporate' if 'corporate' in fpath.lower() else 'Nonprofit'

        for j in jobs:
            c.execute("SELECT id FROM jobs WHERE title = ? AND company = ?", (j['title'], j['company']))
            exists = c.fetchone()

            # All fields
            all_fields = [
                'summary_bullets', 'fit_bullets',
                'company_overview', 'role_insights', 'key_requirements', 'salary_intel',
                'application_strategy', 'red_flags', 'cultural_fit', 'competitive_landscape',
                'skills_gap', 'network_leverage', 'decision_timeline', 'career_trajectory',
                'resume_keywords', 'resume_summary', 'cover_letter', 'why_me_bullets',
                'why_them_bullets', 'interview_prep', 'star_hooks', 'talking_points',
                'questions_to_ask', 'recruiter_email', 'thank_you_email', 'plan_30_60_90'
            ]
            safe_j = {k: j.get(k, "") for k in all_fields}

            if exists:
                # Always update Summary/Fit bullets if present
                if j.get('summary_bullets'):
                    set_clause = ", ".join([f"{k}=?" for k in all_fields])
                    vals = [safe_j[k] for k in all_fields] + [j.get('tier', 2), j.get('url'), exists[0]]
                    c.execute(f"UPDATE jobs SET {set_clause}, tier=?, url=? WHERE id=?", vals)
            else:
                cols = "title, company, location, url, match_score, tier, status, date_added, search_type, " + ", ".join(all_fields)
                placeholders = "?,?,?,?,?,?,?,?,?," + ",".join(["?"] * len(all_fields))
                vals = [
                    j['title'], j['company'], j['location'], j['url'], j['match_score'],
                    j['tier'], 'New', datetime.now().strftime("%Y-%m-%d"), search_type
                ] + [safe_j[k] for k in all_fields]
                c.execute(f"INSERT INTO jobs ({cols}) VALUES ({placeholders})", vals)
                total_imported += 1

    conn.commit()
    conn.close()
    print(f"✅ Migration Complete. Imported/Updated {total_imported} jobs.")

if __name__ == "__main__":
    migrate()
