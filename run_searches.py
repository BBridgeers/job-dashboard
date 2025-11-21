#!/usr/bin/env python3

"""
Strategic Match - Master Search Runner
Executes both corporate and nonprofit searches
"""

import subprocess
import sys
from datetime import datetime

def run_search(script_name, search_type):
    """Run a search script and report results"""
    print(f"\n{'='*60}")
    print(f"🎯 Running {search_type} Search")
    print(f"{'='*60}")

    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=300  # 2 minute timeout per search
        )

        print(result.stdout)

        if result.returncode == 0:
            print(f"\n✅ {search_type} search completed successfully!")
            return True
        else:
            print(f"\n❌ {search_type} search failed!")
            print(result.stderr)
            return False

    except subprocess.TimeoutExpired:
        print(f"\n⏱️  {search_type} search timed out (>2 minutes)")
        return False
    except Exception as e:
        print(f"\n❌ Error running {search_type} search: {e}")
        return False

def main():
    """Run both searches sequentially"""

    print("\n" + "="*60)
    print("🎯 STRATEGIC MATCH - Daily Job Search")
    print(f"   {datetime.now().strftime('%Y-%m-%d %I:%M %p')} CST")
    print("="*60)

    # Track results
    results = {}

    # Run corporate search
    results['corporate'] = run_search(
        'search_corporate_ai_saas.py',
        'CORPORATE/TECH'
    )

    # Run nonprofit search
    results['nonprofit'] = run_search(
        'search_nonprofit_missions.py',
        'NONPROFIT/MISSION'
    )

    # Summary
    print("\n" + "="*60)
    print("📊 SEARCH SUMMARY")
    print("="*60)
    print(f"Corporate: {'✅ SUCCESS' if results['corporate'] else '❌ FAILED'}")
    print(f"Nonprofit: {'✅ SUCCESS' if results['nonprofit'] else '❌ FAILED'}")

    if all(results.values()):
        print("\n🎉 All searches completed!")
        print("\nNext steps:")
        print("  1. python3 migrate_structured.py")
        print("  2. python3 build_pro_dashboard.py")
        print("  3. Open index.html")
        return 0
    else:
        print("\n⚠️  Some searches failed - check logs above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
