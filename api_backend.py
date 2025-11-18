ELSE status END
        WHERE id = ?
    """, (datetime.now().isoformat(), job_id))

    conn.commit()
    conn.close()

    return jsonify({"success": True})

@app.route('/api/job/<int:job_id>/notes', methods=['POST'])
def update_notes(job_id):
    """Update job notes"""
    data = request.json
    notes = data.get('notes')

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE jobs 
        SET notes = ?
        WHERE id = ?
    """, (notes, job_id))

    conn.commit()
    conn.close()

    return jsonify({"success": True})

@app.route('/api/jobs', methods=['GET'])
def get_all_jobs():
    """Get all jobs for tracker"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, company, status, applied_date, last_seen, notes, match_score
        FROM jobs
        ORDER BY match_score DESC, last_seen DESC
    """)

    jobs = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(jobs)

if __name__ == "__main__":
    print("🚀 Starting API Backend on http://localhost:5000")
    app.run(debug=True, port=5000)