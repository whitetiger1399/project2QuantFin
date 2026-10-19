# Feature, Model, and Validation Guide

## Research question

The implemented study asks whether information observable after the SPY close on session `t` can predict the adjusted-close return from `t+1` to `t+2` well enough to support a long/cash SPY strategy after transaction costs. QQQ, IWM, TLT, and GLD are predictor markets; they are not traded. The project uses daily data from 2005 through 2025.

This is a deliberately narrow forecasting problem. It supports careful timing controls, interpretable benchmarks, and a realistic walk-forward test. It does not claim that the adjusted close is an executable price or that a statistical association is causal.

## Information and execution timeline

For every row:

1. All features use observations available through the close of signal session `t`.
2. The position is chosen from the prediction made after that close.
3. Entry is delayed until the close of `t+1`.
4. The target is the adjusted-close return from `t+1` to `t+2`.
5. The label becomes available only at the close of `t+2`.

At each monthly refit with origin `s`, training requires `label_available_session <= s`. Imputation, scaling, PCA, random Fourier features, and the estimator are fit inside the training sample. No full-sample learned transform is stored in the feature table.

## Data roles and sample splits

| Period | Dates | Permitted use |
|---|---:|---|
| Warmup | 2005-01-01 to 2005-12-31 | Establish trailing feature history |
| Initial train | 2006-01-01 to 2014-12-31 | Fit models and perform training-only EDA |
| Screening | 2015-01-01 to 2018-12-31 | Compare the broad model and hyperparameter grid |
| Confirmation | 2019-01-01 to 2021-12-31 | Confirm a small set chosen from screening |
| Final test | 2022-01-01 to 2025-12-31 | One frozen evaluation after selection |

Raw-market EDA defaults to a 2014-12-31 cutoff. Full-sample plots should be generated only after the final strategy freeze. Feature EDA and feature/target tests default to `initial_train`.

## Feature catalog

Let `P_t` denote adjusted close, `r_t = log(P_t/P_{t-1})`, and `V_t` denote volume. A window ending at `t` contains no future observation.

### F0: price history

- **Return lags:** current observed return and lags 1, 2, 3, 4, 9, 14, and 19. These test short memory, reversal, and drift.
- **Momentum:** `P_t/P_{t-k}-1` for 2, 3, 5, 10, 15, 20, 40, 60, 120, and 252 sessions. These span daily to annual trend horizons.
- **Moving-average trend:** price relative to 5, 10, 15, 20, 50, 100, and 200-session simple moving averages; 12/26 EMA spread; 20-session average slope; 50/200 average spread.
- **Volatility and distribution:** rolling standard deviation at 5, 10, 20, 60, and 120 sessions; 10/60 volatility ratio; 20-session downside deviation and EWMA volatility; 20 and 60-session skew, excess kurtosis, and first-order autocorrelation.
- **Drawdown:** distance from the trailing 60 and 252-session price maximum.

F0 is the main compact ablation. It tests whether SPY's own price path contains enough signal.

### F1: technical, trading, and calendar state

F1 contains F0 plus:

- **Technical state:** RSI(14), 20-session Bollinger z score, 14-session stochastic position, normalized MACD, its signal, and histogram.
- **Intraday structure:** open-to-close return, overnight gap relative to the preceding close, and high-low range divided by close.
- **Volume and liquidity:** volume relative to 20 and 60-session averages, log-volume z scores, 5-session log-volume change, scaled 20-session OBV change, and a 20-session Amihud proxy.
- **Interactions:** return times abnormal volume, momentum times volatility, and drawdown times volatility.
- **Calendar:** sine/cosine encodings for weekday and month, plus an indicator for the final five calendar days of a month. These are deterministic from the current date.

These variables test whether the same trend has different implications under stress, unusual volume, or different calendar states.

### F2: cross-asset context

F2 contains F1 plus QQQ, IWM, TLT, and GLD momentum at 2, 5, 20, 60, and 120 sessions, their 20-session volatility, and their 60-session return correlation with SPY. It also includes QQQ-minus-SPY and IWM-minus-SPY 20-session relative strength and the TLT/GLD 60-session correlation.

The predictors approximate growth leadership, small-cap risk appetite, duration, and defensive commodity behavior. Missing values remain missing until the training-only median imputer. No price is forward-filled.

## Cleaning and audit rules

- Raw downloads are immutable, timestamped snapshots with SHA-256 hashes.
- Conflicting duplicate rows, invalid OHLC relationships, nonpositive prices, negative volume, weekend rows, and missing SPY adjusted closes stop cleaning.
- Structurally valid extreme returns and zero volume are retained and reported. Their economic cause should be checked before any removal.
- The panel is anchored to observed SPY sessions. Predictor gaps remain null.
- Adjusted close is the total-return research proxy. Dividends must not be added again.
- Yahoo is the primary source. Stooq comparison is optional and diagnostic; its observations are never silently merged.

## EDA and statistical diagnostics

Market EDA exports coverage, normalized price histories, event windows, return distributions, rolling volatility, annual returns, month and weekday seasonality, federal-holiday proximity, cross-asset correlations, recent trends, and extreme-return candidates. Event labels are descriptive and never become features.

Feature EDA exports missingness, feature correlation, highly correlated pairs, feature/target correlations, distributions, and rolling correlation stability. Use this to identify redundancy and unstable relationships, not to repeatedly redesign against later splits.

The statistical report includes:

- ordinary and heteroskedasticity/autocorrelation consistent mean-return tests;
- Jarque-Bera normality diagnostics;
- ADF and KPSS stationarity diagnostics for price and return series;
- Ljung-Box tests for return and squared-return serial dependence;
- ARCH LM testing for conditional heteroskedasticity;
- a descriptive variance-ratio test;
- Pearson and Spearman feature/target tests with Benjamini-Hochberg false discovery rate adjustment.

P-values are diagnostics. Dependence, multiple model searches, and economic selection mean they cannot establish a tradable causal effect.

## Model families

| Family | Purpose | Main complexity control |
|---|---|---|
| Historical mean | Strict forecasting baseline | One fitted mean |
| Autoregression | Small linear time-series baseline | Three recent returns |
| Ridge | Stable dense linear effects | L2 penalty |
| Lasso | Sparse feature selection | L1 penalty |
| Elastic net | Sparse but correlated groups | L1/L2 mix |
| PCA plus ridge | Compressed common factors | Component count and L2 penalty |
| Random forest | Nonlinear interactions and thresholds | Depth, leaf size, feature sampling |
| Extra Trees | More randomized nonlinear ensemble | Depth and leaf size |
| Histogram gradient boosting | Sequential nonlinear corrections | Leaves, iterations, leaf size, L2 |
| Random Fourier features plus ridge | Controlled nonlinear capacity study | 16 to 4096 basis features and ridge penalty |

The random Fourier family is the planned experiment for parameter count relative to training sample size. The 4096 basis version can cross `P/T = 1`, especially with a rolling window. The report plots out-of-sample Sharpe against parameters per training observation and training error against out-of-sample error. High capacity is regularized and evaluated chronologically; crossing `P/T = 1` is an experiment, not a reason to expect better forecasts.

## Hyperparameter strategy

The pipeline uses a declared finite grid with chronological evaluation. It does not use shuffled cross-validation. The `quick` profile is a smoke-scale research run, `standard` is the main broad comparison, and `deep` expands the nonlinear capacity grid.

Screening evaluates all configured candidates from 2015 through 2018 with monthly refits. Selection ranks candidates by median annual net Sharpe, requires prediction coverage, breaks ties using lower turnover and lower complexity, and selects distinct model families. Confirmation evaluates only those choices plus the two baselines during 2019 through 2021. A new selection is made from confirmation, then frozen with the exact data manifest, code/config hashes, feature set, window, threshold, costs, and configurations. Final testing validates this freeze before it can run.

Feature-set ablation should run F0, F1, and F2 through screening. Treat those as three planned experiments and compare whether added feature blocks improve stable out-of-sample results. Choose one feature set before confirmation. Expanding versus 1260-session rolling training is a second planned sensitivity analysis; choose one before confirmation.

## Portfolio and forecast evaluation

The forecast becomes a long position only when predicted return exceeds 10 basis points. Otherwise the strategy holds cash. A 5 basis point one-way cost is charged on every position change, including entry and final liquidation.

Saved metrics include MSE, MAE, out-of-sample R-squared versus the historical-mean forecast, directional accuracy, annualized net return and volatility, Sharpe, CAGR, maximum drawdown, median annual Sharpe, exposure, turnover, total cost, training error, training-to-test error gap, fit time, and parameter-to-observation ratio. Reports add wealth, drawdown, annual return, rolling Sharpe, exposure, cost sensitivity, feature-diagnostic stability, and a moving-block bootstrap interval for strategy return relative to SPY.

SPY buy-and-hold is an investment benchmark. Historical mean and autoregression are forecast benchmarks. A market-timing strategy can have lower exposure, so Sharpe, return, drawdown, turnover, and exposure must be read together.

## Compute design

The default M1/16 GB configuration uses two tree workers and one numerical thread per fit. Fits run sequentially across model configurations and monthly refits, which limits memory pressure and avoids nested thread oversubscription. Parquet checkpoints are written after every fit. Each checkpoint has a metadata file and content hash. `--resume` reuses only checkpoints whose hashes validate.

The terminal progress bar reports completed fits, elapsed time, rate, and ETA. `--plan-only` prints exact fit counts before starting. `run-status` reports completed checkpoints if a terminal was closed or a run failed. The standard grid is intended for the main run; use deep only after the standard workflow and data checks are sound.

The local content-addressed tracker is sufficient for this assignment and avoids an MLflow service dependency. A run ID hashes the dataset, configs, source code, stage, feature set, window, and selection/freeze inputs. A changed research input creates a different run ID.

## Interpretation checklist

Before accepting a result, verify that its gains survive costs, appear across years, do not depend on one crisis window, exceed both forecast baselines, and remain plausible under a neighboring hyperparameter. Inspect train/test error gaps and `P/T`; review feature signs or tree importance across refits; compare F0, F1, and F2; compare expanding and rolling windows; report negative findings. Avoid presenting event annotations, feature importance, or unadjusted p-values as causal explanations.
