from pathlib import Path
p=Path('src/quantfin/cross_market/panel.py')
s=p.read_text(); a=s.index('def _scheduled_features('); b=s.index('\n\ndef _manual_context_features(',a)
replacement='''def _scheduled_features(path: Path, dates: pd.DatetimeIndex) -> pd.DataFrame:
    """Scheduled-event features only from schedules known by 08:55 IST."""
    result = pd.DataFrame(np.nan, index=dates, columns=[
        "scheduled__days_since_event", "scheduled__days_to_event"], dtype=float)
    if not path.is_file():
        return result
    events = pd.read_csv(path)
    if events.empty or "scheduled_at_utc" not in events:
        return result
    known_column = next((c for c in ("known_at_utc", "announced_at_utc", "announced_at")
                         if c in events.columns), None)
    if known_column is None:
        return result  # Fail closed; actual release time is not announcement time.
    scheduled = pd.to_datetime(events["scheduled_at_utc"], utc=True, errors="coerce")
    known = pd.to_datetime(events[known_column], utc=True, errors="coerce")
    event_dates = scheduled.dt.tz_convert("Asia/Kolkata").dt.tz_localize(None).dt.normalize()
    valid = scheduled.notna() & known.notna() & (known <= scheduled)
    for date in dates:
        day = pd.Timestamp(date).normalize()
        cutoff = (day.tz_localize("Asia/Kolkata") + pd.Timedelta(hours=8, minutes=55)).tz_convert("UTC")
        eligible = pd.DatetimeIndex(event_dates.loc[valid & (known <= cutoff)].unique()).sort_values()
        previous = eligible[eligible < day]
        future = eligible[eligible >= day]
        result.loc[date, "scheduled__days_since_event"] = (day - previous[-1]).days if len(previous) else np.nan
        result.loc[date, "scheduled__days_to_event"] = (future[0] - day).days if len(future) else np.nan
    return result
'''
p.write_text(s[:a]+replacement+s[b:]); print('Patched',p)
