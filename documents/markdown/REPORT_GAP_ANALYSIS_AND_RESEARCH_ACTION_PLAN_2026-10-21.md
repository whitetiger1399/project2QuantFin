# Project 2 — dated gap analysis and research implementation plan

Review date: **21 October 2026, Singapore time**  
Course: Data Science in Quantitative Finance DSA5205  
Team: Project2 Teams 16  
Scope: assignment-to-report review, supported by source code and recorded experiments. This is a new planning document; the 19 October gap analysis and existing report are preserved. No model training or data downloads were performed for this review.

## 1. Assessment and research direction

The current submission has a substantial working foundation: delayed trading execution, training-only preprocessing, 99 features, monthly refits, 37 comparative configurations, chronological screening and confirmation, costs, and a recorded final evaluation. More runtime is useful if it measures a specific effect. The most defensible next experiment is:

> Holding the information set, execution rule and evaluation dates fixed, does increasing random-feature model complexity relative to training sample size improve forecast loss or net timing performance after appropriate shrinkage? Does the result survive random-feature seeds, training windows and simple risk-based benchmarks?

This is an adaptation of Kelly, Malamud and Zhou, not a replication of their monthly market-return study. The assignment permits deeper exploration but explicitly asks for bounded, predeclared searches and grades process rather than profitable outcomes [A, §§4.4–4.9]. A negative complexity result is useful if the experiment actually reaches the intended regime and distinguishes regularization, activity and estimation noise.

Three issues take precedence over a larger search:

1. **Repair the chronology in the report.** The expanded comparison ran after the canonical final evaluation. It is retrospective supporting evidence, not the experiment that generated the earlier freeze.
2. **Measure genuine complexity.** Current RFF sizes are 16, 64 and 256 against a median 2,747 training observations. The largest recorded RFF coefficient/sample ratio is about 0.094; this does not test ratios 10 or 15.
3. **Separate prediction from trading inactivity.** The selected screening RFF traded only three sessions. A high Sharpe from that exposure is weak evidence of reliable market timing. AR also outperformed every shortlisted predictive family on confirmation median annual Sharpe.

## 2. Evidence and what has already improved

The actual DOCX paragraphs and tables were read, together with `Project2.md`, the local converted complexity paper, model and feature configurations, model construction, evaluation, EDA, profiling, verification and reporting code. Existing run metrics, manifests, selections and selected ledger records were inspected. This review is not a new full checkpoint audit or a visual certification of every report page.

| Evidence | Exact object / finding |
|---|---|
| Assignment | `documents/markdown/Project2.md`, §§4.1–4.9, §§5–7 and Appendix B |
| Report reviewed | `reports/Project2_Team16_Report.docx` |
| Earlier analysis retained | `documents/markdown/REPORT_GAP_ANALYSIS_AND_RESEARCH_ACTION_PLAN.md`, dated 19 October |
| Features | `features_yahoo_20261020T055638Z_799f619a4f`; F2 = 99 columns |
| Comparative screening | `models_screening_d7252adb14317fcd`; 37 configurations, 1,776 fits, 1,006 evaluation sessions per configuration |
| Comparative confirmation | `models_confirmation_87083937c8d58d9b`; 5 configurations, 180 fits, 757 sessions per configuration |
| Canonical freeze | `freeze_82db313e0d1839a6`; source is `models_confirmation_96d234651d29fb8c`, not the later comparative confirmation |
| Canonical final run | `models_final_test_3e46f0e36fd220d6`; 144 fits, 1,001 sessions per configuration |
| Complexity implementation | `src/quantfin/models.py`: `RBFSampler`, followed by `NormalizedRidge(alpha = penalty × training rows)` |
| Research scaffolding | `configs/research.yaml` declares additional research intentions; declarations are not evidence that those experiments ran |

Improvements since the earlier analysis: all four authors now appear alphabetically; the report distinguishes warm-up from initial training; imputation is described correctly; final annualized volatility is included; drawdown code includes initial wealth; the ledger has P&L dates; a broad comparison exists. Do not repeat those earlier gaps as if they remain wholly unimplemented.

### 2.1 Actual experiment chronology

All timestamps below are from immutable manifests and shown in UTC to avoid conversion ambiguity.

| Event on 20 October 2026 | UTC time | Consequence |
|---|---|---|
| Canonical freeze created | 06:08:35 | Bound to the earlier single-model confirmation selection |
| Canonical final evaluation completed | 06:12:56 | Final outcomes were available before the expanded comparison |
| Expanded screening started | 06:46:22 | Later retrospective research |
| Expanded screening completed | 06:54:43 | 37 configurations completed |
| Expanded confirmation completed | 06:58:49 | Three predictive candidates plus two controls completed |
| Expanded confirmation selection saved | 07:01:29 | Selected the same RF configuration, but did not create the earlier freeze |

The report's §7.3 currently implies that the expanded confirmation led into the existing freeze. That is incorrect provenance even though the selected RF ID is identical. Correct wording: “The original frozen Random Forest evaluation is retained. A subsequent retrospective comparison on the earlier screening and confirmation periods selected the same specification.” A saved freeze proves artifact ordering within its own chain; it does not prove that the researcher had never seen those market outcomes in earlier work.

### 2.2 Results that should drive the next experiment

| Configuration / stage | Annualized net mean return | Full-stage net Sharpe | Median annual net Sharpe | Interpretation |
|---|---:|---:|---:|---|
| RF screening | 3.73% | 0.597 | 1.206 | Selected by the declared annual-median rule |
| RFF screening, `07171c4e64` | 0.89% | 0.773 | 1.105 | Only 3 active sessions of 1,006; about 0.30% exposure |
| Elastic Net screening, `4150cd34f6` | 1.39% | 0.400 | 0.894 | About 1.09% exposure; also sparse trading |
| AR confirmation | 1.09% | 0.079 | 0.704 | Stronger confirmation selection metric than all three predictive candidates |
| RF confirmation | 0.14% | 0.010 | −0.311 | Best eligible predictive family, not best of all compared models |
| Elastic Net confirmation | −3.90% | −0.448 | −0.774 | Screening gain did not persist |
| RFF confirmation | −2.41% | −0.650 | −1.071 | Sparse screening success did not persist |
| RF canonical final | 2.72% | 0.344 | 0.933 | OOS R² about −0.004; SPY return 11.99%, Sharpe 0.665 |

Thirteen screening configurations have undefined annual-median Sharpe: ten RFF, two Lasso and historical mean. Their zero exposure is a valid strategy outcome, not missing predictions. For the selected RFF, the ledger has one active session in 2015 and two in 2018; 2016 and 2017 are inactive. It also has two P&L observations in 2019 because split membership uses signal date. These details matter more than simply suppressing the NumPy warning.

## 3. One-to-one requirement and integrity gap matrix

Priority P0 means fix before claiming stronger research evidence; P1 means the next substantive experiment; P2 means a conditional extension. “Partial” identifies a specific missing component, not failure of the entire pipeline. File names in implementation columns identify existing change locations or explicitly proposed additions.

| ID / priority | Requirement and present evidence | Specific gap | One implementation action | Acceptance evidence |
|---|---|---|---|---|
| G01 / P0 | §4.5, report §§1, 7 and Appendix A | Comparison/freeze chronology conflated | Add original and retrospective experiment roles plus timestamps to a single report-input manifest; rewrite §7.3 | Every freeze points to its actual selection; no claim that the later comparison preceded it |
| G02 / P0 | §4.7, comparison selection | AR is ineligible, despite stronger confirmation metric | Preserve old rule; introduce a baseline-competitiveness gate for future experiments, allowing “no demonstrated ML improvement” | All controls appear in selection review; RF is labelled best eligible ML candidate only |
| G03 / P0 | §4.7, `evaluation.py` annual median | Undefined years silently disappear from median | Save every year, active sessions, completed round trips, volatility and `metric_status`; explicitly handle all-NaN medians | No empty-slice warning; inactive years remain visible, not changed to zero Sharpe |
| G04 / P0 | §4.9, stage periods | Signal-year evaluation spills into later P&L years | Record both signal bounds and realized P&L bounds; define prospective scoring blocks by realized returns and mature labels | Boundary example covers the two 2019 P&L rows in screening; no two-observation “annual” selection statistic |
| G05 / P0 | Reproducibility, 45-check report badge | `verify_outputs.py` verifies canonical runs, not the added comparison | Extend verifier to the report-input manifest, checking both chains and comparative selection membership | Verification output names every reported run and separately scopes each result |
| G06 / P0 | §4.4, report Figure 4 | Mixed tree leaf counts and RFF coefficients treated as one capacity concept | Label architecture-specific nominal counts; add within-family complexity curves | Main complexity claim derives from controlled RFF sweeps, not a mixed-family scatter |
| G07 / P1 | §4.4, selection rationale | Report lacks a full confirmation table and family assumptions | Add all five confirmation rows and economic assumptions for shrinkage, sparsity, bagging and nonlinear maps | Reader sees AR outperforming shortlisted ML, negative outcomes and inactive baseline |
| G08 / P1 | §4.2, feature table | Counts and representative examples omit complete reproducible definitions | Export feature dictionary from builder with formula, window, units, source, availability and missing policy | All 99 columns resolve to dictionary records; narrative eleven groups reconciles to table's merged categories |
| G09 / P1 | §4.1 and Appendix B, cleaning prose | No compact rule counts or concrete action reconciliation in report | Summarize existing raw/corporate-action audits; inspect dividend and available split events with numeric before/after returns | Show actual examples and tolerance; explicitly state when no split exists in chosen sample |
| G10 / P1 | Optional independent vendor check | Report says Stooq implemented without disclosing skipped comparison | Include `comparison_skipped.json` status and reason in source-quality table | “Implemented” never implies independent vendor verification completed |
| G11 / P1 | §4.9, SPY comparison | Cash zero, benchmark CAGR/drawdown blank, exposure unequal | Fill available SPY risk metrics; add fixed-risk/exposure controls as separate experiments | Same dates/cash/cost conventions; lower drawdown is not automatically labelled timing skill |
| G12 / P1 | §4.6, training details | Solvers and stopping conditions missing from report | Export solver, convergence, actual iterations and parameters per family into appendix | Ridge solve, coordinate descent, boosting rounds and neural epochs distinguished |
| G13 / P0 | §4.5 future experiments | 2022–2025 already observed; new freeze cannot restore independence | Label extensions retrospective; lock design before any genuinely new period is opened | No new “untouched 2022–2025” claim; prior exposure disclosed |
| G14 / P1 | Report references and equations | Complexity paper absent; fixed moving-block implementation cites stationary bootstrap | Cite Kelly et al.; align bootstrap reference with algorithm; typeset appendix subscripts | Formula/citation match implementation; uncertainty described as conditional |
| G15 / P1 | Readable academic report | Manually listed contents have nonmonotone section page numbers; figure caption can cross page | Use updated TOC fields or render-derived page mapping; keep figures with captions | PDF page references match actual headings; no detached figure captions |
| G16 / P1 | §§5–7 delivery | Appendix commands mainly rebuild report; video not established by inspected evidence | Add complete reproducible runbook and verify video availability separately; submission filename `Group_16_Report.pdf` | Clean environment reproduces artifacts; 15–25 minute video and 15–25 page PDF accounted for |

## 4. Complexity experiment: exact definition and implementation

### 4.1 Resolve the ratios before choosing a model

Let d be economic input features (currently 99), T eligible training observations, P generated random features, and K fitted coefficients including the intercept. For RFF-Ridge, K = P + 1; the projection weights are random and fixed, not trained.

- **Primary complexity axis:** c = P/T, with actual K/T also logged. This matches the parameter-versus-observation question motivating Kelly et al. [B].
- **Secondary expansion axis:** e = P/d. It measures how much the input representation expands, not whether the regression is overparameterized relative to observations.
- **Effective flexibility:** ridge degrees of freedom, excluding intercept, `df(λ) = Σ s_j² / (s_j² + Tλ)` for the centered design. Large P need not imply large effective degrees of freedom.

The requested “0.1 to 0.10” has equal endpoints mathematically. This plan interprets the intended sweep as **0.1 through 10, with 15 as an extension**, explicitly including the interpolation region around 1. For example, P = 990 is ten times d = 99 but only c = 0.36 at T = 2,747. Reaching e = 10 therefore does not answer the high-c question.

Use c ∈ {0.1, 0.25, 0.5, 0.75, 1, 1.5, 2, 5, 10, 15}. Set P = round(cT), log rounding, and report the realized ratio. Main experiment uses a fixed rolling T = 504 eligible sessions so each point represents the same sample size. Compare rolling T = 1,260 separately. Retain expanding-window results as a reference, not as an uncontrolled change in T inside the primary curve.

| c = P/T | P at T = 504 | P at T = 1,260 | Purpose |
|---:|---:|---:|---|
| 0.1 | 50 | 126 | Strongly underparameterized control |
| 0.25 | 126 | 315 | Low capacity |
| 0.5 | 252 | 630 | Medium capacity |
| 0.75 | 378 | 945 | Approach interpolation |
| 1 | 504 | 1,260 | Nominal interpolation boundary |
| 1.5 | 756 | 1,890 | Just beyond boundary |
| 2 | 1,008 | 2,520 | Moderate overparameterization |
| 5 | 2,520 | 6,300 | Substantial expansion |
| 10 | 5,040 | 12,600 | Requested high-complexity regime |
| 15 | 7,560 | 18,900 | Stress extension |

Actual interpolation depends on centered design rank, duplicate features and regularization. Do not claim a singularity must occur at exactly c = 1. The current deep profile tops out at 1,024 RFF features; merely selecting it will not implement this experiment.

### 4.2 Controlled design and implementation actions

| ID / priority | Current gap | Specific implementation | Fixed controls and acceptance criterion |
|---|---|---|---|
| C01 / P1 | No ratio-driven estimator specification | Add `complexity_ratio` to model config and resolve P from eligible training rows inside each fit | Log d, T, P, K, rank and K/T; reproduce requested ratios within rounding |
| C02 / P0 | RFF normalization and ridge penalty can confound comparison | Inspect installed `RBFSampler` scaling; choose and record one feature normalization and matching ridge objective | Primary: center and standardize generated columns using training rows only, removing constant columns; do not compare raw penalty numbers across incompatible scales |
| C03 / P1 | Current penalties 0.1 and 1 are narrow | After normalization, predeclare λ ∈ {10⁻⁶, 10⁻⁴, 10⁻², 1, 100, 10,000} for `MSE + λ‖β‖²` | Report all cells including flat forecasts; choose λ using past-only inner folds, never outer block performance |
| C04 / P1 | Single feature-map seed | Use map seeds {17, 29, 43}; extend selected curves to {59, 71} | Report median and seed range; seeds are replications, not candidates to pick the best of |
| C05 / P1 | Different P may create unrelated random projections | Generate one maximum-width frequency bank per seed and input dimension; explicitly slice nested columns | Verify shared columns exactly agree before width-dependent normalization; same seed alone is insufficient assurance |
| C06 / P1 | Repeated dense solves waste compute | Implement primal solve for P < T and dual/Gram solve for P ≥ T; reuse decompositions across λ | Prediction equivalence on a small matrix; residual, condition diagnostics and coefficient norm logged |
| C07 / P1 | Daily binary hurdle differs from paper's strategy | Keep 10 bp hurdle as one fixed arm; separately test predeclared continuous forecast sizing with past-only volatility and capped exposure | Same forecast evaluated under both mappings; do not choose mapping from historical final returns |
| C08 / P1 | No local interpolation study | If pilot shows solver instability, add predeclared c = {0.9, 1.1}; optional ridgeless pseudoinverse diagnostic | Record numerical tolerance/rank; diagnose interpolation without forcing a double-descent story |
| C09 / P1 | Current plot combines architectures | Build c × log(λ) heatmaps plus seed-banded c curves | Show OOS R², net Sharpe, exposure and effective df; a Sharpe improvement alone is insufficient explanation |

Normalization is a central experiment choice. Installed RFF implementations typically use a `sqrt(2/P)` factor to approximate a kernel; as P changes, per-column variance changes. Coupling this representation to `alpha = T × penalty` needs an explicit scaling convention. Do not automatically diagnose all inactive RFF models as a normalization bug: penalty strength, bandwidth, intercept and the 0.001 hurdle can all contribute. Record forecast standard deviation, quantiles, fraction above hurdle, generated-column variance and eigenvalues to distinguish them. The local library implementation and official API documentation [C] should be checked against the pinned installed version before changing behavior.

### 4.3 What would count as evidence for complexity?

For each outer block, choose λ from purged past-only inner folds for each predeclared c; score each c on the same subsequent block. Complexity curves across outer blocks are retrospective comparative evidence. A final operating c must be locked from development evidence before a genuinely new evaluation period is opened.

Evidence is a reasonably broad plateau of gains relative to c < 1 and linear ridge, consistent across seeds and more than one calendar regime, with uncertainty and net costs shown. A single isolated best c/seed/year, tiny exposure, or smaller training loss does not establish improved generalization. Report both prediction and portfolio results because their rankings can differ.

## 5. Epochs, model families and controlled tuning

Ridge and RFF-Ridge use linear algebra, so there are no training epochs to increase. More trees reduce ensemble Monte Carlo noise but do not provide the same capacity axis as neural parameters. Boosting rounds and neural epochs are useful only with chronological stopping and learning curves.

| ID / priority | Model gap | Bounded experiment and implementation | Decision evidence |
|---|---|---|---|
| M01 / P1 | Existing RF fixed at depth 3 | Depth {3, 6, 10}, leaf {20, 50}, trees fixed at 300; 6 configs | Train/inner-validation loss, turnover and stability; no automatic promotion of deepest forest |
| M02 / P2 | Tree-count convergence unknown | For two shortlisted tree structures only, compare 100/300/600 trees | Prediction dispersion across seeds versus seconds; stop when extra trees add negligible stability |
| M03 / P1 | Boosting only 100 rounds | Leaves {7,15}, learning rate {0.03,0.1}, up to 600 rounds; record losses at 50/100/200/400/600 | Past-only validation tail with boundary purge; refit on all eligible rows at selected iteration count |
| M04 / P1 | Linear penalties chosen in raw return units | Preserve existing results; define dimensionless Lasso/Elastic-Net penalties relative to training-derived λ_max; use fractions {0.001,0.01,0.1} | Sparse coefficients and forecast dispersion reported; no accidental all-zero penalty grid |
| M05 / P1 | No epoch learning curves | Add a small MLP: one hidden layer widths {8,32,128}; two weight-decay levels; 3 seeds after pilot | Train/inner-validation MSE by epoch; caps 50/100/200/400, patience 20 with fixed minimum improvement; no random validation split |
| M06 / P2 | No robust-loss sensitivity | Huber regression on same standardized inputs, one bounded robust-loss setting and two regularization levels | Determine whether extremes dominate coefficient fitting without deleting crisis outcomes |
| M07 / P2 | No forecast ensemble | Equal-weight forecasts of at most three development-selected models; optional nonnegative weights fitted within inner folds | Separate calibration from portfolio scoring; compare with strongest member and controls |
| M08 / P2 | Broader neural architectures attractive but unsupported | Consider TCN/LSTM only after MLP and RFF establish a question requiring sequential hidden state | Same horizon, history and dates; parameter count and training cost justified; do not make a Transformer a default upgrade |

For a one-hidden-layer MLP with d inputs, h hidden units and scalar output, K = (d + 2)h + 1. At d = 99, widths 8, 32, 128 imply K = 809, 3,233, 12,929. At T = 504 these already span K/T ≈ 1.61, 6.41, 25.65. Thus a modest neural network can be statistically large even when training is fast. Parameter/input ratios and parameter/sample ratios must both be labelled.

Prefer the implemented histogram boosting family before adding another dependency. XGBoost/CatBoost/LightGBM would be justified by a specific missing capability or matched benchmark, not simply a longer model list. The current 37-configuration comparison already covers eight predictive families.

## 6. Feature engineering and data: information blocks with ablations

Do not add ten adjacent moving-average windows to manufacture dimensionality. Expand **economic information** through feature blocks, and use random features to study representational capacity separately. The existing setup already includes 10/15-day momentum and moving-average measures, calendar cycles, volume and cross-asset features.

| ID / priority | Existing gap | Proposed block / exact construction | Source and leakage control | Acceptance / ablation |
|---|---|---|---|---|
| F01 / P1 | No demonstrated F0/F1/F2 contribution table | Run fixed ridge and RF across existing F0, F1, F2 | Same eligible rows and windows for all blocks | Report paired change in MSE, Sharpe, turnover and exposure; missing feature warm-up must not change test dates |
| F02 / P1 | Trend measures correlated, limited state normalization | Add standardized momentum = trailing return / trailing volatility; 5/20 and 20/60 vol ratios; drawdown duration; 20/60-day recovery fraction | Existing adjusted prices; all windows end at signal close | Add at most 8–12 variables; retain only if incremental evidence exists beyond F2 |
| F03 / P1 | Aggregate cross-asset correlations lack changing exposure | Rolling 60/120-day beta of SPY to QQQ/TLT/GLD; residual momentum; correlation changes over 20 sessions | Fit regressions only to trailing observations | Test as one block; interpret beta as association, not structural causation |
| F04 / P1 | Volatility is trailing-only | VIX level, 5/20-session change, VIX/trailing realized vol | Official Cboe data; timestamp/availability manifest; no historical backfill from future close | Match rows with baseline; report missingness and regime dependence |
| F05 / P1 | No rates/credit context in actual model | DGS10−DGS2, DGS10−DGS3MO, changes in DGS2/DGS10/DFF; optional documented credit spread | FRED/ALFRED or original agency; attach publication/availability date; conservative lag if release time unresolved | As-of join asserts available_at ≤ signal_time; release-day boundary tests |
| F06 / P2 | No macro release state | CPI change, payroll growth, days since release; add surprise only with archived expectation data | ALFRED vintages and official release calendars | Never use latest revised macro series or fabricate consensus; separate monthly value from release date |
| F07 / P1 | Federal-holiday proximity is descriptive and not exchange-specific | Sessions to/from exchange holiday, early-close indicator, month/quarter end | Historical exchange schedule; next scheduled holiday is usable if known then | Correct Good Friday/early-close handling; show cell counts and confidence intervals |
| F08 / P1 | Crisis events only annotations | Maintain two fields: scheduled_event_known_at_signal and retrospective_event_annotation | Scheduled FOMC/CPI/NFP calendars; unscheduled news after publication only | No crisis-end flag or full-period event label in predictive features |
| F09 / P2 | Intraday-range information not tested separately | Overnight gap, open-close return, high-low range normalized by trailing volatility | Consistent OHLC adjustment factors; do not mix raw open with adjusted previous close | Dividend/split-date reconciliation; block ablation versus existing intraday group |
| F10 / P1 | Nonlinear expansions confused with new data | RFF on fixed F2 first, enriched blocks only after independent ablation | Training-only scale/PCA; deterministic seed bank | Distinguish new information effect from greater capacity |
| F11 / P2 | Single horizon limits interpretation | Separate 5-session or monthly target experiment after daily baseline | New labels, realized execution horizon, purge lengths and overlapping-position accounting | Do not score overlapping five-day returns as independent daily portfolio P&L |

FRED's ordinary query defaults to current knowledge; ALFRED real-time periods support retrieving historical information states [D]. A vintage date alone may not identify intraday release time. Store observation date, release date/time, vintage date, availability timestamp, source and transformation separately. Forward carrying an already released macro value with an age field is reasonable; forward filling missing traded prices is a different operation and remains prohibited.

The first complexity study needs **no new data**. For enriched features, request VIX history, release-aware Treasury/policy rates, and historical calendars only after specifying coverage and availability. Annual World Bank indicators, retrospectively rescaled Google Trends pulls, current RSS feeds and hand-picked crisis dummies do not provide a clean immediate improvement for this daily SPY problem. `resources/pytrendsREADME.md`, `BacktestingREADME.md` (bt) and Backtrader documentation are tools, not evidence that those sources or engines are appropriate. An independent small ledger reconciliation can use a backtesting library; replacing the working engine is unnecessary.

## 7. Exhaustive EDA process with a selective report

EDA should answer a research question and trigger a decision. Compute diagnostics broadly, save their underlying tables, and include only the figure answering each question. Initial training supports feature design; later-period EDA is labelled retrospective. Event annotations describe coincidence, not a causal explanation of price movement.

| ID / priority | Question and present gap | Diagnostic / figure to add | Statistical and timing safeguards | Concrete action it informs |
|---|---|---|---|---|
| E01 / P1 | Is apparent signal a data defect? | Coverage/missingness raster by asset and year; rule-count cleaning table; corporate-action event panels | Show original versus cleaned observations and reason codes | Fix source alignment before feature expansion |
| E02 / P1 | Are extreme returns real, and are tails asymmetric? | ECDF and normal QQ plot; KDE by prespecified volatility state; ranked extreme-day table | Fixed bandwidth convention, sample sizes, no automatic crisis deletion | Robust scaling/loss sensitivity, not target clipping |
| E03 / P1 | What persistence is forecastable? | ACF/PACF of returns, ACF of absolute/squared returns, rolling lag associations | Use training data; report intervals and multiple-testing correction for lag search | Select lag blocks and variance states; avoid extrapolating price-level trends |
| E04 / P1 | Are predictors redundant? | Clustered block correlation with 15–25 labelled representatives plus strongest signed pairs | Fit clustering/representative choices on development period; save complete matrix externally | Feature-group ablation and PCA comparison |
| E05 / P1 | Does signal change through time? | Rolling Spearman feature-target IC for 6–8 preselected features, with block-resampled uncertainty | Align delayed labels; choose features before displayed evaluation period | Compare rolling versus expanding estimation |
| E06 / P1 | Are calendar effects supported by enough data? | Month/weekday/holiday mean-return heatmap plus n and uncertainty; separate volatility panel | Calendar-compliant dates; HAC or year/block resampling; FDR across calendar tests | Include calendar block only if repeatable |
| E07 / P1 | Do events coincide with abnormal behavior? | Prespecified −5…+5-session cumulative-return and realized-volatility panels | Avoid overlapping-event double counting; match quiet controls by prior volatility; label descriptive | Quantify event context without claiming causal drivers |
| E08 / P1 | Does the hurdle collapse forecasts into cash? | Forecast ECDF with 0 and 10 bp lines, active-days strip, yearly round-trip count | Same axes across candidates; show all-zero strategies | Diagnose shrinkage, calibration and mapping separately |
| E09 / P1 | Is forecast calibration economically useful? | Forecast decile vs realized mean return with intervals; residuals by prior-volatility decile | Decile boundaries from training/inner folds; autocorrelation-aware intervals | Identify scale bias and risk-dependent failure |
| E10 / P1 | Which model is reliable across regimes? | Model × year OOS R² and net-Sharpe heatmap; grey undefined cells, explicit active counts | Same dates/costs; no cherry-picked crisis windows | Reject single-year winner narratives |
| E11 / P1 | Does added capacity help? | Complexity/shrinkage surfaces and training/validation/OOS learning curves | Same inputs/window/map seeds; log axis; mark c = 1 | Main complexity research result |
| E12 / P1 | Is the gain just lower market exposure? | Wealth/drawdown vs SPY, cash, volatility-managed SPY; turnover-cost frontier | Common realized dates and cash convention; fixed risk target | Distinguish timing from de-risking |
| E13 / P2 | Do model drivers drift? | Grouped permutation-importance and SHAP-by-year panels for shortlisted models | Explain held-out predictions with past-only background; no causal wording | Diagnose reliance on transient predictors |

Main-report figure budget: 8–10 composite figures, normally 2–3 related panels each: data quality; return/tail dependence; selective correlations; calendar/events; forecast activity/calibration; family comparison; complexity/shrinkage; portfolio/risk; attribution drift. Put full matrices, per-trial plots and diagnostics in linked artifacts. Use consistent family colors, vector PDF/SVG where supported, at least readable print-size labels and captions stating sample, dates, units, timing, what is seen and what cannot be inferred. Do not rely on a 300-dpi export to fix physically tiny text.

## 8. Evaluation, interpretation and inference improvements

| ID / priority | Missing element | Implementation action | Completion criterion |
|---|---|---|---|
| V01 / P0 | Data already inspected across phases | Keep historical extension explicitly retrospective; use nested forward folds for procedural discipline | Outer blocks never tune the next winner retrospectively; disclosure remains even with nested folds |
| V02 / P1 | Sparse trading distorts ranking | Primary future ranking uses concatenated net excess-return Sharpe; report annual dispersion and activity alongside it | Predeclare minimum 30 active sessions and 10 completed round trips across development as a practical warning/gate, not a significance theorem; ineligible models retain forecast metrics |
| V03 / P1 | No explicit “do not deploy ML” outcome | Compare candidate with historical mean, AR, SPY and simple volatility-managed timing | No improvement is an allowed conclusion; do not exclude a superior baseline by definition |
| V04 / P1 | Cash and risk fairness | Add cash accrual and excess-return Sharpe as a new convention; fixed 10% volatility-target benchmark, exposure cap 1 | Same cash series/lag and target across models; preserve zero-cash original results |
| V05 / P1 | Fixed threshold can hide useful forecasts | Evaluate one unchanged binary rule plus a separately locked continuous long-only forecast/variance rule | Fit any sizing coefficient in inner folds; show all mapping trials and costs |
| V06 / P1 | Point estimates dominate interpretation | Paired moving-block bootstrap for return and loss differences; blocks {10,20,60}; HAC mean-loss difference | Resample shared dates jointly; distinguish seed variability from sampling uncertainty |
| V07 / P2 | Multiple comparisons | Maintain complete trial registry; apply a prespecified reality-check/SPA-style procedure if making superiority claims | All searched candidates included, no claim that ordinary bootstrap corrects selection bias |
| V08 / P1 | Train/OOS MSE compares different volatility eras | Add naive-relative loss, scaled-target sensitivity and contemporaneous inner-validation curves | A negative train-test MSE gap is not labelled proof against overfitting |
| V09 / P1 | Native impurity importance only | Grouped block permutation, coefficient paths and selected TreeSHAP explanations | Importance shown on OOS dates; correlated feature groups reported; background samples strictly prior |
| V10 / P2 | Excess-return attribution absent | CAPM regression with HAC errors as a descriptive risk decomposition | Report alpha/beta intervals and low-exposure caveat; no causal feature attribution |

Preserve the existing selection rule in the historical run. V02 is a proposed future protocol change, justified by observed sparse activity and therefore itself part of retrospective research. LIME is secondary: unconstrained local perturbations of correlated lagged financial features can create implausible observations. Use it only with a documented local sampling scheme and stability assessment; grouped permutation and SHAP usually answer the current explanation question more directly.

## 9. Compute strategy: spend time on evidence

Recorded screening took about **8 minutes 21 seconds** (06:46:22–06:54:43 UTC) for 1,776 fits; confirmation took about **2 minutes 35 seconds** for 180 fits. These are actual elapsed durations from manifests, not estimates for larger models. The historical hardware plan identifies an M1 MacBook Air with 16 GB RAM; reconfirm available memory and power/thermal conditions before a long run. Target 3–5 hours as a budget, never as a guarantee of stronger results.

### 9.1 Size and solver choices

For float64 Z with T rows and P columns, design memory is 8TP bytes, excluding copies, scaling, workspaces and predictions. At T = 1,260 and c = 15, P = 18,900: Z is approximately 182 MiB, a dense P × P matrix is approximately 2.66 GiB, and a T × T Gram matrix is approximately 12.1 MiB. At T = 504 and P = 7,560, Z is about 29 MiB and the T × T matrix about 1.94 MiB. Multiple work arrays make naive concurrent primal solves risky. For P ≥ T, compute with the dual matrix, and evaluate in feature blocks if necessary.

For centered Z and y:

`β = Zᵀ (ZZᵀ + TλI)⁻¹ y`, with the intercept restored from training means.

Use a stable solve/eigendecomposition rather than an explicit inverse. Reuse one decomposition for every λ at a given fold/seed/P. Nested feature banks permit incremental Gram updates across increasing P if normalization is handled consistently. For much larger T, dual factorization still costs roughly O(T³); profiling remains necessary. Float32 feature storage with float64 solve is a candidate optimization requiring prediction agreement checks, not a default assumption.

### 9.2 Staged workload

| Stage | Prespecified work | Logical workload | Resource decision |
|---|---|---:|---|
| Pilot | T=504, c={0.1,1,10,15}, one seed, 3 representative refit origins, all six λ | 72 coefficient solutions; 12 decompositions if reused | Measure time/RSS/solver residuals; no model selected from pilot test outcomes |
| Primary curve | T=504, 10 ratios, 6 λ, 3 seeds, 48 screening refits | 8,640 fit-equivalent solutions; 1,440 decompositions if reused | This is a response-surface study; retain every cell, not 8,640 independent discoveries |
| Window sensitivity | T=1,260, c={0.5,2,10}, 6 λ, 3 seeds, same 48 refits | 2,592 solutions; 432 decompositions | Run after pilot memory gate; compare all three c values consistently |
| Seed sensitivity | Extend c={0.5,2,10} at T=504 to two more seeds, six λ, 48 refits | 1,728 additional solutions | Quantify seed dispersion, never select winning seed |
| MLP/boosting | Small bounded grids from §5, chronological validation | Separate epoch/round workload | Allocate remaining budget only after complexity pipeline works |

Counts above are the outer response-surface work only. Nested hyperparameter selection adds inner fits. Planner must enumerate those explicitly; it must not advertise 8,640 as the total for a full nested study. A smoke pilot with three calendar origins also does not establish out-of-sample performance.

Use the pilot to allocate the 3–5 hours: approximately 10% diagnostics/profiling, 55% primary complexity experiment, 20% window/seed sensitivity and 15% shortlisted alternatives/interpretation. This allocation is a proposal, adjustable before outcomes are inspected. If the full grid exceeds budget, reduce a prespecified secondary dimension or continue overnight; never stop a model because its interim returns look poor. Record incomplete cells explicitly and do not rank an incomplete experiment as complete.

### 9.3 Engineering changes before a long run

| ID / priority | Existing issue | Implementation action | Acceptance evidence |
|---|---|---|---|
| X01 / P0 | Profiler points to October 19 data and RF only | Add dataset/config/ratio/model arguments to `scripts/profile_compute.py` | Profile actual T/P/solver settings used by proposed experiment |
| X02 / P1 | Per-job ETA ignores model heterogeneity | Log stage, fold, family, P/T, λ, seeds; ETA from recent jobs of comparable complexity | Console shows completed/remaining fits and ETA range without log flooding |
| X03 / P1 | Arrays and decompositions recomputed across shrinkage grid | Cache only by training rows, data hash, transform settings, seed and P | Changing any training boundary invalidates cache; no full-sample preprocessing cache |
| X04 / P1 | Current checkpoints store predictions, not epoch state | Add atomic model/optimizer/RNG/epoch checkpoints for neural fits; retain existing monthly prediction checkpoints | Interrupted/resumed tiny experiment agrees within declared numerical tolerance |
| X05 / P1 | Source hash covers all quantfin Python files | Separate training dependency fingerprint from presentation code fingerprint while recording full revision | Report-only edit does not trigger duplicate expensive training; model edit does invalidate reuse |
| X06 / P1 | No typed invalid-metric reason | Record no-trade, zero-variance, insufficient-observations, failed-fit statuses | Warning suppression never hides invalid training; failed fits cannot rank |
| X07 / P1 | Summarizer labels stage from arguments | Validate manifest stages, dataset/feature/window/cost equality and source selection linkage | Swapped or incompatible runs fail with useful error; comparative CSV has source hashes |
| X08 / P1 | Report uses split sources for RF facts and comparison charts | Use one declarative report manifest with explicit canonical and retrospective roles | Every number and caption points to exact configuration and run; all comparison rows validated |
| X09 / P1 | Cross-platform reporting relies on a user-specific renderer path | Add relative report-export command with discovered LibreOffice and writable cache | macOS/Windows instructions run from repository root; no hardcoded home path required |
| X10 / P1 | Research YAML promises more than runtime supports | Wire only supported options through planner/runner; reject unknown fields | A plan-only command reports resolved folds, horizons, ratios, fits and memory before execution |

Keep one reusable modeling engine with named experiment manifests. No duplicated `v2` implementation tree is needed. An extension configuration is an experiment definition, not a competing production setup. Existing JSON/CSV tracking is sufficient if provenance and resume behavior are correct; MLflow is optional convenience rather than the first task. Keep one large fit active at a time initially; existing tree workers can remain at two with one numerical thread each. Profile before increasing concurrency on shared laptop memory.

## 10. Sequential agent action plan

These are implementation tasks, not claims that the code already supports new flags. Preserve immutable existing results and add new content-addressed experiments within the current architecture.

| Step | Work item and dependency | Concrete deliverable | Exit criterion |
|---:|---|---|---|
| 1 | G01–G07, G13: reconcile facts and chronology | Report-input manifest; chronology table; all confirmation outcomes | Existing canonical freeze and later comparison clearly distinguished |
| 2 | G03–G04, V02: activity and metric audit | `activity_by_year.csv`, boundary audit, metric status schema | Three-session RFF result explained; sparse years and spillovers visible |
| 3 | X07–X08: report/comparison verification | Extended verifier and source-linked fact exports | Every report run covered, not just original 45 checks |
| 4 | C01–C05, V01: lock scientific protocol | Dated complexity specification: ratios, normalization, λ, seeds, windows, sizing and folds | No ambiguous definition of “complexity 10”; retrospective status explicit |
| 5 | C06, X01–X04: build solver and planner | RFF bank, dual ridge, cached shrinkage path, memory/runtime profiler | Small primal/dual equivalence and timing-boundary fixtures pass |
| 6 | E01–E09, F01: analyze existing data first | Focused diagnostic tables/figures and F0/F1/F2 paired ablation | Identify one or two information gaps before new data requests |
| 7 | §9 pilot, then primary c curve | Complete primary experiment with checkpointed cells | All planned cells present or explicitly failed; no silent filtering |
| 8 | Window/seed sensitivity | Seed-banded and window-specific complexity plots | Large-c conclusion survives or fails transparently |
| 9 | F02–F08: add information in blocks | Availability-aware source snapshots and feature dictionary | As-of boundary tests and matched-date ablations pass |
| 10 | M01/M03/M05: focused alternatives | RF capacity, boosting-round and MLP epoch curves | Chronological stopping and numerical convergence recorded |
| 11 | V03–V10: evaluate and explain | Full metric table, risk controls, paired intervals and attribution drift | Baseline superiority/no-improvement outcomes allowed |
| 12 | G14–G16: rebuild research report | 15–25 page report, references, curated figures, exact commands/video plan | Claims match evidence; no promise of publishability or untouched reused data |

Steps 1–5 are prerequisites for an interpretable high-complexity experiment. External macro downloads do not block them. Stop expanding scope once the primary research question has a complete, reproducible answer; additional model families should earn their cost by testing a distinct hypothesis.

## 11. Suggested report allocation after implementation

| Content | Approximate pages | Evidence to prioritize |
|---|---:|---|
| Title, abstract and problem definition | 2 | Full roster, task, hypothesis and research chronology |
| Data quality and timing | 2–3 | Cleaning counts, adjustments, label/entry timeline |
| EDA and feature rationale | 3 | Focused panels and feature-block evidence |
| Models, complexity and temporal design | 3–4 | Exact ratio/objective, grid, folds, solver and compute |
| Comparative results and portfolio evidence | 4–5 | Confirmation table, complexity curves, benchmark/risk/cost outcomes |
| Interpretation, limitations and references | 2–3 | Why gains fail or persist; retrospective status and source citations |
| Reproduction and compact appendix | 2–3 | Exact runs, feature dictionary link and contribution note |

Target about 20–23 pages, adjusted to actual evidence and the assignment's 15–25-page limit. Replace administrative “complete” checklist space with substantive results. A curated report should explain why the RFF signal rarely traded, why AR beat ML on confirmation, and whether a proper high-c experiment changes that evidence.

## 12. Source ledger and review fingerprints

[A] Local assignment: [Project2.md](Project2.md), especially §§4.2–4.9 and §§5–7. This is the authority for assignment requirements.

[B] Kelly, B. T., Malamud, S., and Zhou, K. (2024), “The Virtue of Complexity in Return Prediction,” *Journal of Finance*, 79(1), 459–501, DOI 10.1111/jofi.13298. Local converted paper: [The_Virtue_of_Complexity_in_Return_Prediction.md](The_Virtue_of_Complexity_in_Return_Prediction.md), §V. The local paper describes monthly excess market returns, 15 predictors and rolling 12/60/120-month windows; the daily ETF proposal here is a distinct adaptation. [Author-affiliated publication page](https://www.aqr.com/Insights/Research/Journal-Article/The-Virtue-of-Complexity-in-Return-Prediction), checked 21 October 2026. The paper motivates testing complexity; it does not guarantee that this dataset or strategy will benefit.

[C] [scikit-learn RBFSampler documentation](https://scikit-learn.org/stable/modules/generated/sklearn.kernel_approximation.RBFSampler.html), checked 21 October 2026. Random features approximate a kernel and have their own normalization. Implementation decisions must match the installed scikit-learn 1.7.2 source recorded by current manifests, not assume that the moving stable documentation is the pinned version.

[D] [Federal Reserve Bank of St. Louis: Real-Time Periods](https://fred.stlouisfed.org/docs/api/fred/realtime_period.html), checked 21 October 2026. Supports the distinction between today's revised information and historical vintage availability.

Review fingerprints (SHA-256):

| Reviewed object | SHA-256 |
|---|---|
| `reports/Project2_Team16_Report.docx` | `1ad27549291bedc33ecb46120c462f6c75e96f3d4b77a9dd24ebec4cfa35510e` |
| `documents/markdown/Project2.md` | `66f0175dcfc155e67c922a38e53ce9f73f589c37d736a8b2eb4b7d5af4972220` |
| Earlier gap analysis, retained | `decc026570cad91b2591867fc964d8be35b802ea203cd2a3ee62bb66be8e15de` |

Recommendations are proposed work. Existing artifacts establish completed computational results; they do not establish trading suitability, statistical superiority or publication readiness. This review leaves the existing report and experiment artifacts unchanged.
