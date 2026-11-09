#!/usr/bin/env python3
"""Run the real recording pipeline with isolated outputs and persistent IDs."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime, timezone
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
BASES = {
    'source': 'configs/cross_market_ai_services_research.yaml',
    'source_2026': 'configs/cross_market_ai_services_2026_extension.yaml',
    'model': 'configs/cross_market_ai_capability_research.yaml',
    'model_2026': 'configs/cross_market_ai_capability_2026_extension.yaml',
}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, value):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    temp.replace(path)


def final_json(text):
    """Read the last top-level JSON result without choosing any historical run."""
    decoder = json.JSONDecoder()
    records = []
    offset = 0
    while offset < len(text):
        start = text.find('{', offset)
        if start < 0:
            break
        try:
            value, length = decoder.raw_decode(text[start:])
            if isinstance(value, dict):
                records.append(value)
            offset = start + length
        except json.JSONDecodeError:
            offset = start + 1
    if not records:
        raise RuntimeError('The command produced no JSON completion record; inspect its log.')
    return records[-1]


class Demo:
    def __init__(self, folder, state):
        self.folder, self.state = folder, state

    def save(self):
        write(self.folder / 'session.json', self.state)

    def config(self, name):
        return str(self.folder / 'configs' / (name + '.yaml'))

    def run(self, key, script, *args, id_key=None):
        log = self.folder / 'logs' / f'{key}_{uuid4().hex[:8]}.log'
        command = [sys.executable, '-u', str(ROOT / 'scripts' / script), *map(str, args)]
        print('\nRunning:', ' '.join(command), flush=True)
        env = dict(os.environ, MPLBACKEND='Agg', PYTHONUNBUFFERED='1',
                   MPLCONFIGDIR=str(self.folder / 'matplotlib_cache'))
        # Stream child progress live while capturing its exact final ID and log.
        output = []
        with log.open('w', encoding='utf-8') as handle:
            handle.write('COMMAND: ' + json.dumps(command) + '\n')
            with subprocess.Popen(command, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, text=True, bufsize=1) as proc:
                try:
                    for line in proc.stdout:
                        print(line, end='', flush=True)
                        handle.write(line)
                        output.append(line)
                    code = proc.wait()
                except BaseException:
                    proc.terminate()
                    proc.wait()
                    raise
        if code:
            raise RuntimeError(f'{key} failed (exit {code}). Log: {log}')
        result = final_json(''.join(output))
        if result.get('status') in {'failed', 'fail'}:
            raise RuntimeError(f'{key} reported failure. Log: {log}')
        if id_key and not result.get(id_key):
            raise RuntimeError(f'{key} returned no {id_key}. Log: {log}')
        if id_key and id_key != 'freeze_id' and result.get('status') != 'complete':
            raise RuntimeError(f'{key} is not complete. Log: {log}')
        location = result.get('directory') or result.get('path')
        if location and not Path(location).resolve().is_relative_to(self.folder):
            raise RuntimeError(f'Unexpected output outside this demo: {location}')
        self.state['records'][key] = result
        self.save()
        return result.get(id_key) if id_key else result

    def id(self, name, field):
        return self.state['records'][name][field]

    def fit(self, stage, *args):
        return self.run(stage, 'run_cross_market_experiments.py',
                        '--config', self.config('model'),
                        '--dataset-id', self.id('dataset', 'dataset_id'),
                        '--stage', stage, '--profile', 'submission_rerun',
                        '--training-scheme', 'rolling',
                        '--parallel-workers', self.state['workers'], *args, id_key='run_id')

    def build(self):
        for suffix in ['', '_2026']:
            source = self.run('source' + suffix, 'build_cross_market_panel.py',
                              '--config', self.config('source' + suffix), id_key='dataset_id')
            dataset = self.run('dataset' + suffix, 'build_ai_capability_panel.py',
                               '--config', self.config('model' + suffix),
                               '--source-dataset-id', source, id_key='dataset_id')
            self.run('eda' + suffix, 'run_cross_market_analysis.py',
                     '--config', self.config('model' + suffix), '--dataset-id', dataset, id_key='run_id')
        self.run('capability_analysis', 'analyze_ai_capability_effects.py',
                 '--config', self.config('model'), '--dataset-id', self.id('dataset', 'dataset_id'),
                 id_key='analysis_id')

    def confirm(self):
        confirmation = self.fit('confirmation', '--screening-run-id', self.id('screening', 'run_id'))
        self.run('freeze', 'freeze_cross_market_model.py', '--config', self.config('model'),
                 '--confirmation-run-id', confirmation, id_key='freeze_id')

    def evaluate(self):
        freeze = self.id('freeze', 'freeze_id')
        self.fit('final_test', '--freeze-id', freeze)
        self.run('extension', 'run_frozen_2026_extension.py',
                 '--source-config', self.config('model'), '--forecast-config', self.config('model_2026'),
                 '--dataset-id', self.id('dataset_2026', 'dataset_id'), '--freeze-id', freeze,
                 '--start', '2026-01-01', '--end', '2026-09-30', id_key='run_id')

    def results(self):
        import numpy as np
        import pandas as pd
        from quantfin.io import sha256_file
        # Verify every tracked file in this demo, never resolve latest historical IDs.
        for record in self.state['records'].values():
            if not record.get('directory'):
                continue
            folder = Path(record['directory'])
            manifest = read(folder / 'manifest.json')
            if manifest.get('status') != 'complete':
                raise RuntimeError(f'Incomplete artifact: {folder}')
            for relative, expected in manifest.get('files', {}).items():
                if sha256_file(folder / relative) != expected:
                    raise RuntimeError(f'Hash mismatch: {folder / relative}')
        records = self.state['records']
        screening = read(Path(records['screening']['directory']) / 'manifest.json')
        confirmation = read(Path(records['confirmation']['directory']) / 'manifest.json')
        freeze = read(records['freeze']['path'])
        final = read(Path(records['final_test']['directory']) / 'manifest.json')
        if not (confirmation['screening_run_id'] == screening['run_id']
                and freeze['confirmation_run_id'] == confirmation['run_id']
                and final['freeze_id'] == freeze['freeze_id']
                and final['selected_config_id'] == freeze['selected_config_id']):
            raise RuntimeError('Demo selection lineage does not match.')
        self.run('extension_verification', 'verify_frozen_2026_extension.py',
                 '--config', self.config('model_2026'), '--run-id', self.id('extension', 'run_id'))
        summaries = []
        series = []
        for key, period in [('final_test', '2025'), ('extension', '2026 Jan–Sep')]:
            folder = Path(records[key]['directory'])
            manifest = read(folder / 'manifest.json')
            ledger = pd.read_parquet(folder / 'strategy_ledgers.parquet')
            ledger = ledger.loc[ledger.config_id.eq(manifest['selected_config_id'])].sort_values('decision_date')
            if ledger.empty or ledger.decision_date.duplicated().any():
                raise RuntimeError('Missing or duplicate daily returns.')
            if not np.isfinite(ledger[['gross_return', 'trading_cost', 'net_return']]).all().all():
                raise RuntimeError('Non-finite trading returns.')
            if not np.allclose(ledger.gross_return - ledger.trading_cost, ledger.net_return, atol=1e-12, rtol=0):
                raise RuntimeError('Gross minus cost does not equal net.')
            summaries.append({'period': period, 'sessions': len(ledger),
                              'gross_return_pct': 100 * ((1 + ledger.gross_return).prod() - 1),
                              'net_return_pct': 100 * ((1 + ledger.net_return).prod() - 1)})
            series.append(ledger)
            print('\n' + period + ' selected model: ' + manifest['selected_config_id'])
            leaderboard = pd.read_csv(folder / 'leaderboard.csv')
            print(leaderboard.loc[leaderboard.config_id.eq(manifest['selected_config_id'])].to_string(index=False))
            cols = ['decision_date', 'holdings', 'gross_return', 'trading_cost', 'net_return']
            print(ledger[cols].head(5).to_string(index=False))
            print('Plots:', folder / 'plots')
        combined = pd.concat(series, ignore_index=True).sort_values('decision_date')
        if combined.decision_date.duplicated().any():
            raise RuntimeError('Evaluation periods overlap.')
        summaries.append({'period': '2025–Sep 2026 combined', 'sessions': len(combined),
                          'gross_return_pct': 100 * ((1 + combined.gross_return).prod() - 1),
                          'net_return_pct': 100 * ((1 + combined.net_return).prod() - 1)})
        table = pd.DataFrame(summaries)
        table.to_csv(self.folder / 'results.csv', index=False)
        print('\n' + table.to_string(index=False))
        write(self.folder / 'verification.json', {'status': 'pass', 'session_id': self.state['session_id'],
                                                 'checked_at_utc': datetime.now(timezone.utc).isoformat(),
                                                 'checks': ['artifact_hashes', 'selection_lineage', '2026_extension',
                                                            'unique_daily_returns', 'finite_returns', 'cost_arithmetic']})


def load_bundle(path):
    """Validate pinned processed inputs using repository-relative paths only."""
    from quantfin.io import sha256_file
    from quantfin.progress import progress
    bundle_path = Path(path)
    if not bundle_path.is_absolute():
        bundle_path = ROOT / bundle_path
    bundle = read(bundle_path)
    for name in ['model', 'model_2026']:
        entry = bundle['datasets'][name]
        for field in ['directory', 'config']:
            relative = Path(entry[field])
            if relative.is_absolute() or '..' in relative.parts:
                raise ValueError('Bundle paths must be relative to the repository root.')
        folder = ROOT / entry['directory']
        manifest_path = folder / 'manifest.json'
        if sha256_file(manifest_path) != entry['manifest_sha256']:
            raise RuntimeError('Bundle manifest hash mismatch: ' + str(folder))
        manifest = read(manifest_path)
        if manifest.get('status') != 'complete' or manifest.get('dataset_id') != folder.name:
            raise RuntimeError('Bundled dataset is incomplete or has the wrong ID: ' + str(folder))
        for relative, expected in progress(manifest['files'].items(), description='Verifying ' + name, unit='file'):
            file = (folder / relative).resolve()
            if not file.is_relative_to(folder.resolve()) or sha256_file(file) != expected:
                raise RuntimeError('Bundled input missing, an LFS pointer, or changed: ' + str(file))
        if sha256_file(ROOT / entry['config']) != entry['config_sha256']:
            raise RuntimeError('Bundled configuration hash mismatch: ' + entry['config'])
    return bundle


def initialize(folder, workers, bundle_path=None):
    import yaml
    from quantfin.cross_market.common import load_research_config, latest_audit, snapshot_inventory, root_path
    from quantfin.io import sha256_file
    bundle = load_bundle(bundle_path) if bundle_path else None
    configs = {key: load_research_config(path) for key, path in BASES.items()}
    if bundle:
        for name, entry in bundle['datasets'].items():
            if name in ['model', 'model_2026']:
                configs[name] = load_research_config(ROOT / entry['config'])
    else:
        # Check shared read-only raw inputs before creating output.
        for name in ['source', 'source_2026']:
            config = configs[name]
            latest_audit(config['raw_data']['audit_root'])
            snapshot_inventory(config)
            for membership in ['nifty50', 'sp500']:
                path = root_path(config['raw_data']['membership_files'][membership])
                if not path.is_file():
                    raise FileNotFoundError(f'Missing membership data: {path}. Complete README data setup first.')
    folder.mkdir(parents=True, exist_ok=False)
    (folder / 'configs').mkdir()
    (folder / 'logs').mkdir()
    records = {}
    for name, config in configs.items():
        config['outputs'] = {key: str(folder / name / key.removesuffix('_root'))
                             for key in config['outputs']}
        if name.startswith('model'):
            source = 'source_2026' if name.endswith('_2026') else 'source'
            config['capability_data']['source_processed_root'] = str(folder / source / 'processed')
            if bundle:
                dataset = ROOT / bundle['datasets'][name]['directory']
                config['outputs']['processed_root'] = str(dataset.parent)
                key = 'dataset_2026' if name.endswith('_2026') else 'dataset'
                records[key] = {'dataset_id': dataset.name, 'status': 'complete', 'directory': str(dataset),
                                'input_mode': 'bundled_preprocessed'}
        (folder / 'configs' / (name + '.yaml')).write_text(yaml.safe_dump(config, sort_keys=False), encoding='utf-8')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    state = {'session_id': f'demo_{stamp}_{uuid4().hex[:12]}',
             'created_at_utc': datetime.now(timezone.utc).isoformat(), 'workers': workers,
             'input_mode': 'bundled_preprocessed' if bundle else 'raw_build',
             'completed_steps': [], 'records': records,
             'config_hashes': {p.name: sha256_file(p) for p in (folder / 'configs').glob('*.yaml')}}
    if bundle:
        state['bundle_manifest_sha256'] = sha256_file(root_path(bundle_path))
    write(folder / 'session.json', state)
    return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('step', choices=['prepare', 'build', 'screen', 'confirm', 'evaluate', 'results'])
    parser.add_argument('--session', default='video_demo', help='New folder name for this demo; reuse it for subsequent steps.')
    parser.add_argument('--workers', type=int, choices=[1, 2, 3, 4], default=3, help='Set during prepare or build; saved for later stages.')
    parser.add_argument('--bundle', default='data/preprocessed_bundle.json', help='Pinned processed datasets used by prepare; no raw data required.')
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', args.session):
        parser.error('Session name must contain only letters, digits, underscores or hyphens.')
    folder = ROOT / 'artifacts' / 'recording_demos' / args.session
    try:
        if args.step in {'build', 'prepare'}:
            if folder.exists():
                raise RuntimeError('Demo folder already exists. Choose a new --session name for a fresh demo; previous results are preserved.')
            state = initialize(folder, args.workers, args.bundle if args.step == 'prepare' else None)
        else:
            if not (folder / 'session.json').is_file():
                raise RuntimeError('Run the build step for this --session first.')
            state = read(folder / 'session.json')
        order = ['build', 'screen', 'confirm', 'evaluate', 'results']
        effective_step = 'build' if args.step == 'prepare' else args.step
        index = order.index(effective_step)
        if state['completed_steps'] != order[:index]:
            raise RuntimeError(f'Run steps in order. Completed: {state["completed_steps"]}. No completed step is overwritten.')
        from quantfin.io import sha256_file
        for name, expected in state['config_hashes'].items():
            if sha256_file(folder / 'configs' / name) != expected:
                raise RuntimeError('Demo configuration changed after initialization: ' + name)
        demo = Demo(folder, state)
        lock = folder / '.running'
        # Exclusive lock prevents two commands from writing the same session concurrently.
        with lock.open('x') as handle:
            handle.write(str(os.getpid()))
        try:
            print('Demo:', state['session_id'], '\nOutput:', folder, flush=True)
            {'prepare': lambda: None, 'build': demo.build, 'screen': lambda: demo.fit('screening'),
             'confirm': demo.confirm, 'evaluate': demo.evaluate, 'results': demo.results}[args.step]()
            state['completed_steps'].append(effective_step)
            demo.save()
            print(f'Completed {args.step}. Results and logs: {folder}', flush=True)
        finally:
            lock.unlink(missing_ok=True)
    except (OSError, RuntimeError, ValueError, KeyError) as exc:
        parser.exit(1, f'ERROR: {exc}\n')


if __name__ == '__main__':
    main()
