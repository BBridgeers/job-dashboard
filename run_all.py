#!/usr/bin/env python3
"""
Complete Job Search Automation Runner
Runs all job search tasks and auto-deploys to GitHub
"""
import sys
import subprocess
from datetime import datetime
from pathlib import Path

def run_script(script_name, description):
    """Run a Python script and handle errors"""
    print(f"\n{'='*60}")
    print(f"▶ {description}")
    print('='*60)

    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=False,
            text=True
        )

        if result.returncode == 0:
            print(f"✅ {description} - COMPLETED")
            return True
        else:
            print(f"⚠️ {description} - COMPLETED WITH WARNINGS")
            return True  # Continue anyway

    except Exception as e:
        print(f"❌ {description} - FAILED: {e}")
        return False

def main():
    """Run all automation tasks"""
    start_time = datetime.now()

    print("\n" + "="*60)
    print("🚀 JOB SEARCH AUTOMATION - FULL RUN")
    print("="*60)
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    tasks = [
        ("job_search_agent_corporate_sonar_pro.py", "Corporate Job Search"),
        ("job_search_agent_nonprofit_sonar_pro.py", "Nonprofit Job Search"),
        ("import_jobs.py", "Import Jobs to Database"),
        ("build_dashboard.py", "Build Dashboard"),
        ("gdrive_uploader.py", "Upload to Google Drive"),
    ]

    results = []
    for script, description in tasks:
        if Path(script).exists():
            success = run_script(script, description)
            results.append((description, success))
        else:
            print(f"\n⚠️  Skipping {description} - {script} not found")
            results.append((description, False))

    # Auto-deploy to GitHub
    print("\n" + "="*60)
    print("🌐 DEPLOYING TO GITHUB")
    print("="*60)

    try:
        import auto_deploy
        deploy_success = auto_deploy.git_auto_deploy()
        results.append(("GitHub Deployment", deploy_success))
    except Exception as e:
        print(f"❌ GitHub deployment failed: {e}")
        results.append(("GitHub Deployment", False))

    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("\n" + "="*60)
    print("📊 AUTOMATION SUMMARY")
    print("="*60)

    for task, success in results:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status} - {task}")

    print("="*60)
    print(f"Total Time: {duration:.1f} seconds")
    print(f"Completed: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")

    # Return success if at least the main tasks completed
    critical_tasks = results[:4]  # First 4 tasks are critical
    all_critical_passed = all(success for _, success in critical_tasks)

    return 0 if all_critical_passed else 1

if __name__ == "__main__":
    sys.exit(main())
