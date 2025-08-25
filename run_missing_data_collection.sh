#!/bin/bash

# 누락된 데이터 수집 스크립트
# 순차적으로 모든 작업을 자동 실행

echo "=== 누락된 데이터 수집 시작 ==="
echo "$(date): 총 13개 작업 시작"

# 1. 이탈리아 2021-2022 시즌 3.5 마켓
echo "$(date): [1/13] 이탈리아 2021-2022 시즌 3.5 마켓 수집 시작"
uv run python src/main.py scrape_historic \
  --match_links_csv match_urls_complete/by_league/italy/2021-2022.csv \
  --sport football \
  --markets over_under_3_5 \
  --format csv \
  --file_path data/italy-serie-a_2021_2022_3.5.csv \
  --headless \
  --concurrency_tasks 4 

if [ $? -eq 0 ]; then
    echo "$(date): [1/13] 이탈리아 2021-2022 시즌 3.5 마켓 완료 ✓"
else
    echo "$(date): [1/13] 이탈리아 2021-2022 시즌 3.5 마켓 실패 ✗"
fi

# 2. 네덜란드 2021-2022 시즌 3.5 마켓
echo "$(date): [2/13] 네덜란드 2021-2022 시즌 3.5 마켓 수집 시작"
uv run python src/main.py scrape_historic \
  --match_links_csv match_urls_complete/by_league/netherlands/2021-2022.csv \
  --sport football \
  --markets over_under_3_5 \
  --format csv \
  --file_path data/eredivisie_2021_2022_3.5.csv \
  --headless \
  --concurrency_tasks 4 

if [ $? -eq 0 ]; then
    echo "$(date): [2/13] 네덜란드 2021-2022 시즌 3.5 마켓 완료 ✓"
else
    echo "$(date): [2/13] 네덜란드 2021-2022 시즌 3.5 마켓 실패 ✗"
fi

# 3. 네덜란드 2024-2025 시즌 2.5 마켓
echo "$(date): [3/13] 네덜란드 2024-2025 시즌 2.5 마켓 수집 시작"
uv run python src/main.py scrape_historic \
  --match_links_csv match_urls_complete/by_league/netherlands/2024-2025.csv \
  --sport football \
  --markets over_under_2_5 \
  --format csv \
  --file_path data/eredivisie_2024_2025_2.5.csv \
  --headless \
  --concurrency_tasks 4 

if [ $? -eq 0 ]; then
    echo "$(date): [3/13] 네덜란드 2024-2025 시즌 2.5 마켓 완료 ✓"
else
    echo "$(date): [3/13] 네덜란드 2024-2025 시즌 2.5 마켓 실패 ✗"
fi

# 4. 네덜란드 2024-2025 시즌 3.0 마켓
echo "$(date): [4/13] 네덜란드 2024-2025 시즌 3.0 마켓 수집 시작"
uv run python src/main.py scrape_historic \
  --match_links_csv match_urls_complete/by_league/netherlands/2024-2025.csv \
  --sport football \
  --markets over_under_3 \
  --format csv \
  --file_path data/eredivisie_2024_2025_3.0.csv \
  --headless \
  --concurrency_tasks 4 

if [ $? -eq 0 ]; then
    echo "$(date): [4/13] 네덜란드 2024-2025 시즌 3.0 마켓 완료 ✓"
else
    echo "$(date): [4/13] 네덜란드 2024-2025 시즌 3.0 마켓 실패 ✗"
fi

# 5. 네덜란드 2024-2025 시즌 3.5 마켓
echo "$(date): [5/13] 네덜란드 2024-2025 시즌 3.5 마켓 수집 시작"
uv run python src/main.py scrape_historic \
  --match_links_csv match_urls_complete/by_league/netherlands/2024-2025.csv \
  --sport football \
  --markets over_under_3_5 \
  --format csv \
  --file_path data/eredivisie_2024_2025_3.5.csv \
  --headless \
  --concurrency_tasks 4 

if [ $? -eq 0 ]; then
    echo "$(date): [5/13] 네덜란드 2024-2025 시즌 3.5 마켓 완료 ✓"
else
    echo "$(date): [5/13] 네덜란드 2024-2025 시즌 3.5 마켓 실패 ✗"
fi

# 6. 덴마크 2023-2024 시즌 2.5 마켓
echo "$(date): [6/13] 덴마크 2023-2024 시즌 2.5 마켓 수집 시작"
uv run python src/main.py scrape_historic \
  --match_links_csv match_urls_complete/by_league/denmark/2023-2024.csv \
  --sport football \
  --markets over_under_2_5 \
  --format csv \
  --file_path data/denmark-superliga_2023_2024_2.5.csv \
  --headless \
  --concurrency_tasks 4 

if [ $? -eq 0 ]; then
    echo "$(date): [6/13] 덴마크 2023-2024 시즌 2.5 마켓 완료 ✓"
else
    echo "$(date): [6/13] 덴마크 2023-2024 시즌 2.5 마켓 실패 ✗"
fi

# 7. 덴마크 2023-2024 시즌 3.0 마켓
echo "$(date): [7/13] 덴마크 2023-2024 시즌 3.0 마켓 수집 시작"
uv run python src/main.py scrape_historic \
  --match_links_csv match_urls_complete/by_league/denmark/2023-2024.csv \
  --sport football \
  --markets over_under_3 \
  --format csv \
  --file_path data/denmark-superliga_2023_2024_3.0.csv \
  --headless \
  --concurrency_tasks 4 

if [ $? -eq 0 ]; then
    echo "$(date): [7/13] 덴마크 2023-2024 시즌 3.0 마켓 완료 ✓"
else
    echo "$(date): [7/13] 덴마크 2023-2024 시즌 3.0 마켓 실패 ✗"
fi

# 8. 덴마크 2023-2024 시즌 3.5 마켓
echo "$(date): [8/13] 덴마크 2023-2024 시즌 3.5 마켓 수집 시작"
uv run python src/main.py scrape_historic \
  --match_links_csv match_urls_complete/by_league/denmark/2023-2024.csv \
  --sport football \
  --markets over_under_3_5 \
  --format csv \
  --file_path data/denmark-superliga_2023_2024_3.5.csv \
  --headless \
  --concurrency_tasks 4 

if [ $? -eq 0 ]; then
    echo "$(date): [8/13] 덴마크 2023-2024 시즌 3.5 마켓 완료 ✓"
else
    echo "$(date): [8/13] 덴마크 2023-2024 시즌 3.5 마켓 실패 ✗"
fi

# 9. 덴마크 2024-2025 시즌 2.5 마켓
echo "$(date): [9/13] 덴마크 2024-2025 시즌 2.5 마켓 수집 시작"
uv run python src/main.py scrape_historic \
  --match_links_csv match_urls_complete/by_league/denmark/2024-2025.csv \
  --sport football \
  --markets over_under_2_5 \
  --format csv \
  --file_path data/denmark-superliga_2024_2025_2.5.csv \
  --headless \
  --concurrency_tasks 4 

if [ $? -eq 0 ]; then
    echo "$(date): [9/13] 덴마크 2024-2025 시즌 2.5 마켓 완료 ✓"
else
    echo "$(date): [9/13] 덴마크 2024-2025 시즌 2.5 마켓 실패 ✗"
fi

# 10. 덴마크 2024-2025 시즌 3.0 마켓
echo "$(date): [10/13] 덴마크 2024-2025 시즌 3.0 마켓 수집 시작"
uv run python src/main.py scrape_historic \
  --match_links_csv match_urls_complete/by_league/denmark/2024-2025.csv \
  --sport football \
  --markets over_under_3 \
  --format csv \
  --file_path data/denmark-superliga_2024_2025_3.0.csv \
  --headless \
  --concurrency_tasks 4 

if [ $? -eq 0 ]; then
    echo "$(date): [10/13] 덴마크 2024-2025 시즌 3.0 마켓 완료 ✓"
else
    echo "$(date): [10/13] 덴마크 2024-2025 시즌 3.0 마켓 실패 ✗"
fi

# 11. 덴마크 2024-2025 시즌 3.5 마켓
echo "$(date): [11/13] 덴마크 2024-2025 시즌 3.5 마켓 수집 시작"
uv run python src/main.py scrape_historic \
  --match_links_csv match_urls_complete/by_league/denmark/2024-2025.csv \
  --sport football \
  --markets over_under_3_5 \
  --format csv \
  --file_path data/denmark-superliga_2024_2025_3.5.csv \
  --headless \
  --concurrency_tasks 4 

if [ $? -eq 0 ]; then
    echo "$(date): [11/13] 덴마크 2024-2025 시즌 3.5 마켓 완료 ✓"
else
    echo "$(date): [11/13] 덴마크 2024-2025 시즌 3.5 마켓 실패 ✗"
fi

# 12. 벨기에 2020-2021 시즌 2.5 마켓
echo "$(date): [12/13] 벨기에 2020-2021 시즌 2.5 마켓 수집 시작"
uv run python src/main.py scrape_historic \
  --match_links_csv match_urls_complete/by_league/belgium/2020-2021.csv \
  --sport football \
  --markets over_under_2_5 \
  --format csv \
  --file_path data/belgium-jupiler-pro-league_2020_2021_2.5.csv \
  --headless \
  --concurrency_tasks 4 

if [ $? -eq 0 ]; then
    echo "$(date): [12/13] 벨기에 2020-2021 시즌 2.5 마켓 완료 ✓"
else
    echo "$(date): [12/13] 벨기에 2020-2021 시즌 2.5 마켓 실패 ✗"
fi

# 13. 벨기에 2020-2021 시즌 3.0 마켓
echo "$(date): [13/13] 벨기에 2020-2021 시즌 3.0 마켓 수집 시작"
uv run python src/main.py scrape_historic \
  --match_links_csv match_urls_complete/by_league/belgium/2020-2021.csv \
  --sport football \
  --markets over_under_3 \
  --format csv \
  --file_path data/belgium-jupiler-pro-league_2020_2021_3.0.csv \
  --headless \
  --concurrency_tasks 4 

if [ $? -eq 0 ]; then
    echo "$(date): [13/13] 벨기에 2020-2021 시즌 3.0 마켓 완료 ✓"
else
    echo "$(date): [13/13] 벨기에 2020-2021 시즌 3.0 마켓 실패 ✗"
fi

echo "=== 모든 데이터 수집 완료 ==="
echo "$(date): 13개 작업 완료"
echo ""
echo "수집된 파일:"
echo "- data/italy-serie-a_2021_2022_3.5.csv"
echo "- data/eredivisie_2021_2022_3.5.csv"
echo "- data/eredivisie_2024_2025_2.5.csv"
echo "- data/eredivisie_2024_2025_3.0.csv"
echo "- data/eredivisie_2024_2025_3.5.csv"
echo "- data/denmark-superliga_2023_2024_2.5.csv"
echo "- data/denmark-superliga_2023_2024_3.0.csv"
echo "- data/denmark-superliga_2023_2024_3.5.csv"
echo "- data/denmark-superliga_2024_2025_2.5.csv"
echo "- data/denmark-superliga_2024_2025_3.0.csv"
echo "- data/denmark-superliga_2024_2025_3.5.csv"
echo "- data/belgium-jupiler-pro-league_2020_2021_2.5.csv"
echo "- data/belgium-jupiler-pro-league_2020_2021_3.0.csv"