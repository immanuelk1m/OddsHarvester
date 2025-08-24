#!/bin/bash

# 배치 1: Belgium, Portugal, Germany 리그 데이터 수집
# 총 45개 작업 (Belgium 15 + Portugal 15 + Germany 15)

echo "=== 배치 1: Belgium, Portugal, Germany 데이터 수집 시작 ==="
echo "$(date): 총 45개 작업 시작"

COUNTER=0
TOTAL=45

# ================== BELGIUM (15 작업) ==================
for season in "2019-2020" "2020-2021" "2021-2022" "2022-2023" "2024-2025"; do
    for market in "over_under_2_5:2.5" "over_under_3:3.0" "over_under_3_5:3.5"; do
        IFS=':' read -r market_key market_label <<< "$market"
        COUNTER=$((COUNTER+1))
        season_formatted=$(echo $season | tr '-' '_')
        echo "$(date): [$COUNTER/$TOTAL] Belgium $season 시즌 $market_label 마켓 수집 시작"
        uv run python src/main.py scrape_historic \
          --match_links_csv match_urls_complete/by_league/belgium/$season.csv \
          --sport football \
          --markets $market_key \
          --format csv \
          --file_path data/belgium-jupiler-pro-league_${season_formatted}_$market_label.csv \
          --headless \
          --concurrency_tasks 1
        
        if [ $? -eq 0 ]; then
            echo "$(date): [$COUNTER/$TOTAL] Belgium $season 시즌 $market_label 마켓 완료 ✓"
        else
            echo "$(date): [$COUNTER/$TOTAL] Belgium $season 시즌 $market_label 마켓 실패 ✗"
        fi
    done
done

# ================== PORTUGAL (15 작업) ==================
for season in "2020-2021" "2021-2022" "2022-2023" "2023-2024" "2024-2025"; do
    for market in "over_under_2_5:2.5" "over_under_3:3.0" "over_under_3_5:3.5"; do
        IFS=':' read -r market_key market_label <<< "$market"
        COUNTER=$((COUNTER+1))
        season_formatted=$(echo $season | tr '-' '_')
        echo "$(date): [$COUNTER/$TOTAL] Portugal $season 시즌 $market_label 마켓 수집 시작"
        uv run python src/main.py scrape_historic \
          --match_links_csv match_urls_complete/by_league/portugal/$season.csv \
          --sport football \
          --markets $market_key \
          --format csv \
          --file_path data/portugal-liga-portugal_${season_formatted}_$market_label.csv \
          --headless \
          --concurrency_tasks 1
        
        if [ $? -eq 0 ]; then
            echo "$(date): [$COUNTER/$TOTAL] Portugal $season 시즌 $market_label 마켓 완료 ✓"
        else
            echo "$(date): [$COUNTER/$TOTAL] Portugal $season 시즌 $market_label 마켓 실패 ✗"
        fi
    done
done

# ================== GERMANY (15 작업) ==================
for season in "2020-2021" "2021-2022" "2022-2023" "2023-2024" "2024-2025"; do
    for market in "over_under_2_5:2.5" "over_under_3:3.0" "over_under_3_5:3.5"; do
        IFS=':' read -r market_key market_label <<< "$market"
        COUNTER=$((COUNTER+1))
        season_formatted=$(echo $season | tr '-' '_')
        echo "$(date): [$COUNTER/$TOTAL] Germany $season 시즌 $market_label 마켓 수집 시작"
        uv run python src/main.py scrape_historic \
          --match_links_csv match_urls_complete/by_league/germany/$season.csv \
          --sport football \
          --markets $market_key \
          --format csv \
          --file_path data/germany-bundesliga_${season_formatted}_$market_label.csv \
          --headless \
          --concurrency_tasks 1
        
        if [ $? -eq 0 ]; then
            echo "$(date): [$COUNTER/$TOTAL] Germany $season 시즌 $market_label 마켓 완료 ✓"
        else
            echo "$(date): [$COUNTER/$TOTAL] Germany $season 시즌 $market_label 마켓 실패 ✗"
        fi
    done
done

echo "=== 배치 1 데이터 수집 완료 ==="
echo "$(date): 45개 작업 완료"
echo ""
echo "수집된 리그:"
echo "- Belgium: 5개 시즌 × 3개 마켓 = 15개 파일"
echo "- Portugal: 5개 시즌 × 3개 마켓 = 15개 파일"
echo "- Germany: 5개 시즌 × 3개 마켓 = 15개 파일"