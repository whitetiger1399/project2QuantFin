"""Recording orchestration checks: no downloads or estimators are executed."""
import importlib.util
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('recording_demo', ROOT / 'scripts/run_recording_demo.py')
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


class RecordingDemoTests(unittest.TestCase):
    def test_completion_id_not_starting_id_or_nested_record(self):
        output = 'progress\n{"run_id":"old","status":"starting"}\n'
        output += '{"run_id":"exact","status":"complete","nested":{"run_id":"wrong"}}\n'
        self.assertEqual(demo.final_json(output)['run_id'], 'exact')

    def test_isolated_configs_and_existing_folder_protection(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / 'session'
            with patch('quantfin.cross_market.common.latest_audit'), patch('quantfin.cross_market.common.snapshot_inventory'):
                state = demo.initialize(folder, 3)
                configs = {key: yaml.safe_load((folder / 'configs' / (key + '.yaml')).read_text()) for key in demo.BASES}
                for config in configs.values():
                    for destination in config['outputs'].values():
                        self.assertTrue(Path(destination).is_relative_to(folder))
                self.assertEqual(configs['model']['capability_data']['source_processed_root'], configs['source']['outputs']['processed_root'])
                self.assertEqual(configs['model_2026']['capability_data']['source_processed_root'], configs['source_2026']['outputs']['processed_root'])
                previous = (folder / 'session.json').read_bytes()
                with self.assertRaises(FileExistsError):
                    demo.initialize(folder, 3)
                self.assertEqual((folder / 'session.json').read_bytes(), previous)
                self.assertTrue(state['session_id'].startswith('demo_'))

    def test_model_dispatch_uses_saved_exact_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            runner = demo.Demo(Path(tmp), {'workers': 3, 'records': {
                'dataset': {'dataset_id': 'this_demo_dataset'},
                'dataset_2026': {'dataset_id': 'this_demo_extension_dataset'},
                'freeze': {'freeze_id': 'this_demo_freeze'},
            }})
            with patch.object(runner, 'run') as run:
                runner.evaluate()
            first, second = run.call_args_list
            self.assertIn('this_demo_dataset', first.args)
            self.assertIn('this_demo_freeze', first.args)
            self.assertNotIn('--resume-run-id', first.args)
            self.assertIn('this_demo_extension_dataset', second.args)
            self.assertIn(runner.config('model'), second.args)
            self.assertIn(runner.config('model_2026'), second.args)

    def test_repeated_build_exits_before_any_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / 'artifacts/recording_demos/existing'
            folder.mkdir(parents=True)
            marker = folder / 'important.txt'
            marker.write_text('keep')
            with patch.object(demo, 'ROOT', Path(tmp)), patch('sys.argv', ['runner', 'build', '--session', 'existing']), patch.object(demo, 'initialize') as initialize:
                with self.assertRaises(SystemExit) as exc:
                    demo.main()
                self.assertEqual(exc.exception.code, 1)
                initialize.assert_not_called()
            self.assertEqual(marker.read_text(), 'keep')


    def bundle_fixture(self, root):
        from quantfin.cross_market.common import load_research_config
        bundle = {'datasets': {}}
        for name in ['model', 'model_2026']:
            folder = root / name / 'panel_test'
            folder.mkdir(parents=True)
            panel = folder / 'panel.parquet'
            panel.write_bytes(b'small fixture: never used for model training')
            manifest = {'status': 'complete', 'dataset_id': folder.name,
                        'files': {'panel.parquet': hashlib.sha256(panel.read_bytes()).hexdigest()}}
            (folder / 'manifest.json').write_text(json.dumps(manifest))
            config = root / (name + '.yaml')
            config.write_text(yaml.safe_dump(load_research_config(demo.BASES[name])))
            bundle['datasets'][name] = {
                'directory': str(folder.relative_to(root)), 'config': config.name,
                'manifest_sha256': hashlib.sha256((folder / 'manifest.json').read_bytes()).hexdigest(),
                'config_sha256': hashlib.sha256(config.read_bytes()).hexdigest()}
        path = root / 'bundle.json'
        path.write_text(json.dumps(bundle))
        return path

    def test_preprocessed_prepare_never_requires_raw_and_rebases_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = self.bundle_fixture(root)
            before = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
            with patch.object(demo, 'ROOT', root), \
                 patch('quantfin.cross_market.common.snapshot_inventory', side_effect=AssertionError('raw accessed')), \
                 patch('quantfin.cross_market.common.latest_audit', side_effect=AssertionError('raw accessed')):
                state = demo.initialize(root / 'new_session', 2, bundle)
            self.assertEqual(state['input_mode'], 'bundled_preprocessed')
            self.assertEqual(state['records']['dataset']['directory'], str(root / 'model/panel_test'))
            copied = yaml.safe_load((root / 'new_session/configs/model.yaml').read_text())
            self.assertEqual(copied['outputs']['processed_root'], str(root / 'model'))
            self.assertTrue(Path(copied['outputs']['runs_root']).is_relative_to(root / 'new_session'))
            for path, content in before.items():
                self.assertEqual(path.read_bytes(), content)

    def test_corrupt_preprocessed_input_refused_before_session_created(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = self.bundle_fixture(root)
            (root / 'model/panel_test/panel.parquet').write_bytes(b'corrupt or unexpanded LFS pointer')
            with patch.object(demo, 'ROOT', root):
                with self.assertRaisesRegex(RuntimeError, 'Bundled input'):
                    demo.initialize(root / 'new_session', 2, bundle)
            self.assertFalse((root / 'new_session').exists())


if __name__ == '__main__':
    unittest.main()
