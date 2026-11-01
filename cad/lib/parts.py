"""Shared parametric parts: arbors, tubes, hubs, bearing seats, plates, standoffs, cams.

Every printed fit uses the allowances in ``FITS``. They are estimates [E] until the local tolerance
test (CLAUDE.md: the real minimum comes from a physical test); change them in one place.
All parts are built along +Z from z = 0 unless stated.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Iterable

import numpy as np

from .gears import Gear, spur_gear
from .hardware import BEARINGS, SCREWS, Bearing, Tube


@dataclass
class Fits:
    """Diametral allowances added to printed holes (mm) [E, to be replaced by the tolerance test]."""
    running: float = 0.30     # printed hole turning freely on a rod or tube
    sliding: float = 0.20     # hole that slides on assembly, then is clamped
    press: float = -0.05      # printed hole pressed onto a rod or tube
    bearing_seat: float = 0.0  # pocket for a bearing OD (D4: from measured bearings)


FITS = Fits()


def _cyl(r: float, h: float, z0: float = 0.0):
    import build123d as bd
    return bd.Cylinder(r, h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((0, 0, z0)))


# --- bought items as solids (for layout, interference and renders) --------------------------------
def rod(d: float, length: float, z0: float = 0.0):
    return _cyl(d / 2, length, z0)


def tube(t: Tube, length: float, z0: float = 0.0):
    return _cyl(t.od / 2, length, z0) - _cyl(t.id / 2, length + 2, z0 - 1)


def bearing(b: Bearing | str, z0: float = 0.0):
    b = BEARINGS[b] if isinstance(b, str) else b
    return _cyl(b.od / 2, b.width, z0) - _cyl(b.bore / 2, b.width + 2, z0 - 1)


# --- printed parts ----------------------------------------------------------------------------------
def hub(bore: float, od: float, length: float, fit: str = "press", z0: float = 0.0):
    """Plain printed hub (boss) for a gear, on a rod or tube of diameter ``bore``."""
    allowance = getattr(FITS, fit)
    return _cyl(od / 2, length, z0) - _cyl((bore + allowance) / 2, length + 2, z0 - 1)


def gear_on_hub(g: Gear, face: float, bore: float, hub_od: float | None = None, hub_len: float = 0.0,
                fit: str = "press"):
    """Spur gear with a bore and an optional boss on its back (+Z), as one printable part."""
    import build123d as bd
    part = spur_gear(g, face)
    if hub_len > 0:
        hub_od = hub_od or max(bore + 6, 10.0)
        part = part + _cyl(hub_od / 2, hub_len, face)
    part -= _cyl((bore + getattr(FITS, fit)) / 2, face + hub_len + 2, -1)
    return part


def bearing_seat_cut(b: Bearing | str, depth: float | None = None, z0: float = 0.0, through: float = 0.0):
    """Solid to subtract from a plate: a pocket for the bearing plus an optional through hole."""
    b = BEARINGS[b] if isinstance(b, str) else b
    depth = b.width if depth is None else depth
    cut = _cyl((b.od + FITS.bearing_seat) / 2, depth, z0)
    if through:
        cut = cut + _cyl((b.od - 2) / 2, through, z0 - through)   # leaves a 1 mm shoulder
    return cut


def plate(outline: Iterable[tuple[float, float]] | tuple[float, float], thickness: float,
          holes: Iterable[tuple[float, float, float]] = (), z0: float = 0.0, corner_radius: float = 0.0):
    """Flat plate. ``outline`` is a polygon or (width, height) centred on the origin.

    ``holes`` are (x, y, diameter) through holes.
    """
    import build123d as bd
    if isinstance(outline, tuple) and len(outline) == 2 and not hasattr(outline[0], "__len__"):
        w, h = outline
        face = bd.Rectangle(w, h)
        if corner_radius:
            face = bd.fillet(face.vertices(), corner_radius)
    else:
        pts = [bd.Vector(float(x), float(y), 0) for x, y in outline]
        face = bd.Face(bd.Wire.make_polygon(pts, close=True))
    part = bd.extrude(face, amount=thickness, dir=(0, 0, 1)).moved(bd.Location((0, 0, z0)))
    for x, y, d in holes:
        part -= _cyl(d / 2, thickness + 2, z0 - 1).moved(bd.Location((x, y, 0)))
    return part


def disc(diameter: float, thickness: float, bore: float = 0.0, z0: float = 0.0):
    part = _cyl(diameter / 2, thickness, z0)
    if bore:
        part -= _cyl(bore / 2, thickness + 2, z0 - 1)
    return part


def standoff(height: float, od: float = 7.0, screw: str = "M3", z0: float = 0.0):
    """Printed pillar between two plates, with a clearance hole for a through screw."""
    return _cyl(od / 2, height, z0) - _cyl(SCREWS[screw].clearance / 2, height + 2, z0 - 1)


def hand(length: float, width: float, thickness: float, boss_d: float, bore: float,
         tail: float = 0.0, z0: float = 0.0):
    """Simple straight hand along +X with a boss at the origin and an optional counter-tail."""
    import build123d as bd
    body = bd.extrude(bd.Rectangle(length + tail, width).moved(bd.Location(((length - tail) / 2, 0, 0))),
                      amount=thickness, dir=(0, 0, 1))
    part = (body + _cyl(boss_d / 2, thickness)) - _cyl(bore / 2, thickness + 2, -1)
    return part.moved(bd.Location((0, 0, z0)))


def radial_cam(profile: Callable[[float], float], thickness: float, bore: float, samples: int = 360,
               z0: float = 0.0):
    """Plate cam from a radius function r(theta), theta in radians over one turn."""
    import build123d as bd
    th = np.linspace(0, 2 * math.pi, samples, endpoint=False)
    pts = [bd.Vector(float(profile(t) * math.cos(t)), float(profile(t) * math.sin(t)), 0) for t in th]
    face = bd.Face(bd.Wire([bd.Edge.make_spline(pts + [pts[0]], periodic=False)]))
    part = bd.extrude(face, amount=thickness, dir=(0, 0, 1)) - _cyl(bore / 2, thickness + 2, -1)
    return part.moved(bd.Location((0, 0, z0)))


def cam_pressure_angle(profile: Callable[[float], float], samples: int = 3600) -> float:
    """Largest pressure angle (degrees) of a radial cam with a radial knife/roller follower."""
    th = np.linspace(0, 2 * math.pi, samples, endpoint=False)
    r = np.array([profile(t) for t in th])
    dr = np.gradient(r, th)
    return float(np.degrees(np.max(np.abs(np.arctan2(dr, r)))))
