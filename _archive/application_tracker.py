# application_tracker.py
"""
Job Application Tracker
Manages application status, materials, and follow-ups
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path

class ApplicationTracker:
    def __init__(self, db_path='master_jobs.db'):
        """Initialize connection to existing job database"""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.init_tables()

    def init_tables(self):
        """Create application tracking tables"""

        # Applications table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL,
                application_date DATE NOT NULL,
                resume_version TEXT,
                cover_letter TEXT,
                application_method TEXT,
                confirmation_number TEXT,
                next_action TEXT,
                next_action_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES jobs(id)
            )
        """)

        # Contacts table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                title TEXT,
                email TEXT,
                phone TEXT,
                linkedin_url TEXT,
                notes TEXT,
                FOREIGN KEY (job_id) REFERENCES jobs(id)
            )
        """)

        # Interviews table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS interviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER NOT NULL,
                interview_type TEXT,
                interview_date DATETIME NOT NULL,
                interviewer_names TEXT,
                location TEXT,
                prep_notes TEXT,
                follow_up_sent BOOLEAN DEFAULT 0,
                outcome TEXT,
                FOREIGN KEY (application_id) REFERENCES applications(id)
            )
        """)

        # Offers table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS offers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER NOT NULL,
                offer_date DATE NOT NULL,
                salary_offered TEXT,
                benefits TEXT,
                start_date DATE,
                decision_deadline DATE,
                accepted BOOLEAN,
                declined_reason TEXT,
                FOREIGN KEY (application_id) REFERENCES applications(id)
            )
        """)

        self.conn.commit()

    def add_application(self, job_id, application_data):
        """Record a new job application"""
        self.cursor.execute("""
            INSERT INTO applications (
                job_id, application_date, resume_version, cover_letter,
                application_method, confirmation_number, next_action, next_action_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job_id,
            application_data.get('application_date', datetime.now().date().isoformat()),
            application_data.get('resume_version'),
            application_data.get('cover_letter'),
            application_data.get('application_method'),
            application_data.get('confirmation_number'),
            application_data.get('next_action', 'Follow-up email'),
            application_data.get('next_action_date')
        ))

        application_id = self.cursor.lastrowid

        # Update job status to 'applied'
        self.cursor.execute("""
            UPDATE jobs 
            SET status = 'applied', updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, (job_id,))

        # Log status change
        self.cursor.execute("""
            INSERT INTO status_history (job_id, old_status, new_status, notes)
            VALUES (?, 'new', 'applied', ?)
        """, (job_id, f'Application submitted via {application_data.get("application_method")}'))

        self.conn.commit()
        return application_id

    def add_contact(self, job_id, contact_data):
        """Add a contact for a job"""
        self.cursor.execute("""
            INSERT INTO contacts (job_id, name, title, email, phone, linkedin_url, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            job_id,
            contact_data.get('name'),
            contact_data.get('title'),
            contact_data.get('email'),
            contact_data.get('phone'),
            contact_data.get('linkedin_url'),
            contact_data.get('notes')
        ))

        self.conn.commit()
        return self.cursor.lastrowid

    def schedule_interview(self, application_id, interview_data):
        """Schedule an interview"""
        self.cursor.execute("""
            INSERT INTO interviews (
                application_id, interview_type, interview_date, interviewer_names,
                location, prep_notes
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            application_id,
            interview_data.get('interview_type'),
            interview_data.get('interview_date'),
            interview_data.get('interviewer_names'),
            interview_data.get('location'),
            interview_data.get('prep_notes')
        ))

        interview_id = self.cursor.lastrowid

        # Update application next action
        self.cursor.execute("""
            UPDATE applications 
            SET next_action = 'Interview scheduled',
                next_action_date = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (interview_data.get('interview_date'), application_id))

        # Update job status
        self.cursor.execute("""
            UPDATE jobs 
            SET status = 'interviewing',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = (SELECT job_id FROM applications WHERE id = ?)
        """, (application_id,))

        self.conn.commit()
        return interview_id

    def record_offer(self, application_id, offer_data):
        """Record a job offer"""
        self.cursor.execute("""
            INSERT INTO offers (
                application_id, offer_date, salary_offered, benefits,
                start_date, decision_deadline
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            application_id,
            offer_data.get('offer_date', datetime.now().date().isoformat()),
            offer_data.get('salary_offered'),
            offer_data.get('benefits'),
            offer_data.get('start_date'),
            offer_data.get('decision_deadline')
        ))

        # Update job status
        self.cursor.execute("""
            UPDATE jobs 
            SET status = 'offered',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = (SELECT job_id FROM applications WHERE id = ?)
        """, (application_id,))

        self.conn.commit()
        return self.cursor.lastrowid

    def get_upcoming_actions(self, days=7):
        """Get upcoming actions and deadlines"""
        cutoff_date = (datetime.now() + timedelta(days=days)).date().isoformat()

        self.cursor.execute("""
            SELECT 
                a.id AS application_id,
                j.title AS job_title,
                j.company,
                a.next_action,
                a.next_action_date
            FROM applications a
            JOIN jobs j ON a.job_id = j.id
            WHERE a.next_action_date IS NOT NULL
              AND a.next_action_date <= ?
              AND j.status IN ('applied', 'interviewing', 'offered')
            ORDER BY a.next_action_date ASC
        """, (cutoff_date,))

        columns = [desc[0] for desc in self.cursor.description]
        results = []
        for row in self.cursor.fetchall():
            results.append(dict(zip(columns, row)))

        return results

    def get_application_pipeline(self):
        """Get application pipeline by status"""
        self.cursor.execute("""
            SELECT 
                j.status,
                COUNT(*) as count,
                GROUP_CONCAT(j.company || ' - ' || j.title, '\n') as jobs
            FROM jobs j
            WHERE j.status IN ('applied', 'interviewing', 'offered')
            GROUP BY j.status
            ORDER BY 
                CASE j.status
                    WHEN 'applied' THEN 1
                    WHEN 'interviewing' THEN 2
                    WHEN 'offered' THEN 3
                END
        """)

        pipeline = {}
        for row in self.cursor.fetchall():
            pipeline[row[0]] = {
                'count': row[1],
                'jobs': row[2].split('\n') if row[2] else []
            }

        return pipeline

    def get_application_stats(self):
        """Get application statistics"""
        stats = {}

        # Total applications
        self.cursor.execute("SELECT COUNT(*) FROM applications")
        stats['total_applications'] = self.cursor.fetchone()[0]

        # Applications by month
        self.cursor.execute("""
            SELECT strftime('%Y-%m', application_date) as month, COUNT(*)
            FROM applications
            GROUP BY month
            ORDER BY month DESC
            LIMIT 6
        """)
        stats['by_month'] = dict(self.cursor.fetchall())

        # Interview count
        self.cursor.execute("SELECT COUNT(*) FROM interviews")
        stats['total_interviews'] = self.cursor.fetchone()[0]

        # Offers count
        self.cursor.execute("SELECT COUNT(*) FROM offers")
        stats['total_offers'] = self.cursor.fetchone()[0]

        # Response rate (interviewed / applied)
        if stats['total_applications'] > 0:
            stats['interview_rate'] = (stats['total_interviews'] / stats['total_applications']) * 100
            stats['offer_rate'] = (stats['total_offers'] / stats['total_applications']) * 100
        else:
            stats['interview_rate'] = 0
            stats['offer_rate'] = 0

        return stats

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

# Example usage
if __name__ == "__main__":
    tracker = ApplicationTracker()

    # Get stats
    stats = tracker.get_application_stats()
    print("\n📊 APPLICATION STATS:")
    print(f"Total Applications: {stats['total_applications']}")
    print(f"Total Interviews: {stats['total_interviews']}")
    print(f"Total Offers: {stats['total_offers']}")
    print(f"Interview Rate: {stats['interview_rate']:.1f}%")
    print(f"Offer Rate: {stats['offer_rate']:.1f}%")

    # Get pipeline
    pipeline = tracker.get_application_pipeline()
    print("\n📋 APPLICATION PIPELINE:")
    for status, data in pipeline.items():
        print(f"{status.upper()}: {data['count']} jobs")

    # Get upcoming actions
    upcoming = tracker.get_upcoming_actions(days=7)
    print(f"\n⏰ UPCOMING ACTIONS (Next 7 days): {len(upcoming)}")
    for action in upcoming[:5]:
        print(f"  • {action['next_action_date']}: {action['next_action']} - {action['company']}")

    tracker.close()
