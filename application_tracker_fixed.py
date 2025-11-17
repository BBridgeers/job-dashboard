import sqlite3
from datetime import datetime

class JobTracker:
    def __init__(self):
        self.conn = sqlite3.connect('applications.db')
        self.cursor = self.conn.cursor()
        self.init_db()

    def init_db(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY,
                job_id INTEGER,
                company TEXT,
                position TEXT,
                status TEXT DEFAULT 'Not Applied',
                date_applied TEXT,
                notes TEXT,
                UNIQUE(job_id)
            )
        """)
        self.conn.commit()

    def track_application(self, job_id, company, position):
        try:
            self.cursor.execute("""
                INSERT OR REPLACE INTO applications 
                (job_id, company, position, status, date_applied)
                VALUES (?, ?, ?, 'Applied', ?)
            """, (job_id, company, position, datetime.now().strftime('%Y-%m-%d')))
            self.conn.commit()
            print(f"✅ Tracked: {position} at {company}")
        except Exception as e:
            print(f"❌ Error: {e}")

    def update_status(self, job_id, status):
        self.cursor.execute("UPDATE applications SET status = ? WHERE job_id = ?", (status, job_id))
        self.conn.commit()
        print(f"✅ Updated to: {status}")

    def show_stats(self):
        self.cursor.execute("SELECT status, COUNT(*) FROM applications GROUP BY status")
        stats = self.cursor.fetchall()
        print("\n📊 APPLICATION STATS:")
        for status, count in stats:
            print(f"  {status}: {count}")

    def close(self):
        self.conn.close()

def main():
    tracker = JobTracker()

    jobs_conn = sqlite3.connect('jobs.db')
    jobs_cursor = jobs_conn.cursor()
    jobs_cursor.execute("SELECT id, title, company FROM jobs WHERE url IS NOT NULL LIMIT 20")
    jobs = jobs_cursor.fetchall()
    jobs_conn.close()

    while True:
        print("\n" + "="*50)
        print("JOB APPLICATION TRACKER")
        print("="*50)
        print("\n1. Track new application")
        print("2. Update application status")
        print("3. View statistics")
        print("4. List tracked applications")
        print("0. Exit")

        choice = input("\nChoice: ").strip()

        if choice == "1":
            print("\nAVAILABLE JOBS:")
            for i, (job_id, title, company) in enumerate(jobs, 1):
                print(f"{i}. {title} at {company} (ID: {job_id})")

            try:
                idx = int(input("\nSelect job number: ")) - 1
                job_id, title, company = jobs[idx]
                tracker.track_application(job_id, company, title)
            except:
                print("❌ Invalid selection")

        elif choice == "2":
            tracker.cursor.execute("SELECT id, job_id, position, company, status FROM applications")
            apps = tracker.cursor.fetchall()

            if not apps:
                print("\n❌ No tracked applications")
                continue

            print("\nTRACKED APPLICATIONS:")
            for i, (app_id, job_id, pos, comp, status) in enumerate(apps, 1):
                print(f"{i}. {pos} at {comp} - [{status}]")

            try:
                idx = int(input("\nSelect application: ")) - 1
                job_id = apps[idx][1]

                print("\nSTATUS OPTIONS:")
                print("1. Applied")
                print("2. Interview")
                print("3. Offer")
                print("4. Rejected")

                status_choice = input("New status: ").strip()
                statuses = {"1": "Applied", "2": "Interview", "3": "Offer", "4": "Rejected"}

                if status_choice in statuses:
                    tracker.update_status(job_id, statuses[status_choice])
            except:
                print("❌ Invalid selection")

        elif choice == "3":
            tracker.show_stats()

        elif choice == "4":
            tracker.cursor.execute("SELECT position, company, status, date_applied FROM applications")
            apps = tracker.cursor.fetchall()

            print("\n📋 TRACKED APPLICATIONS:")
            for pos, comp, status, date in apps:
                print(f"  • {pos} at {comp} - {status} ({date})")

        elif choice == "0":
            break

    tracker.close()

if __name__ == "__main__":
    main()
