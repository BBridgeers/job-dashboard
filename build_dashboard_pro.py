#!/usr/bin/env python3
"""
Strategic Match - MASTER DASHBOARD BUILDER (Cloud Sync)
Generates:
1. index.html (Main Dashboard)
2. tracker.html (Tracker Page)
Connects to Render.com Backend for REAL-TIME SYNC across devices.
"""
import sqlite3
import json
from datetime import datetime

# --- CLOUD CONFIGURATION ---
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
            if not j.get('tier'): j['tier'] = 3
            if not j.get('status'): j['status'] = 'New'
            if not j.get('match_score'): j['match_score'] = 0
            j['app_url'] = j.get('application_url') if j.get('application_url') else j.get('url', '#')
            j['list_url'] = j.get('url', '#')

            tags = []
            tags.append(f"Tier {j['tier']}")
            if j['match_score'] >= 90: tags.append("High Match (90+)")
            if 'corporate' in str(j.get('search_type','')).lower(): tags.append("Corporate")
            elif 'nonprofit' in str(j.get('search_type','')).lower(): tags.append("Nonprofit")
            elif not any(x in str(j.get('search_type','')).lower() for x in ['corporate','nonprofit']): 
                if any(x in j['title'].lower() for x in ['program', 'community', 'volunteer', 'development']): tags.append("Nonprofit")
                else: tags.append("Corporate")
            j['tags'] = tags
            jobs.append(j)
        conn.close()
        return jobs
    except Exception as e:
        print(f"Error fetching DB: {e}")
        return []

def build_files():
    print("🚀 Building Dashboard with CLOUD SYNC Wiring...")

    jobs = db_get_jobs()
    jobs_json = json.dumps(jobs)

    total = len(jobs)
    t1 = len([j for j in jobs if j['tier'] == 1])
    t2 = len([j for j in jobs if j['tier'] == 2])
    t3 = len([j for j in jobs if j['tier'] == 3])
    high_match = len([j for j in jobs if j['match_score'] >= 90])
    corp = len([j for j in jobs if 'Corporate' in j['tags']])
    nonprofit = len([j for j in jobs if 'Nonprofit' in j['tags']])

    common_head = """
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #6366f1; --bg-grad: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); --card-bg: #ffffff; --text-main: #1e293b; --text-sub: #64748b; --success: #10b981; --blue-company: #1e40af; --tag-bg: #fee2e2; --tag-text: #991b1b; }
        * { box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: var(--bg-grad); color: var(--text-main); margin: 0; padding-top: 140px; min-height: 100vh; }
        .header { position: fixed; top: 0; left: 0; right: 0; background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); padding: 15px 30px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); z-index: 1000; transition: transform 0.3s ease; }
        .header.hidden { transform: translateY(-100%); }
        .header-content { max-width: 1600px; margin: 0 auto; display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 15px; }
        .filter-badges { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
        .badge-filter { padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; cursor: pointer; border: 1px solid #e2e8f0; background: white; transition: all 0.2s; display: flex; align-items: center; gap: 6px; color: var(--text-sub); }
        .badge-filter:hover, .badge-filter.active { background: var(--primary); color: white; border-color: var(--primary); transform: translateY(-1px); box-shadow: 0 2px 5px rgba(99, 102, 241, 0.3); }
        .header-right { display: flex; align-items: center; gap: 15px; flex-grow: 1; justify-content: flex-end; }
        .search-bar { position: relative; width: 300px; }
        .search-input { width: 100%; padding: 8px 15px 8px 35px; border-radius: 8px; border: 1px solid #cbd5e1; font-size: 13px; }
        .search-icon { position: absolute; left: 10px; top: 50%; transform: translateY(-50%); color: #94a3b8; font-size: 12px; }
        .tracker-btn { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; padding: 8px 16px; border-radius: 8px; text-decoration: none; font-weight: 700; font-size: 13px; box-shadow: 0 4px 6px -1px rgba(245, 158, 11, 0.3); transition: transform 0.2s; white-space: nowrap; }
        .tracker-btn:hover { transform: scale(1.05); }
        .grid-container { max-width: 1600px; margin: 0 auto; padding: 20px; display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 25px; }
        .job-card { background: white; border-radius: 16px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); transition: transform 0.2s, box-shadow 0.2s; position: relative; border: 1px solid #f1f5f9; display: flex; flex-direction: column; }
        .job-card:hover { transform: translateY(-5px); box-shadow: 0 15px 30px -5px rgba(0,0,0,0.1); }
        .card-tags { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 10px; }
        .filter-tag { background: var(--tag-bg); color: var(--tag-text); font-size: 10px; font-weight: 700; padding: 3px 8px; border-radius: 6px; text-transform: uppercase; }
        .job-title { font-size: 16px; font-weight: 700; color: #0f172a; margin: 0 0 5px 0; line-height: 1.4; }
        .job-location { font-size: 12px; color: #64748b; margin-bottom: 2px; }
        .company-name { font-size: 13px; font-weight: 700; color: var(--blue-company); margin-bottom: 8px; }
        .match-summary { font-size: 12px; color: var(--success); font-weight: 600; margin-bottom: 15px; line-height: 1.4; background: #ecfdf5; padding: 6px 10px; border-radius: 6px; }
        .quick-links { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 15px; }
        .ql-btn { font-size: 11px; padding: 4px 8px; border-radius: 12px; background: #f1f5f9; color: #475569; cursor: pointer; border: 1px solid #e2e8f0; transition: all 0.2s; }
        .ql-btn:hover { background: #e2e8f0; color: #1e293b; }
        .action-buttons { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: auto; }
        .btn-3d { padding: 8px; border: none; border-radius: 8px; font-size: 11px; font-weight: 700; cursor: pointer; text-align: center; text-decoration: none; transition: transform 0.1s; color: white; display: flex; align-items: center; justify-content: center; }
        .btn-3d:active { transform: scale(0.95); }
        .btn-details { background: linear-gradient(to bottom, #6366f1, #4f46e5); box-shadow: 0 3px 0 #3730a3; }
        .btn-listing { background: linear-gradient(to bottom, #3b82f6, #2563eb); box-shadow: 0 3px 0 #1d4ed8; }
        .btn-apply { background: linear-gradient(to bottom, #10b981, #059669); box-shadow: 0 3px 0 #047857; }
        .btn-track { background: linear-gradient(to bottom, #f59e0b, #d97706); box-shadow: 0 3px 0 #b45309; }
        .status-row { margin-top: 15px; padding-top: 15px; border-top: 1px solid #f1f5f9; }
        .status-select { width: 100%; padding: 6px; border-radius: 6px; border: 1px solid #cbd5e1; font-size: 12px; font-weight: 600; color: #334155; }
        .notes-area { width: 100%; margin-top: 10px; padding: 8px; border: 1px solid #e2e8f0; border-radius: 6px; font-family: inherit; font-size: 12px; resize: vertical; min-height: 40px; }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); backdrop-filter: blur(4px); z-index: 2000; align-items: center; justify-content: center; }
        .modal-content { background: white; width: 90%; max-width: 800px; max-height: 90vh; border-radius: 20px; overflow-y: auto; padding: 30px; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); animation: modalSlide 0.3s ease; }
        @keyframes modalSlide { from {transform: translateY(50px); opacity: 0;} to {transform: translateY(0); opacity: 1;} }
        .toast { position: fixed; bottom: 20px; right: 20px; background: #10b981; color: white; padding: 12px 24px; border-radius: 8px; font-weight: 600; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); transform: translateY(100px); transition: transform 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55); z-index: 3000; }
        .toast.show { transform: translateY(0); }
        .vertical-stack { max-width: 800px; margin: 0 auto 40px auto; display: flex; flex-direction: column; gap: 15px; }
        .status-section { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }
        .status-header { background: #f8fafc; padding: 12px 20px; font-weight: 700; color: #475569; font-size: 13px; text-transform: uppercase; display: flex; justify-content: space-between; cursor: pointer; border-bottom: 1px solid #e2e8f0; }
        .status-header:hover { background: #f1f5f9; }
        .status-content { padding: 0; display: block; }
        .v-card { padding: 12px 20px; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; transition: background 0.2s; }
        .v-card:last-child { border-bottom: none; }
        .v-card:hover { background: #f8fafc; }
        .v-info { display: flex; flex-direction: column; gap: 2px; }
        .v-title { font-weight: 600; font-size: 14px; color: #1e293b; }
        .v-company { font-size: 12px; color: #64748b; }
        .v-date { font-size: 11px; color: #94a3b8; }
        @media (max-width: 768px) { body { padding-top: 180px; } .header-content { flex-direction: column; align-items: stretch; } .header-right { justify-content: space-between; width: 100%; } .search-bar { width: 100%; max-width: none; } .filter-badges { overflow-x: auto; padding-bottom: 5px; } }
    </style>
    """

    # --- CLOUD-WIRED JS ---
    # Points to the Render URL for persistence
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

                if (res.ok) {{
                    console.log(`Synced Job ${{id}} to ${{newStatus}}`);
                    showToast(`✅ Status synced: ${{newStatus}}`);
                    const select = document.querySelector(`#status-${{id}}`);
                    if(select) select.value = newStatus;
                }} else {{
                    showToast('❌ Error saving status');
                }}
            }} catch (e) {{
                console.error(e);
                showToast('❌ Connection error (Check Cloud Server)');
            }}
        }}

        async function saveNote(id, note) {{
            try {{
                await fetch(`${{API_BASE}}/api/save_note`, {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{id: id, note: note}})
                }});
            }} catch(e) {{ console.error(e); }}
        }}

        function markApplied(id, url) {{
            updateStatus(id, 'Applied');
            window.open(url, '_blank');
        }}

        function markViewed(id, url) {{
            const select = document.querySelector(`#status-${{id}}`);
            if(select && select.value === 'New') {{
                updateStatus(id, 'Viewed');
            }}
            window.open(url, '_blank');
        }}

        function filterJobs(criteria) {{
            const cards = document.querySelectorAll('.job-card');
            const btns = document.querySelectorAll('.badge-filter');
            btns.forEach(b => b.classList.remove('active'));
            if(event.target) event.target.classList.add('active');

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

        function toggleSection(id) {{
            const el = document.getElementById(id);
            el.style.display = el.style.display === 'none' ? 'block' : 'none';
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

    # === 1. BUILD INDEX.HTML ===
    index_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Job Match Dashboard</title>
    {common_head}
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="filter-badges">
                <div class="badge-filter active" onclick="filterJobs('all')">📊 Total: {total}</div>
                <div class="badge-filter" onclick="filterJobs('t1')">🥇 Tier 1: {t1}</div>
                <div class="badge-filter" onclick="filterJobs('t2')">🥈 Tier 2: {t2}</div>
                <div class="badge-filter" onclick="filterJobs('t3')">🥉 Tier 3: {t3}</div>
                <div class="badge-filter" onclick="filterJobs('high')">🔥 High Match: {high_match}</div>
                <div class="badge-filter" onclick="filterJobs('corp')">🏢 Corporate: {corp}</div>
                <div class="badge-filter" onclick="filterJobs('nonprofit')">💚 Nonprofit: {nonprofit}</div>
            </div>

            <div class="header-right">
                <div class="search-bar">
                    <span class="search-icon">🔍</span>
                    <input type="text" class="search-input" placeholder="Search jobs..." onkeyup="searchJobs(this.value)">
                </div>
                <a href="tracker.html" class="tracker-btn">📋 Job Match Tracker</a>
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
            <div style="margin-bottom:20px">
                ${{job.tags.map(t => `<span class="filter-tag">${{t}}</span>`).join(' ')}}
            </div>
            <hr style="border:0; border-top:1px solid #e2e8f0; margin:20px 0;">
        `;

        const fields = [
            ['Company Overview', job.company_overview],
            ['Role Insights', job.role_insights || job.why_this_role],
            ['Key Requirements', job.key_requirements],
            ['Interview Prep', job.interview_prep],
            ['Talking Points', job.talking_points],
            ['Red Flags', job.red_flags],
            ['Full Description', job.full_description]
        ];

        fields.forEach(([label, text]) => {{
            if(text && text.length > 5) {{
                const isTarget = section && label.toLowerCase().includes(section.split(' ')[0].toLowerCase());
                html += `<div id="${{label}}" style="padding:15px; margin-bottom:15px; background:${{isTarget ? '#e0e7ff' : '#f8fafc'}}; border-radius:10px; border:1px solid ${{isTarget ? '#6366f1' : '#e2e8f0'}};">
                    <h4 style="margin-top:0; color:#475569; text-transform:uppercase; font-size:12px;">${{label}}</h4>
                    <p style="white-space: pre-line; font-size:14px; line-height:1.6;">${{text}}</p>
                </div>`;
            }}
        }});

        content.innerHTML = html;
        document.getElementById('modal').style.display = 'flex';

        if(section) {{
            setTimeout(() => {{
                const el = document.getElementById(section); 
                if(el) el.scrollIntoView({{behavior:'smooth', block:'center'}});
            }}, 100);
        }}
    }}
    </script>
</body>
</html>"""

    # === 2. BUILD TRACKER.HTML ===
    tracker_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Job Tracker</title>
    {common_head}
</head>
<body>
    <div class="header">
        <div class="header-content">
            <a href="index.html" class="badge-filter" style="color:var(--primary)">← Back to Dashboard</a>
            <h2>📋 Application Tracker</h2>
        </div>
    </div>

    <div style="padding: 20px; max-width: 1000px; margin: 0 auto;">
        <h3 style="color:#64748b; margin-bottom:20px;">Pipeline Stages</h3>

        <div class="vertical-stack">
            {render_vertical_section('New', jobs)}
            {render_vertical_section('Viewed', jobs)}
            {render_vertical_section('Applied', jobs)}
            {render_vertical_section('Interview', jobs)}
            {render_vertical_section('Offer', jobs)}
            {render_vertical_section('Rejected', jobs)}
        </div>

        <h3 style="margin-top: 40px; color:#64748b; margin-bottom:20px;">All Applications Table</h3>
        <table style="width:100%; border-collapse:collapse; background:white; border-radius:12px; overflow:hidden; box-shadow:0 4px 6px rgba(0,0,0,0.05); border:1px solid #e2e8f0;">
            <thead style="background:#f8fafc; text-align:left; border-bottom:1px solid #e2e8f0;">
                <tr>
                    <th style="padding:12px 20px; font-size:13px; color:#64748b;">Status</th>
                    <th style="padding:12px 20px; font-size:13px; color:#64748b;">Job Title</th>
                    <th style="padding:12px 20px; font-size:13px; color:#64748b;">Company</th>
                    <th style="padding:12px 20px; font-size:13px; color:#64748b;">Added</th>
                    <th style="padding:12px 20px; font-size:13px; color:#64748b;">Action</th>
                </tr>
            </thead>
            <tbody>
                {''.join([render_table_row(j) for j in jobs])}
            </tbody>
        </table>
    </div>

    {wired_js}
</body>
</html>"""

    with open('index.html', 'w', encoding='utf-8') as f: f.write(index_html)
    with open('tracker.html', 'w', encoding='utf-8') as f: f.write(tracker_html)

    print("✅ Generated Cloud-Wired index.html and tracker.html")

def render_job_card(j):
    quick_links = []
    if len(j.get('interview_prep', '')) > 10: quick_links.append(('⚡ Prep', 'Interview Prep'))
    if len(j.get('talking_points', '')) > 10: quick_links.append(('🗣️ Talk', 'Talking Points'))
    if len(j.get('red_flags', '')) > 10: quick_links.append(('🚩 Flags', 'Red Flags'))
    if len(j.get('company_overview', '')) > 10: quick_links.append(('🏢 Info', 'Company Overview'))

    ql_html = ''.join([f'<div class="ql-btn" onclick="openModal({j["id"]}, \'{sec}\')">{label}</div>' for label, sec in quick_links])

    statuses = ["New", "Viewed", "Applied", "Phone Screen", "Interview", "Offer", "Rejected"]
    status_opts = ''.join([f'<option value="{s}" {"selected" if j["status"]==s else ""}>{s}</option>' for s in statuses])

    return f"""
    <div class="job-card" data-tags="{','.join(j['tags'])}">
        <div class="card-tags">
            {''.join([f'<span class="filter-tag">{t}</span>' for t in j['tags']])}
        </div>
        <div class="job-title">{j['title']}</div>
        <div class="job-location">📍 {j['location']}</div>
        <div class="company-name">{j['company']}</div>
        <div class="match-summary">🎯 {j['match_score']}% Match</div>
        <div class="quick-links">{ql_html}</div>

        <div class="action-buttons">
            <button class="btn-3d btn-details" onclick="openModal({j['id']}, null)">📄 Details</button>
            <button class="btn-3d btn-listing" onclick="markViewed({j['id']}, '{j['list_url']}')">🔗 Listing</button>
            <button class="btn-3d btn-apply" onclick="markApplied({j['id']}, '{j['app_url']}')">🚀 Apply</button>
            <a href="tracker.html" class="btn-3d btn-track">📋 Track</a>
        </div>

        <div class="status-row">
            <select id="status-{j['id']}" class="status-select" onchange="updateStatus({j['id']}, this.value)">
                {status_opts}
            </select>
            <textarea id="note-{j['id']}" class="notes-area" placeholder="Notes...">{j.get('notes','')}</textarea>
        </div>
    </div>
    """

def render_vertical_section(status, jobs):
    sec_jobs = [j for j in jobs if j.get('status') == status]
    count = len(sec_jobs)
    cards = ''.join([f"""
        <div class="v-card" onclick="window.location.href='index.html?job={j['id']}'" style="cursor:pointer;">
            <div class="v-info">
                <div class="v-title">{j['title']}</div>
                <div class="v-company">{j['company']}</div>
            </div>
            <div class="v-date">{j['date_added']}</div>
        </div>
    """ for j in sec_jobs])
    display = 'block' if count > 0 else 'none'
    return f"""
    <div class="status-section">
        <div class="status-header" onclick="toggleSection('sec-{status}')">
            <span>{status}</span>
            <span style="background:#e2e8f0; padding:2px 8px; border-radius:10px; font-size:11px;">{count}</span>
        </div>
        <div id="sec-{status}" class="status-content" style="display:{display}">
            {cards if count > 0 else '<div style="padding:15px; font-size:13px; color:#94a3b8;">No jobs in this stage</div>'}
        </div>
    </div>
    """

def render_table_row(j):
    return f"""
    <tr style="border-bottom:1px solid #f1f5f9;">
        <td style="padding:12px 20px;"><span class="filter-tag">{j['status']}</span></td>
        <td style="padding:12px 20px; font-weight:600; font-size:14px;">{j['title']}</td>
        <td style="padding:12px 20px; font-size:13px;">{j['company']}</td>
        <td style="padding:12px 20px; color:#64748b; font-size:12px;">{j['date_added']}</td>
        <td style="padding:12px 20px;"><a href="index.html" style="color:var(--primary); text-decoration:none; font-weight:600; font-size:12px;">View</a></td>
    </tr>
    """

if __name__ == "__main__":
    build_files()
