#!/usr/bin/env python3
# job_search_agent_nonprofit_sonar_pro.py
"""
DFW Nonprofit Job Search Agent (Sonar-Powered)
Uses sonar-pro for search + sonar-reasoning for deep analysis
"""

import os
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Import Google Drive uploader
try:
    from gdrive_uploader import upload_to_gdrive
    GDRIVE_ENABLED = True
except ImportError:
    GDRIVE_ENABLED = False
    print("⚠️  Google Drive upload disabled (gdrive_uploader.py not found)")

load_dotenv()

class NonprofitJobSearchAgent:
    def __init__(self):
        self.api_key = os.getenv('PERPLEXITY_API_KEY')
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY not found in .env file")

        self.base_url = 'https://api.perplexity.ai/chat/completions'
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        # Ensure output directory exists
        self.output_dir = Path('job_search_results')
        self.output_dir.mkdir(exist_ok=True)

    def search_jobs(self):
        """Use sonar-pro to search for nonprofit jobs"""
        print("🔍 Searching for nonprofit jobs in DFW...")

        search_prompt = """
        Find the latest nonprofit job openings in Dallas-Fort Worth (DFW) area that match this profile:

        BACKGROUND:
        - 10+ years experience in sales, customer success, and account management
        - Strong relationship-building and stakeholder engagement skills
        - Proven track record with revenue growth and client retention
        - Tech-savvy with experience in CRM platforms and education technology

        TARGET ROLES:
        - Development Director/Manager
        - Fundraising Manager
        - Donor Relations Manager
        - Major Gifts Officer
        - Grants Manager
        - Nonprofit Operations/Strategy roles

        FOCUS AREAS:
        - Education nonprofits
        - Youth development organizations
        - Social services
        - Arts & culture organizations
        - Health & human services

        SEARCH CRITERIA:
        - Posted within last 7 days
        - Dallas, TX or Fort Worth, TX
        - Salary $60K+ preferred
        - Mid to senior level positions

        For EACH job found (aim for 10-15), provide:
        - Job title and organization
        - Match score (0-100) based on profile
        - Salary range (if available)
        - Organization mission and impact
        - Brief role description
        - Direct application URL
        - Key qualifications
        - Why it's a good match for someone transitioning from corporate to nonprofit

        Focus on jobs from: Idealist, Indeed, LinkedIn, Chronicle of Philanthropy, nonprofit job boards, and organization websites.
        """

        payload = {
            "model": "sonar-pro",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a nonprofit career expert specializing in development and fundraising roles. Provide accurate, up-to-date job listings with mission-focused details."
                },
                {
                    "role": "user",
                    "content": search_prompt
                }
            ],
            "temperature": 0.2,
            "max_tokens": 4000
        }

        response = requests.post(self.base_url, headers=self.headers, json=payload)
        response.raise_for_status()

        return response.json()['choices'][0]['message']['content']

    def analyze_jobs(self, jobs_data):
        """Use sonar-reasoning for deep analysis of top nonprofit jobs"""
        print("🧠 Analyzing top nonprofit matches with sonar-reasoning...")

        analysis_prompt = f"""
        Analyze these nonprofit job search results and provide strategic insights:

        {jobs_data}

        For the TOP 3 highest-match jobs, provide:
        1. Organization analysis (mission, impact, funding sources, financial health)
        2. Role-specific insights (fundraising goals, donor base, team structure)
        3. Salary and benefits context (nonprofit compensation norms, total rewards)
        4. Cultural fit and values alignment assessment
        5. Transition strategy (corporate-to-nonprofit resume translation)
        6. Interview preparation (nonprofit-specific questions and frameworks)
        7. Potential challenges (funding uncertainty, work-life balance)
        8. Growth and impact opportunities

        Also provide:
        - DFW nonprofit landscape overview
        - Transferable skills from corporate to nonprofit
        - Networking strategies for nonprofit sector entry
        - Key certifications or knowledge areas (CFRE, grant writing, etc.)
        """

        payload = {
            "model": "sonar-reasoning",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a nonprofit career strategist with deep knowledge of development, fundraising, and the philanthropic sector."
                },
                {
                    "role": "user",
                    "content": analysis_prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 8000
        }

        response = requests.post(self.base_url, headers=self.headers, json=payload)
        response.raise_for_status()

        return response.json()['choices'][0]['message']['content']

    def save_results(self, jobs_data, analysis_data):
        """Save results to file and optionally upload to Google Drive"""
        timestamp = datetime.now().strftime('%Y-%m-%d')
        filename = self.output_dir / f'job_search_nonprofit_sonar_{timestamp}.txt'

        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# DFW NONPROFIT JOB SEARCH RESULTS\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p CST')}\n")
            f.write("Models: sonar-pro (search) + sonar-reasoning (analysis)\n")
            f.write("="*80 + "\n\n")

            f.write("SECTION 1: JOB LISTINGS\n")
            f.write("="*80 + "\n")
            f.write(jobs_data)
            f.write("\n\n")

            f.write("SECTION 2: STRATEGIC ANALYSIS\n")
            f.write("="*80 + "\n")
            f.write(analysis_data)

        print(f"\n✅ Results saved to: {filename}")

        # Upload to Google Drive if enabled
        if GDRIVE_ENABLED:
            print("\n📤 Uploading to Google Drive...")
            try:
                if upload_to_gdrive(filename):
                    print("✅ Successfully uploaded to Google Drive!")
                else:
                    print("⚠️  Google Drive upload failed (check logs)")
            except Exception as e:
                print(f"⚠️  Google Drive upload error: {str(e)}")

        return filename

    def run(self):
        """Execute full job search workflow"""
        print("\n" + "="*80)
        print("🚀 DFW NONPROFIT JOB SEARCH AGENT")
        print("="*80 + "\n")

        try:
            # Step 1: Search for jobs
            jobs_data = self.search_jobs()

            # Step 2: Analyze top matches
            analysis_data = self.analyze_jobs(jobs_data)

            # Step 3: Save results
            filename = self.save_results(jobs_data, analysis_data)

            print("\n" + "="*80)
            print("✅ JOB SEARCH COMPLETE!")
            print("="*80)
            print(f"\n📄 Results: {filename}")
            print("\n💡 Next steps:")
            print("   1. Review organization missions and impact")
            print("   2. Translate corporate experience to nonprofit language")
            print("   3. Research donor trends and funding sources")
            print("   4. Prepare mission-driven cover letters")
            print("\n")

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            raise

if __name__ == "__main__":
    agent = NonprofitJobSearchAgent()
    agent.run()
