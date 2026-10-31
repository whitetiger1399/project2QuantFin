# Frontier-AI Releases, U.S. IT Services, and Nifty IT: Fresh Experiment Protocol

## Status and separation from the completed study

This is a new experiment with independent configuration, processed-data root,
analysis root, run IDs, model freeze, checkpoints, hashes, and manifests. Prior
cross-market artifacts remain immutable. The experiment does not erase or
reinterpret the earlier result.

The hypothesis was formulated after earlier project results and after historical
2025 returns had been inspected. Consequently, 2025 is called a **historical
replication set**, not an untouched holdout. A genuinely untouched test requires
future paper trading or a later complete calendar year.

## Decision and execution contract

- Frequency: daily.
- Decision cutoff: 08:55 Asia/Kolkata on NSE session date *t*.
- Inputs: information publicly available strictly before that cutoff.
- Position entry: reported NSE open on *t*.
- Mandatory exit: reported NSE close on *t*; no overnight Indian position.
- Target: constituent-level simple open-to-close return.
- Cohort: the already frozen current Nifty IT constituent cohort.
- Costs: entry and exit each incur the configured one-way cost plus slippage.

Prior U.S. close information is aligned with a strict backward as-of join. An AI
release with only a calendar date is assigned a conservative public time of
23:59:59 UTC and therefore cannot influence an Indian decision until the next
eligible NSE pre-open. Exact same-day trading is allowed only when a verifiable
announcement timestamp precedes 08:55 IST.

## Hypotheses

| ID | Predeclared hypothesis | Test |
|---|---|---|
| H1 | Prior completed U.S. IT-services returns contain incremental information for Nifty IT intraday returns. | F2 versus F1 OOS loss, IC, and net strategy comparison. |
| H2 | Frontier-model release sessions have lower equal-weight Nifty IT intraday returns. | HAC event coefficient and date-randomization inference. |
| H3 | AI events add information beyond U.S. services returns. | F3 versus F2 under identical ridge shrinkage. |
| H4 | Broad U.S. and macro features improve beyond the focused services block. | F4/F5 progression versus F3, with confirmation-only selection. |
| H5 | A signed rule improves on long-only after realistic round-trip costs. | Same predictions evaluated under predeclared execution rules. |

Failure to reject any hypothesis is a valid result. Event counts are expected to
be small, so effect sizes and confidence intervals take priority over p-values.
The provider-event heatmap reports event-minus-non-event mean returns rather
than calling a categorical announcement a correlation. The U.S.-services ×
Nifty IT heatmap uses genuine daily Spearman correlations.

## Data blocks

### Primary U.S. IT-services block

ACN, IBM, CTSH, EPAM, GLOB, DXC, JKHY, LDOS, SAIC, CACI, and CNXC. These are
kept separate from product companies and payment processors.

### Robustness blocks

- IT-enabled payments: FI, FIS, and GPN.
- Enterprise software: CRM, SAP, ORCL, NOW, and ADBE.
- Existing broad U.S., ADR, India, global, rates, volatility, FX, and S&P 500
  blocks remain available in later feature sets.

### Frontier-AI event calendar

The supplied `model_publishing.txt` is parsed into a lossless inventory CSV. A
second curated CSV contains only predeclared releases from major providers. The
inventory is a discovery source; official provider announcements determine the
curated dates. Provider tier, source URL, inventory match, timing precision,
and the no-return-selection declaration are retained in every row.

## Feature progression

1. **F0 Own:** asset identity, seasonality, and only the target stock's own
   lagged market history.
2. **F1 Nifty IT peers:** F0 plus leave-one-out peer summaries. The target stock
   is excluded from its own peer aggregate.
3. **F2 U.S. services:** F1 plus individual and aggregate U.S. IT-services
   features and Indian ADR information.
4. **F3 Nifty 50:** F2 plus Indian broad-market and point-in-time Nifty 50
   aggregates.
5. **F4 S&P 500 aggregate:** F3 plus cross-sectional S&P 500 summaries.
6. **F5 S&P 500 constituents:** F4 plus the selected point-in-time constituent
   return panel.
7. **F6 AI events:** F5 plus frontier-event indicators, provider indicators,
   1/3/5-session decays, rolling counts, time since event, and event × U.S.
   services interactions.
8. **F7 Full context:** F6 plus payments, enterprise software, original U.S.
   technology, broad U.S., global, macro, scheduled-event, and nonlinear blocks.

The controlled ladder uses the same ridge penalty, dates, refits, targets,
transaction costs, and signed execution rule at every rung. Therefore, changes
in OOS performance can be attributed to the added information block rather than
to a simultaneous model or trading-rule change.

Each U.S. services block contains lagged returns, momentum, volatility, moving
average distance, gap, range, close location, volume z-score, RSI, and
cross-sectional mean, median, dispersion, extrema, negative share, and coverage.

The economic objective is to improve expected **net** return under a fixed 100%
gross-exposure cap, explicit round-trip costs, and no overnight Indian risk.
Model selection uses confirmation-period net Sharpe rather than unconstrained
raw return, because maximizing a noisy sample return alone rewards unstable
variance and overfitting. Annual return, expected active-day return, drawdown,
and Sharpe are all reported for every information rung.

## Models and temporal validation

The experiment retains zero, asset-mean, and autoregressive baselines. Ridge,
lasso, elastic net, PCA-ridge, extra trees, histogram gradient boosting, and
random-Fourier-feature ridge are evaluated. Screening and confirmation use
quarterly refits with daily out-of-sample forecasts. A single model is frozen
before the 2025 replication is evaluated; the final stage does not reselect.

- Initial estimation: 2016-07-21 to 2020-12-31.
- Screening: 2021-01-01 to 2022-12-31.
- Confirmation: 2023-01-01 to 2024-12-31.
- Historical replication: 2025-01-01 to 2025-12-31.
- Training scheme: rolling 1,260 sessions with a one-session embargo.

## Trading rules

The primary model-comparison rule is `signed_forecast`:

1. Rank predicted open-to-close returns before the NSE open.
2. Long up to three stocks whose forecasts exceed the positive cost-aware
   hurdle.
3. Short up to three stocks whose forecasts fall below the negative hurdle.
4. Permit both sides when both tails contain qualifying forecasts; remain flat
   when neither side qualifies.
5. Enter at the open and close every position at the close.

This rule is applied identically to every information-set rung. It ensures that
F0 is a genuine own-history-only long/short experiment and that later rungs
measure incremental information.

The separate `hybrid_ai_services_signed` robustness rule is:

1. If a curated frontier event is tradable today, short the equal-weight frozen
   cohort at the NSE open and close all shorts at the NSE close.
2. Otherwise, when the prior U.S. services aggregate is negative, short up to
   three constituents with forecasts below the negative hurdle.
3. Otherwise, buy up to three constituents with forecasts above the positive
   hurdle.
4. Remain flat when no forecast clears the cost-aware hurdle.

Gross exposure is capped at 100%; constituent weight is capped at one-third.
Long-only, signed-forecast, direct services-direction, event-only short, and
hybrid rules are retained as transparent comparators. Strategy rules are
compared on the same frozen predictions and are not tuned on 2025.

## Evaluation

- Forecasts: RMSE, MAE, OOS R² versus zero and asset mean, daily Spearman IC,
  and directional accuracy.
- Trading: net annual return, volatility, Sharpe, Sortino, maximum drawdown,
  Calmar, turnover, active sessions, long/short exposure, and cost sensitivity.
- Inference: HAC loss-differential tests, Benjamini–Hochberg correction,
  HAC alpha, circular block-bootstrap Sharpe intervals, and annual stability.
- Event analysis: event/non-event effect size, HAC event coefficient,
  randomization p-value, provider counts, and explicit small-sample warning.
- Transmission visualization: readable U.S.-services × Indian-services heatmap,
  publishing-provider × Nifty IT event heatmap, publishing-provider × U.S.
  services post-release heatmap, mediated post-U.S.-reaction Nifty IT heatmap,
  event return distribution, strategy equity curves, and regime/exposure tables.
- Daily audit: date, information set, forecast-driven position, long and short
  holdings, gross/net exposure, turnover, trading cost, daily net return, and
  cumulative wealth.

## Reproducibility and audit trail

Every material output contains a UTC timestamp and content hash. Dataset hashes
include resolved configuration, raw snapshot manifests, audit contract, event
calendar, membership files, and manual context inputs. Runs contain resumable
per-refit checkpoints. Screening, confirmation, freeze, final replication, and
strategy comparison have parent hashes and separate immutable directories.
