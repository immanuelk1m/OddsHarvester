#!/usr/bin/env python3
"""
Complete collection script for all 13 European leagues
Runs sequentially with 1 processor for stability
"""

import asyncio
import csv
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

sys.path.append(str(Path(__file__).parent.parent))

from src.core.odds_portal_scraper import OddsPortalScraper
from src.core.playwright_manager import PlaywrightManager
from src.core.browser_helper import BrowserHelper
from src.core.odds_portal_market_extractor import OddsPortalMarketExtractor
from src.core.sport_market_registry import SportMarketRegistrar
from src.utils.setup_logging import setup_logger

# Setup logging
setup_logger(log_level=logging.INFO, save_to_file=True)
logger = logging.getLogger("CompleteLeagueCollector")

# Register markets
SportMarketRegistrar.register_all_markets()

# Output directory
OUTPUT_DIR = Path("match_urls_complete")
OUTPUT_DIR.mkdir(exist_ok=True)

# All 13 leagues with their full seasons
ALL_LEAGUES = {
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
        "name": "Belgium Pro League",
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
        "seasons": ["2019", "2020", "2021", "2022", "2023", "2024"]
    },
    "sweden": {
        "id": "sweden-allsvenskan",
        "name": "Sweden Allsvenskan",
        "seasons": ["2019", "2020", "2021", "2022", "2023", "2024"]
    }
}


class CompleteLeagueCollector:
    """Complete collector for all leagues with improved extraction"""
    
    def __init__(self):
        self.playwright_manager = PlaywrightManager()
        self.browser_helper = BrowserHelper()
        self.market_extractor = OddsPortalMarketExtractor(browser_helper=self.browser_helper)
        
        self.scraper = OddsPortalScraper(
            playwright_manager=self.playwright_manager,
            browser_helper=self.browser_helper,
            market_extractor=self.market_extractor,
            preview_submarkets_only=True
        )
        
        self.results = []
        self.summary_file = OUTPUT_DIR / "collection_summary.json"
    
    async def collect_league_season(self, country: str, league_id: str, league_name: str, season: str) -> Dict:
        """Collect URLs for a single league-season with enhanced extraction"""
        
        result = {
            "country": country,
            "league_id": league_id,
            "league_name": league_name,
            "season": season,
            "status": "pending",
            "match_count": 0,
            "pages_found": 0,
            "error": None,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"Collecting: {league_name} - {season}")
            logger.info('='*60)
            
            # Start playwright
            await self.scraper.start_playwright(headless=True)
            
            # Build URL
            from src.core.url_builder import URLBuilder
            base_url = URLBuilder.get_historic_matches_url(
                sport="football",
                league=league_id,
                season=season
            )
            
            logger.info(f"Base URL: {base_url}")
            
            # Navigate to page with longer timeout
            page = self.scraper.playwright_manager.page
            await page.goto(base_url, timeout=30000, wait_until="networkidle")
            
            # Wait for content to fully load
            logger.info("Waiting for page to fully load...")
            await page.wait_for_timeout(5000)
            
            # Try to dismiss any popups/banners
            try:
                await self.browser_helper.dismiss_cookie_banner(page=page)
            except:
                pass
            
            # Get pagination info
            logger.info("Analyzing pagination...")
            pages_to_scrape = await self.scraper._get_pagination_info(page=page, max_pages=None)
            result["pages_found"] = len(pages_to_scrape)
            logger.info(f"Found {len(pages_to_scrape)} pages")
            
            # Collect match URLs
            all_match_urls = []
            
            if len(pages_to_scrape) == 1:
                logger.info("Single page - extracting matches...")
                
                # Scroll multiple times to ensure all content loads
                for i in range(3):
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await page.wait_for_timeout(2000)
                    logger.info(f"Scroll {i+1}/3 completed")
                
                # Extract with improved method
                match_links = await self.scraper.extract_match_links(page=page)
                
                # Filter out invalid URLs
                valid_links = []
                for link in match_links:
                    # Ensure it's a match URL for this league
                    if (league_id.replace('-', '') in link.lower() or 
                        country in link.lower()):
                        if not any(x in link for x in ['/pl/', 'saudi-arabia', 'world-cup', 'copa-']):
                            valid_links.append(link)
                
                all_match_urls = valid_links
                logger.info(f"Extracted {len(valid_links)} valid matches (filtered from {len(match_links)})") 
                
            else:
                logger.info(f"Multiple pages ({len(pages_to_scrape)}) - collecting from all...")
                
                # Use the scraper's collect method
                match_links = await self.scraper._collect_match_links(
                    base_url=base_url,
                    pages_to_scrape=pages_to_scrape,
                    max_matches=None
                )
                
                # Filter valid links
                valid_links = []
                for link in match_links:
                    if (league_id.replace('-', '') in link.lower() or 
                        country in link.lower()):
                        if not any(x in link for x in ['/pl/', 'saudi-arabia', 'world-cup', 'copa-']):
                            valid_links.append(link)
                
                all_match_urls = valid_links
                logger.info(f"Collected {len(valid_links)} valid matches (filtered from {len(match_links)})")
            
            # Save results by league
            if all_match_urls:
                # Create league directory
                league_dir = OUTPUT_DIR / "by_league" / country
                league_dir.mkdir(parents=True, exist_ok=True)
                
                # Save to CSV
                output_file = league_dir / f"{season}.csv"
                
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["league", "season", "match_url"])
                    
                    for url in all_match_urls:
                        writer.writerow([league_name, season, url])
                
                logger.info(f"✅ SUCCESS: Saved {len(all_match_urls)} matches to {output_file}")
                result["status"] = "success"
                result["match_count"] = len(all_match_urls)
                
                # Log sample URLs
                logger.info("Sample URLs:")
                for i, url in enumerate(all_match_urls[:3], 1):
                    logger.info(f"  {i}. {url}")
            else:
                logger.warning("⚠️ No valid matches found")
                result["status"] = "no_data"
            
            await self.scraper.stop_playwright()
            
        except Exception as e:
            logger.error(f"❌ ERROR: {str(e)}")
            result["status"] = "error"
            result["error"] = str(e)
            
            try:
                await self.scraper.stop_playwright()
            except:
                pass
        
        self.results.append(result)
        return result
    
    async def collect_all(self):
        """Collect all leagues sequentially"""
        
        logger.info("="*70)
        logger.info("COMPLETE LEAGUE COLLECTION")
        logger.info(f"Target: {len(ALL_LEAGUES)} leagues, 6 seasons each")
        logger.info("="*70)
        
        total_tasks = sum(len(config["seasons"]) for config in ALL_LEAGUES.values())
        completed = 0
        
        for country, config in ALL_LEAGUES.items():
            for season in config["seasons"]:
                completed += 1
                logger.info(f"\n[{completed}/{total_tasks}] Processing...")
                
                await self.collect_league_season(
                    country=country,
                    league_id=config["id"],
                    league_name=config["name"],
                    season=season
                )
                
                # Delay between collections to avoid overloading
                await asyncio.sleep(3)
        
        # Save summary
        with open(self.summary_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print collection summary"""
        
        logger.info("\n" + "="*70)
        logger.info("COLLECTION SUMMARY")
        logger.info("="*70)
        
        total_matches = sum(r["match_count"] for r in self.results)
        successful = sum(1 for r in self.results if r["status"] == "success")
        failed = sum(1 for r in self.results if r["status"] == "error")
        no_data = sum(1 for r in self.results if r["status"] == "no_data")
        
        logger.info(f"Total Tasks: {len(self.results)}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")
        logger.info(f"No Data: {no_data}")
        logger.info(f"Total Matches Collected: {total_matches:,}")
        
        # By league summary
        logger.info("\nBy League:")
        for country, config in ALL_LEAGUES.items():
            league_results = [r for r in self.results if r["country"] == country]
            league_matches = sum(r["match_count"] for r in league_results)
            logger.info(f"\n{config['name']}:")
            
            for r in league_results:
                status_icon = "✅" if r["status"] == "success" else "❌"
                logger.info(f"  {r['season']}: {r['match_count']} matches (Pages: {r['pages_found']}) {status_icon}")
            
            logger.info(f"  Total: {league_matches} matches")
        
        logger.info(f"\n📊 Grand Total: {total_matches:,} matches collected")
        logger.info(f"📁 Output directory: {OUTPUT_DIR}")
        
        # List any failed collections
        if failed > 0:
            logger.warning("\n⚠️ Failed Collections:")
            for r in self.results:
                if r["status"] == "error":
                    logger.warning(f"  - {r['league_name']} {r['season']}: {r['error']}")


async def main():
    """Main entry point"""
    collector = CompleteLeagueCollector()
    await collector.collect_all()


if __name__ == "__main__":
    asyncio.run(main())