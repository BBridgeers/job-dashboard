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


SECTION 2: STRATEGIC ANALYSIS (TOP 5 ONLY)
================================
For ONLY the TOP 5 jobs, provide deep strategic intelligence:

---START_JOB_1---
TITLE: [Exact job title from SECTION 1]
COMPANY: [Organization name]
MATCH_SCORE: [0-100]
TIER: 1

---COMPANY_OVERVIEW---
[500-800 chars: Mission, programs, funding sources, community impact, organizational size, reputation, board composition, financial health]

---ROLE_INSIGHTS---
[400-600 chars: Team structure, reporting lines, day-to-day activities, program ownership, community engagement approach]

---KEY_REQUIREMENTS---
[300-400 chars: Must-have skills, experience, certifications (CVA relevance), cultural competencies, mission alignment]

---INTERVIEW_PREP---
[400-500 chars: Common nonprofit interview questions, mission alignment questions, scenario-based questions, presentation expectations]

---SALARY_INTEL---
[400-500 chars: Nonprofit salary ranges for role, total compensation including benefits, negotiation approach for mission-driven orgs]

---APPLICATION_STRATEGY---
[400-500 chars: Resume keywords emphasizing impact, cover letter mission connection, volunteer experience to highlight, corporate-to-nonprofit transition positioning]

---RED_FLAGS---
[250-350 chars: Warning signs about funding instability, turnover, mission drift, unrealistic expectations for nonprofit roles]

---CULTURAL_FIT---
[400-500 chars: Work style in nonprofit vs corporate, pace differences, values-driven culture, community engagement expectations, work-life integration]

---COMPETITIVE_LANDSCAPE---
[300-400 chars: Similar roles at other DFW nonprofits, what makes this organization unique, alternative opportunities in the sector]

---SKILLS_GAP_ANALYSIS---
[350-450 chars: Corporate skills that transfer well, nonprofit-specific skills to develop, how to position corporate experience as strength]

---NETWORK_LEVERAGE---
[250-350 chars: DFW nonprofit networks to join, CVA community connections, board members to research, nonprofit conferences/events]

---DECISION_TIMELINE---
[200-300 chars: Nonprofit hiring timelines (often slower), when to follow up, board approval processes, start date flexibility]

---CAREER_TRAJECTORY---
[300-400 chars: Growth path in nonprofit sector, leadership opportunities, how this role builds nonprofit career, long-term impact potential]

---WHY_THIS_ROLE---
[400-500 chars: Mission alignment with your values, corporate-to-nonprofit transition fit, community impact potential, career fulfillment factors]

---FULL_DESCRIPTION---
[600-800 chars: Complete role responsibilities, community engagement activities, program management scope, success metrics for nonprofit context]
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
- Focus on mission alignment and community impact in analysis
- Maintain ---START_JOB_X--- and ---END_JOB_X--- boundaries
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
    """Run nonprofit job search"""

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

    print("🔍 Running NONPROFIT/MISSION search...")
    print("   Focus: Education, Youth, Community Development")
    print("   Sources: 24+ nonprofit job boards (including DFW-specific)")
    print("")

    result = search_nonprofit_jobs(api_key)

    if result:
        filename = output_dir / f"job_search_nonprofit_sonar_{timestamp}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# STRATEGIC MATCH - DFW NONPROFIT JOBS\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')} CST\n")
            f.write(f"Search Type: Nonprofit\n")
            f.write(f"Model: sonar-pro (3-tier structured)\n")
            f.write(f"Focus: Education, Youth Development, Community Impact\n")
            f.write(f"Sources: 24+ nonprofit-specific boards\n")
            f.write("=" * 80 + "\n\n")
            f.write(result)

        print(f"✅ Saved: {filename}")
        print(f"   Ready for: python3 migrate_structured.py")
    else:
        print("❌ Search failed")

if __name__ == "__main__":
    main()
