#!/usr/bin/env python3
"""
Strategic Match - ULTIMATE PRO DASHBOARD
Features: Stacked Kanban + Table, Quick-Jump Links, Full Data
"""
import sqlite3
import json

def build_dashboard():
    print("🎯 Building ULTIMATE PRO Dashboard (Kanban + Table)...")
    
    conn = sqlite3.connect('jobs.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all columns dynamically to prevent errors
    cursor.execute("PRAGMA table_info(jobs)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Select ALL available columns
    cursor.execute(f"SELECT * FROM jobs ORDER BY tier ASC, match_score DESC, date_added DESC")
    
    jobs = []
    for row in cursor.fetchall():
        job = dict(row)
        # Defaults
        if not job.get('tier'): job['tier'] = 3
        if not job.get('status'): job['status'] = 'to_apply'
        if not job.get('match_score'): job['match_score'] = 0
        # Sanitize None to empty string
        for k, v in job.items():
            if v is None: job[k] = ''
        jobs.append(job)
    conn.close()

    # Stats
    total = len(jobs)
    t1 = len([j for j in jobs if j['tier']==1])
    t2 = len([j for j in jobs if j['tier']==2])
    t3 = len([j for j in jobs if j['tier']==3])

    jobs_json = json.dumps(jobs)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Strategic Match PRO</title>
<style>
:root {{ --bg: #f8fafc; --card-bg: #ffffff; --primary: #6366f1; --text: #1e293b; }}
body {{ font-family: 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 20px; }}
.container {{ max-width: 1800px; margin: 0 auto; }}

/* Header */
.header {{ background: white; padding: 20px; border-radius: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; }}
.title h1 {{ margin: 0; font-size: 24px; color: var(--primary); }}
.stats {{ display: flex; gap: 15px; font-weight: 500; color: #64748b; }}
.badge {{ padding: 4px 12px; border-radius: 99px; font-size: 13px; font-weight: 700; }}
.t1 {{ background: #fef3c7; color: #b45309; border: 1px solid #fcd34d; }}
.t2 {{ background: #e2e8f0; color: #475569; border: 1px solid #cbd5e1; }}
.t3 {{ background: #ffedd5; color: #c2410c; border: 1px solid #fdba74; }}

/* Kanban */
.kanban {{ display: grid; grid-template-columns: repeat(5, minmax(280px, 1fr)); gap: 16px; margin-bottom: 40px; overflow-x: auto; padding-bottom: 20px; }}
.column {{ background: #f1f5f9; border-radius: 12px; padding: 16px; min-width: 280px; }}
.col-header {{ font-weight: 700; margin-bottom: 16px; display: flex; justify-content: space-between; color: #475569; text-transform: uppercase; font-size: 12px; letter-spacing: 0.5px; }}
.col-count {{ background: #cbd5e1; padding: 2px 8px; border-radius: 12px; }}

/* Job Card */
.card {{ background: white; padding: 16px; border-radius: 10px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); cursor: grab; border-left: 4px solid transparent; transition: transform 0.2s; position: relative; }}
.card:hover {{ transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }}
.card.tier-1 {{ border-left-color: #f59e0b; }}
.card.tier-2 {{ border-left-color: #94a3b8; }}
.card.tier-3 {{ border-left-color: #fdba74; }}

.card-header {{ display: flex; justify-content: space-between; margin-bottom: 8px; }}
.match {{ font-weight: 800; color: #10b981; font-size: 14px; }}
.role {{ font-weight: 700; font-size: 15px; margin-bottom: 4px; line-height: 1.4; }}
.company {{ color: #64748b; font-size: 13px; margin-bottom: 12px; font-weight: 500; }}

/* Quick Links */
.quick-links {{ display: flex; gap: 6px; flex-wrap: wrap; margin-top: 12px; pt: 12px; border-top: 1px solid #f1f5f9; }}
.q-link {{ font-size: 11px; text-decoration: none; padding: 4px 8px; border-radius: 6px; font-weight: 600; transition: all 0.2s; cursor: pointer; }}
.ql-prep {{ background: #e0e7ff; color: #4338ca; }}
.ql-talk {{ background: #dcfce7; color: #15803d; }}
.ql-flag {{ background: #fee2e2; color: #b91c1c; }}
.ql-view {{ background: #f3f4f6; color: #4b5563; margin-left: auto; }}

/* Table */
.table-section {{ background: white; border-radius: 16px; padding: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}
table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
th {{ text-align: left; padding: 12px; border-bottom: 2px solid #e2e8f0; color: #64748b; }}
td {{ padding: 12px; border-bottom: 1px solid #e2e8f0; }}
tr:hover {{ background: #f8fafc; }}

/* Modal */
.modal {{ display: none; position: fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); align-items:center; justify-content:center; z-index:999; }}
.modal-content {{ background:white; width:800px; max-height:90vh; overflow-y:auto; padding:30px; border-radius:16px; }}
.m-section {{ margin-bottom: 20px; padding: 15px; background: #f8fafc; border-radius: 8px; }}
</style>
</head>
<body>

<div class="container">
    <div class="header">
        <div class="title"><h1>🚀 Strategic Match PRO</h1></div>
        <div class="stats">
            <span class="badge t1">Tier 1: {t1}</span>
            <span class="badge t2">Tier 2: {t2}</span>
            <span class="badge t3">Tier 3: {t3}</span>
            <span>Total: {total}</span>
        </div>
    </div>

    <!-- KANBAN -->
    <h3 style="color:#64748b; margin-bottom:15px">Pipeline</h3>
    <div class="kanban" id="kanban"></div>

    <!-- TABLE -->
    <div class="table-section">
        <div style="display:flex; justify-content:space-between; margin-bottom:20px;">
            <h3 style="margin:0">📋 Full Job List</h3>
            <input type="text" id="search" placeholder="Search jobs..." style="padding:8px 12px; border:1px solid #ccc; border-radius:8px; width:300px;" onkeyup="renderTable()">
        </div>
        <table id="table"><thead><tr><th>Tier</th><th>Role</th><th>Company</th><th>Match</th><th>Status</th><th>Actions</th></tr></thead><tbody id="tbody"></tbody></table>
    </div>
</div>

<!-- MODAL -->
<div class="modal" id="modal" onclick="if(event.target===this)closeModal()"><div class="modal-content" id="modal-body"></div></div>

<script>
const jobs = {jobs_json};
const cols = ['to_apply', 'applied', 'interview', 'offer', 'rejected'];
const labels = {{'to_apply':'To Apply', 'applied':'Applied', 'interview':'Interview', 'offer':'Offer', 'rejected':'Rejected'}};

function init() {{
    renderKanban();
    renderTable();
}}

function renderKanban() {{
    const board = document.getElementById('kanban');
    board.innerHTML = cols.map(c => {{
        const colJobs = jobs.filter(j => j.status === c);
        return `
        <div class="column" ondrop="drop(event, '${{c}}')" ondragover="allowDrop(event)">
            <div class="col-header">${{labels[c]}} <span class="col-count">${{colJobs.length}}</span></div>
            <div class="cards">
                ${{colJobs.map(j => cardHTML(j)).join('')}}
            </div>
        </div>`;
    }}).join('');
}}

function cardHTML(j) {{
    const hasPrep = j.interview_prep && j.interview_prep.length > 5;
    const hasTalk = j.talking_points && j.talking_points.length > 5;
    const hasFlags = j.red_flags && j.red_flags.length > 5;

    return `
    <div class="card tier-${{j.tier}}" draggable="true" ondragstart="drag(event, ${{j.id}})">
        <div class="card-header">
            <span class="match">${{j.match_score}}%</span>
            ${{j.tier===1 ? '🏆' : ''}}
        </div>
        <div class="role">${{j.title}}</div>
        <div class="company">${{j.company}}</div>
        <div class="quick-links">
            ${{hasPrep ? `<span class="q-link ql-prep" onclick="openModal(${{j.id}}, 'prep')">Prep</span>` : ''}}
            ${{hasTalk ? `<span class="q-link ql-talk" onclick="openModal(${{j.id}}, 'talk')">Talk</span>` : ''}}
            ${{hasFlags ? `<span class="q-link ql-flag" onclick="openModal(${{j.id}}, 'flags')">Flags</span>` : ''}}
            <span class="q-link ql-view" onclick="openModal(${{j.id}})">View →</span>
        </div>
    </div>`;
}}

function renderTable() {{
    const term = document.getElementById('search').value.toLowerCase();
    const tbody = document.getElementById('tbody');
    tbody.innerHTML = jobs.filter(j => 
        j.title.toLowerCase().includes(term) || j.company.toLowerCase().includes(term)
    ).map(j => `
        <tr>
            <td><span class="badge t${{j.tier}}">T${{j.tier}}</span></td>
            <td><b>${{j.title}}</b></td>
            <td>${{j.company}}</td>
            <td><b style="color:#10b981">${{j.match_score}}%</b></td>
            <td>${{labels[j.status]}}</td>
            <td><button onclick="openModal(${{j.id}})" style="cursor:pointer; padding:4px 8px;">Details</button></td>
        </tr>
    `).join('');
}}

function allowDrop(ev) {{ ev.preventDefault(); }}
function drag(ev, id) {{ ev.dataTransfer.setData("text", id); }}
function drop(ev, status) {{
    ev.preventDefault();
    const id = ev.dataTransfer.getData("text");
    const job = jobs.find(j => j.id == id);
    job.status = status;
    renderKanban();
    renderTable();
}}

function openModal(id, section=null) {{
    const j = jobs.find(j => j.id == id);
    document.getElementById('modal-body').innerHTML = `
        <h2>${{j.title}}</h2>
        <h3 style="color:#6366f1">${{j.company}}</h3>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin:20px 0; background:#f8fafc; padding:15px; border-radius:8px;">
            <div>📍 ${{j.location}}</div>
            <div>💰 ${{j.salary_range}}</div>
            <div>🔗 <a href="${{j.url}}" target="_blank">Original Listing</a></div>
        </div>
        ${{j.company_overview ? `<div class="m-section"><h4>🏢 Overview</h4><p>${{j.company_overview}}</p></div>` : ''}}
        ${{j.interview_prep ? `<div id="sec-prep" class="m-section" style="${{section==='prep'?'border:2px solid blue':''}}"><h4>⚡ Interview Prep</h4><p>${{j.interview_prep}}</p></div>` : ''}}
        ${{j.talking_points ? `<div id="sec-talk" class="m-section" style="${{section==='talk'?'border:2px solid green':''}}"><h4>🗣️ Talking Points</h4><p>${{j.talking_points}}</p></div>` : ''}}
        ${{j.red_flags ? `<div id="sec-flags" class="m-section" style="${{section==='flags'?'border:2px solid red':''}}"><h4>🚩 Red Flags</h4><p>${{j.red_flags}}</p></div>` : ''}}
        ${{j.full_description ? `<div class="m-section"><h4>📄 Full Description</h4><p>${{j.full_description}}</p></div>` : ''}}
    `;
    document.getElementById('modal').style.display = 'flex';
    if(section) document.getElementById('sec-'+section).scrollIntoView({{behavior:'smooth'}});
}}
function closeModal() {{ document.getElementById('modal').style.display = 'none'; }}

init();
</script>
</body>
</html>"""

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("✅ PRO Dashboard Created Successfully!")

if __name__ == "__main__":
    build_dashboard()
