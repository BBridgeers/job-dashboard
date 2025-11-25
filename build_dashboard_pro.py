import sqlite3
import os
import json
from datetime import datetime

# CONFIGURATION
DB_PATH = 'jobs.db'
HTML_OUTPUT = 'index.html'

def db_get_jobs():
    """Fetch jobs with application status and strategy kits."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Join jobs with applications AND strategy_kits
    c.execute("""
        SELECT j.*, a.status as app_status, a.applied_date, a.id as app_id, s.data as strategy_data
        FROM jobs j
        LEFT JOIN applications a ON j.id = a.job_id
        LEFT JOIN strategy_kits s ON j.id = s.job_id
        ORDER BY j.match_score DESC
    """)
    jobs = [dict(row) for row in c.fetchall()]
    conn.close()
    
    # Normalize data
    for j in jobs:
        # Use application status if exists, else job status, else 'New'
        final_status = j.get('app_status') or j.get('status') or 'New'
        j['display_status'] = final_status
        
        # Parse Strategy Data if exists
        if j.get('strategy_data'):
            try:
                j['strategy'] = json.loads(j['strategy_data'])
                j['has_strategy'] = True
            except:
                j['has_strategy'] = False
        else:
            j['has_strategy'] = False
        
        # Tags
        tags = []
        if j['match_score'] >= 90: tags.append("High Match")
        if j['tier'] == 1: tags.append("Tier 1")
        if j.get('salary_min') and j['salary_min'] > 100000: tags.append("High Pay")
        if j['has_strategy']: tags.append("🧠 Strategy Ready")
        j['tags'] = tags
        
    return jobs

def generate_kanban_html(jobs):
    """Generate the HTML Dashboard with Kanban Board and Strategy Modal."""
    
    # Group by Status
    columns = {
        "New": [],
        "Applied": [],
        "Interview": [],
        "Offer": [],
        "Rejected": []
    }
    
    for j in jobs:
        status = j['display_status']
        if status not in columns: status = "New"
        columns[status].append(j)

    # Serialize jobs for JS
    jobs_json = json.dumps(jobs, default=str)

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Job Search Command Center</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Inter', sans-serif; background-color: #f3f4f6; }}
            .kanban-col {{ min-height: 80vh; }}
            .card {{ transition: transform 0.2s; }}
            .card:hover {{ transform: translateY(-2px); }}
            .tier-1 {{ border-left: 4px solid #10b981; }}
            .tier-2 {{ border-left: 4px solid #f59e0b; }}
            .tier-3 {{ border-left: 4px solid #6b7280; }}
            .modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 50; }}
            .modal-content {{ background: white; margin: 5% auto; padding: 20px; width: 80%; max-width: 900px; max-height: 90vh; overflow-y: auto; border-radius: 8px; }}
        </style>
    </head>
    <body class="p-6">
        <header class="mb-8 flex justify-between items-center">
            <div>
                <h1 class="text-3xl font-bold text-gray-900">🚀 Job Search Command Center</h1>
                <p class="text-gray-600">Tracking {len(jobs)} Opportunities</p>
            </div>
            <div class="space-x-4">
                <a href="#" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">Refresh Data</a>
            </div>
        </header>

        <!-- KANBAN BOARD -->
        <div class="grid grid-cols-1 md:grid-cols-5 gap-4 overflow-x-auto">
            {render_column("New", columns['New'])}
            {render_column("Applied", columns['Applied'], "bg-blue-50", "text-blue-800", "bg-blue-200")}
            {render_column("Interview", columns['Interview'], "bg-purple-50", "text-purple-800", "bg-purple-200")}
            {render_column("Offer", columns['Offer'], "bg-green-50", "text-green-800", "bg-green-200")}
            {render_column("Rejected", columns['Rejected'], "bg-red-50", "text-red-800", "bg-red-200")}
        </div>

        <!-- STRATEGY MODAL -->
        <div id="strategyModal" class="modal">
            <div class="modal-content">
                <div class="flex justify-between items-center mb-4">
                    <h2 id="modalTitle" class="text-2xl font-bold">Strategy Kit</h2>
                    <button onclick="closeModal()" class="text-gray-500 hover:text-gray-700 text-xl">&times;</button>
                </div>
                <div id="modalBody" class="space-y-6"></div>
            </div>
        </div>

        <script>
            const jobs = {jobs_json};

            function openStrategy(jobId) {{
                const job = jobs.find(j => j.id == jobId);
                if (!job || !job.strategy) return;
                
                const s = job.strategy;
                const title = document.getElementById('modalTitle');
                const body = document.getElementById('modalBody');
                
                title.innerText = `Strategy Kit: ${{job.title}}`;
                
                let html = `
                    <div class="grid grid-cols-2 gap-4">
                        <div class="bg-blue-50 p-4 rounded">
                            <h3 class="font-bold text-blue-800 mb-2">🎯 Precision Match</h3>
                            <div class="text-3xl font-bold text-blue-600">${{s.precision_match.total_score}}/100</div>
                            <p class="text-sm mt-1">${{s.precision_match.reasoning}}</p>
                        </div>
                        <div class="bg-yellow-50 p-4 rounded">
                            <h3 class="font-bold text-yellow-800 mb-2">⚠️ Gap Analysis</h3>
                            <ul class="list-disc pl-4 text-sm">
                                ${{s.gap_analysis.hard_gaps.map(g => `<li>${{g}}</li>`).join('')}}
                            </ul>
                        </div>
                    </div>

                    <div class="border-t pt-4">
                        <h3 class="font-bold text-lg mb-2">📄 Resume Customization</h3>
                        <div class="space-y-2">
                            ${{s.resume_customization.swap_instructions.map(i => `
                                <div class="bg-gray-50 p-3 rounded text-sm">
                                    <div class="text-red-500 line-through text-xs">${{i.original}}</div>
                                    <div class="text-green-600 font-medium">→ ${{i.new}}</div>
                                    <div class="text-gray-400 text-xs italic">${{i.reason}}</div>
                                </div>
                            `).join('')}}
                        </div>
                    </div>

                    <div class="border-t pt-4">
                        <h3 class="font-bold text-lg mb-2">💌 Cover Letter Hook</h3>
                        <div class="bg-gray-50 p-4 rounded italic text-gray-700">
                            "${{s.cover_letter.opening_paragraph}}"
                        </div>
                        <p class="text-xs text-gray-500 mt-2">News Hook: ${{s.cover_letter.news_hook}}</p>
                    </div>
                `;
                
                body.innerHTML = html;
                document.getElementById('strategyModal').style.display = 'block';
            }}

            function closeModal() {{
                document.getElementById('strategyModal').style.display = 'none';
            }}
            
            window.onclick = function(event) {{
                if (event.target == document.getElementById('strategyModal')) {{
                    closeModal();
                }}
            }}
        </script>
    </body>
    </html>
    """
    return html

def render_column(title, jobs, bg_color="bg-gray-100", text_color="text-gray-700", count_bg="bg-gray-200"):
    return f"""
    <div class="{bg_color} p-4 rounded-lg kanban-col">
        <h2 class="font-bold {text_color} mb-4 flex justify-between">
            {title} <span class="{count_bg} px-2 rounded text-sm">{len(jobs)}</span>
        </h2>
        <div class="space-y-3">
            {render_cards(jobs)}
        </div>
    </div>
    """

def render_cards(job_list):
    html = ""
    for job in job_list:
        tier_class = f"tier-{job['tier']}"
        score_color = "text-green-600" if job['match_score'] >= 90 else "text-yellow-600"
        
        # Strategy Button
        strategy_btn = ""
        if job.get('has_strategy'):
            strategy_btn = f'<button onclick="openStrategy({job["id"]})" class="w-full mt-2 bg-purple-600 text-white text-xs py-1 rounded hover:bg-purple-700">🧠 View Strategy Kit</button>'
        
        html += f"""
        <div class="bg-white p-4 rounded shadow card {tier_class} cursor-pointer">
            <div class="flex justify-between items-start mb-2">
                <h3 class="font-bold text-gray-900 leading-tight">{job['title']}</h3>
                <span class="font-bold {score_color}">{job['match_score']}</span>
            </div>
            <p class="text-sm text-gray-600 mb-2">{job['company']}</p>
            
            <div class="flex flex-wrap gap-1 mb-3">
                {''.join([f'<span class="text-xs bg-gray-100 px-2 py-1 rounded">{t}</span>' for t in job['tags']])}
            </div>
            
            <div class="flex justify-between items-center text-xs text-gray-500">
                <span>{job.get('location', '')}</span>
            </div>
            
            {strategy_btn}
            
            <div class="mt-3 pt-3 border-t border-gray-100 flex justify-between">
                <a href="{job.get('url', '#')}" target="_blank" class="text-blue-600 text-xs hover:underline">View Job</a>
                <button class="text-gray-400 hover:text-gray-600 text-xs">Details</button>
            </div>
        </div>
        """
    return html

if __name__ == "__main__":
    print("📊 Generating Kanban Dashboard...")
    jobs = db_get_jobs()
    html = generate_kanban_html(jobs)
    with open(HTML_OUTPUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Dashboard saved to {HTML_OUTPUT}")
