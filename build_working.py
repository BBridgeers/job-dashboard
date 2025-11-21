#!/usr/bin/env python3
import sqlite3
import json

conn = sqlite3.connect('jobs.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT * FROM jobs ORDER BY tier ASC, match_score DESC")
rows = cursor.fetchall()

jobs = []
for row in rows:
    job = dict(row)
    if not job.get('tier'):
        job['tier'] = 3
    for key in job:
        if job[key] is None:
            job[key] = ''
    jobs.append(job)

conn.close()

tier1 = len([j for j in jobs if j.get('tier') == 1])
tier2 = len([j for j in jobs if j.get('tier') == 2])
tier3 = len([j for j in jobs if j.get('tier') == 3])

print(f"Building dashboard with {len(jobs)} jobs")
print(f"Tier 1: {tier1} | Tier 2: {tier2} | Tier 3: {tier3}")

jobs_json = json.dumps(jobs)

html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Strategic Match</title>
<style>
body{{font-family:sans-serif;background:linear-gradient(135deg,#667eea,#764ba2);padding:20px;min-height:100vh}}
.container{{max-width:1400px;margin:0 auto}}
.header{{background:white;border-radius:15px;padding:30px;margin-bottom:20px;box-shadow:0 10px 30px rgba(0,0,0,0.1)}}
.header h1{{color:#667eea;font-size:32px}}
.stats{{margin-top:15px;color:#666}}
.jobs-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(350px,1fr));gap:20px}}
.job-card{{background:white;border-radius:12px;padding:25px;box-shadow:0 5px 20px rgba(0,0,0,0.1);transition:transform 0.3s}}
.job-card:hover{{transform:translateY(-5px)}}
.tier-1{{border-left:5px solid #FFD700}}
.tier-2{{border-left:5px solid #C0C0C0}}
.tier-3{{border-left:5px solid #CD7F32}}
.job-title{{font-size:18px;font-weight:700;color:#333;margin-bottom:8px}}
.job-company{{color:#667eea;margin-bottom:12px}}
.job-meta{{color:#666;font-size:14px;margin-bottom:15px}}
.btn{{display:inline-block;padding:10px 20px;background:#667eea;color:white;text-decoration:none;border-radius:8px;margin-top:10px}}
.btn:hover{{background:#5568d3}}
.tier-badge{{display:inline-block;padding:4px 10px;border-radius:10px;font-size:11px;font-weight:700;margin-bottom:10px}}
.tier-1-badge{{background:#FFD700;color:#856404}}
.tier-2-badge{{background:#C0C0C0;color:#495057}}
.tier-3-badge{{background:#CD7F32;color:white}}
</style></head><body>
<div class="container">
<div class="header">
<h1>🎯 Strategic Match</h1>
<div class="stats">
<strong>Total Jobs: {len(jobs)}</strong> | 
🏆 Tier 1: {tier1} | 
🥈 Tier 2: {tier2} | 
🥉 Tier 3: {tier3}
</div>
</div>
<div class="jobs-grid" id="grid"></div>
</div>
<script>
const jobs={jobs_json};
document.getElementById('grid').innerHTML=jobs.map(j=>`
<div class="job-card tier-${{j.tier||3}}">
<span class="tier-badge tier-${{j.tier||3}}-badge">TIER ${{j.tier||3}}</span>
<h3 class="job-title">${{j.title||'Untitled Position'}}</h3>
<div class="job-company">${{j.company||'Unknown Company'}}</div>
<div class="job-meta">
${{j.location?'📍 '+j.location:''}} 
${{j.salary_range?'💰 '+j.salary_range:''}}
${{j.match_score?'⭐ Match: '+j.match_score+'%':''}}
</div>
${{j.why_this_role?'<p style="color:#666;font-size:14px;line-height:1.6">'+j.why_this_role.substring(0,150)+'...</p>':''}}
${{j.url?'<a href="'+j.url+'" target="_blank" class="btn">View Job →</a>':''}}
</div>
`).join('');
console.log('Loaded',jobs.length,'jobs');
</script></body></html>"""

with open('index.html', 'w') as f:
    f.write(html)

print("✅ Dashboard created: index.html")
