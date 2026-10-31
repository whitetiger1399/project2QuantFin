# Model Improvement and Report Gap Analysis

**Review date:** 31 October 2026, 16:48:08 SGT (UTC+08:00).  
**Course:** Data Science in Quantitative Finance DSA5205.  
**Team:** Project2 Teams 16.  
**Scope:** Review and implementation plan only. No training, strategy changes, report regeneration, or replacement of previous analyses is authorized by this document.

## 1. Assessment

The project has a substantial implementation: immutable data snapshots, an explicit pre-open information clock, daily open-to-close targets, a feature progression, multiple model families, chronological screening and confirmation, a frozen specification, signed trading with costs, and reproducible artifacts. The report is already considerably beyond a minimal assignment in breadth.

The main remaining problem is **the strength and consistency of the evidence**, rather than a shortage of models. The next iteration should first reconcile historical evaluation claims, benchmark accounting, event timestamps, and feature ablations. Adding complexity before addressing those issues would make interpretation harder.

The defensible present conclusion is: **a current-constituent, signed Nifty IT strategy has a favorable combined historical evaluation dominated by the declining 2026 segment; the report has not established robust incremental value from AI capability, or broad superiority across market regimes.** A stronger report can present this as a useful result without forcing statistical significance.

The assignment explicitly rewards process more than returns. It requests a 15–25-page PDF, a 15–25-minute video, reproducible code, and a short contribution note. It does not require an IEEE two-column format, a profitable strategy, or replication of either assigned paper. Use IEEE-quality evidence and presentation while retaining the required NUS cover and readable figures.

### Evidence and review boundaries

The review compared all extracted paragraphs and tables in `reports/Project2_Team16_Report.docx` with `documents/markdown/Project2.md`, inspected report-generation logic and selected saved configuration/results files, and visually checked existing rendered pages 4 and 8. Figure recommendations for the remaining pages use their captions, report placement, and plotting code; this is not a new all-page rendering certification. The existing render contains 17 pages. No independent clean-room reproduction or full audit of every raw observation was performed.

Evidence anchors, relative to the repository root:

| ID | Evidence |
|---|---|
| E1 | `documents/markdown/Project2.md`, particularly §§4.1–4.9 and §§5–7 |
| E2 | `reports/Project2_Team16_Report.docx`, sections, tables, and captions |
| E3 | `reports/build_report_ai_capability.py`: `research_period_diagnostics`, predictive correlation, event timeline/response, combined evaluation and report prose |
| E4 | `configs/cross_market_ai_capability_research.yaml`: study interpretation and feature sets |
| E5 | `configs/cross_market_ai_capability_2026_extension.yaml`: static retrospective extension policy |
| E6 | `configs/cross_market_ai_services_research.yaml`: inherited model profiles and signed strategy |
| E7 | `src/quantfin/cross_market/experiments.py`: `_strategy_ledger`, costs and position construction |
| E8 | `scripts/build_ai_capability_panel.py`: `_event_mapping` |
| E9 | `configs/frontier_ai_epoch_model_mapping.yaml` and `scripts/analyze_epoch_capability_market_effects.py` |
| E10 | `artifacts/cross_market_ai_capability/runs/`, pinned screening, confirmation and final leaderboards |
| E11 | `reports/_render_ai_capability_v2/page-4.png` and `page-8.png` |

Pinned runs reviewed: screening `cm_ai_capability_screening_20261031T063709Z_72f2f3e05783`; confirmation `cm_ai_capability_confirmation_20261031T065831Z_c343cf83e423`; final `cm_ai_capability_final_test_20261031T071400Z_864e226d8bad`. The report names extension `cm_ai_capability_2026_forward_20261031T072912Z_885ecbb56a0e` and selected configuration `cm_extra_trees_05a83581b70b`. Preserve these as historical evidence.

## 2. What the current results establish

The following values are reported results, not newly rerun estimates.

| Evidence | Current result | Defensible interpretation | Interpretation to avoid |
|---|---|---|---|
| January 2025–September 2026 | Model +32.10%; Nifty IT −33.83%; Nifty 50 −2.26%; model Sharpe 1.131 | Favorable compounded historical path under modeled costs | One prospectively untouched test or proven persistent alpha |
| 2025 | Model +0.09%, versus Nifty 50 +11.66% | Approximately capital preserving, with substantial opportunity cost | Broad benchmark dominance |
| 2026 through September | Model +31.99%, versus Nifty IT −25.94% | Strong performance in a declining sector segment | A full-year return or proof of AI displacement |
| Combined exposure categories | 19 long, 144 short, 271 flat days | Strongly defensive deployment | Complete stock-level attribution, or necessarily mutually exclusive gross exposures |
| Release event difference | +0.33 percentage points; reported HAC p = 0.191 | Insufficient evidence for the hypothesized negative effect | Proof that releases have no effect |
| Capability association | Epoch rank correlation 0.237, p = 0.289 | Exploratory and statistically inconclusive | A tradable real-time capability signal |
| Full research path, 2021–September 2026 | Model +42.32%; Nifty 50 +73.41%; current-member basket +141.21% | Useful retrospective opportunity-cost diagnostic | A second independent holdout result |

The model can have positive trading returns despite weak return-prediction metrics because the policy trades only a selected subset of forecasts. That possibility requires explicit calibration, exposure, and cost analysis; it is not an explanation by itself.

## 3. Assignment-to-report gap matrix

Priority definitions: **P0** correct before making stronger claims; **P1** high-value evidence improvement; **P2** optional extension. “Partial” means the report contains material but needs qualification or additional evidence, not that the whole implementation is absent.

| Requirement | Present coverage | Gap | Action and completion criterion | Priority |
|---|---|---|---|---|
| §4.1 Assets, frequency, decision and execution | Ten current Nifty IT constituents, daily, 08:55 IST, open–close | Current-cohort scope can be mistaken for a historical index strategy | State cohort snapshot date, membership conditioning, ticker continuity and exact execution assumptions; list all tradeable securities | P0 |
| §4.1/4.3 Investable benchmark | Nifty IT and Nifty 50 index series | Index values are reference series, not themselves directly purchasable instruments | Add an explicitly identified investable comparator with data provenance, costs and dividend convention; retain indices as references | P0 |
| §4.2 Labels and features | O–C formula, F0–F7, temporal clock | Exact feature counts, availability rules and exclusion totals are not consolidated | Produce a feature/data contract with units, lookbacks, availability, missingness and realized dimensions per fold | P1 |
| §4.2 Cleaning | OHLC quarantine, train-only transforms | Prose describes controls without quantifying their effect | Show counts and percentages before/after cleaning by source, year and symbol; distinguish unavailable from invalid | P1 |
| §4.4 Model justification | Sparse/dense shrinkage, nonlinear families | Family comparisons do not isolate information value or capacity | Matched-model ablations and a separate shrinkage–complexity experiment | P1 |
| §4.5 Splits and leakage | Chronological stages and freeze identifiers | Report language overstates untouched status relative to configuration | Use “historical replication” for 2025 and “retrospective forward extension” for 2026; retain refit boundary | P0 |
| §4.6 Training | Parameters, seeds/artifact framework | Actual solver, convergence and training sample details are dispersed | Add compact solver/preprocessing/convergence table generated from diagnostics | P1 |
| §4.7 Selection | Screening, confirmation, one selected model | Configuration counts and model availability need reconciliation | Distinguish promoted candidates, fixed information-ladder controls and baselines; publish objective and tie-break rule | P0 |
| §4.8 Trades and costs | Signed policy and turnover deduction | Exact threshold, weighting, mixed positions and execution feasibility are underexplained | Include numeric policy example and reconciliation to stock-day ledger; state cost and fill assumptions | P0 |
| §4.9 Evaluation | Wealth, yearly returns, regimes, importance | Annualized volatility and paired uncertainty should be visible beside returns; benchmark comparability incomplete | One primary performance table with interval, count, return, volatility, Sharpe, drawdown, exposure, costs and uncertainty | P1 |
| Interpretation | Limitations and negative AI evidence | Some explanatory claims exceed evidence; full research path called testing | Separate observed association, tested mechanism and speculation throughout | P0 |
| Reproducibility | Hashes, manifests, 200/28 checks cited | Checks do not establish economic validity; canonical commands not embedded in report | Exact commands and expected artifacts in appendix/README, plus provenance link for each claim | P1 |
| Submission | Cover, references and appendices | Contribution note, video and clean installation not established by this review | Verify separately; do not mark complete without evidence; prepare required `Group_16_Report.pdf` naming at submission | P1 |

## 4. Corrections that should precede new modeling

| ID | Finding and evidence | Required correction | Acceptance evidence |
|---|---|---|---|
| G01 | E4 explicitly calls 2025 historical replication, not untouched holdout. E2 says neither segment affected selection and implies strict untouched evaluation | Reconcile research history with run-level time ordering. A frozen run does not erase earlier inspection of the same dates | A protocol-history table identifying previously inspected periods, later hypotheses and freeze timestamps |
| G02 | E5 describes one pre-2026 fit, whereas 2025 uses walk-forward refits | Keep a combined wealth display, but disclose two estimator-update regimes; avoid attributing the change only to market conditions | Joined ledger has no duplicate/missing decision dates, boundary marker and separate segment diagnostics |
| G03 | E3 joins screening/confirmation/final/extension ledgers; E2 later calls this the complete testing record | Rename 2021–2026 “retrospective research-period diagnostics”; demote to appendix | No caption describes model-selection periods as independent holdout |
| G04 | E2 fairness box says every comparator shares target and costs, yet index buy-and-hold and daily O–C strategy have different exposure horizons | Replace blanket claim with a comparator contract; distinguish economic opportunity cost from matched forecast tests | Table specifies instrument, return convention, overnight exposure, initial capital and costs for each comparator |
| G05 | E3 passive basket normalizes at first evaluation close, then fills first daily return with zero | Audit entry timing: strategy trades first day while basket begins after that session; define and implement a common capital-start convention | Small hand-worked first-day example reconciles both wealth paths; missing constituent prices cannot silently change weights |
| G06 | Figure 1 includes Epoch benchmarks in the feature-flow box, contradicting ex-post-only policy in E9 | Split forecasting and retrospective event-analysis branches | No arrow from current-vintage Epoch scores into historical model training |
| G07 | E8 defines `post_us_reaction_date` as the Indian session after `tradable_date`; E3 uses it to look up U.S. returns in Figure 8 | Replace the date proxy with first eligible U.S. reaction session determined from release timestamp and exchange calendar | Worked examples for before/after U.S. close, weekends and Indian-only holidays; regenerate affected event outcomes |
| G08 | E9 permits “closest scored family variant”; Gemini 2.0 maps to a January 2025 Thinking variant | Audit exact release/version identity and score publication dates; label approximate mappings and exclude them from the primary event test | Per-event model/version/source/availability/mapping-confidence table; exact-version sensitivity result |
| G09 | E3 cross-market heatmap overwrites multiple U.S. sessions mapping to one Indian session | Declare latest-session versus accumulated-since-last-NSE information; compute both as separate estimands | Holiday mapping fixtures, observation-age metadata, common-session counts and no silent overwrite |
| G10 | E2 says 10 confirmation configurations; E10 contains 13 rows: eight ridge, Extra Trees, boosting and three baselines | Reconcile what “10” counts; label total evaluated, promoted and fixed controls separately | Counts generated from manifest/configuration IDs and leaderboard, with explanations |
| G11 | E2 groups Random Forest with Extra Trees; pinned screening has Extra Trees but no Random Forest | Distinguish supported code from executed models | Family table lists actual run counts and stage availability; no implied unrun results |
| G12 | Combined main chart has strategy and two indices; current-member buy-and-hold appears only in full-period diagnostics | Add the same-cohort passive comparator to the primary interval after accounting correction | Four comparator rows and curves on identical date coverage |
| G13 | Report infers slow signal rotation and cross-market usefulness from descriptive results/importance | Replace causal-sounding explanations with hypotheses until tested | Reversal latency and matched-group ablations support any mechanism claim |

These are not all findings of training leakage. For example, the Epoch diagram and U.S. event-date issue concern presentation/descriptive analysis; the reviewed mapping policy explicitly prohibits using Epoch scores as tradable historical features. Audit the affected scope before invalidating unrelated model results.

## 5. Data and feature engineering improvement design

### 5.1 Dataset contract

Create a human-readable table backed by a machine-readable manifest: source, symbol, security identifier, timezone, observed timestamp, available timestamp, session, raw/adjusted price convention, membership interval, retrieval time, missingness, quarantine reason, first/last usable date and training eligibility. Report both stock-day rows and unique trading dates. Ten correlated stock rows do not represent ten independent realizations of shared macro information.

| Area | Improvement | Test/output |
|---|---|---|
| Broad-universe coverage | Count requested, downloaded, eligible and missing securities over time; identify delisted/renamed failures | Coverage heatmap and denominator table; distinguish membership reconstruction from price survivorship |
| Corporate actions | Verify raw versus adjusted returns around representative splits/dividends and ticker/merger transitions | Event-level reconciliation; exclude unsupported continuity rather than splice names blindly |
| Missing data | Separate closed market, not-yet-listed, stale price, vendor failure and invalid OHLC | Missingness indicators where meaningful; train-only imputation; no fabricated target returns |
| Macro vintages | Separate genuine ALFRED vintage data from latest-vintage fallback | Exclude latest-vintage revised values from primary tradable features unless defensible historical availability is established; release lag alone does not remove revision leakage |
| FX | Retain close-to-close-only handling for Yahoo INR=X | No intraday OHLC-derived FX predictors; explicit availability timestamp |
| Cohort scope | Retain current members as the declared target, rather than quietly claiming historical membership | Limitation in abstract/data/conclusion; historical-index generalization remains untested |

### 5.2 Feature improvements worth testing

| Feature block | Specific candidates | Economic purpose and controls |
|---|---|---|
| Own history | Separate lagged overnight and intraday returns; 1/5/21-session momentum; 21/63-session volatility; downside volatility | Distinguish overnight price discovery from the intraday target; all India inputs end before decision day |
| Relative stock state | Return minus leave-one-out peer return; rolling beta/residual; peer dispersion and breadth | Separate common IT-sector timing from stock-specific opportunity; coefficients fitted on past observations |
| U.S. services | Latest return, cumulative return since previous NSE session, dispersion, downside breadth and observation age | Test spillover and Indian holiday effects without silently changing the lag definition |
| Cross-market interactions | U.S. services downside × India lagged volatility; services residual × INR return | Small economically motivated set instead of every pairwise interaction |
| Broad equities | Train-fitted PCA or sector aggregates alongside raw constituents | Test whether extra information survives dimension reduction; membership and preprocessing remain fold-local |
| Calendar | Low-order annual Fourier terms, day-of-week, pre/post-holiday indicators | Calendar known beforehand; treat as secondary controls, not a large seasonal feature dump |
| Macro | Available rate changes, curve slope, credit/FX state with documented lags | Differentiate policy-announcement surprise from level/trend; avoid unsupported “RBI rate” labels for proxies |
| AI | Verified event indicator, time since event, disclosed-scale increment, availability-qualified score increment | Separate release existence, capability level and surprise; missing score is not zero ability |

Rainfall, unrestricted high-order polynomials and many holiday interactions should not be primary additions without an IT-services mechanism and enough independent observations. Features should earn inclusion through development-sample ablations, not through visual appeal.

Feature selection must occur inside each training fold. For linear models, standardize and remove constant columns on training data; tune regularization on earlier validation blocks. Any supervised preselection must also be fold-local. For tree models, retain missingness semantics and control depth/leaf size. Publish raw, retained and effective feature counts rather than saying only “F7.”

## 6. Modeling experiments: bounded, comparable and informative

### 6.1 What has already been executed

The pinned screening leaderboard has **28 configurations**: zero (1), asset mean (1), autoregression (1), ridge (10), Lasso (2), Elastic Net (2), PCA–ridge (2), Extra Trees (1), histogram boosting (2), RFF–ridge (6). Confirmation has 13 and final has 12 rows including controls/baselines. Therefore, Elastic Net needs a stronger controlled evaluation, not a claim that it was absent. Random Forest is not present in this screening artifact.

The selected Extra Trees specification is 250 trees, depth 8, minimum leaf size 40 and feature subsampling 0.50, using F7. These are meaningful capacity controls. More trees primarily improve ensemble averaging; tree count alone is not equivalent to a neural-network parameter count or the high-dimensional linear complexity ratio.

### 6.2 Proposed experiment registry

All experiments below are proposals, not executed results. Freeze their grids and objectives before running. Previously viewed 2025/2026 data remain historical robustness evidence; genuinely new prospective data are needed for a new untouched claim.

| Experiment | Question | Controlled implementation | Main output / decision |
|---|---|---|---|
| M01 Information value | Does each market block improve forecasts/trades? | F0–F7 with identical Extra Trees parameters, then a small Elastic Net ladder; same dates, targets and policy | Paired daily loss/P&L differences with uncertainty; distinguish information from model-family changes |
| M02 Elastic Net | Does correlated sparse shrinkage beat current linear baselines? | Train-scaled penalty path, e.g. 6 penalties relative to training-derived maximum × L1 ratios 0.1/0.5/0.9; temporal inner validation; convergence diagnostics | Validation surface, sparsity, coefficient stability, runtime; promote only by declared rule |
| M03 Complexity | Can nonlinear expansion help under shrinkage? | RFF–ridge with realized feature-to-training-row ratios targeting 0.1/0.5/1/2/5/10, subject to explicit memory cap; 3 penalties and 3 fixed seeds in a focused experiment | Train/validation loss and net Sharpe versus realized ratio; capped cells labeled unavailable, never mislabeled as attained ratios |
| M04 Capacity | Is Extra Trees under/overfitting? | Depth 4/8/12 and leaf size 20/40/80 with fixed feature set; use development folds | Capacity/error plot plus train–validation gap and runtime; choose stable plateau, not best test point |
| M05 Temporal adaptability | Does update policy explain 2026 strength? | Same model on rolling 3/5-year versus expanding windows; monthly versus quarterly refits; static-fit control | Paired returns, turnover and fit cost; historical comparison explicitly post hoc |
| M06 Economic baselines | Is complexity better than simple defensive timing? | Cash, always-long same-day basket, always-short same-day basket, lagged U.S. services sign, own-history sign; identical cost/exposure caps | Incremental value beyond being short during a sector decline |
| M07 Forecast calibration | Are position hurdles meaningful? | Plot predicted-return bins against realized O–C return; calibrate only on earlier validation predictions | Reliability plot, sign error, expected versus realized net edge; no test-set threshold adjustment |
| M08 Panel structure | Does pooling obscure stock heterogeneity? | Pooled ridge/Elastic Net with asset indicators versus per-stock shrinkage with shared tuning policy | Per-stock paired errors and contribution; compare with common-sector forecast baseline |
| M09 AI incremental value | Does AI add useful information? | Matched model with/without event/parameter features; verified event calendar; Epoch excluded from historical trading unless vintage-qualified | Δloss/Δnet return, event/non-event results and confidence intervals; include zero/negative findings |
| M10 Optional alternative | Is a sign-and-magnitude model useful? | Regularized sign classifier plus conditional magnitude model; train-only probability calibration and cost threshold | Calibration and economic value against the simpler regression policy; defer if sample support is weak |

Do not run this entire Cartesian product. Start with M01, M02 and M06; then one focused M03 or M04 and M05. M08/M10 are optional. Existing histogram boosting is already a capable nonlinear comparator; a deep sequence model is not automatically a better use of a small, dependent daily panel.

### 6.3 Paper linkage and complexity definitions

Chinco, Clark-Joseph and Ye motivate sparse cross-stock lag selection and strict forward timing. This project adapts that principle to daily cross-market data; it does not replicate their minute-frequency setting. Report how many coefficients survive, how their identities change across refits, and whether their incremental predictions survive costs. [Published paper](https://onlinelibrary.wiley.com/doi/10.1111/jofi.12733).

Kelly, Malamud and Zhou motivate testing nonlinear feature expansion jointly with shrinkage. A larger raw feature list or a tree-family leaderboard alone does not test that mechanism. The proposed RFF experiment is an adaptation, and an unfavorable result remains informative. [Published paper](https://onlinelibrary.wiley.com/doi/full/10.1111/jofi.13298).

For every complexity result report: original predictors p, transformed predictors P, training stock-days n, unique dates T, retained features, regularization, and realized P/n and P/T. P/T is a dependence-aware descriptive companion, not a replacement for the paper’s formal ratio. For ridge, effective degrees of freedom can supplement raw dimension. Do not claim that “parameters divided by features exceeds 10” establishes overparameterization relative to observations. Do not compare tree node counts and linear coefficients as interchangeable capacity measures.

### 6.4 Selection and compute discipline

Keep date blocks intact across stocks. Inner validation must occur strictly before each outer evaluation block; fit scalers, imputation, selection, PCA and calibration inside training. When extending labels to multiple days, purge overlapping labels at split boundaries. A daily non-overlapping O–C target does not justify arbitrary long embargoes.

Predeclare one primary selection objective and cost convention, minimum activity requirements, and tie-breaks favoring stability/simplicity. Keep forecast loss and trading value as separate outcomes. Report all attempted configurations and failed/convergence-limited fits. Flat strategies with zero return variance have undefined Sharpe; do not display them as zero or silently drop them without explanation.

Use outer process parallelism with estimator/BLAS threads capped, cache fold-local transformed matrices, and checkpoint by dataset/configuration/fold/seed hashes. Calibrate runtime from a representative small pilot, including the slowest family. Budget the selected experiment batch rather than promising a 3–4-hour wall-clock limit without measurements. Stop a budgeted search at a declared boundary and report unfinished cells; do not alter evidence retrospectively to favor a winner.

## 7. Trading accounting and statistical evaluation

The inspected ledger uses `signed_forecast`, up to three long and three short candidates, a maximum gross exposure of 1, and maximum asset weight approximately 1/3. Configured one-way cost is 5 bps plus 2.5 bps slippage; the effective round-trip hurdle is therefore 15 bps, larger than the configured 5-bps forecast floor. It computes turnover as twice gross exposure, consistent with daily entry and full exit. These concrete facts belong in the report.

| Improvement | Implementation and reporting requirement |
|---|---|
| Complete decision audit | Stock-day export: prediction, hurdle, rank, signed weight, long/short/flat decision, fill prices, realized target, gross contribution, cost and net contribution |
| Portfolio classification | Identify mixed long-and-short days separately; net exposure near zero does not imply flat if gross exposure is positive |
| Accounting tests | Hand-worked one long, one short, mixed portfolio and flat day; reconcile contributions exactly to daily P&L and compounded wealth |
| Benchmark fairness | Add same-day always-long/short controls to isolate timing, alongside passive investable opportunity-cost benchmarks; document overnight and dividend differences |
| Cash and risk | State treatment of uninvested cash, risk-free rate in Sharpe, leverage/margin and zero-interest assumption if used |
| Execution realism | State open/close prices are fill proxies; report stronger slippage scenarios and blocked/unavailable trades; establish applicable short-selling assumptions before production claims |
| Uncertainty | Paired resampling of whole dates/contiguous date blocks, preserving cross-stock dependence; report confidence intervals for mean net return and incremental performance |
| Sharpe | Compute on all evaluation days including flat days, with explicit annualization and risk-free convention; bootstrap the same daily path |
| Multiple testing | Maintain experiment ledger; distinguish primary from exploratory tests; control false discoveries within a declared test family and disclose selection effects |
| Forecast skill | OOS R² against rolling asset mean and zero, MAE/RMSE, date-level rank IC, direction/calibration and undefined-IC counts |
| Concentration | P&L by stock, month and side; share contributed by best five days; report sensitivity without those days as a diagnostic, not a new primary estimate |
| Costs | Cost-response curve, break-even cost and turnover distribution; do not optimize costs to make a result significant |
| Market regimes | Keep ex-post regime attribution descriptive; separately define lagged, implementable state labels |
| Reversals | Measure position-change latency, whipsaw frequency and missed upside after predeclared reversal definitions; show sample counts and uncertainty |

Report yearly return and full-period compounded return together. Label January–September 2026 explicitly as partial-year. Annualized statistics are rates, not realized full-year returns. A combined curve is acceptable; separate protocol labels remain necessary.

## 8. AI event and capability research redesign

The release hypothesis and the prediction strategy answer different questions. A useful trading model does not establish that AI announcements caused IT stock declines. Conversely, an inconclusive event test does not invalidate all cross-market predictors.

1. **Validate events first:** exact model/version, provider, source URL, announcement timestamp/timezone, timestamp confidence, release versus preview, and score-publication timestamp. Keep unknown parameter counts missing and separate total from active parameters.
2. **Define reaction clocks:** first eligible U.S. session, first eligible Indian decision session, and first Indian session after an observed U.S. reaction. These are different dates; compute them from calendars rather than “Indian day plus one.”
3. **Separate outcomes:** U.S. close-to-close, India overnight gap, and India open-to-close. An event can affect the gap before an intraday strategy is able to trade.
4. **Use abnormal returns:** estimate a simple market/sector exposure model on a pre-event window, then plot abnormal-return paths over, for example, −5 to +5 sessions. Predeclare estimation/event windows and exclude or flag overlapping announcements.
5. **Address confounds:** earnings, major macro announcements and common market shocks should be flagged. A market adjustment and controls improve interpretation but do not prove causality.
6. **Quantify uncertainty:** aggregate at event level, report independent event counts, use event/date-cluster-aware uncertainty and matched-date placebo sensitivity. Avoid treating ten stocks around one release as ten independent events.
7. **Capability surprise:** if historically available, use improvement over the previously available frontier on a comparable benchmark; distinguish model release, benchmark revision and evaluation-tool change. Current-vintage retrospective scores remain descriptive.
8. **Audit selection:** the existing timeline selects record-high mapped ECI events. Show the complete eligible-event denominator and prespecified exclusions; record selection must not depend on stock reaction.
9. **Respect coverage:** the reported calendar stops in May 2025. It cannot explain 2026 release shocks. Extend only using verified sources with a new version and treat the resulting historical analysis as exploratory.

A timeline provides context; an abnormal-return event-time panel provides effect evidence. Both are more useful together than a capability-versus-price-level correlation, which confounds time trends and unrelated valuation changes.

## 9. Figure-by-figure redesign

Keep only figures that answer distinct questions. Reuse existing artifacts when valid; do not generate a new graph simply to fill pages.

| Existing figure | Decision | Exact improvement | New information gained |
|---|---|---|---|
| 1 Architecture | Redesign | Two separate forecasting/research branches; explicit availability gate, fold-local transforms, freeze and execution; preserve visible long/flat/short boxes | What can affect a decision versus what is retrospective interpretation |
| 2 Ten stock price paths | Keep, refine | Log-normalized axis or readable small multiples; stable colors; shaded evaluation segments and boundary; mark missing history | Heterogeneity without one high-growth stock compressing all other paths |
| 3 India/U.S. price paths | Merge or appendix | Use aligned returns or rolling relative performance in main text; retain normalized prices only as context | Cross-market relationship rather than repeated trending price plots |
| 4 Indian peer heatmap | Keep | Lower triangle; fixed −1 to +1 scale; legible labels; sample counts and a residual-correlation companion | Sector common factor versus stock-specific co-movement |
| 5 U.S.–India heatmap | Keep after timing correction | Explicit next-India O–C target, observation ages, pair counts, modest correlation scale and uncertainty/FDR note | Predictive lead–lag association with honest effect magnitude |
| 6 Ridge information ladder | Upgrade | Paired Δloss and Δnet-return intervals; annotate feature counts; add matched Extra Trees results | Whether more information helps independently of family changes |
| 7 Frontier timeline | Redesign | Separate event-label track with numbered markers and compact key; no tiny rotated overlapping names; distinguish exact/approximate matches | Readable chronology and source confidence |
| 8 Event response heatmap | Correct then supplement | Recompute U.S. reaction dates; separate window definitions; add event-time abnormal-return median/interval panels | Response magnitude/timing instead of undifferentiated red/blue cells |
| 9 Family Sharpe panels | Refine | Include candidate counts, uncertainty and “not promoted”; compare stages separately; convergence note | Search effort and selection uncertainty rather than best-of-family illusion |
| 10 Combined wealth | Keep as primary | Add corrected passive cohort, drawdown subplot, refit boundary and matched capital start | Return and downside risk across the actual displayed interval |
| 11 Monthly returns/exposure | Keep | Shared date axis; gross and net exposure; mixed/flat distinction; costs where legible | Link positioning to P&L and explain inactivity |
| 12 Group importance | Upgrade | Block/group permutation with repeated seeds; uncertainty; retain negative values; distinguish unavailable from zero | Stability of feature reliance across regimes |
| 13 Full research wealth | Appendix | Clearly shade screening/confirmation and label selected-model hindsight | Historical context without claiming independent validation |
| 14 Annual return bars | Merge with annual table | One compact annual performance panel; partial-year label | Avoid repeating the same wealth story three times |
| 15 Regime averages | Replace/merge | Conditional distributions or points with intervals/counts, plus up/down capture | Dispersion and sample support rather than average-only bars |
| 16 Reversal averages | Replace | Event-time exposure and cumulative net P&L around reversals, with uncertainty | Actual reaction speed and whipsaw behavior |

### High-value additional EDA, in priority order

| Plot | Question answered | Where it belongs |
|---|---|---|
| Coverage/missingness by year and source | How much of the intended universe is actually observed? | Main data section, replacing generic cleaning prose |
| Overnight versus intraday return density/quantiles | Is the proposed information already priced before the trade? | Main EDA; separate country/session conventions |
| Forecast calibration by score bin | Does predicted edge correspond to realized returns above costs? | Main model/evaluation section |
| Complexity × shrinkage validation surface | Does complexity help only under suitable regularization? | Main paper-linkage section after M03 |
| Cost-response and break-even-cost plot | Is the economic result fragile to realistic costs? | Main robustness section |
| Stock/side contribution chart | Is performance broad or driven by one asset/short side? | Main attribution, replacing redundant annual bars |
| Rolling residual cross-market association | Does the relationship survive common-market adjustment and change over time? | Appendix or main if central to H1 |
| Residual tail/volatility diagnostics | Are errors concentrated in stress periods? | Appendix with a concise main-text conclusion |

Avoid decorative 3-D plots, dense all-feature heatmaps, unqualified price-level correlations, and distributions without sample periods/counts. A stylish figure should make comparison easier, not exaggerate weak associations.

## 10. Architecture and document design specification

### Architecture revision

Use a compact vector diagram with three horizontal lanes:

1. **Information available before 08:55 IST:** India through previous close; U.S. completed sessions; historically available macro/events. Route all sources through an availability/calendar gate and data-quality checks.
2. **Forecast and trading:** fold-local preprocessing → F0–F7 experiment choice → chronological training/validation → frozen specification → expected O–C return → cost hurdle/risk caps → LONG / FLAT / SHORT → open/close execution → costs and ledger.
3. **Retrospective research:** current-vintage Epoch scores + verified release inventory + price outcomes → event/capability analysis. Use dashed connectors to interpretation only, not the forecasting lane.

Place a small temporal strip below the diagram identifying initial training, screening 2021–22, confirmation 2023–24, historical replication 2025 and retrospective extension January–September 2026. Label actual refit policies. Use orthogonal arrows, consistent spacing and no fan of diagonal lines converging on a single point. Keep text at least about 9 pt at final printed size; use navy for process, teal for outputs, amber for timing constraints and muted gray for retrospective analysis. These are design proposals, not model changes.

### Structural revision

Recommended narrative: question → data and availability → informative EDA → feature/model design → validation and trade rule → primary results → robustness/event evidence → limitations. Keep methods separate from findings, and avoid discussion of unrun improvements in the main results narrative.

| Section | Target content |
|---|---|
| Cover, abstract, contents | Required team/course/roster; concise question, method, central result and limitation; automatic contents |
| 1 Question and hypotheses | Cross-market incremental value first; AI event question secondary; distinguish prediction from causality |
| 2 Data and decision clock | Universe, dates, provenance, coverage, timestamps, target and benchmark contract |
| 3 EDA and features | Target distribution, peer/lead–lag evidence, cleaning impact, F0–F7 with realized dimensions |
| 4 Models and protocol | Solver and regularization choices, actual executed grids, temporal split and selection, signed cost rule |
| 5 Primary evaluation | Combined 2025–September 2026 display with historical/protocol caveats, annual decomposition, risk and baselines |
| 6 Robustness and interpretation | Controlled ablations, complexity, costs, attribution and AI uncertainty |
| 7 Limitations/conclusion | Survivorship, revision/timing assumptions, selection history, regime concentration, implementation limitations |
| References/appendices | Exact sources, contribution note, AI declaration, commands, IDs, extended research-path diagnostics |

Aim for roughly 17–21 substantive pages within the assignment’s 15–25-page requirement. Do not add whitespace or repeated plots to reach a target. The inspected page 4 is already reasonably dense with compact equations; it should not be criticized as if the old oversized-equation layout were still present. Page 8 still has crowded event labels and sizable unused lower-page space.

Use automatic heading-based TOC and caption cross-references instead of hand-entered page numbers. Use editable math equations with consistent symbols and sub/superscripts. Keep captions with their figures but do not chain whole following sections with “keep with next.” Allow tables to flow with repeated headers; reserve forced page breaks for genuine structural boundaries. Check every page after regeneration for clipped labels, stranded headings, blank regions and legibility at actual print size.

Standardize citation format with numbered in-text citations and full bibliographic entries. Dataset references should include retrieval date, snapshot/version, URL and limitations. Explain each figure with: question, construction/sample, observed result, and limitation. Remove prose about writing style itself from the foreword. Preserve all authors and the required integrity/AI declarations; add the assignment’s short contribution note.

## 11. Sequential action plan and acceptance gates

| Order | Action | Inputs | Deliverable | Gate before continuing |
|---|---|---|---|---|
| 1 | Freeze evidence inventory | Current DOCX, configs, manifests, ledgers | Read-only versioned review manifest | Existing outputs preserved and identified |
| 2 | Correct evidence language/counts | G01–G04, G10–G11 | Claim-to-artifact table and protocol history | No untouched-test or unexecuted-model overclaims |
| 3 | Audit accounting/calendar mappings | G05, G07–G09; ledger rules | Small deterministic accounting/calendar fixtures and corrected descriptive inputs | First-day wealth, holiday mapping and event windows reconcile |
| 4 | Publish dataset/feature contract | Raw audits, panel, dictionary | Coverage/exclusion and feature-dimension tables | Availability rules and revised-macro restrictions explicit |
| 5 | Predeclare focused experiments | M01/M02/M06; optional M03/M04 | Hashed experiment registry with budget and selection rule | No test-driven grid changes; historical evaluation status retained |
| 6 | Run development experiments | Approved configs and data | Checkpoints, convergence logs, paired OOS results | Complete matched-date comparisons; failures disclosed |
| 7 | Evaluate economics and uncertainty | Predictions and stock/day ledgers | Calibration, costs, baseline and confidence tables | Contribution totals and aggregate returns agree |
| 8 | Rebuild AI descriptive analysis | Verified timestamps/version mappings | Event-time response and exclusion table | Tradable and retrospective evidence strictly separated |
| 9 | Regenerate selected figures | Corrected numeric tables | Readable figure set with source manifests | Each figure answers a distinct question and matches text |
| 10 | Rewrite/report QA | Verified evidence and design guide | DOCX/PDF, automatic TOC and cross-references | 15–25 pages, every page visually inspected, no unsupported claims |
| 11 | Submission rehearsal | README, environment, commands | Clean-run verification, contribution note and video checklist | Required deliverables and staff-accessible links verified |

For every new artifact record UTC timestamp, content hash, code/config/input identities, parent run, seed, status, elapsed time and file hashes. Resume only matching completed checkpoints; changed features, targets, costs or selection rules require a new identity. Preserve old results rather than replacing unfavorable outcomes.

## 12. Final recommendation

Prioritize **honest evaluation labeling, investable and matched baselines, event-clock correctness, a matched Extra Trees/Elastic Net information ladder, forecast calibration, and cost-aware uncertainty**. Those changes most directly improve both assignment compliance and scientific credibility.

The current strategy is a plausible defensive cross-market research result, not yet an established AI-capability trading effect or broadly superior investment strategy. A well-supported negative AI finding and a precise explanation of when the signed strategy succeeds are stronger contributions than a larger model search designed to obtain significance. Publication readiness would require further independent evidence and external review; polished formatting alone cannot establish it.
