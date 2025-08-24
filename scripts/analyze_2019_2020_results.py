#!/usr/bin/env python
"""
Analyze test results from 2019-2020 season tests
"""

import csv
from pathlib import Path

def analyze():
    # Find the latest 2019-2020 CSV file
    results_dir = Path("test_results")
    csv_files = sorted(results_dir.glob("last_page_matches_2019_2020*.csv"))
    
    if not csv_files:
        print("No 2019-2020 test results found")
        return
    
    latest_file = csv_files[-1]
    print(f"📊 Analyzing: {latest_file.name}")
    print("=" * 80)
    
    with open(latest_file, 'r') as f:
        reader = csv.DictReader(f)
        results = list(reader)
    
    # Statistics
    total = len(results)
    successful = [r for r in results if r['status'] == 'SUCCESS']
    failed = [r for r in results if r['status'] == 'FAILED']
    
    print(f"Total Tests: {total}/13")
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    print(f"Success Rate: {len(successful)/total*100:.1f}%")
    
    print("\n" + "=" * 80)
    print("DETAILED RESULTS (2019-2020 Complete Seasons)")
    print("-" * 80)
    print(f"{'Country':<15} {'Last Page':<10} {'Matches':<15} {'Status':<10}")
    print("-" * 80)
    
    for r in results:
        status = "✅" if r['status'] == 'SUCCESS' else "❌"
        last_page = r['last_page_num'] if r['last_page_num'] else '0'
        matches = r['matches_on_last_page'] if r['matches_on_last_page'] else '0'
        print(f"{r['country']:<15} {last_page:<10} {matches:<15} {status}")
    
    # Check 3+ pages requirement
    print("\n" + "=" * 80)
    print("📊 PAGINATION ANALYSIS (Requirement: 3+ pages)")
    print("-" * 80)
    
    meets_requirement = [r for r in successful if int(r['last_page_num']) >= 3]
    under_requirement = [r for r in successful if int(r['last_page_num']) < 3]
    
    print(f"✅ Meets requirement (3+ pages): {len(meets_requirement)} leagues")
    for r in meets_requirement:
        print(f"   • {r['country']}: {r['last_page_num']} pages")
    
    if under_requirement:
        print(f"\n⚠️ Under requirement (<3 pages): {len(under_requirement)} leagues")
        for r in under_requirement:
            print(f"   • {r['country']}: {r['last_page_num']} pages")
    
    if failed:
        print(f"\n❌ Failed tests: {len(failed)} leagues")
        for r in failed:
            print(f"   • {r['country']}: {r['error_message'][:50]}...")
    
    print("\n" + "=" * 80)
    print("🎯 SUMMARY")
    print("-" * 80)
    print(f"Leagues with 3+ pages: {len(meets_requirement)}/{total}")
    print(f"Success rate for 3+ pages requirement: {len(meets_requirement)/total*100:.1f}%")

if __name__ == "__main__":
    analyze()