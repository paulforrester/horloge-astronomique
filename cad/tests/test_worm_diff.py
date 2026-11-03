"""Worm drive and spur differential (cad/lib/worm.py, cad/lib/differential.py)."""
import itertools
import math

import pytest

bd = pytest.importorskip("build123d")

from cad.lib.differential import SpurDifferential  # noqa: E402
from cad.lib.worm import Worm, place_worm, worm_centre_distance, worm_solid, worm_wheel  # noqa: E402


def test_worm_geometry_and_self_locking():
    w = Worm()
    assert w.lead_angle == pytest.approx(math.degrees(math.atan(math.pi / (math.pi * 12))))
    assert w.self_locking(mu=0.2)
    assert not Worm(starts=4).self_locking(mu=0.2)
    assert worm_centre_distance(60, w) == 36.0


def test_worm_meshes_with_its_wheel_at_every_angle():
    w = Worm()
    wheel = worm_wheel(60, w, 6.0, bore=8.0)
    worm = worm_solid(w, 24.0, bore=0).moved(bd.Location((0, 0, -12)))
    for psi in (0, 90, 180, 270):
        placed = place_worm(worm, 60, w, 6.0, psi=psi)
        turned = wheel.rotate(bd.Axis.Z, -psi / 60 * w.starts)
        assert (turned & placed).volume < 1e-6, psi
    closer = place_worm(worm, 60, w, 6.0).moved(bd.Location((0, -0.3, 0)))
    assert (wheel & closer).volume > 0.05                          # engaged, not just clear


def test_differential_gears_clear_each_other_and_engage():
    d = SpurDifferential()
    ps = d.parts()
    for a, b in itertools.combinations(ps, 2):
        assert (ps[a] & ps[b]).volume < 1e-6, (a, b)
    # pull each planet 0.3 mm towards its sun (P1 -> A, P2 -> B): it must collide
    for k, ((x1, y1, _), (x2, y2, _)) in enumerate(d.planet_positions()):
        for nm, (x, y), sun in ((f"planet_{k}_1", (x1, y1), "sun_A"), (f"planet_{k}_2", (x2, y2), "sun_B")):
            r = math.hypot(x, y)
            moved = ps[nm].moved(bd.Location((-x / r * 0.3, -y / r * 0.3, 0)))
            assert (moved & ps[sun]).volume > 0.05, nm


def test_differential_kinematics():
    # equal suns: B = 2c - A; carrier still: B = -A; carrier phi: B moves 2 phi
    assert SpurDifferential.output(1.0, 0.0) == -1.0
    assert SpurDifferential.output(0.0, 0.5) == 1.0
    d = SpurDifferential()
    assert d.planet_radius == 19.0 and d.outer_radius == 29.0
