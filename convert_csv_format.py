#!/usr/bin/env python3
"""
Convert Type A CSV files (with match_url column) to Type B format.
Type A: Each bookmaker has its own row
Type B: One row per match with JSON array of bookmaker data
"""

import pandas as pd
import json
import os
import re
from pathlib import Path

def extract_threshold_from_filename(filename):
    """Extract threshold value from filename (e.g., 2.5, 3.0, 3.5)"""
    match = re.search(r'_(\d\.\d)\.csv$', filename)
    if match:
        return match.group(1).replace('.', '_')
    return None

def convert_type_a_to_type_b(input_file):
    """Convert a Type A CSV file to Type B format"""
    print(f"Converting {input_file}...")
    
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    # Check if this is actually a Type A file
    if 'match_url' not in df.columns:
        print(f"Skipping {input_file} - not a Type A file")
        return
    
    # Group by match (using match_date, home_team, away_team as key)
    grouped = df.groupby(['scraped_date', 'match_date', 'home_team', 'away_team', 
                         'league_name', 'home_score', 'away_score', 'partial_results',
                         'venue', 'venue_country', 'venue_town'])
    
    converted_rows = []
    
    for group_key, group_df in grouped:
        # Extract match info from group key
        scraped_date, match_date, home_team, away_team, league_name, home_score, away_score, partial_results, venue, venue_country, venue_town = group_key
        
        # Create JSON array of bookmaker data
        bookmaker_data = []
        for _, row in group_df.iterrows():
            bookmaker_info = {
                'odds_over': str(row['odds_over']),
                'odds_under': str(row['odds_under']),
                'bookmaker_name': row['bookmaker_name'],
                'period': row['period']
            }
            bookmaker_data.append(bookmaker_info)
        
        # Determine the market column name based on filename
        filename = os.path.basename(input_file)
        threshold = extract_threshold_from_filename(filename)
        market_column_name = f"over_under_{threshold}_market" if threshold else "over_under_market"
        
        # Create the converted row
        converted_row = {
            'scraped_date': scraped_date,
            'match_date': match_date,
            'home_team': home_team,
            'away_team': away_team,
            'league_name': league_name,
            'home_score': home_score,
            'away_score': away_score,
            'partial_results': partial_results,
            'venue': venue,
            'venue_town': venue_town,  # Note: order changed from Type A
            'venue_country': venue_country,  # Note: order changed from Type A
            market_column_name: json.dumps(bookmaker_data)
        }
        converted_rows.append(converted_row)
    
    # Create new DataFrame
    converted_df = pd.DataFrame(converted_rows)
    
    # Save back to the same file
    converted_df.to_csv(input_file, index=False)
    print(f"Converted {input_file} - {len(converted_rows)} matches from {len(df)} bookmaker entries")

def main():
    """Main function to convert all Type A files"""
    data_dir = "/Users/mac/Desktop/HIPO/oddsportal/oddssc/origin/OddsHarvester/data"
    
    # List of Type A files (files with match_url column)
    type_a_files = [
        # Denmark Superliga
        "denmark-superliga_2019_2020_2.5.csv",
        "denmark-superliga_2019_2020_3.0.csv",
        "denmark-superliga_2019_2020_3.5.csv",
        "denmark-superliga_2020_2021_2.5.csv",
        "denmark-superliga_2020_2021_3.0.csv",
        "denmark-superliga_2020_2021_3.5.csv",
        "denmark-superliga_2021_2022_2.5.csv",
        "denmark-superliga_2021_2022_3.0.csv",
        "denmark-superliga_2021_2022_3.5.csv",
        "denmark-superliga_2022_2023_2.5.csv",
        "denmark-superliga_2022_2023_3.0.csv",
        "denmark-superliga_2022_2023_3.5.csv",
        # Eredivisie
        "eredivisie_2020_2021_3.0.csv",
        "eredivisie_2020_2021_3.5.csv",
        "eredivisie_2021_2022_2.5.csv",
        "eredivisie_2021_2022_3.0.csv",
        # Liga Portugal
        "liga-portugal_2020_2021_2.5.csv",
        "liga-portugal_2020_2021_3.0.csv",
        "liga-portugal_2020_2021_3.5.csv",
    ]
    
    for filename in type_a_files:
        file_path = os.path.join(data_dir, filename)
        if os.path.exists(file_path):
            try:
                convert_type_a_to_type_b(file_path)
            except Exception as e:
                print(f"Error converting {filename}: {e}")
        else:
            print(f"File not found: {file_path}")
    
    print("Conversion completed!")

if __name__ == "__main__":
    main()