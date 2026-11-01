import unittest

import numpy as np
import pandas as pd

from quantfin.cross_market.hypotheses import (
    regression, adjust_tests, headcount_changes, return_summary, block_indices,
)


class HypothesisTests(unittest.TestCase):
    def test_sparse_period_interaction_is_not_evidence(self):
        data = pd.DataFrame({"y": np.arange(100), "event": [0]*95+[1]*5,
                             "early": [0]*98+[1]*2})
        result = regression(data, "y", ["event"], "event", minimum_events={"early": 8})
        self.assertEqual(result["status"], "insufficient_event_sessions")

    def test_constant_predictor_is_not_estimable(self):
        data = pd.DataFrame({"y": np.arange(100), "x": np.ones(100)})
        self.assertEqual(regression(data, "y", ["x"], "x")["status"], "unidentified_design")

    def test_holm_counts_every_test_and_checks_direction(self):
        rows = [{"pvalue": p, "coefficient": c, "expected_sign": -1}
                for p, c in [(.001, -1), (.04, -1), (.01, 1)]]
        result = adjust_tests(rows)
        self.assertAlmostEqual(result.pvalue_holm.iloc[0], .003)
        self.assertEqual(result.interpretation.iloc[2], "opposite_direction")

    def test_missing_quarter_is_not_qoq(self):
        data = headcount_changes([
            {"company": "A", "period_end": "2026-03-31", "headcount": 100},
            {"company": "A", "period_end": "2026-09-30", "headcount": 110}])
        self.assertTrue(pd.isna(data.iloc[1].headcount_qoq_pct))
        self.assertAlmostEqual(data.iloc[1].headcount_six_month_pct, 10)

    def test_first_day_loss_counts_in_drawdown(self):
        self.assertAlmostEqual(return_summary([-.1, .01])["maximum_drawdown"], -.1)

    def test_block_indices_are_reproducible_and_bounded(self):
        a = block_indices(51, 20, np.random.default_rng(1))
        b = block_indices(51, 20, np.random.default_rng(1))
        np.testing.assert_array_equal(a, b)
        self.assertEqual(len(a), 51)
        self.assertTrue(((a >= 0) & (a < 51)).all())


if __name__ == "__main__":
    unittest.main()
