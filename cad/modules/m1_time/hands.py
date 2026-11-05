"""M1's four hands and the centre cap, after Paul's photographs of 30 Oct 2026 (IMG_0766).

- **gilt minute hand** (mean time): a slender blade with an ornate lozenge near the tip and a short
  counter-tail;
- **gilt hour hand** (mean time): an openwork fleur;
- **silver minute and hour hands** (legal time): plain spears.
A gilt cap covers the centre. Each hand is a flat print (0.2 mm nozzle), its boss pressed onto its
tube or arbor. Lengths [E]: the minute hands reach the minute track, the hour hands the numerals'
inner ends, as photographed.
"""
from __future__ import annotations

import build123d as bd

from cad.lib import parts

T = 1.0                                         # hand thickness
LEN = {"gilt_minute": 45.5, "silver_minute": 44.0, "silver_hour": 27.5, "gilt_hour": 27.0}


def _poly(points):
    from shapely.geometry import Polygon
    return Polygon(points)


def outline(kind: str):
    """Shapely outline of a hand pointing along +Y from its centre (boss not included)."""
    from shapely.geometry import Point
    from shapely.ops import unary_union
    L = LEN[kind]
    if kind == "gilt_minute":
        blade = _poly([(-0.9, -9.0), (0.9, -9.0), (0.75, L * 0.80), (0.0, L), (-0.75, L * 0.80)])
        lozenge = _poly([(0.0, L * 0.70), (2.0, L * 0.79), (0.0, L * 0.88), (-2.0, L * 0.79)])
        hole = _poly([(0.0, L * 0.745), (0.8, L * 0.79), (0.0, L * 0.835), (-0.8, L * 0.79)])
        tail = Point(0.0, -9.0).buffer(2.0, quad_segs=10)
        return unary_union([blade, lozenge.difference(hole), tail])
    if kind == "gilt_hour":
        stem = _poly([(-1.1, -6.0), (1.1, -6.0), (0.9, L * 0.62), (-0.9, L * 0.62)])
        head = Point(0.0, L * 0.76).buffer(3.6, quad_segs=12)
        holes = unary_union([Point(-1.45, L * 0.74).buffer(1.05, quad_segs=8),
                             Point(1.45, L * 0.74).buffer(1.05, quad_segs=8)])
        tip = _poly([(-1.6, L * 0.86), (1.6, L * 0.86), (0.0, L)])
        tail = Point(0.0, -6.0).buffer(1.8, quad_segs=10)
        return unary_union([stem, head.difference(holes), tip, tail])
    if kind in ("silver_minute", "silver_hour"):
        w = 0.7 if kind == "silver_minute" else 0.9
        head = 1.8 if kind == "silver_minute" else 2.4
        shaft = _poly([(-w, -6.0), (w, -6.0), (w, L * 0.82), (-w, L * 0.82)])
        spear = _poly([(-head, L * 0.84), (0.0, L), (head, L * 0.84), (0.0, L * 0.78)])
        return unary_union([shaft, spear])
    raise ValueError(kind)


def hand(kind: str, bore: float, z0: float, angle_deg: float):
    """The printed hand: outline + boss, bored for its tube, at z0, pointing at angle_deg
    (clockwise from noon, as on a clock face)."""
    from cad.lib import lettering as LT
    geom = LT.clean(outline(kind))
    body = bd.extrude(bd.Compound(LT.faces(geom, 0.0)), amount=T, dir=(0, 0, 1))
    boss = parts.disc(bore + 3.2, T, z0=0.0)
    part = (body + boss) - parts.disc(bore + parts.FITS.press, 3 * T, z0=-T)
    return part.rotate(bd.Axis.Z, -angle_deg).moved(bd.Location((0, 0, z0)))


def cap(z0: float, bore: float = 3.0):
    """The gilt centre cap: a small dome pressed on the Ø3 arbor's tip."""
    dome = bd.Sphere(2.6).moved(bd.Location((0, 0, z0)))
    dome -= bd.Box(10, 10, 5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).moved(bd.Location((0, 0, z0)))
    dome = dome.moved(bd.Location((0, 0, 0))) + parts.disc(5.2, 0.6, z0=z0)
    dome -= parts.disc(bore + parts.FITS.press, 1.8, z0=z0 - 0.1)
    return dome
