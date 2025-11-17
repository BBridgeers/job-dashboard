#!/usr/bin/env python3
"""
Job Dashboard Builder with Smart URL Fallback
Builds a mobile-optimized HTML dashboard from jobs.db
- Falls back to Google search if URL is invalid or empty
- Opens links in new tabs
- Mobile-responsive design
"""
import sqlite3
from datetime import datetime

def build_dashboard():
    """Build the HTML dashboard from database"""

    print("🚀 Building Mobile-Optimized Dashboard...")
    print("=" * 60)

    # Connect to database
    conn = sqlite3.connect('jobs.db')
    cursor = conn.cursor()

    # Get all jobs ordered by match score
    cursor.execute("""
        SELECT id, title, company, location, match_score, 
               description, requirements, job_type, url, added_date
        FROM jobs 
        ORDER BY match_score DESC
    """)

    jobs = cursor.fetchall()
    print(f"📊 Loaded {len(jobs)} jobs from database")

    # Count stats
    high_match = sum(1 for j in jobs if j[4] >= 90)
    corporate = sum(1 for j in jobs if j[7] == 'corporate')
    nonprofit = sum(1 for j in jobs if j[7] == 'nonprofit')

    # Build HTML parts
    html_parts = []

    # HTML Header with Smart URL JavaScript
    html_parts.append("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📋 Job Search Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 15px; 
            color: #333;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        header { 
            background: white; 
            padding: 20px; 
            border-radius: 15px; 
            margin-bottom: 20px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
        }
        h1 { color: #667eea; margin-bottom: 10px; font-size: 24px; }
        .stats { display: flex; gap: 15px; flex-wrap: wrap; margin-top: 15px; }
        .stat { 
            background: #f0f4ff; 
            padding: 10px 15px; 
            border-radius: 8px; 
            font-size: 14px; 
        }
        .tabs { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
        .tab { 
            background: white; 
            border: none; 
            padding: 12px 24px; 
            border-radius: 10px; 
            cursor: pointer; 
            font-size: 16px; 
            font-weight: 500; 
            transition: all 0.3s; 
        }
        .tab.active { background: #667eea; color: white; }
        .job-card { 
            background: white; 
            padding: 20px; 
            border-radius: 12px; 
            margin-bottom: 15px; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
            transition: transform 0.2s; 
        }
        .job-card:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 4px 8px rgba(0,0,0,0.15); 
        }
        .job-header { 
            display: flex; 
            justify-content: space-between; 
            align-items: start; 
            margin-bottom: 10px; 
            gap: 10px; 
        }
        .job-title { 
            font-size: 18px; 
            font-weight: 600; 
            color: #333; 
            flex: 1; 
        }
        .match-badge { 
            background: #10b981; 
            color: white; 
            padding: 4px 12px; 
            border-radius: 20px; 
            font-size: 14px; 
            font-weight: 600; 
            white-space: nowrap; 
        }
        .job-company { color: #667eea; font-weight: 500; margin-bottom: 5px; }
        .job-location { color: #666; font-size: 14px; margin-bottom: 10px; }
        .job-description { color: #555; line-height: 1.6; margin: 10px 0; font-size: 14px; }
        .job-button { 
            background: #667eea; 
            color: white; 
            border: none; 
            padding: 10px 20px; 
            border-radius: 8px; 
            cursor: pointer; 
            font-size: 14px; 
            font-weight: 500; 
            transition: background 0.3s; 
            margin-top: 10px; 
        }
        .job-button:hover { background: #5568d3; }
        .type-badge { 
            display: inline-block; 
            padding: 4px 10px; 
            border-radius: 6px; 
            font-size: 12px; 
            font-weight: 500; 
            margin-right: 8px; 
        }
        .corporate { background: #dbeafe; color: #1e40af; }
        .nonprofit { background: #d1fae5; color: #065f46; }
        footer { text-align: center; color: white; padding: 20px; font-size: 14px; }
        @media (max-width: 768px) { 
            .job-header { flex-direction: column; } 
            .match-badge { align-self: flex-start; } 
        }
    </style>
    <script>
        // Smart URL handler - falls back to Google search if URL is invalid
        function openJob(url, title, company) {
            // Check if URL is valid
            if (!url || url === '**' || url === '' || url === 'None' || url === 'null') {
                // Fallback to Google search
                const query = encodeURIComponent(title + ' ' + company + ' Dallas TX job');
                window.open('https://www.google.com/search?q=' + query, '_blank');
            } else {
                // Try the actual URL
                window.open(url, '_blank');
            }
        }

        // Tab filtering
        function filterJobs(tab) {
            const allJobs = document.querySelectorAll('.job-card');
            const tabs = document.querySelectorAll('.tab');

            // Update active tab
            tabs.forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');

            // Filter jobs
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

    # Add stats
    html_parts.append(f'<div class="stat">📊 Total Jobs: <strong>{len(jobs)}</strong></div>')
    html_parts.append(f'<div class="stat">🔥 High Match (90+): <strong>{high_match}</strong></div>')
    html_parts.append(f'<div class="stat">🏢 Corporate: <strong>{corporate}</strong></div>')
    html_parts.append(f'<div class="stat">💚 Nonprofit: <strong>{nonprofit}</strong></div>')

    # Tabs section
    html_parts.append("""
            </div>
        </header>

        <div class="tabs">
            <button class="tab active" onclick="filterJobs('all')">All Jobs</button>
            <button class="tab" onclick="filterJobs('corporate')">🏢 Corporate</button>
            <button class="tab" onclick="filterJobs('nonprofit')">💚 Nonprofit</button>
        </div>

        <div class="jobs-container">""")

    # Add each job
    for job in jobs:
        job_id, title, company, location, match, desc, reqs, job_type, url, added = job

        # Escape quotes for JavaScript
        safe_title = title.replace("'", "\\'").replace('"', '\\"')
        safe_company = company.replace("'", "\\'").replace('"', '\\"')
        safe_url = url if url else ''

        # Truncate description
        desc_preview = desc[:200] + '...' if len(desc) > 200 else desc

        job_html = f"""
            <div class="job-card" data-type="{job_type}">
                <div class="job-header">
                    <div class="job-title">{title}</div>
                    <div class="match-badge">{match}% Match</div>
                </div>
                <div class="job-company">{company}</div>
                <div class="job-location">📍 {location}</div>
                <span class="type-badge {job_type}">{job_type.title()}</span>
                <div class="job-description">{desc_preview}</div>
                <button class="job-button" onclick="openJob('{safe_url}', '{safe_title}', '{safe_company}')">
                    View Job Details →
                </button>
            </div>"""

        html_parts.append(job_html)

    # Close HTML
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

    # Combine all parts
    html = ''.join(html_parts)

    # Write to file
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ Dashboard created: index.html")
    print(f"   📊 {len(jobs)} jobs displayed")
    print(f"   🔥 {high_match} high-match opportunities")
    print(f"   🏢 {corporate} corporate | 💚 {nonprofit} nonprofit")
    print()
    print("🌐 Open index.html in your browser to view the dashboard!")

    # Try to upload to Google Drive (optional)
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
