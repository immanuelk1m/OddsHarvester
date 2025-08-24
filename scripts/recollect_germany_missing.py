#!/usr/bin/env python3
"""
Recollect missing Germany Bundesliga seasons
Target: Seasons with less than 306 matches (standard is 306-308)
"""

import asyncio
import csv
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

sys.path.append(str(Path(__file__).parent.parent))

from src.core.odds_portal_scraper import OddsPortalScraper
from src.core.playwright_manager import PlaywrightManager
from src.core.browser_helper import BrowserHelper
from src.core.odds_portal_market_extractor import OddsPortalMarketExtractor
from src.core.sport_market_registry import SportMarketRegistrar
from src.utils.setup_logging import setup_logger

# Setup logging
setup_logger(log_level=logging.INFO, save_to_file=True)
logger = logging.getLogger("GermanyRecollector")

# Register markets
SportMarketRegistrar.register_all_markets()

# Output directory
OUTPUT_DIR = Path("match_urls_germany_fixed")
OUTPUT_DIR.mkdir(exist_ok=True)

# Missing/incomplete seasons to recollect
# Based on analysis: 2024-2025 has only 263 matches (should be ~306)
# We'll also check other seasons that might have issues
SEASONS_TO_CHECK = [
    "2019-2020",  # Has 306 - recheck
    "2020-2021",  # Has 308 - OK
    "2021-2022",  # Has 308 - OK  
    "2022-2023",  # Has 306 - recheck
    "2023-2024",  # Has 306 - recheck
    "2024-2025",  # Has 263 - definitely needs recollection
]


class GermanyRecollector:
    """Recollector for Germany Bundesliga missing seasons"""
    
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
        self.summary_file = OUTPUT_DIR / "germany_summary.json"
    
    async def collect_season(self, season: str) -> Dict:
        """Collect URLs for a single Germany season"""
        
        result = {
            "country": "germany",
            "league_id": "germany-bundesliga",
            "league_name": "Germany Bundesliga",
            "season": season,
            "status": "pending",
            "match_count": 0,
            "pages_found": 0,
            "error": None,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"Collecting: Germany Bundesliga - {season}")
            logger.info('='*60)
            
            # Start playwright
            await self.scraper.start_playwright(headless=True)
            
            # Build URL using URLBuilder
            from src.core.url_builder import URLBuilder
            base_url = URLBuilder.get_historic_matches_url(
                sport="football",
                league="germany-bundesliga",
                season=season
            )
            
            logger.info(f"URL: {base_url}")
            
            # Navigate to page
            page = self.scraper.playwright_manager.page
            await page.goto(base_url, timeout=30000, wait_until="networkidle")
            
            # Wait for content
            logger.info("Waiting for page to fully load...")
            await page.wait_for_timeout(5000)
            
            # Dismiss popups
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
            if len(pages_to_scrape) == 1:
                logger.info("Single page - extracting matches...")
                
                # Scroll to load all content
                for i in range(3):
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await page.wait_for_timeout(2000)
                    logger.info(f"Scroll {i+1}/3 completed")
                
                # Extract matches
                match_links = await self.scraper.extract_match_links(page=page)
                
                # Filter valid links
                valid_links = []
                for link in match_links:
                    if ("germany" in link.lower() or 
                        "bundesliga" in link.lower()):
                        if not any(x in link for x in ['/pl/', 'saudi-arabia', 'world-cup', 'copa-', '2-bundesliga']):
                            valid_links.append(link)
                
                all_match_urls = valid_links
                logger.info(f"Extracted {len(valid_links)} valid matches")
                
            else:
                logger.info(f"Multiple pages ({len(pages_to_scrape)}) - collecting from all...")
                
                # Collect from all pages
                match_links = await self.scraper._collect_match_links(
                    base_url=base_url,
                    pages_to_scrape=pages_to_scrape,
                    max_matches=None
                )
                
                # Filter valid links
                valid_links = []
                for link in match_links:
                    if ("germany" in link.lower() or 
                        "bundesliga" in link.lower()):
                        if not any(x in link for x in ['/pl/', 'saudi-arabia', 'world-cup', 'copa-', '2-bundesliga']):
                            valid_links.append(link)
                
                all_match_urls = valid_links
                logger.info(f"Collected {len(valid_links)} valid matches")
            
            # Save results
            if all_match_urls:
                output_file = OUTPUT_DIR / f"{season}.csv"
                
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["league", "season", "match_url"])
                    
                    for url in all_match_urls:
                        writer.writerow(["Germany Bundesliga", season, url])
                
                logger.info(f"✅ SUCCESS: Saved {len(all_match_urls)} matches")
                result["status"] = "success"
                result["match_count"] = len(all_match_urls)
                
                # Log samples
                logger.info("Sample URLs:")
                for i, url in enumerate(all_match_urls[:3], 1):
                    logger.info(f"  {i}. {url}")
                    
                # Check if this is the expected count
                if len(all_match_urls) >= 306:
                    logger.info(f"✅ Match count OK: {len(all_match_urls)} (expected: 306-308)")
                else:
                    logger.warning(f"⚠️ Low match count: {len(all_match_urls)} (expected: 306-308)")
                    
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
        """Collect all Germany seasons that need recollection"""
        
        logger.info("="*70)
        logger.info("GERMANY BUNDESLIGA RECOLLECTION")
        logger.info("="*70)
        logger.info("Checking seasons for completeness...")
        
        for season in SEASONS_TO_CHECK:
            # Check existing data first
            existing_file = Path(f"match_urls_complete/by_league/germany/{season}.csv")
            if existing_file.exists():
                with open(existing_file, 'r') as f:
                    existing_count = sum(1 for _ in f) - 1  # Subtract header
                logger.info(f"{season}: {existing_count} matches in existing data")
                
                # Only recollect if count is low
                if existing_count < 306:
                    logger.info(f"  → Recollecting {season} (too few matches)")
                    await self.collect_season(season)
                    await asyncio.sleep(3)
                else:
                    logger.info(f"  → Skipping {season} (sufficient matches)")
                    self.results.append({
                        "country": "germany",
                        "league_id": "germany-bundesliga",
                        "league_name": "Germany Bundesliga",
                        "season": season,
                        "status": "skipped",
                        "match_count": existing_count,
                        "pages_found": 0,
                        "error": None,
                        "timestamp": datetime.now().isoformat()
                    })
            else:
                logger.info(f"{season}: No existing data found")
                await self.collect_season(season)
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
        
        total_matches = sum(r["match_count"] for r in self.results if r["status"] == "success")
        successful = sum(1 for r in self.results if r["status"] == "success")
        skipped = sum(1 for r in self.results if r["status"] == "skipped")
        failed = sum(1 for r in self.results if r["status"] == "error")
        
        logger.info(f"Total Seasons: {len(self.results)}")
        logger.info(f"Recollected: {successful}")
        logger.info(f"Skipped (already OK): {skipped}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Total New Matches: {total_matches:,}")
        
        logger.info("\nBy Season:")
        for r in self.results:
            if r["status"] == "success":
                status_icon = "✅"
                status_text = f"{r['match_count']} matches collected"
            elif r["status"] == "skipped":
                status_icon = "⏭️"
                status_text = f"{r['match_count']} matches (already OK)"
            else:
                status_icon = "❌"
                status_text = "Failed"
            
            logger.info(f"  {r['season']}: {status_text} {status_icon}")
        
        # Check if standard reached
        logger.info("\nStandard Check (306-308 matches per season):")
        for r in self.results:
            if r["match_count"] >= 306:
                logger.info(f"  {r['season']}: ✅ OK ({r['match_count']} matches)")
            else:
                logger.info(f"  {r['season']}: ⚠️ Below standard ({r['match_count']} matches)")
        
        logger.info(f"\n📁 Output directory: {OUTPUT_DIR}")


async def main():
    """Main entry point"""
    collector = GermanyRecollector()
    await collector.collect_all()


if __name__ == "__main__":
    asyncio.run(main())