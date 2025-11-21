#!/usr/bin/env python3
"""
Strategic Match - ULTIMATE PRO DASHBOARD
Features: Stacked Kanban + Table, Quick-Jump Links, Full Data
Plus: Tier Filters (Richest/Semi/Basic)
"""
import sqlite3
import json

def build_dashboard():
    print("🎯 Building PRO Dashboard with Tier Filters...")

    conn = sqlite3.connect('jobs.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get columns
    cursor.execute("PRAGMA table_info(jobs)")
    cols = [c[1] for c in cursor.fetchall()]

    # Select all
    cursor.execute("SELECT * FROM jobs ORDER BY tier ASC, match_score DESC")
    jobs = []
    for row in cursor.fetchall():
        j = dict(row)
        if not j.get('tier'): j['tier'] = 3
        if not j.get('status'): j['status'] = 'to_apply'
        for k,v in j.items():
            if v is None: j[k] = ''
        jobs.append(j)
    conn.close()

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
:root {{ --bg: #f8fafc; --primary: #6366f1; --text: #1e293b; }}
body {{ font-family: 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 20px; }}
.container {{ max-width: 1800px; margin: 0 auto; }}

/* Header & Filters */
.header {{ background: white; padding: 20px; border-radius: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 24px; }}
.top-row {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
.title h1 {{ margin: 0; font-size: 24px; color: var(--primary); }}

.filter-bar {{ display: flex; gap: 10px; flex-wrap: wrap; padding-top: 15px; border-top: 1px solid #e2e8f0; }}
.filter-btn {{ padding: 8px 16px; border: 1px solid #e2e8f0; background: white; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 13px; transition: all 0.2s; display: flex; align-items: center; gap: 6px; }}
.filter-btn:hover {{ background: #f8fafc; }}
.filter-btn.active {{ background: #eef2ff; border-color: var(--primary); color: var(--primary); }}

/* Tier Badges for Buttons */
.tb-dot {{ width: 8px; height: 8px; border-radius: 50%; display: inline-block; }}
.dot-1 {{ background: #f59e0b; }}
.dot-2 {{ background: #94a3b8; }}
.dot-3 {{ background: #d97706; }}

/* Kanban */
.kanban {{ display: grid; grid-template-columns: repeat(5, minmax(280px, 1fr)); gap: 16px; margin-bottom: 40px; overflow-x: auto; padding-bottom: 20px; }}
.column {{ background: #eef2ff; border-radius: 12px; padding: 16px; min-width: 280px; border: 1px solid #e0e7ff; }}
.col-header {{ font-weight: 700; margin-bottom: 16px; display: flex; justify-content: space-between; color: #4338ca; text-transform: uppercase; font-size: 12px; }}
.col-count {{ background: #c7d2fe; padding: 2px 8px; border-radius: 12px; color: #312e81; }}

/* Cards */
.card {{ background: white; padding: 16px; border-radius: 10px; margin-bottom: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); cursor: grab; border-left: 4px solid transparent; }}
.card:hover {{ transform: translateY(-2px); box-shadow: 0 8px 16px -4px rgba(0,0,0,0.1); }}
.card.tier-1 {{ border-left-color: #f59e0b; }}
.card.tier-2 {{ border-left-color: #94a3b8; }}
.card.tier-3 {{ border-left-color: #d97706; }}

.card-header {{ display: flex; justify-content: space-between; margin-bottom: 8px; }}
.match {{ font-weight: 800; color: #059669; font-size: 13px; background: #d1fae5; padding: 2px 6px; border-radius: 4px; }}
.role {{ font-weight: 700; font-size: 15px; margin-bottom: 4px; }}
.company {{ color: #64748b; font-size: 13px; margin-bottom: 12px; }}

/* Quick Links */
.quick-links {{ display: flex; gap: 6px; flex-wrap: wrap; margin-top: 12px; pt: 12px; border-top: 1px solid #f1f5f9; }}
.q-link {{ font-size: 11px; padding: 4px 8px; border-radius: 6px; font-weight: 600; cursor: pointer; }}
.ql-prep {{ background: #e0e7ff; color: #4338ca; }}
.ql-talk {{ background: #dcfce7; color: #166534; }}
.ql-flag {{ background: #fee2e2; color: #991b1b; }}
.ql-view {{ background: #f3f4f6; color: #4b5563; margin-left: auto; }}

/* Modal */
.modal {{ display: none; position: fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); align-items:center; justify-content:center; z-index:999; }}
.modal-content {{ background:white; width:800px; max-height:90vh; overflow-y:auto; padding:30px; border-radius:16px; }}
</style>
</head>
<body>

<div class="container">
    <div class="header">
        <div class="top-row">
            <div class="title"><h1>🚀 Strategic Match PRO</h1></div>
            <div style="color:#64748b; font-weight:600">Total Jobs: {total}</div>
        </div>

        <div class="filter-bar">
            <button class="filter-btn active" onclick="filterTier('all', this)">All Jobs</button>
            <button class="filter-btn" onclick="filterTier(1, this)">
                <span class="tb-dot dot-1"></span> Tier 1: Richest ({t1})
            </button>
            <button class="filter-btn" onclick="filterTier(2, this)">
                <span class="tb-dot dot-2"></span> Tier 2: Semi ({t2})
            </button>
            <button class="filter-btn" onclick="filterTier(3, this)">
                <span class="tb-dot dot-3"></span> Tier 3: Basic ({t3})
            </button>
        </div>
    </div>

    <div class="kanban" id="kanban"></div>
</div>

<!-- MODAL -->
<div class="modal" id="modal" onclick="if(event.target===this)closeModal()"><div class="modal-content" id="modal-body"></div></div>

<script>
const jobs = {jobs_json};
const cols = ['to_apply', 'applied', 'interview', 'offer', 'rejected'];
const labels = {{'to_apply':'To Apply', 'applied':'Applied', 'interview':'Interview', 'offer':'Offer', 'rejected':'Rejected'}};
let currentTier = 'all';

function init() {{ renderKanban(); }}

function filterTier(tier, btn) {{
    currentTier = tier;
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    renderKanban();
}}

function renderKanban() {{
    const board = document.getElementById('kanban');
    const filtered = currentTier === 'all' ? jobs : jobs.filter(j => j.tier == currentTier);

    board.innerHTML = cols.map(c => {{
        const colJobs = filtered.filter(j => j.status === c);
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
            <span style="font-size:10px; font-weight:700; color:#9ca3af">TIER ${{j.tier}}</span>
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

function allowDrop(ev) {{ ev.preventDefault(); }}
function drag(ev, id) {{ ev.dataTransfer.setData("text", id); }}
function drop(ev, status) {{
    ev.preventDefault();
    const id = ev.dataTransfer.getData("text");
    const job = jobs.find(j => j.id == id);
    if(job) {{
        job.status = status;
        renderKanban();
    }}
}}

function openModal(id, section=null) {{
    const j = jobs.find(j => j.id == id);
    document.getElementById('modal-body').innerHTML = `
        <h2>${{j.title}}</h2>
        <h3 style="color:#6366f1">${{j.company}}</h3>
        <div style="margin:20px 0; background:#f8fafc; padding:15px; border-radius:8px;">
            <div>📍 ${{j.location}} | 💰 ${{j.salary_range}}</div>
            <div style="margin-top:8px">🔗 <a href="${{j.url}}" target="_blank">Link</a></div>
        </div>
        ${{j.company_overview ? `<h4>🏢 Overview</h4><p>${{j.company_overview}}</p>` : ''}}
        ${{j.interview_prep ? `<div id="sec-prep"><h4>⚡ Interview Prep</h4><p>${{j.interview_prep}}</p></div>` : ''}}
        ${{j.talking_points ? `<div id="sec-talk"><h4>🗣️ Talking Points</h4><p>${{j.talking_points}}</p></div>` : ''}}
        ${{j.red_flags ? `<div id="sec-flags"><h4>🚩 Red Flags</h4><p>${{j.red_flags}}</p></div>` : ''}}
        ${{j.full_description ? `<div id="sec-desc"><h4>📄 Full Description</h4><p>${{j.full_description}}</p></div>` : ''}}
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
    print("✅ PRO Dashboard Built")

if __name__ == "__main__":
    build_dashboard()
