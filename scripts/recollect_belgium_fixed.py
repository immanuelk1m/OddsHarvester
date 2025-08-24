#!/usr/bin/env python3
"""
Fixed Belgium league collection with corrected URL pattern extraction
Handles both jupiler-league (pre-2021) and jupiler-pro-league (2021+)
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
logger = logging.getLogger("BelgiumFixed")

# Register markets
SportMarketRegistrar.register_all_markets()

# Output directory
OUTPUT_DIR = Path("match_urls_belgium_complete")
OUTPUT_DIR.mkdir(exist_ok=True)


class BelgiumFixedCollector:
    """Fixed collector for Belgium league with corrected pattern extraction"""
    
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
        self.summary_file = OUTPUT_DIR / "belgium_complete_summary.json"
    
    async def collect_season(self, season: str, league_id: str, retry_count: int = 2) -> Dict:
        """Collect URLs for a single Belgium season with retry"""
        
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
        
        for attempt in range(retry_count):
            try:
                logger.info(f"\n{'='*60}")
                logger.info(f"Collecting: Belgium - {season} (Attempt {attempt + 1}/{retry_count})")
                logger.info(f"League ID: {league_id}")
                logger.info('='*60)
                
                # Start playwright with English locale to avoid /pl/ redirect
                await self.scraper.start_playwright(
                    headless=True,
                    browser_locale_timezone="en-US",
                    browser_timezone_id="America/New_York"
                )
                
                # Build URL directly
                base_url = f"https://www.oddsportal.com/football/belgium/{league_id}-{season}/results/"
                logger.info(f"URL: {base_url}")
                
                # Navigate to page
                page = self.scraper.playwright_manager.page
                
                # First navigate to main page to establish session
                await page.goto("https://www.oddsportal.com/", timeout=30000, wait_until="networkidle")
                await page.wait_for_timeout(2000)
                
                # Now navigate to the Belgium URL
                await page.goto(base_url, timeout=30000, wait_until="networkidle")
                
                # Check if redirected to /pl/ and force back to English if needed
                current_url = page.url
                if "/pl/" in current_url:
                    logger.info("Redirected to /pl/, forcing English URL...")
                    english_url = current_url.replace("/pl/", "/")
                    await page.goto(english_url, timeout=30000, wait_until="networkidle")
                    current_url = page.url
                    logger.info(f"Forced to English URL: {current_url}")
                
                # Extended wait for dynamic content
                logger.info("Waiting for page to fully load...")
                await page.wait_for_timeout(7000)
                
                # Dismiss popups
                try:
                    await self.browser_helper.dismiss_cookie_banner(page=page)
                except:
                    pass
                
                # Additional scroll to trigger lazy loading
                logger.info("Scrolling to load all content...")
                for i in range(3):
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await page.wait_for_timeout(2000)
                    logger.info(f"Scroll {i+1}/3 completed")
                
                # Get pagination info
                logger.info("Analyzing pagination...")
                pages_to_scrape = await self.scraper._get_pagination_info(page=page, max_pages=None)
                result["pages_found"] = len(pages_to_scrape)
                logger.info(f"Found {len(pages_to_scrape)} pages")
                
                # Collect match URLs
                if len(pages_to_scrape) <= 1:
                    logger.info("Single page or no pagination - extracting all matches...")
                    
                    # Additional scrolling for single page
                    for i in range(5):
                        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        await page.wait_for_timeout(1500)
                    
                    # Extract matches
                    match_links = await self.scraper.extract_match_links(page=page)
                    logger.info(f"Extracted {len(match_links)} total links")
                    
                    # Filter for Belgium matches
                    valid_links = []
                    for link in match_links:
                        link_lower = link.lower()
                        # Check if it's a Belgium match
                        if ("belgium" in link_lower or "jupiler" in link_lower):
                            # Exclude unwanted patterns
                            if not any(x in link_lower for x in ['/pl/', 'saudi-arabia', 'world-cup', 
                                                                  'copa-', 'euro-', 'champions-league',
                                                                  'europa-', 'conference-', 'nations-league']):
                                valid_links.append(link)
                    
                    all_match_urls = valid_links
                    logger.info(f"Filtered to {len(valid_links)} valid Belgium matches")
                    
                else:
                    logger.info(f"Multiple pages ({len(pages_to_scrape)}) - collecting from all...")
                    
                    # Use the built-in method which handles pagination correctly
                    match_links = await self.scraper._collect_match_links(
                        base_url=base_url,
                        pages_to_scrape=pages_to_scrape,
                        max_matches=None
                    )
                    
                    # Filter for Belgium matches
                    valid_links = []
                    for link in match_links:
                        link_lower = link.lower()
                        if ("belgium" in link_lower or "jupiler" in link_lower):
                            if not any(x in link_lower for x in ['/pl/', 'saudi-arabia', 'world-cup', 
                                                                  'copa-', 'euro-', 'champions-league',
                                                                  'europa-', 'conference-', 'nations-league']):
                                valid_links.append(link)
                    
                    # Remove duplicates while preserving order
                    seen = set()
                    all_match_urls = []
                    for url in valid_links:
                        if url not in seen:
                            seen.add(url)
                            all_match_urls.append(url)
                    
                    logger.info(f"Collected {len(all_match_urls)} unique Belgium matches (from {len(valid_links)} total)")
                
                # Save results if we have matches
                if all_match_urls:
                    output_file = OUTPUT_DIR / f"{season}.csv"
                    
                    with open(output_file, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(["league", "season", "match_url"])
                        
                        for url in all_match_urls:
                            writer.writerow(["Belgium Pro League", season, url])
                    
                    logger.info(f"✅ SUCCESS: Saved {len(all_match_urls)} matches to {output_file}")
                    result["status"] = "success"
                    result["match_count"] = len(all_match_urls)
                    
                    # Log sample URLs
                    logger.info("Sample URLs:")
                    for i, url in enumerate(all_match_urls[:3], 1):
                        logger.info(f"  {i}. {url}")
                    
                    # Check expected match count
                    if season == "2019-2020":
                        expected = "~240 (COVID shortened)"
                    elif season == "2024-2025":
                        expected = "~150-200 (in progress)"
                    else:
                        expected = "~300-340"
                    
                    logger.info(f"Match count: {len(all_match_urls)} (Expected: {expected})")
                    
                    await self.scraper.stop_playwright()
                    break  # Success, exit retry loop
                    
                else:
                    if attempt < retry_count - 1:
                        logger.warning(f"⚠️ No matches found, retrying...")
                        await self.scraper.stop_playwright()
                        await asyncio.sleep(5)
                        continue
                    else:
                        logger.warning("⚠️ No valid matches found after all attempts")
                        result["status"] = "no_data"
                
                await self.scraper.stop_playwright()
                
            except Exception as e:
                logger.error(f"❌ ERROR (Attempt {attempt + 1}): {str(e)}")
                result["status"] = "error"
                result["error"] = str(e)
                
                try:
                    await self.scraper.stop_playwright()
                except:
                    pass
                
                if attempt < retry_count - 1:
                    logger.info("Retrying after error...")
                    await asyncio.sleep(5)
                    continue
        
        self.results.append(result)
        return result
    
    async def collect_all(self):
        """Collect all Belgium seasons with correct URL patterns"""
        
        logger.info("="*70)
        logger.info("BELGIUM LEAGUE COLLECTION (FIXED)")
        logger.info("="*70)
        logger.info("Using corrected league pattern extraction")
        logger.info("")
        
        # Define seasons with correct URL patterns
        # Recollect 2023-2024 only
        seasons_to_collect = [
            ("2023-2024", "jupiler-pro-league"),
        ]
        
        total_start = datetime.now()
        
        for season, league_id in seasons_to_collect:
            season_start = datetime.now()
            await self.collect_season(season, league_id)
            season_duration = (datetime.now() - season_start).total_seconds()
            logger.info(f"Season collection took {season_duration:.1f} seconds")
            
            # Delay between seasons
            if season != seasons_to_collect[-1][0]:
                logger.info("Waiting 5 seconds before next season...")
                await asyncio.sleep(5)
        
        total_duration = (datetime.now() - total_start).total_seconds()
        logger.info(f"\nTotal collection time: {total_duration:.1f} seconds")
        
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
        
        logger.info(f"Total Seasons: {len(self.results)}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")
        logger.info(f"No Data: {no_data}")
        logger.info(f"Total Matches Collected: {total_matches:,}")
        
        logger.info("\nBy Season:")
        for r in self.results:
            if r["status"] == "success":
                status_icon = "✅"
                status_text = f"{r['match_count']} matches"
            elif r["status"] == "no_data":
                status_icon = "⚠️"
                status_text = "No data found"
            else:
                status_icon = "❌"
                status_text = "Failed"
            
            logger.info(f"  {r['season']}: {status_text} (Pages: {r['pages_found']}) {status_icon}")
        
        # Expected totals
        logger.info("\nExpected Match Counts:")
        logger.info("  2019-2020: ~240 (COVID shortened season)")
        logger.info("  2020-2021: ~330-340 (full season)")
        logger.info("  2021-2022: ~330-340 (full season)")
        logger.info("  2022-2023: ~330-340 (full season)")
        logger.info("  2023-2024: ~330-340 (full season)")
        logger.info("  2024-2025: ~150-200 (season in progress)")
        
        logger.info(f"\n📊 Grand Total: {total_matches:,} matches collected")
        logger.info(f"📁 Output directory: {OUTPUT_DIR}")
        
        # Check if we have reasonable counts
        if successful == 6 and total_matches > 1500:
            logger.info("\n✅ Collection appears successful!")
        else:
            logger.info("\n⚠️ Collection may need review")


async def main():
    """Main entry point"""
    collector = BelgiumFixedCollector()
    await collector.collect_all()


if __name__ == "__main__":
    asyncio.run(main())