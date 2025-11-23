#!/usr/bin/env python3

"""
Strategic Match - Corporate/Tech Job Search (Enhanced)
AI/Automation, SaaS, EdTech, Fintech, Healthtech focus
20+ specialized job boards
"""

import os
import requests
from datetime import datetime
from pathlib import Path

def search_corporate_jobs(api_key):
    """Execute enhanced corporate job search with 3-tier structure"""

    url = "https://api.perplexity.ai/chat/completions"

    # ENHANCED CORPORATE SEARCH QUERY
    search_query = """
Search LinkedIn, Indeed, Glassdoor, Built In, AngelList/Wellfound, Dice, 
We Work Remotely, ZipRecruiter, Remote.co, The Muse, Ladders, FlexJobs, 
RepVue, Monster, CareerBuilder, SimplyHired, Stack Overflow Jobs, Remotive, 
YC Jobs, Levels.fyi Jobs, Hired, and CrunchBoard for jobs.

TARGET PROFILE:
- 14+ years B2B SaaS customer success & account management experience
- Expert in retention, expansion, relationship building
- NOT hunter sales / cold outbound roles
- $75,000-$150,000 salary range
- DFW Metroplex (Dallas, Fort Worth, Plano, Frisco) + Remote opportunities

INDUSTRY FOCUS (Priority):
- B2B SaaS (customer success platforms, enterprise software)
- AI/Automation platforms (RPA, workflow automation, AI tools)
- Education technology (EdTech)
- Financial technology (Fintech)
- Healthcare technology (Healthtech)
- Series A+ funded startups with strong product-market fit

TARGET ROLES:
- Customer Success Director/VP
- Strategic Account Manager
- Customer Experience Director
- Enterprise Relationship Manager
- AI Solutions Manager
- Automation Success Manager

LOCATION: Dallas-Fort Worth Metroplex + Remote (US-based) + Hybrid
POSTED: Last 7 days only
EXCLUDE: Pure hunter/quota SDR roles, cold outbound, entry-level IC

Find at least 10 jobs, rank by match score (0-100).

OUTPUT FORMAT (STRICT):
================================

SECTION 1: ALL JOB LISTINGS
================================

TOP 5 MATCHES (TIER 1) - FULL DETAILS
---
Provide ALL 8 core data points for positions 1-5:

1. **[Job Title]** - [Company Name]
   - Match Score: [0-100]
   - Salary: [Range or "Not listed"]
   - Location: [City, State / Remote]
   - Company Overview: [500-800 chars from listing/company site]
   - Role Insights: [400-600 chars from Responsibilities section]
   - Key Requirements: [300-400 chars from Requirements section]
   - URL: [Direct application link]

[Repeat exact format for positions 2-5]

POSITIONS 6-10 (TIER 2) - CORE DETAILS
---
Provide same 8 core data points for positions 6-10.

6. **[Job Title]** - [Company Name]
   [Same 8 data points]

[Repeat for positions 7-10]

ALL OTHER MATCHES (TIER 3) - BASIC LIST
---
For positions 11+, provide ONLY 3 data points:

11. **[Job Title]** - [Company] - Match: [Score]
12. **[Job Title]** - [Company] - Match: [Score]
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
                "content": "You are Strategic Match AI. Provide STRUCTURED 3-tier job analysis with EXACT format markers. Focus on AI/Automation, SaaS, EdTech sectors."
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
    