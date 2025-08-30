#!/bin/bash

# Norway Eliteserien 데이터 수집
# 총 15개 작업 (5개 시즌 × 3개 마켓)
# 주의: Norway는 단일 연도 형식 사용 (2020, 2021, ...)

echo "=== Norway Eliteserien 데이터 수집 시작 ==="
echo "$(date): 총 15개 작업 시작"

COUNTER=0
TOTAL=15

for season in "2020" "2021" "2022" "2023" "2024"; do
    for market in "over_under_2_5:2.5" "over_under_3:3.0" "over_under_3_5:3.5"; do
        IFS=':' read -r market_key market_label <<< "$market"
        COUNTER=$((COUNTER+1))
        echo "$(date): [$COUNTER/$TOTAL] Norway $season 시즌 $market_label 마켓 수집 시작"
        uv run python src/main.py scrape_historic \
          --match_links_csv match_urls_complete/by_league/norway/$season.csv \
          --sport football \
          --markets $market_key \
          --format csv \
          --file_path data/norway-eliteserien_${season}_$market_label.csv \
          --headless \
          --concurrency_tasks 2
        
        if [ $? -eq 0 ]; then
            echo "$(date): [$COUNTER/$TOTAL] Norway $season 시즌 $market_label 마켓 완료 ✓"
        else
            echo "$(date): [$COUNTER/$TOTAL] Norway $season 시즌 $market_label 마켓 실패 ✗"
        fi
    done
done

echo "=== Norway Eliteserien 데이터 수집 완료 ==="
echo "$(date): 15개 작업 완료"
echo ""
echo "수집된 데이터: 5개 시즌 × 3개 마켓 = 15개 파일"