# Repository cleanup and processed-data distribution — 9 November 2026

## Implemented

| Change | Reason and verification |
|---|---|
| Raw downloads excluded from Git/LFS | Restored `data/raw/*` ignore rule and disabled its LFS filter. Existing raw files remain on disk. |
| Preprocessed training route | `prepare` validates pinned historical/2026 datasets, reuses them read-only, rebases output roots and creates an isolated tracked session. No raw lookup or preprocessing is performed. |
| Rebuild route retained | `build` still requires audited raw inputs and performs cleaning, features and EDA. |
| Single input registry | `data/preprocessed_bundle.json` pins existing panels/configuration hashes with repository-relative paths. No duplicate panels were created. |
| Small CSVs in ordinary Git | Removed the blanket CSV LFS filter. Large daily decision tables and the large S&P historical export retain LFS. CSV bytes are not line-ending-normalized because manifests hash their exact content. |
| README and recording guide | Two complete, separate workflows: bundled processed inputs; code-only download/audit/build. Both describe outputs, sequential training and publishing requirements. |
| Abandoned raw-bundle helper removed | The new, uncommitted `verify_bundled_data.py` belonged to the superseded raw-distribution proposal. Processed verification is now in `load_bundle`. |

## Cleanup review and retained evidence

All Python files under scripts, src and tests were parsed successfully. Active scripts, configs and tests were searched for references to header-only CSVs and manual-source folders. The header-only `nifty_it_membership.csv` and `global_events.csv` are explicitly referenced by source contracts, so they remain input templates; neither is claimed as observed data. Prior user deletions of five optional manual CSVs were left untouched.

Run folders, checkpoints, analysis manifests, CSV metrics, logs, report assets and historical experiment code are retained. An entry point that is absent from the new quick-start is not sufficient evidence that it is unused: these scripts support earlier runs, research comparisons, tests and publication evidence. Their deletion would weaken reproducibility. This pass does not claim that every historical experiment is required by the main training path.

Only regenerable Python bytecode caches and empty external-export directories were removed. No research CSV, raw snapshot, processed panel, log, model result or report was deleted.

Removed local generated/empty paths:

- `scripts/__pycache__`
- `src/quantfin/__pycache__`
- `src/quantfin/cross_market/__pycache__`
- `src/quantfin/data/__pycache__`
- `tests/__pycache__`
- `reports/__pycache__`
- `data/external/source_exports/nse (empty directory)`
- `data/external/source_exports/wrds (empty directory)`

## Checks

- Six orchestration tests passed, including no-raw preparation, read-only inputs, relocated output roots, corrupted-panel rejection, exact-ID dispatch and overwrite protection.
- The actual pinned historical and 2026 panel/configuration hashes were verified without downloads or training.
- Python syntax inventory: {"scripts": 57, "src": 31, "tests": 5}.
- Git ignore/LFS attributes and documentation parity are checked separately in this work session.
- Git staging, committing and pushing are left to the maintainer commands in README; local files are not yet a published branch update.
