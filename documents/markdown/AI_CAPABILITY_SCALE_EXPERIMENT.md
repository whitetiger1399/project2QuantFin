# Frontier-Model Scale and Nifty IT — Separate Capability Experiment

## Research question

Does the officially disclosed scale of a newly released frontier model add
predictive information about U.S. IT-services returns and subsequent Nifty IT
open-to-close returns?

The proposed mechanism is investor concern that increasingly capable models may
substitute for some software-development and IT-services work. This is a testable
hypothesis, not an assumed causal fact. More capable AI may also increase IT
services productivity, margins, consulting demand, and implementation work.

## Descriptive correction

The project benchmark does not show a continuous two-year Nifty IT decline. Its
calendar-year close-to-close returns are approximately +25.2% in 2023, +24.8%
in 2024, and -10.7% in 2025. The experiment therefore tests event-window,
post-U.S.-reaction, and 2025 pressure—not a claim that both 2023 and 2024 fell.

## Measurement policy

Parameter count is not treated as synonymous with intelligence or economic
substitution power. The experiment records:

- officially disclosed total parameters;
- officially disclosed active parameters for mixture-of-experts models;
- whether parameters were disclosed;
- within-provider log parameter change when two comparable disclosures exist;
- provider generation order and global release order;
- exponentially decayed release, generation, and disclosed-scale pressure over
  21, 63, and 252 sessions;
- interactions between capability pressure and the latest completed U.S.
  IT-services return.

Rumoured sizes for GPT, Claude, Gemini, and later Grok models are not imputed.
Their release and provider-generation features remain available, while their
parameter fields remain missing/undisclosed. Dense total parameters and MoE
active parameters remain separate.

## Disclosed-scale sample

The curated parameter subset contains Llama 2, Grok 1, Llama 3, Phi-3 Medium,
Llama 3.1, NVIDIA Llama 3.1 Nemotron 51B, Llama 3.2, and Llama 4 Maverick. Each
record retains an official source URL, architecture note, total parameters, and
active parameters when available.

## Temporal mapping

For a release known only by date, availability is conservatively assigned to
23:59:59 UTC. The direct event window is the first NSE 08:55 IST cutoff strictly
after public availability. The mediated window is the following NSE session,
when the first post-announcement U.S. trading response can be observed before
the Indian decision.

No release information is backdated. All positions are entered at the NSE open
and closed at the same NSE close.

## Information ladder

The first six rungs are unchanged:

1. own-stock history;
2. leave-one-out Nifty IT peers;
3. U.S. IT services;
4. Nifty 50;
5. S&P 500 aggregate;
6. S&P 500 constituents.

Rung 7 adds release and disclosed capability-scale information. Rung 8 adds the
remaining cross-market, macro, enterprise-software, payments, and nonlinear
context. The same ridge penalty and symmetric cost-aware long/short rule are
used across the controlled ladder.

## Evaluation

- Spearman correlation between log disclosed parameters and each Nifty IT
  constituent's direct and mediated event-window returns.
- Correlation with the first observable U.S. IT-services response.
- Event-level scatter plots labelled by model family.
- Incremental OOS performance of F6 capability versus F5 S&P constituents.
- Expected and realized daily net return, annual return, Sharpe, Sortino,
  drawdown, turnover, and transaction costs.
- Every daily stock decision retained as LONG, SHORT, or FLAT.
- The single selected model is frozen on confirmation evidence before the 2025
  historical replication.

## Interpretation limitations

The disclosed subset is small and non-random. Parameter scale is correlated
with calendar time, macroeconomic conditions, changing technology demand, and
provider identity. Consequently, the analysis is exploratory and predictive;
it cannot establish that increasing parameter counts caused Nifty IT returns.

## Benchmark-score extension

Benchmark performance is a more direct capability measure than parameter count,
but scores are usable as trading features only after they were publicly known.
The extension separates two evidence layers:

1. **Release-time developer scores.** A score published with the model release
   can enter the first subsequent NSE decision, with the precise benchmark,
   version, prompting/scaffold, metric, and source retained.
2. **Independent Epoch AI evaluations.** These use a more consistent harness and
   are preferred for scientific comparison, but enter a trading feature only
   from the evaluation publication date—not retroactively from model release.

The primary economically relevant benchmark is SWE-bench Verified because it
measures resolution of real software issues. GPQA Diamond captures difficult
reasoning. MATH Level 5 and Mock AIME provide additional reasoning evidence.
MMLU and HumanEval are retained only as robustness measures because they are
older, increasingly saturated, and may use inconsistent protocols.

Scores remain benchmark-specific. They are not averaged directly across tasks.
For each benchmark the panel records the raw score, an expanding historical
percentile using only scores already available at that date, a new-frontier
improvement over the previous known maximum, the evaluation source, and a
missingness indicator. A composite capability score may be used only if supplied
by an independently documented methodology such as the Epoch Capabilities
Index, and only from its historical publication date.

Current 2026 leaderboard values must never be backfilled into 2023–2025 trading
decisions. Doing so would create direct look-ahead leakage.

This experiment has independent dataset, analysis, run, freeze, checkpoint, and
hash roots. The active AI-services experiment remains unchanged.
