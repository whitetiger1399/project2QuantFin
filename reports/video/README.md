# Team 16 video deck

[Watch the project demonstration on YouTube](https://youtu.be/VhtQpD3C_rs).

The submitted deck presents the research question, architecture, six hypotheses, data and timing controls, model selection, long/short backtesting, transaction costs and results.

| Format | File |
|---|---|
| PDF | [Video deck](Group_16_Video_Deck.pdf) |
| Editable Word | [Video deck](Group_16_Video_Deck.docx) |
| Markdown | [Video deck](Group_16_Video_Deck.md) |

The deck uses a widescreen 16:9 layout. Slides 1–16 form the timed presentation; supporting figures and references follow. `timing.csv` records the planned 20-minute sequence.

[recording_commands.md](recording_commands.md) provides complete instructions for training from bundled preprocessed data or rebuilding from raw inputs. New runs are isolated and preserve the submitted results.

The saved backtest can be checked without training:

```sh
python scripts/recording_evidence.py
```

The narration documents and internal production reviews are excluded from this submission branch. Presentation source code is retained in `documents/video_presentation_content.py` and `scripts/build_project2_video_package.py`.

For an intentional deck rebuild, use the mode that exports only the deck:

```sh
python scripts/build_project2_video_package.py --deck-only
```

After rendering the deck DOCX to PDF, refresh its package hashes:

```sh
python scripts/build_project2_video_package.py --deck-only --finalize
```

`package_manifest.json` records the retained deliverables and source hashes. A model rerun does not automatically replace the deck’s reported results.
