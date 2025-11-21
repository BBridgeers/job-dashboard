# 🎯 Strategic Match - Enhanced Search Scripts

Separate, optimized search scripts for corporate and nonprofit job markets.

## 📂 Files Created

1. **search_corporate_ai_saas.py** - Corporate/Tech job search
2. **search_nonprofit_missions.py** - Nonprofit/Mission job search  
3. **run_searches.py** - Master runner (executes both)

## 🚀 Quick Start

### Run Both Searches
```bash
python3 run_searches.py
```

### Run Individual Searches
```bash
# Corporate only
python3 search_corporate_ai_saas.py

# Nonprofit only
python3 search_nonprofit_missions.py
```

## 📊 Corporate Search Details

**Focus Industries:**
- B2B SaaS
- AI/Automation platforms
- Education technology (EdTech)
- Financial technology (Fintech)
- Healthcare technology (Healthtech)
- Series A+ funded startups

**Job Boards (20+):**
- LinkedIn, Indeed, Glassdoor
- Built In, AngelList, Dice
- We Work Remotely, Remote.co
- Ladders ($100K+ jobs)
- FlexJobs (remote/hybrid)
- RepVue (sales/CS with ratings)
- Monster, ZipRecruiter, The Muse
- CareerBuilder, SimplyHired
- Stack Overflow Jobs, Remotive
- YC Jobs, Levels.fyi, Hired, CrunchBoard

**Target Roles:**
- Customer Success Director/VP
- Strategic Account Manager
- Customer Experience Director
- Enterprise Relationship Manager
- AI Solutions Manager

**Output:** `job_search_results/job_search_corporate_sonar_YYYY-MM-DD.txt`

## 💚 Nonprofit Search Details

**Focus Areas:**
- Education nonprofits (K-12, higher ed)
- Youth development organizations
- Community foundations
- Volunteer management
- Program management
- Donor relations (relationship-based)

**Job Boards (24+):**

*Nonprofit-Specific:*
- Idealist.org
- Chronicle of Philanthropy Jobs
- NonprofitJobs.org
- Bridgespan Career Center
- OpportunityKnocks
- Nonprofit Talent
- AFP Career Center
- Council on Foundations Jobs
- Philanthropy News Digest Jobs

*General (nonprofit filter):*
- Indeed, LinkedIn, Glassdoor
- VolunteerMatch

*Healthcare/Community:*
- American Red Cross Careers
- American Heart Association Careers (Dallas HQ!)
- United Way Career Centers
- Feeding America Careers
- SchoolSpring
- MinistryWatch Jobs

*Mission/Impact:*
- Social Impact Jobs
- Changemakers Job Board
- Work for Good
- Foundation List Jobs
- GuideStar/Candid Jobs

*DFW-Specific:*
- DFW Nonprofit Jobs (jobs.dfw501c.com)
- Dallas Foundation
- Communities Foundation of Texas
- North Texas nonprofit boards
- Local United Way DFW

**Target Roles:**
- Program Manager/Director
- Development Manager
- Community Engagement Manager
- Volunteer Coordinator/Manager
- Donor Relations Manager
- Major Gifts Officer

**Output:** `job_search_results/job_search_nonprofit_sonar_YYYY-MM-DD.txt`

## 📋 Output Format (Both Scripts)

### SECTION 1: ALL JOB LISTINGS

**Tier 1 (Top 5):** 8 core data points each
- Title, Company, Match Score, Salary, Location
- Company Overview (500-800 chars)
- Role Insights (400-600 chars)
- Key Requirements (300-400 chars)

**Tier 2 (Positions 6-10):** Same 8 core data points

**Tier 3 (Positions 11+):** 3 basic data points only
- Title, Company, Match Score

### SECTION 2: STRATEGIC ANALYSIS (Top 5 Only)

15 components per job (~6,500 chars each):
1. Company Overview
2. Role Insights
3. Key Requirements
4. Interview Prep
5. Salary Intel
6. Application Strategy
7. Red Flags
8. Cultural Fit
9. Competitive Landscape
10. Skills Gap Analysis
11. Network Leverage
12. Decision Timeline
13. Career Trajectory
14. Why This Role
15. Full Description

## 🔄 Complete Workflow

```bash
# 1. Run searches (both or individual)
python3 run_searches.py

# 2. Parse results to database
python3 migrate_structured.py

# 3. Build dashboard
python3 build_pro_dashboard.py

# 4. View results
open index.html
```

## ⏰ Automation Setup

Add to crontab for daily execution:

```bash
# Run both searches at 8 AM daily
0 8 * * * cd /mnt/c/Users/yoga/Documents/job_search_automation && python3 run_searches.py >> /tmp/job_search.log 2>&1

# Then parse and build dashboard
5 8 * * * cd /mnt/c/Users/yoga/Documents/job_search_automation && python3 migrate_structured.py && python3 build_pro_dashboard.py >> /tmp/job_search.log 2>&1
```

Or use the master `run_all.py` if you have it:

```bash
0 8 * * * cd /mnt/c/Users/yoga/Documents/job_search_automation && python3 run_all.py >> /tmp/job_search.log 2>&1
```

## 🎯 Daily Expected Output

**Corporate Search:**
- Tier 1: 5 jobs × 6,500 chars = 32,500 chars
- Tier 2: 5 jobs × 8 data points
- Tier 3: XX jobs × 3 data points

**Nonprofit Search:**
- Tier 1: 5 jobs × 6,500 chars = 32,500 chars
- Tier 2: 5 jobs × 8 data points
- Tier 3: XX jobs × 3 data points

**Total: 65,000+ characters of strategic intelligence daily!**

## 🔧 Troubleshooting

### Search returns no jobs
- Check API key in credentials.json
- Verify search_recency_filter (set to "week")
- Check job board availability
- Try broader search criteria

### Parser extracts 0 fields
- Verify ---START_JOB_X--- markers present
- Check SECTION 2 exists in output
- Run: python3 debug_all_files.py

### Timeout errors
- Searches have 2-minute timeout each
- Network issues or API slowness
- Run individual searches to isolate issue

## 💡 Pro Tips

- **Corporate focus:** AI/Automation companies are hot right now
- **Nonprofit edge:** DFW-specific boards give you local advantage
- **Best practice:** Run searches early AM for fresh listings
- **Dashboard filters:** Use "Tier 1 + Today" for focused view
- **Application timing:** Apply same day listing posted (Tier 1 only)

## 📈 Success Metrics

Track in dashboard:
- Total jobs found per day
- Tier 1 jobs (richest intel)
- Match scores 90%+
- Applications submitted
- Interview requests received

---

**Strategic Match** - Your intelligent job search partner 🎯
