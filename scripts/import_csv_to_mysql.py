#!/usr/bin/env python3
"""
Import OddsPortal CSV files to MySQL oddsportal_raw table
"""

import csv
import json
import mysql.connector
from pathlib import Path
from datetime import datetime
import re
from typing import List, Dict, Optional, Tuple
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CSVToMySQLImporter:
    def __init__(self, test_mode: bool = False):
        """
        Initialize importer
        
        Args:
            test_mode: If True, only process first 2 files for testing
        """
        self.test_mode = test_mode
        self.test_marker = "TEST_IMPORT_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        self.connection = None
        self.cursor = None
        
    def connect_db(self):
        """Connect to MySQL database"""
        try:
            self.connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="HIPO",
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            self.cursor = self.connection.cursor()
            logger.info("Successfully connected to MySQL database")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
            
    def disconnect_db(self):
        """Disconnect from MySQL database"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("Disconnected from MySQL database")
        
    def parse_filename(self, filepath: Path) -> Tuple[str, str, float, str]:
        """
        Parse league, season, and outcome_point from filename
        
        Example: belgium-jupiler-pro-league_2019_2020_2.5.csv
        Returns: (league, season, outcome_point, market_type)
        """
        filename = filepath.stem  # Remove .csv
        parts = filename.rsplit('_', 3)  # Split from right
        
        if len(parts) != 4:
            raise ValueError(f"Unexpected filename format: {filename}")
            
        league = parts[0].replace('-', ' ').title()
        year1 = parts[1]
        year2 = parts[2]
        outcome_point = float(parts[3])
        
        # Format season as "YYYY-YYYY" or "YYYY/YYYY"
        season = f"{year1}-{year2}"
        
        # Determine market type (always totals for over/under)
        market_type = "totals"
        
        return league, season, outcome_point, market_type
        
    def parse_csv_row(self, row: Dict, filepath: Path) -> List[Dict]:
        """
        Parse a CSV row and convert to MySQL records
        
        Args:
            row: CSV row as dictionary
            filepath: Path to CSV file for extracting metadata
            
        Returns:
            List of dictionaries ready for MySQL insertion
        """
        records = []
        
        # Extract metadata from filename
        league, season, outcome_point, market_type = self.parse_filename(filepath)
        
        # Parse dates
        match_date = datetime.strptime(row['match_date'].replace(' UTC', ''), '%Y-%m-%d %H:%M:%S')
        scraped_date = datetime.strptime(row['scraped_date'].replace(' UTC', ''), '%Y-%m-%d %H:%M:%S')
        
        # Parse market JSON data
        market_data = row.get('over_under_2_5_market', '[]')
        if market_data and market_data != '[]':
            try:
                bookmakers = json.loads(market_data.replace("'", '"'))
            except json.JSONDecodeError:
                # Try alternative parsing for single quotes
                try:
                    bookmakers = eval(market_data)
                except:
                    logger.warning(f"Failed to parse market data for {row['home_team']} vs {row['away_team']}")
                    bookmakers = []
        else:
            bookmakers = []
            
        # Create records for each bookmaker and outcome
        for bookmaker in bookmakers:
            # Create record for Over
            if 'odds_over' in bookmaker:
                record_over = {
                    'league_name': row.get('league_name', league),
                    'sport_key': 'soccer',  # Default for football/soccer
                    'season': season,
                    'bookmaker_title': bookmaker['bookmaker_name'],
                    'market_key': market_type,
                    'home_team_id': None,
                    'away_team_id': None,
                    'issue': 0,
                    'commence_time': match_date,
                    'id': self.test_marker if self.test_mode else None,  # Mark test records
                    'home_team': row['home_team'],
                    'away_team': row['away_team'],
                    'bookmaker_key': bookmaker['bookmaker_name'].lower().replace(' ', '_').replace('.', '_'),
                    'outcome_name': 'Over',
                    'outcome_point': outcome_point,
                    'outcome_price': float(bookmaker['odds_over']),
                    'snapshot_time': scraped_date,
                    'rejected_over_5': 0,
                    'rejection_reason': None
                }
                records.append(record_over)
                
            # Create record for Under
            if 'odds_under' in bookmaker:
                record_under = {
                    'league_name': row.get('league_name', league),
                    'sport_key': 'soccer',
                    'season': season,
                    'bookmaker_title': bookmaker['bookmaker_name'],
                    'market_key': market_type,
                    'home_team_id': None,
                    'away_team_id': None,
                    'issue': 0,
                    'commence_time': match_date,
                    'id': self.test_marker if self.test_mode else None,
                    'home_team': row['home_team'],
                    'away_team': row['away_team'],
                    'bookmaker_key': bookmaker['bookmaker_name'].lower().replace(' ', '_').replace('.', '_'),
                    'outcome_name': 'Under',
                    'outcome_point': outcome_point,
                    'outcome_price': float(bookmaker['odds_under']),
                    'snapshot_time': scraped_date,
                    'rejected_over_5': 0,
                    'rejection_reason': None
                }
                records.append(record_under)
                
        return records
        
    def insert_records(self, records: List[Dict]) -> int:
        """
        Insert records into MySQL database
        
        Args:
            records: List of dictionaries to insert
            
        Returns:
            Number of records inserted
        """
        if not records:
            return 0
            
        # SQL insert statement with ON DUPLICATE KEY UPDATE
        sql = """
        INSERT INTO oddsportal_raw (
            league_name, sport_key, season, bookmaker_title, market_key,
            home_team_id, away_team_id, issue, commence_time, id,
            home_team, away_team, bookmaker_key, outcome_name, outcome_point,
            outcome_price, snapshot_time, rejected_over_5, rejection_reason
        ) VALUES (
            %(league_name)s, %(sport_key)s, %(season)s, %(bookmaker_title)s, %(market_key)s,
            %(home_team_id)s, %(away_team_id)s, %(issue)s, %(commence_time)s, %(id)s,
            %(home_team)s, %(away_team)s, %(bookmaker_key)s, %(outcome_name)s, %(outcome_point)s,
            %(outcome_price)s, %(snapshot_time)s, %(rejected_over_5)s, %(rejection_reason)s
        ) ON DUPLICATE KEY UPDATE
            outcome_price = VALUES(outcome_price),
            snapshot_time = VALUES(snapshot_time)
        """
        
        inserted = 0
        batch_size = 100
        
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]
            try:
                self.cursor.executemany(sql, batch)
                self.connection.commit()
                inserted += len(batch)
            except Exception as e:
                logger.error(f"Failed to insert batch: {e}")
                self.connection.rollback()
                
        return inserted
        
    def process_csv_file(self, filepath: Path) -> Tuple[int, int]:
        """
        Process a single CSV file
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            Tuple of (rows_processed, records_inserted)
        """
        logger.info(f"Processing: {filepath.name}")
        
        rows_processed = 0
        all_records = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    rows_processed += 1
                    records = self.parse_csv_row(row, filepath)
                    all_records.extend(records)
                    
            # Insert all records for this file
            records_inserted = self.insert_records(all_records)
            
            logger.info(f"  Processed {rows_processed} rows, inserted {records_inserted} records")
            return rows_processed, records_inserted
            
        except Exception as e:
            logger.error(f"  Error processing {filepath.name}: {e}")
            return rows_processed, 0
            
    def remove_test_data(self):
        """Remove test data from database"""
        if not self.test_mode:
            logger.warning("Not in test mode, skipping test data removal")
            return
            
        logger.info(f"Removing test data with marker: {self.test_marker}")
        
        try:
            sql = "DELETE FROM oddsportal_raw WHERE id = %s"
            self.cursor.execute(sql, (self.test_marker,))
            deleted = self.cursor.rowcount
            self.connection.commit()
            logger.info(f"Removed {deleted} test records")
        except Exception as e:
            logger.error(f"Failed to remove test data: {e}")
            self.connection.rollback()
            
    def run(self):
        """Run the import process"""
        data_dir = Path("/Users/mac/Desktop/HIPO/oddsportal/oddssc/origin/OddsHarvester/data")
        
        if not data_dir.exists():
            logger.error(f"Data directory not found: {data_dir}")
            return
            
        # Get all CSV files
        csv_files = sorted(list(data_dir.glob("*.csv")))
        
        # Filter out non-match CSV files
        csv_files = [f for f in csv_files if '_' in f.stem and not f.name.startswith('csv_row_counts')]
        
        if self.test_mode:
            logger.info(f"TEST MODE: Processing only first 2 files")
            csv_files = csv_files[:2]
        else:
            logger.info(f"Found {len(csv_files)} CSV files to process")
            
        # Connect to database
        self.connect_db()
        
        # Process files
        total_rows = 0
        total_records = 0
        
        for i, filepath in enumerate(csv_files, 1):
            logger.info(f"[{i}/{len(csv_files)}] {filepath.name}")
            rows, records = self.process_csv_file(filepath)
            total_rows += rows
            total_records += records
            
        logger.info(f"\nSummary: Processed {total_rows} CSV rows, inserted {total_records} database records")
        
        # Verify insertion if in test mode
        if self.test_mode:
            self.verify_test_data()
            
        # Disconnect
        self.disconnect_db()
        
    def verify_test_data(self):
        """Verify test data was inserted correctly"""
        logger.info("\nVerifying test data...")
        
        try:
            sql = "SELECT COUNT(*) FROM oddsportal_raw WHERE id = %s"
            self.cursor.execute(sql, (self.test_marker,))
            count = self.cursor.fetchone()[0]
            logger.info(f"Found {count} test records in database")
            
            # Show sample records
            sql = """
            SELECT league_name, home_team, away_team, bookmaker_title, 
                   outcome_name, outcome_point, outcome_price
            FROM oddsportal_raw 
            WHERE id = %s 
            LIMIT 5
            """
            self.cursor.execute(sql, (self.test_marker,))
            samples = self.cursor.fetchall()
            
            logger.info("\nSample test records:")
            for sample in samples:
                logger.info(f"  {sample}")
                
        except Exception as e:
            logger.error(f"Failed to verify test data: {e}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Import OddsPortal CSV files to MySQL')
    parser.add_argument('--test', action='store_true', help='Run in test mode with 2 files')
    parser.add_argument('--remove-test', action='store_true', help='Remove test data')
    parser.add_argument('--full', action='store_true', help='Run full import')
    
    args = parser.parse_args()
    
    if args.remove_test:
        # Remove test data
        logger.info("=== REMOVING TEST DATA ===")
        importer = CSVToMySQLImporter(test_mode=True)
        importer.connect_db()
        importer.remove_test_data()
        importer.disconnect_db()
        
    elif args.full:
        # Full import
        logger.info("=== FULL IMPORT MODE ===")
        importer = CSVToMySQLImporter(test_mode=False)
        importer.run()
        
    else:
        # Test mode (default)
        logger.info("=== TEST MODE ===")
        importer = CSVToMySQLImporter(test_mode=True)
        importer.run()
        
        # Ask if user wants to remove test data
        response = input("\nRemove test data? (y/n): ")
        if response.lower() == 'y':
            importer.connect_db()
            importer.remove_test_data()
            importer.disconnect_db()
            
            # Ask if user wants to run full import
            response = input("\nRun full import? (y/n): ")
            if response.lower() == 'y':
                logger.info("\n=== STARTING FULL IMPORT ===")
                full_importer = CSVToMySQLImporter(test_mode=False)
                full_importer.run()


if __name__ == "__main__":
    main()