from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__, static_folder='.')
CORS(app)

def get_db_connection():
    conn = sqlite3.connect('jobs.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- Static File Serving (Prod & Local) ---
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/tracker.html')
def serve_tracker():
    return send_from_directory('.', 'tracker.html')

@app.route('/<path:path>')
def serve_static(path):
    # Serve other static files like images or CSS if they exist
    if os.path.exists(path):
        return send_from_directory('.', path)
    return "File not found", 404

# --- API Endpoints ---

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    try:
        conn = get_db_connection()
        jobs = conn.execute('SELECT * FROM jobs').fetchall()
        conn.close()
        return jsonify([dict(ix) for ix in jobs])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
    app.run(host='0.0.0.0', port=port, debug=True)
