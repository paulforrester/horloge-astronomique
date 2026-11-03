"""Single-stroke lettering for printed inlays: no font files, the same result on every machine.

Each glyph is a set of polylines in a cell of cap height 1 (baseline y = 0, x from 0). Text is laid
out as polylines, mapped into the part's plane (straight, or bent round an arc), then thickened to
the stroke width with round caps and joins and merged (Shapely). The result is a list of
build123d faces, ready to extrude into a flush two-colour inlay.

Only the characters the calendar ring needs are drawn: digits, the capitals of the French month
names and of "COMMENCEMENT DE L'ANNÉE COMMUNE", the dominical letters A–G, É, Û and the apostrophe.
"""
from __future__ import annotations

import math

import numpy as np

W = 0.6           # default glyph width (fraction of the cap height)
WM = 0.78         # M
SPACE = 0.45


def _arc(cx, cy, rx, ry, a0, a1, n=10):
    return [(cx + rx * math.cos(math.radians(a)), cy + ry * math.sin(math.radians(a)))
            for a in np.linspace(a0, a1, n)]


def _glyphs() -> dict:
    w, h = W, 0.5
    g = {
        "0": [_arc(w / 2, h, w / 2, h, 0, 360, 20)],
        "1": [[(0.15 * w, 0.78), (0.55 * w, 1.0), (0.55 * w, 0.0)]],
        "2": [_arc(w / 2, 0.72, w / 2, 0.28, 165, -35, 10) + [(0.0, 0.0), (w, 0.0)]],
        "3": [_arc(w / 2, 0.75, 0.46 * w, 0.25, 150, -90, 9) + _arc(w / 2, 0.25, w / 2, 0.25, 90, -150, 10)[1:]],
        "4": [[(0.72 * w, 0.0), (0.72 * w, 1.0), (0.0, 0.32), (w, 0.32)]],
        "5": [[(0.92 * w, 1.0), (0.12 * w, 1.0), (0.06 * w, 0.56)] + _arc(w / 2, 0.31, w / 2, 0.31, 125, -150, 11)],
        "6": [[(0.85 * w, 0.95), (0.45 * w, 1.0), (0.1 * w, 0.75), (0.0, 0.3)], _arc(w / 2, 0.3, w / 2, 0.3, 0, 360, 16)],
        "7": [[(0.0, 1.0), (w, 1.0), (0.3 * w, 0.0)]],
        "8": [_arc(w / 2, 0.76, 0.42 * w, 0.24, 0, 360, 14), _arc(w / 2, 0.26, w / 2, 0.26, 0, 360, 16)],
        "9": [_arc(w / 2, 0.7, w / 2, 0.3, 0, 360, 16), [(w, 0.7), (w, 0.55), (0.55 * w, 0.0)]],
        "A": [[(0.0, 0.0), (w / 2, 1.0), (w, 0.0)], [(0.2 * w, 0.36), (0.8 * w, 0.36)]],
        "B": [[(0.55 * w, 0.52), (0.0, 0.52), (0.0, 1.0), (0.55 * w, 1.0)] + _arc(0.55 * w, 0.76, 0.4 * w, 0.24, 90, -90, 8),
              [(0.0, 0.52), (0.0, 0.0), (0.6 * w, 0.0)] + _arc(0.6 * w, 0.26, 0.4 * w, 0.26, -90, 90, 8) + [(0.0, 0.52)]],
        "C": [_arc(w / 2, h, w / 2, h, 50, 310, 14)],
        "D": [[(0.4 * w, 1.0), (0.0, 1.0), (0.0, 0.0), (0.4 * w, 0.0)] + _arc(0.4 * w, h, 0.6 * w, h, -90, 90, 12)],
        "E": [[(w, 1.0), (0.0, 1.0), (0.0, 0.0), (w, 0.0)], [(0.0, 0.52), (0.75 * w, 0.52)]],
        "F": [[(w, 1.0), (0.0, 1.0), (0.0, 0.0)], [(0.0, 0.52), (0.75 * w, 0.52)]],
        "G": [_arc(w / 2, h, w / 2, h, 45, 360, 16) + [(0.55 * w, h)]],
        "I": [[(0.0, 0.0), (0.0, 1.0)]],
        "J": [[(w, 1.0), (w, 0.3)] + _arc(w / 2, 0.3, w / 2, 0.3, 0, -180, 9)],
        "L": [[(0.0, 1.0), (0.0, 0.0), (w, 0.0)]],
        "M": [[(0.0, 0.0), (0.0, 1.0), (WM / 2, 0.3), (WM, 1.0), (WM, 0.0)]],
        "N": [[(0.0, 0.0), (0.0, 1.0), (w, 0.0), (w, 1.0)]],
        "O": [_arc(w / 2, h, w / 2, h, 0, 360, 20)],
        "P": [[(0.0, 0.0), (0.0, 1.0), (0.55 * w, 1.0)] + _arc(0.55 * w, 0.74, 0.45 * w, 0.26, 90, -90, 9) + [(0.0, 0.48)]],
        "R": [[(0.0, 0.0), (0.0, 1.0), (0.55 * w, 1.0)] + _arc(0.55 * w, 0.74, 0.45 * w, 0.26, 90, -90, 9) + [(0.0, 0.48)],
              [(0.45 * w, 0.48), (w, 0.0)]],
        "S": [_arc(w / 2, 0.75, w / 2, 0.25, 15, 270, 10) + _arc(w / 2, 0.25, w / 2, 0.25, 90, -165, 10)[1:]],
        "T": [[(0.0, 1.0), (w, 1.0)], [(w / 2, 1.0), (w / 2, 0.0)]],
        "U": [[(0.0, 1.0), (0.0, 0.35)] + _arc(w / 2, 0.35, w / 2, 0.35, 180, 360, 10) + [(w, 1.0)]],
        "V": [[(0.0, 1.0), (w / 2, 0.0), (w, 1.0)]],
        "'": [[(0.0, 1.0), (0.0, 0.72)]],
        " ": [],
    }
    g["É"] = g["E"] + [[(0.38 * w, 1.1), (0.68 * w, 1.24)]]
    g["Û"] = g["U"] + [[(0.2 * w, 1.1), (w / 2, 1.24), (0.8 * w, 1.1)]]
    return g


GLYPHS = _glyphs()


def width(ch: str) -> float:
    if ch == " ":
        return SPACE
    xs = [x for line in GLYPHS[ch] for x, _ in line]
    return max(xs) - min(xs)


def layout(text: str, h: float, stroke: float, spacing: float) -> tuple[list, float, tuple]:
    """Polylines of ``text`` at cap height ``h`` along +x from x = 0 (baseline y = 0).

    Returns (polylines, length, (y_min, y_max)); the length and y range include the stroke."""
    lines, x = [], 0.0
    for k, ch in enumerate(text):
        for line in GLYPHS[ch]:
            lines.append([(x + stroke / 2 + px * h, py * h) for px, py in line])
        x += width(ch) * h + stroke + (spacing if k < len(text) - 1 else 0.0)
    ys = [y for line in lines for _, y in line] or [0.0]
    return lines, x, (min(ys) - stroke / 2, max(ys) + stroke / 2)


def outline(polylines: list, stroke: float, resolution: int = 3):
    """Thicken polylines to ``stroke`` (round caps and joins) and merge them: a Shapely geometry."""
    from shapely.geometry import LineString, Point
    from shapely.ops import unary_union
    geoms = [LineString(p).buffer(stroke / 2, quad_segs=resolution) if len(p) > 1 else
             Point(p[0]).buffer(stroke / 2, quad_segs=resolution) for p in polylines if p]
    return unary_union(geoms)


def faces(geom, z: float = 0.0) -> list:
    """build123d faces (with holes) from a Shapely Polygon / MultiPolygon, in the plane z."""
    import build123d as bd
    polys = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
    out = []
    for p in polys:
        if p.is_empty:
            continue
        outer = bd.Wire.make_polygon([bd.Vector(x, y, z) for x, y in list(p.exterior.coords)[:-1]], close=True)
        holes = [bd.Wire.make_polygon([bd.Vector(x, y, z) for x, y in list(r.coords)[:-1]], close=True)
                 for r in p.interiors]
        out.append(bd.Face(outer, holes))
    return out


def radial(text: str, angle_deg: float, r_start: float, h: float, stroke: float, spacing: float,
           inward: bool = True) -> list:
    """Polylines of ``text`` written along the radius at ``angle_deg`` (plane XY), starting at
    ``r_start`` and reading inwards (or outwards), centred across the radius on its glyph extent."""
    lines, _, (y0, y1) = layout(text, h, stroke, spacing)
    t = math.radians(angle_deg)
    u = np.array((math.cos(t), math.sin(t)))
    d = -u if inward else u
    up = np.array((-d[1], d[0]))
    o = r_start * u
    yc = (y0 + y1) / 2
    return [[tuple(o + x * d + (y - yc) * up) for x, y in line] for line in lines]


def along_arc(text: str, centre_deg: float, r_base: float, h: float, stroke: float, spacing: float,
              clockwise: bool = True) -> list:
    """Polylines of ``text`` on the arc of radius ``r_base`` (its baseline), centred on
    ``centre_deg``, reading clockwise with the letters' tops outwards (or anticlockwise, tops in)."""
    lines, length, _ = layout(text, h, stroke, spacing)
    sgn = -1.0 if clockwise else 1.0
    a0 = math.radians(centre_deg) - sgn * (length / 2) / r_base
    out = []
    for line in lines:
        dense = []
        for (xa, ya), (xb, yb) in zip(line[:-1], line[1:]):                 # follow the curvature
            n = max(1, int(math.hypot(xb - xa, yb - ya) / 0.5))
            dense += [(xa + (xb - xa) * k / n, ya + (yb - ya) * k / n) for k in range(n)]
        dense.append(line[-1])
        pts = []
        for x, y in dense:
            r = r_base + (y if clockwise else -y)
            a = a0 + sgn * x / r_base
            pts.append((r * math.cos(a), r * math.sin(a)))
        out.append(pts)
    return out
