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
def get_jobs():
    conn = get_db_connection()
    jobs = conn.execute('SELECT * FROM jobs').fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in jobs])

@app.route('/api/update_status', methods=['POST'])
def update_status():
    data = request.json
    conn = get_db_connection()
    conn.execute('UPDATE jobs SET status = ? WHERE id = ?', (data['status'], data['id']))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

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
