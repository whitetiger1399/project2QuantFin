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

Use the `focused_improvement` profile with quarterly refits and three concurrent workers on the current Apple Silicon machine. Daily forecasts remain fully out of sample within each refit block. The focused design retains all eight information-ladder rungs, forecast baselines, an expanded Elastic Net comparison, bounded Extra Trees/boosting capacity, and nonlinear complexity ratios from 0.5 to 10. It caps random features at 2,048 and avoids an uncontrolled Cartesian search. Exactly one model is frozen before the final stage.

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
  --profile focused_improvement \
  --training-scheme rolling \
  --parallel-workers 3

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
  --profile focused_improvement \
  --training-scheme rolling \
  --parallel-workers 3 \
  --resume-run-id "$SCREENING_RUN_ID"
```

### 5. Confirmation

```bash
python scripts/run_cross_market_experiments.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --dataset-id "$DATASET_ID" \
  --stage confirmation \
  --profile focused_improvement \
  --training-scheme rolling \
  --parallel-workers 3 \
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
  --profile focused_improvement \
  --training-scheme rolling \
  --parallel-workers 3 \
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

Run the stricter contract audit after verification:

```bash
python scripts/audit_ai_capability_contract.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --dataset-id "$DATASET_ID" \
  --run-id "$SCREENING_RUN_ID" \
  --run-id "$CONFIRMATION_RUN_ID" \
  --run-id "$FINAL_RUN_ID"
```

### 8. Build the final diagnostic packs

```bash
python scripts/summarize_information_ladder.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --run-id "$FINAL_RUN_ID"

export LADDER_ANALYSIS_ID=$(python -c "from pathlib import Path; r=Path('artifacts/cross_market_ai_capability/analysis'); p=max((x for x in r.glob('information_ladder_final_test_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")

python scripts/analyze_ai_capability_model_run.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --run-id "$FINAL_RUN_ID"

export MODEL_EVIDENCE_ID=$(python -c "from pathlib import Path; r=Path('artifacts/cross_market_ai_capability/analysis'); p=max((x for x in r.glob('model_evidence_final_test_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")

python scripts/compare_ai_services_strategies.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --run-id "$FINAL_RUN_ID"

export STRATEGY_ANALYSIS_ID=$(python -c "from pathlib import Path; r=Path('artifacts/cross_market_ai_capability/analysis'); p=max((x for x in r.glob('ai_strategy_comparison_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")
```

### 9. Rebuild and verify the January–September 2026 no-reselection extension

This stage reuses the previously downloaded 2026 market panel, rebuilds only the corrected capability overlay, and fits the frozen specification once on pre-2026 observations. It does not reselect a model or tune a hyperparameter on 2026.

```bash
export SOURCE_2026_DATASET_ID=$(python -c "from pathlib import Path; r=Path('data/processed/cross_market_ai_services_2026'); p=max((x for x in r.glob('ai_services_2026_panel_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")

python scripts/build_ai_capability_panel.py \
  --config configs/cross_market_ai_capability_2026_extension.yaml \
  --source-dataset-id "$SOURCE_2026_DATASET_ID"

export DATASET_2026_ID=$(python -c "from pathlib import Path; r=Path('data/processed/cross_market_ai_capability_2026'); p=max((x for x in r.glob('ai_capability_2026_panel_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")

python scripts/run_frozen_2026_extension.py \
  --dataset-id "$DATASET_2026_ID" \
  --freeze-id "$FREEZE_ID" \
  --start 2026-01-01 \
  --end 2026-09-30

export FORWARD_RUN_ID=$(python -c "from pathlib import Path; r=Path('artifacts/cross_market_ai_capability_2026/runs'); p=max((x for x in r.glob('cm_ai_capability_2026_forward_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")

python scripts/verify_frozen_2026_extension.py \
  --run-id "$FORWARD_RUN_ID"
```

### 10. Rebuild the report from the new immutable evidence

The report builder accepts evidence IDs through environment variables, so a fresh result never requires source-code edits. Keep these exports in the same terminal session.

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

python reports/build_report_ai_capability.py
python /Users/whitetiger/.codex/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/render_docx.py \
  reports/Project2_Team16_Report.docx \
  --output_dir reports/_render_final \
  --emit_pdf

cp reports/_render_final/Project2_Team16_Report.pdf \
  reports/Project2_Team16_Report.pdf
```

Inspect all rendered pages before treating the PDF as final. In particular, confirm that the cover contains every author, captions remain attached to figures, equations are legible, tables do not clip, and the evidence IDs in Appendix A match the new run.

### 11. Focused gap diagnostics (separate exploratory run)

Run this only after the canonical freeze and final evaluation above are complete. It does not replace or mutate the canonical freeze. The six predeclared configurations isolate the questions raised by the dated gap analysis: strict point-in-time macro vintage, own-history and peer baselines, U.S.-services incremental value, and AI-feature incremental value. All six use the same selected Extra Trees capacity and the same quarterly walk-forward protocol, so differences are attributable to the declared information exclusions rather than a new model search.

```bash
python scripts/run_cross_market_experiments.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --dataset-id "$DATASET_ID" \
  --stage screening \
  --profile gap_diagnostics \
  --training-scheme rolling \
  --parallel-workers 3

export GAP_DIAGNOSTIC_RUN_ID=$(python -c "from pathlib import Path; r=Path('artifacts/cross_market_ai_capability/runs'); p=max((x for x in r.glob('cm_ai_capability_screening_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")
echo "GAP_DIAGNOSTIC_RUN_ID=$GAP_DIAGNOSTIC_RUN_ID"

python scripts/cross_market_run_status.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --run-id "$GAP_DIAGNOSTIC_RUN_ID"

python scripts/analyze_ai_capability_model_run.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --run-id "$GAP_DIAGNOSTIC_RUN_ID"
```

The revised analysis emits whole-date block inference, repeated whole-date grouped permutation importance, corrected Sortino/drawdown accounting, and both fixed-holdings and policy-responsive cost sensitivity. For strategy-mechanism attribution on the frozen canonical run, execute:

```bash
python scripts/compare_ai_services_strategies.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --run-id "$FINAL_RUN_ID"
```

Interpret the gap run as development evidence. Do not replace the canonical model merely because an ablation, strict-vintage variant, or timing-only strategy looks better on already inspected dates; record it as a prospective candidate for a later freeze.

## Interpretation order

Interpret evidence in this order: data integrity; feature availability and leakage audit; benchmark mapping coverage; descriptive event results; feature-set information gain; model-family comparison; complexity-generalization curve; confirmation stability; frozen final-model forecast accuracy; net strategy performance against Nifty IT and Nifty 50; cost sensitivity; inference and confidence intervals; feature importance; limitations. Statistical significance must not be replaced by a high point-estimate Sharpe, and an event correlation must not be described as causal.
