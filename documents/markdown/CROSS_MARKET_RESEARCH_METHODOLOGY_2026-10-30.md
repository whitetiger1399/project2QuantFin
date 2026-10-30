# Cross-Market Nifty IT Research Methodology

**Protocol date:** 30 October 2026  
**Frequency:** Daily  
**Decision time:** 08:55 Asia/Kolkata, before the NSE pre-open and continuous session  
**Execution:** Reported NSE open to reported NSE close on the same decision date  
**Research status:** Historical backtest only; no live trading

## 1. Research question

The study asks whether information that is observable before the Indian market opens improves forecasts of the same-day open-to-close returns of current Nifty IT constituents. The central comparison is not simply “which model has the highest return.” It is whether progressively richer information sets improve strictly out-of-sample forecasts and post-cost trading performance:

1. each Indian stock’s own history;
2. Indian market and Nifty 50 context;
3. completed US technology sessions and Indian IT ADRs;
4. broad US, global, volatility, rates, currency, and commodity context;
5. point-in-time S&P 500 constituent returns; and
6. conservative macroeconomic and nonlinear transformations.

The economic mechanism is delayed cross-market information transmission. US technology demand, risk appetite, Indian ADR price discovery, dollar conditions, and global volatility may be incorporated into Indian IT prices when NSE trading begins. The alternative explanation is that these signals are noisy and disappear after shrinkage, temporal validation, and costs.

## 2. Assets, cohort, label, and benchmarks

The forecast cross-section is the ten-stock cohort listed in the official current Nifty IT constituent file as of 30 October 2026: COFORGE, HCLTECH, INFY, LTM, MPHASIS, OFSS, PERSISTENT, TCS, TECHM, and WIPRO.

This is intentionally a **fixed-current-cohort retrospective study**. It is not described as a historical replication of the Nifty IT index. Results before the cohort date are subject to survivorship conditioning and must be interpreted as predictability among firms that survive into the current index. The limitation is explicit because reliable point-in-time Nifty IT membership was not available in time for the study.

For stock \(i\) and Indian decision session \(t\), the target is

\[
y_{i,t}=\frac{C_{i,t}}{O_{i,t}}-1,
\]

where \(O_{i,t}\) and \(C_{i,t}\) are the unadjusted reported NSE open and close. Split and dividend fields are retained for audit. Rows with invalid or impossible OHLC values are quarantined rather than winsorizing the target.

Benchmarks are:

- an investable Nifty IT ETF proxy (ITBEES; the Nifty IT index is a documented fallback where ETF history is absent);
- Nifty 50 buy-and-hold through NIFTYBEES, with the Nifty 50 index as fallback;
- an equal-weight portfolio of the fixed ten-stock cohort;
- zero-return, expanding/rolling asset-mean, and autoregressive forecast baselines.

ETF and index benchmark returns are close-to-close buy-and-hold outcomes. They are not inserted into the predictive feature matrix on the same date.

## 3. Data inventory and provenance

The build resolves the newest completed immutable snapshot for every source and hashes every source manifest. A passing `audit_cross_market_raw.py` report is mandatory.

| Information block | Source snapshot | Frequency | Predictive use |
|---|---|---:|---|
| Nifty IT stocks, Indian indices, India VIX, USD/INR, ETFs | Yahoo Finance snapshot | Daily | Prior completed India session only |
| 20 predeclared liquid US technology stocks | Yahoo Finance snapshot | Daily | Latest completed US session before 08:55 IST |
| SPY, QQQ, sectors, VIX, rates/commodity/EM proxies | Yahoo Finance snapshot | Daily | Latest completed US session |
| INFY and WIT ADRs | Yahoo Finance snapshot | Daily | Latest completed US session |
| European and Asian index context | Yahoo Finance snapshot | Daily | Only sessions strictly earlier than the India decision date |
| Historical S&P 500 constituents | Third-party membership history + Yahoo prices | Daily | Membership-filtered, provisional PIT predictors |
| Historical Nifty 50 constituents | NiftyHistory membership file + Yahoo prices | Daily | Membership-filtered breadth aggregates |
| US and Indian rates, spreads, FX, VIX, CPI | FRED/ALFRED snapshot | Daily/monthly | First-vintage availability when available; conservative lag for current-vintage fallbacks |
| Holidays, scheduled events, RBI rates, rainfall | Manual official-data interface | Event/monthly | Used only when populated with publication timestamps |

All run IDs contain a UTC timestamp and deterministic content hash. Manifests retain configuration hashes, source-manifest hashes, package versions, parent IDs, output hashes, and completion state.

The provisional S&P 500 and Nifty 50 files end before the last market observation. For rows after each file's terminal membership date, the last recorded active membership is carried forward until the sample end. This is a state-persistence assumption using the last information in the source, not a claim that no later reconstitution occurred; it is disclosed and can be disabled in the configuration.

## 4. Information clock and leakage controls

Every target row represents an 08:55 IST decision. Market features are aligned with a strict as-of join whose source session must be **earlier** than the decision date. This conservative rule excludes:

- the Indian open, high, low, close, and volume for the target session;
- an Asian market’s partially completed same-date session;
- a US session that has not yet closed;
- any macro release whose availability date is after the decision.

ALFRED observations use `realtime_start` to approximate first availability. Series that only exist as current-vintage FRED histories are marked in the feature dictionary and receive conservative release lags. Revised monthly Indian CPI/rate series enter F5 robustness analysis only, not the primary F0–F4 comparison.

All scaling, median imputation, winsor limits, viable-column checks, PCA loadings, feature selection implicit in regularization, and model fitting are estimated inside each historical training window. The target is never winsorized. One completed Indian session is embargoed before every forecast block.

## 5. Cleaning policy

The pipeline:

1. fails on duplicate sessions;
2. coerces numeric market fields explicitly;
3. requires positive OHLC values;
4. quarantines rows violating the OHLC envelope;
5. uses `INR=X` for close-to-close FX only;
6. removes the known NIFTYBEES 7 July 2009 zero-open row;
7. excludes the eleven optional Nifty 500 symbols identified by the raw audit until independently repaired;
8. retains missing features until each training fold, then drops columns exceeding 40% training-window missingness;
9. median-imputes remaining values using the training window only; and
10. clips predictive features at training-window 0.5% and 99.5% quantiles.

Every removed OHLC row is written to `cleaning_evidence.json`.

## 6. Feature families

### F0 — own-stock and calendar information

- log-return lags at 1, 2, 3, 5, 10, and 21 sessions;
- cumulative momentum over 5, 10, 21, 63, 126, and 252 sessions;
- realized and downside volatility over 5, 10, 21, and 63 sessions;
- price-to-moving-average gaps over 5, 10, 21, 50, 100, and 200 sessions;
- rolling drawdowns, return z-scores, gap return, intraday range, close location, volume z-scores, and RSI(14);
- stock fixed effects;
- weekday, month, annual, and semiannual Fourier terms plus month/quarter-end markers.

### F1 — Indian market context

F0 plus lagged Nifty IT, Nifty 50, Nifty Bank, India VIX, USD/INR, ETF signals, fixed-cohort breadth/dispersion, and point-in-time Nifty 50 breadth aggregates.

### F2 — limited US technology information

F1 plus the predeclared 20-stock US technology basket and INFY/WIT ADR features. This directly tests the sector-spillover hypothesis without broad-market dimensionality.

### F3 — global context

F2 plus SPY, QQQ, US sector ETFs, US VIX, duration, dollar, metals, oil, copper, emerging-market proxies, and completed global index sessions.

### F4 — broad US complexity

F3 plus membership-filtered S&P 500 constituent returns at 1, 5, and 21 sessions and cross-sectional breadth, dispersion, positive-share, and tail summaries. Symbol eligibility and coverage ranking are frozen using data no later than 31 December 2020.

### F5 — macro and nonlinear robustness

F4 plus point-in-time/conservatively lagged macro levels, changes, long-window z-scores, scheduled-event distances when available, squares, signed square roots, and a limited predeclared interaction set. F5 is a robustness experiment because several Indian monthly macro histories are current-vintage fallbacks.

## 7. Hypotheses

| ID | Falsifiable hypothesis | Comparison | Evidence |
|---|---|---|---|
| H1 | Completed US technology information adds incremental signal. | F2 versus F1 under identical ridge settings | OOS \(R^2\), rank IC, post-cost Sharpe |
| H2 | Broad S&P 500 information improves on a limited technology basket. | F4 versus F2/F3 | Same metrics and feature-family permutation importance |
| H3 | Shrinkage is necessary as dimensionality grows. | Ridge/LASSO/elastic net/PCA-ridge versus weak/no regularization | Validation and confirmation errors; coefficient stability |
| H4 | Approximation complexity can improve performance when paired with ridge shrinkage. | RFF component/input ratios 0.25–15 with predeclared penalties | Complexity-generalization curve, parameter ratios, OOS Sharpe |
| H5 | Any signal survives plausible implementation frictions. | 0–40 bps round-trip costs and top-\(k\)/hurdle variants | Net return, Sharpe, turnover, drawdown |
| H6 | Signal is not confined to one market regime. | yearly, volatility, rate, and crisis/event subsamples | Stability tables with confidence intervals |

Failure to reject a null is a valid research result and is not rewritten as evidence of predictability.

## 8. Temporal experiment protocol

| Phase | Dates | Permitted use |
|---|---|---|
| Initial training | 21 Jul 2016–31 Dec 2020 | First estimation windows and predeclared universe ranking |
| Screening | 1 Jan 2021–31 Dec 2022 | Feature progression, model families, complexity grid |
| Confirmation | 1 Jan 2023–31 Dec 2024 | Confirm at most 12 screening candidates and freeze one |
| Final test | 1 Jan 2025–29 Oct 2026 | Open once for the frozen model and forecast baselines |

Models refit at each month start. The primary estimator uses the most recent 1,260 Indian sessions; expanding-window estimation is a robustness check. Within every refit, only dates before the forecast block and before the one-session embargo are used.

Screening includes:

1. a controlled F0→F5 ridge feature progression;
2. LASSO, elastic net, PCA-ridge, random forest, extremely randomized trees, histogram gradient boosting, and ridge comparisons on F4;
3. random Fourier feature ridge models on the fixed F2 information set with complexity ratios 0.25, 0.5, 1, 2, 5, 10, and 15, capped at 10,000 generated features; holding the information set fixed separates functional complexity from the F4 broad-universe experiment;
4. predeclared shrinkage and kernel-scale grids.

The top two configurations per family enter a maximum twelve-candidate confirmation set. Selection is by post-cost net Sharpe, with OOS \(R^2\), rank IC, lower turnover, and lower complexity as ordered tie-breakers. `freeze_cross_market_model.py` records exactly one winner before final testing.

## 9. Forecast-to-position rule

On each decision date, forecasts are ranked cross-sectionally. The primary strategy holds up to the three stocks with the highest positive forecast, provided the forecast exceeds both the declared hurdle and estimated round-trip cost. Eligible stocks receive equal weights subject to a 50% single-name cap; unused capital remains cash. All positions enter at the reported open and exit at the reported close.

Primary friction is 5 bps commission/impact plus 2.5 bps slippage per side (15 bps round trip). Robustness spans 0, 10, 20, and 40 bps round trip, top 1/2/3/5 portfolios, and multiple forecast hurdles. Short portfolios are secondary because daily borrow availability and borrow fees are not observed.

## 10. Evaluation and interpretation

Forecast metrics are RMSE, MAE, directional accuracy, daily cross-sectional Spearman IC, OOS \(R^2\) against zero and asset-mean forecasts, and prediction coverage. Strategy metrics are annualized net return, volatility, Sharpe, Sortino, maximum drawdown, Calmar ratio, turnover, cost sensitivity, and benchmark-relative performance.

Report figures include coverage, distributions, rolling return/volatility, readable correlation extremes, cross-asset correlations, US–India lead/lag diagnostics, volatility regimes, feature-family missingness, validation leaderboard, cumulative wealth, drawdown, rolling IC, and complexity-generalization curves. Giant unreadable correlation matrices are deliberately excluded.

For interpretable models, standardized coefficients or tree importances are saved by refit. During final testing, every model also receives grouped OOS permutation diagnostics by feature family. These explanations are associative: global event overlays and price movements are not labelled causal without an identification design.

## 11. Reproducibility and run identity

Every artifact ID follows `type_YYYYMMDDTHHMMSSZ_hash`. The timestamp distinguishes executions; the deterministic hash identifies the data/configuration/model content. A repeated execution therefore has a new run ID but the same content hash. A resumed execution must name its original run ID and pass a content-hash check before any checkpoint is reused.

The final report must cite the exact dataset ID, analysis ID, screening ID, confirmation ID, freeze ID, and final-test ID. It must also retain the limitations of Yahoo-adjusted data, provisional third-party point-in-time memberships, fixed-current-cohort survivorship conditioning, current-vintage macro fallbacks, reported-open execution, and unmodelled market impact.
