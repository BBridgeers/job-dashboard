#!/usr/bin/env python3
"""
MASTER ORCHESTRATOR - Strategic Match Job Search Automation
===========================================================
This script runs the entire pipeline end-to-end:
1. Runs Search Scripts (Corporate & Nonprofit)
2. Migrates Data to Database
3. Rebuilds the Dashboard
4. (Optional) Pushes updates to GitHub for live deployment

Usage:
    python3 master_orchestrator.py [--push]

Options:
    --push    Automatically git add/commit/push after building.
"""
import subprocess
import sys
import datetime
import os

def run_step(command, description):
    print(f"\n🚀 STARTING: {description}...")
    print(f"   Command: {command}")
    start_time = datetime.datetime.now()

    try:
        # Run the command and capture output
        result = subprocess.run(command, shell=True, check=True, text=True)
        duration = datetime.datetime.now() - start_time
        print(f"✅ COMPLETED: {description} (took {duration.seconds}s)")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ FAILED: {description}")
        print(f"   Error Code: {e.returncode}")
        return False

def git_push():
    print("\n☁️  STARTING: Git Auto-Push...")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    commands = [
        "git add .",
        f'git commit -m "Auto-Update: Job Search Results {timestamp}"',
        "git push origin main"
    ]

    for cmd in commands:
        if not run_step(cmd, f"Git: {cmd}"):
            return False
    return True

def main():
    print("==================================================")
    print("   STRATEGIC MATCH - AUTOMATION MASTER SCRIPT")
    print(f"   Started: {datetime.datetime.now()}")
    print("==================================================")

    # 1. Run Search Scripts
    # Note: Ensure these scripts handle their own output/file saving correctly.
    if not run_step("python3 search_corporate_ai_saas.py", "Corporate Search"):
        print("⚠️  Warning: Corporate search had issues. Continuing...")

    if not run_step("python3 search_nonprofit_missions.py", "Nonprofit Search"):
        print("⚠️  Warning: Nonprofit search had issues. Continuing...")

    # 2. Migrate Data
    if not run_step("python3 migrate_final.py", "Database Migration"):
        print("❌ CRITICAL: Database migration failed. Stopping.")
        sys.exit(1)

    # 3. Build Dashboard
    if not run_step("python3 build_dashboard_pro.py", "Dashboard Build"):
        print("❌ CRITICAL: Dashboard build failed. Stopping.")
        sys.exit(1)

    # 4. Git Push (Optional flag)
    if "--push" in sys.argv:
        if git_push():
            print("\n🎉 SUCCESS: All steps complete & deployed to cloud!")
        else:
            print("\n⚠️  Done locally, but Git push failed.")
    else:
        print("\n✅ SUCCESS: Local update complete.")
        print("   (Use 'python3 master_orchestrator.py --push' to auto-deploy)")

if __name__ == "__main__":
    main()
