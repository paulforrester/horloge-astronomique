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
                "counting_lever_pin": {"counter_pin"}}
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


def test_wheel_C_turns_the_way_the_hook_pulls_it_and_its_teeth_face_the_hook():
    # the first draft had the ratchet the wrong way round: the pawl met the flanks and the jumper
    # met the steep faces, so C could not turn. Check every link of the chain explicitly.
    from shapely.geometry import Point, Polygon
    # 1. counting up turns C anticlockwise: position c + 1 comes to the plunger from the clockwise side
    assert S.position_angle(11, 10) == pytest.approx(S.read_angle() - 3.6)
    # 2. at the station the ring moves towards -x, so the counter pin turns the lever clockwise, and
    #    the hook then moves anticlockwise about C
    P, pin = S.LEVER_PIVOT, S._world(0.0, S.LEVER_PIN_R)
    assert S._world(-1.0, S.COUNTER_PIN_R)[0] < 0                     # the pin's next position
    arm = (pin[0] - P[0], pin[1] - P[1])
    assert arm[0] * 0.0 - arm[1] * (-1.0) < 0                         # push along -x: clockwise torque
    home, end, _ = S.hook_home()
    assert (S._psi(end) - S._psi(home)) % 360 < 180                   # hook: anticlockwise about C
    # 3. every drive face faces clockwise: solid just anticlockwise of it, gap just clockwise
    C = Polygon(S.c_outline())
    for j in range(0, 100, 7):
        a = S.tooth_phase() + 3.6 * j
        r = S.C_R_ROOT + 0.5
        assert C.contains(Point(S._c_polar(S._face_psi(a, r) + 0.3, r)))
        assert not C.contains(Point(S._c_polar(S._face_psi(a, r) - 0.3, r)))
    # 4. at rest the hook waits just behind a drive face, and the jumper's nose sits in a gap
    lever, jumper = Polygon(S.lever_outline()), Polygon(S.jumper_outline())
    assert 0.03 < lever.distance(C) < 0.15
    assert jumper.intersection(C).area < 1e-3


def test_counting_lever_steps_wheel_C_one_tooth_per_pass():
    # C's drive faces are radial, so the jumper's nose passes a tip after exactly one pitch and the
    # next after two: any carry between 1 and 2 pitches ends, once the jumper settles, as one tooth
    pitch = 2 * math.pi * S.HOOK_R / S.C_TEETH
    t = S.hook_travel() / pitch
    assert 1.35 < t < 1.65, t                                         # near the middle of (1, 2)
    # the hook stays on its radius through the stroke (both ends on HOOK_R, the middle just inside)
    P = S.LEVER_PIVOT
    home, _, _ = S.hook_home()
    dev = []
    for k in range(41):
        b = -S.lever_turn() * k / 40
        x = P[0] + (home[0] - P[0]) * math.cos(b) - (home[1] - P[1]) * math.sin(b)
        y = P[1] + (home[0] - P[0]) * math.sin(b) + (home[1] - P[1]) * math.cos(b)
        dev.append(math.dist((x, y), S.C_XY) - S.HOOK_R)
    assert max(abs(d) for d in dev) < 0.15
    # the counter pin catches the lever pin with real overlap, and the rocker never reaches it
    overlap = S.COUNTER_PIN_R + S.COUNTER_PIN_D / 2 - (S.LEVER_PIN_R - S.LEVER_PIN_D / 2)
    assert overlap > 1.5
    from cad.lib.assembly import _mesh
    v, _ = _mesh(S.rocker_parts(0, False)["setter_rocker"], 0.05)
    assert min(math.hypot(x, y) for x, y, _ in v) > S.LEVER_PIN_R + S.LEVER_PIN_D / 2 + 1.0


def test_return_spring_pulls_the_lever_back_onto_its_stop():
    # spring on the tail (straight up from the pivot), pulled towards -x: anticlockwise, against the
    # counter pin's push; the tail's left side rests on the stop pin
    P, tail = S.LEVER_PIVOT, (S.LEVER_PIVOT[0], S.LEVER_PIVOT[1] + S.TAIL)
    f = (S.ANCHOR_XY[0] - tail[0], S.ANCHOR_XY[1] - tail[1])
    assert (tail[0] - P[0]) * f[1] - (tail[1] - P[1]) * f[0] > 0
    assert S.STOP_XY[0] < P[0] and P[1] < S.STOP_XY[1] < tail[1]
    assert S.STOP_XY[0] + 0.75 == pytest.approx(P[0] - 1.3)          # touching the tail (2.6 wide)


def test_follower_and_satellite_timing():
    rb = S.bump_radius()
    assert rb + 1.1 < S.C_R_ROOT                       # bumps inside the teeth
    # the plunger reads position c when C stands at c, for every c
    assert all(S.position_angle(c, c) == pytest.approx(S.read_angle()) for c in range(100))
    # the satellite (position 0) passes its stepping pin, 6° before the reading point, between 97 and 99
    c_step = (-6.0 / 3.6) % 100
    assert 97 < c_step < 99.9
