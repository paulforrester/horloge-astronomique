"""The clockwork time law and EU summer time, in Python (docs/firmware-design.md §6.1, §8.2, §11.6).

This is the simulator's reference copy of the law in firmware/core/time_law.h and summer_time.cpp.
It is written independently (Python's calendar module for the last Sundays, exact integer
arithmetic for the law), and firmware/tests/test_host.py checks that the two give the same answer.
"""

import calendar
import datetime as dt

MEAN_TIME_OFFSET_S = 1860  # Strasbourg mean time = UT + 31.00 min (D2)
CET_OFFSET_S = 3600
EPOCH_UNIX_S = 1767225600  # 2026-01-01 00:00:00 UTC
US_PER_S = 1_000_000
USTEPS_PER_MOTOR_REV = 3200


def usteps_for(dt_us: int) -> int:
    """floor(dt × 3200 / 3600 s) for a span in µs; Python integers are exact."""
    return (dt_us * 8) // (9 * US_PER_S)


def module_time_us(kind: str, utc_unix_us: int, j: int) -> int:
    since = utc_unix_us - EPOCH_UNIX_S * US_PER_S
    if kind == "mean":
        return since + MEAN_TIME_OFFSET_S * US_PER_S
    return since + (CET_OFFSET_S + 3600 * j) * US_PER_S


def target_usteps(kind: str, utc_unix_us: int, j: int, p_k: int) -> int:
    return p_k + usteps_for(module_time_us(kind, utc_unix_us, j))


def eu_change_unix_s(year: int, spring: bool) -> int:
    """01:00 UTC on the last Sunday of March (spring) or October (Directive 2000/84/EC)."""
    month = 3 if spring else 10
    last_sunday = max(week[calendar.SUNDAY] for week in calendar.monthcalendar(year, month))
    return int(dt.datetime(year, month, last_sunday, 1, tzinfo=dt.timezone.utc).timestamp())


def legal_offset_s(unix_s: int) -> int:
    year = dt.datetime.fromtimestamp(unix_s, dt.timezone.utc).year
    return 7200 if eu_change_unix_s(year, True) <= unix_s < eu_change_unix_s(year, False) else 3600


def summer_time_j(unix_s: int) -> int:
    """Hours added to the legal-time modules since the epoch: +1 each spring, +23 each autumn (D14)."""
    year = dt.datetime.fromtimestamp(unix_s, dt.timezone.utc).year
    j = 0
    for y in range(2026, year + 1):
        if eu_change_unix_s(y, True) <= unix_s:
            j += 1
        if eu_change_unix_s(y, False) <= unix_s:
            j += 23
    return j
