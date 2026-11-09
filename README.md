# Cross-Market Forecasting and Long/Short Trading of Nifty IT Stocks

[Watch the project demonstration on YouTube](https://youtu.be/VhtQpD3C_rs).

**Team 16 · Data Science in Quantitative Finance DSA5205 · NUS**

Predict daily open-to-close returns for ten fixed Nifty IT constituents using information available at **08:55 IST**. Compare own-stock history, Indian peers, U.S. IT-services stocks, broad-market context, macro data and frontier AI releases. Forecasts determine **long, short or flat** positions; returns account for trading costs.

Choose one complete path:

| Path | Use it when | Starting data |
|---|---|---|
| **A — Clone and train (recommended)** | Using the complete data-bearing branch | Bundled preprocessed panels; no raw downloads or API key needed |
| **B — Rebuild from raw data** | Using a code-only ZIP, missing processed panels, or deliberately refreshing data | Download raw snapshots, audit, preprocess, then train |

Raw downloads under `data/raw/` are excluded from Git and LFS. Preprocessed panels and retained run evidence use LFS; small reference/metric CSVs use ordinary Git. Use Python **3.10–3.12**, Git and Git LFS. A ZIP may contain LFS pointers rather than actual panels; Path A requires `git lfs pull` or a data-complete archive.

The cohort reflects membership observed on 30 October 2026. The 2025–September 2026 evaluation is retrospective because these periods have already been inspected during development.

## Submission filenames (Project2.md, Section 7)

| Deliverable | Filename / submission method |
|---|---|
| Required report PDF | `Group_16_Report.pdf` |
| Editable report companion | `Group_16_Report.docx` |
| Video | [YouTube demo](https://youtu.be/VhtQpD3C_rs), supplied as a link in Canvas; MP4 is also permitted |
| Code with preprocessed data | `Group_16_Code_Preprocessed_Data.zip` — recommended for a clean training run |
| Code with raw and preprocessed data | `Group_16_Code_Full_Data.zip` — alternative complete local archive |
| Code with logs/results, without input data | `Group_16_Code_With_Logs.zip` |
| Code only, without data or logs | `Group_16_Code_Only.zip` — follow the raw rebuild instructions |

Only the report PDF filename is prescribed exactly by the assignment. The ZIP names above are consistent labels for the four editions, not additional course requirements. Submit one chosen code package or the GitHub link; the four editions are alternatives. The assignment also requires README commands, `requirements.txt`, runnable fetch/build/train/evaluate scripts, and reproducible settings. It prohibits secrets and large proprietary datasets; keep the full-data archive as a local alternative unless redistribution and submission are appropriate. The report must be 15–25 pages, and the video 15–25 minutes.

## A. Clone and train from preprocessed data — recommended

The shared branch is **[`v6-ritik`](https://github.com/whitetiger1399/project2QuantFin/tree/v6-ritik)**. It contains the pinned historical and January–September 2026 preprocessed datasets, configurations and retained experiment evidence. Clone this branch and restore its Git LFS objects before running Path A. Raw-data downloads and API keys are not required for this path.

### A1. Clone the data-bearing branch and install

```sh
git lfs install
git clone --branch v6-ritik https://github.com/whitetiger1399/project2QuantFin.git
cd project2QuantFin
git lfs pull
git lfs fsck
```

macOS / Linux:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

Skip environment creation if `.venv` exists. No shell switching is needed. `quantfin` is this repository’s own package, installed by `pip install -e .`.

### A2. Prepare a fresh session from bundled panels

```sh
python scripts/run_recording_demo.py prepare --session video_demo_02 --workers 3
```

This checks `data/preprocessed_bundle.json`, verifies the pinned dataset/configuration hashes, reuses the historical and 2026 panels, and creates new training output roots. Preprocessing and feature creation have already been completed in these panels. Existing EDA is retained with the supplied evidence. No raw data is required by this path.

Use an unused session name. If `video_demo_02` exists, choose `video_demo_03` in **every command** of this path. Workers are saved during prepare; use 1 or 2 on a machine with less memory.

### A3. Train, confirm, evaluate and inspect

Train and compare models on 2021–2022:

```sh
python scripts/run_recording_demo.py screen --session video_demo_02
```

Confirm the selection on 2023–2024 and freeze one specification:

```sh
python scripts/run_recording_demo.py confirm --session video_demo_02
```

Evaluate 2025 with quarterly refits and January–September 2026 with one pre-2026 fit of the frozen specification:

```sh
python scripts/run_recording_demo.py evaluate --session video_demo_02
```

Verify and display gross/net returns, daily positions and plot locations:

```sh
python scripts/run_recording_demo.py results --session video_demo_02
```

### A4. Find your results

All new outputs are under `artifacts/recording_demos/video_demo_02/`:

| Location | Contents |
|---|---|
| `session.json` | Exact dataset/run/freeze IDs, input mode and configuration hashes |
| `configs/` | Configuration copies resolved for your checkout and session |
| `logs/` | Terminal output and progress from each task |
| `model/runs/` | Screening, confirmation, final 2025 predictions, daily ledgers, metrics and plots |
| `model/freezes/` | Frozen selected specification |
| `model_2026/runs/` | January–September 2026 predictions, ledgers, metrics and plots |
| `results.csv` | Compounded gross/net returns for each segment and their combined period |
| `verification.json` | Hash, lineage, extension, daily-return and cost-accounting checks |

Each new model run has a UTC timestamp and content hash; sessions also have a unique ID. Existing sessions and completed stages are protected. Bundled input panels are read in place. Historical absolute paths inside their manifests describe the original machine; the bundle registry resolves input locations relative to the current checkout.

For detailed metrics, open `leaderboard.csv`, `annual_performance.csv`, `cost_sensitivity.csv`, `predictions.parquet`, `strategy_ledgers.parquet` and `plots/` inside the exact run recorded in `session.json`.

The preparation command verifies the bundled inputs and stops if a required file is missing or an LFS pointer has not been restored. Use `git lfs pull` after cloning; an ordinary code-only ZIP is not equivalent to a complete data checkout.

---

## B. Download raw data, preprocess and train — independent alternative

### B1. Install from a code-only checkout or extracted ZIP

Open a terminal in the extracted repository root (the folder containing `pyproject.toml`), then install:

macOS / Linux:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

Skip environment creation if `.venv` exists. No shell switching is needed. `quantfin` is this repository’s own package, installed by `pip install -e .`.

### B2. Restore reference inputs

If using a Git checkout, restore any LFS reference objects:

```sh
git lfs install
git lfs pull
git lfs fsck
```

Only if the generated membership CSVs are absent:

```sh
python scripts/prepare_provisional_memberships.py --execute
```

Existing membership files are protected; do not use `--overwrite` for the demo. For code-only ZIPs, obtain reference files from the source table below before continuing. Optional RBI/rainfall/calendar exports are described there; they are not automatically downloaded by these commands.

### B3. Download raw Yahoo data

```sh
python scripts/fetch_cross_market_markets.py --group india_core --execute
python scripts/fetch_cross_market_markets.py --group us_limited_tech --execute
python scripts/fetch_cross_market_markets.py --group us_it_services --execute
python scripts/fetch_cross_market_markets.py --group us_it_enabled_payments --execute
python scripts/fetch_cross_market_markets.py --group us_enterprise_software --execute
python scripts/fetch_cross_market_markets.py --group us_context --execute
python scripts/fetch_cross_market_markets.py --group indian_it_adrs --execute
python scripts/fetch_cross_market_markets.py --group global_context --execute
python scripts/fetch_cross_market_markets.py --group nifty50_point_in_time --membership-file data/external/manual/cross_market/nifty50_membership.csv --execute
python scripts/fetch_cross_market_markets.py --group sp500_point_in_time --membership-file data/external/manual/cross_market/sp500_membership.csv --execute
```

Optional Nifty 500 context (not required by this model):

```sh
python scripts/fetch_cross_market_markets.py --group nifty500_point_in_time --membership-file data/external/manual/cross_market/nifty500_membership.csv --execute
```

### B4. Download raw FRED/ALFRED data

Obtain a [FRED API key](https://fredaccount.stlouisfed.org/apikeys). This command prompts privately and passes the key only to the downloader; it works in zsh, Bash and PowerShell:

```sh
python -c "import getpass,os,subprocess,sys; env=dict(os.environ,FRED_API_KEY=getpass.getpass('FRED API key: ')); subprocess.run([sys.executable,'scripts/fetch_point_in_time_context.py','--config','configs/cross_market_data_2026-10-29.yaml','--start','2004-01-01','--end','2026-10-29','--output-root','data/raw/cross_market/fred_alfred','--execute'],env=env,check=True)"
```

### B5. Prepare AI snapshots and audit raw data

These ingest the restored reference files; they do not scrape new AI announcements. Epoch benchmark data is supplementary retrospective evidence, not a trading feature.

```sh
python scripts/build_frontier_ai_release_calendar.py --execute
python scripts/ingest_epoch_benchmark_snapshot.py --execute
python scripts/audit_cross_market_raw.py --required-group india_core --required-group us_limited_tech --required-group us_it_services --required-group us_it_enabled_payments --required-group us_enterprise_software --required-group us_context --required-group indian_it_adrs --required-group global_context --required-group nifty50_point_in_time --required-group sp500_point_in_time
```

Continue only after the audit passes; review any warnings and quarantine restrictions. These downloads create new snapshots rather than replacing previous model results.

### B6. Preprocess, engineer features and generate EDA

```sh
python scripts/run_recording_demo.py build --session video_demo_02 --workers 3
```

This cleans and quarantines audited anomalies, aligns market sessions and availability times, creates lag/rolling/peer/cross-market/context features, adds AI-capability inputs, and generates historical and 2026 EDA. It creates new source and model panels under this session. Do not run `prepare` for this path. Choose an unused session name before starting.

### B7. Train, confirm, evaluate and inspect

Train and compare models on 2021–2022:

```sh
python scripts/run_recording_demo.py screen --session video_demo_02
```

Confirm the selection on 2023–2024 and freeze one specification:

```sh
python scripts/run_recording_demo.py confirm --session video_demo_02
```

Evaluate 2025 with quarterly refits and January–September 2026 with one pre-2026 fit of the frozen specification:

```sh
python scripts/run_recording_demo.py evaluate --session video_demo_02
```

Verify and display gross/net returns, daily positions and plot locations:

```sh
python scripts/run_recording_demo.py results --session video_demo_02
```

Outputs and run-ID tracking follow the same layout described in A4. For this path, new processed panels and EDA also appear under the session’s `source/`, `source_2026/`, `model/` and `model_2026/` folders.

### Data sources for a code-only ZIP

Small CSVs supplied with a complete repository do not need a separate download. If the archive omits reference inputs, restore them as follows:

| Input | Source | Required local path |
|---|---|---|
| Current Nifty IT cohort | [NSE Indices](https://niftyindices.com/indices/equity/sectoral-indices/nifty-it) | `data/external/reference/current_constituents/ind_niftyitlist.csv` |
| Historical S&P 500 membership | [fja05680/sp500](https://github.com/fja05680/sp500) | `data/external/reference/current_constituents/S&P 500 Historical Components & Changes (Updated).csv` |
| Nifty 50/500 histories | [NiftyHistory](https://niftyhistory.in/) | `data/external/reference/current_constituents/nifty50_2001-01-01_to_2026-12-31.csv` and corresponding `nifty500_...csv` |
| AI releases and disclosed model sizes | Supplied curated catalogs with source URLs | `model_publishing.txt` in the constituent-reference folder; `configs/frontier_ai_release_whitelist.yaml` and `configs/frontier_ai_disclosed_parameters.yaml` |
| Epoch benchmark archive | [Epoch AI](https://epoch.ai/benchmarks/use-this-data) | `data/external/reference/epoch_ai/benchmark_data.zip` |

Epoch ingestion expects SHA-256 `28a006632f325e82c61ed28603056784ae185b5b596da6e019edd84fe02ddb43`; it is supplementary retrospective evidence. Current downloads may differ from that frozen archive. The raw rebuild uses the curated AI catalog rather than scraping new announcements automatically.

Optional RBI rates, rainfall and event calendars require timestamped official exports from [RBI](https://data.rbi.org.in/), [IMD](https://mausam.imd.gov.in/imd_latest/contents/index_rainfall_state_new.php), [NSE](https://www.nseindia.com/resources/exchange-communication-holidays) or [NYSE](https://www.nyse.com/markets/hours-calendars). Empty templates contribute no observations. Do not substitute invented values. Changed vendor history, source coverage or optional inputs can change rebuilt results.

### Troubleshooting for either path

| Problem | Action |
|---|---|
| `No module named quantfin` | Activate the intended environment and run `python -m pip install -e .` from the repository root. |
| LFS pointer or bundle hash mismatch | Run `git lfs pull` and `git lfs fsck`. Do not edit panels to bypass verification. Use Path B if processed data was omitted. |
| Session already exists | Choose a new name for a fresh run; preserve the existing session. |
| Interrupted training | Preserve the folder and logs. The wrapper does not automatically resume; the underlying experiment runner supports exact-ID resumption with unchanged settings. |
| `.running` exists after a shutdown | Confirm no process still uses the session before addressing a stale lock. |
| Raw audit fails | Resolve the reported blocking issues. Review quarantine restrictions when warnings are present. |
| PowerShell activation is blocked | Use `.\.venv\Scripts\python.exe` in place of `python` for install/run commands. |

### Reports, checks and repository layout

[Video deck](reports/video/Group_16_Video_Deck.pdf) · [Report DOCX](reports/Group_16_Report.docx) · [Report PDF](reports/Group_16_Report.pdf) · [Recording commands](reports/video/recording_commands.md) · [Assignment](documents/markdown/Project2.md)

Training does not automatically rewrite the report or supplementary hypothesis studies. Report evidence must be rebound and verified explicitly. Source code is in `src/quantfin/`, executable entry points in `scripts/`, and research contracts in `configs/`. Raw inputs stay local; the bundle registry pins existing processed inputs under `artifacts/recording_demos/video_demo_01/`. All prior logs, runs and analysis evidence are retained.

Local checks (no downloads or model training):

```sh
python -m unittest discover -s tests -p test_recording_demo.py -v
python -m unittest discover -s tests/leakage -v
```

The [submission cleanup inventory](SUBMISSION_CLEANUP.md) lists removed internal documents, narration deliverables and unused assets. All Python files and research run evidence are retained.
