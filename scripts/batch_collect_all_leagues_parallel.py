#!/usr/bin/env python3
"""
Parallel Batch Collection Script for Match URLs
Collects match URLs from 13 European leagues (2019-2024/25 seasons) using 4 parallel workers
"""

import asyncio
import csv
import json
import logging
import multiprocessing as mp
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import time
import traceback

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.odds_portal_scraper import OddsPortalScraper
from src.core.playwright_manager import PlaywrightManager
from src.core.browser_helper import BrowserHelper
from src.core.odds_portal_market_extractor import OddsPortalMarketExtractor
from src.core.sport_market_registry import SportMarketRegistrar
from src.utils.setup_logging import setup_logger

# Define all leagues and their seasons
LEAGUES_CONFIG = {
    "england": {
        "id": "england-premier-league",
        "name": "England Premier League",
        "seasons": ["2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024", "2024-2025"]
    },
    "spain": {
        "id": "spain-laliga",
        "name": "Spain La Liga",
        "seasons": ["2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024", "2024-2025"]
    },
    "italy": {
        "id": "italy-serie-a",
        "name": "Italy Serie A",
        "seasons": ["2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024", "2024-2025"]
    },
    "germany": {
        "id": "germany-bundesliga",
        "name": "Germany Bundesliga",
        "seasons": ["2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024", "2024-2025"]
    },
    "france": {
        "id": "france-ligue-1",
        "name": "France Ligue 1",
        "seasons": ["2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024", "2024-2025"]
    },
    "netherlands": {
        "id": "netherlands-eredivisie",
        "name": "Netherlands Eredivisie",
        "seasons": ["2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024", "2024-2025"]
    },
    "portugal": {
        "id": "portugal-liga-portugal",
        "name": "Portugal Liga Portugal",
        "seasons": ["2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024", "2024-2025"]
    },
    "belgium": {
        "id": "belgium-jupiler-pro-league",
        "name": "Belgium Jupiler Pro League",
        "seasons": ["2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024", "2024-2025"]
    },
    "scotland": {
        "id": "scotland-premiership",
        "name": "Scotland Premiership",
        "seasons": ["2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024", "2024-2025"]
    },
    "switzerland": {
        "id": "switzerland-super-league",
        "name": "Switzerland Super League",
        "seasons": ["2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024", "2024-2025"]
    },
    "denmark": {
        "id": "denmark-superliga",
        "name": "Denmark Superliga",
        "seasons": ["2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024", "2024-2025"]
    },
    "norway": {
        "id": "norway-eliteserien",
        "name": "Norway Eliteserien",
        # Norway uses single year format
        "seasons": ["2019", "2020", "2021", "2022", "2023", "2024"]
    },
    "sweden": {
        "id": "sweden-allsvenskan",
        "name": "Sweden Allsvenskan",
        # Sweden uses single year format
        "seasons": ["2019", "2020", "2021", "2022", "2023", "2024"]
    }
}

# Base output directory
OUTPUT_DIR = Path("match_urls_collection")


def setup_directories():
    """Create necessary directory structure"""
    directories = [
        OUTPUT_DIR,
        OUTPUT_DIR / "by_league",
        OUTPUT_DIR / "combined",
        OUTPUT_DIR / "logs",
        OUTPUT_DIR / "progress"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Create league-specific directories
    for country, config in LEAGUES_CONFIG.items():
        league_dir = OUTPUT_DIR / "by_league" / country
        league_dir.mkdir(parents=True, exist_ok=True)


def setup_worker_logger(worker_id: int):
    """Setup logger for each worker process"""
    log_file = OUTPUT_DIR / "logs" / f"worker_{worker_id}.log"
    
    logger = logging.getLogger(f"Worker-{worker_id}")
    logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    logger.handlers = []
    
    # File handler
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.INFO)
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter('[%(asctime)s] [Worker-%(name)s] %(levelname)s: %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger


async def collect_single_season(
    country: str,
    league_id: str,
    league_name: str,
    season: str,
    worker_id: int
) -> Dict:
    """Collect URLs for a single league-season combination"""
    
    logger = setup_worker_logger(worker_id)
    result = {
        "country": country,
        "league_id": league_id,
        "league_name": league_name,
        "season": season,
        "status": "pending",
        "match_count": 0,
        "error": None,
        "duration": 0
    }
    
    start_time = time.time()
    
    try:
        logger.info(f"Starting collection: {league_name} - {season}")
        
        # Register markets (required for scraper initialization)
        SportMarketRegistrar.register_all_markets()
        
        # Initialize components
        playwright_manager = PlaywrightManager()
        browser_helper = BrowserHelper()
        market_extractor = OddsPortalMarketExtractor(browser_helper=browser_helper)
        
        scraper = OddsPortalScraper(
            playwright_manager=playwright_manager,
            browser_helper=browser_helper,
            market_extractor=market_extractor,
            preview_submarkets_only=True
        )
        
        # Start playwright
        await scraper.start_playwright(headless=True)
        
        # Build URL
        from src.core.url_builder import URLBuilder
        base_url = URLBuilder.get_historic_matches_url(
            sport="football",
            league=league_id,
            season=season
        )
        
        logger.info(f"URL: {base_url}")
        
        # Navigate to page
        page = scraper.playwright_manager.page
        await page.goto(base_url, timeout=30000, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        # Get pagination info
        pages_to_scrape = await scraper._get_pagination_info(page=page, max_pages=None)
        logger.info(f"Found {len(pages_to_scrape)} pages")
        
        # Collect match URLs
        all_match_urls = []
        
        if len(pages_to_scrape) == 1:
            # Single page
            logger.info("Extracting from single page...")
            
            await browser_helper.scroll_until_loaded(
                page=page,
                timeout=30,
                scroll_pause_time=2,
                max_scroll_attempts=3,
                content_check_selector="div[class*='eventRow']"
            )
            
            match_links = await scraper.extract_match_links(page=page)
            all_match_urls = match_links
            
        else:
            # Multiple pages
            logger.info(f"Collecting from {len(pages_to_scrape)} pages...")
            match_links = await scraper._collect_match_links(
                base_url=base_url,
                pages_to_scrape=pages_to_scrape,
                max_matches=None
            )
            all_match_urls = match_links
        
        # Save to CSV
        if all_match_urls:
            output_file = OUTPUT_DIR / "by_league" / country / f"{season}.csv"
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["league", "season", "match_url"])
                
                for url in all_match_urls:
                    writer.writerow([league_name, season, url])
            
            logger.info(f"✅ SUCCESS: {league_name} - {season}: {len(all_match_urls)} matches")
            result["status"] = "success"
            result["match_count"] = len(all_match_urls)
        else:
            logger.warning(f"⚠️ No matches found: {league_name} - {season}")
            result["status"] = "no_data"
        
        await scraper.stop_playwright()
        
    except Exception as e:
        logger.error(f"❌ FAILED: {league_name} - {season}: {str(e)}")
        logger.error(traceback.format_exc())
        result["status"] = "failed"
        result["error"] = str(e)
    
    finally:
        result["duration"] = round(time.time() - start_time, 2)
        
        # Save progress
        progress_file = OUTPUT_DIR / "progress" / f"worker_{worker_id}_progress.json"
        progress_data = []
        
        if progress_file.exists():
            with open(progress_file, 'r') as f:
                progress_data = json.load(f)
        
        progress_data.append(result)
        
        with open(progress_file, 'w') as f:
            json.dump(progress_data, f, indent=2)
    
    return result


def worker_process(worker_id: int, tasks: List[Tuple]) -> List[Dict]:
    """Worker process function"""
    logger = setup_worker_logger(worker_id)
    logger.info(f"Worker {worker_id} started with {len(tasks)} tasks")
    
    results = []
    
    for i, (country, league_id, league_name, season) in enumerate(tasks, 1):
        logger.info(f"Task {i}/{len(tasks)}: {league_name} - {season}")
        
        # Run async collection
        result = asyncio.run(collect_single_season(
            country, league_id, league_name, season, worker_id
        ))
        
        results.append(result)
        
        # Small delay between tasks
        time.sleep(2)
    
    logger.info(f"Worker {worker_id} completed all tasks")
    return results


def distribute_tasks(num_workers: int = 4) -> List[List[Tuple]]:
    """Distribute league-season combinations across workers"""
    all_tasks = []
    
    for country, config in LEAGUES_CONFIG.items():
        for season in config["seasons"]:
            all_tasks.append((
                country,
                config["id"],
                config["name"],
                season
            ))
    
    # Distribute tasks evenly
    tasks_per_worker = len(all_tasks) // num_workers
    remainder = len(all_tasks) % num_workers
    
    distributed = []
    start = 0
    
    for i in range(num_workers):
        end = start + tasks_per_worker + (1 if i < remainder else 0)
        distributed.append(all_tasks[start:end])
        start = end
    
    return distributed


def generate_summary(all_results: List[Dict]):
    """Generate collection summary"""
    summary_file = OUTPUT_DIR / "collection_summary.txt"
    
    total_matches = sum(r["match_count"] for r in all_results)
    successful = sum(1 for r in all_results if r["status"] == "success")
    failed = sum(1 for r in all_results if r["status"] == "failed")
    no_data = sum(1 for r in all_results if r["status"] == "no_data")
    
    with open(summary_file, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("MATCH URL COLLECTION SUMMARY\n")
        f.write("=" * 70 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write(f"Total Tasks: {len(all_results)}\n")
        f.write(f"Successful: {successful}\n")
        f.write(f"Failed: {failed}\n")
        f.write(f"No Data: {no_data}\n")
        f.write(f"Total Matches Collected: {total_matches:,}\n\n")
        
        # Group by league
        f.write("BY LEAGUE:\n")
        f.write("-" * 50 + "\n")
        
        for country, config in LEAGUES_CONFIG.items():
            league_results = [r for r in all_results if r["country"] == country]
            league_matches = sum(r["match_count"] for r in league_results)
            f.write(f"\n{config['name']}:\n")
            
            for r in league_results:
                status_icon = "✅" if r["status"] == "success" else "❌"
                f.write(f"  {r['season']}: {r['match_count']} matches {status_icon}\n")
            
            f.write(f"  Total: {league_matches} matches\n")
        
        # Failed tasks
        if failed > 0:
            f.write("\n" + "=" * 50 + "\n")
            f.write("FAILED TASKS:\n")
            for r in all_results:
                if r["status"] == "failed":
                    f.write(f"  - {r['league_name']} {r['season']}: {r['error']}\n")
    
    print(f"\n✅ Summary saved to: {summary_file}")
    print(f"📊 Total matches collected: {total_matches:,}")


def combine_all_csvs():
    """Combine all individual CSV files into one"""
    combined_file = OUTPUT_DIR / "combined" / "all_matches_combined.csv"
    
    with open(combined_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(["league", "season", "match_url"])
        
        for country in LEAGUES_CONFIG.keys():
            league_dir = OUTPUT_DIR / "by_league" / country
            
            for csv_file in sorted(league_dir.glob("*.csv")):
                with open(csv_file, 'r', encoding='utf-8') as infile:
                    reader = csv.reader(infile)
                    next(reader)  # Skip header
                    
                    for row in reader:
                        writer.writerow(row)
    
    print(f"✅ Combined CSV saved to: {combined_file}")


def main():
    """Main execution function"""
    print("=" * 70)
    print("PARALLEL MATCH URL COLLECTION")
    print("13 Leagues × 6 Seasons = 78 Tasks")
    print("=" * 70)
    
    # Setup directories
    setup_directories()
    
    # Distribute tasks
    num_workers = 4
    task_distribution = distribute_tasks(num_workers)
    
    print(f"\n📋 Task Distribution:")
    for i, tasks in enumerate(task_distribution, 1):
        print(f"  Worker {i}: {len(tasks)} tasks")
    
    print(f"\n🚀 Starting {num_workers} parallel workers...")
    start_time = time.time()
    
    # Execute parallel collection
    all_results = []
    
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = []
        
        for worker_id, tasks in enumerate(task_distribution, 1):
            future = executor.submit(worker_process, worker_id, tasks)
            futures.append(future)
        
        # Collect results as they complete
        for future in as_completed(futures):
            try:
                worker_results = future.result()
                all_results.extend(worker_results)
                print(f"✅ Worker completed: {len(worker_results)} tasks")
            except Exception as e:
                print(f"❌ Worker failed: {e}")
    
    # Generate summary
    duration = time.time() - start_time
    print(f"\n⏱️ Total time: {duration/60:.1f} minutes")
    
    # Save final results
    final_results_file = OUTPUT_DIR / "final_results.json"
    with open(final_results_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    # Generate summary report
    generate_summary(all_results)
    
    # Combine all CSV files
    combine_all_csvs()
    
    print("\n✅ Collection complete!")
    print(f"📁 Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    # Ensure multiprocessing works correctly
    mp.set_start_method('spawn', force=True)
    main()