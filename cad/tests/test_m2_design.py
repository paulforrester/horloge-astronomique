"""M2 detailed design: mechanism, calendar station, dial and the whole module checked together."""
import pytest

bd = pytest.importorskip("build123d")

from cad.modules.m2_main_dial import calendar as CAL  # noqa: E402
from cad.modules.m2_main_dial import dial as DIAL  # noqa: E402
from cad.modules.m2_main_dial import full as FULL  # noqa: E402
from cad.modules.m2_main_dial import mechanism as MECH  # noqa: E402


@pytest.fixture(scope="module")
def full():
    a, rep, cinfo = FULL.build()
    return a, FULL.check(a, rep, cinfo)


def test_whole_module_is_clean(full):
    _, r = full
    assert r["interference"] == []
    assert r["ring_sweep_conflicts"] == []          # nothing fixed in the turning ring's path but its readers
    assert r["bed_fit_single"] == [] and r["bed_fit_dual"] == []


def test_module_fits_the_bay_and_depth(full):
    _, r = full
    x0, x1 = r["envelope"]["x"]
    y0, y1 = r["envelope"]["y"]
    z0, z1 = r["envelope"]["z"]
    assert -232 <= x0 and x1 <= 232 and -196 <= y0 and y1 <= 217     # nothing within ~18 mm of the floor
    assert z1 - z0 < 200                                             # envelope.md: >= 200 mm interior


def test_trains_and_senses(full):
    _, r = full
    m = r["mechanism"]
    cds = {x["teeth"]: x["centre_distance"] for x in m["meshes"]}
    assert cds["154/169"] == 161.5 and cds["88/83"] == 85.5 and cds["84/84"] == 84.0
    assert cds["12/72"] == 52.5 and cds["12/48"] == 37.5             # 24:1 at module 1.25
    d = m["directions"]
    assert d["sun_tube"] == d["moon_tube"] == d["shadow_tube"]
    assert 48 * 72 // (12 * 12) == 24                                # motor turns per input-arbor turn


def test_dial_two_bodies_do_not_overlap():
    field, ring = DIAL.build()
    assert field.is_valid and ring.is_valid
    assert (field & ring).volume < 1e-6
    assert len(DIAL.ROMAN) == 12


def test_worm_gain():
    # 1 worm turn = 1 tooth of 60 = 6° of carrier = 12° at sun B; Sun 1:1, Moon 88/83
    assert 360 / MECH.WORM_TEETH * 2 == 12.0
    assert MECH.WORM.self_locking(mu=0.2)


def test_pointer_on_the_viewers_left(full):
    # DA p. 27 "à la droite du calendrier"; ELS i4 "sur la gauche de l'anneau, en face de la flèche"
    a, _ = full
    assert CAL.POINTER_ANGLE == 180.0
    for name in ("apollo_arrow", "stop_lever", "stop_switch", "witness_opto_1_March"):
        bb = a[name].shape.bounding_box()
        assert bb.max.X < -140 and abs((bb.min.Y + bb.max.Y) / 2) < 30, name
    # the readers pass through a window in the M2 front plate
    win = bd.Box(20, 20, 3).moved(bd.Location((-158.5, 0, (MECH.FP[0] + MECH.FP[1]) / 2)))
    assert (a["front_plate"].shape & win).volume < 1e-6


def test_carrier_is_a_printed_frame(full):
    # Paul, PR #5: works printed and independent of the case; plywood only if a print cannot do it
    from cad.lib.assembly import BED_DUAL
    a, _ = full
    segs = [i for i in a.items if i.name.startswith("carrier_segment_")]
    assert len(segs) == 4 and all(i.printed and i.material == "PETG" for i in segs)
    assert all(r["fits"] for r in a.bed_fit(BED_DUAL) if r["part"].startswith("carrier"))
    z_back = min(i.shape.bounding_box().min.Z for i in segs)
    assert z_back == pytest.approx(CAL.RIM_BACK_Z)                  # the L-section rim is there
    assert not [i.name for i in a.items if i.material == "wood"]
    import math
    for ang in CAL.CASE_TABS:                                        # each tab exists, with its M5 hole
        c = (CAL.CARRIER[1] + 7.0) * math.cos(math.radians(ang)), (CAL.CARRIER[1] + 7.0) * math.sin(math.radians(ang))
        probe = bd.Cylinder(6.0, 3.0).moved(bd.Location((c[0], c[1], CAL.RIM_BACK_Z + 2.0)))
        hole = bd.Cylinder(2.0, 3.0).moved(bd.Location((c[0], c[1], CAL.RIM_BACK_Z + 2.0)))
        tab = sum((i.shape & probe).volume for i in segs)
        assert tab > 0.5 * probe.volume and sum((i.shape & hole).volume for i in segs) < 1e-6, ang


def test_print_poses_need_support_only_in_the_sector_seat(full):
    from cad.lib.assembly import overhang_area, print_pose
    a, _ = full
    for k in (1, 2, 3):
        ring = a[f"ring_segment_{k}"]
        assert overhang_area(print_pose([ring.shape], ring.print_up)[0]) < 1.0
    assert overhang_area(print_pose([a["ring_segment_0"].shape], (0, 0, -1))[0]) > 1000   # documented
    for k in range(4):
        seg = a[f"carrier_segment_{k}"]
        assert overhang_area(print_pose([seg.shape], seg.print_up)[0]) < 600   # bridges between tab gussets
