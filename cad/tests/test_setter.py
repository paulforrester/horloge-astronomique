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
    # 4. at rest the hook waits just behind a drive face, and the click's nose sits in a gap
    lever, click = Polygon(S.lever_outline()), Polygon(S.click_outline())
    assert 0.03 < lever.distance(C) < 0.15
    assert click.intersection(C).area < 1e-3


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


def test_plunger_reads_only_its_own_year_and_can_climb():
    # PR #8 review: the first bumps were sheer cylinders as tall as the stroke, so the plunger could
    # not climb them. Now each is a ramp (on the side that reaches the plunger first) and a sheer drop.
    pitch = 2 * math.pi * S.bump_radius() / S.C_TEETH
    # a neighbour's bump may lift the plunger a little, as long as the lowered ramp stays 0.2 mm
    # under the set pin
    allowed = (S.PIN_Z[0] - (S.RAMP_TOP - S.STROKE)) - 0.2
    for err in (-0.25, 0.0, 0.25):                                    # C's position tolerance (mm)
        assert S.plunger_lift(err) == pytest.approx(S.STROKE, abs=0.01)        # its own year: fully up
        assert S.plunger_lift(-pitch + err) < allowed                  # next year's bump (still to come)
        assert S.plunger_lift(pitch + err) < allowed                   # last year's bump
    assert S.pressure_angle() < 50.0
    # a two-point guide (collar in the pocket, shank in the bore) does not jam at that angle:
    # tan(a) < L / (mu (2 x + L)), x the tip's overhang below the collar
    pz = S.plunger_z(False)
    guide = (S.CEILING + (-10.9)) / 2 - (pz["collar"][0] + pz["collar"][1]) / 2
    overhang = (pz["collar"][0] + pz["collar"][1]) / 2 - pz["tip"]
    assert math.tan(math.radians(S.pressure_angle())) < guide / (S.MU * (2 * overhang + guide)) / 1.5


def test_plunger_spring_pushes_the_plunger_onto_C():
    # PR #8 review: the first spring sat in a counterbore under the ramp, which could only push the
    # ramp away from C. Now it sits between the pocket's fixed ceiling and the plunger's collar.
    for engaged in (False, True):
        pz = S.plunger_z(engaged)
        lo, hi = pz["spring"]
        assert lo == pytest.approx(pz["collar"][1]) and hi == pytest.approx(S.CEILING)
        assert pz["collar"][1] < S.CEILING                            # collar below the ceiling: pushes it towards C
    assert S.plunger_z(False)["collar"][0] > S.C_Z[1] + S.STROKE + 0.2    # the collar clears every bump
    assert S.plunger_z(False)["boss_bottom"] > S.C_Z[1] + S.STROKE + 0.2  # and so does the bracket's boss
    assert S.PLUNGER_SPRING["Di"] > S.PLUNGER_D + 0.1 and S.PLUNGER_SPRING["De"] < S.POCKET_D - 0.3


def test_wire_springs_hold_and_stay_elastic():
    w = S.wire_springs()
    assert w["rocker_detent"]["hold_Nmm"] > 3 * w["rocker_detent"]["need_Nmm"]   # the sector's own weight
    assert w["click"]["F_nose_max"] < 0.6                            # light on the counting lever
    if not S.WIRE_RM_MIN:
        pytest.skip("the spring wire's tensile strength is not sourced yet")
    for name, v in w.items():
        assert v["stress_max"] < 0.7 * S.WIRE_RM_MIN[v["d"]], name    # EN 13906-1 style limit for bent wire


def test_satellite_clears_the_plunger_boss_and_its_detent_holds_a_flat():
    rb = S.bump_radius()
    g = S.satellite_geometry(0, 0)
    star_out = g["rs"] + 2.6
    boss_in = rb - (S.POCKET_D + 1.4) / 2
    assert star_out < boss_in - 0.3                                   # the star passes inside the boss
    # the detent wire lies in the hub's layer, under the step pin, which sweeps a circle over C
    wire_top = S.C_Z[1] + S.STROKE / 2 + S.SAT_WIRE_D / 2
    step_pin_bottom = S.C_Z[1] + S.STROKE + 0.3
    assert wire_top < step_pin_bottom - 0.5


def test_bought_springs_as_installed():
    b = S.bought_springs()
    # plunger: always presses (guide friction is all it fights), light when C must lift it
    assert 0.05 < b["plunger"]["F_rest"] < b["plunger"]["F_lift"] < 0.6
    assert b["plunger"]["L_lift"] > S.PLUNGER_SPRING["Ln"] + 2.0           # far from solid
    assert S.PLUNGER_SPRING["Di"] > S.PLUNGER_D + 0.1 and S.PLUNGER_SPRING["De"] < S.POCKET_D - 0.3
    # lever return: at rest it must still drag the hook back up a flank (finger ~0.24 N, 30°, mu 0.3,
    # 11.55 mm from the pivot: ~3 N·mm), with margin
    drag = 0.24 * math.tan(math.radians(30) + math.atan(S.MU)) * S.hook_home()[2]
    assert b["lever_return"]["T_rest"] > 1.5 * drag
    assert S.RETURN_PRELOAD + S.TAIL * S.lever_turn() < S.RETURN_SPRING["Ln"] - S.RETURN_SPRING["L0"]
