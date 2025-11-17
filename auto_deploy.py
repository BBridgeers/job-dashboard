#!/usr/bin/env python3
"""
Auto-Deploy to GitHub
Automatically commits and pushes changes to GitHub Pages
"""
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def run_command(cmd, description=""):
    """Execute shell command and return result"""
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True,
            check=False
        )

        if description:
            print(f"  ✓ {description}")

        return result
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return None

def git_auto_deploy():
    """Automatically commit and push changes to GitHub"""
    try:
        print("\n" + "="*60)
        print("🔄 AUTO-DEPLOYING TO GITHUB")
        print("="*60)

        # Check if we're in a git repo
        check_git = run_command(["git", "status"], "Checking git status")
        if not check_git or check_git.returncode != 0:
            print("❌ Not a git repository!")
            return False

        # Get current timestamp for commit message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_msg = f"Auto-update dashboard - {timestamp}"

        # Stage all changes
        print("\n📦 Staging changes...")
        run_command(["git", "add", "."], "Added all files")

        # Check if there are changes to commit
        status = run_command(["git", "status", "--porcelain"])
        if not status.stdout.strip():
            print("\n✓ No changes to commit - already up-to-date!")
            return True

        # Commit changes
        print("\n💾 Committing changes...")
        commit_result = run_command(
            ["git", "commit", "-m", commit_msg],
            f"Committed with message: {commit_msg}"
        )

        # Push to GitHub
        print("\n🚀 Pushing to GitHub...")
        push_result = run_command(
            ["git", "push", "origin", "main"],
            "Pushed to origin/main"
        )

        if push_result and push_result.returncode == 0:
            print("\n" + "="*60)
            print("✅ SUCCESSFULLY DEPLOYED TO GITHUB!")
            print("="*60)
            print("🌐 Live at: https://bbridgeers.github.io/job-dashboard/")
            print("📊 Repo: https://github.com/BBridgeers/job-dashboard")
            print("="*60 + "\n")
            return True
        else:
            print(f"\n❌ Push failed: {push_result.stderr if push_result else 'Unknown error'}")
            return False

    except Exception as e:
        print(f"\n❌ Deploy error: {e}")
        return False

if __name__ == "__main__":
    success = git_auto_deploy()
    sys.exit(0 if success else 1)
