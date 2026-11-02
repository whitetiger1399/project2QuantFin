# Team 16 recording commands

Prepared 2 November 2026. Run these manually; the document builder does not train models or download data.

## What the assignment requires

`documents/markdown/Project2.md`, Section 5, asks for an end-to-end run: **data build → fit → validation → out-of-sample evaluation with costs**, inside a 15–25 minute video. It does not explicitly demand an unedited real-time fit. Capture a genuine execution, retain the launch and completion, and label accelerated waiting and cuts. There is no requirement to place real orders. The assignment explicitly limits the project to historical research.

The timed presentation is 20:00, with speech ending by 19:40. Scenes 11–12 reserve screen time for the execution montage. Film the actual stages before editing the video; the raw training job can take much longer than its edited appearance. Keep readable progress and successful completion. A plan-only command or inspection of an old run does **not** demonstrate a fresh fit.

The prepared deck reports the named historical results in the supplied report. A fresh reproduction gets new IDs and may differ if sources, dependencies or configuration files have changed. Show its actual output and label it as a reproduction. If it changes the headline findings, reconcile the deck and report before submission; do not claim the old numbers came from the new run.

## Recording setup

Open a terminal at the repository root. The macOS/Linux commands below use Bash; on Windows use WSL Bash, or translate the environment activation for PowerShell. The project README documents native Windows installation.

```bash
bash
set -euo pipefail
source .venv/bin/activate
export MPLBACKEND=Agg
export MPLCONFIGDIR="${TMPDIR:-/tmp}/quantfin_recording_mpl"
export VIDEO_SESSION_START=$(date -u +%Y-%m-%dT%H:%M:%SZ)
```

On WSL, activate the virtual environment created inside WSL. Do not reuse a macOS or Windows `.venv`.

Define these two helpers once. They select only a completed object created during this recording session. They fail rather than silently reuse an old run. A failed stage stops the Bash sequence.

```bash
latest_complete() {
  python - "$1" "$2" "$VIDEO_SESSION_START" <<'PY'
import json, sys
from pathlib import Path
from datetime import datetime, timezone
root, pattern, since = sys.argv[1:]
cutoff = datetime.fromisoformat(since.replace('Z', '+00:00')).timestamp()
eligible=[]
for p in Path(root).glob(pattern):
    m=p/'manifest.json'
    if not m.is_file() or m.stat().st_mtime < cutoff:
        continue
    d=json.loads(m.read_text())
    if d.get('status')=='complete':
        eligible.append((m.stat().st_mtime_ns,p.name))
if not eligible:
    raise SystemExit('No completed object from this recording session: '+root)
print(max(eligible)[1])
PY
}
latest_freeze() {
  python - "$VIDEO_SESSION_START" <<'PY'
from pathlib import Path
from datetime import datetime
import sys
cutoff=datetime.fromisoformat(sys.argv[1].replace('Z','+00:00')).timestamp()
paths=[p for p in Path('artifacts/cross_market_ai_capability/freezes').glob('cm_ai_capability_freeze_*.json') if p.stat().st_mtime>=cutoff]
if not paths:raise SystemExit('No freeze created during this recording session')
print(max(paths,key=lambda p:p.stat().st_mtime_ns).stem)
PY
}
```

Before the recording, obtain the raw data through README Sections 4–5 if it is absent. Data providers can revise history. A data build from existing audited raw files is a real build and does not need to pretend to be a fresh API download. Never put an API key on screen.

## D1 — build and inspect the data

Show the build launch, its progress, completion, and feature dictionary. The builders read the latest compatible audited snapshots. Compare that inventory with the report if exact replication is intended.

```bash
python scripts/build_cross_market_panel.py \
  --config configs/cross_market_ai_services_research.yaml
export SOURCE_DATASET_ID=$(latest_complete data/processed/cross_market_ai_services 'ai_services_panel_*')

python scripts/build_ai_capability_panel.py \
  --source-dataset-id "$SOURCE_DATASET_ID"
export DATASET_ID=$(latest_complete data/processed/cross_market_ai_capability 'ai_capability_panel_*')

python scripts/build_cross_market_panel.py \
  --config configs/cross_market_ai_services_2026_extension.yaml
export SOURCE_2026_DATASET_ID=$(latest_complete data/processed/cross_market_ai_services_2026 'ai_services_2026_panel_*')

python scripts/build_ai_capability_panel.py \
  --config configs/cross_market_ai_capability_2026_extension.yaml \
  --source-dataset-id "$SOURCE_2026_DATASET_ID"
export DATASET_2026_ID=$(latest_complete data/processed/cross_market_ai_capability_2026 'ai_capability_2026_panel_*')
```

Create the matching analysis records needed by the existing pipeline verifier. These are data analyses, not extra model searches.

```bash
python scripts/run_cross_market_analysis.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --dataset-id "$DATASET_ID"
export EDA_RUN_ID=$(latest_complete artifacts/cross_market_ai_capability/analysis 'analysis_*')

python scripts/analyze_ai_capability_effects.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --dataset-id "$DATASET_ID"
export CAPABILITY_ANALYSIS_ID=$(latest_complete artifacts/cross_market_ai_capability/analysis 'ai_capability_analysis_*')

export EPOCH_SNAPSHOT_ID=$(python -c "import json; print(json.load(open('reports/releases/project2_team16_v2_2026-11-01/release_registry.json'))['ids']['EPOCH_SNAPSHOT_ID'])")
python scripts/analyze_epoch_capability_market_effects.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --dataset-id "$DATASET_ID" \
  --epoch-snapshot-id "$EPOCH_SNAPSHOT_ID"
export EPOCH_ANALYSIS_ID=$(latest_complete artifacts/cross_market_ai_capability/analysis 'epoch_capability_analysis_*')
```

## D2 — fit the screening candidates

Record a real fit. Display a training end date earlier than its prediction block. Do not describe `--plan-only` as training. Three workers match the documented laptop default; use fewer if memory is tight.

```bash
python scripts/run_cross_market_experiments.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --dataset-id "$DATASET_ID" \
  --stage screening --profile submission_rerun \
  --training-scheme rolling --parallel-workers 3
export SCREENING_RUN_ID=$(latest_complete artifacts/cross_market_ai_capability/runs 'cm_ai_capability_screening_*')
python scripts/cross_market_run_status.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --run-id "$SCREENING_RUN_ID"
```

## D3 — confirmation and freeze

```bash
python scripts/run_cross_market_experiments.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --dataset-id "$DATASET_ID" \
  --stage confirmation --profile submission_rerun \
  --training-scheme rolling --parallel-workers 3 \
  --screening-run-id "$SCREENING_RUN_ID"
export CONFIRMATION_RUN_ID=$(latest_complete artifacts/cross_market_ai_capability/runs 'cm_ai_capability_confirmation_*')

python scripts/freeze_cross_market_model.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --confirmation-run-id "$CONFIRMATION_RUN_ID"
export FREEZE_ID=$(latest_freeze)
```

## D4 — historical evaluation with costs and the extension

```bash
python scripts/run_cross_market_experiments.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --dataset-id "$DATASET_ID" \
  --stage final_test --profile submission_rerun \
  --training-scheme rolling --parallel-workers 3 \
  --freeze-id "$FREEZE_ID"
export FINAL_RUN_ID=$(latest_complete artifacts/cross_market_ai_capability/runs 'cm_ai_capability_final_test_*')

python scripts/run_frozen_2026_extension.py \
  --dataset-id "$DATASET_2026_ID" \
  --freeze-id "$FREEZE_ID" \
  --start 2026-01-01 --end 2026-09-30
export FORWARD_RUN_ID=$(latest_complete artifacts/cross_market_ai_capability_2026/runs 'cm_ai_capability_2026_forward_*')
```

## D5 — validate and inspect actual outputs

```bash
python scripts/verify_ai_capability_pipeline.py \
  --dataset-id "$DATASET_ID" \
  --epoch-snapshot-id "$EPOCH_SNAPSHOT_ID" \
  --eda-run-id "$EDA_RUN_ID" \
  --capability-analysis-id "$CAPABILITY_ANALYSIS_ID" \
  --epoch-analysis-id "$EPOCH_ANALYSIS_ID" \
  --screening-run-id "$SCREENING_RUN_ID" \
  --confirmation-run-id "$CONFIRMATION_RUN_ID" \
  --freeze-id "$FREEZE_ID" \
  --final-run-id "$FINAL_RUN_ID"

python scripts/verify_frozen_2026_extension.py --run-id "$FORWARD_RUN_ID"

python - <<'PY'
import os,json
from pathlib import Path
import numpy as np
import pandas as pd
for key,root in [('FINAL_RUN_ID','artifacts/cross_market_ai_capability/runs'),('FORWARD_RUN_ID','artifacts/cross_market_ai_capability_2026/runs')]:
    folder=Path(root)/os.environ[key]
    m=json.loads((folder/'manifest.json').read_text())
    selected=m['selected_config_id']
    x=pd.read_parquet(folder/'strategy_ledgers.parquet')
    x=x.loc[x.config_id.eq(selected)] if 'config_id' in x else x
    assert np.allclose(x.gross_return-x.trading_cost,x.net_return,atol=1e-12)
    print(key,m['status'],'sessions:',len(x),'net return:',(1+x.net_return).prod()-1)
    print(x.loc[x.gross_exposure.gt(0),['decision_date','expected_gross_return','expected_net_return','holdings','gross_return','trading_cost','net_return']].head(2).to_string(index=False))
PY
```

This last block reads the **fresh** run variables from this terminal. If the selected model differs from the historical report, show that difference openly. It must not be renamed to match the old result.

## Optional supporting inspection of the report’s recorded backtest

```bash
python scripts/recording_evidence.py
```

This command checks the two **existing report runs**, their saved ledger hashes where recorded, training-date order, exposure caps, two-sided turnover, cost rate, and gross-minus-cost arithmetic. It prints sample expected returns and realized returns. The output explicitly says that it is a recorded historical run, not a new fit. It is supporting evidence for the deck’s numbers, not a substitute for D1–D4.

## What “backtesting” means here

The custom implementation is in `src/quantfin/cross_market/experiments.py`:

- `_fit_block`: training observations precede the prediction block; transformations use the fitting window.
- `_strategy_ledger`: thresholded long/short/flat selection, capped weights, open-to-close returns and square-off.
- Entry plus exit turnover is twice gross exposure; one-way assumed friction is 7.5 basis points.
- Net return is gross minus turnover costs; `_annualized_metrics` compounds returns and calculates return, volatility, Sharpe and drawdown.
- ETF benchmarks hold overnight exposure; the daily strategy does not. Public opening prices approximate fills. The assumed fee/spread/slippage schedule does not fully model taxes, borrow availability or market impact.

The assignment’s Backtrader/backtesting.py/bt examples are optional illustrations. The current code does not need one of those packages to count as a backtest. It does need the timing, cost, benchmark and validation controls above, and the report correctly discloses their practical limits.

## Rebuild these presentation documents only

```bash
MPLBACKEND=Agg MPLCONFIGDIR=/tmp/quantfin_video_mpl XDG_CACHE_HOME=/tmp/quantfin_video_cache \
  python scripts/build_project2_video_package.py
```

Render both DOCX files to PDF with Word, Pages, or LibreOffice; preserve the custom 960 × 540 pt page size. Inspect every page and confirm 20 deck pages (16 timed, three supporting figures, one reference page) and 18 script pages. The four appendix pages are excluded from the 20-minute recording. Then hash all six final formats:

```bash
python scripts/build_project2_video_package.py --finalize
```

No training job is launched by rebuilding or finalizing the presentation package.
