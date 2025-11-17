#!/usr/bin/env python3
"""
job_database_manager.py - STRATEGIC ANALYSIS PARSER
Parses rich analysis reports from sonar-pro + sonar-reasoning
"""

import sqlite3
import re
from datetime import datetime

class JobDatabaseManager:
    def __init__(self, db_path='jobs.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_type TEXT NOT NULL,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT,
                salary TEXT,
                url TEXT UNIQUE NOT NULL,
                match_score INTEGER,
                brief TEXT,
                first_seen DATE NOT NULL,
                last_seen DATE NOT NULL,
                status TEXT DEFAULT 'new',
                notes TEXT
            )
        ''')
        self.conn.commit()

    def import_from_file(self, filepath, job_type='corporate'):
        """Parse strategic analysis reports with numbered job listings"""
        inserted = 0
        updated = 0
        today = datetime.now().strftime('%Y-%m-%d')

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract jobs from numbered list format
        # Pattern: "1. Senior Account Executive" or "TITLE...RESULTS - 1. Position"
        job_blocks = re.split(r'\n(?=\d+\.\s+[A-Z])', content)

        for block in job_blocks:
            if len(block.strip()) < 50:
                continue

            job = self._parse_strategic_job(block, job_type)
            if not job:
                continue

            # Check if exists
            self.cursor.execute('SELECT id, last_seen FROM jobs WHERE url = ?', (job['url'],))
            existing = self.cursor.fetchone()

            if existing:
                self.cursor.execute(
                    'UPDATE jobs SET last_seen = ?, match_score = ?, salary = ?, location = ?, brief = ? WHERE id = ?',
                    (today, job['match_score'], job['salary'], job['location'], job['brief'], existing[0])
                )
                updated += 1
            else:
                self.cursor.execute('''
                    INSERT INTO jobs (job_type, title, company, location, salary, url, 
                                    match_score, brief, first_seen, last_seen, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'new')
                ''', (job_type, job['title'], job['company'], job['location'], 
                       job['salary'], job['url'], job['match_score'], job['brief'], today, today))
                inserted += 1

        self.conn.commit()
        return inserted, updated

    def _parse_strategic_job(self, text, job_type):
        """Extract job from strategic analysis format"""
        # Extract title from numbered heading
        title_match = re.search(r'\d+\.\s+([^\n]+?)(?:\n|-|\s{2,})', text)
        if not title_match:
            return None

        title = title_match.group(1).strip()
        # Clean title: remove location/company if embedded
        title = re.sub(r'[,;]\s+(?:Dallas|Fort Worth|TX|Remote).*$', '', title).strip()

        # Extract match score
        match_match = re.search(r'-?\s*Match Score[:\s]+([89]\d|100)', text, re.I)
        match_score = int(match_match.group(1)) if match_match else 85

        # Extract salary
        salary_match = re.search(r'-?\s*Salary(?:\s+Range)?[:\s]+([^\n]+)', text, re.I)
        salary = salary_match.group(1).strip() if salary_match else "Not specified"

        # Extract location  
        loc_match = re.search(r'-?\s*Location[:\s]+([^\n]+)', text, re.I)
        location = loc_match.group(1).strip() if loc_match else "Dallas-Fort Worth, TX"

        # Extract company
        comp_match = re.search(r'-?\s*Company(?:\s+Description)?[:\s]+([^\n\.]+)', text, re.I)
        company = comp_match.group(1).strip() if comp_match else "Strategic Match"

        # Extract URL
        url_match = re.search(r'-?\s*(?:Direct\s+)?Application\s+URL[:\s]+([^\n\s]+)', text, re.I)
        if not url_match:
            # Fallback: generate synthetic URL
            url = f"https://strategic-match.com/job/{hash(title + company) % 100000}"
        else:
            url = url_match.group(1).strip()

        # Extract brief (key requirements or description)
        req_match = re.search(r'-?\s*Key Requirements[:\s]+([^\n]+(?:\n[^\n-][^\n]+)*)', text, re.I)
        brief = req_match.group(1).strip()[:500] if req_match else text[:300]

        return {
            'title': title,
            'company': company,
            'location': location,
            'salary': salary,
            'url': url,
            'match_score': match_score,
            'brief': brief
        }

    def get_stats(self):
        """Return database statistics"""
        self.cursor.execute('SELECT COUNT(*) FROM jobs')
        total = self.cursor.fetchone()[0]

        self.cursor.execute('SELECT COUNT(*) FROM jobs WHERE match_score >= 90')
        high_match = self.cursor.fetchone()[0]

        self.cursor.execute('SELECT job_type, COUNT(*) FROM jobs GROUP BY job_type')
        by_type = dict(self.cursor.fetchall())

        self.cursor.execute('SELECT status, COUNT(*) FROM jobs GROUP BY status')
        by_status = dict(self.cursor.fetchall())

        return {
            'total': total,
            'high_match': high_match,
            'by_type': by_type,
            'by_status': by_status
        }

    def export_to_csv(self, filename='job_tracker.csv'):
        """Export jobs to CSV"""
        import csv
        self.cursor.execute('''
            SELECT title, company, location, salary, match_score, url, status, first_seen 
            FROM jobs ORDER BY match_score DESC, first_seen DESC
        ''')

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Title', 'Company', 'Location', 'Salary', 'Match', 'URL', 'Status', 'First Seen'])
            writer.writerows(self.cursor.fetchall())

    def close(self):
        self.conn.close()
