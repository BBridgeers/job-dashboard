#!/usr/bin/env python3
import subprocess
import sys
import os
from datetime import datetime

print("=" * 60)
print("🚀 JOB SEARCH AUTOMATION - FULL RUN")
print("=" * 60)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

def run_script(name, script):
    print(f"▶️  Running: {name}")
    try:
        result = subprocess.run(
            [sys.executable, script],
            capture_output=True,
            text=True,
            timeout=300
        )
        print(result.stdout)
        if result.returncode != 0:
            print(f"❌ Error in {name}:")
            print(result.stderr)
            return False
        print(f"✅ {name} complete\n")
        return True
    except subprocess.TimeoutExpired:
        print(f"⏱️  {name} timed out\n")
        return False
    except Exception as e:
        print(f"❌ {name} failed: {e}\n")
        return False

def git_push():
    print("\n📤 STEP 5: Push to GitHub")
    print("-" * 60)
    try:
        # Check if git repo exists
        if not os.path.exists('.git'):
            print("⚠️  No git repo found. Skipping GitHub push.")
            return True

        # Add dashboard
        subprocess.run(['git', 'add', 'dashboard.html'], check=True)

        # Commit
        commit_msg = f"Auto-update dashboard {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        result = subprocess.run(
            ['git', 'commit', '-m', commit_msg],
            capture_output=True,
            text=True
        )

        if "nothing to commit" in result.stdout:
            print("ℹ️  Dashboard unchanged, no push needed")
            return True

        # Push
        subprocess.run(['git', 'push'], check=True)
        print("✅ Pushed to GitHub\n")
        return True

    except subprocess.CalledProcessError as e:
        print(f"⚠️  Git push failed: {e}")
        print("Dashboard still updated locally\n")
        return True  # Don't fail entire run

# Step 1: Run corporate job search
print("\n📊 STEP 1: Corporate Job Search")
print("-" * 60)
run_script("Corporate Search", "job_search_agent_corporate_sonar_pro.py")

# Step 2: Run nonprofit job search  
print("\n🏛️  STEP 2: Nonprofit Job Search")
print("-" * 60)
run_script("Nonprofit Search", "job_search_agent_nonprofit_sonar_pro.py")

# Step 3: Clean database
print("\n🧹 STEP 3: Clean Database")
print("-" * 60)
run_script("Database Cleaner", "clean_database.py")

# Step 4: Build dashboard
print("\n📈 STEP 4: Build Dashboard")
print("-" * 60)
run_script("Dashboard Builder", "dashboard_ULTIMATE.py")

# Step 5: Push to GitHub
git_push()

print()
print("=" * 60)
print(f"✅ ALL DONE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)
print()
print("📍 Your dashboard is live at:")
print("   🌐 https://yourusername.github.io/repo-name/dashboard.html")
print("   💻 Local: file:///path/to/dashboard.html")
print()
