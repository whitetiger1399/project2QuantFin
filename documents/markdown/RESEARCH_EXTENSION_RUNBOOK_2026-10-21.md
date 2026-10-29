# Research extension runbook — 21 October 2026

Run these commands from the repository root. Expensive scripts are plan-only until `--execute` is supplied. The extension is retrospective and leaves the canonical final run unchanged.

## 0. Environment

```bash
cd /Users/whitetiger/Desktop/WhiteTiger/17_projects/24_Project2_QuantFin/project2QuantFin
source .venv/bin/activate
python -m pip install -e .
mkdir -p artifacts/logs
```

## 1. Provenance, activity, and boundary audits

```bash
python scripts/audit_research_provenance.py

python scripts/audit_model_activity.py \
  --run-id models_screening_fe6e26bdd5521077 \
  --run-id models_confirmation_96d234651d29fb8c \
  --run-id models_final_test_3e46f0e36fd220d6 \
  --run-id models_screening_d7252adb14317fcd \
  --run-id models_confirmation_87083937c8d58d9b

python scripts/verify_research_extension.py
```

## 2. Focused EDA and feature definitions

```bash
python scripts/export_feature_dictionary.py \
  --feature-dataset-id features_yahoo_20261020T055638Z_799f619a4f \
  --feature-set F2

python scripts/run_focused_eda.py

python -m quantfin stat-tests \
  --market-dataset-id market_yahoo_20261020T055638Z \
  --feature-dataset-id features_yahoo_20261020T055638Z_799f619a4f \
  --feature-set F2 --split initial_train
```

## 3. Matched F0/F1/F2 ablations

Plan the three runs first:

```bash
for FEATURE_SET in F0 F1 F2; do
  python -m quantfin run-models \
    --models-config configs/models_comparison.yaml \
    --feature-dataset-id features_yahoo_20261020T055638Z_799f619a4f \
    --feature-set "$FEATURE_SET" --stage screening --profile quick --plan-only
done
```

Execute and capture actual IDs without placeholders:

```bash
python -m quantfin run-models --models-config configs/models_comparison.yaml \
  --feature-dataset-id features_yahoo_20261020T055638Z_799f619a4f \
  --feature-set F0 --stage screening --profile quick | tee artifacts/logs/ablation_f0.log
export F0_RUN_ID=$(sed -n 's/^Completed run: //p' artifacts/logs/ablation_f0.log | tail -1)

python -m quantfin run-models --models-config configs/models_comparison.yaml \
  --feature-dataset-id features_yahoo_20261020T055638Z_799f619a4f \
  --feature-set F1 --stage screening --profile quick | tee artifacts/logs/ablation_f1.log
export F1_RUN_ID=$(sed -n 's/^Completed run: //p' artifacts/logs/ablation_f1.log | tail -1)

python -m quantfin run-models --models-config configs/models_comparison.yaml \
  --feature-dataset-id features_yahoo_20261020T055638Z_799f619a4f \
  --feature-set F2 --stage screening --profile quick | tee artifacts/logs/ablation_f2.log
export F2_RUN_ID=$(sed -n 's/^Completed run: //p' artifacts/logs/ablation_f2.log | tail -1)

printf 'F0_RUN_ID=%s\nF1_RUN_ID=%s\nF2_RUN_ID=%s\n' "$F0_RUN_ID" "$F1_RUN_ID" "$F2_RUN_ID"

python scripts/summarize_feature_ablations.py \
  --f0-run-id "$F0_RUN_ID" --f1-run-id "$F1_RUN_ID" --f2-run-id "$F2_RUN_ID" \
  --family random_forest
```

## 4. Bounded compute profile

```bash
python scripts/profile_compute.py \
  --feature-dataset features_yahoo_20261020T055638Z_799f619a4f \
  --feature-set F2 --sample-sizes 504 1260 2747

python scripts/profile_compute.py \
  --feature-dataset features_yahoo_20261020T055638Z_799f619a4f \
  --feature-set F2 --sample-sizes 504 1260 2747 \
  --execute --max-minutes 20
```

## 5. Random-feature complexity study

### Pilot

```bash
python scripts/run_complexity_experiment.py --mode pilot
export COMPLEXITY_PILOT_ID=$(python scripts/run_complexity_experiment.py --mode pilot | python -c 'import json,sys; print(json.load(sys.stdin)["run_id"])')
python scripts/run_complexity_experiment.py --mode pilot --execute --max-hours 1
cat "artifacts/research/complexity_runs/$COMPLEXITY_PILOT_ID/run_manifest.json"
```

Resume after an interruption or `budget_stop`:

```bash
python scripts/run_complexity_experiment.py --mode pilot --execute --resume --max-hours 1
```

### Primary curve

Run after reviewing pilot time, memory, rank, and condition diagnostics.

```bash
python scripts/run_complexity_experiment.py --mode primary
export COMPLEXITY_PRIMARY_ID=$(python scripts/run_complexity_experiment.py --mode primary | python -c 'import json,sys; print(json.load(sys.stdin)["run_id"])')
python scripts/run_complexity_experiment.py --mode primary --execute --max-hours 5
```

Resume the same run in additional five-hour slices if required:

```bash
python scripts/run_complexity_experiment.py --mode primary --execute --resume --max-hours 5
```

### Window and seed sensitivity

```bash
export COMPLEXITY_WINDOW_ID=$(python scripts/run_complexity_experiment.py --mode window_sensitivity | python -c 'import json,sys; print(json.load(sys.stdin)["run_id"])')
python scripts/run_complexity_experiment.py --mode window_sensitivity --execute --max-hours 5

export COMPLEXITY_SEED_ID=$(python scripts/run_complexity_experiment.py --mode seed_sensitivity | python -c 'import json,sys; print(json.load(sys.stdin)["run_id"])')
python scripts/run_complexity_experiment.py --mode seed_sensitivity --execute --max-hours 5
```

Use `--resume` with the matching mode if either run stops. Do not rank an incomplete run.

## 6. Tree-capacity screening and confirmation

```bash
python -m quantfin run-models \
  --models-config configs/models_capacity_2026-10-21.yaml \
  --feature-dataset-id features_yahoo_20261020T055638Z_799f619a4f \
  --feature-set F2 --stage screening --profile standard --window 1260 --plan-only

python -m quantfin run-models \
  --models-config configs/models_capacity_2026-10-21.yaml \
  --feature-dataset-id features_yahoo_20261020T055638Z_799f619a4f \
  --feature-set F2 --stage screening --profile standard --window 1260 \
  | tee artifacts/logs/capacity_screening.log
export CAPACITY_SCREENING_RUN_ID=$(sed -n 's/^Completed run: //p' artifacts/logs/capacity_screening.log | tail -1)

python scripts/select_research_candidates.py --run-id "$CAPACITY_SCREENING_RUN_ID" --top 2

python -m quantfin run-models \
  --models-config configs/models_capacity_2026-10-21.yaml \
  --feature-dataset-id features_yahoo_20261020T055638Z_799f619a4f \
  --feature-set F2 --stage confirmation --profile standard --window 1260 \
  --selection "artifacts/runs/$CAPACITY_SCREENING_RUN_ID/selection_research.json" --plan-only

python -m quantfin run-models \
  --models-config configs/models_capacity_2026-10-21.yaml \
  --feature-dataset-id features_yahoo_20261020T055638Z_799f619a4f \
  --feature-set F2 --stage confirmation --profile standard --window 1260 \
  --selection "artifacts/runs/$CAPACITY_SCREENING_RUN_ID/selection_research.json" \
  | tee artifacts/logs/capacity_confirmation.log
export CAPACITY_CONFIRMATION_RUN_ID=$(sed -n 's/^Completed run: //p' artifacts/logs/capacity_confirmation.log | tail -1)

python -m quantfin plot-run --models-config configs/models_capacity_2026-10-21.yaml \
  --run-id "$CAPACITY_SCREENING_RUN_ID" --top-n 12
python -m quantfin plot-run --models-config configs/models_capacity_2026-10-21.yaml \
  --run-id "$CAPACITY_CONFIRMATION_RUN_ID" --top-n 8
```

Do not create another final-test freeze from these retrospective experiments.

## 7. Boosting-round and MLP-epoch studies

Run three-origin pilots:

```bash
python scripts/run_learning_curve_experiment.py --family boosting --origin-limit 3
python scripts/run_learning_curve_experiment.py --family mlp --origin-limit 3
python scripts/run_learning_curve_experiment.py --family boosting --origin-limit 3 --execute --max-hours 1
python scripts/run_learning_curve_experiment.py --family mlp --origin-limit 3 --execute --max-hours 1
```

Then run full screening studies, one process at a time:

```bash
export BOOSTING_RUN_ID=$(python scripts/run_learning_curve_experiment.py --family boosting | python -c 'import json,sys; print(json.load(sys.stdin)["run_id"])')
python scripts/run_learning_curve_experiment.py --family boosting --execute --max-hours 5

export MLP_RUN_ID=$(python scripts/run_learning_curve_experiment.py --family mlp | python -c 'import json,sys; print(json.load(sys.stdin)["run_id"])')
python scripts/run_learning_curve_experiment.py --family mlp --execute --max-hours 5
```

Resume if needed:

```bash
python scripts/run_learning_curve_experiment.py --family boosting --execute --resume --max-hours 5
python scripts/run_learning_curve_experiment.py --family mlp --execute --resume --max-hours 5
```

## 8. Risk fairness, sizing, uncertainty, and driver drift

The first command selects a complexity configuration for retrospective diagnostics only.

```bash
export BEST_COMPLEXITY_CONFIG_ID=$(python -c 'import pandas as pd,os; p=os.path.join("artifacts/research/complexity_runs",os.environ["COMPLEXITY_PRIMARY_ID"],"config_metrics.csv"); d=pd.read_csv(p); d=d[d.activity_gate_pass.astype(bool)]; print(d.sort_values("oos_r2_vs_historical_mean",ascending=False).iloc[0].config_id)')

python scripts/analyze_strategy_robustness.py \
  --predictions "artifacts/research/complexity_runs/$COMPLEXITY_PRIMARY_ID/predictions.parquet" \
  --config-id "$BEST_COMPLEXITY_CONFIG_ID"

python scripts/analyze_feature_drift.py \
  --run-id "$CAPACITY_CONFIRMATION_RUN_ID" \
  --feature-dataset-id features_yahoo_20261020T055638Z_799f619a4f --feature-set F2
```

## 9. Optional point-in-time macro and VIX data

This phase does not block the complexity experiment. Obtain a FRED API key. Optionally download the official historical VIX CSV to `data/external/manual/vix_history.csv`. Inspect the request before downloading:

```bash
python scripts/fetch_point_in_time_context.py --vix-csv data/external/manual/vix_history.csv
```

Then execute. Do not commit the API key.

```bash
export FRED_API_KEY='REPLACE_WITH_YOUR_FRED_API_KEY'
python scripts/fetch_point_in_time_context.py \
  --vix-csv data/external/manual/vix_history.csv --execute \
  | tee artifacts/logs/context_fetch.json
export CONTEXT_SNAPSHOT_ID=$(python -c 'import json; print(json.load(open("artifacts/logs/context_fetch.json"))["snapshot_id"])')

python scripts/build_context_features.py --context-snapshot "$CONTEXT_SNAPSHOT_ID" \
  | tee artifacts/logs/context_features.json
export CONTEXT_FEATURE_DATASET_ID=$(python -c 'import json; print(json.load(open("artifacts/logs/context_features.json"))["dataset_id"])')

python -m quantfin check-timing --feature-dataset-id "$CONTEXT_FEATURE_DATASET_ID"
python scripts/export_feature_dictionary.py \
  --feature-dataset-id "$CONTEXT_FEATURE_DATASET_ID" --feature-set F3 \
  --output-dir artifacts/research/feature_dictionary_F3_2026-10-21
```

If VIX is unavailable, remove `--vix-csv`. The first context experiment should compare F2 and F3 on identical screening dates.

## 10. Final extension verification

```bash
python scripts/verify_research_extension.py \
  --complexity-run-dir "artifacts/research/complexity_runs/$COMPLEXITY_PRIMARY_ID" \
  --complexity-run-dir "artifacts/research/complexity_runs/$COMPLEXITY_WINDOW_ID" \
  --complexity-run-dir "artifacts/research/complexity_runs/$COMPLEXITY_SEED_ID" \
  --learning-run-dir "artifacts/research/learning_curve_runs/$BOOSTING_RUN_ID" \
  --learning-run-dir "artifacts/research/learning_curve_runs/$MLP_RUN_ID"

python scripts/audit_model_activity.py \
  --run-id "$CAPACITY_SCREENING_RUN_ID" \
  --run-id "$CAPACITY_CONFIRMATION_RUN_ID" \
  --minimum-active-sessions 30 --minimum-round-trips 10

git status --short
```

Preserve every printed run ID. Rebuild the report only after complete-cell counts, activity tables, uncertainty results, and figures have been reviewed. The report must retain the original frozen final result and identify every extension as retrospective.

