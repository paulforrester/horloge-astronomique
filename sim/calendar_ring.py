"""The calendar ring and E6, as docs/m2-design.md §6 describes them.

- 368 divisions. d = 0, 1, 2: "COMMENCEMENT DE L'ANNÉE" … "commune"; 3 … 61: the movable sector
  (1 Jan … 28 Feb) in its common-year place; 61: "29 Feb" on the fixed ring; 62 … 367: 1 Mar … 31 Dec.
- In a leap year the sector sits one division back: 1 Jan at d = 2, 29 Feb uncovered at 61.
- E6 runs at each mean midnight: one division, or into 1 January 4 (common year) or 3 (leap year).
- The year counter sets the sector each October for the coming year from a four-year count, so
  in v1 every year divisible by 4 is leap. 2100 needs the computus (v2; architecture §4).
"""

import datetime as dt

DIVISIONS = 368
FIRST_MARCH = 62


def mechanism_leap(year: int) -> bool:
    """What the v1 mechanism does (a four-year count)."""
    return year % 4 == 0


def gregorian_leap(year: int) -> bool:
    return (year % 4 == 0 and year % 100 != 0) or year % 400 == 0


def divisions_into(date: dt.date, leap=mechanism_leap) -> int:
    """E6's divisions on the night that brings `date` to the pointer."""
    if date.month == 1 and date.day == 1:
        return 3 if leap(date.year) else 4
    return 1


def division_of(date: dt.date, leap=gregorian_leap) -> int:
    """Where `date` sits on the ring (the division that should be at the pointer)."""
    if date.month >= 3:
        return FIRST_MARCH + (date - dt.date(date.year, 3, 1)).days
    first = 2 if leap(date.year) else 3
    return first + (date - dt.date(date.year, 1, 1)).days


def run_ring(start: dt.date, end: dt.date, leap=mechanism_leap):
    """Set the ring at `start`, run E6 every night to `end`. Yields (date, division, steps)."""
    pos = division_of(start, leap)
    d = start
    yield d, pos, 0
    while d < end:
        d += dt.timedelta(days=1)
        n = divisions_into(d, leap)
        pos = (pos + n) % DIVISIONS
        yield d, pos, n
