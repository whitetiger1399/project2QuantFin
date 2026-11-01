# Signed Cross-Market Forecasting of Nifty IT Stocks

This repository contains Team 16's reproducible DSA5205 Project 2 workflow. It predicts each fixed current Nifty IT constituent's same-session open-to-close return from information available at 08:55 IST, then takes a long, short, or flat position and closes it on the same NSE session. Returns are reported after modeled transaction costs.

The active study is defined by `configs/cross_market_ai_capability_research.yaml`; its January–September 2026 extension is defined by `configs/cross_market_ai_capability_2026_extension.yaml`. The target cohort is fixed to the ten companies in `data/external/reference/current_constituents/ind_niftyitlist.csv` as observed on 30 October 2026. This is a current-universe retrospective study, not historical Nifty IT membership reconstruction. The 2025 evaluation is a historical protocol replication and 2026 is a retrospective no-reselection extension, not a pristine holdout.

## Reproducibility modes

1. **Full Git LFS clone:** inspect the committed data, artifacts, figures, DOCX, and PDF.
2. **Code-only checkout:** recreate raw vendor snapshots using Sections 3–5, then execute the complete pipeline.
3. **Existing raw data, fresh models:** begin at Section 6 after confirming a passing raw-data audit.

New downloads normally produce new timestamps and hashes. Yahoo or upstream revisions can prevent byte-identical reproduction while still reproducing the method. Do not mix identifiers from older generic cross-market, AI-services, and canonical AI-capability runs.

## 1. Environment

Python 3.10–3.12 and Git LFS are required.

### macOS or Linux

```bash
git lfs install
git clone https://github.com/whitetiger1399/project2QuantFin.git
cd project2QuantFin
git lfs pull

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .

export PYTHONUNBUFFERED=1
export MPLCONFIGDIR="$PWD/artifacts/.matplotlib-cache"
mkdir -p "$MPLCONFIGDIR"
python -m quantfin --help
```

### Windows PowerShell

```powershell
git lfs install
git clone https://github.com/whitetiger1399/project2QuantFin.git
Set-Location project2QuantFin
git lfs pull

py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .

$env:PYTHONUNBUFFERED = "1"
$env:MPLCONFIGDIR = "$PWD\artifacts\.matplotlib-cache"
New-Item -ItemType Directory -Force $env:MPLCONFIGDIR | Out-Null
python -m quantfin --help
```

The commands below use POSIX environment syntax. On Windows, use Git Bash after activating `.venv`, or translate `export NAME=value` to `$env:NAME = "value"` and `\` line continuations to PowerShell backticks.

Run the inexpensive checks first:

```bash
python -m unittest discover -s tests -v
python -m compileall -q src scripts reports
```

## 2. Data inventory and code-only recovery

Raw vendor downloads under `data/raw/` are intentionally not committed because they can be large and may have redistribution restrictions. Small source and manual files under `data/external/` are committed through Git LFS. Restore them with:

```bash
git lfs pull
git lfs fsck
```

| Data block | Source and local file | Acquisition | Role and limitation |
|---|---|---|---|
| Current Nifty IT cohort | [NSE Indices Nifty IT page](https://niftyindices.com/indices/equity/sectoral-indices/nifty-it); committed `ind_niftyitlist.csv` | Git LFS | Fixed targets only; not historical membership. |
| Indian, U.S., ADR, ETF, index, FX and global OHLCV | Yahoo Finance through [`yfinance`](https://ranaroussi.github.io/yfinance/) | `fetch_cross_market_markets.py` | Public adjusted data; retrieval revisions are possible. |
| Rates, yields, spreads, dollar, VIX and India macro | [FRED/ALFRED](https://fred.stlouisfed.org/docs/api/fred/) | `fetch_point_in_time_context.py` | Initial-release observations where available; fallbacks are marked current-vintage. |
| Historical S&P 500 membership | Committed source from [fja05680/sp500](https://github.com/fja05680/sp500) | `prepare_provisional_memberships.py` | Public provisional reconstruction, not CRSP/Compustat. |
| Nifty 50/500 histories | Committed sources from [NiftyHistory](https://niftyhistory.in/) | `prepare_provisional_memberships.py` | Effective dates; announcement timestamps unavailable. |
| Frontier AI releases | Committed `model_publishing.txt` and curated whitelist | `build_frontier_ai_release_calendar.py` | Official provider announcements determine accepted dates. The declared general-purpose release universe covers 14 March 2023–30 September 2026; specialized media/embedding models and product-only updates are excluded. |
| Disclosed model scale | Committed `frontier_ai_disclosed_parameters.yaml` | `build_ai_capability_panel.py` | Missing proprietary sizes remain missing; scale is not complete capability. |
| AI benchmark snapshot | [Epoch AI](https://epoch.ai/benchmarks/use-this-data), committed `benchmark_data.zip` | `ingest_epoch_benchmark_snapshot.py` | Ex-post evidence only; never a backfilled tradable feature. |
| RBI, holidays, events, rainfall | CSVs in `data/external/manual/cross_market/` | Official exports supplied manually | Optional context; blank templates add no observations. |

For the optional manual files, use the [RBI data portal](https://data.rbi.org.in/), [NSE holiday calendar](https://www.nseindia.com/resources/exchange-communication-holidays), [NYSE calendar](https://www.nyse.com/markets/hours-calendars), official FOMC/RBI announcement calendars, and [IMD rainfall service](https://mausam.imd.gov.in/imd_latest/contents/index_rainfall_state_new.php). Preserve each row's publication/effective timestamp and source URL. Do not substitute an undated secondary compilation.

If a code-only archive omitted the LFS objects, download the provisional membership sources and place them at these exact paths:

```text
data/external/reference/current_constituents/S&P 500 Historical Components & Changes (Updated).csv
data/external/reference/current_constituents/nifty50_2001-01-01_to_2026-12-31.csv
data/external/reference/current_constituents/nifty500_2001-01-01_to_2026-12-31.csv
```

Download the Epoch archive to `data/external/reference/epoch_ai/benchmark_data.zip`. The ingestion script requires SHA-256 `28a006632f325e82c61ed28603056784ae185b5b596da6e019edd84fe02ddb43`.

The small cohort, event whitelist, disclosed-scale catalog, company-evidence file, and event-timing catalog are included in the repository. Do not silently replace them. Never commit API keys, cookies, or credentials. Review current upstream terms before redistributing source files.

## 3. Prepare membership files

Inspect the conversion first:

```bash
python scripts/prepare_provisional_memberships.py
```

For a code-only checkout where the three generated membership CSVs are absent, execute:

```bash
python scripts/prepare_provisional_memberships.py --execute
```

Skip that execution command when populated outputs already exist: it deliberately refuses to replace them. Use the committed reviewed outputs; pass `--overwrite` only after intentionally reviewing a changed source.

## 4. Acquire raw data

Download Yahoo groups sequentially to reduce throttling:

```bash
python scripts/fetch_cross_market_markets.py --group india_core --execute
python scripts/fetch_cross_market_markets.py --group us_limited_tech --execute
python scripts/fetch_cross_market_markets.py --group us_it_services --execute
python scripts/fetch_cross_market_markets.py --group us_it_enabled_payments --execute
python scripts/fetch_cross_market_markets.py --group us_enterprise_software --execute
python scripts/fetch_cross_market_markets.py --group us_context --execute
python scripts/fetch_cross_market_markets.py --group indian_it_adrs --execute
python scripts/fetch_cross_market_markets.py --group global_context --execute

python scripts/fetch_cross_market_markets.py \
  --group nifty50_point_in_time \
  --membership-file data/external/manual/cross_market/nifty50_membership.csv \
  --execute

python scripts/fetch_cross_market_markets.py \
  --group sp500_point_in_time \
  --membership-file data/external/manual/cross_market/sp500_membership.csv \
  --execute
```

The Nifty 500 universe is optional and is not required by the canonical model:

```bash
python scripts/fetch_cross_market_markets.py \
  --group nifty500_point_in_time \
  --membership-file data/external/manual/cross_market/nifty500_membership.csv \
  --execute
```

Resume an interrupted required download with the exact snapshot ID printed by it:

```bash
python scripts/fetch_cross_market_markets.py --group GROUP_NAME --resume-snapshot EXACT_SNAPSHOT_ID --execute
```

Unavailable former Yahoo tickers remain recorded as a coverage limitation; do not delete them from membership history simply to remove failures.

Create a free FRED key at <https://fredaccount.stlouisfed.org/apikeys>, enter it without saving it in history, and run:

```bash
read -s "FRED_API_KEY?FRED API key: "
export FRED_API_KEY
echo

python scripts/fetch_point_in_time_context.py \
  --config configs/cross_market_data_2026-10-29.yaml \
  --start 2004-01-01 \
  --end 2026-10-29 \
  --output-root data/raw/cross_market/fred_alfred \
  --execute

unset FRED_API_KEY
```

In PowerShell, set it for the current process with `$env:FRED_API_KEY = Read-Host "FRED API key" -MaskInput`, run the same Python command on one line, and then use `Remove-Item Env:FRED_API_KEY`.

The downloader uses verified TLS and partitions ALFRED real-time dates to stay below API limits. Do not disable certificate verification.

Build the curated AI calendar and ingest the verified Epoch archive:

```bash
python scripts/build_frontier_ai_release_calendar.py
python scripts/build_frontier_ai_release_calendar.py --execute
python scripts/ingest_epoch_benchmark_snapshot.py --execute
```

The first command is a no-write plan. The second materializes an immutable,
hash-tracked calendar snapshot. Release dates are maintained in
`configs/frontier_ai_release_whitelist.yaml` with one official-provider URL per
event. Date-only announcements are conservatively mapped to the first NSE
08:55 IST decision cutoff strictly after 23:59:59 UTC on the published date;
this prevents an announcement of unknown intraday time from becoming available
too early.

## 5. Audit raw inputs

```bash
python scripts/audit_cross_market_raw.py \
  --required-group india_core \
  --required-group us_limited_tech \
  --required-group us_it_services \
  --required-group us_it_enabled_payments \
  --required-group us_enterprise_software \
  --required-group us_context \
  --required-group indian_it_adrs \
  --required-group global_context \
  --required-group nifty50_point_in_time \
  --required-group sp500_point_in_time
```

`fail` is blocking. `pass_with_warnings` is acceptable only after reviewing the listed quarantine rules. Inspect the latest result:

```bash
export RAW_AUDIT=$(find artifacts/data_audits/cross_market -name 'audit_*.json' -type f -print0 | xargs -0 ls -t | head -1)
python -m json.tool "$RAW_AUDIT"
```

## 6. Build historical and 2026 panels

```bash
python scripts/build_cross_market_panel.py \
  --config configs/cross_market_ai_services_research.yaml \
  --plan-only
python scripts/build_cross_market_panel.py \
  --config configs/cross_market_ai_services_research.yaml

export SOURCE_DATASET_ID=$(python -c "from pathlib import Path; r=Path('data/processed/cross_market_ai_services'); p=max((x for x in r.glob('ai_services_panel_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")

python scripts/build_ai_capability_panel.py --source-dataset-id "$SOURCE_DATASET_ID" --plan-only
python scripts/build_ai_capability_panel.py --source-dataset-id "$SOURCE_DATASET_ID"

export DATASET_ID=$(python -c "from pathlib import Path; r=Path('data/processed/cross_market_ai_capability'); p=max((x for x in r.glob('ai_capability_panel_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")

python scripts/build_cross_market_panel.py \
  --config configs/cross_market_ai_services_2026_extension.yaml

export SOURCE_2026_DATASET_ID=$(python -c "from pathlib import Path; r=Path('data/processed/cross_market_ai_services_2026'); p=max((x for x in r.glob('ai_services_2026_panel_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")

python scripts/build_ai_capability_panel.py \
  --config configs/cross_market_ai_capability_2026_extension.yaml \
  --source-dataset-id "$SOURCE_2026_DATASET_ID"

export DATASET_2026_ID=$(python -c "from pathlib import Path; r=Path('data/processed/cross_market_ai_capability_2026'); p=max((x for x in r.glob('ai_capability_2026_panel_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")

echo "DATASET_ID=$DATASET_ID"
echo "DATASET_2026_ID=$DATASET_2026_ID"
```

## 7. EDA and capability studies

```bash
python scripts/run_cross_market_analysis.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --dataset-id "$DATASET_ID"
export EDA_RUN_ID=$(python -c "from pathlib import Path; r=Path('artifacts/cross_market_ai_capability/analysis'); p=max((x for x in r.glob('analysis_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")

python scripts/analyze_ai_capability_effects.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --dataset-id "$DATASET_ID"
export CAPABILITY_ANALYSIS_ID=$(python -c "from pathlib import Path; r=Path('artifacts/cross_market_ai_capability/analysis'); p=max((x for x in r.glob('ai_capability_analysis_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")

export EPOCH_SNAPSHOT_ID=$(python -c "from pathlib import Path; r=Path('data/raw/cross_market/epoch_benchmarks'); p=max((x for x in r.glob('epoch_benchmarks_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")
python scripts/analyze_epoch_capability_market_effects.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --dataset-id "$DATASET_ID" \
  --epoch-snapshot-id "$EPOCH_SNAPSHOT_ID"
export EPOCH_ANALYSIS_ID=$(python -c "from pathlib import Path; r=Path('artifacts/cross_market_ai_capability/analysis'); p=max((x for x in r.glob('epoch_capability_analysis_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")
```

## 8. Screen, confirm, freeze, and evaluate

The `submission_rerun` profile compares baselines, shrinkage, PCA, Extra Trees, and histogram boosting across the information ladder. It excludes RFF Ridge because the earlier RFF configurations never crossed the trading hurdle and therefore had undefined trading Sharpe. Quarterly refits retain daily out-of-sample predictions. Three workers are the tested laptop default.

```bash
python scripts/run_cross_market_experiments.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --dataset-id "$DATASET_ID" \
  --stage screening \
  --profile submission_rerun \
  --training-scheme rolling \
  --parallel-workers 3

export SCREENING_RUN_ID=$(python -c "from pathlib import Path; r=Path('artifacts/cross_market_ai_capability/runs'); p=max((x for x in r.glob('cm_ai_capability_screening_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")
python scripts/cross_market_run_status.py --config configs/cross_market_ai_capability_research.yaml --run-id "$SCREENING_RUN_ID"
```

Resume an interrupted screening run without changing its inputs or settings:

```bash
python scripts/run_cross_market_experiments.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --dataset-id "$DATASET_ID" \
  --stage screening \
  --profile submission_rerun \
  --training-scheme rolling \
  --parallel-workers 3 \
  --resume-run-id "$SCREENING_RUN_ID"
```

Continue sequentially:

```bash
python scripts/run_cross_market_experiments.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --dataset-id "$DATASET_ID" \
  --stage confirmation \
  --profile submission_rerun \
  --training-scheme rolling \
  --parallel-workers 3 \
  --screening-run-id "$SCREENING_RUN_ID"
export CONFIRMATION_RUN_ID=$(python -c "from pathlib import Path; r=Path('artifacts/cross_market_ai_capability/runs'); p=max((x for x in r.glob('cm_ai_capability_confirmation_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")

python scripts/freeze_cross_market_model.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --confirmation-run-id "$CONFIRMATION_RUN_ID"
export FREEZE_ID=$(python -c "from pathlib import Path; r=Path('artifacts/cross_market_ai_capability/freezes'); p=max(r.glob('cm_ai_capability_freeze_*.json'), key=lambda x:x.stat().st_mtime_ns); print(p.stem)")

python scripts/run_cross_market_experiments.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --dataset-id "$DATASET_ID" \
  --stage final_test \
  --profile submission_rerun \
  --training-scheme rolling \
  --parallel-workers 3 \
  --freeze-id "$FREEZE_ID"
export FINAL_RUN_ID=$(python -c "from pathlib import Path; r=Path('artifacts/cross_market_ai_capability/runs'); p=max((x for x in r.glob('cm_ai_capability_final_test_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")

python scripts/run_frozen_2026_extension.py \
  --dataset-id "$DATASET_2026_ID" \
  --freeze-id "$FREEZE_ID" \
  --start 2026-01-01 \
  --end 2026-09-30
export FORWARD_RUN_ID=$(python -c "from pathlib import Path; r=Path('artifacts/cross_market_ai_capability_2026/runs'); p=max((x for x in r.glob('cm_ai_capability_2026_forward_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")
```

The 2026 command reuses the frozen family, feature set, hyperparameters, preprocessing, and policy and fits once using pre-2026 observations. It does not tune on 2026.

## 9. Diagnostics and verification

```bash
python scripts/analyze_ai_capability_model_run.py --config configs/cross_market_ai_capability_research.yaml --run-id "$FINAL_RUN_ID"
export MODEL_EVIDENCE_ID=$(python -c "from pathlib import Path; r=Path('artifacts/cross_market_ai_capability/analysis'); p=max((x for x in r.glob('model_evidence_final_test_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")

python scripts/summarize_information_ladder.py --config configs/cross_market_ai_capability_research.yaml --run-id "$FINAL_RUN_ID"
export LADDER_ANALYSIS_ID=$(python -c "from pathlib import Path; r=Path('artifacts/cross_market_ai_capability/analysis'); p=max((x for x in r.glob('information_ladder_final_test_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")

python scripts/compare_ai_services_strategies.py --config configs/cross_market_ai_capability_research.yaml --run-id "$FINAL_RUN_ID"
export STRATEGY_ANALYSIS_ID=$(python -c "from pathlib import Path; r=Path('artifacts/cross_market_ai_capability/analysis'); p=max((x for x in r.glob('ai_strategy_comparison_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")

python scripts/verify_ai_capability_pipeline.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --dataset-id "$DATASET_ID" \
  --epoch-snapshot-id "$EPOCH_SNAPSHOT_ID" \
  --eda-run-id "$EDA_RUN_ID" \
  --capability-analysis-id "$CAPABILITY_ANALYSIS_ID" \
  --epoch-analysis-id "$EPOCH_ANALYSIS_ID" \
  --screening-run-id "$SCREENING_RUN_ID" \
  --confirmation-run-id "$CONFIRMATION_RUN_ID" \
  --freeze-id "$FREEZE_ID" \
  --final-run-id "$FINAL_RUN_ID"

python scripts/audit_ai_capability_contract.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --dataset-id "$DATASET_ID" \
  --run-id "$SCREENING_RUN_ID" \
  --run-id "$CONFIRMATION_RUN_ID" \
  --run-id "$FINAL_RUN_ID"

python scripts/verify_frozen_2026_extension.py --run-id "$FORWARD_RUN_ID"
```

Do not publish results unless all verifiers pass.

## 10. Exploratory hypotheses

This six-hypothesis analysis uses already inspected history. It does not select or change the frozen model.

```bash
export EPOCH_EVENT_FILE="artifacts/cross_market_ai_capability/analysis/$EPOCH_ANALYSIS_ID/epoch_event_capability_returns.csv"
python scripts/analyze_research_hypotheses.py \
  --dataset "data/processed/cross_market_ai_capability/$DATASET_ID" \
  --dataset "data/processed/cross_market_ai_capability_2026/$DATASET_2026_ID" \
  --run "artifacts/cross_market_ai_capability/runs/$SCREENING_RUN_ID" \
  --run "artifacts/cross_market_ai_capability/runs/$CONFIRMATION_RUN_ID" \
  --epoch-events "$EPOCH_EVENT_FILE" \
  --execute

export HYPOTHESIS_ANALYSIS_ID=$(python -c "from pathlib import Path; r=Path('artifacts/research_hypotheses'); p=max((x for x in r.glob('hypotheses_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")
```

Non-significance is inconclusive, not proof of no effect. Event associations and current-vintage benchmark scores are not causal evidence.

## 11. Figures and report

The submitted publication pack and report are evidence-bound to the verified canonical chain. For an exact rebuild of the committed report, leave `REPORT_*` variables unset and retain the committed canonical artifacts. For a fresh chain, export the verified core IDs:

```bash
export SELECTED_CONFIG_ID=$(python -c "import json,os; print(json.load(open('artifacts/cross_market_ai_capability/runs/' + os.environ['FINAL_RUN_ID'] + '/manifest.json'))['selected_config_id'])")
export REPORT_DATASET_ID="$DATASET_ID"
export REPORT_EDA_RUN_ID="$EDA_RUN_ID"
export REPORT_CAPABILITY_ANALYSIS_ID="$CAPABILITY_ANALYSIS_ID"
export REPORT_EPOCH_ANALYSIS_ID="$EPOCH_ANALYSIS_ID"
export REPORT_SCREENING_RUN_ID="$SCREENING_RUN_ID"
export REPORT_CONFIRMATION_RUN_ID="$CONFIRMATION_RUN_ID"
export REPORT_FREEZE_ID="$FREEZE_ID"
export REPORT_FINAL_RUN_ID="$FINAL_RUN_ID"
export REPORT_FORWARD_RUN_ID="$FORWARD_RUN_ID"
export REPORT_SELECTED_CONFIG_ID="$SELECTED_CONFIG_ID"
export REPORT_LADDER_ANALYSIS_ID="$LADDER_ANALYSIS_ID"
export REPORT_MODEL_EVIDENCE_ID="$MODEL_EVIDENCE_ID"
export REPORT_STRATEGY_ANALYSIS_ID="$STRATEGY_ANALYSIS_ID"

python scripts/build_publication_figure_pack.py
python reports/build_report_ai_capability.py
```

A fresh submission also requires reviewing and updating the separately pinned raw snapshots, event analysis, hypothesis analysis, and publication-figure references. The builder intentionally fails on absent or hash-mismatched evidence.

Export PDF with Microsoft Word or LibreOffice and update fields. A LibreOffice CLI example is:

```bash
mkdir -p reports/_render_final
soffice --headless --convert-to pdf --outdir reports/_render_final reports/Project2_Team16_Report.docx
python scripts/cache_report_contents.py --pdf reports/_render_final/Project2_Team16_Report.pdf
soffice --headless --convert-to pdf --outdir reports/_render_final reports/Project2_Team16_Report.docx
cp reports/_render_final/Project2_Team16_Report.pdf reports/Project2_Team16_Report.pdf
```

On macOS, use `/Applications/LibreOffice.app/Contents/MacOS/soffice` if `soffice` is not on `PATH`. On Windows, use the full path to `soffice.exe`. Inspect every rendered page before submission.

## Outputs

| Stage | Output root |
|---|---|
| Raw snapshots | `data/raw/cross_market/` |
| Raw audit | `artifacts/data_audits/cross_market/` |
| Processed panels | `data/processed/cross_market_ai_services*` and `cross_market_ai_capability*` |
| EDA and analyses | `artifacts/cross_market_ai_capability/analysis/` |
| Runs and checkpoints | `artifacts/cross_market_ai_capability/runs/` |
| Frozen contract | `artifacts/cross_market_ai_capability/freezes/` |
| 2026 extension | `artifacts/cross_market_ai_capability_2026/runs/` |
| Hypotheses | `artifacts/research_hypotheses/` |
| Figures and submission | `reports/` |

Every completed dataset, analysis, and run has a manifest and hashes. An interrupted model run can be resumed only with its exact run ID and unchanged inputs, configuration, and code.

## Common failures

- **No raw snapshot:** rerun that fetch command with `--execute`; a failed directory without `manifest.json` is incomplete.
- **FRED vintage-limit HTTP 400:** use the current script's default five-year chunks.
- **FRED series absent from ALFRED:** retain the recorded current-vintage fallback and conservative lag.
- **Yahoo 404 for a former ticker:** keep the failure in the manifest unless an independently verified symbol mapping exists.
- **OHLC audit warnings:** follow the emitted cleaning restrictions; the panel builder quarantines declared anomalies.
- **Interrupted model run:** resume its exact `--resume-run-id`; changed inputs require a new run.
- **Apparently idle model run:** inspect it with `cross_market_run_status.py` from another terminal; never start a second writer for the same run.
- **Report evidence missing:** restore LFS artifacts or export the matching verified `REPORT_*` identifiers.
- **Stale contents page:** render once, run `cache_report_contents.py`, export again, and inspect every page.

## Repository structure

- `src/quantfin/`: timing, cleaning, features, models, evaluation, and tracking.
- `scripts/`: acquisition, audit, panel, EDA, modeling, verification, and figures.
- `configs/`: data contracts, feature ladders, model grids, costs, and evidence catalogs.
- `data/external/`: committed source/reference files and manual templates.
- `data/raw/`: local immutable vendor snapshots excluded from Git.
- `data/processed/`: immutable content-hashed feature panels.
- `artifacts/`: analyses, checkpoints, runs, freezes, and audits.
- `documents/markdown/`: assignment, methods, dated reviews, and historical runbooks.
- `reports/`: publication figures, report builder, DOCX, and PDF.
- `tests/`: deterministic timing, accounting, and contract tests.

Before submission, verify the run IDs, alphabetical author roster, AI-use declaration, NUS academic-integrity references, figure readability, and required filenames. The video should explain the information clock, leakage controls, long/short/flat policy, transaction costs, statistically inconclusive results, and limitations.
