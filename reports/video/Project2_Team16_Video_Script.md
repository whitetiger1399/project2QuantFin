# Team 16 — video script and screen directions

Read only the narration aloud. All 16 scene numbers match deck pages. Four presenters have five minutes each. The last 20 seconds are a production buffer; end speech by 19:40.

Timing is a rehearsal/editing budget, not a guarantee from word count. Rehearse at about 120 wpm; preserve graph-reading time and label accelerated genuine execution. See recording_commands.md for the required demonstration.

## 01 · Cross-Market Forecasting and Signed Trading of Nifty IT Stocks

**00:00–00:45 · PRATYUSH SINHA · 81 spoken words**

**SHOW VIDEO DECK SLIDE 01  ·  PDF PAGE 01**

**Deck title:** Cross-Market Forecasting and Signed Trading of Nifty IT Stocks

### Spoken narration

Hello. We are Team Sixteen. Our project asks whether U.S. market information can help us trade Indian IT services stocks before the Indian market opens. Each day, the model can choose long, short, or flat. We also test whether frontier AI releases affect these stocks. We will explain the design, show the pipeline running, and examine the returns after trading costs. The central question is simple: does extra information improve a decision we could actually have made at the time?

### Screen directions — not spoken

Start on deck slide 01: Cross-Market Forecasting and Signed Trading of Nifty IT Stocks.

Keep the title, NUS logo, course, team, four names and IDs visible. Begin the presentation clock at the first spoken word.

At 00:45, advance to video deck slide 02.

Narration allowance at 120 wpm: 41 s; visual/transition allowance: 4 s.

Source: Report: title page and Section 1; assets/authors.json.

## 02 · The question: can U.S. information help the next Indian trade?

**00:45–01:45 · PRATYUSH SINHA · 113 spoken words**

**SHOW VIDEO DECK SLIDE 02  ·  PDF PAGE 02**

**Deck title:** The question: can U.S. information help the next Indian trade?

### Spoken narration

Indian and U.S. services firms share some customers and technology risks. The U.S. session also finishes before the next Indian open. Could that earlier information help predict the Indian trading day? We trade only Indian stocks, and predict their return from open to close. The two papers guide our design. Chinco and coauthors study short-lived signals across stocks, using penalties to limit complexity. Kelly and coauthors show why richer models can help when complexity is controlled through shrinkage. We apply those ideas to daily Indian trading; we do not reproduce their experiments. Our test has three steps: improve the forecast, turn it into a position, and check the return after costs.

### Screen directions — not spoken

Start on deck slide 02: The question: can U.S. information help the next Indian trade?.

Point to the three lines in order. Explain that shares are traded in India and returns are measured in rupees. Introduce the two papers without reading their titles in full.

At 01:45, advance to video deck slide 03.

Narration allowance at 120 wpm: 57 s; visual/transition allowance: 3 s.

Source: Report Sections 1–2; Chinco et al. (2019); Kelly et al. (2024).

## 03 · Research architecture: from available data to a daily trade

**01:45–03:30 · PRATYUSH SINHA · 171 spoken words**

**SHOW VIDEO DECK SLIDE 03  ·  PDF PAGE 03**

**Deck title:** Research architecture: from available data to a daily trade

### Spoken narration

This diagram connects the whole project. On the left, Indian inputs describe each stock, its peers, and the wider market. U.S. inputs add services firms and broad-market conditions. Rates, currencies, and dated AI releases provide context. First, everything passes the eight fifty-five Indian-time gate. We use only information available before that decision. We then construct features such as past returns, momentum, volatility, and peer movements. The fitting block learns from earlier observations, including its cleaning and transformation rules. Screening compares candidates; confirmation selects the settings; the freeze records that choice. Selection happens during research, while later refits follow the declared schedule. Each day's forecast then estimates an Indian stock's open-to-close return. A threshold turns that forecast into a long, short, or flat choice. Exposure limits control the portfolio, and every position closes that day. Finally, we subtract entry and exit costs. Follow that last link carefully: predicting a return and earning it after costs are different tests. The next slides unpack the timing, features, and trading rule behind these boxes.

### Screen directions — not spoken

Start on deck slide 03: Research architecture: from available data to a daily trade.

Spend the full slot here. Trace the source groups, then the 08:55 gate, training, forecast, and three position choices. Pause after each arrow; do not read every box.

At 03:30, advance to video deck slide 04.

Narration allowance at 120 wpm: 86 s; visual/transition allowance: 19 s.

Source: Report Figure 1 and Sections 2, 4–5; cross_market/panel.py, timing.py and experiments.py.

## 04 · Six questions guide the experiments

**03:30–05:00 · PRATYUSH SINHA · 138 spoken words**

**SHOW VIDEO DECK SLIDE 04  ·  PDF PAGE 04**

**Deck title:** Six questions guide the experiments

### Spoken narration

We organised the study around six questions. Does U.S. services information help predict Indian IT returns? Do frontier AI releases precede weaker returns? Has that reaction become less negative after twenty twenty-four? Do larger capability advances produce stronger negative reactions? Can our forecasts earn reliable returns after costs? And are services firms adapting through AI offerings and workforce changes? The first four concern market relationships. The fifth tests the trading strategy. The sixth examines company disclosures. Keeping these questions separate matters. An AI offering does not prove an improvement in margins, and a return correlation does not guarantee a profitable trade. We report what the evidence supports, what contradicts a claim, and what remains uncertain. These questions developed during historical research, so we treat the tests as exploratory. Ramyani will now explain the data and timing controls.

### Screen directions — not spoken

Start on deck slide 04: Six questions guide the experiments.

Read the intent of each hypothesis, not the whole row. Pause on H5 and H6 to distinguish a trading test from a descriptive company study. Handover to Ramyani at 05:00.

At 05:00, advance to video deck slide 05.

Narration allowance at 120 wpm: 69 s; visual/transition allowance: 21 s.

Source: Report Sections 1 and 7; saved hypothesis-analysis protocol.

## 05 · Data: ten Indian IT stocks, several information sources

**05:00–06:15 · RAMYANI PALIT · 115 spoken words**

**SHOW VIDEO DECK SLIDE 05  ·  PDF PAGE 05**

**Deck title:** Data: ten Indian IT stocks, several information sources

### Spoken narration

We follow ten current Nifty IT members, including TCS, Infosys, Wipro, and HCL Technologies. Their names are shown below. This is a fixed current-member study, so it cannot represent every company that once belonged to the index. Yahoo Finance supplies daily prices, volumes, and ETF benchmarks. FRED and ALFRED supply economic series. Public membership histories support broader Indian and U.S. inputs. Dated AI releases identify events. Epoch benchmark scores support a separate retrospective study; we do not backfill them into forecasts made before those scores were available. Before creating features, we check prices, quarantine invalid rows, and retain genuine missing values. Source records also preserve the timing and vintage limitations of the economic data.

### Screen directions — not spoken

Start on deck slide 05: Data: ten Indian IT stocks, several information sources.

Point to each source and its role. Display the ten company names in a small separate line. Note that benchmark scores are used retrospectively and are not backfilled into past forecasts.

At 06:15, advance to video deck slide 06.

Narration allowance at 120 wpm: 58 s; visual/transition allowance: 17 s.

Source: Report Sections 2–3; public sources listed in report references [3]–[8].

## 06 · Timing: what was known before 08:55 IST?

**06:15–07:30 · RAMYANI PALIT · 115 spoken words**

**SHOW VIDEO DECK SLIDE 06  ·  PDF PAGE 06**

**Deck title:** Timing: what was known before 08:55 IST?

### Spoken narration

At prediction time, the latest completed U.S. session may be available. Today's Indian close, high, low, and volume are still in the future and cannot be inputs. Our target is closing price divided by opening price, minus one. We observe it only after the session ends. Holidays are matched through trading sessions, rather than a simple calendar-day shift. Preprocessing follows the same rule. Imputation, outlier cutoffs, scaling, and feature selection learn from the earlier training window, then apply forward. A full-sample average could otherwise leak future information into the past. Each rolling fit also leaves a one-session embargo. The key check is whether every input and fitted transformation existed before the prediction it supports.

### Screen directions — not spoken

Start on deck slide 06: Timing: what was known before 08:55 IST?.

Trace the timing steps from top to bottom. Contrast a U.S. close already observed with an Indian close still in the future. Point to the training-only transformation line.

At 07:30, advance to video deck slide 07.

Narration allowance at 120 wpm: 58 s; visual/transition allowance: 17 s.

Source: Report Sections 2.1 and 3.1; timing.py; experiments.py::_fit_block.

## 07 · More information did not improve the fixed ridge model

**07:30–09:00 · RAMYANI PALIT · 148 spoken words**

**SHOW VIDEO DECK SLIDE 07  ·  PDF PAGE 07**

**Deck title:** More information did not improve the fixed ridge model

### Spoken narration

Read this heatmap from top to bottom. We start with each stock's own history, then add peers, U.S. services, Nifty Fifty, broad U.S. aggregates, individual S and P stocks, and AI context. Features include lagged returns, momentum, rolling volatility, and moving-average distances. Each column is a year. The score compares forecast error with a simple asset-mean forecast; below zero means worse prediction. The comparison holds the ridge penalty fixed and uses matched stock-session outcomes. Look at the jump from F4 to F5: adding individual U.S. stocks sharply worsens the score across years. One volatile year cannot explain that pattern. Redundant inputs and too little shrinkage are possible explanations, not established causes. This is a fixed linear-model diagnostic. It does not show that U.S. information is useless, and it is separate from the selected tree model. The lesson is to test information and complexity together.

### Screen directions — not spoken

Start on deck slide 07: More information did not improve the fixed ridge model.

Explain the rows first: own history, peers, U.S. services, Nifty 50, S&P aggregate, constituents, AI, full context. Trace F0 to F5 in one year, then compare across years. R² is a forecast score, not a return.

At 09:00, advance to video deck slide 08.

Narration allowance at 120 wpm: 74 s; visual/transition allowance: 16 s.

Source: Report Figure 5; matched quarterly feature-progression audit; F0–F7 ridge penalty 0.1.

## 08 · Choose settings through 2024; evaluate forward in time

**09:00–10:00 · RAMYANI PALIT · 102 spoken words**

**SHOW VIDEO DECK SLIDE 08  ·  PDF PAGE 08**

**Deck title:** Choose settings through 2024; evaluate forward in time

### Spoken narration

Screening compares candidates in twenty twenty-one and twenty twenty-two. Confirmation uses twenty twenty-three and twenty twenty-four, then records one set of settings. In twenty twenty-five, we refit quarterly on earlier observations, using at most twelve hundred and sixty trading sessions. For January to September twenty twenty-six, we use the same settings but fit once on pre-twenty-twenty-six data. That boundary is marked on the results graph. Predictions follow time order, but earlier project iterations had already examined both evaluation periods. These are historical evaluations, not untouched tests of a newly proposed idea. Ritik will now show how the models produce a trading ledger.

### Screen directions — not spoken

Start on deck slide 08: Choose settings through 2024; evaluate forward in time.

Distinguish model settings from fitted parameters. Explain that a quarterly refit updates the estimator but does not choose a new model. Handover to Ritik at 10:00.

At 10:00, advance to video deck slide 09.

Narration allowance at 120 wpm: 51 s; visual/transition allowance: 9 s.

Source: Report Section 5.2; run manifests and freeze record in report Appendix A.

## 09 · Confirmation selected Extra Trees

**10:00–11:15 · RITIK SRIVASTAVA · 121 spoken words**

**SHOW VIDEO DECK SLIDE 09  ·  PDF PAGE 09**

**Deck title:** Confirmation selected Extra Trees

### Spoken narration

We tested linear penalties, PCA compression, boosting, and Extra Trees. Ridge shrinks coefficients; Lasso can remove them; Elastic Net combines both effects. Tree models capture nonlinear relationships. In this chart, histogram boosting leads screening, but its confirmation Sharpe turns negative. Extra Trees wins the declared confirmation rule. Its two hundred and fifty trees have depth capped at six, at least forty samples per leaf, and half the features available at each split. These limits reduce the model's ability to fit small, noisy patterns. Selection also checks prediction coverage and declared tie-breakers. Elastic Net was included and did not win. Grey cells mean not evaluated. The later columns assess frozen choices and controls; they are not another search for the best family.

### Screen directions — not spoken

Start on deck slide 09: Confirmation selected Extra Trees.

Point to histogram boosting in screening, then Extra Trees in confirmation. Explain grey cells as not evaluated. Do not call the 2025/2026 columns a fresh family search.

At 11:15, advance to video deck slide 10.

Narration allowance at 120 wpm: 61 s; visual/transition allowance: 14 s.

Source: Report Figure 8 and Section 5.1; screening and confirmation leaderboards.

## 10 · The trading rule: long, short, or flat

**11:15–12:30 · RITIK SRIVASTAVA · 128 spoken words**

**SHOW VIDEO DECK SLIDE 10  ·  PDF PAGE 10**

**Deck title:** The trading rule: long, short, or flat

### Spoken narration

The forecast becomes a position through a clear rule. Above fifteen basis points, a stock is eligible for a long position. Below minus fifteen, it is eligible for a short. Between those thresholds, it stays flat. Fifteen basis points is zero point one five percent. We take up to three eligible stocks on each side, with capped weights and total gross exposure at most one. Every position opens from cash and closes that session. Costs therefore apply twice: five basis points for fees and spread, plus two and a half for slippage, on each side. We subtract costs from the signed return and compound the daily net results. This is a historical simulation. Opening prices approximate fills, and taxes, borrowing restrictions, and market impact are not fully modelled.

### Screen directions — not spoken

Start on deck slide 10: The trading rule: long, short, or flat.

Point to the threshold line, then the exposure and cost rules. In code, point to the signed gross return, twice-gross turnover, and net-return calculation. Explain 100 basis points equals one percent.

At 12:30, advance to video deck slide 11.

Narration allowance at 120 wpm: 64 s; visual/transition allowance: 11 s.

Source: Report Section 5.4; experiments.py::_strategy_ledger and _annualized_metrics.

## 11 · Run the pipeline: build data, then fit candidates

**12:30–13:45 · RITIK SRIVASTAVA · 69 spoken words**

**SHOW VIDEO DECK SLIDE 11  ·  PDF PAGE 11**

**Deck title:** Run the pipeline: build data, then fit candidates

### Spoken narration

First, the builder turns audited sources into a panel and feature dictionary. Screening then fits candidates on earlier observations and predicts later sessions. Watch the training end date and the first prediction date: they must be in the right order. The output records settings, input fingerprints, and checkpoints. We show the actual launch, progress, and completion, with waiting accelerated and labelled. Now inspect one completed block and its dates.

### Screen directions — not spoken

Start on deck slide 11: Run the pipeline: build data, then fit candidates.

Use recording_commands.md D1–D2. Reserve at least 30 seconds for genuine launch/progress/completion footage and a readable date check. On-screen label during accelerated footage: ‘Training wait accelerated; commands and outputs are real’. Explain narration over the relevant output. Do not fill spare time with a static terminal or read hashes aloud.

Switch from slide 11 to the terminal for the demonstration, then return to slide 11.

At 13:45, advance to video deck slide 12.

Narration allowance at 120 wpm: 35 s; visual/transition allowance: 40 s.

Source: Project2.md Section 5; recording_commands.md D1–D2; panel.py and experiments.py.

## 12 · Run the pipeline: select, freeze, evaluate

**13:45–15:00 · RITIK SRIVASTAVA · 78 spoken words**

**SHOW VIDEO DECK SLIDE 12  ·  PDF PAGE 12**

**Deck title:** Run the pipeline: select, freeze, evaluate

### Spoken narration

Confirmation compares the promoted candidates, then the freeze records one specification. The evaluation runner uses it for twenty twenty-five, followed by the twenty twenty-six extension. We inspect forecasts and positions alongside the daily ledger. The ledger shows gross return, transaction cost, and net return. Our check verifies that gross minus cost equals net and that fitting dates precede predictions. This demonstrates the full path from data through validation to evaluation after costs. Victor will now explain the results.

### Screen directions — not spoken

Start on deck slide 12: Run the pipeline: select, freeze, evaluate.

Use recording_commands.md D3–D5. Reserve at least 24 seconds for readable output: chosen family, completion, date check, forecast/position record and portfolio ledger. These may be separate files; do not imply every field is in one ledger row. If a reproduction selects differently, show its actual result and distinguish it from the report's saved evaluation. Handover to Victor at 15:00.

Switch from slide 12 to the terminal for the demonstration, then return to slide 12.

At 15:00, advance to video deck slide 13.

Narration allowance at 120 wpm: 39 s; visual/transition allowance: 36 s.

Source: recording_commands.md D3–D5; verify_ai_capability_pipeline.py; verify_frozen_2026_extension.py.

## 13 · Returns: +10.37% combined, with very different years

**15:00–16:30 · VICTOR LEE CHIA SWEA · 143 spoken words**

**SHOW VIDEO DECK SLIDE 13  ·  PDF PAGE 13**

**Deck title:** Returns: +10.37% combined, with very different years

### Spoken narration

The model gained ten point three seven percent after costs from January twenty twenty-five through September twenty twenty-six. Over that interval, the Nifty IT ETF lost thirty-three point eight three percent, Nifty Fifty lost two point two six percent, and holding the fixed stock cohort lost twenty-five point two eight percent. Follow the blue line across the boundary. The model lost four point zero four percent in twenty twenty-five, then gained fifteen point zero one percent in the nine-month extension. Sharpe moved from minus zero point two six to one point four six, but both uncertainty intervals include zero. The model looks defensive in this sample, rather than consistently profitable. Remember the comparison: passive holdings stay invested overnight, while our trades close each day. The fitting schedule also changes at the boundary. These differences limit what we can attribute to the model alone.

### Screen directions — not spoken

Start on deck slide 13: Returns: +10.37% combined, with very different years.

Trace the model line across the 2026 boundary, then compare the passive lines. Point to period returns and Sharpe below. Explain 2026 is nine months and the fitting schedule changes. Leave time to inspect the drawdowns; do not read every plotted value.

At 16:30, advance to video deck slide 14.

Narration allowance at 120 wpm: 72 s; visual/transition allowance: 18 s.

Source: Report Figure 9, Section 6 and selected daily ledgers; ETF comparators include overnight exposure.

## 14 · Costs turn the 2025 gross gain into a net loss

**16:30–17:45 · VICTOR LEE CHIA SWEA · 119 spoken words**

**SHOW VIDEO DECK SLIDE 14  ·  PDF PAGE 14**

**Deck title:** Costs turn the 2025 gross gain into a net loss

### Spoken narration

These bars use exactly the same trades before and after costs. In twenty twenty-five, a five point one six percent gross gain becomes a four point zero four percent net loss. In the twenty twenty-six segment, twenty-six point nine five percent gross becomes fifteen point zero one percent net. The difference includes lost compounding; it is not simply the sum of fees. The activity counts below help interpret the curve: fourteen long days, one hundred and thirteen short days, and three hundred and seven flat days. No day held both sides. That pattern is consistent with defensive behaviour during the sector decline. It also shows why profitability depends on both signal strength and the cost of acting on it.

### Screen directions — not spoken

Start on deck slide 14: Costs turn the 2025 gross gain into a net loss.

Compare the paired 2025 bars first, then 2026. Point to the visible activity counts below. Explain that flat means no position that day. Treat the exposure pattern as descriptive; do not claim it causally explains all returns.

At 17:45, advance to video deck slide 15.

Narration allowance at 120 wpm: 60 s; visual/transition allowance: 15 s.

Source: Report Figures 10–11; 07_cost_accounting.csv; combined ledger activity counts.

## 15 · What the six tests establish

**17:45–19:00 · VICTOR LEE CHIA SWEA · 123 spoken words**

**SHOW VIDEO DECK SLIDE 15  ·  PDF PAGE 15**

**Deck title:** What the six tests establish

### Spoken narration

The findings are mixed. H1 supports a positive U.S.-India association after accounting for multiple tests. H2 is inconclusive overall, although the twenty twenty-six subgroup shows a negative release-day association after adjustment. That is exploratory evidence, not proof that releases caused the fall. H3 does not establish that the effect weakened after twenty twenty-four. H4 has only twenty-one scored event dates, below our specified minimum of thirty. H5 does not establish a stable advantage after costs. One losing year alone cannot disprove positive expected returns; the uncertainty and variation across periods are the reason for caution. H6 documents company adaptation, but does not test whether AI caused higher margins. We therefore distinguish supported associations, insufficient evidence, and questions our design cannot answer.

### Screen directions — not spoken

Start on deck slide 15: What the six tests establish.

Use the same H1–H6 order as slide 04. Point to H1 support, then H2's overall/subgroup distinction. Explain adjusted p-values account for multiple testing. Group H3/H4 as unresolved for different reasons. H5 is not rejected just because one year lost money. H6 is descriptive, not a causal margin test.

At 19:00, advance to video deck slide 16.

Narration allowance at 120 wpm: 62 s; visual/transition allowance: 13 s.

Source: Report Section 7; date-level HAC regressions, Holm corrections and company disclosures.

## 16 · The lesson: useful signals must survive timing and costs

**19:00–20:00 · VICTOR LEE CHIA SWEA · 64 spoken words**

**SHOW VIDEO DECK SLIDE 16  ·  PDF PAGE 16**

**Deck title:** The lesson: useful signals must survive timing and costs

### Spoken narration

The project connects information, prediction, and trading in one reproducible process. More features hurt the fixed ridge model. The selected tree strategy behaved defensively, but costs erased its twenty twenty-five gross gain. The next tests should compare features under matched settings, use more realistic execution, and freeze the method before future data arrive. Our code, forecasts, and ledgers make these findings inspectable. Thank you.

### Screen directions — not spoken

Start on deck slide 16: The lesson: useful signals must survive timing and costs.

End spoken narration by 19:40. Keep the final slide visible for the final 20-second production buffer; shorten pauses if behind. Do not add an unscripted extra summary. Sources and command appendix follow outside the recorded 16 slides.

Finish on video deck slide 16. Do not advance into the reference appendix during the timed recording.

Narration allowance at 120 wpm: 32 s; visual/transition allowance: 28 s.

Source: Report Sections 7.4 and 8; regime labels are retrospective; README and recording_commands.md.

## Production notes — not spoken

The assignment explicitly requires data build → fit → validation → evaluation with costs. Record real launches and completion, accelerate waiting with an on-screen label, and use the saved report results only as the named historical evidence. A plan-only call is not a model fit.

Own-code backtesting is implemented in src/quantfin/cross_market/experiments.py. The assignment’s backtesting libraries are illustrative. See recording_commands.md and recording_evidence.py for concrete steps.

Use the fixed timing schedule in timing.csv. A word is a match of the Unicode regex recorded in package_manifest.json; headings and directions are excluded. Presenter allocations describe the proposed video roles only.

