#!/usr/bin/env python
"""
Analyze and display test results from last page collection tests
"""

import csv
from pathlib import Path
from datetime import datetime
import sys

def analyze_results():
    """Analyze test results from CSV files"""
    
    # Find all result CSV files
    results_dir = Path("test_results")
    csv_files = sorted(results_dir.glob("last_page_matches_2021*.csv"))
    
    if not csv_files:
        print("❌ No test result files found")
        return
    
    # Use the latest file
    latest_file = csv_files[-1]
    print(f"📊 Analyzing results from: {latest_file.name}")
    print("=" * 80)
    
    # Read and analyze results
    with open(latest_file, 'r') as f:
        reader = csv.DictReader(f)
        results = list(reader)
    
    if not results:
        print("❌ No test results in file")
        return
    
    # Calculate statistics
    total_tests = len(results)
    successful = [r for r in results if r['status'] == 'SUCCESS']
    failed = [r for r in results if r['status'] == 'FAILED']
    
    success_count = len(successful)
    failed_count = len(failed)
    success_rate = (success_count / total_tests * 100) if total_tests > 0 else 0
    
    # Display overall summary
    print("📈 OVERALL SUMMARY")
    print("-" * 40)
    print(f"Total Tests Run: {total_tests}/13")
    print(f"Successful: {success_count} ✅")
    print(f"Failed: {failed_count} ❌")
    print(f"Success Rate: {success_rate:.1f}%")
    
    # Calculate timing statistics
    if successful:
        durations = [float(r['test_duration_sec']) for r in successful if r['test_duration_sec']]
        if durations:
            avg_duration = sum(durations) / len(durations)
            print(f"Average Test Duration: {avg_duration:.2f}s")
            print(f"Total Execution Time: {sum(durations):.2f}s")
    
    print("\n" + "=" * 80)
    print("📋 DETAILED RESULTS BY LEAGUE")
    print("-" * 40)
    
    # Display detailed results
    print(f"{'Country':<15} {'League':<35} {'Season':<12} {'Last Page':<10} {'Matches':<10} {'Duration':<10} {'Status':<10}")
    print("-" * 120)
    
    for r in results:
        country = r['country'][:15]
        league = r['league_id'][:35]
        season = r['season']
        last_page = r['last_page_num'] if r['last_page_num'] else '0'
        matches = r['matches_on_last_page'] if r['matches_on_last_page'] else '0'
        duration = f"{float(r['test_duration_sec']):.1f}s" if r['test_duration_sec'] else 'N/A'
        status = "✅" if r['status'] == 'SUCCESS' else "❌"
        
        print(f"{country:<15} {league:<35} {season:<12} {last_page:<10} {matches:<10} {duration:<10} {status:<10}")
    
    # Show failed tests details
    if failed:
        print("\n" + "=" * 80)
        print("❌ FAILED TESTS DETAILS")
        print("-" * 40)
        for r in failed:
            print(f"\n{r['country']} - {r['league_id']}:")
            print(f"  Error: {r['error_message']}")
    
    # Show interesting findings
    print("\n" + "=" * 80)
    print("🔍 INTERESTING FINDINGS")
    print("-" * 40)
    
    # Leagues with multiple pages
    multi_page = [r for r in successful if int(r['last_page_num']) > 1]
    if multi_page:
        print("\nLeagues with multiple pages:")
        for r in multi_page:
            print(f"  • {r['country']}: {r['last_page_num']} pages, {r['matches_on_last_page']} matches on last page")
    else:
        print("\n⚠️ All successful leagues had only 1 page of results")
    
    # Leagues with most matches on last page
    if successful:
        sorted_by_matches = sorted(successful, key=lambda x: int(x['matches_on_last_page']), reverse=True)
        print("\nTop 3 leagues by matches on last page:")
        for r in sorted_by_matches[:3]:
            print(f"  • {r['country']}: {r['matches_on_last_page']} matches")
    
    # Missing leagues
    all_leagues = [
        "belgium", "switzerland", "england", "italy", "spain", "sweden", 
        "france", "portugal", "norway", "denmark", "germany", "netherlands", "scotland"
    ]
    tested_leagues = [r['country'] for r in results]
    missing = [l for l in all_leagues if l not in tested_leagues]
    
    if missing:
        print(f"\n⚠️ Missing leagues (not tested): {', '.join(missing)}")
    
    print("\n" + "=" * 80)
    print(f"📁 Full results saved in: {latest_file}")
    print(f"📁 Individual logs in: test_logs/last_page_2021/")
    print("=" * 80)

if __name__ == "__main__":
    analyze_results()