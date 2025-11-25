from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

DB_PATH = 'jobs.db'

# --- DEBUG BLOCK START ---
print("🚀 SERVER STARTING...")
if os.path.exists(DB_PATH):
    size = os.path.getsize(DB_PATH)
    print(f"✅ Found database: {DB_PATH} (Size: {size} bytes)")
else:
    print(f"❌ DATABASE NOT FOUND at {DB_PATH}")
    # Attempt to create an empty one if missing so app doesn't crash
    open(DB_PATH, 'a').close()
# --- DEBUG BLOCK END ---

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/tracker.html')
def serve_tracker():
    return send_from_directory('.', 'tracker.html')

@app.route('/api/jobs', methods=['GET'])
def get_jobs_legacy():
    """Legacy endpoint - kept for backwards compatibility."""
    conn = get_db_connection()
    jobs = conn.execute('SELECT * FROM jobs').fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in jobs])

@app.route('/api/get_jobs', methods=['GET'])
def get_jobs():
    """NEW: Fetch all jobs with application status and strategy kit indicators."""
    conn = get_db_connection()
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
        if j.get('match_score', 0) >= 90: tags.append("High Match")
        if j.get('tier') == 1: tags.append("Tier 1")
        if j.get('salary_min') and j['salary_min'] > 100000: tags.append("High Pay")
        if j['has_strategy']: tags.append("🧠 Strategy Ready")
        j['tags'] = tags
        
    return jsonify(jobs)

@app.route('/api/get_strategy/<int:job_id>', methods=['GET'])
def get_strategy(job_id):
    """NEW: Fetch strategy kit for a specific job."""
    import json as json_lib
    conn = get_db_connection()
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
        "strategy": json_lib.loads(result['data']) if result['data'] else None
    }
    
    return jsonify(response)

@app.route('/api/update_status', methods=['POST'])
def update_status():
    """UPDATED: Works with new applications table."""
    data = request.json
    job_id = data.get('id') or data.get('job_id')
    new_status = data.get('status')
    
    if not job_id or not new_status:
        return jsonify({"error": "Missing job_id or status"}), 400
    
    conn = get_db_connection()
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
    
    # Also update jobs table for backwards compatibility
    conn.execute('UPDATE jobs SET status = ? WHERE id = ?', (new_status, job_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "job_id": job_id, "status": new_status})

@app.route('/api/save_note', methods=['POST'])
def save_note():
    data = request.json
    conn = get_db_connection()
    conn.execute('UPDATE jobs SET notes = ? WHERE id = ?', (data['note'], data['id']))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
