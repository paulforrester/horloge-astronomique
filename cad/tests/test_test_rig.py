"""Test rig (Phase 2 step 3): checks the brief asks for, and that every pair is engaged."""
import math

import pytest

bd = pytest.importorskip("build123d")

from cad.modules.test_rig import rig  # noqa: E402


@pytest.fixture(scope="module")
def built():
    a, data = rig.build()
    return a, rig.check(a, data)


def test_no_interference_and_everything_fits_the_bed(built):
    _, r = built
    assert r["interference"] == []
    assert r["bed_fit_single"] == [] and r["bed_fit_dual"] == []


def test_trains_are_the_spec_trains(built):
    _, r = built
    cds = [m["centre_distance"] for m in r["meshes"]]
    assert cds[:2] == [30.0, 30.0]          # reverted motion work, M1.hour_hand 12/48 x 15/45
    assert cds[2:4] == [33.0, 38.0]         # M1.noon_cam 12/54 x 12/64
    assert len(cds) == 5


def test_every_mesh_is_engaged(built):
    """Pull each driven wheel 0.4 mm towards its driver: it must collide (so 'no interference'
    means meshing, not a gap)."""
    a, r = built
    pos = r["positions"]
    checks = [("noon_pinion_12_A", "noon_wheel_54_12_X", "A_minute", "X_noon"),
              ("noon_wheel_54_12_X", "day_wheel_64_B", "X_noon", "B_24h"),
              ("sun_drive_48_B", "sun_wheel_48_C", "B_24h", "C_24h_dial"),
              ("shadow_drive_48_B", "shadow_wheel_48_C", "B_24h", "C_24h_dial"),
              ("cannon_pinion_12", "minute_wheel_48_15", "A_minute", "minute_stud"),
              ("hour_wheel_45", "minute_wheel_48_15", "A_minute", "minute_stud")]
    for drv, dvn, p1, p2 in checks:
        (x1, y1), (x2, y2) = pos[p1], pos[p2]
        d = math.hypot(x2 - x1, y2 - y1)
        moved = a[dvn].shape.moved(bd.Location((-(x2 - x1) / d * 0.4, -(y2 - y1) / d * 0.4, 0)))
        assert (a[drv].shape & moved).volume > 0.05, (drv, dvn)


def test_coupons_cover_the_planned_matrix():
    from cad.lib.assembly import BED_DUAL
    from cad.modules.test_rig import coupons as C
    a = C.build()
    assert a.interference() == []
    assert all(r["fits"] for r in a.bed_fit(BED_DUAL))
    gears = [i.name for i in a.items if i.name.startswith("gear_m")]
    assert len(gears) == 2 * len(C.MODULES) * len(C.BACKLASHES)
    fit = a["fit_coupon"].shape
    # 3 rods x 7 allowances = 21 holes through a 6 mm plate
    import math
    hole_area = sum(math.pi / 4 * (d + al) ** 2 for d in (3.0, 5.0, 8.0) for al in C.FIT_ALLOWANCES)
    w, h = 14.0 * len(C.FIT_ALLOWANCES) + 8, 14.0 * 3 + 8
    assert fit.volume == pytest.approx((w * h - hole_area) * 6.0 - 6 * 6 / 2 * 6, rel=0.01)
