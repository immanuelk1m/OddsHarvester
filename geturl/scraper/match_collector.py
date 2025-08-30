"""경기 URL 수집 모듈"""

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


class MatchCollector:
    """페이지에서 경기 URL을 수집하는 클래스"""
    
    @staticmethod
    def check_no_odds_message(driver):
        """'no odds available' 메시지 확인"""
        try:
            no_odds_xpath = "/html/body/div[1]/div[1]/div[1]/div/main/div[3]/div[4]/div[1]/div[2]"
            no_odds_element = driver.find_element(By.XPATH, no_odds_xpath)
            
            if no_odds_element and "Unfortunately, no matches can be displayed" in no_odds_element.text:
                print("  ⚠️ 'No odds available' 메시지 감지 - 시즌 수집 중단")
                return True
        except NoSuchElementException:
            pass
        except Exception:
            pass
        
        return False
    
    @staticmethod
    def collect_match_urls_from_page(driver, league_name, season, page_num, country=None):
        """특정 페이지에서 경기 URL 수집
        
        Args:
            driver: Selenium 웹드라이버
            league_name: 리그 이름
            season: 시즌
            page_num: 페이지 번호
            country: 국가 코드 (optional)
        """
        match_data = []
        
        try:
            main_container_xpath = "/html/body/div[1]/div[1]/div[1]/div/main/div[3]/div[4]"
            event_rows_xpath = f"{main_container_xpath}//div[contains(@class, 'eventRow')]"
            event_rows = driver.find_elements(By.XPATH, event_rows_xpath)
            
            if not event_rows:
                print(f"  페이지 {page_num}: 경기 없음")
                return match_data
                
            print(f"  페이지 {page_num}: {len(event_rows)}개 경기 발견")
            
            for row in event_rows:
                try:
                    link_element = row.find_element(By.XPATH, ".//div[@data-testid='game-row']/a")
                    relative_url = link_element.get_attribute('href')
                    
                    if relative_url:
                        if relative_url.startswith('/'):
                            full_url = "https://www.oddsportal.com" + relative_url
                        else:
                            full_url = relative_url
                        
                        match_info = {
                            'league': league_name,
                            'season': season,
                            'match_url': full_url
                        }
                        
                        # 국가 정보가 제공되면 추가
                        if country:
                            match_info['country'] = country
                        
                        match_data.append(match_info)
                        
                except NoSuchElementException:
                    continue
                except Exception as e:
                    print(f"    경기 URL 수집 오류: {e}")
                    continue
        
        except Exception as e:
            print(f"  페이지 {page_num} 처리 오류: {e}")
        
        return match_data