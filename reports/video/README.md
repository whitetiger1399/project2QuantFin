# Team 16 video package

Prepared 2 November 2026 from `reports/Project2_Team16_Report.docx` and `documents/markdown/Project2.md`. Layout follows the old project’s 960 × 540 pt widescreen deck, including serif typography, NUS cover and restrained academic colors.

| Deliverable | Word | PDF | Markdown |
|---|---|---|---|
| Video deck | [DOCX](Project2_Team16_Video_Deck.docx) | [PDF](Project2_Team16_Video_Deck.pdf) | [MD](Project2_Team16_Video_Deck.md) |
| Narration and screen directions | [DOCX](Project2_Team16_Video_Script.docx) | [PDF](Project2_Team16_Video_Script.pdf) | [MD](Project2_Team16_Video_Script.md) |

Record **slides 1–16 only**. The following three supporting-figure pages and reference page are outside the recording. The deck has 20 pages; the script has 18. Both use 16:9 screen pages. The DOCX text remains editable.

## Timing and proposed presenters

| Time | Presenter | Material |
|---|---|---|
| 00:00–05:00 | PRATYUSH SINHA · A0352482A | Research question, architecture, six hypotheses |
| 05:00–10:00 | RAMYANI PALIT · A0357066X | Sources, information clock, feature complexity, temporal selection |
| 10:00–15:00 | RITIK SRIVASTAVA · A0355860X | Models, backtest, genuine recorded execution |
| 15:00–20:00 | VICTOR LEE CHIA SWEA · A0350886R | Returns, costs, hypothesis verdicts and conclusions |

The narration contains **1,828 words** under the declared counting rule. At 120 words per minute, conservative per-scene narration allowances total 15:19; the remainder is allocated to figures, terminal evidence and transitions. Finish speaking by **19:40** and use the last 20 seconds as the editing buffer. Word count cannot guarantee a person’s actual pace: rehearse once against `timing.csv` and keep the final cut at or below 20:00.

The roles are a proposed recording allocation, not an assertion of past implementation contributions.

## End-to-end demonstration

The assignment requires an end-to-end run on video. [recording_commands.md](recording_commands.md) contains the manual sequence for data build, screening, confirmation, freeze, evaluation, extension and checks. It distinguishes a new run from inspection of the report’s saved results. Genuine waiting may be accelerated with a visible label; no new fitting was performed while preparing these documents.

The read-only command below checks the recorded backtest used in the slides:

```bash
python scripts/recording_evidence.py
```

It passed for 249 sessions in 2025 and 185 in January–September 2026, reproducing −4.04% and +15.01% net period returns. It checks earlier training end dates, gross exposure, entry/exit turnover, the assumed cost rate, and gross-minus-cost ledger arithmetic. See [BACKTEST_AND_VIDEO_REQUIREMENTS_REVIEW.md](BACKTEST_AND_VIDEO_REQUIREMENTS_REVIEW.md) for the implementation review and limits.

## Editing and rebuilding

One source, `documents/video_presentation_content.py`, defines scene titles, spoken text, timing, speaker, screen directions and evidence pointers. Rebuild both documents together:

Each script scene has an explicit **SHOW VIDEO DECK SLIDE XX · PDF PAGE XX** cue, repeats the exact deck title in the screen directions, and states the next slide and change time. Demonstration scenes identify when to switch to the terminal and which slide to return to. These cues are generated from the shared scene order; finalization checks them against the deck titles. After changing slide order or titles, rebuild both documents together rather than editing only one Word file.

```bash
MPLBACKEND=Agg MPLCONFIGDIR=/tmp/quantfin_video_mpl XDG_CACHE_HOME=/tmp/quantfin_video_cache \
  python scripts/build_project2_video_package.py
```

After editing, render both DOCX files to PDF while preserving the custom page size. Review every page. Then run:

```bash
python scripts/build_project2_video_package.py --finalize
```

`package_manifest.json` records input and output SHA-256 hashes, the exact word-count rule and timing budgets. No report, original template, model configuration, dataset or historical run is overwritten by the presentation builder.

## Editorial review · 2 November 2026

The revised package shortens narration by 327 words (15.2%), clarifies the hypothesis verdicts, and simplifies the main results slide. The 20-minute timeline includes deliberate figure reading and genuine demonstration footage; avoid padding it with silent static slides. See [the gap analysis](../../documents/markdown/VIDEO_SCRIPT_DECK_GAP_ANALYSIS_2026-11-02.md) for each change and its acceptance checks. The previous package is preserved in `review_archive/before_editorial_review_2026-11-02.zip`.
