#!/usr/bin/env python3

"""
Strategic Match - Complete Dashboard Builder
Generates full HTML dashboard with embedded job data
"""

import sqlite3
import json
from datetime import datetime

def build_dashboard():
    """Build complete dashboard from database"""
    print("🎯 Building Strategic Match Dashboard")
    print("=" * 60)

    # Connect to database
    conn = sqlite3.connect('jobs.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Fetch all jobs
    cursor.execute("""
        SELECT
            id, title, company, job_type, salary_range, location, match_score,
            company_overview, why_this_role, interview_prep, talking_points,
            red_flags, url, status, date_added, tier, search_type,
            key_requirements, full_description
        FROM jobs
        ORDER BY tier ASC, match_score DESC, date_added DESC
    """)

    rows = cursor.fetchall()

    # Convert to list of dicts
    jobs = []
    for row in rows:
        job = dict(row)
        # Ensure tier exists
        if not job.get('tier') or job['tier'] is None:
            job['tier'] = 3
        # Ensure all text fields are strings
        for key in job:
            if job[key] is None:
                job[key] = ''
        jobs.append(job)

    conn.close()

    print(f"📊 Loaded {len(jobs)} jobs from database")

    # Count by tier
    tier1 = len([j for j in jobs if j.get('tier') == 1])
    tier2 = len([j for j in jobs if j.get('tier') == 2])
    tier3 = len([j for j in jobs if j.get('tier') == 3 or not j.get('tier')])

    print(f"   Tier 1: {tier1} | Tier 2: {tier2} | Tier 3: {tier3}")

    # Generate complete HTML
    jobs_json = json.dumps(jobs, ensure_ascii=False, indent=2)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Strategic Match - Job Search Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .header {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}

        .header h1 {{
            font-size: 32px;
            color: #667eea;
            display: flex;
            align-items: center;
            gap: 15px;
        }}

        .header h1::before {{
            content: "🎯";
            font-size: 40px;
        }}

        .filters {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin-top: 20px;
        }}

        .filter-btn {{
            padding: 12px 24px;
            border: none;
            border-radius: 25px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            background: #f0f0f0;
            color: #333;
        }}

        .filter-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}

        .filter-btn.active {{
            background: #667eea;
            color: white;
        }}

        .search-box {{
            margin-top: 20px;
            position: relative;
        }}

        .search-box input {{
            width: 100%;
            padding: 15px 50px 15px 20px;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            font-size: 16px;
            transition: border 0.3s;
        }}

        .search-box input:focus {{
            outline: none;
            border-color: #667eea;
        }}

        .search-box::after {{
            content: "🔍";
            position: absolute;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 20px;
        }}

        .jobs-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}

        .job-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            transition: all 0.3s;
            cursor: pointer;
        }}

        .job-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }}

        .job-card.tier-1 {{
            border-left: 5px solid #FFD700;
        }}

        .job-card.tier-2 {{
            border-left: 5px solid #C0C0C0;
        }}

        .job-card.tier-3 {{
            border-left: 5px solid #CD7F32;
        }}

        .job-title {{
            font-size: 18px;
            font-weight: 700;
            color: #333;
            margin-bottom: 8px;
        }}

        .job-company {{
            font-size: 14px;
            color: #667eea;
            margin-bottom: 15px;
        }}

        .job-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 15px;
        }}

        .meta-tag {{
            padding: 5px 12px;
            background: #f0f0f0;
            border-radius: 12px;
            font-size: 12px;
            color: #666;
        }}

        .job-description {{
            font-size: 14px;
            color: #666;
            line-height: 1.6;
            margin-bottom: 15px;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}

        .job-actions {{
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }}

        .btn {{
            padding: 8px 16px;
            border: none;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }}

        .btn-primary {{
            background: #667eea;
            color: white;
        }}

        .btn-primary:hover {{
            background: #5568d3;
        }}

        .btn-secondary {{
            background: #f0f0f0;
            color: #333;
        }}

        .btn-secondary:hover {{
            background: #e0e0e0;
        }}

        .tier-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
        }}

        .tier-1-badge {{
            background: #FFD700;
            color: #856404;
        }}

        .tier-2-badge {{
            background: #C0C0C0;
            color: #495057;
        }}

        .tier-3-badge {{
            background: #CD7F32;
            color: #fff;
        }}

        .match-score {{
            font-size: 24px;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 10px;
        }}

        .no-jobs {{
            text-align: center;
            padding: 60px 20px;
            background: white;
            border-radius: 15px;
            color: #999;
        }}

        .no-jobs::before {{
            content: "📭";
            font-size: 60px;
            display: block;
            margin-bottom: 20px;
        }}

        @media (max-width: 768px) {{
            .jobs-grid {{
                grid-template-columns: 1fr;
            }}

            .filters {{
                flex-direction: column;
            }}

            .filter-btn {{
                width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Strategic Match</h1>

            <div class="filters">
                <button class="filter-btn active" onclick="filterJobs('all')">
                    📊 Total Jobs ( {len(jobs)} )
                </button>
                <button class="filter-btn" onclick="filterJobs('high-match')">
                    ⭐ High Match 90+ ( {len([j for j in jobs if j.get('match_score') and int(j['match_score']) >= 90])} )
                </button>
                <button class="filter-btn" onclick="filterJobs('corporate')">
                    💼 Corporate ( {len([j for j in jobs if j.get('search_type') == 'corporate'])} )
                </button>
                <button class="filter-btn" onclick="filterJobs('nonprofit')">
                    💚 Nonprofit ( {len([j for j in jobs if j.get('search_type') == 'nonprofit'])} )
                </button>
                <button class="filter-btn" onclick="filterJobs('tier-1')">
                    🏆 Tier 1 ( {tier1} )
                </button>
                <button class="filter-btn" onclick="filterJobs('tier-2')">
                    🥈 Tier 2 ( {tier2} )
                </button>
                <button class="filter-btn" onclick="filterJobs('tier-3')">
                    🥉 Tier 3 ( {tier3} )
                </button>
            </div>

            <div class="search-box">
                <input type="text" id="searchInput" placeholder="Search jobs..." onkeyup="searchJobs()">
            </div>
        </div>

        <div class="jobs-grid" id="jobsGrid"></div>
    </div>

    <script>
        const jobsData = {jobs_json};

        let currentFilter = 'all';
        let currentSearch = '';

        function renderJobs() {{
            const grid = document.getElementById('jobsGrid');

            let filtered = jobsData.filter(job => {{
                // Filter logic
                let matchFilter = true;

                if (currentFilter === 'high-match') {{
                    matchFilter = job.match_score && parseInt(job.match_score) >= 90;
                }} else if (currentFilter === 'corporate') {{
                    matchFilter = job.search_type === 'corporate';
                }} else if (currentFilter === 'nonprofit') {{
                    matchFilter = job.search_type === 'nonprofit';
                }} else if (currentFilter === 'tier-1') {{
                    matchFilter = job.tier === 1;
                }} else if (currentFilter === 'tier-2') {{
                    matchFilter = job.tier === 2;
                }} else if (currentFilter === 'tier-3') {{
                    matchFilter = job.tier === 3 || !job.tier;
                }}

                // Search logic
                let matchSearch = true;
                if (currentSearch) {{
                    const searchLower = currentSearch.toLowerCase();
                    matchSearch = 
                        (job.title && job.title.toLowerCase().includes(searchLower)) ||
                        (job.company && job.company.toLowerCase().includes(searchLower)) ||
                        (job.location && job.location.toLowerCase().includes(searchLower));
                }}

                return matchFilter && matchSearch;
            }});

            if (filtered.length === 0) {{
                grid.innerHTML = '<div class="no-jobs"><h3>No jobs match your filters</h3><p>Try adjusting your search criteria</p></div>';
                return;
            }}

            grid.innerHTML = filtered.map(job => `
                <div class="job-card tier-${{job.tier || 3}}">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
                        <div>
                            <span class="tier-${{job.tier || 3}}-badge tier-badge">Tier ${{job.tier || 3}}</span>
                        </div>
                        ${{job.match_score ? `<div class="match-score">${{job.match_score}}%</div>` : ''}}
                    </div>

                    <h3 class="job-title">${{job.title || 'Untitled Position'}}</h3>
                    <div class="job-company">${{job.company || 'Unknown Company'}}</div>

                    <div class="job-meta">
                        ${{job.location ? `<span class="meta-tag">📍 ${{job.location}}</span>` : ''}}
                        ${{job.salary_range ? `<span class="meta-tag">💰 ${{job.salary_range}}</span>` : ''}}
                        ${{job.search_type ? `<span class="meta-tag">${{job.search_type === 'corporate' ? '💼' : '💚'}} ${{job.search_type}}</span>` : ''}}
                    </div>

                    ${{job.why_this_role || job.company_overview ? `
                        <div class="job-description">
                            ${{job.why_this_role || job.company_overview || ''}}
                        </div>
                    ` : ''}}

                    <div class="job-actions">
                        ${{job.url ? `<a href="${{job.url}}" target="_blank" class="btn btn-primary">View Job</a>` : ''}}
                        <button class="btn btn-secondary" onclick="alert('Job ID: ${{job.id}}')">Details</button>
                    </div>
                </div>
            `).join('');
        }}

        function filterJobs(filter) {{
            currentFilter = filter;

            // Update active button
            document.querySelectorAll('.filter-btn').forEach(btn => {{
                btn.classList.remove('active');
            }});
            event.target.classList.add('active');

            renderJobs();
        }}

        function searchJobs() {{
            currentSearch = document.getElementById('searchInput').value;
            renderJobs();
        }}

        // Initial render
        renderJobs();

        console.log(`✅ Dashboard loaded with ${{jobsData.length}} jobs`);
        console.log(`   Tier 1: ${{jobsData.filter(j => j.tier === 1).length}}`);
        console.log(`   Tier 2: ${{jobsData.filter(j => j.tier === 2).length}}`);
        console.log(`   Tier 3: ${{jobsData.filter(j => j.tier === 3 || !j.tier).length}}`);
    </script>
</body>
</html>"""

    # Save dashboard
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print("\n✅ Dashboard built successfully!")
    print(f"   File: index.html")
    print(f"   Total jobs: {len(jobs)}")
    print("=" * 60)

if __name__ == "__main__":
    build_dashboard()
