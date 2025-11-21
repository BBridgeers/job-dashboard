#!/usr/bin/env python3
"""
Strategic Match - API Backend Server
Handles data persistence for Dashboard and Tracker
"""
from flask import Flask, jsonify, request, send_from_directory
import sqlite3
import os
from datetime import datetime

app = Flask(__name__, static_folder='.')

# Ensure DB connection
def get_db():
    conn = sqlite3.connect('jobs.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/api/update_status', methods=['POST'])
def update_status():
    """Update job status in database"""
    data = request.json
    job_id = data.get('id')
    new_status = data.get('status')

    if not job_id or not new_status:
        return jsonify({'error': 'Missing id or status'}), 400

    try:
        conn = get_db()
        c = conn.cursor()

        # If applied, update applied_date too
        if new_status == 'Applied':
            today = datetime.now().strftime("%Y-%m-%d")
            c.execute("UPDATE jobs SET status = ?, applied_date = ? WHERE id = ?", (new_status, today, job_id))
        else:
            c.execute("UPDATE jobs SET status = ? WHERE id = ?", (new_status, job_id))

        conn.commit()
        conn.close()
        print(f"✅ Updated Job {job_id} -> {new_status}")
        return jsonify({'success': True, 'message': f'Status updated to {new_status}'})
    except Exception as e:
        print(f"❌ DB Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/save_note', methods=['POST'])
def save_note():
    """Save user notes"""
    data = request.json
    job_id = data.get('id')
    note = data.get('note')

    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("UPDATE jobs SET notes = ? WHERE id = ?", (note, job_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Strategic Match API Server Running on http://localhost:5000")
    app.run(debug=True, port=5000)
