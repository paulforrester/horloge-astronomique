"""E1, the two genies, detail design part 1 (docs/e1-design.md §16): the count wheel's program, the silencing,
the glass drive, the controller's view, and the model's cleanliness and service."""
import math
from fractions import Fraction

import build123d as bd
import pytest

from cad.lib.gears import centre_distance
from cad.modules.e1_angels import program as P


# ------------------------------------------------------------------------------------------------ the trains
def test_the_count_wheel_turns_once_in_twenty_bell_turns():
    assert Fraction(P.Z_B, P.Z_I1) * Fraction(P.Z_I2, P.Z_W) == Fraction(1, 20)     # exact [D]
    assert P.TURNS_PER_HOUR == 20 and P.STROKES_PER_HOUR == sum(P.QUARTER_STROKES) == 10


def test_the_axes_sit_at_the_centre_distances():
    g, ax = P.gears(), P.axes()
    assert math.dist(ax["B"], ax["I"]) == pytest.approx(centre_distance(g["b12"], g["i48"]), abs=1e-6)
    assert math.dist(ax["I"], ax["W"]) == pytest.approx(centre_distance(g["i12"], g["w60"]), abs=1e-6)
    assert math.dist(ax["W"], ax["C"]) == pytest.approx(centre_distance(g["sector"], g["c36"]), abs=1e-6)


def test_the_cross_shaft_runs_below_m1s_motor_adapters():
    """M1's adapters reach y −55.5; a Ø12 coupling on the cross shaft clears them, so M1's motors draw out."""
    assert P.axes()["C"][0] + 6.0 < -55.5 - 2.0


def test_the_sector_turns_the_cross_shaft_half_a_turn():
    assert P.SECTOR_TEETH * 360.0 / P.Z_C == pytest.approx(180.0)
    assert P.Z_SECTOR == P.Z_C                                     # 1:1 while engaged
    assert P.THETA_WC % 10.0 == pytest.approx(8.0)                 # 18 lattice teeth fit between c 182° and 358°


# ------------------------------------------------------------------------------------------------ the bell
def test_the_stroke_is_quick_and_the_cycle_ends_before_the_next_cue():
    t = P.timing()
    assert t["latency_s"] <= 0.3                                   # E2: the age strikes 1 s after the cue
    assert t["turn_s"] < t["pair_period_s"]                        # locked again long before the next cue


def test_the_snail_is_gentle():
    assert P.snail_pressure_angle() <= 30.0


def test_ten_strokes_then_ten_silent_turns():
    for k in range(20):
        c_drop = P.count_angle(k + P.U_DROP / 360.0)
        held = P.roller_radius(P.U_DROP + 1.0, c_drop)
        if k < 10:
            assert P.silencing(c_drop) == 0.0
            assert held < P.R_MAX - 3.0                            # the arm flicks to its bank: a stroke
        else:
            assert held >= P.R_MAX + 0.4 * P.SILENCE_LIFT          # held off the snail: silent


def test_the_silencing_cam_clears_the_pin_during_the_strokes_and_holds_it_after():
    s_bank = (P.R_MAX - (P.R_MIN + P.BANK_CLEAR)) / P.A_ROLLER
    pin_low = (P.PF[0] - P.W[0]) - P.A_PIN * s_bank                # the pin's centre, the arm at its bank
    for i in range(0, 1700):
        c = 0.5 + i * 0.1                                          # c 0.5 .. 170.4: every stroke of the hour
        assert P.silencing_cam_profile(-c) <= pin_low - P.PIN_D / 2 - P.CAM_CLEAR + 1e-6
    on = P.silencing_cam_radius(200.0)
    rest = (P.PF[0] - P.W[0]) - P.PIN_D / 2                        # the cam radius that just touches the cocked pin
    for k in range(10, 20):                                        # each silent drop: the roller is held off
        c = P.count_angle(k + P.U_DROP / 360.0)
        assert P.silencing_cam_profile(-c) >= rest + 0.2
    for i in range(0, 1700):
        c = 183.0 + i * 0.1                                        # c 183 .. 353: held fully (the ramps' envelopes
        #                                                            reach about 2.7° either side, the pin's width)
        assert P.silencing_cam_profile(-c) >= on - 0.05


def test_the_lever_is_lifted_and_lowered_on_the_snails_high_dwell():
    """The silencing ramps fall where the snail is at R_MAX, so the arm never twitches."""
    (u0, _), (d0, d1) = P.SILENCE_RAMPS
    for c in (u0, d0, d1):
        u = (c * P.TURNS_PER_HOUR) % 360.0
        assert u >= P.U_RISE[1] or u < P.U_DROP
        assert P.snail_radius(u) == P.R_MAX


def test_the_home_notch_takes_only_the_twentieth_lock():
    lo, hi = P.HOME_NOTCH
    stops = [k * 18.0 for k in range(1, 21)]
    inside = [c for c in stops if lo <= c < hi or lo <= c + 360.0 < hi]
    assert inside == [360.0]


def test_the_wire_cocks_the_arm_through_its_angle():
    assert P.tip_travel() == pytest.approx(3.6 * P.A_TIP / P.A_ROLLER)


# ------------------------------------------------------------------------------------------------ the glass
def test_the_crank_gives_exactly_half_a_pinion_turn():
    assert 2 * P.crank_radius() == pytest.approx(math.pi * P.pinion_pitch_radius())
    assert P.glass_angle(180.0) == pytest.approx(180.0)
    assert P.glass_angle(360.0) == pytest.approx(0.0, abs=1e-9)    # back the other way: alternates


def test_the_glass_turns_only_in_the_silent_half_and_takes_three_seconds():
    assert P.cross_shaft_turn(179.0) == 0.0 and P.cross_shaft_turn(360.0) == 180.0
    assert P.timing()["glass_s"] == pytest.approx(3.0)             # Paul: about 3 s


def test_a_crank_overrun_hardly_moves_the_glass():
    assert P.overrun_error(5.0) == pytest.approx(0.342, abs=1e-3)


# ------------------------------------------------------------------------------------------------ the controller
def test_a_normal_day_stays_in_step():
    r = P.simulate([1, 2, 3, 4] * 24)
    assert r["strokes"] == 240 and r["glass_turns"] == 24 and r["makeup_strokes"] == 0
    assert r["in_step"] and r["final_turns"] == 0


def test_quiet_hours_that_skip_whole_cycles_keep_the_count():
    r = P.simulate([1, 2, 3, 4] + [None] * 36 + [1, 2, 3, 4], makeup=False)
    assert r["in_step"] and r["glass_turns"] == 2


def test_a_skip_mid_cycle_is_made_up_alone_before_the_next_show():
    r = P.simulate([1, 2, None, 4])                                # :45 lost (a power cut)
    assert r["makeup_strokes"] == 3 and r["strokes"] == 7 and r["glass_turns"] == 1 and r["in_step"]
    r = P.simulate([1, 2, 3, None, 1])                             # the hour lost: the glass turns in the make-up
    assert r["makeup_strokes"] == 4 and r["glass_turns"] == 1 and r["final_turns"] == 1
    assert not P.simulate([1, 2, None, 4], makeup=False)["in_step"]


# ------------------------------------------------------------------------------------------------ the model
@pytest.fixture(scope="module")
def built():
    from cad.modules.e1_angels import mechanism as M
    a, data = M.build()
    return a, M.check(a, data)


def test_no_interference_and_everything_fits_the_bed(built):
    _, r = built
    assert r["interference"] == []
    assert r["bed_fit_single"] == [] and r["bed_fit_dual"] == []


def _hits(shape, others):
    sb = shape.bounding_box()
    out = []
    for o in others:
        ob = o.shape.bounding_box()
        if sb.max.X < ob.min.X or ob.max.X < sb.min.X or sb.max.Y < ob.min.Y or ob.max.Y < sb.min.Y or \
                sb.max.Z < ob.min.Z or ob.max.Z < sb.min.Z:
            continue
        v = (shape & o.shape).volume
        if v > 1e-3:
            out.append((o.name, round(v, 3)))
    return out


@pytest.fixture(scope="module")
def m1():
    from cad.modules.m1_time import mechanism as M1
    return M1.build()[0]


def test_e1_is_clear_of_m1(built, m1):
    a, _ = built
    clashes = [(i.name, h) for i in a.items for h in _hits(i.shape, m1.items)]
    assert clashes == []


def test_m1s_motors_still_draw_out_backwards(built, m1):
    """D16: M1's two NEMA 17 and their adapters leave straight back; E1's cross shaft passes below them."""
    a, _ = built
    for n in ("motor_M1", "motor_M1b", "adapter_M1", "adapter_M1b"):
        for dz in (-10.0, -40.0, -80.0):
            assert _hits(m1[n].shape.moved(bd.Location((0, 0, dz))), a.items) == [], (n, dz)


def test_the_gearmotor_lifts_out_upwards_with_its_saddle(built):
    """Paul, PR #23: the motor folded inside the bell tower. Undo the saddle's screws: the saddle, the gearmotor and
    its pinion lift straight up; the pinion leaves the bell shaft's 20 and touches nothing."""
    a, _ = built
    unit = ("gearmotor", "motor_pinion_20", "gearmotor_bracket")
    others = [i for i in a.items if i.name not in unit]
    for dy in (0.5, 5.0, 25.0, 60.0):
        for n in unit:
            assert _hits(a[n].shape.moved(bd.Location((0, dy, 0))), others) == [], (n, dy)


def test_the_gearmotor_stays_inside_the_towers_width(built):
    from cad.modules.e1_angels import mechanism as M
    a, _ = built
    bb = a["gearmotor"].shape.bounding_box()
    assert bb.min.X >= M.X_OUTER[0] - 1.0 and bb.max.X <= -82.0       # outer plate .. clear of M1's back plate (−81)
    assert math.dist(P.axes()["M"], P.axes()["B"]) == pytest.approx(centre_distance(P.gears()["drive"],
                                                                                    P.gears()["drive"]))


def test_the_sceptre_is_shown_cocked_and_its_tip_reaches_the_bell(built):
    from cad.modules.e1_angels import mechanism as M
    a, _ = built
    sx, sy = M.SHOULDER
    struck = a["sceptre_arm"].shape.rotate(bd.Axis((sx, sy, 0), (0, 0, 1)), P.COCK_DEG)
    gap = struck.distance_to(a["bell"].shape)
    assert 0.2 <= gap <= 1.0                                       # the bank: just short of the rim
    assert a["sceptre_arm"].shape.distance_to(a["bell"].shape) > 2.0   # at rest, cocked: clear
