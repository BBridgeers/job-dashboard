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
Find impactful leadership roles (Director, VP, Manager) in Mission-Driven organizations.
Output STRICTLY as a JSON list of objects. No conversational text."""

SEARCH_QUERY = """
Find 5 Director/Manager level roles in Non-Profits (Dallas/TX or Remote).
Focus on: Food Banks, Education, Youth Development, Arts, or Healthcare foundations.
Comp: $80k+. Posted in the last 14 days.

For EACH job, generate these 30 fields in valid JSON:

1. title
2. company
3. location
4. match_score (Fit for mission-driven leadership)
5. listing_url
6. application_url
7. summary_bullets (Mission impact summary)
8. company_overview
9. role_insights
10. key_requirements
11. salary_intel
12. application_strategy
13. red_flags
14. cultural_fit
15. competitive_landscape
16. skills_gap
17. network_leverage
18. decision_timeline
19. career_trajectory
20. resume_keywords
21. resume_summary
22. cover_letter
23. why_me_bullets
24. why_them_bullets
25. interview_prep
26. star_hooks
27. talking_points
28. questions_to_ask
29. recruiter_email
30. plan_30_60_90

OUTPUT FORMAT:
[
  {
    "title": "...",
    ...
  }
]
"""

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
        response = requests.post("https://api.perplexity.ai/chat/completions", json=payload, headers=HEADERS)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]

        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        os.makedirs("job_search_results", exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✅ Nonprofit Search Complete. Saved to {OUTPUT_FILE}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_search()
