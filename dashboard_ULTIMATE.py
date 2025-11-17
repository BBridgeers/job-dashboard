import sqlite3
from datetime import datetime

def build_dashboard():
    jobs_conn = sqlite3.connect('jobs.db')
    jobs_cursor = jobs_conn.cursor()

    # Check what columns exist
    jobs_cursor.execute("PRAGMA table_info(jobs)")
    columns = [col[1] for col in jobs_cursor.fetchall()]

    # Build query dynamically
    select_cols = ["id", "title", "company", "location", "url", "match_score"]

    for col in ['date_posted', 'job_type', 'description', 'requirements', 'salary_range']:
        if col in columns:
            select_cols.append(col)
        else:
            select_cols.append(f"'N/A' as {col}")

    query = f"SELECT {', '.join(select_cols)} FROM jobs WHERE url IS NOT NULL AND url != '' ORDER BY match_score DESC"
    jobs_cursor.execute(query)
    jobs = jobs_cursor.fetchall()

    try:
        apps_conn = sqlite3.connect('applications.db')
        apps_cursor = apps_conn.cursor()
        apps_cursor.execute("SELECT job_id, status FROM applications")
        apps_dict = {row[0]: row[1] for row in apps_cursor.fetchall()}
        apps_conn.close()
    except:
        apps_dict = {}

    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job Dashboard</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: #0f172a;
            color: #e2e8f0;
        }}
        h1 {{ color: #38bdf8; text-align: center; margin-bottom: 30px; }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: #1e293b;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border: 1px solid #334155;
        }}
        .stat-value {{ font-size: 2em; font-weight: bold; color: #38bdf8; }}
        .jobs-grid {{ display: grid; gap: 20px; }}
        .job-card {{
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 20px;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .job-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(56, 189, 248, 0.3);
        }}
        .job-title {{ color: #38bdf8; font-size: 1.3em; font-weight: bold; margin-bottom: 10px; }}
        .job-company {{ color: #94a3b8; font-size: 1.1em; margin-bottom: 15px; }}
        .job-details {{ 
            display: flex; 
            flex-wrap: wrap; 
            gap: 15px; 
            margin-bottom: 15px;
            align-items: center;
        }}
        .detail-item {{
            background: #0f172a;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.9em;
        }}
        .match-score {{
            display: inline-block;
            background: #22c55e;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
        }}
        .status-badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        .status-applied {{ background: #3b82f6; color: white; }}
        .status-interview {{ background: #22c55e; color: white; }}
        .status-offer {{ background: #eab308; color: white; }}
        .status-rejected {{ background: #ef4444; color: white; }}
        .btn {{
            display: inline-block;
            background: #38bdf8;
            color: #0f172a;
            padding: 10px 20px;
            border-radius: 5px;
            text-decoration: none;
            font-weight: bold;
            margin-top: 10px;
            margin-right: 10px;
            border: none;
            cursor: pointer;
        }}
        .btn:hover {{ background: #0ea5e9; }}
        .btn-secondary {{
            background: #475569;
            color: #e2e8f0;
        }}
        .btn-secondary:hover {{ background: #334155; }}
        .job-details-full {{
            display: none;
            margin-top: 15px;
            padding: 15px;
            background: #0f172a;
            border-radius: 5px;
            border-left: 3px solid #38bdf8;
            max-height: 400px;
            overflow-y: auto;
        }}
        .job-details-full.show {{ display: block; }}
        .section-title {{
            color: #38bdf8;
            font-weight: bold;
            margin-top: 10px;
            margin-bottom: 5px;
            font-size: 1.1em;
        }}
        .detail-content {{
            color: #cbd5e1;
            line-height: 1.6;
            white-space: pre-wrap;
        }}
    </style>
    <script>
        function toggleDetails(id) {{
            const elem = document.getElementById('details-' + id);
            const btn = document.getElementById('btn-' + id);
            if (elem.classList.contains('show')) {{
                elem.classList.remove('show');
                btn.textContent = 'Show Full Details ▼';
            }} else {{
                elem.classList.add('show');
                btn.textContent = 'Hide Details ▲';
            }}
        }}
    </script>
</head>
<body>
    <h1>🚀 Job Search Dashboard</h1>

    <div class="stats">
        <div class="stat-card">
            <div class="stat-value">{len(jobs)}</div>
            <div>Total Jobs</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{len([j for j in jobs if j[5] >= 85])}</div>
            <div>High Priority (85%+)</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{len(apps_dict)}</div>
            <div>Applications Tracked</div>
        </div>
    </div>

    <div class="jobs-grid">
'''

    for job in jobs:
        job_id = job[0]
        title = job[1]
        company = job[2]
        location = job[3]
        url = job[4]
        match = job[5]
        date = job[6] if len(job) > 6 else "N/A"
        job_type = job[7] if len(job) > 7 else "Full-time"
        description = job[8] if len(job) > 8 and job[8] else "No description available"
        requirements = job[9] if len(job) > 9 and job[9] else "No requirements listed"
        salary = job[10] if len(job) > 10 and job[10] else "Not specified"

        status = apps_dict.get(job_id, None)
        status_html = ""
        if status:
            status_html = f'<span class="status-badge status-{status.lower()}">{status}</span>'

        html += f'''
        <div class="job-card">
            <div class="job-title">{title}</div>
            <div class="job-company">{company}</div>
            <div class="job-details">
                <div class="detail-item">📍 {location}</div>
                <div class="detail-item">💼 {job_type}</div>
                <div class="detail-item">📅 {date}</div>
                <div class="detail-item">💰 {salary}</div>
                <span class="match-score">{match}% Match</span>
                {status_html}
            </div>
            <a href="{url}" class="btn" target="_blank">View Job →</a>
            <button class="btn btn-secondary" id="btn-{job_id}" onclick="toggleDetails({job_id})">Show Full Details ▼</button>

            <div class="job-details-full" id="details-{job_id}">
                <div class="section-title">📋 Job Description</div>
                <div class="detail-content">{description}</div>

                <div class="section-title">✅ Requirements</div>
                <div class="detail-content">{requirements}</div>
            </div>
        </div>
'''

    html += '''
    </div>
</body>
</html>
'''

    with open('dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html)

    jobs_conn.close()
    print(f"✅ Dashboard built with {len(jobs)} jobs")
    print(f"📌 Full details available with expandable sections")
    print(f"📍 Open: dashboard.html")

if __name__ == "__main__":
    build_dashboard()
