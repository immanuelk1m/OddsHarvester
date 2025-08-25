#!/bin/bash

# 배치 4: Spain, Italy, Netherlands(일부) 리그 데이터 수집
# 총 45개 작업 (Spain 18 + Italy 18 + Netherlands 9)

echo "=== 배치 4: Spain, Italy, Netherlands(일부) 데이터 수집 시작 ==="
echo "$(date): 총 45개 작업 시작"

COUNTER=0
TOTAL=45

# ================== SPAIN (18 작업) ==================
for season in "2019-2020" "2020-2021" "2021-2022" "2022-2023" "2023-2024" "2024-2025"; do
    for market in "over_under_2_5:2.5" "over_under_3:3.0" "over_under_3_5:3.5"; do
        IFS=':' read -r market_key market_label <<< "$market"
        COUNTER=$((COUNTER+1))
        season_formatted=$(echo $season | tr '-' '_')
        echo "$(date): [$COUNTER/$TOTAL] Spain $season 시즌 $market_label 마켓 수집 시작"
        uv run python src/main.py scrape_historic \
          --match_links_csv match_urls_complete/by_league/spain/$season.csv \
          --sport football \
          --markets $market_key \
          --format csv \
          --file_path data/spain-la-liga_${season_formatted}_$market_label.csv \
          --headless \
          --concurrency_tasks 4
        
        if [ $? -eq 0 ]; then
            echo "$(date): [$COUNTER/$TOTAL] Spain $season 시즌 $market_label 마켓 완료 ✓"
        else
            echo "$(date): [$COUNTER/$TOTAL] Spain $season 시즌 $market_label 마켓 실패 ✗"
        fi
    done
done

# ================== ITALY (18 작업) ==================
for season in "2019-2020" "2020-2021" "2021-2022" "2022-2023" "2023-2024" "2024-2025"; do
    for market in "over_under_2_5:2.5" "over_under_3:3.0" "over_under_3_5:3.5"; do
        IFS=':' read -r market_key market_label <<< "$market"
        COUNTER=$((COUNTER+1))
        season_formatted=$(echo $season | tr '-' '_')
        echo "$(date): [$COUNTER/$TOTAL] Italy $season 시즌 $market_label 마켓 수집 시작"
        uv run python src/main.py scrape_historic \
          --match_links_csv match_urls_complete/by_league/italy/$season.csv \
          --sport football \
          --markets $market_key \
          --format csv \
          --file_path data/italy-serie-a_${season_formatted}_$market_label.csv \
          --headless \
          --concurrency_tasks 4
        
        if [ $? -eq 0 ]; then
            echo "$(date): [$COUNTER/$TOTAL] Italy $season 시즌 $market_label 마켓 완료 ✓"
        else
            echo "$(date): [$COUNTER/$TOTAL] Italy $season 시즌 $market_label 마켓 실패 ✗"
        fi
    done
done

# ================== NETHERLANDS 일부 (9 작업: 2019-2020, 2020-2021, 2021-2022) ==================
for season in "2019-2020" "2020-2021" "2021-2022"; do
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

echo "=== 배치 4 데이터 수집 완료 ==="
echo "$(date): 45개 작업 완료"
echo ""
echo "수집된 리그:"
echo "- Spain: 6개 시즌 × 3개 마켓 = 18개 파일"
echo "- Italy: 6개 시즌 × 3개 마켓 = 18개 파일"
echo "- Netherlands: 3개 시즌 × 3개 마켓 = 9개 파일"