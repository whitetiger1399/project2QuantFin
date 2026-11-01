# Quantitative Finance Project 2

This repository contains the single active research setup for Project2 Teams 16 in DSA5205. It forecasts same-session open-to-close returns for ten fixed current Nifty IT constituents at 08:55 IST and converts forecasts into signed stock positions after a cost hurdle.

The canonical study is the AI-capability cross-market experiment:

- Research configuration: `configs/cross_market_ai_capability_research.yaml`
- 2026 retrospective extension: `configs/cross_market_ai_capability_2026_extension.yaml`
- Sequential commands: `documents/markdown/AI_CAPABILITY_COMPLETE_RUNBOOK_2026-10-31.md`
- Improvement audit: `documents/markdown/MODEL_IMPROVEMENT_GAP_ANALYSIS_2026-10-31_164808_SGT.md`
- Report builder: `reports/build_report_ai_capability.py`
- Final report: `reports/Project2_Team16_Report.docx` and `.pdf`

Earlier SPY, generic cross-market, and AI-services experiments are retained as historical artifacts. They are not active model setups and must not be mixed with the canonical selection lineage.

## Setup

Python 3.10 or newer is required. Commands use project-relative paths and work on Apple Silicon, Intel macOS, and Windows.

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .
python -m quantfin --help
```

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .
python -m quantfin --help
```

Never commit API keys. Use environment variables and keep `.env` local.

## Fast verification

These checks do not train a model:

```bash
source .venv/bin/activate
export MPLCONFIGDIR="$PWD/artifacts/.matplotlib-cache"
mkdir -p "$MPLCONFIGDIR"
python -m unittest discover -s tests -v
python -m compileall -q src scripts reports
```

After a fresh dataset and model run, run both lineage verifiers documented in the current runbook. The final report must only be regenerated after they pass.

## Research protocol

- Target: each constituent's NSE open-to-close simple return.
- Decision time: 08:55 Asia/Kolkata.
- Information: only observations available before the decision cutoff.
- Feature ladder: own history, Nifty IT peers, U.S. IT services, Nifty 50, S&P 500 aggregates and constituents, dated AI context, then full macro/global context.
- Validation: chronological screening and confirmation with fold-local cleaning, scaling, selection and PCA.
- Strategy: up to three long and three short positions, maximum gross exposure 1, and modeled 15-bps round-trip friction.
- Evidence status: 2025 is a historical protocol replication; January–September 2026 is a retrospective no-reselection extension with a separate pre-2026 fit.
- Epoch AI scores are current-vintage explanatory evidence and are never backfilled as historical tradable features.

The fixed target cohort is conditioned on current Nifty IT membership and is not a reconstruction of historical index membership. Public price opens and closes are research fill proxies, not exchange-certified executions.

## Data and artifacts

Raw vendor downloads remain local under `data/raw/`. Processed panels and model artifacts are immutable, timestamped, content-hashed, and tracked through manifests. A new source, feature rule, target, cost convention, or selection policy creates a new dataset or run identity.

Do not delete completed evidence runs simply because a later experiment supersedes them. Report QA renders and Python caches are reproducible and ignored.

## Report

The report builder reads pinned immutable evidence and does not train models:

```bash
python reports/build_report_ai_capability.py
```

The builder defaults to the completed canonical identifiers and accepts verified
rerun identifiers through `REPORT_*` environment variables. The current runbook
contains the exact exports. Do not edit source pins or replace the PDF until the
dataset, model-lineage, 2026-extension, and contract audits pass; then render and
inspect every page.

## Repository structure

- `src/quantfin/`: reusable data, timing, modeling, evaluation, and tracking code.
- `scripts/`: executable ingestion, analysis, model, freeze, verification, and audit stages.
- `configs/`: versioned research contracts and bounded experiment grids.
- `data/`: raw-local, external-reference, and immutable processed data.
- `artifacts/`: completed analyses, model runs, freezes, audits, and plots.
- `documents/markdown/`: assignment, methodology, runbook, design guide, and dated review documents.
- `reports/`: one active report builder and final submission artifacts.
- `tests/`: deterministic exchange-clock and accounting checks.

## Submission safeguards

Before submission, confirm that the report is 15–25 pages, includes the full alphabetical roster and contribution note, uses the required filename, and matches verified run identifiers. Preserve the AI-use declaration and NUS academic-integrity references. The accompanying video must demonstrate the end-to-end time-respecting pipeline and explain what worked, what did not, and why.
