# Cross-Market Nifty IT Data Acquisition Runbook

**Date:** 29 October 2026  
**Scope:** Raw-data acquisition only for the fixed cohort of companies that are Nifty IT constituents on 30 October 2026. No cleaning, feature construction, model fitting, or report regeneration is performed here. This is a retrospective fixed-cohort study, not a historical replication of Nifty IT membership.

## 1. Source contract

| Layer | Source | Automated? | Point-in-time control |
|---|---|---:|---|
| India and global daily OHLCV/actions | Yahoo Finance through `yfinance` | Yes | Immutable retrieval snapshot; exchange session must have finished before 08:55 IST |
| Fed rates, Treasury yields, spreads, dollar, USD/INR, VIX | FRED/ALFRED API | Yes, API key | `output_type=4` initial-release observations and `realtime_start` |
| Current Nifty IT cohort definition | Official NSE Indices constituent file | Local verified file | Fixed as of 30 October 2026; historical membership is not inferred |
| Historical S&P 500 membership | WRDS/CRSP/Compustat or another licensed point-in-time source | No | `valid_from`, `valid_to`, `announced_at` |
| RBI policy and bank lending rates | RBI DBIE/publications | Official export/manual | `published_at` and `effective_at` |
| NSE/NYSE holidays and special sessions | Official exchange calendars | Official export/manual | `announced_at` |
| FOMC/RBI/macro/earnings/rebalance events | Official historical calendars | Official export/manual | scheduled and actual release timestamps |
| Rainfall | IMD | Official export/manual | `published_at` and `revision_at` |

Current constituent lists are not valid replacements for historical membership. Here the current list deliberately defines a fixed retrospective cohort. The full S&P 500 experiment uses the separately prepared provisional point-in-time reconstruction and must disclose its limitations.

## 2. Setup

Run from the repository root:

```bash
cd /Users/whitetiger/Desktop/WhiteTiger/17_projects/24_Project2_QuantFin/project2QuantFin
source .venv/bin/activate
python -m pip install -e .
```

The new scripts are plan-only unless `--execute` is explicitly supplied.

## 3. Inspect every automated market request

Run these commands one at a time and inspect the symbols and dates printed:

```bash
python scripts/fetch_cross_market_markets.py --group india_core
```

```bash
python scripts/fetch_cross_market_markets.py --group india_extended
```

```bash
python scripts/fetch_cross_market_markets.py --group us_limited_tech
```

```bash
python scripts/fetch_cross_market_markets.py --group us_context
```

```bash
python scripts/fetch_cross_market_markets.py --group indian_it_adrs
```

```bash
python scripts/fetch_cross_market_markets.py --group global_context
```

## 4. Download the automated market groups

Execute sequentially to reduce throttling:

```bash
python scripts/fetch_cross_market_markets.py --group india_core --execute
```

```bash
python scripts/fetch_cross_market_markets.py --group india_extended --execute
```

```bash
python scripts/fetch_cross_market_markets.py --group us_limited_tech --execute
```

```bash
python scripts/fetch_cross_market_markets.py --group us_context --execute
```

```bash
python scripts/fetch_cross_market_markets.py --group indian_it_adrs --execute
```

```bash
python scripts/fetch_cross_market_markets.py --group global_context --execute
```

Each command prints a snapshot identifier. Retain it. Required groups stop if any ticker fails. Optional groups commit a manifest with the failed tickers recorded.

To resume an incomplete required group, use the exact identifier printed in its directory name:

```bash
python scripts/fetch_cross_market_markets.py --group GROUP_NAME --execute --resume-snapshot EXACT_SNAPSHOT_ID
```

Do not type `GROUP_NAME` or `EXACT_SNAPSHOT_ID` literally.

## 5. Obtain and download FRED/ALFRED data

Create a free FRED API key at <https://fredaccount.stlouisfed.org/apikeys>. In zsh, enter it without echoing it:

```bash
read -s "FRED_API_KEY?FRED API key: "
export FRED_API_KEY
echo
```

Never paste the key into chat, source code, a command saved in shell history, or a committed `.env` file. If a key is exposed, revoke it in the FRED account and generate a replacement before continuing. The downloader uses the `certifi` CA bundle so macOS framework Python can verify the FRED HTTPS certificate without disabling TLS verification.

Inspect the request:

```bash
python scripts/fetch_point_in_time_context.py --config configs/cross_market_data_2026-10-29.yaml --start 2004-01-01 --end 2026-10-29 --output-root data/raw/cross_market/fred_alfred
```

Execute it:

```bash
python scripts/fetch_point_in_time_context.py --config configs/cross_market_data_2026-10-29.yaml --start 2004-01-01 --end 2026-10-29 --output-root data/raw/cross_market/fred_alfred --execute
```

The script splits the ALFRED real-time interval into adjacent five-year periods because the API limits each JSON request to 2,000 vintage dates. For the expanded fixed-cohort configuration the progress bar counts 85 requests (17 series × 5 periods), then combines and deduplicates the initial-release observations by series. The four India additions are the overnight call-money rate, discount rate, long-term government-bond yield, and CPI. These are lower-frequency context variables and must not be mislabeled as an exact daily RBI policy-repo series.

If FRED reports that a financial series has no ALFRED archive, the script downloads that series once as a current-vintage FRED history and records `availability_mode: current_vintage_fallback`. Such a series requires a later official effective-date/release-time audit and cannot be described as release-vintage data. All other series remain `alfred_initial_release`.

Remove the key from the current shell after the request:

```bash
unset FRED_API_KEY
```

## 6. Prepare official/manual files

Create a working directory and copy non-destructive templates:

```bash
mkdir -p data/external/manual/cross_market
cp -n resources/data_templates/*.csv data/external/manual/cross_market/
```

Populate the files without changing their headers:

1. `nifty_it_membership.csv`: obtain historical Nifty IT membership from NSE Indices. Include delisted and former members.
2. `sp500_membership.csv`: obtain point-in-time S&P 500 membership through NUS/WRDS if available. Map historical identifiers to Yahoo tickers carefully.

The user-supplied Nifty IT reconstruction is retained at
`data/external/reference/unverified/nifty_it_constituent_snapshots_user_supplied_2001_2025.csv`.
It is quarantined because its source review found chronological and constituent-count contradictions.
See `documents/markdown/NIFTY_IT_MEMBERSHIP_SOURCE_REVIEW_2026-10-30.md`. Do not copy this
candidate into the manual input directory or use it for modelling until the review's acceptance
contract has been satisfied.
3. `rbi_rates.csv`: export policy repo, SDF/reverse repo, MSF, bank rate, CRR, SLR, WALR on fresh/outstanding loans, and one-year median MCLR from RBI DBIE/publications. Record original publication and effective dates.
4. `nse_holidays.csv` and `nyse_holidays.csv`: use official exchange calendars, including special and shortened sessions.
5. `scheduled_events.csv`: use official FOMC, RBI MPC, US macro-release, earnings, and index-rebalance histories.
6. `global_events.csv`: record only the first verified public timestamp; eventual crisis end dates are retrospective metadata.
7. `imd_rainfall.csv`: obtain official daily/subdivisional or all-India data with publication and revision timestamps.

Every data row must retain its source URL. Blank templates deliberately fail validation.

Inspect which manual files are present:

```bash
python scripts/ingest_cross_market_manual_data.py
```

After populating all files, validate and create an immutable snapshot:

```bash
python scripts/ingest_cross_market_manual_data.py --require-all --execute
```

If sources arrive in stages, ingest a specific subset by repeating `--source`, for example:

```bash
python scripts/ingest_cross_market_manual_data.py --source nifty_it_membership --source sp500_membership --execute
```

## 7. Download the point-in-time membership unions

Only after the corresponding membership CSV has been populated and validated:

```bash
python scripts/fetch_cross_market_markets.py --group nifty_it_point_in_time --membership-file data/external/manual/cross_market/nifty_it_membership.csv
```

```bash
python scripts/fetch_cross_market_markets.py --group nifty_it_point_in_time --membership-file data/external/manual/cross_market/nifty_it_membership.csv --execute
```

The S&P 500 union is the largest request and should run last:

```bash
python scripts/fetch_cross_market_markets.py --group sp500_point_in_time --membership-file data/external/manual/cross_market/sp500_membership.csv
```

```bash
python scripts/fetch_cross_market_markets.py --group sp500_point_in_time --membership-file data/external/manual/cross_market/sp500_membership.csv --execute
```

Delisted securities may not be available from Yahoo. Their failures are evidence of a coverage limitation, not permission to remove those historical members silently. If material coverage is missing, obtain CRSP/NSE security histories through the licensed source.

## 8. Audit the completed raw layer

First audit the automated core before the two membership-union downloads:

```bash
python scripts/audit_cross_market_raw.py --required-group india_core --required-group us_limited_tech --required-group us_context --required-group indian_it_adrs
```

After both point-in-time union downloads and the official manual snapshot are complete:

```bash
python scripts/audit_cross_market_raw.py --required-group india_core --required-group us_limited_tech --required-group us_context --required-group indian_it_adrs --required-group nifty_it_point_in_time --required-group sp500_point_in_time
```

The audit exits with status 2 when required evidence is missing or a blocking hash/structure check fails. `pass_with_warnings` is permitted only when every warning has an explicit downstream cleaning restriction. The current Yahoo snapshot records two such restrictions: use `INR=X` close-to-close only because its vendor OHLC envelopes are inconsistent, and quarantine the `NIFTYBEES.NS` row dated 7 July 2009 from open-to-close calculations because its reported open is zero.

## 9. Expected raw directories

```text
data/raw/cross_market/
├── yahoo/
│   ├── yahoo_india_core_.../
│   ├── yahoo_us_limited_tech_.../
│   ├── yahoo_us_context_.../
│   ├── yahoo_indian_it_adrs_.../
│   ├── yahoo_nifty_it_point_in_time_.../
│   └── yahoo_sp500_point_in_time_.../
├── fred_alfred/
│   └── fred_alfred_.../
└── manual_official/
    └── manual_official_.../
```

Every completed directory contains `manifest.json`. Incomplete or failed downloads contain `state.json` and/or `FAILED.json` but no completed manifest.

## 10. Recorded symbol changes

The configuration maps LTIMindtree's old NSE symbol `LTIM` to `LTM`, effective 27 February 2026, using the official NSE circular. The current Yahoo request therefore uses `LTM.NS`. Downstream cleaning must map both exchange symbols to the stable security identifier `INE214T01019` rather than treating the rename as a new company.
