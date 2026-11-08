"""Straight bevel gears (Tredgold's approximation), for printed right-angle drives.

Added for M7 (docs/m7-design.md): a 1:1 pair turns M2's horizontal weekday arbor W up into the
carousel's vertical lay shaft. Like ``gears.py`` the module is a parameter and the backlash is a
parameter (the total gap of a mesh, split between the mates, D4).

Construction (Tredgold [S: e.g. Shigley, *Mechanical Engineering Design*, §13-6, "the back cone";
the standard textbook method]):
- A bevel gear of ``teeth`` z and pitch-cone angle δ has, at its large end, the tooth profile of a
  spur gear of the same module with z_v = z / cos δ teeth (the *virtual* gear on the back cone).
- The profile is laid on the large end: a point at radius r_v on the virtual gear sits at
  r = r_p + (r_v − r_pv) cos δ on the real gear, and its arc distance from the tooth centre is kept.
- Every point of the large-end section is joined by a straight line to the cone's apex. The small end
  is the same section scaled towards the apex by (R − b) / R, where R is the cone distance and b the
  face width. A ruled loft between the two sections gives the teeth.

The sections are taken in planes perpendicular to the axis (not on the back cone itself), which keeps
the loft between two planar faces. At the slow speeds of the clock (one turn a week) the small error
in the profile is harmless; the mesh test in ``cad/tests/test_bevel.py`` checks the pair turns without
interference and is engaged.

Frame: the gear's axis is +Z. Its large end (back) is the plane z = 0; the teeth point towards +Z and
the cone's apex is on the axis at z = ``apex_z``.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, replace

import numpy as np

from .gears import DEFAULT_BACKLASH, DEFAULT_MODULE, Gear


@dataclass(frozen=True)
class Bevel:
    teeth: int
    mate_teeth: int
    module: float = DEFAULT_MODULE
    face_width: float = 4.0
    shaft_angle: float = 90.0          # degrees between the two axes
    pressure_angle: float = 20.0
    backlash: float = DEFAULT_BACKLASH
    clearance: float = 0.25

    # --- cone geometry ---------------------------------------------------------------------------
    @property
    def pitch_angle(self) -> float:
        """Pitch-cone half angle δ (degrees)."""
        s = math.radians(self.shaft_angle)
        return math.degrees(math.atan2(math.sin(s), self.mate_teeth / self.teeth + math.cos(s)))

    @property
    def pitch_radius(self) -> float:
        return self.module * self.teeth / 2

    @property
    def cone_distance(self) -> float:
        return self.pitch_radius / math.sin(math.radians(self.pitch_angle))

    @property
    def apex_z(self) -> float:
        """Distance from the large-end plane to the apex, along the axis."""
        return self.pitch_radius / math.tan(math.radians(self.pitch_angle))

    @property
    def scale_small(self) -> float:
        return (self.cone_distance - self.face_width) / self.cone_distance

    @property
    def virtual(self) -> Gear:
        zv = max(int(round(self.teeth / math.cos(math.radians(self.pitch_angle)))), 4)
        return Gear(zv, self.module, self.pressure_angle, backlash=self.backlash, clearance=self.clearance)

    @property
    def tip_radius(self) -> float:
        return self.pitch_radius + self.module * math.cos(math.radians(self.pitch_angle))

    @property
    def root_radius(self) -> float:
        return self.pitch_radius - self.module * (1 + self.clearance) * math.cos(math.radians(self.pitch_angle))

    @property
    def ratio(self) -> float:
        """Turns of the mate per turn of this gear."""
        return self.teeth / self.mate_teeth

    def mate(self) -> "Bevel":
        return replace(self, teeth=self.mate_teeth, mate_teeth=self.teeth)

    # --- section ---------------------------------------------------------------------------------
    def section(self, flank_points: int = 8) -> np.ndarray:
        """Closed (x, y) outline of the large-end section, tooth 0 centred on +X."""
        v = self.virtual
        rs, half = v.tooth_flank(flank_points)           # radii and half angles on the virtual gear
        rpv, rp = v.pitch_radius, self.pitch_radius
        cd = math.cos(math.radians(self.pitch_angle))
        r_real = rp + (rs - rpv) * cd
        half_real = rs * half / r_real                   # keep the arc half-thickness at each point
        pa = 2 * math.pi / self.teeth
        root = self.root_radius
        pts = []
        for k in range(self.teeth):
            c = k * pa
            rise = [(r, c - h) for r, h in zip(r_real, half_real)]
            fall = [(r, c + h) for r, h in zip(r_real[::-1], half_real[::-1])]
            pts += rise + fall
            # root land to the next tooth: a few points on the root circle
            a0, a1 = c + half_real[0], c + pa - half_real[0]
            for t in np.linspace(a0, a1, 4)[1:-1]:
                pts.append((root, t))
        return np.array([(r * math.cos(a), r * math.sin(a)) for r, a in pts])


def bevel_gear(b: Bevel, bore: float | None = None, hub_len: float = 0.0, hub_od: float | None = None,
               fit_allowance: float = 0.0):
    """Solid straight bevel gear: large end on z = 0, teeth towards +Z, optional hub behind (−Z)."""
    import build123d as bd
    sec = b.section()
    k = b.scale_small
    dz = b.apex_z * (1 - k)
    f0 = bd.Face(bd.Wire.make_polygon([bd.Vector(float(x), float(y), 0.0) for x, y in sec], close=True))
    f1 = bd.Face(bd.Wire.make_polygon([bd.Vector(float(x * k), float(y * k), dz) for x, y in sec], close=True))
    part = bd.loft([f0, f1], ruled=True)
    if hub_len > 0:
        hub_od = hub_od or max((bore or 0) + 6, b.root_radius * 1.2)
        part = part + bd.Cylinder(hub_od / 2, hub_len, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
    if bore:
        part -= bd.Cylinder((bore + fit_allowance) / 2, 4 * (hub_len + dz + 10),
                            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))
    return part


def mesh_phase(b: Bevel) -> float:
    """Rotation (degrees) of the mate about its own axis that puts a tooth space where this gear's
    tooth 0 is, for a pair placed by ``place_pair``. Half a pitch of the mate, as for spur gears."""
    return 180.0 / b.mate_teeth
