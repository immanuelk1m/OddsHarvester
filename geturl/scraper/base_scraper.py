"""기본 스크래퍼 클래스 - 웹 드라이버 관리 및 공통 기능"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class BaseScraper:
    """웹 드라이버 초기화 및 관리를 담당하는 기본 스크래퍼 클래스"""
    
    def __init__(self):
        self.driver = None
    
    def init_driver(self):
        """Chrome 드라이버 초기화"""
        self.driver = webdriver.Chrome()
        return self.driver
    
    def close_driver(self):
        """드라이버 종료"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
    
    def navigate_to_page(self, url):
        """페이지로 이동 및 초기 설정"""
        if not self.driver:
            self.init_driver()
        
        self.driver.get(url)
        
        # 쿠키 수락 버튼 처리
        self._handle_cookie_consent()
        
        # 페이지 줌 설정
        self._set_page_zoom()
        
        # 페이지 로딩 대기
        time.sleep(3)
    
    def _handle_cookie_consent(self):
        """쿠키 동의 팝업 처리"""
        try:
            cookie_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            cookie_button.click()
            time.sleep(1)
        except TimeoutException:
            pass
    
    def _set_page_zoom(self, zoom_level='25%'):
        """페이지 줌 레벨 설정"""
        self.driver.execute_script(f"document.body.style.zoom='{zoom_level}'")
    
    def wait_for_element(self, by, value, timeout=10):
        """특정 요소가 나타날 때까지 대기"""
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_element_located((by, value)))