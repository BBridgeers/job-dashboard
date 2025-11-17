import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

class JobQueryHelper:
    def __init__(self):
        self.db_path = Path("master_job_tracker.db")

    def get_jobs_by_match_score(self, min_score=80):
        """Get jobs above minimum match score"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT job_title, company, match_score, salary_min, salary_max, location, date_found, status
            FROM jobs
            WHERE match_score >= ? AND status = 'new'
            ORDER BY match_score DESC
        """, (min_score,))
        results = cursor.fetchall()
        conn.close()

        print(f"\n🔥 JOBS WITH {min_score}%+ MATCH SCORE:\n")
        for job in results:
            print(f"{job[2]}% - {job[0]} at {job[1]}")
            print(f"   💰 ${job[3]}-{job[4]}K | 📍 {job[5]} | 📅 {job[6]}")
            print()
        return results

    def get_unapplied_jobs(self):
        """Get all jobs you haven't applied to yet"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, job_title, company, match_score, date_found, search_type
            FROM jobs
            WHERE status = 'new'
            ORDER BY match_score DESC, date_found DESC
        """)
        results = cursor.fetchall()
        conn.close()

        print(f"\n📋 UNAPPLIED JOBS ({len(results)} total):\n")
        for job in results:
            print(f"#{job[0]} - {job[3]}% - {job[1]} at {job[2]} ({job[5].title()}) - {job[4]}")
        return results

    def get_jobs_by_date_range(self, days_back=7):
        """Get jobs found in last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT job_title, company, match_score, date_found, search_type
            FROM jobs
            WHERE date_found >= date('now', '-' || ? || ' days')
            ORDER BY date_found DESC, match_score DESC
        """, (days_back,))
        results = cursor.fetchall()
        conn.close()

        print(f"\n📅 JOBS FROM LAST {days_back} DAYS:\n")
        for job in results:
            print(f"{job[3]} - {job[2]}% - {job[0]} at {job[1]} ({job[4].title()})")
        return results

    def get_jobs_by_company(self, company_name):
        """Find jobs at specific company"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM jobs
            WHERE company LIKE ?
            ORDER BY date_found DESC
        """, (f"%{company_name}%",))
        results = cursor.fetchall()
        conn.close()

        print(f"\n🏢 JOBS AT {company_name.upper()}:\n")
        for job in results:
            print(f"{job[3]} - Match: {job[5]}% - Status: {job[18]}")
        return results

    def get_summary_stats(self):
        """Get overall statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Total jobs
        cursor.execute("SELECT COUNT(*) FROM jobs")
        total_jobs = cursor.fetchone()[0]

        # By search type
        cursor.execute("SELECT search_type, COUNT(*) FROM jobs GROUP BY search_type")
        by_type = cursor.fetchall()

        # By status
        cursor.execute("SELECT status, COUNT(*) FROM jobs GROUP BY status")
        by_status = cursor.fetchall()

        # High priority
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE match_score >= 85 AND status = 'new'")
        high_priority = cursor.fetchone()[0]

        conn.close()

        print("\n📊 JOB SEARCH STATISTICS\n")
        print(f"Total Jobs Found: {total_jobs}")
        print(f"\nBy Search Type:")
        for search_type, count in by_type:
            print(f"  {search_type.title()}: {count}")
        print(f"\nBy Status:")
        for status, count in by_status:
            print(f"  {status.title()}: {count}")
        print(f"\n🔥 High Priority (85%+): {high_priority}")

        return {
            "total": total_jobs,
            "by_type": dict(by_type),
            "by_status": dict(by_status),
            "high_priority": high_priority
        }

    def mark_job_applied(self, job_id, resume_path=None, cover_letter_path=None):
        """Mark a job as applied"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Update job status
        cursor.execute("UPDATE jobs SET status = 'applied' WHERE id = ?", (job_id,))

        # Add to applications table
        cursor.execute("""
            INSERT INTO applications (job_id, applied_date, customized_resume_path, customized_cover_letter_path)
            VALUES (?, ?, ?, ?)
        """, (job_id, datetime.now().strftime("%Y-%m-%d"), resume_path, cover_letter_path))

        conn.commit()
        conn.close()
        print(f"✅ Marked job #{job_id} as applied!")

def main():
    """Interactive query tool"""
    helper = JobQueryHelper()

    print("\n" + "="*80)
    print("JOB SEARCH DATABASE QUERY TOOL")
    print("="*80)

    while True:
        print("\nOptions:")
        print("1. Show high-priority jobs (85%+)")
        print("2. Show all unapplied jobs")
        print("3. Show jobs from last 7 days")
        print("4. Search by company name")
        print("5. Show summary statistics")
        print("6. Mark job as applied")
        print("0. Exit")

        choice = input("\nEnter choice: ").strip()

        if choice == "1":
            helper.get_jobs_by_match_score(85)
        elif choice == "2":
            helper.get_unapplied_jobs()
        elif choice == "3":
            helper.get_jobs_by_date_range(7)
        elif choice == "4":
            company = input("Enter company name: ").strip()
            helper.get_jobs_by_company(company)
        elif choice == "5":
            helper.get_summary_stats()
        elif choice == "6":
            job_id = int(input("Enter job ID: ").strip())
            helper.mark_job_applied(job_id)
        elif choice == "0":
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()
