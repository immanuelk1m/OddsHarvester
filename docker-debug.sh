#!/bin/bash

# Docker 환경 디버깅 스크립트

echo "=== Docker 환경에서 배당 수집 디버그 ==="

# 1. 단일 매치로 테스트 (로그 레벨 상세)
echo "1. 단일 매치 테스트 시작..."
uv run python src/main.py scrape_historic \
  --match_links "https://www.oddsportal.com/football/belgium/jupiler-league-2020-2021/antwerp-anderlecht-Iusx5MVa/" \
  --sport football \
  --leagues belgium-jupiler-pro-league \
  --season 2020-2021 \
  --markets over_under_2_5 \
  --format csv \
  --file_path debug_test.csv \
  --headless \
  --concurrency_tasks 1 2>&1 | tee debug_log.txt

echo ""
echo "2. 수집된 데이터 확인:"
if [ -f debug_test.csv ]; then
    echo "헤더 컬럼:"
    head -1 debug_test.csv | tr ',' '\n'
    echo ""
    echo "데이터 샘플:"
    head -2 debug_test.csv
else
    echo "CSV 파일이 생성되지 않음"
fi

echo ""
echo "3. 마켓 관련 로그 확인:"
grep -i "market\|odds\|over_under" debug_log.txt | head -20

echo ""
echo "4. 에러 로그 확인:"
grep -i "error\|warning\|failed" debug_log.txt | head -20

echo ""
echo "5. Chromium 브라우저 정보:"
uv run playwright show chromium

echo ""
echo "=== 디버그 완료 ==="