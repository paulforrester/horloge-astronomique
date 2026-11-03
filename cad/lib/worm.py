"""Single-start (or multi-start) worm and a matching helical worm wheel, for printing.

Used for the M2 differential carriers (Paul, 3 Nov 2026: "Worm 60:1"): the worm turns the carrier
by one tooth per turn, and a single-start worm with a small lead angle is self-locking, so in v1 it
holds the carrier still with no separate key.

Geometry (ISO-style, axial module m):
- axial pitch p = pi * m, lead L = starts * p, pitch diameter d1 (chosen), lead angle
  gamma = atan(L / (pi * d1));
- thread in the axial section: straight-sided, 20° flank angle, addendum 1.0 m, dedendum
  (1 + clearance) m, thickness on the pitch line p/2 - backlash/2;
- the wheel is an involute gear of module m twisted to a helix angle equal to the lead angle, with
  a throat cut by the worm's tip torus. Strictly its transverse module is m / cos(gamma); for the
  small lead angles used here (< 6°) that is a 0.4 % difference, absorbed by the backlash.

Self-locking needs tan(gamma) < mu. With PLA on PLA, mu is about 0.2–0.35 [E], and the default
d1 = 12 mm at m = 1 gives gamma = 4.76°, tan = 0.083.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .gears import DEFAULT_BACKLASH, Gear, gear_face


@dataclass(frozen=True)
class Worm:
    module: float = 1.0
    pitch_diameter: float = 12.0
    starts: int = 1
    pressure_angle: float = 20.0
    backlash: float = DEFAULT_BACKLASH
    clearance: float = 0.25

    @property
    def axial_pitch(self) -> float:
        return math.pi * self.module

    @property
    def lead(self) -> float:
        return self.starts * self.axial_pitch

    @property
    def lead_angle(self) -> float:
        """Degrees."""
        return math.degrees(math.atan(self.lead / (math.pi * self.pitch_diameter)))

    @property
    def tip_radius(self) -> float:
        return self.pitch_diameter / 2 + self.module

    @property
    def root_radius(self) -> float:
        return self.pitch_diameter / 2 - self.module * (1 + self.clearance)

    def self_locking(self, mu: float = 0.2) -> bool:
        return math.tan(math.radians(self.lead_angle)) < mu

    def section(self, samples: int = 96) -> np.ndarray:
        """Transverse section at z = 0 as an (N, 2) outline: radius as a function of angle."""
        a = math.radians(self.pressure_angle)
        rp, ra, rf = self.pitch_diameter / 2, self.tip_radius, self.root_radius
        s = self.axial_pitch / 2 - self.backlash / 2
        th = np.linspace(0, 2 * math.pi, samples, endpoint=False)
        pts = []
        for t in th:
            # axial distance from the nearest thread centre line at this angle (right-hand thread)
            u = (-(self.lead * t / (2 * math.pi)) % self.axial_pitch)
            u = min(u, self.axial_pitch - u)
            r = rp + (s / 2 - u) / math.tan(a)
            r = min(max(r, rf), ra)
            pts.append((r * math.cos(t), r * math.sin(t)))
        return np.array(pts)


def worm_solid(w: Worm, length: float, bore: float = 5.0, sections_per_turn: int = 12):
    """Worm along +Z from z = 0 to ``length``, as a loft of rotated transverse sections."""
    import build123d as bd
    base = w.section()
    n = max(2, int(math.ceil(length / w.lead * sections_per_turn)) + 1)
    wires = []
    for k in range(n):
        z = length * k / (n - 1)
        rot = 2 * math.pi * z / w.lead            # the section turns with the helix
        c, s_ = math.cos(rot), math.sin(rot)
        pts = [bd.Vector(float(x * c - y * s_), float(x * s_ + y * c), z) for x, y in base]
        wires.append(bd.Wire([bd.Edge.make_spline(pts + [pts[0]], periodic=False)]))
    part = bd.Solid.make_loft(wires, ruled=False)
    if bore:
        part -= bd.Cylinder(bore / 2, length * 3, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))
    return part


def worm_wheel(teeth: int, w: Worm, face_width: float, bore: float | None = None):
    """Throated helical worm wheel along +Z from z = 0.

    An involute gear twisted to the worm's lead angle (a loft of rotated sections), with a throat:
    the torus swept by the worm's tip circle (plus clearance) is cut from the tips, so the wheel
    wraps the worm instead of touching it only at the mid-plane. Checked against the worm at six
    worm angles with zero interference at the default 0.15 mm backlash (cad/tests/test_worm_diff.py).
    """
    import build123d as bd
    g = Gear(teeth, w.module, backlash=w.backlash, pressure_angle=w.pressure_angle)
    twist = math.degrees(face_width * math.tan(math.radians(w.lead_angle)) / g.pitch_radius)
    base = gear_face(g)
    faces = [base.rotate(bd.Axis.Z, -twist / 2 + twist * k / 3).moved(bd.Location((0, 0, face_width * k / 3)))
             for k in range(4)]
    part = bd.loft(faces, ruled=True)
    a = worm_centre_distance(teeth, w)
    part = part - bd.Torus(a, w.tip_radius + w.clearance * w.module).moved(bd.Location((0, 0, face_width / 2)))
    if bore:
        part -= bd.Cylinder(bore / 2, face_width * 3, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))
    return part


def place_worm(worm_part, teeth: int, w: Worm, face_width: float, wheel_axis_xy=(0.0, 0.0), z0: float = 0.0,
               side_angle: float = 90.0, psi: float = 0.0):
    """Put a worm (built along +Z, centred on z = 0) tangent to a wheel whose axis is Z at
    ``wheel_axis_xy`` and whose face starts at ``z0``. ``side_angle`` (degrees) is where the worm
    sits around the wheel; the worm axis is perpendicular to that direction, in the XY plane.
    ``psi`` turns the worm about its own axis."""
    import build123d as bd
    a = worm_centre_distance(teeth, w)
    part = worm_part.rotate(bd.Axis.Z, psi).rotate(bd.Axis.Y, 90)          # worm axis along X
    part = part.moved(bd.Location((0, a, z0 + face_width / 2)))             # above the wheel (+Y)
    return part.rotate(bd.Axis.Z, side_angle - 90.0).moved(bd.Location((wheel_axis_xy[0], wheel_axis_xy[1], 0)))


def worm_centre_distance(teeth: int, w: Worm) -> float:
    return (w.pitch_diameter + teeth * w.module) / 2
