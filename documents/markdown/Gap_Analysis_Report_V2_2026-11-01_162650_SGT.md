# Updated report assessment — 88/100

**Report/project-evidence score: 88/100**, compared with **83/100** at the 14:11:52 SGT review. **Research-publication readiness: 74/100**, compared with 68/100. These are reviewer judgments using the same category weights, not official course marks or a prediction of acceptance by an IEEE journal. The assignment emphasizes process rather than positive returns; negative returns have not been treated as a defect by themselves.

**Review started:** 1 November 2026, **16:26:50 SGT (UTC+08:00)**.  
**Reviewed release:** `project2_team16_v2_2026-11-01`, registry revision **4**.  
**Primary document:** `reports/Project2_Team16_Report_V2.docx`.  
**Requirements:** `documents/markdown/Project2.md`.  
**Companion PDF:** 21 pages; 15 numbered report figures.  
**Audit directory:** `artifacts/report_reviews/v2_2026-11-01_162650_SGT/`.

This revision closes substantial gaps: exact-model strict-vintage sensitivity, paired timing comparisons, explicit annualization, release negative controls, figure input hashes, and a usable reproduction recipe. The remaining work is more targeted. The most important new findings are a report-text verification loophole, incomplete retention of strict-variant forecast evidence, an incorrect Figure 5 evidence address, and incomplete interpretation of the strict variant's forecast-versus-trading trade-off.

The report and canonical results were not modified. A deliberately corrupted DOCX was created **only in the audit directory**, clearly named `NEGATIVE_CONTROL_NOT_FOR_SUBMISSION.docx`, to test the verifier.

## 1. Score and requirement coverage

| Category | Maximum | Previous | Updated | Assessment |
|---|---:|---:|---:|---|
| Research question/economic logic | 10 | 9 | 9 | Clear timing/selection distinction; conditional claims remain appropriate. |
| Data provenance, timing, leakage | 15 | 11 | 13 | Exact depth-6 exclusion sensitivity now completed; remaining historical-data assumptions disclosed. |
| Feature engineering/preprocessing | 10 | 8 | 8 | Good training-only processing and expanded ridge evidence; selected-family source ablations still missing. |
| Models, validation, selection | 15 | 13 | 13 | Clear search/confirmation/freeze design; no new prospective validation. |
| Trading, costs, benchmarks | 10 | 9 | 9 | Appropriate hurdle, costs, ETF identities and matched alternatives; attribution/execution realism can improve. |
| Evaluation/statistical inference | 15 | 13 | 14 | Paired date-block intervals now included; conclusions remain restrained. |
| EDA, figures, architecture | 10 | 9 | 9 | Less redundant EDA; more informative annual ridge matrix; targeted diagnostics still needed. |
| Structure/interpretation | 10 | 8 | 9 | Cleaner 21-page document, appendix addresses and annualization; a few important omissions and splits remain. |
| Reproducibility/submission readiness | 5 | 3 | 4 | Previous checker/environment defects fixed; report-text checks and final submission inputs remain open. |
| **Total** | **100** | **83** | **88** | **Substantial improvement in evidence, not merely formatting.** |

Requirements §§4.1–4.8 are substantially addressed: assets and decision clock, label, features, benchmark identity, model story, overfitting controls, temporal splits, training settings, selection rule and score-to-trade conversion are visible. §4.9 now explicitly separates cumulative and annualized returns and reports costs, volatility, Sharpe and benchmark comparisons. The 21-page PDF satisfies the 15–25-page limit. Remaining assignment-facing issues are truthful individual contribution notes and reproducible access to every new figure prerequisite. Video duration/access, Canvas membership and final source-package delivery were not verified.

Publication readiness remains lower because evidence is retrospective, the fixed current cohort is survivorship-conditioned, source-group contributions are unresolved, and the inference does not establish robust incremental stock-selection value. These are separate from whether the report meets a sound course-project standard.

## 2. Review scope and test results

Read the DOCX paragraphs/tables, current requirements, release registry, relevant builders, strict-vintage and paired-inference code, manifests and output tables. Reviewed all 21 PDF pages through contact sheets, with detailed inspection of pages 4, 11 and 14. Visual findings refer to the supplied companion PDF; this review did **not independently render the DOCX again**. DOCX and PDF hashes match the saved release verification. That establishes file identity with the release record, not proof of semantic equivalence between the two formats.

| Executed check | Result | Audit evidence |
|---|---|---|
| Full discovered unit suite | **15 passed** | `unit_tests.log` |
| AI capability pipeline verifier | **201 passed; 0 failed** | `pipeline.json` |
| Frozen 2026 extension verifier | **28 passed; 0 failed** | `extension.json` |
| Current release verifier against isolated registry copy | **225 passed; 0 failed** | `release_verification.json` |
| Existing four negative controls | **All four correctly rejected**: wrong freeze, wrong configuration, altered registered claim, stale figure input | `negative_controls.json` |
| Independent figure input/output SHA256 audit | **127/127 match** | `figure_hash_audit.json` |
| TOC resolver in project `.venv` | Succeeds; **18 heading destinations match** stored mapping | `toc_pages.json` |
| Strict-variant ledger accounting | Exact `gross − cost = net`; cumulative results reconcile | `strict_reconciliation.json` |
| Fresh ridge progression audit from saved predictions | 20 quarters per feature set; values reproduce the paragraph's rounded means | `feature_progression_recheck/` |
| New corrupted-DOCX negative control | **Failed acceptance test:** false abstract return accepted, exit 0, 225 checks passed | `report_text_negative_result.json` |

Counts overlap and are not independent scientific confirmations. Unit tests remain the same 15 tests; the new paired-bootstrap and strict-run orchestration scripts are not fully covered by dedicated unit tests. No new model fit, raw-data download, clean-machine rebuild or external citation sweep was performed. The new strict-vintage fit was evaluated from its saved evidence and source code, not rerun.

## 3. What is now closed, and what is only partly closed

| Prior issue | Current status |
|---|---|
| Missing freeze/claim checks | **Fixed for registered artifact claims.** The four old negative controls now fail correctly. Displayed document text remains unchecked. |
| Stale figure input hash | **Fixed.** All 127 recorded input/output entries match. |
| Wrong-version reproduction commands | **Substantially fixed.** README selects the registry and documents render/TOC passes. New ridge prerequisite remains implicit. |
| Undeclared PyMuPDF dependency | **Fixed by removal.** TOC resolver uses declared/documented external PDF tools and runs in `.venv`. |
| Cumulative/annualized confusion | **Fixed.** Section 6 and Figure 13 correctly distinguish them. |
| Clipped calibration chart | **Removed from main report; supplementary builder now includes uncertainty endpoints in its limits.** Do not demand reinsertion solely to close an old finding. |
| Strict-vintage sensitivity at wrong depth | **Fixed and executed.** The selected depth-6 parameters are preserved and all 60 flagged columns excluded. |
| Missing paired timing-versus-selection inference | **Fixed and reported.** Intervals remain inconclusive, which is a valid result. |
| Redundant India/U.S. price-path chart | **Removed.** Main report now has 15 figures. |
| Incorrect seasonality alignment claim | **Fixed.** Appendix B explicitly avoids a standalone seasonality claim. |
| Missing circular-block method citation | **Fixed.** Reference [21] added. |
| Individual contribution note | **Still open.** A roster is not a role allocation. |
| Exact-model source-group ablation, P&L attribution, prospective evidence | **Still open.** Strict-vintage exclusion does not replace these analyses. |

## 4. Numerical interpretation of the new evidence

The original selected model remains `cm_extra_trees_cd9235695e6b`; canonical returns are still **−4.04% in 2025**, **+15.01% in January–September 2026**, and **+10.37% combined**. The new strict-variant result is a separate sensitivity, not a replacement selected result.

Source: `artifacts/cross_market_ai_capability/analysis/strict_vintage_sensitivity_20261101T072530Z_d98ad9caf3b8/strict_vintage_metrics.csv`.

| Metric | 2025 selected | 2025 strict | 2026 selected | 2026 strict |
|---|---:|---:|---:|---:|
| Cumulative net return | −4.04% | −1.84% | +15.01% | +24.93% |
| Annualized net return | −4.09% | −1.87% | +20.99% | +35.42% |
| Sharpe | −0.260 | −0.086 | 1.456 | 2.270 |
| R² vs asset mean | −0.748% | −0.198% | +1.411% | +1.244% |
| Mean cross-sectional IC | −0.0437 | +0.0194 | +0.0819 | **−0.0129** |
| Directional accuracy | 54.18% | 53.09% | 56.38% | 56.16% |
| Mean daily turnover | 0.4900 | 0.4819 | 0.7135 | 0.7459 |
| Mean viable features | 3,013 | 2,964 | 3,040 | 2,991 |

The strict variant improves net-return point estimates without uniformly improving forecast quality. Its 2026 IC changes sign, R² declines slightly, and turnover rises. This is an important research finding, not an inconvenient result to omit. It suggests testing how aggregate direction, threshold crossings and position allocation change; it does not by itself identify the mechanism.

Strict-minus-selected daily-return intervals are **+0.90 bps [−3.26, +4.71]** in 2025 and **+4.47 bps [−4.26, +14.56]** in 2026. Both cross zero. The strict variant cannot yet be called statistically superior or a proven remedy for leakage. Removing known fallback flags addresses a defined sensitivity, not every point-in-time problem.

The paired selected-minus-cohort-timing comparison is similarly inconclusive: **+0.63 bps/day [−2.27, +3.49]** in 2025 and **−3.33 [−10.47, +3.61]** in 2026 at the primary 10-session block. The report now states this correctly. Inference completion closes the analysis gap; it does not require the result to become significant.

## 5. Remaining gaps: precise changes and acceptance criteria

### G01 — High priority: verify the actual document claims, not just the registry

**Where:** `scripts/verify_report_release.py`; Abstract page 3; Appendix A verification assurance.

**Confirmed test:** In a copied DOCX, the abstract's 2025 return was changed from `-4.04%` to `99.00%`. The registry still pointed to the correct artifact claims and original PDF. The verifier returned **PASS, 225/225, exit 0**. Its new claims layer validates artifacts against registry expectations, but does not validate displayed DOCX values or DOCX/PDF consistency.

**Change:** Bind report claims to stable claim IDs or document bookmarks/content controls. Extract their displayed values and compare with registered source selectors, units and rounding tolerances. Register strict-vintage, paired-inference, annualization and principal hypothesis claims as well as the existing headline values. Verify final PDF text against the same claims after rendering. Preserve source and final-output manifests separately.

**Acceptance:** A false return introduced into either DOCX or PDF is rejected; a missing required claim fails; the untouched report passes. Retain the existing four successful negative controls. This finding does not imply the current report contains 99%; only the audit copy does.

### G02 — High priority: retain the strict 2026 predictions needed to reproduce forecast metrics

**Where:** `scripts/run_strict_vintage_sensitivity.py`, approximately lines 320–375; strict analysis A8/E12.

**Confirmed gap:** The script creates `predictions_2026` in memory, evaluates it, and persists metrics, ledgers and diagnostics, but does not write that 2026 prediction table. The analysis directory has 2025 prediction checkpoints; it has no corresponding persisted 2026 strict predictions. Consequently the strict 2026 R², IC and directional accuracy cannot be independently recomputed from the saved strict forecast rows without refitting. The saved ledgers do support return/accounting checks.

**Change:** Persist both strict-model and asset-mean predictions with date, asset, target, prediction, configuration and reference-baseline keys; store 2026 importance if it will be cited. Add output hashes and parent dataset/config links. Do not fabricate missing rows from aggregate metrics. If regeneration is needed, use exact pinned source snapshots and a new analysis ID; compare regenerated aggregates before adopting it.

**Acceptance:** A separate read-only verification command reproduces strict R², IC, directional accuracy, trading decisions and returns from saved predictions. Assert unique date/asset/config keys and exact matched evaluation dates.

### G03 — High priority: fix Figure 5's evidence address and fresh-build dependency

**Where:** §4.1 page 7 ends “Analysis record: Appendix E8”; Figure 5 page 8; Appendix E8 pages 20–21; `progression_quarters()` in the figure builder.

**Confirmed mismatch:** E8 names `information_ladder_final_test_20261101T030705Z_4fcf7b07672b`, the older single-period ladder. The expanded five-year figure and quarterly-means paragraph use `artifacts/report_reviews/feature_progression_20261101/quarterly_feature_progression.csv`. The builder hardcodes that directory. The README build sequence does not show how to create this prerequisite.

**Change:** Promote the progression audit to a proper timestamped analysis artifact, register its ID, update E8 and the figure source mapping, and remove the hardcoded review-folder dependency. Document `audit_report_feature_progression.py` before the figure build. Export the annual plotted matrix as well as quarterly inputs. Explain that the paragraph averages quarterly R² while the figure pools squared errors within each year; the two need not numerically coincide.

**Acceptance:** E8 resolves to the exact plotted source. A fresh documented build creates it without a preexisting review folder. Annual matrix equals `1 − sum(SSE)/sum(baseline SSE)`, not an unweighted mean of quarterly R². The present code uses the correct pooled calculation; this is a traceability/communication issue, not a discovered calculation error.

### G04 — High priority: interpret the strict variant's forecast/trading trade-off

**Where:** §5.3 page 11, Abstract page 3, §§8.2–8.3 pages 17–18.

**Gap:** The main sensitivity table emphasizes return improvement and feature counts. It omits the 2026 IC decline from **+0.0819 to −0.0129**, R² decline and turnover increase. These qualify what “improves” means.

**Change:** Add a compact forecast-and-trading panel using the metrics in §4 above. State that net returns improve while forecast-quality measures are mixed. Compare strict versus selected aggregate forecast direction, trade count, threshold crossings, per-stock weights and contribution. Explain why removing 60 columns reduces mean *viable* counts by 49: excluded dictionary columns and post-filter input counts are different quantities; validate the per-refit counts before attributing a cause.

**Acceptance:** Every “improvement” claim identifies its metric; no inference that all predictive quality improves. Strict remains a post-selection sensitivity, not a newly untouched winning model.

### G05 — High priority for the research claim: perform selected-family source ablations

**Where:** §8.1 page 17 says matched group ablations are required; §6.2 page 14 says incremental cross-market value remains unresolved.

**Gap:** The ridge ladder tests information expansion under a fixed linear specification. Strict-vintage exclusion tests fallback-flagged inputs. Neither establishes the selected Extra Trees model's incremental use of U.S. services or AI inputs.

**Change:** Fix depth 6, 250 trees, leaf 40, max features 0.5, seed, dates, windows and trading rules. Compare F0, F2, F7, F7-minus-U.S.-services and F7-minus-AI, removing related interactions consistently. Include the asset-mean baseline and matched-date paired differences. Archive separately as retrospective ablation; do not promote a new winner on the same evaluation periods.

**Acceptance:** Source-linked feature lists, counts and Δforecast/Δtrading metrics with uncertainty. Null results are acceptable and should simplify the economic story rather than trigger an unrestricted model search.

### G06 — Medium priority: reconcile the conclusion with unresolved analyses

**Where:** §8.3 ends, “The remaining evidentiary requirement is genuinely future observation after a prospective freeze.”

**Gap:** This sounds exclusive, while §§6.2 and 8.1 explicitly say source-group ablation is still required, and the report lacks portfolio contribution attribution.

**Suggested replacement:** “Remaining work includes matched source-group ablations, portfolio contribution and concentration analysis, and genuinely future evaluation under a prospectively frozen design.”

**Acceptance:** The conclusion agrees with the limitations and open evidence table. Do not describe prospective testing as the only remaining task.

### G07 — Medium priority: quantify attribution and concentration

**Where:** §6.2 “Monthly behavior, attribution, and uncertainty”, pages 12–14; Figures 9–11.

**Gap:** Long/short/flat counts and cost curves explain activity but not which holdings or days generate gains and drawdowns. The attribution table gives qualitative conclusions rather than reconciled P&L attribution.

**Change:** Add per-asset/per-side net contribution, top-five-day contribution concentration, largest drawdown start/trough/recovery and an underwater plot. Allocate costs with a stated rule. Use additive daily attribution or a declared geometric linking method rather than summing independently compounded stock returns.

**Acceptance:** Daily contributions sum to portfolio returns and costs. Explain whether 2026 gains survive removing the largest few profitable days as a sensitivity, without presenting that removal as a tradable rule. Prefer one combined figure replacing lower-value material.

### G08 — Medium priority: strengthen the paired-analysis audit contract

**Where:** `scripts/analyze_paired_strategy_differences.py`; paired artifact E11.

**Gap:** The current script inner-joins dates without `validate='one_to_one'` or an explicit full-coverage assertion; it records base seed 17 although the actual seed adds period/comparator/block offsets. The manifest hashes source ledgers but does not record the script hash. Current reported samples are the expected 249/185 dates; no date-loss error was observed.

**Change:** Reject duplicates/unmatched dates, persist effective seed or seed-derivation formula, record source code/environment hashes, and test identical-series zero differences plus deliberate missing-date/duplicate inputs. State that cohort timing is the closer exposure-matched comparison; the services-direction policy has its own exposure/activity profile. Include turnover/gross exposure already available in the CSV when interpreting differences.

**Acceptance:** Malformed joins fail rather than silently changing the sample; the saved interval can be reproduced with an unambiguous seed and code snapshot. Do not label the existing paired intervals “missing”; they are now implemented.

### G09 — Medium priority: finish immutable release and source provenance

**Where:** Same V2 filename/release directory now at revision 4; strict manifest `identity.registry_sha256`; final verification has `git_dirty: true`.

**Gap:** Current file hashes are valid, but a mutable V2 path plus dirty HEAD is not a recoverable source snapshot. The strict run records the earlier registry hash `09654222…`; the current revision-4 registry hash is `6e0a24f1…`. This difference is expected when the registry is updated after analysis, not proof of invalid results, but the exact input registry must be archived. The verifier checks strict output hashes/flags but does not resolve all strict input identity hashes against archived objects.

**Change:** Archive the analysis-input registry/config/code snapshots, use revision-specific release directories, hash the source diff or commit/archive the source, and validate strict parent links and input identities. Distinguish immutable analysis inputs from the later publication registry to avoid self-referential hash cycles.

**Acceptance:** Another machine can recover the exact input state by hash. Prior release files remain recoverable after later updates. No requirement to change the historical selected-run IDs merely because report formatting changes.

### G10 — Medium priority: report structure and specific figure improvements

**Where:** Current rendered PDF.

- **Figure 1, page 4:** simpler, legible and correctly connects fitting to forecasting. Keep this design. Add small labels distinguishing quarterly 2025 refits from the single 2026 fit, or an offline-training/daily-inference lane. Avoid implying model fitting occurs at every 08:55 decision. No need to restore decorative logos.
- **Figure 5, page 8:** valuable replacement for the single-period ladder. Export the matrix and add feature counts/pooled-error formula to supplementary metadata; label the fixed penalty prominently. Do not infer that Extra Trees or every penalty must behave similarly.
- **Figures 6–7, pages 8–9:** still a retrospective, limited Epoch-mapped subset. Consider moving one to supplementary material and using its space for paired-difference or contribution plots. Preserve unequal-horizon/noncausal caveats.
- **Headline performance table, pages 11–12:** keep the entire table together; two final rows currently continue on the next page.
- **Matched-policy table, pages 13–14:** move as one unit or pair it with the interval table; the last two policies appear on the following page.
- **H1–H6 table, pages 14–15:** keep together so the verdicts can be compared at once.
- **Appendix E, pages 20–21:** a short continuation occupies the last page. Reflow rather than globally shrinking text.

**Acceptance:** All pages remain readable at normal viewing size, tables have clear continuation headers where unavoidable, and the total remains 15–25 pages. Contact-sheet inspection showed no obvious major overlap; this is a layout refinement, not a claim that the current document is unreadable.

### G11 — Medium priority: add mechanism-oriented EDA rather than more price charts

**Where:** §3 and the current Figure 4 decision-aligned correlation matrix.

**Change:** On development dates, compare U.S. signals against Indian overnight gaps and subsequent intraday returns separately, including usable dates and uncertainty. This tests whether the apparent information is largely incorporated at the open. Add a compact input-freshness/coverage table by family, distinguishing known-time data from fallback-excluded sensitivity inputs. Tie each plot to one hypothesis.

**Acceptance:** Explicit horizons and information clocks, no causal interpretation from correlations, no unmarked reuse of 2025/2026 as development data. These are optional research-strengthening analyses, not mandatory extra graph counts.

### G12 — Required submission completion and publication limitations

**Where:** Team contribution statement page 18; registry `blocked_author_inputs`; assignment §§6–7.

The statement still lists names only. Authors must supply actual contributions, verify the 15–25-minute video and staff access/downloadability, confirm the submission group and required `Group_X_Report.pdf` filename, and check the source package. Do not infer that a video does not exist just because no URL is supplied here.

For publication, preserve the retrospective label. The November 2026 freeze occurs after both evaluated segments. A new prospective protocol must set windows, refit policy, costs, source inclusion and evaluation dates before observing outcomes. Current-cohort survivorship and opening-price execution assumptions remain limitations. More complex models are not a prerequisite; establish where the current design adds value first.

## 6. Agent execution plan and commands

1. **Before final release:** G01–G03 and G06. These improve correctness and traceability without changing the canonical model.
2. **Interpret the existing sensitivity:** G04 and G08; retain all existing uncertainty statements.
3. **Finish research diagnostics:** G05, G07 and G11 in separate analysis artifacts.
4. **Finish packaging:** G09–G10 and author-supplied G12.
5. **Later research:** prospectively registered evaluation; do not optimize repeatedly on the displayed retrospective periods.

Run from the repository root:

```bash
.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v

# Existing four controls should pass by rejecting each mutation.
.venv/bin/python scripts/test_report_release_negative_controls.py

# Isolated audit registry: verification output stays in the review directory.
.venv/bin/python scripts/verify_report_release.py \
  --release-registry artifacts/report_reviews/v2_2026-11-01_162650_SGT/registry_audit.json

# NEW acceptance defect: currently exits 0; after G01 it must reject the fake DOCX.
.venv/bin/python scripts/verify_report_release.py \
  --release-registry artifacts/report_reviews/v2_2026-11-01_162650_SGT/report_text_negative_registry.json

# Recreate the missing figure prerequisite in a NEW analysis destination.
.venv/bin/python scripts/audit_report_feature_progression.py \
  --registry reports/releases/project2_team16_v2_2026-11-01/release_registry.json \
  --output artifacts/report_reviews/feature_progression_recheck_new

# Inspect the strict-fit plan without starting a new fit.
.venv/bin/python scripts/run_strict_vintage_sensitivity.py \
  --release-registry reports/releases/project2_team16_v2_2026-11-01/release_registry.json \
  --plan-only
```

Do not blindly rerun strict training to obtain a higher score. First fix persistence and provenance requirements, then rerun only if needed to recover missing forecast-level evidence. Repeated post-selection fits remain diagnostic work. Re-running review commands can update audit outputs; copy the evidence directory first if preserving the original review state matters.

## 7. Source hashes and gap-analysis checksum

These SHA-256 hashes identify the reviewed inputs:

| Input | SHA-256 |
|---|---|
| V2 DOCX | `4c2336488f19d19b6ef931482ff9af6274a22a79ddb73f8e60ffe0c4e9c73af7` |
| V2 PDF | `8c7ba6e9d15ed02d32938ca6cf94f651808f9657e436c23fdcc87b556e3a5adc` |
| Project requirements | `66f0175dcfc155e67c922a38e53ce9f73f589c37d736a8b2eb4b7d5af4972220` |
| Revision-4 release registry | `6e0a24f13a5efa33035b86daf483ff31f1fb54aec86839bfc3d8dee5462991a6` |

Additional script/README hashes are in the audit directory's `source_hashes.json`. This Markdown's own checksum is stored in the adjacent **`.md.sha256` sidecar**, rather than embedded in the file it hashes. The sidecar is generated after the Markdown is finalized; subsequent edits invalidate it.

Verify from the repository root:

```bash
shasum -a 256 -c documents/markdown/Gap_Analysis_Report_V2_2026-11-01_162650_SGT.md.sha256
```

The score is **88/100 for this exact reviewed state**. The most valuable next improvement is complete claim-to-artifact traceability and a fuller explanation of what the new sensitivity does—and does not—demonstrate.
