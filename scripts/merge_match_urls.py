#!/usr/bin/env python3
"""
Merge recollected match URLs with existing collection
"""

import csv
import json
import logging
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Directories
ORIGINAL_DIR = Path("match_urls_collection/by_league")
RECOLLECTION_DIR = Path("match_urls_recollection")
MERGED_DIR = Path("match_urls_merged/by_league")

# Recollected leagues
RECOLLECTED_LEAGUES = {
    "switzerland": ["2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024"],
    "scotland": ["2019-2020", "2020-2021", "2021-2022"],
    "netherlands": ["2019-2020", "2020-2021", "2023-2024"],
    "france": ["2021-2022", "2022-2023", "2023-2024"],
    "spain": ["2019-2020", "2021-2022"]
}

def read_csv_urls(file_path):
    """Read match URLs from CSV file"""
    urls = []
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                urls.append(row)
    return urls

def write_csv_urls(file_path, data, fieldnames):
    """Write match URLs to CSV file"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def merge_league_data():
    """Merge recollected data with original collection"""
    
    logger.info("="*70)
    logger.info("MERGING MATCH URL COLLECTIONS")
    logger.info("="*70)
    
    merge_summary = {}
    total_original = 0
    total_recollected = 0
    total_merged = 0
    
    # First, add recollected data for missing seasons
    for country, seasons in RECOLLECTED_LEAGUES.items():
        country_dir = ORIGINAL_DIR / country
        country_dir.mkdir(parents=True, exist_ok=True)
        
        for season in seasons:
            # Check if recollection file exists
            recollection_file = RECOLLECTION_DIR / f"{country}_{season.replace('-', '_')}.csv"
            if recollection_file.exists():
                logger.info(f"Adding recollected data: {country} {season}")
    
    # Process each league
    for country_dir in ORIGINAL_DIR.iterdir():
        if not country_dir.is_dir():
            continue
            
        country = country_dir.name
        league_summary = {
            "original": 0,
            "recollected": 0,
            "merged": 0,
            "seasons": {}
        }
        
        logger.info(f"\nProcessing {country.upper()}...")
        
        # Process all seasons (both original and recollected)
        all_seasons = set()
        
        # Get seasons from original files
        for season_file in country_dir.glob("*.csv"):
            all_seasons.add(season_file.stem)
        
        # Add seasons from recollection if this country was recollected
        if country in RECOLLECTED_LEAGUES:
            all_seasons.update(RECOLLECTED_LEAGUES[country])
        
        # Process each season
        for season in sorted(all_seasons):
            season_file = country_dir / f"{season}.csv"
            
            # Read original data if it exists
            if season_file.exists():
                original_data = read_csv_urls(season_file)
                league_summary["original"] += len(original_data)
                total_original += len(original_data)
            else:
                original_data = []
            
            # Check if this season was recollected
            if country in RECOLLECTED_LEAGUES and season in RECOLLECTED_LEAGUES[country]:
                # Use recollected data - the files already have underscores
                recollection_file = RECOLLECTION_DIR / f"{country}_{season.replace('-', '_')}.csv"
                if recollection_file.exists():
                    recollected_data = read_csv_urls(recollection_file)
                    league_summary["recollected"] += len(recollected_data)
                    total_recollected += len(recollected_data)
                    
                    # Use recollected data for merge
                    merged_data = recollected_data
                    logger.info(f"  {season}: Replaced {len(original_data)} with {len(recollected_data)} recollected matches")
                    
                    league_summary["seasons"][season] = {
                        "original": len(original_data),
                        "recollected": len(recollected_data),
                        "action": "replaced"
                    }
                else:
                    # Recollection file not found, use original
                    merged_data = original_data
                    logger.warning(f"  {season}: Recollection file not found, using original {len(original_data)} matches")
                    league_summary["seasons"][season] = {
                        "original": len(original_data),
                        "action": "kept_original"
                    }
            else:
                # Not recollected, use original data
                merged_data = original_data
                logger.info(f"  {season}: Keeping original {len(original_data)} matches")
                league_summary["seasons"][season] = {
                    "original": len(original_data),
                    "action": "kept_original"
                }
            
            # Save merged data
            merged_file = MERGED_DIR / country / f"{season}.csv"
            if merged_data:
                write_csv_urls(
                    merged_file, 
                    merged_data,
                    fieldnames=["league", "season", "match_url"]
                )
                league_summary["merged"] += len(merged_data)
                total_merged += len(merged_data)
        
        merge_summary[country] = league_summary
    
    # Save merge summary
    summary_file = MERGED_DIR / "merge_summary.json"
    summary_file.parent.mkdir(parents=True, exist_ok=True)
    
    final_summary = {
        "timestamp": datetime.now().isoformat(),
        "totals": {
            "original_total": total_original,
            "recollected_total": total_recollected,
            "merged_total": total_merged,
            "improvement": total_merged - (total_original - total_recollected)
        },
        "leagues": merge_summary
    }
    
    with open(summary_file, 'w') as f:
        json.dump(final_summary, f, indent=2)
    
    # Print final summary
    logger.info("\n" + "="*70)
    logger.info("MERGE COMPLETE")
    logger.info("="*70)
    logger.info(f"Original Collection: {total_original:,} matches")
    logger.info(f"Recollected: {total_recollected:,} matches")
    logger.info(f"Final Merged: {total_merged:,} matches")
    logger.info(f"Net Improvement: +{total_merged - total_original + total_recollected:,} matches")
    
    # League breakdown
    logger.info("\nBy League:")
    for country, summary in merge_summary.items():
        if summary["recollected"] > 0:
            logger.info(f"\n{country.upper()}:")
            logger.info(f"  Original: {summary['original']} matches")
            logger.info(f"  Recollected: {summary['recollected']} matches")
            logger.info(f"  Final: {summary['merged']} matches")
            
            for season, details in summary["seasons"].items():
                if details["action"] == "replaced":
                    improvement = details.get("recollected", 0) - details["original"]
                    logger.info(f"    {season}: {details['original']} → {details.get('recollected', 0)} (+{improvement})")
    
    logger.info(f"\n📁 Merged data saved to: {MERGED_DIR}")
    logger.info(f"📊 Summary saved to: {summary_file}")
    
    return final_summary

def verify_merge():
    """Verify the merged data"""
    
    logger.info("\n" + "="*70)
    logger.info("VERIFYING MERGED DATA")
    logger.info("="*70)
    
    all_leagues_ok = True
    
    for country_dir in MERGED_DIR.iterdir():
        if not country_dir.is_dir() or country_dir.name == "by_league":
            continue
        
        country = country_dir.name
        season_files = list(country_dir.glob("*.csv"))
        
        if not season_files:
            logger.error(f"❌ {country}: No season files found")
            all_leagues_ok = False
            continue
        
        total_matches = 0
        for season_file in season_files:
            urls = read_csv_urls(season_file)
            total_matches += len(urls)
        
        if total_matches > 0:
            logger.info(f"✅ {country}: {len(season_files)} seasons, {total_matches:,} total matches")
        else:
            logger.error(f"❌ {country}: No matches found")
            all_leagues_ok = False
    
    if all_leagues_ok:
        logger.info("\n✅ All leagues verified successfully!")
    else:
        logger.warning("\n⚠️ Some leagues have issues")
    
    return all_leagues_ok

if __name__ == "__main__":
    # Perform merge
    summary = merge_league_data()
    
    # Verify results
    verify_merge()
    
    # Print instructions
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("1. Review the merged data in: match_urls_merged/")
    print("2. Check merge_summary.json for detailed statistics")
    print("3. Use merged data for odds collection with:")
    print("   python src/main.py scrape_historic --match_links match_urls_merged/...")