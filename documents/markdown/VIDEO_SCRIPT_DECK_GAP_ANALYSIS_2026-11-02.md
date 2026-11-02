# Video script and deck: editorial gap analysis and implemented actions

Review date: 2 November 2026 (Singapore). Scope: the 16 timed slides, synchronized narration, supporting slides, production instructions, and the assignment's video requirements. This is an editorial review of existing research evidence; it does not change model results or run new experiments.

## Overall assessment

The previous package had a sound research sequence: question → architecture → hypotheses → data and timing → features and models → backtest and demonstration → results and limitations. Its problem was uneven information density, rather than missing substance. The architecture, temporal safeguards, cost analysis and six-question structure should be retained. Replacing them with a shorter generic pitch would weaken the submission.

The main results slide combined a cumulative-return plot with annualized returns, volatility, Sharpe, forecast R², rank correlation and repeated endpoint returns. The audience had too many simultaneous reading tasks. Some narration repeated what the source footer or production instructions already explained. The demo slides also displayed instructions to the editor instead of showing the audience what the pipeline does.

One substantive interpretation needed correction: a losing year contradicts a claim of positive returns every year, but does **not** disprove a positive expected return or alpha. H5 now states the actual limitation—stable post-cost advantage has not been established—and explains the period variation and uncertainty.

## Agent action matrix

All actions below have been implemented in the shared content source or builder. Render and synchronization checks are recorded in `reports/video/verification.json`.

| ID / location | Specific gap | Implemented action | Acceptance criterion |
|---|---|---|---|
| V01 · opening / slide 1 | Opening repeated the later methodology checklist. | Lead with the decision, target market and AI question; shorten the preview. | Listener can identify the target, information source and long/short/flat choice in the opening minute. |
| V02 · slide 2 | Paper discussion used abstract methodological phrasing. | Explain penalties and shrinkage plainly, then connect forecast → position → costs. | Both papers remain attributed; daily application is distinguished from replication. |
| V03 · architecture / slide 3 | The pipeline could imply that selection happens before every daily forecast. | Label scheduled refits and research selection separately; explicitly explain the distinction in narration. | All source groups, the availability gate, model selection, daily forecast, positions and costs remain visible. |
| V04 · hypotheses / slide 4 | Long introductions and qualifications competed with six questions. | Use short questions, then group market tests, trading tests and company disclosures. | H1–H6 retain their meaning and match the final verdict slide. |
| V05 · sources / slide 5 | Dense explanation could obscure what each source contributes. | Give each source one clear role; explain fixed-current-member conditioning plainly. | Yahoo, FRED/ALFRED, memberships, AI releases and Epoch remain identified; retrospective scores are not described as historical trading inputs. |
| V06 · timing / slide 6 | Leakage explanation repeated architecture language. | Use the concrete contrast between a completed U.S. close and today's unavailable Indian OHLCV; retain training-only transformations and embargo. | Prediction cutoff, target horizon and preprocessing boundary remain explicit. |
| V07 · feature ladder / slide 7 | Viewers needed help reading the heatmap; explanations could sound like proven causes. | Give reading order, explain negative R², direct attention to F4→F5, and label noise/shrinkage as possible explanations. | Fixed penalty and matched outcomes are stated; the result is not generalized to all U.S. information or all models. |
| V08 · temporal protocol / slide 8 | Freeze, settings and estimator terminology made the timeline harder to follow. | Describe selection through 2024, quarterly 2025 fits and a single pre-2026 fit directly. | Earlier inspection of both evaluation periods remains disclosed. |
| V09 · model comparison / slide 9 | Long family descriptions distracted from the selection outcome. | Compress family explanations and foreground the screening-to-confirmation ranking change. | Elastic Net remains included; selected tree constraints and the meaning of grey cells remain clear. |
| V10 · trading rule / slide 10 | Definition of basis points lacked a direct conversion for the actual threshold. | State that 15 bps is 0.15%; retain both cost components and entry/exit turnover. | Signed choice, position limits, daily square-off and simulation limitations remain. |
| V11 · demonstration / slides 11–12 | Deck included editing instructions such as accelerated-wait labels; narration implied every field was in one ledger row. | Put production instructions in the unspoken script; show pipeline stages on deck. Distinguish forecast/position records from portfolio ledger fields. | Real execution remains required; an artifact inspection is not represented as a fresh fit. |
| V12 · performance / slide 13 | Plot plus many metric types created a competing set of messages. | Keep the benchmark curve, period return and Sharpe; refer detailed forecast/risk metrics to the report. Avoid repeating every endpoint in the bold takeaway. | Combined and annual/partial-year outcomes remain accurate; overnight exposure, changed fitting schedule and uncertainty remain explained. |
| V13 · cost / slide 14 | Script asked viewers to inspect activity counts that were not on the slide. | Add a visible line: 434 sessions, 14 long, 113 short, 307 flat, zero mixed. Shorten narration around paired bars. | Counts reconcile; gross/net bars use identical trades; compounding caveat remains. |
| V14 · verdicts / slide 15 | H5 wording could confuse a losing year with a statistical refutation of expected profitability. | Explicitly state the distinction; retain uncertainty. Keep H2 pooled and 2026 subgroup findings separate. | No unsupported causal or profitability claim; H4 sample insufficiency and H6 untested causal margin effect remain distinct. |
| V15 · conclusion / slide 16 | Last slide introduced new regime statistics without time to interpret their definitions. | Remove those figures from the timed closing; retain the regime plot in the supporting appendix. Close on three findings and the next credible tests. | Closing synthesizes existing evidence instead of introducing a new analysis. |
| V16 · pacing and maintenance | Shorter narration could become dead time; deck/script edits could drift. | Use a 120-wpm rehearsal budget, explicit visual tasks, fixed slide cues, shared source, and matching-title checks. Preserve the old package in a ZIP. | 16 scenes, four five-minute sections, no narration over budget, final buffer, all cues and titles synchronized. |

## What was deliberately retained

- All six hypotheses, including supported, inconclusive and untested causal claims.
- The architecture as the main explanatory visual, with 105 seconds allocated to it.
- The two motivating papers and the distinction between applying principles and reproducing their studies.
- Daily Indian open-to-close forecasting and the 08:55 IST information cutoff.
- Own-history → peer → U.S. services → wider-market information progression.
- Screening, confirmation, freeze, historical evaluation and extension; no claim of pristine research holdouts.
- Long, short and flat decisions, exposure limits, modeled fees/slippage, and daily square-off.
- Combined January 2025–September 2026 results alongside different period outcomes.
- All four authors and IDs, the NUS cover, Times New Roman, and the 16:9 screen format.
- U.S.–India correlation, event-response and regime figures as optional supporting pages, outside the timed recording. These remain available for questions without crowding the main narrative.

## Quantified editorial changes

The original narration had **2,155 words**; the revision has **1,828**, a reduction of **327 words (15.2%)** under the existing word-count rule. This reduction removes repetition and simplifies delivery rather than deleting the research design.

The fixed schedule remains **20:00**, with four five-minute sections. At the revised rehearsal pace of **120 words per minute**, conservatively rounded scene allowances total **15:19** of narration and **4:41** of visual reading, terminal footage, handovers and the final buffer. This is a production budget, not a measured speaking duration. Do not pad spare time with silence: trace the indicated chart comparison or show the specified real output. Rehearse with the actual footage; retain the 20-minute cap.

| Slides | Presenter role | Allocated time | Purpose of visual time |
|---|---|---|---|
| 1–4 | Question, architecture, hypotheses | 00:00–05:00 | Trace the information-to-trade path and distinguish the research questions. |
| 5–8 | Data, timing, feature test, protocol | 05:00–10:00 | Read the information ladder and locate time boundaries. |
| 9–12 | Models, trading, actual execution | 10:00–15:00 | Inspect model comparison and genuine execution outputs at readable speed. |
| 13–16 | Returns, costs, verdicts, lessons | 15:00–20:00 | Compare curves and cost bars; close by 19:40 with a final buffer. |

## Evidence and implementation trace

Primary requirement: `documents/markdown/Project2.md`, Section 5. It asks for an end-to-end data build → fit → validation → evaluation with costs, economic rationale, assumptions, overfitting controls, position rules and lessons. The revised scenes cover these explicitly. Actual recorded execution still has to be captured by the presenters; document generation does not complete that recording requirement.

Primary research source: `reports/Project2_Team16_Report.docx`. Supporting evidence: the existing publication figure pack and its cost/accounting and position-count CSVs. This revision reuses the reported measurements and does not infer new results from the shorter wording.

Changed implementation:

- `documents/video_presentation_content.py`: narration, titles, deck points, takeaways, screen directions.
- `scripts/build_project2_video_package.py`: clearer architecture labels, reduced results strip, visible activity counts, 120-wpm timing budget.
- `reports/video/README.md`: revised word count, pacing and review link.
- `reports/video/Project2_Team16_Video_{Deck,Script}.{docx,pdf,md}`: synchronized deliverables.
- `reports/video/timing.csv`, `package_manifest.json`, `verification.json`: timing, source/output hashes and checks.

Before-change evidence is preserved in `reports/video/review_archive/before_editorial_review_2026-11-02.zip`, including the former six deliverables, shared source, builder and tracking files. The research report, datasets, training configuration and historical run results are unchanged.

## Remaining production work

1. Record genuine D1–D5 execution as specified in `reports/video/recording_commands.md`; label accelerated waits.
2. Rehearse with all four presenters and the actual footage. A word-count estimate cannot verify pronunciation, pauses or transitions.
3. Confirm the final video is at most 20 minutes, every spoken result matches the displayed saved evaluation, and fresh-run results are not silently substituted for the report's historical results.

These are recording tasks, not unimplemented document changes.
