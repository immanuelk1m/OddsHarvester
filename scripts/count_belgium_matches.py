#!/usr/bin/env python3
"""
Simple script to count actual matches on Belgium 2023-2024 page
"""

import asyncio
import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.core.odds_portal_scraper import OddsPortalScraper
from src.core.playwright_manager import PlaywrightManager
from src.core.browser_helper import BrowserHelper
from src.core.odds_portal_market_extractor import OddsPortalMarketExtractor
from src.core.sport_market_registry import SportMarketRegistrar
from src.utils.setup_logging import setup_logger

# Setup logging
setup_logger(log_level=logging.INFO, save_to_file=False)
logger = logging.getLogger("MatchCounter")

# Register markets
SportMarketRegistrar.register_all_markets()


async def count_matches():
    """Count matches on each page"""
    
    playwright_manager = PlaywrightManager()
    browser_helper = BrowserHelper()
    market_extractor = OddsPortalMarketExtractor(browser_helper=browser_helper)
    
    scraper = OddsPortalScraper(
        playwright_manager=playwright_manager,
        browser_helper=browser_helper,
        market_extractor=market_extractor,
        preview_submarkets_only=True
    )
    
    try:
        # Start playwright
        await scraper.start_playwright(
            headless=False,
            browser_locale_timezone="en-US",
            browser_timezone_id="America/New_York"
        )
        
        # Build URL
        base_url = "https://www.oddsportal.com/football/belgium/jupiler-pro-league-2023-2024/results/"
        logger.info(f"URL: {base_url}")
        
        # Navigate to page
        page = scraper.playwright_manager.page
        
        # First navigate to main page
        await page.goto("https://www.oddsportal.com/", timeout=30000, wait_until="networkidle")
        await page.wait_for_timeout(2000)
        
        # Navigate to Belgium URL
        await page.goto(base_url, timeout=30000, wait_until="networkidle")
        
        # Check for redirect
        current_url = page.url
        if "/pl/" in current_url:
            english_url = current_url.replace("/pl/", "/")
            await page.goto(english_url, timeout=30000, wait_until="networkidle")
        
        # Wait for content
        await page.wait_for_timeout(5000)
        
        # Dismiss popups
        try:
            await browser_helper.dismiss_cookie_banner(page=page)
        except:
            pass
        
        # Get pagination info
        pages_to_scrape = await scraper._get_pagination_info(page=page, max_pages=None)
        logger.info(f"\n{'='*60}")
        logger.info(f"TOTAL PAGES FOUND: {len(pages_to_scrape)}")
        logger.info('='*60)
        
        total_all_links = 0
        total_belgium_links = 0
        
        # Check each page manually
        for page_num in pages_to_scrape[:3]:  # Just check first 3 pages
            logger.info(f"\nPage {page_num}:")
            
            # Navigate to page
            page_url = f"{base_url}#/page/{page_num}"
            await page.goto(page_url, timeout=30000, wait_until="networkidle")
            await page.wait_for_timeout(3000)
            
            # Scroll to load all content
            for i in range(3):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(1500)
            
            # Count all event rows
            all_rows = await page.query_selector_all('div[class*="eventRow"]')
            logger.info(f"  Total event rows: {len(all_rows)}")
            
            # Extract all links
            all_links = await scraper.extract_match_links(page=page)
            logger.info(f"  Total match links extracted: {len(all_links)}")
            
            # Count Belgium-specific links
            belgium_links = []
            other_links = []
            for link in all_links:
                link_lower = link.lower()
                if "belgium" in link_lower or "jupiler" in link_lower:
                    if not any(x in link_lower for x in ['/pl/', 'world-cup', 'euro-', 
                                                         'champions-league', 'europa-', 
                                                         'conference-', 'nations-league']):
                        belgium_links.append(link)
                else:
                    other_links.append(link)
            
            logger.info(f"  Belgium matches: {len(belgium_links)}")
            logger.info(f"  Other matches: {len(other_links)}")
            
            if other_links and len(other_links) <= 10:
                logger.info("  Sample of non-Belgium matches:")
                for i, link in enumerate(other_links[:5], 1):
                    logger.info(f"    {i}. {link}")
            
            total_all_links += len(all_links)
            total_belgium_links += len(belgium_links)
        
        logger.info(f"\n{'='*60}")
        logger.info("SUMMARY FOR FIRST 3 PAGES:")
        logger.info(f"  Total matches found: {total_all_links}")
        logger.info(f"  Belgium matches: {total_belgium_links}")
        logger.info(f"  Non-Belgium matches: {total_all_links - total_belgium_links}")
        
        # Expected for full season
        if len(pages_to_scrape) == 7:
            # First 6 pages should have 50 each, last page partial
            expected_belgium = total_belgium_links / 3 * 6.5  # Rough estimate
            logger.info(f"\nEstimated total for all {len(pages_to_scrape)} pages: ~{int(expected_belgium)} Belgium matches")
        
        await scraper.stop_playwright()
        
    except Exception as e:
        logger.error(f"ERROR: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        try:
            await scraper.stop_playwright()
        except:
            pass


if __name__ == "__main__":
    asyncio.run(count_matches())