# Project 2 Research v2 — Sequential Implementation Runbook

**Purpose:** execute A00–A04 from `REPORT_GAP_ANALYSIS_AND_RESEARCH_ACTION_PLAN.md` without changing or retraining the v1 experiment.

## Rules for this checkpoint

- Run commands from the repository root.
- Stop if a command raises an exception; preserve its output before continuing.
- The v1 run directories are read-only evidence. New outputs go under `artifacts/research_v2/`.
- The 2022–2025 period is already inspected. v2 scripts must describe it as retrospective.
- No external data are required for A00–A04.

## 0. Activate the project environment

```bash
cd /Users/whitetiger/Desktop/WhiteTiger/17_projects/24_Project2_QuantFin/project2QuantFin
source .venv/bin/activate
python --version
git status --short
```

## 1. Preview and create the immutable v1 evidence manifest (A00)

The first command only shows the intended scope. The second hashes and copies canonical data, runs, configurations, verification output, and reports into an immutable payload. Checkpoints are excluded because their predictions are already represented in the canonical run outputs and manifests. Re-running the same command resumes missing copies and verifies copies already present.

```bash
python scripts/archive_v1.py --plan-only
python scripts/archive_v1.py
```

Optional full checkpoint inventory:

```bash
python scripts/archive_v1.py --include-checkpoints
```

Expected output location:

```text
artifacts/research_v2/baseline_archives/v1_<content-hash>/manifest.json
```

## 2. Verify exact report facts and rebuild the DOCX source (A01)

The verifier now resolves the selected screening, confirmation, and final configurations by immutable `config_id`. It also writes `reports/report_facts.json`. The report builder uses that facts object and no longer assumes that the first random-forest row is the selected model.

```bash
python scripts/verify_outputs.py
python reports/build_report_ieee.py
```

The DOCX command does not convert the file to PDF. If LibreOffice is installed, use:

```bash
mkdir -p reports/rendered
soffice --headless --convert-to pdf --outdir reports/rendered reports/Project2_Team16_Report.docx
```

Review these corrected facts in the rebuilt report:

- warm-up is 2005 and initial model training is 2006–2014;
- the selected screening forest is `random_forest_6aa9f5d449`;
- the AR baseline uses three lagged returns plus an intercept;
- predictor missingness is handled by training-fitted median imputation;
- the walk-forward loop is sequential, with estimator-level jobs where supported;
- annualized volatility is included in the final results table.

## 3. Preview and run the independent accounting audit (A02)

```bash
python scripts/audit_v1_accounting.py --plan-only
python scripts/audit_v1_accounting.py \
  --run-id models_final_test_53e047b58e92e27b \
  --freeze-id freeze_f98a78b584d0ca42
```

Expected output location:

```text
artifacts/research_v2/accounting_audits/accounting_<content-hash>/
```

Inspect the findings:

```bash
find artifacts/research_v2/accounting_audits -name audit_report.json -print
find artifacts/research_v2/accounting_audits -name annual_returns_by_pnl_session.csv -print
```

The corrected ledger uses `label_end_session` as `pnl_session`, includes initial wealth in the drawdown peak, and preserves entry and final liquidation costs. Any difference from v1 is reported rather than silently replacing legacy files.

## 4. Validate and freeze the v2 protocol (A03)

The dry run validates the protocol and reports the deterministic freeze ID. The second command writes it.

```bash
python scripts/freeze_research_v2.py --config configs/research_v2.yaml --dry-run
python scripts/freeze_research_v2.py --config configs/research_v2.yaml
```

Expected output location:

```text
artifacts/research_v2/freezes/research_v2_<content-hash>.json
```

Do not enable the optional 2026 period or retrieve those observations before this freeze exists.

## 5. Preview the bounded compute profile (A04)

This command does not fit a model:

```bash
python scripts/profile_compute.py \
  --config configs/research_v2.yaml \
  --sample-sizes 1000 2500 4000 \
  --repeats 1 \
  --estimator-jobs 1 \
  --max-minutes 20
```

## 6. Run the bounded compute profile when ready

These are profiling runs, not the full search. Run the one-job profile first. If memory and temperature remain acceptable, compare it with the two-job profile.

```bash
python scripts/profile_compute.py \
  --config configs/research_v2.yaml \
  --execute \
  --sample-sizes 1000 2500 4000 \
  --repeats 1 \
  --estimator-jobs 1 \
  --max-minutes 20
```

```bash
python scripts/profile_compute.py \
  --config configs/research_v2.yaml \
  --execute \
  --sample-sizes 1000 2500 4000 \
  --repeats 1 \
  --estimator-jobs 2 \
  --max-minutes 20
```

Expected output location:

```text
artifacts/research_v2/compute_profiles/compute_<content-hash>/profile.json
```

The profile has a live progress bar, a hard time budget checked between fits, environment metadata, per-family fit time, and available peak-memory measurements.

## Data required for the next checkpoint (A05–A09)

No data need to be downloaded yet. After A03 succeeds, prepare:

1. A free FRED API key for `DGS3MO`, `DGS2`, `DGS10`, and `DFF` observations and vintage-aware metadata.
2. Permission for the data adapter to retrieve official FRED/ALFRED, CBOE VIX, Federal Reserve/FOMC, BLS release-calendar, NYSE holiday, and crisis-marker source files.
3. Do not manually edit downloaded files. The next scripts will save immutable raw responses, request metadata, access timestamps, hashes, licensing notes, and availability timestamps.

Do not download January–September 2026 market data until the v2 freeze is written and its path has been recorded.

