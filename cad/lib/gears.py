"""Involute spur gears, internal gears and racks for printed clockwork (decision D4).

Conventions
-----------
- Units: millimetres and degrees at the interface; radians inside.
- Involute, 20° pressure angle by default, ISO 53 basic rack: addendum 1.0 m, dedendum
  (1 + clearance) m with clearance 0.25.
- **Backlash** is the total circumferential gap of a mesh, measured on the pitch circle (D4: default
  0.15 mm). It is applied as tooth thinning, split equally: each gear's tooth is thinner by
  backlash / 2. Two gears built with the same ``backlash`` value therefore mesh with exactly that
  gap at the standard centre distance.
- **Profile shift** ``x`` (in modules) moves the generating rack outward. ``auto_shift(z)`` gives the
  smallest shift that avoids undercut, the same rule as BOSL2: x = 1 - z / (2 / sin²α), for
  z <= 17. ``pair_shifts`` gives the wheel the opposite shift where it can take it, so the centre
  distance stays standard (the Phase 1 trains assume standard centre distances).
- A tooth's centre line lies on the +X axis for tooth 0.

The outline includes the trochoid that the generating rack's tip corner cuts (undercut), as BOSL2
does, so unshifted small pinions come out with their real, weakened root.

Validated against BOSL2 ``spur_gear2d`` in ``cad/tests/test_gears_bosl2.py`` (area and symmetric
difference of the 2-D outlines).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, replace

import numpy as np

DEFAULT_BACKLASH = 0.15   # mm, D4 parameter
DEFAULT_MODULE = 1.0      # mm, D4 parameter (0.8 with the 0.2 mm nozzle)


def _inv(a: float | np.ndarray):
    """Involute function tan(a) - a (radians)."""
    return np.tan(a) - a


def min_teeth_without_undercut(pressure_angle: float = 20.0) -> float:
    return 2.0 / math.sin(math.radians(pressure_angle)) ** 2


def auto_shift(teeth: int, pressure_angle: float = 20.0) -> float:
    """Smallest profile shift that avoids undercut (0 for z above the limit). Same rule as BOSL2."""
    mt = min_teeth_without_undercut(pressure_angle)
    return 0.0 if teeth > math.floor(mt) else 1.0 - teeth / mt


def pair_shifts(z1: int, z2: int, pressure_angle: float = 20.0) -> tuple[float, float]:
    """Shifts for a pair, keeping the standard centre distance when possible.

    The smaller gear gets ``auto_shift``. The larger takes the opposite shift if it then still
    avoids undercut (z_large >= z_min * (1 + x)); otherwise it gets its own ``auto_shift`` and the
    centre distance must come from ``centre_distance``.
    """
    small, large = (z1, z2) if z1 <= z2 else (z2, z1)
    xs = auto_shift(small, pressure_angle)
    mt = min_teeth_without_undercut(pressure_angle)
    xl = -xs if large >= mt * (1 + xs) else auto_shift(large, pressure_angle)
    return (xs, xl) if z1 <= z2 else (xl, xs)


@dataclass(frozen=True)
class Gear:
    """One gear's tooth geometry (no hub, bore or face width: see ``spur_gear``)."""
    teeth: int
    module: float = DEFAULT_MODULE
    pressure_angle: float = 20.0
    shift: float = 0.0
    backlash: float = DEFAULT_BACKLASH
    clearance: float = 0.25
    internal: bool = False

    def __post_init__(self):
        if self.teeth < 4:
            raise ValueError("a gear needs at least 4 teeth")
        if self.internal and self.shift:
            raise ValueError("profile shift on internal gears is not supported")

    # --- radii -------------------------------------------------------------------------------
    @property
    def alpha(self) -> float:
        return math.radians(self.pressure_angle)

    @property
    def pitch_radius(self) -> float:
        return self.module * self.teeth / 2.0

    @property
    def base_radius(self) -> float:
        return self.pitch_radius * math.cos(self.alpha)

    @property
    def tip_radius(self) -> float:
        m, x = self.module, self.shift
        return self.pitch_radius - m if self.internal else self.pitch_radius + m * (1 + x)

    @property
    def root_radius(self) -> float:
        m, x, c = self.module, self.shift, self.clearance
        return self.pitch_radius + m * (1 + c) if self.internal else self.pitch_radius - m * (1 + c - x)

    @property
    def tooth_thickness(self) -> float:
        """Arc thickness of a tooth on the pitch circle, after thinning by backlash / 2."""
        m = self.module
        return m * (math.pi / 2 + 2 * self.shift * math.tan(self.alpha)) - self.backlash / 2

    @property
    def outer_diameter(self) -> float:
        """Envelope diameter: tip circle for an external gear (an internal gear needs a rim)."""
        return 2 * self.tip_radius

    def with_(self, **kw) -> "Gear":
        return replace(self, **kw)

    # --- outline -----------------------------------------------------------------------------
    def _half_angle(self, r: np.ndarray, s: float, undercut: bool) -> np.ndarray:
        """Half angular thickness of a tooth of pitch thickness s at radius r (external form)."""
        rp, rb, a = self.pitch_radius, self.base_radius, self.alpha
        ar = np.arccos(np.clip(rb / np.maximum(r, rb), -1, 1))
        psi = s / (2 * rp) + _inv(a) - _inv(ar)
        if not undercut:
            return psi
        # trochoid of the generating rack's tip corner (rack addendum = 1 m, as BOSL2). Only the
        # branch that leaves the corner's innermost point towards the tooth cuts this flank.
        m, x = self.module, self.shift
        yt = rp - m * (1 - x)                         # rack tip line
        w = s / 2 + (rp - yt) * math.tan(a)          # rack space half-width at the tip line
        best = None
        for sign in (1.0, -1.0):
            phi = sign * np.linspace(0.0, math.pi / 2, 1201)
            cx, cy = w - rp * phi, np.full_like(phi, yt)
            X = cx * np.cos(phi) + cy * np.sin(phi)  # rotate by -phi into the gear frame
            Y = -cx * np.sin(phi) + cy * np.cos(phi)
            rr, beta = np.hypot(X, Y), np.arctan2(X, Y)   # beta from the tooth centre line
            if beta[1] < beta[0]:
                best = (rr, beta)
        rr, beta = best
        keep = np.r_[True, np.diff(rr) > 0]          # monotonic outward part of the branch
        keep &= np.cumprod(keep).astype(bool)
        rr, beta = rr[keep], beta[keep]
        out = psi.copy()
        inside = (r >= rr[0]) & (r <= rr[-1])
        out[inside] = np.minimum(psi[inside], np.interp(r[inside], rr, beta))
        return out

    def tooth_flank(self, flank_points: int = 14) -> tuple[np.ndarray, np.ndarray]:
        """(radii, half angular thickness) of one tooth, from the root circle to the tip.

        For an internal gear the "tooth" is the tooth *space* of the ring (the cutter's tooth).
        """
        m = self.module
        if self.internal:
            s = math.pi * m - self.tooth_thickness            # space width = p - ring tooth
            r_lo, r_hi, undercut = self.pitch_radius - m, self.root_radius, False
        else:
            s = self.tooth_thickness
            r_lo, r_hi, undercut = self.root_radius, self.tip_radius, True
        rs = np.linspace(r_lo, r_hi, flank_points * 2 + 1)
        half = self._half_angle(rs, s, undercut)
        ok = half > 1e-4                                      # pointed tips: stop where flanks meet
        rs, half = rs[ok], half[ok]
        half = np.minimum(half, math.pi / self.teeth - 1e-6)  # never wider than one pitch
        return rs, half

    def outline(self, flank_points: int = 14, arc_points: int = 4) -> np.ndarray:
        """Closed 2-D outline, counter-clockwise, as an (N, 2) array.

        For an internal gear this is the outline of the tooth *spaces* seen from inside, i.e. the
        boundary of the hole cut in the rim (see ``internal_gear``).
        """
        rs, half = self.tooth_flank(flank_points)
        pitch_ang = 2 * math.pi / self.teeth
        pts = []
        for k in range(self.teeth):
            c = k * pitch_ang
            # rising flank (smaller angle side), tip arc, falling flank, root arc to next tooth
            for r, h in zip(rs, half):
                pts.append((r, c - h))
            ta = np.linspace(c - half[-1], c + half[-1], arc_points + 2)[1:-1]
            pts += [(rs[-1], a) for a in ta]
            for r, h in zip(rs[::-1], half[::-1]):
                pts.append((r, c + h))
            ra = np.linspace(c + half[0], c + pitch_ang - half[0], arc_points + 2)[1:-1]
            pts += [(rs[0], a) for a in ra]
        P = np.array(pts)
        return np.column_stack([P[:, 0] * np.cos(P[:, 1]), P[:, 0] * np.sin(P[:, 1])])


def centre_distance(g1: Gear, g2: Gear) -> float:
    """Operating centre distance (mm) of an external pair, or of a pinion inside a ring."""
    if g1.module != g2.module or g1.pressure_angle != g2.pressure_angle:
        raise ValueError("gears must share module and pressure angle")
    m, a = g1.module, g1.alpha
    if g1.internal or g2.internal:
        ring, pin = (g1, g2) if g1.internal else (g2, g1)
        return m * (ring.teeth - pin.teeth) / 2
    zs, xs = g1.teeth + g2.teeth, g1.shift + g2.shift
    if abs(xs) < 1e-12:
        return m * zs / 2
    target = float(_inv(a)) + 2 * math.tan(a) * xs / zs
    aw = a
    for _ in range(50):                                  # Newton on inv(aw) = target
        aw -= (float(_inv(aw)) - target) / (math.tan(aw) ** 2)
    return m * zs / 2 * math.cos(a) / math.cos(aw)


def mesh_phase(driver: Gear, driven: Gear) -> float:
    """Rotation (degrees) to give ``driven`` so that it meshes with ``driver`` (tooth 0 of the
    driver on +X, driven placed on the +X side for external pairs, inside for a ring)."""
    if driven.internal or driver.internal:
        return 0.0          # the ring has a tooth space on +X, the pinion a tooth on +X
    return 180.0 + 180.0 / driven.teeth


def mesh_rotation(driver: Gear, driven: Gear, theta: float, driver_rot: float = 0.0) -> float:
    """Rotation (degrees) for ``driven`` placed at polar angle ``theta`` (degrees) from ``driver``'s
    centre, when the driver is rotated by ``driver_rot`` degrees (tooth 0 on +X at rotation 0).

    External pairs only. Generalises ``mesh_phase`` (which is the case theta = 0, driver_rot = 0).
    """
    if driver.internal or driven.internal:
        raise ValueError("mesh_rotation handles external pairs")
    pitch1 = 360.0 / driver.teeth
    delta = ((driver_rot - theta + pitch1 / 2) % pitch1) - pitch1 / 2   # driver offset from tooth-on-line
    return theta + 180.0 + 180.0 / driven.teeth - delta * driver.teeth / driven.teeth


# --- solids (build123d) ---------------------------------------------------------------------------

def _face_from_points(points: np.ndarray):
    import build123d as bd
    wire = bd.Wire.make_polygon([bd.Vector(float(x), float(y), 0) for x, y in points], close=True)
    return bd.Face(wire)


def gear_face(g: Gear, flank_points: int = 10):
    """Flat face of an external gear (or of the space cutter of an internal gear).

    Each flank is one B-spline through the computed points and the tip and root are circular
    arcs: four edges per tooth, which keeps booleans fast on 100+ tooth wheels.
    """
    import build123d as bd
    rs, half = g.tooth_flank(flank_points)
    pa = 2 * math.pi / g.teeth

    def P(r, a):
        return bd.Vector(float(r * math.cos(a)), float(r * math.sin(a)), 0.0)

    edges = []
    for k in range(g.teeth):
        c = k * pa
        rise = [P(r, c - h) for r, h in zip(rs, half)]
        fall = [P(r, c + h) for r, h in zip(rs[::-1], half[::-1])]
        edges.append(bd.Edge.make_spline(rise))
        if half[-1] > 1e-5:
            edges.append(bd.Edge.make_three_point_arc(rise[-1], P(rs[-1], c), fall[0]))
        edges.append(bd.Edge.make_spline(fall))
        if pa - 2 * half[0] > 1e-5:
            edges.append(bd.Edge.make_three_point_arc(fall[-1], P(rs[0], c + pa / 2),
                                                      P(rs[0], c + pa - half[0])))
    return bd.Face(bd.Wire(edges))


def spur_gear(g: Gear, face_width: float, bore: float | None = None, **kw):
    """Extruded external spur gear along +Z from z = 0, with an optional plain bore."""
    import build123d as bd
    if g.internal:
        raise ValueError("use internal_gear for internal gears")
    part = bd.extrude(gear_face(g, **kw), amount=face_width, dir=(0, 0, 1))
    if bore:
        part -= bd.Cylinder(bore / 2, face_width * 3, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))
    return part


def internal_gear(g: Gear, face_width: float, rim: float = 3.0, **kw):
    """Ring gear: a disc of radius root + rim with the tooth spaces cut out."""
    import build123d as bd
    if not g.internal:
        g = g.with_(internal=True)
    outer = bd.Cylinder(g.root_radius + rim, face_width, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    cutter = bd.extrude(gear_face(g, **kw), amount=face_width * 3, dir=(0, 0, 1)).moved(bd.Location((0, 0, -face_width)))
    return outer - cutter


def rack_outline(module: float, teeth: int, pressure_angle: float = 20.0,
                 backlash: float = DEFAULT_BACKLASH, clearance: float = 0.25,
                 back: float = 3.0) -> np.ndarray:
    """Closed outline of a straight rack, pitch line on y = 0, teeth pointing +Y, starting at x = 0."""
    m, a = module, math.radians(pressure_angle)
    p = math.pi * m
    s = p / 2 - backlash / 2                       # tooth thickness on the pitch line
    ha, hf = m, m * (1 + clearance)
    pts = [(0.0, -hf - back)]
    for k in range(teeth):
        c = (k + 0.5) * p
        pts += [(c - s / 2 - hf * math.tan(a), -hf), (c - s / 2 + ha * math.tan(a), ha),
                (c + s / 2 - ha * math.tan(a), ha), (c + s / 2 + hf * math.tan(a), -hf)]
    pts += [(teeth * p, -hf), (teeth * p, -hf - back)]
    pts.insert(1, (0.0, -hf))
    return np.array(pts)


def rack(module: float, teeth: int, face_width: float, **kw):
    import build123d as bd
    return bd.extrude(_face_from_points(rack_outline(module, teeth, **kw)), amount=face_width, dir=(0, 0, 1))
