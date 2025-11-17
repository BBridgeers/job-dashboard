@echo off
REM Daily Job Search Automation
REM Runs at 7:00 AM daily

echo ========================================
echo JOB SEARCH AUTOMATION - DAILY RUN
echo Started: %date% %time%
echo ========================================

cd /d C:\Users\yoga\Documents\job_search_automation

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the complete automation
echo.
echo Running job searches and updating dashboard...
python run_all.py >> logs\daily_run.log 2>&1

echo.
echo ========================================
echo Daily run completed: %date% %time%
echo Check logs\daily_run.log for details
echo ========================================

REM Keep window open if run manually (will auto-close if scheduled)
if "%1" NEQ "scheduled" pause
