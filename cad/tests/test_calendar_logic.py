"""The calendar ring's mechanism logic reproduces the Gregorian calendar (M2, inventory I8)."""
import datetime as dt

import pytest

from cad.modules.m2_main_dial import calendar_logic as L


@pytest.mark.parametrize("start", [dt.date(2026, 11, 3), dt.date(2027, 1, 1), dt.date(2027, 11, 15),
                                   dt.date(2028, 2, 29), dt.date(2028, 4, 1), dt.date(2099, 12, 30)])
def test_every_day_shown_correctly_for_four_centuries(start):
    r = L.simulate(start, dt.date(2427, 1, 1))
    assert r["errors"] == []
    for year, n in r["new_year_jumps"].items():
        assert n == (3 if L.is_leap(year) else 4), year     # Ungerer: 4 in common years, 3 in leap years


def test_century_years():
    r = L.simulate(dt.date(2026, 6, 1), dt.date(2401, 3, 2))
    assert r["errors"] == []
    assert r["new_year_jumps"][2100] == 4 and r["new_year_jumps"][2400] == 3


def test_layout_adds_up():
    assert len(L.COMMENCEMENT) + L.SECTOR_DAYS + 1 + (dt.date(2027, 1, 1) - dt.date(2026, 3, 1)).days == L.N + 1
    # 3 + 59 + (29 Feb) + 306 = 369 divisions of content on 368 places: 29 Feb shares d = 61 with the
    # sector's last common-year place, which is why the sector covers it in common years
    assert L.SECTOR_COMMON_START + L.SECTOR_DAYS - 1 == L.FEB29


def test_counter_then_reset_then_set_between_march_and_december():
    pin_at = (L.COUNTER_PIN - L.STATION_OFFSET) % L.N
    reset_at = (L.ROCKER_D - L.RESET_OFFSET) % L.N
    set_at = (L.ROCKER_D - L.SET_OFFSET) % L.N
    # after 1 Mar; the counter first (1 Oct), then the reset ramp, then the set ramp, before New Year
    assert L.MARCH1 < pin_at < reset_at < set_at < L.N - 1
    day = lambda d: dt.date(2026, 3, 1) + dt.timedelta(days=d - L.MARCH1)
    assert day(pin_at) == dt.date(2026, 10, 1)
    assert dt.date(2026, 10, 5) <= day(reset_at) < day(set_at) <= dt.date(2026, 10, 31)
