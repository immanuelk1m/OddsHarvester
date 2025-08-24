#!/usr/bin/env python3
"""
Test conversion script on a single file
"""

import pandas as pd
import json
import os
import re

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
    print(f"Original file has {len(df)} rows")
    print(f"Columns: {list(df.columns)}")
    
    # Check if this is actually a Type A file
    if 'match_url' not in df.columns:
        print(f"Skipping {input_file} - not a Type A file")
        return
    
    # Group by match (using match_date, home_team, away_team as key)
    grouped = df.groupby(['scraped_date', 'match_date', 'home_team', 'away_team', 
                         'league_name', 'home_score', 'away_score', 'partial_results',
                         'venue', 'venue_country', 'venue_town'])
    
    print(f"Found {len(grouped)} unique matches")
    
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
        
        print(f"Market column will be: {market_column_name}")
        
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
    print(f"Converted DataFrame has {len(converted_df)} rows")
    print(f"New columns: {list(converted_df.columns)}")
    
    # Show sample of converted data
    print("\nSample converted data:")
    print(converted_df.head(1).to_string())
    
    return converted_df

def main():
    """Test conversion on one file"""
    test_file = "/Users/mac/Desktop/HIPO/oddsportal/oddssc/origin/OddsHarvester/data/denmark-superliga_2019_2020_2.5.csv"
    
    if os.path.exists(test_file):
        converted_df = convert_type_a_to_type_b(test_file)
        if converted_df is not None:
            # Save to a test output file
            test_output = "/Users/mac/Desktop/HIPO/oddsportal/oddssc/origin/OddsHarvester/data/test_converted.csv"
            converted_df.to_csv(test_output, index=False)
            print(f"Test conversion saved to: {test_output}")
    else:
        print(f"Test file not found: {test_file}")

if __name__ == "__main__":
    main()