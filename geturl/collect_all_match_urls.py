import time
import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# 리그 설정 (국가별 URL 패턴 정의)
LEAGUE_CONFIGS = {
    "belgium": {
        "name": "Belgium Jupiler League",
        "seasons": {
            "2020-2021": "https://www.oddsportal.com/football/belgium/jupiler-league-2020-2021/results/",
            "2021-2022": "https://www.oddsportal.com/football/belgium/jupiler-pro-league-2021-2022/results/",
            "2022-2023": "https://www.oddsportal.com/football/belgium/jupiler-pro-league-2022-2023/results/",
            "2023-2024": "https://www.oddsportal.com/football/belgium/jupiler-pro-league-2023-2024/results/",
            "2024-2025": "https://www.oddsportal.com/football/belgium/jupiler-pro-league-2024-2025/results/"
        }
    },
    "switzerland": {
        "name": "Switzerland Super League",
        "seasons": {
            "2020-2021": "https://www.oddsportal.com/football/switzerland/super-league-2020-2021/results/",
            "2021-2022": "https://www.oddsportal.com/football/switzerland/super-league-2021-2022/results/",
            "2022-2023": "https://www.oddsportal.com/football/switzerland/super-league-2022-2023/results/",
            "2023-2024": "https://www.oddsportal.com/football/switzerland/super-league-2023-2024/results/",
            "2024-2025": "https://www.oddsportal.com/football/switzerland/super-league-2024-2025/results/"
        }
    },
    "england": {
        "name": "England Premier League",
        "seasons": {
            "2020-2021": "https://www.oddsportal.com/football/england/premier-league-2020-2021/results/",
            "2021-2022": "https://www.oddsportal.com/football/england/premier-league-2021-2022/results/",
            "2022-2023": "https://www.oddsportal.com/football/england/premier-league-2022-2023/results/",
            "2023-2024": "https://www.oddsportal.com/football/england/premier-league-2023-2024/results/",
            "2024-2025": "https://www.oddsportal.com/football/england/premier-league-2024-2025/results/"
        }
    },
    "italy": {
        "name": "Italy Serie A",
        "seasons": {
            "2020-2021": "https://www.oddsportal.com/football/italy/serie-a-2020-2021/results/",
            "2021-2022": "https://www.oddsportal.com/football/italy/serie-a-2021-2022/results/",
            "2022-2023": "https://www.oddsportal.com/football/italy/serie-a-2022-2023/results/",
            "2023-2024": "https://www.oddsportal.com/football/italy/serie-a-2023-2024/results/",
            "2024-2025": "https://www.oddsportal.com/football/italy/serie-a-2024-2025/results/"
        }
    },
    "spain": {
        "name": "Spain La Liga",
        "seasons": {
            "2020-2021": "https://www.oddsportal.com/football/spain/laliga-2020-2021/results/",
            "2021-2022": "https://www.oddsportal.com/football/spain/laliga-2021-2022/results/",
            "2022-2023": "https://www.oddsportal.com/football/spain/laliga-2022-2023/results/",
            "2023-2024": "https://www.oddsportal.com/football/spain/laliga-2023-2024/results/",
            "2024-2025": "https://www.oddsportal.com/football/spain/laliga-2024-2025/results/"
        }
    },
    "sweden": {
        "name": "Sweden Allsvenskan",
        "seasons": {
            "2020": "https://www.oddsportal.com/football/sweden/allsvenskan-2020/results/",
            "2021": "https://www.oddsportal.com/football/sweden/allsvenskan-2021/results/",
            "2022": "https://www.oddsportal.com/football/sweden/allsvenskan-2022/results/",
            "2023": "https://www.oddsportal.com/football/sweden/allsvenskan-2023/results/",
            "2024": "https://www.oddsportal.com/football/sweden/allsvenskan-2024/results/"
        }
    },
    "france": {
        "name": "France Ligue 1",
        "seasons": {
            "2020-2021": "https://www.oddsportal.com/football/france/ligue-1-2020-2021/results/",
            "2021-2022": "https://www.oddsportal.com/football/france/ligue-1-2021-2022/results/",
            "2022-2023": "https://www.oddsportal.com/football/france/ligue-1-2022-2023/results/",
            "2023-2024": "https://www.oddsportal.com/football/france/ligue-1-2023-2024/results/",
            "2024-2025": "https://www.oddsportal.com/football/france/ligue-1-2024-2025/results/"
        }
    },
    "portugal": {
        "name": "Portugal Liga",
        "seasons": {
            "2020-2021": "https://www.oddsportal.com/football/portugal/primeira-liga-2020-2021/results/",
            "2021-2022": "https://www.oddsportal.com/football/portugal/liga-portugal-2021-2022/results/",
            "2022-2023": "https://www.oddsportal.com/football/portugal/liga-portugal-2022-2023/results/",
            "2023-2024": "https://www.oddsportal.com/football/portugal/liga-portugal-2023-2024/results/",
            "2024-2025": "https://www.oddsportal.com/football/portugal/liga-portugal-2024-2025/results/"
        }
    },
    "norway": {
        "name": "Norway Eliteserien",
        "seasons": {
            "2020": "https://www.oddsportal.com/football/norway/eliteserien-2020/results/",
            "2021": "https://www.oddsportal.com/football/norway/eliteserien-2021/results/",
            "2022": "https://www.oddsportal.com/football/norway/eliteserien-2022/results/",
            "2023": "https://www.oddsportal.com/football/norway/eliteserien-2023/results/",
            "2024": "https://www.oddsportal.com/football/norway/eliteserien-2024/results/"
        }
    },
    "denmark": {
        "name": "Denmark Superliga",
        "seasons": {
            "2020-2021": "https://www.oddsportal.com/football/denmark/superliga-2020-2021/results/",
            "2021-2022": "https://www.oddsportal.com/football/denmark/superliga-2021-2022/results/",
            "2022-2023": "https://www.oddsportal.com/football/denmark/superliga-2022-2023/results/",
            "2023-2024": "https://www.oddsportal.com/football/denmark/superliga-2023-2024/results/",
            "2024-2025": "https://www.oddsportal.com/football/denmark/superliga-2024-2025/results/"
        }
    },
    "germany": {
        "name": "Germany Bundesliga",
        "seasons": {
            "2020-2021": "https://www.oddsportal.com/football/germany/bundesliga-2020-2021/results/",
            "2021-2022": "https://www.oddsportal.com/football/germany/bundesliga-2021-2022/results/",
            "2022-2023": "https://www.oddsportal.com/football/germany/bundesliga-2022-2023/results/",
            "2023-2024": "https://www.oddsportal.com/football/germany/bundesliga-2023-2024/results/",
            "2024-2025": "https://www.oddsportal.com/football/germany/bundesliga-2024-2025/results/"
        }
    },
    "netherlands": {
        "name": "Netherlands Eredivisie",
        "seasons": {
            "2020-2021": "https://www.oddsportal.com/football/netherlands/eredivisie-2020-2021/results/",
            "2021-2022": "https://www.oddsportal.com/football/netherlands/eredivisie-2021-2022/results/",
            "2022-2023": "https://www.oddsportal.com/football/netherlands/eredivisie-2022-2023/results/",
            "2023-2024": "https://www.oddsportal.com/football/netherlands/eredivisie-2023-2024/results/",
            "2024-2025": "https://www.oddsportal.com/football/netherlands/eredivisie-2024-2025/results/"
        }
    },
    "scotland": {
        "name": "Scotland Premiership",
        "seasons": {
            "2020-2021": "https://www.oddsportal.com/football/scotland/premiership-2020-2021/results/",
            "2021-2022": "https://www.oddsportal.com/football/scotland/premiership-2021-2022/results/",
            "2022-2023": "https://www.oddsportal.com/football/scotland/premiership-2022-2023/results/",
            "2023-2024": "https://www.oddsportal.com/football/scotland/premiership-2023-2024/results/",
            "2024-2025": "https://www.oddsportal.com/football/scotland/premiership-2024-2025/results/"
        }
    }
}

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

def collect_match_urls_from_page(driver, league_name, season, page_num):
    """특정 페이지에서 경기 URL 수집"""
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
                    
                    match_data.append({
                        'league': league_name,
                        'season': season,
                        'url': full_url
                    })
                    
            except NoSuchElementException:
                continue
            except Exception as e:
                print(f"    경기 URL 수집 오류: {e}")
                continue
    
    except Exception as e:
        print(f"  페이지 {page_num} 처리 오류: {e}")
    
    return match_data

# --- [변경] 재시도 로직이 추가된 함수 ---
def collect_all_matches_for_season(league_name, season, base_url):
    """
    특정 시즌의 모든 경기 URL을 수집합니다.
    페이지 로딩 타임아웃 발생 시 최대 2회 재시도합니다.
    """
    all_matches = []
    page_num = 1
    max_pages = 9
    max_retries = 2  # 재시도 횟수 설정 (총 3번 시도: 최초 1 + 재시도 2)
    
    print(f"\n{league_name} - {season} 시즌 수집 시작")
    print(f"  URL: {base_url}")
    
    while page_num <= max_pages:
        if page_num == 1:
            page_url = base_url
        else:
            page_url = f"{base_url}#/page/{page_num}/"
        
        print(f"\n  페이지 {page_num} 처리 시도...")
        
        page_processed_successfully = False
        # --- [추가] 재시도 루프 시작 ---
        for attempt in range(max_retries + 1):
            driver = None  # driver 변수 초기화
            try:
                # 각 시도마다 새 브라우저 인스턴스 생성
                driver = webdriver.Chrome()
                
                driver.get(page_url)
                
                try:
                    cookie_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
                    )
                    cookie_button.click()
                    time.sleep(1)
                except TimeoutException:
                    pass
                
                driver.execute_script("document.body.style.zoom='25%'")
                time.sleep(3)
                
                if check_no_odds_message(driver):
                    print(f"  페이지 {page_num}에서 'no odds available' 메시지 발견 - 시즌 수집 종료")
                    # 이 경우는 에러가 아니므로, 바깥 루프를 탈출해야 함
                    page_num = max_pages + 1 # 바깥 while 루프를 종료시키기 위한 트릭
                    page_processed_successfully = True # 성공 처리
                    break

                # --- [수정] WebDriverWait를 사용하여 타임아웃 처리 ---
                # 경기가 있는지 10초간 대기
                wait = WebDriverWait(driver, 10)
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "eventRow")))
                
                time.sleep(10)  # 데이터가 완전히 로드될 시간을 추가로 확보
                
                matches = collect_match_urls_from_page(driver, league_name, season, page_num)
                
                if matches:
                    all_matches.extend(matches)
                    print(f"  페이지 {page_num}: {len(matches)}개 경기 수집 완료 (시도 {attempt + 1})")
                else:
                    print(f"  페이지 {page_num}: 경기 없음 - 시즌 수집 종료")
                    page_num = max_pages + 1 # 바깥 while 루프 종료
                
                page_processed_successfully = True
                break  # 성공했으므로 재시도 루프(for)를 탈출

            # --- [수정] 타임아웃 예외 처리 ---
            except TimeoutException:
                print(f"  페이지 {page_num}: 경기 없음 (timeout) - 시도 {attempt + 1}/{max_retries + 1}")
                if attempt < max_retries:
                    print("  브라우저 종료 후 재시도합니다...")
                    time.sleep(3)  # 재시도 전 잠시 대기
                # 이 블록이 끝나면 finally를 거쳐 for 루프의 다음 시도로 넘어감
            
            except Exception as e:
                print(f"  페이지 {page_num} 처리 중 예상치 못한 오류 발생 (시도 {attempt + 1}): {e}")
                if attempt < max_retries:
                    print("  브라우저 종료 후 재시도합니다...")
                    time.sleep(3)
            
            finally:
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass
        # --- [추가] 재시도 루프 종료 ---
        
        # 모든 재시도 실패 시 해당 시즌 수집 중단
        if not page_processed_successfully:
            print(f"  페이지 {page_num}: {max_retries + 1}회 시도 후에도 수집 실패. 이 시즌 수집을 중단합니다.")
            break # 페이지 루프(while)를 탈출

        page_num += 1
        if page_num <= max_pages:
            time.sleep(2)
    
    print(f"  {season} 시즌 수집 완료: 총 {len(all_matches)}개 경기")
    return all_matches


def save_to_csv(all_data, filename):
    """수집된 데이터를 CSV 파일로 저장"""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['league', 'season', 'url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        if all_data: # 데이터가 있을 경우에만 쓰기
            writer.writerows(all_data)
    
    print(f"\n데이터가 {filename}에 저장되었습니다.")

def main():
    """메인 실행 함수"""
    all_match_data = []
    
    start_time = datetime.now()
    print(f"수집 시작: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        for country, config in LEAGUE_CONFIGS.items():
            league_name = config['name']
            print(f"\n{'='*60}")
            print(f"{league_name} 처리 중...")
            print(f"{'='*60}")
            
            for season, url in config['seasons'].items():
                season_matches = collect_all_matches_for_season(
                    league_name, season, url
                )
                all_match_data.extend(season_matches)
                time.sleep(3)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f"all_match_urls_{timestamp}.csv"
        save_to_csv(all_match_data, csv_filename)
        
        print("\n" + "=" * 80)
        print("수집 완료 요약:")
        print("=" * 80)
        
        league_stats = {}
        for match in all_match_data:
            key = f"{match['league']} - {match['season']}"
            league_stats[key] = league_stats.get(key, 0) + 1
        
        for key in sorted(league_stats.keys()):
            print(f"{key}: {league_stats[key]}개 경기")
        
        print(f"\n총 수집된 경기 수: {len(all_match_data)}개")
        
        end_time = datetime.now()
        duration = end_time - start_time
        print(f"\n소요 시간: {duration}")
        print(f"수집 종료: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"\n스크립트 실행 중 치명적인 오류 발생: {e}")
        
    finally:
        print("\n수집 프로세스 완전 종료")

if __name__ == "__main__":
    main()