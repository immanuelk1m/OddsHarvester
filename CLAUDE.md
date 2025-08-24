# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

OddsHarvester is a web scraper for oddsportal.com that extracts sports betting odds and match data. It uses Playwright for browser automation and supports both upcoming and historical odds extraction across multiple sports and markets.

## Architecture

### Core Components
- **CLI Layer** (`src/cli/`): Argument parsing, validation, and command routing
- **Scraper Core** (`src/core/`): Playwright-based browser automation and data extraction
  - `OddsPortalScraper`: Main scraper orchestrator
  - `OddsPortalMarketExtractor`: Handles market-specific extraction logic
  - Market extraction modules in `market_extraction/`: Specialized extractors for odds parsing, history, and submarkets
- **Storage Layer** (`src/storage/`): Local (JSON/CSV) and remote (S3) data persistence
- **Utils** (`src/utils/`): Sport/market constants, proxy management, logging

### Key Design Patterns
- Command pattern for CLI operations (`command_enum.py`)
- Registry pattern for sport-market mappings (`sport_market_registry.py`)
- Strategy pattern for storage types (`storage_manager.py`)
- Factory pattern for market extractors based on sport type

## Common Commands

### Development Setup
```bash
# Install uv package manager and sync dependencies
pip install uv
uv sync

# Install Playwright browser (required for scraping)
uv run playwright install chromium
```

### Running the Scraper
```bash
# Scrape upcoming matches
uv run python src/main.py scrape_upcoming --sport football --date 20250101 --markets 1x2 --headless

# Scrape historical data
uv run python src/main.py scrape_historic --sport football --leagues england-premier-league --season 2022-2023 --markets 1x2 --headless

# Get help
uv run python src/main.py --help
```

### Testing
```bash
# Run all tests with coverage
uv run pytest --cov=src/core --cov=src/utils --cov=src/cli --cov=src/storage --cov-report=term

# Run specific test file
uv run pytest tests/core/test_odds_portal_scraper.py

# Run tests matching pattern
uv run pytest -k "test_market"
```

### Code Quality
```bash
# Run linter and formatter
uv run ruff check src tests
uv run ruff format src tests

# Auto-fix linting issues
uv run ruff check --fix src tests
```

## Project Structure

```
src/
├── cli/                    # CLI interface and argument handling
├── core/                   # Scraping logic and browser automation
│   ├── market_extraction/  # Market-specific data extractors
│   └── *.py               # Core scraper classes
├── storage/               # Data persistence (local/S3)
├── utils/                 # Constants, enums, helpers
├── main.py               # Entry point for CLI
└── lambda_handler.py     # AWS Lambda entry point

tests/                    # Comprehensive test suite
```

## Key Implementation Details

### Sport and Market Configuration
- Sports and markets defined in `src/utils/sport_market_constants.py`
- League mappings in `src/utils/sport_league_constants.py`
- Sport-market relationships managed by `SportMarketRegistry`
- Adding new sports/markets requires updating these constants and registry

### Browser Automation
- Uses Playwright with Chromium by default
- Supports headless/headful modes
- Proxy rotation capability via `ProxyManager`
- Browser fingerprinting customization (user agent, timezone, locale)

### Data Extraction Flow
1. URL building based on sport/league/date parameters
2. Page navigation and market tab selection
3. Submarket extraction (visible or all via modal interaction)
4. Bookmaker odds parsing with optional history tracking
5. Data aggregation and storage

### Storage Options
- **Local**: JSON or CSV format with customizable file paths
- **Remote**: S3 bucket upload (requires AWS credentials)
- Storage abstraction allows easy extension for new storage types

### Concurrency and Performance
- Configurable concurrent task execution (`--concurrency_tasks`)
- Preview mode (`--preview_submarkets_only`) for faster, limited data extraction
- Batch processing support for multiple leagues/dates

## Important Notes

- The scraper respects `--match_links` as highest priority, overriding other filters
- When both `--leagues` and `--date` provided, leagues take precedence
- Proxy region should match browser locale/timezone for best results
- Tests use mocked Playwright pages to avoid actual web scraping
- Lambda deployment uses Docker due to Playwright's size requirements