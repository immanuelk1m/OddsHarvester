"""
브라우저 옵션 수정 스크립트
Docker 환경에서 더 나은 렌더링을 위한 추가 옵션
"""

import sys
import os

def add_docker_browser_args():
    """Docker 환경을 위한 브라우저 인자 추가"""
    
    # PlaywrightManager 파일 경로
    file_path = "src/core/playwright_manager.py"
    
    # 추가할 브라우저 인자들
    docker_args = [
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-accelerated-2d-canvas",
        "--no-first-run",
        "--no-zygote",
        "--single-process",  # Docker 환경에서 중요
        "--disable-gpu",
        "--disable-features=IsolateOrigins,site-per-process",
        "--disable-web-security",  # CORS 문제 해결
        "--disable-blink-features=AutomationControlled",
    ]
    
    print(f"Adding Docker-specific browser arguments to {file_path}")
    
    # 파일 읽기
    with open(file_path, 'r') as f:
        content = f.read()
    
    # browser_args 찾기 및 수정
    if "browser_args = [" in content:
        # 기존 args 섹션 찾기
        start_idx = content.find("browser_args = [")
        end_idx = content.find("]", start_idx) + 1
        
        # 새로운 args 생성
        new_args_str = f"""browser_args = {docker_args}"""
        
        # 내용 교체
        new_content = content[:start_idx] + new_args_str + content[end_idx:]
        
        # 파일 쓰기
        with open(file_path, 'w') as f:
            f.write(new_content)
        
        print("✓ Browser arguments updated for Docker environment")
    else:
        print("✗ Could not find browser_args in the file")
        
    # 추가로 wait_for_timeout 증가 제안
    print("\nRecommended: Increase wait_for_timeout values in scraper for slower Docker environment")
    print("  - page.wait_for_timeout(3000) -> page.wait_for_timeout(5000)")
    print("  - Navigation timeout: 30000 -> 60000")

if __name__ == "__main__":
    add_docker_browser_args()