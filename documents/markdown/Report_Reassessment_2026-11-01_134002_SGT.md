# Quant 2 Fin — Updated report and model assessment

Review baseline: **1 November 2026, 13:40:02 SGT**. Previous assessment: [31 October gap analysis](Model_Improvement_Plan_Gap_Analysis_2026-10-31_171449_SGT.md).

## Updated verdict

**Overall: 80/100, up from 72/100. Publication readiness: 66/100, up from 58/100.**

The report is substantially more rigorous and informative. It now clearly acknowledges historical researcher exposure, documents the trading contract, separates segment results, explains cost erosion, and distinguishes association from causality. New hypothesis analysis and dependence-aware diagnostics strengthen the underlying work.

It remains an exploratory retrospective study with unresolved data-vintage and incremental-value questions. Presentation has improved, but the current PDF has a broken contents page and the saved publication verification does not cover the current files. These prevent calling the submission finished.

Scores are reviewer judgments, not official marks. The same overall weights as the first review are retained. The numerical equivalent is **28.0/35**, but the assignment's 35 points cover the submission package, including a video that was not assessed here; this is not a predicted instructor grade.

## 1. Comparable scorecard

| Area | Maximum | Previous | Current | Assessment |
|---|---:|---:|---:|---|
| Research question and economic logic | 10 | 8 | 9 | Explicit hypotheses and careful distinction between association, trading value and causality. |
| Data provenance, timing and leakage controls | 15 | 10 | 11 | Retrospective status is now transparent; current-vintage inputs remain unresolved. |
| Feature engineering and preprocessing | 10 | 8 | 8 | Relevant existing design; still lacks concise formulas, feature counts and empirical feature ablations. |
| Models, validation and selection | 15 | 11 | 12 | Actual window/embargo/seed and revised candidate outcomes are clearer; research search history and exact selection details need consolidation. |
| Trading, costs and benchmarks | 10 | 7 | 8 | Precise hurdle, weights and costs; ETF proxy identity confirmed in code; available matched comparisons underreported. |
| Evaluation and statistical inference | 15 | 10 | 12 | Segment forecast/risk metrics, Holm correction and date-based inference; important completed diagnostics remain outside the narrative. |
| EDA, figures and architecture | 10 | 7 | 8 | Much clearer architecture, matrix comparison, cost plot and regime distributions; some repetitive EDA remains. |
| Structure and interpretation | 10 | 7 | 8 | Better abstract and conclusions; stale statements, split tables and page-zero contents need correction. |
| Reproducibility and submission readiness | 5 | 4 | 4 | Strong evidence IDs and figure provenance; stale verification, incomplete contribution note and limited embedded run commands. |
| **Total** | **100** | **72** | **80** | **Meaningful improvement; not yet final.** |

The separate publication score reflects research validity and completeness, not whether the document resembles an IEEE template. Additional prospective evidence cannot be replaced by attractive figures.

## 2. What was reviewed

- Full current DOCX text/tables and the **21-page current PDF**, with all pages viewed in contact sheets and the architecture page inspected separately. The page count meets the required 15–25 pages.
- Current report builder, publication sections, figure-generation code, hypothesis protocol and figure-review notes.
- Current screening/confirmation freeze, final and extension ledgers/leaderboards, forecast inference, feature-importance artifacts and strategy-comparison summaries.
- Publication verification hashes compared with the current DOCX and PDF.
- Selected metrics recomputed directly from saved ledgers. No model was retrained and no report was changed.

Visual observations refer to the supplied PDF; this review did not independently re-render the DOCX. Company disclosure numbers and external links were not independently reverified during this reassessment. Full verification suites and the video were not rerun/reviewed.

## 3. The model changed: use the new results

The selected specification changed from depth 8, `cm_extra_trees_05a83581b70b`, to depth 6, **`cm_extra_trees_cd9235695e6b`**. Current screening has 25 configurations, compared with 28 previously. The new freeze is dated 1 November 2026. This is a revised historical research iteration, not just a reformatted report.

| Metric | 2025 replication | Jan–Sep 2026 extension |
|---|---:|---:|
| Sessions | 249 | 185 |
| Gross cumulative return | +5.16% | +26.95% |
| Net cumulative return | **−4.04%** | **+15.01%** |
| Annualized net volatility | 12.86% | 13.74% |
| Net Sharpe | −0.260 | 1.456 |
| R² versus asset-mean forecast | −0.748% | +1.411% |
| Mean daily cross-sectional IC | −0.0437 | +0.0819 |
| Saved model-run 95% bootstrap Sharpe interval | [−1.883, 1.506] | [−1.577, 3.865] |

Combined cumulative net return is **10.37%**, rather than the previous model's 32.10%. The new confirmation Sharpe is approximately 1.546, but subsequent 2025 results remain weak. The score rises because the report and methods improve, not because historical gains increase.

Both displayed Sharpe intervals include zero. The 2026 alpha HAC p-value is approximately **0.303**. Positive 2026 realized performance therefore does not establish repeatable alpha. The report's new qualified conclusion is appropriate.

The intervals above come from the model-run inference files using 1,000 repetitions. The separate H5 analysis describes 2,000 draws; label the source and bootstrap settings whenever displaying an interval, rather than silently interchanging analyses.

## 4. Improvements that deserve credit

1. **Historical evaluation is disclosed.** The contents-page callout and split table explicitly acknowledge prior inspection of 2025 and 2026. The abstract no longer implies an untouched holdout.
2. **Trading is reproducible from the prose.** The report gives 7.5 bps per side, 15 bps effective hurdle, up to three names per side, approximately one-third stock cap, gross exposure cap and intraday liquidation.
3. **Costs are a result, not a footnote.** The 2025 gross/net comparison now distinguishes compounded wealth loss from the 9.15% arithmetic cost sum. Fixed-holdings cost stress is the correct complement to changing-policy sensitivity.
4. **Forecast quality is visible.** R², IC and volatility appear next to segment returns. Negative 2025 results are retained.
5. **Hypothesis interpretation is stronger.** Date-level regressions, HAC uncertainty, Holm correction, sparse-sample abstention for H4, and explicit retrospective status are substantial gains. The report correctly avoids treating significant versus insignificant annual estimates as a significant difference between years.
6. **Actual inference code improved.** Saved forecast inference now uses circular date-block bootstrap and majority-sign comparison. Drawdown includes initial wealth and Sortino uses squared downside deviations. These close several implementation concerns from the first review.
7. **Architecture and figures improved.** Figure 1 now has a recognizable availability gate, forecast-to-position logic and cost ledger. The lower-triangle peer heatmap removes duplicate cells, family results use a matrix, and regime plots show individual observations.
8. **Benchmarks are better identified.** Panel construction maps the Nifty IT and Nifty 50 benchmark columns to `ITBEES.NS` and `NIFTYBEES.NS`. The earlier index-investability concern should not be repeated as if no ETF proxy exists. Put the actual tickers in the report too.

## 5. Submission fixes needed now

### P0-A — Contents page is broken

Every one of the 18 contents entries in the current PDF displays page **0**. This is visible in both PDF text and the rendered page image, not merely an XML field-cache issue.

**Action:** refresh/materialize the table of contents, export again, and check every destination against the final PDF. Do not rely on an older verification result.

### P0-B — Publication verification belongs to an older release

`reports/report_publication_verification.json` records **20 pages** and an earlier verification timestamp. The current PDF has **21 pages**. Both recorded DOCX and PDF hashes fail to match the present files.

**Action:** rerun publication verification after all edits; record actual hashes and page count, and inspect the final PDF. This is a publication-QA provenance mismatch, not proof that the underlying model-run checks failed.

### P0-C — Remove stale numerical and methodological wording

| Location | Current issue | Required correction |
|---|---|---|
| Section 8.1 claim table | “2025 is flat” | State that the current model loses 4.04% net. |
| Figure 16 caption | Says 2025 approaches zero at the recorded 15 bps cost | At 15 bps, the current model is approximately −4.04%; describe the actual crossing or omit the claim. |
| Section 6 segment table | Still says “2025 frozen final” / “2026 forward extension” | Use historical replication / retrospective extension consistently with the abstract. |
| Figure 18 and adjacent discussion | Says the artifacts use a single stock-day permutation | Current run artifacts contain repeated `oos_date_block_group_permutation_mse_increase` rows; reconcile the embedded plot with the current source and describe the actual method. |
| Supporting figure-review Markdown | Retains previous gross/net results and zero recorded 2026 events | Archive explicitly as an earlier review or update it to the current evidence. |

For Figure 18, the current implementation shuffles **whole dates**, retaining the matching asset, across repetitions. This preserves within-day cross-sectional relationships but does not preserve runs of consecutive dates. It should not be described as a multi-session block permutation unless that method is actually implemented. The plot builder averages the importance rows; it still does not display their variability.

### P0-D — Contribution statement does not state contributions

The heading exists, but the paragraph only repeats four names. The requirement asks for a contribution note.

**Action:** have the team supply truthful roles: data, modeling, evaluation, literature, report and video contributions as applicable. Do not invent allocations.

### P0-E — Complete the methods/reproduction contract

The report includes figure/report-building commands, but not a compact end-to-end reproduction sequence or resolved software versions. The current selection metric is net Sharpe; include promotion logic, tie-breakers, candidate count, training method/solver and a pointer to the exact realized grid.

**Action:** add a short appendix with exact data/panel → screening → confirmation → freeze → evaluation → verification → report commands, or a precise versioned runbook reference with expected outputs. Distinguish code that exists from artifacts actually produced.

## 6. Most important remaining research gap: use the comparisons already computed

The report says timing-versus-selection evidence awaits matched analysis. Current strategy-comparison artifacts already contain useful first-pass evidence:

| Strategy | 2025 Sharpe | 2026 Sharpe |
|---|---:|---:|
| Selected signed stock portfolio | −0.260 | 1.456 |
| Cohort-mean signed timing | −0.427 | **2.203** |
| U.S.-services direction, equal weight | −0.906 | 2.021 |
| Always-short cohort | −0.763 | −0.139 |
| Stock-relative residual strategy | Undefined: no trades | Undefined: no trades |

The selected portfolio and cohort-mean comparator have matching reported active-session counts and nearly identical mean turnover in these summaries: 61 active dates in 2025 and 66 in 2026. They are useful timing-versus-selection diagnostics. A full date-by-date exposure match and paired uncertainty calculation should still precede a strong incremental-value claim.

**Interpretation:** the selected portfolio has the better point-estimate Sharpe in 2025, but the simpler cohort timing comparator has the better point estimate in 2026. Positive 2026 IC does not automatically translate into superior portfolio selection. Also, always shorting the cohort loses after costs, so the result is not explained simply by holding a permanent short.

**Action:** add this compact table, paired daily net-return differences, and dependence-aware intervals. Keep these as diagnostic comparisons; do not replace the selected model with the highest 2026 performer after inspecting that year.

## 7. Validity gaps still open

### Current-vintage sensitivity

The new processed feature dictionary still contains **60 flagged fallback features**. Disclosure is improved, but disclosure does not establish robustness. Confirm which columns enter each fit and compare a strictly point-in-time variant with identical model parameters.

A `gap_diagnostics` profile exists, but its reference and strict-vintage configurations still specify **depth 8**, whereas the new canonical model has **depth 6**. Therefore those settings would test the previous specification, not isolate vintage sensitivity for the current model. Update both paired configurations consistently before running a current-model diagnostic. No completed strict-vintage result was located in the reviewed November 1 leaderboard files.

### Feature-family incremental value

Retain the Ridge ladder, but it does not establish how the chosen Extra Trees model benefits from U.S. services or AI inputs. Add current-depth selected-family ablations with fixed training/trading rules. Record results as exploratory on inspected data.

### Forecast calibration and direction

The saved 2025 date-block diagnostic gives directional accuracy about **54.18%**, compared with **53.69%** for the descriptive majority-sign baseline. The 95% interval for incremental accuracy is approximately **[−2.29, +3.70] percentage points**. This valuable negative/uncertain finding should be shown rather than leaving the reader with only generic metric names.

Add calibration bins against the ±15 bps trading thresholds, with date-based uncertainty. Estimate any recalibration on forward development folds; do not tune thresholds to improve the already inspected 2026 result.

### Research search history

The new depth, expanded Elastic Net search, RFF omission and refreshed event calendar are reasonable exploratory changes. Report their chronology and the fact that they follow earlier outcome inspection. A bounded current grid does not capture the full project-wide search. The current admission of retrospective refinement is a major improvement and should remain.

### AI-event scope and inferential consistency

The 2026 negative event association is interesting, but a raw event/non-event test, shuffled-label test and controlled Holm-adjusted regression answer different questions. Label outcome horizon, sample, controls and multiplicity for each; do not present their p-values as interchangeable confirmations.

H4 is not estimable under the final sample rule, while Section 4.3 still lists older small-sample capability estimates. Label those as legacy descriptive sensitivities, distinct from the final protocol. A 30-event minimum is an estimation rule, not a guarantee of power or causality.

## 8. Further figure and structure refinements

- Keep the new architecture. Add a compact validation timeline distinguishing model fitting cutoffs from the November research freeze; state that vintage checks retain known exceptions.
- Keep the new cost decomposition, family matrix and observation-level regime plots.
- Replace one of the two market-path figures with target-return tails, missingness/freshness, calibration, or U.S.-return association with **overnight versus intraday** outcomes. The latter directly tests whether information is incorporated before the modeled trade begins.
- Add a drawdown panel to the main wealth chart. Returns alone obscure the cost of waiting for the favorable 2026 segment.
- Present repeated importance variability and ensure the caption matches the current artifact generation method.
- Keep short tables together. The source table splits across pages 4–5, the feature ladder across 7–8, and the stage table across 10–11. Repeated headers help, but these short tables would read better unbroken.
- Number substantive tables and refer to them explicitly. Trim duplicated interpretation between captions and immediately adjacent paragraphs.
- Keep H6 adaptation discussion proportionate. It adds useful context and counterevidence, but it is not validation of the trading model or a causal productivity analysis.

## 9. Recommended order of work

1. **Correct the release:** contents, stale statements, contribution note, exact benchmark labels, refreshed verification hashes and page count.
2. **Surface completed evidence:** timing-only comparisons, paired uncertainty, calibration/majority-sign diagnostics, actual importance method.
3. **Run narrowly scoped missing diagnostics:** depth-6 strict-vintage comparison and selected-family information ablations under fixed settings.
4. **Improve information density:** replace one price plot, add drawdown and uncertainty, improve short-table pagination.
5. **Preserve research integrity:** retain historical labels and freeze a future evaluation protocol before collecting genuinely new outcomes.

After the first two steps, an **84–86/100 report-quality target** is reasonable, conditional on accurate execution. A 90+ assessment would require stronger resolution of data-vintage, incremental-value and reproducibility questions; a favorable 2026 return alone is insufficient. Publication readiness needs additional independent evidence, not just these editorial fixes.

## 10. Evidence addresses

- Report: `reports/Project2_Team16_Report.docx` and `.pdf`.
- Current selected model: `cm_extra_trees_cd9235695e6b`.
- Dataset: `data/processed/cross_market_ai_capability/ai_capability_panel_20261101T012801Z_ff277b55597d727a`.
- Freeze: `artifacts/cross_market_ai_capability/freezes/cm_ai_capability_freeze_20261101T025756Z_b80ca3883e16.json`.
- 2025 run: `artifacts/cross_market_ai_capability/runs/cm_ai_capability_final_test_20261101T025817Z_30ebf00d8090`.
- 2026 run: `artifacts/cross_market_ai_capability_2026/runs/cm_ai_capability_2026_forward_20261101T030225Z_6a066bcfcc82`.
- 2025 model evidence: `artifacts/cross_market_ai_capability/analysis/model_evidence_final_test_20261101T030544Z_a4d9077ee46e`.
- 2025 strategy comparison: `artifacts/cross_market_ai_capability/analysis/ai_strategy_comparison_20261101T030717Z_591c864e3aba`.
- 2026 strategy comparison: `artifacts/cross_market_ai_capability_2026/analysis/ai_strategy_comparison_20261101T030726Z_9660a3a84bc3`.
- Hypothesis analysis: `artifacts/research_hypotheses/hypotheses_20261101T030841Z_d494c2f238ca64a6`.
- Stale publication-QA record: `reports/report_publication_verification.json`.

This reassessment preserves the earlier review as a baseline. No report, model, configuration or original result was modified.
