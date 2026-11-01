# Publication figure review — 1 November 2026

Scope: review and generate figures only. Existing reports and trained-model runs are preserved. The new pack is in `reports/publication_figure_pack_2026-11-01/`; `index.html` and `figure_review.pdf` present the figures with explanatory captions. The catalog records each replacement's purpose and suggested main-text/appendix placement. These are candidates for a concise report, not a requirement to include all 18.

## Evidence and visual conventions

India uses blue country headings and labels; U.S. uses orange. Cross-country price panels additionally distinguish solid and dashed lines. Gross/net returns use teal/navy, short exposure rose, and flat/missing observations gray. Return heatmaps use diverging scales around zero. Missing model-family results are masked rather than coloured as poor performance.

Price comparisons are normalized local-currency price paths, not currency-converted investment returns. Correlations use returns, not price levels. The U.S.–India matrix uses the actual decision-aligned features: U.S. information available before the Indian decision and the subsequent Indian intraday return. Correlation is not causal transmission.

## Review of the existing report figures

| Existing figure | Decision and replacement |
|---|---|
| Research architecture | Replace with 01: explicit per-stock long/short/flat eligibility, cost ledger, hypothesis layer, quarterly 2025 refits and fixed-fit 2026 extension. |
| Nifty IT constituent trends | Replace with 02: log-price index, readable legend, evaluation boundary. Avoid compressing lower-growth names. |
| India/U.S. services trends | Replace with 03: separate country panels, country colours and line styles, common normalization. |
| Indian peer correlation | Replace with 04: triangular annotated return matrix removes redundant cells. |
| U.S./India predictive correlation | Replace with 05: clearly labelled countries, decision timing and annotated coefficients. |
| Information ladder | Replace with 12: named feature blocks, separate forecast and economic metrics. |
| Frontier-record event timeline | Replace with 06a: country price paths with cross-stock dispersion and numbered event key. |
| Frontier-event response heatmap | Replace with 06b: paired country panels with explicit, different return horizons; shared event numbering. |
| Model-family stages | Replace with 11: symmetric colour scale, gray missing cells and configuration counts. Best configurations can differ across stages. |
| Combined evaluation wealth | Replace with 08: one continuous 2025–September 2026 curve with benchmark definitions and protocol divider. |
| Combined evaluation positioning | Replace with 09: signed exposure and monthly long-only/short-only/mixed/flat counts. A portfolio may hold both sides simultaneously. |
| Group permutation importance | Retain unchanged as 17 in the appendix. Do not imply causal feature effects or date-independent observations. |
| Stitched research-period wealth | Omit from headline results: selected-model historical development paths must not be presented as an untouched investment test. |
| Research-period annual returns | Consolidate into 07 for reported evaluation years; separate later candidate diagnostic in 15. |
| Research-period regime returns | Replace with 16: evaluation-period monthly distributions, with ex-post regime caveat. |
| Research-period reversal returns | Consolidate into 16 to avoid redundant figures and show observation-level dispersion. |

## Additional evidence

- **07: Transaction-cost drag.** Cumulative gross/net curves and yearly/combined returns use identical positions. Actual 2025 gross return is **11.0473%**, versus **0.0860% net**. Do not use illustrative 19–20% figures. The difference between compounded gross and net wealth is not simply summed daily costs.
- **10: Cost sensitivity.** Reprice fixed holdings under alternate charges; this is a sensitivity calculation, not reoptimization or a new strategy selection exercise.
- **13: Transmission inference.** Coefficients and confidence intervals accompany multiplicity-adjusted significance, rather than relying solely on coloured correlations.
- **14: Event coverage.** Zero recorded 2026 events is a coverage limitation, not evidence that no releases occurred. Do not infer attenuation from that missing coverage.
- **15: Later candidate diagnostic.** Keep the later candidate's screening/confirmation outcomes separate from the canonical model's final evaluation.

## Interpretation requirements

The cost assumption is 7.5 bps per side (5 bps fee/spread proxy plus 2.5 bps slippage), or 15 bps round trip at full gross exposure. It is not a complete instrument-specific Indian tax schedule. Long and short trades are intraday and close by session end. Eligibility does not guarantee a position: ranking and portfolio caps also apply.

The combined evaluation joins 2025 quarterly-refit predictions and the 2026 fixed-fit extension. It must retain the protocol boundary and cannot be described as a single pristine, never-inspected holdout after repeated research revisions. Event plots are exploratory associations; price changes cannot be attributed to AI releases from temporal proximity alone.

## Verification and reproduction

All generated charts were visually reviewed in contact sheets; the architecture and long price-axis label were subsequently corrected and re-rendered. Ledger assertions check gross minus cost equals net, the assumed turnover charge, duplicate dates and finite returns. The pack manifest records UTC generation time, source content hash, input checksums and output checksums. No models were retrained.

```bash
cd /Users/whitetiger/Desktop/WhiteTiger/17_projects/24_Project2_QuantFin/project2QuantFin
source .venv/bin/activate
python scripts/build_publication_figure_pack.py
```

Before inserting these figures, retain readable full-width placement for annotated matrices and event panels, use the supplied captions, and check the final DOCX/PDF pagination separately. Plot-level review does not establish that a future report layout is free from clipping or whitespace problems.
