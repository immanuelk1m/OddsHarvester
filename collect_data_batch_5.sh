#!/bin/bash

# 배치 5: Sweden 리그 데이터 수집
# 총 18개 작업 (Sweden 18)

echo "=== 배치 5: Sweden 데이터 수집 시작 ==="
echo "$(date): 총 18개 작업 시작"

COUNTER=0
TOTAL=18

# ================== SWEDEN (18 작업) ==================
for season in "2019" "2020" "2021" "2022" "2023" "2024"; do
    for market in "over_under_2_5:2.5" "over_under_3:3.0" "over_under_3_5:3.5"; do
        IFS=':' read -r market_key market_label <<< "$market"
        COUNTER=$((COUNTER+1))
        echo "$(date): [$COUNTER/$TOTAL] Sweden $season 시즌 $market_label 마켓 수집 시작"
        uv run python src/main.py scrape_historic \
          --match_links_csv match_urls_complete/by_league/sweden/$season.csv \
          --sport football \
          --markets $market_key \
          --format csv \
          --file_path data/sweden-allsvenskan_${season}_$market_label.csv \
          --headless \
          --concurrency_tasks 1
        
        if [ $? -eq 0 ]; then
            echo "$(date): [$COUNTER/$TOTAL] Sweden $season 시즌 $market_label 마켓 완료 ✓"
        else
            echo "$(date): [$COUNTER/$TOTAL] Sweden $season 시즌 $market_label 마켓 실패 ✗"
        fi
    done
done

echo "=== 배치 5 데이터 수집 완료 ==="
echo "$(date): 18개 작업 완료"
echo ""
echo "수집된 리그:"
echo "- Sweden: 6개 시즌 × 3개 마켓 = 18개 파일"
echo ""
echo "=== 전체 데이터 수집 현황 ==="
echo "배치 1: Belgium (15), Denmark (18), Switzerland (18) = 51개"
echo "배치 2: England (18), Scotland (18), Portugal (15) = 51개"
echo "배치 3: France (18), Spain (18), Germany (15) = 51개"
echo "배치 4: Italy (18), Netherlands (18), Norway (18) = 54개"
echo "배치 5: Sweden (18) = 18개"
echo "총합: 225개 파일"