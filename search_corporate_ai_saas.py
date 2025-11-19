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


SECTION 2: STRATEGIC ANALYSIS (TOP 5 ONLY)
================================
For ONLY the TOP 5 jobs, provide deep strategic intelligence:

---START_JOB_1---
TITLE: [Exact job title from SECTION 1]
COMPANY: [Company name]
MATCH_SCORE: [0-100]
TIER: 1

---COMPANY_OVERVIEW---
[500-800 chars: Company stage, funding, market position, reputation, growth trajectory, tech stack, competitors, AI/automation focus if applicable]

---ROLE_INSIGHTS---
[400-600 chars: Team structure, reporting lines, day-to-day, P&L ownership, decision authority, travel requirements]

---KEY_REQUIREMENTS---
[300-400 chars: Must-have skills, years experience, certifications, technical proficiencies, soft skills]

---INTERVIEW_PREP---
[400-500 chars: Common questions for this role type, what they evaluate, presentation tips, case study prep, technical assessments]

---SALARY_INTEL---
[400-500 chars: Market rates, negotiation leverage, total comp breakdown (base/bonus/equity), benefits to expect]

---APPLICATION_STRATEGY---
[400-500 chars: Resume keywords to emphasize, cover letter angle, referral opportunities, ATS optimization, when to apply]

---RED_FLAGS---
[250-350 chars: Warning signs, Glassdoor concerns, high turnover indicators, unrealistic expectations]

---CULTURAL_FIT---
[400-500 chars: Work style, pace, values alignment, remote/hybrid culture, team dynamics, leadership style]

---COMPETITIVE_LANDSCAPE---
[300-400 chars: Similar roles at other companies, what makes this unique, alternative opportunities]

---SKILLS_GAP_ANALYSIS---
[350-450 chars: What you have that matches, what you're missing, how to position gaps as growth opportunities]

---NETWORK_LEVERAGE---
[250-350 chars: LinkedIn connections, alumni network, industry contacts, recruiters to engage, informational interview targets]

---DECISION_TIMELINE---
[200-300 chars: Urgency to apply, follow-up schedule, expected response times, offer deadline expectations]

---CAREER_TRAJECTORY---
[300-400 chars: How this advances your path, next role after this, skills you'll build, 3-5 year outlook]

---WHY_THIS_ROLE---
[400-500 chars: Compelling reasons for YOUR background, unique fit factors, risk/reward assessment]

---FULL_DESCRIPTION---
[600-800 chars: Complete responsibilities, day-to-day activities, success metrics, what "great" looks like]
---END_JOB_1---

---START_JOB_2---
TIER: 1
[Same 15-section structure]
---END_JOB_2---

---START_JOB_3---
TIER: 1
[Same 15-section structure]
---END_JOB_3---

---START_JOB_4---
TIER: 1
[Same 15-section structure]
---END_JOB_4---

---START_JOB_5---
TIER: 1
[Same 15-section structure]
---END_JOB_5---

CRITICAL RULES:
- Use EXACT markers: ---SECTION_NAME---
- NO extra formatting (no **, no ##, just plain text after markers)
- All 15 sections MUST be present for each job
- Stay within character limits
- Maintain ---START_JOB_X--- and ---END_JOB_X--- boundaries
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
    """Run corporate job search"""

    # Load API key
    try:
        with open('credentials.json', 'r') as f:
            import json
            creds = json.load(f)
            api_key = creds['perplexity_api_key']
    except FileNotFoundError:
        print("❌ credentials.json not found!")
        return

    # Ensure output directory exists
    output_dir = Path('job_search_results')
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d")

    print("🔍 Running CORPORATE/TECH search...")
    print("   Focus: AI/Automation, SaaS, EdTech, Fintech, Healthtech")
    print("   Sources: 20+ job boards")
    print("")

    result = search_corporate_jobs(api_key)

    if result:
        filename = output_dir / f"job_search_corporate_sonar_{timestamp}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# STRATEGIC MATCH - DFW CORPORATE/TECH JOBS\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')} CST\n")
            f.write(f"Search Type: Corporate\n")
            f.write(f"Model: sonar-pro (3-tier structured)\n")
            f.write(f"Focus: AI/Automation, SaaS, EdTech, Fintech, Healthtech\n")
            f.write(f"Sources: 20+ job boards\n")
            f.write("=" * 80 + "\n\n")
            f.write(result)

        print(f"✅ Saved: {filename}")
        print(f"   Ready for: python3 migrate_structured.py")
    else:
        print("❌ Search failed")

if __name__ == "__main__":
    main()
