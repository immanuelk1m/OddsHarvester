#!/usr/bin/env python
"""
Match URL Collector for European Football Leagues
Collects match URLs for specified leagues and seasons without scraping odds data
"""

import asyncio
import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from src.core.odds_portal_scraper import OddsPortalScraper
from src.core.playwright_manager import PlaywrightManager
from src.core.browser_helper import BrowserHelper
from src.core.odds_portal_market_extractor import OddsPortalMarketExtractor
from src.core.sport_market_registry import SportMarketRegistrar
from src.utils.setup_logging import setup_logger

# Setup logging
setup_logger(log_level=logging.INFO, save_to_file=True)
logger = logging.getLogger("MatchURLCollector")

# Register all markets
SportMarketRegistrar.register_all_markets()

# Output directories
OUTPUT_DIR = Path("match_urls_collection")
OUTPUT_DIR.mkdir(exist_ok=True)

# Define leagues with their configurations
LEAGUES_CONFIG = {
    "belgium": {
        "id": "belgium-jupiler-pro-league",
        "name": "Belgium Jupiler Pro League",
        "seasons": ["2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024", "2024-2025"]
    },
    "switzerland": {
        "id": "switzerland-super-league",
        "name": "Switzerland Super League",
        "seasons": ["2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024", "2024-2025"]
    },
    "england": {
        "id": "england-premier-league",
        "name": "England Premier League",
        "seasons": ["2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024", "2024-2025"]
    },
    "italy": {
        "id": "italy-serie-a",
        "name": "Italy Serie A",
        "seasons": ["2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024", "2024-2025"]
    },
    "spain": {
        "id": "spain-laliga",
        "name": "Spain La Liga",
        "seasons": ["2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024", "2024-2025"]
    },
    "sweden": {
        "id": "sweden-allsvenskan",
        "name": "Sweden Allsvenskan",
        # Sweden uses single year format
        "seasons": ["2019", "2020", "2021", "2022", "2023", "2024"]
    },
    "france": {
        "id": "france-ligue-1",
        "name": "France Ligue 1",
        "seasons": ["2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024", "2024-2025"]
    },
    "portugal": {
        "id": "portugal-liga-portugal",
        "name": "Portugal Liga Portugal",
        "seasons": ["2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024", "2024-2025"]
    },
    "norway": {
        "id": "norway-eliteserien",
        "name": "Norway Eliteserien",
        # Norway uses single year format
        "seasons": ["2019", "2020", "2021", "2022", "2023", "2024"]
    },
    "denmark": {
        "id": "denmark-superliga",
        "name": "Denmark Superliga",
        "seasons": ["2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024", "2024-2025"]
    },
    "germany": {
        "id": "germany-bundesliga",
        "name": "Germany Bundesliga",
        "seasons": ["2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024", "2024-2025"]
    },
    "netherlands": {
        "id": "netherlands-eredivisie",
        "name": "Netherlands Eredivisie",
        "seasons": ["2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024", "2024-2025"]
    },
    "scotland": {
        "id": "scotland-premiership",
        "name": "Scotland Premiership",
        "seasons": ["2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024", "2024-2025"]
    }
}


class MatchURLCollector:
    """Collector for match URLs only, without odds data"""
    
    def __init__(self):
        # Initialize required components
        self.playwright_manager = PlaywrightManager()
        self.browser_helper = BrowserHelper()
        self.market_extractor = OddsPortalMarketExtractor(browser_helper=self.browser_helper)
        
        # Initialize the scraper with required components
        self.scraper = OddsPortalScraper(
            playwright_manager=self.playwright_manager,
            browser_helper=self.browser_helper,
            market_extractor=self.market_extractor,
            preview_submarkets_only=True  # We only need URLs, not full odds data
        )
        
        self.collected_urls = []
        self.progress_file = OUTPUT_DIR / "collection_progress.json"
        self.load_progress()
    
    def load_progress(self):
        """Load progress from previous runs"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                self.progress = json.load(f)
        else:
            self.progress = {}
    
    def save_progress(self):
        """Save current progress"""
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    def is_completed(self, league_id: str, season: str) -> bool:
        """Check if a league-season combination was already collected"""
        key = f"{league_id}_{season}"
        return self.progress.get(key, {}).get("completed", False)
    
    def mark_completed(self, league_id: str, season: str, urls_count: int):
        """Mark a league-season combination as completed"""
        key = f"{league_id}_{season}"
        self.progress[key] = {
            "completed": True,
            "timestamp": datetime.now().isoformat(),
            "urls_count": urls_count
        }
        self.save_progress()
    
    async def collect_match_urls(self, league_id: str, season: str) -> List[Dict]:
        """
        Collect match URLs for a specific league and season
        
        Returns list of dicts with: match_url, home_team, away_team, match_date
        """
        try:
            logger.info(f"Collecting URLs for {league_id} - Season {season}")
            
            # Start playwright
            await self.scraper.start_playwright(headless=True)
            
            # Navigate to historic matches page
            from src.core.url_builder import URLBuilder
            base_url = URLBuilder.get_historic_matches_url(
                sport="football",
                league=league_id,
                season=season
            )
            
            logger.info(f"Base URL: {base_url}")
            
            page = self.scraper.playwright_manager.page
            await page.goto(base_url, timeout=20000, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            
            # Get pagination info
            pages_to_scrape = await self.scraper._get_pagination_info(page=page, max_pages=None)
            logger.info(f"Found {len(pages_to_scrape)} pages to scrape")
            
            # Collect all match links using scraper's existing method
            all_match_urls = []
            
            # If only one page, extract from current page
            if len(pages_to_scrape) == 1:
                logger.info("Single page detected, extracting match links...")
                
                # Scroll to load all content
                await self.browser_helper.scroll_until_loaded(
                    page=page,
                    timeout=30,
                    scroll_pause_time=2,
                    max_scroll_attempts=3,
                    content_check_selector="div[class*='eventRow']"
                )
                
                # Use the scraper's built-in method to extract links
                match_links = await self.scraper.extract_match_links(page=page)
                
                # Convert to our format
                for link in match_links:
                    all_match_urls.append({
                        "match_url": link,
                        "home_team": "",
                        "away_team": "",
                        "match_date": ""
                    })
                    
                logger.info(f"Extracted {len(match_links)} matches from single page")
            else:
                # Multiple pages - use scraper's _collect_match_links method
                logger.info(f"Multiple pages detected ({len(pages_to_scrape)}), collecting from all...")
                match_links = await self.scraper._collect_match_links(
                    base_url=base_url,
                    pages_to_scrape=pages_to_scrape,
                    max_matches=None
                )
                
                # Convert to our format
                for link in match_links:
                    all_match_urls.append({
                        "match_url": link,
                        "home_team": "",
                        "away_team": "",
                        "match_date": ""
                    })
                    
                logger.info(f"Extracted {len(match_links)} matches from {len(pages_to_scrape)} pages")
            
            logger.info(f"Total matches collected: {len(all_match_urls)}")
            return all_match_urls
            
        except Exception as e:
            logger.error(f"Error collecting URLs for {league_id} - {season}: {e}")
            return []
        finally:
            await self.scraper.stop_playwright()
    
    async def _extract_match_data_from_page(self, page) -> List[Dict]:
        """Extract match URLs and basic info from current page"""
        try:
            from bs4 import BeautifulSoup
            import re
            
            html_content = await page.content()
            soup = BeautifulSoup(html_content, "lxml")
            
            matches = []
            event_rows = soup.find_all(class_=re.compile("^eventRow"))
            
            for row in event_rows:
                try:
                    # Find match link
                    match_link = None
                    for link in row.find_all("a", href=True):
                        href = link["href"]
                        if len(href.strip("/").split("/")) > 3:
                            match_link = f"https://www.oddsportal.com{href}"
                            break
                    
                    if not match_link:
                        continue
                    
                    # Extract teams and date
                    match_info = {
                        "match_url": match_link,
                        "home_team": "",
                        "away_team": "",
                        "match_date": ""
                    }
                    
                    # Try to extract team names
                    team_elements = row.find_all(class_=re.compile("participant"))
                    if len(team_elements) >= 2:
                        match_info["home_team"] = team_elements[0].get_text(strip=True)
                        match_info["away_team"] = team_elements[1].get_text(strip=True)
                    
                    # Try to extract date
                    date_element = row.find(class_=re.compile("date"))
                    if date_element:
                        match_info["match_date"] = date_element.get_text(strip=True)
                    
                    matches.append(match_info)
                    
                except Exception as e:
                    logger.debug(f"Error extracting match from row: {e}")
                    continue
            
            return matches
            
        except Exception as e:
            logger.error(f"Error extracting match data from page: {e}")
            return []
    
    async def collect_all_leagues(self):
        """Collect URLs for all configured leagues and seasons"""
        total_combinations = sum(len(config["seasons"]) for config in LEAGUES_CONFIG.values())
        completed = 0
        
        logger.info(f"Starting collection for {len(LEAGUES_CONFIG)} leagues")
        logger.info(f"Total league-season combinations: {total_combinations}")
        
        for country, config in LEAGUES_CONFIG.items():
            league_id = config["id"]
            league_name = config["name"]
            
            # Create league-specific output file
            output_file = OUTPUT_DIR / f"{country}_{league_id.replace('-', '_')}_matches.csv"
            
            # Prepare CSV file if it doesn't exist
            if not output_file.exists():
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=[
                        "league", "season", "match_url", "home_team", "away_team", "match_date"
                    ])
                    writer.writeheader()
            
            for season in config["seasons"]:
                completed += 1
                
                # Check if already completed
                if self.is_completed(league_id, season):
                    logger.info(f"[{completed}/{total_combinations}] Skipping {league_name} - {season} (already completed)")
                    continue
                
                logger.info(f"[{completed}/{total_combinations}] Processing {league_name} - {season}")
                
                # Collect URLs
                match_urls = await self.collect_match_urls(league_id, season)
                
                if match_urls:
                    # Add league and season info
                    for match in match_urls:
                        match["league"] = league_name
                        match["season"] = season
                    
                    # Append to CSV
                    with open(output_file, 'a', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=[
                            "league", "season", "match_url", "home_team", "away_team", "match_date"
                        ])
                        writer.writerows(match_urls)
                    
                    # Mark as completed
                    self.mark_completed(league_id, season, len(match_urls))
                    logger.info(f"✅ Saved {len(match_urls)} URLs for {league_name} - {season}")
                else:
                    logger.warning(f"⚠️ No URLs collected for {league_name} - {season}")
                
                # Small delay between seasons
                await asyncio.sleep(2)
        
        logger.info("Collection completed!")
        self.generate_summary()
    
    def generate_summary(self):
        """Generate a summary report of collected URLs"""
        summary_file = OUTPUT_DIR / "collection_summary.txt"
        
        with open(summary_file, 'w') as f:
            f.write("Match URL Collection Summary\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            total_urls = 0
            for country, config in LEAGUES_CONFIG.items():
                league_id = config["id"]
                league_name = config["name"]
                f.write(f"\n{league_name}:\n")
                
                for season in config["seasons"]:
                    key = f"{league_id}_{season}"
                    if key in self.progress:
                        count = self.progress[key].get("urls_count", 0)
                        total_urls += count
                        status = "✅" if self.progress[key].get("completed") else "❌"
                        f.write(f"  {season}: {count} matches {status}\n")
                    else:
                        f.write(f"  {season}: Not processed ❌\n")
            
            f.write(f"\n" + "=" * 50 + "\n")
            f.write(f"Total matches collected: {total_urls}\n")
        
        logger.info(f"Summary saved to {summary_file}")
        logger.info(f"Total matches collected: {total_urls}")


async def main():
    """Main entry point"""
    collector = MatchURLCollector()
    await collector.collect_all_leagues()


if __name__ == "__main__":
    asyncio.run(main())