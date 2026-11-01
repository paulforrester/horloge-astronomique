"""Gear geometry: radii, tooth thickness, backlash, meshing (cad/lib/gears.py)."""
import math

import pytest

from cad.lib.gears import (Gear, auto_shift, centre_distance, mesh_phase, min_teeth_without_undercut,
                           pair_shifts, rack, spur_gear, internal_gear)

bd = pytest.importorskip("build123d")


def test_radii_standard_and_shifted():
    g = Gear(89)
    assert (g.pitch_radius, g.tip_radius, g.root_radius) == (44.5, 45.5, 43.25)
    x = auto_shift(12)
    p = Gear(12, shift=x)
    assert p.tip_radius == pytest.approx(6 + 1 + x)
    assert p.root_radius == pytest.approx(6 - 1.25 + x)
    assert Gear(60, internal=True).tip_radius == 29 and Gear(60, internal=True).root_radius == 31.25


def test_auto_shift_rule_matches_bosl2():
    mt = min_teeth_without_undercut(20)
    assert mt == pytest.approx(17.0973, abs=1e-4)
    assert auto_shift(12) == pytest.approx(1 - 12 / mt)
    assert auto_shift(18) == 0.0


def test_pitch_thickness_includes_half_the_backlash():
    for g in [Gear(12, shift=auto_shift(12)), Gear(40), Gear(89, backlash=0.3)]:
        rs, half = g.tooth_flank(60)
        h = float(__import__("numpy").interp(g.pitch_radius, rs, half))
        arc = 2 * h * g.pitch_radius
        expect = g.module * (math.pi / 2 + 2 * g.shift * math.tan(g.alpha)) - g.backlash / 2
        assert arc == pytest.approx(expect, abs=2e-3)


def test_pair_shifts_keep_standard_centre_distance():
    x1, x2 = pair_shifts(12, 89)
    assert x2 == -x1 and centre_distance(Gear(12, shift=x1), Gear(89, shift=x2)) == 50.5
    a, b = pair_shifts(12, 14)                      # 14 cannot take a negative shift
    assert a > 0 and b > 0
    assert centre_distance(Gear(12, shift=a), Gear(14, shift=b)) > 13.0


def _pair(g1, g2, face=3.0, extra_cd=0.0, turn1=0.0, play2=0.0):
    a = centre_distance(g1, g2) + extra_cd
    p1 = spur_gear(g1, face).rotate(bd.Axis.Z, turn1)
    ang2 = mesh_phase(g1, g2) - turn1 * g1.teeth / g2.teeth + play2
    p2 = spur_gear(g2, face).rotate(bd.Axis.Z, ang2).moved(bd.Location((a, 0, 0)))
    return (p1 & p2).volume


@pytest.mark.parametrize("z1, z2", [(12, 89), (15, 99), (25, 169), (12, 14)])
def test_conjugate_meshing_has_no_interference(z1, z2):
    x1, x2 = pair_shifts(z1, z2)
    g1, g2 = Gear(z1, shift=x1), Gear(z2, shift=x2)
    for turn in (0.0, 7.3, 15.0):
        assert _pair(g1, g2, turn1=turn) < 1e-6, (z1, z2, turn)
    assert _pair(g1, g2, extra_cd=-0.5) > 0.1          # half a millimetre short collides


def test_backlash_is_the_angular_play():
    g1, g2 = Gear(20), Gear(60)
    play = math.degrees(g2.backlash / g2.pitch_radius)   # total play of the driven gear
    assert _pair(g1, g2, play2=+0.4 * play) < 1e-6
    assert _pair(g1, g2, play2=-0.4 * play) < 1e-6
    assert _pair(g1, g2, play2=+0.8 * play) > 0 or _pair(g1, g2, play2=-0.8 * play) > 0


def test_internal_gear_meshes():
    ring, pin = Gear(60, internal=True), Gear(18)
    r = internal_gear(ring, 3)
    for turn in (0.0, 5.0):
        p = spur_gear(pin, 3).rotate(bd.Axis.Z, turn).moved(bd.Location((centre_distance(ring, pin), 0, 0)))
        r_t = r.rotate(bd.Axis.Z, turn * pin.teeth / ring.teeth)
        assert (r_t & p).volume < 1e-6, turn


def test_rack_meshes_with_pinion():
    g = Gear(20)
    p = math.pi * g.module
    r = rack(g.module, 8, 3)
    pin = spur_gear(g, 3).rotate(bd.Axis.Z, -90).moved(bd.Location((3 * p, g.pitch_radius, 0)))
    assert (r & pin).volume < 1e-6
    pin_low = spur_gear(g, 3).rotate(bd.Axis.Z, -90).moved(bd.Location((3 * p, g.pitch_radius - 0.5, 0)))
    assert (r & pin_low).volume > 0.1


@pytest.mark.parametrize("z1, z2, theta, rot1", [(12, 54, -20.0, 0.0), (12, 64, 10.0, 13.0), (48, 48, 20.0, 3.3),
                                                 (15, 45, 270.0, 0.0), (20, 37, 133.0, 41.0)])
def test_mesh_rotation_meshes_at_any_angle(z1, z2, theta, rot1):
    from cad.lib.gears import mesh_rotation
    x1, x2 = pair_shifts(z1, z2)
    g1, g2 = Gear(z1, shift=x1), Gear(z2, shift=x2)
    a = centre_distance(g1, g2)
    p1 = spur_gear(g1, 3).rotate(bd.Axis.Z, rot1)
    r2 = mesh_rotation(g1, g2, theta, rot1)

    def placed(cd):
        x, y = cd * math.cos(math.radians(theta)), cd * math.sin(math.radians(theta))
        return spur_gear(g2, 3).rotate(bd.Axis.Z, r2).moved(bd.Location((x, y, 0)))
    assert (p1 & placed(a)).volume < 1e-6
    assert (p1 & placed(a - 0.4)).volume > 0.05       # engaged: 0.4 mm closer collides
