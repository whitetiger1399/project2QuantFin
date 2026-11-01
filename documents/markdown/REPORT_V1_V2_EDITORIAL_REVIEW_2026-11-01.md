# V1–V2 editorial and evidence review

Date: 1 November 2026. Release: project2_team16_v2_2026-11-01, revision 4.

## Verdict

V2 strengthened evidence traceability, strict-vintage sensitivity, paired inference, and explicit historical-evaluation limitations. Its presentation regressed: the architecture became overloaded, diagnostic graphics distracted from the economic result, and page flow suffered. Revision 4 retains those substantive improvements and edits their presentation. V1 remains unchanged. No canonical model or prediction was retrained or replaced in this revision.

## Changes and rationale

| Concern | Revision | Evidence retained |
|---|---|---|
| Crowded architecture with overlapping badges | Monochrome outlined boxes, three input groups, pre-open feature construction, temporal model selection, forecast, and explicit long/flat/short execution | Audit results remain in Section 5.3 and Appendix A/E |
| Calibration-decile plot lacks a clear main-story role | Removed from report; retained numerical calibration findings | Original diagnostic and source hashes remain in the figure pack |
| Two-period strict-vintage uncertainty plot | Replaced by compact sensitivity table and explanation | Completed refits and paired intervals remain reported; no pending check concealed |
| Excess figures and repetition | Reduced report figures from 20 to 15; removed duplicate India/U.S. price chart, event-count bars, and permutation chart from report | Figure pack still preserves all diagnostics |
| Feature ladder shown without temporal context | Annual matched-date R² heatmap for 2021–2025; saved quarterly audit | `artifacts/report_reviews/feature_progression_20261101/` records hashes and quarterly MSE/baseline MSE |
| Empty space and stranded prose | Move interpretation before figures where possible; reduce figure width modestly; remove forced appendix break; keep short tables together | Figure order/captions and heading bookmarks regenerated |
| All hypotheses appear rejected | Distinguish supported associations, contradictory evidence, and inconclusive tests | Estimates, adjusted p-values, sample sizes and causal limitations preserved |

## What the feature ladder actually establishes

Eight ridge information sets share penalty 0.1 and are compared on matching stock/session keys against the same rolling asset-mean baseline. Annual R² is computed from summed squared errors, not by averaging quarterly R². The full-context specification underperforms the baseline in each of 2021–2025; adding raw S&P constituents is associated with a marked deterioration. This pattern repeats across years, so a single volatile period is not an adequate explanation. All specifications face the same outcomes within each comparison.

This is evidence against this fixed ridge specification, not against all additional information or every model family. Noisy/redundant predictors and inappropriate fixed shrinkage are plausible mechanisms, not established causes. Ridge uses a different quadratic solver from coordinate-descent Lasso/Elastic Net: their convergence warnings cannot explain this ridge plot. The saved predictions do not by themselves prove numerical optimality; a controlled training-only penalty sweep and solver-residual audit would be needed to distinguish these mechanisms. Such a new experiment must not be tuned on the already inspected 2025–2026 results. The selected Extra Trees results remain a separate comparison.

## Hypothesis interpretation

- H1: evidence supports a conditional U.S.–India association; this does not itself establish profitable trading.
- H2: the pooled negative AI-release prediction is inconclusive; the negative 2026 association is an exploratory period-specific result.
- H3: attenuation of the AI-release effect after 2024 remains inconclusive; the negative interaction estimate does not establish that the effect weakened or strengthened.
- H4: capability-shock evidence is inconclusive with small event groups.
- H5: stable repeatable alpha is not established; the stronger claim of positive returns every year is contradicted by 2025.
- H6: reported AI offerings and workforce changes support descriptive adaptation. A causal profit-margin benefit is a different question requiring a credible comparison design; repeated testing of these prices cannot prove it.

Absence of significance is not proof of no relationship. Conversely, favorable point estimates or company narratives cannot establish causality. These distinctions make the report more informative without changing results to support a preferred story.

## Reproduction

Run the feature audit before rebuilding the publication pack:

```bash
.venv/bin/python scripts/audit_report_feature_progression.py --registry reports/releases/project2_team16_v2_2026-11-01/release_registry.json --output artifacts/report_reviews/feature_progression_20261101
REPORT_RELEASE_REGISTRY=reports/releases/project2_team16_v2_2026-11-01/release_registry.json MPLCONFIGDIR=/private/tmp/quantfin_mpl .venv/bin/python scripts/build_publication_figure_pack.py --output reports/publication_figure_pack_v2_2026-11-01
REPORT_RELEASE_REGISTRY=reports/releases/project2_team16_v2_2026-11-01/release_registry.json MPLCONFIGDIR=/private/tmp/quantfin_mpl .venv/bin/python reports/build_report_ai_capability.py
```

Render, resolve contents page numbers, rebuild, and render once more as described in README. Release verification checks figure input hashes and pinned lineage. Full run identifiers remain in the appendices.
