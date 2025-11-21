#!/usr/bin/env python3
"""
Strategic Match - Professional Dashboard Builder
Generates Kanban tracker + searchable table dashboard
"""
import sqlite3
import json
from datetime import datetime

def build_dashboard():
    """Build professional dashboard with Kanban + table"""
    print("🎯 Building Strategic Match Professional Dashboard")
    print("=" * 60)

    # Connect to databases
    jobs_conn = sqlite3.connect('jobs.db')
    jobs_conn.row_factory = sqlite3.Row
    jobs_cursor = jobs_conn.cursor()

    # Fetch all jobs with full data
    jobs_cursor.execute("""
        SELECT 
            id, title, company, job_type, salary_range, location, match_score,
            company_overview, why_this_role, interview_prep, talking_points,
            red_flags, url, status, date_added, tier, search_type,
            key_requirements, full_description
        FROM jobs
        ORDER BY tier ASC, match_score DESC, date_added DESC
    """)

    jobs_data = []
    for row in jobs_cursor.fetchall():
        job = dict(row)
        # Ensure tier exists
        if not job.get('tier'):
            job['tier'] = 3
        # Ensure status exists
        if not job.get('status'):
            job['status'] = 'to_apply'
        # Convert None to empty string
        for key in job:
            if job[key] is None:
                job[key] = ''
        jobs_data.append(job)

    jobs_conn.close()

    # Count stats
    total = len(jobs_data)
    tier1 = len([j for j in jobs_data if j['tier'] == 1])
    tier2 = len([j for j in jobs_data if j['tier'] == 2])
    tier3 = len([j for j in jobs_data if j['tier'] == 3])

    # Count by status
    to_apply = len([j for j in jobs_data if j['status'] == 'to_apply'])
    applied = len([j for j in jobs_data if j['status'] == 'applied'])
    interview = len([j for j in jobs_data if j['status'] == 'interview'])
    offer = len([j for j in jobs_data if j['status'] == 'offer'])
    rejected = len([j for j in jobs_data if j['status'] == 'rejected'])

    print(f"📊 Loaded {total} jobs")
    print(f"   Tier 1: {tier1} | Tier 2: {tier2} | Tier 3: {tier3}")
    print(f"   To Apply: {to_apply} | Applied: {applied} | Interview: {interview}")

    # Generate jobs JSON for JavaScript
    jobs_json = json.dumps(jobs_data, indent=2)

    # Build complete HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Strategic Match - Job Tracker</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1600px;
            margin: 0 auto;
        }}

        /* Header */
        .header {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}

        .header h1 {{
            color: #667eea;
            font-size: 36px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 15px;
        }}

        .header h1::before {{
            content: "🎯";
            font-size: 48px;
        }}

        /* Stats Grid */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}

        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }}

        .stat-value {{
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 5px;
        }}

        .stat-label {{
            font-size: 14px;
            opacity: 0.9;
        }}

        /* Tabs */
        .tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }}

        .tab {{
            background: white;
            border: none;
            padding: 15px 30px;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        .tab:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.15);
        }}

        .tab.active {{
            background: #667eea;
            color: white;
        }}

        /* Kanban Board */
        .kanban-board {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .kanban-column {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }}

        .kanban-header {{
            font-size: 18px;
            font-weight: 700;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .kanban-header.to-apply {{ background: #fef3c7; color: #92400e; }}
        .kanban-header.applied {{ background: #dbeafe; color: #1e40af; }}
        .kanban-header.interview {{ background: #fce7f3; color: #831843; }}
        .kanban-header.offer {{ background: #d1fae5; color: #065f46; }}
        .kanban-header.rejected {{ background: #fee2e2; color: #991b1b; }}

        .kanban-count {{
            background: rgba(0,0,0,0.1);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 14px;
        }}

        .kanban-cards {{
            display: flex;
            flex-direction: column;
            gap: 10px;
            min-height: 200px;
        }}

        .kanban-card {{
            background: #f8fafc;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            padding: 15px;
            cursor: move;
            transition: all 0.3s;
        }}

        .kanban-card:hover {{
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }}

        .kanban-card.dragging {{
            opacity: 0.5;
        }}

        .card-title {{
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 5px;
            font-size: 14px;
        }}

        .card-company {{
            color: #667eea;
            font-size: 13px;
            margin-bottom: 10px;
        }}

        .card-meta {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-top: 10px;
        }}

        .card-badge {{
            font-size: 11px;
            padding: 3px 8px;
            border-radius: 6px;
            font-weight: 600;
        }}

        .tier-1 {{ background: #FFD700; color: #856404; }}
        .tier-2 {{ background: #C0C0C0; color: #495057; }}
        .tier-3 {{ background: #CD7F32; color: #fff; }}

        .match-badge {{
            background: #22c55e;
            color: white;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
        }}

        /* Table View */
        .table-container {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            overflow-x: auto;
        }}

        .search-bar {{
            margin-bottom: 20px;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }}

        .search-bar input,
        .search-bar select {{
            padding: 12px 20px;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            font-size: 14px;
            flex: 1;
            min-width: 200px;
        }}

        .search-bar input:focus,
        .search-bar select:focus {{
            outline: none;
            border-color: #667eea;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th, td {{
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }}

        th {{
            background: #f8fafc;
            font-weight: 700;
            color: #475569;
            position: sticky;
            top: 0;
            cursor: pointer;
        }}

        th:hover {{
            background: #e2e8f0;
        }}

        tr:hover {{
            background: #f8fafc;
        }}

        .job-link {{
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }}

        .job-link:hover {{
            text-decoration: underline;
        }}

        .status-select {{
            padding: 6px 12px;
            border: 2px solid #e2e8f0;
            border-radius: 6px;
            font-size: 13px;
            cursor: pointer;
        }}

        .action-btn {{
            padding: 6px 12px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            transition: all 0.3s;
        }}

        .action-btn:hover {{
            background: #5568d3;
        }}

        .hidden {{
            display: none !important;
        }}

        /* Modal */
        .modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }}

        .modal.active {{
            display: flex;
        }}

        .modal-content {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            max-width: 800px;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}

        .modal-header {{
            margin-bottom: 20px;
        }}

        .modal-title {{
            font-size: 24px;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 5px;
        }}

        .modal-company {{
            font-size: 18px;
            color: #667eea;
        }}

        .modal-section {{
            margin-bottom: 20px;
        }}

        .modal-section h3 {{
            color: #475569;
            margin-bottom: 10px;
            font-size: 16px;
        }}

        .modal-section p {{
            color: #64748b;
            line-height: 1.6;
        }}

        .close-btn {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: #f1f5f9;
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            font-size: 24px;
            cursor: pointer;
            transition: all 0.3s;
        }}

        .close-btn:hover {{
            background: #e2e8f0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>Strategic Match</h1>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{total}</div>
                    <div class="stat-label">Total Jobs</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{tier1}</div>
                    <div class="stat-label">🏆 Tier 1</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{tier2}</div>
                    <div class="stat-label">🥈 Tier 2</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{tier3}</div>
                    <div class="stat-label">🥉 Tier 3</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{to_apply}</div>
                    <div class="stat-label">To Apply</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{applied}</div>
                    <div class="stat-label">Applied</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{interview}</div>
                    <div class="stat-label">Interview</div>
                </div>
            </div>
        </div>

        <!-- Tabs -->
        <div class="tabs">
            <button class="tab active" onclick="showView('kanban')">📊 Kanban Board</button>
            <button class="tab" onclick="showView('table')">📋 Table View</button>
        </div>

        <!-- Kanban Board -->
        <div id="kanban-view">
            <div class="kanban-board">
                <div class="kanban-column">
                    <div class="kanban-header to-apply">
                        To Apply
                        <span class="kanban-count" id="count-to-apply">{to_apply}</span>
                    </div>
                    <div class="kanban-cards" id="column-to-apply" data-status="to_apply"></div>
                </div>

                <div class="kanban-column">
                    <div class="kanban-header applied">
                        Applied
                        <span class="kanban-count" id="count-applied">{applied}</span>
                    </div>
                    <div class="kanban-cards" id="column-applied" data-status="applied"></div>
                </div>

                <div class="kanban-column">
                    <div class="kanban-header interview">
                        Interview
                        <span class="kanban-count" id="count-interview">{interview}</span>
                    </div>
                    <div class="kanban-cards" id="column-interview" data-status="interview"></div>
                </div>

                <div class="kanban-column">
                    <div class="kanban-header offer">
                        Offer
                        <span class="kanban-count" id="count-offer">{offer}</span>
                    </div>
                    <div class="kanban-cards" id="column-offer" data-status="offer"></div>
                </div>

                <div class="kanban-column">
                    <div class="kanban-header rejected">
                        Rejected
                        <span class="kanban-count" id="count-rejected">{rejected}</span>
                    </div>
                    <div class="kanban-cards" id="column-rejected" data-status="rejected"></div>
                </div>
            </div>
        </div>

        <!-- Table View -->
        <div id="table-view" class="hidden">
            <div class="table-container">
                <div class="search-bar">
                    <input type="text" id="search-input" placeholder="🔍 Search jobs..." onkeyup="filterTable()">
                    <select id="tier-filter" onchange="filterTable()">
                        <option value="">All Tiers</option>
                        <option value="1">Tier 1</option>
                        <option value="2">Tier 2</option>
                        <option value="3">Tier 3</option>
                    </select>
                    <select id="status-filter" onchange="filterTable()">
                        <option value="">All Statuses</option>
                        <option value="to_apply">To Apply</option>
                        <option value="applied">Applied</option>
                        <option value="interview">Interview</option>
                        <option value="offer">Offer</option>
                        <option value="rejected">Rejected</option>
                    </select>
                </div>

                <table id="jobs-table">
                    <thead>
                        <tr>
                            <th onclick="sortTable(0)">Title</th>
                            <th onclick="sortTable(1)">Company</th>
                            <th onclick="sortTable(2)">Location</th>
                            <th onclick="sortTable(3)">Match</th>
                            <th onclick="sortTable(4)">Tier</th>
                            <th onclick="sortTable(5)">Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="table-body"></tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- Job Details Modal -->
    <div class="modal" id="job-modal">
        <div class="modal-content">
            <button class="close-btn" onclick="closeModal()">×</button>
            <div class="modal-header">
                <div class="modal-title" id="modal-title"></div>
                <div class="modal-company" id="modal-company"></div>
            </div>
            <div id="modal-body"></div>
        </div>
    </div>

    <script>
        const jobsData = {jobs_json};
        let currentView = 'kanban';

        // Initialize
        function init() {{
            renderKanban();
            renderTable();
        }}

        // Show view
        function showView(view) {{
            currentView = view;
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            event.target.classList.add('active');

            if (view === 'kanban') {{
                document.getElementById('kanban-view').classList.remove('hidden');
                document.getElementById('table-view').classList.add('hidden');
            }} else {{
                document.getElementById('kanban-view').classList.add('hidden');
                document.getElementById('table-view').classList.remove('hidden');
            }}
        }}

        // Render Kanban
        function renderKanban() {{
            const statuses = ['to_apply', 'applied', 'interview', 'offer', 'rejected'];

            statuses.forEach(status => {{
                const column = document.getElementById(`column-${{status}}`);
                column.innerHTML = '';

                const jobs = jobsData.filter(j => j.status === status);

                jobs.forEach(job => {{
                    const card = document.createElement('div');
                    card.className = 'kanban-card';
                    card.draggable = true;
                    card.dataset.jobId = job.id;
                    card.innerHTML = `
                        <div class="card-title">${{job.title}}</div>
                        <div class="card-company">${{job.company}}</div>
                        <div class="card-meta">
                            <span class="card-badge tier-${{job.tier}}">Tier ${{job.tier}}</span>
                            ${{job.match_score ? `<span class="match-badge">${{job.match_score}}%</span>` : ''}}
                        </div>
                    `;

                    card.addEventListener('dragstart', handleDragStart);
                    card.addEventListener('dragend', handleDragEnd);
                    card.addEventListener('click', () => showJobDetails(job.id));

                    column.appendChild(card);
                }});
            }});

            // Setup drop zones
            document.querySelectorAll('.kanban-cards').forEach(column => {{
                column.addEventListener('dragover', handleDragOver);
                column.addEventListener('drop', handleDrop);
            }});
        }}

        // Drag and drop handlers
        let draggedElement = null;

        function handleDragStart(e) {{
            draggedElement = this;
            this.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
        }}

        function handleDragEnd(e) {{
            this.classList.remove('dragging');
        }}

        function handleDragOver(e) {{
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
        }}

        function handleDrop(e) {{
            e.preventDefault();
            if (draggedElement && this !== draggedElement.parentElement) {{
                const jobId = parseInt(draggedElement.dataset.jobId);
                const newStatus = this.dataset.status;

                // Update job status
                const job = jobsData.find(j => j.id === jobId);
                if (job) {{
                    job.status = newStatus;
                    updateJobStatus(jobId, newStatus);
                    renderKanban();
                    updateCounts();
                }}
            }}
        }}

        // Update job status (would call API in production)
        function updateJobStatus(jobId, status) {{
            console.log(`Updating job ${{jobId}} to status: ${{status}}`);
            // In production, call your API:
            // fetch('/api/update-status', {{
            //     method: 'POST',
            //     headers: {{'Content-Type': 'application/json'}},
            //     body: JSON.stringify({{jobId, status}})
            // }});
        }}

        // Update counts
        function updateCounts() {{
            const statuses = ['to_apply', 'applied', 'interview', 'offer', 'rejected'];
            statuses.forEach(status => {{
                const count = jobsData.filter(j => j.status === status).length;
                const el = document.getElementById(`count-${{status}}`);
                if (el) el.textContent = count;
            }});
        }}

        // Render Table
        function renderTable() {{
            const tbody = document.getElementById('table-body');
            tbody.innerHTML = '';

            jobsData.forEach(job => {{
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td><a href="${{job.url}}" target="_blank" class="job-link">${{job.title}}</a></td>
                    <td>${{job.company}}</td>
                    <td>${{job.location || 'N/A'}}</td>
                    <td>${{job.match_score || 'N/A'}}%</td>
                    <td><span class="card-badge tier-${{job.tier}}">Tier ${{job.tier}}</span></td>
                    <td>
                        <select class="status-select" onchange="changeStatus(${{job.id}}, this.value)">
                            <option value="to_apply" ${{job.status === 'to_apply' ? 'selected' : ''}}>To Apply</option>
                            <option value="applied" ${{job.status === 'applied' ? 'selected' : ''}}>Applied</option>
                            <option value="interview" ${{job.status === 'interview' ? 'selected' : ''}}>Interview</option>
                            <option value="offer" ${{job.status === 'offer' ? 'selected' : ''}}>Offer</option>
                            <option value="rejected" ${{job.status === 'rejected' ? 'selected' : ''}}>Rejected</option>
                        </select>
                    </td>
                    <td><button class="action-btn" onclick="showJobDetails(${{job.id}})">Details</button></td>
                `;
            }});
        }}

        // Filter table
        function filterTable() {{
            const searchTerm = document.getElementById('search-input').value.toLowerCase();
            const tierFilter = document.getElementById('tier-filter').value;
            const statusFilter = document.getElementById('status-filter').value;

            const rows = document.getElementById('table-body').getElementsByTagName('tr');

            Array.from(rows).forEach(row => {{
                const cells = row.getElementsByTagName('td');
                const title = cells[0].textContent.toLowerCase();
                const company = cells[1].textContent.toLowerCase();
                const tier = cells[4].textContent;
                const status = cells[5].querySelector('select').value;

                const matchesSearch = title.includes(searchTerm) || company.includes(searchTerm);
                const matchesTier = !tierFilter || tier.includes(tierFilter);
                const matchesStatus = !statusFilter || status === statusFilter;

                row.style.display = (matchesSearch && matchesTier && matchesStatus) ? '' : 'none';
            }});
        }}

        // Sort table
        function sortTable(column) {{
            const table = document.getElementById('jobs-table');
            const tbody = table.tBodies[0];
            const rows = Array.from(tbody.rows);

            rows.sort((a, b) => {{
                const aVal = a.cells[column].textContent;
                const bVal = b.cells[column].textContent;
                return aVal.localeCompare(bVal);
            }});

            rows.forEach(row => tbody.appendChild(row));
        }}

        // Change status from table
        function changeStatus(jobId, newStatus) {{
            const job = jobsData.find(j => j.id === jobId);
            if (job) {{
                job.status = newStatus;
                updateJobStatus(jobId, newStatus);
                renderKanban();
                updateCounts();
            }}
        }}

        // Show job details modal
        function showJobDetails(jobId) {{
            const job = jobsData.find(j => j.id === jobId);
            if (!job) return;

            document.getElementById('modal-title').textContent = job.title;
            document.getElementById('modal-company').textContent = job.company;

            const body = document.getElementById('modal-body');
            body.innerHTML = `
                <div class="modal-section">
                    <h3>📍 Location</h3>
                    <p>${{job.location || 'Not specified'}}</p>
                </div>
                <div class="modal-section">
                    <h3>💰 Salary Range</h3>
                    <p>${{job.salary_range || 'Not specified'}}</p>
                </div>
                <div class="modal-section">
                    <h3>🎯 Match Score</h3>
                    <p>${{job.match_score || 'N/A'}}% match</p>
                </div>
                ${{job.company_overview ? `
                <div class="modal-section">
                    <h3>🏢 Company Overview</h3>
                    <p>${{job.company_overview}}</p>
                </div>
                ` : ''}}
                ${{job.why_this_role ? `
                <div class="modal-section">
                    <h3>✨ Why This Role</h3>
                    <p>${{job.why_this_role}}</p>
                </div>
                ` : ''}}
                ${{job.key_requirements ? `
                <div class="modal-section">
                    <h3>📋 Key Requirements</h3>
                    <p>${{job.key_requirements}}</p>
                </div>
                ` : ''}}
                ${{job.interview_prep ? `
                <div class="modal-section">
                    <h3>💼 Interview Prep</h3>
                    <p>${{job.interview_prep}}</p>
                </div>
                ` : ''}}
                ${{job.talking_points ? `
                <div class="modal-section">
                    <h3>💬 Talking Points</h3>
                    <p>${{job.talking_points}}</p>
                </div>
                ` : ''}}
                ${{job.red_flags ? `
                <div class="modal-section">
                    <h3>🚩 Red Flags</h3>
                    <p>${{job.red_flags}}</p>
                </div>
                ` : ''}}
                <div class="modal-section">
                    <a href="${{job.url}}" target="_blank" class="action-btn" style="display: inline-block; margin-top: 10px;">View Job Posting →</a>
                </div>
            `;

            document.getElementById('job-modal').classList.add('active');
        }}

        // Close modal
        function closeModal() {{
            document.getElementById('job-modal').classList.remove('active');
        }}

        // Initialize on load
        init();
        console.log(`✅ Dashboard loaded with ${{jobsData.length}} jobs`);
    </script>
</body>
</html>"""

    # Save dashboard
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print("\n✅ Professional Dashboard Created!")
    print(f"   File: index.html")
    print(f"   Total jobs: {total}")
    print(f"   Features: Kanban board, table view, drag-drop, search, filters")
    print("=" * 60)

if __name__ == "__main__":
    build_dashboard()
