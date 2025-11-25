#!/usr/bin/env python3
# job_search_agent_corporate_sonar_pro.py
"""
DFW Corporate/Tech Job Search Agent (Sonar-Powered)
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

class CorporateJobSearchAgent:
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
        """Use sonar-pro to search for jobs"""
        print("🔍 Searching for corporate/tech jobs in DFW...")

        search_prompt = """
        Find the latest tech and corporate job openings in Dallas-Fort Worth (DFW) area that match this profile:

        BACKGROUND:
        - 10+ years sales/customer success/account management experience
        - Strong tech background (education technology, SaaS, CRM platforms)
        - Proven track record with enterprise clients and revenue growth
        - Skilled at stakeholder engagement, relationship building, and strategic planning

        TARGET ROLES:
        - Customer Success Manager/Director
        - Account Executive/Account Manager
        - Sales Director/VP
        - Business Development roles
        - Client Relationship Management

        SEARCH CRITERIA:
        - Posted within last 7 days
        - Dallas, TX or Fort Worth, TX or Remote (US)
        - Salary $80K+ preferred
        - Focus on: tech companies, SaaS, enterprise software, education technology

        For EACH job found (aim for 10-15), provide:
        - Job title and company
        - Match score (0-100) based on profile
        - Salary range (if available)
        - Location details
        - Brief company description
        - Direct application URL
        - Key requirements
        - Why it's a good match

        Focus on jobs from: Indeed, LinkedIn, ZipRecruiter, Glassdoor, and company career pages.
        """

        payload = {
            "model": "sonar-pro",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a job search expert specializing in tech and corporate roles. Provide accurate, up-to-date job listings with detailed information."
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
        """Use sonar-reasoning for deep analysis of top jobs"""
        print("🧠 Analyzing top matches with sonar-reasoning...")

        analysis_prompt = f"""
        Analyze these job search results and provide strategic insights:

        {jobs_data}

        For the TOP 3 highest-match jobs, provide:
        1. Detailed company analysis (funding, growth, reputation, recent news)
        2. Role-specific insights (team structure, growth path, challenges)
        3. Salary negotiation intelligence (market rates, company comp philosophy)
        4. Cultural fit assessment
        5. Application strategy (key resume points to emphasize, cover letter angle)
        6. Interview preparation tips specific to this company/role
        7. Potential red flags or concerns
        8. Competitive landscape (similar roles at other companies)

        Also provide:
        - Overall DFW job market analysis for these roles
        - Trending skills and technologies
        - Strategic recommendations for application prioritization
        """

        payload = {
            "model": "sonar-reasoning",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a career strategist with deep knowledge of the tech industry, hiring practices, and job market trends."
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
        filename = self.output_dir / f'job_search_corporate_sonar_{timestamp}.txt'

        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# DFW CORPORATE/TECH JOB SEARCH RESULTS\n")
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
        print("🚀 DFW CORPORATE/TECH JOB SEARCH AGENT")
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
            print("   1. Review the top 3 matches")
            print("   2. Customize resume for each position")
            print("   3. Draft tailored cover letters")
            print("   4. Apply within 24-48 hours of posting")
            print("\n")

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            raise

if __name__ == "__main__":
    agent = CorporateJobSearchAgent()
    agent.run()
