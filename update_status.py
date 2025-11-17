#!/usr/bin/env python3
# update_status.py - Update application status
"""
Application Status Updater
Usage: python3 update_status.py [app_id] [status] [options]
"""

import sys
from application_tracker import ApplicationTracker

VALID_STATUSES = [
    'applied',
    'screening',
    'phone_screen',
    'interviewing',
    'offered',
    'accepted',
    'declined',
    'rejected',
    'ghosted'
]

def show_applications():
    """Show all active applications"""
    tracker = ApplicationTracker()
    apps = tracker.get_applications()

    print(f"\n📋 ACTIVE APPLICATIONS ({len(apps)}):")
    print("="*80)

    for app in apps:
        print(f"\n[{app['app_id']}] {app['title']} - {app['company']}")
        print(f"    Applied: {app['application_date']} | Status: {app['status'].upper()}")
        if app['next_action']:
            print(f"    Next Action: {app['next_action']} on {app['next_action_date']}")

    tracker.close()

def update_status(app_id, new_status, notes=None, next_action=None, next_action_date=None):
    """Update application status"""
    tracker = ApplicationTracker()

    success = tracker.update_status(
        app_id=app_id,
        new_status=new_status,
        notes=notes,
        next_action=next_action,
        next_action_date=next_action_date
    )

    if success:
        print(f"\n✅ Status updated to: {new_status.upper()}")
        if next_action:
            print(f"   Next Action: {next_action} on {next_action_date}")

    tracker.close()

def main():
    if len(sys.argv) == 1:
        show_applications()
        print(f"\n🔄 VALID STATUSES: {', '.join(VALID_STATUSES)}")
        print("\n📝 TO UPDATE STATUS:")
        print("   python3 update_status.py [app_id] [status]")
        print("   python3 update_status.py 1 phone_screen --notes 'Scheduled for Monday'")
        print("   python3 update_status.py 2 interviewing --next 'Second interview' --date '2025-11-20'")
        return

    if len(sys.argv) < 3:
        print("❌ Usage: python3 update_status.py [app_id] [status]")
        return

    app_id = int(sys.argv[1])
    new_status = sys.argv[2]

    if new_status not in VALID_STATUSES:
        print(f"❌ Invalid status. Valid: {', '.join(VALID_STATUSES)}")
        return

    # Parse optional arguments
    notes = None
    next_action = None
    next_action_date = None

    for i, arg in enumerate(sys.argv[3:], 3):
        if arg == '--notes' and i+1 < len(sys.argv):
            notes = sys.argv[i+1]
        elif arg == '--next' and i+1 < len(sys.argv):
            next_action = sys.argv[i+1]
        elif arg == '--date' and i+1 < len(sys.argv):
            next_action_date = sys.argv[i+1]

    update_status(app_id, new_status, notes, next_action, next_action_date)

if __name__ == "__main__":
    main()
