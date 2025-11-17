@echo off
REM Daily Job Search Automation with Auto-Deploy
REM Run this batch file to execute all job search tasks and deploy to GitHub

echo ========================================
echo  DAILY JOB SEARCH AUTOMATION
echo ========================================
echo.

cd /d C:\Users\yoga\Documents\job_search_automation

echo Activating virtual environment...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found
)

echo.
echo Running full automation suite...
echo.

python run_all.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo  AUTOMATION COMPLETED SUCCESSFULLY!
    echo ========================================
    echo.
    echo Your dashboard is live at:
    echo https://bbridgeers.github.io/job-dashboard/
    echo.
) else (
    echo.
    echo ========================================
    echo  AUTOMATION COMPLETED WITH ERRORS
    echo ========================================
    echo Please review the output above
    echo.
)

pause
