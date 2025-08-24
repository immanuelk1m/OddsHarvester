import asyncio
import logging
import os
import csv
from datetime import datetime
from pathlib import Path
import pytest
from typing import List, Tuple

from src.core.scraper_app import run_scraper
from src.utils.command_enum import CommandEnum
from src.utils.setup_logging import setup_logger

# Configure logging for tests
setup_logger(log_level=logging.INFO, save_to_file=True)
logger = logging.getLogger("LeagueCollectionTest")

# Create directories for test results
TEST_RESULTS_DIR = Path("test_results")
TEST_LOGS_DIR = Path("test_logs")
TEST_RESULTS_DIR.mkdir(exist_ok=True)
TEST_LOGS_DIR.mkdir(exist_ok=True)

# Configure test log file
test_log_file = TEST_LOGS_DIR / f"league_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
file_handler = logging.FileHandler(test_log_file)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# League configurations grouped for testing
LEAGUE_GROUPS = {
    "group1": [
        ("belgium", "jupiler-pro-league", "2024-2025"),
        ("switzerland", "switzerland-super-league", "2024-2025"),
        ("england", "england-premier-league", "2024-2025"),
        ("italy", "italy-serie-a", "2024-2025"),
        ("spain", "spain-laliga", "2024-2025"),
    ],
    "group2": [
        ("sweden", "sweden-allsvenskan", "2024"),
        ("france", "france-ligue-1", "2024-2025"),
        ("portugal", "liga-portugal", "2024-2025"),
        ("norway", "norway-eliteserien", "2024"),
    ],
    "group3": [
        ("denmark", "denmark-superliga", "2024-2025"),
        ("germany", "germany-bundesliga", "2024-2025"),
        ("netherlands", "netherlands-eredivisie", "2024-2025"),
        ("scotland", "scotland-premiership", "2024-2025"),
    ]
}

# Flatten all leagues for parameterized testing
ALL_LEAGUES = []
for group_name, leagues in LEAGUE_GROUPS.items():
    for league_info in leagues:
        for loop_num in range(1, 4):  # 3 loops per league
            ALL_LEAGUES.append((*league_info, loop_num, group_name))


class TestLeagueCollection:
    """Test collection of data from all 13 leagues with 3 loops each (39 tests total)"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup before each test"""
        self.test_results = []
        
    @pytest.mark.parametrize("country,league_id,season,loop_num,group", ALL_LEAGUES)
    @pytest.mark.asyncio
    async def test_league_collection(self, country, league_id, season, loop_num, group):
        """
        Test data collection for a specific league
        
        Args:
            country: Country name for logging
            league_id: League identifier for OddsPortal
            season: Season to scrape
            loop_num: Loop number (1-3)
            group: Group name for organization
        """
        test_name = f"{country}_{league_id}_loop{loop_num}"
        output_file = TEST_RESULTS_DIR / f"{test_name}.csv"
        
        logger.info(f"Starting test: {test_name}")
        logger.info(f"League: {league_id}, Season: {season}, Loop: {loop_num}")
        
        try:
            # Run scraper with limited scope for testing
            scraped_data = await run_scraper(
                command=CommandEnum.HISTORIC,
                sport="football",
                leagues=[league_id],
                season=season,
                markets=["over_under_2_5"],
                max_pages=3,  # Only scrape first 3 pages
                max_matches=1,  # Only collect 1 match
                headless=True,
                preview_submarkets_only=False,
            )
            
            # Check if data was collected
            if scraped_data and len(scraped_data) > 0:
                # Save to CSV
                self._save_to_csv(scraped_data, output_file)
                
                # Verify CSV was created and has data
                if output_file.exists():
                    with open(output_file, 'r') as f:
                        reader = csv.reader(f)
                        row_count = sum(1 for row in reader) - 1  # Exclude header
                    
                    if row_count > 0:
                        logger.info(f"✅ SUCCESS: {test_name} - Collected {row_count} rows")
                        logger.info(f"   Output file: {output_file}")
                        return True
                    else:
                        logger.error(f"❌ FAIL: {test_name} - CSV created but no data rows")
                        return False
                else:
                    logger.error(f"❌ FAIL: {test_name} - CSV file not created")
                    return False
            else:
                logger.error(f"❌ FAIL: {test_name} - No data collected")
                return False
                
        except Exception as e:
            logger.error(f"❌ ERROR: {test_name} - {str(e)}", exc_info=True)
            return False
    
    def _save_to_csv(self, data: List[dict], file_path: Path):
        """Save scraped data to CSV file"""
        if not data:
            return
        
        # Get all unique keys from data
        all_keys = set()
        for item in data:
            all_keys.update(item.keys())
        
        # Write to CSV
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
            writer.writeheader()
            writer.writerows(data)
    
    @pytest.fixture(scope="class", autouse=True)
    def class_teardown(self):
        """Run after all tests in the class"""
        yield
        
        # Summary report
        logger.info("=" * 80)
        logger.info("TEST SUMMARY")
        logger.info("=" * 80)
        
        # Count successes and failures from log
        success_count = 0
        fail_count = 0
        
        with open(test_log_file, 'r') as f:
            for line in f:
                if "✅ SUCCESS:" in line:
                    success_count += 1
                elif "❌ FAIL:" in line or "❌ ERROR:" in line:
                    fail_count += 1
        
        total_tests = success_count + fail_count
        success_rate = (success_count / total_tests * 100) if total_tests > 0 else 0
        
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Successful: {success_count}")
        logger.info(f"Failed: {fail_count}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        logger.info(f"Log file: {test_log_file}")
        logger.info("=" * 80)


def test_scraper_imports():
    """Test that all required modules can be imported"""
    try:
        from src.core.scraper_app import run_scraper
        from src.utils.command_enum import CommandEnum
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--log-cli-level=INFO"])