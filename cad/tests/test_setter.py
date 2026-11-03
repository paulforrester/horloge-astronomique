"""M2 calendar setter (rocker and ramps) and year counter: the rules the design must keep."""
import math

import pytest

bd = pytest.importorskip("build123d")
pytest.importorskip("shapely")

from cad.lib import parts  # noqa: E402
from cad.lib.assembly import _mesh  # noqa: E402
from cad.modules.m2_main_dial import calendar as CAL  # noqa: E402
from cad.modules.m2_main_dial import calendar_logic as L  # noqa: E402
from cad.modules.m2_main_dial import setter as S  # noqa: E402


def _r_range(points):
    rs = [math.hypot(x, y) for x, y in points]
    return min(rs), max(rs)


def test_rocker_moves_the_sector_exactly_one_division():
    throw = S.pin_radii(False)["tab_along"] - S.pin_radii(True)["tab_along"]
    assert throw == pytest.approx(2 * math.pi * S.TAB_R / L.N, abs=1e-6)


def test_each_ramp_reaches_only_its_own_pin_in_the_right_state():
    c, lp = S.pin_radii(False), S.pin_radii(True)
    h = S.PIN_D / 2
    r0, r1 = _r_range(S.ramp_outlines()["reset"])
    assert r0 < lp["reset"] - h                       # catches the reset pin when it is out (leap)
    assert r1 < c["reset"] - h                        # ...and lets it go once pushed to common
    assert r1 < lp["set"] - h - 0.5                   # never touches the set pin
    s0, s1 = _r_range(S.ramp_outlines()["set"])
    assert s1 > c["set"] + h                          # catches the set pin when it is out (common)
    assert s0 > lp["set"] + h                         # ...and lets it go once pushed to leap
    assert s0 > c["reset"] + h + 0.5                  # never touches the reset pin
    # depths: both ramps stay under the rocker's bars; the set ramp, when down, under its pin
    assert S.RAMP_TOP < S.BAR_Z[0] and S.RAMP_TOP > S.PIN_Z[0]
    assert S.RAMP_TOP - S.STROKE < S.PIN_Z[0]


@pytest.mark.parametrize("leap", [False, True])
def test_fixed_readers_meet_only_their_partners_on_the_ring(leap):
    # the ring sweeps every fixed part in its path; each reader's band may only hold its partner
    a, _ = CAL.build(sector_leap=leap, set_engaged=True, dates=False)
    partners = {"setter_reset_ramp": {"setter_rocker"}, "setter_set_ramp": {"setter_rocker"},
                "counting_lever": {"counter_pin"}}
    sweep_z = (CAL.BAND[2] - 0.3, 0.1)
    for reader, ok in partners.items():
        clip = a[reader].shape & parts.disc(400.0, sweep_z[1] - sweep_z[0], z0=sweep_z[0])
        v, _ = _mesh(clip, 0.05)
        r0, r1 = _r_range(v[:, :2])
        z0, z1 = v[:, 2].min(), v[:, 2].max()
        band = parts.disc(2 * r1, z1 - z0, bore=2 * r0, z0=z0)
        hits = set()
        for it in a.items:
            if it.group != "ring" or it.inside:
                continue
            bb = it.shape.bounding_box()
            if bb.max.Z < z0 or bb.min.Z > z1:
                continue
            if (it.shape & band).volume > 1e-3:
                hits.add(it.name)
        assert hits <= ok, (reader, hits - ok)


def test_counting_lever_steps_wheel_C_one_tooth_per_pass():
    piv, pin = S.LEVER_PIVOT, S._world(0.0, S.COUNTER_PIN_R)
    L_pin = math.dist(piv, pin)
    a0 = math.atan2(pin[1] - piv[1], pin[0] - piv[0])
    # turn the lever (the counter pin pushes its pin along the ring) until the pin is clear of the
    # counter pin's path: radially outside it by the two radii
    need = S.COUNTER_PIN_R + 1.25 + 0.8
    turn = 0.0
    while math.hypot(piv[0] + L_pin * math.cos(a0 - turn), piv[1] + L_pin * math.sin(a0 - turn)) < need:
        turn += math.radians(0.1)
    d = (piv[0] - S.C_XY[0], piv[1] - S.C_XY[1])
    pawl_r = math.dist(piv, (S.C_XY[0] + (S.C_R_ROOT + 0.9) * d[0] / math.hypot(*d),
                             S.C_XY[1] + (S.C_R_ROOT + 0.9) * d[1] / math.hypot(*d)))
    travel = pawl_r * turn
    pitch = 2 * math.pi * (S.C_R_ROOT + 0.9) / S.C_TEETH
    assert pitch < travel < 2 * pitch                 # one tooth, never two (the jumper finishes it)


def test_follower_and_satellite_timing():
    rb = S.bump_radius()
    assert rb + 1.1 < S.C_R_ROOT                       # bumps inside the teeth
    # the plunger reads position c when C stands at c, for every c
    assert all(S.position_angle(c, c) == pytest.approx(S.read_angle()) for c in range(100))
    # the satellite (position 0) passes its stepping pin, 6° before the reading point, between 97 and 99
    c_step = (-6.0 / 3.6) % 100
    assert 97 < c_step < 99.9
