"""E2, the four ages and Death, detail design parts 1 and 2a (docs/e2-design.md §10): the walk's selection, the
layout against the 2011 photograph, the stops, the walk train's program, the state module, and the model's
cleanliness."""
import math
from fractions import Fraction

import pytest

from cad.modules.e2_ages import layout as L
from cad.modules.e2_ages import program as G


@pytest.mark.parametrize("waiting", range(4))
@pytest.mark.parametrize("due", range(4))
def test_the_walk_always_strikes_the_due_age_and_leaves_the_next_waiting(waiting, due):
    """Every pair of resting age and due age (skipped shows included): the program runs one quarter turn per
    cycle until the due age is caught at the bell; then the next age waits at the right doorway."""
    r = L.simulate_walk(waiting, due)
    assert r.struck == due
    assert r.waiting == (due + 1) % 4
    assert r.cycles == (due - waiting) % 4 + 1
    assert r.travel == pytest.approx(90.0 * r.cycles)


def test_walk_timing_matches_pauls_observation():
    t = L.walk_timing()
    assert t["walk_on_s"] == pytest.approx(10.0)               # Paul, 6 Nov 2026
    assert L.RING_SPEED == pytest.approx(6.0)                  # 1 rpm
    assert t["slip_A_deg"] > 0 and t["slip_B_deg"] > 0        # each phase ends with a little clutch slip


def test_layout_matches_the_2011_photograph():
    """The waiting ages stand in the doorways, between the back wall's ends and the piers, at Death's depth;
    the age at the bell stands just right of the ages' bell, near enough to strike it."""
    for phi in (L.PHI_WAIT, L.PHI_WAIT - L.PHI_SPACING):
        x, y = L.polar(phi, L.R_PATH)
        assert L.BACK_WALL["x"] < abs(x) < L.PIER["x"][0]
        assert abs(y) < L.BACK_WALL["y"][1]
        assert 0.41 <= abs(x) / L.W <= 0.51                   # photo: +0.41 W and -0.46 W
    bx, by = L.polar(L.PHI_BELL, L.R_PATH)
    gap = math.hypot(bx - L.BELL["x"], by - L.BELL["y"]) - L.BELL["d"] / 2 - 5.5
    assert bx > L.BELL["x"] and 3.0 < gap < 12.0              # its attribute reaches the bell


def test_figure_heights_are_the_decided_ones():
    assert L.DEATH_H == 78.0 and dict(L.AGES)["old_man"] == 78.0
    assert dict(L.AGES)["child"] == pytest.approx(0.75 * 78.0)


# ------------------------------------------------------------------------------------------------ the program
def test_the_phase_travel_used_by_the_walk_simulation_is_the_programs():
    lim = G.ring_travel_limits()
    assert lim["A"] == pytest.approx(L.PHASE_TRAVEL["A"], abs=0.05)
    assert lim["B"] == pytest.approx(L.PHASE_TRAVEL["B"], abs=0.05)


def test_the_program_leaves_margins_for_the_walk():
    """The lock switch closes up to 4° (program) before each stop angle. Even so the waiting age reaches the bell
    in phase A (30°), the struck age reaches the left doorway in phase B (60°), with 5° of clutch slip to spare;
    in a skipped show the waiting arm is back in well before the next waiting peg comes (90°), and one program
    turn carries the ring a full quarter."""
    lim, lead = G.ring_travel_limits(), 4.0 * G.ring_deg_per_program_deg()
    assert lim["A"] - lead >= 30.0 + 5.0
    assert lim["B"] - lead >= 60.0 + 5.0
    assert lim["free"] <= 90.0 - 20.0
    assert lim["turn"] - lead >= 90.0 + 5.0


def test_one_arm_always_holds_or_can_hold():
    """BA: the bell arm can hold before the waiting arm lets the waiting age go; AB: the waiting arm can hold
    before the bell arm lets the struck age go."""
    e = G.events()
    assert e["bell_holds"] < e["wait_lets_go"] < G.TRANSITION
    assert G.LOCK_N < e["wait_holds"] < e["bell_lets_go"] < G.LOCK_N + G.TRANSITION
    assert G.alpha_catch() < G.alpha_clear() < L.STOP["swing"]


def test_the_program_cam_is_gentle_enough():
    assert G.pressure_angle_max() <= 40.0


def test_the_lock_switch_closes_only_at_the_two_stops():
    for t in G.LOCK_NOTCHES:
        assert G.lock_closed(t)
    for t in (20.0, 90.0, 200.0, 300.0):
        assert not G.lock_closed(t)


def test_the_walk_train_turns_the_ring_at_6_deg_per_s():
    """Gearmotor ≈ 32 rpm [E] -> 12/24 -> walk shaft -> 16/264 -> the ring ≈ 1 rpm = 6°/s (Paul's 10 s walk on);
    one program turn = 6 turns of the walk shaft (12'/72)."""
    ring_rpm = 32.0 * Fraction(12, 24) * Fraction(16, 264)
    assert float(ring_rpm) * 6.0 == pytest.approx(L.RING_SPEED, rel=0.05)
    assert G.PROG_RATIO * G.WALK_PINION / L.TEETH["z"] == pytest.approx(G.ring_deg_per_program_deg())


def test_the_motion_work_is_one_twelfth():
    assert Fraction(12, 48) * Fraction(15, 45) == Fraction(1, 12)
    assert 12 + 48 == 15 + 45                                  # one centre distance (30 at m 1)


bd = pytest.importorskip("build123d")
from cad.modules.e2_ages import drives as D  # noqa: E402
from cad.modules.e2_ages import mechanism as M  # noqa: E402


def test_the_age_cam_sets_the_bell_arm_to_the_due_ages_peg():
    """At each quarter's show the cam's radius puts the bell arm at that quarter's age's peg height; between the
    old man and the child the cam ramps (no step the riding rod could catch on)."""
    for k, minute in enumerate((15, 30, 45, 0)):
        r = M.age_cam_radius(minute)
        assert r - M.age_cam_radius(15) == pytest.approx(L.PEG_Z[k] - L.PEG_Z[0])
    rs = [M.age_cam_radius(1.0 + 6.0 * i / 60) for i in range(61)]
    assert all(b >= a - 1e-9 for a, b in zip(rs, rs[1:]))     # the rise is monotonic, spread over 6 min


def test_the_snails_give_the_counts():
    assert [D.quarter_snail_radius(m) for m in (15, 30, 45, 0)] == list(D.SNAIL_Q)
    assert [D.hour_snail_radius(h) for h in range(1, 13)] == list(D.SNAIL_H)
    assert all(a > b for a, b in zip(D.SNAIL_H, D.SNAIL_H[1:]))   # more strokes, deeper fall


PAST = 0.6     # deg: a peg pushed this far past its station (downstream) must run into a holding arm


def _peg(phi, z, kind="sel"):
    p = L.PEG if kind == "sel" else L.WAIT_PEG
    return M.peg_at(phi, z, p["r"][0], p["r"][1], p["d"])


def _bell_arm(z_sel, swing):
    sb = G.plan()["bell_shaft"]
    return D.stop_arm(sb, z_sel - L.STOP["h"] / 2, z_sel + L.STOP["h"] / 2, swing, hub_d=7.0)


def _wait_arm(swing):
    sw = G.plan()["wait_shaft"]
    return D.stop_arm(sw, *L.STOP["wait_z"], swing)


@pytest.mark.parametrize("selected", range(4))
def test_the_bell_arm_catches_only_the_selected_peg(selected):
    """In, at the selected age's height, the bell arm stops that age's peg at the bell station and lets the other
    three by, and every waiting peg; swung out, it lets every peg by."""
    st = L.stop_phis()["bell_station"]
    arm = _bell_arm(L.PEG_Z[selected], 0.0)
    for k in range(4):
        hit = (arm & _peg(st - PAST, L.PEG_Z[k])).volume > 1e-3
        assert hit == (k == selected), (selected, k)
    assert (arm & _peg(st - PAST, L.WAIT_PEG["z"], "wait")).volume < 1e-6
    out = _bell_arm(L.PEG_Z[selected], L.STOP["swing"])
    for k in range(4):
        for d in (0.0, PAST, 3.0):
            assert (out & _peg(st - d, L.PEG_Z[k])).volume < 1e-6


def test_the_waiting_arm_catches_every_waiting_peg_and_no_selection_peg():
    st = L.stop_phis()["wait_station"]
    arm = _wait_arm(0.0)
    assert (arm & _peg(st - PAST, L.WAIT_PEG["z"], "wait")).volume > 1e-3
    assert (arm & _peg(st, L.WAIT_PEG["z"], "wait")).volume < 1e-6      # it rests just against the arm
    for z in L.PEG_Z:
        assert (arm & _peg(st - PAST, z)).volume < 1e-6
    out = _wait_arm(L.STOP["swing"])
    for d in (0.0, PAST, 3.0):
        assert (out & _peg(st - d, L.WAIT_PEG["z"], "wait")).volume < 1e-6


def test_the_waiting_peg_puts_the_age_at_the_doorway():
    assert L.stop_phis()["wait_station"] - L.WAIT_PEG_OFFSET == pytest.approx(L.PHI_WAIT)
    assert L.stop_spacing() == pytest.approx(math.dist(G.plan()["bell_shaft"], G.plan()["wait_shaft"]))


@pytest.mark.parametrize("shaft", ["bell_shaft", "wait_shaft"])
def test_each_arm_swings_out_downstream(shaft):
    """A held peg pushes its arm downstream (φ decreasing); each arm releases by swinging that way, so the peg's
    push helps, and nothing is pushed back against the clutch."""
    s = G.plan()[shaft]
    reach = math.dist(s, L.C) - L.STOP["tip"]

    def tip(sw):
        a = math.radians(G.radial_dir(s) + sw)
        return (s[0] + reach * math.cos(a), s[1] + reach * math.sin(a))

    phis = [L.phi_of(tip(sw)) for sw in (0.0, 10.0, 30.0, 50.0)]
    assert all(b < a for a, b in zip(phis, phis[1:]))


@pytest.fixture(scope="module")
def built():
    a, data = M.build()
    return a, M.check(a, data)


def test_no_interference_and_everything_fits_the_bed(built):
    _, r = built
    assert r["interference"] == []
    assert r["bed_fit_single"] == [] and r["bed_fit_dual"] == []


def _withdraw(a, unit, moves, allowed=()):
    others = [i for i in a.items if i.name not in unit and i.name not in allowed]
    for mv in moves:
        for n in unit:
            moved = a[n].shape.moved(bd.Location(mv))
            mb = moved.bounding_box()
            for o in others:
                ob = o.shape.bounding_box()
                if mb.max.X < ob.min.X or ob.max.X < mb.min.X or mb.max.Y < ob.min.Y or ob.max.Y < mb.min.Y or \
                        mb.max.Z < ob.min.Z or ob.max.Z < mb.min.Z:
                    continue
                v = (moved & o.shape).volume
                assert v < 1e-3, f"{n} moved {mv} hits {o.name} ({v:.3f} mm³)"


def test_the_state_stepper_withdraws_to_the_right(built):
    """D16: undo two M3 and draw the NEMA 17, its adapter and its shaft out to the right; the D-shaft leaves the
    coupling's socket and touches nothing."""
    a, _ = built
    _withdraw(a, ["state_motor", "state_motor_shaft", "state_motor_adapter"],
              [(dx, 0, 0) for dx in (0.2, 3.0, 10.0, 26.0)])


def test_the_walk_gearmotor_drops_out_with_its_pinion(built):
    """Undo the bracket's two M2: the gearmotor, its pinion and the bracket come down and out; the pinion passes
    the deck's Ø16 hole."""
    a, _ = built
    _withdraw(a, ["walk_motor", "walk_motor_pinion_12", "walk_motor_bracket"],
              [(0, 0, dz) for dz in (-0.2, -3.0, -10.0, -40.0)])


def test_the_rest_state_holds_the_child_at_the_doorway(built):
    """At rest (12:10, program 0): the waiting arm is in, 0.2 mm in front of the child's waiting peg; the bell arm
    is out, clear of every peg."""
    a, r = built
    assert r["stops"]["swing"] == {"bell": L.STOP["swing"], "wait": 0.0}
    assert a["wait_arm"].shape.distance_to(a["ring"].shape) == pytest.approx(L.STOP["gap"], abs=0.05)
    assert a["bell_arm"].shape.distance_to(a["ring"].shape) > 2.0
