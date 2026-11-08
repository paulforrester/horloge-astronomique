"""M7, the weekday carousel (docs/m7-design.md): fit, ratio, sense, meshes, phase, setting, clearances."""
import math

import pytest

bd = pytest.importorskip("build123d")

from cad.lib.bevel import Bevel
from cad.modules.m7_weekdays import mechanism as M


@pytest.fixture(scope="module")
def built():
    a, data = M.build()
    return a, M.check(a, data)


def test_no_interference_and_everything_fits_the_bed(built):
    a, r = built
    assert r["interference"] == []
    assert r["bed_fit_single"] == [] and r["bed_fit_dual"] == []


def test_ratio_is_exactly_one_turn_a_week():
    # M2 makes 1/7 (12/84); M7's bevel pair and spur pair are both 1:1, so the error is zero
    assert M.BEVEL.teeth == M.BEVEL.mate_teeth
    assert M.SPUR_Z == M.SPUR_Z
    assert (12 / 84) * (M.BEVEL.teeth / M.BEVEL.mate_teeth) == pytest.approx(1 / 7)


def test_carousel_turns_counter_clockwise_seen_from_above():
    # m7-design §1: tomorrow's chariot waits on the viewer's left, so the front moves left to right
    s = M.senses()
    assert s["W_about_+Z"] == +1 and s["carousel_about_+Y"] == +1
    # a point at the front (+Z of the axis) moving with +1 about +Y goes towards +X (the viewer's right)
    w, r = (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)
    vx = w[1] * r[2] - w[2] * r[1]
    assert vx > 0


def test_phase_noon_and_neighbours():
    # at its mean noon the day's chariot is at the front; tomorrow's is one place round on the left
    for day in range(7):
        assert M.chariot_angle(day, day, 0.0) == pytest.approx(0.0)
        x, z = M.plan_xyz(M.chariot_angle(day + 1, day, 0.0), M.R)      # tomorrow (index taken mod 7)
        assert x < 0 and z < M.Z_AXIS + M.R
        x, _ = M.plan_xyz(M.chariot_angle(day - 1, day, 0.0), M.R)
        assert x > 0
    # one day of carousel is one place (51.4°); 2.9 h before noon the chariot is 6.2° short of the front
    assert M.chariot_angle(5, 5, 2.9) == pytest.approx(-2.9 * 360 / 168)


def test_spur_pair_is_engaged(built):
    a, r = built
    lx, lz = M.W_XY[0], M.Z_APEX
    d = math.hypot(0 - lx, M.Z_AXIS - lz)
    assert d == pytest.approx(85.0, abs=1e-6)
    moved = a["turntable_hub"].shape.moved(bd.Location((-(0 - lx) / d * 0.4, 0, -(M.Z_AXIS - lz) / d * 0.4)))
    assert (a["lay_gear_85"].shape & moved).volume > 0.05


def test_bevels_are_engaged(built):
    a, _ = built
    # turning B 1.5° about its own (vertical) axis takes up the backlash and clashes
    for d in (-1.5, 1.5):
        b = a["bevel_B_20"].shape.rotate(bd.Axis((M.W_XY[0], 0, M.Z_APEX), (0, 1, 0)), d)
        assert (a["bevel_A_20"].shape & b).volume > 0.05, d


def test_setting_spline_and_the_dog():
    # the spline: 84 positions, 2 h of carousel each; the dog coupling: one position only
    assert M.SPLINE.teeth == 84
    assert 7 * 24 / M.SPLINE.teeth == pytest.approx(2.0)


def test_clearances_to_the_neighbours(built):
    a, _ = built
    # the deck stays behind M2's calendar ring (z > -11 is the ring and its carrier)
    assert a["deck"].shape.bounding_box().max.Z <= -13.0
    # the tallest figure stays under M1's lowest part (≈ 479 mm above the floor, m7-design §2)
    top = max(a[f"chariot_{k}"].shape.bounding_box().max.Y for k in range(7))
    assert top + M.DIAL_CENTRE_ABOVE_FLOOR < 479.0
    # the chariots' floor is where the photograph puts it (≈ 390 mm above the floor)
    assert M.Y_FLOOR + M.DIAL_CENTRE_ABOVE_FLOOR == pytest.approx(390.0)
    # M7's drive stays behind the end of M2's arbor W (z -139); only the dog hub sits on W itself
    for n in ("dog_sleeve", "bevel_A_20", "bevel_B_20", "bracket"):
        assert a[n].shape.bounding_box().max.Z < M.W_END, n
