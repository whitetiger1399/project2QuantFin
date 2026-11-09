# Project 2 Team 16 — Version 2 implementation ledger

Release ID: `project2_team16_v2_2026-11-01`  
Release registry: `reports/releases/project2_team16_v2_2026-11-01/release_registry.json`  
Verification time: `2026-11-01T06:10:28.039865+00:00`  
Verification result: **PASS — 90 passed, 0 failed; 23 pages**  
Git evidence: HEAD `9dc39aff5a503a5bd308c243634bac48381e7964`; the release records that the worktree was dirty at verification time.

## Preservation and output identity

The original report was not edited:

| Artifact | SHA-256 |
|---|---|
| `reports/Project2_Team16_Report.docx` | `854695f7ee0ed436b0bf91a0f9467cacb21f140db758579b590d7d7a5ee32866` |
| `reports/Project2_Team16_Report.pdf` | `6ff43414a676c1e2dfc5941a5723922f380bd2ffb5091e1861db33b2b86e8306` |

Version 2 outputs:

| Artifact | SHA-256 |
|---|---|
| `reports/Project2_Team16_Report_V2.docx` | `e21629dc964f63a91b0055b07a0a1969fa40eab9f617eb7c7f5f97c7d5b1a722` |
| `reports/Project2_Team16_Report_V2.pdf` | `deb276c8ed51addb84e30010953d291fbb501cdfa122ea7f032dac0489552c4e` |

The V2 build is bound to the immutable IDs in the release registry, including dataset `ai_capability_panel_20261101T012801Z_ff277b55597d727a`, 2026 dataset `ai_capability_2026_panel_20261101T012848Z_7f83e6f3f4f128f8`, selected configuration `cm_extra_trees_cd9235695e6b`, historical run `cm_ai_capability_final_test_20261101T025817Z_30ebf00d8090`, and extension run `cm_ai_capability_2026_forward_20261101T030225Z_6a066bcfcc82`.

## Action disposition

| ID | Applicability and status | Implemented change and verification | Remaining limitation |
|---|---|---|---|
| R01 | Applicable — **verified** | Added a two-pass heading-to-page resolver, rebuilt the cached contents, and failed verification on zero destinations. All 18 entries resolve to non-zero pages. | None for this release. |
| R02 | Applicable — **verified** | Added a typed release registry and a failing verifier for manifests, parent dataset/config consistency, figure hashes, report hashes, page count and contents. | The registry protects this V2 release; it does not rewrite immutable legacy run manifests. |
| R03 | Applicable — **verified** | Rebuilt the fee-sensitivity figure from the saved ledger. At 15 bps, 2025 is −4.04% net; fixed-holdings break-even is 8.25 bps for 2025 and 36.21 bps for Jan–Sep 2026. | The curve is explicitly a fixed-holdings sensitivity, not a policy re-optimization. |
| R04 | Applicable — **verified** | Replaced “2025 is flat,” corrected the gross-to-net interpretation, stated the actual 2026 training window (25 Nov 2020–30 Dec 2025), and relabeled the periods as historical replication and retrospective extension. | These periods remain historically inspected; no pristine holdout claim is made. |
| R05 | Applicable — **verified** | Rebuilt group reliance directly from the pinned importance CSVs using the exact `oos_date_block_group_permutation_mse_increase` rows. Captions now say whole-date group permutation and describe variability as descriptive SD, not a confidence interval. | Permutation reliance is predictive sensitivity, not causal attribution. |
| R06 | Applicable — **verified** | Repaired short-table pagination, preserved readable plot sizing, inserted calibration evidence, and visually inspected all 23 rendered pages. | Page layout can still vary if opened with a non-LibreOffice renderer; the supplied PDF is canonical. |
| R07 | Applicable — **verified** | Named ITBEES.NS and NIFTYBEES.NS, their INR adjusted close-to-close semantics, overnight exposure, raw snapshot, and confirmed that no fallback ticker was used. | Passive benchmark timing is not execution-matched to the intraday strategy and is labeled accordingly. |
| R08 | Applicable — **verified** | Added artifact-derived stage counts (25/13/12/4), coverage threshold, ranking/tie-break contract, rolling window, embargo, seed, package versions, family settings and RFF exclusion status. | Capacity proxies are not presented as exact independent parameter counts. |
| R09 | Applicable — **implemented** | Centralized release IDs, paths and headline values; report, figure pack and appendix resolve through the same registry or fail. | A fully exhaustive row-selector registry for every sentence and every externally sourced company fact remains future engineering work. |
| R10 | Applicable — **blocked by author input** | Preserved the complete author roster and documented the unresolved items in the release registry. | Truthful individual roles, final video URL/access check and required submission filename must be supplied by the team. |
| A01 | Applicable — **implemented** | Added the saved timing-versus-selection comparison with definitions and correctly limited inference. | Paired date-block uncertainty for selected-minus-timing daily returns was not present in saved evidence and was not manufactured. |
| A02 | Applicable — **implemented and verified** | Added artifact-derived calibration bins, numerical ordering, thresholds and descriptive directional-baseline uncertainty. | A prospectively trained majority-sign comparator is still desirable for a future run. |
| A03 | Applicable — **partially implemented** | Added gross/net/cost interpretation, fee break-even analysis, turnover/exposure context and explicit fixed-holdings caveat. | Full side/asset P&L reconciliation, top-day concentration and a dedicated drawdown panel remain open diagnostics. |
| A04 | Applicable — **partially implemented** | Removed the unsupported calendar-effect claim and retained only evidence-backed development diagnostics and cross-market plots. | A new overnight-versus-intraday mechanism panel and fuller feature-age/coverage panel were not produced in this no-refit release. |
| A05 | Applicable — **verified** | Reconciled effect sizes, units, sample scopes, raw/adjusted inference and not-estimable capability tests; added method references. | Findings remain associational and retrospective. |
| M01 | Scientifically applicable — **deferred** | No model was refit and no canonical artifact was changed. The strict-vintage diagnostic remains a separately predeclared future experiment. | Must reproduce the depth-6 reference, include valid baselines and compare matched dates before reporting. |
| M02 | Scientifically applicable — **deferred** | Not run because it depends on the repaired M01 diagnostic profile and would create new fitted evidence. | Requires fixed-capacity, identical-date ablations with exact feature inventories. |
| M03 | Conditionally applicable — **deferred** | No extra model family was added merely to improve the inspected result. | Only trigger after a diagnosed failure mechanism and a prospective decision rule. |
| CITE01 | Applicable — **verified** | Corrected the Kelly, Malamud and Zhou page range to 459–503. | None. |
| CITE02 | Applicable — **verified** | Added citations for Extra Trees, Newey–West HAC and Holm multiplicity control. | None. |
| CITE03 | Applicable — **partially implemented** | Retained traceable source locators and separated external evidence from experimental claims. | External web pages were not all independently archived into immutable local captures in this release. |
| CITE04 | Applicable — **implemented** | Added named snapshot/ticker lineage and explicit event-selection provenance in the main report and evidence appendix. | Provider data licensing and future event-calendar maintenance remain operational responsibilities. |

## Files changed or added

- `reports/build_report_ai_capability.py` — V2 output binding, cover marker, revised sections and report facts.
- `reports/publication_report_sections.py` — release-bound inputs, methodology/benchmark sections, appendix and contents support.
- `scripts/build_publication_figure_pack.py` — V2 calibration, fee sensitivity and direct group-reliance figures.
- `reports/report_release.py` — shared registry/path/hash helpers.
- `scripts/resolve_report_toc_pages.py` — rendered-page contents resolver.
- `scripts/verify_report_release.py` — release integrity and publication acceptance gate.
- `reports/releases/project2_team16_v2_2026-11-01/release_registry.json` — canonical IDs, outputs, headline claims and blocked inputs.
- `reports/publication_figure_pack_v2_2026-11-01/` — 19 release-bound figures and manifest, revision-2 content hash `b25b3277ee4a29ab`.
- `reports/Project2_Team16_Report_V2.docx` and `.pdf` — final V2 artifacts.

## Reproduction and verification commands

The release was built and checked with the project virtual environment. The registry prevents “latest directory” discovery from silently mixing releases.

```bash
cd /Users/whitetiger/Desktop/WhiteTiger/17_projects/24_Project2_QuantFin/project2QuantFin
source .venv/bin/activate

export REPORT_RELEASE_REGISTRY=reports/releases/project2_team16_v2_2026-11-01/release_registry.json

python scripts/build_publication_figure_pack.py \
  --output reports/publication_figure_pack_v2_2026-11-01

python reports/build_report_ai_capability.py

python scripts/verify_report_release.py \
  --release-registry reports/releases/project2_team16_v2_2026-11-01/release_registry.json
```

The DOCX was rendered to PDF and all 23 pages were inspected at final size. The final machine-readable result is `verification.json`; it records 90 passing checks, zero failures, output hashes, Git state and page count.

## Acceptance conclusion

The plan's applicable no-refit report, provenance, citation and visualization repairs are included in V2 without modifying V1. The release intentionally does **not** represent M01–M03 or the author-dependent R10 items as complete. Those items require new experiments or team-supplied evidence and therefore remain visible rather than being silently inferred.

## Revision 2 — response to `Gap_Analysis_Report_V2_2026-11-01_141152_SGT.md`

Verified on 1 November 2026 after the first V2 review. This revision overwrites only the V2 deliverables; V1 remains unchanged.

### Implemented and verified

- **V2-01:** The release verifier now validates dataset→screening→confirmation→freeze→final→extension identities, parent hashes, the selected configuration, paired-analysis inputs, every figure input/output hash, and every structured registered claim. Adversarial tests confirm nonzero failure for a nonexistent freeze, nonexistent selected configuration, altered return claim and stale figure input.
- **V2-02:** The figure pack was regenerated from final sources. Its manifest now records the report builder, publication sections, registry loader and release registry alongside data/analysis inputs; no stale input hash remains.
- **V2-03:** README and Appendix E now select V2 through `REPORT_RELEASE_REGISTRY`, document the figure→DOCX→render→contents→rebuild→verify sequence, and name LibreOffice/Poppler prerequisites. The contents resolver now uses declared external Poppler commands rather than an undeclared PyMuPDF import and succeeds in the project `.venv`.
- **V2-04:** Segment tables distinguish cumulative from geometric annualized net return. The report shows −4.04% cumulative / −4.09% annualized for 249 sessions in 2025 and +15.01% cumulative / +20.99% annualized for 185 sessions through September 2026. Figure 15 is labeled as a calendar-period record, not a full-year 2026 return.
- **V2-05:** Calibration limits include all mean ± one-SE endpoints. Points are unconnected, count ranges are stated in the caption, and no uncertainty whisker is clipped.
- **V2-07:** A new no-refit paired circular date-block analysis compares the selected policy with cohort-mean and U.S.-services timing on identical dates. It retains 5/10/20-session block sensitivities, 2,000 draws and seed 17. Every 10-session interval shown in the report crosses zero, so incremental stock-selection value remains unestablished.
- **V2-12:** The architecture now shows information gate→feature engineering→model validation→daily inference, separates offline selection from daily decisions, and states that 60 fallback flags remain subject to strict-vintage sensitivity.
- **V2-13:** Added the Politis–Romano circular block-resampling reference and distinguished circular date blocks from whole-date permutation diagnostics.
- Removed the residual unsupported “seasonality” alignment claim.
- Removed a reproduction-command spill that created an almost-empty page; the final report is 24 pages.

### Still open or author-dependent

- **V2-06 and V2-08:** Correct depth-6 strict-vintage and selected-family ablation experiments require new fitted diagnostics. They were not fabricated or mixed into the canonical report.
- **V2-09:** Truthful individual contribution allocation, video verification and final Canvas filename remain author inputs.
- **V2-10 and V2-11:** Full asset/side P&L attribution and a new overnight-versus-intraday mechanism panel remain useful secondary analyses.
- **V2-14:** The project remains retrospective until genuinely future observations are generated under a prospectively timestamped protocol.

### Final revision-2 acceptance

- Canonical release verification: **183 passed, 0 failed**.
- Adversarial verification: **4/4 mutations rejected** with targeted diagnostics.
- Unit tests: **15 passed**.
- PDF length: **24 pages**; all 18 contents destinations are nonzero and resolved.
- Visual review: every page inspected after the final render; no clipping, overlap, trailing blank page or hidden calibration interval remains.
- Accessibility audit: **0 high, 0 medium and 0 low findings** after adding the NUS-logo alternative text, marking table header rows and replacing the raw cover URL with descriptive link text.
- Final revision-2 hashes: DOCX `6781151f74a0b8534b57a4934b5c1408f52e8177ee9c85af3071e204e8ae4dd9`; PDF `fde1193c46d8310220cc58e42747ef34a9fb7e4e68b991ce61828634364a39c4`.

## Revision 3 — completed strict-vintage sensitivity

Implemented on 1 November 2026 in response to the architecture-diagram review. This revision resolves the former V2-06 empirical gap rather than hiding it.

- Corrected every `gap_diagnostics` Extra Trees configuration from depth 8 to the selected model's exact depth 6.
- Added `scripts/run_strict_vintage_sensitivity.py`, a hash-tracked, resumable focused runner with progress bars and a noninteractive plotting backend.
- Refit the exact selected depth-6 specification under identical dates, rolling windows, seed, signed policy and trading costs after excluding all fallback-flagged F7 columns.
- Exclusion audit: **60 flagged columns removed; 0 retained**. Mean viable inputs changed from 3,013 to 2,964 in 2025 and from 3,040 to 2,991 in the 2026 extension.
- Point estimates improved from **−4.04% to −1.84%** in 2025 and from **+15.01% to +24.93%** through September 2026.
- Paired 10-session circular date-block intervals still cross zero: 2025 mean difference **+0.90 bps/day [−3.26, +4.71]**; 2026 **+4.47 bps/day [−4.26, +14.56]**. The report therefore treats the result as robustness evidence, not proof that the strict variant dominates.
- Replaced the overflowing “pending” architecture text with the completed audit result and added a main-text sensitivity table and figure.
- Bound analysis `strict_vintage_sensitivity_20261101T072530Z_d98ad9caf3b8` into release-registry revision 3, the figure manifest, Appendix A/E and the release verifier.
- Final release verification: **224 passed, 0 failed**; adversarial mutations **4/4 rejected**; unit tests **15 passed**; accessibility findings **0/0/0**; PDF length **25 pages** with all 18 contents destinations resolved.
- Final revision-3 hashes: DOCX `949d9c8df2375634b3cb3862e85bd938184cdcb701877ae6c982bea90c954ba4`; PDF `fe602e0dc630f1713477f63c535af120bd4bdecd3ad3140ab6b5d02077d29d08`.

## Revision 4 — evidence-preserving editorial review

Compared V1 with V2 and reviewed every rendered page. V2 added substantive safeguards but overloaded its architecture and main visual narrative. Revision 4 reduces the report from 25 to 21 pages and from 20 to 15 figures, while retaining the underlying diagnostic files.

- Replaced the architecture with monochrome outlined boxes and explicit input → feature → temporal fit → forecast → long/flat/short execution flow. Removed badges and vintage-audit counts from the diagram.
- Kept strict-vintage and calibration findings as concise numerical text/table evidence. Removed duplicate price paths, event-count bars and permutation graphics from the report, retaining them in the figure pack.
- Added `scripts/audit_report_feature_progression.py` and a matched stock/date quarterly audit. The report shows annual R² computed from summed squared errors for eight fixed-penalty ridge information sets over 2021–2025. The explanatory paragraph distinguishes repeated deterioration from volatility, unrelated Lasso warnings, and untested causal mechanisms.
- Reclassified hypotheses as supported, contradicted or inconclusive at the appropriate claim level. Did not manufacture causal identification or promote a model based on inspected evaluation periods.
- Improved prose placement ahead of large figures, figure sizing and appendix flow; refreshed all 18 contents destinations.
- Comparative rationale: `documents/markdown/REPORT_V1_V2_EDITORIAL_REVIEW_2026-11-01.md`.
- Release verification: **225 passed, 0 failed**. All 21 rendered pages visually reviewed. V1 DOCX/PDF hashes unchanged.
- Revision-4 DOCX SHA-256: `78a55f079a539ff72689c501c7012ae1bf299b92c4b45c1fe6a1480e6bd5aac7`.
- Revision-4 PDF SHA-256: `4123ee6e0116b2b6825d7b2ef2709b5526dfae6f486be072e22792624f8f5db9`.

### Submission wording and appendix-reference follow-up

Architecture typography follow-up: enlarged the figure to 6.2 inches in the document, added a prominent Research Architecture heading, and explicitly set every diagram text label to Times New Roman (font availability checked). Enlarged flags and replaced process glyphs with a marked 08:55 clock, a decision tree with validation check, and a chart showing history plus a dashed forecast. Separated long/flat/short into three columns. Statistical figures and model results were preserved; the architecture-only refresh updates its source and output hashes.

Removed the internal version/traceability label from the cover and document title. Replaced the contents-page status jargon with a plain explanation of selection through 2024, quarterly past-only refits in 2025, the single pre-2026 fit, and prior researcher inspection of both evaluation periods. Restored small country flags and monochrome process icons without changing the black architecture outlines. Added A1–A9 and E1–E13 reference mappings; the Yahoo dataset identifier now appears only as A9 in the appendix. Main-text discussions reference the mappings. The builder now rejects timestamped identifiers and long hexadecimal hashes before Appendix A. The release verifier checks the submission cover rather than requiring an internal version label. Current final artifact hashes are in verification.json; the hashes above describe the preceding revision-4 render.
