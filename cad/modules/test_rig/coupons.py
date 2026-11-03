"""Tolerance coupons, printed with the test rig (BOM Batch 1: tolerance, bearing-seat tests).

They turn the [E] allowances in ``cad/lib/parts.py`` (FITS) and the working module (D4, CLAUDE.md:
"the real minimum will be set later by a physical tolerance test") into measured values.

1. ``fit_coupon``: Ø3, Ø5 and Ø8 holes, each with diametral allowances from -0.10 to +0.40 mm.
   Push each rod in: note press / slide / run for each hole.
2. ``bearing_coupon``: pockets for MR85ZZ (Ø8) and 688ZZ (Ø16) with OD allowances -0.10 … +0.15.
3. ``gear_board`` + its gears: 15/30 pairs at module 1.0, 0.8 and 0.6 × backlash 0.10, 0.15 and
   0.20 mm, on Ø3 pins at the nominal centre distance. Turn each pair by hand: note binding, play,
   noise.

Orientation marks: every coupon has its low-allowance end at the chamfered corner (bottom left as
modelled), and allowances rise to the right. Rows run bottom to top in the order listed.
"""
from __future__ import annotations

import build123d as bd

from cad.lib import parts
from cad.lib.assembly import Assembly
from cad.lib.gears import Gear, centre_distance, pair_shifts, spur_gear
from cad.lib.hardware import BEARINGS

FIT_ALLOWANCES = (-0.10, -0.05, 0.00, 0.10, 0.20, 0.30, 0.40)
SEAT_ALLOWANCES = (-0.10, -0.05, 0.00, 0.05, 0.10, 0.15)
MODULES = (1.0, 0.8, 0.6)
BACKLASHES = (0.10, 0.15, 0.20)


def _corner_mark(w, h, t, size=6.0):
    """Triangular prism removed from the bottom-left corner: the orientation mark."""
    tri = bd.Face(bd.Wire.make_polygon([bd.Vector(-w / 2, -h / 2, 0), bd.Vector(-w / 2 + size, -h / 2, 0),
                                        bd.Vector(-w / 2, -h / 2 + size, 0)], close=True))
    return bd.extrude(tri, amount=t + 2, dir=(0, 0, 1)).moved(bd.Location((0, 0, -1)))


def fit_coupon(thickness: float = 6.0):
    rods = (3.0, 5.0, 8.0)
    pitch, row = 14.0, 14.0
    w, h = pitch * len(FIT_ALLOWANCES) + 8, row * len(rods) + 8
    holes = []
    for j, d in enumerate(rods):
        for i, al in enumerate(FIT_ALLOWANCES):
            holes.append((-w / 2 + 4 + pitch * (i + 0.5), -h / 2 + 4 + row * (j + 0.5), d + al))
    return parts.plate((w, h), thickness, holes=holes) - _corner_mark(w, h, thickness)


def bearing_coupon(thickness: float = 7.0):
    names = ("MR85ZZ", "688ZZ")
    pitch, row = 22.0, 24.0
    w, h = pitch * len(SEAT_ALLOWANCES) + 8, row * len(names) + 8
    part = parts.plate((w, h), thickness)
    for j, nm in enumerate(names):
        b = BEARINGS[nm]
        for i, al in enumerate(SEAT_ALLOWANCES):
            x, y = -w / 2 + 4 + pitch * (i + 0.5), -h / 2 + 4 + row * (j + 0.5)
            pocket = parts.disc(b.od + al, b.width + 1, z0=thickness - b.width) + \
                parts.disc(b.od - 2.0, thickness + 2, z0=-1)            # through hole leaves a 1 mm shoulder
            part -= pocket.moved(bd.Location((x, y, 0)))
    return part - _corner_mark(w, h, thickness)


def gear_board(z1: int = 15, z2: int = 30, thickness: float = 5.0, pin: float = 3.0):
    """Board with press holes for Ø3 pins at each pair's nominal centre distance, plus the gears."""
    cell_w, cell_h = 62.0, 42.0
    w, h = cell_w * len(BACKLASHES) + 6, cell_h * len(MODULES) + 6
    holes, gears = [], []
    for j, m in enumerate(MODULES):
        for i, bl in enumerate(BACKLASHES):
            x1, x2 = pair_shifts(z1, z2)
            g1, g2 = Gear(z1, m, shift=x1, backlash=bl), Gear(z2, m, shift=x2, backlash=bl)
            cd = centre_distance(g1, g2)
            cx, cy = -w / 2 + 3 + cell_w * (i + 0.5), -h / 2 + 3 + cell_h * (j + 0.5)
            p1, p2 = (cx - cd / 2, cy), (cx + cd / 2, cy)
            holes += [(p1[0], p1[1], pin + parts.FITS.press), (p2[0], p2[1], pin + parts.FITS.press)]
            tag = f"m{m:g}_b{bl:.2f}".replace(".", "p")
            gears.append((f"gear_{tag}_{z1}", g1, p1))
            gears.append((f"gear_{tag}_{z2}", g2, p2))
    board = parts.plate((w, h), thickness, holes=holes) - _corner_mark(w, h, thickness)
    return board, gears


def build() -> Assembly:
    a = Assembly("tolerance_coupons")
    a.add("fit_coupon", fit_coupon())
    a.add("bearing_coupon", bearing_coupon().moved(bd.Location((0, 75, 0))))
    board, gears = gear_board()
    off = (0, 190)
    a.add("gear_board", board.moved(bd.Location((off[0], off[1], 0))))
    from cad.lib.gears import mesh_phase
    for k, (name, g, p) in enumerate(gears):
        part = spur_gear(g, 4.0) - parts.disc(3.0 + parts.FITS.running, 10, z0=-1)
        rot = 0.0 if k % 2 == 0 else mesh_phase(gears[k - 1][1], g)
        a.add(name, part.rotate(bd.Axis.Z, rot).moved(bd.Location((p[0] + off[0], p[1] + off[1], 5.5))),
              explode=(0, 0, 25))
    return a
