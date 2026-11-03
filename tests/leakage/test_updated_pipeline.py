
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
from quantfin.cross_market.panel import _asof_align, _market_features, _scheduled_features
from quantfin.cross_market.experiments import _winsorize, feature_columns
from quantfin.cross_market.timing import map_release_sessions

SETTINGS = {
    "return_lags": [1, 2, 5], "momentum_windows": [5, 21],
    "volatility_windows": [5, 21], "moving_average_windows": [5, 10],
    "volume_windows": [5, 21], "rsi_window": 14
}

def market(n=90):
    d = pd.bdate_range("2025-01-01", periods=n)
    c = 100 + np.arange(n, dtype=float) * .2 + np.sin(np.arange(n))
    return pd.DataFrame({"session": d, "open": c-.1, "high": c+1,
                         "low": c-1, "close": c,
                         "adjusted_close": c, "volume": np.arange(n)+1000})

def test_asof_excludes_same_day_and_future():
    s = pd.DataFrame({"value": [1.,2.,3.]},
        index=pd.DatetimeIndex(["2025-01-02","2025-01-03","2025-01-06"], name="session"))
    result = _asof_align(s, pd.DatetimeIndex(["2025-01-03","2025-01-06"]))
    np.testing.assert_allclose(result.value.to_numpy(), [1.,2.])

def test_future_ohlc_perturbation_cannot_change_past_features():
    original = market()
    changed = original.copy()
    changed.loc[changed.index >= 60, ["open","high","low","close","adjusted_close","volume"]] *= 4
    first = _market_features(original, SETTINGS).iloc[:60]
    second = _market_features(changed, SETTINGS).iloc[:60]
    assert_frame_equal(first, second)

def test_decision_features_use_previous_completed_stock_session():
    raw = market()
    features = _market_features(raw, SETTINGS)
    aligned = _asof_align(features, pd.DatetimeIndex([raw.session.iloc[55]]))
    assert np.isclose(aligned["intraday_return"].iloc[0], features["intraday_return"].iloc[54])

def test_winsorization_never_learns_from_test_values():
    train = pd.DataFrame({"x": [1.,2.,3.,4.,5.]})
    test = pd.DataFrame({"x": [10.]})
    _, clipped = _winsorize(train, test, [0.1,0.9])
    _, clipped_extreme = _winsorize(train, pd.DataFrame({"x":[1e12]}), [0.1,0.9])
    assert np.isclose(clipped.x.iloc[0], clipped_extreme.x.iloc[0])

def test_current_vintage_fallback_excluded_when_requested():
    dictionary = pd.DataFrame({"feature": ["macro__safe","macro__fallback","own__momentum"],
        "feature_sets":["F4_full_us"]*3,
        "current_vintage_fallback":[False,True,False]})
    selected = feature_columns(dictionary,"F4_full_us",exclude_current_vintage_fallback=True)
    assert "macro__fallback" not in selected
    assert "macro__safe" in selected

def test_release_after_cutoff_is_next_nse_session():
    nse = pd.DatetimeIndex(["2025-01-06","2025-01-07"])
    us = pd.DatetimeIndex(["2025-01-06","2025-01-07"])
    before = map_release_sessions(pd.Timestamp("2025-01-06T03:24:00Z"),nse,us)
    after = map_release_sessions(pd.Timestamp("2025-01-06T03:26:00Z"),nse,us)
    assert before["tradable_date"] == pd.Timestamp("2025-01-06")
    assert after["tradable_date"] == pd.Timestamp("2025-01-07")

def test_us_dst_close_to_next_indian_decision():
    nse = pd.DatetimeIndex(["2025-03-07","2025-03-10","2025-03-11"])
    us = pd.DatetimeIndex(["2025-03-07","2025-03-10"])
    mapped = map_release_sessions(pd.Timestamp("2025-03-10T19:00:00Z"),nse,us)
    assert mapped["first_nse_after_us_reaction_date"] == pd.Timestamp("2025-03-11")
