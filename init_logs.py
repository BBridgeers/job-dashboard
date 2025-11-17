#!/usr/bin/env python3
# init_logs.py - Create logs directory if it doesn't exist

from pathlib import Path

logs_dir = Path('logs')
logs_dir.mkdir(exist_ok=True)

log_file = logs_dir / 'daily_run.log'
if not log_file.exists():
    log_file.write_text(f"Job Search Automation Log\nInitialized: {Path.cwd()}\n\n")

print(f"✅ Logs directory ready: {logs_dir.absolute()}")
