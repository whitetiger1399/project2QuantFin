# Cross-Market Report Figure Plan

This plan keeps the report concise. A figure is included only when it answers a distinct Project 2 requirement or materially improves interpretation.

## Main-text figures before final results

1. **Cross-market information architecture.** Defines the traded cohort, external information blocks, 08:55 IST availability gate, F0–F5 ladder, prediction target, model stage, and trading rule. Arrows indicate predictive information flow, not causality.
2. **Experiment design and selection funnel.** Separates the incremental-information, model-family, and complexity experiments; shows screening, confirmation, freeze, and untouched final holdout.
3. **Leakage-safe daily information clock.** Shows which completed sessions are available at 08:55 IST and when the open-to-close target becomes observable.
4. **Open-to-close return distributions.** Establishes heavy tails and cross-asset heterogeneity relevant to robust cleaning and regularization.
5. **Rolling cohort return and volatility.** Shows nonstationary mean/volatility and motivates rolling estimation and regime analysis.
6. **Nifty IT cross-asset correlation.** Shows common variation without using an unreadable feature-level correlation dump.
7. **US technology to India lead/lag diagnostic.** Directly examines the central cross-market timing premise; it must be described as descriptive rather than causal.

## Diagnostics or appendix

- Strongest positive/negative feature–target rank correlations, with multiple-testing caveats.
- Lagged-US-volatility regime distributions.
- Feature-family missingness and source coverage.
- Statistical test tables: ADF, KPSS, Ljung–Box, ARCH LM, Jarque–Bera, and FDR-adjusted feature tests.

## Exclude from the main report

- The current target-coverage heatmap: coverage is essentially complete, so the rendered heatmap is visually blank. Report row/date/asset counts in text instead.
- The current trend-shift/event plot: it contains statistical shift markers but zero populated retrospective global-event records. It should not imply an event explanation until a sourced event file is available.
- Full 3,333-feature correlation heatmaps: labels are unreadable and the plot does not support a defensible decision.
- Multiple versions of the same leaderboard, cumulative-wealth chart, or feature-importance chart.

## Final-results figures to add only after the frozen test

1. F0–F5 feature-progression comparison.
2. Validation/confirmation model-family comparison.
3. RFF complexity versus OOS performance and shrinkage.
4. Frozen strategy versus ITBEES, NIFTYBEES, and equal-weight cohort cumulative wealth.
5. Drawdown and annual/subperiod performance.
6. Cost sensitivity and turnover.
7. Rolling information coefficient.
8. Final grouped permutation importance or stable standardized coefficients.

The main report should use at most four EDA figures, three design diagrams, and four to six final-result figures. Remaining diagnostics belong in the appendix or repository artifacts.
