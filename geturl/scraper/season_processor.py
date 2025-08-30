"""시즌별 데이터 처리 모듈"""

import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from .base_scraper import BaseScraper
from .match_collector import MatchCollector


class SeasonProcessor:
    """시즌별 경기 데이터 수집을 관리하는 클래스"""
    
    def __init__(self, max_pages=9, max_retries=2):
        self.max_pages = max_pages
        self.max_retries = max_retries
        self.collector = MatchCollector()
    
    def collect_all_matches_for_season(self, league_name, season, base_url, country=None):
        """
        특정 시즌의 모든 경기 URL을 수집합니다.
        페이지 로딩 타임아웃 발생 시 최대 2회 재시도합니다.
        
        Args:
            league_name: 리그 이름
            season: 시즌
            base_url: 기본 URL
            country: 국가 코드 (optional)
        """
        all_matches = []
        page_num = 1
        
        print(f"\n{league_name} - {season} 시즌 수집 시작")
        print(f"  URL: {base_url}")
        
        while page_num <= self.max_pages:
            if page_num == 1:
                page_url = base_url
            else:
                page_url = f"{base_url}#/page/{page_num}/"
            
            print(f"\n  페이지 {page_num} 처리 시도...")
            
            page_processed_successfully = False
            
            # 재시도 루프
            for attempt in range(self.max_retries + 1):
                scraper = BaseScraper()
                
                try:
                    # 페이지 로드
                    scraper.navigate_to_page(page_url)
                    
                    # 'no odds available' 메시지 확인
                    if self.collector.check_no_odds_message(scraper.driver):
                        print(f"  페이지 {page_num}에서 'no odds available' 메시지 발견 - 시즌 수집 종료")
                        page_num = self.max_pages + 1
                        page_processed_successfully = True
                        break
                    
                    # 경기 목록 로딩 대기
                    scraper.wait_for_element(By.CLASS_NAME, "eventRow", timeout=10)
                    time.sleep(10)  # 데이터 완전 로딩 대기
                    
                    # 경기 URL 수집
                    matches = self.collector.collect_match_urls_from_page(
                        scraper.driver, league_name, season, page_num, country
                    )
                    
                    if matches:
                        all_matches.extend(matches)
                        print(f"  페이지 {page_num}: {len(matches)}개 경기 수집 완료 (시도 {attempt + 1})")
                    else:
                        print(f"  페이지 {page_num}: 경기 없음 - 시즌 수집 종료")
                        page_num = self.max_pages + 1
                    
                    page_processed_successfully = True
                    break
                
                except TimeoutException:
                    print(f"  페이지 {page_num}: 경기 없음 (timeout) - 시도 {attempt + 1}/{self.max_retries + 1}")
                    if attempt < self.max_retries:
                        print("  브라우저 종료 후 재시도합니다...")
                        time.sleep(3)
                
                except Exception as e:
                    print(f"  페이지 {page_num} 처리 중 예상치 못한 오류 발생 (시도 {attempt + 1}): {e}")
                    if attempt < self.max_retries:
                        print("  브라우저 종료 후 재시도합니다...")
                        time.sleep(3)
                
                finally:
                    scraper.close_driver()
            
            # 모든 재시도 실패 시 시즌 수집 중단
            if not page_processed_successfully:
                print(f"  페이지 {page_num}: {self.max_retries + 1}회 시도 후에도 수집 실패. 이 시즌 수집을 중단합니다.")
                break
            
            page_num += 1
            if page_num <= self.max_pages:
                time.sleep(2)
        
        print(f"  {season} 시즌 수집 완료: 총 {len(all_matches)}개 경기")
        return all_matches