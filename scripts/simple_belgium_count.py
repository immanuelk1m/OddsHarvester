#!/usr/bin/env python3
"""
Very simple script to count matches on Belgium page
"""

import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            locale="en-US",
            timezone_id="America/New_York",
            extra_http_headers={"Accept-Language": "en-US,en;q=0.9"}
        )
        page = await context.new_page()
        
        # Go to main page first
        await page.goto("https://www.oddsportal.com/", timeout=30000)
        await page.wait_for_timeout(2000)
        
        # Now go to Belgium 2023-2024
        url = "https://www.oddsportal.com/football/belgium/jupiler-pro-league-2023-2024/results/"
        await page.goto(url, timeout=30000)
        
        # Wait for content
        await page.wait_for_timeout(5000)
        
        # Try to dismiss cookie banner
        try:
            cookie_button = await page.query_selector('button:has-text("Accept")')
            if cookie_button:
                await cookie_button.click()
        except:
            pass
        
        # Check pagination
        pagination = await page.query_selector_all('div.pagination a')
        print(f"Pagination links found: {len(pagination)}")
        
        # Get page numbers
        page_numbers = []
        for link in pagination:
            text = await link.inner_text()
            if text.isdigit():
                page_numbers.append(int(text))
        
        if page_numbers:
            max_page = max(page_numbers)
            print(f"Max page number: {max_page}")
        else:
            max_page = 1
            print("Single page (no pagination)")
        
        total_matches = 0
        belgium_matches = 0
        
        # Count matches on each page
        for page_num in range(1, min(max_page + 1, 4)):  # Check first 3 pages
            if page_num > 1:
                # Navigate to page
                await page.goto(f"{url}#/page/{page_num}", timeout=30000)
                await page.wait_for_timeout(3000)
            
            # Scroll to load all content
            for _ in range(3):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(1500)
            
            # Count all event rows
            event_rows = await page.query_selector_all('div[class*="eventRow"]')
            print(f"  Event rows found: {len(event_rows)}")
            
            # Get all links within event rows
            match_links = []
            for row in event_rows:
                links = await row.query_selector_all('a[href*="/football/"]')
                for link in links:
                    href = await link.get_attribute('href')
                    if href and '/football/' in href and not '#' in href:
                        # Check if it's a match URL (has team names at the end)
                        parts = href.split('/')
                        if len(parts) >= 7 and '-' in parts[-2]:
                            match_links.append(href)
                            break  # Only take first match link from each row
            
            # Remove duplicates
            unique_matches = list(set(match_links))
            
            print(f"\nPage {page_num}:")
            print(f"  Total unique match links: {len(unique_matches)}")
            
            # Count Belgium-specific
            belgium_count = 0
            for link in unique_matches:
                if "belgium/jupiler-pro-league-2023-2024" in link:
                    belgium_count += 1
            
            print(f"  Belgium league matches: {belgium_count}")
            
            total_matches += len(unique_matches)
            belgium_matches += belgium_count
            
            # Show first few matches
            if unique_matches:
                print("  First 3 matches:")
                for i, match in enumerate(unique_matches[:3], 1):
                    print(f"    {i}. {match}")
        
        print(f"\n{'='*60}")
        print(f"SUMMARY (first {min(3, max_page)} pages):")
        print(f"  Total matches found: {total_matches}")
        print(f"  Belgium matches: {belgium_matches}")
        
        if max_page > 3:
            # Estimate for full season
            avg_per_page = total_matches / min(3, max_page)
            estimated_total = avg_per_page * max_page
            print(f"\nEstimated total for all {max_page} pages: ~{int(estimated_total)} matches")
        
        # Keep browser open for manual inspection
        print("\nBrowser will stay open for 10 seconds for inspection...")
        await page.wait_for_timeout(10000)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())