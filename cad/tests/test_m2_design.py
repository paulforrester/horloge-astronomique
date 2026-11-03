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
