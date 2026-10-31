# AI Services Experiment — Sequential Fresh-Run Commands

Run each numbered block only after the preceding block succeeds. Expensive
downloads and model fits are intentionally not executed by the code authoring
step.

## 1. Environment and plan checks

```bash
cd /Users/whitetiger/Desktop/WhiteTiger/17_projects/24_Project2_QuantFin/project2QuantFin
source .venv/bin/activate
export PYTHONUNBUFFERED=1
export MPLCONFIGDIR="$PWD/artifacts/.matplotlib-cache"
mkdir -p "$MPLCONFIGDIR"

python scripts/build_frontier_ai_release_calendar.py
python scripts/fetch_cross_market_markets.py --group us_it_services
python scripts/fetch_cross_market_markets.py --group us_it_enabled_payments
python scripts/fetch_cross_market_markets.py --group us_enterprise_software
```

## 2. Build the immutable event snapshot

```bash
python scripts/build_frontier_ai_release_calendar.py --execute
```

Review the curated events before continuing:

```bash
EVENT_SNAPSHOT=$(find data/raw/cross_market/frontier_ai_events -mindepth 1 -maxdepth 1 -type d -name 'frontier_ai_events_*' -print0 | xargs -0 ls -td | head -1)
python -c "import pandas as pd,sys; p=sys.argv[1]; d=pd.read_csv(p+'/frontier_ai_releases.csv'); print(d[['release_date','provider','model_family','primary_event','inventory_match','source_url']].to_string(index=False))" "$EVENT_SNAPSHOT"
```

## 3. Download the new U.S. market blocks

```bash
python scripts/fetch_cross_market_markets.py --group us_it_services --execute
python scripts/fetch_cross_market_markets.py --group us_it_enabled_payments --execute
python scripts/fetch_cross_market_markets.py --group us_enterprise_software --execute
```

If a command reports an incomplete snapshot, use the exact snapshot ID printed
by that command:

```bash
python scripts/fetch_cross_market_markets.py --group GROUP_NAME --resume-snapshot SNAPSHOT_ID --execute
```

## 4. Audit all required raw inputs

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

Stop if the status is `fail`. `pass_with_warnings` is acceptable only after the
listed quarantine restrictions are reviewed.

## 5. Build the new hashed panel

```bash
python scripts/build_cross_market_panel.py \
  --config configs/cross_market_ai_services_research.yaml \
  --plan-only

python scripts/build_cross_market_panel.py \
  --config configs/cross_market_ai_services_research.yaml

export DATASET_ID=$(python -c "from pathlib import Path; import json; root=Path('data/processed/cross_market_ai_services'); p=max((x for x in root.glob('ai_services_panel_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")
echo "DATASET_ID=$DATASET_ID"
```

## 6. Run general and focused EDA

```bash
python scripts/run_cross_market_analysis.py \
  --config configs/cross_market_ai_services_research.yaml \
  --dataset-id "$DATASET_ID"

python scripts/analyze_ai_services_experiment.py \
  --config configs/cross_market_ai_services_research.yaml \
  --dataset-id "$DATASET_ID" \
  --plan-only

python scripts/analyze_ai_services_experiment.py \
  --config configs/cross_market_ai_services_research.yaml \
  --dataset-id "$DATASET_ID"
```

## 7. Screening run

```bash
python scripts/run_cross_market_experiments.py \
  --config configs/cross_market_ai_services_research.yaml \
  --dataset-id "$DATASET_ID" \
  --stage screening \
  --profile balanced \
  --training-scheme rolling \
  --parallel-workers 2 \
  --plan-only

python scripts/run_cross_market_experiments.py \
  --config configs/cross_market_ai_services_research.yaml \
  --dataset-id "$DATASET_ID" \
  --stage screening \
  --profile balanced \
  --training-scheme rolling \
  --parallel-workers 2

```

Capture the completed run ID automatically, then:

```bash
export SCREENING_RUN_ID=$(python -c "from pathlib import Path; p=max((x for x in Path('artifacts/cross_market_ai_services/runs').glob('cm_ai_services_screening_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")
echo "SCREENING_RUN_ID=$SCREENING_RUN_ID"
python scripts/cross_market_run_status.py \
  --config configs/cross_market_ai_services_research.yaml \
  --run-id "$SCREENING_RUN_ID"

python scripts/summarize_information_ladder.py \
  --config configs/cross_market_ai_services_research.yaml \
  --run-id "$SCREENING_RUN_ID"
```

Resume only the same content-hash run if interrupted:

```bash
python scripts/run_cross_market_experiments.py \
  --config configs/cross_market_ai_services_research.yaml \
  --dataset-id "$DATASET_ID" \
  --stage screening \
  --profile balanced \
  --training-scheme rolling \
  --parallel-workers 2 \
  --resume-run-id "$SCREENING_RUN_ID"
```

## 8. Confirmation run

```bash
python scripts/run_cross_market_experiments.py \
  --config configs/cross_market_ai_services_research.yaml \
  --dataset-id "$DATASET_ID" \
  --stage confirmation \
  --profile balanced \
  --training-scheme rolling \
  --parallel-workers 2 \
  --screening-run-id "$SCREENING_RUN_ID"

export CONFIRMATION_RUN_ID=$(python -c "from pathlib import Path; p=max((x for x in Path('artifacts/cross_market_ai_services/runs').glob('cm_ai_services_confirmation_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")
echo "CONFIRMATION_RUN_ID=$CONFIRMATION_RUN_ID"
python scripts/cross_market_run_status.py \
  --config configs/cross_market_ai_services_research.yaml \
  --run-id "$CONFIRMATION_RUN_ID"

python scripts/summarize_information_ladder.py \
  --config configs/cross_market_ai_services_research.yaml \
  --run-id "$CONFIRMATION_RUN_ID"
```

## 9. Freeze exactly one model

```bash
python scripts/freeze_cross_market_model.py \
  --config configs/cross_market_ai_services_research.yaml \
  --confirmation-run-id "$CONFIRMATION_RUN_ID" \
  --plan-only

python scripts/freeze_cross_market_model.py \
  --config configs/cross_market_ai_services_research.yaml \
  --confirmation-run-id "$CONFIRMATION_RUN_ID"

export FREEZE_ID=$(python -c "from pathlib import Path; p=max(Path('artifacts/cross_market_ai_services/freezes').glob('cm_ai_services_freeze_*.json'), key=lambda x:x.stat().st_mtime_ns); print(p.stem)")
echo "FREEZE_ID=$FREEZE_ID"
```

## 10. Evaluate the frozen 2025 historical replication

```bash
python scripts/run_cross_market_experiments.py \
  --config configs/cross_market_ai_services_research.yaml \
  --dataset-id "$DATASET_ID" \
  --stage final_test \
  --profile balanced \
  --training-scheme rolling \
  --parallel-workers 2 \
  --freeze-id "$FREEZE_ID"

export FINAL_RUN_ID=$(python -c "from pathlib import Path; p=max((x for x in Path('artifacts/cross_market_ai_services/runs').glob('cm_ai_services_final_test_*') if (x/'manifest.json').is_file()), key=lambda x:(x/'manifest.json').stat().st_mtime_ns); print(p.name)")
echo "FINAL_RUN_ID=$FINAL_RUN_ID"
python scripts/cross_market_run_status.py \
  --config configs/cross_market_ai_services_research.yaml \
  --run-id "$FINAL_RUN_ID"

python scripts/summarize_information_ladder.py \
  --config configs/cross_market_ai_services_research.yaml \
  --run-id "$FINAL_RUN_ID"
```

## 11. Compare trading rules on the same frozen predictions

```bash
python scripts/compare_ai_services_strategies.py \
  --config configs/cross_market_ai_services_research.yaml \
  --run-id "$FINAL_RUN_ID" \
  --plan-only

python scripts/compare_ai_services_strategies.py \
  --config configs/cross_market_ai_services_research.yaml \
  --run-id "$FINAL_RUN_ID"
```

## 12. Verify lineage and hashes

```bash
python scripts/verify_cross_market_outputs.py \
  --config configs/cross_market_ai_services_research.yaml \
  --dataset-id "$DATASET_ID" \
  --screening-run-id "$SCREENING_RUN_ID" \
  --confirmation-run-id "$CONFIRMATION_RUN_ID" \
  --freeze-id "$FREEZE_ID" \
  --final-run-id "$FINAL_RUN_ID"
```

Do not update the report with the new result until the verification command
passes and the event-calendar review has been retained as evidence.
