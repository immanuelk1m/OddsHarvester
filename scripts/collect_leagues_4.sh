#!/bin/bash
# Processor 4: Denmark, Germany, Netherlands, Scotland
# Seasons: 2018-2019 to 2024-2025
# Markets: over_under_2_5, over_under_3, over_under_3_5

echo "Starting Processor 4: Denmark, Germany, Netherlands, Scotland"

# Denmark (denmark-superliga)
echo "Processing Denmark..."
for season in "2018-2019" "2019-2020" "2020-2021" "2021-2022" "2022-2023" "2023-2024" "2024-2025"; do
    echo "Denmark season: $season"
    uv run python src/main.py scrape_historic \
        --sport football \
        --leagues denmark-superliga \
        --season "$season" \
        --markets over_under_2_5,over_under_3,over_under_3_5 \
        --storage local \
        --format csv \
        --file_path "data/denmark_${season}.csv" \
        --headless \
        --concurrency_tasks 1
done

# Germany (germany-bundesliga)
echo "Processing Germany..."
for season in "2018-2019" "2019-2020" "2020-2021" "2021-2022" "2022-2023" "2023-2024" "2024-2025"; do
    echo "Germany season: $season"
    uv run python src/main.py scrape_historic \
        --sport football \
        --leagues germany-bundesliga \
        --season "$season" \
        --markets over_under_2_5,over_under_3,over_under_3_5 \
        --storage local \
        --format csv \
        --file_path "data/germany_${season}.csv" \
        --headless \
        --concurrency_tasks 1
done

# Netherlands (eredivisie) - CORRECTED LEAGUE ID
echo "Processing Netherlands..."
for season in "2018-2019" "2019-2020" "2020-2021" "2021-2022" "2022-2023" "2023-2024" "2024-2025"; do
    echo "Netherlands season: $season"
    uv run python src/main.py scrape_historic \
        --sport football \
        --leagues eredivisie \
        --season "$season" \
        --markets over_under_2_5,over_under_3,over_under_3_5 \
        --storage local \
        --format csv \
        --file_path "data/netherlands_${season}.csv" \
        --headless \
        --concurrency_tasks 1
done

# Scotland (scotland-premiership)
echo "Processing Scotland..."
for season in "2018-2019" "2019-2020" "2020-2021" "2021-2022" "2022-2023" "2023-2024" "2024-2025"; do
    echo "Scotland season: $season"
    uv run python src/main.py scrape_historic \
        --sport football \
        --leagues scotland-premiership \
        --season "$season" \
        --markets over_under_2_5,over_under_3,over_under_3_5 \
        --storage local \
        --format csv \
        --file_path "data/scotland_${season}.csv" \
        --headless \
        --concurrency_tasks 1
done

echo "Processor 4 completed!"