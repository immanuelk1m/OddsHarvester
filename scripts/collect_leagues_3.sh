#!/bin/bash
# Processor 3: France, Portugal, Norway
# Seasons: 2018-2019 to 2024-2025 (France, Portugal), 2018-2024 (Norway)
# Markets: over_under_2_5, over_under_3, over_under_3_5

echo "Starting Processor 3: France, Portugal, Norway"

# France (france-ligue-1)
echo "Processing France..."
for season in "2018-2019" "2019-2020" "2020-2021" "2021-2022" "2022-2023" "2023-2024" "2024-2025"; do
    echo "France season: $season"
    uv run python src/main.py scrape_historic \
        --sport football \
        --leagues france-ligue-1 \
        --season "$season" \
        --markets over_under_2_5,over_under_3,over_under_3_5 \
        --storage local \
        --format csv \
        --file_path "data/france_${season}.csv" \
        --headless \
        --concurrency_tasks 1
done

# Portugal (liga-portugal)
echo "Processing Portugal..."
for season in "2018-2019" "2019-2020" "2020-2021" "2021-2022" "2022-2023" "2023-2024" "2024-2025"; do
    echo "Portugal season: $season"
    uv run python src/main.py scrape_historic \
        --sport football \
        --leagues liga-portugal \
        --season "$season" \
        --markets over_under_2_5,over_under_3,over_under_3_5 \
        --storage local \
        --format csv \
        --file_path "data/portugal_${season}.csv" \
        --headless \
        --concurrency_tasks 1
done

# Norway (norway-eliteserien) - Single year format
echo "Processing Norway..."
for year in "2018" "2019" "2020" "2021" "2022" "2023" "2024"; do
    echo "Norway year: $year"
    uv run python src/main.py scrape_historic \
        --sport football \
        --leagues norway-eliteserien \
        --season "$year" \
        --markets over_under_2_5,over_under_3,over_under_3_5 \
        --storage local \
        --format csv \
        --file_path "data/norway_${year}.csv" \
        --headless \
        --concurrency_tasks 1
done

echo "Processor 3 completed!"