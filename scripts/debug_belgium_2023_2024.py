#!/usr/bin/env python3
"""
Debug script to investigate why 2023-2024 Belgium season shows 313 instead of 321 matches
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
logger = logging.getLogger("BelgiumDebug")

# Register markets
SportMarketRegistrar.register_all_markets()

# Output directory
OUTPUT_DIR = Path("debug_output")
OUTPUT_DIR.mkdir(exist_ok=True)


class BelgiumDebugCollector:
    """Debug collector to understand filtering issues"""
    
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
        
        self.all_links = []
        self.filtered_out = []
        self.valid_links = []
    
    async def debug_collect_2023_2024(self):
        """Debug collection for 2023-2024 season"""
        
        season = "2023-2024"
        league_id = "jupiler-pro-league"
        
        logger.info(f"\n{'='*60}")
        logger.info(f"DEBUG: Belgium {season}")
        logger.info(f"League ID: {league_id}")
        logger.info('='*60)
        
        try:
            # Start playwright
            await self.scraper.start_playwright(
                headless=False,
                browser_locale_timezone="en-US",
                browser_timezone_id="America/New_York"
            )
            
            # Build URL
            base_url = f"https://www.oddsportal.com/football/belgium/{league_id}-{season}/results/"
            logger.info(f"URL: {base_url}")
            
            # Navigate to page
            page = self.scraper.playwright_manager.page
            
            # First navigate to main page
            await page.goto("https://www.oddsportal.com/", timeout=30000, wait_until="networkidle")
            await page.wait_for_timeout(2000)
            
            # Navigate to Belgium URL
            await page.goto(base_url, timeout=30000, wait_until="networkidle")
            
            # Check for redirect
            current_url = page.url
            if "/pl/" in current_url:
                logger.info("Redirected to /pl/, forcing English URL...")
                english_url = current_url.replace("/pl/", "/")
                await page.goto(english_url, timeout=30000, wait_until="networkidle")
                current_url = page.url
            
            logger.info(f"Current URL: {current_url}")
            
            # Wait for content
            await page.wait_for_timeout(7000)
            
            # Dismiss popups
            try:
                await self.browser_helper.dismiss_cookie_banner(page=page)
            except:
                pass
            
            # Scroll to load content
            for i in range(3):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(2000)
            
            # Get pagination info
            pages_to_scrape = await self.scraper._get_pagination_info(page=page, max_pages=None)
            logger.info(f"Found {len(pages_to_scrape)} pages: {pages_to_scrape}")
            
            if len(pages_to_scrape) > 1:
                # Collect from all pages
                logger.info("Using built-in pagination handler...")
                match_links = await self.scraper._collect_match_links(
                    base_url=base_url,
                    pages_to_scrape=pages_to_scrape,
                    max_matches=None
                )
            else:
                # Single page
                logger.info("Single page collection...")
                for i in range(5):
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await page.wait_for_timeout(1500)
                match_links = await self.scraper.extract_match_links(page=page)
            
            logger.info(f"\nTotal links extracted: {len(match_links)}")
            self.all_links = match_links
            
            # Analyze each link
            logger.info("\n" + "="*60)
            logger.info("ANALYZING ALL EXTRACTED LINKS")
            logger.info("="*60)
            
            for i, link in enumerate(match_links, 1):
                link_lower = link.lower()
                is_belgium = "belgium" in link_lower or "jupiler" in link_lower
                
                excluded_patterns = ['/pl/', 'saudi-arabia', 'world-cup', 
                                   'copa-', 'euro-', 'champions-league',
                                   'europa-', 'conference-', 'nations-league']
                has_excluded = any(x in link_lower for x in excluded_patterns)
                
                if is_belgium and not has_excluded:
                    self.valid_links.append(link)
                    status = "✅ VALID"
                else:
                    self.filtered_out.append({
                        'url': link,
                        'is_belgium': is_belgium,
                        'has_excluded': has_excluded,
                        'excluded_pattern': [x for x in excluded_patterns if x in link_lower]
                    })
                    status = "❌ FILTERED"
                
                # Log first 10 and last 10 for brevity
                if i <= 10 or i > len(match_links) - 10:
                    logger.info(f"{i:3}. {status} | Belgium: {is_belgium} | Excluded: {has_excluded} | {link[:100]}")
                elif i == 11:
                    logger.info("     ... (showing first 10 and last 10 only) ...")
            
            # Remove duplicates from valid links
            seen = set()
            unique_valid = []
            for url in self.valid_links:
                if url not in seen:
                    seen.add(url)
                    unique_valid.append(url)
            
            # Summary
            logger.info("\n" + "="*60)
            logger.info("SUMMARY")
            logger.info("="*60)
            logger.info(f"Total links extracted: {len(match_links)}")
            logger.info(f"Valid Belgium matches: {len(self.valid_links)}")
            logger.info(f"Unique valid matches: {len(unique_valid)}")
            logger.info(f"Filtered out: {len(self.filtered_out)}")
            
            # Save debug data
            debug_file = OUTPUT_DIR / "belgium_2023_2024_debug.json"
            with open(debug_file, 'w') as f:
                json.dump({
                    'total_extracted': len(match_links),
                    'valid_count': len(self.valid_links),
                    'unique_valid_count': len(unique_valid),
                    'filtered_count': len(self.filtered_out),
                    'filtered_details': self.filtered_out[:20],  # First 20 filtered
                    'sample_valid': unique_valid[:10],  # First 10 valid
                    'pages_found': len(pages_to_scrape)
                }, f, indent=2)
            
            logger.info(f"\nDebug data saved to: {debug_file}")
            
            # If we have filtered items, show why
            if self.filtered_out:
                logger.info("\n" + "="*60)
                logger.info("FILTERED OUT DETAILS (First 20)")
                logger.info("="*60)
                for i, item in enumerate(self.filtered_out[:20], 1):
                    logger.info(f"{i}. {item['url'][:80]}")
                    logger.info(f"   Belgium: {item['is_belgium']} | Pattern: {item['excluded_pattern']}")
            
            # Save the valid URLs to CSV for comparison
            output_file = OUTPUT_DIR / "belgium_2023_2024_debug.csv"
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["league", "season", "match_url"])
                for url in unique_valid:
                    writer.writerow(["Belgium Pro League", season, url])
            
            logger.info(f"Valid matches saved to: {output_file}")
            logger.info(f"\n✅ Found {len(unique_valid)} unique valid Belgium matches")
            
            await self.scraper.stop_playwright()
            
        except Exception as e:
            logger.error(f"❌ ERROR: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            try:
                await self.scraper.stop_playwright()
            except:
                pass


async def main():
    """Main entry point"""
    collector = BelgiumDebugCollector()
    await collector.debug_collect_2023_2024()


if __name__ == "__main__":
    asyncio.run(main())