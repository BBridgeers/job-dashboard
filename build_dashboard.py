#!/usr/bin/env python3
import sqlite3
from datetime import datetime

def build_dashboard():
    print("🚀 Building Mobile-Optimized Dashboard...")
    print("=" * 60)

    conn = sqlite3.connect('jobs.db')
    cursor = conn.cursor()

    # Query matching YOUR actual database schema
    cursor.execute("""
        SELECT id, job_type, title, company, location, salary,
               url, match_score, brief, first_seen
        FROM jobs 
        ORDER BY match_score DESC
    """)

    jobs = cursor.fetchall()
    print(f"📊 Loaded {len(jobs)} jobs from database")

    high_match = sum(1 for j in jobs if j[7] >= 90)
    corporate = sum(1 for j in jobs if j[1] == 'corporate')
    nonprofit = sum(1 for j in jobs if j[1] == 'nonprofit')

    # Build HTML
    html_parts = []
    html_parts.append("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📋 Job Search Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; color: #333; }
        .container { max-width: 1200px; margin: 0 auto; }
        header { background: white; padding: 20px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h1 { color: #667eea; margin-bottom: 10px; font-size: 24px; }
        .stats { display: flex; gap: 15px; flex-wrap: wrap; margin-top: 15px; }
        .stat { background: #f0f4ff; padding: 10px 15px; border-radius: 8px; font-size: 14px; }
        .tabs { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
        .tab { background: white; border: none; padding: 12px 24px; border-radius: 10px; cursor: pointer; font-size: 16px; font-weight: 500; transition: all 0.3s; }
        .tab.active { background: #667eea; color: white; }
        .job-card { background: white; padding: 20px; border-radius: 12px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); transition: transform 0.2s; }
        .job-card:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.15); }
        .job-header { display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px; gap: 10px; }
        .job-title { font-size: 18px; font-weight: 600; color: #333; flex: 1; }
        .match-badge { background: #10b981; color: white; padding: 4px 12px; border-radius: 20px; font-size: 14px; font-weight: 600; white-space: nowrap; }
        .job-company { color: #667eea; font-weight: 500; margin-bottom: 5px; }
        .job-location { color: #666; font-size: 14px; margin-bottom: 5px; }
        .job-salary { color: #059669; font-size: 14px; font-weight: 600; margin-bottom: 10px; }
        .job-brief { color: #555; line-height: 1.6; margin: 10px 0; font-size: 14px; }
        .job-button { background: #667eea; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 500; transition: background 0.3s; margin-top: 10px; }
        .job-button:hover { background: #5568d3; }
        .type-badge { display: inline-block; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 500; margin-right: 8px; }
        .corporate { background: #dbeafe; color: #1e40af; }
        .nonprofit { background: #d1fae5; color: #065f46; }
        footer { text-align: center; color: white; padding: 20px; font-size: 14px; }
        @media (max-width: 768px) { .job-header { flex-direction: column; } .match-badge { align-self: flex-start; } }
    </style>
    <script>
        function openJob(url, title, company) {
            if (!url || url === '**' || url === '' || url === 'None' || url === 'null') {
                const query = encodeURIComponent(title + ' ' + company + ' Dallas TX job');
                window.open('https://www.google.com/search?q=' + query, '_blank');
            } else {
                window.open(url, '_blank');
            }
        }
        function filterJobs(tab) {
            const allJobs = document.querySelectorAll('.job-card');
            const tabs = document.querySelectorAll('.tab');
            tabs.forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            allJobs.forEach(job => {
                if (tab === 'all') {
                    job.style.display = 'block';
                } else {
                    const jobType = job.dataset.type;
                    job.style.display = jobType === tab ? 'block' : 'none';
                }
            });
        }
    </script>
</head>
<body>
    <div class="container">
        <header>
            <h1>📋 Job Search Dashboard</h1>
            <p>Your personalized job matches in DFW</p>
            <div class="stats">""")

    html_parts.append(f'<div class="stat">📊 Total Jobs: <strong>{len(jobs)}</strong></div>')
    html_parts.append(f'<div class="stat">🔥 High Match (90+): <strong>{high_match}</strong></div>')
    html_parts.append(f'<div class="stat">🏢 Corporate: <strong>{corporate}</strong></div>')
    html_parts.append(f'<div class="stat">💚 Nonprofit: <strong>{nonprofit}</strong></div>')

    html_parts.append("""
            </div>
        </header>
        <div class="tabs">
            <button class="tab active" onclick="filterJobs('all')">All Jobs</button>
            <button class="tab" onclick="filterJobs('corporate')">🏢 Corporate</button>
            <button class="tab" onclick="filterJobs('nonprofit')">💚 Nonprofit</button>
        </div>
        <div class="jobs-container">""")

    for job in jobs:
        job_id, job_type, title, company, location, salary, url, match, brief, first_seen = job
        safe_title = (title or '').replace("'", "\\'").replace('"', '\\"')
        safe_company = (company or '').replace("'", "\\'").replace('"', '\\"')
        safe_url = url if url else ''
        brief_preview = (brief or 'No description available')[:200] + '...' if brief and len(brief) > 200 else (brief or 'No description available')
        salary_display = f'💰 {salary}' if salary and salary.strip() else ''

        html_parts.append(f"""
            <div class="job-card" data-type="{job_type}">
                <div class="job-header">
                    <div class="job-title">{title}</div>
                    <div class="match-badge">{match}% Match</div>
                </div>
                <div class="job-company">{company}</div>
                <div class="job-location">📍 {location}</div>
                {f'<div class="job-salary">{salary_display}</div>' if salary_display else ''}
                <span class="type-badge {job_type}">{job_type.title()}</span>
                <div class="job-brief">{brief_preview}</div>
                <button class="job-button" onclick="openJob('{safe_url}', '{safe_title}', '{safe_company}')">
                    View Job Details →
                </button>
            </div>""")

    timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p %Z")
    html_parts.append(f"""
        </div>
        <footer>
            <p>Last updated: {timestamp}</p>
            <p>Job Search Automation System v2.0</p>
        </footer>
    </div>
</body>
</html>""")

    html = ''.join(html_parts)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ Dashboard created: index.html")
    print(f"   📊 {len(jobs)} jobs displayed")
    print(f"   🔥 {high_match} high-match opportunities")
    print(f"   🏢 {corporate} corporate | 💚 {nonprofit} nonprofit")
    print()
    print("🌐 Open index.html in your browser to view the dashboard!")

    try:
        from google_drive_uploader import upload_file
        print("\n📤 Uploading to Google Drive...")
        upload_file('index.html', 'Dashboard')
        print("✅ Successfully uploaded to Google Drive!")
    except Exception as e:
        print(f"⚠️  Google Drive upload failed: {e}")

    conn.close()

if __name__ == "__main__":
    build_dashboard()
