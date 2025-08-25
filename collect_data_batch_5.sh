#!/bin/bash

# 배치 5: Netherlands(나머지), Norway, Sweden 리그 데이터 수집
# 총 45개 작업 (Netherlands 9 + Norway 18 + Sweden 18)

echo "=== 배치 5: Netherlands(나머지), Norway, Sweden 데이터 수집 시작 ==="
echo "$(date): 총 45개 작업 시작"

COUNTER=0
TOTAL=45

# ================== NETHERLANDS 나머지 (9 작업: 2022-2023, 2023-2024, 2024-2025) ==================
for season in "2022-2023" "2023-2024" "2024-2025"; do
    for market in "over_under_2_5:2.5" "over_under_3:3.0" "over_under_3_5:3.5"; do
        IFS=':' read -r market_key market_label <<< "$market"
        COUNTER=$((COUNTER+1))
        season_formatted=$(echo $season | tr '-' '_')
        echo "$(date): [$COUNTER/$TOTAL] Netherlands $season 시즌 $market_label 마켓 수집 시작"
        uv run python src/main.py scrape_historic \
          --match_links_csv match_urls_complete/by_league/netherlands/$season.csv \
          --sport football \
          --markets $market_key \
          --format csv \
          --file_path data/netherlands-eredivisie_${season_formatted}_$market_label.csv \
          --headless \
          --concurrency_tasks 4
        
        if [ $? -eq 0 ]; then
            echo "$(date): [$COUNTER/$TOTAL] Netherlands $season 시즌 $market_label 마켓 완료 ✓"
        else
            echo "$(date): [$COUNTER/$TOTAL] Netherlands $season 시즌 $market_label 마켓 실패 ✗"
        fi
    done
done

# ================== NORWAY (18 작업) ==================
for season in "2019" "2020" "2021" "2022" "2023" "2024"; do
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
          --concurrency_tasks 4
        
        if [ $? -eq 0 ]; then
            echo "$(date): [$COUNTER/$TOTAL] Norway $season 시즌 $market_label 마켓 완료 ✓"
        else
            echo "$(date): [$COUNTER/$TOTAL] Norway $season 시즌 $market_label 마켓 실패 ✗"
        fi
    done
done

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
          --concurrency_tasks 4
        
        if [ $? -eq 0 ]; then
            echo "$(date): [$COUNTER/$TOTAL] Sweden $season 시즌 $market_label 마켓 완료 ✓"
        else
            echo "$(date): [$COUNTER/$TOTAL] Sweden $season 시즌 $market_label 마켓 실패 ✗"
        fi
    done
done

echo "=== 배치 5 데이터 수집 완료 ==="
echo "$(date): 45개 작업 완료"
echo ""
echo "수집된 리그:"
echo "- Netherlands: 3개 시즌 × 3개 마켓 = 9개 파일"
echo "- Norway: 6개 시즌 × 3개 마켓 = 18개 파일"
echo "- Sweden: 6개 시즌 × 3개 마켓 = 18개 파일"
echo ""
echo "=== 전체 데이터 수집 현황 ==="
echo "배치 1: Belgium (15), Portugal (15), Germany (15) = 45개"
echo "배치 2: Denmark (18), England (18), Switzerland 일부 (9) = 45개"
echo "배치 3: Switzerland 나머지 (9), Scotland (18), France (18) = 45개"
echo "배치 4: Spain (18), Italy (18), Netherlands 일부 (9) = 45개"
echo "배치 5: Netherlands 나머지 (9), Norway (18), Sweden (18) = 45개"
echo "총합: 225개 파일 (각 배치 정확히 45개)"