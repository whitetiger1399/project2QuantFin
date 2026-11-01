# Agent action plan — Project 2 report, evidence and model improvement

**Audit baseline:** 1 November 2026, **13:45:13 SGT / UTC+08:00**.  
**Purpose:** actionable gap analysis against `documents/markdown/Project2.md`, with exact report/source locations, verified facts, implementation instructions, commands and closure criteria.  
**Reviewed release:** current `reports/Project2_Team16_Report.docx` and `.pdf`; PDF has **21 pages**.  
**Repository HEAD at audit:** `9dc39aff5a503a5bd308c243634bac48381e7964`.  
**Current assessment:** **80/100 overall; 66/100 publication readiness**, unchanged from the immediately preceding reassessment. These are reviewer assessments, not course marks.  
**Work performed here:** read-only research/report audit plus creation of this action plan and audit evidence. No report rewrite, model training, model reselection or historical-artifact modification.

## 0. Instructions for the implementing agent

Implement this plan in dependency order. Fix factual/reporting errors first, expose completed evidence second, and run narrowly defined missing experiments third. The objective is **verifiable conclusions and better understanding**, not a guaranteed increase in historical Sharpe.

1. Treat the current depth-6 model as the canonical baseline. Preserve its runs, freeze, predictions and ledgers unchanged.
2. Do not replace 2025/2026 results with more favorable variants selected after inspecting those periods. New variants are exploratory and get new IDs and a recorded research chronology.
3. Read the named source before editing. Report page numbers below describe the current PDF; locate future versions by heading, figure number and quoted phrase.
4. Fix generators, then regenerate. A manual DOCX-only correction will otherwise disappear on the next build.
5. Do not overwrite immutable manifests to make checks pass. A changed input produces a new analysis/release identity; an old valid run remains valid under its original inputs.
6. Mark each action `open`, `implemented`, `verified`, or `blocked`, with evidence paths and actual commands. An action is closed only when its acceptance criterion is satisfied.
7. Ask the authors for actual contribution roles when needed; do not fabricate them. Do not describe a video or external citation as checked unless checked.
8. Distinguish **existing commands** from **proposed interfaces requiring implementation** in Section 7. Do not run a proposed command before its script exists.

### Severity and work classes

- **P0:** accuracy, reproducibility or submission defect; close before release.
- **P1:** important analysis or evidence gap; address before stronger research claims.
- **P2:** optional extension, not necessary for course compliance.
- **R:** report/build correction, no model fitting.
- **A:** analysis of existing predictions/ledgers, no model fitting.
- **M:** new fitting experiment required; new immutable outputs.

## 1. Audit evidence: what is correct and what fails

Evidence directory: [`artifacts/report_reviews/2026-11-01_134513_SGT`](../../artifacts/report_reviews/2026-11-01_134513_SGT).

| Check executed during this review | Result | Evidence |
|---|---|---|
| Canonical capability pipeline verifier | **201 passed, 0 failed** | [pipeline_verification.json](../../artifacts/report_reviews/2026-11-01_134513_SGT/pipeline_verification.json) |
| Frozen 2026 extension verifier | **28 passed, 0 failed** | [extension_verification.json](../../artifacts/report_reviews/2026-11-01_134513_SGT/extension_verification.json) |
| Inspected dataset/run/analysis/figure manifest file checks | All inspected checks passed | [release_audit.json](../../artifacts/report_reviews/2026-11-01_134513_SGT/release_audit.json) |
| Published DOCX against publication-QA hash | **Mismatch** | Same audit JSON |
| Published PDF against publication-QA hash | **Mismatch** | Same audit JSON |
| Publication-QA page count | Recorded 20; current **21** | Same audit JSON |
| Contents page | All **18** entries point to **0** | PDF page 2; text retained in audit JSON |
| Selected results recomputed from ledgers | Reconciled | [verified_metrics.json](../../artifacts/report_reviews/2026-11-01_134513_SGT/verified_metrics.json) |

The broken publication-QA record is **not evidence that the model ledgers are corrupt**. The figure pack's currently recorded input/output hashes also matched when checked; its main weakness is incomplete semantic lineage/build guarantees, not a demonstrated current hash mismatch.

Current full-file SHA-256 values:

```text
DOCX actual: 854695f7ee0ed436b0bf91a0f9467cacb21f140db758579b590d7d7a5ee32866
DOCX in old QA: 317db35b06e9cc59af5f100335dbdfdf3e45d3463e8853bae4227520d1df6402
PDF actual: 6ff43414a676c1e2dfc5941a5723922f380bd2ffb5091e1861db33b2b86e8306
PDF in old QA: 19d94b4628f976ddd876a4c3a86e7e62019af5309acb043af767791f29f9d8b5
```

Do not update the old QA hashes alone and call the document verified. Repair, render, inspect, validate and then generate a new QA record.

### Current metric reference — use these values, not the October model's values

Selected configuration: **`cm_extra_trees_cd9235695e6b`**, Extra Trees, 250 trees, maximum depth **6**, minimum leaf 40, feature fraction 0.5, F7 full context.

| Quantity | 2025 replication | Jan–Sep 2026 extension |
|---|---:|---:|
| Sessions | 249 | 185 |
| Gross cumulative return | +5.15688158% | +26.94850548% |
| Net cumulative return | **−4.03842270%** | **+15.01411638%** |
| Arithmetic sum of ledger trading costs | 9.15000000% | 9.90000000% |
| Net Sharpe | −0.259955 | 1.455718 |
| Annualized net volatility | 12.864476% | 13.738307% |
| R² versus asset mean | −0.747603% | +1.411364% |
| Mean daily cross-sectional IC | −0.043716 | +0.081876 |
| HAC alpha p-value | 0.887401 | 0.302776 |
| Model-run 95% Sharpe bootstrap interval | [−1.882878, 1.506301] | [−1.577016, 3.864731] |
| Fixed-holdings break-even round-trip cost, newly recomputed | **8.2454 bps** | **36.2149 bps** |

Combined net cumulative return is **10.36936020%**. The bootstrap intervals above use the model-run 1,000-draw procedure; H5 separately uses 2,000 draws. These are distinct inference artifacts, not necessarily identical intervals.

Break-even cost solves `prod(1 + gross_return - turnover * round_trip_bps / 20000) - 1 = 0` on each saved selected-model ledger. It is a counterfactual holding positions fixed, not a tradable fee choice or optimized strategy. Arithmetic costs and compounded return differences must remain separate.

## 2. Assignment crosswalk and missing evidence

| Assignment item | Current state | Required action |
|---|---|---|
| §4.1 Assets, timing, frequency, lawful sources | Clearly stated; ETF proxies exist in code | R07: name actual benchmark tickers/return definitions; A04: add data/availability evidence. |
| §4.2 Features, labels, cleaning | Train-only processing explained; formulas/counts sparse | R08/A04: feature dictionary summary; M01: vintage sensitivity. |
| §4.3 Investable and forecast benchmarks | ETF and baseline artifacts exist | A01: expose matched timing/selection results; R07: document passive/intraday distinction. |
| §4.4 Model justification and overfitting | Appropriate shrinkage/tree families | R08: objectives, assumptions, realized grids and RFF status. |
| §4.5 Split and no leakage | Retrospective status substantially improved | R04: remove remaining contradictory labels and incorrect all-history claim. |
| §4.6 Training methods, seeds, versions | Seed/window reported; resolved versions in manifest | R08/R09: add methods and exact end-to-end reproduction contract. |
| §4.7 Time-respecting validation and selection | Stages given; exact promotion/ranking incomplete | R08: coverage threshold, tie-breakers and actual candidate rows. |
| §4.8 Positions and costs | Exact signed contract now present | R03: repair cost caption; A01/A03: interpret implementation consequences. |
| §4.9 OOS evaluation and interpretation | Segment metrics and wealth present | A01–A04: paired benchmarks, uncertainty, calibration, drawdown and mechanism diagnostics. |
| 15–25-page PDF | Current 21 pages: **satisfied** | R01/R06: navigation and pagination fixes without padding. |
| Contribution note | Only roster repeated | R10: actual roles required from authors. |
| PDF filename, runnable code, environment, video | Not fully verified | R09/R10: release checklist; video remains unassessed. |

The assignment rewards process, not necessarily positive returns. Deep learning, causal identification and production execution are not mandatory. Do not delay essential submission repairs to add an impressive-sounding model.

## 3. Pinpointed report and build defects

### R01 — Fix the page-zero contents [P0, R, confirmed]

**Location:** PDF page 2; `reports/publication_report_sections.py`, `make_contents`, approximately lines 251–279; `finalize_publication` calls it without a page map around line 233.

**Defect:** cached `PAGEREF` text is generated using `(pages or {}).get(h.text, 0)`. The rendered final PDF contains zeros for all 18 destinations.

**Change:** implement a two-pass publication build. Render draft; resolve each Heading 1 to its actual PDF page, excluding matches on the contents page; call `make_contents(doc, pages=resolved_map)` or refresh fields through the document renderer; save and re-render. Iterate until page references stabilize. Fail the build on any missing/zero destination. Do not hardcode the current 21-page map.

**Acceptance:** all 18 entries match actual headings in the final PDF; neither DOCX cached entries nor PDF contains page-zero destinations; full final render reviewed. Depends on other layout-changing tasks finishing first.

### R02 — Replace stale publication QA and strengthen release lineage [P0, R, confirmed]

**Location:** `reports/report_publication_verification.json`; `reports/publication_report_sections.py:18`, `publication_pack`; report evidence JSON.

**Defect:** published files do not match the recorded QA hashes/page count. `publication_pack` checks pack `files`, but does not validate `inputs` or enforce that the pack's `canonical_config` equals the report's selected configuration.

**Change:** create one explicit release input manifest and make the builder resolve every input from it. Validate selected-config consistency, dataset/run/freeze parent edges, hypothesis/strategy-analysis parents, input hashes, and final report hashes. Distinguish short run content IDs from full file SHA-256. Record Git HEAD, dirty state, resolved configuration hash, source-file hashes, renderer version and verification logs.

**Acceptance:** deliberately changing the selected-config ID or swapping an analysis from another run causes a hard failure. A finished release has a new release ID and a QA record written **after** final visual and numeric verification. Never alter original run manifests to match new code.

### R03 — Correct Figure 16's numerical claim [P0, R, confirmed]

**Location:** PDF page 20, Figure 16; `scripts/build_publication_figure_pack.py:383`.

**Current phrase:** “The 2025 curve approaches zero at the recorded 15 bps assumption.”

**Evidence:** selected 2025 net return at 15 bps is −4.0384%. Fixed-holdings break-even is approximately 8.2454 bps. The 2026 break-even is approximately 36.2149 bps.

**Change:** generate caption and annotations from the same cost-sweep data. Suggested wording: “At the modeled 15 bps round-trip cost, 2025 returns −4.04% net; its fixed-holdings break-even cost is approximately 8.25 bps. The 2026 extension breaks even near 36.21 bps.” Add the unchanged-holdings caveat.

**Acceptance:** the point at 15 bps reconciles to each original net ledger within numeric tolerance; plotted crossings agree with computed roots. Do not rerun prediction selection to make this graph.

### R04 — Remove three contradictory claims [P0, R, confirmed]

| Exact location | Current phrase | Replacement grounded in evidence |
|---|---|---|
| Section 8.1, PDF p.17; `build_report_ai_capability.py:792` | “2025 is flat” | “The 2025 replication loses 4.04% net; the positive 2026 extension remains retrospective and regime-specific.” |
| Section 8.3, p.18; builder around line 798 | “costs remove most gross gains” | “Costs more than eliminate the 2025 gross gain, taking +5.16% gross to −4.04% net.” |
| Section 7.3, p.16; `publication_report_sections.py:84` | “one fit on all pre-2026 observations” | “One fit on the declared rolling pre-2026 window, 25 November 2020–30 December 2025.” |

The extension manifest records `training_scheme=rolling`, `training_start=2020-11-25`, `training_end=2025-12-30`. It did not fit on all data since 2016.

Also replace residual “2025 frozen final” / “2026 forward extension” display labels in the segment table and `combined_evaluation` with “historical replication” / “retrospective extension.” Keep internal run IDs unchanged. **Acceptance:** report prose, tables, captions and abstract use the same evidence status; dates derive from manifests.

### R05 — Repair Figure 18's method description and build dependency [P0, R/A, confirmed mismatch; image lineage must be resolved]

**Location:** PDF p.21, Figure 18; Section 6.2 p.14; `scripts/build_publication_figure_pack.py:519–524`; report builder `groups` around lines 487–492.

**Defect:** caption says “single stock-day permutation.” Current selected runs contain repeated `oos_date_block_group_permutation_mse_increase` records. The current implementation permutes whole dates while preserving asset identities, repeating across seeds. It does **not** permute consecutive multi-day blocks. The figure pack copies `reports/figures_ai_capability/group_importance_2025_2026.png`, a previously generated image, instead of directly binding itself to the raw importance CSVs.

**Change:** generate the figure directly from the pinned final/extension importance CSVs, filter the selected config and exact `measure`, and record both CSV hashes. Describe the actual date-group permutation. Show across-permutation/refit variability, clearly distinguishing descriptive variability from a statistical confidence interval. Avoid implying causal contribution.

**Acceptance:** fresh checkout → figure pack works without a preexisting legacy PNG; caption method matches artifact values; per-group plotted means reconcile to selected rows; no changed source image is silently carried into an earlier pack. The current pack's hashes passed—the issue is provenance/method accuracy, not proven image tampering.

### R06 — Fix short-table pagination and redundant visuals [P1, R]

**Location:** source table pp.4–5; feature ladder pp.7–8; temporal-stage table pp.10–11. Current Figures 2–3 p.6 repeat market-path context.

**Change:** keep these short tables together when they fit on one page, repeat headers when unavoidable, number substantive tables and provide references. Retain Figure 2's logarithmic context plot; replace Figure 3 with A04's overnight/intraday diagnostic or calibration if the outcome data are not ready. Retain the improved Figure 9 family matrix and Figure 15 individual regime observations.

**Acceptance:** inspect each rendered page; no header plus one-row fragments where avoidable, readable final-size plot labels, stable contents, 15–25 pages. No statistical smoothing or shortened axes that conceal adverse outcomes.

### R07 — Make benchmark identity explicit [P0, R/A]

**Location:** Sections 2.2/5.3, Figures 10/15, main results tables; `src/quantfin/cross_market/panel.py:607`.

**Evidence:** code prefers `ITBEES.NS` and `NIFTYBEES.NS`, with `^CNXIT`/`^NSEI` fallback if absent. Some captions say ETF while table columns simply say Nifty IT/Nifty 50. The report lacks an exact observed-source contract.

**Change:** verify the current dataset's benchmark source against the raw series and record ticker, exchange/currency, adjusted-return semantics, sample coverage, actual fallback usage, and overnight inclusion. Distinguish fixed-share buy-and-hold from daily equal-weight open-to-close cohort. Do not merely infer actual ETF use from the preferred code branch.

**Acceptance:** benchmark return series recomputes from the named raw snapshot; captions and table names identify the same instrument and horizon; any fallback is explicit. This supersedes the first review's generic concern that only index benchmarks existed.

### R08 — Complete the model-selection and feature contract [P0, R]

**Location:** Sections 4.1/5.1/5.2; Appendix A. Sources: each run's `configurations.json`, resolved YAML, `experiments.py`, freeze `selection_values`.

**Change:** add one compact methodology table containing:

- actual initial training/warmup and rolling periods; feature formulas/units/lookbacks; missingness cutoff and winsor quantiles;
- candidate family, estimation method/solver, actual tested parameters, seed and refit policy;
- 25 screening rows, 13 confirmation rows, **12 final diagnostic configurations** and **4 extension configurations**, distinguishing the one selected strategy from baselines/diagnostics;
- minimum prediction coverage 0.98; primary metric net Sharpe; tie-breakers R² versus asset mean, IC, lower turnover and lower complexity, as implemented;
- RFF status: earlier historical work exists; excluded from this submission rerun. Do not label RFF results as newly obtained in this run;
- realized feature counts by family and refit; do not equate tree capacity proxies with exact independent parameter counts.

**Acceptance:** every count/setting is extracted from artifacts, not inferred from all combinations listed in YAML. The final evaluated counts do not imply 12 separately selected winners. Include saved package versions (e.g. scikit-learn 1.7.2, pandas 2.3.3) from the actual run environment rather than current installation defaults.

### R09 — Eliminate hardcoded scientific numbers and fragmented input IDs [P0, R]

**Locations:** `reports/publication_report_sections.py:74–84` hardcodes H4/H5/annual-return prose; `company_discussion` hardcodes workforce figures; `evidence_appendix` hardcodes several analysis IDs; `publication_pack` and regime CSV path hardcode the figure directory. `REPORT_*` overrides in the main builder therefore do not update everything.

**Change:** create one release registry with typed full paths, IDs and hashes. Read scientific prose values through a central report-facts function. Add a claim registry with `claim_id`, report anchor, artifact, row selector, formula, units, rounding, expected value and uncertainty source. Treat externally sourced facts separately from experiment outputs. Generate Appendix A/E from the registry.

**Acceptance:** switching a test fixture to a different valid run updates all text/tables/plots/appendices together or fails explicitly; no mixed-release report is possible. Do not automatically select the newest filesystem directory. Record every newly returned analysis ID and its parents explicitly.

### R10 — Finish course deliverables [P0, R, author input needed for roles]

**Location:** contribution statement p.18; requirement §§5–7.

**Change:** replace the repeated roster with truthful individual/shared contributions supplied by authors. Verify 15–25-minute video, accessible/downloadable link, complete runnable code, `requirements.txt`, README exact commands/expected outputs, and required `Group_X_Report.pdf` name (confirm X is the team's submission group, currently Team 16).

**Acceptance:** submission checklist links actual deliverables. Do not mark video or contribution balance verified from report text alone. No submission/upload is requested by this plan.

## 4. Completed analysis that should be shown and further interpreted

### A01 — Report timing-versus-selection comparisons already saved [P1, A/R]

**Location to change:** Section 6.2 attribution table and conclusion's “matched timing-versus-selection attribution” future-work statement.

**Evidence:** current `ai_strategy_comparison` summaries, IDs in Section 6.

| Policy | 2025 net Sharpe | 2026 net Sharpe |
|---|---:|---:|
| Selected signed stock portfolio | −0.260 | 1.456 |
| Cohort-mean signed timing | −0.427 | **2.203** |
| U.S.-services direction/equal weight | −0.906 | 2.021 |
| Always-short cohort | −0.763 | −0.139 |
| Cross-sectional residual policy | Undefined, no trades | Undefined, no trades |

**Change:** add this compact diagnostic table and state the useful implication: positive 2026 average IC did not produce a higher portfolio Sharpe than the cohort-timing policy; a permanent short also did not explain the net result. Align daily ledgers, validate exposure/cost comparability, and calculate paired date-block uncertainty for selected minus timing-only net returns. Compare arithmetic mean differences with their interval; do not subtract Sharpes and treat that as a significance test.

**Acceptance:** identical aligned dates and explicitly defined exposure convention; report both point estimates and paired uncertainty. The existing comparator uses its own cohort-mean gate—if exact gate matching is required, add a version using the selected strategy's identical active dates/sign/gross exposure. Never reselect the headline model using the 2026 winner.

### A02 — Put calibration and directional-baseline uncertainty into the report [P1, A/R]

**Location:** Section 5 metric inventory / Section 6 results; replace Figure 3 if page space is tight.

**Evidence:** 2025 `forecast_inference.json`: directional accuracy 54.1767%; majority-down baseline 53.6948%; incremental-accuracy interval approximately [−2.2902, +3.6968] percentage points. Calibration slope interval approximately [−0.7656, 1.7171]. These are not clear evidence of calibrated, incremental direction skill.

**Change:** show a calibration plot using saved forecast bins plus ±15 bps trading thresholds, numerical bin sorting and observations/date counts. Retain date-based uncertainty. The majority sign reported from evaluation labels is a descriptive reference, not a forecast selected prospectively; add a training-determined majority baseline for a deployable comparator.

**Acceptance:** bins are ordered by numerical prediction, not string interval labels; zero/flat observations remain represented; uncertainty preserves dates and cross-asset clustering. Any fitted calibration map must be estimated only in forward development folds.

### A03 — Convert raw cost/exposure scores into an economic explanation [P1, A/R]

**Location:** Figures 10–12 and 16; Section 6 narrative.

**Change:** add long/short/asset P&L attribution, active-day versus all-day performance, trade count, turnover and concentration in the best 1/5/10 days. Use actual ledger arithmetic for attribution and explain how the compounded portfolio total differs. Add a drawdown panel under Figure 10. Present fixed-holdings fee stress separately from the existing policy-responsive sensitivity that changes the cost-dependent hurdle.

**Acceptance:** sum of daily asset/side contributions minus costs equals the original daily net ledger; all-day metrics include flat days; deleting top days is labeled sensitivity rather than an improved strategy. Preserve zero-cash-return Sharpe convention or explicitly change and re-audit it.

### A04 — Replace assertion-only EDA with diagnostic evidence [P1, A/R]

**Location:** Section 3 diagnostic table claims “heavy tails,” “volatility clustering,” “modest calendar effects,” and common movement; Figures 2–5 mainly show paths/correlation.

**Change:** produce a compact development-only panel: intraday target quantiles/ECDF, rolling volatility or squared-return dependence, feature-family coverage/age, and first-PC variance share. For the cross-market mechanism, compare prior U.S. services return with next Indian **overnight** and **open-to-close** outcomes on the same sample. Keep current-session outcomes out of features. Existing lagged `own__gap_return` must not be substituted for the current overnight outcome.

**Acceptance:** figures use only the declared development period unless prominently labeled retrospective; price adjustment and holiday mapping are consistent; lag definitions and uncertainty are stated. Drop unsupported calendar-effect prose if evidence is weak rather than manufacturing significance.

### A05 — Reconcile hypothesis effect sizes and inference scopes [P1, A/R]

**Location:** Section 4.3 capability table; Section 7.1–7.2; Figure 13; Appendix D event coverage.

**Verified values:** H1 all dates: coefficient 0.097977, Holm p=0.005638, n=1,421. H2 pooled: −0.001695 decimal / −0.1695 percentage points, Holm p=1.0, n=925. H2 2026: −0.006954 / −0.6954 percentage points, Holm p=0.015507, n=185, 22 event sessions. H4 has 21 scored dates and is not estimable under the 30-date rule.

**Change:** label raw event/non-event, randomization and controlled regression estimates separately. Report effect size, interval, event count, non-event count, controls, covariance, raw and adjusted p-values. H1's coefficient means about 0.098 percentage points of Indian response per 1 percentage point U.S. return; it is not a 9.8% trading gain. Explain that Section 4.3's older capability correlations are descriptive legacy analyses, not a successful H4 test under the final protocol.

**Acceptance:** recompute Holm values from the declared complete test family; missing tests remain not-estimable. Distinguish the 1,000-draw model inference from the 2,000-draw H5 artifact. Preserve the correct statement that significance in one year but not another does not prove a between-year difference.

## 5. Missing experiments: tightly scoped, with no promised favorable outcome

### M01 — Strict-vintage sensitivity of the actual selected model [P1, M]

**Gap:** 60 current-vintage fallback features remain in the new dictionary and F7 includes them. The report discloses this but has no demonstrated current-model sensitivity result.

**Configuration defect:** `configs/cross_market_ai_capability_research.yaml`, `models.profiles.gap_diagnostics.custom_configurations`, still uses depth **8**, not current depth **6**. It also sets `include_standard_components: false` and lists only Extra Trees variants; without explicit asset-mean predictions, `evaluate_predictions` cannot calculate a valid R² versus asset mean.

**Change:** create a new diagnostic config/profile (preserve the canonical one). Generate both reference and fallback-excluded variants directly from the frozen depth-6 parameters. Include zero and asset-mean baselines. Export exact retained feature names/vintage flags per refit; count only actual used columns. Keep sample, trading rule, seeds and update schedule identical.

**Acceptance:** reference reproduces canonical predictions within a documented tolerance; no flagged fallback column enters the strict variant; finite matched baseline R²; report paired loss/net-return differences with intervals. A loss of the apparent edge is a valid finding.

### M02 — Within-family incremental information ablations [P1, M; depends on M01 setup]

**Gap:** Ridge F0–F7 ladder cannot show which groups help the selected Extra Trees estimator.

**Change:** one fixed-capacity comparison: full F7, F0, F2, F7 without U.S.-services groups, F7 without AI groups, and strict-vintage F7. Define whether removing services also removes aggregate/interaction/ADR-derived proxies; list exact families so “removal” is not nominal. Avoid simultaneously retuning hyperparameters in this attribution test.

**Acceptance:** identical dates, parameters and execution across variants; selected feature inventory proves exclusions; report both statistical loss and net economic value. Continue to call prior periods retrospective.

### M03 — Optional model improvement after evidence gaps close [P2, M]

**Trigger:** only if A01–A04 identify a specific failure mechanism. Examples: cost-aware forecast calibration if magnitudes are miscalibrated; Huber regression if tails dominate error; a sector-common plus residual model if ranking underperforms timing. Existing Elastic Net, boosting and tree comparisons are already substantive; another model is not needed merely for breadth.

**Protocol:** predeclare a small grid on forward development folds, compare with current model and a simple timing policy, freeze the choice, preserve failed variants, and evaluate prospectively when genuinely new data exist. Define success as stable paired incremental value with acceptable costs/risk, not the highest inspected 2026 Sharpe.

**Acceptance:** documented decision before evaluating new data. No claim that this task makes 2025/2026 untouched again.

## 6. Canonical evidence registry to preserve and extend

These are current baseline IDs. New analysis IDs must be captured from actual command output; never invent or hand-edit a content-hash suffix.

| Key | Current immutable ID |
|---|---|
| DATASET_ID | `ai_capability_panel_20261101T012801Z_ff277b55597d727a` |
| FORWARD_DATASET_ID | `ai_capability_2026_panel_20261101T012848Z_7f83e6f3f4f128f8` |
| EPOCH_SNAPSHOT_ID | `epoch_benchmarks_20261031T063140Z_694be8985284cf56` |
| SCREENING_RUN_ID | `cm_ai_capability_screening_20261101T013231Z_038064c84d36` |
| CONFIRMATION_RUN_ID | `cm_ai_capability_confirmation_20261101T020346Z_327cf6e7c3bd` |
| FREEZE_ID | `cm_ai_capability_freeze_20261101T025756Z_b80ca3883e16` |
| FINAL_RUN_ID | `cm_ai_capability_final_test_20261101T025817Z_30ebf00d8090` |
| FORWARD_RUN_ID | `cm_ai_capability_2026_forward_20261101T030225Z_6a066bcfcc82` |
| SELECTED_CONFIG_ID | `cm_extra_trees_cd9235695e6b` |
| EDA_RUN_ID | `analysis_20261101T013012Z_d50423d05d5c` |
| FORWARD_EDA_ID | `analysis_20261101T013030Z_3ebb036affd8` |
| EVENT_ANALYSIS_ID | `ai_services_analysis_20261101T013058Z_e88408b9a16d` |
| CAPABILITY_ANALYSIS_ID | `ai_capability_analysis_20261101T013123Z_97f653e82ec8` |
| EPOCH_ANALYSIS_ID | `epoch_capability_analysis_20261101T013137Z_45f5b1bd11ec` |
| MODEL_EVIDENCE_ID | `model_evidence_final_test_20261101T030544Z_a4d9077ee46e` |
| FORWARD_MODEL_EVIDENCE_ID | `model_evidence_forward_extension_2026_20261101T030629Z_2f2c1a45c5fc` |
| LADDER_ANALYSIS_ID | `information_ladder_final_test_20261101T030705Z_4fcf7b07672b` |
| STRATEGY_ANALYSIS_ID | `ai_strategy_comparison_20261101T030717Z_591c864e3aba` |
| FORWARD_STRATEGY_ANALYSIS_ID | `ai_strategy_comparison_20261101T030726Z_9660a3a84bc3` |
| HYPOTHESIS_ANALYSIS_ID | `hypotheses_20261101T030841Z_d494c2f238ca64a6` |
| Current figure pack content hash | `38ea26773f587009` |

Base paths:

- Historical datasets: `data/processed/cross_market_ai_capability/`.
- Extension datasets: `data/processed/cross_market_ai_capability_2026/`.
- Historical runs/analyses: `artifacts/cross_market_ai_capability/{runs,analysis}/`.
- Extension runs/analyses: `artifacts/cross_market_ai_capability_2026/{runs,analysis}/`.
- Event study: `artifacts/cross_market_ai_services_2026/analysis/` (**different root**).
- Hypotheses: `artifacts/research_hypotheses/`.
- Current figure pack: `reports/publication_figure_pack_2026-11-01/`.

**Required dependency checks:** confirmation → screening → dataset; freeze → confirmation; final → freeze + dataset + selected config; extension → same freeze/config + extension dataset; model/strategy analyses → correct run; hypothesis analysis → exact panels + ledgers + source files; figure → exact analysis/CSV selectors; report → exact figure pack and release registry; final QA → exact DOCX/PDF.

A file hash proves file identity. It does not prove a scientific interpretation, correct source timing, complete event coverage, or causal validity.

## 7. Command book

### C0 — Baseline audit, read-only

These interfaces were inspected; the two verifiers below were actually executed during this review. Run from repository root using the project virtual environment. Commands shown here do not train a model.

```bash
cd /Users/whitetiger/Desktop/WhiteTiger/17_projects/24_Project2_QuantFin/project2QuantFin

python3 artifacts/report_reviews/2026-11-01_134513_SGT/audit_release.py \
  > /tmp/quant_release_recheck.json

.venv/bin/python scripts/verify_ai_capability_pipeline.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --dataset-id ai_capability_panel_20261101T012801Z_ff277b55597d727a \
  --epoch-snapshot-id epoch_benchmarks_20261031T063140Z_694be8985284cf56 \
  --eda-run-id analysis_20261101T013012Z_d50423d05d5c \
  --capability-analysis-id ai_capability_analysis_20261101T013123Z_97f653e82ec8 \
  --epoch-analysis-id epoch_capability_analysis_20261101T013137Z_45f5b1bd11ec \
  --screening-run-id cm_ai_capability_screening_20261101T013231Z_038064c84d36 \
  --confirmation-run-id cm_ai_capability_confirmation_20261101T020346Z_327cf6e7c3bd \
  --freeze-id cm_ai_capability_freeze_20261101T025756Z_b80ca3883e16 \
  --final-run-id cm_ai_capability_final_test_20261101T025817Z_30ebf00d8090 \
  > /tmp/quant_pipeline_recheck.json

.venv/bin/python scripts/verify_frozen_2026_extension.py \
  --config configs/cross_market_ai_capability_2026_extension.yaml \
  --run-id cm_ai_capability_2026_forward_20261101T030225Z_6a066bcfcc82 \
  > /tmp/quant_extension_recheck.json
```

The included `audit_release.py` is a baseline-specific reporting helper requiring PyMuPDF in `python3` (available in this review environment). It emits JSON and does not itself fail the process on a mismatch. Inspect `publication_files`, `manifest_checks[].failed`, `pdf_pages` and contents text. It is **not** the proposed general release gate. After changing the canonical release, update the registry-driven checker rather than assuming this pinned baseline helper audits new IDs.

### C1 — Existing no-fit diagnostic builders

Use only when code/data-derived diagnostics actually need refreshing. Each execution creates a new analysis identity; existing saved results already support A01/A02.

```bash
.venv/bin/python scripts/analyze_ai_capability_model_run.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --run-id cm_ai_capability_final_test_20261101T025817Z_30ebf00d8090 \
  --plan-only

.venv/bin/python scripts/compare_ai_services_strategies.py \
  --config configs/cross_market_ai_capability_2026_extension.yaml \
  --run-id cm_ai_capability_2026_forward_20261101T030225Z_6a066bcfcc82 \
  --plan-only
```

Remove `--plan-only` from the relevant command after the required code change to execute it. For 2026 model evidence use the extension config and extension run; for 2025 strategies use the historical config and final run. These commands do not implement the proposed paired-bootstrap analysis by themselves; extend the strategy analysis first and hash its source.

### C2 — Exact current hypothesis inputs, preview only

```bash
.venv/bin/python scripts/analyze_research_hypotheses.py \
  --dataset data/processed/cross_market_ai_capability/ai_capability_panel_20261101T012801Z_ff277b55597d727a \
  --dataset data/processed/cross_market_ai_capability_2026/ai_capability_2026_panel_20261101T012848Z_7f83e6f3f4f128f8 \
  --run artifacts/cross_market_ai_capability/runs/cm_ai_capability_final_test_20261101T025817Z_30ebf00d8090 \
  --run artifacts/cross_market_ai_capability_2026/runs/cm_ai_capability_2026_forward_20261101T030225Z_6a066bcfcc82 \
  --epoch-events artifacts/cross_market_ai_capability/analysis/epoch_capability_analysis_20261101T013137Z_45f5b1bd11ec/epoch_event_capability_returns.csv \
  --company-evidence configs/company_adaptation_evidence_2026-11-01.json \
  --start 2021-01-01 --end 2026-09-30 --break-date 2025-01-01 \
  --minimum-events 8 --bootstrap-draws 2000 --block-sessions 20 --seed 5205
```

This matches current manifest settings, including both overlapping panels. The current script reconciles exact overlapping hypothesis inputs and fails conflicts. Do not concatenate duplicated rows manually. Add `--execute` only if inputs/code changed or a deliberate rerun is needed. Capture the actual returned ID; never use filesystem “latest” selection.

### C3 — Development diagnostic profile, only after M01/M02 configuration repair

**Required implementation first:** create `configs/cross_market_gap_diagnostics_2026-11-01.yaml` extending the capability config, with a copied corrected `gap_diagnostics` profile, depth-6 variants, explicit baseline configurations, separate output runs/analysis roots, and an exploratory study description. It must retain the original immutable dataset path. This config does not exist as part of this plan.

Then the existing runner can preview and execute development screening:

```bash
.venv/bin/python scripts/run_cross_market_experiments.py \
  --config configs/cross_market_gap_diagnostics_2026-11-01.yaml \
  --dataset-id ai_capability_panel_20261101T012801Z_ff277b55597d727a \
  --stage screening --profile gap_diagnostics \
  --training-scheme rolling --parallel-workers 2 --plan-only
```

Check the enumerated configuration list—not just the summary count—for correct depth, exclusions and baselines. Removing `--plan-only` fits on the declared **screening** period. It does **not** run all variants through 2025/2026. Do not misuse `--stage final_test` expecting arbitrary diagnostic variants: the existing final stage loads configurations from the freeze.

For paired retrospective 2025/2026 ablations, implement a dedicated diagnostic evaluator that accepts explicit fixed configurations, preserves the canonical quarterly/static fit policies, writes separate diagnostic runs and never promotes a winner. Suggested interface to implement and test, **not currently available**:

```bash
# Proposed interface: create this script before executing.
.venv/bin/python scripts/run_report_gap_ablation.py \
  --release-config configs/cross_market_gap_diagnostics_2026-11-01.yaml \
  --reference-freeze cm_ai_capability_freeze_20261101T025756Z_b80ca3883e16 \
  --historical-dataset-id ai_capability_panel_20261101T012801Z_ff277b55597d727a \
  --extension-dataset-id ai_capability_2026_panel_20261101T012848Z_7f83e6f3f4f128f8 \
  --plan-only
```

Before expensive fitting, verify the full-feature reference reproduces the frozen model configuration and schedule; then test prediction equivalence on a representative block. Record actual runtime; do not promise an unmeasured duration.

### C4 — Publication rebuild after source repairs

**Current commands exist but do not by themselves fix the broken contents/lineage.** First implement R01/R02/R05/R09. The publication code currently hardcodes its pack directory; modify it to consume the release registry before choosing a new pack path.

```bash
# After source fixes and explicit release input binding:
.venv/bin/python scripts/build_publication_figure_pack.py \
  --output reports/publication_figure_pack_2026-11-01_revised

.venv/bin/python reports/build_report_ai_capability.py

python3 /Users/whitetiger/.codex/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/render_docx.py \
  reports/Project2_Team16_Report.docx \
  --output_dir /tmp/quant_report_revised_render --emit_pdf
```

The DOCX renderer may require permission to launch LibreOffice outside the sandbox. Complete the contents-resolution second pass, re-render, inspect every page, then copy the verified PDF into `reports/`. Save the previous published DOCX/PDF under a versioned release before overwriting. Do not run the statistical figure pipeline against hidden `REPORT_*` variables from a different shell session.

**Release verifier to implement:** one command should read the release registry, verify lineage/claims/TOC/page count/citations/figure files and emit machine-readable results with nonzero exit on failure. This interface is proposed, not present:

```bash
# Proposed interface: implement and test first.
.venv/bin/python scripts/verify_report_release.py \
  --release-manifest reports/releases/REPLACE_WITH_ACTUAL_RELEASE_ID/manifest.json
```

Use an actual emitted release ID; the placeholder is intentionally not executable. The verifier must never write `status: pass` before checks have completed.

## 8. Citation and external-evidence repairs

### CITE01 — Correct the Kelly reference [P0, R, confirmed externally]

**Location:** Reference [2], PDF p.18; `publication_report_sections.py` `REFS`.

The report says **459–501**. The American Finance Association's official issue listing gives **459–503**, DOI `10.1111/jofi.13298`. Correct the report bibliography and its evidence register. The supplied assignment also contains the shorter range; keep the assignment document unchanged and cite the publisher's metadata for the report. [Official journal issue](https://afajof.org/issue/volume-79-issue-1/)

Reference [1]'s 449–492 and DOI `10.1111/jofi.12733` are supported by the publisher listing; no correction identified. [Publisher record](https://onlinelibrary.wiley.com/doi/10.1111/jofi.12733)

### CITE02 — Add method citations where the report currently names techniques without sources [P1, R]

**Locations:** Section 5.1 Extra Trees/PCA/regularized-model discussion; Section 7.1 HAC, Holm and circular block-bootstrap paragraph.

Add primary method references or official software documentation tied to the exact implementation, especially Extra Trees and the dependence/multiplicity procedures. Verify metadata before insertion; do not copy invented DOIs. State actual software version and explicit Holm method rather than assuming a package's default. The official [statsmodels multiple-testing documentation](https://www.statsmodels.org/v0.12.2/generated/statsmodels.stats.multitest.multipletests.html) distinguishes correction methods; select documentation appropriate to the saved installed version when finalizing.

This is a scholarly completeness improvement, not evidence that the implemented Holm correction is wrong.

### CITE03 — Archive source evidence with locators; do not count a URL as full validation [P1, R/A]

Checked during this review:

| Report claim | Source check | Required final evidence |
|---|---|---|
| TCS March 584,519 and September 598,056 headcount | Both primary press releases support the totals | Preserve publication dates, human-resources section locator and source snapshot hash. |
| Infosys June 328,062 / September 332,542 | Fact sheet p.2 supports both | Retain page locator; arithmetic change +4,480 / +1.37%. |
| Wipro June 243,044 | Primary June data sheet supports total | Retain p.1 locator and definition. |
| Wipro September 236,328 | SEC URL resolves, but extracted page is image-based | Visually inspect the exhibit image or use a corroborating primary PDF before marking this value reverified. No mismatch is asserted here. |
| BoE/FCA 2% fully autonomous use cases | Supported by official survey executive summary | Keep UK-financial-services population qualification; not direct evidence about Indian IT customers. |

Primary sources: [TCS March](https://www.tcs.com/who-we-are/newsroom/press-release/tcs-financial-results-q4-fy-2026), [TCS September](https://www.tcs.com/who-we-are/newsroom/press-release/tcs-financial-results-q2-fy-2027), [Infosys fact sheet](https://www.infosys.com/investors/reports-filings/quarterly-results/2026-2027/q2/documents/fact-sheet.pdf), [Wipro June](https://www.wipro.com/content/dam/nexus/en/investor/quarterly-results/2026-2027/q1fy27/datasheet-q1fy27.pdf), [Wipro SEC exhibit](https://www.sec.gov/Archives/edgar/data/1123799/000119312526426841/d188224dex995.htm), [BoE/FCA survey](https://www.bankofengland.co.uk/report/2024/artificial-intelligence-in-uk-financial-services-2024).

Store source URL, retrieval time, publication time, page/section, precise fact, units/population, local snapshot SHA-256 where permitted, and verification status. Reuters/Klarna contextual claims were not independently reverified in this audit; retain their existing citations and verify before final release rather than marking every reference “checked” by default. Correct company facts must still not be presented as causal AI-productivity evidence.

### CITE04 — Cite data snapshots and event selection, not just provider homepages [P1, R]

**Location:** Section 2.2 source table and Figures 7/8/17 captions.

Add the relevant raw snapshot IDs, source endpoint/file and retrieval timestamp; link the exact official release calendar and inclusion criteria. Epoch mapping is a current-vintage retrospective subset, not the complete 2026 event calendar. Record duplicate releases mapped to one session, excluded events and their reasons. An event-count bar chart is coverage evidence, not evidence that omitted years had no AI releases.

## 9. Agent deliverables and acceptance gates

### Gate 1 — Correctness before new research

- [ ] R01–R05, R07–R10 and CITE01 implemented.
- [ ] Central release inputs and numeric claim registry generated.
- [ ] Current values in Section 1 reproduced; no silent changes to the canonical model.
- [ ] New publication QA matches actual final files, not just legacy artifact hashes.

### Gate 2 — Existing evidence explained

- [ ] A01 paired comparator results reported with uncertainty.
- [ ] A02 calibration/directional baseline plotted and interpreted.
- [ ] A03 costs/drawdown/attribution reconciled to ledgers.
- [ ] A05 inference scopes and source settings explicit.
- [ ] Figure 18 method corrected and variability appropriately labeled.

### Gate 3 — Missing scientific checks

- [ ] M01 and M02 completed on fixed, matched specifications or clearly left open with reduced claims.
- [ ] No false assertion that a profile definition constitutes a completed experiment.
- [ ] A04 data/timing diagnostics shown or unsupported prose removed.
- [ ] No retrospective variant promoted as a pristine new test.

### Gate 4 — Final submission package

- [ ] Every main empirical claim has an artifact selector/formula or external-source locator.
- [ ] Figures and tables numbered and cross-referenced; all contents destinations correct.
- [ ] All pages inspected at final size; 15–25-page requirement maintained.
- [ ] Truthful contribution note, verified source-code/environment instructions and 15–25-minute video.
- [ ] Submission filename/roster/access checked; no upload performed without the user's request.

### Required completion log

For every action, append:

```text
Action ID:
Status: open | implemented | verified | blocked
Changed files and functions:
Command actually executed:
Input IDs and hashes:
Output IDs and hashes:
Numeric/visual checks and result:
Report headings/figures updated:
Remaining limitation:
Verified at: YYYY-MM-DD HH:MM:SS SGT
```

Recommended order: **R09/R02 input architecture → R03/R04/R05/CITE01 content fixes → A01/A02/A03/A05 existing-data analysis → M01/M02 only where needed → R06/A04 figure consolidation → R01 final contents → R02 final QA → R10 submission checklist.**

The key improvement is not simply “more analysis.” It is that a reader can move from a precise claim to its data, calculation, uncertainty, configuration and immutable run, and obtain the same result.
