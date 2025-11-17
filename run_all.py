#!/usr/bin/env python3

# run_all.py

"""
Master Job Search Automation Script
Runs everything: searches, imports, dashboard, uploads
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

def run_command(description, command):
    """Run a command and handle errors"""
    print("\n" + "="*80)
    print(f"🚀 {description}")
    print("="*80)

    try:
        result = subprocess.run(command, check=True, capture_output=False, text=True)
        print(f"✅ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ {description} - FILE NOT FOUND")
        return False

def main():
    """Run complete job search automation"""
    print("\n" + "="*80)
    print("🚀 JOB SEARCH AUTOMATION - FULL RUN")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %I:%M %p CST')}")

    success_count = 0
    total_steps = 6

    # Step 1: Corporate job search
    if run_command(
        "CORPORATE JOB SEARCH",
        ["python3", "job_search_agent_corporate_sonar_pro.py"]
    ):
        success_count += 1

    # Step 2: Nonprofit job search
    if run_command(
        "NONPROFIT JOB SEARCH",
        ["python3", "job_search_agent_nonprofit_sonar_pro.py"]
    ):
        success_count += 1

    # Step 3: Import to database
    if run_command(
        "DATABASE IMPORT",
        ["python3", "import_jobs.py"]
    ):
        success_count += 1

    # Step 4: Build dashboard
    if run_command(
        "BUILD DASHBOARD",
        ["python3", "build_dashboard.py"]
    ):
        success_count += 1

    # Step 5: Upload to Perplexity
    if run_command(
        "UPLOAD TO PERPLEXITY",
        ["python3", "perplexity_uploader.py"]
    ):
        success_count += 1

    # Step 6: Upload to Google Drive
    if run_command(
        "UPLOAD TO GOOGLE DRIVE",
        ["python3", "gdrive_uploader.py"]
    ):
        success_count += 1

    print("\n" + "="*80)
    print(f"✅ AUTOMATION COMPLETE: {success_count}/{total_steps} steps successful")
    print("="*80)
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %I:%M %p CST')}")
    print("="*80)

if __name__ == "__main__":
    main()
