"""Exchange-clock helpers for release-event research.

The functions in this module deliberately separate three estimands:
the first NSE decision cutoff after publication, the first completed U.S.
session after publication, and the first NSE decision cutoff after that U.S.
close.  A calendar date is not used as a substitute for an exchange session.
"""

from __future__ import annotations

import pandas as pd


def session_close_utc(sessions: pd.DatetimeIndex, timezone: str, hour: int, minute: int = 0) -> pd.Series:
    """Return timezone-aware UTC close timestamps indexed by local session date."""
    local_dates = pd.DatetimeIndex(pd.to_datetime(sessions)).tz_localize(None).normalize()
    local_closes = local_dates.tz_localize(timezone) + pd.Timedelta(hours=hour, minutes=minute)
    return pd.Series(local_closes.tz_convert("UTC"), index=local_dates)


def map_release_sessions(
    public_at_utc: pd.Timestamp,
    nse_sessions: pd.DatetimeIndex,
    us_sessions: pd.DatetimeIndex,
    decision_hour: int = 8,
    decision_minute: int = 55,
) -> dict[str, pd.Timestamp]:
    """Map a release timestamp to decision and reaction sessions.

    U.S. closes use 16:00 America/New_York.  DST is handled by the timezone
    database. NSE decision cutoffs use 08:55 Asia/Kolkata.
    """
    published = pd.Timestamp(public_at_utc)
    if published.tzinfo is None:
        published = published.tz_localize("UTC")
    else:
        published = published.tz_convert("UTC")

    nse_dates = pd.DatetimeIndex(pd.to_datetime(nse_sessions)).tz_localize(None).normalize().unique().sort_values()
    us_dates = pd.DatetimeIndex(pd.to_datetime(us_sessions)).tz_localize(None).normalize().unique().sort_values()
    nse_cutoffs = session_close_utc(nse_dates, "Asia/Kolkata", decision_hour, decision_minute)
    us_closes = session_close_utc(us_dates, "America/New_York", 16, 0)

    eligible_nse = nse_cutoffs[nse_cutoffs.gt(published)]
    eligible_us = us_closes[us_closes.gt(published)]
    tradable_date = eligible_nse.index[0] if len(eligible_nse) else pd.NaT
    first_us_session = eligible_us.index[0] if len(eligible_us) else pd.NaT
    first_us_close = eligible_us.iloc[0] if len(eligible_us) else pd.NaT
    after_us = nse_cutoffs[nse_cutoffs.gt(first_us_close)] if pd.notna(first_us_close) else nse_cutoffs.iloc[0:0]
    first_nse_after_us = after_us.index[0] if len(after_us) else pd.NaT
    return {
        "tradable_date": tradable_date,
        "first_us_reaction_session": first_us_session,
        "first_us_close_utc": first_us_close,
        "first_nse_after_us_reaction_date": first_nse_after_us,
    }
