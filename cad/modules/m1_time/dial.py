"""M1 mean-time dial: a two-colour print, gilt on black, after Paul's photographs of 30 Oct 2026.

What the original shows [S: Paul's photographs IMG_0766–0768; docs/reference-notes.md]:
- a 12-hour face: gilt Roman numerals on a black ground, four written IIII, standing on the radius
  (their tops point outwards);
- a minute track (a band of short bars between two circles) with small figures 5 … 60 outside it;
- "TEMPS MOYEN" on an arc above the centre, "HEURE PUBLIQUE" on an arc below it (reading left to
  right, tops towards the centre);
- a pearled gilt bezel.

Two bodies, printed together face down (one per filament), as the M2 dial:
- **field** (black): the disc with pockets 0.6 mm deep;
- **gilt**: the numerals, the track, the figures and the lettering, filling the pockets flush.

Sizes: the dial is Ø 104 [E: the pearled minute ring is ≈ 0.83 m on the original, scaled on the
calendar ring in Paul's photograph, ±15 %]; the bezel Ø 120 [E: ≈ 0.98 m on the original, the same way]. Numeral height ≈ 0.1 of the dial, as photographed [E].
The figures (2.2 mm) and the lettering need the 0.2 mm nozzle.
"""
from __future__ import annotations

import math

import build123d as bd

from cad.lib import lettering as T
from cad.lib import parts
from cad.modules.m2_main_dial.dial import _bar, numeral

DIAL_D = 104.0                      # [E] see above
FIELD_T, INLAY_T = 2.0, 0.6
BORE = 6.6                          # the OD 6 tube (gilt hour hand) passes with clearance
NUM_R, NUM_H, NUM_STROKE = 34.0, 10.0, 1.3
ROMAN = ["XII", "I", "II", "III", "IIII", "V", "VI", "VII", "VIII", "IX", "X", "XI"]
TRACK = (44.0, 47.0)                # the minute track's two circles (centre lines)
TRACK_LINE = 0.4
FIG_R, FIG_H, FIG_STROKE = 48.0, 2.2, 0.35
TEXT_H, TEXT_STROKE = 3.4, 0.55
TOP_TEXT, TOP_R = "TEMPS MOYEN", 18.5
BOTTOM_TEXT, BOTTOM_R = "HEURE PUBLIQUE", 21.5
BEZEL = dict(od=120.0, id_lip=101.0, id_seat=DIAL_D + 0.4, z0=-FIELD_T - 0.6, z1=1.2, pearls=72,
             pearl_r=1.0, pearl_ring=55.0)


def _ring(r, w, n=180):
    from shapely.geometry import Point
    return Point(0, 0).buffer(r + w / 2, quad_segs=n // 4).difference(Point(0, 0).buffer(r - w / 2, quad_segs=n // 4))


def gilt_geometry():
    """All gilt marks as Shapely geometry in the dial plane (x right, y up, noon at the top)."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    geoms = []
    # numerals, standing on the radius, tops outwards (VI upside down at the bottom, as photographed)
    for k, label in enumerate(ROMAN):
        ang = 90.0 - 30.0 * k
        for f in numeral(label, NUM_H, NUM_STROKE):
            f = f.rotate(bd.Axis.Z, ang - 90.0).moved(
                bd.Location((NUM_R * math.cos(math.radians(ang)), NUM_R * math.sin(math.radians(ang)), 0)))
            geoms.append(Polygon([(v.X, v.Y) for v in f.outer_wire().vertices()]))
    # minute track: two circles and a bar per minute (wider at every fifth)
    geoms += [_ring(TRACK[0], TRACK_LINE), _ring(TRACK[1], TRACK_LINE)]
    for m in range(60):
        t = math.radians(90.0 - 6.0 * m)
        w = 0.8 if m % 5 == 0 else 0.45
        f = _bar(TRACK[0] * math.cos(t), TRACK[0] * math.sin(t), TRACK[1] * math.cos(t), TRACK[1] * math.sin(t), w)
        geoms.append(Polygon([(v.X, v.Y) for v in f.outer_wire().vertices()]))
    # figures 5 … 60 outside the track, tops outwards
    for m in range(5, 61, 5):
        lines = T.along_arc(str(m), 90.0 - 6.0 * m, FIG_R, FIG_H, FIG_STROKE, 0.25, clockwise=True)
        geoms.append(T.outline(lines, FIG_STROKE))
    # lettering
    geoms.append(T.outline(T.along_arc(TOP_TEXT, 90.0, TOP_R, TEXT_H, TEXT_STROKE, 0.5, clockwise=True), TEXT_STROKE))
    geoms.append(T.outline(T.along_arc(BOTTOM_TEXT, 270.0, BOTTOM_R, TEXT_H, TEXT_STROKE, 0.5, clockwise=False),
                           TEXT_STROKE))
    return T.clean(unary_union(geoms))


def build():
    """(field, gilt) solids, the dial face at z = 0, the field from z -2 to 0."""
    inlay = bd.extrude(bd.Compound(T.faces(gilt_geometry(), 0.0)), amount=INLAY_T, dir=(0, 0, -1))
    field = parts.disc(DIAL_D, FIELD_T, bore=BORE, z0=-FIELD_T) - inlay
    return field, inlay


def bezel():
    """The pearled gilt bezel: the dial sits in its seat, a lip covers the dial's edge."""
    b = BEZEL
    ring = parts.disc(b["od"], b["z1"] - b["z0"], bore=b["id_lip"], z0=b["z0"])
    ring -= parts.disc(b["id_seat"], -b["z0"] + 0.01, z0=b["z0"] - 0.01)            # the dial's seat
    for k in range(b["pearls"]):
        t = 2 * math.pi * k / b["pearls"]
        ring += bd.Sphere(b["pearl_r"]).moved(bd.Location((b["pearl_ring"] * math.cos(t), b["pearl_ring"] * math.sin(t),
                                                           b["z1"])))
    return ring - bd.Box(200, 200, 10, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(
        bd.Location((0, 0, b["z1"] + b["pearl_r"] * 0.7)))
