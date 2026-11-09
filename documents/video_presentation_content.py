"""Single editorial source for the Team 16 deck and timed narration."""

SCENES = [{'title': 'Cross-Market Forecasting and Signed Trading of Nifty IT Stocks',
  'seconds': 45,
  'speaker': 0,
  'kind': 'cover',
  'takeaway': 'Can information available before the Indian open improve a daily trading decision?',
  'source': 'Report: title page and Section 1; assets/authors.json.',
  'show': 'Keep the title, NUS logo, course, team, four names and IDs visible. Begin the presentation clock '
          'at the first spoken word.',
  'say': 'Hello. We are Team Sixteen. Our project asks whether U.S. market information can help us trade '
         'Indian IT services stocks before the Indian market opens. Each day, the model can choose long, '
         'short, or flat. We also test whether frontier AI releases affect these stocks. We will explain the '
         'design, show the pipeline running, and examine the returns after trading costs. The central '
         'question is simple: does extra information improve a decision we could actually have made at the '
         'time?'},
 {'title': 'The question: can U.S. information help the next Indian trade?',
  'seconds': 60,
  'speaker': 0,
  'kind': 'question',
  'takeaway': 'A cross-market association is a starting point; a profitable trading rule requires a separate '
              'test.',
  'points': ['Targets: ten fixed current Nifty IT members',
             'Inputs: Indian history + completed U.S. sessions',
             'Daily decision: 08:55 IST; trade NSE open → close'],
  'source': 'Report Sections 1–2; Chinco et al. (2019); Kelly et al. (2024).',
  'show': 'Point to the three lines in order. Explain that shares are traded in India and returns are '
          'measured in rupees. Introduce the two papers without reading their titles in full.',
  'say': 'Indian and U.S. services firms share some customers and technology risks. The U.S. session also '
         'finishes before the next Indian open. Could that earlier information help predict the Indian '
         'trading day? We trade only Indian stocks, and predict their return from open to close. The two '
         'papers guide our design. Chinco and coauthors study short-lived signals across stocks, using '
         'penalties to limit complexity. Kelly and coauthors show why richer models can help when complexity '
         'is controlled through shrinkage. We apply those ideas to daily Indian trading; we do not reproduce '
         'their experiments. Our test has three steps: improve the forecast, turn it into a position, and '
         'check the return after costs.'},
 {'title': 'Research architecture: from available data to a daily trade',
  'seconds': 105,
  'speaker': 0,
  'kind': 'architecture',
  'figure': 'video_architecture.png',
  'takeaway': 'Every input must pass the information clock before it can affect a trade.',
  'source': 'Report Figure 1 and Sections 2, 4–5; cross_market/panel.py, timing.py and experiments.py.',
  'show': 'Spend the full slot here. Trace the source groups, then the 08:55 gate, training, forecast, and '
          'three position choices. Pause after each arrow; do not read every box.',
  'say': 'This diagram connects the whole project. On the left, Indian inputs describe each stock, its '
         'peers, and the wider market. U.S. inputs add services firms and broad-market conditions. Rates, '
         'currencies, and dated AI releases provide context. First, everything passes the eight fifty-five '
         'Indian-time gate. We use only information available before that decision. We then construct '
         'features such as past returns, momentum, volatility, and peer movements. The fitting block learns '
         'from earlier observations, including its cleaning and transformation rules. Screening compares '
         'candidates; confirmation selects the settings; the freeze records that choice. Selection happens '
         "during research, while later refits follow the declared schedule. Each day's forecast then "
         "estimates an Indian stock's open-to-close return. A threshold turns that forecast into a long, "
         'short, or flat choice. Exposure limits control the portfolio, and every position closes that day. '
         'Finally, we subtract entry and exit costs. Follow that last link carefully: predicting a return '
         'and earning it after costs are different tests. The next slides unpack the timing, features, and '
         'trading rule behind these boxes.'},
 {'title': 'Six questions guide the experiments',
  'seconds': 90,
  'speaker': 0,
  'kind': 'hypotheses',
  'takeaway': 'Price association, economic performance, and company adaptation are different claims.',
  'points': ['H1  U.S. services returns predict subsequent Indian IT returns',
             'H2  Frontier AI releases precede negative Indian IT returns',
             'H3  The release effect becomes less negative after 2024',
             'H4  Larger capability advances imply larger negative reactions',
             'H5  Signed forecasts produce robust returns after costs',
             'H6  Services firms adapt through AI offerings and workforce change'],
  'source': 'Report Sections 1 and 7; saved hypothesis-analysis protocol.',
  'show': 'Read the intent of each hypothesis, not the whole row. Pause on H5 and H6 to distinguish a '
          'trading test from a descriptive company study. Handover to Ramyani at 05:00.',
  'say': 'We organised the study around six questions. Does U.S. services information help predict Indian IT '
         'returns? Do frontier AI releases precede weaker returns? Has that reaction become less negative '
         'after twenty twenty-four? Do larger capability advances produce stronger negative reactions? Can '
         'our forecasts earn reliable returns after costs? And are services firms adapting through AI '
         'offerings and workforce changes? The first four concern market relationships. The fifth tests the '
         'trading strategy. The sixth examines company disclosures. Keeping these questions separate '
         'matters. An AI offering does not prove an improvement in margins, and a return correlation does '
         'not guarantee a profitable trade. We report what the evidence supports, what contradicts a claim, '
         'and what remains uncertain. These questions developed during historical research, so we treat the '
         'tests as exploratory. Ramyani will now explain the data and timing controls.'},
 {'title': 'Data: ten Indian IT stocks, several information sources',
  'seconds': 75,
  'speaker': 1,
  'kind': 'sources',
  'takeaway': 'A fixed current-member cohort: results do not represent every historical Nifty IT '
              'constituent.',
  'points': ['Yahoo Finance: daily prices, volumes, ETFs and global market context',
             'FRED / ALFRED: rates, yields and macro conditions',
             'Membership histories: public Nifty and S&P reconstructions',
             'AI releases + Epoch AI: dated events and retrospective capability analysis'],
  'source': 'Report Sections 2–3; public sources listed in report references [3]–[8].',
  'show': 'Point to each source and its role. Display the ten company names in a small separate line. Note '
          'that benchmark scores are used retrospectively and are not backfilled into past forecasts.',
  'say': 'We follow ten current Nifty IT members, including TCS, Infosys, Wipro, and HCL Technologies. Their '
         'names are shown below. This is a fixed current-member study, so it cannot represent every company '
         'that once belonged to the index. Yahoo Finance supplies daily prices, volumes, and ETF benchmarks. '
         'FRED and ALFRED supply economic series. Public membership histories support broader Indian and '
         'U.S. inputs. Dated AI releases identify events. Epoch benchmark scores support a separate '
         'retrospective study; we do not backfill them into forecasts made before those scores were '
         'available. Before creating features, we check prices, quarantine invalid rows, and retain genuine '
         'missing values. Source records also preserve the timing and vintage limitations of the economic '
         'data.'},
 {'title': 'Timing: what was known before 08:55 IST?',
  'seconds': 75,
  'speaker': 1,
  'kind': 'clock',
  'takeaway': 'A daily row is safe only when each feature was available before its decision time.',
  'points': ['Before 08:55 IST: completed U.S. session and earlier Indian information',
             'At the NSE open: enter eligible positions',
             'At the NSE close: exit and observe the return label',
             'Inside each fit: filter, impute, winsorize, scale and select using training data'],
  'source': 'Report Sections 2.1 and 3.1; timing.py; experiments.py::_fit_block.',
  'show': 'Trace the timing steps from top to bottom. Contrast a U.S. close already observed with an Indian '
          'close still in the future. Point to the training-only transformation line.',
  'say': "At prediction time, the latest completed U.S. session may be available. Today's Indian close, "
         'high, low, and volume are still in the future and cannot be inputs. Our target is closing price '
         'divided by opening price, minus one. We observe it only after the session ends. Holidays are '
         'matched through trading sessions, rather than a simple calendar-day shift. Preprocessing follows '
         'the same rule. Imputation, outlier cutoffs, scaling, and feature selection learn from the earlier '
         'training window, then apply forward. A full-sample average could otherwise leak future information '
         'into the past. Each rolling fit also leaves a one-session embargo. The key check is whether every '
         'input and fitted transformation existed before the prediction it supports.'},
 {'title': 'More information did not improve the fixed ridge model',
  'seconds': 90,
  'speaker': 1,
  'kind': 'figure',
  'figure': '12_information_ladder.png',
  'takeaway': 'The sharp drop at F5 concerns this fixed-penalty ridge test—not every possible use of U.S. '
              'data.',
  'source': 'Report Figure 5; matched quarterly feature-progression audit; F0–F7 ridge penalty 0.1.',
  'show': 'Explain the rows first: own history, peers, U.S. services, Nifty 50, S&P aggregate, constituents, '
          'AI, full context. Trace F0 to F5 in one year, then compare across years. R² is a forecast score, '
          'not a return.',
  'say': "Read this heatmap from top to bottom. We start with each stock's own history, then add peers, U.S. "
         'services, Nifty Fifty, broad U.S. aggregates, individual S and P stocks, and AI context. Features '
         'include lagged returns, momentum, rolling volatility, and moving-average distances. Each column is '
         'a year. The score compares forecast error with a simple asset-mean forecast; below zero means '
         'worse prediction. The comparison holds the ridge penalty fixed and uses matched stock-session '
         'outcomes. Look at the jump from F4 to F5: adding individual U.S. stocks sharply worsens the score '
         'across years. One volatile year cannot explain that pattern. Redundant inputs and too little '
         'shrinkage are possible explanations, not established causes. This is a fixed linear-model '
         'diagnostic. It does not show that U.S. information is useless, and it is separate from the '
         'selected tree model. The lesson is to test information and complexity together.'},
 {'title': 'Choose settings through 2024; evaluate forward in time',
  'seconds': 60,
  'speaker': 1,
  'kind': 'protocol',
  'takeaway': 'Settings are selected through 2024; 2025 and 2026 use different declared fitting schedules.',
  'points': ['2021–2022: screening; 2023–2024: confirmation',
             '2025: selected settings, quarterly past-only refits',
             'Jan–Sep 2026: same settings, one pre-2026 fit',
             'Both evaluation periods were inspected in earlier research iterations'],
  'source': 'Report Section 5.2; run manifests and freeze record in report Appendix A.',
  'show': 'Distinguish model settings from fitted parameters. Explain that a quarterly refit updates the '
          'estimator but does not choose a new model. Handover to Ritik at 10:00.',
  'say': 'Screening compares candidates in twenty twenty-one and twenty twenty-two. Confirmation uses twenty '
         'twenty-three and twenty twenty-four, then records one set of settings. In twenty twenty-five, we '
         'refit quarterly on earlier observations, using at most twelve hundred and sixty trading sessions. '
         'For January to September twenty twenty-six, we use the same settings but fit once on '
         'pre-twenty-twenty-six data. That boundary is marked on the results graph. Predictions follow time '
         'order, but earlier project iterations had already examined both evaluation periods. These are '
         'historical evaluations, not untouched tests of a newly proposed idea. Ritik will now show how the '
         'models produce a trading ledger.'},
 {'title': 'Confirmation selected Extra Trees',
  'seconds': 75,
  'speaker': 2,
  'kind': 'figure',
  'figure': '11_model_family_evidence.png',
  'takeaway': 'Extra Trees wins the declared confirmation rule; the screening leader does not remain the '
              'leader.',
  'source': 'Report Figure 8 and Section 5.1; screening and confirmation leaderboards.',
  'show': 'Point to histogram boosting in screening, then Extra Trees in confirmation. Explain grey cells as '
          'not evaluated. Do not call the 2025/2026 columns a fresh family search.',
  'say': 'We tested linear penalties, PCA compression, boosting, and Extra Trees. Ridge shrinks '
         'coefficients; Lasso can remove them; Elastic Net combines both effects. Tree models capture '
         'nonlinear relationships. In this chart, histogram boosting leads screening, but its confirmation '
         'Sharpe turns negative. Extra Trees wins the declared confirmation rule. Its two hundred and fifty '
         'trees have depth capped at six, at least forty samples per leaf, and half the features available '
         "at each split. These limits reduce the model's ability to fit small, noisy patterns. Selection "
         'also checks prediction coverage and declared tie-breakers. Elastic Net was included and did not '
         'win. Grey cells mean not evaluated. The later columns assess frozen choices and controls; they are '
         'not another search for the best family.'},
 {'title': 'The trading rule: long, short, or flat',
  'seconds': 75,
  'speaker': 2,
  'kind': 'trading',
  'takeaway': 'The recorded strategy can go long, short or flat, and it charges both entry and exit.',
  'points': ['Long above +15 bps; short below −15 bps; otherwise flat',
             'Up to three stocks per side; gross exposure at most one',
             '5 bps fee/spread proxy + 2.5 bps slippage per side',
             'Net daily return = signed position return − turnover cost'],
  'source': 'Report Section 5.4; experiments.py::_strategy_ledger and _annualized_metrics.',
  'show': 'Point to the threshold line, then the exposure and cost rules. In code, point to the signed gross return, twice-gross '
          'turnover, and net-return calculation. Explain 100 basis points equals one percent.',
  'say': 'The forecast becomes a position through a clear rule. Above fifteen basis points, a stock is '
         'eligible for a long position. Below minus fifteen, it is eligible for a short. Between those '
         'thresholds, it stays flat. Fifteen basis points is zero point one five percent. We take up to '
         'three eligible stocks on each side, with capped weights and total gross exposure at most one. '
         'Every position opens from cash and closes that session. Costs therefore apply twice: five basis '
         'points for fees and spread, plus two and a half for slippage, on each side. We subtract costs from '
         'the signed return and compound the daily net results. This is a historical simulation. Opening '
         'prices approximate fills, and taxes, borrowing restrictions, and market impact are not fully '
         'modelled.'},
 {'title': 'Run the pipeline: build data, then fit candidates',
  'seconds': 75,
  'speaker': 2,
  'kind': 'demo',
  'takeaway': 'The saved panel links source information to dated model predictions.',
  'points': ['Build: audited sources → daily panel + feature dictionary',
             'Fit: earlier observations → later-session predictions',
             'Check: training end precedes the prediction window',
             'Record: completion, settings and input fingerprints'],
  'source': 'Project2.md Section 5; recording_commands.md D1–D2; panel.py and experiments.py.',
  'show': 'Use recording_commands.md D1–D2. Reserve at least 30 seconds for genuine '
          'launch/progress/completion footage and a readable date check. On-screen label during accelerated '
          'footage: ‘Training wait accelerated; commands and outputs are real’. Explain narration over the '
          'relevant output. Do not fill spare time with a static terminal or read hashes aloud.',
  'say': 'First, the builder turns audited sources into a panel and feature dictionary. Screening then fits '
         'candidates on earlier observations and predicts later sessions. Watch the training end date and '
         'the first prediction date: they must be in the right order. The output records settings, input '
         'fingerprints, and checkpoints. We show the actual launch, progress, and completion, with waiting '
         'accelerated and labelled. Now inspect one completed block and its dates.'},
 {'title': 'Run the pipeline: select, freeze, evaluate',
  'seconds': 75,
  'speaker': 2,
  'kind': 'demo',
  'takeaway': 'The freeze links the selected settings to predictions and the post-cost trade ledger.',
  'points': ['Confirm candidates → freeze one specification',
             'Evaluate 2025 → extend through September 2026',
             'Check dates and the link to the frozen settings',
             'Inspect forecasts, positions, gross returns, costs and net returns'],
  'source': 'recording_commands.md D3–D5; verify_ai_capability_pipeline.py; verify_frozen_2026_extension.py.',
  'show': 'Use recording_commands.md D3–D5. Reserve at least 24 seconds for readable output: chosen family, '
          'completion, date check, forecast/position record and portfolio ledger. These may be separate '
          'files; do not imply every field is in one ledger row. If a reproduction selects differently, show '
          "its actual result and distinguish it from the report's saved evaluation. Handover to Victor at "
          '15:00.',
  'say': 'Confirmation compares the promoted candidates, then the freeze records one specification. The '
         'evaluation runner uses it for twenty twenty-five, followed by the twenty twenty-six extension. We '
         'inspect forecasts and positions alongside the daily ledger. The ledger shows gross return, '
         'transaction cost, and net return. Our check verifies that gross minus cost equals net and that '
         'fitting dates precede predictions. This demonstrates the full path from data through validation to '
         'evaluation after costs. Victor will now explain the results.'},
 {'title': 'Returns: +10.37% combined, with very different years',
  'seconds': 90,
  'speaker': 3,
  'kind': 'figure',
  'figure': '08_combined_benchmarks.png',
  'takeaway': 'The model beat passive comparators here; the two periods do not establish stable performance.',
  'source': 'Report Figure 9, Section 6 and selected daily ledgers; ETF comparators include overnight '
            'exposure.',
  'show': 'Trace the model line across the 2026 boundary, then compare the passive lines. Point to period '
          'returns and Sharpe below. Explain 2026 is nine months and the fitting schedule changes. Leave '
          'time to inspect the drawdowns; do not read every plotted value.',
  'say': 'The model gained ten point three seven percent after costs from January twenty twenty-five through '
         'September twenty twenty-six. Over that interval, the Nifty IT ETF lost thirty-three point eight '
         'three percent, Nifty Fifty lost two point two six percent, and holding the fixed stock cohort lost '
         'twenty-five point two eight percent. Follow the blue line across the boundary. The model lost four '
         'point zero four percent in twenty twenty-five, then gained fifteen point zero one percent in the '
         'nine-month extension. Sharpe moved from minus zero point two six to one point four six, but both '
         'uncertainty intervals include zero. The model looks defensive in this sample, rather than '
         'consistently profitable. Remember the comparison: passive holdings stay invested overnight, while '
         'our trades close each day. The fitting schedule also changes at the boundary. These differences '
         'limit what we can attribute to the model alone.'},
 {'title': 'Costs turn the 2025 gross gain into a net loss',
  'seconds': 75,
  'speaker': 3,
  'kind': 'costs',
  'figure': 'video_costs.png',
  'takeaway': '2025: +5.16% gross becomes −4.04% net. The combined ledger is mostly flat or short.',
  'source': 'Report Figures 10–11; 07_cost_accounting.csv; combined ledger activity counts.',
  'show': 'Compare the paired 2025 bars first, then 2026. Point to the visible activity counts below. '
          'Explain that flat means no position that day. Treat the exposure pattern as descriptive; do not '
          'claim it causally explains all returns.',
  'say': 'These bars use exactly the same trades before and after costs. In twenty twenty-five, a five point '
         'one six percent gross gain becomes a four point zero four percent net loss. In the twenty '
         'twenty-six segment, twenty-six point nine five percent gross becomes fifteen point zero one '
         'percent net. The difference includes lost compounding; it is not simply the sum of fees. The '
         'activity counts below help interpret the curve: fourteen long days, one hundred and thirteen short '
         'days, and three hundred and seven flat days. No day held both sides. That pattern is consistent '
         'with defensive behaviour during the sector decline. It also shows why profitability depends on '
         'both signal strength and the cost of acting on it.'},
 {'title': 'What the six tests establish',
  'seconds': 75,
  'speaker': 3,
  'kind': 'verdicts',
  'takeaway': 'Supported association ≠ causality; inconclusive evidence ≠ proof of no relationship.',
  'points': ['H1: U.S.–India association supported; adjusted p = 0.0056',
             'H2: overall inconclusive; negative 2026 association (p = 0.0155, adjusted)',
             'H3: weaker release effects after 2024 remain inconclusive',
             'H4: insufficient scored events: 21 dates; minimum specified = 30',
             'H5: stable post-cost advantage not established; returns vary by period',
             'H6: adaptation documented; its causal effect on margins is untested'],
  'source': 'Report Section 7; date-level HAC regressions, Holm corrections and company disclosures.',
  'show': "Use the same H1–H6 order as slide 04. Point to H1 support, then H2's overall/subgroup "
          'distinction. Explain adjusted p-values account for multiple testing. Group H3/H4 as unresolved '
          'for different reasons. H5 is not rejected just because one year lost money. H6 is descriptive, '
          'not a causal margin test.',
  'say': 'The findings are mixed. H1 supports a positive U.S.-India association after accounting for '
         'multiple tests. H2 is inconclusive overall, although the twenty twenty-six subgroup shows a '
         'negative release-day association after adjustment. That is exploratory evidence, not proof that '
         'releases caused the fall. H3 does not establish that the effect weakened after twenty twenty-four. '
         'H4 has only twenty-one scored event dates, below our specified minimum of thirty. H5 does not '
         'establish a stable advantage after costs. One losing year alone cannot disprove positive expected '
         'returns; the uncertainty and variation across periods are the reason for caution. H6 documents '
         'company adaptation, but does not test whether AI caused higher margins. We therefore distinguish '
         'supported associations, insufficient evidence, and questions our design cannot answer.'},
 {'title': 'The lesson: useful signals must survive timing and costs',
  'seconds': 60,
  'speaker': 3,
  'kind': 'closing',
  'takeaway': 'A reproducible daily trading study with conditional defensive results and clear limits.',
  'points': ['Additional inputs need appropriate complexity control',
             'Costs and exposure change the investment conclusion',
             'Next: matched feature tests, realistic fills, future evaluation',
             'Code, forecasts and daily ledgers make the result reproducible'],
  'source': 'Report Sections 7.4 and 8; regime labels are retrospective; README and recording_commands.md.',
  'show': 'End spoken narration by 19:40. Keep the final slide visible for the final 20-second production '
          'buffer; shorten pauses if behind. Do not add an unscripted extra summary. Sources and command '
          'appendix follow outside the recorded 16 slides.',
  'say': 'The project connects information, prediction, and trading in one reproducible process. More '
         'features hurt the fixed ridge model. The selected tree strategy behaved defensively, but costs '
         'erased its twenty twenty-five gross gain. The next tests should compare features under matched '
         'settings, use more realistic execution, and freeze the method before future data arrive. Our code, '
         'forecasts, and ledgers make these findings inspectable. Thank you.'}]

REFERENCES = [('Assignment',
  'documents/markdown/Project2.md',
  'Sections 4–7: timing, models, evaluation, video and submission'),
 ('Report',
  'reports/Group_16_Report.docx',
  'Presentation source; Appendix A/E maps exact evidence records'),
 ('Chinco et al. (2019)',
  'https://doi.org/10.1111/jofi.12733',
  'Sparse signals in the cross-section of returns'),
 ('Kelly et al. (2024)',
  'https://doi.org/10.1111/jofi.13298',
  'The virtue of complexity in return prediction'),
 ('Market and macro data', 'README.md', 'Yahoo Finance, FRED/ALFRED; public membership reconstructions'),
 ('AI and company context',
  'reports/publication_report_sections.py',
  'Report references include Epoch AI, company disclosures and attributed news')]
