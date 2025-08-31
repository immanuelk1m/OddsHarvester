#!/usr/bin/env python
"""Test script to debug odds collection"""
import asyncio
import json
from src.scraper_app import ScraperApp

async def test_single_match():
    """Test scraping a single match with debug output"""
    
    # Test with a single Belgium match
    test_link = "https://www.oddsportal.com/football/belgium/jupiler-league-2020-2021/antwerp-anderlecht-Iusx5MVa/"
    
    params = {
        'command': 'scrape_historic',
        'match_links': [test_link],
        'sport': 'football',
        'leagues': ['belgium-jupiler-pro-league'],
        'season': '2020-2021',
        'markets': ['over_under_2_5'],
        'scrape_odds_history': False,
        'target_bookmaker': None,
        'headless': True,
        'preview_submarkets_only': False,
        'concurrency_tasks': 1
    }
    
    app = ScraperApp()
    result = await app.run_scraper(**params)
    
    if result:
        print(f"\n=== SCRAPED DATA ===")
        print(f"Number of records: {len(result)}")
        if result:
            print(f"\nFirst record keys: {list(result[0].keys())}")
            print(f"\nFirst record (formatted):")
            print(json.dumps(result[0], indent=2, default=str))
            
            # Check for market data
            market_keys = [k for k in result[0].keys() if 'market' in k.lower() or 'over' in k.lower() or 'under' in k.lower()]
            if market_keys:
                print(f"\nMarket-related keys found: {market_keys}")
                for key in market_keys:
                    print(f"  {key}: {result[0].get(key)}")
            else:
                print("\n⚠️ NO MARKET DATA FOUND IN RESULT!")
    else:
        print("No data returned from scraper")

if __name__ == "__main__":
    asyncio.run(test_single_match())