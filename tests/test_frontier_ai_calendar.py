from __future__ import annotations

import unittest
from pathlib import Path
from urllib.parse import urlparse

import yaml


ROOT = Path(__file__).resolve().parents[1]


class FrontierAICalendarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = yaml.safe_load(
            (ROOT / "configs/frontier_ai_release_whitelist.yaml").read_text(encoding="utf-8")
        )
        cls.events = cls.config["events"]

    def test_identifiers_dates_and_sources_are_valid(self) -> None:
        policy = self.config["policy"]
        identifiers = [event["event_id"] for event in self.events]
        self.assertEqual(len(identifiers), len(set(identifiers)))
        for event in self.events:
            self.assertLessEqual(policy["coverage_start"], event["release_date"])
            self.assertLessEqual(event["release_date"], policy["coverage_end"])
            self.assertEqual(urlparse(event["source_url"]).scheme, "https")
            self.assertFalse(event.get("selection_used_returns", False))

    def test_2026_primary_provider_coverage_is_frozen(self) -> None:
        expected = {
            "Anthropic": 10,
            "Google DeepMind": 6,
            "Meta": 4,
            "OpenAI": 5,
            "xAI": 1,
        }
        observed: dict[str, int] = {}
        for event in self.events:
            if event["release_date"].startswith("2026-"):
                observed[event["provider"]] = observed.get(event["provider"], 0) + 1
                self.assertTrue(event["primary_event"])
        self.assertEqual(observed, expected)
        self.assertEqual(self.config["policy"]["coverage_end"], "2026-09-30")


if __name__ == "__main__":
    unittest.main()
