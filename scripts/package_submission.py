#!/usr/bin/env python3
"""Create four submission ZIPs with explicit data and run-evidence boundaries."""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile
from zoneinfo import ZoneInfo

from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
MODES = ('full_data', 'preprocessed_data', 'code_only_with_logs', 'code_only_no_logs')
NAMES = {'full_data': 'Group_16_Code_Full_Data.zip', 'preprocessed_data': 'Group_16_Code_Preprocessed_Data.zip', 'code_only_with_logs': 'Group_16_Code_With_Logs.zip', 'code_only_no_logs': 'Group_16_Code_Only.zip'}
CACHE_PARTS = {'.git', '.venv', '__pycache__', '.pytest_cache', '.ruff_cache', '.cache', 'matplotlib_cache', '.matplotlib-cache'}
STORED = {'.png', '.jpg', '.jpeg', '.pdf', '.docx', '.zip', '.mp4', '.npz'}


def sha256(path):
    result = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def common_exclusion(path):
    parts = path.parts
    if set(parts) & CACHE_PARTS or any(p.endswith('.egg-info') for p in parts):
        return 'local environment, Git metadata or regenerable cache'
    if path.name in {'.DS_Store', '.running'} or path.suffix in {'.pyc', '.pyo'}:
        return 'local cache or process lock'
    if path.name == '.env' or path.name.startswith('.env.') and path.name != '.env.example':
        return 'local credentials'
    if any(p == '_rendered' or p.startswith('_render_') for p in parts):
        return 'local document render cache'
    return None


def data_class(path):
    parts = path.parts
    if len(parts) > 1 and parts[:2] == ('data', 'raw'):
        return 'raw'
    if len(parts) > 1 and parts[:2] == ('data', 'external'):
        return 'source_reference'
    if len(parts) > 1 and parts[:2] == ('data', 'processed'):
        return 'processed'
    if parts[0] == 'artifacts' and any(part in {'processed', 'raw', 'source_exports'} for part in parts):
        return 'processed' if 'processed' in parts else 'raw'
    return 'code_or_evidence'


def included(mode, category, path=None):
    if mode == 'code_only_no_logs':
        relative = Path(path)
        parts = relative.parts
        if parts[0] in {'src', 'scripts', 'configs', 'tests'}:
            return True
        if parts[:2] == ('resources', 'data_templates'):
            return True
        if parts[0] == 'assets':
            return True
        if parts[0] in {'reports', 'documents'} and relative.suffix == '.py':
            return True
        return path in {'README.md', 'pyproject.toml', 'requirements.txt', '.gitignore', '.gitattributes', '.env.example', 'reports/video/recording_commands.md'}
    return mode == 'full_data' or (mode == 'preprocessed_data' and category != 'raw') or (
        mode == 'code_only_with_logs' and category == 'code_or_evidence')


def package_readme(mode):
    description = {
        'full_data': 'Code, preprocessed panels, raw downloads, reference sources and all retained run evidence.',
        'preprocessed_data': 'Code, preprocessed panels, reference sources and all retained run evidence. Raw downloads are excluded.',
        'code_only_with_logs': 'Code, configuration, reports, deck, run logs and model-result evidence. Input raw, reference and processed datasets are excluded.',
        'code_only_no_logs': 'Only source code, configuration, tests, templates, builder assets and usage instructions. No input datasets, logs, run evidence, generated reports or deck.',
    }[mode]
    instructions = (
        'Install the environment as described in README Path A, skipping its Git clone/LFS commands: this ZIP contains actual file contents. Then run:\n\n'
        '```sh\npython scripts/run_recording_demo.py prepare --session archive_demo_01 --workers 3\n'
        'python scripts/run_recording_demo.py screen --session archive_demo_01\n'
        'python scripts/run_recording_demo.py confirm --session archive_demo_01\n'
        'python scripts/run_recording_demo.py evaluate --session archive_demo_01\n'
        'python scripts/run_recording_demo.py results --session archive_demo_01\n```\n'
        if mode not in {'code_only_with_logs', 'code_only_no_logs'} else
        'Install the environment and obtain reference inputs using README Path B. Download raw data, audit it, then run `build`, `screen`, `confirm`, `evaluate` and `results` in that order. This archive cannot train without obtaining the excluded inputs.\n'
    )
    evidence_note = ('No run logs, checkpoints, model outputs or generated deliverables are included. Builder logo assets are retained as code dependencies.\n' if mode == 'code_only_no_logs' else 'Logs, metrics, predictions, checkpoints, plots and report evidence remain in their original paths under `artifacts/`; they are retained model outputs, not bundled training inputs. In the code-only-with-logs archive, historical manifests can refer to deliberately excluded input files.\n')
    return ('# Submission archive: ' + mode + '\n\n' + description + '\n\n'
            'Extract the ZIP and open a terminal inside `project2QuantFin/`. Virtual environments, Git history, credentials and caches are excluded.\n\n'
            + instructions + '\nUse an unused session name. ' + evidence_note + '\n'
            'Submission report filename: `Group_16_Report.pdf` (Project2.md Section 7). ZIP edition names are descriptive; the assignment prescribes no exact ZIP filename.\n\n'
            '`PACKAGE_MANIFEST.json` lists included files with SHA-256 hashes, original run identities, exclusions and the source commit. The full-data archive supports the raw rebuild route as well.\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT.parent)
    parser.add_argument('--replace-existing-dir', type=Path, help='Explicitly replace previous editions from this folder, one at a time after validating their input files.')
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output == ROOT or output.is_relative_to(ROOT):
        parser.error('Use an output folder outside the repository to prevent recursive packaging.')
    output.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(ZoneInfo('Asia/Singapore')).strftime('%Y%m%dT%H%M%S_SGT')
    try:
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    except subprocess.CalledProcessError:
        commit = None
    records = []
    common_skips = []
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        reason = common_exclusion(relative)
        if reason:
            common_skips.append({'path': relative.as_posix(), 'reason': reason})
            continue
        if path.is_symlink():
            raise RuntimeError('Inspect symlink before packaging: ' + str(relative))
        records.append({'path': relative.as_posix(), 'bytes': path.stat().st_size, 'class': data_class(relative)})
    for record in tqdm(records, desc='Hashing submission files', unit='file', dynamic_ncols=True):
        path = ROOT / record['path']
        with path.open('rb') as handle:
            if handle.read(100).startswith(b'version https://git-lfs.github.com/spec/v1'):
                raise RuntimeError('Restore LFS object before packaging: ' + record['path'])
        record['sha256'] = sha256(path)
    summaries = []
    for mode in MODES:
        selected = [r for r in records if included(mode, r['class'], r['path'])]
        omitted = [dict(path=r['path'], reason='excluded input category: ' + r['class']) for r in records if not included(mode, r['class'], r['path'])]
        destination = output / NAMES[mode]
        if args.replace_existing_dir:
            previous_root = args.replace_existing_dir.resolve()
            candidates = sorted(previous_root.glob(f'Project2_Team16_{mode}_*.zip'))
            canonical_previous = previous_root / NAMES[mode]
            if canonical_previous.exists():
                candidates.append(canonical_previous)
            if len(candidates) != 1:
                raise RuntimeError(f'Expected one previous {mode} archive in {previous_root}; found {len(candidates)}. Nothing removed for this edition.')
            previous = candidates[0]
            if destination.exists() and previous != destination:
                raise FileExistsError(destination)
            with zipfile.ZipFile(previous) as old:
                old_manifest = json.loads(old.read('project2QuantFin/PACKAGE_MANIFEST.json'))
                if old_manifest['archive_kind'] != mode:
                    raise RuntimeError('Previous archive has unexpected edition: ' + str(previous))
                for item in old_manifest['files']:
                    relative = item['path'].replace('Project2_Team16_Report.docx', 'Group_16_Report.docx').replace('Project2_Team16_Report.pdf', 'Group_16_Report.pdf')
                    if not (ROOT / relative).is_file():
                        raise RuntimeError('Previous archive contains a file absent from the repository; preserve it before replacement: ' + relative)
            print('Replacing prior edition after checking source files: ' + str(previous), flush=True)
            previous.unlink()
        elif destination.exists():
            raise FileExistsError('Archive already exists; use --replace-existing-dir explicitly: ' + str(destination))
        manifest = {'schema_version': 1, 'archive_kind': mode, 'created_at_sgt': datetime.now(ZoneInfo('Asia/Singapore')).isoformat(),
                    'source_commit': commit, 'source_is_working_tree': True,
                    'description': 'Input datasets and run evidence are included according to this edition; see PACKAGE_README.md.',
                    'files': selected, 'excluded': omitted, 'common_exclusions': common_skips}
        try:
            with zipfile.ZipFile(destination, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as archive:
                for record in tqdm(selected, desc='Packing ' + mode, unit='file', dynamic_ncols=True):
                    path = ROOT / record['path']
                    if path.stat().st_size != record['bytes']:
                        raise RuntimeError('File changed during packaging: ' + record['path'])
                    archive.write(path, 'project2QuantFin/' + record['path'],
                                  compress_type=zipfile.ZIP_STORED if path.suffix.lower() in STORED else zipfile.ZIP_DEFLATED)
                archive.writestr('project2QuantFin/PACKAGE_MANIFEST.json', json.dumps(manifest, indent=2) + '\n')
                archive.writestr('project2QuantFin/PACKAGE_README.md', package_readme(mode))
            with zipfile.ZipFile(destination) as archive:
                bad = archive.testzip()
                if bad:
                    raise RuntimeError('ZIP integrity failure: ' + bad)
                packed_manifest = json.loads(archive.read('project2QuantFin/PACKAGE_MANIFEST.json'))
                names = set(archive.namelist())
                assert all('project2QuantFin/' + r['path'] in names for r in selected)
                # Verify file bytes against the SHA-256 inventory, not only ZIP CRCs.
                for record in tqdm(packed_manifest['files'], desc='Verifying ' + mode, unit='file', dynamic_ncols=True):
                    digest = hashlib.sha256()
                    with archive.open('project2QuantFin/' + record['path']) as handle:
                        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
                            digest.update(chunk)
                    if digest.hexdigest() != record['sha256']:
                        raise RuntimeError('Archive SHA-256 mismatch: ' + record['path'])
        except BaseException:
            # Do not leave an incomplete ZIP looking like a completed deliverable.
            if destination.exists():
                destination.rename(destination.with_suffix('.zip.incomplete'))
            raise
        summaries.append({'archive': destination.name, 'files': len(selected), 'bytes': destination.stat().st_size,
                          'sha256': sha256(destination)})
    index = output / f'archives_{stamp}.json'
    index.write_text(json.dumps({'status': 'complete', 'archives': summaries}, indent=2) + '\n')
    print(json.dumps({'status': 'complete', 'output_directory': str(output), 'index': str(index), 'archives': summaries}, indent=2))


if __name__ == '__main__':
    main()
