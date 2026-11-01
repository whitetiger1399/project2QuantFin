import unittest

import numpy as np
import pandas as pd

from quantfin.cross_market.experiments import _annualized_metrics, _strategy_ledger, feature_columns


class EvaluationAccountingTest(unittest.TestCase):
    def test_drawdown_includes_initial_capital(self):
        metrics = _annualized_metrics(pd.Series([-0.10, 0.05]), 252)
        self.assertAlmostEqual(metrics["maximum_drawdown"], -0.10)

    def test_sortino_uses_target_downside_deviation(self):
        values = pd.Series([-0.02, 0.01, 0.03])
        expected_downside = np.sqrt(np.mean(np.square(np.minimum(values, 0)))) * np.sqrt(252)
        expected = values.mean() * 252 / expected_downside
        self.assertAlmostEqual(_annualized_metrics(values, 252)["sortino"], expected)

    def test_strict_vintage_and_family_exclusions(self):
        dictionary = pd.DataFrame({
            "feature": ["own__lag", "macro__revised", "us_it_services__return", "ai_event__today"],
            "feature_sets": ["F7", "F7", "F7", "F7"],
            "current_vintage_fallback": [False, True, False, False],
        })
        selected = feature_columns(
            dictionary,
            "F7",
            exclude_current_vintage_fallback=True,
            excluded_feature_families=["ai_event"],
        )
        self.assertEqual(selected, ["own__lag", "us_it_services__return"])

    def test_timing_only_strategy_uses_equal_weight_cohort(self):
        predictions = pd.DataFrame({
            "decision_date": [pd.Timestamp("2025-01-02")] * 2,
            "asset": ["A", "B"],
            "prediction": [-0.01, -0.02],
            "target_oc_return": [-0.01, 0.02],
            "benchmark_nifty_it_cc_return": [0.0, 0.0],
            "benchmark_nifty50_cc_return": [0.0, 0.0],
            "benchmark_cohort_ew_oc_return": [0.005, 0.005],
        })
        config = {"strategy": {"primary": {
            "name": "cohort_mean_signed", "one_way_cost_bps": 5, "slippage_bps": 2.5,
            "forecast_hurdle": 0.0005, "top_k": 3, "short_k": 3,
            "maximum_weight": 1 / 3, "maximum_gross_exposure": 1.0,
        }}}
        ledger = _strategy_ledger(predictions, config).iloc[0]
        self.assertEqual(ledger["short_holdings"], "A|B")
        self.assertAlmostEqual(ledger["gross_exposure"], 2 / 3)
        self.assertLess(ledger["net_return"], ledger["gross_return"])


if __name__ == "__main__":
    unittest.main()
