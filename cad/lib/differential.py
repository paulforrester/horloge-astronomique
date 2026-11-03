"""Spur-gear differential with meshing planet pairs (all spur gears, all from ``gears.py``).

Two equal sun gears A and B on one axis. Each planet pair is P1 (meshes sun A) and P2 (meshes sun
B); P1 and P2 mesh with each other in a middle level where neither sun reaches. The carrier holds
the planet pins. With equal suns:

    omega_B = 2 * omega_carrier - omega_A

so with the carrier still (v1), B turns at A's rate in the opposite sense, and turning the carrier
by phi moves B by 2 * phi. In M2 the carrier's rim is a worm wheel (``worm.py``): the correction
input of architecture §13. A self-locking worm holds it still in v1.

Levels along +Z from ``z0``:
    carrier plate 1 | level 1: sun A + P1 | level 2: P1 + P2 | level 3: P2 + sun B | carrier plate 2
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from .gears import Gear, centre_distance, mesh_rotation, spur_gear


@dataclass
class SpurDifferential:
    sun_teeth: int = 20
    planet_teeth: int = 18
    module: float = 1.0
    face: float = 4.0
    pairs: int = 2
    gap: float = 0.4               # axial running gap between levels and plates
    plate: float = 3.0             # carrier plate thickness (plate 2 may be the worm wheel)
    backlash: float = 0.15

    def __post_init__(self):
        self.sun = Gear(self.sun_teeth, self.module, backlash=self.backlash)
        self.planet = Gear(self.planet_teeth, self.module, backlash=self.backlash)
        if self.sun_teeth < 18 or self.planet_teeth < 18:
            raise ValueError("use >= 18 teeth so no profile shift is needed (standard centre distances)")

    # --- geometry -------------------------------------------------------------------------------
    @property
    def planet_radius(self) -> float:
        return centre_distance(self.sun, self.planet)

    @property
    def pair_angle(self) -> float:
        """Angle (degrees) between P1 and P2 of one pair, seen from the axis."""
        cd = centre_distance(self.planet, self.planet)
        return math.degrees(2 * math.asin(cd / 2 / self.planet_radius))

    @property
    def outer_radius(self) -> float:
        return self.planet_radius + self.planet.tip_radius

    def levels(self, z0: float = 0.0) -> dict:
        p, f, g = self.plate, self.face, self.gap
        z = z0
        out = {"plate1": (z, z + p)}
        z += p + g
        for k in (1, 2, 3):
            out[f"level{k}"] = (z, z + f)
            z += f + g
        out["plate2"] = (z, z + p)
        out["total"] = (z0, z + p)
        return out

    def planet_positions(self) -> list[tuple]:
        """[(x1, y1, rot1), (x2, y2, rot2)] per pair; rotations make every mesh conjugate."""
        a, half = self.planet_radius, self.pair_angle / 2
        out = []
        for k in range(self.pairs):
            c = 360.0 * k / self.pairs
            t1, t2 = math.radians(c - half), math.radians(c + half)
            p1 = (a * math.cos(t1), a * math.sin(t1))
            p2 = (a * math.cos(t2), a * math.sin(t2))
            r1 = mesh_rotation(self.sun, self.planet, math.degrees(t1), 0.0)
            ang12 = math.degrees(math.atan2(p2[1] - p1[1], p2[0] - p1[0]))
            # P2 relative to P1: express P1's rotation in a frame centred on P1
            r2 = mesh_rotation(self.planet, self.planet, ang12, r1)
            out.append(((p1[0], p1[1], r1), (p2[0], p2[1], r2)))
        return out

    def sun_b_rotation(self) -> float:
        """Rotation of sun B that meshes with the first pair's P2."""
        (_, (x2, y2, r2)) = self.planet_positions()[0]
        ang = math.degrees(math.atan2(-y2, -x2))          # from P2 towards the axis
        return mesh_rotation(self.planet, self.sun, ang, r2) - 0.0

    @staticmethod
    def output(omega_a: float, omega_carrier: float) -> float:
        return 2 * omega_carrier - omega_a

    # --- solids -----------------------------------------------------------------------------------
    def parts(self, z0: float = 0.0, sun_bore: float = 5.0, pin: float = 3.0) -> dict:
        """Named solids, positioned about the Z axis. Suns and planets only; the caller adds the
        carrier plates (one may be a worm wheel) and the pins."""
        import build123d as bd
        from . import parts as P
        lv = self.levels(z0)
        out = {}
        out["sun_A"] = spur_gear(self.sun, self.face, bore=sun_bore).moved(bd.Location((0, 0, lv["level1"][0])))
        out["sun_B"] = spur_gear(self.sun, self.face, bore=sun_bore).rotate(bd.Axis.Z, self.sun_b_rotation()).moved(
            bd.Location((0, 0, lv["level3"][0])))
        h = lv["level2"][1] - lv["level1"][0]
        for k, ((x1, y1, r1), (x2, y2, r2)) in enumerate(self.planet_positions()):
            b = pin + P.FITS.running
            out[f"planet_{k}_1"] = (spur_gear(self.planet, h) - P.disc(b, h + 2, z0=-1)).rotate(bd.Axis.Z, r1).moved(
                bd.Location((x1, y1, lv["level1"][0])))
            out[f"planet_{k}_2"] = (spur_gear(self.planet, h) - P.disc(b, h + 2, z0=-1)).rotate(bd.Axis.Z, r2).moved(
                bd.Location((x2, y2, lv["level2"][0])))
        return out

    def pin_positions(self) -> list[tuple]:
        return [(x, y) for pair in self.planet_positions() for (x, y, _) in pair]
