"""M2 main dial face: a two-colour print (Paul, 3 Nov 2026).

Schwilgué: "Le cadran du temps apparent, peint en azur, est entouré d'un cercle en argent sur lequel
on voit deux fois les heures de 1 à 12 avec leurs subdivisions en minutes" [S: DA p. 30–32].

Two bodies, printed together on the H2D (one per filament):
- **field** (azure): the Ø 287.5 disc, 3 mm, with a 0.8 mm recess for the hour ring, and raised
  bosses that fill the numerals and ticks flush with the ring's surface;
- **hour ring** (silver): r 128 … 143.75, 0.8 mm, with the numerals and ticks cut through it.

So the numerals and ticks read azure on silver, with no paint and no font: the Roman numerals are
built from straight strokes (I, V, X). Noon (XII) is at the top and midnight (XII) at the bottom
[E: convention; the original's orientation is to be confirmed on a photo]. Ticks: every quarter hour
(long) and every 5 minutes (short).
"""
from __future__ import annotations

import math

import build123d as bd

from cad.lib import parts
from cad.modules.m2_main_dial import feasibility as F

R_RING_IN, R_RING_OUT = 128.0, F.DIAL_D / 2
RING_T = 0.8
NUMERAL_H = 7.0
STROKE = 1.0
ROMAN = ["XII", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI"]


def _bar(x0, y0, x1, y1, w):
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    nx, ny = -dy / L * w / 2, dx / L * w / 2
    pts = [(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)]
    return bd.Face(bd.Wire.make_polygon([bd.Vector(x, y, 0) for x, y in pts], close=True))


def glyph(ch: str, h: float, w: float):
    """Strokes of one Roman letter in a box of height h starting at x = 0; returns (faces, width)."""
    if ch == "I":
        return [_bar(w / 2, 0, w / 2, h, w)], w
    if ch == "V":
        W = 0.62 * h
        return [_bar(0 + w / 2, h, W / 2, 0 + w / 3, w), _bar(W / 2, w / 3, W - w / 2, h, w)], W
    if ch == "X":
        W = 0.62 * h
        return [_bar(w / 2, 0, W - w / 2, h, w), _bar(w / 2, h, W - w / 2, 0, w)], W
    raise ValueError(ch)


def numeral(text: str, h: float = NUMERAL_H, w: float = STROKE, gap: float = 0.8):
    faces, x = [], 0.0
    for ch in text:
        fs, W = glyph(ch, h, w)
        faces += [f.moved(bd.Location((x, 0, 0))) for f in fs]
        x += W + gap
    total = x - gap
    return [f.moved(bd.Location((-total / 2, -h / 2, 0))) for f in faces]


def marks():
    """All numeral and tick faces in the dial plane (z = 0)."""
    faces = []
    r_num = (R_RING_IN + R_RING_OUT) / 2 - 1.5
    for k in range(24):
        ang = 90.0 - 15.0 * k                       # clockwise from noon at the top
        label = ROMAN[k % 12]
        for f in numeral(label):
            # letters stand upright on the radius (their top points outwards)
            faces.append(f.rotate(bd.Axis.Z, ang - 90.0).moved(
                bd.Location((r_num * math.cos(math.radians(ang)), r_num * math.sin(math.radians(ang)), 0))))
    for k in range(24 * 12):                         # 5-minute ticks; quarter hours long
        ang = 90.0 - 360.0 * k / (24 * 12)
        long_ = k % 3 == 0
        if k % 12 == 0:
            continue                                  # the numeral sits there
        r0 = R_RING_OUT - (4.0 if long_ else 2.2)
        r1 = R_RING_OUT - 0.8
        t = math.radians(ang)
        faces.append(_bar(r0 * math.cos(t), r0 * math.sin(t), r1 * math.cos(t), r1 * math.sin(t), 0.7 if long_ else 0.5))
    return faces


def build():
    """(field, hour_ring) solids. The field sits from z -3 to 0, the ring in its recess."""
    m = marks()
    inlay = bd.extrude(bd.Compound(m), amount=RING_T, dir=(0, 0, 1)).moved(bd.Location((0, 0, -RING_T)))
    field = parts.disc(F.DIAL_D, 3.0, bore=10.5, z0=-3.0)
    recess = parts.disc(2 * R_RING_OUT + 1, RING_T + 1, bore=2 * R_RING_IN, z0=-RING_T)
    field = field - recess + inlay
    ring = parts.disc(2 * R_RING_OUT, RING_T, bore=2 * R_RING_IN, z0=-RING_T) - inlay
    return field, ring
