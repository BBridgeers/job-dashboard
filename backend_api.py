# backend_api.py
# Add these endpoints to your existing Render Flask/FastAPI app

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

DB_PATH = 'jobs.db'

# ==========================================
# 2️⃣ NEW API ENDPOINTS TO ADD
# ==========================================

@app.route('/api/get_jobs', methods=['GET'])
def get_jobs():
    """Fetch all jobs with application status and strategy kit indicators."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("""
        SELECT j.*, a.status as app_status, a.applied_date, a.id as app_id, s.id as strategy_id
        FROM jobs j
        LEFT JOIN applications a ON j.id = a.job_id
        LEFT JOIN strategy_kits s ON j.id = s.job_id
        ORDER BY j.match_score DESC
    """)
    jobs = [dict(row) for row in c.fetchall()]
    conn.close()
    
    # Normalize data
    for j in jobs:
        j['display_status'] = j.get('app_status') or j.get('status') or 'New'
        j['has_strategy'] = bool(j.get('strategy_id'))
        
        # Tags
        tags = []
        if j['match_score'] >= 90: tags.append("High Match")
        if j['tier'] == 1: tags.append("Tier 1")
        if j.get('salary_min') and j['salary_min'] > 100000: tags.append("High Pay")
        if j['has_strategy']: tags.append("🧠 Strategy Ready")
        j['tags'] = tags
        
    return jsonify(jobs)


@app.route('/api/get_strategy/<int:job_id>', methods=['GET'])
def get_strategy(job_id):
    """Fetch strategy kit for a specific job."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("""
        SELECT j.title, j.company, s.data 
        FROM jobs j
        LEFT JOIN strategy_kits s ON j.id = s.job_id
        WHERE j.id = ?
    """, (job_id,))
    result = c.fetchone()
    conn.close()
    
    if not result:
        return jsonify({"error": "Job not found"}), 404
    
    response = {
        "title": result['title'],
        "company": result['company'],
        "strategy": json.loads(result['data']) if result['data'] else None
    }
    
    return jsonify(response)


@app.route('/api/update_status', methods=['POST'])
def update_status():
    """Update job status (works with applications table)."""
    data = request.json
    job_id = data.get('job_id')
    new_status = data.get('status')
    
    if not job_id or not new_status:
        return jsonify({"error": "Missing job_id or status"}), 400
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check if application exists
    c.execute("SELECT id FROM applications WHERE job_id = ?", (job_id,))
    app = c.fetchone()
    
    if app:
        # Update existing application
        c.execute("UPDATE applications SET status = ? WHERE job_id = ?", (new_status, job_id))
    else:
        # Create new application
        c.execute("INSERT INTO applications (job_id, status) VALUES (?, ?)", (job_id, new_status))
    
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "job_id": job_id, "status": new_status})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
