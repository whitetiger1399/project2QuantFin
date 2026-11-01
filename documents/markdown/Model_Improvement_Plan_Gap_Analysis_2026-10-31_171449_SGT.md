# Quant 2 Fin — Model Improvement Plan and Report Gap Analysis

**Review baseline:** 31 October 2026, 17:14:49 SGT (UTC+08:00)  
**Version:** 1.0 — initial evidence-based review  
**Reviewed report:** `reports/Project2_Team16_Report.docx`  
**Requirements:** `documents/markdown/Project2.md`  
**Scope:** report structure, assignment compliance, research claims, data and feature design, modeling, validation, trading, inference, EDA, figures, architecture, and reproducibility.  
**Status:** recommendations only; no model retraining or report changes performed.

## 1. Overall assessment and score

**Current overall quality score: 72/100.** This is a substantial, thoughtfully engineered course project with a stronger implementation than its report currently communicates. It is not yet a publication-ready empirical study. Its central improvement should be a more defensible evaluation and clearer evidence, rather than simply adding more model families or more charts.

The strongest contribution is a reproducible cross-market forecasting and signed intraday trading experiment with temporal alignment, regularization, staged selection, cost accounting, and candid rejection of a simple AI-displacement story. The weakest points are the retrospective status of the evaluation, current-vintage macro inputs in the selected feature set, incomplete presentation of forecast and cost results, and insufficient separation of sector timing from stock selection.

Weak returns do **not** themselves justify a lower grade: the assignment explicitly rewards process. The deductions below concern incomplete disclosure, unresolved validity questions, and evidence that is available but not shown.

### 1.1 Scoring rubric

These weights are reviewer-defined. The assignment gives **35 total points for the report/video package**, without assigning the subweights below. This is not an official predicted mark.

| Assessment area | Maximum | Awarded | Main basis for deduction |
|---|---:|---:|---|
| Research question, economic logic, hypothesis discipline | 10 | 8 | Good questions; predictive mechanism and contribution need sharper separation from AI-event narrative. |
| Data provenance, information timing, leakage control | 15 | 10 | Strong engineering; retrospective cohort and current-vintage fallbacks weaken strict point-in-time claims. |
| Feature engineering and preprocessing | 10 | 8 | Broad relevant design; exact formulas, dimensions, availability, and stability insufficiently exposed. |
| Model design, validation, selection, overfitting control | 15 | 11 | Appropriate families and time splits; test reuse history and search accounting need stronger disclosure. |
| Portfolio construction, costs, benchmark fairness | 10 | 7 | Signed ledger is explicit in code; report omits operational constants and matched investable comparison. |
| Forecast/economic evaluation and statistical inference | 15 | 10 | Useful saved metrics; key negative findings omitted, dependence handling uneven across analyses. |
| EDA, figures, architecture communication | 10 | 7 | Attractive, coherent visuals; redundant paths/tables and missing diagnostic evidence. |
| Report structure, scholarly positioning, interpretation | 10 | 7 | Logical sections; overly strong wording, repeated conclusions, thin related work. |
| Reproducibility and submission readiness | 5 | 4 | Excellent immutable evidence; report lacks exact commands, contribution note, and full environment specification. |
| **Total** | **100** | **72** | **Strong foundation with material evaluation/reporting gaps.** |

**Arithmetic equivalent:** 72% × 35 = **25.2/35**. Use this only as a normalized score, not a forecast of the instructor's award. The video, Canvas package, and team contribution balance were not assessed.

**Publication-readiness assessment: 58/100**, separately judged against a higher research bar: credible prospective or clearly qualified retrospective evidence, incremental contribution, matched benchmarks, dependence-aware uncertainty, execution realism, and full reproducibility. This second score is a judgment, not an IEEE certification or acceptance probability. A polished layout alone cannot raise this to publication standard.

### 1.2 Review coverage and boundaries

- Read the full DOCX text and tables, requirements, report builder, inherited configurations, selected modeling/trading/inference code, and pinned run artifacts.
- Rendered the actual DOCX successfully to **17 pages**, reviewed all pages in overview, and inspected the architecture and crowded model-comparison page at full size. The report satisfies the assignment's **15–25-page** range.
- Checked selected saved CSV/JSON results and recomputed class-frequency baselines from saved predictions. No new model experiment was run.
- Existing repository edits were preserved. This is a targeted evidence review, not an independent re-download of every data source or an exhaustive audit of every feature.
- “Confirmed” below means visible in the reviewed report, code, or saved artifacts. Proposed ablations and suspected implications are explicitly distinguished from demonstrated results.

## 2. What the existing evidence actually says

### 2.1 Results that should become the center of the report

| Quantity | 2025 historical replication | Jan–Sep 2026 retrospective extension | Interpretation |
|---|---:|---:|---|
| Trading sessions | 249 | 185 | Calendar-day sample size matters more than stock-day row count. |
| Net cumulative return | 0.086%, reported as 0.09% | 31.99% | Strong combined return is overwhelmingly concentrated in 2026. |
| Annualized net volatility | 12.55% | 18.37% | Required risk metric should be shown alongside return. |
| Net Sharpe, zero risk-free convention | 0.0696 | 2.1505 | Large regime/update-policy variation. |
| OOS R² versus zero | −0.4534% | +2.4974% | 2025 squared-error forecasts fail to beat zero. |
| OOS R² versus asset mean | −0.6836% | +2.1582% | 2025 also fails to beat the historical-mean forecast. |
| Mean daily cross-sectional Spearman IC | −0.02125 | −0.00325 | No positive average cross-sectional ranking evidence in either segment. |
| Directional accuracy | 55.58% | 55.78% | Needs class-imbalance and dependence-aware baselines. |
| Always-predict-down accuracy, descriptive | 53.69% | 55.08% | Directional gain is only about 1.89 and 0.70 percentage points respectively. |
| Nifty 50 regression alpha p-value, HAC | 0.813 | 0.0446 | 2026 result is nominal, regime-specific evidence, not a definitive discovery. |
| Block-bootstrap 95% Sharpe interval | [−1.937, 2.240] | [0.817, 3.525] | Report these intervals, not just an assertion that inference exists. |

Source: pinned final/extension leaderboards, `selected_model_inference.json`, and selected prediction rows; identifiers are in Section 12. The always-down statistic is a diagnostic class-frequency reference, not a newly selected trading rule. It does not account for costs or magnitude.

The selected model's **2023–2024 confirmation Sharpe is only 0.0311**, with annualized return approximately **−0.0278%**. It wins the configured ranking, but “wins confirmation” should not imply strong confirmation of an economically useful edge. A small positive arithmetic-mean Sharpe can coexist with negative compounded annual return; this is not automatically a calculation error.

### 2.2 Cost erosion is a major finding

The saved 2025 model evidence reports:

- Gross cumulative return: **11.047%**.
- Net cumulative return: **0.086%**.
- Gross Sharpe: **0.9043**; net Sharpe: **0.0696**.
- Mean daily two-sided turnover: **0.5569**.

The gross/net compounded-return difference is approximately **10.96 percentage points**. Do not label this difference the arithmetic sum of transaction costs; compounding matters. Show both the actual ledger cost sum and the compounded wealth effect.

This changes the improvement priority: investigate cost-aware calibration, trading thresholds, and stock selection before expanding the model zoo. The report currently attributes flat 2025 performance mainly to conservative hurdles and limited magnitude capture; it should explicitly discuss the much more directly documented gross-to-net erosion.

### 2.3 Recommended central conclusion

> The selected cross-market model exhibits conditional downside-timing value in a retrospective 2026 extension, but little net economic value in the 2025 replication. Its average cross-sectional ranking is weak, trading costs materially reduce returns, and direct AI-release evidence is inconclusive. The study supports further investigation of a defensive timing mechanism rather than a general claim of robust stock-selection alpha.

This conclusion is stronger scientifically than advertising the combined **32.10%** return. Keep the combined curve, but make the two segment results equally prominent in the abstract and results table.

## 3. Assignment requirement gap matrix

| Requirement | Existing evidence | Gap and exact improvement | Priority |
|---|---|---|---|
| §4.1 Assets, frequency, decision and fill timing | Ten named stocks; 08:55 IST decision; reported open-to-close trading | Add base currency INR, sample dates, holiday/stale-data rules, and opening-fill assumption in one contract table. | P0 |
| §4.1/4.3 Investable benchmark | Nifty IT/Nifty 50 index series and fixed-cohort passive basket | An index is a reference, not directly purchasable. Add a suitable verified ETF/futures implementation with dividends and costs, retaining index series as descriptive references. | P0 |
| §4.2 Labels and available features | Target equation, F0–F7 ladder, train-only cleaning | Add formulas, units, lookbacks, precise availability and feature counts. Identify current-vintage exceptions explicitly. | P0 |
| §4.4 Model story and overfitting | Shrinkage, PCA, trees, staged promotion | Explain sparse versus dense signal assumptions; distinguish timing and stock ranking; include completed RFF work. | P1 |
| §4.5 Training/validation/testing | Dates for screening, confirmation, final and extension | Add initial training period and actual 1,260-session rolling window, one-session embargo, plus prior inspection history. | P0 |
| §4.6 Training and reproducibility | Frozen model values and run IDs | Add solvers/training methods, seed 17, actual package versions, realized grid, and exact run commands. | P0 |
| §4.7 Validation and selection | 28 screening configurations; 13 confirmation rows | State primary metric, tie-breakers, promotion logic, searched versus baseline rows, and no-trade policy. | P0 |
| §4.8 Scores to positions, costs | Signed return equation and conceptual threshold | State actual 15 bps effective hurdle, top/bottom three, one-third cap, gross cap, and round-trip accounting. | P0 |
| §4.9 Evaluation | Wealth plots, Sharpe, regime and uncertainty discussion | Show selected-model forecast R², annual volatility, IC, gross/net comparison, uncertainty and matched baselines. | P0 |
| Interpretation and code/figure linkage | Limitations and immutable evidence IDs | Replace categorical claims with measured support; give each figure an input artifact and generation command. | P1 |
| Report format and contribution note | 17 pages and full roster | Add short contributions; verify requested `Group_X_Report.pdf` submission naming, with the team's group number. | P0 |
| 15–25-minute video and source package | Not assessed in this review | Verify end-to-end demonstration, exact commands, accessible/downloadable video, dependency lock, and submission packaging. | P0 |

P0 means necessary for an accurate, complete submission; P1 means high-value research improvement; P2 means optional extension. Advanced models and causal identification are not mandatory course requirements.

## 4. Critical validity and interpretation gaps

### G01 — Historical replication is not an untouched holdout [P0, confirmed]

`configs/cross_market_ai_services_research.yaml` explicitly says 2025 was inspected in an earlier project; `cross_market_ai_capability_research.yaml` calls it historical replication. The freeze was created on **31 October 2026**, after both displayed evaluation periods. That is compatible with temporally honest retrospective forecasts, but does not establish prospective precommitment.

The report instead repeatedly uses “frozen final,” “primary OOS estimate,” and “neither segment affected model selection.” The last claim may describe the mechanics of the latest run, but it does not disclose earlier researcher exposure.

**Fix:** distinguish three concepts everywhere: observations withheld from each estimator fit; dates excluded from the current selection routine; dates never seen by the research team. Label 2025 “historical replication, selected specification” and 2026 “retrospective extension, no reselection within this run.” Preserve internal `final_test` artifact IDs without treating the identifier as evidence of virgin test data. Add a short chronology of research iterations and design changes.

**Acceptance:** abstract, split table, captions, conclusion and README use consistent language. Any improved model gets a new version and is not presented as newly validated on 2025/2026.

### G02 — Point-in-time macro claims need qualification and an ablation [P0, confirmed metadata; effect unmeasured]

The processed feature dictionary contains **60 current-vintage fallback features** from 12 series, including Indian monthly macro series, credit spreads, FX-related series, yield spreads and VIX. Their `feature_sets` include **F7_full_context**, the selected feature set. The inherited base configuration's prose says revised monthly macro series are confined to an older F5 robustness setting; that wording no longer describes the selected F7 design.

A conservative release lag addresses publication delay, but cannot reconstruct values before subsequent revisions. The dictionary's `known_at_0855_ist=True` must therefore not be read as proof that the historical value itself was available then. Not every flagged series is necessarily materially revised; the issue is unsupported blanket certainty.

**Fix:** list affected series, actual selected-column usage by refit, vintage source, release lag, and revision status. Run a **strict-vintage variant excluding every flagged fallback** under an unchanged model/trading policy. Report its incremental loss/return difference as retrospective sensitivity. Rebuild true vintage histories where feasible; otherwise retain the exclusion.

**Acceptance:** a retained-feature audit proves what actually entered each fitted estimator, and the report distinguishes timestamp alignment from data-vintage integrity.

### G03 — Time-series timing and cross-sectional selection are conflated [P0/P1, confirmed metrics]

The saved mean daily IC is negative in both evaluation segments. There are also no mixed long/short days in the reported combined ledger. These facts are consistent with a common sector signal dominating stock-level rankings, but do not alone prove the mechanism.

**Fix:** decompose forecasts into a daily common component and stock-relative deviations. Compare the selected portfolio with (a) equal-weight cohort exposure using the same timing gate, (b) a simple predeclared U.S.-services directional rule, and (c) a stock-relative residual model. Attribute P&L to long side, short side, cash, and individual assets. Use paired dates and identical costs.

**Acceptance:** demonstrate incremental value of stock ranking over a matched timing-only strategy, or explicitly recast the contribution as timing. A Nifty 50 beta regression alone does not establish stock-specific alpha.

### G04 — Dependence handling is inconsistent across diagnostic tests [P1, confirmed code]

The portfolio analysis already includes a circular block bootstrap and HAC inference. However, `analyze_ai_capability_model_run.py` applies a binomial test to **2,490 stock-day outcomes**, compares accuracy to 50%, and computes simple calibration-bin standard errors. Stocks within one day are correlated. Calibration OLS applies ordinary HAC to flattened stock-day rows, which does not clearly represent calendar-time panel dependence.

**Fix:** bootstrap blocks of whole dates, preserving every asset in each sampled day. Use the same blocks for paired model comparisons. For calibration, use calendar-aware clustered/serial-dependence-robust inference or date-block bootstrap coefficients. Compare sign accuracy with a training-established majority-sign baseline as well as 50%. Do not headline the saved binomial p-value of approximately 1.37e−8 as strong independent evidence.

**Acceptance:** report day count, block length, repetitions, paired comparison definition, and sensitivity to reasonable block lengths. Label exploratory confidence intervals as conditional on the chosen specification.

### G05 — Model-search uncertainty remains [P1]

The 28-row screening grid is bounded, which is good. It is not necessarily the total research search: older studies, feature changes, strategy variants and later proposed grids also matter. Existing forecast comparison code contains Benjamini–Hochberg adjustments, so the gap is **not** absence of all multiplicity handling. Those adjustments do not automatically correct the selected strategy's performance for the full research search.

**Fix:** maintain an experiment ledger including failed, flat and discarded models. Report nominal and adjusted inference separately. If the trial history is sufficiently documented, add a deflated Sharpe analysis with stated assumptions about effective independent trials; otherwise acknowledge that the adjustment cannot be reliably estimated. Bailey and López de Prado motivate adjustment for selection and non-normality in the [original Deflated Sharpe Ratio paper](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf).

### G06 — Execution and comparators support a simulation, not demonstrated tradability [P0/P1]

The strategy buys/sells at vendor opens and exits at vendor closes, while main benchmarks use close-to-close index or passive returns. This mismatch is disclosed, but the matched intraday comparator is not prominent. The fixed-cohort basket is purchasable in principle, yet survivorship-conditioned; it does not establish historical index investability.

**Fix:** add the already available equal-weight open-to-close cohort baseline alongside passive buy-and-hold; distinguish these two similarly named series. Add cash and an investable broad-market reference with explicit total-return treatment. Model opening execution uncertainty, closing execution, stock-specific friction and unavailable short trades as sensitivities. Verify applicable venue/broker constraints before asserting any real implementation.

Keep a simple cost assumption if needed for the course; clearly state what it omits. Research-quality execution claims require stronger data and evidence than daily OHLC.

### G07 — Current importance plot is exploratory [P1, confirmed code]

`_fit_block(..., explain=True)` shuffles feature groups across individual stock-day rows once. This can break cross-asset/day structure and generate unrealistic combinations, especially for shared global features. Correlated groups can substitute for each other, so permutation loss increase is not an isolated economic contribution.

**Fix:** permute shared predictors in blocks of dates with assets kept together, repeat across seeds, and show uncertainty. Add leave-one-group-out refits with identical settings as a complementary test. State that importance measures predictive reliance, not causality.

### G08 — Metric definitions need a small accounting audit [P1, code observations]

`_annualized_metrics` computes Sharpe with no risk-free subtraction; its Sortino denominator is the standard deviation of returns clipped at zero rather than the usual square-root mean squared shortfall from a target. Its drawdown calculation starts at the first realized wealth point instead of explicitly including initial wealth 1.0, so an initial loss can be omitted from the peak baseline.

**Fix:** document the zero-cash-return convention or use a consistent risk-free series; specify the Sortino definition or adopt target downside deviation; include starting wealth in drawdown. Reconcile metrics across scripts before regenerating tables. These are implementation definitions/edge cases, not evidence that the headline cumulative returns are wrong.

## 5. Model and feature engineering review

### 5.1 What has actually been implemented

The pipeline applies relevant quantitative-finance/data-science principles. It is not missing feature engineering, preprocessing, regularization, or model selection as broad capabilities.

| Completed screening family | Configurations | Assessment and reporting action |
|---|---:|---|
| Zero forecast | 1 | Essential loss baseline; report no-trade/undefined Sharpe correctly. |
| Asset mean | 1 | Appropriate past-data forecast baseline; show estimation window. |
| Autoregression | 1 | Useful low-complexity benchmark; state actual inputs and estimator. |
| Ridge | 10 | Dense weak-signal baseline plus information ladder; distinguish ladder rows from other experiments. |
| Lasso | 2 | Sparse-signal comparator; report training-only feature selection and selection stability. |
| Elastic Net | 2 | Relevant for correlated predictors; best screening Sharpe −0.722, no confirmation result. |
| PCA + Ridge | 2 | Sensible compression; show components, explained variance and fold-specific fitting. |
| Histogram gradient boosting | 2 | Nonlinear comparator; screening Sharpe reaches 0.782 but does not remain the selected winner. |
| Extra Trees | 1 | Selected nonlinear ensemble; 250 trees, depth 8, leaf minimum 40, feature fraction 0.5. |
| Random Fourier features + Ridge | 6 | Already implemented and evaluated, but omitted from the report's family table/chart. |
| **Total** | **28** | **Actual saved screening rows, not all theoretically configured combinations.** |

The six RFF configurations have positive but small screening R² versus zero, zero turnover, zero portfolio return, and undefined Sharpe. This is an informative **forecast-to-trade threshold result**, not grounds to silently omit the family or call it an execution failure. It also connects directly to the assignment's complexity paper. Show “no trades / Sharpe undefined” and investigate forecast scale on development data.

The report's model table is therefore incomplete. An ordinary random forest exists as an option in a broader profile, but is **not** one of these 28 completed screening rows; do not describe it as tested here.

### 5.2 Existing controls worth preserving

- Rolling history restricted to dates before each prediction block; one-session embargo.
- Median imputation, variance/missingness filtering, winsorization, standardization, PCA and sparse-model preselection fit within the training data where applicable.
- Economic information hierarchy F0–F7; leave-one-out Indian peers; prior completed U.S. session mapping.
- Regularization, constrained tree depth/leaf size, bounded candidate search and frozen configuration IDs.
- Separate 2026 static-estimator policy and immutable provenance.

Explain why these controls fit the problem. Regularization addresses many weak/correlated predictors; shallow trees allow nonlinear conditional relationships while limiting unstable partitions. Heavy-tailed returns motivate robust loss/inference investigation, but **trees alone do not make estimation robust to outliers**.

### 5.3 Feature additions and revisions ranked by value

1. **Availability and missingness features:** source age, market-holiday flags, vintage status and missing-source indicators. Measure whether the model is using stale-data patterns rather than economics.
2. **Sector-relative lagged features:** stock return minus a leave-one-out sector return, residual momentum, relative volatility and breadth dispersion. Fit any beta/residualization using past data only.
3. **Common versus idiosyncratic decomposition:** model a market/sector component and a stock-relative component separately. Training labels may use realized outcomes; inference inputs cannot use same-day realized sector returns.
4. **Parsimonious cross-market surprise features:** U.S. services return relative to broad U.S. return, ADR-relative movements, and currency interactions available before 08:55. Compare against existing raw returns before adding more dimensions.
5. **Past-only regime state:** lagged trend, realized volatility, dispersion and drawdown. Keep the existing ex-post monthly ±3% regime labels out of training.
6. **AI context revision:** maintain a prospective event calendar with publication timestamps and disclosure status. Exclude current-vintage benchmark levels from tradable historical predictors. Parameter count and model capability are distinct constructs.

For each new feature require a mechanism, formula, units, availability timestamp, missing-value policy and development-only ablation. More features are useful only if they add reliable incremental evidence.

### 5.4 Proposed experiments — not yet measured results

Run a small, predeclared sequence. Preserve the current evidence as Version 1. Any experiment motivated by this review is exploratory on previously seen 2025/2026 data.

| ID | Experiment | Design and comparator | Success criterion | Priority |
|---|---|---|---|---|
| E1 | Strict-vintage Extra Trees | Same configuration; remove flagged fallback features; matched dates and policy | Determine whether claimed signal persists without vintage uncertainty; report deterioration honestly. | P0 |
| E2 | Timing-only versus stock-selection attribution | Same timing gate with equal-weight cohort; compare actual top-k selections | Positive incremental paired net value from ranking, or revise claim to timing. | P0 |
| E3 | Selected-family information ablations | Extra Trees F0, F2, F7; F7 minus U.S. services; F7 minus AI; fixed capacity | Quantify incremental information within the actual chosen family. | P1 |
| E4 | Cost-aware calibration and hurdle | Calibrate forecast scale using forward development folds; retain signed return accounting | Net utility improves across folds without relying on a few days or excessive concentration. | P1 |
| E5 | Revisit sparse/dense baselines fairly | Compact Elastic Net penalty/mixing grid; Ridge; PCA-Ridge; inspect convergence and scaling | Stable development loss/economic performance; never force Elastic Net into the winner role. | P1 |
| E6 | Explain existing RFF non-trading | Show prediction quantiles against 15 bps hurdle; inspect feature scale and shrinkage | Establish whether no trades reflect prudent abstention, excessive shrinkage, or implementation settings. | P1 |
| E7 | Robust regression or a two-stage decision model | Huber regression; alternatively calibrated sign model plus conditional magnitude | Better calibration/net performance than simple baselines, not merely higher accuracy. | P2 |
| E8 | Common-sector plus residual model | Separate time-series component and stock-relative residual forecasts | Improved daily IC and incremental selection P&L after costs. | P1 |
| E9 | Consistent refit/window sensitivity | Rolling versus expanding; compare quarterly versus static policies on development folds | Determine whether drift or update policy explains instability. | P1 |
| E10 | Simple fixed blend | Ridge + Extra Trees with development-fixed weights | Lower instability and drawdown without material cost inflation. | P2 |

Do not prioritize LSTM/Transformer models merely to appear advanced. Effective independent history is limited, and the strongest present gaps are not architecture capacity. The financial ML literature provides a basis for comparing regularized and nonlinear methods, but not a promise that a more complex method wins on this dataset; see [Gu, Kelly and Xiu](https://www.nber.org/papers/w25398).

For every experiment store: hypothesis, predeclared grid and maximum trial count, fold dates, seeds, input hashes, fitted preprocessing, predictions, trading policy, runtime and rejection reason. Use date-grouped forward folds; choose models only on development folds. Future observations collected after a genuine new freeze can provide prospective evidence. Do not call a newly chosen slice of already examined history untouched.

### 5.5 Exact trading rule that belongs in the report

The inherited configuration and `_strategy_ledger` implement:

- One-way modeled friction = 5 bps commission + 2.5 bps slippage = **7.5 bps**.
- Round-trip friction = **15 bps**.
- Effective forecast hurdle = max(5 bps configured hurdle, 15 bps round-trip cost) = **15 bps**.
- Long up to three forecasts above +15 bps; short up to three below −15 bps.
- If N positions qualify, absolute weight per position is min(1/3, 1/N), subject to the configured approximate one-third cap and gross exposure ≤1.
- Enter from cash at open; exit to cash at close. Two-sided turnover = 2 × gross exposure.
- Daily net return = weighted signed open-to-close returns − 0.00075 × two-sided turnover.

The +1/0/−1 architecture boxes are **directions**, not actual portfolio weights. Say so explicitly. Configuration fields for an AI-event override exist, but the active `signed_forecast` branch does **not** use that override; avoid inferring a forced AI-release short policy from inherited settings.

Existing cost sensitivity changes the cost-dependent hurdle and hence holdings. Present two distinct analyses: **fixed-holdings cost stress** to isolate friction, and **policy-responsive cost stress** that recomputes eligible trades. Also note that the sensitivity loop varies `top_k` while leaving configured `short_k` unchanged; a symmetric breadth experiment must vary both intentionally.

## 6. EDA plan: add new information instead of more price lines

Development EDA should use the declared development sample. Evaluation-period diagnostics are legitimate, but must be labeled retrospective and must not secretly drive a supposedly unchanged model.

| New diagnostic | Question answered | Exact visual/data design | What it replaces or adds |
|---|---|---|---|
| Target distribution and tail risk | How heavy-tailed is the actual traded label? | Open-to-close return ECDF or compact violins by stock; quantile table and tail exceedance rates | Replaces one repetitive normalized-price figure. |
| Overnight versus intraday decomposition | Is U.S. information already incorporated by the Indian open? | Compare aligned U.S. services returns with next Indian overnight gap and open-to-close return; same-date sample, intervals | Adds a direct mechanism test missing from close-price paths. |
| Lag-response profile | Is there a short-lived incremental spillover? | Past U.S. lags versus Indian intraday target; sector/broad-market-controlled sensitivity; block intervals | More informative than one static correlation matrix alone. |
| Coverage and freshness | Is the signal driven by data availability? | Monthly coverage heatmap plus observation-age distribution by feature family | Supplies evidence for current cleaning claims. |
| Rolling common-factor strength | Is this a stock-selection problem or sector timing? | Development rolling mean peer correlation, first-PC variance share and dispersion | Complements/reduces the symmetric peer heatmap. |
| Conditional response curves | Does U.S. signal sign/size matter nonlinearly? | Training-defined U.S.-return bins versus next Indian intraday mean, confidence bands and counts | Tests the economic rationale for tree models. |
| Feature dimension and redundancy | Where does complexity grow without information gain? | Retained features per refit, PCA effective rank, family counts; separate date and stock-row sample sizes | Complements the information ladder. |
| Forecast calibration | Are forecast magnitudes actionable? | Mean forecast versus realized return, zero and 45-degree lines, date-block intervals, ±15 bps references | Elevates existing calibration artifacts. |
| Drift and trade activation | Why does behavior differ in 2025 and 2026? | Forecast/feature distributions and threshold-crossing fractions by segment | Adds evidence beyond calling 2026 a falling regime. |
| Event-time abnormal returns | Are release effects economically distinct from broad moves? | Prespecified event window, benchmark-adjusted cumulative response, bands, event counts and overlap flags | Replaces price lines with many vertical markers as primary event evidence. |

Do not produce all ten as full-page main figures. Prioritize target/timing, calibration, coverage, and cost/attribution; put supporting diagnostics in an appendix. Event-study estimates remain associational without a credible identification design, especially with sparse overlapping events and current-vintage capability mappings.

## 7. Figure-by-figure improvement instructions

### 7.1 Existing figures

| Figure | Current value/problem | Specific change |
|---|---|---|
| 1 — Research architecture | Coherent style; arrows converge diagonally; availability gate looks like another input; ex-post branch is tiny | Redraw as the three-part architecture specified below. Distinguish preprocessing fit from transform and show actual evaluation policies. |
| 2 — Ten-stock normalized prices | One large winner compresses most trajectories; dense legend | Use log-scale normalized wealth or small multiples; directly label endpoint names. Keep one context plot only. |
| 3 — India/U.S. selected paths | Partly repeats Figure 2 and later AI paths; stock-path divergence does not prove tradable forecast value | Replace with overnight-versus-intraday response diagnostic; move original to appendix if needed. |
| 4 — Peer correlation | Symmetric cells duplicate information; close-to-close correlation differs from target horizon | Show clustered lower triangle; specify return definition and sample; add intraday/common-factor summary. |
| 5 — Aligned U.S./India correlation | Correctly respects timing; many small noisy cells | Keep if useful, add valid pair counts and uncertainty/FDR guidance; use a zero-centered scale and selected lag-response companion. |
| 6 — Ridge information ladder | Valuable controlled experiment; diagonal labels are small; mixes feature-design section with evaluation result | Move to Results. Use short F0–F7 labels, adjacent legend, feature counts, baseline zero line and paired uncertainty. Add selected-family ablation separately. |
| 7 — AI record-event price timeline | Repeats price trajectories; vertical labels crowded; record selection is ex-post | Compress into a calendar/coverage strip; label current-vintage mapping as retrospective and show calendar ending May 2025. |
| 8 — Event-stock response heatmap | Mixed responses useful descriptively; one session and raw returns provide weak event evidence | Use predeclared abnormal-return event-time curve with intervals; retain heatmap in appendix with event counts and timestamps. |
| 9 — Best family Sharpe by stage | Label crowding between panels; row order changes; changing family winners are not a fixed-model trajectory | Use fixed family rows and stage columns, numeric cells/dots, configuration ID markers and explicit missing/no-trade states. Include RFF; distinguish unpromoted from failed. |
| 10 — Combined wealth | Useful overview; masks nearly all gain arriving in 2026 | Keep boundary; add separate segment metrics and a drawdown panel. Title as retrospective combined display. |
| 11 — Monthly performance and positions | Important but dense daily exposure panel under monthly bars | Use common monthly axis and show mean exposure, active-day fraction and positive/negative P&L attribution. Define aggregation. |
| 12 — Grouped importance | Useful evidence but lacks stability and dependent-row permutation caveats | Add repeated date-block permutation intervals; consistent group ordering; separate panels if distributions differ markedly. |
| 13 — Stitched 2021–2026 wealth | Overlaps Figure 10; contains selection periods | Move to appendix; retain stage shading and selection-bias warning in the figure itself. |
| 14 — Annual returns | Duplicates adjacent detailed table | Keep either compact return heatmap or table; add volatility/Sharpe/active-days rather than repeating return bars. Mark 2026 partial year. |
| 15 — Regime means | Useful insight, but duplicates table and lacks uncertainty | Combine with Figure 16 into point-and-interval panels with counts and explicit ex-post labels. |
| 16 — Reversal means | Only 12/11 events; explanatory language exceeds measured mechanism | Add intervals, counts and per-event dots; keep asymmetric response as observation, not proof of why thresholds caused it. |

### 7.2 Architecture redesign: exact steps

**Diagram A: Research and inference architecture**

1. Arrange four source groups in one top row: Indian markets, completed U.S./global markets, macro, and timestamped AI releases/disclosures.
2. Connect them through one shared connector to a distinct **08:55 IST availability and vintage gate**. The gate filters inputs; it is not another data source.
3. Split below the gate into a training lane and a prediction lane. Training: eligible historical rows → fit cleaning/scaling/selection/PCA → fit estimator. Prediction: available current inputs → apply fitted transforms → forecast. A dashed connector transfers fitted state only.
4. Continue the prediction lane through forecast calibration/hurdle → long/short eligibility → weights/risk caps → open/close simulated execution → gross P&L → costs → net P&L.
5. Show output evaluation in two boxes: **2025 replication, quarterly refits** and **2026 extension, one pre-2026 fit**. Combined wealth is a small optional display downstream.
6. Put current-vintage Epoch scores in a separate gray **ex-post analysis** lane leading only to event/capability tests. No arrow from that lane to trading forecasts.
7. Use aligned rectangles, equal spacing, orthogonal connectors, one accent color for trainable steps and one for execution. Avoid diagonal arrow crossings and long prose inside boxes.

**Diagram B: Temporal validation and evidence-status timeline**

- Show initial data from July 2016, feature warmup, 2021–2022 screening, 2023–2024 confirmation, 2025 replication, and Jan–Sep 2026 extension.
- Add one magnified rolling fold: 1,260 prior sessions → one-session embargo → next quarterly forecast block. Earlier test labels may enter later refits only after they become available.
- Show the 2026 single-fit policy on a separate row; do not imply continuing quarterly updates there.
- Place the actual October 2026 freeze timestamp separately from the historical data periods. A historical training cutoff and a research freeze date are different events.
- Add a legend distinguishing development, historical evaluation and genuinely future data. No speculative future performance curve.

**Diagram C: Forecast-to-position numerical example**

Show three illustrative forecasts relative to ±15 bps thresholds, the eligible top/bottom names, capped signed weights, round-trip turnover, and net-return formula. Mark example values as illustrative, not observed performance. This makes the trading rule easier to understand than showing only +1/0/−1 boxes.

### 7.3 Visual specification and layout fixes

- Retain the restrained navy/teal style. Use orange or a patterned line for short/negative exposure, with labels so color is not the only encoding.
- Target 9–10 pt chart labels at final printed size; body text about 10.5–11 pt and captions at least approximately 9 pt where the page budget permits. Test actual rendered size, not source-image resolution alone.
- Use vector PDF/SVG masters for plots where supported; use sufficiently high-resolution embedded raster copies only when necessary. Avoid screenshots of charts.
- Remove internal chart titles when they duplicate the caption. Captions should state sample, units, return definition, uncertainty, and whether the plot is developmental or retrospective.
- Number substantive tables and cite them in text. Most current tables are unnumbered, making evidence harder to reference.
- In the rendered DOCX, the main combined metrics table splits across pages 10–11 and the attribution table across 11–12. Keep short tables together; keep headers repeated for unavoidable multi-page tables.
- Figure 9 on page 10 needs wider gutters or a single matrix layout; labels visually crowd adjacent panels.
- The contents page says Section 7 starts on page 12, which is correct, but groups declaration, references and appendices under page 15 even though references/Appendix A begin on page 16 and B/C on page 17. Use generated individual entries.
- Reduce the largely empty contents page if space is needed for exact methods. Keep institutional cover conventions if required.
- Remove the foreword sentence about avoiding first-person language and the planned-rerun sentence in Section 5.1. These are drafting/process notes, not scientific results.

## 8. Proposed report structure and page budget

Keep the assignment's 15–25-page constraint. Aim for about **21 pages**, including references and appendices; do not force an IEEE two-column template unless requested by the course. IEEE's author guidance supports a clear introduction, methods, results, discussion and conclusion, with a concise self-contained abstract; the layout below is adapted to this course deliverable. [IEEE article structure guidance](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-the-text-of-your-article/structure-your-article/)

| Section | Approximate pages | Content |
|---|---:|---|
| Cover, roster, compact contents | 2 | Team details; accurate navigation. |
| Abstract, introduction, contribution and related work | 2 | Conditional cross-market timing question; AI hypothesis secondary; limited novelty claim. |
| Data, target and information clock | 2 | Universe, snapshots, availability, vintages, benchmark definitions, cleaning evidence. |
| Hypothesis-driven EDA | 2 | Target tails, common component, overnight/intraday distinction and coverage. |
| Features and models | 2 | Feature dictionary summary, model assumptions/objectives, completed family inventory. |
| Experimental design and trading | 3 | Training windows, search, historical status, exact position rule, costs and metrics. |
| Results | 3 | Segment table, forecast baselines, wealth/drawdown, cost erosion and matched attribution. |
| Robustness and interpretation | 2 | Vintage/feature ablations, dependence-aware inference, regime limits and AI negative result. |
| Conclusion, contributions and declarations | 1 | Evidence-supported takeaways; team contributions and AI disclosure. |
| References and reproducibility appendix | 2 | Full citations, exact commands, software versions and evidence map. |
| **Total** | **21** | **Redistribute as needed without padding.** |

Suggested abstract order: research question → temporal/data design → selected model and rule → 2025 result → separate 2026 result → uncertainty/limitations → negative AI finding. Avoid giving the combined return more prominence than the separate estimates.

For related work, add a compact comparison of the two assigned papers and this study: market/frequency, information set, target, complexity control, evaluation and implementation assumptions. Verify bibliographic details against publisher sources; the Kelly paper page range differs between the supplied assignment and current report. Do not silently choose one without verification during revision.

## 9. Research-level evaluation package

### 9.1 Minimum main results table

For each segment and comparator show: observations/dates, cumulative net return, annualized return, volatility, Sharpe with convention, maximum drawdown, turnover, trading-day fraction, mean gross/net exposure, R² versus baseline, mean daily IC, and uncertainty where meaningful. Use separate panels for portfolio and forecast metrics to avoid an unreadable wide table.

Show baselines even when they fail to trade. Undefined Sharpe is not zero Sharpe. Report the selected configuration separately from any per-period best model; never pick the winning configuration retrospectively for each period and call that one strategy.

### 9.2 Required robustness questions

1. **Costs:** Does any net benefit survive higher friction with both frozen holdings and responsive thresholds?
2. **Exposure:** Does performance exceed a simple timing-only, same-exposure comparison?
3. **Concentration:** How much comes from the largest 1/5/10 winning days and individual stocks? Treat exclusions as sensitivity, not a new headline strategy.
4. **Data integrity:** What changes when current-vintage inputs are removed?
5. **Information value:** What changes when U.S. services or AI groups are removed from the selected family?
6. **Update policy:** How sensitive are results to static versus quarterly refits on comparable development windows?
7. **Forecast calibration:** Do predictions exceeding the hurdle have corresponding realized expected returns?
8. **Uncertainty:** Do paired conclusions survive day-block dependence and reasonable block lengths?
9. **Regimes:** Are results stable across regimes defined before observing the return, as well as descriptive realized regimes?
10. **Implementation:** What remains after realistic missing fills/short restrictions and investable benchmark treatment?

### 9.3 Claims to rewrite

| Current wording or implication | Better evidence-calibrated wording |
|---|---|
| “Leakage-controlled” / “strict temporal information set” without nearby vintage qualification | “Temporally aligned retrospective design, with identified current-vintage macro limitations.” |
| “Extra Trees generalizes better than simpler candidates” | “Extra Trees ranks highest under the configured confirmation metric; 2025 forecast and economic evidence remains weak.” |
| “U.S. services are predictively useful” from importance alone | “The fitted model relies on U.S.-services predictors; incremental value requires matched ablation.” |
| “Reversal response is slow because lagged signals and hurdles delay switching” | “Weak upward-reversal performance is observed; lag and hurdle effects are plausible mechanisms to test.” |
| “AI displacement rejected” as proof of no effect | “The available sample does not support the proposed negative effect; uncertainty and low power remain.” |
| “Full out-of-sample ledger” as a historical track record | “Stitched predictions from multiple research stages, including periods used for selection.” |

## 10. Prioritized execution plan

The course deadline is **12 November 2026, 23:59 SGT**, per the supplied requirements. The dates below are a proposed work plan, not scheduled automations. Estimates depend on artifact availability and compute.

### Phase A — Correct and complete the existing evidence, 31 October–2 November

Estimated effort: 1–2 focused working days.

- [ ] G01: correct historical-evaluation language and add research chronology.
- [ ] G02: identify actual fallback columns retained by each model refit; qualify timing claims.
- [ ] Add the segment-level forecast/economic metrics and gross/net cost evidence already saved.
- [ ] Add exact training window, seed, selection rule, trade hurdle, weights, costs and update policies.
- [ ] Add RFF/no-trade outcomes and remove unperformed-rerun narrative.
- [ ] Add matched intraday benchmark and clearly distinguish passive cohort from daily equal-weight intraday series.
- [ ] Verify metric conventions, drawdown initialization and consistency across reporting scripts.

**Exit criterion:** every primary claim can be traced to a table or artifact, and no wording suggests pristine evaluation where it did not occur.

### Phase B — Focused diagnostics and limited experiments, 3–6 November

Estimated effort: 2–3 working days plus compute; register a compact budget before running.

- [ ] E1 strict-vintage sensitivity.
- [ ] E2 timing-versus-selection attribution.
- [ ] E3 selected-family information ablations, prioritizing U.S. services and AI removal.
- [ ] Date-block calibration/accuracy/importance uncertainty.
- [ ] Fixed-holdings and policy-responsive cost stress; stock/day concentration.
- [ ] Development-only overnight/intraday EDA and feature coverage/freshness evidence.

**Exit criterion:** a short results note states supported, unsupported and unresolved hypotheses. Negative findings are retained. No result-driven enlargement of the search without recording a new exploratory round.

### Phase C — Restructure and redraw, 7–9 November

Estimated effort: 1–2 working days.

- [ ] Follow the proposed section sequence; move stitched historical results to the appendix.
- [ ] Replace repetitive price plots with target/timing and cost/calibration diagnostics.
- [ ] Redraw architecture and validation timeline; fix Figure 9 and table pagination.
- [ ] Update abstract, conclusions, captions and bibliography from final evidence.
- [ ] Render the report and inspect every page at final size; update generated contents.

**Exit criterion:** 15–25 readable pages with a coherent claim → method → evidence → limitation sequence.

### Phase D — Reproducibility and submission, 10–12 November

- [ ] Run the documented verification commands on pinned artifacts; retain logs and distinguish rerun checks from historical reported counts.
- [ ] Record resolved package versions/lockfile, seeds, actual grids, exact commands and expected outputs.
- [ ] Add team contribution statement and verify citation/data permissions.
- [ ] Record a 15–25-minute video showing data → preprocessing → fitting/selection → predictions → costs → evaluation.
- [ ] Verify PDF name, roster, code archive/link, video accessibility and Canvas package.

**Exit criterion:** another reviewer can reproduce the displayed outputs from the supplied instructions and locate each figure's evidence.

### Beyond the course deadline

Prospectively freeze the strongest well-defined variant, maintain the event/data availability calendar, and collect genuinely future observations. A longer sample spanning both rising and falling markets, stronger execution data and a documented historical universe are the largest publication-oriented gains. These cannot be manufactured by rerunning already inspected 2025/2026 data.

## 11. Improvement targets and decision discipline

**Report-quality target after Phase A/C/D: 82–86/100**, conditional on accurate revisions and completed submission evidence. This is a reviewer target, not a guaranteed grade. A rigorous negative-result report can reach it without improving returns.

**Research-readiness target after successful Phase B: approximately 70–78/100**, conditional on what the ablations actually establish. Stronger claims require additional evidence; an ablation that removes the apparent edge should reduce the claim, not be hidden.

Do not optimize this plan toward a higher backtest Sharpe. Optimize it toward answers to four questions:

1. Was the input genuinely available at the decision time, including its data vintage?
2. What improves beyond a fair simple baseline under the same trading contract?
3. How stable is that improvement across time, costs, assets and uncertainty procedures?
4. Can another person reproduce the result without undocumented choices?

## 12. Evidence map and review provenance

All paths below are repository-relative. Run IDs refer to reviewed immutable objects, not newly executed experiments.

### Primary documents and implementation

- [Project requirements](Project2.md): §§4.1–4.9, deliverables, grading principle and deadline.
- [Reviewed report](../../reports/Project2_Team16_Report.docx): Sections 1–8, Figures 1–16, appendices.
- [Report builder](../../reports/build_report_ai_capability.py): pinned inputs, combined and stitched performance displays.
- [Report layout components](../../reports/report_components.py): table/figure and document styling.
- [Capability configuration](../../configs/cross_market_ai_capability_research.yaml), [services parent](../../configs/cross_market_ai_services_research.yaml), [base configuration](../../configs/cross_market_research.yaml): feature sets, search, timing, costs and interpretation.
- [2026 extension configuration](../../configs/cross_market_ai_capability_2026_extension.yaml): retrospective static-estimator policy.
- [Modeling/evaluation implementation](../../src/quantfin/cross_market/experiments.py): `_fit_block`, `_strategy_ledger`, `_annualized_metrics`, `cost_sensitivity`, `inferential_tests`.
- [Model-evidence analysis](../../scripts/analyze_ai_capability_model_run.py): calibration, sign accuracy and diagnostic exports.
- [Panel construction](../../src/quantfin/cross_market/panel.py): macro availability and fallback handling.

### Pinned artifacts

| Evidence | Identifier / location |
|---|---|
| Dataset | `data/processed/cross_market_ai_capability/ai_capability_panel_20261031T063249Z_928de985ea1dd4f8` |
| Screening | `artifacts/cross_market_ai_capability/runs/cm_ai_capability_screening_20261031T063709Z_72f2f3e05783` |
| Confirmation | `artifacts/cross_market_ai_capability/runs/cm_ai_capability_confirmation_20261031T065831Z_c343cf83e423` |
| Freeze | `artifacts/cross_market_ai_capability/freezes/cm_ai_capability_freeze_20261031T071336Z_cb837a5393f8.json` |
| 2025 replication | `artifacts/cross_market_ai_capability/runs/cm_ai_capability_final_test_20261031T071400Z_864e226d8bad` |
| 2026 extension | `artifacts/cross_market_ai_capability_2026/runs/cm_ai_capability_2026_forward_20261031T072912Z_885ecbb56a0e` |
| Model evidence | `artifacts/cross_market_ai_capability/analysis/model_evidence_final_test_20261031T072352Z_b18bf0b8f6a6` |
| Selected specification | `cm_extra_trees_05a83581b70b` |

The current report states 200 pipeline verification checks and 28 extension checks passed. This review did not rerun those suites; it treats those counts as reported provenance, not as independently repeated verification.

### Change log

| Version | Review timestamp | Change | Status |
|---|---|---|---|
| 1.0 | 2026-10-31 17:14:49 SGT | Initial report/model gap analysis, evidence-backed scores, figure redesign and prioritized execution plan | Review complete; improvement actions pending |
| 1.1 | 2026-10-31 SGT | Implemented leakage exclusions, six matched diagnostic configurations, timing/ranking strategy attribution, fixed-versus-responsive cost sensitivity, corrected Sortino/drawdown accounting, whole-date block inference and permutation importance, report architecture/results/limitations revisions, and reproducible run commands | Code and report implementation complete; fresh diagnostic artifacts require user-executed runs |

### Implementation status by action class

| Status | Implemented items | Evidence / next action |
|---|---|---|
| Implemented in code | Strict current-vintage exclusion switch; feature-family ablations; F0/F2/F7 matched Extra Trees diagnostics; U.S.-services and AI exclusion variants; timing-only, residual-ranking, always-long and always-short strategy ledgers; fixed-holdings and policy-responsive cost grids; corrected target-downside Sortino and initial-capital drawdown; whole-date block forecast inference; repeated whole-date grouped importance | `src/quantfin/cross_market/experiments.py`, `scripts/analyze_ai_capability_model_run.py`, `scripts/compare_ai_services_strategies.py`, and the `gap_diagnostics` profile in `configs/cross_market_ai_capability_research.yaml` |
| Implemented in report | Honest retrospective status; related-work comparison; exact data/target/benchmark/trading contracts; RFF disclosure; 2025/2026 segment metrics; cost erosion; reliance-not-causality language; redesigned architecture and model-stage figure; contribution statement; revised limitations and conclusion | Rebuild `reports/Project2_Team16_Report.docx` with `reports/build_report_ai_capability.py`; the current report deliberately retains historical artifact caveats until new diagnostics are run |
| Verification complete without model training | Unit tests for accounting/exclusions/timing strategy; Python compilation; diagnostic plan resolves to six configurations and 48 quarterly checkpoints | Rerun the commands in `AI_CAPABILITY_COMPLETE_RUNBOOK_2026-10-31.md`, Section 11, to create immutable result artifacts |
| Requires a fresh user-run artifact | Strict-vintage performance delta; matched U.S.-services and AI incremental value; date-block calibration confidence intervals; revised importance uncertainty; fixed-holdings cost break-even; timing-versus-ranking return attribution | Execute the focused gap diagnostic and strategy-comparison commands, then update only claims supported by those outputs |
| External or submission work | Licensed/official historical membership evidence, realistic auction/borrow/impact data, genuinely prospective evaluation, contribution percentages if required, and the recorded submission video | Cannot be inferred or manufactured from the current repository; complete with source owners and team members |

For later updates, append a dated change-log row and record completed action IDs, evidence artifacts, score rationale and any revised claims. Preserve this baseline for comparison.
