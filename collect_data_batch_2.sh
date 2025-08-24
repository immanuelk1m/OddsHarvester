#!/bin/bash

# 배치 2: England, Scotland, Portugal 리그 데이터 수집
# 총 51개 작업 (England 18 + Scotland 18 + Portugal 15)

echo "=== 배치 2: England, Scotland, Portugal 데이터 수집 시작 ==="
echo "$(date): 총 51개 작업 시작"

COUNTER=0
TOTAL=51

# ================== ENGLAND (18 작업) ==================
for season in "2019-2020" "2020-2021" "2021-2022" "2022-2023" "2023-2024" "2024-2025"; do
    for market in "over_under_2_5:2.5" "over_under_3:3.0" "over_under_3_5:3.5"; do
        IFS=':' read -r market_key market_label <<< "$market"
        COUNTER=$((COUNTER+1))
        season_formatted=$(echo $season | tr '-' '_')
        echo "$(date): [$COUNTER/$TOTAL] England $season 시즌 $market_label 마켓 수집 시작"
        uv run python src/main.py scrape_historic \
          --match_links_csv match_urls_complete/by_league/england/$season.csv \
          --sport football \
          --markets $market_key \
          --format csv \
          --file_path data/england-premier-league_${season_formatted}_$market_label.csv \
          --headless \
          --concurrency_tasks 1
        
        if [ $? -eq 0 ]; then
            echo "$(date): [$COUNTER/$TOTAL] England $season 시즌 $market_label 마켓 완료 ✓"
        else
            echo "$(date): [$COUNTER/$TOTAL] England $season 시즌 $market_label 마켓 실패 ✗"
        fi
    done
done

# ================== SCOTLAND (18 작업) ==================
for season in "2019-2020" "2020-2021" "2021-2022" "2022-2023" "2023-2024" "2024-2025"; do
    for market in "over_under_2_5:2.5" "over_under_3:3.0" "over_under_3_5:3.5"; do
        IFS=':' read -r market_key market_label <<< "$market"
        COUNTER=$((COUNTER+1))
        season_formatted=$(echo $season | tr '-' '_')
        echo "$(date): [$COUNTER/$TOTAL] Scotland $season 시즌 $market_label 마켓 수집 시작"
        uv run python src/main.py scrape_historic \
          --match_links_csv match_urls_complete/by_league/scotland/$season.csv \
          --sport football \
          --markets $market_key \
          --format csv \
          --file_path data/scotland-premiership_${season_formatted}_$market_label.csv \
          --headless \
          --concurrency_tasks 1
        
        if [ $? -eq 0 ]; then
            echo "$(date): [$COUNTER/$TOTAL] Scotland $season 시즌 $market_label 마켓 완료 ✓"
        else
            echo "$(date): [$COUNTER/$TOTAL] Scotland $season 시즌 $market_label 마켓 실패 ✗"
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

echo "=== 배치 2 데이터 수집 완료 ==="
echo "$(date): 51개 작업 완료"
echo ""
echo "수집된 리그:"
echo "- England: 6개 시즌 × 3개 마켓 = 18개 파일"
echo "- Scotland: 6개 시즌 × 3개 마켓 = 18개 파일"
echo "- Portugal: 5개 시즌 × 3개 마켓 = 15개 파일"