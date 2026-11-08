"""Simulator tests (docs/firmware-design.md §11-12). The sky test needs Skyfield and the kernel."""

import datetime as dt
from fractions import Fraction

import pytest

from sim import calendar_ring, ephemeris, sheet, validate
from sim.model import Clock

US = 1_000_000
T0 = 1798761600  # 2027-01-01 00:00 UTC


@pytest.fixture(scope="module")
def clock():
    return Clock()


def test_input_arbors_turn_at_clockwork_rates(clock):
    day = 86400 * US
    assert clock.axes["M2"].input_turns(T0 * US, T0 * US + day) == 1          # 1 rev per mean day
    assert clock.axes["M1"].input_turns(T0 * US, T0 * US + 3600 * US) == 1    # 1 rev per hour
    # A day of the weekday drive is exactly a seventh of a turn (exact train, spec M2.weekday).
    assert clock.delta_deg("M2.weekday", T0 * US, T0 * US + day) == Fraction(360, 7)


def test_legal_axis_jumps_with_the_changes(clock):
    from sim import timelaw

    m1b = clock.axes["M1b"]
    a = timelaw.eu_change_unix_s(2027, False)  # autumn: +23 h
    assert m1b.usteps(a * US) - m1b.usteps((a - 1) * US) in (73600, 73601)
    s = timelaw.eu_change_unix_s(2027, True)   # spring: +1 h
    assert m1b.usteps(s * US) - m1b.usteps((s - 1) * US) in (3200, 3201)


def test_ring_turns_once_a_year_and_2100_is_the_v1_limit():
    positions = {d: p for d, p, _ in calendar_ring.run_ring(dt.date(2026, 1, 1), dt.date(2030, 1, 1))}
    for y in range(2027, 2031):
        assert positions[dt.date(y, 1, 1)] == calendar_ring.division_of(dt.date(y, 1, 1))
    assert calendar_ring.division_of(dt.date(2028, 2, 29)) == 61   # uncovered in a leap year
    assert calendar_ring.division_of(dt.date(2027, 3, 1)) == calendar_ring.FIRST_MARCH
    assert calendar_ring.divisions_into(dt.date(2028, 1, 1)) == 3
    assert calendar_ring.divisions_into(dt.date(2027, 1, 1)) == 4
    assert calendar_ring.mechanism_leap(2100) and not calendar_ring.gregorian_leap(2100)


def test_all_checks_pass_over_ten_years():
    results = validate.run_all(T0, years=10)
    failed = [(r.row, r.what, r.worst, r.budget) for r in results if not r.passed]
    assert not failed, failed
    rows = {r.row for r in results}
    assert {"1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "14"} <= rows


def test_a_wrong_ratio_is_caught(clock):
    """The checks can fail: a Moon-globe train one tooth off is outside its budget."""
    spec = dict(clock.spec)
    spec["trains"] = [dict(t) for t in clock.spec["trains"]]
    for t in spec["trains"]:
        if t["id"] == "M5.moon_globe":
            t["stages"] = [[19, 83], [25, 170]]
    bad = Clock(spec)
    c = next(c for c in validate.train_checks(bad) if c.train == "M5.moon_globe")
    honest = next(c for c in validate.train_checks(clock) if c.train == "M5.moon_globe")
    times = validate.sample_times(T0, 1, 86400)
    r = validate.run_train_check(bad, c, T0, times)
    # The tool's own drift for the wrong train is huge, so compare with the true train's budget.
    good = validate.run_train_check(clock, honest, T0, times)
    assert abs(r.worst) > good.budget


def test_setting_sheet_without_the_sky():
    text = sheet.setting_sheet(T0 + 10 * 3600)
    assert "I1 gilt hands" in text and "division" in text and "Friday" in text  # 1 Jan 2027


@pytest.mark.skipif(not ephemeris.available(), reason="Skyfield or the DE440s kernel not available")
def test_sky_gaps_one_year():
    gaps = {g.what: g for g in validate.sky_gaps(1767225600, years=1)}
    eot = next(g for k, g in gaps.items() if k.startswith("Sun hand"))
    assert -15 < eot.lo < -13 and 16 < eot.hi < 17           # equation of time, min [S: probe]
    earth = next(g for k, g in gaps.items() if k.startswith("Earth"))
    assert 1.8 < earth.hi < 2.0                                # the Sun's equation of centre ≈ 1.9°


def test_sheet_times_round_cleanly():
    assert sheet._hm(10 + 31 / 60 - 1e-9) == "10:31:00.0"
    assert sheet._hm(23.99999999) == "00:00:00.0"
