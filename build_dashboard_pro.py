#!/usr/bin/env python3
"""
Strategic Match Dashboard Builder - PRODUCTION VERSION
Fixes: UI Layout, Color Coding, Link Functionality, Data Injection
"""
import sqlite3
import json
import html

API_BASE = "https://my-job-dashboard.onrender.com"

def db_get_jobs():
    """Fetch all jobs from SQLite and prepare for rendering"""
    try:
        conn = sqlite3.connect('jobs.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM jobs ORDER BY match_score DESC")
        rows = c.fetchall()
        jobs = []

        for r in rows:
            j = dict(r)

            # Set defaults
            if not j.get('tier'): j['tier'] = 3
            if not j.get('status'): j['status'] = 'New'
            if not j.get('match_score'): j['match_score'] = 0

            # SANITIZE: Replace None with empty strings
            for k, v in j.items():
                if v is None:
                    j[k] = ""
                elif isinstance(v, str):
                    # Basic escaping for JSON safety
                    j[k] = v.replace('"', '&quot;').replace("'", "&apos;")

            # Fix URLs
            list_url = j.get('url', '#')
            if list_url and not list_url.startswith('http') and list_url != '#':
                list_url = 'https://' + list_url

            app_url = j.get('application_url', '')
            if not app_url or app_url == '#':
                app_url = list_url  # Fallback
            elif not app_url.startswith('http'):
                app_url = 'https://' + app_url

            j['list_url'] = list_url
            j['app_url'] = app_url

            # Tags
            tags = []
            tags.append(f"Tier {j['tier']}")
            if 'corporate' in str(j.get('search_type', '')).lower():
                tags.append("Corporate")
            else:
                tags.append("Nonprofit")
            j['tags'] = tags

            jobs.append(j)

        conn.close()
        return jobs
    except Exception as e:
        print(f"❌ Database Error: {e}")
        return []

def build_dashboard():
    """Generate index.html with all UI fixes"""
    print("🚀 Building Dashboard...")

    jobs = db_get_jobs()

    # Stats
    total = len(jobs)
    t1 = len([j for j in jobs if j['tier'] == 1])
    t2 = len([j for j in jobs if j['tier'] == 2])
    t3 = len([j for j in jobs if j['tier'] == 3])
    corp = len([j for j in jobs if 'Corporate' in j['tags']])
    nonp = len([j for j in jobs if 'Nonprofit' in j['tags']])

    # Inject data as JSON
    js_data = json.dumps(jobs, default=str)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Strategic Match</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #f3f4f6; --card-bg: #ffffff; --text: #111827;
            --c-tier1: #fef9c3; --t-tier1: #854d0e; --b-tier1: #eab308;
            --c-tier2: #e5e7eb; --t-tier2: #374151; --b-tier2: #9ca3af;
            --c-tier3: #ffedd5; --t-tier3: #9a3412; --b-tier3: #f97316;
            --c-corp: #dbeafe; --t-corp: #1e40af; --b-corp: #3b82f6;
            --c-nonp: #dcfce7; --t-nonp: #166534; --b-nonp: #22c55e;
        }}
        * {{ box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; background: var(--bg); margin: 0; padding-top: 80px; }}

        /* HEADER */
        .header {{ position: fixed; top: 0; left: 0; right: 0; background: white; padding: 15px 30px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); z-index: 1000; height: 60px; display: flex; align-items: center; }}
        .header-content {{ width: 100%; max-width: 1600px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; }}

        .app-logo {{ font-size: 20px; font-weight: 800; color: #4f46e5; margin-right: 30px; white-space: nowrap; }}

        /* FILTERS LEFT */
        .filters {{ display: flex; gap: 10px; flex: 1; }}
        .filter-btn {{ 
            padding: 8px 16px; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; border: 1px solid transparent; transition: all 0.2s;
            color: #6b7280; background: #f9fafb; border-color: #e5e7eb;
        }}
        .filter-btn:hover {{ transform: translateY(-1px); box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}

        /* COLOR CODED FILTERS */
        .f-all.active {{ background: #111827; color: white; }}
        .f-t1.active {{ background: var(--c-tier1); color: var(--t-tier1); border-color: var(--b-tier1); }}
        .f-t2.active {{ background: var(--c-tier2); color: var(--t-tier2); border-color: var(--b-tier2); }}
        .f-t3.active {{ background: var(--c-tier3); color: var(--t-tier3); border-color: var(--b-tier3); }}
        .f-corp.active {{ background: var(--c-corp); color: var(--t-corp); border-color: var(--b-corp); }}
        .f-nonp.active {{ background: var(--c-nonp); color: var(--t-nonp); border-color: var(--b-nonp); }}

        /* SEARCH RIGHT */
        .search-box {{ margin-left: 20px; position: relative; }}
        .search-input {{ 
            width: 250px; padding: 10px 15px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; outline: none; transition: width 0.2s;
        }}
        .search-input:focus {{ width: 350px; border-color: #4f46e5; }}

        /* GRID */
        .grid {{ max-width: 1600px; margin: 20px auto; display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; padding: 0 30px; }}

        /* JOB CARD */
        .card {{ background: white; border-radius: 10px; padding: 20px; border: 1px solid #e5e7eb; display: flex; flex-direction: column; position: relative; transition: all 0.2s; }}
        .card:hover {{ border-color: #4f46e5; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); transform: translateY(-2px); }}

        /* TAGS */
        .tags {{ display: flex; gap: 6px; margin-bottom: 12px; flex-wrap: wrap; }}
        .tag {{ font-size: 10px; font-weight: 700; padding: 4px 8px; border-radius: 4px; text-transform: uppercase; }}
        .t-tier1 {{ background: var(--c-tier1); color: var(--t-tier1); }}
        .t-tier2 {{ background: var(--c-tier2); color: var(--t-tier2); }}
        .t-tier3 {{ background: var(--c-tier3); color: var(--t-tier3); }}
        .t-corp {{ background: var(--c-corp); color: var(--t-corp); }}
        .t-nonp {{ background: var(--c-nonp); color: var(--t-nonp); }}

        .title {{ font-size: 16px; font-weight: 700; color: #111827; margin-bottom: 4px; line-height: 1.4; }}
        .company {{ font-size: 13px; color: #6b7280; font-weight: 500; margin-bottom: 15px; }}

        /* ACTIONS */
        .actions {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: auto; }}
        .btn {{ padding: 8px; border-radius: 6px; font-size: 12px; font-weight: 600; text-align: center; cursor: pointer; text-decoration: none; border: none; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }}

        .btn-details {{ background: #4f46e5; color: white; grid-column: span 2; }}
        .btn-details:hover {{ background: #4338ca; }}
        .btn-listing {{ background: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; }}
        .btn-listing:hover {{ background: #dbeafe; }}
        .btn-apply {{ background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; }}
        .btn-apply:hover {{ background: #d1fae5; }}

        /* STATUS */
        .status-wrap {{ margin-top: 12px; padding-top: 12px; border-top: 1px solid #f3f4f6; }}
        .status-select {{ width: 100%; padding: 6px; border-radius: 5px; border: 1px solid #e5e7eb; font-size: 12px; color: #374151; cursor: pointer; }}

        /* MODAL */
        .modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 2000; align-items: center; justify-content: center; }}
        .modal-box {{ background: white; width: 90%; max-width: 900px; height: 85vh; border-radius: 12px; display: flex; flex-direction: column; overflow: hidden; }}
        .modal-head {{ padding: 20px; border-bottom: 1px solid #e5e7eb; display: flex; justify-content: space-between; align-items: center; }}
        .modal-body {{ padding: 20px; overflow-y: auto; background: #f9fafb; flex: 1; }}

        .tabs {{ display: flex; gap: 2px; background: #f3f4f6; padding: 2px; border-radius: 8px; margin-bottom: 20px; }}
        .tab {{ flex: 1; padding: 10px; text-align: center; font-size: 12px; font-weight: 600; cursor: pointer; border-radius: 6px; color: #6b7280; transition: all 0.2s; }}
        .tab.active {{ background: white; color: #4f46e5; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}

        .field {{ margin-bottom: 15px; background: white; padding: 15px; border-radius: 8px; border: 1px solid #e5e7eb; }}
        .label {{ font-size: 11px; font-weight: 700; color: #9ca3af; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.5px; }}
        .val {{ font-size: 14px; color: #1f2937; line-height: 1.6; white-space: pre-line; }}
    </style>
</head>
<body>

<div class="header">
    <div class="header-content">
        <div class="app-logo">Strategic Match 🚀</div>

        <div class="filters">
            <div class="filter-btn f-all active" onclick="filter('all', this)">All ({total})</div>
            <div class="filter-btn f-t1" onclick="filter('Tier 1', this)">Tier 1 ({t1})</div>
            <div class="filter-btn f-t2" onclick="filter('Tier 2', this)">Tier 2 ({t2})</div>
            <div class="filter-btn f-t3" onclick="filter('Tier 3', this)">Tier 3 ({t3})</div>
            <div class="filter-btn f-corp" onclick="filter('Corporate', this)">Corp ({corp})</div>
            <div class="filter-btn f-nonp" onclick="filter('Nonprofit', this)">Nonprofit ({nonp})</div>
        </div>

        <div class="search-box">
            <input type="text" class="search-input" placeholder="Search roles or companies..." onkeyup="search(this.value)">
        </div>

        <a href="tracker.html" class="filter-btn" style="background:#111827;color:white;margin-left:10px;">Tracker</a>
    </div>
</div>

<div class="grid">
"""
    # RENDER CARDS
    for j in jobs:
        t_cls = "t-tier3"
        if "Tier 1" in j['tags']: t_cls = "t-tier1"
        elif "Tier 2" in j['tags']: t_cls = "t-tier2"

        s_cls = "t-nonp"
        if "Corporate" in j['tags']: s_cls = "t-corp"

        tags_html = f'<span class="tag {t_cls}">Tier {j["tier"]}</span> <span class="tag {s_cls}">{"Corporate" if "Corporate" in j["tags"] else "Nonprofit"}</span>'

        # Preview
        preview = ""
        if j.get('summary_bullets') and len(str(j['summary_bullets'])) > 10:
            preview = f'<div style="font-size:12px;color:#4b5563;margin-bottom:15px;background:#f9fafb;padding:10px;border-radius:6px;line-height:1.5;">{j["summary_bullets"][:200]}...</div>'

        html_content += f"""
        <div class="card" data-tags='{json.dumps(j['tags'])}' data-title="{j['title'].lower()} {j['company'].lower()}">
            <div class="tags">{tags_html}</div>
            <div class="title">{j['title']}</div>
            <div class="company">{j['company']}</div>
            {preview}

            <div class="actions">
                <button class="btn btn-details" onclick="openModal({j['id']})">View Full Details</button>
                <a href="{j['list_url']}" target="_blank" class="btn btn-listing">Listing</a>
                <a href="{j['app_url']}" target="_blank" class="btn btn-apply" onclick="updateStatus({j['id']}, 'Applied')">Apply</a>
            </div>

            <div class="status-wrap">
                <select class="status-select" onchange="updateStatus({j['id']}, this.value)">
                    <option value="New" {'selected' if j['status']=='New' else ''}>New</option>
                    <option value="Applied" {'selected' if j['status']=='Applied' else ''}>Applied</option>
                    <option value="Interview" {'selected' if j['status']=='Interview' else ''}>Interview</option>
                    <option value="Offer" {'selected' if j['status']=='Offer' else ''}>Offer</option>
                    <option value="Rejected" {'selected' if j['status']=='Rejected' else ''}>Rejected</option>
                </select>
            </div>
        </div>
        """

    html_content += f"""
</div>

<!-- MODAL -->
<div id="modal" class="modal" onclick="if(event.target===this)this.style.display='none'">
    <div class="modal-box">
        <div class="modal-head">
            <h2 id="m-title" style="margin:0;font-size:18px;"></h2>
            <button onclick="document.getElementById('modal').style.display='none'" style="border:none;background:none;font-size:20px;cursor:pointer;">&times;</button>
        </div>
        <div style="padding:20px 20px 0;">
            <div class="tabs">
                <div class="tab active" onclick="tab('strategy', this)">Strategy</div>
                <div class="tab" onclick="tab('interview', this)">Interview</div>
                <div class="tab" onclick="tab('assets', this)">Assets</div>
            </div>
        </div>
        <div class="modal-body">
            <div id="t-strategy" class="tab-content active"></div>
            <div id="t-interview" class="tab-content"></div>
            <div id="t-assets" class="tab-content"></div>
        </div>
    </div>
</div>

<script>
    const JOBS = {js_data};

    function filter(tag, btn) {{
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        document.querySelectorAll('.card').forEach(c => {{
            const t = JSON.parse(c.dataset.tags);
            if(tag === 'all') c.style.display = 'flex';
            else if(t.includes(tag)) c.style.display = 'flex';
            else c.style.display = 'none';
        }});
    }}

    function search(val) {{
        val = val.toLowerCase();
        document.querySelectorAll('.card').forEach(c => {{
            c.style.display = c.dataset.title.includes(val) ? 'flex' : 'none';
        }});
    }}

    function openModal(id) {{
        const job = JOBS.find(j => j.id == id);
        if(!job) return;

        document.getElementById('m-title').innerText = job.title + ' - ' + job.company;

        const f = (lbl, val) => val && val.length > 2 ? `<div class="field"><div class="label">${{lbl}}</div><div class="val">${{val}}</div></div>` : '';

        document.getElementById('t-strategy').innerHTML = 
            f('Company Overview', job.company_overview) + f('Role Insights', job.role_insights) + f('Key Requirements', job.key_requirements) + f('Red Flags', job.red_flags) + f('Cultural Fit', job.cultural_fit);

        document.getElementById('t-interview').innerHTML = 
            f('Interview Prep', job.interview_prep) + f('STAR Hooks', job.star_hooks) + f('Talking Points', job.talking_points) + f('Salary Intel', job.salary_intel);

        document.getElementById('t-assets').innerHTML = 
            f('Resume Summary', job.resume_summary) + f('Cover Letter', job.cover_letter) + f('Recruiter Email', job.recruiter_email) + f('Why Me', job.why_me_bullets);

        document.getElementById('modal').style.display = 'flex';
    }}

    function tab(name, btn) {{
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        btn.classList.add('active');
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        document.getElementById('t-'+name).classList.add('active');
    }}

    async function updateStatus(id, status) {{
        try {{
            await fetch('{API_BASE}/api/update_status', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{id, status}})
            }});
        }} catch(e) {{ console.error('Status update failed:', e); }}
    }}
</script>
</body>
</html>
"""

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ Dashboard Built: {total} jobs, Fixed UI, Color-Coded, Functional Links")

if __name__ == "__main__":
    build_dashboard()
