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

    section_1_prompt = """
    For EACH listing, you MUST include:
    1. **Job Title**
    2. **Company Name**
    3. **Match Score** (0-100)
    4. **Salary** (Provided or Estimated)
    5. **Location**
    6. **URL**
    7. **SUMMARY_BULLETS**: 3 concise bullets summarizing the role.
    8. **FIT_BULLETS**: 3 concise bullets on why this fits the candidate profile.
    """

    section_2_prompt = """
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

    search_query = f"""
    Search Idealist.org, Chronicle of Philanthropy Jobs, NonprofitJobs.org,
    Bridgespan Career Center, OpportunityKnocks, Nonprofit Talent, AFP Career Center,
    Council on Foundations Jobs, Philanthropy News Digest Jobs, Indeed (nonprofit),
    LinkedIn (nonprofit sector), Glassdoor (nonprofit companies), VolunteerMatch,
    American Red Cross Careers, American Heart Association Careers, United Way Career Centers,
    Feeding America Careers, SchoolSpring, MinistryWatch Jobs, Social Impact Jobs,
    Changemakers Job Board, Work for Good, Foundation List Jobs, GuideStar Job Board.

    TARGET PROFILE:
    - 14+ years program management, community engagement, & relationship building
    - Experience with volunteers, grants, development, and strategic partnerships
    - Passion for social impact and mission-driven work
    - $60,000-$120,000 salary range
    - DFW Metroplex (Dallas, Fort Worth, Plano) or REMOTE

    ROLES:
    - Program Director/Manager
    - Community Engagement Director
    - Volunteer Director
    - Development Director
    - Strategic Partnerships Manager

    {section_1_prompt}

    {section_2_prompt}

    CRITICAL RULES:
    1. Prioritize recently posted jobs (last 7 days).
    2. Do NOT invent jobs. Only list real, active listings found.
    3. Follow the exact output format with "---HEADER---" separators.
    """

    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "You are an expert nonprofit career agent. Find high-impact matches."},
            {"role": "user", "content": search_query}
        ]
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    print("🔍 Scanning 24+ Nonprofit Job Boards...")
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        content = response.json()['choices'][0]['message']['content']

        # Save to file
        output_dir = Path("job_search_results")
        output_dir.mkdir(exist_ok=True)
        filename = output_dir / f"job_search_nonprofit_sonar_{datetime.now().strftime('%Y-%m-%d')}.txt"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✅ Nonprofit Search Complete. Saved to {filename}")
        return str(filename)
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return None

if __name__ == "__main__":
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        try:
            with open("Perplexity_Corp_Job_Search.txt", "r") as f:
                api_key = f.read().strip()
        except:
            print("❌ API Key not found.")
            exit(1)

    search_nonprofit_jobs(api_key)
