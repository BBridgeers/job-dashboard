# APPLICATION TRACKING SYSTEM - USER GUIDE

## 🎯 QUICK START

### View Available Jobs
```bash
python3 apply.py
```
Shows all jobs you haven't applied to yet, sorted by match score.

---

## 📝 LOG AN APPLICATION

### Basic Application
```bash
python3 apply.py [job_id]
```
Example:
```bash
python3 apply.py 3
```

### Application with Details
```bash
python3 apply.py [job_id] --resume 'Resume Version' --notes 'Application notes'
```
Example:
```bash
python3 apply.py 5 --resume 'Tech_Resume_v2' --notes 'Applied via company website'
```

---

## 🔄 UPDATE APPLICATION STATUS

### View All Applications
```bash
python3 update_status.py
```

### Update Status
```bash
python3 update_status.py [app_id] [status]
```

### Valid Statuses:
- `applied` - Just submitted
- `screening` - Under review
- `phone_screen` - Phone screen scheduled
- `interviewing` - In interview process
- `offered` - Received offer
- `accepted` - Accepted offer
- `declined` - Declined offer
- `rejected` - Application rejected
- `ghosted` - No response

### Examples:
```bash
# Simple status update
python3 update_status.py 1 phone_screen

# With notes
python3 update_status.py 2 interviewing --notes 'Second round scheduled'

# With next action
python3 update_status.py 3 phone_screen --next 'Phone call with HR' --date '2025-11-20'
```

---

## 📊 VIEW STATISTICS

```bash
python3 application_tracker.py
```

Shows:
- Total applications
- Applications by status
- Total interviews
- Total offers
- Accepted offers
- Recent application history

---

## 🎬 FULL WORKFLOW EXAMPLE

### 1. Find Jobs to Apply
```bash
python3 apply.py
```
Output shows jobs with IDs, like `[3]`, `[5]`, `[12]`

### 2. Apply to a Job
```bash
python3 apply.py 5 --resume 'Tech_Resume_2025' --notes 'Found via LinkedIn'
```
Returns application ID (e.g., `Application ID: 1`)

### 3. Update When You Get Response
```bash
# Got a phone screen
python3 update_status.py 1 phone_screen --next 'Call with HR' --date '2025-11-25'

# After phone screen
python3 update_status.py 1 interviewing --notes 'Moved to technical interview'

# Got an offer!
python3 update_status.py 1 offered --notes 'Salary: $85k, Benefits look good'
```

### 4. Check Your Pipeline
```bash
python3 update_status.py
```
Shows all applications and their current status

---

## 📋 DASHBOARD INTEGRATION

The dashboard automatically shows:
- ✅ Jobs you've applied to
- 🔄 Current status of each application
- 📅 Next actions and dates
- 📊 Application success rate

Run `python3 build_dashboard.py` after updating applications to see changes.

---

## 💾 DATABASE TABLES

### Applications Table
Stores: Application date, resume used, status, next actions

### Interviews Table
Stores: Interview dates, types, interviewers, outcomes

### Offers Table
Stores: Salary, benefits, start date, decision

### Status History
Tracks all status changes with timestamps

---

## 🔧 ADVANCED USAGE

### Python Script Integration
```python
from application_tracker import ApplicationTracker

tracker = ApplicationTracker()

# Log application
app_id = tracker.log_application(
    job_id=5,
    resume_version='Tech_Resume_v2',
    notes='Applied via LinkedIn'
)

# Update status
tracker.update_status(
    app_id=app_id,
    new_status='phone_screen',
    next_action='Call with HR',
    next_action_date='2025-11-20'
)

# Get all applications
apps = tracker.get_applications()
for app in apps:
    print(f"{app['title']} - {app['status']}")

tracker.close()
```

### Log Interview
```python
tracker.log_interview(
    app_id=1,
    interview_date='2025-11-25 10:00:00',
    interview_type='Technical Phone Screen',
    interviewer_name='John Smith',
    interviewer_role='Engineering Manager',
    location='Zoom',
    notes='Focus on Python and system design'
)
```

### Log Offer
```python
offer_id = tracker.log_offer(
    app_id=1,
    salary_offered='$85,000',
    benefits='Health, 401k match, PTO',
    start_date='2026-01-15',
    deadline_date='2025-12-01',
    notes='Great benefits package'
)

# Accept offer
tracker.accept_offer(offer_id, notes='Excited to join!')

# Or decline
tracker.decline_offer(offer_id, reason='Accepted another offer')
```

---

## 📈 DAILY WORKFLOW

**Morning (After 7 AM automated search):**
1. Check dashboard for new jobs
2. Review match scores and decide which to apply to
3. Log applications as you submit them

**Throughout the week:**
1. Update statuses when you hear back
2. Log interviews when scheduled
3. Add notes about each interaction

**Weekly review:**
1. Run `python3 application_tracker.py` to see stats
2. Check which applications need follow-up
3. Review next actions and upcoming interviews

---

## ✨ PRO TIPS

1. **Log immediately** - Log applications right after submitting
2. **Be specific with notes** - Include where you applied, who referred you, etc.
3. **Set next actions** - Always know your next step
4. **Review weekly** - Check your pipeline every Friday
5. **Track versions** - Note which resume/cover letter you used

---

## 🆘 TROUBLESHOOTING

### "Job ID not found"
- Run `python3 apply.py` to see valid job IDs
- Make sure the job is in the database

### "Application not found"
- Run `python3 update_status.py` to see application IDs
- Use the app_id from the list, not the job_id

### Database errors
- Make sure you're in the project directory
- Run `python3 import_jobs.py` to rebuild database if needed

---

## 🎯 QUICK REFERENCE

```bash
# View jobs to apply
python3 apply.py

# Apply to job
python3 apply.py [job_id]

# View applications
python3 update_status.py

# Update status
python3 update_status.py [app_id] [status]

# View stats
python3 application_tracker.py

# Rebuild dashboard
python3 build_dashboard.py
```

---

**You're now ready to track your entire job search!** 🚀
