import os
import json
import sqlite3
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class PerplexityUploader:
    def __init__(self):
        self.api_key = os.getenv("PERPLEXITY_API_KEY", "")
        self.api_url = "https://api.perplexity.ai/chat/completions"
        self.db_path = Path("master_job_tracker.db")
        self._init_database()

    def _init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_found DATE NOT NULL,
                search_type TEXT NOT NULL,
                job_title TEXT NOT NULL,
                company TEXT NOT NULL,
                match_score INTEGER,
                salary_min INTEGER,
                salary_max INTEGER,
                location TEXT,
                employment_type TEXT,
                posted_date DATE,
                job_board TEXT,
                url TEXT,
                description TEXT,
                requirements TEXT,
                benefits TEXT,
                red_flags TEXT,
                priority TEXT,
                status TEXT DEFAULT 'new',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL,
                applied_date DATE NOT NULL,
                customized_resume_path TEXT,
                customized_cover_letter_path TEXT,
                application_url TEXT,
                status TEXT DEFAULT 'submitted',
                follow_up_date DATE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES jobs (id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER NOT NULL,
                interview_date DATE NOT NULL,
                interview_type TEXT,
                interviewer_name TEXT,
                interviewer_title TEXT,
                interview_notes TEXT,
                prep_doc_path TEXT,
                outcome TEXT,
                next_steps TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (application_id) REFERENCES applications (id)
            )
        """)
        conn.commit()
        conn.close()
        print("✅ Database initialized")

    def parse_results_file(self, filepath: Path) -> Dict:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        search_type = "nonprofit" if "nonprofit" in filepath.name.lower() else "corporate"
        date_found = datetime.now().strftime("%Y-%m-%d")
        return {"search_type": search_type, "date_found": date_found, "content": content, "filepath": str(filepath)}

    def store_jobs_in_database(self, results: Dict):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO jobs (date_found, search_type, job_title, company, match_score, description, status)
            VALUES (?, ?, ?, ?, ?, ?, 'new')
        """, (results['date_found'], results['search_type'], f"Bulk upload - {results['date_found']}", "Multiple", 0, results['content']))
        conn.commit()
        job_id = cursor.lastrowid
        conn.close()
        return job_id

    def create_perplexity_message(self, results: Dict) -> str:
        message = f"""📅 DAILY JOB SEARCH RESULTS - {results['date_found']}
📊 Search Type: {results['search_type'].upper()}

{results['content']}

---
Stored in master database. Ready to generate custom resumes/cover letters on demand.
"""
        return message

    def save_for_manual_upload(self, results: Dict):
        upload_file = Path(f"perplexity_upload_{results['date_found']}_{results['search_type']}.txt")
        message = self.create_perplexity_message(results)
        with open(upload_file, 'w', encoding='utf-8') as f:
            f.write(message)
        print(f"✅ Created upload file: {upload_file}")
        print("📤 Drag this file into your Perplexity thread!")
        return str(upload_file)

    def generate_daily_summary(self) -> str:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("SELECT search_type, COUNT(*) as count FROM jobs WHERE date_found = ? GROUP BY search_type", (today,))
        results = cursor.fetchall()
        conn.close()
        summary = f"📊 Daily Summary - {today}\n\n"
        for search_type, count in results:
            summary += f"- {search_type.title()}: {count} jobs found\n"
        return summary

    def get_high_priority_jobs(self, days: int = 7, min_score: int = 80) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM jobs WHERE match_score >= ? AND status = 'new'
            AND date_found >= date('now', '-' || ? || ' days')
            ORDER BY match_score DESC, date_found DESC
        """, (min_score, days))
        results = cursor.fetchall()
        conn.close()
        return results

def main():
    uploader = PerplexityUploader()
    results_dir = Path("job_search_results")
    today = datetime.now().strftime("%Y-%m-%d")
    nonprofit_file = results_dir / f"job_search_{today}.txt"
    corporate_file = results_dir / f"job_search_corporate_{today}.txt"
    files_to_process = []
    if nonprofit_file.exists():
        files_to_process.append(nonprofit_file)
    if corporate_file.exists():
        files_to_process.append(corporate_file)
    if not files_to_process:
        print("⚠️  No results files found for today")
        return
    for filepath in files_to_process:
        print(f"\n📂 Processing: {filepath.name}")
        results = uploader.parse_results_file(filepath)
        job_id = uploader.store_jobs_in_database(results)
        print(f"✅ Stored in database (Job ID: {job_id})")
        uploader.save_for_manual_upload(results)
    summary = uploader.generate_daily_summary()
    print(f"\n{summary}")
    high_priority = uploader.get_high_priority_jobs(days=7, min_score=85)
    if high_priority:
        print(f"\n🔥 {len(high_priority)} high-priority jobs (85%+ match) in last 7 days!")

if __name__ == "__main__":
    main()
