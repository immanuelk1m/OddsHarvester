#!/usr/bin/env python
"""
Test last page collection for all 13 European leagues' 2021 season
Runs with 4 parallel processes and detailed logging
"""

import asyncio
import csv
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pytest
from bs4 import BeautifulSoup

from src.core.browser_helper import BrowserHelper
from src.core.odds_portal_market_extractor import OddsPortalMarketExtractor
from src.core.odds_portal_scraper import OddsPortalScraper
from src.core.playwright_manager import PlaywrightManager
from src.core.sport_market_registry import SportMarketRegistrar
from src.core.url_builder import URLBuilder
from src.utils.setup_logging import setup_logger

# Register all markets
SportMarketRegistrar.register_all_markets()

# Create directories for logs and results
BASE_LOG_DIR = Path("test_logs/last_page_2019_2020")
TEST_RESULTS_DIR = Path("test_results")
BASE_LOG_DIR.mkdir(parents=True, exist_ok=True)
TEST_RESULTS_DIR.mkdir(exist_ok=True)

# Summary log file
SUMMARY_LOG = BASE_LOG_DIR / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
CSV_OUTPUT = TEST_RESULTS_DIR / f"last_page_matches_2019_2020_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

# Initialize CSV file with headers
with open(CSV_OUTPUT, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'country', 'league_id', 'season', 'last_page_num', 
        'matches_on_last_page', 'test_duration_sec', 'status', 'error_message'
    ])
    writer.writeheader()

# League configurations for complete seasons with more data
LEAGUES_2021 = [
    ("belgium", "belgium-jupiler-pro-league", "2019-2020"),  # Complete season
    ("switzerland", "switzerland-super-league", "2019-2020"),  # Complete season
    ("england", "england-premier-league", "2019-2020"),  # Complete season
    ("italy", "italy-serie-a", "2019-2020"),  # Complete season
    ("spain", "spain-laliga", "2019-2020"),  # Complete season
    ("sweden", "sweden-allsvenskan", "2019"),  # Single year format, complete
    ("france", "france-ligue-1", "2019-2020"),  # Complete season
    ("portugal", "portugal-liga-portugal", "2019-2020"),  # Complete season
    ("norway", "norway-eliteserien", "2019"),  # Single year format, complete
    ("denmark", "denmark-superliga", "2019-2020"),  # Complete season
    ("germany", "germany-bundesliga", "2019-2020"),  # Complete season
    ("netherlands", "netherlands-eredivisie", "2019-2020"),  # Complete season
    ("scotland", "scotland-premiership", "2019-2020"),  # Complete season
]


def setup_league_logger(country: str, league_id: str, season: str) -> logging.Logger:
    """
    Setup individual logger for each league test
    
    Args:
        country: Country name
        league_id: League identifier
        season: Season being tested
        
    Returns:
        Configured logger instance
    """
    log_name = f"{country}_{season.replace('-', '_')}"
    log_file = BASE_LOG_DIR / f"{log_name}.log"
    
    # Create logger
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers
    logger.handlers = []
    
    # File handler with detailed formatting
    file_handler = logging.FileHandler(log_file, mode='w')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler for INFO and above
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        f'[{country}] %(levelname)s: %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger


def log_to_summary(message: str, level: str = "INFO"):
    """Write to summary log file"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(SUMMARY_LOG, 'a') as f:
        f.write(f"[{timestamp}] {level}: {message}\n")


def save_test_result(result: Dict):
    """Save test result to CSV"""
    with open(CSV_OUTPUT, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'country', 'league_id', 'season', 'last_page_num', 
            'matches_on_last_page', 'test_duration_sec', 'status', 'error_message'
        ])
        writer.writerow(result)


class TestLastPageCollection2021:
    """Test collection from last page of 2019-2020 season for all leagues"""
    
    @pytest.mark.parametrize("country,league_id,season", LEAGUES_2021)
    @pytest.mark.asyncio
    async def test_last_page_collection(self, country: str, league_id: str, season: str):
        """
        Test collecting match URLs from the last page of a league's 2021 season
        
        Args:
            country: Country name for logging
            league_id: League identifier
            season: Season to test (2020-2021 or 2021)
        """
        # Setup individual logger
        logger = setup_league_logger(country, league_id, season)
        
        # Track test execution time
        start_time = time.time()
        
        # Initialize test result
        test_result = {
            'country': country,
            'league_id': league_id,
            'season': season,
            'last_page_num': 0,
            'matches_on_last_page': 0,
            'test_duration_sec': 0,
            'status': 'FAILED',
            'error_message': ''
        }
        
        # Initialize scraper components
        playwright_manager = None
        scraper = None
        
        try:
            logger.info(f"Starting test for {country} - {league_id} - {season}")
            log_to_summary(f"Starting test: {country} - {league_id} - {season}")
            
            # Initialize components
            logger.debug("Initializing scraper components...")
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
            logger.debug("Starting Playwright browser...")
            await scraper.start_playwright(headless=True)
            
            # Build URL for the league's 2021 season
            base_url = URLBuilder.get_historic_matches_url(
                sport="football",
                league=league_id,
                season=season
            )
            logger.info(f"Base URL: {base_url}")
            
            # Navigate to the results page
            page = playwright_manager.page
            logger.debug(f"Navigating to results page...")
            nav_start = time.time()
            await page.goto(base_url, timeout=30000, wait_until="domcontentloaded")
            await page.wait_for_timeout(5000)  # Wait for dynamic content to fully load
            nav_duration = time.time() - nav_start
            logger.info(f"Page loaded in {nav_duration:.2f}s")
            
            # Get pagination information
            logger.debug("Analyzing pagination...")
            pagination_start = time.time()
            pages_list = await scraper._get_pagination_info(page=page, max_pages=None)
            pagination_duration = time.time() - pagination_start
            
            if not pages_list or len(pages_list) == 0:
                raise ValueError("No pagination found - unable to determine last page")
            
            last_page_num = max(pages_list)
            logger.info(f"Found {len(pages_list)} total pages, last page is {last_page_num}")
            logger.debug(f"Pagination analysis took {pagination_duration:.2f}s")
            
            # Navigate directly to the last page
            if last_page_num > 1:
                last_page_url = f"{base_url}#/page/{last_page_num}"
                logger.info(f"Navigating to last page: {last_page_url}")
                
                nav_start = time.time()
                await page.goto(last_page_url, timeout=30000, wait_until="domcontentloaded")
                await page.wait_for_timeout(5000)  # Wait for content to fully load
                nav_duration = time.time() - nav_start
                logger.debug(f"Last page loaded in {nav_duration:.2f}s")
            else:
                logger.info("Only one page found, already on last page")
            
            # Scroll to load all content on the page
            logger.debug("Scrolling to load all content...")
            scroll_start = time.time()
            await browser_helper.scroll_until_loaded(
                page=page,
                timeout=30,
                scroll_pause_time=2,
                max_scroll_attempts=3,
                content_check_selector="div[class*='eventRow']"
            )
            scroll_duration = time.time() - scroll_start
            logger.debug(f"Scrolling completed in {scroll_duration:.2f}s")
            
            # Extract match URLs from the last page
            logger.info("Extracting match URLs from last page...")
            extract_start = time.time()
            match_urls = await scraper.extract_match_links(page=page)
            extract_duration = time.time() - extract_start
            
            matches_count = len(match_urls)
            logger.info(f"Found {matches_count} matches on last page")
            logger.debug(f"Extraction took {extract_duration:.2f}s")
            
            # Log sample matches (first 3)
            if match_urls:
                logger.info("Sample match URLs:")
                for i, url in enumerate(match_urls[:3], 1):
                    logger.info(f"  {i}. {url}")
                if matches_count > 3:
                    logger.info(f"  ... and {matches_count - 3} more matches")
            
            # Validate match URLs
            valid_urls = [url for url in match_urls if url.startswith("https://www.oddsportal.com")]
            if len(valid_urls) != matches_count:
                logger.warning(f"Found {matches_count - len(valid_urls)} invalid URLs")
            
            # Test assertions - requiring at least 3 pages
            assert last_page_num >= 3, f"Last page should be at least 3 (found: {last_page_num})"
            assert matches_count > 0, "Should find matches on the last page"
            assert len(valid_urls) > 0, "Should have at least one valid match URL"
            
            # Update test result
            test_duration = time.time() - start_time
            test_result.update({
                'last_page_num': last_page_num,
                'matches_on_last_page': matches_count,
                'test_duration_sec': round(test_duration, 2),
                'status': 'SUCCESS',
                'error_message': ''
            })
            
            logger.info(f"✅ Test completed successfully in {test_duration:.2f}s")
            logger.info(f"Summary: Last page={last_page_num}, Matches={matches_count}")
            log_to_summary(f"SUCCESS: {country} - Page {last_page_num} - {matches_count} matches - {test_duration:.2f}s")
            
        except Exception as e:
            test_duration = time.time() - start_time
            error_msg = str(e)
            
            logger.error(f"❌ Test failed: {error_msg}", exc_info=True)
            log_to_summary(f"FAILED: {country} - {error_msg}", "ERROR")
            
            test_result.update({
                'test_duration_sec': round(test_duration, 2),
                'status': 'FAILED',
                'error_message': error_msg[:200]  # Truncate long error messages
            })
            
            # Re-raise for pytest to handle
            raise
            
        finally:
            # Cleanup
            if scraper:
                try:
                    logger.debug("Cleaning up Playwright resources...")
                    await scraper.stop_playwright()
                except Exception as cleanup_error:
                    logger.warning(f"Error during cleanup: {cleanup_error}")
            
            # Save result to CSV
            save_test_result(test_result)
            
            # Log separator for readability
            logger.info("=" * 60)


@pytest.fixture(scope="session", autouse=True)
def session_setup_teardown():
    """Setup and teardown for the entire test session"""
    # Setup
    log_to_summary("=" * 80)
    log_to_summary("LAST PAGE COLLECTION TEST - 2019-2020 COMPLETE SEASONS")
    log_to_summary(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_to_summary(f"Testing {len(LEAGUES_2021)} leagues (expecting 3+ pages each)")
    log_to_summary("=" * 80)
    
    yield
    
    # Teardown - Generate summary report
    log_to_summary("=" * 80)
    log_to_summary("TEST SESSION COMPLETED")
    
    # Read CSV to generate summary
    try:
        with open(CSV_OUTPUT, 'r') as f:
            reader = csv.DictReader(f)
            results = list(reader)
        
        success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
        failed_count = sum(1 for r in results if r['status'] == 'FAILED')
        total_matches = sum(int(r['matches_on_last_page']) for r in results if r['matches_on_last_page'])
        total_duration = sum(float(r['test_duration_sec']) for r in results if r['test_duration_sec'])
        
        log_to_summary(f"Total tests: {len(results)}")
        log_to_summary(f"Successful: {success_count}")
        log_to_summary(f"Failed: {failed_count}")
        log_to_summary(f"Success rate: {(success_count/len(results)*100):.1f}%")
        log_to_summary(f"Total matches collected: {total_matches}")
        log_to_summary(f"Total execution time: {total_duration:.2f}s")
        log_to_summary(f"Average time per test: {(total_duration/len(results)):.2f}s")
        
        # Log failed tests
        if failed_count > 0:
            log_to_summary("\nFailed tests:")
            for r in results:
                if r['status'] == 'FAILED':
                    log_to_summary(f"  - {r['country']}: {r['error_message']}")
        
    except Exception as e:
        log_to_summary(f"Error generating summary: {e}", "ERROR")
    
    log_to_summary(f"Ended at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_to_summary(f"Results saved to: {CSV_OUTPUT}")
    log_to_summary(f"Logs directory: {BASE_LOG_DIR}")
    
    # Check if all leagues have 3+ pages
    if results:
        leagues_under_3_pages = [r for r in results if r['status'] == 'SUCCESS' and int(r['last_page_num']) < 3]
        if leagues_under_3_pages:
            log_to_summary("\n⚠️ Leagues with less than 3 pages:")
            for r in leagues_under_3_pages:
                log_to_summary(f"  - {r['country']}: only {r['last_page_num']} page(s)")
    log_to_summary("=" * 80)


if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v", "-n", "4", "--tb=short"])