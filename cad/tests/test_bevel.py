"""Straight bevel gears (cad/lib/bevel.py): cone geometry, and a 1:1 right-angle pair that runs clear
and is engaged."""
import math

import pytest

bd = pytest.importorskip("build123d")

from cad.lib.bevel import Bevel, bevel_gear


def test_cone_geometry():
    b = Bevel(20, 20, module=1.0, face_width=4.5)
    assert b.pitch_angle == pytest.approx(45.0)
    assert b.pitch_radius == pytest.approx(10.0)
    assert b.cone_distance == pytest.approx(10 * math.sqrt(2))
    assert b.apex_z == pytest.approx(10.0)
    assert b.virtual.teeth == 28                                  # 20 / cos 45°
    assert b.ratio == 1.0
    # an unequal pair: the two pitch angles add up to the shaft angle
    p, w = Bevel(15, 30), Bevel(30, 15)
    assert p.pitch_angle + w.pitch_angle == pytest.approx(90.0)
    assert math.tan(math.radians(p.pitch_angle)) == pytest.approx(0.5)


@pytest.fixture(scope="module")
def pair():
    b = Bevel(20, 20, module=1.0, face_width=4.5)
    g = bevel_gear(b, bore=5.0)
    assert g.is_valid

    def A(spin):          # axis +Z, body on -Z, apex at the origin
        return g.rotate(bd.Axis.Z, spin).moved(bd.Location((0, 0, -b.apex_z)))

    def B(spin):          # axis +Y, body on -Y, apex at the origin
        return g.rotate(bd.Axis.Z, spin).moved(bd.Location((0, 0, -b.apex_z))).rotate(bd.Axis.X, -90)
    return b, A, B


def test_pair_runs_clear(pair):
    b, A, B = pair
    half = 180.0 / b.teeth
    for th in (0.0, 4.0, 11.0):             # A turns th, B turns -th about its own axis (1:1)
        assert (A(th) & B(half - th)).volume < 1e-3, th


def test_pair_is_engaged(pair):
    """1.5° either way (more than the 0.15 mm backlash, ≈ 0.86° at the pitch radius) makes them clash."""
    b, A, B = pair
    half = 180.0 / b.teeth
    for d in (-1.5, 1.5):
        assert (A(0) & B(half + d)).volume > 0.05, d
