# DSA5205 Project 2 — Feature Engineering and Leakage Audit

**Scope:** Main US–India / Nifty IT cross-market return-prediction pipeline, plus a separately identified legacy SPY dataset audit.  
**Evidence status:** Results below were reported from the team's local checkout on 2 November 2026. They are not claims of an independently replayed full experiment.  
**Safety:** All commands in this document are read-only except installing dependencies and writing audit logs/CSVs. Do not rebuild or overwrite the frozen final-test artifacts.

## Executive summary

The study predicts the same-day open-to-close return of ten Indian IT stocks using an 08:55 IST information cutoff and progressively richer Indian, US, global, and macro feature sets. The saved main panel has **25,380 rows, 2,538 decision dates, 10 assets, 3,341 columns**, including **3,333 documented features**. The selected frozen configuration is Elastic Net (`cm_elastic_net_329a4ccca456`) using `F4_full_us` (3,140 candidate features), `alpha=0.0005`, `l1_ratio=0.8`, `preselect_k=500`, `max_iter=4000`, and `tolerance=0.0001`.

**Verified by reported tests and inspected code:**

- All **456** saved training checkpoints matched reconstructed chronological training windows: screening **288/288**, confirmation **80/80**, final test **88/88**. Configured rolling window: **1,260 sessions**; embargo: **one session**; minimum training rows: **5,000**. This is a date-level/metadata audit, not a model replay or an independent check of intraday label-publication times.
- Four main prediction files were reported to have no duplicate prediction keys and no nonfinite predictions; the 2025 derived final slice matched the frozen final run exactly on prediction, target, and benchmark values. The slice manifest declares no refit and no model reselection.
- Confirmation and final-test manifests reference the same dataset and configuration hashes and the same selected Elastic Net configuration. The final-test manifest points to the confirmation run and freeze artifact. The freeze's recorded confirmation-manifest SHA-256 matched the actual file bytes.
- The inspected `_fit_block` implementation selects dates before each forecast block, applies the embargo, and fits preprocessing and the estimator on training observations. `_viable_columns` uses training missingness and variance; `_winsorize` learns clipping thresholds from training; the `SelectKBest(f_regression)` selector is inside the sklearn Pipeline fitted on `x_train, y_train`.
- All **60** `current_vintage_fallback=True` features are macro features in `F5_macro_nonlinear` only; none are declared in the selected `F4_full_us` set. This is structural exclusion, conditional on the feature-selection implementation respecting the dictionary.
- `_market_features` computes trailing OHLCV indicators and `_asof_align` uses backward `merge_asof(..., allow_exact_matches=False)` to exclude same-date observations. This establishes conservative **date-level** alignment, not historical source publication timestamps.
- The legacy SPY dataset audit found **5,281 complete rows** with valid chronology and **two unlabeled terminal rows** in `final_test`; those rows must be excluded from realized-return evaluation. This legacy dataset is *not* the active cross-market panel.

**Not yet verified / limitations:** original Yahoo and FRED/ALFRED snapshots are absent from the local checkout; exact 08:55 IST source availability, historical price-adjustment vintages, real-source future perturbation, point-in-time constituent membership, and full model replay remain open. The earlier scheduled-event availability issue was patched in a proposed add-on, but a successful rerun against the current checkout has not been demonstrated in the shared evidence. Do not describe it as closed.

## 1. Reproducible environment setup

From the repository root (`project2QuantFin`):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m pip install pytest
python -m pip check
python -m quantfin --help
```

If the repository already provides a supported lockfile, follow its documented install procedure instead. Do not append `pip freeze` blindly to `requirements.txt`; it can introduce duplicate/conflicting pins. Record the exact environment separately if desired:

```bash
python -m pip freeze > requirements-lock-local.txt
```

For Git LFS-backed artifacts, ensure actual files are present (not just pointer text):

```bash
git lfs install
git lfs pull
git rev-parse HEAD
```

`git lfs pull` may download large files. Run it only if required artifacts are missing.

## 2. Audit scripts and expected locations

The following scripts were developed during the audit. **They are not necessarily committed to the main repository.** Before using the commands, verify they exist in your checkout and commit them to a dedicated audit branch if necessary.

```text
scripts/audit_real_features.py
scripts/audit_cross_market_predictions.py
scripts/audit_final_slice.py
scripts/audit_training_provenance.py

tests/leakage/
audits/training_provenance/
```

Check availability:

```bash
ls scripts/audit_real_features.py scripts/audit_cross_market_predictions.py \
   scripts/audit_final_slice.py scripts/audit_training_provenance.py
find tests/leakage -maxdepth 1 -name 'test_*.py' -print
```

If a script is missing, obtain it from the audit branch or project handoff before running its command. Do not treat a missing script as a failed model validation.

## 3. Recommended demonstration sequence

### A. Run automated leakage and regression tests

```bash
python -m pytest tests/leakage -v -rx
python -m pytest tests -v -rx
```

**Interpretation:** `PASSED` means the asserted behavior passed; `XFAIL` is an unresolved/expected failing condition, **not** evidence that the leakage risk is fixed. Check the scheduled-event availability regression specifically and ensure the fix is installed before removing its `xfail` marker. The previously reported broader suite result was **22 passed, 1 xfailed**; a new checkout may differ.

### B. Inspect the main panel and feature dictionary

```bash
python - <<'PY'
from pathlib import Path
import pandas as pd
root = Path('data/processed/cross_market')
p = sorted(root.glob('cross_market_panel_*/panel.parquet'))[-1]
d = p.parent / 'feature_dictionary.csv'
panel = pd.read_parquet(p)
features = pd.read_csv(d)
print('Panel:', p)
print('Rows, columns:', panel.shape)
print('Dates, assets:', panel.decision_date.nunique(), panel.asset.nunique())
print('Date range:', panel.decision_date.min(), panel.decision_date.max())
print('Missing target rows:', panel.target_oc_return.isna().sum())
print('Dictionary rows:', len(features))
print('Families:\n', features.family.value_counts())
print('Fallbacks:\n', features.current_vintage_fallback.value_counts(dropna=False))
print('Feature ladder:\n', features.feature_sets.str.split('|').explode().value_counts())
PY
```

**Reproducibility caution:** `sorted(...)[-1]` selects the latest directory *by name*, which may change after new runs. For formal evaluation, pin the **exact** panel used by the frozen main study:

```text
data/processed/cross_market/cross_market_panel_20261030T044550Z_e8964cacce4208c3/panel.parquet
```

### C. Validate all 456 walk-forward checkpoints

```bash
python scripts/audit_training_provenance.py --runs \
  cm_screening_20261030T093727Z_0e77ef60dd73 \
  cm_confirmation_20261030T111633Z_8bb9c211fb41 \
  cm_final_test_20261030T115442Z_120878a67dbc
```

Expected reported summary (re-run to verify):

| Stage | Checkpoints | Passed | Failed |
|---|---:|---:|---:|
| Screening | 288 | 288 | 0 |
| Confirmation | 80 | 80 | 0 |
| Final test | 88 | 88 | 0 |
| **Total** | **456** | **456** | **0** |

The script writes `audits/training_provenance/training_provenance.csv` and `training_provenance_summary.csv` (confirm output paths against the local script's help/source). This test checks saved metadata against reconstructed panel session windows; it does not prove source release times or reproduce fitted weights.

### D. Inspect prediction integrity

```bash
python scripts/audit_cross_market_predictions.py
```

Previously reported file sizes: screening **178,560** rows; confirmation **49,100**; final test **18,120**; derived 2025 slice **9,960**. The audit checks unique `(decision_date, asset, config_id)` keys, finite predictions, and missing targets. These files contain multiple configurations; their row counts are **not** independent trading days.

### E. Verify the 2025 derived slice

```bash
python scripts/audit_final_slice.py
```

Previously reported: **0 unmatched rows**, exact equality of predictions, target and benchmark columns, and manifest flags `model_reselection_performed=False`, `refit_performed=False`. A matching manifest flag is an assertion by the pipeline, not an independent process audit.

### F. Verify freeze hash and model-selection identity

```bash
python - <<'PY'
from pathlib import Path
import json, hashlib
root = Path('artifacts/cross_market')
f = json.loads((root / 'freezes/cm_freeze_20261030T115423Z_7c6b1efba4dc.json').read_text())
c = root / 'runs' / f['confirmation_run_id'] / 'manifest.json'
actual = hashlib.sha256(c.read_bytes()).hexdigest()
print('Freeze ID:', f['freeze_id'])
print('Selected config:', f['selected_config_id'])
print('Selection metric:', f['selection_metric'])
print('Confirmation manifest SHA-256 match:', actual == f['confirmation_manifest_sha256'])
assert actual == f['confirmation_manifest_sha256']
PY
```

The selected model is `cm_elastic_net_329a4ccca456`, feature set `F4_full_us`. Confirmation net Sharpe recorded in the freeze is approximately **1.257** (confirmation, not final test). A hash match establishes byte consistency with the referenced manifest, not that the experiment was immune to human research iteration on final-test results.

### G. Review training-only preprocessing and as-of alignment

```bash
sed -n '178,275p' src/quantfin/cross_market/experiments.py
sed -n '295,390p' src/quantfin/cross_market/experiments.py
sed -n '80,175p' src/quantfin/cross_market/panel.py
```

Review that missingness/variance screening, winsorization, imputation, `SelectKBest`, scaling and model fitting all learn from `train` only. Confirm `merge_asof` uses `direction='backward'` and `allow_exact_matches=False`. This is a code inspection, not a point-in-time price-source reconstruction.

### H. Legacy SPY chronology (separate from cross-market)

```bash
python scripts/audit_real_features.py
```

Previously reported: 5,283 rows, 108 columns; 5,281 complete chronological observations and two legitimate unlabeled terminal rows on 2025-12-30/31, both in `final_test`. The script dynamically discovers a `features_*/features_and_labels.parquet` dataset; it does **not** audit the cross-market panel.

## 4. Raw snapshot reproducibility gap

The frozen cross-market panel manifest lists these original snapshot IDs:

| Group | Snapshot ID |
|---|---|
| India core | `yahoo_india_core_20261029T124839Z` |
| US limited tech | `yahoo_us_limited_tech_20261029T125019Z` |
| US context | `yahoo_us_context_20261029T125033Z` |
| Indian IT ADRs | `yahoo_indian_it_adrs_20261029T125050Z` |
| Global context | `yahoo_global_context_20261029T125100Z` |
| Nifty 50 PIT | `yahoo_nifty50_point_in_time_20261030T005526Z` |
| S&P 500 PIT | `yahoo_sp500_point_in_time_20261030T005819Z` |
| Nifty 500 PIT | `yahoo_nifty500_point_in_time_20261030T015703Z` |
| FRED/ALFRED | `fred_alfred_20261030T023950Z` |

Configured raw roots: `data/raw/cross_market/yahoo` and `data/raw/cross_market/fred_alfred`. The local checkout lacked both; `.gitignore` deliberately ignores `data/raw/*`. Git LFS contains extensive processed/model artifacts but does not, from the provided listing, establish raw snapshot availability. Request the **exact original snapshots and their manifests** from the project leader. Do not substitute a new Yahoo download when attempting to reproduce the frozen panel.

Useful commands:

```bash
git check-ignore -v data/raw/cross_market/yahoo/
git check-ignore -v data/raw/cross_market/fred_alfred/
git lfs ls-files | grep 'data/raw/cross_market' || true
python - <<'PY'
import json
from pathlib import Path
p = Path('data/processed/cross_market/cross_market_panel_20261030T044550Z_e8964cacce4208c3/manifest.json')
m = json.loads(p.read_text())
print('Snapshots:', json.dumps(m.get('snapshots'), indent=2))
print('Snapshot manifest references:', json.dumps(m.get('snapshot_manifests'), indent=2)[:8000])
PY
```

Once raw snapshots are restored, compare each snapshot manifest's hash with the saved panel's provenance before recomputing features. Keep raw files out of Git unless the team has approved storage and redistribution.

## 5. Remaining work and limitations

| Area | Current evidence | Next action |
|---|---|---|
| Date-level train/test chronology | 456/456 checkpoint audit | Preserve CSV evidence and source commit |
| Training-only feature selection | Verified from code | Optional model replay on a development checkpoint |
| Freeze integrity | Hash match and config consistency | Preserve freeze/manifest hashes |
| Current-vintage macro fallbacks | 60 confined to F5, selected model F4 | Verify feature dictionary and selected configuration on each run |
| Source availability by 08:55 IST | Date-level as-of code only | Recover raw snapshots and verify exchange closes/publication times |
| US DST / India and US holidays | Synthetic timing tests | Validate against actual source sessions |
| Corporate-action adjustment revisions | Unverified | Inspect original adjusted-price policy and sensitivity |
| Historical S&P 500/Nifty membership | Unverified | Audit membership files for historical validity |
| Scheduled-event announcement times | Earlier documented risk; fix not reverified | Run regression test on current checkout; require `known_at_utc` |
| Real-data future perturbation | Not run | Rebuild from immutable raw copy and compare earlier panel values |
| Final holdout research governance | Manifest references consistent | Document selection chronology; do not use holdout to tune models |

## 6. Evidence capture for professor/leader

Create a clean evidence directory and capture a deterministic log:

```bash
mkdir -p audits/evidence
{
  date -u
  git rev-parse HEAD
  python --version
  python -m pip check
  python -m pytest tests/leakage -v -rx
  python scripts/audit_training_provenance.py --runs \
    cm_screening_20261030T093727Z_0e77ef60dd73 \
    cm_confirmation_20261030T111633Z_8bb9c211fb41 \
    cm_final_test_20261030T115442Z_120878a67dbc
  python scripts/audit_cross_market_predictions.py
  python scripts/audit_final_slice.py
} > audits/evidence/feature_audit_run.log 2>&1
cat audits/evidence/feature_audit_run.log
```

**Caution:** A shell group continues after failed commands unless `set -e` is enabled. Check individual exit codes or run each command separately. For strict CI-style evidence capture use `set -e` inside the group and inspect the final log if it stops early.

Include the following with the final submission: this README, committed audit scripts/tests, generated audit CSVs/logs (subject to team Git policy), pinned source commit and configuration hashes, and a limitations paragraph. A professor without raw snapshots can reproduce saved-panel/checkpoint checks but **cannot** reproduce the complete source-to-panel build.

## 7. Report-ready statement

> We audited the US–India cross-market return-prediction pipeline for chronological training and feature-engineering leakage. Across 456 saved walk-forward checkpoints (288 screening, 80 confirmation, 88 final testing), the recorded training windows matched reconstructed rolling-session and one-session embargo rules with zero detected date-level violations. Code inspection showed training-only preprocessing, supervised feature selection, and strict backward date-level market alignment. The frozen final-test model was the same Elastic Net F4 configuration recorded at confirmation; its freeze referenced the correct confirmation manifest and the stored SHA-256 matched the file. The 60 identified current-vintage macro fallback features were confined to F5 and excluded from the selected F4 feature set. These findings support the chronological design but do not certify historical point-in-time availability of every source feature: original raw Yahoo/FRED snapshots, corporate-action vintages, historical constituent eligibility, and full real-data perturbation remain to be independently verified.

