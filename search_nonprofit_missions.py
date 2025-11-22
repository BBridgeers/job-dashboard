#!/usr/bin/env python3

"""
Strategic Match - Nonprofit/Mission Job Search (Enhanced)
24 specialized nonprofit job boards including DFW-specific
"""

import os
import requests
from datetime import datetime
from pathlib import Path

def search_nonprofit_jobs(api_key):
    """Execute enhanced nonprofit job search with 3-tier structure"""

    url = "https://api.perplexity.ai/chat/completions"

    # ENHANCED NONPROFIT SEARCH QUERY
    search_query = """
Search Idealist.org, Chronicle of Philanthropy Jobs, NonprofitJobs.org, 
Bridgespan Career Center, OpportunityKnocks, Nonprofit Talent, AFP Career Center, 
Council on Foundations Jobs, Philanthropy News Digest Jobs, Indeed (nonprofit), 
LinkedIn (nonprofit sector), Glassdoor (nonprofit companies), VolunteerMatch, 
American Red Cross Careers, American Heart Association Careers, United Way Career Centers, 
Feeding America Careers, SchoolSpring, MinistryWatch Jobs, Social Impact Jobs, 
Changemakers Job Board, Work for Good, Foundation List Jobs, GuideStar/Candid Jobs,
DFW Nonprofit Jobs (jobs.dfw501c.com), Dallas Foundation, Communities Foundation of Texas, 
and North Texas nonprofit boards for jobs.

TARGET PROFILE:
- Transitioning from 14+ years corporate relationship management to nonprofit sector
- CVA certification (Certified in Volunteer Administration)
- Expert in stakeholder engagement, community building, program development
- $60,000-$90,000 salary range
- Mission-driven focus on education, youth development, community impact

NONPROFIT FOCUS (Priority):
- Education nonprofits (K-12, higher ed support, scholarship programs)
- Youth development organizations (mentorship, after-school, enrichment)
- Community foundations and development
- Volunteer management and coordination
- Program management and community engagement
- Donor relations and development (relationship-focused, NOT cold fundraising)

TARGET ROLES:
- Program Manager / Program Director
- Development Manager (relationship-based)
- Community Engagement Manager
- Volunteer Coordinator / Manager
- Donor Relations Manager
- Major Gifts Officer (relationship-focused)
- Strategic Partnerships Manager

LOCATION: Dallas-Fort Worth Metroplex + Hybrid opportunities
POSTED: Last 7 days only
EXCLUDE: Entry-level, part-time only, unpaid internships, pure grant writing

Find at least 10 jobs, rank by match score (0-100).

OUTPUT FORMAT (STRICT):
================================

SECTION 1: ALL JOB LISTINGS
================================

TOP 5 MATCHES (TIER 1) - FULL DETAILS
---
Provide ALL 8 core data points for positions 1-5:

1. **[Job Title]** - [Organization Name]
   - Match Score: [0-100]
   - Salary: [Range or "Not listed"]
   - Location: [City, State / Hybrid]
   - Organization Overview: [500-800 chars about mission, programs, funding, impact]
   - Role Insights: [400-600 chars from Responsibilities section]
   - Key Requirements: [300-400 chars from Requirements section]
   - URL: [Direct application link]

[Repeat exact format for positions 2-5]

POSITIONS 6-10 (TIER 2) - CORE DETAILS
---
Provide same 8 core data points for positions 6-10.

6. **[Job Title]** - [Organization Name]
   [Same 8 data points]

[Repeat for positions 7-10]

ALL OTHER MATCHES (TIER 3) - BASIC LIST
---
For positions 11+, provide ONLY 3 data points:

11. **[Job Title]** - [Organization] - Match: [Score]
12. **[Job Title]** - [Organization] - Match: [Score]
[Continue for all remaining jobs found]



SECTION 2: DEEP DIVE ANALYSIS (TIER 1 & TIER 2)
===============================================

For Jobs 1-5 (TIER 1), provide ALL DATA FIELDS below (Applied Research + Application Pack).
For Jobs 6-10 (TIER 2), provide ONLY the "APPLIED RESEARCH" fields.

---START_JOB_X---
TITLE: [Exact Title]
COMPANY: [Company]
TIER: [1 or 2]

# === APPLIED RESEARCH (TIER 1 & 2) ===
---COMPANY_OVERVIEW---
[Financial Health, Funding, Mission, Values, Press]

---ROLE_INSIGHTS---
[Team structure, Core Responsibilities, Success Metrics, Tech Stack]

---KEY_REQUIREMENTS---
[Must-haves vs Nice-to-haves]

---SALARY_INTEL---
[Market rate, leverage, negotiation data]

---APPLICATION_STRATEGY---
[Resume keywords, specific angles]

---RED_FLAGS---
[Turnover, risks, funding issues]

---CULTURAL_FIT---
[Pace, style, values alignment]

---COMPETITIVE_LANDSCAPE---
[Market position, competitors]

---SKILLS_GAP_ANALYSIS---
[Missing skills & how to pivot]

---NETWORK_LEVERAGE---
[Who to contact, alumni, board]

---DECISION_TIMELINE---
[Urgency, hiring speed]

---CAREER_TRAJECTORY---
[Exit opps, growth path]

# === APPLICATION PACK (TIER 1 ONLY - JOBS 1-5) ===
---RESUME_KEYWORDS---
[ATS keyword list]

---RESUME_SUMMARY---
[Tailored summary text]

---COVER_LETTER_DRAFT---
[Full tailored draft]

---WHY_ME_BULLETS---
[3-5 value prop bullets]

---WHY_THEM_BULLETS---
[3-5 company interest bullets]

---INTERVIEW_PREP---
[15 Qs: 5 Behavioral, 5 Technical, 5 Cultural]

---STAR_HOOKS---
[3 Story ideas]

---TALKING_POINTS---
[Negotiation strategy]

---QUESTIONS_TO_ASK---
[3-5 smart questions for them]

---RECRUITER_EMAIL---
[Outreach draft]

---THANK_YOU_EMAIL---
[Post-interview draft]

---30_60_90_PLAN---
[High-level outline]

---END_JOB_X---

"""

    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "system",
                "content": "You are Strategic Match AI for nonprofit careers. Provide STRUCTURED 3-tier job analysis with EXACT format markers. Emphasize mission alignment, community impact, and corporate-to-nonprofit transition strengths."
            },
            {
                "role": "user",
                "content": search_query
            }
        ],
        "temperature": 0.3,
        "return_citations": True,
        "search_recency_filter": "week"
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        result = response.json()
        return result['choices'][0]['message']['content']
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return None

def main():
    