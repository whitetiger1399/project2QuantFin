"""Read-only provenance audit of DSA5205 cross-market walk-forward checkpoints."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
STAGES = ('screening', 'confirmation', 'final_test')


def choose_panel(root: Path, explicit: str | None) -> Path:
    if explicit:
        return (root / explicit).resolve()
    paths = sorted((root / 'data/processed/cross_market').glob('cross_market_panel_*/panel.parquet'))
    if not paths:
        raise FileNotFoundError('No cross-market panel found')
    if len(paths) > 1:
        raise ValueError('Multiple panels found: specify --panel to prevent mixing dataset versions')
    return paths[0]


def audit(root: Path, panel_path: Path, runs: list[str], window: int, embargo: int, minimum_rows: int, output: Path) -> int:
    panel = pd.read_parquet(panel_path, columns=['decision_date', 'asset', 'target_oc_return'])
    panel['decision_date'] = pd.to_datetime(panel['decision_date']).dt.normalize()
    dates = pd.DatetimeIndex(sorted(panel.decision_date.dropna().unique()))
    counts = panel.groupby('decision_date').size()
    bad_labels = panel.groupby('decision_date')['target_oc_return'].apply(lambda s: s.isna().any())
    rows = []
    for run_id in runs:
        directory = root / 'artifacts/cross_market/runs' / run_id
        manifest_path = directory / 'manifest.json'
        if not manifest_path.exists():
            raise FileNotFoundError(manifest_path)
        manifest = json.loads(manifest_path.read_text())
        if manifest.get('training_scheme') != 'rolling':
            raise ValueError(f'{run_id}: not a rolling run')
        paths = sorted((directory / 'checkpoints').glob('*/*.json'))
        if not paths:
            raise ValueError(f'{run_id}: no checkpoint JSON files')
        for path in paths:
            record = json.loads(path.read_text())
            block_start = pd.Timestamp(record['block_start']).normalize()
            prior = dates[dates < block_start]
            if embargo:
                prior = prior[:-embargo]
            expected = prior[-window:]
            expected_start = expected.min() if len(expected) else pd.NaT
            expected_end = expected.max() if len(expected) else pd.NaT
            expected_rows = int(counts.reindex(expected, fill_value=0).sum())
            observed_start = pd.Timestamp(record['training_start']).normalize()
            observed_end = pd.Timestamp(record['training_end']).normalize()
            conditions = {
                'start_matches': observed_start == expected_start,
                'end_matches': observed_end == expected_end,
                'dates_match': int(record['training_dates']) == len(expected),
                'rows_match': int(record['training_rows']) == expected_rows,
                'minimum_rows': expected_rows >= minimum_rows,
                'training_before_block': observed_end < block_start,
                'labels_nonmissing': not bool(bad_labels.reindex(expected, fill_value=True).any()),
                'block_date_in_panel': block_start in dates,
                'config_id_matches_path': record.get('config_id') == path.parent.name,
                'checkpoint_filename_matches': path.stem == str(block_start.date()),
            }
            rows.append({
                'run_id': run_id, 'stage': manifest.get('stage'),
                'config_id': record.get('config_id'), 'block_start': str(block_start.date()),
                'training_start': str(observed_start.date()), 'training_end': str(observed_end.date()),
                'expected_training_start': str(expected_start.date()) if pd.notna(expected_start) else '',
                'expected_training_end': str(expected_end.date()) if pd.notna(expected_end) else '',
                'training_dates': record['training_dates'], 'training_rows': record['training_rows'],
                'expected_rows': expected_rows,
                **conditions, 'pass': all(conditions.values()),
            })
        declared = manifest.get('checkpoint_count')
        if declared is not None and int(declared) != len(paths):
            print(f'FAIL {run_id}: manifest declares {declared}, found {len(paths)} checkpoints')
    result = pd.DataFrame(rows)
    output.mkdir(parents=True, exist_ok=True)
    result.to_csv(output / 'training_provenance.csv', index=False)
    summary = result.groupby(['run_id', 'stage'], dropna=False).agg(checkpoints=('pass', 'size'), passed=('pass', 'sum')).reset_index()
    summary['failed'] = summary.checkpoints - summary.passed
    summary.to_csv(output / 'training_provenance_summary.csv', index=False)
    print(summary.to_string(index=False))
    failures = result.loc[~result['pass']]
    if not failures.empty:
        print('\nFAILURE EXAMPLES:')
        print(failures.head(15).to_string(index=False))
    print('\nNOTE: Date-level label checks assume same-day OC returns are available before the next refit. Actual 08:55 release timestamps and model replay remain unverified.')
    return 1 if len(failures) else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--panel', help='Panel path, relative to repository root')
    parser.add_argument('--runs', nargs='+', required=True, help='Exact run directory names')
    parser.add_argument('--window', type=int, default=1260)
    parser.add_argument('--embargo', type=int, default=1)
    parser.add_argument('--minimum-rows', type=int, default=5000)
    parser.add_argument('--output', default='audits/training_provenance')
    args = parser.parse_args()
    root = args.root.resolve()
    return audit(root, choose_panel(root, args.panel), args.runs, args.window, args.embargo, args.minimum_rows, root / args.output)

if __name__ == '__main__':
    raise SystemExit(main())
