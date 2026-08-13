"""Dependency-free alarm scheduling helpers."""

from __future__ import annotations

from datetime import datetime, time, timedelta


def next_alarm_target(
    reference: datetime,
    weekday_time: time,
    weekend_time: time,
    skip_through: datetime | None = None,
) -> datetime:
    """Return the first alarm after now and after any stopped occurrence."""
    for days_ahead in range(8):
        date_value = (reference + timedelta(days=days_ahead)).date()
        alarm_time = weekday_time if date_value.weekday() < 5 else weekend_time
        candidate = datetime.combine(date_value, alarm_time, tzinfo=reference.tzinfo)
        if candidate > reference and (skip_through is None or candidate > skip_through):
            return candidate
    raise RuntimeError("Geen volgende wektijd gevonden")
