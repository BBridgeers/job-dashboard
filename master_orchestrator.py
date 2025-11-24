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
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        duration = datetime.datetime.now() - start_time
        print(f"✅ COMPLETED: {description} (took {duration.seconds}s)")
        if result.stdout.strip():
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ FAILED: {description}")
        print(f"   Error Code: {e.returncode}")
        if e.stdout:
            print(f"   STDOUT: {e.stdout}")
        if e.stderr:
            print(f"   STDERR: {e.stderr}")
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

def check_prerequisites():
    """Check if required files exist before running"""
    required_files = [
        "search_corporate_ai_saas.py",
        "search_nonprofit_missions.py",
        "migrate_final.py",
        "build_dashboard_pro.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ MISSING REQUIRED FILES: {', '.join(missing_files)}")
        return False
    return True

def check_environment():
    """Check if required environment variables are set"""
    required_vars = ["PERPLEXITY_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ MISSING ENVIRONMENT VARIABLES: {', '.join(missing_vars)}")
        print("   Please set these environment variables before running.")
        return False
    return True

def main():
    print("==================================================")
    print("   STRATEGIC MATCH - AUTOMATION MASTER SCRIPT")
    print(f"   Started: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("==================================================")

    # Check prerequisites
    if not check_prerequisites():
        print("❌ PREREQUISITES NOT MET. Exiting.")
        sys.exit(1)

    # Check environment variables
    if not check_environment():
        print("❌ ENVIRONMENT NOT READY. Exiting.")
        sys.exit(1)

    # Create job_search_results directory if it doesn't exist
    os.makedirs("job_search_results", exist_ok=True)
    print("📁 Ensured job_search_results directory exists")

    # 1. Run Search Scripts
    print("\n🔍 PHASE 1: Running Job Search Scripts...")
    corporate_success = run_step("python3 search_corporate_ai_saas.py", "Corporate Search")
    if not corporate_success:
        print("⚠️  Warning: Corporate search had issues. Continuing...")

    nonprofit_success = run_step("python3 search_nonprofit_missions.py", "Nonprofit Search")
    if not nonprofit_success:
        print("⚠️  Warning: Nonprofit search had issues. Continuing...")

    # 2. Migrate Data
    print("\n💾 PHASE 2: Migrating Data to Database...")
    if not run_step("python3 migrate_final.py", "Database Migration"):
        print("❌ CRITICAL: Database migration failed. Stopping.")
        sys.exit(1)

    # 3. Build Dashboard
    print("\n🎨 PHASE 3: Building Dashboard...")
    if not run_step("python3 build_dashboard_pro.py", "Dashboard Build"):
        print("❌ CRITICAL: Dashboard build failed. Stopping.")
        sys.exit(1)

    # 4. Git Push (Optional flag)
    print("\n📤 PHASE 4: Deployment...")
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
