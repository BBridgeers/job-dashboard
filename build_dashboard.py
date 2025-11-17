#!/usr/bin/env python3
"""
Dashboard Builder - Mobile Optimized + Google Drive Integration
Reads job search results from jobs.db SQLite database and generates mobile-friendly dashboard
"""

import sqlite3
import os
import json
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Google Drive setup
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_gdrive_service():
    """Authenticate and return Google Drive service"""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('gdrive_credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('drive', 'v3', credentials=creds)

def upload_to_gdrive(filename):
    """Upload dashboard to Google Drive"""
    try:
        service = get_gdrive_service()
        file_metadata = {'name': filename}
        media = MediaFileUpload(filename, mimetype='text/html')
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f"✅ Uploaded to Google Drive (ID: {file.get('id')})")
    except Exception as e:
        print(f"⚠️  Google Drive upload failed: {e}")

print("🚀 Building Mobile-Optimized Dashboard...")
print("=" * 60)

# Connect to database
db_path = 'jobs.db'
if not os.path.exists(db_path):
    print(f"❌ Database not found: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all jobs
cursor.execute('''
    SELECT id, job_type, title, company, location, salary, url, 
           match_score, brief, first_seen, status
    FROM jobs
    ORDER BY match_score DESC, first_seen DESC
''')

jobs = []
for row in cursor.fetchall():
    jobs.append({
        'id': row[0],
        'sector': row[1],  # job_type maps to sector
        'title': row[2],
        'company': row[3],
        'location': row[4],
        'salary': row[5],
        'link': row[6],  # url maps to link
        'match_score': row[7],
        'description': row[8],  # brief maps to description
        'date_posted': row[9],  # first_seen maps to date_posted
        'status': row[10],
        'skills': []  # Your schema doesn't have skills, so empty list
    })

conn.close()

print(f"📊 Loaded {len(jobs)} jobs from database")

if len(jobs) == 0:
    print("⚠️  No jobs found in database!")
    exit(0)

# Calculate stats
high_match_jobs = [j for j in jobs if j['match_score'] >= 80]
medium_match_jobs = [j for j in jobs if 60 <= j['match_score'] < 80]
corporate_jobs = [j for j in jobs if j['sector'] == 'corporate']
nonprofit_jobs = [j for j in jobs if j['sector'] == 'nonprofit']

# Generate HTML
html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Job Search Dashboard - {len(jobs)} Opportunities">
    <title>Job Dashboard - {len(jobs)} Opportunities</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 15px;
            color: #333;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        
        .header h1 {{
            font-size: 28px;
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            color: #666;
            font-size: 14px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .stat-card h2 {{
            font-size: 32px;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .stat-card p {{
            color: #666;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .filters {{
            background: white;
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        
        .filter-btn {{
            padding: 8px 16px;
            border: 2px solid #667eea;
            background: white;
            color: #667eea;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
        }}
        
        .filter-btn:hover, .filter-btn.active {{
            background: #667eea;
            color: white;
        }}
        
        .job-card {{
            background: white;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 12px;
            border-left: 5px solid #667eea;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .job-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }}
        
        .job-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 12px;
            flex-wrap: wrap;
            gap: 10px;
        }}
        
        .job-title {{
            font-size: 20px;
            font-weight: 700;
            color: #333;
            flex: 1;
            min-width: 200px;
        }}
        
        .match-badge {{
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 700;
            white-space: nowrap;
        }}
        
        .match-high {{
            background: linear-gradient(135deg, #10b981, #059669);
            color: white;
        }}
        
        .match-medium {{
            background: linear-gradient(135deg, #f59e0b, #d97706);
            color: white;
        }}
        
        .match-low {{
            background: linear-gradient(135deg, #6b7280, #4b5563);
            color: white;
        }}
        
        .job-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 12px;
            color: #666;
            font-size: 14px;
        }}
        
        .job-meta-item {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        
        .job-description {{
            color: #555;
            line-height: 1.6;
            margin-bottom: 15px;
            font-size: 14px;
        }}
        
        .job-skills {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 15px;
        }}
        
        .skill-tag {{
            background: #f3f4f6;
            color: #667eea;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: 600;
        }}
        
        .job-link {{
            display: inline-block;
            padding: 10px 20px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            transition: transform 0.2s;
        }}
        
        .job-link:hover {{
            transform: scale(1.05);
        }}
        
        .sector-badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        
        .sector-corporate {{
            background: #dbeafe;
            color: #1e40af;
        }}
        
        .sector-nonprofit {{
            background: #dcfce7;
            color: #166534;
        }}
        
        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}
            
            .header h1 {{
                font-size: 22px;
            }}
            
            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            
            .job-title {{
                font-size: 18px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Job Search Dashboard</h1>
            <p class="subtitle">Last Updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h2>{len(jobs)}</h2>
                <p>Total Jobs</p>
            </div>
            <div class="stat-card">
                <h2>{len(high_match_jobs)}</h2>
                <p>High Match</p>
            </div>
            <div class="stat-card">
                <h2>{len(corporate_jobs)}</h2>
                <p>Corporate</p>
            </div>
            <div class="stat-card">
                <h2>{len(nonprofit_jobs)}</h2>
                <p>Nonprofit</p>
            </div>
        </div>
        
        <div class="filters">
            <button class="filter-btn active" onclick="filterJobs('all')">All Jobs</button>
            <button class="filter-btn" onclick="filterJobs('high')">High Match (80%+)</button>
            <button class="filter-btn" onclick="filterJobs('corporate')">Corporate</button>
            <button class="filter-btn" onclick="filterJobs('nonprofit')">Nonprofit</button>
        </div>
        
        <div id="job-list">
'''

for job in jobs:
    # Determine match class
    if job['match_score'] >= 80:
        match_class = 'match-high'
    elif job['match_score'] >= 60:
        match_class = 'match-medium'
    else:
        match_class = 'match-low'
    
    # Sector badge
    sector_class = f"sector-{job['sector'].lower()}" if job['sector'] else "sector-corporate"
    
    # Parse skills
    skills_list = []
    if job['skills']:
        try:
            skills_list = json.loads(job['skills']) if isinstance(job['skills'], str) else job['skills']
        except:
            skills_list = []
    
    html += f'''
        <div class="job-card" data-match="{job['match_score']}" data-sector="{job['sector']}">
            <div class="job-header">
                <div class="job-title">{job['title']}</div>
                <span class="match-badge {match_class}">{job['match_score']}% Match</span>
            </div>
            
            <div class="job-meta">
                <div class="job-meta-item">
                    <span>🏢</span>
                    <strong>{job['company']}</strong>
                </div>
                <div class="job-meta-item">
                    <span>📍</span>
                    {job['location']}
                </div>
                <div class="job-meta-item">
                    <span>📅</span>
                    {job['date_posted']}
                </div>
                <span class="sector-badge {sector_class}">{job['sector']}</span>
            </div>
            
            <div class="job-description">
                {job['description'][:250]}{'...' if len(job['description']) > 250 else ''}
            </div>
            
            {'<div class="job-skills">' + ''.join([f'<span class="skill-tag">{skill}</span>' for skill in skills_list[:5]]) + '</div>' if skills_list else ''}
            
            <a href="{job['link']}" target="_blank" class="job-link">View Job Details →</a>
        </div>
    '''

html += '''
        </div>
    </div>
    
    <script>
        function filterJobs(filter) {
            const jobs = document.querySelectorAll('.job-card');
            const buttons = document.querySelectorAll('.filter-btn');
            
            buttons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            jobs.forEach(job => {
                const match = parseInt(job.dataset.match);
                const sector = job.dataset.sector;
                
                if (filter === 'all') {
                    job.style.display = 'block';
                } else if (filter === 'high' && match >= 80) {
                    job.style.display = 'block';
                } else if (filter === 'corporate' && sector === 'corporate') {
                    job.style.display = 'block';
                } else if (filter === 'nonprofit' && sector === 'nonprofit') {
                    job.style.display = 'block';
                } else {
                    job.style.display = 'none';
                }
            });
        }
    </script>
</body>
</html>
'''

# Save HTML
output_file = 'dashboard.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✅ Dashboard created: {output_file}")
print(f"   📊 {len(jobs)} jobs displayed")
print(f"   🔥 {len(high_match_jobs)} high-match opportunities")
print(f"   🏢 {len(corporate_jobs)} corporate | 💚 {len(nonprofit_jobs)} nonprofit")
print(f"\n🌐 Open {output_file} in your browser to view the dashboard!")

# Optional: Upload to Google Drive
try:
    if os.path.exists('gdrive_credentials.json'):
        upload_to_gdrive(output_file)
except Exception as e:
    print(f"⚠️  Google Drive upload skipped: {e}")
