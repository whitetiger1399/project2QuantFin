# Cross-Market Pipeline Execution Runbook

This runbook executes one protocol from immutable raw snapshots to one frozen model and one final holdout evaluation. Commands are intentionally separated so each output can be inspected before the next stage.

## Identity contract

- Dataset ID: `cross_market_panel_<UTC timestamp>_<source hash>`
- Analysis ID: `analysis_<UTC timestamp>_<content hash>`
- Experiment ID: `cm_<stage>_<UTC timestamp>_<content hash>`
- Freeze ID: `cm_freeze_<UTC timestamp>_<content hash>`
- Model-summary ID: `model_summary_<UTC timestamp>_<content hash>`

The timestamp distinguishes executions. The hash proves the content identity. Use `--resume-run-id` to continue an interrupted experiment; do not start a new run if checkpoint reuse is intended.

## Stage order

1. Verify raw snapshots.
2. Build the cleaned, point-in-time panel.
3. Run EDA and statistical diagnostics.
4. Run deep screening on 2021–2022.
5. Summarize screening and inspect feature/model/complexity tables.
6. Confirm preselected candidates on 2023–2024.
7. Freeze exactly one model.
8. Run the frozen model once on 2025–2026.
9. Summarize and verify the complete lineage.

The final test includes forecast baselines for comparison, but `final_model_count` remains one: only the frozen confirmation winner is the selected research model.

## Compute controls

The protocol limits numerical libraries to one thread per model worker and uses four workers for tree ensembles. Screening and confirmation checkpoint quarterly; the frozen final model checkpoints monthly. The deep profile contains 36 configurations and eight screening quarters, producing 288 screening refits instead of the superseded 2,160-refit plan. Training-only 500-feature screening and practical convergence settings reduce a representative F4 LASSO refit from roughly 347 seconds to 3.62 seconds on the development machine. The quick profile remains a pipeline check only and is not a substitute for the deep research run.

To resume an interrupted screening run:

```bash
python scripts/run_cross_market_experiments.py \
  --dataset-id "$DATASET_ID" \
  --stage screening \
  --profile deep \
  --resume-run-id "$SCREENING_RUN_ID"
```

The command refuses to resume if stage, dataset, configuration, candidates, or training scheme produce a different content hash.

## Complete terminal sequence

Run from the repository root:

```bash
cd /Users/whitetiger/Desktop/WhiteTiger/17_projects/24_Project2_QuantFin/project2QuantFin
source .venv/bin/activate
export PYTHONHASHSEED=17
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
```

Verify the raw-data gate:

```bash
python scripts/audit_cross_market_raw.py \
  --required-group india_core \
  --required-group us_limited_tech \
  --required-group us_context \
  --required-group indian_it_adrs \
  --required-group global_context \
  --required-group nifty50_point_in_time \
  --required-group sp500_point_in_time
```

Build the panel:

```bash
python scripts/build_cross_market_panel.py --plan-only
python scripts/build_cross_market_panel.py

export DATASET_ID=$(python -c "from pathlib import Path; p=max((x for x in Path('data/processed/cross_market').glob('cross_market_panel_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")
echo "DATASET_ID=$DATASET_ID"
python scripts/cross_market_run_status.py --run-id "$DATASET_ID"
```

Run descriptive and statistical analysis:

```bash
python scripts/run_cross_market_analysis.py --dataset-id "$DATASET_ID" --plan-only
python scripts/run_cross_market_analysis.py --dataset-id "$DATASET_ID"

export ANALYSIS_RUN_ID=$(python -c "from pathlib import Path; p=max((x for x in Path('artifacts/cross_market/analysis').glob('analysis_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")
echo "ANALYSIS_RUN_ID=$ANALYSIS_RUN_ID"
```

Run the complete deep screening suite:

```bash
python scripts/run_cross_market_experiments.py \
  --dataset-id "$DATASET_ID" \
  --stage screening \
  --profile deep \
  --training-scheme rolling \
  --plan-only

python scripts/run_cross_market_experiments.py \
  --dataset-id "$DATASET_ID" \
  --stage screening \
  --profile deep \
  --training-scheme rolling

export SCREENING_RUN_ID=$(python -c "from pathlib import Path; import json; ps=[p for p in Path('artifacts/cross_market/runs').glob('cm_screening_*') if (p/'manifest.json').is_file() and json.load(open(p/'manifest.json'))['status']=='complete']; print(max(ps,key=lambda p:(p/'manifest.json').stat().st_mtime_ns).name)")
echo "SCREENING_RUN_ID=$SCREENING_RUN_ID"
python scripts/cross_market_run_status.py --run-id "$SCREENING_RUN_ID"
python scripts/summarize_cross_market_run.py --run-id "$SCREENING_RUN_ID"
```

Run confirmation:

```bash
python scripts/run_cross_market_experiments.py \
  --dataset-id "$DATASET_ID" \
  --stage confirmation \
  --profile deep \
  --screening-run-id "$SCREENING_RUN_ID" \
  --training-scheme rolling \
  --plan-only

python scripts/run_cross_market_experiments.py \
  --dataset-id "$DATASET_ID" \
  --stage confirmation \
  --profile deep \
  --screening-run-id "$SCREENING_RUN_ID" \
  --training-scheme rolling

export CONFIRMATION_RUN_ID=$(python -c "from pathlib import Path; import json; ps=[p for p in Path('artifacts/cross_market/runs').glob('cm_confirmation_*') if (p/'manifest.json').is_file() and json.load(open(p/'manifest.json')).get('screening_run_id')=='$SCREENING_RUN_ID']; print(max(ps,key=lambda p:(p/'manifest.json').stat().st_mtime_ns).name)")
echo "CONFIRMATION_RUN_ID=$CONFIRMATION_RUN_ID"
python scripts/cross_market_run_status.py --run-id "$CONFIRMATION_RUN_ID"
```

Freeze one model, then open the final holdout once:

```bash
python scripts/freeze_cross_market_model.py \
  --confirmation-run-id "$CONFIRMATION_RUN_ID" \
  --plan-only

python scripts/freeze_cross_market_model.py \
  --confirmation-run-id "$CONFIRMATION_RUN_ID"

export FREEZE_ID=$(python -c "from pathlib import Path; import json; ps=[p for p in Path('artifacts/cross_market/freezes').glob('cm_freeze_*.json') if json.load(open(p)).get('confirmation_run_id')=='$CONFIRMATION_RUN_ID']; print(max(ps,key=lambda p:p.stat().st_mtime_ns).stem)")
echo "FREEZE_ID=$FREEZE_ID"

python scripts/run_cross_market_experiments.py \
  --dataset-id "$DATASET_ID" \
  --stage final_test \
  --profile deep \
  --freeze-id "$FREEZE_ID" \
  --training-scheme rolling \
  --plan-only

python scripts/run_cross_market_experiments.py \
  --dataset-id "$DATASET_ID" \
  --stage final_test \
  --profile deep \
  --freeze-id "$FREEZE_ID" \
  --training-scheme rolling

export FINAL_RUN_ID=$(python -c "from pathlib import Path; import json; ps=[p for p in Path('artifacts/cross_market/runs').glob('cm_final_test_*') if (p/'manifest.json').is_file() and json.load(open(p/'manifest.json')).get('freeze_id')=='$FREEZE_ID']; print(max(ps,key=lambda p:(p/'manifest.json').stat().st_mtime_ns).name)")
echo "FINAL_RUN_ID=$FINAL_RUN_ID"
python scripts/cross_market_run_status.py --run-id "$FINAL_RUN_ID"
python scripts/summarize_cross_market_run.py --run-id "$FINAL_RUN_ID"
```

Verify the complete lineage:

```bash
python scripts/verify_cross_market_outputs.py \
  --dataset-id "$DATASET_ID" \
  --analysis-run-id "$ANALYSIS_RUN_ID" \
  --screening-run-id "$SCREENING_RUN_ID" \
  --confirmation-run-id "$CONFIRMATION_RUN_ID" \
  --freeze-id "$FREEZE_ID" \
  --final-run-id "$FINAL_RUN_ID"
```

Optional expanding-window confirmation should be run before freezing if it will influence interpretation. It must not replace the predeclared rolling primary result:

```bash
python scripts/run_cross_market_experiments.py \
  --dataset-id "$DATASET_ID" \
  --stage confirmation \
  --profile deep \
  --screening-run-id "$SCREENING_RUN_ID" \
  --training-scheme expanding
```
