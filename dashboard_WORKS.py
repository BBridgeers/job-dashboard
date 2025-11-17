import sqlite3
from datetime import datetime

def build_dashboard():
    jobs_conn = sqlite3.connect('jobs.db')
    jobs_cursor = jobs_conn.cursor()

    # Get actual column names first
    jobs_cursor.execute("PRAGMA table_info(jobs)")
    columns = [col[1] for col in jobs_cursor.fetchall()]
    print(f"Available columns: {columns}")

    # Build SELECT query based on available columns
    base_cols = "id, title, company, location, url, match_score"
    optional_cols = []

    if 'date_posted' in columns:
        optional_cols.append('date_posted')
    else:
        optional_cols.append("'N/A' as date_posted")

    if 'job_type' in columns:
        optional_cols.append('job_type')
    else:
        optional_cols.append("'Full-time' as job_type")

    query = f"SELECT {base_cols}, {', '.join(optional_cols)} FROM jobs WHERE url IS NOT NULL AND url != '' ORDER BY match_score DESC"

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
        .job-details {{ display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 15px; }}
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
        }}
        .btn:hover {{ background: #0ea5e9; }}
    </style>
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
        job_id, title, company, location, url, match, date, job_type = job
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
                <span class="match-score">{match}% Match</span>
                {status_html}
            </div>
            <a href="{url}" class="btn" target="_blank">View Job →</a>
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
    print(f"📍 Open: dashboard.html")

if __name__ == "__main__":
    build_dashboard()
