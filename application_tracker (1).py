#!/usr/bin/env python3
# application_tracker.py
"""
Application Tracking System
Log and manage job applications with status updates
"""

import sqlite3
from datetime import datetime
from pathlib import Path

class ApplicationTracker:
    def __init__(self, db_path='master_jobs.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.init_tables()

    def init_tables(self):
        """Create applications and related tables"""

        # Applications table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL,
                application_date DATE NOT NULL,
                resume_version TEXT,
                cover_letter TEXT,
                status TEXT DEFAULT 'applied',
                next_action TEXT,
                next_action_date DATE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES jobs(id)
            )
        """)

        # Application status history
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS application_status_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER NOT NULL,
                old_status TEXT,
                new_status TEXT NOT NULL,
                changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (application_id) REFERENCES applications(id)
            )
        """)

        # Interview rounds
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS interviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER NOT NULL,
                interview_date DATETIME NOT NULL,
                interview_type TEXT,
                interviewer_name TEXT,
                interviewer_role TEXT,
                location TEXT,
                notes TEXT,
                outcome TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
                deadline_date DATE,
                accepted BOOLEAN,
                declined_reason TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (application_id) REFERENCES applications(id)
            )
        """)

        self.conn.commit()

    def log_application(self, job_id, resume_version=None, cover_letter=None, notes=None):
        """Log a new job application"""
        today = datetime.now().date().isoformat()

        self.cursor.execute("""
            INSERT INTO applications (
                job_id, application_date, resume_version, 
                cover_letter, status, notes
            ) VALUES (?, ?, ?, ?, 'applied', ?)
        """, (job_id, today, resume_version, cover_letter, notes))

        app_id = self.cursor.lastrowid

        # Log status history
        self.cursor.execute("""
            INSERT INTO application_status_history (
                application_id, old_status, new_status, notes
            ) VALUES (?, NULL, 'applied', 'Application submitted')
        """, (app_id,))

        # Update job status
        self.cursor.execute("""
            UPDATE jobs SET status = 'applied', updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (job_id,))

        self.conn.commit()
        return app_id

    def update_status(self, app_id, new_status, notes=None, next_action=None, next_action_date=None):
        """Update application status"""

        # Get current status
        self.cursor.execute("SELECT status FROM applications WHERE id = ?", (app_id,))
        result = self.cursor.fetchone()

        if not result:
            print(f"❌ Application {app_id} not found")
            return False

        old_status = result[0]

        # Update application
        self.cursor.execute("""
            UPDATE applications 
            SET status = ?,
                notes = COALESCE(?, notes),
                next_action = ?,
                next_action_date = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (new_status, notes, next_action, next_action_date, app_id))

        # Log status history
        self.cursor.execute("""
            INSERT INTO application_status_history (
                application_id, old_status, new_status, notes
            ) VALUES (?, ?, ?, ?)
        """, (app_id, old_status, new_status, notes))

        self.conn.commit()
        print(f"✅ Updated application {app_id}: {old_status} → {new_status}")
        return True

    def log_interview(self, app_id, interview_date, interview_type=None, 
                     interviewer_name=None, interviewer_role=None, 
                     location=None, notes=None):
        """Log an interview"""

        self.cursor.execute("""
            INSERT INTO interviews (
                application_id, interview_date, interview_type,
                interviewer_name, interviewer_role, location, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (app_id, interview_date, interview_type, interviewer_name, 
              interviewer_role, location, notes))

        interview_id = self.cursor.lastrowid

        # Update application status if not already interviewing
        self.cursor.execute("SELECT status FROM applications WHERE id = ?", (app_id,))
        current_status = self.cursor.fetchone()[0]

        if current_status not in ['interviewing', 'offered', 'accepted', 'declined']:
            self.update_status(app_id, 'interviewing', f'Interview scheduled: {interview_date}')

        self.conn.commit()
        print(f"✅ Logged interview for application {app_id}")
        return interview_id

    def log_offer(self, app_id, salary_offered=None, benefits=None, 
                  start_date=None, deadline_date=None, notes=None):
        """Log a job offer"""
        today = datetime.now().date().isoformat()

        self.cursor.execute("""
            INSERT INTO offers (
                application_id, offer_date, salary_offered, benefits,
                start_date, deadline_date, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (app_id, today, salary_offered, benefits, start_date, deadline_date, notes))

        offer_id = self.cursor.lastrowid

        # Update application status
        self.update_status(app_id, 'offered', f'Offer received: {salary_offered}')

        self.conn.commit()
        print(f"✅ Logged offer for application {app_id}")
        return offer_id

    def accept_offer(self, offer_id, notes=None):
        """Accept a job offer"""
        self.cursor.execute("""
            UPDATE offers SET accepted = 1, notes = COALESCE(?, notes)
            WHERE id = ?
        """, (notes, offer_id))

        # Get application ID and update status
        self.cursor.execute("SELECT application_id FROM offers WHERE id = ?", (offer_id,))
        app_id = self.cursor.fetchone()[0]

        self.update_status(app_id, 'accepted', f'Offer accepted: {notes}')

        self.conn.commit()
        print(f"✅ Accepted offer {offer_id}")

    def decline_offer(self, offer_id, reason=None):
        """Decline a job offer"""
        self.cursor.execute("""
            UPDATE offers 
            SET accepted = 0, declined_reason = ?
            WHERE id = ?
        """, (reason, offer_id))

        # Get application ID and update status
        self.cursor.execute("SELECT application_id FROM offers WHERE id = ?", (offer_id,))
        app_id = self.cursor.fetchone()[0]

        self.update_status(app_id, 'declined', f'Offer declined: {reason}')

        self.conn.commit()
        print(f"✅ Declined offer {offer_id}")

    def get_applications(self, status=None):
        """Get all applications with job details"""
        query = """
            SELECT 
                a.id as app_id,
                a.application_date,
                a.status,
                a.next_action,
                a.next_action_date,
                j.title,
                j.company,
                j.location,
                j.match_score,
                j.url
            FROM applications a
            JOIN jobs j ON a.job_id = j.id
        """

        if status:
            query += " WHERE a.status = ?"
            self.cursor.execute(query + " ORDER BY a.application_date DESC", (status,))
        else:
            self.cursor.execute(query + " ORDER BY a.application_date DESC")

        columns = [desc[0] for desc in self.cursor.description]
        results = []
        for row in self.cursor.fetchall():
            results.append(dict(zip(columns, row)))

        return results

    def get_stats(self):
        """Get application statistics"""
        stats = {}

        # Total applications
        self.cursor.execute("SELECT COUNT(*) FROM applications")
        stats['total_applications'] = self.cursor.fetchone()[0]

        # By status
        self.cursor.execute("""
            SELECT status, COUNT(*) FROM applications GROUP BY status
        """)
        stats['by_status'] = dict(self.cursor.fetchall())

        # Interviews
        self.cursor.execute("SELECT COUNT(*) FROM interviews")
        stats['total_interviews'] = self.cursor.fetchone()[0]

        # Offers
        self.cursor.execute("SELECT COUNT(*) FROM offers")
        stats['total_offers'] = self.cursor.fetchone()[0]

        # Accepted offers
        self.cursor.execute("SELECT COUNT(*) FROM offers WHERE accepted = 1")
        stats['accepted_offers'] = self.cursor.fetchone()[0]

        return stats

    def close(self):
        if self.conn:
            self.conn.close()

# CLI for quick application logging
if __name__ == "__main__":
    import sys

    tracker = ApplicationTracker()

    if len(sys.argv) == 1:
        # Show stats
        stats = tracker.get_stats()
        print("\n📊 APPLICATION STATS:")
        print(f"Total Applications: {stats['total_applications']}")
        print(f"By Status: {stats['by_status']}")
        print(f"Total Interviews: {stats['total_interviews']}")
        print(f"Total Offers: {stats['total_offers']}")
        print(f"Accepted Offers: {stats['accepted_offers']}")

        # Show recent applications
        apps = tracker.get_applications()
        if apps:
            print(f"\n📝 RECENT APPLICATIONS ({len(apps)}):")
            for app in apps[:10]:
                print(f"\n  [{app['app_id']}] {app['title']} - {app['company']}")
                print(f"      Applied: {app['application_date']} | Status: {app['status']}")
                if app['next_action']:
                    print(f"      Next: {app['next_action']} on {app['next_action_date']}")

    tracker.close()
