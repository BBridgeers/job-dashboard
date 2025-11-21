#!/usr/bin/env python3

"""
DEBUG Parser - Shows exactly what's in each job block
"""

import re

txt_file = 'job_search_corporate_sonar_2025-11-17.txt'
with open(txt_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Find SECTION 2
section2_match = re.search(r'SECTION 2[:\s]+STRATEGIC ANALYSIS(.+)', content, re.DOTALL | re.IGNORECASE)
if not section2_match:
    print("❌ No SECTION 2 found!")
    exit()

section2_content = section2_match.group(1)
print(f"✅ Found SECTION 2 ({len(section2_content)} chars)\n")

# Split by ## X. Job Title format
job_blocks = re.split(r'##\s+(\d+)\.\s+(.+?)\s+\(Match Score:\s+(\d+)\)', section2_content)

print(f"Total blocks after split: {len(job_blocks)}\n")

# Process first job only to see format
if len(job_blocks) >= 4:
    job_num = job_blocks[1]
    job_title = job_blocks[2].strip()
    match_score = job_blocks[3]
    block = job_blocks[4]

    print("=" * 70)
    print(f"JOB #{job_num}: {job_title} (Score: {match_score})")
    print("=" * 70)
    print(f"Block has {len(block)} characters\n")
    print("FIRST 1000 CHARACTERS OF BLOCK:")
    print("-" * 70)
    print(block[:1000])
    print("-" * 70)
    print("\n\nSEARCHING FOR SECTION HEADERS...")

    # Try different header patterns
    patterns = [
        (r'####\s+([^\n]+)', '#### Header'),
        (r'\*\*([A-Z][^*]+)\*\*', '**Header**'),
        (r'###\s+([^\n]+)', '### Header'),
        (r'##\s+([^\n]+)', '## Header'),
    ]

    for pattern, name in patterns:
        headers = re.findall(pattern, block)
        if headers:
            print(f"\n{name} found ({len(headers)} matches):")
            for h in headers[:10]:  # Show first 10
                print(f"  - {h}")
