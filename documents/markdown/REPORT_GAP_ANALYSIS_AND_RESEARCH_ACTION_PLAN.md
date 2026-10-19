# Project 2: requirement-to-report gap analysis and research action plan

**Review date:** 19 October 2026  
**Course:** Data Science in Quantitative Finance DSA5205  
**Team:** Project2 Teams 16  
**Scope:** planning and evidence review; no new models trained and no existing research artifacts overwritten during this review.

## 1. Decision and recommended direction

The report establishes a useful research baseline, but it needs factual reconciliation and stronger evidence before it can support publication-style claims. The main opportunity is not simply a larger algorithm. It is a controlled investigation of **whether information available at the decision time about volatility, interest rates and scheduled events improves SPY timing across horizons and training windows**.

Recommended research question:

> Does adding release-aware macroeconomic and market-state information improve net economic utility and forecast accuracy beyond price-only and volatility-managed benchmarks, and how does that result depend on model capacity and training-window adaptation?

This is a testable research contribution, not a claim of novelty or publishability. A literature comparison and independent replication are needed before either claim. Weak or negative results remain valid outcomes. The assignment explicitly grades clean timing, leakage control, fair benchmarks and interpretation more heavily than profitable returns.

Recommended implementation order:

1. Reconcile the report with selected configuration IDs and actual training/evaluation code.
2. Preserve the original experiment and define an honest protocol for additional research.
3. Add stronger benchmarks and precise execution/calendar accounting.
4. Introduce release-aware rates, VIX and event features in controlled blocks.
5. Compare feature blocks, horizons, windows and model families through bounded chronological experiments.
6. Investigate complexity, learning curves and attribution drift in the finalists.
7. Produce readable evidence with uncertainty, captions and interpretation, then rebuild the submission package.

A three-to-five-hour laptop training budget is reasonable as a **measured resource limit**. It is not a guaranteed runtime or a promise of stronger performance. Expensive models must earn their place against simpler models on identical evaluation dates.

## 2. Evidence reviewed and limits of this review

Primary documents:

- `documents/markdown/Project2.md`: assignment requirements, §§4.1–4.9, deliverables and Appendices A–B.
- `reports/Project2_Team16_Report.docx`: actual paragraphs and tables extracted from the DOCX, not merely the builder source.

Supporting evidence:

- `configs/protocol.yaml`, `configs/models.yaml`, `configs/features.yaml`, `configs/events.yaml`.
- `src/quantfin/models.py`, `modeling.py`, `evaluation.py`, `reporting.py`, `eda.py`.
- `reports/build_report_ieee.py` and `reports/output_verification.json`.
- Screening, confirmation and final `config_metrics.csv`, selection records and manifests.
- `resources/pytrendsREADME.md`, `resources/BacktestingREADME.md` (actually the **bt** README), `resources/backtrackerREADME.rst` (Backtrader).
- Prior hardware inventory in `documents/markdown/AGENT_ACTION_PLAN.md`.

The existing 41-check result verifies specified artifact properties. It does **not** verify every statement in the report or independently prove scientific correctness. This review found mismatches despite that passing result. Source inspection identified further accounting and reporting risks that require targeted tests before declaring their numerical impact.

The current saved author file contains one person. The complete Canvas roster cannot be verified from that file. Do not invent additional members or assign identical contributions to people without confirmation.

## 3. Requirement coverage matrix

Status definitions: **covered** means evidence is present, not independently certified; **partial** means a requirement is addressed but has omissions or mismatches; **missing** means it was not established in the reviewed material.

| Assignment requirement | Report evidence | Status | Required improvement | Priority |
|---|---|---|---|---|
| §4.1 assets, frequency, benchmark and execution | §§2–4 identify SPY, predictors and delayed close execution | Covered / partial | State USD, America/New_York, 18:00 decision time and exact calendar handling in the report | P0 |
| §4.1 lawful data source | Yahoo and optional Stooq identified | Partial | Cite actual API/library and data terms; distinguish access from redistribution; explicitly report skipped Stooq verification | P0 |
| §4.2 label and timing | Equations and availability rule | Covered / partial | Distinguish two-session forecast lead from one-session holding period; add boundary examples | P0 |
| §4.2 feature list, rationale, windows | Group table and five examples | Partial | Export full 99-feature dictionary with formula, window, source, availability and economic rationale | P1 |
| §4.2 cleaning | Rules described | Partial | Rule-level row counts, missingness lineage, extreme-event decisions and corporate-action evidence | P1 |
| §4.3 investable and forecast benchmarks | SPY, historical mean, AR | Covered / partial | Correct AR description; complete SPY risk metrics; add cash and exposure/volatility controls | P0/P1 |
| §4.4 economic story and overfitting | Regularization and model list | Partial | State hypotheses per feature/model block; compare matched complexity and data sizes | P1 |
| §4.5 splits and untouched testing | Three-stage chronology | Partial | Correct 2005 warm-up versus 2006 training; preserve original final period as already inspected for future work | P0 |
| §4.6 training algorithms, versions and seeds | Seed and parameter ranges | Partial | Specify actual solvers, iterations, convergence and installed environment; distinguish current sequential refits from estimator threads | P0/P1 |
| §4.7 bounded predeclared search and selection | 57 configurations, median annual Sharpe | Partial | Fix selected-ID mismatch, report all trials and family exclusions, predeclare extension budget and metric | P0 |
| §4.8 mapping, execution, costs, limits | Binary threshold, 5 bp and no leverage | Covered / partial | Reconcile entry/exit dates, cash, annual attribution and initial wealth; explain threshold versus expected holding-period cost | P0 |
| §4.9 annualized return, volatility, Sharpe | Return and Sharpe table | Partial | **Annualized volatility is absent from final report table**, although stored in metrics; add it for every benchmark | P0 |
| §4.9 OOS plots and period comparisons | Wealth, drawdown, complexity and annual returns | Partial | Add OOS R² and Sharpe by period, complete benchmark metrics and interval estimates | P1 |
| Interpretation and exact reproduction commands | Report Appendix A rebuilds report | Partial | Include data → features → screening → selection → freeze → evaluation commands, not just report generation | P0 |
| PDF 15–25 pages | Current delivered PDF reported as 15 pages | Covered / quality gap | Replace administrative filler with substantive findings; repair contents, captions and numeric consistency | P1 |
| Full roster and short contribution note | One author and broad contribution statement | Partial | Reconcile with Canvas team and actual contributions; maintain alphabetical rendering | P0 |
| Submission naming | `Project2_Team16_Report.pdf` | Partial | Deliver `Group_16_Report.pdf` as specified, retaining internal build filename if useful | P0 |
| 15–25 minute video | No finished video established in reviewed report | Missing evidence | Record end-to-end demonstration and provide accessible downloadable video/link | P1 |
| Clean reproducibility package | Environment and README exist | Partial | Fresh-environment reproduction, relative report commands, artifact hashes, dependency locks and redistribution review | P1 |

Do not infer a grade from this matrix: the assignment supplies a total of 35 points but no reliable per-row weighting for this review.

## 4. Verified defects and implementation risks

### G01 — Wrong random-forest configuration in report comparisons

**Verified.** `reports/build_report_ieee.py` selects `screen[screen.family.eq("random_forest")].iloc[0]`; `plot_stage` repeats this approach. The first row is not the selected configuration.

| Quantity | Current report, first RF row | Selected RF in `selection.json` |
|---|---:|---:|
| Configuration | `random_forest_37e6adddd4` | `random_forest_6aa9f5d449` |
| Screening annualized net return | 1.58% | **3.73%** |
| Screening net Sharpe | 0.21 | **0.60** |
| Median annual net Sharpe | 0.75 | **0.95** |

The report labels the first row with the selected model's depth/leaf parameters, combining two different configurations. Affects Table 6, Figure 5 and the confirmation narrative. The final metrics were not shown to be affected by this particular error.

**Solution:** resolve selected IDs through `selection.json` and the final freeze; join metrics by ID with one-to-one validation. Generate captions, tables and narrative from the same structured fact object. Assert that displayed parameters and metrics share a configuration ID. Never identify a champion from row order or current-period ranking.

### G02 — Training-period mismatch

**Verified.** Report Table 2 says initial training is 2005–2014; `protocol.yaml` defines 2005 as warm-up and initial training as 2006–2014. `run_walk_forward` enforces that lower bound. Market EDA can legitimately include the warm-up but must label it differently.

**Solution:** distinguish raw coverage, feature warm-up, estimation sample and evaluation sample in one timeline and table; export actual first/last eligible timestamps and counts for every fold.

### G03 — AR order is misdescribed

**Verified.** The report says “four lags.” Code uses return offsets 0, 1 and 2, with an intercept: three inputs and four fitted coefficients.

**Solution:** write “three return predictors plus intercept.” Clarify that the delayed one-session-return target makes this a lagged-return linear baseline, not automatically a conventional next-return AR(3) equation.

### G04 — Missing-value and compute claims exceed implementation

**Verified discrepancy.** The report says mature rows require complete values for every feature, but inspected training code filters label availability and uses training-fitted median imputation. It does not enforce a complete-case condition there. The report also says two process workers; the main refit loop is sequential, with `n_jobs` passed into supported estimators.

**Solution:** document actual imputation and warm-up eligibility, inspect nulls per selected feature and fit, and show observed estimator/process/thread behavior. Do not call estimator parallelism parallel walk-forward scheduling.

### G05 — Calendar and P&L labeling

**Verified implementation, impact to quantify.** Annual groupings and plots use `signal_session`; returns are realized over later entry/label-end sessions. Split membership also follows signal date. Cross-year and cross-stage labels therefore require explicit handling.

**Solution:** retain `signal_ts`, `fit_ts`, `entry_ts`, `exit_ts`, `label_available_ts` and `pnl_date`. Define evaluation boundaries and year grouping on realized P&L dates. Audit trades crossing every year/stage boundary. Treat closing/reopening at stage boundaries consistently, with costs documented.

### G06 — Risk metrics and drawdown initialization

**Verified code risk.** `_drawdown` compares cumulative wealth only with its observed running maximum; initial wealth 1 is not inserted. An initial loss can therefore be missed when measuring peak-to-trough loss from inception. Numerical effect on the current runs has not been recomputed here.

**Solution:** include initial capital as a peak; test a first-day loss and all-negative toy path; distinguish annualized arithmetic mean, CAGR and excess-return Sharpe. Add benchmark volatility, CAGR, drawdown, exposure and turnover to the report. For a zero-cash convention explicitly label the Sharpe assumption. A later cash-interest extension must revise both portfolio and benchmark comparisons consistently.

### G07 — Selection and inference need better controls

Current family selection excludes historical mean and AR from eligibility. This can advance an ML family even when a baseline is stronger. A median of annual Sharpes can also be unstable when the strategy rarely trades and zero-variance years become undefined.

**Solution:** retain v1 selection unchanged for provenance; for v2, include baselines in a no-incremental-value decision gate. Predeclare how inactive years, minimum exposure/trade counts and NaN Sharpe are handled. Report every year and trial, not just successful ones.

The bootstrap code implements fixed-length moving blocks, whereas reference [10] describes the stationary bootstrap. Match the citation and implementation or implement the stated alternative explicitly; report block-length sensitivity. Do not label either interval as selection-bias corrected.

### G08 — Report and claim quality

The DOCX contains a manually numbered contents list whose early section page numbers are inconsistent with the earlier render. Some caption paragraphs are separated from their figures. Several formulas in appendix tables use plain-text `Pt−1` rather than typeset indices. The report does not cite the assignment's central complexity paper by Kelly, Malamud and Zhou even though its RFF experiment follows that motivation.

**Solution:** field-generated contents or PDF-derived validated page mapping; keep each image with its caption; native equations or verified high-resolution mathematical rendering; cite the relevant primary papers. Remove prose about the previous report redesign and administrative “complete” claims. Add metric-specific evidence and exact code references instead.

### G09 — Existing checks are necessary but insufficient

The 41 checks did not catch G01–G04. Extend assurance with independent hand-calculated cases for timing, capital, cost and return accounting; artifact-to-report fact checks; source-availability boundary tests; and interrupted-versus-resumed output reconciliation. These are proposed checks for implementation, not tests run during this review.

## 5. Temporal integrity for the next research version

### 5.1 Preserve the original result

Archive the v1 configuration, selection/freeze files, data hashes, report and evaluation outputs before modifications. The original final evaluation remains part of the project history. New findings may correct reporting errors, but revised methods must not be presented as the original preregistered strategy.

**2022–2025 is now an inspected period.** Repeated tuning against it turns it into research data. Renaming it “test” or using new seeds cannot restore independence. Nested walk-forward results in this period can still be valuable, provided they are described as retrospective and affected by prior researcher exposure.

### 5.2 Proposed v2 protocol

- Development: initial training 2006–2010; outer forward evaluation blocks 2011–2014, 2015–2018 and 2019–2021. Refit monthly within each block.
- Hyperparameters and window/horizon choices are selected only using inner forward folds ending before the corresponding outer block; eligible labels must mature by the inner cutoff.
- Retrospective stress panel: 2022–2025, reported separately with an explicit inspected-period label. Do not promote a new model using those results and call it unbiased.
- Optional later-period check: Jan–Sep 2026, **only if those observations/results have not been accessed for this project**, freeze all v2 choices before retrieval, and record the audit trail. General awareness of market history still limits claims of a perfectly blind historical test.
- Strongest independence: prospective shadow evaluation starting after the v2 freeze. The assignment deadline is 12 November 2026, so only a short prospective window is possible before submission; report limited power.
- If later data has already been inspected, state that no new untouched final holdout is available. Deliver honest retrospective research plus the original v1 evaluation.

For a primary daily experiment, retain the original entry convention. Do not simultaneously alter execution, labels, model and sources in the first comparison.

### 5.3 Window and horizon experiment

Candidate training windows: expanding, trailing 756 sessions (~3 years), trailing 1,260 sessions (~5 years). Explore trailing 2,520 only if enough history remains. Add exponential recency weighting as a separate ablation, half-life 252 or 756 sessions, only for estimators that support it.

Candidate holding horizons: 1, 5 and 20 trading sessions. The 5/20-session experiments should use declared rebalance schedules and non-overlapping holds initially. If daily forecasts of overlapping returns are evaluated, purge training labels whose payoff intervals overlap validation and use dependence-aware inference. Do not compound overlapping H-day target returns as daily wealth or annualize them with 252 mechanically. A daily portfolio ledger with explicitly allocated overlapping sleeves is required for that alternative.

Match common evaluation dates when comparing windows. Report both common-sample results and any full-coverage extension. Monthly horizons reduce the number of independent observations; they do not automatically justify larger networks.

### 5.4 Extending the timeline backwards

Attempt earlier SPY-only or SPY/QQQ data only after checking actual vendor coverage and inception. The full five-ETF panel is constrained by the youngest asset. Never manufacture pre-inception GLD/TLT histories by filling or casually splicing proxies. Treat a long-history price-only experiment and a shorter rich-data experiment as separate datasets, with a common-period comparison to distinguish history from feature effects.

## 6. Data acquisition and availability contracts

Each observation must carry `source`, `series_id`, `observation_period`, `value`, `units`, `published_at`, `available_at`, `retrieved_at`, `vintage_id`, `quality_flag` and `license_reference`. For event schedules also retain `schedule_announced_at`. Dates alone are insufficient when publication happens after the 18:00 New York signal cutoff.

| Source/block | Proposed data | Why it may help | Timing rule and acceptance condition | Priority |
|---|---|---|---|---|
| Existing Yahoo snapshots | SPY/QQQ/IWM/TLT/GLD OHLCV/actions | Reproducible price-only anchor | Freeze existing snapshot; compare any update as a different dataset | P0 |
| FRED/ALFRED | DGS2, DGS10, DGS3MO, DFF; policy target where historically supported | Curve slope, rate regime and daily changes | Audit each series' metadata, vintage coverage and release lag; date of observation is not availability | P1 |
| New York Fed | EFFR; later-period SOFR/repo measures | Overnight funding conditions | Respect publication timestamp and source history; do not backfill SOFR through the full 2005 sample | P1/P2 |
| Cboe | VIX history; VIX3M if coverage supports it | Implied volatility and term structure | Confirm history, units and end-of-day availability; volatility indices are predictors, not directly investable benchmarks | P1 |
| BLS + ALFRED | CPI inflation, unemployment/payroll releases | Inflation/labor state and announcements | Join first available vintage after publication; retain release age; never join monthly values to month start | P2 |
| Federal Reserve | FOMC calendars, statements and target changes | Scheduled uncertainty and observed policy changes | Use historic announcement/schedule records; changes only after publication | P1 |
| NYSE calendar | Closures, early closes, session distances | Holiday liquidity and seasonality | Exchange calendar rather than federal holiday list; unscheduled closures only after announcement | P1 |
| US Treasury | Daily yield-curve observations | Primary-source rate cross-check | Document publication schedule and differences from FRED; no silent replacement | P2 |
| Kenneth French data library | Market excess return, RF and factors | Performance attribution | Use ex-post for attribution; avoid treating retrospectively published factors as contemporaneous predictors | P2 |
| Caldara–Iacoviello GPR | Geopolitical risk indices | Global risk-state context | Research/descriptive first; predictive use requires historical availability/revision evidence | P2 |
| GDELT/news | Publication-aware crisis/news counts | External shock coverage | Separate later-history experiment; verify archive coverage, ingestion latency, deduplication and revisions | P3 |
| Google Trends / pytrends | Search attention | Optional alternative signal | Window normalization, sampling changes and reproducibility make this unsuitable for the core extension | P3 |

For US equities the relevant monetary-policy concepts are the federal funds target and effective funds rate. SOFR/repo rates measure secured funding conditions; an unrelated foreign “repo policy rate” should not be inserted without a stated economic channel.

FRED supports real-time periods/vintage queries; the default current information set is not a historical point-in-time dataset [S1–S2]. Intraday release timestamps may require publisher archives beyond ALFRED dates. Use a conservative next-session delay when historical timing cannot be established, and disclose that convention rather than imply precision.

Known macro values may be carried forward **after their release** until superseded, with an age feature and maximum-staleness policy. This is distinct from fabricating missing asset prices. Do not interpolate revised macro series backwards. Low-frequency World Bank annual series offer little direct value for this daily target and create avoidable release-lag complexity.

## 7. Cleaning and feature-engineering experiments

### 7.1 Cleaning deliverables

Produce a row-count waterfall per source/asset; duplicate conflict report; calendar completeness heatmap; stale-value and missingness matrix; corporate-action event windows; raw-versus-adjusted return reconciliation; and explicit retain/exclude decisions for extremes.

Cross-source agreement is a diagnostic, not majority voting. The current Stooq comparison was skipped; report this clearly. Test at least one dividend and, if no split exists for the traded asset, a separate split fixture or auxiliary instrument. Do not invent a SPY split. Verify the assignment's PDF-to-Markdown adjustment formulas against source data before using them as a mathematical oracle.

Keep raw and repaired vendor outputs separately: `repair=True` can alter downloaded history, so “raw snapshot” should mean the exact retained vendor response with request flags, not an assumption of untouched exchange observations. Write repair settings and differences into provenance.

### 7.2 Feature blocks and hypotheses

| Block | Proposed variables | Hypothesis | Ablation |
|---|---|---|---|
| F0/F1/F2 existing | Existing return, trend, volatility and cross-asset groups | Price-state nonlinearities provide weak timing information | Reproduce each existing set on matched rows |
| M1 rates/volatility | Available yield levels; 10Y–2Y and 10Y–3M spreads; 1/5/20-session changes; VIX level/change; VIX/realized-vol ratio | Risk compensation varies with policy and uncertainty | F2 vs F2+M1 |
| E1 scheduled calendar | Sessions to/from FOMC, CPI, payrolls; pre/post exchange holiday; early close; month/quarter end | Scheduled events alter return/risk distributions | Add E1 alone before interactions |
| M2 releases | First-release CPI growth, unemployment/payroll changes, release age, forecast errors only with an archived expectation | Slow macro state changes conditional returns | Compare M2 incremental to M1 |
| P1 price action | Overnight vs intraday decomposition; gap/ATR; close location; prior breakout distance; realized semivariance; volatility-of-volatility | Price moves have different meanings by liquidity/risk state | Each group introduced independently |
| X1 interactions | Momentum×VIX, curve×equity momentum, FOMC×volatility | Economic state moderates otherwise weak predictors | Small declared interaction list |
| R1 adaptive regimes | Trailing volatility percentile; causal trend regime; filtered state probabilities | Adaptive models reduce stale-history effects | Fixed-window vs regime/recency variant |

Every feature must have a formula, timestamp lineage and expected sign or reason for sign ambiguity. Fit percentiles, winsorization bounds, PCA, correlation pruning and clustering on eligible training data only. If a hidden-state model is used, use filtered past-information probabilities, never full-sample smoothed states. Avoid centered moving averages and global z-scores.

Do not add hundreds of near-duplicate indicators merely to inflate dimension. Compare fixed economically motivated features, controlled random nonlinear expansion and a richer data block separately.

### 7.3 Holiday and global-event design

Keep three categories distinct:

1. **Known schedule:** holiday, early-close and announced FOMC/release dates. Future schedule proximity can be a feature only if the schedule was known at the signal time.
2. **Observed surprise/event:** emergency policy change, invasion or bank failure. Features activate only after a documented publication timestamp.
3. **Retrospective annotation:** market peaks, troughs, recession boundaries and manually selected crisis episodes. These may label charts and stress tables but cannot become contemporaneously known predictors.

The current “COVID market peak” and “COVID market trough” entries belong to category 3. Brexit voting day and result publication are different events. A recession indicator dated to economic onset may have been announced much later.

Predeclare candidate annotation families: financial crisis, euro-area stress, US fiscal/debt episodes, trade-policy changes, pandemic interventions, invasion/energy shocks and banking stress. Link each selected marker to a primary dated source before inclusion. Do not label every large loss with a convenient story.

Event study: choose [-5,+5] sessions plus pre-event estimation interval, compare changes in return, volatility, volume, forecast and position; report counts, overlapping-event treatment and block intervals. Scheduled event panels can pool repeated announcements; one-off crises support descriptive case studies rather than strong causal identification. “Actual minus previous release” is not a market surprise without a credible expectation measure.

## 8. Model program and rigorous complexity experiments

### 8.1 Recommended model order

1. **Controls:** historical mean, correctly specified lagged-return regression, ridge, buy-and-hold, cash, causal 200-day trend filter and causal volatility-managed SPY.
2. **Strong tabular challengers:** XGBoost histogram trees and CatBoost CPU; keep current shallow RF/extra trees/HistGB as controls. LightGBM is a useful later comparison if installation and profiling are satisfactory, but three nearly identical boosting sweeps should not consume the whole budget.
3. **Controlled complexity:** RFF ridge with normalized penalty and multiple map seeds; PCA ridge and regularized splines as interpretable controls.
4. **Neural challengers:** small residual MLP and causal TCN. Sequence lengths 20/60 sessions, one or two hidden stages, width 16/64, dropout 0/0.2, weight decay and Huber or squared loss.
5. **Optional bounded challenge:** compact transformer or LSTM on identical sample/timing contracts after stronger tabular models. Treat these as hypotheses; approximately 5,000 daily observations do not automatically support large networks. Pretrained financial/foundation models require a training-corpus/time audit before any OOS claim.
6. **Ensemble:** equal-weight or nonnegative regularized combination of genuinely out-of-fold forecasts. Fit ensemble weights and any calibration only on earlier inner predictions.

No universal best model can be named before evaluation. The selected model may remain a regularized linear baseline or a simple allocation rule.

### 8.2 Capacity versus error

For RFF, declare components {16, 64, 256, 1,024, 4,096} and normalized ridge penalties {0.001, 0.01, 0.1, 1, 10, 100}. First run a reduced declared subset; reserve the complete matrix for the deep extension. Reuse a seeded maximal feature map's prefixes where appropriate so differences do not mainly reflect random-map changes. Repeat shortlisted maps on seeds 17, 29 and 43.

Report training observations T, approximation dimension P, fitted coefficients, penalty and effective degrees of freedom, such as `trace(Z (Z'Z + λI)^−1 Z')` under the documented normalization. A tree leaf count and a neural weight count are different complexity proxies; do not label all P/T=1 boundaries as the same interpolation phenomenon.

For boosting: depth {2,4,6}, regularization bounds, learning rates {0.01,0.03,0.1}, maximum 2,000 rounds and chronological early stopping. For neural models: max 200 epochs, patience 20 and minimum meaningful improvement; save best inner-validation epoch and convergence history. Report actual rounds/epochs, not just limits. Epochs are not a useful tuning axis for closed-form ridge.

Use a trailing inner-validation block with label purging for early stopping. Then refit on the full eligible outer training sample with the selected iteration count. Never early-stop on the outer test block.

Generate separate within-family plots of complexity versus OOS R², net utility, turnover, fit time and memory. Use matched fold sizes and seed bands. The current mixed-family train/OOS MSE scatter compares different return regimes; lower OOS MSE can reflect lower market volatility, not superior generalization. Add baseline-normalized loss and fold-specific residual diagnostics.

### 8.3 Objective and selection

Primary deployment objective should be declared in advance, for example net mean-variance utility at fixed risk aversion and a position cap. Secondary diagnostics: excess Sharpe, OOS R², drawdown, turnover and stability. Report performance differences relative to both buy-and-hold and risk-matched benchmarks.

Select in inner validation; report outer blocks without ranking them into a new winner. Include a simple-model preference within a block-bootstrap uncertainty band. If incremental utility is not credible, record “no improvement over baseline.” Do not promise to obtain significance by increasing the search.

For assignment compliance, prefer a small frozen grid/random list. If Optuna TPE is used, predeclare bounds, seed, maximum trial count and objective, and disclose that proposals are adaptive within inner training folds [S8]. This is a methodological extension, not a claim to have used a fixed grid. Use the same inner folds for comparable trials. Pruning must not discard difficult historical regimes selectively: prune only after all candidate methods have comparable initial fold evidence or use a fixed pilot phase.

## 9. Backtesting and inference upgrades

### 9.1 Strategy mappings

Compare only a small declared family after forecast comparisons:

- Original binary hurdle rule, preserved as a control.
- Long/cash classification with calibrated probability and expected payoff estimate; probability alone does not measure economic magnitude.
- Capped risk-scaled exposure `clip(k * expected_excess_return / predicted_variance, 0, 1)` with k chosen on earlier data.
- No-trade band/hysteresis to reduce turnover; thresholds tuned only inside the development protocol.

Evaluate cost scenarios 0, 2, 5, 10 and 20 bp on identical predictions. Model a lagged cash-rate accrual in a separate ledger version, with correct yield-to-daily-return conversion and calendar-day accrual. A quoted annual yield divided blindly by 252 is not always the applicable convention. Report any initial/final transaction charges for the investable benchmark.

### 9.2 Metrics and uncertainty

Required: arithmetic annualized net return, annualized volatility, explicitly defined Sharpe, matched benchmark. Add CAGR, drawdown and duration, turnover, exposure, trade count, downside capture and tail loss. Forecast panels include MAE, MSE, OOS R², directional accuracy against majority-sign baseline, calibration and residual autocorrelation.

Use paired stationary or moving-block bootstrap intervals with blocks {5,20,60} sessions and at least 2,000 resamples for finalists; state method and assumptions. Add HAC loss-difference tests and, if nested models are compared, the relevant nested-model adjustment rather than an unqualified t-test. For repeated model selection, report trial counts and consider a deflated Sharpe or a block-based reality-check procedure only after implementing and validating it correctly. Neither procedure cancels all selection bias.

CAPM/factor attribution can help explain low exposure and market beta. Estimate strategy excess returns against matched excess factors with HAC errors; report alpha, beta, uncertainty and sample coverage. A positive low-beta return is not automatically alpha. Event-window findings require multiplicity control and cannot establish why a particular price move occurred.

## 10. Explainability over time

Prioritize **TreeSHAP plus grouped permutation importance and ablation**. LIME is optional local triangulation, not the primary explanation for correlated time-series features.

At every chosen refit:

1. Retain the fitted preprocessing and estimator snapshot, feature names, seed and eligible data hash.
2. Use a reproducible training-only background, e.g. 128–256 rows sampled from eligible history; record the SHAP dependence assumption [S7].
3. Explain later OOS forecasts, including sampled normal sessions and predeclared extreme-error/trade cases. Case selection is retrospective interpretation, not model selection.
4. Save signed contributions in return units, baseline prediction, raw prediction and any transformation/calibration.
5. Verify additivity within numerical tolerance where supported. Report model-agnostic approximation error where exact explanation is unavailable.
6. Aggregate by feature group and quarter/year: mean absolute contribution, signed distribution, rank persistence and top-feature turnover.

Use a training-only frozen reference background within an outer fold to compare attribution changes; a moving background changes the reference distribution and must be labeled. SHAP distributions can change because the input regime, model parameters or background changed. They do not prove changing causal effects.

For highly correlated lags, perturb feature groups in blocks rather than independently producing impossible combinations. Evaluate held-out loss/utility changes with a dependence-aware permutation design. ALE or restricted dependence plots help explain nonlinear shape, but warn about sparse support.

A return explanation should separate forecast drivers, threshold/weight transformation, market move and trading cost. SHAP explains a model output, not the realized market return. For a disappointing trade show the forecast, its attribution, uncertainty, realized outcome and cost, without claiming the attribution caused the outcome.

## 11. Visual research and writing specification

Use restrained navy/teal with rust for negative values, consistent legends, serif report typography and ≥8–9 pt labels **at final printed size**. Export vector PDF/SVG for plots where supported and 300 dpi PNG for DOCX. Plotnine/ggplot-style grammar is optional; consistent semantics and readability matter more than the library.

| Figure | Design | Analytical question | Required explanation |
|---|---|---|---|
| Data quality | Row-count waterfall + coverage heatmap | What changed during cleaning? | Counts, retained extremes and unresolved gaps |
| Temporal protocol | Training/validation/test bands with label intervals | What was known at each fit? | Warm-up, release lag, purging and inspected-period status |
| Market context | Price/wealth, yield/VIX and exposure aligned panels | What changed around risk episodes? | Dated annotations, association not causal claim |
| Return distributions | ECDF plus KDE/violin small multiples by regime | Are tails/skew changing? | Bandwidth, common scale, counts and tail quantiles |
| Calendar effects | Holiday/FOMC raincloud or violin with interval estimates | Do event/non-event distributions differ? | Actual exchange sessions, sample sizes, uncertainty |
| Seasonality | Year×month return heatmap with annotations and side marginal summaries | Is seasonality stable across years? | Fixed scale, losses/gains, incomplete periods |
| Feature dependence | Clustered group matrix + top positive/negative pair panels | Which features are redundant? | Train-only clustering, readable names, exact correlations |
| Ablation | Paired effect forest plot | Does each block add value? | Same dates/seeds and confidence interval |
| Complexity | P/T×penalty heatmaps, separate families | Where does capacity help? | Effective complexity, repetitions and chosen region |
| Learning | Epoch/round loss curves + seed bands | When does overfitting start? | Inner validation only and stopping epoch |
| Runtime | Accuracy/utility versus wall-time Pareto plot | What is the compute return? | Hardware, actual time, peak memory and fold count |
| Forecasts | Calibration bins, residual ACF, rolling R² | Where does prediction fail? | Baseline comparison and uncertainty |
| Performance | Wealth/drawdown/exposure with a shared date axis | What produced economic outcomes? | P&L dates, cash, costs and realized risk |
| Attribution | Quarterly feature-group SHAP heatmap + local waterfalls | Which model drivers change over time? | Background, sign, units and non-causality |
| Events | Small-multiple event paths and outcome table | Is behavior robust across episodes? | All predeclared episodes including failures |

Every figure must have: source dataset/run/hash; time span; sample size; axis definitions/units; one descriptive finding; one interpretation; one limitation; and a cross-reference in the main text. A caption is not a substitute for discussion.

Example prose contract: “Figure X shows … on … observations. The estimated difference is … with … uncertainty. This is consistent with … but cannot distinguish … . The result motivates … .” Populate from artifacts, never fabricate a movement explanation from the chart alone.

Price-action case studies should distinguish documented contemporaneous facts from inferred mechanisms. Match actual announcement timestamps to the signal cutoff and give alternative explanations. A historical crisis band does not identify causality.

## 12. Three-to-five-hour compute plan

### 12.1 Machine and execution assumptions

The previous project inventory records **MacBook Air M1, 8 CPU cores, 16 GB unified memory**. This review could read the prior inventory but a new sandboxed `sysctl` probe was denied; therefore these are prior recorded specifications, not a freshly verified hardware claim.

Start with total active-process memory below roughly 8 GB and one/two concurrent fits; profile sustained runs because a fanless laptop can slow under heat. Use CPU for tree boosting. PyTorch MPS can accelerate compatible neural operations on Apple Silicon [S9], but CUDA-based CatBoost GPU execution is not an M1 option [S10]. Compare CPU versus MPS on the actual small sequence batch; acceleration is not guaranteed. Windows CPU fallback is required; CUDA only when compatible hardware exists.

Use float64 for numerical solves and financial accounting. Float32 tree/network arrays are acceptable after prediction/metric reconciliation. No nested parallelism: either parallel outer jobs with one thread per job, or one estimator with limited threads. Record observed behavior.

### 12.2 Bounded experiment ledger

A practical **base three-hour session** can allocate:

| Stage | Budget | Planned work / fit bound |
|---|---:|---|
| Integrity and timing pilot | 15 min | Audit + early/mid/late representative fit times; no parameter selection on final data |
| Baseline and data-block ablation | 25 min | 6 declared variants × 12 development refits = 72 fits |
| Capacity/family screening | 55 min | 32 declared configurations × 12 refits = 384 fits |
| Full temporal confirmation | 50 min | 4 survivors × 24 refits = 96 fits |
| Seed and window sensitivity | 20 min | 2 survivors × 2 additional seeds × 12 refits = 48 fits |
| Uncertainty and explanation | 15 min | Finalists only; bounded background and OOS sample |
| **Total** | **180 min** | **600 scheduled model fits, excluding pilot** |

Twelve-refit screening is a declared approximation for development triage; it does not replace full monthly OOS confirmation. Candidate comparison must use the same refit dates. If the pilot predicts 600 fits will not fit the budget, reduce the frozen candidate allocation **before** the experiment, log the decision, and preserve full evaluation for the survivors.

Optional additional two hours: 40 minutes for high-dimensional RFF, 45 minutes for compact MLP/TCN challengers and training curves, 20 minutes for a 5/20-session horizon comparison, 15 minutes for explanation/event robustness. These are allocations, not measured completion promises. Full nested multi-window, multi-source, multi-horizon replication will likely require multiple sessions; it is not honestly compressible into one guaranteed five-hour run.

Runtime projection: sum measured seconds per fit by family and training size, account for checkpoint hits and measured parallel efficiency, then add a thermal/I/O margin. For 5,000 × 4,096 float64 RFF values, one design matrix is ~164 MB (decimal); factorization, Gram matrices, copies and processes add substantial memory. Reuse decompositions/feature transforms across penalties where mathematically valid. Consider primal versus dual solves; never materialize several large copies per worker without profiling.

### 12.3 Tracking, progress and restart

Run identity must hash source version, dirty-tree source hashes, dataset/vintages, protocol, features, folds, models, seeds, cost/mapping rules and environment. Save trial/fold/refit status, elapsed time, peak memory and exception diagnostics. ETA should use family-specific observed fit times and remaining work, with an uncertainty range early in execution.

Checkpoint atomically at each refit; persist model/preprocessor snapshots for explanation. Resume only when hashes agree; retain failed trials in the experiment ledger. Optional MLflow provides browsing of metrics/artifacts; existing content hashes remain the identity authority. A local SQLite-backed experiment registry can be sufficient. Disk/network data acquisition is budgeted separately from model fitting.

## 13. Sequential agent implementation backlog

These are future implementation work packets, not claims that the modules or commands already exist. Each packet should finish with its artifacts and acceptance evidence before the next dependent packet starts.

| ID | Dependencies | Implementation and suggested location | Deliverables | Acceptance gate |
|---|---|---|---|---|
| A00 | None | Archive v1 outputs and register inspected periods | v1 manifest + exposure log | Original hashes recoverable; no artifact overwritten |
| A01 | A00 | Repair report fact resolution in `reports/build_report_ieee.py` | Canonical facts table and corrected report | Selected IDs, parameters, dates and metrics reconcile |
| A02 | A00 | Audit ledger/date/drawdown in `evaluation.py` and `modeling.py` | Accounting audit, boundary fixtures | Hand-calculated paths reconcile; P&L dates explicit |
| A03 | A01–02 | Freeze v2 protocol in proposed `configs/research_v2.yaml` | Trial ledger, splits, objective, holdout status | No unbounded search or fresh-test mislabeling |
| A04 | A03 | Profile hardware/families in proposed `scripts/profile_compute.py` | Machine/environment record, runtime/memory projection | One/two-worker settings measured, budget feasible |
| A05 | A03 | Add proposed `data/fred.py`, rates/VIX/calendar adapters | Immutable snapshots, source registry | Coverage, licensing and availability provenance documented |
| A06 | A05 | Implement release-aware joins and source quality audit | As-of panel, release-age/missingness tables | No available_at later than signal time; vintage cases verified |
| A07 | A06 | Add M1/E1/M2/P1 blocks to feature registry | Full feature dictionary and versioned datasets | Formulas/windows/timing traceable; no future perturbation changes earlier features |
| A08 | A02,A07 | Extend benchmark ledger and cash convention | Baseline predictions, holdings, costs | All methods use common dates and comparable risk reporting |
| A09 | A03,A07 | Add nested forward splitter, window and horizon contracts | Fold manifest, purge/boundary audit | No overlapping target leakage; proper holding-period accounting |
| A10 | A04,A09 | Add bounded boosted-tree/RFF/neural configurations | Trial snapshots, inner loss curves, fit metadata | No outer-test early stopping; failed/converged status recorded |
| A11 | A08,A10 | Run planned feature and family screening | Complete screening results including failures | Fixed counts/folds; baseline no-improvement gate applied |
| A12 | A11 | Run finalists, seed/window and complexity ablations | Paired differences, complexity maps, runtime frontier | Comparable dates, matched features and seed bands |
| A13 | A12 | Add grouped SHAP/permutation and drift summaries | Explainer manifest, local and temporal attributions | Training-only background, additivity/approximation audit |
| A14 | A12 | Add bootstrap, HAC/factor and event analysis | Inference tables and case studies | Methods/citations match; sparse events not overinterpreted |
| A15 | A13–14 | Build proposed `figure_registry` with narrative facts | Exported figures + caption/source metadata | Printed labels readable; every figure discussed |
| A16 | A15 | Freeze candidate; execute eligible later/prospective evaluation | Locked predictions and independent-status record | No subsequent selection from evaluation results |
| A17 | A01,A16 | Rebuild 15–25-page report and supplement | `Group_16_Report.pdf`, source DOCX, evidence appendix | Contents, references, equations, roster and metrics verified |
| A18 | A17 | Clean-environment replay and video package | README/env/zip or repo + 15–25-minute video | Staff can reproduce stated outputs; accessible video link |

Suggested commit boundaries follow A00–A18. Changes to a frozen dataset, feature definition or protocol create a new run identity. A failed acceptance gate is an implementation task, not a reason to quietly exclude unfavorable evidence.

### First concrete implementation milestone

Complete A00–A04 before collecting more data or training a larger model. This corrects known report errors and fixes how future evidence will be judged. The next milestone is A05–A09: a release-aware macro/event panel and fair benchmark/split layer. Only then spend the long training budget.

## 14. Report architecture and publication-readiness gates

Suggested 20–23-page report allocation: cover/contents 2; question/data/cleaning 3; timing/features 3; EDA/statistics 3; model/validation/compute 3; results/robustness 3–4; interpretation/limitations 1–2; references and concise reproduction appendix 2–3. Adjust to fit the assignment; longer feature dictionaries and all trial details belong in a repository supplement.

Replace the current administrative risk-register/checklist space with relevant evidence where possible. Main report should center on one primary scientific question, one primary endpoint and a small number of interpretable ablations. The report is not a catalogue of every model attempted.

Publication-readiness criteria:

- No known discrepancy between text, chart, table and configuration identity.
- Full feature/release/label timing and source availability audit.
- An honest evaluation narrative accounting for already inspected periods.
- Strong simple and risk-matched benchmarks with costs and uncertainty.
- Controlled ablations that separate new data, more history and more capacity.
- Reproducible experiments and independent reproduction on a second environment.
- A literature comparison establishing what is actually new.
- Limitations that acknowledge observational inference and sample size.

Passing those gates supports a serious research manuscript; it does not guarantee acceptance by a journal or a successful trading strategy.

## 15. Resource/library decisions

- **bt:** useful for an independent portfolio-allocation cross-check of weights and costs. It does not replace feature timing, model validation or the canonical accounting contract.
- **Backtrader:** useful for a small independent event-driven execution check. Verify signal t / entry t+1 behavior explicitly before comparing numbers. Do not migrate the entire pipeline merely to obtain prettier plots.
- **pytrends:** optional separate research module. The local README calls it an unofficial API and flags backend fragility. Freeze requests and responses; investigate normalization and history coverage before any predictive use.
- **Matplotlib/Seaborn or plotnine:** publication figures generated from saved results with a shared style and artifact metadata. Interactive Plotly can support exploration, but static report figures need readable final-size exports.
- **SHAP:** temporal explanation layer for stored model snapshots, with dependency/feature dependence choices recorded.
- **Optuna/MLflow:** optional optimization/tracking interfaces; keep chronology, trial budget and content-addressed provenance explicit.

## 16. Primary-source research links

These sources inform proposed extensions; they do not validate the project's empirical claims. Availability, historical coverage and redistribution terms must be checked for each downloaded series.

- **S1 — FRED observations/vintage query:** https://fred.stlouisfed.org/docs/api/fred/series_observations.html
- **S2 — FRED real-time periods and defaults:** https://fred.stlouisfed.org/docs/api/fred/realtime_period.html
- **S3 — Federal Reserve FOMC calendar and historical links:** https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm
- **S4 — New York Fed effective funds rate:** https://www.newyorkfed.org/markets/reference-rates/effr ; market API https://markets.newyorkfed.org/static/docs/markets-api.html
- **S5 — Cboe VIX historical data:** https://www.cboe.com/tradable_products/vix/vix_historical_data
- **S6 — NYSE exchange calendar:** https://www.nyse.com/markets/hours-calendars ; BLS release archives https://www.bls.gov/bls/news-release/
- **S7 — SHAP TreeExplainer, background and perturbation choices:** https://shap.readthedocs.io/en/latest/generated/shap.TreeExplainer.html
- **S8 — Optuna optimization and pruning methods:** https://optuna.readthedocs.io/en/stable/tutorial/10_key_features/003_efficient_optimization_algorithms.html
- **S9 — PyTorch MPS backend:** https://docs.pytorch.org/docs/main/notes/mps.html
- **S10 — CatBoost GPU support:** https://catboost.ai/docs/en/features/training-on-gpu ; platform requirements https://catboost.ai/docs/en/concepts/cli-installation
- **S11 — XGBoost histogram tree methods:** https://xgboost.readthedocs.io/en/release_3.2.0/treemethod.html
- **S12 — Caldara–Iacoviello geopolitical risk data and research:** https://www.matteoiacoviello.com/gpr.htm

Additional required literature validation before submission: Kelly–Malamud–Zhou (2024), Chinco–Clark-Joseph–Ye (2019), suitable moving-block/bootstrap references, nested forecast comparison methods and multiple-testing corrections. The assignment already provides the two main finance-paper citations; cite their actual methodology where used rather than treating any complexity increase as a replication of their result.
