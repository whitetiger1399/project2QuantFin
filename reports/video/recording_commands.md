# Recording commands

Choose **one complete path**. Stay in your existing shell. Run commands sequentially and stop if a command fails. Use an unused session name consistently; the examples use `video_demo_02`.

## A. Clone with preprocessed data — recommended

### 1. Restore the repository and activate the environment

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

### 2. Prepare bundled preprocessed data

```sh
python scripts/run_recording_demo.py prepare --session video_demo_02 --workers 3
```

Verifies and reuses the already cleaned, engineered historical and 2026 datasets. No raw downloads or API keys are needed.

### 3. Screening

```sh
python scripts/run_recording_demo.py screen --session video_demo_02
```

### 4. Confirmation and freeze

```sh
python scripts/run_recording_demo.py confirm --session video_demo_02
```

### 5. Final evaluation and 2026 extension

```sh
python scripts/run_recording_demo.py evaluate --session video_demo_02
```

### 6. Verify and show results

```sh
python scripts/run_recording_demo.py results --session video_demo_02
```

Logs, models, plots, `session.json`, `results.csv` and `verification.json` are under `artifacts/recording_demos/video_demo_02/`. The exact training runs are recorded in `session.json`; existing results are protected.

---

## B. Code-only checkout — download raw data and rebuild

Use this path if the preprocessed panels are absent or a raw rebuild is intended. Run from the extracted repository root. The complete source links and missing-reference-file paths are in [README Path B](../../README.md#b-download-raw-data-preprocess-and-train--independent-alternative).

### 1. Activate the environment

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

### 2. Restore reference inputs

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

Existing membership files are protected; do not use `--overwrite` for the demo. For code-only ZIPs, obtain reference files from the source table in README Path B before continuing. Optional RBI/rainfall/calendar exports are described there; they are not automatically downloaded by these commands.

### 3. Download raw Yahoo data

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

### 4. Download raw FRED/ALFRED data

Obtain a [FRED API key](https://fredaccount.stlouisfed.org/apikeys). This command prompts privately and passes the key only to the downloader; it works in zsh, Bash and PowerShell:

```sh
python -c "import getpass,os,subprocess,sys; env=dict(os.environ,FRED_API_KEY=getpass.getpass('FRED API key: ')); subprocess.run([sys.executable,'scripts/fetch_point_in_time_context.py','--config','configs/cross_market_data_2026-10-29.yaml','--start','2004-01-01','--end','2026-10-29','--output-root','data/raw/cross_market/fred_alfred','--execute'],env=env,check=True)"
```

### 5. Prepare AI snapshots and audit raw data

These ingest the restored reference files; they do not scrape new AI announcements. Epoch benchmark data is supplementary retrospective evidence, not a trading feature.

```sh
python scripts/build_frontier_ai_release_calendar.py --execute
python scripts/ingest_epoch_benchmark_snapshot.py --execute
python scripts/audit_cross_market_raw.py --required-group india_core --required-group us_limited_tech --required-group us_it_services --required-group us_it_enabled_payments --required-group us_enterprise_software --required-group us_context --required-group indian_it_adrs --required-group global_context --required-group nifty50_point_in_time --required-group sp500_point_in_time
```

Continue only after the audit passes; review any warnings and quarantine restrictions. These downloads create new snapshots rather than replacing previous model results.

### 6. Preprocess, create features and EDA

```sh
python scripts/run_recording_demo.py build --session video_demo_02 --workers 3
```

### 7. Train, confirm, evaluate and show results

```sh
python scripts/run_recording_demo.py screen --session video_demo_02
python scripts/run_recording_demo.py confirm --session video_demo_02
python scripts/run_recording_demo.py evaluate --session video_demo_02
python scripts/run_recording_demo.py results --session video_demo_02
```

Run one command at a time. Outputs use the same session layout as Path A, plus newly built panels and EDA. Raw downloads remain local and excluded from Git. During the recording, Path A is sufficient to demonstrate a fresh complete model run from preprocessed inputs.
