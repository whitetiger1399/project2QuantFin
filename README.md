# Quantitative Finance Project 2

The active v3 research setup predicts same-day open-to-close returns for a fixed cohort of current Nifty IT constituents using only information available at 08:55 IST. It progressively compares own-stock, Indian-market, US-technology, global, broad S&P 500, macro, and nonlinear information while preserving temporal order.

The implementation covers immutable source snapshots, audits, conservative cleaning, causal feature creation, exploratory and statistical analysis, resumable walk-forward model fitting, chronological selection, final-test freezing, portfolio evaluation, and report-ready plots. Every new dataset, analysis, experiment, model summary, and freeze receives a UTC timestamp plus a deterministic content hash.

Use the single active configuration in [`configs/cross_market_research.yaml`](configs/cross_market_research.yaml). The [cross-market methodology](documents/markdown/CROSS_MARKET_RESEARCH_METHODOLOGY_2026-10-30.md) defines the hypotheses, information clock, feature ladder, validation protocol, and evaluation. The [execution runbook](documents/markdown/CROSS_MARKET_EXECUTION_RUNBOOK_2026-10-30.md) contains the exact sequential terminal commands.

The earlier SPY study and its frozen artifacts remain below as read-only historical evidence. They are not a second active model setup and must not be mixed with v3 cross-market selection or reporting.

### Archived v1 verified run

The verification scripts and final-holdout sections of the report are bound to the following immutable October 20, 2026 artifact chain. The report also includes the separate comparative screening and confirmation runs listed below.

| Object | Identifier |
|---|---|
| Yahoo snapshot | `yahoo_20261020T055638Z` |
| Clean market dataset | `market_yahoo_20261020T055638Z` |
| Feature dataset | `features_yahoo_20261020T055638Z_799f619a4f` |
| Screening run | `models_screening_fe6e26bdd5521077` |
| Confirmation run | `models_confirmation_96d234651d29fb8c` |
| Frozen selection | `freeze_82db313e0d1839a6` |
| Final test run | `models_final_test_3e46f0e36fd220d6` |
| Comparative screening | `models_screening_d7252adb14317fcd` |
| Comparative confirmation | `models_confirmation_87083937c8d58d9b` |

The final run completed all 144 planned fits with no invalid checkpoints and 100% prediction coverage. To verify the immutable chain and rebuild the academic report without retraining:

```bash
python scripts/verify_outputs.py
python reports/build_report_ieee.py
python /path/to/render_docx.py reports/Project2_Team16_Report.docx --output_dir reports/_rendered --emit_pdf
cp reports/_rendered/Project2_Team16_Report.pdf reports/Project2_Team16_Report.pdf
```

The first two commands regenerate the verification records and DOCX from the canonical run. The rendering step performs visual QA and produces the PDF. The repository-specific renderer path used by Codex is documented in `reports/README.md`; a normal local LibreOffice installation can also export the DOCX as PDF.

## Optional comparative model research

`configs/models_comparison.yaml` is a separate research configuration. It compares Ridge, Lasso, Elastic Net, PCA-Ridge, Random Forest, Extra Trees, Histogram Gradient Boosting and Random Fourier Features plus the historical-mean and autoregressive baselines. It does not modify or replace the frozen canonical run. Run screening first, retain the top three distinct predictive families, and confirm those families on the next chronological period. Do not run a comparative final holdout unless a new freeze is intentionally created.

The screening plan contains 37 configurations and 1,776 expanding-window fits. The exact command sequence is documented in `scripts/summarize_model_comparison.py` usage and should be run from the repository root.

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

## Git LFS for processed data and research artifacts

The repository tracks Parquet, CSV, plot, PDF, DOCX, ZIP and MP4 files through Git LFS. Raw Yahoo/Stooq downloads remain ignored because vendor redistribution terms can differ. Processed datasets, intermediate checkpoints, run artifacts and report outputs are no longer ignored.

Install Git LFS once, then initialize and check this repository:

```bash
git lfs install
python scripts/setup_git_lfs.py --install
git lfs track
```

The same commands work in macOS Terminal, Windows PowerShell and Windows Command Prompt when `git` and `git-lfs` are on `PATH`. To stage the research package:

```bash
git add .gitattributes .gitignore
git add data/processed artifacts reports assets
git lfs ls-files
git status --short
```

Inspect `git status` before committing. A Git host can enforce per-file, repository and LFS-storage quotas; check the course repository limits before the first large push.

## Build the academic report

The report builder reads completed immutable outputs and does not retrain models:

```bash
python scripts/verify_outputs.py
python reports/build_report_ieee.py
```

The generated editable report is `reports/Project2_Team16_Report.docx`. See `reports/README.md` for PDF rendering and author-roster instructions.

## Configuration review

The new India-before-open cross-market Nifty IT study has a separate raw-data contract. Follow the dated [cross-market data acquisition runbook](documents/markdown/CROSS_MARKET_DATA_ACQUISITION_RUNBOOK_2026-10-29.md). Its commands write under `data/raw/cross_market/` and do not alter the frozen SPY artifacts documented above.

Before downloading anything, review:

- `configs/protocol.yaml`: symbols, sample dates, timing, splits, and paths.
- `configs/features.yaml`: trailing windows and feature-set membership.
- `configs/models.yaml`: model grids, compute limits, costs, selection, and uncertainty settings.
- `configs/events.yaml`: fixed descriptive event annotations used only in plots.

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

## Analysis and modeling commands

Run commands from the repository root with the virtual environment active. Every long loop shows a progress bar with elapsed time and ETA. Generated run IDs and paths are printed by the commands; copy the actual value into later commands. Text such as `SCREENING_RUN_ID` is a placeholder. Never type `...` as a path.

### 8. Development-only market EDA

```bash
python -m quantfin eda-market --through 2014-12-31
```

This keeps screening, confirmation, and final observations hidden during feature design. Inspect `artifacts/eda/market_.../eda_manifest.json`, its `plots/` directory, and its `tables/` directory. The outputs cover source coverage, price history, returns, volatility, annual and seasonal behavior, holidays, correlations, recent trends, event windows, and extreme observations.

### 9. Training-only feature EDA and statistical tests

```bash
python -m quantfin eda-features --feature-set F2 --split initial_train
python -m quantfin stat-tests --feature-set F2 --split initial_train
```

Inspect `artifacts/eda/features_.../` and `artifacts/statistics/.../`. Feature p-values include false-discovery-rate corrections. They are diagnostics and should not be used to search repeatedly against confirmation or final data.

### 10. Preview the compute load

```bash
python -m quantfin run-models --stage screening --profile quick --feature-set F2 --window expanding --plan-only
python -m quantfin run-models --stage screening --profile standard --feature-set F2 --window expanding --plan-only
python -m quantfin run-models --stage screening --profile deep --feature-set F2 --window 1260 --plan-only
```

`--plan-only` reads the feature dataset and prints model counts, monthly refits, and total fits. It does not create a run. Runtime depends on hardware and cannot be inferred reliably before the first measured fits; the live ETA adapts after they begin.

### 11. Optional short pipeline check

```bash
python -m quantfin run-models --stage screening --profile quick --feature-set F2 --window expanding
python -m quantfin plot-run --run-id QUICK_RUN_ID
```

This is useful for checking the command flow. Do not use its results as the main broad comparison.

### 12. Main model screening

```bash
python -m quantfin run-models --stage screening --profile standard --feature-set F2 --window expanding
```

If the process stops, use the same arguments plus `--resume`:

```bash
python -m quantfin run-models --stage screening --profile standard --feature-set F2 --window expanding --resume
```

The content-addressed run ID is identical when all inputs are identical. A valid monthly checkpoint is reused; an incomplete or hash-mismatched pair is rebuilt. To inspect completion from another terminal:

```bash
python -m quantfin run-status --run-id SCREENING_RUN_ID
```

Generate reports and apply the declared selection rule:

```bash
python -m quantfin plot-run --run-id SCREENING_RUN_ID --top-n 8
python -m quantfin select-models --run-id SCREENING_RUN_ID --top 2
```

The selection file is `artifacts/runs/SCREENING_RUN_ID/selection.json`.

### 13. Planned feature and window sensitivity

Run these before confirmation if the report will compare feature blocks and training-memory assumptions:

```bash
python -m quantfin run-models --stage screening --profile standard --feature-set F0 --window expanding
python -m quantfin run-models --stage screening --profile standard --feature-set F1 --window expanding
python -m quantfin run-models --stage screening --profile standard --feature-set F2 --window 1260
```

Plot each explicit run ID. Choose F0, F1, or F2 and expanding or 1260 observations from screening evidence, then keep that choice fixed for confirmation and final testing. F0 contains price-history features, F1 adds technical, intraday, volume, interaction, and calendar features, and F2 adds cross-asset context.

The optional high-capacity experiment uses the deep profile. It includes random Fourier models from 16 to 4096 basis features and is the intended analysis of parameter count relative to observations:

```bash
python -m quantfin run-models --stage screening --profile deep --feature-set F2 --window 1260
python -m quantfin plot-run --run-id DEEP_RUN_ID --top-n 12
```

### 14. Confirmation

The following example assumes F2 and expanding training were selected. Use the exact feature set and window chosen in the preceding step.

```bash
python -m quantfin run-models --stage confirmation --profile standard --feature-set F2 --window expanding --selection artifacts/runs/SCREENING_RUN_ID/selection.json
python -m quantfin plot-run --run-id CONFIRMATION_RUN_ID --top-n 4
python -m quantfin select-models --run-id CONFIRMATION_RUN_ID --top 1
```

Confirmation evaluates only the screened configurations plus the historical-mean and autoregressive baselines. The second selection file is `artifacts/runs/CONFIRMATION_RUN_ID/selection.json`.

### 15. Freeze and run the final holdout once

```bash
python -m quantfin freeze --feature-set F2 --window expanding --selection artifacts/runs/CONFIRMATION_RUN_ID/selection.json
```

Copy the printed freeze path, then run:

```bash
python -m quantfin run-models --stage final_test --profile standard --feature-set F2 --window expanding --selection artifacts/runs/CONFIRMATION_RUN_ID/selection.json --freeze artifacts/freezes/FREEZE_ID.json
python -m quantfin plot-run --run-id FINAL_RUN_ID --top-n 3
```

The final command refuses to run if the selection, feature manifest, protocol, model config, feature set, or window differs from the freeze. After this evaluation, any change defines a new analysis whose 2022–2025 period is no longer untouched.

### 16. Full-period descriptive EDA after freezing

```bash
python -m quantfin eda-market --through 2025-12-31
```

This produces the full event timeline and recent-period plots for the written report without feeding those observations back into model design.

## Run outputs

Each model run is stored under `artifacts/runs/models_STAGE_HASH/` and contains:

- `run_manifest.json`: status, hashes, environment, git revision, workload, and outputs;
- `configurations.json`: exact estimator settings;
- `checkpoints/`: verified monthly prediction checkpoints and feature diagnostics;
- `predictions.parquet` and `strategy_ledgers.parquet`;
- `config_metrics.csv`: forecast, portfolio, complexity, and timing metrics;
- `selection.json` after explicit selection;
- `plots/`, `evaluation_report.json`, `annual_returns.csv`, `cost_sensitivity.csv`, and, when available, `feature_stability.csv` after plotting.

The plot report includes the leaderboard, cumulative wealth, drawdown, calendar-year returns, rolling Sharpe and exposure, parameter-to-observation behavior, train versus out-of-sample error, cost sensitivity, and feature stability. The evaluation report also contains a moving-block bootstrap interval.

## Compute recommendations

For the M1 MacBook Air with 16 GB RAM, keep `n_jobs: 2` and `numerical_threads_per_worker: 1` in `configs/models.yaml`. This avoids nested numerical and tree-library thread contention while preserving responsiveness. Close memory-heavy applications for the deep 4096-component experiment. The implementation fits one configuration/refit job at a time and immediately checkpoints it, so RAM usage does not scale with the total grid size.

Use `quick` to validate the workflow, `standard` for the assignment's main comparison, and `deep` only for the focused capacity experiment. More exhaustive blind grid search is statistically costly and unnecessary: the staged screening and confirmation periods provide chronological tuning while preserving the final holdout.

On a Windows laptop, use the same `python -m quantfin ...` commands in PowerShell or Command Prompt. Paths passed as argument values should be quoted if the repository is stored under a directory containing spaces.

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

## Design documents

The assignment interpretation and full work sequence are in [the agent action plan](documents/markdown/AGENT_ACTION_PLAN.md). Feature formulas, model rationale, validation rules, metrics, and interpretation guidance are in [the feature and model guide](documents/markdown/FEATURE_AND_MODEL_GUIDE.md).

