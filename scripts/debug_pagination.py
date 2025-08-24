#!/usr/bin/env python
"""
Debug pagination for specific leagues
"""

import asyncio
import logging
from pathlib import Path

from src.core.browser_helper import BrowserHelper
from src.core.odds_portal_market_extractor import OddsPortalMarketExtractor
from src.core.odds_portal_scraper import OddsPortalScraper
from src.core.playwright_manager import PlaywrightManager
from src.core.sport_market_registry import SportMarketRegistrar
from src.core.url_builder import URLBuilder
from src.utils.setup_logging import setup_logger

# Setup logging
setup_logger(log_level=logging.DEBUG, save_to_file=False)
logger = logging.getLogger("PaginationDebug")

# Register markets
SportMarketRegistrar.register_all_markets()


async def debug_league_pagination(country: str, league_id: str, season: str):
    """Debug pagination for a specific league"""
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Debugging: {country} - {league_id} - {season}")
    logger.info(f"{'='*60}")
    
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
    
    try:
        # Start playwright
        await scraper.start_playwright(headless=True)
        
        # Build URL
        base_url = URLBuilder.get_historic_matches_url(
            sport="football",
            league=league_id,
            season=season
        )
        logger.info(f"URL: {base_url}")
        
        # Navigate to page
        page = playwright_manager.page
        await page.goto(base_url, timeout=20000, wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)  # Extra wait for dynamic content
        
        # Try to find pagination with different methods
        logger.info("\n🔍 Method 1: Looking for all <a> tags with href containing '#/page/'")
        page_links = await page.query_selector_all("a[href*='#/page/']")
        if page_links:
            logger.info(f"   Found {len(page_links)} links with #/page/ in href")
            for i, link in enumerate(page_links[:5], 1):  # Show first 5
                href = await link.get_attribute("href")
                text = await link.inner_text()
                logger.info(f"   {i}. Text: '{text}', Href: {href}")
        else:
            logger.warning("   No links found with #/page/ in href")
        
        logger.info("\n🔍 Method 2: Looking for div with class containing 'pagination'")
        pagination_divs = await page.query_selector_all("div[class*='pagination']")
        if pagination_divs:
            logger.info(f"   Found {len(pagination_divs)} divs with 'pagination' in class")
            for div in pagination_divs:
                class_name = await div.get_attribute("class")
                logger.info(f"   Class: {class_name}")
                # Check children
                children = await div.query_selector_all("a")
                if children:
                    logger.info(f"     Contains {len(children)} <a> tags")
        else:
            logger.warning("   No divs found with 'pagination' in class")
        
        logger.info("\n🔍 Method 3: Looking for any element with pagination-related classes")
        selectors = [
            ".pagination",
            ".paginator", 
            ".pages",
            "[class*='page-']",
            "nav.pagination",
            "ul.pagination"
        ]
        
        for selector in selectors:
            elements = await page.query_selector_all(selector)
            if elements:
                logger.info(f"   Selector '{selector}': Found {len(elements)} elements")
            else:
                logger.debug(f"   Selector '{selector}': No elements found")
        
        logger.info("\n🔍 Method 4: Checking page HTML structure")
        # Get a sample of the HTML to understand structure
        html_content = await page.content()
        
        # Look for pagination patterns in HTML
        if "pagination" in html_content.lower():
            logger.info("   ✓ Found 'pagination' text in HTML")
            # Find context around pagination
            import re
            matches = re.findall(r'.{0,100}pagination.{0,100}', html_content.lower())
            if matches:
                logger.info(f"   Sample context: {matches[0][:200]}...")
        else:
            logger.warning("   ✗ No 'pagination' text found in HTML")
        
        if "#/page/" in html_content:
            logger.info("   ✓ Found '#/page/' pattern in HTML")
            # Count occurrences
            count = html_content.count("#/page/")
            logger.info(f"   Found {count} occurrences of '#/page/'")
        else:
            logger.warning("   ✗ No '#/page/' pattern found in HTML")
        
        logger.info("\n🔍 Method 5: Using scraper's _get_pagination_info")
        pages = await scraper._get_pagination_info(page=page, max_pages=None)
        logger.info(f"   Scraper found pages: {pages}")
        
        # Also check for match links
        logger.info("\n📊 Checking for match links")
        match_links = await scraper.extract_match_links(page=page)
        logger.info(f"   Found {len(match_links)} match links on current page")
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        await scraper.stop_playwright()
    
    logger.info(f"\n{'='*60}\n")


async def main():
    """Debug problematic leagues"""
    
    # Test problematic leagues
    problematic_leagues = [
        ("belgium", "belgium-jupiler-pro-league", "2019-2020"),
        ("spain", "spain-laliga", "2019-2020"),
    ]
    
    # Also test a working league for comparison
    working_league = ("england", "england-premier-league", "2019-2020")
    
    logger.info("Testing working league first for comparison...")
    await debug_league_pagination(*working_league)
    
    logger.info("\nNow testing problematic leagues...")
    for league in problematic_leagues:
        await debug_league_pagination(*league)


if __name__ == "__main__":
    asyncio.run(main())