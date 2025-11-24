#!/usr/bin/env python3
"""
Strategic Match - MASTER DASHBOARD BUILDER
Generates index.html (Dashboard) linking to tracker.html (Standalone Tracker)
"""
import sqlite3
import json
from datetime import datetime

# This base URL is used for the Javascript inside the dashboard to talk to the API
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
            # Safe Defaults
            if not j.get('tier'): j['tier'] = 3
            if not j.get('status'): j['status'] = 'New'
            if not j.get('match_score'): j['match_score'] = 0

            # Safe Strings
            for k in ['company_overview', 'role_insights', 'key_requirements', 
                      'interview_prep', 'talking_points', 'red_flags', 'full_description']:
                if j.get(k) is None: j[k] = ""

            # Fix URL
            raw_url = j.get('url', '#')
            if raw_url and not raw_url.startswith('http') and raw_url != '#':
                raw_url = 'https://' + raw_url
            j['app_url'] = raw_url
            j['list_url'] = raw_url

            tags = []
            tags.append(f"Tier {j['tier']}")
            if j['match_score'] >= 90: tags.append("High Match")
            if 'corporate' in str(j.get('search_type','')).lower(): tags.append("Corporate")
            elif 'nonprofit' in str(j.get('search_type','')).lower(): tags.append("Nonprofit")

            j['tags'] = tags
            jobs.append(j)
        conn.close()
        return jobs
    except Exception as e:
        print(f"Error fetching DB: {e}")
        return []

def build_files():
    print("🚀 Building Polished Dashboard...")

    jobs = db_get_jobs()
    jobs_json = json.dumps(jobs)

    total = len(jobs)
    t1 = len([j for j in jobs if j['tier'] == 1])
    t2 = len([j for j in jobs if j['tier'] == 2])
    t3 = len([j for j in jobs if j['tier'] == 3])

    common_head = """
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root { 
            --primary: #2563eb; 
            --primary-dark: #1d4ed8;
            --bg-color: #f8fafc; 
            --card-bg: #ffffff; 
            --text-main: #0f172a;
            --text-secondary: #64748b;
            --header-bg: #1e3a8a;
            --header-text: #f1f5f9;
            --blue-company: #1e40af;
            --tier-1: #f59e0b;
            --tier-2: #94a3b8;
            --tier-3: #cd7f32;
            --corporate: #3b82f6;
            --nonprofit: #10b981;
            --high-match: #8b5cf6;
            --border-color: #e2e8f0;
        }
        * { box-sizing: border-box; }
        body { 
            font-family: 'Inter', sans-serif; 
            background: var(--bg-color); 
            color: var(--text-main); 
            margin: 0; 
            padding-top: 120px; 
            min-height: 100vh;
        }
        .header {
            position: fixed;
            top: 0; left: 0; right: 0;
            background: var(--header-bg);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding: 15px 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            z-index: 1000;
            transition: transform 0.3s ease;
        }
        .header.hidden { transform: translateY(-100%); }
        .app-title {
            font-size: 28px;
            font-weight: 800;
            color: var(--header-text);
            margin: 0 0 12px 0;
            letter-spacing: -0.5px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .app-title-icon {
            font-size: 24px;
        }
        .header-content {
            max-width: 1600px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .controls-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }
        .search-section {
            flex: 1;
            max-width: 400px;
            position: relative;
        }
        .search-input {
            width: 100%;
            padding: 12px 15px 12px 45px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            font-size: 14px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
        }
        .search-input::placeholder {
            color: rgba(255, 255, 255, 0.7);
        }
        .search-input:focus {
            outline: none;
            border-color: rgba(255, 255, 255, 0.5);
            background: rgba(255, 255, 255, 0.15);
        }
        .search-icon {
            position: absolute;
            left: 15px; top: 50%; transform: translateY(-50%);
            color: rgba(255, 255, 255, 0.7);
            font-size: 18px;
        }
        .filter-badges {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        .badge-filter {
            padding: 8px 14px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: var(--header-text);
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .badge-filter:hover {
            background: rgba(255, 255, 255, 0.2);
            border-color: rgba(255, 255, 255, 0.3);
        }
        .badge-filter.active {
            background: rgba(255, 255, 255, 0.9);
            color: var(--header-bg);
            border-color: rgba(255, 255, 255, 0.9);
        }
        .badge-filter.tier-1 { background: var(--tier-1); color: white; border-color: var(--tier-1); }
        .badge-filter.tier-2 { background: var(--tier-2); color: white; border-color: var(--tier-2); }
        .badge-filter.tier-3 { background: var(--tier-3); color: white; border-color: var(--tier-3); }
        .badge-filter.corporate { background: var(--corporate); color: white; border-color: var(--corporate); }
        .badge-filter.nonprofit { background: var(--nonprofit); color: white; border-color: var(--nonprofit); }
        .badge-filter.high-match { background: var(--high-match); color: white; border-color: var(--high-match); }
        .badge-filter.all-jobs { background: #60a5fa; color: white; border-color: #60a5fa; }
        
        .tracker-link {
            margin-left: auto;
            background: #8b5cf6;
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 700;
            font-size: 13px;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: background 0.2s;
        }
        .tracker-link:hover {
            background: #7c3aed;
        }
        .grid-container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
            gap: 25px;
        }
        .job-card {
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            transition: transform 0.2s, box-shadow 0.2s;
            display: flex;
            flex-direction: column;
            border: 1px solid var(--border-color);
        }
        .job-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1);
            border-color: var(--primary);
        }
        .card-tags { display: flex; gap: 6px; margin-bottom: 12px; flex-wrap: wrap; }
        .tag { font-size: 10px; font-weight: 700; padding: 4px 8px; border-radius: 4px; text-transform: uppercase; letter-spacing: 0.5px; }
        .tag-tier-1 { background: #fef3c7; color: #92400e; border: 1px solid #fcd34d; }
        .tag-tier-2 { background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }
        .tag-tier-3 { background: #fff7ed; color: #c2410c; border: 1px solid #fdba74; }
        .tag-high { background: #ede9fe; color: #5b21b6; border: 1px solid #c4b5fd; }
        .tag-corp { background: #dbeafe; color: #1e40af; border: 1px solid #93c5fd; }
        .tag-nonprofit { background: #dcfce7; color: #166534; border: 1px solid #86efac; }

        .job-title {
            font-size: 18px;
            font-weight: 700;
            color: #0f172a;
            margin: 0 0 4px 0;
            line-height: 1.3;
        }
        .company-name {
            font-size: 14px;
            font-weight: 600;
            color: var(--blue-company);
            margin-bottom: 12px;
        }
        .quick-links {
            display: flex;
            gap: 6px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .ql-btn {
            font-size: 11px;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 20px;
            background: #f8fafc;
            color: #64748b;
            border: 1px solid #e2e8f0;
            cursor: pointer;
            transition: all 0.1s;
        }
        .ql-btn:hover { background: #e2e8f0; color: #0f172a; border-color: #cbd5e1; }
        .action-buttons {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: auto;
        }
        .btn-3d {
            padding: 10px;
            border: none;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 700;
            cursor: pointer;
            color: white;
            text-align: center;
            text-decoration: none;
            box-shadow: 0 2px 0 rgba(0,0,0,0.1);
            transition: transform 0.1s;
        }
        .btn-3d:active { transform: translateY(2px); box-shadow: none; }
        .btn-details { background: #2563eb; }
        .btn-listing { background: #3b82f6; }
        .btn-apply { background: #10b981; }
        .btn-track { background: #8b5cf6; }
        .status-row {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #f1f5f9;
        }
        .status-select { width: 100%; padding: 8px; border-radius: 6px; border: 1px solid #cbd5e1; font-weight: 600; }
        .notes-area { width: 100%; margin-top: 8px; padding: 8px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 12px; resize: vertical; min-height: 40px; }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); z-index: 2000; align-items: center; justify-content: center; }
        .modal-content { background: white; width: 90%; max-width: 700px; max-height: 85vh; border-radius: 12px; padding: 30px; overflow-y: auto; }
        .toast { position: fixed; bottom: 20px; right: 20px; background: #10b981; color: white; padding: 12px 24px; border-radius: 8px; font-weight: 600; transform: translateY(100px); transition: transform 0.3s; }
        .toast.show { transform: translateY(0); }
        @media (max-width: 768px) { 
            .controls-row { flex-direction: column; align-items: stretch; }
            .search-section, .tracker-link { width: 100%; max-width: none; }
            .filter-badges { justify-content: flex-start; overflow-x: auto; padding-bottom: 5px; }
            .app-title { font-size: 24px; }
        }
    </style>
    """

    wired_js = f"""
    <script>
        const API_BASE = "{API_BASE}";
        let lastScroll = 0;
        window.addEventListener('scroll', () => {{
            const currentScroll = window.pageYOffset;
            const header = document.querySelector('.header');
            if (currentScroll > lastScroll && currentScroll > 100) {{
                header.classList.add('hidden');
            }} else {{
                header.classList.remove('hidden');
            }}
            lastScroll = currentScroll;
        }});
        function showToast(msg) {{
            const toast = document.getElementById('toast');
            toast.innerText = msg;
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 3000);
        }}
        async function updateStatus(id, newStatus) {{
            try {{
                const res = await fetch(`${{API_BASE}}/api/update_status`, {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{id: id, status: newStatus}})
                }});
                if (res.ok) showToast(`✅ Status synced: ${{newStatus}}`);
            }} catch (e) {{ console.error(e); }}
        }}
        async function saveNote(id, note) {{
            try {{
                await fetch(`${{API_BASE}}/api/save_note`, {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{id: id, note: note}})
                }});
            }} catch(e) {{ }}
        }}
        function markApplied(id, url) {{ updateStatus(id, 'Applied'); window.open(url, '_blank'); }}
        function markViewed(id, url) {{ updateStatus(id, 'Viewed'); window.open(url, '_blank'); }}
        function filterJobs(criteria) {{
            const cards = document.querySelectorAll('.job-card');
            const btns = document.querySelectorAll('.badge-filter');
            btns.forEach(b => b.classList.remove('active'));
            if(event && event.target) event.target.classList.add('active');
            cards.forEach(card => {{
                const tags = card.dataset.tags.toLowerCase();
                let match = true;
                if (criteria === 'high' && !tags.includes('high')) match = false;
                if (criteria === 'corp' && !tags.includes('corporate')) match = false;
                if (criteria === 'nonprofit' && !tags.includes('nonprofit')) match = false;
                if (criteria === 't1' && !tags.includes('tier 1')) match = false;
                if (criteria === 't2' && !tags.includes('tier 2')) match = false;
                if (criteria === 't3' && !tags.includes('tier 3')) match = false;
                card.style.display = match ? 'flex' : 'none';
            }});
        }}
        function searchJobs(query) {{
            const cards = document.querySelectorAll('.job-card');
            cards.forEach(card => {{
                card.style.display = card.innerText.toLowerCase().includes(query.toLowerCase()) ? 'flex' : 'none';
            }});
        }}
        document.addEventListener('DOMContentLoaded', () => {{
            document.querySelectorAll('.notes-area').forEach(area => {{
                area.addEventListener('change', (e) => {{
                    const id = e.target.id.replace('note-', '');
                    saveNote(id, e.target.value);
                }});
            }});
        }});
    </script>
    """

    index_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Strategic Match Dashboard</title>
    {common_head}
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="app-title">
                <span class="app-title-icon">🎯</span>
                Strategic Match
            </div>
            <div class="controls-row">
                <div class="search-section">
                    <span class="search-icon">🔍</span>
                    <input type="text" class="search-input" placeholder="Search jobs..." onkeyup="searchJobs(this.value)">
                </div>
                <div class="filter-badges">
                    <div class="badge-filter all-jobs active" onclick="filterJobs('all')">All Jobs ({total})</div>
                    <div class="badge-filter tier-1" onclick="filterJobs('t1')">🥇 Tier 1 ({t1})</div>
                    <div class="badge-filter tier-2" onclick="filterJobs('t2')">🥈 Tier 2 ({t2})</div>
                    <div class="badge-filter tier-3" onclick="filterJobs('t3')">🥉 Tier 3 ({t3})</div>
                    <div class="badge-filter high-match" onclick="filterJobs('high')">🔥 High Match</div>
                    <div class="badge-filter corporate" onclick="filterJobs('corp')">🏢 Corporate</div>
                    <div class="badge-filter nonprofit" onclick="filterJobs('nonprofit')">💚 Nonprofit</div>
                </div>
                <a href="tracker.html" class="tracker-link">
                    <span>📋</span>
                    Tracker
                </a>
            </div>
        </div>
    </div>
    <div class="grid-container">
        {''.join([render_job_card(j) for j in jobs])}
    </div>
    <div id="toast" class="toast">Notification</div>
    <div id="modal" class="modal" onclick="if(event.target===this)document.getElementById('modal').style.display='none'">
        <div id="modal-content" class="modal-content"></div>
    </div>
    {wired_js}
    <script>
    function openModal(id, section) {{
        const jobs = {jobs_json};
        const job = jobs.find(j => j.id == id);
        const content = document.getElementById('modal-content');
        let html = `
            <h2 style="margin-bottom:5px">${{job.title}}</h2>
            <h3 style="color:var(--blue-company); margin-top:0">${{job.company}}</h3>
            <div style="margin-bottom:20px; display:flex; gap:5px;">
                ${{job.tags.map(t => `<span class="tag tag-tier-1">${{t}}</span>`).join('')}}
            </div>
            <hr style="border:0; border-top:1px solid #e2e8f0; margin:20px 0;">
        `;
        const fields = [
            ['Company Overview', job.company_overview],
            ['Role Insights', job.role_insights],
            ['Key Requirements', job.key_requirements],
            ['Interview Prep', job.interview_prep],
            ['Talking Points', job.talking_points],
            ['Red Flags', job.red_flags],
            ['Full Description', job.full_description]
        ];
        let hasData = false;
        fields.forEach(([label, text]) => {{
            if(text && text.length > 10) {{
                hasData = true;
                html += `<div id="${{label}}" style="padding:15px; margin-bottom:15px; background:#f8fafc; border-radius:8px; border:1px solid #e2e8f0;">
                    <h4 style="margin-top:0; color:#475569; font-size:12px; text-transform:uppercase;">${{label}}</h4>
                    <p style="font-size:14px; line-height:1.6; white-space: pre-line;">${{text}}</p>
                </div>`;
            }}
        }});
        if(!hasData) {{
            html += `<div style="padding:20px; text-align:center; color:#64748b;">No rich analysis data available for this role.</div>`;
        }}
        content.innerHTML = html;
        document.getElementById('modal').style.display = 'flex';
    }}
    </script>
</body>
</html>"""

    # --- CHANGED: Removed tracker.html writing logic ---
    with open('index.html', 'w', encoding='utf-8') as f: f.write(index_html)
    print("✅ Generated Polished Dashboard (index.html only)")

def render_job_card(j):
    quick_links = []
    if len(str(j.get('interview_prep', ''))) > 10: quick_links.append(('⚡ Prep', 'Interview Prep'))
    if len(str(j.get('talking_points', ''))) > 10: quick_links.append(('🗣️ Talk', 'Talking Points'))
    ql_html = ''.join([f'<div class="ql-btn" onclick="openModal({j["id"]}, \'{sec}\')">{label}</div>' for label, sec in quick_links])
    tag_html = ''
    for t in j['tags']:
        cls = 'tag-tier-3'
        if 'tier 1' in t.lower(): cls = 'tag-tier-1'
        elif 'tier 2' in t.lower(): cls = 'tag-tier-2'
        elif 'high' in t.lower(): cls = 'tag-high'
        elif 'corp' in t.lower(): cls = 'tag-corp'
        elif 'nonprofit' in t.lower(): cls = 'tag-nonprofit'
        tag_html += f'<span class="tag {cls}">{t}</span>'
    status_opts = ''.join([f'<option value="{s}" {"selected" if j["status"]==s else ""}>{s}</option>' for s in ["New", "Applied", "Interview", "Offer", "Rejected"]])
    return f"""
    <div class="job-card" data-tags="{','.join(j['tags'])}">
        <div class="card-tags">{tag_html}</div>
        <div class="job-title">{j['title']}</div>
        <div class="company-name">{j['company']}</div>
        <div class="quick-links">{ql_html}</div>
        <div class="action-buttons">
            <button class="btn-3d btn-details" onclick="openModal({j['id']}, null)">Details</button>
            <button class="btn-3d btn-listing" onclick="markViewed({j['id']}, '{j['list_url']}')">Listing</button>
            <button class="btn-3d btn-apply" onclick="markApplied({j['id']}, '{j['app_url']}')">APPLY</button>
            <a href="tracker.html" class="btn-3d btn-track">Track</a>
        </div>
        <div class="status-row">
            <select id="status-{j['id']}" class="status-select" onchange="updateStatus({j['id']}, this.value)">
                {status_opts}
            </select>
            <textarea id="note-{j['id']}" class="notes-area" placeholder="Notes...">{j.get('notes','') if j.get('notes') else ''}</textarea>
        </div>
    </div>
    """

if __name__ == "__main__":
    build_files()
