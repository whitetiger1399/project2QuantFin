# Backtest and video requirement review

Date: 2 November 2026. Scope: supplied Project 2 assignment, current report, model implementation and the saved 2025/2026 evaluation ledgers. This is a code/artifact review, not a new model experiment or a brokerage execution audit.

## Submission and recording requirements

| Assignment requirement | Prepared response |
|---|---|
| Team of four; roughly balanced contributions | Four proposed five-minute presenter sections; alphabetical author roster and student IDs on cover |
| Video 15–25 minutes | 20-minute schedule; 16 timed slides, speech ends by 19:40 |
| Show data build → fit → validation → out-of-sample with costs | Scenes 11–12 and manual recording commands D1–D5; actual execution must be recorded by the team |
| Economic idea and model assumptions | Shared-sector information, market-hour ordering, sparse/dense/nonlinear model assumptions |
| Overfitting and timing controls | Past-only preprocessing, rolling windows, embargo, screening/confirmation/freeze; prior research inspection disclosed |
| Prediction-to-trade rule | Long/short/flat hurdle, position caps, daily close-out and transaction costs |
| OOS figures and interpretation | Forecast-complexity plot, family comparison, cumulative benchmark comparison, annualized metrics and cost chart |
| Source package | Existing README/environment/code; recording commands link to actual entry points |
| Report PDF | Assignment naming pattern: Group_X_Report.pdf; confirm Canvas group number before final naming |
| Video delivery | MP4 or staff-accessible downloadable link, with password if needed |
| Deadline | 12 November 2026, 23:59 Singapore time |

Section 5 asks to show an end-to-end run. It does not explicitly require an unedited live multi-hour fit. A labelled recording of genuine launch, progress and completion can fit the presentation; plan-only output or old output inspection alone cannot stand in for the fit. The safety note calls for historical research, not real orders.

## Is backtesting implemented?

**Yes.** The project uses a custom backtesting engine in `src/quantfin/cross_market/experiments.py`. The assignment’s named libraries are illustrative, so using this engine is compatible with the requirement.

| Code location | Reviewed behavior |
|---|---|
| `forecast_blocks` | Daily predictions grouped into quarterly refitting blocks |
| `_fit_block` | Earlier training dates; one-session embargo; rolling window; training-only viability filtering and transformations |
| `_strategy_ledger` | Uses forecast signs and an effective 15-bps hurdle; selects eligible longs and shorts; caps weights/exposure |
| `_strategy_ledger` | Signed realized open-to-close return; every position begins/ends in cash; turnover equals twice gross exposure |
| `_strategy_ledger` | Assumed one-way cost = 5 bps fee/spread proxy + 2.5 bps slippage; net = gross − turnover × one-way cost |
| `_annualized_metrics` | Compounds daily net returns; computes geometric annualized return, annualized volatility, mean/std Sharpe and drawdown |
| `cost_sensitivity` | Includes fixed-holdings friction stress tests; distinguishes them from policy-responsive sensitivity |
| `inferential_tests` | Includes dependence-aware inference; report uses date-level/block uncertainty |

## Read-only checks performed

`scripts/recording_evidence.py` was run during presentation preparation. It did not fit models or place trades.

| Period | Sessions | Net compounded return | Checks |
|---|---:|---:|---|
| 2025 calendar year | 249 | −4.04% | PASS |
| 2026 January–September | 185 | +15.01% | PASS |

Checks: completed run status; unique session rows for the selected configuration; finite returns/costs; gross-minus-cost equals net; two-sided turnover; recorded 7.5-bps one-way cost; gross exposure cap; training end precedes prediction block; saved ledger/diagnostic hashes where present in the run manifest. Exact source IDs remain in the report’s appendices and release registry. Combined report net return is +10.37%; the code review does not imply that this is a guaranteed expected future return.

## Limits that remain material

The backtest is a coherent historical simulation under declared assumptions. Public opening prices approximate execution; full taxes, borrow constraints, impact and opening-auction slippage are not modeled. The chosen current cohort has survivorship conditioning. The canonical full feature set contains flagged macro vintage fallbacks, with a completed stricter exclusion sensitivity reported separately. ETF alternatives include overnight exposure and different cost treatment. The 2025 refits and 2026 fixed-fit extension use different schedules. Both periods had been examined in earlier research iterations; model-OOS predictions do not create a pristine research holdout. Sparse retrospective AI releases support exploratory associations, not causal identification.

These limits are included in the spoken script and screen directions. They do not erase the implemented backtest, but they constrain the claims that can be made from it.
