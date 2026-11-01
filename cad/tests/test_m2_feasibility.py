"""M2 main-dial feasibility layout: the checks the Phase 2 brief asks for."""
import pytest

bd = pytest.importorskip("build123d")

from cad.lib.assembly import Assembly  # noqa: E402
from cad.lib import parts  # noqa: E402
from cad.modules.m2_main_dial import feasibility as F  # noqa: E402


@pytest.fixture(scope="module")
def result():
    a, rep = F.build()
    return a, F.check(a, rep)


def test_no_interference_and_no_sweep_conflict(result):
    _, r = result
    assert r["interference"] == []
    assert r["sweep_conflicts"] == []


def test_only_the_calendar_ring_exceeds_the_bed(result):
    _, r = result
    assert [x["part"] for x in r["bed_fit_single"]] == ["calendar_ring"]
    assert [x["part"] for x in r["bed_fit_dual"]] == ["calendar_ring"]


def test_layout_stays_in_the_m2_bay_and_depth_budget(result):
    _, r = result
    assert r["inside_bay"]
    z0, z1 = r["envelope"]["z"]
    assert z1 - z0 < 200          # envelope.md: plan the case around >= 200 mm interior depth


def test_centre_stack_within_d4_tube_limit(result):
    _, r = result
    tubes = r["report"]["tubes"]
    assert len(tubes) <= 7 and max(t["od"] for t in tubes) <= 10


def test_latitude_cam_reproduces_schwilgue_design_point():
    # ELS: mean radius 134 mm, R - r = 40.4 mm, slope limited to 5/6 x 45° = 37.5°
    slope = parts.cam_pressure_angle(F.latitude_profile(134, 40.4), 36000)
    assert slope == pytest.approx(37.5, abs=0.2)
    assert F.rho_for_slope(40.4) == pytest.approx(134, abs=1.0)


def test_sweep_check_catches_a_collision():
    a = Assembly("t")
    a.add("dial", parts.disc(100, 1, z0=-1))
    a.add("hemisphere", parts.disc(10, 1, z0=5))
    for n in ["calendar_ring", "hand_sunset", "hand_sunrise", "hand_sun", "sun_disc", "latitude_cam", "hand_moon",
              "arm_shadow", "shadow_disc"]:
        a.add(n, parts.disc(2, 0.5, z0=50 + len(a.items)).moved(bd.Location((200, 0, 0))))
    a.add("moon_ball", parts.disc(3, 3, z0=0.5).moved(bd.Location((40, 0, 0))))
    a.items[[i.name for i in a.items].index("hand_sun")].shape = parts.hand(45, 2, 1.5, 6, 3, z0=1.0)
    hits = {frozenset((c["a"], c["b"])) for c in F.sweep_conflicts(a)}
    assert frozenset(("hand_sun", "moon_ball")) in hits
