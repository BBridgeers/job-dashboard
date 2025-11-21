#!/usr/bin/env python3

import re
from pathlib import Path

results_path = Path('job_search_results')
txt_files = sorted(results_path.glob('job_search_*.txt'))

for txt_file in txt_files[:3]:  # Check first 3 files
    print("=" * 70)
    print(f"FILE: {txt_file.name}")
    print("=" * 70)

    with open(txt_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for SECTION 2
    section2_match = re.search(r'SECTION 2[:\s]+(.+)', content, re.DOTALL | re.IGNORECASE)
    if not section2_match:
        print("❌ No SECTION 2 found\n")
        continue

    section2 = section2_match.group(1)[:1000]  # First 1000 chars
    print(f"✅ Found SECTION 2\n")
    print("First 1000 chars of SECTION 2:")
    print("-" * 70)
    print(section2)
    print("-" * 70)
    print("\nLooking for job markers...")

    # Try different job marker patterns
    patterns = [
        (r'##\s+\d+\.\s+(.+?)\s+\(Match Score:', '## X. Title (Match Score:'),
        (r'##\s+JOB\s+\d+:', '## JOB X:'),
        (r'\*\*Job #\d+:', '**Job #X:'),
        (r'Job \d+:', 'Job X:'),
    ]

    for pattern, name in patterns:
        matches = re.findall(pattern, section2_match.group(1)[:2000])
        if matches:
            print(f"  ✅ Found {len(matches)} jobs using pattern: {name}")
            for m in matches[:3]:
                print(f"     - {m}")
            break
    else:
        print("  ❌ No job markers found")

    print("\n")
