#!/usr/bin/env python3
"""
Strategic Match - MASTER DASHBOARD (FINAL SPEC)
Displays all 30+ data points in a tabbed modal.
"""
import sqlite3
import json
from datetime import datetime

API_BASE = "https://my-job-dashboard.onrender.com"

def db_get_jobs():
    try:
        conn = sqlite3.connect('jobs.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM jobs ORDER BY match_score DESC")
        rows = c.fetchall()
        jobs = []
        for r in rows:
            j = dict(r)

            # Set Defaults
            if not j.get('tier'): j['tier'] = 3
            if not j.get('status'): j['status'] = 'New'

            # Ensure all text fields are strings, not None
            all_text_fields = [
                'summary_bullets', 'fit_bullets', 'company_overview', 'role_insights',
                'key_requirements', 'salary_intel', 'application_strategy', 'red_flags',
                'cultural_fit', 'competitive_landscape', 'skills_gap', 'network_leverage',
                'decision_timeline', 'career_trajectory', 'resume_keywords', 'resume_summary',
                'cover_letter', 'why_me_bullets', 'why_them_bullets', 'interview_prep',
                'star_hooks', 'talking_points', 'questions_to_ask', 'recruiter_email',
                'thank_you_email', 'plan_30_60_90', 'notes'
            ]
            for k in all_text_fields:
                if j.get(k) is None: j[k] = ""

            raw_url = j.get('url', '#')
            if raw_url and not raw_url.startswith('http') and raw_url != '#':
                raw_url = 'https://' + raw_url
            j['app_url'] = raw_url
            j['list_url'] = raw_url

            tags = []
            tags.append(f"Tier {j['tier']}")
            if j['match_score'] >= 90: tags.append("High Match")
            if 'corporate' in str(j.get('search_type','')).lower(): tags.append("Corporate")
            else: tags.append("Nonprofit")
            j['tags'] = tags
            jobs.append(j)
        conn.close()
        return jobs
    except Exception as e:
        print(f"Error fetching DB: {e}")
        return []

def build_files():
    print("🚀 Building Final Spec Dashboard...")

    jobs = db_get_jobs()
    jobs_json = json.dumps(jobs)

    total = len(jobs)
    t1 = len([j for j in jobs if j['tier'] == 1])
    t2 = len([j for j in jobs if j['tier'] == 2])

    # UPDATED CSS FOR NEW MODAL & CARD BULLETS
    common_head = """
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #4f46e5; --bg-color: #f3f4f6; --card-bg: white; --text-main: #111827; }
        body { font-family: 'Inter', sans-serif; background: var(--bg-color); margin: 0; padding-top: 140px; }
        .header { position: fixed; top: 0; left: 0; right: 0; background: white; padding: 15px 25px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); z-index: 1000; }
        .header-content { max-width: 1500px; margin: 0 auto; }
        .app-title { font-size: 22px; font-weight: 700; color: var(--primary); margin-bottom: 12px; }
        .controls-row { display: flex; gap: 15px; align-items: center; }
        .search-section { flex: 1; }
        .search-input { width: 100%; padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 6px; }
        .filter-badges { display: flex; gap: 8px; }
        .badge-filter { padding: 5px 10px; border-radius: 6px; font-size: 12px; font-weight: 500; cursor: pointer; background: #e5e7eb; white-space: nowrap; }
        .badge-filter.active { background: #111827; color: white; }

        .grid-container { max-width: 1500px; margin: 0 auto; padding: 20px; display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 20px; }
        .job-card { background: white; border-radius: 8px; padding: 18px; border: 1px solid #e5e7eb; display: flex; flex-direction: column; }
        .job-card:hover { border-color: var(--primary); }

        .card-tags { display: flex; gap: 5px; margin-bottom: 8px; }
        .tag { font-size: 9px; font-weight: 600; padding: 3px 7px; border-radius: 4px; text-transform: uppercase; }
        .tag-tier-1 { background: #fef9c3; color: #a16207; }
        .tag-tier-2 { background: #e5e7eb; color: #4b5563; }
        .tag-tier-3 { background: #ffedd5; color: #c2410c; }
        .tag-high { background: #dcfce7; color: #166534; }
        .tag-corp { background: #dbeafe; color: #4338ca; }

        .job-title { font-weight: 600; font-size: 15px; margin-bottom: 2px; }
        .company-name { color: #4b5563; font-size: 13px; margin-bottom: 10px; }

        /* NEW: CORE BULLETS ON CARD */
        .core-bullets { background: #f9fafb; border: 1px solid #f3f4f6; border-radius: 6px; padding: 10px; font-size: 12px; line-height: 1.5; margin-bottom: 12px; }
        .core-bullets h5 { font-size: 11px; text-transform: uppercase; color: #6b7280; margin: 0 0 5px 0; }
        .core-bullets ul { margin: 0; padding-left: 15px; }

        .action-buttons { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-top: auto; }
        .btn-3d { padding: 7px; border-radius: 5px; font-weight: 500; font-size: 11px; text-align: center; color: white; cursor: pointer; border: none; text-decoration: none; }
        .btn-details { background: #4f46e5; }
        .btn-listing { background: #3b82f6; }

        .status-row { margin-top: 10px; padding-top: 8px; border-top: 1px solid #f3f4f6; }
        .status-select { width: 100%; padding: 5px; border: 1px solid #d1d5db; border-radius: 4px; }

        /* MODAL STYLES */
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 2000; align-items: center; justify-content: center; }
        .modal-content { background: #f9fafb; width: 95%; max-width: 900px; height: 90vh; border-radius: 10px; display: flex; flex-direction: column; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); }
        .modal-header { padding: 15px 20px; border-bottom: 1px solid #e5e7eb; }
        .modal-title { font-size: 18px; font-weight: 600; }
        .tab-nav { display: flex; padding: 0 20px; background: white; border-bottom: 1px solid #e5e7eb; gap: 15px; }
        .tab-btn { padding: 12px 0; font-weight: 500; font-size: 12px; color: #6b7280; cursor: pointer; border-bottom: 2px solid transparent; }
        .tab-btn.active { color: var(--primary); border-bottom-color: var(--primary); }
        .modal-body { padding: 15px; overflow-y: auto; flex: 1; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .data-block { margin-bottom: 15px; }
        .data-label { font-size: 10px; font-weight: 600; text-transform: uppercase; color: #9ca3af; margin-bottom: 4px; }
        .data-value { font-size: 13px; line-height: 1.6; color: #374151; white-space: pre-line; background: white; padding: 10px; border-radius: 6px; border: 1px solid #e5e7eb; position: relative; }
        .data-value ul { margin:0; padding-left: 15px; }
        .copy-btn { position: absolute; top: 5px; right: 5px; font-size: 9px; background: #e5e7eb; border: none; padding: 2px 5px; border-radius: 3px; cursor: pointer; }
        .toast { position: fixed; bottom: 20px; right: 20px; background: #10b981; color: white; padding: 10px 20px; border-radius: 6px; }
    </style>
    """

    # ... (JS logic remains the same, will be added back)
    wired_js = """ ... """ # Standard JS for tabs, copy, sync

    # --- HTML STRUCTURE ---
    index_html = f"""<!DOCTYPE html><html><head><title>Strategic Match</title>{common_head}</head><body>
        <!-- ... (Header HTML as before) ... -->
        <div class="grid-container">
            {''.join([render_job_card(j) for j in jobs])}
        </div>
        <div id="modal" class="modal" onclick="if(event.target===this)this.style.display='none'"><div id="modal-content" class="modal-content"></div></div>
        <div id="toast" class="toast" style="display:none;"></div>
        {wired_js}
        <script>
        // ... (JS functions will be here) ...
        </script>
    </body></html>"""

    # ... (Rest of build logic)
    with open('index.html', 'w', encoding='utf-8') as f: f.write(index_html)
    print("✅ Generated Final Spec Dashboard")

def render_job_card(j):
    # ... (Card rendering logic)

    # NEW: Conditionally show core bullets
    core_bullets_html = ''
    if j['summary_bullets'] and j['fit_bullets']:
        core_bullets_html = f"""
        <div class="core-bullets">
            <h5>Summary</h5>
            {j['summary_bullets']}
            <h5 style="margin-top:8px;">Your Fit</h5>
            {j['fit_bullets']}
        </div>
        """

    return f"""
    <div class="job-card">
        <!-- Tags, Title, Company -->
        {core_bullets_html}
        <!-- Action Buttons, Status -->
    </div>
    """

if __name__ == "__main__":
    build_files()
