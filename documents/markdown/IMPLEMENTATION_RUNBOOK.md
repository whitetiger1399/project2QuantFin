# Project 2 — Canonical Research Runbook

This repository uses one research setup and one selected model. The canonical model is `random_forest_6aa9f5d449`: 300 trees, maximum depth 3, minimum leaf size 50, maximum feature fraction 0.5, monthly refits, an expanding training window, seed 17, a 0.001 forecast hurdle and 5 bp one-way costs.

The completed screening and confirmation outputs document how this model was selected. Historical mean, autoregression and buy-and-hold SPY are benchmarks, not alternative model setups.

## 1. Activate the environment

```bash
cd /Users/whitetiger/Desktop/WhiteTiger/17_projects/24_Project2_QuantFin/project2QuantFin
source .venv/bin/activate
python --version
git status --short
```

## 2. Verify the canonical evidence

```bash
python scripts/verify_outputs.py
```

Expected result: `status: pass` with the canonical final run `models_final_test_53e047b58e92e27b`.

## 3. Audit accounting

The plan command does not write files:

```bash
python scripts/audit_accounting.py --plan-only
```

The audit command writes a content-addressed result under `artifacts/research/accounting_audits/`:

```bash
python scripts/audit_accounting.py \
  --run-id models_final_test_53e047b58e92e27b \
  --freeze-id freeze_f98a78b584d0ca42
```

## 4. Freeze the improved research protocol

The canonical configuration is `configs/research.yaml`. There is no separate v1 or v2 configuration.

```bash
python scripts/freeze_research.py --config configs/research.yaml --dry-run
python scripts/freeze_research.py --config configs/research.yaml
```

The freeze is written under `artifacts/research/freezes/`.

## 5. Profile compute before a long run

Plan only:

```bash
python scripts/profile_compute.py \
  --config configs/research.yaml \
  --sample-sizes 1000 2500 4000 \
  --repeats 1 \
  --estimator-jobs 1 \
  --max-minutes 20
```

Execute the bounded profile only when ready:

```bash
python scripts/profile_compute.py \
  --config configs/research.yaml \
  --execute \
  --sample-sizes 1000 2500 4000 \
  --repeats 1 \
  --estimator-jobs 1 \
  --max-minutes 20
```

## 6. Rebuild the report

```bash
python scripts/verify_outputs.py
python reports/build_report_ieee.py
```

The report contains one detailed model specification. Candidate searches appear only as selection evidence, and benchmark series appear only for fair evaluation.

## External data checkpoint

No additional data are needed for the commands above. Before adding FRED/ALFRED rates, CBOE VIX, FOMC, BLS, NYSE holiday or crisis-event data, write the canonical protocol freeze and preserve source timestamps and hashes.
