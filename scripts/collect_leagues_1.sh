#!/bin/bash
# Processor 1: Belgium, Switzerland, England
# Seasons: 2018-2019 to 2024-2025
# Markets: over_under_2_5, over_under_3, over_under_3_5

echo "Starting Processor 1: Belgium, Switzerland, England"

# Belgium (belgium-jupiler-pro-league)
echo "Processing Belgium..."
for season in "2018-2019" "2019-2020" "2020-2021" "2021-2022" "2022-2023" "2023-2024" "2024-2025"; do
    echo "Belgium season: $season"
    uv run python src/main.py scrape_historic \
        --sport football \
        --leagues belgium-jupiler-pro-league \
        --season "$season" \
        --markets over_under_2_5,over_under_3,over_under_3_5 \
        --storage local \
        --format csv \
        --file_path "data/belgium_${season}.csv" \
        --headless \
        --concurrency_tasks 1
done

# Switzerland (switzerland-super-league)
echo "Processing Switzerland..."
for season in "2018-2019" "2019-2020" "2020-2021" "2021-2022" "2022-2023" "2023-2024" "2024-2025"; do
    echo "Switzerland season: $season"
    uv run python src/main.py scrape_historic \
        --sport football \
        --leagues switzerland-super-league \
        --season "$season" \
        --markets over_under_2_5,over_under_3,over_under_3_5 \
        --storage local \
        --format csv \
        --file_path "data/switzerland_${season}.csv" \
        --headless \
        --concurrency_tasks 1
done

# England (england-premier-league)
echo "Processing England..."
for season in "2018-2019" "2019-2020" "2020-2021" "2021-2022" "2022-2023" "2023-2024" "2024-2025"; do
    echo "England season: $season"
    uv run python src/main.py scrape_historic \
        --sport football \
        --leagues england-premier-league \
        --season "$season" \
        --markets over_under_2_5,over_under_3,over_under_3_5 \
        --storage local \
        --format csv \
        --file_path "data/england_${season}.csv" \
        --headless \
        --concurrency_tasks 1
done

echo "Processor 1 completed!"