import pandas as pd
from quantfin.cross_market.panel import _scheduled_features

def test_unannounced_event_excluded(tmp_path):
    p=tmp_path/'events.csv'
    pd.DataFrame([{'scheduled_at_utc':'2025-01-08T10:00:00Z','known_at_utc':'2025-01-07T10:00:00Z'}]).to_csv(p,index=False)
    r=_scheduled_features(p,pd.DatetimeIndex(['2025-01-06','2025-01-08']))
    assert pd.isna(r.loc['2025-01-06','scheduled__days_to_event'])
    assert r.loc['2025-01-08','scheduled__days_to_event']==0

def test_missing_announcement_fails_closed(tmp_path):
    p=tmp_path/'events.csv'
    pd.DataFrame([{'scheduled_at_utc':'2025-01-08T10:00:00Z','actual_release_at_utc':'2025-01-08T10:00:00Z'}]).to_csv(p,index=False)
    r=_scheduled_features(p,pd.DatetimeIndex(['2025-01-06']))
    assert pd.isna(r.loc['2025-01-06','scheduled__days_to_event'])

def test_after_cutoff_is_not_same_day_known(tmp_path):
    p=tmp_path/'events.csv'
    pd.DataFrame([{'scheduled_at_utc':'2025-01-10T10:00:00Z','known_at_utc':'2025-01-06T03:26:00Z'}]).to_csv(p,index=False)
    r=_scheduled_features(p,pd.DatetimeIndex(['2025-01-06','2025-01-07']))
    assert pd.isna(r.loc['2025-01-06','scheduled__days_to_event'])
    assert r.loc['2025-01-07','scheduled__days_to_event']==3
