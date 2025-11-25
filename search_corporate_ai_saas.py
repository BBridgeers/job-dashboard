import os
import requests
import json
import datetime

# CONFIGURATION
API_KEY = os.environ.get("PERPLEXITY_API_KEY")
if not API_KEY:
    raise ValueError("❌ PERPLEXITY_API_KEY not found in environment variables.")

TODAY = datetime.datetime.now().strftime("%Y-%m-%d")
OUTPUT_FILE = f"job_search_results/job_search_corporate_sonar_{TODAY}.txt"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# THE RICH DATA PROMPT
SYSTEM_PROMPT = """You are a high-level Executive Recruiter Agent. 
Your goal is to find live, high-value job openings and extract structured, actionable data for a candidate.
You must output your answer STRICTLY as a JSON list of objects. No markdown, no conversational text.

SCORING RUBRIC (0-100):
1. Responsibilities Alignment (40pts): Does the day-to-day work match the candidate's expertise in driving retention, expansion, and strategic relationships?
2. Experience/Role Title Match (30pts): Target roles INCLUDE BUT ARE NOT LIMITED TO: Customer Success Manager, Senior Customer Success Manager, Customer Success Specialist, Customer Success Associate, Customer Success Consultant, Customer Success Lead, Client Success Manager, Client Success Specialist, Client Services Manager, Client Relationship Manager, Customer Experience Manager, Customer Engagement Manager, Customer Account Manager, Customer Retention Manager, Adoption Manager, Renewal Manager, Expansion Manager, Account Manager (existing accounts/growth), Strategic Account Manager, Key Account Manager, Major Account Manager, Named Account Manager, National Account Manager, Enterprise Account Manager, Global Account Manager, Partner Account Manager, Customer Account Executive, Channel Account Manager, Strategic Relationship Manager, Strategic Partnerships Manager, Partnership Manager, Partner Success Manager, Partner Success Specialist, Partner Engagement Manager, Partner Enablement Manager, Partner Relationship Manager, Ecosystem Manager, Alliance Manager, Channel Manager, Channel Development Manager, Implementation Specialist, Implementation Consultant, Implementation Manager, Client Implementation Manager, Software Implementation Specialist, Technical Implementation Consultant, Customer Onboarding Specialist, Onboarding Consultant, Onboarding Manager, Deployment Specialist, Delivery Consultant, Engagement Manager, Solutions Consultant, Solutions Delivery Manager, Training Specialist, Training Consultant, Training Manager, Enablement Specialist, Customer Enablement Manager, Learning & Development Specialist, Instructional Specialist, Adoption Consultant, User Enablement Manager, Education Services Manager, Customer Education Specialist, Customer Growth Manager, Value Manager, Business Value Consultant, Customer Outcomes Manager, Retention Specialist, Renewals Manager, Expansion Specialist, Customer Value Manager, Engagement Specialist.
3. Skills/Tools (15pts): Salesforce, Gainsight, MEDDIC, Churn Prediction, Python/AI.
4. Culture/Location (10pts): Remote or Dallas-Ft. Worth. High-growth/Innovation culture.
5. Salary Range (5pts): >$90k.

CRITICAL: AUTO-REJECT (Score = 0) any "SDR", "BDR", "Sales Development Representative", or "Business Development Representative" roles.
"""

SEARCH_QUERY = """
Find 30-50 high-paying Customer Success, Account Management, or Strategic Partnership roles in AI/SaaS companies (Remote or Dallas/TX).
Focus on: High-growth Series B+ or Public Tech companies.
Comp: $90k+. Only include roles posted in the last 14 days.
EXCLUDE: "Sales Development", "Business Development Representative", "SDR", "BDR", "Inside Sales".

PRIORITY SOURCES (Prioritize listings from these domains):
1. Major Boards: LinkedIn, Indeed, Glassdoor, Wellfound (AngelList).
2. Tech/SaaS Specific: Built In, Remote.co, We Work Remotely, SaaS Jobs, CrunchBoard, Stack Overflow.
3. ATS Direct Links: site:lever.co, site:greenhouse.io, site:myworkdayjobs.com, site:ashbyhq.com.
4. Diversity/Niche: Tech Ladies, PowerToFly, The Muse.
5. Google Search Logic: (site:lever.co OR site:greenhouse.io OR site:ashbyhq.com) ("Customer Success" OR "Account Manager") ("Dallas" OR "Remote") -intitle:engineer.

For EACH job, you MUST extract or generate the following 30 fields in a valid JSON object:

1. title (Job Title)
2. company (Company Name)
3. location (City/State or Remote)
4. match_score (0-100 based on high-growth SaaS fit)
5. listing_url (Direct link to the job post)
6. application_url (Direct link to apply - if different, otherwise same as listing)
7. summary_bullets (3 key highlights of the role)
8. company_overview (Brief 2-sentence company description)
9. role_insights (What success looks like in this role)
10. key_requirements (Top 3 hard skills needed)
11. salary_intel (Estimated range or mentioned comp)
12. application_strategy (One specific tip to stand out)
13. red_flags (Any potential downsides or risks)
14. cultural_fit (Describe the vibe)
15. competitive_landscape (Who are their main rivals?)
16. skills_gap (One skill the candidate might need to brush up on)
17. network_leverage (Who to reach out to?)
18. decision_timeline (Urgent? Rolling? Estimated timeline)
19. career_trajectory (Where does this role lead?)
20. resume_keywords (5 ATS keywords to include)
21. resume_summary (A tailored 2-sentence summary for the CV)
22. cover_letter (A draft opening paragraph for the cover letter)
23. why_me_bullets (3arguments for why I am the perfect fit)
24. why_them_bullets (3 reasons why I want to join THEM)
25. interview_prep (3 likely interview questions)
26. star_hooks (A suggestion for a STAR story to tell)
27. talking_points (2 strategic topics to discuss with leadership)
28. questions_to_ask (2 smart questions to ask the hiring manager)
29. recruiter_email (Guess the format: firstname.lastname@company.com)
30. plan_30_60_90 (A rough 30-60-90 day plan outline)

OUTPUT FORMAT:
[
  {
    "title": "...",
    "company": "...",
    ... (all fields)
  },
  ...
]
"""

def validate_json_content(content):
    """Validate that the content is valid JSON"""
    try:
        parsed = json.loads(content)
        if not isinstance(parsed, list):
            raise ValueError("JSON should be a list of job objects")
        print(f"✅ Successfully parsed {len(parsed)} jobs.")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ JSON Decode Error: {e}")
        return False
    except ValueError as e:
        print(f"❌ Validation Error: {e}")
        return False

def run_search():
    print(f"🔍 Scanning Corporate Jobs via Perplexity...")

    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": SEARCH_QUERY}
        ]
    }

    try:
        print("📡 Sending request to Perplexity API...")
        response = requests.post("https://api.perplexity.ai/chat/completions", json=payload, headers=HEADERS, timeout=120)
        response.raise_for_status()
        
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        print("✅ Received response from API")

        # Basic cleanup to ensure it's pure JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        # Validate JSON
        if not validate_json_content(content):
            print("⚠️ Warning: AI output might not be valid JSON. Saving raw output anyway.")

        # Save to file
        os.makedirs("job_search_results", exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✅ Search Complete. Saved to {OUTPUT_FILE}")

    except requests.exceptions.Timeout:
        print("❌ Error: Request timed out. Try again later.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Network Error: {e}")
    except KeyError as e:
        print(f"❌ API Response Error: Missing expected field {e}")
        print(f"   Response: {data if 'data' in locals() else 'No response data'}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    run_search()
