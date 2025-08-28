#!/bin/bash

# 불완전한 데이터 파일들 재수집 스크립트
# Belgium Jupiler Pro League: 2024-2025 (3.0)
# Denmark Superliga: 2021-2022, 2022-2023 (3.0)

echo "=== 불완전한 데이터 재수집 시작 ==="
echo "$(date): 작업 시작"

# Belgium Jupiler Pro League 2024-2025 시즌 - 3.0 마켓만
echo ""
echo "=== Belgium Jupiler Pro League 2024-2025 재수집 ==="

season="2024-2025"
market="3.0"
url_file="match_urls_complete/by_league/belgium/${season}.csv"

if [ ! -f "$url_file" ]; then
    echo "$(date): ${season} URL 파일이 없음, 일반 수집 모드 사용"
    echo "$(date): Belgium Jupiler Pro League ${season} ${market} 마켓 수집 시작"
    uv run python src/main.py scrape_historic \
        --sport football \
        --leagues belgium-jupiler-pro-league \
        --season $season \
        --markets over_under_3 \
        --format csv \
        --file_path "data/belgium-jupiler-pro-league_${season//-/_}_${market}.csv" \
        --headless \
        --concurrency_tasks 4
    
    if [ $? -eq 0 ]; then
        echo "$(date): Belgium Jupiler Pro League ${season} ${market} 마켓 완료 ✓"
    else
        echo "$(date): Belgium Jupiler Pro League ${season} ${market} 마켓 실패 ✗"
    fi
else
    url_count=$(($(wc -l < "$url_file") - 1))
    echo "$(date): ${season} 시즌 ${url_count}개 경기 URL 발견"
    
    echo "$(date): Belgium Jupiler Pro League ${season} ${market} 마켓 수집 시작 (${url_count} 경기)"
    uv run python src/main.py scrape_historic \
        --sport football \
        --match_links_csv "$url_file" \
        --markets over_under_3 \
        --format csv \
        --file_path "data/belgium-jupiler-pro-league_${season//-/_}_${market}.csv" \
        --headless \
        --concurrency_tasks 4
    
    if [ $? -eq 0 ]; then
        echo "$(date): Belgium Jupiler Pro League ${season} ${market} 마켓 완료 ✓"
    else
        echo "$(date): Belgium Jupiler Pro League ${season} ${market} 마켓 실패 ✗"
    fi
fi

echo "잠시 대기..."
sleep 5

# Denmark Superliga 재수집 - 2021-2022 (3.0), 2022-2023 (2.5, 3.0, 3.5)
echo ""
echo "=== Denmark Superliga 재수집 ==="

denmark_seasons=("2021-2022" "2022-2023")
denmark_2021_markets=("3.0")
denmark_2022_markets=("2.5" "3.0" "3.5")

for season in "${denmark_seasons[@]}"; do
    denmark_url_file="match_urls_complete/by_league/denmark/${season}.csv"
    
    # 시즌별로 다른 마켓 사용
    if [ "$season" = "2021-2022" ]; then
        markets=("${denmark_2021_markets[@]}")
    else
        markets=("${denmark_2022_markets[@]}")
    fi
    
    if [ -f "$denmark_url_file" ]; then
        url_count=$(($(wc -l < "$denmark_url_file") - 1))  # 헤더 제외
        echo "$(date): Denmark Superliga ${season} ${url_count}개 경기 URL 발견"
        
        # --match_links_csv 파라미터 사용
        for market in "${markets[@]}"; do
            echo "$(date): Denmark Superliga ${season} ${market} 마켓 수집 시작 (${url_count} 경기)"
            
            # 마켓 값에 따라 적절한 파라미터 설정
            if [ "$market" = "2.5" ]; then
                market_param="over_under_2_5"
            elif [ "$market" = "3.0" ]; then
                market_param="over_under_3"
            elif [ "$market" = "3.5" ]; then
                market_param="over_under_3_5"
            fi
            
            uv run python src/main.py scrape_historic \
                --sport football \
                --match_links_csv "$denmark_url_file" \
                --markets $market_param \
                --format csv \
                --file_path "data/denmark-superliga_${season//-/_}_${market}.csv" \
                --headless \
                --concurrency_tasks 4
            
            if [ $? -eq 0 ]; then
                echo "$(date): Denmark Superliga ${season} ${market} 마켓 완료 ✓"
            else
                echo "$(date): Denmark Superliga ${season} ${market} 마켓 실패 ✗"
            fi
            
            echo "잠시 대기..."
            sleep 5
        done
    else
        echo "Denmark ${season} URL 파일 없음, 일반 수집 모드 사용"
        for market in "${markets[@]}"; do
            echo "$(date): Denmark Superliga ${season} ${market} 마켓 수집 시작"
            
            # 마켓 값에 따라 적절한 파라미터 설정
            if [ "$market" = "2.5" ]; then
                market_param="over_under_2_5"
            elif [ "$market" = "3.0" ]; then
                market_param="over_under_3"
            elif [ "$market" = "3.5" ]; then
                market_param="over_under_3_5"
            fi
            
            uv run python src/main.py scrape_historic \
                --sport football \
                --leagues denmark-superliga \
                --season $season \
                --markets $market_param \
                --format csv \
                --file_path "data/denmark-superliga_${season//-/_}_${market}.csv" \
                --headless \
                --concurrency_tasks 4
            
            if [ $? -eq 0 ]; then
                echo "$(date): Denmark Superliga ${season} ${market} 마켓 완료 ✓"
            else
                echo "$(date): Denmark Superliga ${season} ${market} 마켓 실패 ✗"
            fi
            
            echo "잠시 대기..."
            sleep 5
        done
    fi
done

echo ""
echo "$(date): 모든 불완전한 데이터 재수집 작업 완료"
echo ""
echo "재수집된 파일들:"
echo "- Belgium Jupiler Pro League 2024-2025: 3.0 마켓 (1개 파일)"
echo "- Denmark Superliga 2021-2022: 3.0 마켓 (1개 파일)"
echo "- Denmark Superliga 2022-2023: 2.5, 3.0, 3.5 마켓 (3개 파일)"
echo "총 5개 파일 재수집 완료"콛