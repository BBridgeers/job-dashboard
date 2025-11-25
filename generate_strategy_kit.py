import sqlite3
import requests
import json
import os
import sys
from datetime import datetime

# CONFIGURATION
DB_PATH = 'jobs.db'
PROFILE_PATH = 'profile.txt'
API_KEY = os.environ.get("PERPLEXITY_API_KEY")

if not API_KEY:
    print("❌ Error: PERPLEXITY_API_KEY not found.")
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

SYSTEM_PROMPT = """You are a Career Strategy AI. 
Your goal is to generate a "Strategy Kit" for a specific job opportunity based on the candidate's profile.
You must output STRICTLY valid JSON.

INPUT DATA:
1. Candidate Profile (Blake)
2. Job Description

REQUIRED OUTPUT (JSON Object):
{
  "experience_translation": {
    "summary": "High-level pitch of why Blake fits",
    "key_matches": ["Match 1", "Match 2"],
    "narrative_strategy": "How to frame the 14 years experience"
  },
  "gap_analysis": {
    "hard_gaps": ["Gap 1", "Gap 2"],
    "soft_gaps": ["Gap 1"],
    "unhappiness_predictors": ["Potential frustration 1"],
    "mitigation_strategies": ["Strategy 1"]
  },
  "precision_match": {
    "responsibilities_score": 0-40,
    "role_match_score": 0-30,
    "skills_score": 0-15,
    "culture_score": 0-10,
    "salary_score": 0-5,
    "total_score": 0-100,
    "reasoning": "Brief explanation"
  },
  "resume_customization": {
    "swap_instructions": [
      {"original": "Old bullet...", "new": "New bullet...", "reason": "Why"}
    ],
    "keywords_to_add": ["Keyword 1", "Keyword 2"]
  },
  "cover_letter": {
    "news_hook": "Recent company news to mention",
    "opening_paragraph": "Draft text...",
    "body_paragraphs": "Draft text..."
  },
  "networking": {
    "hiring_manager_search": "LinkedIn search query...",
    "peer_search": "LinkedIn search query...",
    "outreach_template": "Draft message..."
  },
  "risk_mitigation": {
    "interview_probes": ["Question to ask 1", "Question to ask 2"],
    "red_flag_checks": ["What to look for"]
  }
}
"""

def get_profile():
    if not os.path.exists(PROFILE_PATH):
        return "Candidate Profile: 14 Years SaaS Customer Success Experience. Strategic Account Management."
    with open(PROFILE_PATH, 'r', encoding='utf-8') as f:
        return f.read()

def get_job(job_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
    job = c.fetchone()
    conn.close()
    return dict(job) if job else None

def save_kit(job_id, data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO strategy_kits (job_id, data) 
        VALUES (?, ?)
    """, (job_id, json.dumps(data)))
    conn.commit()
    conn.close()
    print(f"✅ Strategy Kit saved for Job ID {job_id}")

def generate_kit(job_id):
    job = get_job(job_id)
    if not job:
        print(f"❌ Job ID {job_id} not found.")
        return

    print(f"🧠 Generating Strategy Kit for: {job['title']} at {job['company']}...")
    profile = get_profile()
    
    # Construct User Prompt
    user_prompt = f"""
    CANDIDATE PROFILE:
    {profile}

    JOB DESCRIPTION:
    Title: {job['title']}
    Company: {job['company']}
    Description: {job.get('description', '')}
    Requirements: {job.get('requirements', '')}
    Role Insights: {job.get('role_insights', '')}
    
    TASK:
    Generate the full Strategy Kit JSON based on the schema. 
    For the "Cover Letter", perform a search for recent news about {job['company']} if possible, or simulate a generic news hook if live search is unavailable.
    """

    payload = {
        "model": "sonar-reasoning-pro",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
    }

    try:
        response = requests.post("https://api.perplexity.ai/chat/completions", json=payload, headers=HEADERS, timeout=180)
        response.raise_for_status()
        
        content = response.json()["choices"][0]["message"]["content"]
        
        # Clean JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        data = json.loads(content)
        save_kit(job_id, data)
        
    except Exception as e:
        print(f"❌ Error generating kit: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_strategy_kit.py <job_id>")
        sys.exit(1)
    
    job_id = sys.argv[1]
    generate_kit(job_id)
