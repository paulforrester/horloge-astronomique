"""Calendar-ring logic: the mechanism as a discrete simulation, checked against the real calendar.

Ring layout (368 divisions, Ungerer [S: ELS i4]; positions counted in the ring's own frame):

    d = 0, 1, 2      "COMMENCEMENT DE L'ANNÉE" … "commune" (d = 2 carries the word "commune")
    d = 3 … 61       movable sector, 1 Jan … 28 Feb (59 divisions), in its COMMON position
    d = 61           "29 Feb", printed on the fixed ring, covered by the sector in common years
    d = 62 … 367     fixed part, 1 Mar … 31 Dec (306 divisions)

In a LEAP year the sector slides back one division (d = 2 … 60): it covers "commune" and uncovers
"29 Feb" (Ungerer: the sector "covers 'commune' and uncovers 29 Feb").

Each night E6 runs one crank turn = one division. It keeps running while the **stop lever** at the
pointer is held up (Ungerer's projection S):
  - fixed bumps at d = 0 and 1;
  - a **lug on the sector**, one division before its first day: at d = 2 when the sector is in its
    common position (so the New Year jump is 4 divisions), at d = 1 when it is in its leap position
    (the jump is 3). The sector's position alone decides 3 or 4: no separate cam is needed.

The **station** at the bottom of the ring sees the division ``pointer + STATION_OFFSET``. The ring
turns clockwise seen from the front (Paul's photograph of the original, PR #6: tomorrow's date is
just below Apollo's arrow), so a division leaving the arrow at 9 o'clock reaches the station at
6 o'clock three quarters of a turn later: the station sees the division that will reach the arrow
in 92 days.
  - a pin on the ring at d = COUNTER_PIN advances the year counter, wheel C (100 positions, one per
    year), once per turn, on 1 October. A pin on C advances the satellite (4 positions, one per
    century) when C passes from 99 to 0;
  - later in the same turn the **rocker** on the ring (beside the sector's tab, its tip pins at
    d = ROCKER_D) passes two ramps. The fixed **reset ramp** (about 13 October) puts the sector in
    its common position. Then the **set ramp** (about 20 October), which stands in the rocker's lane
    only when the follower on wheel C reads a leap year, puts it in the leap position. The sector is
    thus set for the year to come, from C and the satellite, two months before it reaches the
    arrow.

``simulate`` runs the mechanism day by day and reports every day on which the ring shows the wrong
date. The test runs 2026–2426, which covers 2100, 2200, 2300 (not leap) and 2400 (leap).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

N = 368
COMMENCEMENT = (0, 1, 2)
SECTOR_COMMON_START = 3
SECTOR_DAYS = 59
FEB29 = 61
MARCH1 = 62
STATION_OFFSET = 92           # the station (6 o'clock) sees the division 92 days ahead of the pointer
COUNTER_PIN = 0               # ring division carrying the counter pin
SECTOR_TAB = 30               # sector division carrying the tab the rocker drives (mid-sector)
ROCKER_D = 32                 # ring division of the rocker's tip pins (the rocker sits beside the tab)
RESET_OFFSET = STATION_OFFSET + 19   # the reset ramp sees the division 111 ahead of the pointer
SET_OFFSET = STATION_OFFSET + 12     # the set ramp, a little after it: 104 ahead
S_BUMPS = (0, 1)              # fixed projection S


def leap_from_counter(c: int, satellite: int) -> bool:
    """What the follower reads: wheel C has bumps at 4, 8, …, 96; position 0 is common unless the
    satellite's single bump is under it (once every four centuries)."""
    if c % 4 == 0 and c != 0:
        return True
    return c == 0 and satellite == 0


@dataclass
class Mechanism:
    pointer: int                  # ring division at Apollo's arrow
    sector_leap: bool             # sector position
    c: int                        # wheel C: (year it has been set for) % 100
    satellite: int                # (century of that year) % 4
    log: list = field(default_factory=list)

    @property
    def sector_start(self) -> int:
        return SECTOR_COMMON_START - (1 if self.sector_leap else 0)

    def lever_held(self) -> bool:
        lug = self.sector_start - 1
        return self.pointer in S_BUMPS or self.pointer == lug

    def station_sees(self) -> int:
        return (self.pointer + STATION_OFFSET) % N

    def step(self):
        """One crank turn of E6: the ring advances one division."""
        self.pointer = (self.pointer + 1) % N
        seen = self.station_sees()
        if seen == COUNTER_PIN:
            if self.c == 99:
                self.satellite = (self.satellite + 1) % 4
            self.c = (self.c + 1) % 100
        if (self.pointer + RESET_OFFSET) % N == ROCKER_D:          # reset ramp: always, to common
            self.sector_leap = False
        if (self.pointer + SET_OFFSET) % N == ROCKER_D and leap_from_counter(self.c, self.satellite):
            self.sector_leap = True                                  # set ramp: only for a leap year

    def night(self) -> int:
        """Midnight release: run until the stop lever is down. Returns the divisions advanced."""
        n = 0
        while True:
            self.step()
            n += 1
            if not self.lever_held():
                return n
            if n > 10:
                raise RuntimeError("E6 would run away")

    def shown(self, year: int) -> tuple:
        """(month, day) under the pointer, or a label."""
        d = self.pointer
        start = self.sector_start
        if start <= d < start + SECTOR_DAYS:
            day = dt.date(year, 1, 1) + dt.timedelta(days=d - start)
            return (day.month, day.day)
        if d == FEB29:
            return (2, 29)
        if d >= MARCH1:
            day = dt.date(year, 3, 1) + dt.timedelta(days=d - MARCH1)
            return (day.month, day.day)
        return ("commencement", d)


def is_leap(y: int) -> bool:
    return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)


def initial_state(date: dt.date) -> Mechanism:
    """The setting procedure (architecture §7): ring turned to the date, sector and wheel C set."""
    y = date.year
    leap = is_leap(y)
    start = SECTOR_COMMON_START - (1 if leap else 0)       # where the sector is for this year's dates
    if date.month <= 2:
        d = start + (date - dt.date(y, 1, 1)).days if not (date.month == 2 and date.day == 29) else FEB29
    else:
        d = MARCH1 + (date - dt.date(y, 3, 1)).days
    # wheel C shows the year the sector will next be set for: this year until the October advance
    # has happened (pin seen when the pointer reaches COUNTER_PIN - STATION_OFFSET), then next year
    pin_pointer = (COUNTER_PIN - STATION_OFFSET) % N
    target = y + 1 if d >= pin_pointer else y
    # after the October setting the sector already stands for next year
    set_pointer = (ROCKER_D - SET_OFFSET) % N
    sector_leap = is_leap(y + 1) if d >= set_pointer else leap
    return Mechanism(pointer=d, sector_leap=sector_leap, c=target % 100, satellite=(target // 100) % 4)


def simulate(start: dt.date, end: dt.date) -> dict:
    m = initial_state(start)
    errors, jumps = [], {}
    day = start
    while day < end:
        n = m.night()
        day += dt.timedelta(days=1)
        if day.month == 1 and day.day == 1:
            jumps[day.year] = n
        got = m.shown(day.year)
        if got != (day.month, day.day):
            errors.append((day.isoformat(), got))
    return {"errors": errors, "new_year_jumps": jumps, "final": (m.pointer, m.c, m.satellite)}
