#!/usr/bin/env python3
"""
Deep debugging script for Belgium and Switzerland pagination/match detection issues.
Captures screenshots, network activity, and detailed HTML analysis.
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup


class DeepDebugger:
    def __init__(self, output_dir="debug_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    async def debug_league(self, league_name, league_url, season="2019-2020"):
        """Debug a specific league with comprehensive analysis."""
        print(f"\n{'='*60}")
        print(f"DEBUGGING: {league_name} - {season}")
        print(f"URL: {league_url}")
        print('='*60)
        
        league_dir = self.output_dir / f"{league_name}_{self.timestamp}"
        league_dir.mkdir(exist_ok=True)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)  # Visible for debugging
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            
            # Enable network monitoring
            page = await context.new_page()
            network_logs = []
            
            async def log_request(request):
                if 'ajax' in request.url or 'api' in request.url:
                    network_logs.append({
                        'type': 'request',
                        'url': request.url,
                        'method': request.method
                    })
            
            async def log_response(response):
                if 'ajax' in response.url or 'api' in response.url:
                    network_logs.append({
                        'type': 'response',
                        'url': response.url,
                        'status': response.status
                    })
            
            page.on("request", log_request)
            page.on("response", log_response)
            
            try:
                # Navigate to the page
                print(f"1. Navigating to {league_url}")
                await page.goto(league_url, wait_until="networkidle", timeout=30000)
                await page.wait_for_timeout(3000)
                
                # Screenshot initial page
                await page.screenshot(path=league_dir / "1_initial_page.png", full_page=True)
                print("   ✓ Screenshot saved: 1_initial_page.png")
                
                # Save initial HTML
                html_content = await page.content()
                with open(league_dir / "1_initial_page.html", "w", encoding="utf-8") as f:
                    f.write(html_content)
                print("   ✓ HTML saved: 1_initial_page.html")
                
                # Analyze pagination with multiple strategies
                print("\n2. Analyzing pagination...")
                pagination_info = await self._analyze_pagination(page, league_dir)
                
                # If pagination exists, navigate to last page
                if pagination_info['last_page'] > 1:
                    last_page_url = f"{league_url}#/page/{pagination_info['last_page']}"
                    print(f"\n3. Navigating to last page: {last_page_url}")
                    await page.goto(last_page_url, wait_until="networkidle", timeout=30000)
                    await page.wait_for_timeout(5000)
                    
                    # Screenshot last page
                    await page.screenshot(path=league_dir / "2_last_page.png", full_page=True)
                    print("   ✓ Screenshot saved: 2_last_page.png")
                    
                    # Save last page HTML
                    html_content = await page.content()
                    with open(league_dir / "2_last_page.html", "w", encoding="utf-8") as f:
                        f.write(html_content)
                    print("   ✓ HTML saved: 2_last_page.html")
                    
                    # Analyze matches on last page
                    matches_info = await self._analyze_matches(page, league_dir)
                else:
                    print("   ⚠️ No pagination detected - analyzing matches on single page")
                    matches_info = await self._analyze_matches(page, league_dir)
                
                # Save network logs
                with open(league_dir / "network_logs.json", "w") as f:
                    json.dump(network_logs, f, indent=2)
                print(f"\n   ✓ Network logs saved: {len(network_logs)} entries")
                
                # Generate report
                report = {
                    'league': league_name,
                    'url': league_url,
                    'season': season,
                    'pagination': pagination_info,
                    'matches': matches_info,
                    'timestamp': self.timestamp
                }
                
                with open(league_dir / "debug_report.json", "w") as f:
                    json.dump(report, f, indent=2)
                print(f"\n   ✓ Debug report saved: debug_report.json")
                
                # Print summary
                print(f"\n{'='*40}")
                print(f"SUMMARY for {league_name}:")
                print(f"  - Last page: {pagination_info['last_page']}")
                print(f"  - Total pages: {pagination_info['total_pages']}")
                print(f"  - Matches found: {matches_info['count']}")
                print(f"  - Selectors that worked: {pagination_info['working_selectors']}")
                print(f"  - Match selectors: {matches_info['working_selectors']}")
                print(f"{'='*40}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                import traceback
                traceback.print_exc()
                
            finally:
                await browser.close()
    
    async def _analyze_pagination(self, page, output_dir):
        """Analyze pagination with multiple strategies."""
        print("   Trying multiple pagination strategies...")
        
        pagination_info = {
            'last_page': 1,
            'total_pages': 1,
            'working_selectors': [],
            'all_attempts': []
        }
        
        # Strategy 1: Standard pagination links
        selectors = [
            "div.pagination a",
            "a[href*='#/page/']",
            "div[class*='pagination'] a",
            "span[class*='pagination'] a",
            "ul.pagination a",
            "nav a[href*='page']",
            "a.pagination-link"
        ]
        
        for selector in selectors:
            try:
                elements = await page.query_selector_all(selector)
                if elements:
                    print(f"   ✓ Found {len(elements)} elements with selector: {selector}")
                    pagination_info['working_selectors'].append(selector)
                    
                    # Extract page numbers
                    for element in elements:
                        href = await element.get_attribute("href")
                        text = await element.inner_text()
                        
                        if href and "#/page/" in href:
                            page_num = href.split("#/page/")[-1].strip("/")
                            try:
                                page_num = int(page_num)
                                pagination_info['last_page'] = max(pagination_info['last_page'], page_num)
                            except:
                                pass
                        elif text.isdigit():
                            page_num = int(text)
                            pagination_info['last_page'] = max(pagination_info['last_page'], page_num)
                    
                pagination_info['all_attempts'].append({
                    'selector': selector,
                    'found': len(elements) if elements else 0
                })
            except:
                pass
        
        # Strategy 2: JavaScript execution
        try:
            js_pages = await page.evaluate("""
                () => {
                    const links = document.querySelectorAll('a[href*="#/page/"]');
                    const pages = [];
                    links.forEach(link => {
                        const match = link.href.match(/#\/page\/(\d+)/);
                        if (match) pages.push(parseInt(match[1]));
                    });
                    return pages;
                }
            """)
            if js_pages:
                max_page = max(js_pages)
                print(f"   ✓ JavaScript found pages: {js_pages}")
                pagination_info['last_page'] = max(pagination_info['last_page'], max_page)
                pagination_info['working_selectors'].append("JavaScript extraction")
        except:
            pass
        
        # Strategy 3: Check for "Next" button
        try:
            next_selectors = [
                "a:has-text('Next')",
                "a[title='Next']",
                "button:has-text('Next')",
                "a.next",
                "a[rel='next']"
            ]
            
            for selector in next_selectors:
                try:
                    next_btn = await page.query_selector(selector)
                    if next_btn:
                        print(f"   ✓ Found Next button with: {selector}")
                        pagination_info['has_next'] = True
                        # Click through pages to find total
                        current_page = 1
                        while next_btn and not await next_btn.is_disabled():
                            await next_btn.click()
                            await page.wait_for_timeout(2000)
                            current_page += 1
                            next_btn = await page.query_selector(selector)
                            if current_page > 10:  # Safety limit
                                break
                        pagination_info['last_page'] = max(pagination_info['last_page'], current_page)
                except:
                    pass
        except:
            pass
        
        pagination_info['total_pages'] = pagination_info['last_page']
        return pagination_info
    
    async def _analyze_matches(self, page, output_dir):
        """Analyze match detection with multiple strategies."""
        print("\n4. Analyzing matches...")
        
        matches_info = {
            'count': 0,
            'urls': [],
            'working_selectors': [],
            'all_attempts': []
        }
        
        # Wait for content to load
        await page.wait_for_timeout(3000)
        
        # Scroll to load lazy content
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(2000)
        
        # Strategy 1: Direct match link selectors
        match_selectors = [
            "a.eventRowLink",
            "div.eventRow a[href*='/football/']",
            "tr.event a[href*='/football/']",
            "a[href*='/football/'][href*='-']",
            "td.name a",
            "div[class*='match'] a",
            "div[class*='event'] a[href*='/football/']"
        ]
        
        for selector in match_selectors:
            try:
                elements = await page.query_selector_all(selector)
                if elements:
                    urls = []
                    for element in elements:
                        href = await element.get_attribute("href")
                        if href and "/football/" in href and href.count("-") >= 2:
                            urls.append(href)
                    
                    if urls:
                        print(f"   ✓ Found {len(urls)} matches with selector: {selector}")
                        matches_info['working_selectors'].append(selector)
                        matches_info['urls'] = list(set(matches_info['urls'] + urls))
                
                matches_info['all_attempts'].append({
                    'selector': selector,
                    'found': len(urls) if 'urls' in locals() else 0
                })
            except:
                pass
        
        # Strategy 2: JavaScript extraction
        try:
            js_matches = await page.evaluate("""
                () => {
                    const links = [];
                    document.querySelectorAll('a').forEach(a => {
                        if (a.href && a.href.includes('/football/') && 
                            a.href.split('-').length > 2 && 
                            !a.href.includes('/results/') &&
                            !a.href.includes('#/page/')) {
                            links.push(a.href);
                        }
                    });
                    return [...new Set(links)];
                }
            """)
            if js_matches:
                print(f"   ✓ JavaScript found {len(js_matches)} matches")
                matches_info['urls'] = list(set(matches_info['urls'] + js_matches))
                matches_info['working_selectors'].append("JavaScript extraction")
        except:
            pass
        
        # Strategy 3: BeautifulSoup parsing
        try:
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find all links that look like match URLs
            bs_matches = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/football/' in href and href.count('-') >= 2:
                    if not any(x in href for x in ['/results/', '#/page/', '/standings/']):
                        bs_matches.append(href)
            
            if bs_matches:
                print(f"   ✓ BeautifulSoup found {len(bs_matches)} matches")
                matches_info['urls'] = list(set(matches_info['urls'] + bs_matches))
                matches_info['working_selectors'].append("BeautifulSoup parsing")
        except:
            pass
        
        matches_info['count'] = len(matches_info['urls'])
        
        # Save sample URLs
        if matches_info['urls']:
            print(f"\n   Sample match URLs:")
            for i, url in enumerate(matches_info['urls'][:3]):
                print(f"     {i+1}. {url}")
        
        return matches_info


async def main():
    """Debug Belgium and Switzerland leagues."""
    debugger = DeepDebugger()
    
    # Belgium with both URL variations
    await debugger.debug_league(
        "belgium-jupiler-league",
        "https://www.oddsportal.com/football/belgium/jupiler-league-2019-2020/results/",
        "2019-2020"
    )
    
    # Switzerland
    await debugger.debug_league(
        "switzerland-super-league", 
        "https://www.oddsportal.com/football/switzerland/super-league-2019-2020/results/",
        "2019-2020"
    )


if __name__ == "__main__":
    asyncio.run(main())