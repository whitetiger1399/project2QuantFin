# Cross-Market Forecasting and Signed Trading of Nifty IT Stocks

Data Science in Quantitative Finance DSA5205 · Project2 Teams 16

Format: 960 × 540 pt (16:9), matching the supplied old-project PDF. Recording: 20:00 maximum.

![NUS logo](../../assets/nus_logo_full-vertical.jpg)

- PRATYUSH SINHA · A0352482A
- RAMYANI PALIT · A0357066X
- RITIK SRIVASTAVA · A0355860X
- VICTOR LEE CHIA SWEA · A0350886R
---

## 01 · Cross-Market Forecasting and Signed Trading of Nifty IT Stocks

00:00–00:45 · PRATYUSH SINHA

**Key message:** Can information available before the Indian open improve a daily trading decision?

Source: Report: title page and Section 1; assets/authors.json.

---

## 02 · The question: can U.S. information help the next Indian trade?

00:45–01:45 · PRATYUSH SINHA

- Targets: ten fixed current Nifty IT members
- Inputs: Indian history + completed U.S. sessions
- Daily decision: 08:55 IST; trade NSE open → close

**Key message:** A cross-market association is a starting point; a profitable trading rule requires a separate test.

Source: Report Sections 1–2; Chinco et al. (2019); Kelly et al. (2024).

---

## 03 · Research architecture: from available data to a daily trade

01:45–03:30 · PRATYUSH SINHA

![Research architecture: from available data to a daily trade](video_architecture.png)

**Key message:** Every input must pass the information clock before it can affect a trade.

Source: Report Figure 1 and Sections 2, 4–5; cross_market/panel.py, timing.py and experiments.py.

---

## 04 · Six questions guide the experiments

03:30–05:00 · PRATYUSH SINHA

- H1  U.S. services returns predict subsequent Indian IT returns
- H2  Frontier AI releases precede negative Indian IT returns
- H3  The release effect becomes less negative after 2024
- H4  Larger capability advances imply larger negative reactions
- H5  Signed forecasts produce robust returns after costs
- H6  Services firms adapt through AI offerings and workforce change

**Key message:** Price association, economic performance, and company adaptation are different claims.

Source: Report Sections 1 and 7; saved hypothesis-analysis protocol.

---

## 05 · Data: ten Indian IT stocks, several information sources

05:00–06:15 · RAMYANI PALIT

- Yahoo Finance: daily prices, volumes, ETFs and global market context
- FRED / ALFRED: rates, yields and macro conditions
- Membership histories: public Nifty and S&P reconstructions
- AI releases + Epoch AI: dated events and retrospective capability analysis

**Key message:** A fixed current-member cohort: results do not represent every historical Nifty IT constituent.

Source: Report Sections 2–3; public sources listed in report references [3]–[8].

---

## 06 · Timing: what was known before 08:55 IST?

06:15–07:30 · RAMYANI PALIT

- Before 08:55 IST: completed U.S. session and earlier Indian information
- At the NSE open: enter eligible positions
- At the NSE close: exit and observe the return label
- Inside each fit: filter, impute, winsorize, scale and select using training data

**Key message:** A daily row is safe only when each feature was available before its decision time.

Source: Report Sections 2.1 and 3.1; timing.py; experiments.py::_fit_block.

---

## 07 · More information did not improve the fixed ridge model

07:30–09:00 · RAMYANI PALIT

![More information did not improve the fixed ridge model](../publication_figure_pack_v2_2026-11-01/12_information_ladder.png)

**Key message:** The sharp drop at F5 concerns this fixed-penalty ridge test—not every possible use of U.S. data.

Source: Report Figure 5; matched quarterly feature-progression audit; F0–F7 ridge penalty 0.1.

---

## 08 · Choose settings through 2024; evaluate forward in time

09:00–10:00 · RAMYANI PALIT

- 2021–2022: screening; 2023–2024: confirmation
- 2025: selected settings, quarterly past-only refits
- Jan–Sep 2026: same settings, one pre-2026 fit
- Both evaluation periods were inspected in earlier research iterations

**Key message:** Settings are selected through 2024; 2025 and 2026 use different declared fitting schedules.

Source: Report Section 5.2; run manifests and freeze record in report Appendix A.

---

## 09 · Confirmation selected Extra Trees

10:00–11:15 · RITIK SRIVASTAVA

![Confirmation selected Extra Trees](../publication_figure_pack_v2_2026-11-01/11_model_family_evidence.png)

**Key message:** Extra Trees wins the declared confirmation rule; the screening leader does not remain the leader.

Source: Report Figure 8 and Section 5.1; screening and confirmation leaderboards.

---

## 10 · The trading rule: long, short, or flat

11:15–12:30 · RITIK SRIVASTAVA

- Long above +15 bps; short below −15 bps; otherwise flat
- Up to three stocks per side; gross exposure at most one
- 5 bps fee/spread proxy + 2.5 bps slippage per side
- Net daily return = signed position return − turnover cost

**Key message:** The recorded strategy can go long, short or flat, and it charges both entry and exit.

Source: Report Section 5.4; experiments.py::_strategy_ledger and _annualized_metrics.

---

## 11 · Run the pipeline: build data, then fit candidates

12:30–13:45 · RITIK SRIVASTAVA

- Build: audited sources → daily panel + feature dictionary
- Fit: earlier observations → later-session predictions
- Check: training end precedes the prediction window
- Record: completion, settings and input fingerprints

**Key message:** The saved panel links source information to dated model predictions.

Source: Project2.md Section 5; recording_commands.md D1–D2; panel.py and experiments.py.

---

## 12 · Run the pipeline: select, freeze, evaluate

13:45–15:00 · RITIK SRIVASTAVA

- Confirm candidates → freeze one specification
- Evaluate 2025 → extend through September 2026
- Check dates and the link to the frozen settings
- Inspect forecasts, positions, gross returns, costs and net returns

**Key message:** The freeze links the selected settings to predictions and the post-cost trade ledger.

Source: recording_commands.md D3–D5; verify_ai_capability_pipeline.py; verify_frozen_2026_extension.py.

---

## 13 · Returns: +10.37% combined, with very different years

15:00–16:30 · VICTOR LEE CHIA SWEA

![Returns: +10.37% combined, with very different years](../publication_figure_pack_v2_2026-11-01/08_combined_benchmarks.png)

2025: −4.04% net; Sharpe −0.26. 2026 Jan–Sep: +15.01% net; Sharpe 1.46.

Both Sharpe uncertainty intervals include zero. Passive comparators hold overnight; the model closes daily.

**Key message:** The model beat passive comparators here; the two periods do not establish stable performance.

Source: Report Figure 9, Section 6 and selected daily ledgers; ETF comparators include overnight exposure.

---

## 14 · Costs turn the 2025 gross gain into a net loss

16:30–17:45 · VICTOR LEE CHIA SWEA

![Costs turn the 2025 gross gain into a net loss](video_costs.png)

434 sessions: 14 long · 113 short · 307 flat · 0 mixed long/short

**Key message:** 2025: +5.16% gross becomes −4.04% net. The combined ledger is mostly flat or short.

Source: Report Figures 10–11; 07_cost_accounting.csv; combined ledger activity counts.

---

## 15 · What the six tests establish

17:45–19:00 · VICTOR LEE CHIA SWEA

- H1: U.S.–India association supported; adjusted p = 0.0056
- H2: overall inconclusive; negative 2026 association (p = 0.0155, adjusted)
- H3: weaker release effects after 2024 remain inconclusive
- H4: insufficient scored events: 21 dates; minimum specified = 30
- H5: stable post-cost advantage not established; returns vary by period
- H6: adaptation documented; its causal effect on margins is untested

**Key message:** Supported association ≠ causality; inconclusive evidence ≠ proof of no relationship.

Source: Report Section 7; date-level HAC regressions, Holm corrections and company disclosures.

---

## 16 · The lesson: useful signals must survive timing and costs

19:00–20:00 · VICTOR LEE CHIA SWEA

- Additional inputs need appropriate complexity control
- Costs and exposure change the investment conclusion
- Next: matched feature tests, realistic fills, future evaluation
- Code, forecasts and daily ledgers make the result reproducible

**Key message:** A reproducible daily trading study with conditional defensive results and clear limits.

Source: Report Sections 7.4 and 8; regime labels are retrospective; README and recording_commands.md.

---

## Supporting figures — outside timed recording

![Decision-aligned U.S.–India services correlations](../publication_figure_pack_v2_2026-11-01/05_cross_market_correlations.png)

Descriptive correlation of completed U.S. returns with following eligible Indian intraday returns.

![Mapped frontier event reactions](../publication_figure_pack_v2_2026-11-01/06b_event_responses.png)

U.S. and Indian outcome horizons differ. Limited mapped subset; not all 2026 events.

![Retrospective regime outcomes](../publication_figure_pack_v2_2026-11-01/16_regime_distributions.png)

Small retrospective monthly groups; these labels are not trading signals.

## Reference appendix — outside timed recording

- Assignment: Sections 4–7: timing, models, evaluation, video and submission. documents/markdown/Project2.md
- Report: Presentation source; Appendix A/E maps exact evidence records. reports/Group_16_Report.docx
- Chinco et al. (2019): Sparse signals in the cross-section of returns. https://doi.org/10.1111/jofi.12733
- Kelly et al. (2024): The virtue of complexity in return prediction. https://doi.org/10.1111/jofi.13298
- Market and macro data: Yahoo Finance, FRED/ALFRED; public membership reconstructions. README.md
- AI and company context: Report references include Epoch AI, company disclosures and attributed news. reports/publication_report_sections.py
