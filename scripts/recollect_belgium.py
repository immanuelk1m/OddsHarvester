#!/usr/bin/env python3
"""
Recollect Belgium league with correct URL patterns
2020-21 이전: jupiler-league
2021-22 이후: jupiler-pro-league
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
logger = logging.getLogger("BelgiumRecollector")

# Register markets
SportMarketRegistrar.register_all_markets()

# Output directory
OUTPUT_DIR = Path("match_urls_belgium_fixed")
OUTPUT_DIR.mkdir(exist_ok=True)


class BelgiumRecollector:
    """Recollector for Belgium league with correct URL patterns"""
    
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
        self.summary_file = OUTPUT_DIR / "belgium_summary.json"
    
    async def collect_season(self, season: str, league_id: str) -> Dict:
        """Collect URLs for a single Belgium season"""
        
        result = {
            "country": "belgium",
            "league_id": league_id,
            "league_name": "Belgium Pro League",
            "season": season,
            "status": "pending",
            "match_count": 0,
            "pages_found": 0,
            "error": None,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"Collecting: Belgium Pro League - {season}")
            logger.info(f"Using URL pattern: {league_id}")
            logger.info('='*60)
            
            # Start playwright
            await self.scraper.start_playwright(headless=True)
            
            # Build URL directly (bypass the buggy url_builder)
            base_url = f"https://www.oddsportal.com/football/belgium/{league_id}-{season}/results/"
            
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
                    if ("belgium" in link.lower() or 
                        "jupiler" in link.lower()):
                        if not any(x in link for x in ['/pl/', 'saudi-arabia', 'world-cup', 'copa-']):
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
                    if ("belgium" in link.lower() or 
                        "jupiler" in link.lower()):
                        if not any(x in link for x in ['/pl/', 'saudi-arabia', 'world-cup', 'copa-']):
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
                        writer.writerow(["Belgium Pro League", season, url])
                
                logger.info(f"✅ SUCCESS: Saved {len(all_match_urls)} matches")
                result["status"] = "success"
                result["match_count"] = len(all_match_urls)
                
                # Log samples
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
        """Collect all Belgium seasons with correct URL patterns"""
        
        logger.info("="*70)
        logger.info("BELGIUM LEAGUE RECOLLECTION")
        logger.info("="*70)
        
        # Define seasons with correct URL patterns
        seasons_to_collect = [
            ("2019-2020", "jupiler-league"),
            ("2020-2021", "jupiler-league"),
            ("2021-2022", "jupiler-pro-league"),
            ("2022-2023", "jupiler-pro-league"),
            ("2023-2024", "jupiler-pro-league"),
            ("2024-2025", "jupiler-pro-league"),
        ]
        
        for season, league_id in seasons_to_collect:
            await self.collect_season(season, league_id)
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
        
        logger.info(f"Total Seasons: {len(self.results)}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Total Matches Collected: {total_matches:,}")
        
        logger.info("\nBy Season:")
        for r in self.results:
            status_icon = "✅" if r["status"] == "success" else "❌"
            logger.info(f"  {r['season']}: {r['match_count']} matches (Pages: {r['pages_found']}) {status_icon}")
        
        logger.info(f"\n📊 Grand Total: {total_matches:,} matches collected")
        logger.info(f"📁 Output directory: {OUTPUT_DIR}")


async def main():
    """Main entry point"""
    collector = BelgiumRecollector()
    await collector.collect_all()


if __name__ == "__main__":
    asyncio.run(main())