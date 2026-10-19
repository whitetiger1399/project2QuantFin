# Quantitative Finance Project 2

This repository contains the staged research pipeline for a daily SPY timing study. The core data are daily Yahoo Finance observations for SPY, QQQ, IWM, TLT, and GLD from 2005 through 2025. SPY is the only traded asset; the other ETFs are predictors. Stooq is an optional verification source and is never silently merged into the Yahoo series.

The current implementation covers environment setup, immutable source snapshots, data audits, conservative cleaning, a research panel, causal feature creation, delayed labels, split assignment, source comparison, and timing checks. Model fitting and portfolio evaluation come after this data layer passes its quality gates.

## Timing convention

For each observed trading session `t`:

1. Features are calculated after the close of `t`.
2. The target position executes at the close of `t+1`.
3. The label is the adjusted-close return from `t+1` to `t+2`.
4. That label can enter a future training fit only after the close of `t+2`.

This deliberate delay prevents a same-close look-ahead assumption. The feature output contains both causal predictors and future labels, so later training code must enforce `label_available_session <= fit_cutoff` at every refit.

## Cross-platform setup

Python 3.10 or newer is required; Python 3.11 is the recommended common version for macOS and Windows. Open a terminal in the repository directory—the directory containing this README and `pyproject.toml`—before running the commands below. The code uses `pathlib` and project-relative paths, so no source file contains a required user-specific or operating-system-specific data path.

Use `python -m quantfin` in scripts because it works even when the environment's console-script directory is not on `PATH`. After installation, the shorter `quantfin` command is equivalent.

### Apple Silicon macOS (`arm64`)

Use a native Apple Silicon Python rather than a Python running through Rosetta:

```bash
python3 --version
python3 -c "import platform; print(platform.machine())"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .
python -m quantfin --help
```

The architecture command should print `arm64`.

### Intel macOS (`x86_64`)

```bash
python3 --version
python3 -c "import platform; print(platform.machine())"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .
python -m quantfin --help
```

The architecture command should print `x86_64`.

### Intel/AMD Windows using PowerShell

Open PowerShell in the repository directory. Quote the path when it contains spaces:

```powershell
Set-Location 'C:\path\to\project2QuantFin'
py -3.11 --version
py -3.11 -c "import platform; print(platform.machine())"
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .
python -m quantfin --help
```

On a conventional 64-bit Intel Windows laptop, Python usually reports `AMD64`; that label includes Intel-compatible 64-bit Windows installations. If PowerShell blocks the activation script, allow it for the current process only and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Intel/AMD Windows using Command Prompt

```bat
cd /d C:\path\to\project2QuantFin
py -3.11 --version
py -3.11 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .
python -m quantfin --help
```

To return to the environment in a later terminal session, activate the existing `.venv`; do not recreate it. Use `deactivate` to leave it.

After a successful setup, record exact installed versions for the reproducibility package:

```bash
python -m pip freeze > requirements-lock.txt
```

`requirements.txt` and `pyproject.toml` contain bounded, cross-platform direct dependencies. `requirements-lock.txt`, produced on the working machine, records the complete resolved environment. Keep separate lock files when the team uses different operating systems, for example `requirements-lock-macos-arm64.txt` and `requirements-lock-windows-amd64.txt`, because transitive wheels can be platform-specific.

## Configuration review

Before downloading anything, review:

- `configs/protocol.yaml`: symbols, sample dates, timing, splits, and paths.
- `configs/features.yaml`: trailing windows and feature-set membership.

The Yahoo end date is exclusive. The configured `2026-01-01` endpoint includes sessions through 31 December 2025. Changing a source, asset, sample boundary, or timing rule after inspecting validation results is a research decision and should be recorded.

## Data pipeline commands

Run one command at a time and inspect the generated manifest or report before continuing.

### 1. Fetch the primary Yahoo snapshot

```bash
python -m quantfin fetch --source yahoo
```

This creates a timestamped folder such as `data/raw/yahoo/yahoo_YYYYMMDDTHHMMSSZ/`. It stores one Parquet file per symbol and a `manifest.json` with request settings, coverage, versions, and hashes. A later fetch creates a new snapshot and does not overwrite the old one.

If a request fails, inspect `FAILED.json` in the newly created snapshot directory. A failed directory has no `manifest.json` and is ignored when a later command selects the latest completed snapshot.

### 2. Audit the latest Yahoo snapshot

```bash
python -m quantfin audit-data
```

Inspect the printed `artifacts/data_audits/.../quality_report.json`. The audit reports duplicates, nulls, impossible OHLC relationships, nonpositive prices, negative or zero volume, weekend records, corporate-action counts, and predictor-session differences relative to observed SPY sessions.

To audit a particular snapshot:

```bash
python -m quantfin audit-data --snapshot-id yahoo_YYYYMMDDTHHMMSSZ
```

Export dividend, split, and capital-gain event windows separately:

```bash
python -m quantfin audit-actions
```

Inspect `artifacts/corporate_actions/.../action_report.json`, `events.parquet`, and `event_windows.parquet`. The cash-dividend calculation is a diagnostic rather than an assumption that it exactly matches the vendor's adjustment method. Split windows require manual review because vendor "raw" prices can already contain split normalization.

### 3. Clean and align market data

```bash
python -m quantfin clean
```

The cleaning command stops on conflicting duplicates, structurally impossible bars, nonpositive prices, negative volumes, weekend rows, or missing adjusted closes. It retains structurally valid extreme returns and zero-volume rows for investigation. It does not forward-fill market prices.

The output contains:

- `market_long.parquet`: one row per session and symbol.
- `market_panel.parquet`: one row per observed SPY session, with asset/field columns.
- `manifest.json`: source hashes, cleaning rules, coverage, and remaining predictor null counts.

### 4. Fetch and compare the optional Stooq verification source

```bash
python -m quantfin fetch --source stooq
python -m quantfin verify-sources
```

Stooq is optional and its public download service can be unavailable, rate limited, moved, or require credentials. A failed fetch writes `FAILED.json` and prints a concise error without a traceback. Running `verify-sources` without a completed Stooq snapshot records `comparison_skipped.json`, returns successfully, and allows the Yahoo pipeline to continue.

When Stooq succeeds, inspect `artifacts/source_verification/.../comparison.json`. Differences may reflect adjustment conventions or session definitions. This diagnostic never modifies the Yahoo data and does not authorize joining the two vendors.

### 5. Build features and delayed labels

```bash
python -m quantfin build-features
```

This writes a new `data/processed/features_.../` dataset containing:

- trailing SPY returns, momentum, moving averages, volatility, drawdown, intraday, and volume features;
- QQQ, IWM, TLT, and GLD momentum and cross-asset relationships;
- signal, entry, label-end, and label-availability sessions;
- the delayed target return;
- warmup, training, screening, confirmation, and final-test labels.

No full-sample scaler, imputer, clipping threshold, or learned feature selector is applied at this stage. Those transformations belong inside each past-only training fit.

### 6. Audit temporal alignment

```bash
python -m quantfin check-timing
```

Inspect `artifacts/timing_audits/.../timing_report.json`. The command checks that signal, entry, and label sessions are ordered correctly, labels reconstruct from their stored entry and exit prices, and signal sessions are unique.

### 7. Inspect the selected manifests

```bash
python -m quantfin show-manifest --kind yahoo
python -m quantfin show-manifest --kind stooq
python -m quantfin show-manifest --kind market
python -m quantfin show-manifest --kind features
```

All commands default to the latest completed matching snapshot or dataset. For reproducible report runs, pass explicit IDs rather than relying on `latest` behavior:

```bash
python -m quantfin clean --snapshot-id yahoo_YYYYMMDDTHHMMSSZ
python -m quantfin build-features --market-dataset-id market_yahoo_YYYYMMDDTHHMMSSZ
python -m quantfin check-timing --feature-dataset-id features_yahoo_YYYYMMDDTHHMMSSZ_CONFIGHASH
```

## Useful inspection commands

These Python commands work on macOS and Windows and read generated files without changing them:

```bash
python -c "import pandas as pd; p='data/processed/MARKET_DATASET_ID/market_panel.parquet'; d=pd.read_parquet(p); print(d.info()); print(d.head()); print(d.tail())"

python -c "import pandas as pd; p='data/processed/FEATURE_DATASET_ID/features_and_labels.parquet'; d=pd.read_parquet(p); print(d.shape); print(d[['signal_session','entry_session','label_end_session','target_return','split']].tail())"
```

Replace `MARKET_DATASET_ID` and `FEATURE_DATASET_ID` with the directory names printed by the pipeline.

## Data and legal notes

Yahoo/yfinance is used for educational research. Review Yahoo's terms before use and do not publish the downloaded raw dataset unless redistribution is permitted. The repository excludes `data/raw`, `data/processed`, and generated `artifacts`; submit the scripts and retrieval instructions instead.

Adjusted Close is treated as a vendor-provided total-return research proxy. It is a synthetic adjusted series rather than an exchange execution price. Raw OHLC, dividends, and splits are retained for a later corporate-action reconciliation. Do not add dividends again to returns computed from Adjusted Close.

Stooq is only an independent check. Its price-adjustment semantics must be reconciled before interpreting differences. The core pipeline never fills one vendor's missing data with another vendor's values.

## Troubleshooting

### No completed Stooq snapshot

If Stooq returns HTML, a moved-page response, a rate-limit response, or a credential requirement, the fetch ends with exit code 3 and points to its `FAILED.json`. This does not invalidate the primary Yahoo dataset. Record the skipped comparison and continue:

```bash
python -m quantfin verify-sources
python -m quantfin clean
python -m quantfin build-features
python -m quantfin check-timing
```

### `quantfin` is not recognized on Windows

Use the module form, which does not depend on the console-script `PATH`:

```powershell
python -m quantfin --help
```

If that fails with `No module named quantfin`, activate `.venv` and rerun `python -m pip install -e .` from the repository directory.

### Wrong Python or environment

Use these portable checks:

```bash
python -c "import sys, platform; print(sys.executable); print(sys.version); print(platform.system(), platform.machine())"
python -m pip --version
python -m pip show project2-quantfin
```

The Python and pip paths should both point inside `.venv`. If they do not, reactivate the environment using the operating-system-specific command above.

### Re-running immutable stages

Fetching creates a new timestamped snapshot. Cleaning the same snapshot or rebuilding the same feature/configuration combination intentionally refuses to overwrite its previous output. Use the existing manifest, or fetch a new source snapshot after intentionally changing the protocol. Do not delete prior research artifacts merely to hide a failed or changed experiment.

## Current boundary

The next implementation phase is the walk-forward modeling and portfolio layer: training-only preprocessing, expanding and five-year rolling fits, forecast baselines, ridge/elastic-net/tree/RFF models, monthly refits, immutable predictions, trade accounting, costs, benchmark metrics, and reporting. The research design and work sequence are documented in [documents/markdown/AGENT_ACTION_PLAN.md](documents/markdown/AGENT_ACTION_PLAN.md).

