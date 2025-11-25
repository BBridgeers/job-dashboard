import os
import requests
import json
import datetime

API_KEY = os.environ.get("PERPLEXITY_API_KEY")
if not API_KEY:
    raise ValueError("❌ PERPLEXITY_API_KEY not found.")

TODAY = datetime.datetime.now().strftime("%Y-%m-%d")
OUTPUT_FILE = f"job_search_results/job_search_nonprofit_sonar_{TODAY}.txt"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

SYSTEM_PROMPT = """You are a specialized Non-Profit Executive Recruiter.
Find mid-level roles where corporate polish is a "value add".
Output STRICTLY as a JSON list of objects. No conversational text.

SCORING RUBRIC (0-100):
1. Responsibilities Alignment (40pts): Does the role involve program management, community engagement, or strategic partnerships?
2. Experience/Role Title Match (30pts): Target roles INCLUDE BUT ARE NOT LIMITED TO: Program Manager, Senior Program Manager, Program Director, Program Implementation Manager, Community Engagement Manager, Community Outreach Manager, Community Partnerships Manager, Volunteer Engagement Manager, Member Services Manager, Member Engagement Manager, Stakeholder Engagement Manager, Donor Relations Manager, Donor Success Manager, Development Manager, Philanthropy Manager, Partnership Development Manager, Corporate Partnerships Manager, Impact Manager, Grants & Partnerships Manager, Education & Training Manager, Learning & Development Manager, Adoption & Enablement Manager, Client Services Manager, Community Success Manager, Program Success Manager, Nonprofit Partnerships Manager.
3. Skills/Tools (15pts): Corporate Relations, Major Gifts, Strategic Planning, Stakeholder Management.
4. Culture/Location (10pts): Dallas-Ft. Worth or Remote. Mission-driven (Community, Health, Education).
5. Salary Range (5pts): >$60k.

CRITICAL: AUTO-REJECT (Score = 0) any entry-level "Canvasser", "Street Team", or "Door-to-Door" roles.
"""

SEARCH_QUERY = """
Find 30-50 mid-level Program, Engagement, or Development roles in Non-Profits (Dallas/TX or Remote).
Focus on: Community Impact, Children, Homeless, Hunger, Education, Youth, or Health.
Comp: $60k+. Posted in the last 14 days.
EXCLUDE: "Canvasser", "Door-to-Door", "Street Team", "Entry Level", "Intern".

PRIORITY SOURCES (Prioritize listings from these domains):
1. Major Nonprofit Boards: Idealist.org, Work for Good, Philanthropy News Digest, Chronicle of Philanthropy.
2. DFW Regional (CRITICAL): DFW501c.com, jobs.thecnm.org (Center for Nonprofit Management), TANO, DFW Nonprofit Resource Center, AFP DFW, YNPN DFW.
3. University Boards: SMU, UT Dallas, UNT, TCU Career Centers.
4. Google Search Logic: site:.org ("Careers" OR "Jobs") ("Dallas" OR "Fort Worth" OR "Arlington" OR "Irving" OR "Plano").

For EACH job, you MUST extract or generate the following 30 fields in a valid JSON object:

1. title (Job Title)
2. company (Company Name)
3. location (City/State or Remote)
4. match_score (0-100 based on fit for mission-driven leadership)
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
23. why_me_bullets (3 arguments for why I am the perfect fit)
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
    print(f"🔍 Scanning Nonprofit Jobs...")

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

        print(f"✅ Nonprofit Search Complete. Saved to {OUTPUT_FILE}")

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
