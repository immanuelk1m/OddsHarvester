#!/bin/bash

# 배치 1: Belgium, Denmark, Switzerland 리그 데이터 수집
# 총 51개 작업 (Belgium 15 + Denmark 18 + Switzerland 18)

echo "=== 배치 1: Belgium, Denmark, Switzerland 데이터 수집 시작 ==="
echo "$(date): 총 51개 작업 시작"

COUNTER=0
TOTAL=51

# ================== BELGIUM (15 작업) ==================
# Belgium 2019-2020
for market in "over_under_2_5:2.5" "over_under_3:3.0" "over_under_3_5:3.5"; do
    IFS=':' read -r market_key market_label <<< "$market"
    COUNTER=$((COUNTER+1))
    echo "$(date): [$COUNTER/$TOTAL] Belgium 2019-2020 시즌 $market_label 마켓 수집 시작"
    uv run python src/main.py scrape_historic \
      --match_links_csv match_urls_complete/by_league/belgium/2019-2020.csv \
      --sport football \
      --markets $market_key \
      --format csv \
      --file_path data/belgium-jupiler-pro-league_2019_2020_$market_label.csv \
      --headless \
      --concurrency_tasks 1
    
    if [ $? -eq 0 ]; then
        echo "$(date): [$COUNTER/$TOTAL] Belgium 2019-2020 시즌 $market_label 마켓 완료 ✓"
    else
        echo "$(date): [$COUNTER/$TOTAL] Belgium 2019-2020 시즌 $market_label 마켓 실패 ✗"
    fi
done

# Belgium 2020-2021
for market in "over_under_2_5:2.5" "over_under_3:3.0" "over_under_3_5:3.5"; do
    IFS=':' read -r market_key market_label <<< "$market"
    COUNTER=$((COUNTER+1))
    echo "$(date): [$COUNTER/$TOTAL] Belgium 2020-2021 시즌 $market_label 마켓 수집 시작"
    uv run python src/main.py scrape_historic \
      --match_links_csv match_urls_complete/by_league/belgium/2020-2021.csv \
      --sport football \
      --markets $market_key \
      --format csv \
      --file_path data/belgium-jupiler-pro-league_2020_2021_$market_label.csv \
      --headless \
      --concurrency_tasks 1
    
    if [ $? -eq 0 ]; then
        echo "$(date): [$COUNTER/$TOTAL] Belgium 2020-2021 시즌 $market_label 마켓 완료 ✓"
    else
        echo "$(date): [$COUNTER/$TOTAL] Belgium 2020-2021 시즌 $market_label 마켓 실패 ✗"
    fi
done

# Belgium 2021-2022
for market in "over_under_2_5:2.5" "over_under_3:3.0" "over_under_3_5:3.5"; do
    IFS=':' read -r market_key market_label <<< "$market"
    COUNTER=$((COUNTER+1))
    echo "$(date): [$COUNTER/$TOTAL] Belgium 2021-2022 시즌 $market_label 마켓 수집 시작"
    uv run python src/main.py scrape_historic \
      --match_links_csv match_urls_complete/by_league/belgium/2021-2022.csv \
      --sport football \
      --markets $market_key \
      --format csv \
      --file_path data/belgium-jupiler-pro-league_2021_2022_$market_label.csv \
      --headless \
      --concurrency_tasks 1
    
    if [ $? -eq 0 ]; then
        echo "$(date): [$COUNTER/$TOTAL] Belgium 2021-2022 시즌 $market_label 마켓 완료 ✓"
    else
        echo "$(date): [$COUNTER/$TOTAL] Belgium 2021-2022 시즌 $market_label 마켓 실패 ✗"
    fi
done

# Belgium 2022-2023
for market in "over_under_2_5:2.5" "over_under_3:3.0" "over_under_3_5:3.5"; do
    IFS=':' read -r market_key market_label <<< "$market"
    COUNTER=$((COUNTER+1))
    echo "$(date): [$COUNTER/$TOTAL] Belgium 2022-2023 시즌 $market_label 마켓 수집 시작"
    uv run python src/main.py scrape_historic \
      --match_links_csv match_urls_complete/by_league/belgium/2022-2023.csv \
      --sport football \
      --markets $market_key \
      --format csv \
      --file_path data/belgium-jupiler-pro-league_2022_2023_$market_label.csv \
      --headless \
      --concurrency_tasks 1
    
    if [ $? -eq 0 ]; then
        echo "$(date): [$COUNTER/$TOTAL] Belgium 2022-2023 시즌 $market_label 마켓 완료 ✓"
    else
        echo "$(date): [$COUNTER/$TOTAL] Belgium 2022-2023 시즌 $market_label 마켓 실패 ✗"
    fi
done

# Belgium 2024-2025
for market in "over_under_2_5:2.5" "over_under_3:3.0" "over_under_3_5:3.5"; do
    IFS=':' read -r market_key market_label <<< "$market"
    COUNTER=$((COUNTER+1))
    echo "$(date): [$COUNTER/$TOTAL] Belgium 2024-2025 시즌 $market_label 마켓 수집 시작"
    uv run python src/main.py scrape_historic \
      --match_links_csv match_urls_complete/by_league/belgium/2024-2025.csv \
      --sport football \
      --markets $market_key \
      --format csv \
      --file_path data/belgium-jupiler-pro-league_2024_2025_$market_label.csv \
      --headless \
      --concurrency_tasks 1
    
    if [ $? -eq 0 ]; then
        echo "$(date): [$COUNTER/$TOTAL] Belgium 2024-2025 시즌 $market_label 마켓 완료 ✓"
    else
        echo "$(date): [$COUNTER/$TOTAL] Belgium 2024-2025 시즌 $market_label 마켓 실패 ✗"
    fi
done

# ================== DENMARK (18 작업) ==================
for season in "2019-2020" "2020-2021" "2021-2022" "2022-2023" "2023-2024" "2024-2025"; do
    for market in "over_under_2_5:2.5" "over_under_3:3.0" "over_under_3_5:3.5"; do
        IFS=':' read -r market_key market_label <<< "$market"
        COUNTER=$((COUNTER+1))
        season_formatted=$(echo $season | tr '-' '_')
        echo "$(date): [$COUNTER/$TOTAL] Denmark $season 시즌 $market_label 마켓 수집 시작"
        uv run python src/main.py scrape_historic \
          --match_links_csv match_urls_complete/by_league/denmark/$season.csv \
          --sport football \
          --markets $market_key \
          --format csv \
          --file_path data/denmark-superliga_${season_formatted}_$market_label.csv \
          --headless \
          --concurrency_tasks 1
        
        if [ $? -eq 0 ]; then
            echo "$(date): [$COUNTER/$TOTAL] Denmark $season 시즌 $market_label 마켓 완료 ✓"
        else
            echo "$(date): [$COUNTER/$TOTAL] Denmark $season 시즌 $market_label 마켓 실패 ✗"
        fi
    done
done

# ================== SWITZERLAND (18 작업) ==================
for season in "2019-2020" "2020-2021" "2021-2022" "2022-2023" "2023-2024" "2024-2025"; do
    for market in "over_under_2_5:2.5" "over_under_3:3.0" "over_under_3_5:3.5"; do
        IFS=':' read -r market_key market_label <<< "$market"
        COUNTER=$((COUNTER+1))
        season_formatted=$(echo $season | tr '-' '_')
        echo "$(date): [$COUNTER/$TOTAL] Switzerland $season 시즌 $market_label 마켓 수집 시작"
        uv run python src/main.py scrape_historic \
          --match_links_csv match_urls_complete/by_league/switzerland/$season.csv \
          --sport football \
          --markets $market_key \
          --format csv \
          --file_path data/switzerland-super-league_${season_formatted}_$market_label.csv \
          --headless \
          --concurrency_tasks 1
        
        if [ $? -eq 0 ]; then
            echo "$(date): [$COUNTER/$TOTAL] Switzerland $season 시즌 $market_label 마켓 완료 ✓"
        else
            echo "$(date): [$COUNTER/$TOTAL] Switzerland $season 시즌 $market_label 마켓 실패 ✗"
        fi
    done
done

echo "=== 배치 1 데이터 수집 완료 ==="
echo "$(date): 51개 작업 완료"
echo ""
echo "수집된 리그:"
echo "- Belgium: 5개 시즌 × 3개 마켓 = 15개 파일"
echo "- Denmark: 6개 시즌 × 3개 마켓 = 18개 파일"
echo "- Switzerland: 6개 시즌 × 3개 마켓 = 18개 파일"