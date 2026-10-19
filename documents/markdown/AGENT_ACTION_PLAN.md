# Project 2 — Research design and sequential agent action plan

**Draft v1 · 19 October 2026 · Deadline: 12 November 2026, 23:59 SGT**

This document specifies a proposed research project and its implementation order. It contains design decisions, budgets, artifacts, and acceptance criteria; no data acquisition, model training, or backtest results are claimed. Paths below are relative to `project2QuantFin/`. The submission requirements come from [Project2.md](Project2.md). Proposed defaults may be revised during feasibility work, before validation results are inspected, and must then be recorded in a dated research protocol.

## 1. What the assignment is actually asking for

Build an original, economically motivated trading strategy and demonstrate that its evaluation could have been performed using only information available at each historical decision time. The central contribution is a defensible research process: data provenance, cleaning, alignment, overfitting controls, executable trading rules, fair comparisons, and honest interpretation.

High returns, numerous data sources, deep learning, and exact paper replication are not requirements. Data richness should mean useful, documented information and clear treatment of its limitations. A weak strategy with convincing diagnostics can satisfy the assignment. A profitable chart with leakage cannot.

The two supplied papers motivate different hypotheses. [Chinco et al.](Sparse_Signals_in_the_Cross_Section_of_Returns.md) use sparsity to identify brief cross-stock signals in minute data. [Kelly et al.](The_Virtue_of_Complexity_in_Return_Prediction.md) study rich nonlinear approximations with shrinkage for monthly market timing. Their assumptions and empirical settings differ. We will compare sparse, linear, and nonlinear approaches on a common daily task; this is an adaptation, not a replication or a guarantee that either result transfers.

### Requirements and evidence matrix

| Assignment component                    | Required evidence in our project                                                   | Planned artifact                                     |
| --------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------- |
| §4.1 Markets, assets, frequency, timing | Named tradable asset, timezone, decision and execution timestamps, benchmark       | `configs/protocol.yaml`, timing diagram              |
| §4.2 Labels and features                | Exact formulas, availability rules, cleaning, past-only preprocessing              | Feature dictionary, label audit, data quality report |
| §4.3 Benchmarks                         | Investable buy-and-hold on identical evaluation dates                              | Benchmark return series and comparison chart         |
| §4.4 Model and economic story           | Hypothesis, assumptions, shrinkage and complexity rationale                        | Model cards and experiment comparison                |
| §4.5 Data splits                        | Chronological development, validation, final evaluation; leakage controls          | Split manifest and training timestamp audit          |
| §4.6 Training                           | Methods, seeds, versions, reproducible configuration                               | Environment files, run manifests                     |
| §4.7 Selection                          | Small predeclared search and one explicit selection rule                           | Search registry and validation leaderboard           |
| §4.8 Trading and costs                  | Prediction-to-position rule, execution, costs, constraints                         | Position and transaction ledgers                     |
| §4.9 Evaluation                         | Out-of-sample annualized return, volatility, Sharpe; benchmarks and interpretation | Metrics tables, equity curves, period charts         |
| Report                                  | PDF, 15–25 pages, named team and contributions                                     | `Group_X_Report.pdf`                                 |
| Video                                   | 15–25 minutes; runnable end-to-end demonstration and explanation                   | MP4 or accessible, downloadable link                 |
| Code                                    | ZIP or GitHub link; README, requirements, runnable scripts, seeds, relative paths  | Clean submission package                             |
| Submission                              | One package per Canvas team; verify roster                                         | Final submission checklist                           |

The Markdown mentions 35 total points but does not preserve a detailed numerical allocation. Do not invent category weights. The brief allows zero costs by explicit assumption for daily/monthly strategies; our stronger design includes nonzero costs. Forecast baselines and some risk controls are optional in the brief but included here. Implement all three suggested plot types to remove ambiguity about the plotting requirements.

## 2. Recommended research project and scope

**Working title:** Can interpretable price, volume, and cross-asset signals improve daily SPY timing after costs under expanding-window learning?

**Tradable universe:** SPY and uninvested USD cash. No leverage, short selling, derivatives, or live orders. SPY is an investable S&P 500 ETF with a long history; see the [issuer description](https://www.ssga.com/us/en/individual/etfs/state-street-spdr-sp-500-etf-trust-spy). We select it for economic breadth and feasibility, before comparing historical model returns.

**Predictor universe:** SPY, QQQ, IWM, TLT, and GLD daily prices and volumes. QQQ and IWM proxy different equity exposures; TLT and GLD provide different asset-market information. These four auxiliary ETFs are predictors, not additional traded positions. Verify symbols, inception, coverage, and adjustment semantics in the acquisition step. A fixed ETF selection avoids reconstructing current index constituents backwards; it does not eliminate all retrospective asset-selection limitations.

**Primary sample:** fetch 2005-01-01 through 2025-12-31. Use 2005 as feature warm-up, 2006–2014 for initial training, 2015–2018 for model screening, 2019–2021 for confirmation, and 2022–2025 for a sealed final walk-forward evaluation. These are calendar bounds; actual rows follow the observed SPY calendar and label-maturity rules. Require enough preceding observations for every selected feature. Exclude 2026 from the main study to use complete calendar years and a fixed endpoint.

**Economic hypotheses:**

1. Slow information diffusion may produce trend persistence, while very recent price pressure may reverse.
2. Volatility and volume may identify conditions in which otherwise similar trends behave differently.
3. Cross-asset returns may contain information about changes in risk appetite and relative equity leadership.
4. These effects may be weak and unstable. Shrinkage and modest nonlinear interactions may help; more features may also hurt.

**Primary learning design:** expanding historical training data, daily feature updates and predictions, monthly parameter refits. Include a prespecified five-year rolling-window version of the selected model to study adaptation versus sample size. The brief explicitly mentions fixed-window testing, so deliver that comparison as well as the requested expanding design. Both produce genuinely forward predictions.

**Minimum complete study:** SPY-only features, historical-mean and autoregressive baselines, ridge, expanding evaluation, buy-and-hold, costs, interpretation, report, video, and reproducible scripts. Build this first.

**Planned full study:** add cross-asset features, elastic net, modest boosted trees, random Fourier features (RFF) with ridge, fixed-window comparison, group ablations, and sensitivity analysis. Macro and alternative data are extensions gated by availability and time, not dependencies of the submission.

## 3. Resource assessment and implementation choices

| Existing resource                                     | Finding                                                                           | Planned use                                                                  |
| ----------------------------------------------------- | --------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `resources/BacktestingREADME.md`                      | Describes **bt**, not the separate Backtesting.py package                         | Portfolio scheduling and benchmark examples; optional multi-asset extension  |
| `resources/backtrackerREADME.rst`                     | Describes **Backtrader**; filename is misleading                                  | Secondary event-driven execution reconciliation for the selected strategy    |
| `resources/pytrendsREADME.md`                         | Unofficial Google Trends client                                                   | Optional feasibility experiment only                                         |
| `documents/txt/GDELT 2.1 Document API.txt`            | Contains a June 2026 migration/ngram notice, not a complete DOC API specification | Evidence of infrastructure and historical coverage risks                     |
| Sibling `bt/`, `backtrader/`, `pytrends/` directories | Local source copies outside project repository                                    | Read examples; record versions if used; never require sibling absolute paths |
| Two paper Markdown files                              | Full converted papers with extraction artifacts                                   | Research rationale; consult PDFs for exact mathematics and tables            |

Use a transparent NumPy/pandas portfolio ledger for the main one-asset experiment: it makes timestamp alignment and costs easy to inspect and is fast across thousands of small fits. Reconcile representative periods and the final selected configuration with Backtrader using precomputed signals. Its documented market-order behavior uses a subsequent bar, and close orders have their own timing rules; configure and audit explicitly ([Backtrader execution documentation](https://www.backtrader.com/docu/order-creation-execution/order-creation-execution/)). Disable cheat modes. Do not assume two engines agree until dividend treatment, fractional holdings, cost timing, and closing-price execution match.

`bt` is useful for allocation and rebalancing experiments ([official documentation](https://pmorissette.github.io/bt/)). Avoid maintaining three backtesting engines. Backtesting.py is another distinct package; its `trade_on_close` behavior would require care if adopted ([API documentation](https://kernc.github.io/backtesting.py/doc/backtesting/backtesting.html)). It is not needed for the initial design.

Use a local experiment registry: one immutable JSON manifest per run, Parquet predictions, CSV metrics, and optional SQLite indexing. MLflow is a later convenience if tracking becomes cumbersome; hosted tracking is unnecessary for this scale.

## 4. Data sources, access, and availability gates

### 4.1 Source plan

| Source                      | Specific data                                                                    | Role and decision                                                                 |
| --------------------------- | -------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| Yahoo Finance via yfinance  | Daily OHLCV, adjusted close, dividends, splits for five ETFs                     | Primary candidate; fetch raw and adjusted representations explicitly and cache    |
| Stooq via pandas-datareader | Daily SPY overlap, if coverage supports it                                       | Independent spot-check; do not splice vendor series without reconciling semantics |
| FRED/ALFRED                 | Candidate DGS10, DGS2, DTB3; CPIAUCSL and UNRATE only with historical vintages   | Optional yield-curve and macro extension                                          |
| Google Trends               | Fixed terms such as “stock market”, “recession”, “market crash”; fixed geography | Exploratory attention extension, subject to historical availability limitations   |
| GDELT                       | Timestamped news metadata, counts, tone if archive and coverage are verified     | Optional short-sample extension; no dependence in core model                      |
| SEC EDGAR                   | Accepted filing timestamps and historical company facts                          | More suitable for a later individual-stock study; omit from SPY core              |
| Google News RSS             | Recent headlines                                                                 | Collection demo only; not a multi-year historical backtest source                 |
| World Bank WDI              | Annual macro observations                                                        | Too slow for the proposed daily model; omit                                       |

The yfinance documentation describes research/educational use and points to Yahoo's personal-use terms. That is not a blanket redistribution license. Save retrieval instructions and source terms, keep downloaded data private unless redistribution is permitted, and ship scripts rather than a public raw-data bundle ([yfinance documentation](https://ranaroussi.github.io/yfinance/)). No paid provider or cloud subscription is assumed. If source access is unsuitable, record a permitted substitute and freeze the change before validation.

For FRED, observation dates and historical availability are different. The API defaults to current information about past observations; historical vintages require real-time period controls ([FRED real-time documentation](https://fred.stlouisfed.org/docs/api/fred/realtime_period.html)). A lag applied to today's revised CPI does not recreate a historical vintage. If vintage and release information cannot be obtained, exclude that series from confirmatory claims.

The pytrends repository was archived on 17 April 2025 ([repository releases](https://github.com/GeneralMills/pytrends/releases)). Google Trends values are sampled and normalized, not absolute search counts ([Google methodology](https://support.google.com/trends/answer/4365533?hl=en-GB)). A historical download made today is not proof of what was observable then. Full-window normalization, sampling revisions, and stitching overlapping windows can contaminate historical comparisons. Only use in a separate exploratory analysis unless a defensible historical availability method is established; a one-day lag alone is insufficient.

The GDELT notice describes temporary search migration issues and suggests ngram files ([official notice](https://blog.gdeltproject.org/using-the-new-web-ngrams-dataset-to-find-relevant-coverage/)). It does not establish current endpoint health or a complete multi-year archive. Validate access and archive continuity before planning a news experiment. Count articles rather than query hits, deduplicate URLs/syndication, normalize counts by monitored coverage, and retain first-seen times. Do not download the full global archive onto this laptop.

### 4.2 Data contract

Every source adapter must produce provenance sufficient to reproduce the dataset:

```text
source, source_version, request_parameters, retrieved_at_utc, checksum
asset_or_series, observation_date, event_time_utc, available_at_utc
open, high, low, close, adjusted_close, volume, dividend, split_ratio
vintage_date, units, timezone, quality_flags, raw_file_reference
```

Fields not applicable to a source remain explicitly null. Distinguish recorded availability from an assumed conservative cutoff. Historical vendor bars usually do not provide historical ingestion timestamps; document this limitation rather than fabricating them. Price features are assumed available by 18:00 America/New_York after the session, and orders execute the following session's close. If a real download were delayed, the operational policy would skip the signal.

Archive immutable responses, request windows, retry outcomes, schemas, and file hashes. Use bounded retry/backoff and respect source limits. Incremental fetches must not silently overwrite historical snapshots. A rebuilt dataset gets a new version and a change report.

### 4.3 Source acceptance gate

Before opening validation performance, require: coverage sufficient for the frozen split; a consistent trading calendar; identified units and adjustment conventions; audited missing sessions; reproducible retrieval or a permitted private snapshot; and an availability rule for every feature source. If auxiliary ETFs fail, proceed with SPY-only data and disclose the narrower question. If an optional source consumes more than one working day without passing the gate, defer it and retain the complete core study.

## 5. Cleaning, exploration, and corporate actions

Explore the training period first. Restrict final-test inspection to mechanical schema, calendar, and integrity checks. Do not use test correlations, returns, or charts to design features or choose dates.

| Check                         | Treatment                                                              | Evidence              |
| ----------------------------- | ---------------------------------------------------------------------- | --------------------- |
| Duplicated asset/session keys | Compare provenance; resolve deterministically or quarantine            | Duplicate log         |
| Out-of-order timestamps       | Sort and assert monotonicity                                           | Calendar audit        |
| Holiday versus missing bar    | Join actual exchange sessions; never insert weekend price observations | Coverage heatmap      |
| Missing tradable price        | Refetch; stop if material unresolved gaps remain                       | Gap-resolution report |
| Optional missing predictor    | Past-only imputation plus missing flag where justified                 | Imputation counts     |
| Impossible OHLC               | Require low ≤ open/close ≤ high and positive prices                    | Rejected rows         |
| Zero/negative volume          | Investigate source and session; flag rather than invent liquidity      | Volume audit          |
| Extreme returns               | Check actions and a second source; retain genuine crashes              | Outlier case studies  |
| Units and scale shifts        | Validate yields, percentages, splits and volume conventions            | Unit dictionary       |
| Stale observations            | Record time since last release; set source-specific maximum age        | Staleness report      |

Never forward-fill SPY OHLC to create synthetic tradable sessions. Hold existing positions through a nontradable interval and account for the next observable price; do not erase the intervening return. For substantial unresolved gaps, block the run. Forward-filling macro values is permitted only after their release and with documented staleness limits. No backward fill, centered moving averages, interpolation using future endpoints, or full-sample clipping thresholds.

Keep raw vendor OHLC separate from adjusted research prices. Verify what “raw” means for that vendor; it can already contain split normalization. Do not adjust split-normalized history twice. Use dimensionless ratios and returns as predictors, avoiding absolute adjusted-price levels that depend on later adjustment conventions.

**Corporate-action issue in Appendix B:** the Markdown gives a dividend factor `1/(1 + D_t/P_(t-1))` and claims exact agreement with `(P_t + D_t)/P_(t-1) - 1`. With only that dividend event, its implied adjusted-price ratio is `(P_t/P_(t-1)) × (1 + D_t/P_(t-1))`, which is generally different. Check the original PDF before adopting either expression. Vendor reinvestment conventions can also differ from a simple cash-dividend return.

The action audit must therefore compare: vendor adjusted returns; a clearly specified cash-dividend ledger; and any manually reconstructed adjusted series. Explain convention differences and set tolerances accordingly. Do not demand machine precision between economically different conventions. Show at least one dividend example and one verified split example; use a separate AAPL action fixture if the traded ETF sample does not contain a useful split. That fixture does not expand the strategy universe.

Planned training-data EDA: coverage by asset/year, missingness before and after cleaning, action examples, return distributions and tails, rolling volatility, volume seasonality, feature distributions, within-training correlation clusters, trend persistence, and simple lagged feature/label relationships. Correlation is descriptive evidence, not a trading rule selection shortcut. Save before/after row counts and reasons for every exclusion.

## 6. Exact temporal contract: features, labels, fills, and learning

Choose **next-session close execution** for the primary experiment. This adds a deliberate delay and makes total-return accounting more transparent than an adjusted-open proxy. It is an allowed assignment choice. State the delay prominently; this is not a same-close strategy.

Let `t` index actual trading sessions and `A_t` denote the documented adjusted close:

```text
session t, after close:       observe x_t; calculate prediction and target weight
session t+1, before close:    submit the already determined closing order
session t+1, close:           execute using closing-price proxy plus assumed costs
session t+1 to t+2 close:     earn the next holding-period return
session t+2, after close:     y_t has matured and can enter later training

y_t = A_(t+2) / A_(t+1) - 1
```

The prediction is made one session before entry, and forecasts a one-session holding return. The label is not `A_(t+1)/A_t - 1`. Each row stores `signal_time`, `entry_time`, `label_end_time`, and `label_available_at`. At a fit after session `t`, only rows with `label_available_at <= fit_time` are eligible; conservatively, this means feature dates no later than `t-2`. A date shift alone is insufficient without checking label end times.

At a monthly refit, fit preprocessing and the estimator on eligible history. Freeze both until the next scheduled refit. Generate predictions daily using new features. Do not update the scaler daily while leaving model coefficients expressed in the old scale. Predictions are saved once with the model version and are never recomputed using later models for the historical performance series.

For an expanding fit, eligible history begins in 2006 and grows. For the fixed-window companion, retain the latest 1,260 eligible trading observations, approximately five years. Warm-up prices may precede those dates. A daily-refit sensitivity can be added after profiling; it is not necessary for daily forecasts.

**Final-test protocol:** after model and rules are frozen, replay 2022–2025 chronologically. Earlier test labels may enter subsequent scheduled refits after they mature, under the frozen algorithm. This is legitimate online learning. They may not be used to invent features, alter thresholds, select the model family, or change the search grid. The final test is a single locked simulation with scheduled refits, not a single permanently frozen estimator.

Purge training rows whose target interval crosses an evaluation boundary. Derive the gap from actual timestamps; do not assume a one-row gap is sufficient for this delayed target. If a five-session target is added, extend label maturity and purging accordingly, and account for overlapping holdings and serial dependence. No shuffled cross-validation. Standard time-series splitting is useful but does not replace the label timestamp audit ([scikit-learn cross-validation guidance](https://scikit-learn.org/stable/modules/cross_validation.html)).

## 7. Feature dictionary and staged feature sets

Use `r_t = log(A_t/A_(t-1))`. All windows are trailing, end at the signal session, and use only observations available by the decision cutoff. Store the exact minimum-observation rule. Drop initial warm-up rows rather than fill indicators with future data.

| Group                    | Proposed definitions                                                                           | Hypothesis / caution                                                    |
| ------------------------ | ---------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| Recent returns           | `r_t, r_(t-1), r_(t-2), r_(t-4), r_(t-9)`                                                      | Short reversal or continuation                                          |
| Cumulative returns       | `A_t/A_(t-k)-1`, k = 5, 10, 15, 20, 60, 120, 252                                               | Persistence at several horizons                                         |
| Moving averages          | `A_t/SMA_k(t)-1`, k = 10, 15, 20, 50, 200                                                      | Position relative to a trend                                            |
| Trend slopes             | `SMA_20(t)/SMA_20(t-5)-1`; `SMA_50/SMA_200-1`                                                  | Trend direction and strength                                            |
| Exponential trends       | `EMA_12/EMA_26-1`, trailing EMA initialization                                                 | Faster weighted response                                                |
| Realized volatility      | `std(r, k)`, k = 10, 20, 60; `vol_10/vol_60`                                                   | Risk and changes in risk                                                |
| Downside and drawdown    | Downside semideviation over 20; distance from trailing 60/252-session maximum                  | Asymmetric stress                                                       |
| Within-session structure | `close/open-1`, `open/previous_close-1`, `(high-low)/close` using consistent prices            | Gap versus session movement; verify action effects                      |
| Volume                   | `log1p(volume)` trailing z-score over 20/60; volume/SMA20; five-session change in log volume   | Participation and unusual activity; audit splits                        |
| Price-volume interaction | `r_t × volume_z20`                                                                             | Whether movement has unusual participation                              |
| Cross-asset returns      | QQQ, IWM, TLT, GLD cumulative returns over 5/20/60                                             | Market state proxies                                                    |
| Relative strength        | QQQ−SPY and IWM−SPY 20-session returns                                                         | Equity leadership                                                       |
| Co-movement              | SPY–TLT trailing 60-session return correlation                                                 | Asset relationship changes                                              |
| Calendar                 | Weekday and month-end indicator                                                                | Optional nuisance controls; no large calendar search                    |
| Macro extension          | Released 10y−2y yield spread, 20-session changes, vintage-aware inflation/unemployment changes | Slow state information; stale daily copies are not independent releases |
| Attention extension      | Coverage-adjusted news counts; trailing attention changes                                      | Exploratory until point-in-time data qualify                            |

Freeze three nested groups before screening: **F0**, approximately 15–20 SPY return/trend/risk features; **F1**, approximately 35–50 SPY features including volume and interactions; **F2**, approximately 55–75 features with cross-asset signals. The implementation dictionary must enumerate exact counts; these ranges are planning estimates. Use F2 for the common family comparison if it passes the data gate. Ablate groups later with a fixed estimator rather than crossing every feature set with every model grid.

Training-only preprocessing: remove constant columns, impute justified missing predictors with training medians plus indicators, and standardize linear-model inputs. Any clipping thresholds are fitted on training data and recorded. Keep target returns untrimmed for reported P&L. Fit feature selection, PCA, or correlation pruning within the training pipeline if added. Deterministic trailing features can be precomputed across the timeline provided their prefix values are invariant when future rows are removed.

RFF enriches transformations of existing information; it does not add independent observations. Do not equate a thousand transformed features with a thousand distinct economic signals. Avoid large automatic indicator libraries and unrestricted feature combinations.

## 8. Model families, training methods, and bounded search

Predict returns as a regression task. A classification extension is optional and needs probability calibration and an economic conversion rule; high directional accuracy alone is not sufficient. Keep the first comparison on the same target, data, timestamps, feature set, portfolio rule, and costs.

| Model                       | Purpose                                   | Training and predeclared settings                                                                            | Configurations |
| --------------------------- | ----------------------------------------- | ------------------------------------------------------------------------------------------------------------ | -------------: |
| Historical mean             | Forecast baseline                         | Mean of eligible past labels, updated monthly                                                                |              1 |
| Small autoregression        | Transparent linear baseline               | OLS on intercept and last three daily returns; same target                                                   |              1 |
| Ridge                       | Primary interpretable shrinkage model     | Normalized penalty λ ∈ {0.001, 0.01, 0.1, 1, 10}                                                             |              5 |
| Elastic net                 | Sparse and correlated-feature alternative | λ ∈ {0.0001, 0.001, 0.01}; l1_ratio ∈ {0.2, 0.8}                                                             |              6 |
| Histogram gradient boosting | Small nonlinear interaction model         | max_leaf_nodes ∈ {3, 7}; l2_regularization ∈ {1, 10}; learning_rate=0.05, max_iter=100, min_samples_leaf=100 |              4 |
| RFF + ridge                 | Nonlinear approximation with shrinkage    | P ∈ {64, 256, 512}; λ ∈ {0.01, 0.1, 1}; fixed bandwidth and seed                                             |              9 |
| **Total initial screen**    |                                           | Two baselines plus 24 model configurations                                                                   |         **26** |

Define ridge as minimizing `mean((y-Xβ-b)^2) + λ||β||²`, with an unpenalized intercept. For a library using a sum-of-squares objective, set its penalty to `n_train × λ`. This keeps the meaning of shrinkage consistent as the expanding sample grows. Elastic-net objective scaling differs by library; document the mapping, tolerances, maximum iterations, and convergence status. Targets stay in decimal return units. The grid is a proposed starting grid, checked for numerical feasibility on training-only data before locking.

For RFF, standardize original inputs within each fit, use `sqrt(2/P) cos(Wx+b)` with a fixed seed and a specified kernel parameter, for example scikit-learn RBF `gamma=1/p` where p is the retained input dimension. Store W and b generation rules; use nested feature prefixes with appropriate normalization. Freeze the bandwidth in the initial screen. This is an adaptation of Kelly et al.; their paired sine/cosine parameterization and monthly design are not identical.

P ≤ 512 will generally be below the expanding training sample size, so this screen tests nonlinear approximation, not their extreme overparameterized claim. A separate optional monthly experiment could use 60 observations and P ∈ {16, 64, 256}; it requires its own target, costs, split, and experiment budget. Do not describe the daily screen as a replication of P ≫ T results.

Ridge uses a stable linear solver; do not explicitly invert matrices. Elastic net uses coordinate descent. Boosting uses a bounded number of sequential trees. RFF has fixed random features and a ridge fit. These are not neural-network epochs. Disable any default random validation split for early stopping; use the fixed 100 boosting iterations initially. Random forests, SVMs, neural networks, LSTMs, Transformers, and reinforcement learning are not first-stage necessities given the sample size and interpretability aim.

### Selection and deeper investigation

1. Freeze the initial grid, portfolio mapping, cost assumption, and score before screening.
2. Run every configuration through the 48 monthly refits in 2015–2018; predict every eligible session.
3. Rank by median annual post-cost Sharpe across the four screening years. A year with zero volatility is undefined, not an infinite success; configurations with undefined annual scores cannot win this ranking. Record forecast MSE, OOS R², drawdown, exposure, and turnover alongside the primary score.
4. For scores within 0.05 Sharpe units, choose lower turnover, then fewer parameters, then a deterministic configuration ID. These thresholds are design choices, not significance tests.
5. Optionally investigate at most six additional settings within the winning family on the same screening period. Define them before running them and record the additional trials. Examples: adjacent ridge penalties; elastic-net sparsity stability; tree leaf size; RFF bandwidth. No new family after this gate.
6. Send at most two candidate configurations to 2019–2021 confirmation. Use the same median annual net-Sharpe rule, with the same tie-breaks. Confirmation is still validation, not an independent final performance claim.
7. Lock one champion, one five-year-window companion with the same selected hyperparameters, and the two forecast baselines. If evidence of an advantage is weak, retain the selected model and explicitly report that weakness. Do not keep searching until it beats buy-and-hold.

A small exhaustive grid is preferable here because it is auditable and computationally bounded. If the future space becomes much larger, a fixed-budget randomized search can replace it before the protocol is frozen. Adaptive Bayesian search is possible, but creates more research choices and is not needed for 24 configurations. Portfolio thresholds, risk targets, window lengths, feature subsets, and seeds are also research trials; hiding them outside the model grid does not avoid selection bias.

## 9. Trading rule, costs, and benchmark accounting

Predeclare a simple binary long/cash rule for the family comparison:

```text
forecast expected holding return at signal t
target weight = 1 if forecast > 0.001, else 0
execute target at close of session t+1
cash weight = 1 - SPY weight
```

The 10 bp forecast hurdle is a fixed conservative trading filter, corresponding to a hypothetical round trip at 5 bp per side. It is not a calibrated guarantee that every trade covers its costs; actual holding durations vary. Use the same rule for all predictive models. Begin from cash, constrain weight to [0,1], permit fractional units as an explicit research assumption, and use a notional starting portfolio such as USD 100,000.

**Costs:** main scenario 5 bp per dollar of one-way traded notional, treated as an all-in commission/spread/slippage assumption. Report 0, 2, 5, 10, and 20 bp sensitivities. These are scenario assumptions, not observed historical spread estimates. Never charge both an all-in cost and the same spread component again. ETF fund expenses are already reflected in prices and should not be deducted a second time.

Compute turnover from target holdings versus holdings after market drift, not simply yesterday's target weight. Record entry and final liquidation costs. At an execution boundary, compute pretrade wealth and holdings, deduct costs on actual traded notional, and rebalance the remaining wealth. An exact fractional-share ledger should resolve buys net of their costs; if an approximate target-weight formula is used for screening, reconcile its error and disclose it. Costs paid at entry reduce the wealth that earns the subsequent return.

Use vendor adjusted close as the documented total-return research convention. Do not then add cash dividends a second time. Adjusted prices are synthetic research prices, not actual exchange fill quotes. For the execution audit, reconcile raw-price fills, split handling, distributions, and reinvestment convention with the adjusted-price ledger. Material unresolved action-accounting differences block final metrics.

**Cash:** use zero interest as the core assumption, for both strategy and cash benchmark; label the resulting Sharpe as using zero risk-free rate. Optional sensitivity uses a lagged, available short-term yield with documented day-count conversion and calendar-day accrual. A quoted discount yield is not automatically a realized tradable cash return. Do not mix risk-free conventions across strategies.

**Comparators:** SPY total-return buy-and-hold, cash, a fixed 200-session trend filter, historical-mean forecast strategy, and autoregressive forecast strategy. Apply the same execution delay, period endpoints, initial/final cost conventions, and cash treatment where relevant. Buy-and-hold starts at the first strategy entry boundary and ends at the same final valuation boundary. Add a volatility-controlled SPY comparator only as a prespecified diagnostic using past volatility; avoid ex-post full-test volatility scaling.

A continuous weight rule such as clipped expected return divided by lagged variance is a useful later extension, but it introduces a risk-aversion parameter and often more turnover. Keep it out of the initial grid. Likewise, an alternative next-open execution experiment needs a new matched target and dividend-aware open-to-open accounting; changing only the fill price is invalid.

## 10. Evaluation, interpretation, and robustness

Save one canonical out-of-sample prediction table and derive all charts and performance tables from it. Never reconstruct historical forecasts with the final fitted model.

| Dimension          | Outputs                                                                                                             |
| ------------------ | ------------------------------------------------------------------------------------------------------------------- |
| Forecast quality   | MSE, MAE, OOS R² against the recursively available historical mean; directional accuracy as secondary               |
| Investment results | Net CAGR, arithmetic annualized mean, annualized volatility, Sharpe, drawdown, turnover, exposure, trading count    |
| Comparisons        | Same-date strategy/benchmark equity curves; active returns and information ratio where meaningful                   |
| Stability          | Calendar-year results, rolling metrics, expanding versus fixed-window, sensitivity to costs                         |
| Interpretation     | Standardized coefficients, selection frequency, group ablations, dependence plots, failure periods                  |
| Uncertainty        | Paired block bootstrap intervals on strategy and benchmark returns; descriptive caveats for selection and few years |

For daily returns, label the conventional 252-session annualization. Report CAGR separately from arithmetic annualized return. Define Sharpe from excess returns under the declared cash/risk-free convention. Compute `R²_OOS = 1 - Σ(y-yhat)² / Σ(y-yhat_mean_past)²`; do not use a full-test mean as the forecast baseline. The historical-mean denominator uses the same label availability rule.

Use paired contiguous blocks when bootstrapping strategy versus benchmark; a proposed diagnostic is 1,000 resamples with 20-session blocks and 10/60-session sensitivity. This evaluates uncertainty conditional on the chosen strategy and does not erase model-selection bias. Record all tried configurations and avoid strong significance claims from one short test period. Optional CAPM alpha uses aligned excess returns and serial-correlation-robust uncertainty.

Interpretation should answer concrete questions: Does the model mainly stay long? Does lower drawdown come primarily from reduced exposure? Does performance survive 10 bp costs? Does one year explain most gains? Are coefficients stable? Are correlated features interchangeable? Does nonlinear modeling improve results on the same information? Which failures contradict the economic story?

For ridge/elastic net, report sign and standardized-coefficient stability across monthly fits, plus active-feature counts for elastic net. For trees, use grouped block permutation and selected dependence plots; raw impurity importance can be misleading. For RFF, interpret original feature groups through ablations, not individual sine/cosine coefficients. Correlated groups complicate attribution; importance is predictive evidence, not proof of causation.

Perform three planned group-drop ablations on the screening period with the fixed finalist settings: remove cross-asset information, remove volume, and remove long-horizon trends. Do not turn every ablation into a new tuned model. Final-period explanatory analysis is descriptive and must not trigger redesign. Predefine calendar reporting and any event windows before inspecting their performance; do not cherry-pick favorable stress dates.

Required figures: data coverage/cleaning; timing and split schematic; feature groups; validation comparison; complexity/shrinkage response; OOS prediction performance; strategy versus benchmark cumulative returns; drawdown and exposure; annual returns and Sharpe; cost sensitivity; and feature stability/ablation summary.

## 11. Compute strategy for the actual machine

Hardware inspected locally: **MacBook Air, Apple M1, 8 CPU cores (4 performance + 4 efficiency), 16 GB unified memory, 8-core GPU**. No runtime benchmarks have been measured. The following are resource limits and scheduling estimates, not performance promises.

The raw problem is small: roughly 5,300 daily sessions, five assets, and fewer than 100 conventional features. The main compute multiplier is repeated fitting across dates and configurations. Start with native arm64 Python and a clean virtual environment; record the exact Python and package versions after a dependency smoke test. CPU execution is the default for scikit-learn estimators. The Apple GPU is not automatically used by ridge, elastic net, or histogram boosting. GPU infrastructure is unnecessary for the proposed pipeline.

| Operating mode          | Policy                                                                            |
| ----------------------- | --------------------------------------------------------------------------------- |
| Interactive development | One worker; one symbol or a short training-only slice; 2–3 refit dates            |
| Full screening          | Two concurrent configuration workers; one numerical-library thread each initially |
| Overnight batch         | Same safe memory limits, resumable jobs, atomic writes, captured logs             |
| RFF profiling           | One worker first; increase only after measuring peak resident memory              |
| Reporting               | Reuse saved predictions; never refit to regenerate a chart                        |

Avoid nested parallelism: multiple joblib workers each launching many BLAS/OpenMP threads can slow the machine. Control threads with `threadpoolctl` and the applicable environment variables; verify what the installed numerical backend actually uses ([scikit-learn resource guidance](https://scikit-learn.org/stable/computing/parallelism.html)). Start with two workers and compare one versus two on the same small workload. Four is an upper experimental setting, not the default. Preserve responsiveness and stop increasing parallelism if memory pressure or sustained swapping appears.

Set an initial total-process memory budget of about 8 GB, leaving headroom for macOS and applications. With 5,000 rows and 512 float64 RFF columns, the feature matrix is about 20 MB, but transforms, copies, factorizations, workers, and interpreters add overhead. Float64 is appropriate for linear solves and financial accounting. Float32 storage can be considered only after numerical reconciliation.

Cache cleaned data and deterministic trailing features as versioned Parquet. Cache training transformations within a refit date across compatible model settings. Ridge penalties can reuse a decomposition for the same transformed design matrix. Do not reuse a scaler fitted at a later date. RFFs depend on the current scaler, so a single globally standardized RFF cache would leak. Use stable solves and the smaller primal/dual formulation where appropriate; do not materialize huge inverses.

### Fit-count budget

One “fit” means one estimator at one scheduled monthly origin. It is distinct from a tree iteration, coordinate-descent iteration, or neural epoch.

| Stage                                 | Calculation                                               | Maximum planned fits |
| ------------------------------------- | --------------------------------------------------------- | -------------------: |
| Main standard screen                  | 57 configurations × 48 monthly refits                    |                2,736 |
| F0 and F1 feature ablations           | 2 standard grids × 2,736                                  |                5,472 |
| Five-year rolling-window sensitivity  | 57 configurations × 48                                   |                2,736 |
| Optional deep-capacity screen         | 75 configurations × 48                                   |                3,600 |
| 2019–2021 confirmation                | 2 finalists + 2 baselines, each × 36                     |                  144 |
| Final 2022–2025 evaluation            | Champion + 2 baselines, each × 48                         |                  144 |
| **Core standard + confirmation/final**| Excludes optional ablations, rolling, and deep runs       |            **3,024** |

Buy-and-hold, fixed trend rules, and re-costing saved positions require no model fits. These counts assume one SPY target, one primary feature set for family screening, monthly refits, and full calendar blocks. Actual counts are generated from the calendar manifest. A separate daily-refit, multi-target, macro, or monthly RFF study consumes an additional explicitly approved research budget; it is not included silently.

Seed stability is diagnostic: use fixed seeds such as 17, 29, 43, and never pick the most profitable seed. The main RFF run uses seed 17. If an ensemble is later chosen, declare and validate that decision before the final test and count its additional fits.

**Profile before scheduling:** use `run-models --plan-only` to obtain exact fit counts, then let the live progress bar estimate elapsed and remaining time from completed fits. Measure representative early and late fits before committing to optional deep and ablation runs. Estimate total time as `Σ(number_of_fits_family × measured_time_family)` plus preprocessing, I/O, and contingency. A preflight estimate over four hours for routine screening triggers a documented reduction in optional runs before execution, never removal of leakage controls or cost checks.

Long runs should checkpoint completed configuration/date jobs, handle interruption, and resume without duplicate forecasts. Keep the machine connected to power and ensure sleep settings allow the run. A native process wrapper can prevent idle sleep when intentionally launched. Longer training is useful only if convergence or a planned sensitivity requires it; it is not intrinsically better for noisy daily returns.

## 12. Proposed software and artifact architecture

```text
configs/
  protocol.yaml              # asset, timing, splits, costs, freeze status
  features.yaml              # formulas, groups, lags, availability
  models.yaml                # bounded grids, compute limits, costs, selection
src/quantfin/
  data/                      # source adapters, snapshots, calendar, actions
  features/                  # causal transforms and feature dictionary
  labels.py                  # entry/end/availability timestamps
  splits.py                  # chronological origins and purging
  preprocessing.py           # fitted training-only transforms
  models/                    # mean, AR, ridge, elastic net, trees, RFF
  walkforward.py             # refit schedule and immutable predictions
  portfolio/                 # positions, costs, cash, return ledger
  evaluation/                # metrics, diagnostics, interpretation
  tracking.py                # hashes, manifests, resume state
  cli.py                     # reproducible command interface
tests/                       # timing, actions, ledger, integration fixtures
data/raw/                    # private immutable source snapshots
data/processed/              # versioned cleaned data and features
artifacts/runs/<run_id>/     # predictions, ledgers, metrics, plots, manifests
reports/                     # report source, rendered PDF, video outline
README.md
requirements.txt
.env.example
```

Implemented command structure; the README contains the complete ordered commands and placeholders:

```bash
python -m quantfin fetch --source yahoo
python -m quantfin audit-data
python -m quantfin clean
python -m quantfin build-features
python -m quantfin check-timing
python -m quantfin run-models --stage screening --profile standard --plan-only
python -m quantfin run-models --stage screening --profile standard
python -m quantfin select-models --run-id SCREENING_RUN_ID
python -m quantfin run-models --stage confirmation --selection PATH_TO_SELECTION
python -m quantfin freeze --selection PATH_TO_CONFIRMATION_SELECTION
python -m quantfin run-models --stage final_test --selection PATH --freeze PATH
python -m quantfin plot-run --run-id FINAL_RUN_ID
```

Each manifest records code revision, input hashes, config hash, feature count, eligible training dates, model settings, seed, versions, fit/convergence status, runtime, and output paths. Save fitted estimators at least at monthly origins for the finalist; large artifacts can be private and regenerated if redistribution/storage constraints apply. Write predictions atomically. Separate failed jobs from valid zero-return outcomes.

## 13. Sequential agent work orders

Each work order is a bounded future agent task. Execute in order unless its dependencies are complete. The agent must read the current protocol, inspect existing artifacts, make only the scoped changes, verify its acceptance criteria, and leave a short handoff: files changed, commands run, findings, unresolved issues, and the next work order. Never mark a task complete because a chart looks profitable.

### A01 — Freeze the research question and assignment checklist

**Inputs:** this plan, Project2.md, team preferences. **Actions:** choose the primary asset, next-close timing, sample, feature groups, cost rule, and scope; record any feasibility-dependent alternatives. Map every submission requirement. **Outputs:** protocol draft and requirements matrix. **Accept:** no ambiguous target, fill time, benchmark, or deliverable. **Depends:** none.

### A02 — Establish reproducible project scaffolding

**Inputs:** A01. **Actions:** create package/config structure, arm64 environment, relative paths, logging, excluded private-data paths, and manifest schema. Pin working dependencies after import checks. **Outputs:** README setup steps, requirements, `.env.example`, CLI skeleton. **Accept:** fresh environment imports the package without depending on sibling repositories or local absolute paths.

### A03 — Acquire and inventory data

**Inputs:** A02 and source policy. **Actions:** implement one adapter at a time; download raw/adjusted OHLCV and actions; cache requests and hashes; produce coverage metadata without exploratory test analysis. **Outputs:** versioned raw snapshot and source registry. **Accept:** all chosen assets pass the source gate or a documented SPY-only fallback is frozen before screening.

### A04 — Audit and reconcile corporate actions

**Inputs:** A03. **Actions:** check schema, sessions, duplicates, OHLC, missingness and action conventions; consult original PDF for the inconsistent formula; reconcile a dividend and split fixture. **Outputs:** cleaned prices, exceptions log, corporate-action note. **Accept:** no unexplained material action jumps, double adjustments, or synthetic tradable prices.

### A05 — Produce training-only EDA

**Inputs:** A04. **Actions:** inspect distributions, tails, trends, volume, correlation and missingness in 2006–2014; document hypotheses and limitations. **Outputs:** EDA tables and exported figures. **Accept:** reproducible outputs and no later-period feature selection.

### A06 — Implement the temporal contract and labels

**Inputs:** A04 and A01. **Actions:** create signal/entry/end/availability times, delayed labels, eligible training masks, expanding and fixed windows. **Outputs:** label table, split manifest, timing schematic. **Accept:** toy hand calculations match; no fit includes a label ending after its cutoff; boundaries are purged correctly.

### A07 — Build feature and preprocessing pipelines

**Inputs:** A05–A06. **Actions:** implement F0 first, then F1/F2, exact dictionaries, warm-up rules, fold-fitted transforms, and data hashes. **Outputs:** causal feature table and pipeline objects. **Accept:** truncating or perturbing future data leaves earlier features and predictions unchanged; scalers/imputers fit only eligible training rows.

### A08 — Build portfolio ledger and benchmarks

**Inputs:** A04 and A06. **Actions:** implement trade timing, binary positions, drift-aware turnover, costs, cash, initial/final boundaries and benchmarks using synthetic signals. **Outputs:** ledger, benchmark series, accounting fixtures. **Accept:** zero-price-move round trip loses only specified costs; continuous holding matches the chosen total-return convention; delayed signals cannot capture preceding returns.

### A09 — Complete the minimal walk-forward strategy

**Inputs:** A07–A08. **Actions:** implement mean, AR and ridge with monthly refits and daily predictions on development data. **Outputs:** a complete baseline run and metrics from saved predictions. **Accept:** at least one end-to-end reproducible strategy works, with valid timing and accounting, before adding complex models.

### A10 — Profile and implement safe batch execution

**Inputs:** A09. **Actions:** measure early/late fit sizes and memory, set worker limits, add checkpoint/resume and cache invalidation. **Outputs:** compute profile and runtime forecast. **Accept:** interruption/resume reproduces an uninterrupted small run; different configs/data cannot reuse incompatible cached artifacts.

### A11 — Lock the search and run family screening

**Inputs:** A09–A10. **Actions:** implement regularized linear, PCA, bounded tree ensemble, histogram boosting, and RFF families; register every trial before execution; run the 57 standard configurations over 2015–2018. **Outputs:** full search ledger and validation ranking. **Accept:** identical evaluation dates and costs; failed fits disclosed; numerical convergence checked; no confirmation or final-test performance viewed.

### A12 — Drill into the selected family

**Inputs:** A11. **Actions:** inspect coefficient/feature stability, perform three group ablations, optional bounded refinement and RFF seed diagnostics, plus rolling-window development comparison. **Outputs:** family analysis, revised trial count, rationale for at most two finalists. **Accept:** refinement budget honored; seed/window/feature decisions documented; no undocumented manual trials.

### A13 — Confirm and freeze

**Inputs:** A12. **Actions:** evaluate the two finalists and baselines on 2019–2021; apply the fixed selection rule; freeze champion, features, window, threshold, costs, metrics, seeds and final-test analysis plan. **Outputs:** signed-off-by-team freeze manifest and model card. **Accept:** every choice needed for final evaluation is deterministically specified; low performance does not cause an unbounded new search.

### A14 — Run the sealed final evaluation

**Inputs:** A13. **Actions:** replay 2022–2025 once with scheduled refits and matured-label updates; save canonical forecasts and ledgers. **Outputs:** final performance artifacts, execution audit, timestamp audit. **Accept:** no post-result parameter changes; any discovered correctness bug is documented, corrected, and all affected results labeled as a rerun rather than a new untouched test.

### A15 — Complete robustness and interpretation

**Inputs:** A14. **Actions:** re-cost saved trades, compare expanding/fixed windows, explain exposure and failure years, compute intervals and final descriptive importance, reconcile Backtrader accounting. **Outputs:** final figures and limitations. **Accept:** core claims trace to artifacts; no favorable-period cherry-picking; discrepancies resolved or explicitly bounded.

### A16 — Write the report and record the video

**Inputs:** A15. **Actions:** assemble 15–25-page PDF and 15–25-minute demonstration, cross-reference code/figures, document contributions, citations and exact run commands. **Outputs:** report PDF, video, README. **Accept:** all requirements mapped to a page/figure/command; assumptions and weak results clearly explained.

### A17 — Reproduce and package

**Inputs:** A16. **Actions:** run from a clean environment, verify artifacts, audit credentials/paths/data permissions, check file names and team roster, prepare ZIP or repository link. **Outputs:** submission manifest and ready-to-submit package. **Accept:** independent clean run works; video link accessible/downloadable; PDF readable; no secrets or large proprietary datasets. Canvas submission remains a human team action unless explicitly delegated.

## 14. Verification gates that protect the research

Prioritize meaningful invariants over superficial test coverage:

1. Future-row perturbations cannot change earlier features, fitted transforms, or predictions.
2. Every training label is observable at its fit timestamp; every fill follows the signal cutoff.
3. A scaler, imputer, clipping rule, feature selector, or early-stopping choice never sees its evaluation block.
4. Dividend and split fixtures preserve the stated wealth convention without double counting.
5. Buy-and-hold, all-cash, and a hand-calculated switch sequence reconcile against the ledger.
6. Raising costs cannot improve returns for the same fixed trades and fixed fills; this invariant does not apply if the strategy itself is retuned or trades change.
7. Models share the same evaluation dates; no failed forecasts or losing dates are silently dropped.
8. A resumed run has no duplicate/missing predictions and matches uninterrupted execution within declared numerical tolerances.
9. Final-test output is generated only with a frozen protocol hash; later edits invalidate its frozen status.

Acceptance tolerances must be specified before checks run. Use exact comparisons for timestamps/keys and suitable numerical tolerances for floating-point accounting. A test failure blocks the dependent research phase rather than being explained away by good performance.

## 15. Report, video, and delivery schedule

Proposed report allocation, totaling 22 pages: title/abstract/contributions 1; economic question and literature 2; data and cleaning 3; timing/labels/features 3; models and selection 3; trading/benchmarks/costs 2; results and interpretation 4; limitations/reproducibility/conclusion 2; references 2. Adjust layout within 15–25 pages without omitting required evidence.

Proposed 20-minute video: 2 minutes question and strategy; 4 data/actions/timing; 4 features/models/validation; 4 end-to-end execution using a short reproducible demo and clearly identified saved full-run artifacts; 4 results/interpretation; 2 limitations/reproduction. The demo must actually run the pipeline; a cached full run should be labeled as such. Do not spend the video waiting for a long hyperparameter search.

| Dates, SGT            | Milestone                                                 |
| --------------------- | --------------------------------------------------------- |
| 19–20 October         | A01–A02: scope, protocol, environment                     |
| 21–23 October         | A03–A05: sources, cleaning, actions, training EDA         |
| 24–26 October         | A06–A09: labels, features, ledger, complete baseline      |
| 27–29 October         | A10–A11: profiling and bounded family screen              |
| 30 October–1 November | A12–A13: family analysis, confirmation, freeze            |
| 2–4 November          | A14–A15: final evaluation, reconciliation, interpretation |
| 5–8 November          | A16: report, figures, video                               |
| 9–11 November         | A17: clean reproduction, corrections, package             |
| 12 November           | Submission buffer; deadline 23:59 SGT                     |

With four teammates, suggested ownership is data/actions, features/temporal evaluation, models/compute, and portfolio/report integration. Everyone reviews at least one other component and contributes to interpretation. These are team responsibilities, not automatic parallel coding instructions; dependencies and shared contracts still govern implementation.

## 16. Risk register and stopping rules

| Risk                                     | Trigger and response                                                                     |
| ---------------------------------------- | ---------------------------------------------------------------------------------------- |
| Historical source unavailable            | Use documented core fallback before validation; do not shrink dates after seeing returns |
| Attention/news unavailable as of history | Keep exploratory or omit; retain core price/volume study                                 |
| Action formula or vendor disagreement    | Reconcile original PDF and conventions before final P&L                                  |
| Weak forecasting signal                  | Report uncertainty and benchmark comparison; finish the process                          |
| Nonlinear model unstable                 | Stronger bounded regularization or simpler model via validation; no test-guided rescue   |
| Search exceeds resource budget           | Reduce optional experiments based on profiling, record changed grid before results       |
| Slow final audit                         | Preserve report/reproduction buffer; defer extensions                                    |
| Test inspected and strategy changed      | Disclose contamination; no longer label revised performance as untouched holdout         |
| Daily close execution approximation      | State closing auction/slippage assumptions; do not claim realized execution quality      |

Completion means a reproducible, timestamp-audited study with explained limitations and all required deliverables. It does not require outperforming SPY. Start implementation with A01, then complete the minimal end-to-end pipeline through A09 before committing time to optional data or larger models.
