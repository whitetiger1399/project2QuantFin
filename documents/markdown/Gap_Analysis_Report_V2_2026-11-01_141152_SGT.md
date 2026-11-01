# V2 gap analysis and agent improvement plan

**Review baseline:** 1 November 2026, 14:11:52 SGT (UTC+08:00).  
**Report:** `reports/Project2_Team16_Report_V2.docx`; companion PDF, 23 pages.  
**Requirements:** `documents/markdown/Project2.md`.  
**Release:** `project2_team16_v2_2026-11-01`.  
**Assessment:** **83/100 for the report and supporting project evidence**, up from 80/100 in the preceding reassessment. **Research-publication readiness: 68/100**, a separate judgment. These are reviewer estimates, not the instructor's grade; the supplied requirements give a 35-point overall component and do not prescribe the category weights below. The video and Canvas submission were not assessed.

V2 is a materially clearer and more defensible retrospective study. The headline returns reconcile, the contents pages are corrected, and several previously underreported diagnostics are now visible. It is not yet a fully reproducible final release: an input hash is stale, the release checker accepts deliberately invalid evidence, and the documented reproduction commands do not select V2. Scientific limitations remain even after these release defects are fixed. Negative returns are not themselves a grading defect: the assignment explicitly rewards sound process and interpretation.

## 1. Scope, evidence and score

Reviewed the full DOCX text/tables, requirements, release registry, report/figure builders, relevant configurations, saved run checks, and ledger evidence. Viewed all 23 PDF pages through contact sheets, with detailed images of pages 4, 12 and 23. Existing rendered PDF SHA256 matches the supplied companion PDF. This review did **not independently re-render the DOCX**, so visual observations refer to that matching PDF, not a fresh Word rendering. No report, model configuration or canonical result was changed; no model was retrained. Tests and audit evidence were written separately.

Evidence directory: [`artifacts/report_reviews/v2_2026-11-01_141152_SGT`](../../artifacts/report_reviews/v2_2026-11-01_141152_SGT). `review_identity.json` records source hashes, Git HEAD, review timestamps and visual scope. `report_extracted_text.txt` preserves the reviewed report wording. The working tree contains uncommitted release implementation changes; Git HEAD alone cannot reconstruct it.

| Category | Weight | Previous | V2 | Reason |
|---|---:|---:|---:|---|
| Research question and economic logic | 10 | 9 | 9 | Clear conditional hypothesis; avoids unsupported causal claims. |
| Data provenance, timing, leakage | 15 | 11 | 11 | Good availability-clock checks; 60 fallback-flagged features and current-member conditioning remain. |
| Feature engineering/preprocessing | 10 | 8 | 8 | Relevant lagged/context features and training-only transforms; selected-family empirical ablations remain absent. |
| Models, validation, selection | 15 | 12 | 13 | Selection contract now spells out candidate counts and settings. |
| Trading, costs, benchmarks | 10 | 8 | 9 | Matched policy table, exact ETF identities and fixed-holdings costs improve interpretation. |
| Evaluation/statistical inference | 15 | 12 | 13 | Calibration and uncertainty are now discussed; paired incremental-value inference remains missing. |
| EDA, figures, architecture | 10 | 8 | 9 | Better evidential captions and figures; calibration clipping and redundant price paths remain. |
| Structure and interpretation | 10 | 8 | 8 | Contents corrected; split tables, annualization ambiguity and incomplete contribution note remain. |
| Reproducibility/submission readiness | 5 | 4 | 3 | Actual adversarial-check failure, stale input hash and environment/reproduction defects. |
| **Total** | **100** | **80** | **83** | Stronger report; no new evidence of robust alpha. |

Publication readiness improves only modestly because the data, selected model and core performance evidence are unchanged. More diagrams or a more complex estimator cannot substitute for prospective validation, strict-vintage sensitivity and incremental-value tests.

## 2. Tests actually executed and results

The full discovered repository unit suite and applicable canonical-chain verifiers were executed. Check totals overlap; they must not be presented as hundreds of independent statistical validations.

| Check | Outcome | Saved evidence |
|---|---|---|
| `unittest discover -s tests -p 'test_*.py' -v` | **15 tests passed** across all four test files | `unit_tests.log` |
| AI capability pipeline verifier | **201 passed, 0 failed** | `pipeline_verification.json` |
| Frozen 2026 extension verifier | **28 passed, 0 failed** | `extension_verification.json` |
| Cross-market outputs/lineage verifier | **78 passed, 0 failed** | `cross_market_verification.json` |
| Capability data/ledger contract audit | **21 checks passed**; confirms 60 current-vintage fallback features | `contract_audit.json` |
| V2 release verifier, copied registry with isolated output | **90 passed, 0 failed** under its existing checks | `release_verification.json`, `registry_audit.json` |
| Release checker negative control | **Acceptance failure:** returns PASS/exit 0 after false return and nonexistent freeze are injected into a registry copy | `registry_negative_control.json`, `negative_control_verification.json` |
| Independent figure output **and input** SHA256 audit | **114 matched, 1 mismatch** out of 115 recorded entries | `figure_hash_audit.json` |
| Published DOCX/PDF vs saved release verification hashes | Both match | `review_identity.json` and canonical `verification.json` |
| Independently resolved contents destinations | All **18 headings match** the stored contents-page mapping | `toc_pages.json` |
| TOC resolver in project `.venv` | **Fails:** `ModuleNotFoundError: No module named 'pymupdf'` | Exact command in §6; succeeds using available system Python |
| Headline cumulative returns recomputed from selected ledgers | Reconcile to reported rounding | `recomputed_metrics.json` |

The passing unit suite covers accounting, initial-capital drawdown, downside deviation, feature exclusion, timing-only weights, cross-market timing, event calendar and hypothesis utilities. It does not test all report claims, document layouts, source citations or external execution assumptions. No fresh data download, complete training replay, clean-machine install, live website-link sweep or video accessibility test was performed. Older unrelated research-branch verifiers were not treated as V2 acceptance tests.

## 3. Numerical reconciliation and interpretation

Selected configuration: **`cm_extra_trees_cd9235695e6b`**, Extra Trees, 250 trees, depth 6, leaf size 40, max features 0.5, F7 full context. Canonical freeze: `cm_ai_capability_freeze_20261101T025756Z_b80ca3883e16`.

| Metric | 2025 replication | Jan–Sep 2026 extension |
|---|---:|---:|
| Sessions | 249 | 185 |
| Gross cumulative return, recomputed | 5.1569% | 26.9485% |
| Net cumulative return, recomputed | **−4.0384%** | **15.0141%** |
| Arithmetic sum of daily cost deductions | 9.1500% | 9.9000% |
| Annualized geometric net return, 252-session convention | **−4.0861%** | **20.9910%** |
| Saved annualized volatility | 12.8645% | 13.7383% |
| Saved net Sharpe | −0.2600 | 1.4557 |
| Saved R² versus asset mean | −0.7476% | 1.4114% |
| Saved mean cross-sectional IC | −0.0437 | 0.0819 |
| Saved 95% block-bootstrap Sharpe interval | [−1.883, 1.506] | [−1.577, 3.865] |
| Saved HAC alpha p-value | 0.8874 | 0.3028 |

Combined cumulative return is **10.3694%**, computed by compounding the two segments. The arithmetic cost sum is not the compounded gross–net wealth gap. The 2026 cumulative return is not an annualized return. Inference values above are saved-run outputs, not a new bootstrap run in this review.

The report correctly avoids claiming robust alpha. Both Sharpe intervals include zero, and the 2026 alpha test is inconclusive. The matched-policy table on page 15 is particularly important: the selected model's 2026 Sharpe is **1.456**, below cohort-mean signed timing **2.203** and U.S.-services-direction equal weighting **2.021**. These are descriptive comparisons, not proof that either alternative is statistically superior. A stock-selection contribution has not been established.

## 4. Pinpointed remaining gaps and agent actions

Priorities: **P0** = release/traceability defect to fix before declaring verification complete; **P1** = assignment completeness or central evidential issue; **P2** = useful research/presentation improvement. “Confirmed” means directly observed; “not established” means missing evidence, not proof of an implementation error.

### V2-01 — P0 — Release verifier accepts invalid lineage and false claims [confirmed]

**Location:** `scripts/verify_report_release.py`; Appendix A, page 21, verification assurances.

**Evidence:** In a copy of the release registry, `FREEZE_ID` was set to `NONEXISTENT_FREEZE_NEGATIVE_CONTROL` and `claims.return_2025_net` to `0.99`. The checker still returned 90 passed, zero failed and exit 0. Canonical files were untouched. Source inspection confirms the checker does not validate the freeze or recompute that numeric claim. The canonical lineage separately passes the stronger pipeline verifier; this finding does not mean the actual freeze is missing.

**Change:** Validate dataset → screening → confirmation → freeze → final → extension links and their hashes. For each registered claim, specify artifact path, configuration selector, column/aggregation, unit, precision and tolerance; recompute and compare. Fail closed on missing IDs and unknown required fields. Run separate negative tests for wrong freeze, wrong config, changed source file and altered numeric claim.

**Acceptance:** Each single mutation exits nonzero with a useful diagnostic; untouched canonical evidence passes. Appendix A reports exactly which verifier checks what. Do not merely increase a check counter.

### V2-02 — P0 — Figure manifest contains a stale report-builder hash [confirmed]

**Location:** `reports/publication_figure_pack_v2_2026-11-01/manifest.json`, `inputs["reports/build_report_ai_capability.py"]`.

**Expected SHA256:** `5d1ca2026d3cb3214d881ad5a8d39d180049f95940e85657a9c2c7c7f799bdf4`.  
**Actual SHA256:** `a47eb17562a441b2f0827512b9cbf666c8c64c3a2ba955eb7ab2eb5d03bca025`.

All other recorded figure input/output hash entries match. The release checker checks figure files but misses this input mismatch. Current DOCX/PDF hashes do match their final verification record; the older “published document hash is stale” issue is therefore closed, while source provenance remains open.

**Change:** Freeze source changes first; regenerate the figure pack, rebuild the report, resolve contents after rendering, then verify every input and output hash. Preserve the old release and publish a new release identity. Record hashes for publication sections, registry loader, report builder and figure builder, plus environment and source snapshot/patch; a dirty HEAD alone is insufficient. Avoid self-referential hash cycles by separating build-input and final-output manifests.

**Acceptance:** Zero input/output mismatches; rebuilding from the recorded source snapshot produces semantically identical figures, claims and page references. Do not repair this by editing the expected hash without rebuilding/verifying the affected outputs.

### V2-03 — P0 — Published reproduction commands default to V1 [confirmed]

**Location:** Appendix E, page 23, final two command lines; `README.md`; `reports/report_release.py`.

Appendix E says only `python scripts/build_publication_figure_pack.py` and `python reports/build_report_ai_capability.py`. The registry loader requires `REPORT_RELEASE_REGISTRY`; without it the builder's default DOCX is `reports/Project2_Team16_Report.docx`. The README has no V2 registry instruction. The TOC resolver also imports PyMuPDF, absent from both `requirements.txt` and `pyproject.toml`, and fails in `.venv`.

**Change:** Add a V2/new-release build recipe with explicit registry, interpreter, dependencies, render tools, contents-resolution pass and final verification. Declare a tested compatible PyMuPDF version in the reporting environment and document LibreOffice/Poppler requirements as applicable. Build into new versioned outputs. Include expected filenames, page count, IDs and semantic checks. Preserve a tested environment lock/snapshot.

**Acceptance:** A clean environment follows the README and generates the intended version without relying on system Python packages, hidden environment variables, or `/tmp` assets. The figure/report/TOC/verification sequence is documented in full.

### V2-04 — P1 — Cumulative versus annualized return needs explicit reporting [confirmed]

**Location:** Section 6.1 page 13 segment metrics; Figure 15 page 17 caption says “Annual net returns” while 2026 ends in September. Requirement §4.9 asks for annualized return, volatility and Sharpe.

**Change:** Add separate columns for period cumulative return and geometric annualized net return, with 249/185 sessions and formula `prod(1+r)^(252/n) − 1`. Display −4.09% and +20.99% as annualized values; retain −4.04% and +15.01% as cumulative values. Rename Figure 15 to “Calendar-period net returns; 2026 through September” and its caption accordingly. Label benchmark conventions identically.

**Acceptance:** No reader can mistake +15.01% for annualized return; the new annualized columns agree with the selected leaderboard and ledger calculation. Annualizing a short sample is a scaling convention, not a forecast.

### V2-05 — P1 — Figure 10 clips calibration uncertainty [confirmed]

**Location:** Figure 10, page 12; `scripts/build_publication_figure_pack.py`, `forecast_calibration`, approximately lines 460–478.

The axis bound uses only means and predictions, excluding error-bar endpoints. The 2026 lowest mean-minus-one-SE is **−1.1386%**, beyond the displayed lower axis. The plotted lower whisker is visibly cut off.

**Change:** Determine shared limits from both panels' `x`, `y−SE` and `y+SE`, with padding; test that every endpoint is inside the axes. Keep the caption's honest “one date-clustered standard error” wording. Add bin observation/date counts in a compact supplement. Consider points without connecting lines to avoid implying a fitted calibration curve.

**Acceptance:** All error bars visible; exported data and plotted means/errors match exactly. Date-clustered SE should not be relabeled a serial-dependence-robust confidence interval. For inferential calibration, use a separate date-block calculation.

### V2-06 — P1 — Strict-vintage sensitivity is configured incorrectly for the selected model [confirmed configuration mismatch; empirical effect unresolved]

**Location:** Abstract; §§2–3 and 8.2; `configs/cross_market_ai_capability_research.yaml`, `gap_diagnostics`, approximately lines 52–83.

Contract audit confirms **60 fallback-flagged features** in the dictionary. All six diagnostic Extra Trees configurations use `max_depth: 8`, while the selected model has depth **6**. A depth-8 reference/strict comparison would test a different estimator. The profile also has `include_standard_components: false`; explicit forecast baselines must be checked/added for interpretable R² comparisons.

**Change:** Create a new diagnostic profile derived from the exact depth-6 selected specification. Compare full F7 versus excluding flagged features on identical dates, seeds, rolling windows, costs and baselines. Record actual excluded columns/counts and availability assumptions. Archive results as post-selection sensitivity, not a replacement untouched test. Correct release-lag/revision exposure upstream if strict point-in-time macro reconstruction is feasible.

**Acceptance:** Manifest records depth 6 and exact parent configuration; strict feature list has zero fallback flags; report shows paired metric changes and uncertainty. A passing feature-exclusion unit test is not an empirical robustness result. Excluding flags alone does not establish that every remaining feature is point-in-time correct.

### V2-07 — P1 — Timing versus stock selection remains unresolved [missing inference]

**Location:** Section 6.2 matched-policy table, page 15; conclusion page 19.

**Change:** Reuse existing matched daily ledgers. Join on identical dates; preserve flat sessions and identical cost assumptions. Bootstrap paired model-minus-comparator daily returns in date blocks, using the same sampled dates for both policies. Report differences in mean net return and Sharpe with intervals for selected model versus cohort-mean timing and U.S.-services timing. Prespecify block lengths and sensitivity; do not choose a block length because it produces significance. Also report turnover/exposure differences so “stock selection” is not confused with different risk budgets.

**Acceptance:** A source-linked comparison CSV, method/seed/block length metadata and a difference-with-interval figure. Retain “incremental stock-selection value not established” if intervals cross zero. No claim of dominance from point estimates alone.

### V2-08 — P1 — Selected-family information ablation is still missing [missing evidence]

**Location:** Figure 6 page 8 uses fixed **ridge**, while the selected model is Extra Trees; Figure 19 page 23 shows permutation reliance.

**Change:** At fixed depth-6 Extra Trees settings, compare F0, F2, F7, F7-minus-U.S.-services and F7-minus-AI, including forecast baselines. Use the same sample and prediction coverage. Show ΔR², Δnet return/Sharpe and feature counts, with paired uncertainty where feasible. Record group membership to avoid leaving AI interactions in the supposedly AI-free variant.

**Acceptance:** Selected-family ablation table and one compact plot, explicitly retrospective. Do not present permutation importance as the result of retraining without a feature group. Correlated predictors can complicate permutation interpretation; see the [scikit-learn primary documentation](https://scikit-learn.org/stable/auto_examples/inspection/plot_permutation_importance_multicollinear.html).

### V2-09 — P1 — Contributions and submission package remain incomplete [confirmed/report; external items unverified]

**Location:** “Team contribution statement”, page 19, contains a roster only; release registry lists blocked author inputs. Requirements §§6–7 request a contribution note, 15–25-minute video, source package/link and `Group_X_Report.pdf`.

**Change:** Authors supply truthful roles and review responsibilities. Confirm Canvas group number and create the corresponding submission filename (for group 16, `Group_16_Report.pdf`, only after confirming the group). Verify the video duration, staff access and downloadability, and code/environment package completeness.

**Acceptance:** Actual contributions, accessible video and reproducible package recorded in a submission checklist. Do not fabricate roles or infer that a missing video URL in the report proves no video exists elsewhere.

### V2-10 — P2 — P&L attribution remains too coarse [missing analysis]

**Location:** Figures 11–13, pages 13–15. Costs/exposure are now well described, but the report does not identify which assets/sessions/side account for performance and drawdown.

**Change:** Derive per-asset and long/short daily contribution from saved predictions/weights and reconcile to the portfolio ledger. Show gross contribution, allocated trading costs and net contribution, top-five-day concentration, worst drawdown dates/duration and recovery. Specify a cost allocation rule. Use arithmetic daily attribution or a stated geometric linking method; do not sum independent compounded asset returns into portfolio cumulative return.

**Acceptance:** Contributions reconcile numerically, and the text explains whether results depend on a few shorts or events. Replace a repetitive price-path chart with a contribution chart and underwater panel.

### V2-11 — P2 — EDA should test the information mechanism more directly [improvement]

**Location:** Figures 2–3 page 6 repeat price-path context; Figure 5 page 7 is more directly relevant.

**Change:** Keep Figure 2 or move Figure 3 to a supplement. Add development-period U.S.-signal associations separately with Indian overnight gap and intraday return, with clear calendars/horizons and date-based uncertainty. Add feature freshness/coverage by family and vintage status. Report effect magnitudes and usable date counts, not only colour intensity. Any 2025/2026 breakdown is retrospective diagnostic evidence.

**Acceptance:** New plots answer whether information is already incorporated at the open and how stale inputs are. Avoid adding decorative heatmaps without a decision-relevant question. Appendix B page 21 still claims “seasonality” under Section 3 although the main text disclaims a tested calendar effect: remove that alignment claim or cite the exact available analysis and its limited interpretation.

### V2-12 — P2 — Architecture and layout can communicate dependencies more accurately [visual improvement]

**Location:** Figure 1 page 4; tables crossing pages 4–5, 7–8 and 12–13.

The architecture is legible and much improved, but feature engineering and model validation appear as parallel branches both feeding prediction; the model's dependence on transformed features is not explicit. “Vintage checks” can look stronger than the unresolved fallback policy warrants.

**Change:** Draw a clear feature → train/validate → frozen estimator → forecast dependency. Separate offline fitting/selection from daily inference using two lanes, and label the 2025 quarterly versus 2026 fixed-fit protocols. Add a concise “60 fallback-flagged features; strict sensitivity pending” note near the input gate. Keep retrospective Epoch analysis outside the trading path. Standardize arrow widths, padding and alignment; use provider marks as secondary identifiers. Place the source table and F0–F7 table together or repeat headers across pages; keep the Section 6 headline table together if possible.

**Acceptance:** A reader can follow the actual computation without guessing; no clipped labels, stranded first rows or unexplained parallel data paths. Keep within the required 15–25 pages by replacing redundant material, not shrinking all text.

### V2-13 — P2 — Method/source citation traceability is not yet complete [improvement; not a claim that sources are false]

**Location:** §7.1 page 16, Figure 19 page 23, references page 20, company discussion §7.5 pages 18–19.

Extra Trees, Newey–West and Holm citations are now present, and the Kelly page range is corrected. The circular-block bootstrap still needs a direct method reference and explicit block length/repetition/seed details near its use. Distinguish whole-date permutations from multi-day temporal blocks. Archive precise provider announcement and company-document addresses, retrieval dates, quoted claim locations and content hashes where permitted; do not rely only on a generic website citation.

**Change:** For the existing circular-block method cite the matching original method, e.g. Politis and Romano's 1992 circular block-resampling work listed on the [author's publication page](https://mathweb.ucsd.edu/~politis/DPpublication.html). Do not cite a stationary-bootstrap method as if it were the identical algorithm. Add a citation/claim register for factual claims and quantitative table entries. Treat whole-date permutation SD as descriptive dispersion, as the current caption correctly does.

**Acceptance:** Every important empirical statement resolves to a saved artifact row or a specific source passage. This review did not re-open every corporate source; those disclosures are not newly externally verified here.

### V2-14 — P1 for publication — No genuinely prospective evidence yet [known limitation]

**Location:** §§5.2, 6 and 8; Figure 15. The freeze is dated November 2026, after both displayed evaluation segments. The report appropriately calls them historical replication/retrospective extension.

**Change:** Preserve that language and the original result. If pursuing publication, register the next design before observing its evaluation outcomes, log the research search history and collect genuinely unseen dates. Specify refit frequency, cost model, inclusion rules and stopping/reporting dates in advance. A new model explored now must remain a separate research branch.

**Acceptance:** Timestamped prospective protocol and future predictions made under it, or an explicit statement that the study remains retrospective. No retrospective relabeling can close this gap.

## 5. What V2 has already fixed

Do not spend another iteration redoing these without new evidence:

- Contents page destinations are nonzero and all 18 match independently resolved headings; PDF is 23 pages, within the assignment range.
- DOCX/PDF hashes now match the saved release record.
- Exact selected parameters, selection counts, seed/software context and 2026 fitting window are substantially clearer.
- Calibration evidence, matched policy comparisons and benchmark identities are now in the report.
- Figure 17 now correctly shows the approximately **8.25 bps** 2025 and **36.21 bps** 2026 fixed-holdings break-even costs.
- Figure 19 correctly distinguishes descriptive permutation variability from confidence intervals and causality.
- References now include Extra Trees/HAC/Holm; the conclusions retain appropriate limitations.

Earlier action-plan labels such as “implemented” should mean implemented presentation, not necessarily resolved research uncertainty. In particular, adding the matched table did not complete paired inference; adding a strict-vintage configuration did not run the correct selected-model sensitivity.

## 6. Concrete commands and execution sequence

Run from the repository root. These commands verify existing evidence; they do not retrain or silently replace the release.

```bash
.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v

.venv/bin/python scripts/verify_cross_market_outputs.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --dataset-id ai_capability_panel_20261101T012801Z_ff277b55597d727a \
  --analysis-run-id analysis_20261101T013012Z_d50423d05d5c \
  --screening-run-id cm_ai_capability_screening_20261101T013231Z_038064c84d36 \
  --confirmation-run-id cm_ai_capability_confirmation_20261101T020346Z_327cf6e7c3bd \
  --freeze-id cm_ai_capability_freeze_20261101T025756Z_b80ca3883e16 \
  --final-run-id cm_ai_capability_final_test_20261101T025817Z_30ebf00d8090

.venv/bin/python scripts/verify_frozen_2026_extension.py \
  --run-id cm_ai_capability_2026_forward_20261101T030225Z_6a066bcfcc82

.venv/bin/python scripts/verify_report_release.py \
  --release-registry artifacts/report_reviews/v2_2026-11-01_141152_SGT/registry_audit.json

# Negative control: currently incorrectly returns success.
# After V2-01 is fixed, this must fail.
.venv/bin/python scripts/verify_report_release.py \
  --release-registry artifacts/report_reviews/v2_2026-11-01_141152_SGT/registry_negative_control.json
```

Both copied registries direct verifier output into the review folder; rerunning will update those audit outputs, not the canonical release verification. Preserve the original review evidence before retesting changed code.

Reproduce the missing-environment-dependency failure:

```bash
.venv/bin/python scripts/resolve_report_toc_pages.py \
  --docx reports/Project2_Team16_Report_V2.docx \
  --pdf reports/Project2_Team16_Report_V2.pdf \
  --output /tmp/project2_v2_toc_recheck.json
```

This review successfully resolved headings with available `python3`; that is a diagnostic workaround, not a clean-environment solution. Fix the dependency declarations and rerun through `.venv`.

For the future build recipe, the missing selector is:

```bash
export REPORT_RELEASE_REGISTRY=reports/releases/project2_team16_v2_2026-11-01/release_registry.json
```

Do **not** immediately run the builders against that archived output: copy the registry to a new release directory, change all output destinations and release identity, then set the variable to the new registry. Execute figure build → DOCX build → PDF render → contents resolve → DOCX rebuild/re-render if destinations changed → final hash/claim verification. Add exact rendering commands from the tested local reporting toolchain to the README; the two existing appendix commands are not the whole workflow.

For modeling, first fix V2-06/V2-08 in a new diagnostic configuration. Inspect the enumerated design before any fit:

```bash
.venv/bin/python scripts/run_cross_market_experiments.py \
  --config configs/cross_market_ai_capability_research.yaml \
  --dataset-id ai_capability_panel_20261101T012801Z_ff277b55597d727a \
  --stage screening --profile gap_diagnostics --plan-only
```

As currently configured, this is the depth-8 design, **not an approved selected-model robustness experiment**. Adapt the command to the corrected copied configuration. Plan-only does not execute the ablation. Do not reselect a “better” model on 2025/2026 and continue calling those periods untouched tests.

Recommended order:

1. **Release correctness:** V2-01–03, with regression/negative tests and a source snapshot.
2. **Report correctness/completeness:** V2-04–05, V2-09, residual seasonality claim and layout fixes.
3. **Use existing results better:** V2-07 and V2-10; these chiefly need saved-ledger analysis, not new models.
4. **Run controlled research sensitivities:** V2-06 and V2-08, keeping the canonical release intact.
5. **Improve explanatory evidence:** V2-11–13; replace redundant charts rather than growing beyond 25 pages.
6. **Publication extension:** V2-14. Consider alternative models only after a defined failure mode motivates them. Existing AR, ridge, sparse linear, PCA, boosting and tree families already provide substantial model diversity; adding an LSTM/transformer is not a requirement or an evidence-backed shortcut.

## 7. Release acceptance checklist

- [ ] All discovered unit tests and applicable chain verifiers pass.
- [ ] Incorrect freeze, altered claims, stale inputs and wrong configuration each fail their own negative test.
- [ ] Every required figure input/output hash matches; final source snapshot is recoverable.
- [ ] Clean environment reproduces the correct release using only documented commands.
- [ ] Cumulative and annualized returns are separately labeled and reconciled.
- [ ] Figure 10 uncertainty is fully visible; tables and contents survive final rendering.
- [ ] Claims/figures/tables resolve to artifact selectors, units, methods and IDs.
- [ ] Remaining research sensitivities are completed or explicitly labeled unresolved, with no unsupported alpha/causal claim.
- [ ] Actual contribution note, submission filename, video and code package are checked by the authors.

**Decision:** V2 is a strong course-project report in progress, with credible negative and conditional findings. It is not yet a fully verified release or a demonstrated robust trading edge. Fixing the concrete release, graph and reporting defects should precede another model search.
