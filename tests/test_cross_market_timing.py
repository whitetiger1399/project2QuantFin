from __future__ import annotations

import unittest

import pandas as pd

from quantfin.cross_market.timing import map_release_sessions


class ReleaseSessionMappingTest(unittest.TestCase):
    def setUp(self) -> None:
        self.nse = pd.DatetimeIndex(["2025-01-03", "2025-01-06", "2025-01-07"])
        self.us = pd.DatetimeIndex(["2025-01-03", "2025-01-06", "2025-01-07"])

    def test_release_before_us_close_uses_same_us_session(self) -> None:
        result = map_release_sessions(pd.Timestamp("2025-01-03 15:00:00Z"), self.nse, self.us)
        self.assertEqual(result["first_us_reaction_session"], pd.Timestamp("2025-01-03"))
        self.assertEqual(result["first_nse_after_us_reaction_date"], pd.Timestamp("2025-01-06"))

    def test_release_after_us_close_uses_next_us_session(self) -> None:
        result = map_release_sessions(pd.Timestamp("2025-01-03 22:00:00Z"), self.nse, self.us)
        self.assertEqual(result["first_us_reaction_session"], pd.Timestamp("2025-01-06"))
        self.assertEqual(result["first_nse_after_us_reaction_date"], pd.Timestamp("2025-01-07"))

    def test_nse_direct_decision_is_independent_of_us_reaction(self) -> None:
        result = map_release_sessions(pd.Timestamp("2025-01-03 02:00:00Z"), self.nse, self.us)
        self.assertEqual(result["tradable_date"], pd.Timestamp("2025-01-03"))
        self.assertEqual(result["first_us_reaction_session"], pd.Timestamp("2025-01-03"))


if __name__ == "__main__":
    unittest.main()
