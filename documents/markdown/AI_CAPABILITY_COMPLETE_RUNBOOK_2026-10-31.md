# AI Capability Experiment: Complete Sequential Runbook

## Scope and leakage rule

This is a new, separately hashed experiment. It preserves the completed AI-services experiment and does not overwrite its dataset, checkpoints, runs, freezes, or analyses. The prediction target is each fixed-cohort Nifty IT constituent's same-session open-to-close return. Every position is opened after the 08:55 IST decision cutoff and closed by the same session's close.

Officially disclosed release metadata and model scale may enter the predictor panel only after their first eligible NSE cutoff. Current-vintage Epoch Capabilities Index and benchmark scores are **ex-post explanatory variables only**. They must not be backfilled into historical forecasts because the model release date does not establish when Epoch's independent evaluation was public. The empty release-time benchmark catalog is a deliberate gate: only scores with a verified public timestamp, exact benchmark version, protocol, scale, and primary source may later enter predictive features.

The 2025 evaluation is a protocol-final historical replication. Since 2025 results have already been inspected elsewhere in the project, it must not be described as a pristine untouched holdout.

## Evidence produced

The pipeline produces:

1. An immutable, hash-verified Epoch benchmark snapshot and schema inventory.
2. A separately hashed AI-capability panel with leakage-safe release/parameter features.
3. Dataset EDA: coverage, missingness, distributions, stationarity, autocorrelation, ARCH effects, normality, seasonality, trend shifts, lead-lag structure, feature-target correlations with FDR control, and cross-asset correlations.
4. Parameter-scale and Epoch benchmark event studies with mapping coverage, rank correlations, robust time-controlled regressions, and explicit non-causal guardrails.
5. A predeclared information ladder from own history through Nifty IT peers, U.S. IT services, Nifty 50, S&P 500 aggregates/constituents, AI capability, and full context.
6. Model-family screening across statistical baselines, shrinkage, dimension reduction, tree ensembles, boosting, and random-feature nonlinear models.
7. Complexity diagnostics using trainable-parameter proxies, parameter/observation ratios, runtime, and out-of-sample performance.
8. Rolling walk-forward screening and confirmation, followed by a single frozen model and a final 2025 evaluation.
9. Daily predictions, expected returns, long/short holdings, exposures, turnover, costs, gross/net returns, benchmark returns, Sharpe/Sortino/Calmar, drawdown, OOS R-squared, IC, directional accuracy, calibration, HAC tests, block-bootstrap Sharpe intervals, alpha, annual stability, and cost sensitivity.
10. Hash and lineage verification across the dataset, analyses, stage runs, freeze, and final result.

## Compute policy

Use the `balanced` profile with quarterly refits and two concurrent shared-memory workers. Daily forecasts remain fully out of sample within each refit block. The balanced design retains all eight information-ladder rungs, three forecast baselines, multiple shrinkage/PCA/boosting settings, a 250-tree ensemble, and nonlinear complexity ratios of 0.5, 2, 5, and 10 with penalty sensitivity. It removes only pathological unlimited trees and caps random features at 2,048. Exactly one model is frozen before the final stage.

## Sequential commands

Run these commands only after the currently running AI-services job has completed. Keep the same terminal session so exported identifiers remain available.

```bash
cd /Users/whitetiger/Desktop/WhiteTiger/17_projects/24_Project2_QuantFin/project2QuantFin
source .venv/bin/activate
export PYTHONUNBUFFERED=1
export MPLCONFIGDIR="$PWD/artifacts/.matplotlib-cache"
mkdir -p "$MPLCONFIGDIR"
```

### 1. Ingest and verify Epoch data

```bash
python scripts/ingest_epoch_benchmark_snapshot.py --execute

export EPOCH_SNAPSHOT_ID=$(python -c "from pathlib import Path; r=Path('data/raw/cross_market/epoch_benchmarks'); p=max((x for x in r.glob('epoch_benchmarks_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")
echo "EPOCH_SNAPSHOT_ID=$EPOCH_SNAPSHOT_ID"
```

### 2. Build the leakage-safe capability dataset

Use the already verified AI-services source panel:

```bash
export SOURCE_DATASET_ID=ai_services_panel_20261031T023944Z_fc3fbc83bdc45226

python scripts/build_ai_capability_panel.py \
  --source-dataset-id "$SOURCE_DATASET_ID" \
  --plan-only

python scripts/build_ai_capability_panel.py \
  --source-dataset-id "$SOURCE_DATASET_ID"

export DATASET_ID=$(python -c "from pathlib import Path; r=Path('data/processed/cross_market_ai_capability'); p=max((x for x in r.glob('ai_capability_panel_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")
echo "DATASET_ID=$DATASET_ID"
```

### 3. Run EDA and capability analyses

```bash
python scripts/run_cross_market_analysis.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --dataset-id "$DATASET_ID"

export EDA_RUN_ID=$(python -c "from pathlib import Path; r=Path('artifacts/cross_market_ai_capability/analysis'); p=max((x for x in r.glob('analysis_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")

python scripts/analyze_ai_capability_effects.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --dataset-id "$DATASET_ID"

export CAPABILITY_ANALYSIS_ID=$(python -c "from pathlib import Path; r=Path('artifacts/cross_market_ai_capability/analysis'); p=max((x for x in r.glob('ai_capability_analysis_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")

python scripts/analyze_epoch_capability_market_effects.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --dataset-id "$DATASET_ID" \
  --epoch-snapshot-id "$EPOCH_SNAPSHOT_ID"

export EPOCH_ANALYSIS_ID=$(python -c "from pathlib import Path; r=Path('artifacts/cross_market_ai_capability/analysis'); p=max((x for x in r.glob('epoch_capability_analysis_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")
```

### 4. Screening

```bash
python scripts/run_cross_market_experiments.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --dataset-id "$DATASET_ID" \
  --stage screening \
  --profile balanced \
  --training-scheme rolling \
  --parallel-workers 2

export SCREENING_RUN_ID=$(python -c "from pathlib import Path; r=Path('artifacts/cross_market_ai_capability/runs'); p=max((x for x in r.glob('cm_ai_capability_screening_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")
echo "SCREENING_RUN_ID=$SCREENING_RUN_ID"

python scripts/cross_market_run_status.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --run-id "$SCREENING_RUN_ID"

python scripts/analyze_ai_capability_model_run.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --run-id "$SCREENING_RUN_ID"
```

If interrupted, resume the exact same run:

```bash
python scripts/run_cross_market_experiments.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --dataset-id "$DATASET_ID" \
  --stage screening \
  --profile balanced \
  --training-scheme rolling \
  --parallel-workers 2 \
  --resume-run-id "$SCREENING_RUN_ID"
```

### 5. Confirmation

```bash
python scripts/run_cross_market_experiments.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --dataset-id "$DATASET_ID" \
  --stage confirmation \
  --profile balanced \
  --training-scheme rolling \
  --parallel-workers 2 \
  --screening-run-id "$SCREENING_RUN_ID"

export CONFIRMATION_RUN_ID=$(python -c "from pathlib import Path; r=Path('artifacts/cross_market_ai_capability/runs'); p=max((x for x in r.glob('cm_ai_capability_confirmation_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")
echo "CONFIRMATION_RUN_ID=$CONFIRMATION_RUN_ID"

python scripts/analyze_ai_capability_model_run.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --run-id "$CONFIRMATION_RUN_ID"
```

### 6. Freeze one model and run the final 2025 evaluation

```bash
python scripts/freeze_cross_market_model.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --confirmation-run-id "$CONFIRMATION_RUN_ID"

export FREEZE_ID=$(python -c "from pathlib import Path; r=Path('artifacts/cross_market_ai_capability/freezes'); p=max(r.glob('cm_ai_capability_freeze_*.json'), key=lambda x:x.stat().st_mtime_ns); print(p.stem)")
echo "FREEZE_ID=$FREEZE_ID"

python scripts/run_cross_market_experiments.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --dataset-id "$DATASET_ID" \
  --stage final_test \
  --profile balanced \
  --training-scheme rolling \
  --parallel-workers 2 \
  --freeze-id "$FREEZE_ID"

export FINAL_RUN_ID=$(python -c "from pathlib import Path; r=Path('artifacts/cross_market_ai_capability/runs'); p=max((x for x in r.glob('cm_ai_capability_final_test_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")
echo "FINAL_RUN_ID=$FINAL_RUN_ID"

python scripts/analyze_ai_capability_model_run.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --run-id "$FINAL_RUN_ID"

python scripts/summarize_cross_market_run.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --run-id "$FINAL_RUN_ID"
```

### 7. Verify the complete lineage and evidence

```bash
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
```

The final verifier must report `"status": "pass"` before any result is transferred into the report.

## Interpretation order

Interpret evidence in this order: data integrity; feature availability and leakage audit; benchmark mapping coverage; descriptive event results; feature-set information gain; model-family comparison; complexity-generalization curve; confirmation stability; frozen final-model forecast accuracy; net strategy performance against Nifty IT and Nifty 50; cost sensitivity; inference and confidence intervals; feature importance; limitations. Statistical significance must not be replaced by a high point-estimate Sharpe, and an event correlation must not be described as causal.
