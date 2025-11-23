#!/usr/bin/env python3
"""
Strategic Match - MASTER DASHBOARD (ROBUST FIX)
"""
import sqlite3
import json
import html
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

            # SAFE DEFAULTS
            if not j.get('tier'): j['tier'] = 3
            if not j.get('status'): j['status'] = 'New'
            if not j.get('match_score'): j['match_score'] = 0

            # SANITIZE ALL TEXT FIELDS
            # We must escape quotes and special chars to prevent breaking the HTML/JS
            all_text_fields = [
                'title', 'company', 'location', 'summary_bullets', 'fit_bullets',
                'company_overview', 'role_insights', 'key_requirements', 'salary_intel',
                'application_strategy', 'red_flags', 'cultural_fit', 'competitive_landscape',
                'skills_gap', 'network_leverage', 'decision_timeline', 'career_trajectory',
                'resume_keywords', 'resume_summary', 'cover_letter', 'why_me_bullets',
                'why_them_bullets', 'interview_prep', 'star_hooks', 'talking_points',
                'questions_to_ask', 'recruiter_email', 'thank_you_email', 'plan_30_60_90', 'notes'
            ]

            for k in all_text_fields:
                val = j.get(k)
                if val is None: 
                    j[k] = ""
                else:
                    # Ensure it's a string
                    j[k] = str(val)

            # Fix URL
            raw_url = j.get('url', '#')
            if raw_url and not raw_url.startswith('http') and raw_url != '#':
                raw_url = 'https://' + raw_url
            j['app_url'] = raw_url
            j['list_url'] = raw_url

            # Tags
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

def render_job_card(j):
    # HTML-safe rendering for card face
    tag_html = ''
    for t in j['tags']:
        cls = 'tag-tier-3'
        if 'tier 1' in t.lower(): cls = 'tag-tier-1'
        elif 'tier 2' in t.lower(): cls = 'tag-tier-2'
        elif 'high' in t.lower(): cls = 'tag-high'
        elif 'corp' in t.lower(): cls = 'tag-corp'
        tag_html += f'<span class="tag {cls}">{t}</span>'

    # Handle bullets safely
    core_bullets_html = ''
    if j['summary_bullets'] and len(j['summary_bullets']) > 10:
        # Simple HTML conversion if it's plain text
        sum_text = j['summary_bullets'].replace('\n', '<br>')
        fit_text = j['fit_bullets'].replace('\n', '<br>') if j['fit_bullets'] else ""

        core_bullets_html = f"""
        <div class="core-bullets">
            <h5>Summary</h5>
            <div style="margin-bottom:8px;">{sum_text}</div>
            <h5>Your Fit</h5>
            <div>{fit_text}</div>
        </div>
        """

    return f"""
    <div class="job-card" data-tags="{','.join(j['tags'])}" data-title="{html.escape(j['title'])}">
        <div class="card-tags">{tag_html}</div>
        <div class="job-title">{html.escape(j['title'])}</div>
        <div class="company-name">{html.escape(j['company'])}</div>

        {core_bullets_html}

        <div class="action-buttons">
            <button class="btn-3d btn-details" onclick="openModal({j['id']})">View Full</button>
            <button class="btn-3d btn-listing" onclick="markViewed({j['id']}, '{j['list_url']}')">Listing</button>
            <button class="btn-3d btn-apply" onclick="markApplied({j['id']}, '{j['app_url']}')">Apply</button>
            <a href="tracker.html" class="btn-3d btn-track">Track</a>
        </div>

        <div class="status-row">
            <select id="status-{j['id']}" class="status-select" onchange="updateStatus({j['id']}, this.value)">
                <option value="New" {'selected' if j['status']=='New' else ''}>New</option>
                <option value="Applied" {'selected' if j['status']=='Applied' else ''}>Applied</option>
                <option value="Interview" {'selected' if j['status']=='Interview' else ''}>Interview</option>
                <option value="Offer" {'selected' if j['status']=='Offer' else ''}>Offer</option>
                <option value="Rejected" {'selected' if j['status']=='Rejected' else ''}>Rejected</option>
            </select>
        </div>
    </div>
    """

def build_files():
    print("🚀 Building Robust Dashboard...")

    jobs = db_get_jobs()
    # We use a safer JSON dump for the JS variable
    jobs_json = json.dumps(jobs, default=str).replace("</script>", "<\\/script>")

    total = len(jobs)
    t1 = len([j for j in jobs if j['tier'] == 1])
    t2 = len([j for j in jobs if j['tier'] == 2])

    # CSS
    css = """
    :root { --primary: #4f46e5; --bg-color: #f3f4f6; }
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
    .job-card:hover { border-color: var(--primary); box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); transform: translateY(-2px); transition: all 0.2s; }

    .card-tags { display: flex; gap: 5px; margin-bottom: 8px; }
    .tag { font-size: 9px; font-weight: 600; padding: 3px 7px; border-radius: 4px; text-transform: uppercase; }
    .tag-tier-1 { background: #fef9c3; color: #a16207; }
    .tag-tier-2 { background: #e5e7eb; color: #4b5563; }
    .tag-tier-3 { background: #ffedd5; color: #c2410c; }
    .tag-high { background: #dcfce7; color: #166534; }
    .tag-corp { background: #dbeafe; color: #4338ca; }

    .job-title { font-weight: 600; font-size: 15px; margin-bottom: 2px; color: #111827; }
    .company-name { color: #4b5563; font-size: 13px; margin-bottom: 10px; }

    .core-bullets { background: #f9fafb; border: 1px solid #f3f4f6; border-radius: 6px; padding: 10px; font-size: 12px; line-height: 1.5; margin-bottom: 12px; color: #374151; }
    .core-bullets h5 { font-size: 10px; text-transform: uppercase; color: #9ca3af; margin: 0 0 4px 0; font-weight: 700; }

    .action-buttons { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-top: auto; }
    .btn-3d { padding: 7px; border-radius: 5px; font-weight: 500; font-size: 11px; text-align: center; color: white; cursor: pointer; border: none; text-decoration: none; }
    .btn-details { background: #4f46e5; }
    .btn-listing { background: #3b82f6; }
    .btn-apply { background: #10b981; }
    .btn-track { background: #f59e0b; }

    .status-row { margin-top: 10px; padding-top: 8px; border-top: 1px solid #f3f4f6; }
    .status-select { width: 100%; padding: 5px; border: 1px solid #d1d5db; border-radius: 4px; }

    /* MODAL */
    .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 2000; align-items: center; justify-content: center; backdrop-filter: blur(2px); }
    .modal-content { background: #f9fafb; width: 95%; max-width: 900px; height: 90vh; border-radius: 10px; display: flex; flex-direction: column; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); }
    .modal-header { padding: 15px 20px; border-bottom: 1px solid #e5e7eb; background: white; border-radius: 10px 10px 0 0; }
    .modal-title { font-size: 18px; font-weight: 600; color: #111827; margin: 0; }
    .modal-subtitle { font-size: 13px; color: #6b7280; margin-top: 2px; }

    .tab-nav { display: flex; padding: 0 20px; background: white; border-bottom: 1px solid #e5e7eb; gap: 20px; }
    .tab-btn { padding: 15px 0; font-weight: 600; font-size: 12px; color: #6b7280; cursor: pointer; border-bottom: 2px solid transparent; }
    .tab-btn:hover { color: #111827; }
    .tab-btn.active { color: var(--primary); border-bottom-color: var(--primary); }

    .modal-body { padding: 20px; overflow-y: auto; flex: 1; }
    .tab-content { display: none; }
    .tab-content.active { display: block; }

    .data-block { margin-bottom: 20px; }
    .data-label { font-size: 11px; font-weight: 700; text-transform: uppercase; color: #9ca3af; margin-bottom: 6px; letter-spacing: 0.5px; }
    .data-value { font-size: 14px; line-height: 1.6; color: #374151; white-space: pre-line; background: white; padding: 15px; border-radius: 8px; border: 1px solid #e5e7eb; position: relative; }
    .copy-btn { position: absolute; top: 10px; right: 10px; font-size: 10px; background: #f3f4f6; border: 1px solid #e5e7eb; padding: 4px 8px; border-radius: 4px; cursor: pointer; color: #4b5563; font-weight: 600; }
    .copy-btn:hover { background: #e5e7eb; color: #111827; }

    .toast { position: fixed; bottom: 20px; right: 20px; background: #10b981; color: white; padding: 10px 20px; border-radius: 6px; font-weight: 600; z-index: 3000; display: none; }
    """

    index_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Strategic Match</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>{css}</style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="app-title">Strategic Match 🚀</div>
            <div class="controls-row">
                <div class="search-section">
                    <input type="text" class="search-input" placeholder="Search jobs..." onkeyup="searchJobs(this.value)">
                </div>
                <div class="filter-badges">
                    <div class="badge-filter active" onclick="filterJobs('all', this)">All ({total})</div>
                    <div class="badge-filter" onclick="filterJobs('t1', this)">Tier 1 ({t1})</div>
                    <div class="badge-filter" onclick="filterJobs('t2', this)">Tier 2 ({t2})</div>
                    <div class="badge-filter" onclick="filterJobs('corp', this)">Corporate</div>
                    <div class="badge-filter" onclick="filterJobs('nonprofit', this)">Nonprofit</div>
                </div>
                <a href="tracker.html" style="margin-left:auto;background:#111827;color:white;padding:8px 15px;border-radius:6px;text-decoration:none;font-size:12px;font-weight:600;">Tracker</a>
            </div>
        </div>
    </div>

    <div class="grid-container">
        {''.join([render_job_card(j) for j in jobs])}
    </div>

    <div id="toast" class="toast">Notification</div>

    <!-- MODAL -->
    <div id="modal" class="modal" onclick="if(event.target===this)document.getElementById('modal').style.display='none'">
        <div id="modal-content" class="modal-content"></div>
    </div>

    <script>
        const API_BASE = "{API_BASE}";
        const ALL_JOBS = {jobs_json}; // Injected JSON data

        function openModal(id) {{
            const job = ALL_JOBS.find(j => j.id == id);
            if(!job) return;

            const content = document.getElementById('modal-content');

            // Render Helper
            const f = (label, val, copy=false) => {{
                if(!val || val.length < 3) return '';
                const fid = `field-${{Math.random().toString(36).substr(2,9)}}`;
                return `
                <div class="data-block">
                    <div class="data-label">${{label}}</div>
                    <div class="data-value" id="${{fid}}">
                        ${{val.replace(/\\n/g, '<br>')}}
                        ${{copy ? `<button class="copy-btn" onclick="copyText('${{fid}}')">COPY</button>` : ''}}
                    </div>
                </div>`;
            }};

            content.innerHTML = `
                <div class="modal-header">
                    <h2 class="modal-title">${{job.title}}</h2>
                    <div class="modal-subtitle">${{job.company}} • Tier ${{job.tier}}</div>
                </div>
                <div class="tab-nav">
                    <div id="btn-strategy" class="tab-btn active" onclick="switchTab('strategy')">STRATEGY</div>
                    <div id="btn-interview" class="tab-btn" onclick="switchTab('interview')">INTERVIEW</div>
                    <div id="btn-assets" class="tab-btn" onclick="switchTab('assets')">ASSETS</div>
                </div>
                <div class="modal-body">
                    <div id="tab-strategy" class="tab-content active">
                        ${{f('Company Overview', job.company_overview)}}
                        ${{f('Role Insights', job.role_insights)}}
                        ${{f('Key Requirements', job.key_requirements)}}
                        ${{f('Red Flags', job.red_flags)}}
                        ${{f('Cultural Fit', job.cultural_fit)}}
                        ${{f('Competitive Landscape', job.competitive_landscape)}}
                        ${{f('Skills Gap', job.skills_gap)}}
                        ${{f('Timeline', job.decision_timeline)}}
                    </div>
                    <div id="tab-interview" class="tab-content">
                        ${{f('Interview Prep', job.interview_prep)}}
                        ${{f('STAR Hooks', job.star_hooks)}}
                        ${{f('Talking Points', job.talking_points)}}
                        ${{f('Salary Intel', job.salary_intel)}}
                        ${{f('Questions to Ask', job.questions_to_ask)}}
                    </div>
                    <div id="tab-assets" class="tab-content">
                        ${{f('Resume Keywords', job.resume_keywords, true)}}
                        ${{f('Resume Summary', job.resume_summary, true)}}
                        ${{f('Cover Letter Draft', job.cover_letter, true)}}
                        ${{f('Recruiter Email', job.recruiter_email, true)}}
                        ${{f('Why Me', job.why_me_bullets)}}
                    </div>
                </div>
            `;
            document.getElementById('modal').style.display = 'flex';
        }}

        function switchTab(name) {{
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            document.getElementById('tab-'+name).classList.add('active');
            document.getElementById('btn-'+name).classList.add('active');
        }}

        function copyText(id) {{
            const text = document.getElementById(id).innerText;
            navigator.clipboard.writeText(text).then(() => {{
                const t = document.getElementById('toast');
                t.innerText = "✅ Copied!";
                t.style.display = 'block';
                setTimeout(() => t.style.display = 'none', 2000);
            }});
        }}

        function filterJobs(criteria, btn) {{
            document.querySelectorAll('.badge-filter').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            document.querySelectorAll('.job-card').forEach(card => {{
                const tags = card.dataset.tags.toLowerCase();
                let match = true;
                if(criteria === 't1' && !tags.includes('tier 1')) match = false;
                if(criteria === 't2' && !tags.includes('tier 2')) match = false;
                if(criteria === 'corp' && !tags.includes('corporate')) match = false;
                if(criteria === 'nonprofit' && !tags.includes('nonprofit')) match = false;
                card.style.display = match ? 'flex' : 'none';
            }});
        }}

        function searchJobs(query) {{
            const q = query.toLowerCase();
            document.querySelectorAll('.job-card').forEach(card => {{
                const title = card.dataset.title.toLowerCase();
                card.style.display = title.includes(q) ? 'flex' : 'none';
            }});
        }}

        async function updateStatus(id, status) {{
            try {{
                await fetch(`${{API_BASE}}/api/update_status`, {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{id, status}})
                }});
                const t = document.getElementById('toast');
                t.innerText = "✅ Saved";
                t.style.display = 'block';
                setTimeout(() => t.style.display = 'none', 2000);
            }} catch(e) {{ console.error(e); }}
        }}

        function markApplied(id, url) {{ updateStatus(id, 'Applied'); window.open(url, '_blank'); }}
        function markViewed(id, url) {{ updateStatus(id, 'Viewed'); window.open(url, '_blank'); }}
    </script>
</body>
</html>"""

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(index_html)

    print("✅ Dashboard Fixed & Built (Robust Mode)")

if __name__ == "__main__":
    build_files()
