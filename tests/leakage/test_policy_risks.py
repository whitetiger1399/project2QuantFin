
import pandas as pd
import pytest
from quantfin.cross_market.panel import _scheduled_features

# @pytest.mark.xfail(strict=True, reason="Scheduled event calendar lacks historical announcement/known-at timestamp")
def test_future_unannounced_schedule_must_not_affect_past_features(tmp_path):
    dates = pd.DatetimeIndex(["2025-01-06"])
    p = tmp_path / "events.csv"
    pd.DataFrame({"scheduled_at_utc":["2025-01-08T10:00:00Z"],
                  "announced_at":["2025-01-07T10:00:00Z"]}).to_csv(p,index=False)
    baseline = _scheduled_features(p,dates)
    assert pd.isna(baseline["scheduled__days_to_event"].iloc[0])
