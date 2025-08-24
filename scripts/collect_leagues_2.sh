#!/bin/bash
# Processor 2: Italy, Spain, Sweden
# Seasons: 2018-2019 to 2024-2025 (Italy, Spain), 2018-2024 (Sweden)
# Markets: over_under_2_5, over_under_3, over_under_3_5

echo "Starting Processor 2: Italy, Spain, Sweden"

# Italy (italy-serie-a)
echo "Processing Italy..."
for season in "2018-2019" "2019-2020" "2020-2021" "2021-2022" "2022-2023" "2023-2024" "2024-2025"; do
    echo "Italy season: $season"
    uv run python src/main.py scrape_historic \
        --sport football \
        --leagues italy-serie-a \
        --season "$season" \
        --markets over_under_2_5,over_under_3,over_under_3_5 \
        --storage local \
        --format csv \
        --file_path "data/italy_${season}.csv" \
        --headless \
        --concurrency_tasks 1
done

# Spain (spain-laliga)
echo "Processing Spain..."
for season in "2018-2019" "2019-2020" "2020-2021" "2021-2022" "2022-2023" "2023-2024" "2024-2025"; do
    echo "Spain season: $season"
    uv run python src/main.py scrape_historic \
        --sport football \
        --leagues spain-laliga \
        --season "$season" \
        --markets over_under_2_5,over_under_3,over_under_3_5 \
        --storage local \
        --format csv \
        --file_path "data/spain_${season}.csv" \
        --headless \
        --concurrency_tasks 1
done

# Sweden (sweden-allsvenskan) - Single year format
echo "Processing Sweden..."
for year in "2018" "2019" "2020" "2021" "2022" "2023" "2024"; do
    echo "Sweden year: $year"
    uv run python src/main.py scrape_historic \
        --sport football \
        --leagues sweden-allsvenskan \
        --season "$year" \
        --markets over_under_2_5,over_under_3,over_under_3_5 \
        --storage local \
        --format csv \
        --file_path "data/sweden_${year}.csv" \
        --headless \
        --concurrency_tasks 1
done

echo "Processor 2 completed!"