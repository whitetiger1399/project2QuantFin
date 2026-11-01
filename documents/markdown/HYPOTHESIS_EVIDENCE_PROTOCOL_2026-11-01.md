# Six hypotheses: cross-market prediction, AI disruption and company adaptation

Protocol written 1 November 2026, after inspection of the earlier model results.
Status: exploratory extension; scripts implemented, empirical tests awaiting user execution.

## Purpose and integrity

Project2.md explicitly grades data quality, temporal alignment, leakage control, fair benchmarks, out-of-sample performance after costs, and interpretation. Negative performance is compatible with a successful research project. The aim here is to explain what the evidence supports, not to manufacture a favourable outcome.

Earlier results were +12.26% annualized net return / 1.22 Sharpe in 2021–2022 for F2 Extra Trees, then -11.36% / -0.98 in 2023–2024. This establishes instability of this tested strategy, not that AI caused a regime change. F2 does not contain AI-release features. Selection from one confirmation candidate is not independent evidence of model superiority. The previously inspected 2025–2026 results are historical evaluation, not a newly untouched holdout. Existing freezes are retained for provenance, not as proof of profitability.

## Hypothesis register

| ID | Assumption and economic mechanism | Expected result / competing explanation | Test and evidence | Current verdict before new tests |
|---|---|---|---|---|
| H1 | U.S. services returns convey common demand information to Indian IT firms. | Positive conditional association; it may weaken or reverse with changing demand, FX and market conditions. | Daily cohort open-to-close return regressed on pre-open observable U.S. services return, own-cohort lag and Nifty50 lag. Annual estimates and a fixed 2025 interaction. | Stable tradable advantage not supported by F2 confirmation; association still requires separate testing. |
| H2 | Frontier releases threaten labour-intensive IT-services revenue. | Negative Indian intraday event association; alternatively the response is neutral/positive or already incorporated at the open. | Release-session indicator with lagged Indian controls; annual and pooled post-2022 estimates, event counts and HAC intervals. | Prior event study was not decisive. Automatic event shorting lost money in the inspected 2025 experiment. |
| H3 | Adaptation makes later release reactions less negative. | Positive later-minus-earlier event interaction, conditional on an earlier negative effect. Alternatively disruption fears persist or increase. | Fixed break 2025-01-01; 2023–2024 versus 2025–September 2026. Estimate the interaction and each period effect jointly. | Unresolved. A significant result in one period and nonsignificant result in another is not evidence of a significant difference. |
| H4 | A larger frontier capability improvement produces a more negative stock response. | Negative coefficient on incremental capability beyond the prior frontier; competing hypothesis: integration opportunity offsets displacement. | Epoch score increment, calendar time and lagged Indian controls; one observation per mapped event date; HC3 inference. | Exploratory only. Retrospective benchmark scoring is not a point-in-time trading feature; insufficient samples must remain inconclusive. |
| H5 | The frozen strategy has positive net returns and beats the benchmark consistently. | Positive mean net return and net-minus-Nifty50 mean return; economic and statistical uncertainty both matter. | Existing ledgers only; annual and full-period returns, HAC means, 20-session circular block bootstrap Sharpe interval, 2,000 draws. | New F2 candidate failed confirmation. Canonical run is retained rather than retroactively replaced. |
| H6 | IT firms adapt commercially and change workforce intensity rather than uniformly disappear. | Company-specific employment and profitability paths, AI services/bookings, upskilling and client retention. | Verified quarterly workforce totals; absolute, QoQ, six-month and YoY percentage changes where matching quarters exist; earnings documents and caveats. | Evidence of commercial adaptation exists, but heterogeneous headcounts and margins do not establish AI-caused productivity gains. |

## Statistical specification and decision rules

- Unit of inference is the Indian trading date, using a daily equal-weight cohort outcome. Ten companies on one event date are not ten independent AI shocks.
- Regression uncertainty: Newey–West/HAC, five lags for daily data. H4 uses HC3 on irregular event dates, with the limitation that closely spaced announcements may still be dependent.
- Holm adjustment is applied jointly to every reported regression p-value in the run, including annual and benchmark comparisons. The correction covers this declared batch, not all prior project searches. Confidence intervals shown on plots are pointwise.
- A regression needs at least 30 complete dates and five observations per estimated coefficient. Event contrasts require at least eight event and eight non-event dates. H3 requires eight event dates in each era. These are minimum estimation checks, not guarantees of power.
- Fixed break and sample windows must not be moved to improve significance. H3 support requires negative earlier response plus positive later-minus-earlier interaction; a positive interaction alone is insufficient. The later effect may be uncertain without proving disappearance.
- Constant or rank-deficient predictors and sparse events produce explicit `insufficient_*` / `unidentified_design` output. Missing capability values remain missing.
- H4 compares each dated model with the best scored frontier strictly before that release date. Same-day releases are grouped; the first scored frontier has no change observation. Retrospective scoring, incomplete catalog coverage and date-only timestamps limit interpretation.
- For H5 a zero-cash-return Sharpe convention is labelled explicitly. Buy-and-hold includes overnight exposure; differences from intraday strategy returns are investor comparisons, not matched-exposure attribution.
- No cutoffs, models, long/short rules or costs are optimized using these outputs. H5 comparisons for multiple runs do not create new untouched tests.
- Quarterly headcount is a reported population total. A change of 1% or 5% is economically interpretable but does not call for a t-test on individual employees. Net changes include hiring, exits, acquisitions and reclassifications, and do not equal layoffs.

## Quarterly evidence collected

The JSON source register contains exact workforce totals and source URLs for TCS, Infosys and Wipro. March–September 2026 is a fixed recent six-month window, selected for all companies before inspecting the new hypothesis regressions.

| Company | March 2026 | June 2026 | September 2026 | March–September change |
|---|---:|---:|---:|---:|
| TCS | 584,519 | Not transcribed | 598,056 | +2.32% |
| Infosys | 328,594 | 328,062 | 332,542 | +1.20% |
| Wipro | 242,156 | 243,044 | 236,328 | -2.41% |

TCS's missing June observation must not turn its six-month change into a QoQ change. Wipro's June–September change is -2.76%; Infosys's is +1.37%. These show heterogeneity. They do not justify selecting whichever company/window favours a universal displacement story.

September reports published in October 2026 are available for today's retrospective discussion, but were unavailable for September trading decisions. The register is deliberately excluded from predictive features. TCS headline margins exclude specified one-offs; Wipro reports an IT-services segment margin; cross-company margin levels are not directly interchangeable. Increasing revenue per employee would also require consistent average headcount, currency, segment boundaries and acquisition adjustments, not just quarter-end headcount.

Primary sources:

- [TCS March 2026 results](https://www.tcs.com/who-we-are/newsroom/press-release/tcs-financial-results-q4-fy-2026)
- [TCS September 2026 results](https://www.tcs.com/who-we-are/newsroom/press-release/tcs-financial-results-q2-fy-2027)
- [Infosys March 2026 fact sheet](https://www.infosys.com/investors/reports-filings/quarterly-results/2025-2026/q4/documents/fact-sheet.pdf)
- [Infosys September 2026 fact sheet](https://www.infosys.com/investors/reports-filings/quarterly-results/2026-2027/q2/documents/fact-sheet.pdf)
- [Wipro March 2026 data sheet](https://www.wipro.com/content/dam/nexus/en/investor/quarterly-results/2025-2026/q4fy26/datasheet-q4fy26.pdf)
- [Wipro June 2026 data sheet](https://www.wipro.com/content/dam/nexus/en/investor/quarterly-results/2026-2027/q1fy27/datasheet-q1fy27.pdf)
- [Wipro September 2026 SEC highlights](https://www.sec.gov/Archives/edgar/data/1123799/000119312526426841/d188224dex995.htm)

Additional context: the JSON register includes Accenture AI business disclosures, Infosys Topaz, the Bank of England/FCA oversight survey, Klarna's customer-support reversal and Reuters on the February 2026 IT selloff. Management statements document company positioning; they do not independently establish investor sentiment or causal return effects. The counterevidence is retained alongside the adaptation examples.

## Outputs and report use

`hypothesis_tests.csv`: coefficients, sample sizes, pointwise intervals, raw and Holm-adjusted p-values and cautious evidence labels.

`portfolio_periods.csv`: existing strategies' annual/full-period net performance and full-period block-bootstrap Sharpe intervals.

`company_headcount_changes.csv`: source-linked workforce totals and changes using exact matching quarters. `event_coverage_by_year.csv`: effective event counts. `capability_event_dates.csv`: available retrospective scores and outcomes. `interpretation.md`: source list and limitations.

Three compact figures: H1 annual association intervals, H2 annual event-effect intervals, H6 company workforce trajectories. Tables provide additional information without adding redundant figures. Report each hypothesis's proposed mechanism, estimate, interval, multiplicity-adjusted evidence and limitations. A small p-value does not prove the proposed mechanism.

Unimplemented extension requiring additional verified outcomes: split stock close-to-close reactions into overnight gap and same-day intraday reaction with corporate-action-consistent prices. Existing `own__gap_return` is lagged input, not the current session outcome; it must not be substituted. Full causal adaptation tests would require longer quarterly firm panels, dated adoption measures, credible controls and earnings/announcement confounder flags. These are future work rather than implied completed tests.

## Sequential terminal commands

No training or model reselection is needed. The extension dataset already contains historical dates through September 2026, so do not also pass the overlapping 2025 panel.

```bash
cd /Users/whitetiger/Desktop/WhiteTiger/17_projects/24_Project2_QuantFin/project2QuantFin
source .venv/bin/activate

export HYP_PANEL=data/processed/cross_market_ai_capability_2026/ai_capability_2026_panel_20261031T072834Z_950e4bb969ac963e
export HYP_EPOCH=artifacts/cross_market_ai_capability/analysis/epoch_capability_analysis_20261031T063613Z_f3595944da18/epoch_event_capability_returns.csv
export HYP_SCREEN=artifacts/cross_market_ai_capability/runs/cm_ai_capability_screening_20261031T131402Z_b2cf65577643
export HYP_CONFIRM=artifacts/cross_market_ai_capability/runs/cm_ai_capability_confirmation_20261101T001942Z_ebff5b985708

# 1. Preview the exact inputs and content hash; no output artifacts written.
python scripts/analyze_research_hypotheses.py \
  --dataset "$HYP_PANEL" --epoch-events "$HYP_EPOCH" \
  --run "$HYP_SCREEN" --run "$HYP_CONFIRM"

# 2. Run the descriptive/inference extension (no retraining).
python scripts/analyze_research_hypotheses.py \
  --dataset "$HYP_PANEL" --epoch-events "$HYP_EPOCH" \
  --run "$HYP_SCREEN" --run "$HYP_CONFIRM" --execute
```

Record the `analysis_id` and `directory` printed by step 2. Inspect `hypothesis_tests.csv`, `portfolio_periods.csv`, `company_headcount_changes.csv`, `event_coverage_by_year.csv` and the three figures there. The old Epoch export may not cover 2026 releases: H4 reports only observed mapped dates and must not be described as complete 2026 evidence.

If interrupted, repeat the identical step-2 command with `--resume-analysis-id` followed by its printed ID. Input/code/settings hashes must match. Completed portfolio bootstrap evidence is reused from a hash-verified checkpoint; other inexpensive phases safely recompute in that analysis directory. No original model artifacts are overwritten. No runtime guarantee is made; bootstrap progress reports elapsed time and ETA.
