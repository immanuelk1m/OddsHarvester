#!/bin/bash

# 특정 CSV 파일 삭제 후 재수집 스크립트
# Eredivisie, Germany Bundesliga, Liga Portugal 데이터 재수집

echo "=== 특정 데이터 파일 삭제 및 재수집 시작 ==="
echo "$(date): 작업 시작"

# ============================
# 1. 파일 삭제 섹션
# ============================

echo ""
echo "=== 1. 데이터 파일 삭제 ==="

# 삭제할 파일 목록
files_to_delete=(
    "data/eredivisie_2021_2022_3.0.csv"
    "data/eredivisie_2024_2025_3.5.csv"
    "data/germany-bundesliga_2024_2025_2.5.csv"
    "data/germany-bundesliga_2024_2025_3.0.csv"
    "data/germany-bundesliga_2024_2025_3.5.csv"
    "data/liga-portugal_2024_2025_2.5.csv"
    "data/liga-portugal_2024_2025_3.0.csv"
    "data/liga-portugal_2024_2025_3.5.csv"
)

# 파일 삭제 실행
for file in "${files_to_delete[@]}"; do
    if [ -f "$file" ]; then
        rm "$file"
        echo "$(date): $file 삭제됨 ✓"
    else
        echo "$(date): $file 파일이 존재하지 않음"
    fi
done

echo ""
echo "=== 파일 삭제 완료 ==="
echo "잠시 대기..."
sleep 3

# ============================
# 2. 데이터 재수집 섹션
# ============================

echo ""
echo "=== 2. 데이터 재수집 시작 ==="

# Eredivisie 2021-2022 시즌 - 3.0 마켓
echo ""
echo "=== Eredivisie 2021-2022 재수집 ==="

url_file="match_urls_complete/by_league/netherlands/2021-2022.csv"
if [ -f "$url_file" ]; then
    url_count=$(($(wc -l < "$url_file") - 1))
    echo "$(date): Eredivisie 2021-2022 ${url_count}개 경기 URL 발견"
    
    echo "$(date): Eredivisie 2021-2022 3.0 마켓 수집 시작 (${url_count} 경기)"
    uv run python src/main.py scrape_historic \
        --sport football \
        --match_links_csv "$url_file" \
        --markets over_under_3 \
        --format csv \
        --file_path "data/eredivisie_2021_2022_3.0.csv" \
        --headless \
        --concurrency_tasks 4
    
    if [ $? -eq 0 ]; then
        echo "$(date): Eredivisie 2021-2022 3.0 마켓 완료 ✓"
    else
        echo "$(date): Eredivisie 2021-2022 3.0 마켓 실패 ✗"
    fi
else
    echo "$(date): Eredivisie 2021-2022 URL 파일이 없음"
fi

echo "잠시 대기..."
sleep 5

# Eredivisie 2024-2025 시즌 - 3.5 마켓
echo ""
echo "=== Eredivisie 2024-2025 재수집 ==="

url_file="match_urls_complete/by_league/netherlands/2024-2025.csv"
if [ -f "$url_file" ]; then
    url_count=$(($(wc -l < "$url_file") - 1))
    echo "$(date): Eredivisie 2024-2025 ${url_count}개 경기 URL 발견"
    
    echo "$(date): Eredivisie 2024-2025 3.5 마켓 수집 시작 (${url_count} 경기)"
    uv run python src/main.py scrape_historic \
        --sport football \
        --match_links_csv "$url_file" \
        --markets over_under_3_5 \
        --format csv \
        --file_path "data/eredivisie_2024_2025_3.5.csv" \
        --headless \
        --concurrency_tasks 4
    
    if [ $? -eq 0 ]; then
        echo "$(date): Eredivisie 2024-2025 3.5 마켓 완료 ✓"
    else
        echo "$(date): Eredivisie 2024-2025 3.5 마켓 실패 ✗"
    fi
else
    echo "$(date): Eredivisie 2024-2025 URL 파일이 없음"
fi

echo "잠시 대기..."
sleep 5

# Germany Bundesliga 2024-2025 시즌 - 2.5, 3.0, 3.5 마켓
echo ""
echo "=== Germany Bundesliga 2024-2025 재수집 ==="

url_file="match_urls_complete/by_league/germany/2024-2025.csv"
if [ -f "$url_file" ]; then
    url_count=$(($(wc -l < "$url_file") - 1))
    echo "$(date): Germany Bundesliga 2024-2025 ${url_count}개 경기 URL 발견"
    
    germany_markets=("2.5" "3.0" "3.5")
    
    for market in "${germany_markets[@]}"; do
        echo "$(date): Germany Bundesliga 2024-2025 ${market} 마켓 수집 시작 (${url_count} 경기)"
        
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
            --match_links_csv "$url_file" \
            --markets $market_param \
            --format csv \
            --file_path "data/germany-bundesliga_2024_2025_${market}.csv" \
            --headless \
            --concurrency_tasks 4
        
        if [ $? -eq 0 ]; then
            echo "$(date): Germany Bundesliga 2024-2025 ${market} 마켓 완료 ✓"
        else
            echo "$(date): Germany Bundesliga 2024-2025 ${market} 마켓 실패 ✗"
        fi
        
        echo "잠시 대기..."
        sleep 5
    done
else
    echo "$(date): Germany Bundesliga 2024-2025 URL 파일이 없음"
fi

# Liga Portugal 2024-2025 시즌 - 2.5, 3.0, 3.5 마켓
echo ""
echo "=== Liga Portugal 2024-2025 재수집 ==="

url_file="match_urls_complete/by_league/portugal/2024-2025.csv"
if [ -f "$url_file" ]; then
    url_count=$(($(wc -l < "$url_file") - 1))
    echo "$(date): Liga Portugal 2024-2025 ${url_count}개 경기 URL 발견"
    
    portugal_markets=("2.5" "3.0" "3.5")
    
    for market in "${portugal_markets[@]}"; do
        echo "$(date): Liga Portugal 2024-2025 ${market} 마켓 수집 시작 (${url_count} 경기)"
        
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
            --match_links_csv "$url_file" \
            --markets $market_param \
            --format csv \
            --file_path "data/liga-portugal_2024_2025_${market}.csv" \
            --headless \
            --concurrency_tasks 4
        
        if [ $? -eq 0 ]; then
            echo "$(date): Liga Portugal 2024-2025 ${market} 마켓 완료 ✓"
        else
            echo "$(date): Liga Portugal 2024-2025 ${market} 마켓 실패 ✗"
        fi
        
        echo "잠시 대기..."
        sleep 5
    done
else
    echo "$(date): Liga Portugal 2024-2025 URL 파일이 없음"
fi

echo ""
echo "$(date): 모든 재수집 작업 완료"
echo ""
echo "=== 재수집 요약 ==="
echo "삭제된 파일: 8개"
echo "재수집된 파일:"
echo "- Eredivisie 2021-2022: 3.0 마켓 (1개)"
echo "- Eredivisie 2024-2025: 3.5 마켓 (1개)"
echo "- Germany Bundesliga 2024-2025: 2.5, 3.0, 3.5 마켓 (3개)"
echo "- Liga Portugal 2024-2025: 2.5, 3.0, 3.5 마켓 (3개)"
echo "총 8개 파일 재수집 완료"