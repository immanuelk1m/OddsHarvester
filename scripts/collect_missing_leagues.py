#!/usr/bin/env python3
"""
Collect missing league seasons from OddsPortal
Based on the working Belgium collection script
"""

import asyncio
import csv
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.append(str(Path(__file__).parent.parent))

from src.core.odds_portal_scraper import OddsPortalScraper
from src.core.playwright_manager import PlaywrightManager
from src.core.browser_helper import BrowserHelper
from src.core.odds_portal_market_extractor import OddsPortalMarketExtractor
from src.core.sport_market_registry import SportMarketRegistrar
from src.utils.setup_logging import setup_logger

# Setup logging
setup_logger(log_level=logging.INFO, save_to_file=True)
logger = logging.getLogger("MissingLeaguesCollector")

# Register markets
SportMarketRegistrar.register_all_markets()

# Output directory
OUTPUT_DIR = Path("match_urls_complete/by_league")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class MissingLeaguesCollector:
    """Collector for missing league seasons"""
    
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
        self.summary_file = OUTPUT_DIR / "missing_leagues_collection_summary.json"
        
        # Define missing seasons to collect
        self.leagues_to_collect = [
            # Germany - Bundesliga (3 seasons)
            ("germany", "bundesliga", "2019-2020", "Bundesliga"),
            ("germany", "bundesliga", "2022-2023", "Bundesliga"),
            ("germany", "bundesliga", "2023-2024", "Bundesliga"),
            
            # Netherlands - Eredivisie (2 seasons)
            ("netherlands", "eredivisie", "2022-2023", "Eredivisie"),
            ("netherlands", "eredivisie", "2023-2024", "Eredivisie"),
            
            # Portugal - Liga Portugal (2 seasons)
            ("portugal", "liga-portugal", "2019-2020", "Liga Portugal"),
            ("portugal", "liga-portugal", "2022-2023", "Liga Portugal"),
            
            # Scotland - Premiership (2 seasons)
            ("scotland", "premiership", "2022-2023", "Premiership"),
            ("scotland", "premiership", "2023-2024", "Premiership"),
            
            # Switzerland - Super League (3 seasons)
            ("switzerland", "super-league", "2019-2020", "Super League"),
            ("switzerland", "super-league", "2020-2021", "Super League"),
            ("switzerland", "super-league", "2022-2023", "Super League"),
        ]
    
    async def collect_season(self, country: str, league_id: str, season: str, 
                           league_name: str, retry_count: int = 2) -> Dict:
        """Collect URLs for a single season with retry"""
        
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
        
        for attempt in range(retry_count):
            try:
                logger.info(f"\n{'='*60}")
                logger.info(f"Collecting: {country.upper()} - {league_name} - {season}")
                logger.info(f"Attempt {attempt + 1}/{retry_count}")
                logger.info('='*60)
                
                # Start playwright with English locale
                await self.scraper.start_playwright(
                    headless=True,
                    browser_locale_timezone="en-US",
                    browser_timezone_id="America/New_York"
                )
                
                # Build URL
                base_url = f"https://www.oddsportal.com/football/{country}/{league_id}-{season}/results/"
                logger.info(f"URL: {base_url}")
                
                # Navigate to page
                page = self.scraper.playwright_manager.page
                
                # First navigate to main page to establish session
                await page.goto("https://www.oddsportal.com/", timeout=30000, wait_until="networkidle")
                await page.wait_for_timeout(2000)
                
                # Now navigate to the league URL
                await page.goto(base_url, timeout=30000, wait_until="networkidle")
                
                # Check if redirected to /pl/ and force back to English if needed
                current_url = page.url
                if "/pl/" in current_url:
                    logger.info("Redirected to /pl/, forcing English URL...")
                    english_url = current_url.replace("/pl/", "/")
                    await page.goto(english_url, timeout=30000, wait_until="networkidle")
                    current_url = page.url
                    logger.info(f"Forced to English URL: {current_url}")
                
                # Wait for dynamic content
                logger.info("Waiting for page to fully load...")
                await page.wait_for_timeout(7000)
                
                # Dismiss popups
                try:
                    await self.browser_helper.dismiss_cookie_banner(page=page)
                except:
                    pass
                
                # Scroll to trigger lazy loading
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
                    
                    # Filter for league matches
                    valid_links = []
                    for link in match_links:
                        link_lower = link.lower()
                        # Check if it's a match from this league
                        if f"{country}/{league_id}" in link_lower:
                            # Exclude unwanted patterns
                            if not any(x in link_lower for x in ['/pl/', 'world-cup', 
                                                                'copa-', 'euro-', 'champions-league',
                                                                'europa-', 'conference-', 'nations-league',
                                                                'friendly', 'qualification']):
                                valid_links.append(link)
                    
                    all_match_urls = valid_links
                    logger.info(f"Filtered to {len(valid_links)} valid {league_name} matches")
                    
                else:
                    logger.info(f"Multiple pages ({len(pages_to_scrape)}) - collecting from all...")
                    
                    # Use the built-in method which handles pagination correctly
                    match_links = await self.scraper._collect_match_links(
                        base_url=base_url,
                        pages_to_scrape=pages_to_scrape,
                        max_matches=None
                    )
                    
                    # Filter for league matches
                    valid_links = []
                    for link in match_links:
                        link_lower = link.lower()
                        if f"{country}/{league_id}" in link_lower:
                            if not any(x in link_lower for x in ['/pl/', 'world-cup', 
                                                                'copa-', 'euro-', 'champions-league',
                                                                'europa-', 'conference-', 'nations-league',
                                                                'friendly', 'qualification']):
                                valid_links.append(link)
                    
                    # Remove duplicates while preserving order
                    seen = set()
                    all_match_urls = []
                    for url in valid_links:
                        if url not in seen:
                            seen.add(url)
                            all_match_urls.append(url)
                    
                    logger.info(f"Collected {len(all_match_urls)} unique {league_name} matches")
                
                # Save results if we have matches
                if all_match_urls:
                    # Create country directory if needed
                    country_dir = OUTPUT_DIR / country
                    country_dir.mkdir(exist_ok=True)
                    
                    output_file = country_dir / f"{season}.csv"
                    
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
                    
                    # Check expected match count
                    expected = self.get_expected_matches(country, season)
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
    
    def get_expected_matches(self, country: str, season: str) -> str:
        """Get expected match count for validation"""
        
        expectations = {
            "germany": "306 (18 teams)",
            "netherlands": "306 (18 teams)",
            "portugal": "306 (18 teams)",
            "scotland": "228 (12 teams, split season)",
            "switzerland": "180 (10 teams, split season)"
        }
        
        # Special cases
        if country == "germany" and season == "2019-2020":
            return "306 (COVID affected)"
        elif country == "netherlands" and season == "2019-2020":
            return "~300 (COVID shortened)"
        elif country == "scotland" and "2019-2020" in season:
            return "~200 (COVID shortened)"
        
        return expectations.get(country, "Unknown")
    
    async def collect_all(self):
        """Collect all missing league seasons"""
        
        logger.info("="*70)
        logger.info("MISSING LEAGUES COLLECTION")
        logger.info("="*70)
        logger.info(f"Collecting {len(self.leagues_to_collect)} missing seasons")
        logger.info("")
        
        total_start = datetime.now()
        
        for i, (country, league_id, season, league_name) in enumerate(self.leagues_to_collect, 1):
            logger.info(f"\n[{i}/{len(self.leagues_to_collect)}] Processing {country} - {season}")
            
            season_start = datetime.now()
            await self.collect_season(country, league_id, season, league_name)
            season_duration = (datetime.now() - season_start).total_seconds()
            logger.info(f"Season collection took {season_duration:.1f} seconds")
            
            # Delay between seasons (except for last one)
            if i < len(self.leagues_to_collect):
                logger.info("Waiting 5 seconds before next season...")
                await asyncio.sleep(5)
        
        total_duration = (datetime.now() - total_start).total_seconds()
        logger.info(f"\nTotal collection time: {total_duration:.1f} seconds ({total_duration/60:.1f} minutes)")
        
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
        
        # Group by country
        logger.info("\nBy Country:")
        countries = {}
        for r in self.results:
            country = r["country"]
            if country not in countries:
                countries[country] = {"success": 0, "failed": 0, "matches": 0}
            
            if r["status"] == "success":
                countries[country]["success"] += 1
                countries[country]["matches"] += r["match_count"]
            else:
                countries[country]["failed"] += 1
        
        for country, stats in sorted(countries.items()):
            logger.info(f"  {country.upper()}: {stats['success']} successful, "
                       f"{stats['matches']} matches")
        
        # Detailed results
        logger.info("\nDetailed Results:")
        for r in self.results:
            if r["status"] == "success":
                status_icon = "✅"
                status_text = f"{r['match_count']} matches"
            elif r["status"] == "no_data":
                status_icon = "⚠️"
                status_text = "No data found"
            else:
                status_icon = "❌"
                status_text = f"Failed: {r.get('error', 'Unknown error')[:50]}"
            
            logger.info(f"  {r['country']}/{r['season']}: {status_text} "
                       f"(Pages: {r['pages_found']}) {status_icon}")
        
        logger.info(f"\n📊 Grand Total: {total_matches:,} matches collected")
        logger.info(f"📁 Output directory: {OUTPUT_DIR}")
        
        if successful == len(self.results):
            logger.info("\n✅ All collections successful!")
        elif successful > 0:
            logger.info(f"\n⚠️ Partial success: {successful}/{len(self.results)} seasons collected")
        else:
            logger.info("\n❌ Collection failed")


async def main():
    """Main entry point"""
    collector = MissingLeaguesCollector()
    await collector.collect_all()


if __name__ == "__main__":
    asyncio.run(main())