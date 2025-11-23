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
You must output your answer STRICTLY as a JSON list of objects. No markdown, no conversational text."""

SEARCH_QUERY = """
Find 5 high-paying Customer Success or Account Executive roles in AI/SaaS companies (Remote or Dallas/TX).
Focus on: OpenAI, Anthropic, Stripe, Databricks, or similar high-growth tech.
Only include roles posted in the last 14 days.

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
14. cultural_fit (Describe the vibe: e.g., "Fast-paced, chaotic")
15. competitive_landscape (Who are their main rivals?)
16. skills_gap (One skill the candidate might need to brush up on)
17. network_leverage (Who to reach out to? e.g., "Connect with VP of Success")
18. decision_timeline (Urgent? Rolling? Estimated.)
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
29. recruiter_email (Guess the format: e.g., firstname.lastname@company.com)
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
        response = requests.post("https://api.perplexity.ai/chat/completions", json=payload, headers=HEADERS)
        response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        # Basic cleanup to ensure it's pure JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        # Validate JSON
        try:
            parsed = json.loads(content)
            print(f"✅ Successfully parsed {len(parsed)} jobs.")
        except json.JSONDecodeError:
            print("⚠️ Warning: AI output might not be valid JSON. Saving raw output anyway.")

        # Save to file
        os.makedirs("job_search_results", exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✅ Search Complete. Saved to {OUTPUT_FILE}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_search()
