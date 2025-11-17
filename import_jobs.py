#!/usr/bin/env python3
# import_jobs.py - FIXED - uses 'total' not 'total_jobs'

from job_database_manager import JobDatabaseManager
from datetime import datetime
import glob

db = JobDatabaseManager()
today = datetime.now().strftime('%Y-%m-%d')

# Corporate
corporate_files = glob.glob(f'job_search_results/job_search_corporate_sonar_{today}.txt')
if not corporate_files:
    corporate_files = glob.glob('job_search_results/job_search_corporate_sonar_*.txt')
    if corporate_files:
        corporate_files.sort(reverse=True)

if corporate_files:
    print(f"\n📥 Importing corporate jobs from: {corporate_files[0]}")
    inserted, updated = db.import_from_file(corporate_files[0], 'corporate')
    print(f"✅ Corporate: {inserted} new, {updated} updated")
else:
    print("⚠️  No corporate job file found")

# Nonprofit
nonprofit_files = glob.glob(f'job_search_results/job_search_nonprofit_sonar_{today}.txt')
if not nonprofit_files:
    nonprofit_files = glob.glob('job_search_results/job_search_*sonar_*.txt')
    if nonprofit_files:
        nonprofit_files = [f for f in nonprofit_files if 'corporate' not in f.lower()]
        nonprofit_files.sort(reverse=True)

if nonprofit_files:
    print(f"\n📥 Importing nonprofit jobs from: {nonprofit_files[0]}")
    inserted, updated = db.import_from_file(nonprofit_files[0], 'nonprofit')
    print(f"✅ Nonprofit: {inserted} new, {updated} updated")
else:
    print("⚠️  No nonprofit job file found")

# Stats - FIXED FIELD NAME
stats = db.get_stats()
print(f"\n📊 DATABASE STATS:")
print(f"   Total Jobs: {stats['total']}")  # FIXED: was 'total_jobs'
print(f"   High Match (90+): {stats['high_match']}")
print(f"   By Type: {stats['by_type']}")
print(f"   By Status: {stats['by_status']}")

# Export
db.export_to_csv('job_tracker.csv')
db.close()

print("\n✅ IMPORT COMPLETE!")
