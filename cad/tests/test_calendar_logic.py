"""The calendar ring's mechanism logic reproduces the Gregorian calendar (M2, inventory I8)."""
import datetime as dt

import pytest

from cad.modules.m2_main_dial import calendar_logic as L


@pytest.mark.parametrize("start", [dt.date(2026, 11, 3), dt.date(2027, 1, 1), dt.date(2028, 2, 29),
                                   dt.date(2028, 4, 1), dt.date(2099, 12, 30)])
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


def test_counter_and_setter_act_between_march_and_december():
    pin_at = (L.COUNTER_PIN - L.STATION_OFFSET) % L.N
    tab_at = (L.SECTOR_TAB - L.STATION_OFFSET) % L.N
    assert L.MARCH1 < pin_at < tab_at < L.N - 1           # after 1 Mar, the pin before the setter
