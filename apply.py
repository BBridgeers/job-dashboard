#!/usr/bin/env python3
# apply.py - Quick CLI for logging applications
"""
Quick Application Logger
Usage: python3 apply.py [job_id] [options]
"""

import sys
from application_tracker import ApplicationTracker
from job_database_manager import JobDatabaseManager
from datetime import datetime

def show_available_jobs():
    """Show jobs that haven't been applied to yet"""
    db = JobDatabaseManager()
    tracker = ApplicationTracker()

    # Get all jobs
    jobs = db.get_jobs(status='new', min_score=70)

    # Get applied job IDs
    applied = tracker.get_applications()
    applied_job_ids = set()

    # Match applications to jobs
    for app in applied:
        db.cursor.execute("SELECT id FROM jobs WHERE title = ? AND company = ?", 
                         (app['title'], app['company']))
        result = db.cursor.fetchone()
        if result:
            applied_job_ids.add(result[0])

    # Filter unapplied
    unapplied = [j for j in jobs if j['id'] not in applied_job_ids]

    print(f"\n🎯 TOP JOBS TO APPLY ({len(unapplied)} available):")
    print("="*70)

    for job in unapplied[:20]:
        print(f"\n[{job['id']}] {job['title']}")
        print(f"    Company: {job['company']}")
        print(f"    Location: {job['location']}")
        print(f"    Match: {job['match_score']}%")
        print(f"    URL: {job['url']}")

    db.close()
    tracker.close()

def log_application(job_id, resume=None, notes=None):
    """Log an application"""
    tracker = ApplicationTracker()
    db = JobDatabaseManager()

    # Verify job exists
    db.cursor.execute("SELECT title, company FROM jobs WHERE id = ?", (job_id,))
    result = db.cursor.fetchone()

    if not result:
        print(f"❌ Job ID {job_id} not found")
        return

    title, company = result

    # Log application
    app_id = tracker.log_application(
        job_id=job_id,
        resume_version=resume,
        notes=notes
    )

    print(f"\n✅ APPLICATION LOGGED!")
    print(f"Application ID: {app_id}")
    print(f"Job: {title} - {company}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")

    tracker.close()
    db.close()

def main():
    if len(sys.argv) == 1:
        show_available_jobs()
        print("\n📝 TO LOG AN APPLICATION:")
        print("   python3 apply.py [job_id]")
        print("   python3 apply.py [job_id] --resume 'Tech_Resume_v2' --notes 'Applied via LinkedIn'")
        return

    job_id = int(sys.argv[1])

    # Parse optional arguments
    resume = None
    notes = None

    for i, arg in enumerate(sys.argv[2:], 2):
        if arg == '--resume' and i+1 < len(sys.argv):
            resume = sys.argv[i+1]
        elif arg == '--notes' and i+1 < len(sys.argv):
            notes = sys.argv[i+1]

    log_application(job_id, resume, notes)

if __name__ == "__main__":
    main()
