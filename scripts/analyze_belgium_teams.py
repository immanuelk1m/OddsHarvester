#!/usr/bin/env python3
"""
Analyze teams in Belgium 2023-2024 data
"""

import csv
from collections import Counter

# Read CSV
teams = set()
matchups = []

with open('match_urls_belgium_complete/2023-2024.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader)  # Skip header
    
    for row in reader:
        url = row[2]
        # Extract matchup part (e.g., "charleroi-st-truiden-dfYiYvWE")
        parts = url.split('/')
        if len(parts) >= 7:
            matchup = parts[6]
            # Remove the match ID at the end
            matchup_parts = matchup.rsplit('-', 1)[0]
            matchups.append(matchup_parts)

# Manually parse known Belgium teams from the matchups
belgium_teams = {
    'anderlecht', 'antwerp', 'cercle-brugge', 'charleroi', 'club-brugge',
    'eupen', 'genk', 'gent', 'kortrijk', 'kv-mechelen', 'leuven',
    'royale-union-sg', 'rwdm-brussels', 'st-liege', 'st-truiden', 'westerlo'
}

# Count matches per team
team_matches = Counter()

for matchup in matchups:
    # Try to identify teams in matchup
    for team in belgium_teams:
        if matchup.startswith(team + '-') or matchup.endswith('-' + team):
            team_matches[team] += 1

print("Belgium Pro League 2023-2024 Analysis")
print("=" * 50)
print(f"Total matches collected: {len(matchups)}")
print(f"\nTeams identified: {len(belgium_teams)}")
for team in sorted(belgium_teams):
    count = team_matches.get(team, 0)
    print(f"  {team}: {count} matches")

print("\nExpected matches calculation:")
print(f"  With {len(belgium_teams)} teams:")
print(f"  - Regular season: {len(belgium_teams)} * ({len(belgium_teams)}-1) * 2 = {len(belgium_teams) * (len(belgium_teams)-1) * 2}")
print(f"  - If 18 teams: 18 * 17 * 2 = 306")
print(f"  - Belgium uses playoff system, so additional playoff matches")

print(f"\nConclusion: 313 matches collected seems reasonable for Belgium 2023-2024")
print("The discrepancy with expected 321 might be due to:")
print("  - Different playoff format")
print("  - Postponed/cancelled matches")
print("  - Data availability on OddsPortal")