"""Deck-only distribution must not recreate removed narration documents."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('video_builder', ROOT / 'scripts/build_project2_video_package.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class DeckOnlyTests(unittest.TestCase):
    def test_markdown_keeps_deck_and_omits_narration(self):
        module, authors = builder.load()
        with tempfile.TemporaryDirectory() as tmp, patch.object(builder, 'OUT', Path(tmp)):
            builder.markdown(module, authors, deck_only=True)
            self.assertTrue((Path(tmp) / 'Group_16_Video_Deck.md').is_file())
            self.assertFalse((Path(tmp) / 'Project2_Team16_Video_Script.md').exists())

    def test_deck_only_dispatch_never_exports_script(self):
        with tempfile.TemporaryDirectory(dir=ROOT, prefix='.video-test-') as tmp:
            folder = Path(tmp)
            (folder / 'recording_commands.md').write_text('fixture')
            with patch.object(builder, 'OUT', folder), \
                 patch('sys.argv', ['builder', '--deck-only']), \
                 patch.object(builder, 'figures'), \
                 patch.object(builder, 'deck') as deck, \
                 patch.object(builder, 'script') as script, \
                 patch.object(builder, 'markdown') as markdown:
                builder.main()
                deck.assert_called_once()
                script.assert_not_called()
                self.assertTrue(markdown.call_args.kwargs['deck_only'])


if __name__ == '__main__':
    unittest.main()
