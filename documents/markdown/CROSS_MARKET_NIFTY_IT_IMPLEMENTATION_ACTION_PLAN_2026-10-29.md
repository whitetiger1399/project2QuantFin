# Cross-market prediction of Nifty IT stocks

## Research design and agent implementation action plan

**Design date:** 29 October 2026, Singapore time  
**Course:** Data Science in Quantitative Finance DSA5205  
**Status:** Design only. No data retrieval, pipeline changes, feature generation, model fitting, or backtesting is authorized by this document.  
**Primary question:** Does information from completed US technology stocks and the full point-in-time S&P 500 improve forecasts and net trading performance for Nifty IT constituents beyond information already available from Nifty IT, Nifty 50, and other Indian sector indices?  
**Primary traded market:** National Stock Exchange of India  
**Primary traded universe:** Point-in-time Nifty IT constituents  
**Prediction frequency:** Daily, once for every eligible NSE trading session  
**Decision timestamp:** 08:55 Asia/Kolkata, immediately before the regular NSE pre-open session begins  
**Primary horizon:** NSE open to NSE close on the same trading session  
**Literature anchors:** Chinco, Clark-Joseph, and Ye (2019); Kelly, Malamud, and Zhou (2024)

---

## 1. Executive design decision

The proposed project uses one locked event-time protocol. The primary experiment generates one forecast per eligible NSE trading day at 08:55 Asia/Kolkata, immediately before the regular NSE pre-open session begins. It trades the point-in-time constituents of Nifty IT from the official NSE opening price to the official NSE close. It may use the most recent completed US session because that information is available several hours before the NSE opens.

The following is the primary protocol:

1. Determine the NSE trading session $d$.
2. Set the decision timestamp to 08:55 Asia/Kolkata, before the regular pre-open session begins at 09:00.
3. Locate the latest US session whose official close timestamp is strictly earlier than the decision timestamp.
4. Construct all Indian and international features using information available by the decision timestamp.
5. Generate one daily prediction for each eligible point-in-time Nifty IT constituent's open-to-close return for NSE session $d$.
6. Submit the model-implied basket for execution at, or immediately following, the official open.
7. Close all positions at, or immediately before, the NSE close.

The target for stock $i$ on NSE session $d$ is:

\[
r^{OC}_{i,d}=\frac{C_{i,d}}{O_{i,d}}-1,
\]

where $O_{i,d}$ and $C_{i,d}$ are consistently corporate-action-adjusted open and close prices. Neither the opening price nor any information generated during session $d$ may enter the forecast for session $d$.

The primary data frequency is daily. Stock, index, ETF, volume, and volatility features are derived from completed daily sessions. Lower-frequency macroeconomic observations may be carried forward only after their historical release time, with an age feature. Minute bars, live pre-open indications, opening-auction order data, and other intraday predictors are excluded from the primary study.

The official NSE schedule currently places the regular pre-open process from 09:00 to 09:15 and normal trading from 09:15 to 15:30. Special sessions, exchange outages, and notified schedule changes must use the dated official calendar rather than the ordinary clock rule.

The suggested alternative, “decide just before the US open and trade US open to close,” is a valid reverse-direction experiment, but it trades US securities using Indian information. It does not answer the primary NSE question. It is excluded from the first implementation and may be considered after the NSE study is complete.

### 1.1 Recommended research architecture

The research should use two connected prediction layers:

- **Technology-market layer:** predict the Nifty IT open-to-close index return and determine broad technology exposure.
- **Cross-sectional layer:** predict each Nifty IT constituent's return relative to Nifty IT and rank the technology stocks.

For stock $i$:

\[
\widehat r_{i,d}
=
\widehat r^{MKT}_{d}
+
\widehat r^{REL}_{i,d}.
\]

This architecture gives each reference paper a precise role:

- Chinco, Clark-Joseph, and Ye motivate sparse, short-lived cross-market links in the stock-selection layer.
- Kelly, Malamud, and Zhou motivate nonlinear random-feature complexity with shrinkage in the market-timing layer.

The work is an adaptation, not a replication. The original papers use different markets, frequencies, targets, sample structures, and execution assumptions.

---

## 2. Research scope and exclusions

### 2.1 In scope

- Daily Nifty IT constituent open-to-close expected returns, generated once immediately before each eligible NSE opening process.
- Point-in-time Nifty IT constituent membership where licensing and access permit it.
- Nifty 50 and major Indian sector indices as domestic market-state predictors and benchmarks.
- A controlled progression from a limited US technology-stock universe to the full point-in-time S&P 500 constituent universe.
- Indian stock, index, sector, volatility, liquidity, currency, and calendar information.
- Completed US broad-market, style, volatility, and sector sessions.
- Strict timestamp-based US-to-India alignment.
- India-only versus India-plus-US feature ablations.
- Sparse linear, shrinkage, tree, and random-feature model comparisons.
- Chronological nested validation and an untouched final evaluation after the protocol is frozen.
- Long-only primary portfolio and intraday long-short secondary analysis.
- Transaction costs, turnover, exposure, drawdown, uncertainty, and model interpretation.

### 2.2 Excluded from the first implementation

- Minute-level data, pre-open order-book data, live auction indications, or reconstruction of the Chinco et al. experiment.
- Trading at the US open.
- Unscheduled news sentiment gathered retrospectively.
- Current Nifty IT or S&P 500 constituents backfilled over the full history without a survivorship disclosure.
- LSTM, Transformer, or large deep-learning searches before simple models are complete.
- Same-day Indian open, high, low, close, or volume as predictors of that day's open-to-close return.
- Macroeconomic observations without a defensible historical availability timestamp.
- Selection based on the final evaluation period.
- Claims that a statistical association is a causal international transmission mechanism.

---

## 3. Data-source decision

The source hierarchy is determined before implementation. Each source must be accompanied by a retrieval timestamp, raw-file hash, license or usage note, field dictionary, timezone, and availability rule. Raw snapshots are immutable.

### 3.1 Source-of-record hierarchy

| Priority | Data block | Preferred source | Practical fallback | Decision and restriction |
|---:|---|---|---|---|
| 1 | NSE stock OHLCV and trades | Official NSE daily CM-UDiFF Common Bhavcopy and security master | NSE security-wise historical price-volume download | Official NSE is the source of record for Indian execution prices and volume |
| 1 | Nifty IT point-in-time membership | Licensed historical constituent data from NSE Indices or an authorized institutional vendor available through NUS | Reconstructed membership from dated NSE Indices notices and archived factsheets, with manual verification | Implementation cannot claim a historical Nifty IT constituent strategy until this gate passes |
| 1 | Nifty 50 and Indian sector indices | NSE Indices historical index data | NSE historical index archives | Use official OHLC and documented index names |
| 1 | India VIX | Official NSE India VIX historical data | No unverified substitute in the primary model | India VIX is available from official NSE historical reports |
| 1 | Corporate actions and identifiers | NSE corporate-action reports, security masters, ISIN mappings | Authorized institutional vendor | Symbol changes must be linked by security identifier rather than ticker text alone |
| 2 | Point-in-time S&P 500 membership and US stock OHLCV | CRSP/Compustat through WRDS, Bloomberg, Refinitiv, FactSet, or another authorized NUS institutional source | Licensed historical S&P constituent source plus timestamped Yahoo price snapshots | A current S&P 500 constituent list must never be backfilled as the historical top-500 universe |
| 2 | US broad and sector ETFs | Authorized NUS institutional source, if available | Timestamped Yahoo Finance snapshots through `yfinance`, subject to Yahoo terms | Free fallback is acceptable for academic research but must retain the legal disclaimer and verification |
| 2 | US VIX | Official Cboe historical VIX data | FRED VIX close only as a checked secondary representation | Cboe is the preferred source for the volatility index |
| 2 | Federal Reserve policy and US rates | Federal Reserve FOMC rate history and calendars; FRED/ALFRED real-time series | Treasury or Federal Reserve source files | Use target range, effective federal funds rate, dated decisions, and release-aware yields; revised data must not be backfilled |
| 2 | RBI policy, liquidity, and bank lending rates | RBI DBIE/publications and dated Monetary Policy Committee releases | Authorized vendor retaining publication dates | Repo/SDF/MSF/bank rate/CRR/SLR are distinct from monthly WALR and MCLR lending-rate series; each uses its actual availability date |
| 2 | USD/INR | RBI/FBIL reference-rate history | Authorized vendor or timestamped market-data snapshot | Publication time determines whether the value is available for the next NSE decision |
| 3 | Indian rainfall and climate context | India Meteorological Department daily/subdivisional data and official climate normals | No weather block if historical publication timing or license cannot be established | Rainfall is optional, low-priority context; use anomalies available before the signal, never final-season totals |
| 3 | Scheduled policy and exchange events | Official Federal Reserve, RBI, NSE, NYSE, and Nasdaq calendars | Manually versioned event calendar with source links | Calendar features are known in advance; realized outcomes enter only after official release |
| 3 | Exchange sessions and holidays | Official NSE, NYSE, and Nasdaq calendars | A maintained exchange-calendar library verified against official calendars | Join by timestamps and trading sessions, never by naive date equality |

Official NSE historical reports expose daily and monthly capital-market archives, security-wise OHLCV, historical indices, and India VIX. NSE changed current bhavcopy distribution to the CM-UDiFF common format after discontinuing older formats in July 2024. The ingestion design must therefore be version-aware rather than assume one schema over the entire retrieval process.

NSE Indices publishes current constituents and historical index levels, but consistent historical constituent files are a separate data product. A current constituent download is not evidence of historical membership. The preferred solution is licensed point-in-time Nifty IT membership through NSE Indices or an authorized institutional source. The same rule applies to the S&P 500 predictor universe: today's members cannot be used as if they were the top 500 US stocks throughout history.

### 3.2 Exact initial asset list

The experiment deliberately expands from a small, interpretable information set to the complete point-in-time S&P 500 cross-section. The stages are fixed in advance so that information gain is distinguishable from model complexity.

#### Indian traded universe

- Point-in-time Nifty IT constituents. The official Nifty IT factsheet currently describes a capped, free-float index of 10 companies; the historical count and members must come from the dated membership source.
- Common equity series only.
- Valid NSE open, close, volume, and identifier on the target session.
- Minimum history and liquidity rules estimated using past data only.

#### Indian context series

- Nifty 50.
- Nifty 500 as a broad-market sensitivity, if source coverage is complete.
- Nifty IT as the primary sector market.
- Nifty Bank.
- Nifty Financial Services.
- Nifty Private Bank, Nifty PSU Bank, and Nifty NBFC where coverage is consistent.
- Nifty Auto.
- Nifty FMCG.
- Nifty Pharma or Healthcare.
- Nifty Metal.
- Nifty Energy or Oil & Gas.
- Nifty Realty.
- Nifty Infrastructure and a capital-goods index where coverage is consistent.
- Nifty Media and Nifty Consumer Durables.
- India VIX.
- USD/INR.

These sector indices are context variables and robustness universes. They do not replace the primary Nifty IT traded universe in the first study.

#### Limited US technology-stock universe

Do not choose today's famous winners and backfill them. At each annual rebalance, define the limited technology universe using information known at the preceding year end:

1. Start from point-in-time S&P 500 members classified in Information Technology.
2. Rank them by lagged free-float or ordinary market capitalization from the approved source.
3. Retain the top 20, subject to at least 252 prior trading sessions.
4. Freeze that set for the following calendar year.

This creates an interpretable “limited US technology” block without hindsight selection. A fixed named list may be reported as a sensitivity only, with survivorship explicitly disclosed.

#### Complete US top-500 universe

- Every point-in-time S&P 500 constituent on the mapped US session.
- Daily adjusted OHLCV and stable security identifier.
- Point-in-time sector classification.
- Membership effective dates.
- Delisting and corporate-action information where the approved source provides it.
- Equal-date universe snapshots so missing stocks cannot silently change feature dimension.

The full universe is represented in two ways: compressed market-state features and direct stock-level lagged returns with shrinkage. These are separate experiments.

#### US broad-market and style proxies

- SPY: US large-cap market.
- QQQ: Nasdaq-oriented growth and technology exposure.
- IWM: US small-cap risk appetite.
- DIA: large-cap industrial sensitivity, optional after redundancy review.
- VIX: US implied volatility.

#### US sector proxies

- XLK: information technology.
- XLF: financials.
- XLV: health care.
- XLE: energy.
- XLI: industrials.
- XLY: consumer discretionary.
- XLP: consumer staples.
- XLB: materials.
- XLU: utilities.

The first feature set excludes XLC and XLRE because their shorter histories would shorten the common sample. They may enter a later block with matched-date comparison. The official State Street sector list confirms the sector ETF identities; market histories still require the licensed or fallback price source described above.

### 3.3 Data-access gates

Before code is written, the researcher must answer these questions:

1. Does NUS provide Bloomberg, Refinitiv, FactSet, WRDS, or another authorized source with historical Nifty IT membership and adjusted Indian OHLCV?
2. If not, can historical Nifty IT constituent membership be licensed from NSE Indices or reconstructed from dated official materials?
3. Does the approved institutional source provide point-in-time S&P 500 membership, US security identifiers, sector classifications, corporate actions, and daily OHLCV?
4. If complete US history is unavailable, will the full-US experiment be replaced by sector ETFs and breadth data rather than a biased current-member backfill?
5. Are Yahoo Finance data rights acceptable for the academic submission and repository policy?
6. Will raw licensed data be excluded from public Git and replaced with retrieval instructions and hashes?

**Stop condition:** if point-in-time Nifty IT membership cannot be obtained, the project must choose one of two narrower claims:

- Trade a fixed, explicitly survivorship-biased cohort of continuously listed Indian technology stocks; or
- Trade a Nifty IT tracking instrument rather than historical constituent stocks.

It must not describe a current-constituent backfill as an unbiased historical Nifty IT strategy. If point-in-time S&P 500 membership is unavailable, the S&P 500 stock-level experiment is blocked independently; the domestic and limited-US experiments may still proceed.

### 3.4 Proposed research dates

The provisional sample is 2010 through 2025 because India VIX and the legacy US sector ETFs have adequate coverage. Dates remain provisional until the constituent and price coverage audit is complete.

| Phase | Provisional dates | Purpose |
|---|---|---|
| Warm-up | 2010–2011 | Long-window feature construction only |
| Initial training | 2012–2016 | Initial scaling and model estimation |
| Screening | 2017–2019 | Feature-block and bounded model comparison |
| Confirmation | 2020–2022 | Confirm families and robustness across a difficult regime |
| Final evaluation | 2023–2025 | One locked evaluation after protocol freeze |

The exact calendar dates will be resolved to NSE sessions. If Indian data for the final phase has already been inspected during project development, it cannot be called untouched. The protocol must disclose prior exposure and designate a later genuinely unobserved period if one exists.

---

## 4. Information timing and leakage contract

### 4.1 Timestamp rule

For every predictor observation $x$, store:

- source observation timestamp;
- source exchange timezone;
- source publication or market-close timestamp;
- first permitted availability timestamp;
- corresponding NSE signal session;
- transformation window;
- raw snapshot identifier.

An observation is eligible only when:

\[
\operatorname{available\_at}(x)<\operatorname{decision\_time}(d).
\]

Strict inequality is preferred at the boundary. If release-time precision is unavailable, delay the variable to the next NSE session.

For the primary protocol, $\operatorname{decision\_time}(d)$ is 08:55 Asia/Kolkata on NSE session $d$. No feature may use information first available at or after that timestamp. The model produces one prediction batch per NSE session; it does not update during pre-open or continuous trading.

### 4.2 US-to-NSE alignment

For NSE session $d$, choose:

\[
u(d)=\max\{u:USCloseTimestamp_u<DecisionTimestamp_d\}.
\]

US predictors for NSE session $d$ are computed through US session $u(d)$. This rule automatically handles:

- US daylight-saving transitions;
- Indian and US holiday mismatches;
- a Monday NSE session following a Friday US session;
- an NSE holiday followed by several available US sessions;
- a US holiday before an open NSE session.

No code may join US and Indian records with `date == date` unless a prior timestamp mapping has already established that equality is correct.

### 4.3 Daily frequency contract

- One signal batch is generated per eligible NSE trading session.
- All primary market predictors use daily bars from completed sessions.
- The prediction target is the same-day NSE open-to-close return.
- Monthly refitting may be used for model estimation, but forecast production remains daily.
- Feature windows such as 5, 20, or 60 refer to completed trading sessions.
- A missing US trading day is resolved through the latest completed-session mapping; it does not create a missing NSE prediction automatically.
- No intraday model update, second signal, or overnight position is part of the primary design.

### 4.4 Indian feature availability

At the decision for NSE session $d$, the following are prohibited:

- $O_{i,d}$, $H_{i,d}$, $L_{i,d}$, $C_{i,d}$, or volume from session $d$;
- India VIX close from session $d$;
- index breadth computed from session $d$;
- corporate actions published after the decision timestamp;
- constituent membership effective after session $d$.

The latest ordinary Indian price information is from NSE session (d-1). Scheduled membership changes known in advance require a documented effective-date policy.

### 4.5 Labels and overlap

The primary open-to-close label has no multi-day overlap. All Nifty IT stocks for the same NSE session form one date cluster. Training, validation, and test splitting must keep the complete date together. Treating same-day constituent returns as independent random rows is prohibited.

---

## 5. Research hypotheses

Each hypothesis has a null, a controlled comparison, and required evidence.

| ID | Hypothesis | Null | Controlled comparison | Evidence required |
|---|---|---|---|---|
| H1 | Completed US technology-stock information improves Nifty IT forecasts | A limited US technology block does not improve matched-date predictive loss or IC beyond Indian information | Same Ridge model: Indian context versus Indian context plus limited US technology stocks | Paired loss difference, daily IC difference, date-block interval |
| H2 | The complete S&P 500 cross-section adds information beyond major US technology stocks | Expanding from the limited technology universe to the full point-in-time S&P 500 produces no matched-date gain | Same estimator and target: limited-US block versus compressed and sparse full-S&P blocks | OOS loss, IC, net returns, uncertainty, feature-selection stability |
| H3 | Nifty 50 and Indian sector states improve Nifty IT stock forecasts | Cross-sectional Nifty IT history is sufficient | Nifty-IT-only block versus Nifty IT plus Nifty 50 and sector-index context | Matched-date prediction and portfolio differences |
| H4 | US-to-Nifty-IT effects are sparse and short-lived | Dense or long-lag specifications perform equally well | Elastic Net/Lasso with 1, 2, and 5-session US stock lags versus dense Ridge | Selected-link count, persistence, sign stability, lag decay |
| H5 | Shrinkage permits useful nonlinear complexity | Higher random-feature complexity does not improve OOS evidence after shrinkage | Fixed information set, RFF complexity × ridge penalty surface | OOS loss, net Sharpe, exposure, seed bands, effective degrees of freedom |
| H6 | Global information helps during high-volatility transmission regimes | Incremental value is constant or absent across regimes | Prespecified US VIX and India VIX regimes without retuning | Interaction and stratified results with adequate counts |
| H7 | Forecast value is not merely technology beta or broad Indian market beta | Results disappear against Nifty IT and Nifty 50 controls | Stock strategy versus Nifty IT, Nifty 50, volatility-managed Nifty IT, and the long-short spread | Net alpha-style decomposition, betas, long-short spread |
| H8 | More features help only when they add information | Mechanical feature proliferation improves equally | Economic information blocks versus random nonlinear expansion | Separate information-complexity and model-complexity ablations |
| H9 | A no-ML conclusion is possible | At least one ML model must win | All models versus historical, AR, Ridge, and simple ranking controls | Baselines remain eligible in every comparison |
| H10 | Policy, calendar, regime, and climate context adds small incremental information | D9/D10 do not improve matched-date results beyond equity-market blocks | D7 versus D9 and D9 versus D10, with identical models and dates | Stable incremental loss/IC, bounded turnover effect, and block-level uncertainty |

The primary paper claim should be H1. H2 is the central feature-information-complexity experiment. H3–H5 explain domestic context, sparsity, and model complexity. The remaining hypotheses are supporting robustness questions.

---

## 6. Experimental comparison matrix

### 6.1 Information-set comparison

Hold the model, training dates, preprocessing, hyperparameters, stocks, target, and costs fixed. Use Ridge as the first controlled estimator.

| Block | Information set | Purpose |
|---|---|---|
| D0 | Intercept, stock identity, calendar, historical mean | Minimal control |
| D1 | D0 plus each target stock's own Indian history | Own-history baseline |
| D2 | D1 plus lagged returns and states of all point-in-time Nifty IT constituents | Indian technology cross-section |
| D3 | D2 plus Nifty IT index, Nifty 50, major Indian sector indices, breadth, India VIX, and USD/INR | Full Indian information baseline |
| D4 | D3 plus the lagged point-in-time top-20 US technology-stock universe and point-in-time US-traded ADRs of Indian technology firms | Limited US technology and direct overnight price-discovery information |
| D5 | D4 plus SPY, QQQ, IWM, XLK, all US sector ETFs, US VIX, and US breadth | US market and sector context |
| D6 | D5 plus compressed full-S&P-500 features: breadth, dispersion, sectors, and training-only principal components | Full-US compressed information |
| D7 | D6 plus stock-level 1, 2, and 5-session returns for every point-in-time S&P 500 member, fitted with sparse shrinkage | Full-US high-dimensional sparse information |
| D8 | Fixed selected economic information set plus random nonlinear features | Representation/model complexity, not new information |
| D9 | D7 plus release-aware Federal Reserve, RBI policy, bank lending-rate, yield, FX, and credit context | Monetary-policy and financing-cost extension |
| D10 | D9 plus calendar seasonality, holidays, scheduled-event proximity, causal regime-shift markers, and optional rainfall anomalies | Minor contextual feature extension, evaluated last as one bounded block |

Primary cross-market comparison: **D3 versus D4**.  
Primary feature-information-complexity comparison: **D4 versus D6 versus D7**.  
Domestic-context comparison: **D2 versus D3**.  
US context comparison: **D4 versus D5**.  
Model-complexity comparison: keep the chosen information set fixed and evaluate **D8**.  
Optional monetary-policy comparison: **D7 versus D9**.  
Optional minor-context comparison: **D9 versus D10**, with no promotion unless the improvement is stable and survives multiple-testing controls.

Every comparison uses the intersection of eligible stock-date rows. A richer feature block cannot win by silently changing the evaluation dates or universe.

### 6.2 Model-family comparison

After the development evidence selects one information block, hold that block constant and compare:

| Model | Role | Main controlled dimension |
|---|---|---|
| Historical stock/sector mean | Naive control | No learned dynamics |
| Previous-return and AR controls | Persistence/reversal control | Short stock lags |
| Ridge | Dense linear reference | Shrinkage strength |
| Elastic Net | Sparse spillover model | Penalty and L1 fraction |
| PCA plus Ridge | Correlated-feature control | Component count |
| Histogram gradient boosting | Bounded nonlinear interactions | Leaves, learning rate, rounds |
| Random Forest/Extra Trees | Bagged nonlinear comparison | Depth and leaf size |
| RFF plus Ridge | Kelly-style complexity experiment | Generated features $P$, shrinkage, seeds |
| One-hidden-layer MLP | Secondary complexity sensitivity | Width, decay, epochs |

The project does not need every fashionable model. Each retained family must test a distinct hypothesis.

### 6.3 Strategy comparison

Use identical forecasts to evaluate:

- Primary long-only top-stock strategy.
- Secondary sector-neutral long-short spread.
- Nifty IT total-return-index buy-and-hold.
- Nifty 50 total-return-index buy-and-hold.
- Session-matched Nifty IT open-to-close return.
- Session-matched Nifty 50 open-to-close return.
- Equal-weight point-in-time Nifty IT constituent return.
- Volatility-managed Nifty IT.
- Investable Nifty IT ETF and Nifty 50 ETF benchmarks over their available histories.
- Simple prior-return ranking strategy.
- Cash.

Forecast ranking and portfolio sizing are separate experimental stages. Do not tune the model and strategy mapping simultaneously on the same outer block.

### 6.4 Three distinct complexity axes

The project must never use “complexity” as one undifferentiated label.

| Axis | Definition | Controlled experiment | Logged measures |
|---|---|---|---|
| Information breadth | How many economically distinct markets and securities are observed | D1 → D2 → D3 → D4 → D6 → D7 | source blocks, securities, raw columns, missingness, matched dates |
| Engineered-feature dimension | How many lags, transformations, aggregates, PCA scores, and interactions are supplied | Within a fixed source universe, add predeclared feature groups | raw $p$, retained $p$, group counts, incremental loss/IC |
| Model flexibility | How many trainable or effective degrees of freedom transform a fixed information set | Ridge penalty, tree structure, RFF $P/T$, or MLP width | parameter count, effective degrees of freedom, $K/T$, $P/T$, train-validation gap |

The primary information-gain curve uses one fixed Ridge estimator across D1–D6. D7 necessarily uses sparse shrinkage because a dense 1,500-variable stock-lag matrix is the hypothesis being tested. The model-complexity study begins only after an economic information block is selected and holds that block constant.

For every transition (D_a\rightarrow D_b), save:

- incremental matched-date OOS loss;
- incremental daily rank IC;
- incremental net return and turnover;
- incremental source and feature count;
- incremental runtime and memory;
- block-bootstrap interval for the difference;
- performance by year and volatility state.

This produces a real information-gain curve rather than a leaderboard of unrelated models.

---

## 7. Feature design

### 7.1 Indian stock features

All rolling windows end at NSE session (d-1).

| Group | Candidate features | Initial windows |
|---|---|---|
| Returns | close-to-close log-return lags; prior open-to-close; prior overnight gap | 1, 2, 3, 5 sessions |
| Momentum | cumulative total return | 5, 10, 20, 60, 120 sessions |
| Trend | price/SMA, short/long SMA ratio, EMA ratio, normalized slope | 10, 20, 50, 200 sessions |
| Volatility | realized volatility, downside deviation, EWMA volatility | 5, 20, 60 sessions |
| Tail state | rolling skewness, excess kurtosis, largest loss | 20, 60 sessions |
| Drawdown | drawdown magnitude, duration, recovery fraction | 60, 252 sessions |
| Liquidity | log turnover, volume/average, Amihud proxy, zero-volume flag | 20, 60 sessions |
| Relative performance | stock minus Nifty IT; stock minus Nifty 50; residual momentum | 5, 20, 60 sessions |
| Risk loading | trailing beta to Nifty IT, Nifty 50, QQQ, and XLK; residual volatility | 60, 120 sessions |
| Technical state | RSI, Bollinger z-score, MACD scaled by price | standard bounded definitions |

Do not create dozens of adjacent windows merely to increase dimension. The first stock block should contain approximately 30–50 economically distinct variables.

### 7.2 Indian market and sector features

The domestic context block includes:

- Nifty IT returns, momentum, drawdown, and realized volatility.
- Nifty 50 returns, momentum, realized volatility, and Nifty-IT-minus-Nifty-50 relative return.
- India VIX level, 5-session change, and India-VIX/realized-volatility ratio.
- Nifty Bank and Nifty Financial Services states.
- Nifty Auto, FMCG, Pharma/Healthcare, Metal, Energy/Oil & Gas, Realty, Infrastructure/Capital Goods, Media, and Consumer Durables states.
- Cross-sector breadth: fraction of sector indices rising on session (d-1).
- Cross-sector return dispersion, downside concentration, and leadership concentration.
- Nifty IT constituent breadth, dispersion, and equal-weight-minus-cap-weight return.
- USD/INR change where the release timestamp permits it.
- Month-end, weekday, expiry-week, and exchange-holiday proximity.

Other sector indices are contextual signals. Their constituent stocks are not traded in the primary strategy. Later robustness experiments may repeat the design for another sector, but such repetitions remain separate trials.

### 7.3 Limited US technology-stock features

All US windows end at the mapped completed US session $u(d)$. For each member of the predeclared annual top-20 US technology universe, construct:

- 1, 2, and 5-session close-to-close return lags;
- latest open-to-close return and overnight gap;
- 5 and 20-session momentum;
- 5 and 20-session realized volatility;
- standardized one-session return shock;
- drawdown and distance from 20-session trend;
- volume surprise and Amihud proxy where fields are consistent;
- stock return minus XLK and stock return minus SPY;
- point-in-time industry subgroup.

Aggregate limited-universe features include equal-weight return, fraction positive, return dispersion, top-five concentration, and first few training-only principal components. Direct stock-level lags and aggregated features must be evaluated as separate sub-blocks.

#### US-traded Indian technology ADRs

ADRs provide a direct overnight price-discovery bridge because their US session finishes before the next NSE decision. Include an ADR only while it was actively listed and map it to the corresponding Indian security using point-in-time depositary ratios and corporate-action adjustments.

- Latest completed ADR open-to-close, overnight, and close-to-close returns.
- ADR volume and dollar-volume surprises relative to 20-session history.
- ADR return relative to QQQ, XLK, and the limited-US-technology basket.
- ADR return relative to the corresponding stock's preceding NSE-session return.
- Currency-adjusted ADR-versus-local-price basis, only when depositary ratios and timestamps are reliable.
- Observation age, stale-price, suspension, and active-listing indicators.

The ADR basis is a secondary signal because transaction costs, depositary mechanics, currency conversion, and nonsynchronous clocks can create apparent deviations. The primary ADR feature is the latest completed US return, not an assumed arbitrage profit.

### 7.4 Full point-in-time S&P 500 features

The full S&P 500 block is deliberately high dimensional. It has two representations.

#### D6: compressed full-market representation

- Equal-weight and capitalization-weighted S&P 500 returns.
- Fraction positive, fraction above 20-day average, and fraction at 20-day highs/lows.
- Cross-sectional mean, median, dispersion, skewness, and tail quantiles.
- Sector breadth, sector return, and sector dispersion.
- Top/bottom return concentration.
- Training-only PCA scores from the point-in-time stock-return matrix.
- Missingness and constituent-turnover indicators.

#### D7: direct sparse stock-level representation

- 1, 2, and 5-session lagged returns for every point-in-time S&P 500 member.
- Optional standardized return shock and 20-session momentum only after the lag-only experiment.
- Stable security-ID columns, with absent nonmembers represented by an explicit structural-missing convention.
- Lasso/Elastic-Net shrinkage so most US stock-to-Nifty-IT links remain zero.

At roughly 500 stocks and three lags, the return block contains about 1,500 candidate variables before interactions. This dimension is the intended Chinco-style sparse-information experiment. It must not be combined immediately with a large technical-indicator grid.

### 7.5 US market and sector context

- SPY open-to-close, overnight, and close-to-close returns.
- QQQ and IWM returns relative to SPY.
- XLK return, volatility, breadth proxy, and XLK-minus-SPY return.
- XLF, XLV, XLE, XLI, XLY, XLP, XLB, and XLU returns.
- US market momentum over 2, 5, 20, and 60 sessions.
- US realized volatility over 5 and 20 sessions.
- VIX level and 1, 5, and 20-session changes.
- VIX relative to SPY realized volatility.
- US market drawdown and distance from trend.
- Cross-sector breadth and dispersion.

### 7.6 Cross-market interactions

For Indian technology stock $i$:

\[
CrossShock_{i,d}
=
z\!\left(r^{\mathrm{US\,Tech}}_{u(d)}\right)
\times
\widehat\beta^{US\rightarrow India}_{i,d-1}.
\]

Candidate features:

- XLK or QQQ shock × trailing Nifty IT stock sensitivity.
- US technology-stock breadth × India VIX state.
- US technology dispersion × Nifty IT dispersion.
- US software subgroup return × Indian software-services indicator.
- US hardware/semiconductor subgroup return × relevant Indian exposure classification, if historically supportable.
- US tech minus SPY × Nifty IT minus Nifty 50.
- USD/INR movement × US technology return.
- Matched Indian-technology ADR shock × corresponding Nifty IT constituent.
- Selected S&P 500 stock shock × Nifty IT constituent, only through sparse shrinkage.

Trailing sensitivities must be fitted only on data available before the signal. Firm classifications must be point-in-time or treated as static with a disclosed limitation.

### 7.7 Sparse predictor pool inspired by Chinco et al.

The principal sparse pool contains:

- approximately 1,500 S&P 500 return-lag candidates;
- limited-US-technology return shocks;
- Nifty IT cross-stock lags;
- Indian sector-index lags;
- a small, predeclared volatility-state interaction block.

Elastic Net or Lasso selects active links separately within each monthly refit. Report the number of nonzero predictors, their lifespan, source sectors, signs, and stability. Compare stock-level D7 against compressed D6 to determine whether detailed cross-sectional information adds value beyond aggregate breadth and principal components.

### 7.8 Federal Reserve, US rate, and credit features

Use levels sparingly because policy-rate series are persistent. Changes, relative positions, and time since decisions are usually more informative.

- Effective federal funds rate.
- Target federal funds lower bound, upper bound, midpoint, and range width.
- Latest target change in basis points.
- Direction of the latest change: tightening, unchanged, or easing.
- Sessions and calendar days since the latest effective rate change.
- Days until the next scheduled FOMC decision, using only the calendar known at the signal time.
- FOMC decision-day and first-NSE-session-after-decision indicators.
- Two-year and ten-year Treasury yields and their 1, 5, and 20-session changes.
- 10-year minus 2-year and 10-year minus 3-month term spreads.
- High-yield and investment-grade credit spreads where point-in-time coverage is available.
- Fed-rate midpoint minus US inflation, only with release-aware inflation vintages.
- Rate-change × QQQ/XLK return and rate-change × US-tech-duration proxy interactions.

Actual policy outcomes enter only after the Federal Reserve's official release time. A “surprise” feature requires a historically archived market-expectation source. Without that source, use the realized change after publication and do not label it a surprise.

### 7.9 RBI policy, liquidity, and Indian lending-rate features

“RBI loan rates” must be separated into policy instruments and observed bank lending rates.

#### RBI policy and liquidity instruments

- Policy repo rate.
- Standing Deposit Facility rate.
- Reverse repo rate where historically applicable.
- Marginal Standing Facility rate.
- Bank rate.
- Cash Reserve Ratio and Statutory Liquidity Ratio.
- Latest change in basis points and direction.
- Days since the latest effective change.
- Days until the next scheduled Monetary Policy Committee decision.
- First NSE session after an RBI policy announcement.

#### Bank lending conditions

- Weighted average lending rate on fresh rupee loans.
- Weighted average lending rate on outstanding rupee loans.
- One-year median Marginal Cost of Funds based Lending Rate, if a consistent official history and publication date are available.
- Lending-rate minus repo-rate spread.
- Month-over-month and three-month lending-rate changes.
- Age in days of the currently available lending-rate observation.

Bank lending rates are typically monthly and published with a lag. Carry the latest released observation forward with an age field. Never assign a monthly value to every day of its reference month if it was published later.

#### Cross-country monetary features

- RBI repo minus Fed target midpoint.
- Change in the India-US policy-rate differential.
- Indian 10-year yield minus US 10-year yield, if point-in-time Indian yield coverage is available.
- Joint tightening/easing regime.
- Policy divergence indicator.
- Policy differential × USD/INR change.
- Policy differential × Nifty-IT-minus-Nifty-50 return.

### 7.10 Calendar, holiday, seasonal, and scheduled-event features

These features are known or computable before 08:55 and therefore may enter the predictive model.

#### Exchange and holiday structure

- NSE weekday, month, quarter, and Indian financial-year position.
- Sessions to and from an NSE holiday.
- Sessions to and from a US market holiday.
- Indicator that the latest US observation is more than one calendar day old.
- First NSE session after a US holiday.
- First NSE session after an Indian holiday while the US traded.
- Month-end, quarter-end, calendar-year-end, and Indian financial-year-end.
- Derivatives expiry week and expiry-day indicator where the calendar is known.
- Diwali/Muhurat and other special-session indicator using the dated NSE calendar.

#### Scheduled economic and company events

- Days until and since scheduled FOMC decisions.
- Days until and since scheduled RBI MPC decisions.
- Days until and since scheduled US CPI, payroll, and GDP releases when an official historical calendar is available.
- Nifty IT earnings-season indicator.
- Days until a constituent's scheduled earnings date only when the date was publicly known then.
- First NSE session after a Nifty IT company's results release.

The actual earnings or macro value is available only after its timestamp. Rescheduled events require the calendar version known on that historical date.

#### Deterministic seasonality

- Weekday sine/cosine or categorical encoding.
- Month and quarter indicators.
- Day-of-year Fourier harmonics.
- Indian financial-year phase.
- Monsoon-season indicator.
- US earnings-season and Indian earnings-season indicators.

Calendar features should be evaluated as one small block. A large set of festival dummy variables with very few observations will overfit.

### 7.11 Global events and event markers

Maintain two explicitly different tables:

1. **Predictive scheduled events:** known before the decision, such as policy meetings, economic releases, index rebalances, and holidays.
2. **Retrospective global-event annotations:** crises, wars, pandemics, bank failures, cyber incidents, and other unscheduled events used only for interpretation and regime analysis.

An unscheduled event may become a predictor only from its first verified public timestamp onward. Permitted causal markers include:

- days since first public announcement;
- first NSE session after announcement;
- post-event day 1–5 indicator;
- event-active flag defined by contemporaneous public status, not the eventual end date.

Prohibited features include future crisis-end dates, labels spanning the complete eventual event, and hand-picked markers created after inspecting strategy losses. Event studies should show −5 to +5 sessions descriptively without claiming causality.

### 7.12 Rainfall and climate context

Rainfall has a weak direct mechanism for export-oriented Nifty IT firms, so it is a minor D10 sensitivity rather than a core predictor. Its possible channel is broad Indian demand, power/infrastructure conditions, inflation, or macro risk appetite.

Candidate features from official IMD data:

- all-India daily rainfall anomaly relative to historical day-of-year normal;
- cumulative monsoon rainfall anomaly available to date;
- fraction of meteorological subdivisions in deficit or excess;
- 5 and 20-day rainfall totals and anomalies;
- extreme-rainfall-area fraction;
- monsoon onset or withdrawal state only from the official announcement date;
- rainfall anomaly × Indian sector breadth;
- rainfall anomaly × Nifty IT minus Nifty 50 return.

The release timestamp and later revisions must be established. If only final cleaned seasonal totals are available, they may be used for retrospective description but not daily prediction. Rainfall should be removed if it shortens the common sample materially or adds unstable complexity without evidence.

#### Other optional minor-context features

These belong only in D10, enter as predeclared groups, and must never displace the primary D3–D7 comparisons:

- Broad US-dollar-index change, complementing USD/INR.
- Oil, gold, and copper returns as compact global growth, inflation, and risk-state proxies.
- Emerging-market ETF return and volatility, using the latest completed US session.
- Returns of major European and Asian indices whose relevant session had completed by 08:55 IST.
- Global month-end and quarter-end rebalance indicators.
- Nifty and S&P index-reconstitution effective-date indicators known from prior public announcements.
- ADR stale-price and cross-listing-dislocation indicators.

Each group requires an economic channel, source timestamp, missingness rule, and ablation test. These are low-priority controls, not a license to create an unbounded macro-feature catalogue.

### 7.13 Causal trend-shift and regime markers

Trend-shift features must be computable recursively without full-sample break detection.

#### Price and return shifts

- Price crossing above/below 20, 50, or 200-session moving averages.
- 5/20 and 20/60-session momentum sign changes.
- Fast-minus-slow EWMA return.
- Momentum acceleration: recent 5-session momentum minus prior 5-session momentum.
- Drawdown entry, recovery, and new-high indicators.

#### Volatility and correlation shifts

- 5/20 and 20/60 realized-volatility ratios.
- EWMA volatility minus slow volatility.
- VIX or India VIX crossing a training-derived percentile.
- Change in trailing QQQ–Nifty IT or XLK–Nifty IT correlation.
- Change in US-tech-to-Indian-stock rolling beta.
- Cross-sectional dispersion jump relative to its trailing distribution.

#### Online statistical shifts

- One-sided and two-sided CUSUM using thresholds estimated only on training data.
- Page-Hinkley change flag as a sensitivity.
- Online Bayesian change-point probability only if the prior and hazard are frozen before evaluation.
- Rolling residual mean or variance break from the baseline model.

Full-sample Bai-Perron breaks, retrospective HMM states, or regimes fitted using future observations may be displayed as EDA annotations but cannot enter predictive features. If an HMM is tested, it must be refitted inside each training window and filtered forward rather than smoothed with future data.

### 7.14 Feature-engineering transformation library

Feature engineering is organized into predeclared families. Each family receives a separate ablation before combinations are promoted.

#### Rolling and moving-window features

- Rolling mean, median, standard deviation, downside deviation, and median absolute deviation.
- Rolling skewness, excess kurtosis, quantiles, minimum, maximum, and hit rate.
- Rolling cumulative return, drawdown, recovery, beta, correlation, and residual volatility.
- Rolling breadth, dispersion, concentration, and principal components.
- Windows 2, 5, 10, 20, 60, 120, and 252 only where economically appropriate; every feature does not receive every window.

#### Moving averages and exponentially weighted features

- Price/SMA and short-SMA/long-SMA ratios.
- EMA differences and MACD-style normalized differences.
- EWMA return, volatility, covariance, and beta.
- Half-lives 5, 20, and 60 sessions for selected variables.
- Moving-average slope and change in slope.

#### Deterministic Fourier features

For a periodic variable $q_d\in[0,1)$, construct:

\[
\sin(2\pi kq_d),\qquad \cos(2\pi kq_d),
\]

with predeclared low-order harmonics. Use:

- weekday cycle: normally categorical or first harmonic;
- annual/day-of-year cycle: $k\in\{1,2,3\}$;
- month or quarter cycle: first and second harmonics;
- Indian financial-year phase: first harmonic;
- optional monsoon phase: first harmonic within the defined season.

Deterministic calendar Fourier terms model seasonality. They are different from random Fourier features used to approximate nonlinear kernels.

#### Random Fourier features

After the economic information set is fixed, standardize training inputs and generate nested random Fourier maps:

\[
z_j(x)=\sqrt{2}\cos(\omega_j^\top x+b_j).
\]

Vary generated dimension through the predeclared $P/T$ grid and apply ridge shrinkage. Keep kernel bandwidth fixed in the primary study and use multiple map seeds as replications.

#### Higher-order polynomial and interaction features

Use degree-two transformations only on a small core set, never blindly on the 1,500-variable D7 matrix:

- squared standardized shock and volatility terms;
- rate-change × technology return;
- VIX × US-tech breadth;
- India VIX × Nifty IT dispersion;
- USD/INR × US-tech return;
- Nifty-IT momentum × Nifty-50 regime;
- US-tech shock × trailing Indian-stock beta;
- policy divergence × growth-versus-value spread.

Degree-three or higher raw polynomial expansions are excluded from the primary study. RFF or tree models provide controlled nonlinear flexibility without explicitly materializing every polynomial.

#### Cross-sectional transformations

- Within-date rank and percentile.
- Within-date robust z-score.
- Stock return relative to Nifty IT and equal-weight peers.
- Sector-neutral or market-neutral residual.
- Breadth, dispersion, top-bottom spread, and concentration.
- Winsorization thresholds learned from training dates only.

#### Compression and selection

- Training-only PCA for full-S&P returns.
- Sparse PCA only as a sensitivity.
- Elastic-Net coefficient paths.
- Group ablation by source, country, sector, lag, and transformation family.
- Stability selection across temporal folds.
- Remove zero-variance and near-duplicate columns inside each training fit.

Feature count is capped at every stage. A proposed transformation must state its economic purpose, raw inputs, availability, expected dimension, and ablation group before implementation.

### 7.15 Feature registry requirements

Every feature record must include:

- unique feature name;
- economic group;
- exact formula;
- units;
- raw fields and source;
- lookback window;
- observation timestamp;
- availability timestamp;
- missingness policy;
- normalization policy;
- first eligible date;
- whether it is stock, sector, market, or global level;
- permitted experimental blocks.

---

## 8. Data cleaning and feature processing

### 8.1 Raw-data validation

For each source and symbol:

- verify schema and data types;
- validate exchange timezone;
- reject duplicate symbol-session rows with conflicting values;
- verify OHLC inequalities;
- flag nonpositive prices or volumes;
- reconcile official session calendars;
- quantify missing sessions;
- record symbol and ISIN changes;
- inspect corporate-action dates;
- compare a sample against a second permitted source;
- hash every raw file.

### 8.2 Corporate actions

Use one consistent adjustment factor across open, high, low, and close. Mixing a raw open with an adjusted previous close creates artificial overnight returns. Preserve raw and adjusted columns. Validate split and dividend dates with numerical before/after examples.

The target open-to-close return is usually invariant to a same-day multiplicative adjustment when both prices use the same factor, but the feature history and overnight gaps are not safe unless all fields are consistent.

### 8.3 Point-in-time universe

Create separate point-in-time membership tables for Nifty IT and the S&P 500:

```text
universe | effective_start | effective_end | security_id | symbol | sector | source_notice
```

Membership changes become effective only on the documented date. Do not use future membership to remove a company before it leaves the index.

### 8.4 Missing values

- Missing target open or close: stock-date row is ineligible.
- Missing Nifty IT membership: blocking error for the traded universe.
- Missing S&P 500 membership: blocking error for D6/D7, but it does not block the domestic or limited-US experiments.
- Missing traded stock feature: retain null until training-only preprocessing.
- Missing external market observation due to holiday: use the latest completed source session through timestamp mapping, not an arbitrary price forward fill.
- Missing newly listed stock history: retain with missingness indicators if minimum-history rule passes.
- Model imputation: fit medians on eligible training data only.

Lower-frequency policy, lending-rate, and climate observations use an as-of join on `available_at`, not their reference period. Carry the latest released value forward and include observation age. Revised values create a new vintage from their revision timestamp; they do not overwrite the historical information state.

### 8.5 Scaling and outliers

- Fit time-series scaling on training rows only.
- Permit cross-sectional rank or z-score features computed across the eligible stocks at the signal timestamp.
- Clip predictor outliers only by thresholds estimated on training data.
- Do not clip the primary return target.
- Run Huber or robust-scaling sensitivity without deleting crisis sessions.
- Log both pre- and post-transformation quantiles.

### 8.6 Panel weighting

Each date contains the point-in-time Nifty IT cross-section, currently around 10 constituents but not assumed constant historically. Primary model fitting should give every date equal total weight:

\[
w_{i,d}=\frac{1}{N_d},
\]

where $N_d$ is the number of eligible stocks on date $d$. This prevents dates with more valid stocks from receiving greater influence. Liquidity-weighted fitting is a secondary sensitivity.

---

## 9. Modeling design

### 9.1 Market layer

Target:

\[
r^{IT}_{d}=\frac{NiftyITClose_d}{NiftyITOpen_d}-1.
\]

Models:

- historical mean;
- AR/Ridge domestic baseline;
- Ridge evaluated sequentially across D1–D7;
- Elastic Net;
- histogram gradient boosting;
- RFF-Ridge complexity surface;
- small MLP sensitivity.

The Kelly-style complexity experiment belongs here because the independent observation count is clearly the number of training dates.

### 9.2 Cross-sectional layer

Target:

\[
r^{REL}_{i,d}=r^{OC}_{i,d}-r^{IT}_{d}.
\]

Models:

- stock/sector historical mean;
- panel Ridge;
- Elastic Net sparse spillover model;
- histogram gradient boosting;
- shallow Random Forest or Extra Trees;
- optional pooled MLP only after simpler models.

Stock and sector identity may enter as one-hot encodings or regularized effects. A model must not create a separate unconstrained parameter set for every stock without logging the resulting complexity.

### 9.3 Sparse-penalty design

For Lasso/Elastic Net, define the penalty relative to the training sample:

\[
\lambda_{max}
=
\frac{\|X^\top y\|_{\infty}}{T}.
\]

Test fractions such as:

\[
\lambda/\lambda_{max}
\in
\{1,0.3,0.1,0.03,0.01,0.003,0.001\}.
\]

This avoids arbitrary raw penalty values that accidentally make every forecast zero. Elastic-Net L1 fractions may be limited to \(\{0.2,0.5,0.8,1.0\}\). Choose penalties through chronological inner validation.

### 9.4 Random-feature complexity design

Use the development-selected economic information block, held fixed across every complexity cell. Generate deterministic nested random Fourier feature banks and fit Ridge:

\[
\widehat\beta
=
\arg\min_\beta
\left[
\frac{1}{T}\|y-Z\beta\|_2^2
+
\lambda\|\beta\|_2^2
\right].
\]

Primary complexity axis:

\[
c=P/T,
\]

with:

\[
c\in\{0.1,0.25,0.5,0.75,1,1.5,2,5,10\}.
\]

Use rolling windows of 504 and 1,260 NSE sessions. Use at least three feature-map seeds and treat seeds as replications rather than candidates. Test a predeclared ridge grid after generated-column normalization. Log:

- economic input dimension;
- generated dimension $P$;
- training dates $T$;
- coefficient count;
- $P/T$;
- effective ridge degrees of freedom;
- matrix rank;
- train, validation, and OOS loss;
- solver and condition diagnostics;
- runtime and memory.

Do not mix tree leaf counts, RFF coefficients, and neural weights on one unlabeled complexity axis.

### 9.5 Neural complexity sensitivity

A one-hidden-layer MLP with $d$ inputs and width $h$ has approximately:

\[
K=(d+2)h+1
\]

parameters. Use widths 8, 32, and 128; two weight-decay settings; three seeds; and checkpoints at 50, 100, 200, and 400 epochs. Choose stopping using a chronological validation tail. Do not use a random validation split.

### 9.6 Hyperparameter hierarchy

Tune in this order:

1. Fix data and information block.
2. Select training-window policy.
3. Select preprocessing using training evidence.
4. Tune family-specific regularization or structure.
5. Lock the model.
6. Tune one bounded strategy mapping on past-only predictions.
7. Open the next outer block.

Avoid a global Cartesian search over every feature, model, and portfolio parameter.

---

## 10. Temporal validation and leakage control

### 10.1 Outer walk-forward design

Use monthly outer evaluation blocks:

```text
rolling/expanding training dates
        ↓
past-only inner folds
        ↓
lock preprocessing and hyperparameters
        ↓
predict every eligible stock in the next month
        ↓
advance one month and repeat
```

All stock rows for one NSE session stay together.

### 10.2 Inner validation

Use two or three forward folds inside the eligible training window. The final inner validation segment must precede the outer month. Preprocessing, feature selection, PCA, imputation, scaling, penalty selection, and early stopping are re-fitted within each inner fold.

### 10.3 Purging and embargo

The one-session intraday label has little overlap, but apply at least a one-session purge at boundaries to protect against timing mistakes and later multi-day extensions. Any feature using a 20-session window does not require a 20-session label embargo; it requires correct historical feature construction.

### 10.4 Fixed versus expanding windows

- Primary stock-selection window: rolling 1,260 sessions.
- Sensitivity stock window: rolling 504 sessions.
- Reference: expanding history.
- Complexity experiment: fixed $T$ windows so $P/T$ is comparable.

### 10.5 Final protocol freeze

Before final evaluation, save an immutable freeze containing:

- raw snapshot hashes;
- membership-source hash;
- source licenses and retrieval timestamps;
- exact dates;
- feature registry hash;
- selected information block;
- model and hyperparameters;
- training window;
- strategy rule;
- transaction-cost assumptions;
- random seeds;
- code revision;
- selection evidence.

The final period is evaluated once. If it has already been inspected, label the exercise retrospective.

---

## 11. Trading strategy

### 11.1 Primary long-only strategy

For each NSE session:

1. Compute market forecast \(\widehat r^{MKT}_d\).
2. Compute each stock's relative forecast \(\widehat r^{REL}_{i,d}\).
3. Form total expected returns.
4. Require the market forecast or stock forecast to clear a predeclared hurdle.
5. Rank eligible stocks.
6. Buy the top 30% of eligible Nifty IT constituents, with a minimum of two and a default of three names when ten constituents are eligible.
7. Weight by capped inverse trailing volatility.
8. Enforce stock and sector limits.
9. Enter at the official open plus slippage.
10. Exit at the official close minus slippage.

Provisional constraints:

- maximum 40% per stock, with weights renormalized across the small Nifty IT universe;
- no sector cap because every traded stock belongs to the technology index;
- optional software-services subgroup cap if the historical classification is reliable;
- gross exposure from 0% to 100%;
- no overnight holdings;
- no leverage in the primary strategy;
- stocks failing liquidity or price checks receive zero weight.

Weights:

\[
\widetilde w_{i,d}
=
\frac{\max(\widehat r_{i,d}-h,0)}
{\widehat\sigma_{i,d}},
\]

followed by caps and normalization. The hurdle $h$ must include the estimated round-trip cost and must be chosen from development data only.

### 11.2 Secondary long-short strategy

- Long the top 30% and short the bottom 30% of eligible Nifty IT constituents.
- Neutralize gross long and short exposure; a software-services subgroup constraint is optional if classifications support it.
- Equal long and short gross exposure.
- Close every position intraday.

This strategy tests cross-sectional ranking more directly but requires a separate operational analysis of Indian intraday shorting, security availability, auction risk, margin, and costs. It is secondary research evidence.

### 11.3 Transaction costs

The cost engine must itemize rather than assume one generic number:

- bid-ask spread or opening slippage;
- brokerage;
- exchange and clearing charges;
- Securities Transaction Tax;
- GST on applicable fees;
- stamp duty;
- regulatory charges;
- adverse movement at the closing execution;
- short-side costs where applicable.

Exact rates can change. Verify the applicable schedule before implementation and state whether current or historically varying rates are used. Report at least low, base, and high cost scenarios.

---

## 12. Exploratory data analysis

EDA must lead to a decision. Compute broadly, retain underlying tables, and include only interpretable figures in the report.

| Question | Diagnostic | Decision informed |
|---|---|---|
| Is the universe historically correct? | Membership count and changes by effective date | Block modeling if membership is invalid |
| Are OHLCV fields reliable? | Missingness raster, OHLC violations, action panels | Cleaning and exclusions |
| Does US information precede NSE targets correctly? | Timestamp-alignment examples around holidays and DST | Alignment contract |
| Are tails or jumps driving results? | ECDF, Q–Q, extreme-day table, robust-scale sensitivity | Robust loss/scaling |
| Is there broad US-tech-to-Nifty-IT lead-lag correlation? | Lagged QQQ/XLK/US-tech versus Nifty IT cross-correlation with intervals | Lag pool |
| Does the full S&P 500 add information? | D4/D6/D7 matched-date IC and loss panels | Compression versus sparse stock-level design |
| Which US stocks enter the sparse signal? | Selection-frequency network grouped by US sector and Indian target | Economic interpretation and instability warning |
| Are effects short-lived? | IC or regression coefficient by lag 1–10 | Sparse lag design |
| Do policy changes alter transmission? | Fed/RBI decision and rate-differential event panels | D9 promotion decision |
| Do holidays and scheduled events change behavior? | Holiday/event means with counts and block intervals | Bounded D10 calendar block |
| Are detected trend shifts causal in time? | Online-marker activation around later returns | Retain or reject CUSUM/regime features |
| Does rainfall add anything beyond broad Indian state? | Monsoon/rainfall anomaly ablation on matched dates | Retain only as minor context or remove |
| Are features redundant? | Clustered representative correlation map | Block reduction/PCA |
| Does predictive strength drift? | Rolling daily rank IC by feature group | Rolling versus expanding window |
| Are results concentrated in crises? | Year/regime panels with observations | Stability and limitations |
| Does the portfolio trade enough? | Forecast distribution, active-day strip, turnover | Hurdle and activity gate |
| Does complexity help? | $P/T\times\lambda$ surfaces and seed bands | Complexity conclusion |

Event labels such as the pandemic, rate shocks, or geopolitical crises are retrospective annotations unless they were scheduled and known at the signal time. They may explain co-movement descriptively but must not become predictive features through future period labels.

---

## 13. Evaluation framework

### 13.1 Prediction metrics

#### Market layer

- MSE and MAE.
- OOS \(R^2\) versus historical mean and domestic Ridge.
- Directional accuracy.
- Forecast calibration.
- Loss by year and volatility regime.

#### Cross-sectional layer

- Daily Pearson information coefficient.
- Daily Spearman rank IC.
- Mean and median IC.
- IC information ratio using date-level series.
- Top-minus-bottom realized return.
- Cross-sectional MSE and MAE with equal date weighting.
- Decile calibration.
- Metrics by Nifty IT constituent, US information block, and year.

### 13.2 Portfolio metrics

- Net annualized arithmetic return.
- CAGR.
- Annualized volatility.
- Sharpe and Sortino ratios.
- Maximum drawdown and recovery duration.
- Daily hit rate.
- Average and maximum gross exposure.
- Average number of holdings.
- Turnover and holding duration.
- Total and annualized transaction costs.
- Active sessions and completed round trips.
- Nifty IT beta, Nifty 50 beta, and constituent concentration.
- Capacity proxy based on turnover relative to traded value.

### 13.3 Fair benchmarks

- Cash under the declared cash-return convention.
- Nifty IT total-return-index buy-and-hold as the primary opportunity-set benchmark.
- Nifty 50 total-return-index buy-and-hold as the broad Indian-market benchmark.
- Nifty IT and Nifty 50 open-to-close returns as execution-horizon-matched benchmarks.
- Volatility-managed Nifty IT.
- Equal-weight eligible point-in-time Nifty IT constituents.
- ITBEES or another liquid Nifty IT tracking ETF and NIFTYBEES over matched available dates, after liquidity and tracking-error review.
- India-only Ridge strategy.
- Previous-return ranking strategy.
- AR market timing.

The central economic comparisons are D3 versus D4 for limited US technology information and D4 versus D6 versus D7 for the information gain from the full S&P 500 cross-section. Full close-to-close buy-and-hold benchmarks and intraday open-to-close benchmarks must be reported separately because the strategy holds cash overnight.

### 13.4 Inference

- Paired date-level loss differences.
- Moving-block bootstrap using shared dates.
- Block lengths 10, 20, and 60 sessions.
- HAC standard errors for mean loss or alpha-style decompositions.
- Seed dispersion reported separately from date-sampling uncertainty.
- Multiple-testing registry containing every completed and failed candidate.
- Reality-check or SPA-style correction before making broad superiority claims.

The bootstrap unit is the NSE date, retaining the full cross-section within each sampled date block.

### 13.5 Practical validity gates

A strategy remains in tables but receives a warning if it has:

- fewer than 30 active development sessions;
- fewer than 10 completed round trips;
- zero return variance;
- incomplete prediction coverage;
- unstable results across feature-map seeds;
- performance concentrated in one year or sector;
- high turnover that becomes negative under base costs.

These thresholds are practical warnings, not statistical significance tests.

---

## 14. Interpretation and explainability

### 14.1 Required explanations

- Ridge and Elastic-Net standardized coefficient paths.
- Sparse-link selection frequency by refit and year.
- Grouped permutation importance on OOS dates.
- TreeSHAP for shortlisted tree models, using background observations strictly before each explained outer block.
- Feature-group importance rather than isolated correlated variables.
- Importance drift by year and volatility regime.
- Market-layer versus stock-selection contribution to portfolio return.

### 14.2 Interpretation limits

- Feature importance does not prove causality.
- A US-sector coefficient may proxy for global risk rather than direct sector transmission.
- Tree impurity importance is biased toward flexible or high-cardinality predictors.
- SHAP allocates model output under a dependence convention; it does not identify an economic shock.
- LIME is not primary because unconstrained perturbations can create implausible combinations of correlated market lags.

---

## 15. Compute and reproducibility strategy

### 15.1 Staged compute plan

| Stage | Work | Budget intent | Promotion rule |
|---|---|---:|---|
| Smoke | One month, few stocks, two models | Minutes | Timing, schema, and accounting pass |
| Pilot | One year, all stocks, small grids | Under 30 minutes | Memory and runtime measured |
| Information ablation | D0–D6 with fixed Ridge and D7 with sparse shrinkage | Moderate | Measure domestic, limited-US, compressed-S&P, and stock-level-S&P information gain |
| Sparse study | Elastic Net penalty/lag grid | Moderate | Links and performance stable across folds |
| Model screen | Bounded families on D4 | 1–2 hours | Distinct families only |
| Complexity study | RFF $P/T\times\lambda$, seeds | 2–5 hours | Complete cells, no interim stopping by returns |
| Confirmation | Shortlisted families | 1–2 hours | Baseline and activity gates reviewed |
| Final | Frozen protocol once | Fixed | No further selection |

### 15.2 Engineering requirements

- Plan-only mode before every expensive run.
- Content-addressed run IDs.
- Atomic monthly checkpoints.
- Resume without refitting completed cells.
- Progress bar with stage, completed jobs, recent comparable-job ETA, and memory.
- One large model process at a time initially.
- Deterministic seeds.
- Training dependency fingerprint separate from report code fingerprint.
- Complete environment and package versions.
- Trial registry with failed and inactive candidates.
- Immutable raw and processed manifests.
- No API credentials in Git.

### 15.3 Complexity accounting

For panel models, report:

- trainable parameters / stock-date rows;
- trainable parameters / independent dates;
- effective degrees of freedom / dates;
- observations per date;
- number of stocks and sectors;
- feature count before and after encoding.

This avoids overstating sample size by treating correlated same-day returns as independent.

---

## 16. Proposed repository design

This section specifies intended artifacts only. It does not authorize their creation yet.

```text
configs/
  cross_market_protocol.yaml
  cross_market_sources.yaml
  cross_market_universe.yaml
  cross_market_sector_map.yaml
  cross_market_features.yaml
  cross_market_models.yaml
  cross_market_costs.yaml

data/raw/
  nse_bhavcopy/<snapshot_id>/
  nse_indices/<snapshot_id>/
  nifty_membership/<snapshot_id>/
  us_market/<snapshot_id>/
  cboe/<snapshot_id>/
  macro/<snapshot_id>/

data/processed/
  security_master_<id>/
  cross_market_sessions_<id>/
  nse_panel_<id>/
  cross_market_features_<id>/

artifacts/
  data_audits/
  timing_audits/
  eda/
  runs/
  freezes/
  research/

src/quantfin/
  cross_market_data/
  cross_market_alignment.py
  cross_market_features.py
  cross_market_models.py
  cross_market_portfolio.py
  cross_market_evaluation.py
```

One modeling engine should support named experiment manifests. Do not create competing `v2`, `v3`, or duplicate production trees.

---

## 17. Sequential agent action plan

No downstream step begins until its dependency and exit criterion pass.

| Step | Agent action | Deliverable | Exit criterion |
|---:|---|---|---|
| 1 | Record the locked daily NSE timing | Signed protocol note | 08:55 decision, one forecast batch per NSE day, official open entry, official close exit, target, and timezone are recorded |
| 2 | Resolve data licenses and access | Source decision record | India price source, point-in-time US source, public-Git rules, and credentials policy approved |
| 3 | Resolve both historical memberships | Nifty IT and S&P 500 point-in-time membership samples and coverage report | Every target date and predictor date maps to auditable universes, or the affected scope is narrowed |
| 4 | Inventory symbols and identifiers | Security master specification | ISIN/symbol changes and sector mappings are defined |
| 5 | Specify exchange calendars | Timestamp mapping examples | DST, US holiday, NSE holiday, and weekend fixtures pass |
| 6 | Write data contracts | Raw schemas and manifests | Required fields, types, timezones, hashes, and availability fields fixed |
| 7 | Design retrieval commands | Plan-only source acquisition document | No download occurs without destination, rate, retry, and failure policy |
| 8 | Design cleaning and action audits | Cleaning rule table | Every mutation has a reason code and numeric reconciliation |
| 9 | Construct point-in-time panel design | Stock-date panel schema | No future membership, target, or same-day NSE field enters predictors |
| 10 | Lock D0–D10 feature registry | Feature dictionary | Formula, source, window, availability, missingness, universe, transformation family, and group complete |
| 11 | Design focused EDA | Figure/table specification | Each diagnostic answers a stated data or research question |
| 12 | Implement baseline labels and splits | Temporal split manifest | All same-day stocks remain in one fold and labels obey timing |
| 13 | Implement D0–D6 controlled information ablation | Matched-date comparison | Domestic, limited-US-tech, and compressed-S&P gains are measured without model-family confounding |
| 14 | Implement D7 sparse full-S&P spillover experiment | Elastic-Net path and US-stock link registry | Penalty is past-only; link count, source sector, stability, and lag decay recorded |
| 15 | Implement bounded nonlinear screen | Tree and boosting runs | Same information, dates, costs, and evaluation rules |
| 16 | Implement RFF complexity study | $P/T\times\lambda$ surfaces | Nested maps, seeds, effective degrees of freedom, runtime, and activity complete |
| 17 | Implement portfolio mappings | Long-only and secondary long-short ledgers | Trades reconcile to positions, prices, costs, and realized P&L |
| 18 | Run screening and select candidates | Selection manifest | Baselines remain visible; no-improvement conclusion is allowed |
| 19 | Run confirmation | Confirmation report | Family, information, activity, and cost results stable enough to freeze or reject |
| 20 | Freeze the final protocol | Immutable freeze | All hashes, dates, model, features, strategy, and costs bound |
| 21 | Run final evaluation once | Final predictions and ledger | Complete without post-final tuning |
| 22 | Produce inference and explanations | Bootstrap, HAC, attribution, drift artifacts | Claims distinguish prediction, portfolio performance, and association |
| 23 | Build the academic report | 15–25 page report and appendices | Every figure has dates, units, timing, interpretation, and limitations |
| 24 | Reproduce from a clean environment | Verification manifest | Commands rebuild derived evidence from permitted source inputs |

---

## 18. Agent work packages

### WP-A: Data access and governance

Tasks:

- Confirm institutional data access.
- Record source terms and redistribution limits.
- Select point-in-time membership source.
- Decide whether raw data may enter Git LFS.
- Produce source field dictionaries and retrieval manifests.

Blocking output: approved `cross_market_sources.yaml` design.

### WP-B: Event-time alignment

Tasks:

- Enforce the locked 08:55 Asia/Kolkata NSE decision timestamp.
- Enforce one daily forecast batch per eligible NSE trading session.
- Build exchange-session mapping specification.
- Create DST and holiday fixtures.
- Define latest-completed-session logic.
- Define macro release delay rules.

Blocking output: alignment audit with zero future observations.

### WP-C: Indian panel and membership

Tasks:

- Reconcile identifiers and corporate actions.
- Apply point-in-time membership.
- Generate adjusted OHLCV fields.
- Construct open-to-close targets.
- Audit missingness and liquidity.

Blocking output: immutable stock-date panel manifest.

### WP-D: Feature blocks and EDA

Tasks:

- Implement D0–D10 independently, with D7 stored as a sparse high-dimensional branch and D9/D10 retained as optional contextual branches.
- Export complete feature dictionary.
- Measure warm-up and coverage.
- Produce targeted cross-market lag and sector diagnostics.
- Decide whether D5, D9, and D10 are justified.

Promotion output: one locked economic information specification selected from D3–D7, with all earlier block results retained.

### WP-E: Modeling and complexity

Tasks:

- Fit controls and Ridge ablations.
- Fit sparse models and record selected links.
- Fit bounded tree families.
- Run RFF response surface and seed sensitivity.
- Record learning curves and complexity measures.

Promotion output: screening selection with baseline review.

### WP-F: Portfolio and evaluation

Tasks:

- Implement execution ledger.
- Add itemized costs.
- Apply long-only and long-short mappings.
- Compute benchmarks, uncertainty, activity, and capacity.
- Produce driver-drift explanations.

Promotion output: confirmation evidence and freeze recommendation.

### WP-G: Reporting and verification

Tasks:

- Build evidence-linked tables and figures.
- Describe adaptations of both papers accurately.
- Document negative and inactive results.
- Verify every claim against run manifests.
- Render and inspect the final PDF.

Output: submission package with reproducibility appendix.

---

## 19. Decision rules before implementation

Implementation begins only after these decisions are recorded:

1. **Traded universe:** point-in-time Nifty IT constituents, a disclosed fixed technology cohort, or a Nifty IT tracking instrument.
2. **Indian source:** official NSE downloads or licensed institutional source.
3. **US source:** institutional point-in-time S&P 500 source, with an explicitly narrower fallback if unavailable.
4. **Sample dates:** selected after a coverage report, before outcome inspection.
5. **Decision timestamp:** locked at 08:55 Asia/Kolkata, before the 09:00 regular pre-open session; entry uses the official daily open and exit uses the official daily close.
6. **Primary strategy:** long-only top 30% of eligible Nifty IT constituents with capped inverse-volatility weights.
7. **Primary comparisons:** D3 versus D4, followed by D4 versus D6 versus D7 on matched dates.
8. **Primary model evidence:** market-layer and relative-return forecasts reported separately.
9. **Final-period status:** genuinely untouched or explicitly retrospective.
10. **Repository policy:** which raw data may be shared publicly.

---

## 20. Risks and mitigations

| Risk | Consequence | Mitigation |
|---|---|---|
| Historical constituents unavailable | Survivorship bias | License membership, reconstruct notices, or narrow the claim |
| Naive date join | US future leakage or wrong-session mapping | Timestamp-based latest-completed-session join |
| Mixed adjusted/raw OHLC | Artificial gaps and returns | One adjustment factor across OHLC; action audit |
| Too many correlated stock rows | Overstated effective sample size | Date clusters, equal-date weighting, date-block inference |
| US feature block wins through different coverage | Invalid ablation | Matched stock-date intersection |
| Current revised macro history | Look-ahead bias | ALFRED real-time periods and conservative release lags |
| Monthly RBI lending rates assigned to their reference month | Look-ahead bias | Join on publication timestamp and carry forward with an age feature |
| Retrospective crisis or trend labels used as predictors | Future leakage | Scheduled-event table plus causal online markers; retrospective annotations remain descriptive |
| Rainfall and holiday feature proliferation | Spurious significance | One bounded D10 block, matched dates, block inference, and no promotion without stable incremental evidence |
| Sparse forecasts produce no trades | Misleading Sharpe | Activity gates and forecast metrics retained |
| High turnover eliminates gains | Nonviable strategy | Cost hurdle and cost sensitivity before selection |
| Crisis-only relationship | Poor generalization | Year/regime panels and confirmation block |
| Many searches | Selection bias | Predeclared registry and multiple-testing adjustment |
| Sector mapping changes | Misclassification | Dated mapping configuration and sensitivity |
| Public repository violates source terms | Legal/reproducibility conflict | Commit manifests and scripts; restrict licensed raw files |

---

## 21. Acceptance checklist

### Data and timing

- [ ] Point-in-time Nifty IT membership is sourced or the traded scope is explicitly narrowed.
- [ ] Point-in-time S&P 500 membership is sourced or D6/D7 are explicitly removed.
- [ ] Every source has a license note and immutable manifest.
- [ ] All joins use availability timestamps.
- [ ] DST and holiday fixtures pass.
- [ ] Corporate actions and symbol changes reconcile.
- [ ] Same-day NSE target information is absent from features.

### Experimental design

- [ ] H1–H5 and the optional H10 contextual test are frozen before screening.
- [ ] D3 versus D4 is the limited-US-tech comparison.
- [ ] D4 versus D6 versus D7 is the full-S&P information-complexity comparison.
- [ ] Information and model complexity are tested separately.
- [ ] D9 monetary-policy and D10 minor-context blocks are evaluated after the equity-information experiments.
- [ ] Scheduled events and unscheduled retrospective annotations are stored separately.
- [ ] Baselines use identical dates and costs.
- [ ] All stock rows for one date remain in one fold.
- [ ] Final dates are not used for tuning.

### Modeling and evaluation

- [ ] Penalties are selected chronologically.
- [ ] Sparse links, RFF seeds, and effective complexity are logged.
- [ ] Prediction and portfolio results are both reported.
- [ ] Activity, turnover, exposure, and costs accompany Sharpe.
- [ ] Date-block uncertainty and multiple-search limits are disclosed.
- [ ] No-ML improvement is an allowed conclusion.

### Reporting

- [ ] Both papers are described as methodological inspirations, not replicated results.
- [ ] Every figure states data, dates, units, target, and timing.
- [ ] Feature importance is not described causally.
- [ ] Data-source and licensing limitations are visible.
- [ ] Commands, manifests, and hashes support reproduction.

---

## 22. References and source ledger

### Research papers

Chinco, A. M., Clark-Joseph, A. D., and Ye, M. (2019). “Sparse Signals in the Cross-Section of Returns.” *The Journal of Finance*, 74(1), 449–492. DOI: 10.1111/jofi.12733. Local converted source: [Sparse Signals in the Cross-Section of Returns](Sparse_Signals_in_the_Cross_Section_of_Returns.md).

Kelly, B. T., Malamud, S., and Zhou, K. (2024). “The Virtue of Complexity in Return Prediction.” *The Journal of Finance*, 79(1), 459–501. DOI: 10.1111/jofi.13298. Local converted source: [The Virtue of Complexity in Return Prediction](The_Virtue_of_Complexity_in_Return_Prediction.md).

### Data and methodology sources checked on 29 October 2026

- [NSE historical capital-market reports](https://www.nseindia.com/static/resources/historical-reports-capital-market-daily-monthly-archives): official daily/monthly equity archives, historical indices, India VIX, and security-wise data.
- [NSE all reports](https://www.nseindia.com/all-reports): current bhavcopy and CM-UDiFF report catalogue.
- [NSE security-wise historical price-volume data](https://www.nseindia.com/historical/price-and-volume-data-per-security): official OHLCV fields.
- [Nifty Indices historical index data](https://www.niftyindices.com/reports/historical-data): official index history interface.
- [Nifty 50 index page](https://www.niftyindices.com/indices/equity/broad-based-indices/nifty--50): broad Indian-market benchmark, current constituents, factsheet, and methodology.
- [Nifty IT index page](https://www.niftyindices.com/indices/equity/sectoral-indices/nifty-it): primary sector index, current constituent download, factsheet, and methodology.
- [NSE Indices data subscription](https://www.niftyindices.com/offerings/data-subscription): historical constituent data access and authorized distribution channels.
- [NSE ETF market](https://www.nseindia.com/market-data/exchange-traded-funds-etf): listed Nifty IT and Nifty 50 tracking instruments for investable benchmark review.
- [NSE equity-derivative products](https://www.nseindia.com/static/products-services/equity-derivatives-products): product-status check; the current page lists Nifty IT among discontinued derivative indices, so the design must not assume a live Nifty IT futures benchmark for all periods.
- [NSE India VIX history](https://www.nseindia.com/reports-indices-historical-vix): official India VIX historical interface.
- [Cboe VIX historical data](https://www.cboe.com/tradable_products/vix/vix_historical_data): official daily VIX history.
- [State Street sector ETF list](https://www.ssga.com/us/en/individual/capabilities/equities/sector-investing/sector-and-industry-etfs): official sector names and ETF tickers.
- [Federal Reserve target-rate history](https://www.federalreserve.gov/monetarypolicy/openmarket.htm): official target federal-funds range and effective-date changes.
- [Federal Reserve FOMC calendars](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm): scheduled meetings, statements, minutes, and release dates.
- [FRED/ALFRED real-time-period documentation](https://fred.stlouisfed.org/docs/api/fred/realtime_period.html): historical information-state and revision handling.
- [RBI data releases](https://statistics.rbi.org.in/): official Indian economic, policy, lending, and reference-rate data access.
- [RBI major monetary-policy rates and reserve requirements](https://systemhealth.rbi.org.in/Scripts/PublicationsView.aspx_id%3D22517.html): effective-date history for repo, reverse repo, SDF, MSF, bank rate, CRR, and SLR.
- [India Meteorological Department data-supply description](https://mausam.imd.gov.in/newdelhi/docs/data-procedure.pdf): official daily, monthly, subdivisional, and other rainfall holdings and access conditions.
- [yfinance documentation and legal disclaimer](https://ranaroussi.github.io/yfinance/): practical fallback interface and personal-use warning.

---

## 23. Recommended first decision

Before any implementation, confirm access to both historical point-in-time Nifty IT constituents and historical point-in-time S&P 500 constituents. The Indian membership determines whether the project can validly claim a historical Nifty IT stock-selection strategy; the US membership determines whether D6/D7 can validly claim full-S&P information. Once membership is resolved, the first implemented experiment should be the matched-date D3-versus-D4 Ridge comparison, followed by D4-versus-D6 Ridge and D4-versus-D7 sparse shrinkage. This sequence directly measures the information gained by moving from Indian context, to a limited US technology universe, to the full US top-500 cross-section.

