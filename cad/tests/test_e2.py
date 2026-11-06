"""E2, the four ages and Death, detail design part 1 (docs/e2-design.md §10): the walk's selection, the layout
against the 2011 photograph, and the model's cleanliness."""
import math

import pytest

from cad.modules.e2_ages import layout as L


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


bd = pytest.importorskip("build123d")
from cad.modules.e2_ages import mechanism as M  # noqa: E402


def test_the_age_cam_sets_the_bell_finger_to_the_due_ages_peg():
    """At each quarter's show the cam's radius puts the finger at that quarter's age's peg height; between the
    old man and the child the cam ramps (no step the riding shaft could catch on)."""
    for k, minute in enumerate((15, 30, 45, 0)):
        r = M.age_cam_radius(minute)
        assert r - M.age_cam_radius(15) == pytest.approx(L.PEG_Z[k] - L.PEG_Z[0])
    rs = [M.age_cam_radius(1.0 + 6.0 * i / 60) for i in range(61)]
    assert all(b >= a - 1e-9 for a, b in zip(rs, rs[1:]))     # the rise is monotonic, spread over 6 min


PAST = 0.6     # deg: a peg pushed this far past its station (downstream) must run into an engaged finger


@pytest.mark.parametrize("selected", range(4))
def test_the_bell_finger_catches_only_the_selected_peg(selected):
    """Engaged at the selected age's height, the finger stops that age's peg at the bell station (it cannot pass
    it) and lets the other three by; withdrawn, it lets every peg by."""
    finger, _ = M.finger(L.PHI_BELL, L.PEG_Z[selected], engaged=True)
    for k in range(4):
        peg = M.peg_at(L.PHI_BELL - PAST, L.PEG_Z[k], L.PEG["r"][0], L.PEG["r"][1], L.PEG["d"])
        hit = (finger & peg).volume > 1e-3
        assert hit == (k == selected), (selected, k)
    off, _ = M.finger(L.PHI_BELL, L.PEG_Z[selected], engaged=False)
    for k in range(4):
        peg = M.peg_at(L.PHI_BELL - PAST, L.PEG_Z[k], L.PEG["r"][0], L.PEG["r"][1], L.PEG["d"])
        assert (off & peg).volume < 1e-6                       # withdrawn, it lets every peg by


def test_the_waiting_finger_catches_every_peg():
    finger, _ = M.finger(L.PHI_WAIT, None, z_lo=L.PEG_Z[-1] - 2.0, z_hi=L.PEG_Z[0] + 2.0, engaged=True)
    for k in range(4):
        peg = M.peg_at(L.PHI_WAIT - PAST, L.PEG_Z[k], L.PEG["r"][0], L.PEG["r"][1], L.PEG["d"])
        assert (finger & peg).volume > 1e-3
        at_station = M.peg_at(L.PHI_WAIT, L.PEG_Z[k], L.PEG["r"][0], L.PEG["r"][1], L.PEG["d"])
        assert (finger & at_station).volume < 1e-6            # it rests just against the finger, not in it


@pytest.fixture(scope="module")
def built():
    a, data = M.build()
    return a, M.check(a, data)


def test_no_interference_and_everything_fits_the_bed(built):
    _, r = built
    assert r["interference"] == []
    assert r["bed_fit_single"] == [] and r["bed_fit_dual"] == []
