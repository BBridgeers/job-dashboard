#!/usr/bin/env python3

import re

txt_file = 'job_search_nonprofit_sonar_2025-11-18.txt'
with open(txt_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Find SECTION 2
section2_match = re.search(r'SECTION 2[:\s]+STRATEGIC ANALYSIS(.+)', content, re.DOTALL | re.IGNORECASE)
if not section2_match:
    print("❌ No SECTION 2 found!")
    exit()

print(f"✅ Found SECTION 2\n")

# Split by ## X. Job Title format
job_blocks = re.split(r'##\s+(\d+)\.\s+(.+?)\s+\(Match Score:\s+(\d+)\)', section2_match.group(1))

print(f"Found {(len(job_blocks)-1)//4} jobs\n")

# Check first job for sections
if len(job_blocks) >= 4:
    job_num = job_blocks[1]
    job_title = job_blocks[2].strip()
    block = job_blocks[4]

    print(f"JOB #{job_num}: {job_title}")
    print(f"Block has {len(block)} chars\n")
    print("Looking for **Header** sections...")

    headers = re.findall(r'\*\*([A-Z][^*]+)\*\*', block)
    print(f"Found {len(headers)} section headers:")
    for h in headers[:8]:
        print(f"  - {h}")

    if len(headers) >= 6:
        print("\n✅ This file has FULL analysis format!")
        print("Parser should extract 6/6 fields")
    else:
        print(f"\n⚠️ Only {len(headers)} sections found")
