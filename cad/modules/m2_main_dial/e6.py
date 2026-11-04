"""M2 calendar: E6, the ring's nightly drive, and the stop lever that decides how many divisions.

Concept approved by Paul (4 Nov 2026; `docs/m2-design.md` §6). Two variants share one ring:

- **"star"** (built by default), the classic calendar finger and star. The gearmotor turns a finger
  once per division; the finger pushes a 12-point star one point. The star's shaft carries a
  12-tooth pinion that stays meshed with the ring's 368 gear teeth, so one point is 1/12 of a turn
  of the pinion, which is one tooth of the ring: one division. A jumper on the star holds it, and
  through the pinion the ring, between steps, and settles each step to exactly one point.
- **"pawl"** (Paul's fallback), a crank and pawl. The gearmotor turns a crank; the crank pushes a
  spring-loaded pawl along the ring's teeth by 1.25 pitches; a jumper on the ring settles the step.

Rejected on the way, by simulation (see the doc): a one-tooth pinion (it pushes the ring 2–3
divisions per turn) and a 12-slot Geneva (its wheel passes 0.65 mm from the motor shaft).

The ring's teeth are involute gear teeth for both variants (module 0.922, 368 teeth, tips at the
lip's old r 170.5). Everything that meshes with them stays in the lip's 2.5 mm depth, above the
setter's rocker, which passes under the lip once a year.

Station parts are built in the world frame (6 o'clock is -90°). The ring lip and the pointer side
are built in the calendar's canonical frame (pointer at 0°) and turned 180° by ``calendar.build``.
"""
from __future__ import annotations

import math

import build123d as bd

from cad.lib import gears as G
from cad.lib import parts
from cad.modules.m2_main_dial import calendar_logic as L

E6_DRIVE = "star"                  # "star" (built) or "pawl" (the fallback)
DIV = 360.0 / L.N

# --- the ring's gear teeth -----------------------------------------------------------------------
RING_TIP_R = 170.5                 # the lip's outer radius (calendar.LIP[1])
M_RING = 2 * RING_TIP_R / (L.N + 2)               # module, full-depth teeth: 0.9216
RING = G.Gear(L.N, M_RING, 20.0)
PINION = G.Gear(12, M_RING, 20.0)
LIP_Z = (-5.5, -3.0)               # the lip (calendar.LIP[2], FACE_Z[0])
MESH_Z = (-5.3, -3.1)              # everything that meshes with the teeth stays in the lip's depth: the
                                   # setter's rocker passes under the lip once a year (bars to -5.6)


def ring_lip(pointer: int, lip_r_in: float):
    """The lip with its 368 gear teeth (canonical frame), tooth k centred on division k (spline
    flanks: 4 edges a tooth, which keeps the booleans fast)."""
    toothed = bd.extrude(G.gear_face(RING), amount=LIP_Z[1] - LIP_Z[0], dir=(0, 0, 1)).moved(bd.Location((0, 0, LIP_Z[0])))
    toothed = toothed.rotate(bd.Axis.Z, -pointer * DIV)
    return toothed - bd.Cylinder(lip_r_in, 20, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))


# --- variant "star": placement ---------------------------------------------------------------------
STATION = -90.0
PSI_E = STATION - 10.0             # E6 sits 10° before the station, beside the roller at 6 o'clock
A_PINION = G.centre_distance(RING, PINION)        # 175.11: ring centre to the star's shaft
FINGER_A = 13.0                    # star shaft to the finger (motor) axis, radially outward
STAR_N, STAR_TIP, STAR_ROOT, STAR_FLAT = 12, 10.0, 7.4, 0.5
FINGER_TIP, FINGER_W, FINGER_HUB = 5.0, 1.4, 2.5
STAR_Z = (-15.0, -12.0)            # the star and finger plane, behind the carrier (back at -10.9)
PINION_Z = MESH_Z
PLATE_Z = (-21.2, -19.2)           # bracket plate on the gearmotor's face
GEARBOX_FACE = PLATE_Z[0]
CARRIER_BACK = -10.9
JUMPER_ARM, JUMPER_AT = 9.0, 90.0  # star jumper: nose to pivot (mm); its gap, degrees from the finger side


def _u(deg):
    return math.cos(math.radians(deg)), math.sin(math.radians(deg))


def star_xy():
    ux, uy = _u(PSI_E)
    return A_PINION * ux, A_PINION * uy


def finger_xy():
    ux, uy = _u(PSI_E)
    return (A_PINION + FINGER_A) * ux, (A_PINION + FINGER_A) * uy


def pinion_rotation(pointer: int) -> float:
    """World rotation (degrees) of the pinion meshing with the ring at rest (ring tooth 0 at
    world 180 - pointer * DIV, the ring turned 180° from its canonical frame)."""
    return G.mesh_rotation(RING, PINION, PSI_E, 180.0 - pointer * DIV)


def star_rotation(pointer: int) -> float:
    """The star turns with the pinion; at rest one of its gaps faces the finger (direction PSI_E)."""
    off = (PSI_E - 180.0 / STAR_N) - pinion_rotation(0)
    return pinion_rotation(pointer) + off


def star_outline(rot: float, centre=(0.0, 0.0)):
    """12 V-teeth (tips flattened), tip k at angle rot + 30 k about centre."""
    pts = []
    for k in range(STAR_N):
        c = math.radians(rot + 360.0 * k / STAR_N)
        ht = math.asin(STAR_FLAT / 2 / STAR_TIP)
        pts += [(STAR_TIP * math.cos(c - ht), STAR_TIP * math.sin(c - ht)),
                (STAR_TIP * math.cos(c + ht), STAR_TIP * math.sin(c + ht))]
        cr = c + math.pi / STAR_N
        pts.append((STAR_ROOT * math.cos(cr), STAR_ROOT * math.sin(cr)))
    return [(centre[0] + x, centre[1] + y) for x, y in pts]


def finger_outline(rot: float, centre=(0.0, 0.0)):
    """Hub and one finger pointing at angle rot."""
    from shapely.geometry import Polygon, Point
    from shapely import affinity
    w = FINGER_W
    f = Polygon([(0, -w / 2), (FINGER_TIP - w / 2, -w / 2), (FINGER_TIP - w / 2, w / 2), (0, w / 2)]).union(
        Point(FINGER_TIP - w / 2, 0).buffer(w / 2, 24)).union(Point(0, 0).buffer(FINGER_HUB, 48))
    f = affinity.translate(affinity.rotate(f, rot, origin=(0, 0)), *centre)
    return f


def finger_push(depth_error: float = 0.0, phase_error: float = 0.0, dth: float = 0.5):
    """One finger turn against the star, in the star's own frame (star at the origin, finger axis on
    +X, a star gap facing it): the star is pushed round only as far as the finger forces it.
    Returns (star advance in points, jammed). The jumper then settles the star to a whole point."""
    from shapely.geometry import Polygon
    from shapely import affinity
    pitch = 360.0 / STAR_N
    star = Polygon(star_outline(-180.0 / STAR_N))
    a = FINGER_A - depth_error
    phi = phase_error * pitch
    for th in [360.0 - dth * k for k in range(int(360 / dth))]:          # the finger turns clockwise
        F = finger_outline(th, (a, 0.0))
        if F.intersection(affinity.rotate(star, phi, origin=(0, 0))).area > 1e-6:
            step, d = pitch / 400, pitch / 400
            while d < 0.6 * pitch and F.intersection(affinity.rotate(star, phi + d, origin=(0, 0))).area > 1e-6:
                d += step
            if d >= 0.6 * pitch:
                return (phi - phase_error * pitch) / pitch, True
            phi += d
    return (phi - phase_error * pitch) / pitch, False


def finger_dwell() -> float:
    """Degrees of the finger's turn during which it is clear of the star's tip circle: the window in
    which the motor may stop (home) and coast."""
    # finger tip circle (radius FINGER_TIP) about the finger axis crosses the star tip circle
    a, rf, rs = FINGER_A, FINGER_TIP, STAR_TIP
    x = (rf * rf - rs * rs + a * a) / (2 * a)            # from the finger axis towards the star
    half = math.degrees(math.acos(max(-1.0, min(1.0, x / rf))))
    return 360.0 - 2 * half


# --- variant "star": parts ------------------------------------------------------------------------
STUD_D = 3.0
HEX_AF = 5.0                       # the star's tube ends in a hex; the pinion is pressed on it
TUBE_R = 3.0
JUMPER_NOSE_R = 1.0
JUMPER_WIRE_D, JUMPER_WIRE_L, JUMPER_WIRE_AT = 0.5, 17.5, 0.6     # wire Ø, free length, contact (x arm from the pivot)
JUMPER_F_NOSE = 0.30              # N at the nose, at rest [E]: holds the star 7x, settles it 2x
MAGNET = (5.0, 2.0)                # Ø x thickness, as the other Hall sensors (BOM)
MAGNET_R = 4.8                     # on the finger's flange
FLANGE_R, FLANGE_Z = 7.5, (-19.0, -16.4)
STANDOFF_D = 6.0


def _prism(points, z0, z1):
    face = bd.Face(bd.Wire.make_polygon([bd.Vector(x, y, z0) for x, y in points], close=True))
    return bd.extrude(face, amount=z1 - z0, dir=(0, 0, 1))


def _poly_prism(poly, z0, z1, xform=None):
    """Prism of a shapely polygon, holes included; xform maps each (x, y) (e.g. local -> world)."""
    f = xform or (lambda q: q)
    wire = lambda ring: bd.Wire.make_polygon([bd.Vector(*f(q), z0) for q in list(ring.coords)[:-1]], close=True)
    face = bd.Face(wire(poly.exterior), [wire(r) for r in poly.interiors])
    return bd.extrude(face, amount=z1 - z0, dir=(0, 0, 1))


def wire_tilt(contact, pivot, direction, outward, clearance):
    """Smallest outward tilt (radians) of a wire leaving `contact` along `direction` so that its
    line passes `clearance` from `pivot` (a lever's pivot boss)."""
    for k in range(0, 600):
        t = math.radians(k * 0.1)
        u = (direction[0] * math.cos(t) + outward[0] * math.sin(t), direction[1] * math.cos(t) + outward[1] * math.sin(t))
        w = (pivot[0] - contact[0], pivot[1] - contact[1])
        along = w[0] * u[0] + w[1] * u[1]
        if math.hypot(w[0] - along * u[0], w[1] - along * u[1]) >= clearance:
            return t
    raise RuntimeError("no tilt clears the pivot")


def _at(c, r, deg):
    return c[0] + r * math.cos(math.radians(deg)), c[1] + r * math.sin(math.radians(deg))


def _bar(p, q, w):
    (x0, y0), (x1, y1) = p, q
    L_ = math.hypot(x1 - x0, y1 - y0)
    nx, ny = -(y1 - y0) / L_ * w / 2, (x1 - x0) / L_ * w / 2
    return [(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)]


def _circle(c, r, n=32):
    return [(c[0] + r * math.cos(2 * math.pi * k / n), c[1] + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def jumper_geometry():
    """The star jumper: nose seated in the gap at PSI_E + JUMPER_AT (from the star's centre), arm
    along the anticlockwise tangent to its pivot (the star turns anticlockwise, so the drag pulls
    the arm), wire contact on the arm's outer edge, wire anchored beyond the pivot."""
    S = star_xy()
    g = PSI_E + JUMPER_AT
    # nose centre on the gap's bisector, JUMPER_NOSE_R from both flanks
    half = math.pi / STAR_N
    tip = (STAR_TIP * math.cos(half), STAR_TIP * math.sin(half))          # gap on +X in the local frame
    root = (STAR_ROOT, 0.0)
    fx, fy = tip[0] - root[0], tip[1] - root[1]
    n = math.hypot(fx, fy)
    nx, ny = fy / n, -fx / n                                               # flank normal, towards the gap axis
    lo, hi = STAR_ROOT, STAR_TIP + 2
    for _ in range(60):                                                    # distance to the flank = nose radius
        mid = (lo + hi) / 2
        d = abs((mid - root[0]) * nx + (0 - root[1]) * ny)
        lo, hi = (mid, hi) if d < JUMPER_NOSE_R else (lo, mid)
    r_n = (lo + hi) / 2
    nose = _at(S, r_n, g)
    t = (-math.sin(math.radians(g)), math.cos(math.radians(g)))           # anticlockwise tangent
    o = (math.cos(math.radians(g)), math.sin(math.radians(g)))           # outward
    arm0 = (nose[0] + 1.2 * o[0], nose[1] + 1.2 * o[1])
    pivot = (arm0[0] + JUMPER_ARM * t[0], arm0[1] + JUMPER_ARM * t[1])
    c_at = (pivot[0] - JUMPER_WIRE_AT * JUMPER_ARM * t[0] + (0.7 + JUMPER_WIRE_D / 2) * o[0],
            pivot[1] - JUMPER_WIRE_AT * JUMPER_ARM * t[1] + (0.7 + JUMPER_WIRE_D / 2) * o[1])
    tilt = wire_tilt(c_at, pivot, t, o, 1.6 + JUMPER_WIRE_D / 2 + 0.15)    # outward, past the pivot's boss
    u = (t[0] * math.cos(tilt) + o[0] * math.sin(tilt), t[1] * math.cos(tilt) + o[1] * math.sin(tilt))
    anchor = (c_at[0] + JUMPER_WIRE_L * u[0], c_at[1] + JUMPER_WIRE_L * u[1])
    return {"nose": nose, "nose_r": r_n, "arm0": arm0, "pivot": pivot, "contact": c_at, "anchor": anchor,
            "lift": STAR_TIP - (r_n - JUMPER_NOSE_R)}


def jumper_outline():
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    g = jumper_geometry()
    body = unary_union([Polygon(_circle(g["nose"], JUMPER_NOSE_R, 24)), Polygon(_bar(g["nose"], g["arm0"], 1.6)),
                        Polygon(_bar(g["arm0"], g["pivot"], 1.4)), Polygon(_circle(g["pivot"], 1.6, 24))])
    return list(body.exterior.coords)[:-1]


def _wire(p0, p1, d, z, overrun=0.8):
    L_ = math.dist(p0, p1) + overrun
    ang = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
    return parts.rod(d, L_).rotate(bd.Axis.Y, 90).rotate(bd.Axis.Z, ang).moved(bd.Location((p0[0], p0[1], z)))


def standoff_xy():
    S, F = star_xy(), finger_xy()
    ux, uy = _u(PSI_E)
    tx, ty = -uy, ux
    return [(S[0] - 13.0 * ux, S[1] - 13.0 * uy), (F[0] + 11.0 * tx, F[1] + 11.0 * ty),
            (F[0] - 11.0 * tx, F[1] - 11.0 * ty)]


def hall_xy():
    """The home Hall sensor, under the finger flange's magnet when the finger points away from the
    star (home: the middle of the finger's dwell)."""
    F = finger_xy()
    return _at(F, MAGNET_R, PSI_E + 180.0)


def star_parts(pointer: int) -> list:
    """[(name, solid, add() kwargs)] of variant "star", world frame, at rest (finger at home)."""
    out = []
    S, F = star_xy(), finger_xy()
    ux, uy = _u(PSI_E)
    tx, ty = -uy, ux
    s_rot, p_rot = star_rotation(pointer), pinion_rotation(pointer)
    # star part: star, tube through the carrier, hex end for the pinion; it turns on a fixed stud
    star = _prism(star_outline(s_rot, S), *STAR_Z)
    star += parts.disc(2 * TUBE_R, PINION_Z[0] - STAR_Z[1] + 0.01, z0=STAR_Z[1] - 0.01).moved(bd.Location((S[0], S[1], 0)))
    hexp = [_at(S, HEX_AF / math.sqrt(3), s_rot + 30 + 60 * k) for k in range(6)]
    star += _prism(hexp, PINION_Z[0] - 0.01, PINION_Z[1])
    star -= parts.disc(STUD_D + 0.2, 40, z0=-30).moved(bd.Location((S[0], S[1], 0)))
    out.append(("e6_star", star, dict(material="PLA", group="station", nozzle=0.2, print_up=(0, 0, 1),
                                      note="12-point star with its tube; one finger turn = one point")))
    pin = G.spur_gear(PINION, PINION_Z[1] - PINION_Z[0]).rotate(bd.Axis.Z, p_rot).moved(bd.Location((S[0], S[1], PINION_Z[0])))
    hexb = [_at(S, (HEX_AF + 0.15) / math.sqrt(3), s_rot + 30 + 60 * k) for k in range(6)]
    pin -= _prism(hexb, PINION_Z[0] - 1, PINION_Z[1] + 1)
    out.append(("e6_pinion", pin, dict(material="PLA", group="station", nozzle=0.2,
                                       note="12 teeth, module 0.922, meshed with the ring; pressed on the star's hex, glued")))
    out.append(("e6_stud", parts.rod(STUD_D, PINION_Z[1] - 0.3 - PLATE_Z[0]).moved(bd.Location((S[0], S[1], PLATE_Z[0]))),
                dict(material="steel", printed=False, group="station", note="Ø3 stud pressed into the bracket")))
    # finger: flange (magnet pocket, open at the back), hub on the D-shaft, the finger
    f_rot = PSI_E                                                     # home: pointing away from the star
    fing = parts.disc(2 * FLANGE_R, FLANGE_Z[1] - FLANGE_Z[0], z0=FLANGE_Z[0]).moved(bd.Location((F[0], F[1], 0)))
    fing += parts.disc(2 * FINGER_HUB, STAR_Z[1] - FLANGE_Z[1] + 0.01, z0=FLANGE_Z[1] - 0.01).moved(bd.Location((F[0], F[1], 0)))
    fing += _poly_prism(finger_outline(f_rot, F), *STAR_Z)
    wedge_tip = _at(F, FINGER_TIP - FINGER_W, f_rot)
    fing += _prism(_bar(F, wedge_tip, FINGER_W), FLANGE_Z[1] - 0.01, STAR_Z[0] + 0.01)  # support under the finger
    m = _at(F, MAGNET_R, f_rot + 180.0)
    fing -= parts.disc(MAGNET[0] + 0.2, MAGNET[1] + 0.1, z0=FLANGE_Z[0] - 0.01).moved(bd.Location((m[0], m[1], 0)))
    dshaft = parts.disc(3.05, 20, z0=FLANGE_Z[0] - 1).moved(bd.Location((F[0], F[1], 0)))
    fing -= dshaft
    out.append(("e6_finger", fing, dict(material="PETG", group="station", nozzle=0.2, print_up=(0, 0, 1),
                                        note="on the gearmotor's D-shaft; flange with the home magnet")))
    out.append(("e6_magnet", parts.disc(*MAGNET, z0=FLANGE_Z[0]).moved(bd.Location((m[0], m[1], 0))),
                dict(material="steel", printed=False, group="station", note="Ø5 x 2 magnet: home")))
    # gearmotor (Pololu micro-metal, 298:1 HP 6 V): gearbox 12 x 10 x 9, motor 15, D-shaft 10 from the face
    blk = lambda w_t, w_u, z0, z1: _prism([(F[0] + sx * w_t / 2 * tx + sy * w_u / 2 * ux, F[1] + sx * w_t / 2 * ty + sy * w_u / 2 * uy)
                                           for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))], z0, z1)
    motor = blk(12.0, 10.0, GEARBOX_FACE - 9.0 - 15.0, GEARBOX_FACE)
    motor += parts.disc(4.0, 0.7, z0=GEARBOX_FACE).moved(bd.Location((F[0], F[1], 0)))
    motor += parts.disc(3.0, 10.0 - 0.7, z0=GEARBOX_FACE + 0.7).moved(bd.Location((F[0], F[1], 0)))
    out.append(("E6_gearmotor", motor, dict(material="black", printed=False, group="station",
                                            note="Pololu 298:1 micro metal gearmotor HP 6 V (#994)")))
    # bracket: plate on the gearbox face, sleeve under the star, jumper pivot boss, wire anchor, standoffs
    jg = jumper_geometry()
    pts = [S, F, jg["pivot"], jg["anchor"], hall_xy()] + standoff_xy()
    from shapely.geometry import MultiPoint
    hull = MultiPoint(pts).convex_hull.buffer(4.0, 16)
    plate = _poly_prism(hull, *PLATE_Z)
    plate -= parts.disc(5.0, 10, z0=PLATE_Z[0] - 1).moved(bd.Location((F[0], F[1], 0)))          # gearbox boss
    for sx in (-1, 1):                                                                          # 2 x M1.6, counterbored
        h = (F[0] + sx * 4.5 * tx, F[1] + sx * 4.5 * ty)
        plate -= parts.disc(1.8, 10, z0=PLATE_Z[0] - 1).moved(bd.Location((h[0], h[1], 0)))
        plate -= parts.disc(3.4, 1.1, z0=PLATE_Z[1] - 1.0).moved(bd.Location((h[0], h[1], 0)))
    plate += parts.disc(2 * TUBE_R, STAR_Z[0] - 0.1 - PLATE_Z[1] + 0.01, z0=PLATE_Z[1] - 0.01).moved(bd.Location((S[0], S[1], 0)))
    plate -= parts.disc(STUD_D - 0.05, 30, z0=PLATE_Z[0] - 1).moved(bd.Location((S[0], S[1], 0)))
    plate += parts.disc(3.2, STAR_Z[0] - 0.1 - PLATE_Z[1] + 0.01, z0=PLATE_Z[1] - 0.01).moved(
        bd.Location((jg["pivot"][0], jg["pivot"][1], 0)))
    plate += _prism(_circle(jg["anchor"], 1.5, 16), PLATE_Z[1] - 0.01, STAR_Z[1])
    for p in standoff_xy():
        plate += parts.disc(STANDOFF_D, CARRIER_BACK - PLATE_Z[1] + 0.01, z0=PLATE_Z[1] - 0.01).moved(bd.Location((p[0], p[1], 0)))
        plate -= parts.disc(4.0, 5.0, z0=CARRIER_BACK - 5.0).moved(bd.Location((p[0], p[1], 0)))   # M3 heat-set insert
    hx, hy = hall_xy()
    plate -= _prism([(hx + sx * 2.1 * tx + sy * 0.9 * ux, hy + sx * 2.1 * ty + sy * 0.9 * uy)
                     for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))], PLATE_Z[1] - 1.6, PLATE_Z[1] + 0.1)
    out.append(("e6_bracket", plate, dict(material="PETG", group="station", print_up=(0, 0, 1),
                                          note="holds the gearmotor (2 x M1.6), the star's stud, the jumper, the Hall sensor; 3 x M3 to the carrier")))
    out.append(("e6_hall", _prism([(hx + sx * 2.0 * tx + sy * 0.75 * ux, hy + sx * 2.0 * ty + sy * 0.75 * uy)
                                   for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))], PLATE_Z[1] - 1.5, PLATE_Z[1] - 0.05),
                dict(material="green", printed=False, group="station", note="DRV5032 Hall switch (TO-92): E6 home")))
    # star jumper, its pivot pin and wire spring
    jump = _prism(jumper_outline(), *STAR_Z) - parts.disc(1.6, 10, z0=STAR_Z[0] - 1).moved(
        bd.Location((jg["pivot"][0], jg["pivot"][1], 0)))
    out.append(("e6_jumper", jump, dict(material="PETG", group="station", nozzle=0.2,
                                        note="holds the star (so the ring) between steps; settles each step")))
    out.append(("e6_jumper_pivot", parts.rod(1.5, STAR_Z[1] - 0.2 - PLATE_Z[0]).moved(
        bd.Location((jg["pivot"][0], jg["pivot"][1], PLATE_Z[0]))), dict(material="steel", printed=False, group="station")))
    out.append(("e6_jumper_spring", _wire(jg["anchor"], jg["contact"], JUMPER_WIRE_D, (STAR_Z[0] + STAR_Z[1]) / 2),
                dict(material="steel", printed=False, group="station",
                     note=f"Ø{JUMPER_WIRE_D} spring wire, glued in the bracket's anchor; presses the jumper")))
    return out


STAR_ALLOW = [("e6_star", "e6_pinion"), ("e6_star", "e6_stud"), ("e6_pinion", "e6_stud"), ("e6_stud", "e6_bracket"),
              ("e6_finger", "E6_gearmotor"), ("e6_finger", "e6_magnet"), ("E6_gearmotor", "e6_bracket"),
              ("e6_bracket", "e6_hall"), ("e6_jumper", "e6_jumper_pivot"), ("e6_jumper_pivot", "e6_bracket"),
              ("e6_jumper", "e6_jumper_spring"), ("e6_jumper_spring", "e6_bracket"), ("e6_star", "e6_jumper")]


def carrier_cuts():
    """Holes in the carrier: the star's tube, and the bracket's three M3 screws (countersunk)."""
    S = star_xy()
    cut = parts.disc(2 * TUBE_R + 1.0, 10, z0=-15).moved(bd.Location((S[0], S[1], 0)))
    for p in standoff_xy():
        cut += parts.disc(3.4, 10, z0=-15).moved(bd.Location((p[0], p[1], 0)))
    return cut


# --- springs and loads -------------------------------------------------------------------------------
def jumper_spring() -> dict:
    """The star jumper's wire: forces at the nose and the wire's stress, at rest and with the nose
    lifted over a star point [D: cantilever F = 3EI d / L^3, stress 3E d d / (2 L^2)]."""
    from cad.modules.m2_main_dial import setter as S
    g = jumper_geometry()
    arm_n = math.dist(g["pivot"], g["nose"])
    arm_c = JUMPER_WIRE_AT * JUMPER_ARM
    d, L_ = JUMPER_WIRE_D, JUMPER_WIRE_L
    f_w0 = JUMPER_F_NOSE * arm_n / arm_c
    k = S._cantilever(d, L_, 1.0)[0]
    d0 = f_w0 / k
    lift_w = g["lift"] * arm_c / arm_n
    f_w1, stress = S._cantilever(d, L_, d0 + lift_w)
    return dict(d=d, L=L_, preload=d0, F_nose_rest=JUMPER_F_NOSE, F_nose_max=f_w1 * arm_c / arm_n,
                stress_max=stress, limit=0.7 * S.WIRE_RM_MIN[d])


# --- the stop lever at the pointer (canonical frame: pointer on +X, the ring moves -Y there) ---------
# It reads track S: the fixed bumps at d 0 and 1 (inner half) and the sector's lug (outer half) push its
# tip back 1.8 mm; while it is back, E6 runs another division (calendar_logic, architecture §5).
SL_TIP_X = (150.4, 154.6)          # spans both halves of track S, clear of the witness flag (r 148-149.5)
SL_TIP_W = 3.0                     # tangential width
SL_RIM_Z = -6.5                    # track S rim face (calendar.RIM_Z); bumps reach -8.3
SL_BUMP = 1.8
SL_PIVOT = (162.0, -12.0)          # (x, z): pivot axis along Y, behind the carrier, in the plate's window
SL_TAIL_X = 169.0
SL_WIRE_D, SL_WIRE_AT = 0.4, 6.2   # wire Ø; its contact, along the arm from the pivot
SL_WIRE_ANCHOR = (169.5, -19.4)    # (x, z) in the bridge, low enough to pass 2.0 under the pivot axis
SL_BRIDGE_Z0 = -20.6
SL_F_TIP = 0.20                    # N at the tip, resting on the rim [E]
BRIDGE_Y = 22.0                    # the bracket bridges the carrier's pointer opening (±6°) to screw on either side


def _xz_prism(points_xz, y0, y1):
    """Prism of an X-Z outline, extruded along Y from y0 to y1."""
    face = bd.Face(bd.Wire.make_polygon([bd.Vector(x, y0, z) for x, z in points_xz], close=True))
    return bd.extrude(face, amount=y1 - y0, dir=(0, 1, 0))


def stop_lever_rotation() -> float:
    """Lever turn (radians) that pushes the tip back by the bump height."""
    tip = ((SL_TIP_X[0] + SL_TIP_X[1]) / 2, SL_RIM_Z - 1.0)
    return SL_BUMP / abs(tip[0] - SL_PIVOT[0])


def stop_parts() -> list:
    """[(name, solid, kwargs)] at the pointer, canonical frame (calendar turns them 180°)."""
    out = []
    px, pz = SL_PIVOT
    w = SL_TIP_W / 2
    z_top = SL_RIM_Z - 0.05
    # lever (X-Z profile extruded along Y): pivot boss, arm down to the tip, tail with the opto flag
    arm = _xz_prism(_bar((px, pz), ((SL_TIP_X[0] + SL_TIP_X[1]) / 2, z_top - 1.0), 2.0), -w, w)
    boss = parts.disc(3.4, 2 * w, z0=-w).rotate(bd.Axis.X, 90).moved(bd.Location((px, w, pz)))
    boss = bd.Cylinder(1.7, 2 * w, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.X, 90).moved(
        bd.Location((px, 0, pz)))
    tail = _xz_prism(_bar((px, pz), (SL_TAIL_X, pz), 2.0), -w, w)
    flag = _xz_prism([(SL_TAIL_X - 1.0, pz - 1.0), (SL_TAIL_X + 0.6, pz - 1.0), (SL_TAIL_X + 0.6, pz + 3.0),
                      (SL_TAIL_X - 1.0, pz + 3.0)], -0.4, 0.4)
    # the tip: a block under the rim face, its +Y side bevelled at 45° (the bumps arrive from +Y)
    z0 = z_top - 2.0
    tip_yz = [(-w, z0), (w, z0), (w, z0 + 0.1), (w - (z_top - z0 - 0.1), z_top), (-w, z_top)]
    tip = bd.extrude(bd.Face(bd.Wire.make_polygon([bd.Vector(SL_TIP_X[0], y, z) for y, z in tip_yz], close=True)),
                     amount=SL_TIP_X[1] - SL_TIP_X[0], dir=(1, 0, 0))
    lever = arm + boss + tail + flag + tip
    lever -= bd.Cylinder(0.8, 10, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.X, 90).moved(
        bd.Location((px, 0, pz)))
    out.append(("stop_lever", lever, dict(material="PETG", group="pointer", nozzle=0.2, print_up=(0, 1, 0),
                                          note="held back by S and the sector's lug: keeps E6 running")))
    out.append(("stop_lever_pivot", bd.Cylinder(0.75, 2 * w + 4.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(
        bd.Axis.X, 90).moved(bd.Location((px, 0, pz))), dict(material="steel", printed=False, group="pointer",
                                                             note="Ø1.5 pin in the bridge's cheeks")))
    # bridge: spans the carrier's opening, cheeks either side of the lever, wire anchor, opto pocket
    zb = (SL_BRIDGE_Z0, -10.9)
    bridge = _xz_prism([(px - 4.0, zb[0]), (SL_TAIL_X + 4.0, zb[0]), (SL_TAIL_X + 4.0, zb[1]), (px - 4.0, zb[1])],
                       -BRIDGE_Y, BRIDGE_Y)
    bridge -= _xz_prism([(px - 4.5, zb[0] - 1), (SL_TAIL_X + 4.5, zb[0] - 1), (SL_TAIL_X + 4.5, zb[1] + 1),
                         (px - 4.5, zb[1] + 1)], -w - 0.3, w + 0.3)                 # slot for the lever
    bridge -= bd.Cylinder(0.73, 2 * w + 4.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(
        bd.Axis.X, 90).moved(bd.Location((px, 0, pz)))
    for sy in (-1, 1):
        bridge -= bd.Cylinder(2.0, 6.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).moved(
            bd.Location(((px + SL_TAIL_X) / 2, sy * (BRIDGE_Y - 3.0), zb[1] + 0.01)))        # M3 heat-set insert
    out.append(("stop_bridge", bridge, dict(material="PETG", group="pointer", print_up=(0, 0, 1),
                                            note="bridges the carrier's pointer opening; 2 x M3 into the carrier")))
    # wire spring under the arm, pushing it forward (+Z): from the bridge, under the pivot boss
    (ax_, az_), (cx, cz) = SL_WIRE_ANCHOR, stop_wire_contact()
    L_ = math.hypot(cx - ax_, cz - az_) + 0.6
    ang = math.degrees(math.atan2(cz - az_, cx - ax_))
    wire = parts.rod(SL_WIRE_D, L_).rotate(bd.Axis.Y, 90).rotate(bd.Axis.Y, -ang).moved(bd.Location((ax_, 0.0, az_)))
    out.append(("stop_lever_spring", wire, dict(material="steel", printed=False, group="pointer",
                                                note=f"Ø{SL_WIRE_D} spring wire, glued in the bridge; presses the lever forward")))
    # opto fork astride the flag (slot along X), body in the bridge
    fork = _xz_prism([(SL_TAIL_X - 3.0, pz + 1.2), (SL_TAIL_X + 3.0, pz + 1.2), (SL_TAIL_X + 3.0, pz + 2.6),
                      (SL_TAIL_X - 3.0, pz + 2.6)], -3.0, 3.0)
    fork -= _xz_prism([(SL_TAIL_X - 3.5, pz + 1.1), (SL_TAIL_X + 3.5, pz + 1.1), (SL_TAIL_X + 3.5, pz + 2.7),
                       (SL_TAIL_X - 3.5, pz + 2.7)], -1.55, 1.55)
    out.append(("stop_opto", fork, dict(material="green", printed=False, group="pointer",
                                        note="slotted opto switch (3 mm slot): the flag breaks the beam when the lever is back")))
    return out


STOP_ALLOW = [("stop_lever", "stop_lever_pivot"), ("stop_lever_pivot", "stop_bridge"), ("stop_lever", "stop_lever_spring"),
              ("stop_lever_spring", "stop_bridge"), ("stop_opto", "stop_bridge")]


def stop_wire_contact():
    """(x, z) of the wire's centre where it presses the arm's underside."""
    px, pz = SL_PIVOT
    t = ((SL_TIP_X[0] + SL_TIP_X[1]) / 2 - px, (SL_RIM_Z - 0.05 - 1.0) - pz)
    n = math.hypot(*t)
    ax_, az_ = t[0] / n, t[1] / n
    under = (az_, -ax_) if az_ < 0 else (-az_, ax_)                       # the normal pointing to -Z
    under = (-abs(under[0]) if ax_ < 0 else abs(under[0]), -abs(under[1]))
    return (px + ax_ * SL_WIRE_AT + under[0] * (1.0 + SL_WIRE_D / 2),
            pz + az_ * SL_WIRE_AT + under[1] * (1.0 + SL_WIRE_D / 2))


def stop_spring() -> dict:
    from cad.modules.m2_main_dial import setter as S
    tip_arm = abs((SL_TIP_X[0] + SL_TIP_X[1]) / 2 - SL_PIVOT[0])
    L_ = math.dist(SL_WIRE_ANCHOR, stop_wire_contact())
    f_w0 = SL_F_TIP * tip_arm / SL_WIRE_AT
    k = S._cantilever(SL_WIRE_D, L_, 1.0)[0]
    d0 = f_w0 / k
    f_w1, stress = S._cantilever(SL_WIRE_D, L_, d0 + SL_BUMP * SL_WIRE_AT / tip_arm)
    return dict(d=SL_WIRE_D, L=L_, preload=d0, F_tip_rest=SL_F_TIP, F_tip_max=f_w1 * SL_WIRE_AT / tip_arm,
                stress_max=stress, limit=0.7 * S.WIRE_RM_MIN[SL_WIRE_D])


# --- variant "pawl" (the fallback): crank, slotted pawl over a fixed fulcrum, ring jumper ------------
# Local frame at the hook: x along the ring's motion (clockwise), y outward, origin on the pitch line
# at PSI_E. The pawl slides over the fulcrum pin, so its hook traces an oval: down into a gap while
# it moves forward (pushing 1.21 pitches), lifted 2.5 mm clear of the tips on the way back; no pawl
# spring. Everything stays outside r 171.5 and in the lip's front 2.3 mm, clear of the rocker.
PAWL_K, PAWL_E, PAWL_Q, PAWL_LEN = (-16.0, 5.5), 2.4, (-6.0, 3.0), 17.31
PAWL_Z = MESH_Z
CRANK_Z = (-8.6, -7.1)             # crank disc in front of the carrier (front at -8.8)
PAWL_PLATE_Z = (-17.6, -15.6)      # bracket plate on the gearbox face (shaft reaches the crank disc)
PAWL_REST_PHASE = -0.30            # ring's rest phase at the hook (pitches): the middle of the window
RING_JUMPER_X = 12.0               # the ring jumper, downstream of the pawl
RJ_NOSE_R, RJ_ARM = 1.3, 9.0
RJ_WIRE_D, RJ_WIRE_L, RJ_WIRE_AT = 0.5, 17.0, 0.6
RJ_F_NOSE = 0.40                   # N at rest [E]


def _frame():
    """World origin and unit vectors (x along the ring's clockwise motion, y outward) at the hook."""
    R = RING.pitch_radius
    ux, uy = _u(PSI_E)
    x_hat = (uy, -ux)                                                       # clockwise tangent
    return (R * ux, R * uy), x_hat, (ux, uy)


def _w(p):
    o, xh, yh = _frame()
    return (o[0] + p[0] * xh[0] + p[1] * yh[0], o[1] + p[0] * xh[1] + p[1] * yh[1])


def pawl_pose(beta_deg: float):
    """(crank pin, hook tip, unit pawl direction) in the local frame, crank angle beta."""
    b = math.radians(beta_deg)
    P = (PAWL_K[0] + PAWL_E * math.cos(b), PAWL_K[1] + PAWL_E * math.sin(b))
    dx, dy = PAWL_Q[0] - P[0], PAWL_Q[1] - P[1]
    n = math.hypot(dx, dy)
    d = (dx / n, dy / n)
    return P, (P[0] + PAWL_LEN * d[0], P[1] + PAWL_LEN * d[1]), d


def _engaged_mean_angle() -> float:
    """Mean pawl direction (degrees, local frame) while the hook is below the tooth tips."""
    R = RING.pitch_radius
    angs = [math.degrees(math.atan2(pawl_pose(b)[2][1], pawl_pose(b)[2][0])) for b in range(0, 360, 2)
            if pawl_pose(b)[1][1] < RING.tip_radius - R]
    return sum(angs) / len(angs)


def hook_outline(beta_deg: float):
    """The hook, local frame. Drawn upright at the pawl's mean engaged angle (front face along +y,
    a 0.5 mm tip, back at 20° like the flank of the tooth behind, 2.2 mm tall), then carried
    rigidly with the pawl: it tilts only by the pawl's swing about that mean (about ±13°)."""
    P, H, d = pawl_pose(beta_deg)
    rot = math.atan2(d[1], d[0]) - math.radians(_engaged_mean_angle())
    back = 0.5 + 2.2 * math.tan(math.radians(20.0))
    loc = [(0.0, 0.0), (0.0, 2.2), (-back, 2.2), (-0.5, 0.0)]              # (x, y) from the tip, upright
    c, s_ = math.cos(rot), math.sin(rot)
    return [(H[0] + x * c - y * s_, H[1] + x * s_ + y * c) for x, y in loc]


def pawl_home() -> float:
    """Crank angle at rest: the hook at the top of its oval (clear of the teeth)."""
    return max(range(0, 360, 2), key=lambda b: pawl_pose(b)[1][1])


def pawl_push(phase_error: float = 0.0, depth_error: float = 0.0, dth: float = 1.0):
    """One crank turn (from home) pushing the ring's teeth, local frame: returns (advance in
    pitches, jammed). depth_error moves the ring outward (towards the pawl)."""
    from shapely.geometry import Polygon
    from shapely import affinity
    R = RING.pitch_radius
    o = RING.outline(flank_points=4, arc_points=2)
    ring = Polygon(o).buffer(0)
    # local frame: rotate so the hook's angle (pitch point) sits on +Y... place the ring centre at (0, -R)
    # with its tooth/gap phase as the rest pose (a gap centred where the hook lands is set by the jumper)
    ring = affinity.translate(affinity.rotate(ring, 90.0, origin=(0, 0)), 0.0, -R + depth_error)
    pitch = 360.0 / L.N
    land = None
    b0 = pawl_home()
    for k in range(int(360 / dth)):                                       # find where the hook dips below the tips
        b = b0 - k * dth                                                  # the crank turns with beta decreasing
        if pawl_pose(b)[1][1] < RING.tip_radius - R:
            land = pawl_pose(b)[1][0]
            break
    # rest phase: a gap's centre just ahead of the landing point (the jumper holds this), plus the error
    gap_x = land + 0.5 + phase_error * (2 * math.pi * R / L.N)
    phi0 = -math.degrees(gap_x / R) + 180.0 / L.N * 0 - 180.0 / L.N     # tooth 0 on +Y: gaps at +/- half a pitch
    phi = phi0
    for k in range(int(360 / dth) + 1):
        b = b0 - k * dth
        hook = Polygon(hook_outline(b))
        cur = affinity.rotate(ring, phi, origin=(0, -R + depth_error))
        if hook.intersection(cur).area > 1e-6:
            step, d = pitch / 400, pitch / 400
            while d < 0.6 * pitch and hook.intersection(
                    affinity.rotate(ring, phi - d, origin=(0, -R + depth_error))).area > 1e-6:
                d += step
            if d >= 0.6 * pitch:
                return (phi0 - phi) / pitch, True
            phi -= d
    return (phi0 - phi) / pitch, False


def pawl_landing_x() -> float:
    """Local x where the hook tip first dips below the tooth tips, the crank turning from home."""
    R = RING.pitch_radius
    b0 = pawl_home()
    for k in range(720):
        b = b0 - k * 0.5
        if pawl_pose(b)[1][1] < RING.tip_radius - R:
            return pawl_pose(b)[1][0]
    raise RuntimeError("the hook never reaches the teeth")


def pawl_gap_x() -> float:
    """Local x of the ring gap the hook must land in, at rest (set by the ring jumper)."""
    return pawl_landing_x() + 0.5 + PAWL_REST_PHASE * (2 * math.pi * RING.pitch_radius / L.N)


def psi_pawl() -> float:
    """Angle of the pawl station's frame: PSI_E nudged so that a gap of the ring (gaps at world
    180 + DIV/2 + j DIV at rest, teeth centred on divisions) sits at pawl_gap_x()."""
    R = RING.pitch_radius
    want = PSI_E - math.degrees(pawl_gap_x() / R)                     # where the gap must be (world)
    base = 180.0 + DIV / 2
    j = round((want - base) / DIV)
    return PSI_E + (base + j * DIV - want)


def _frame_a():
    R = RING.pitch_radius
    ux, uy = _u(psi_pawl())
    return (R * ux, R * uy), (uy, -ux), (ux, uy)


def _wa(p):
    o, xh, yh = _frame_a()
    return (o[0] + p[0] * xh[0] + p[1] * yh[0], o[1] + p[0] * xh[1] + p[1] * yh[1])


def ring_jumper_geometry():
    """Ring jumper (variant "pawl"): a round nose resting on two tooth tips over the gap at about
    RING_JUMPER_X, its arm running forward (the ring's drag pulls it) to a pivot outside r 172."""
    from shapely.geometry import Polygon, Point
    from shapely import affinity
    R = RING.pitch_radius
    p_len = 2 * math.pi * R / L.N
    xg = pawl_gap_x() + round((RING_JUMPER_X - pawl_gap_x()) / p_len) * p_len
    ring = _local_ring(xg)
    lo, hi = RING.tip_radius - R - 2.0, RING.tip_radius - R + RJ_NOSE_R + 1.0
    for _ in range(50):                                                  # nose centre: lowest without overlap
        mid = (lo + hi) / 2
        if Point(xg, mid).buffer(RJ_NOSE_R, 64).intersection(ring).area > 1e-7: lo = mid
        else: hi = mid
    nose = (xg, hi)
    pivot = (xg + RJ_ARM, hi + 2.2)
    arm = (RJ_ARM, 2.2)
    na = math.hypot(*arm)
    ad, an_ = (arm[0] / na, arm[1] / na), (-arm[1] / na, arm[0] / na)        # along the arm, its outer normal
    c_at = (pivot[0] - RJ_WIRE_AT * arm[0] + (0.8 + RJ_WIRE_D / 2) * an_[0],
            pivot[1] - RJ_WIRE_AT * arm[1] + (0.8 + RJ_WIRE_D / 2) * an_[1])
    tilt = wire_tilt(c_at, pivot, ad, an_, 1.6 + RJ_WIRE_D / 2 + 0.15)
    u = (ad[0] * math.cos(tilt) + an_[0] * math.sin(tilt), ad[1] * math.cos(tilt) + an_[1] * math.sin(tilt))
    anchor = (c_at[0] + RJ_WIRE_L * u[0], c_at[1] + RJ_WIRE_L * u[1])
    return {"gap_x": xg, "nose": nose, "pivot": pivot, "contact": c_at, "anchor": anchor}


def _local_ring(x_gap: float):
    """The ring's teeth in the pawl's local frame with a gap centred at x_gap (shapely)."""
    from shapely.geometry import Polygon
    from shapely import affinity
    R = RING.pitch_radius
    ring = Polygon(RING.outline(flank_points=4, arc_points=2)).buffer(0)
    ring = affinity.translate(affinity.rotate(ring, 90.0, origin=(0, 0)), 0.0, -R)
    phi = -math.degrees(x_gap / R) - 180.0 / L.N
    return affinity.rotate(ring, phi, origin=(0, -R))


def ring_jumper_ride():
    """The nose's height as the ring moves one pitch under it (local frame), and the steepest
    slope it climbs: (lift mm, max slope degrees)."""
    from shapely.geometry import Point
    from shapely import affinity
    g = ring_jumper_geometry()
    R = RING.pitch_radius
    p_len = 2 * math.pi * R / L.N
    ys, xs = [], []
    for k in range(41):
        s = p_len * k / 40
        ring = _local_ring(g["gap_x"] + s)
        lo, hi = g["nose"][1] - 0.5, RING.tip_radius - R + RJ_NOSE_R + 0.5
        for _ in range(40):
            mid = (lo + hi) / 2
            if Point(g["nose"][0], mid).buffer(RJ_NOSE_R, 64).intersection(ring).area > 1e-7: lo = mid
            else: hi = mid
        ys.append(hi); xs.append(s)
    slope = max(abs(ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i]) for i in range(40))
    return max(ys) - min(ys), math.degrees(math.atan(slope))


def ring_jumper_spring() -> dict:
    """Ring jumper's wire (variant "pawl"): forces at the nose and the wire's stress."""
    from cad.modules.m2_main_dial import setter as S
    g = ring_jumper_geometry()
    lift, _ = ring_jumper_ride()
    arm_n = math.dist(g["pivot"], g["nose"])
    arm_c = RJ_WIRE_AT * math.hypot(RJ_ARM, 2.2)
    f_w0 = RJ_F_NOSE * arm_n / arm_c
    k = S._cantilever(RJ_WIRE_D, RJ_WIRE_L, 1.0)[0]
    d0 = f_w0 / k
    f_w1, stress = S._cantilever(RJ_WIRE_D, RJ_WIRE_L, d0 + lift * arm_c / arm_n)
    return dict(d=RJ_WIRE_D, L=RJ_WIRE_L, lift=lift, F_nose_rest=RJ_F_NOSE, F_nose_max=f_w1 * arm_c / arm_n,
                stress_max=stress, limit=0.7 * S.WIRE_RM_MIN[RJ_WIRE_D])


def pawl_parts(pointer: int) -> list:
    """[(name, solid, kwargs)] of variant "pawl", world frame, at rest (crank at home)."""
    out = []
    o, xh, yh = _frame_a()
    W = _wa
    b0 = pawl_home()
    P, H, d = pawl_pose(b0)
    K = W(PAWL_K)
    Kl = PAWL_K
    # gearmotor at K, face on the bracket plate; crank disc (pin at the home angle) in front of the carrier
    face_z = PAWL_PLATE_Z[0]
    tx, ty = xh
    ux, uy = yh
    blk = [(K[0] + sx * 6.0 * tx + sy * 5.0 * ux, K[1] + sx * 6.0 * ty + sy * 5.0 * uy)
           for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    motor = _prism(blk, face_z - 24.0, face_z)
    motor += parts.disc(4.0, 0.7, z0=face_z).moved(bd.Location((K[0], K[1], 0)))
    motor += parts.disc(3.0, 9.3, z0=face_z + 0.7).moved(bd.Location((K[0], K[1], 0)))
    out.append(("E6_gearmotor", motor, dict(material="black", printed=False, group="station",
                                            note="Pololu 298:1 micro metal gearmotor HP 6 V (#994)")))
    crank = parts.disc(6.6, CRANK_Z[1] - CRANK_Z[0], z0=CRANK_Z[0]).moved(bd.Location((K[0], K[1], 0)))
    crank += parts.disc(5.0, CRANK_Z[0] - (PAWL_PLATE_Z[1] + 0.2) + 0.01, z0=PAWL_PLATE_Z[1] + 0.2).moved(bd.Location((K[0], K[1], 0)))
    crank += parts.disc(13.0, 2.4, z0=PAWL_PLATE_Z[1] + 0.2).moved(bd.Location((K[0], K[1], 0)))     # magnet flange
    m = W((Kl[0] + 4.3 * math.cos(math.radians(b0 + 180)), Kl[1] + 4.3 * math.sin(math.radians(b0 + 180))))
    crank -= parts.disc(MAGNET[0] + 0.2, MAGNET[1] + 0.1, z0=PAWL_PLATE_Z[1] + 0.19).moved(bd.Location((m[0], m[1], 0)))
    crank -= parts.disc(3.05, 30, z0=-30).moved(bd.Location((K[0], K[1], 0)))
    pin = W(P)
    crank -= parts.disc(1.45, 10, z0=CRANK_Z[0] - 1).moved(bd.Location((pin[0], pin[1], 0)))
    out.append(("e6_crank", crank, dict(material="PETG", group="station", nozzle=0.2,
                                        note="on the D-shaft; crank pin r 2.4; flange with the home magnet")))
    out.append(("e6_magnet", parts.disc(*MAGNET, z0=PAWL_PLATE_Z[1] + 0.2).moved(bd.Location((m[0], m[1], 0))),
                dict(material="steel", printed=False, group="station", note="Ø5 x 2 magnet: home")))
    out.append(("e6_crank_pin", parts.rod(1.5, PAWL_Z[1] - 0.1 - CRANK_Z[0]).moved(bd.Location((pin[0], pin[1], CRANK_Z[0]))),
                dict(material="steel", printed=False, group="station", note="Ø1.5, pressed into the crank")))
    # pawl: eye on the crank pin, bar along d, slot over the fulcrum, hook at the end
    from shapely.geometry import Polygon, Point
    from shapely.ops import unary_union
    dmin = min(math.dist(pawl_pose(b)[0], PAWL_Q) for b in range(0, 360, 3))
    dmax = max(math.dist(pawl_pose(b)[0], PAWL_Q) for b in range(0, 360, 3))
    along = lambda a: (P[0] + a * d[0], P[1] + a * d[1])
    bar = Polygon(_bar(P, along(PAWL_LEN - 0.3), 2.4))
    eye = Point(*P).buffer(1.7, 24)
    slot = Polygon(_bar(along(dmin - 0.9), along(dmax + 0.9), 1.7)).union(Point(*along(dmin - 0.9)).buffer(0.85, 16)).union(
        Point(*along(dmax + 0.9)).buffer(0.85, 16))
    body = unary_union([bar, eye, Polygon(hook_outline(b0))]).difference(slot).difference(Point(*P).buffer(0.8, 16))
    pawl = _poly_prism(body, *PAWL_Z, xform=W)
    out.append(("e6_pawl", pawl, dict(material="PETG", group="station", nozzle=0.2,
                                      note="slides over the fulcrum pin: hook down and forward, then up and back")))
    Q = W(PAWL_Q)
    out.append(("e6_fulcrum", parts.rod(1.5, PAWL_Z[1] - 0.1 - PAWL_PLATE_Z[0]).moved(bd.Location((Q[0], Q[1], PAWL_PLATE_Z[0]))),
                dict(material="steel", printed=False, group="station", note="Ø1.5, pressed into the bracket")))
    # ring jumper, its pivot, wire and the wire's anchor post
    g = ring_jumper_geometry()
    jb = unary_union([Point(*g["nose"]).buffer(RJ_NOSE_R, 32), Polygon(_bar(g["nose"], g["pivot"], 1.6)),
                      Point(*g["pivot"]).buffer(1.6, 24)]).difference(Point(*g["pivot"]).buffer(0.8, 16))
    out.append(("ring_jumper", _poly_prism(jb, *PAWL_Z, xform=W),
                dict(material="PETG", group="station", nozzle=0.2,
                     note="round nose on two tooth tips: holds the ring, settles each step")))
    jp = W(g["pivot"])
    out.append(("ring_jumper_pivot", parts.rod(1.5, PAWL_Z[1] - 0.1 - PAWL_PLATE_Z[0]).moved(bd.Location((jp[0], jp[1], PAWL_PLATE_Z[0]))),
                dict(material="steel", printed=False, group="station")))
    an, ct = W(g["anchor"]), W(g["contact"])
    out.append(("ring_jumper_spring", _wire(an, ct, RJ_WIRE_D, (PAWL_Z[0] + PAWL_Z[1]) / 2),
                dict(material="steel", printed=False, group="station", note=f"Ø{RJ_WIRE_D} spring wire, glued in its post")))
    # bracket: plate on the gearbox face, standoffs, the post for the wire anchor, Hall pocket
    hall = W((Kl[0] + 4.3 * math.cos(math.radians(b0 + 180)), Kl[1] + 4.3 * math.sin(math.radians(b0 + 180))))
    stand = [W((PAWL_K[0] - 10.5, PAWL_K[1] + 2.0)), W((PAWL_K[0] + 8.0, PAWL_K[1] + 6.0)), W((g["anchor"][0] + 3.0, g["anchor"][1] + 3.0))]
    from shapely.geometry import MultiPoint
    hull = MultiPoint([K, Q, jp, an, hall] + stand).convex_hull.buffer(4.0, 16)
    plate = _poly_prism(hull, *PAWL_PLATE_Z)
    plate -= parts.disc(5.0, 10, z0=PAWL_PLATE_Z[0] - 1).moved(bd.Location((K[0], K[1], 0)))
    for sx in (-1, 1):
        h = (K[0] + sx * 4.5 * tx, K[1] + sx * 4.5 * ty)
        plate -= parts.disc(1.8, 10, z0=PAWL_PLATE_Z[0] - 1).moved(bd.Location((h[0], h[1], 0)))
        plate -= parts.disc(3.4, 1.1, z0=PAWL_PLATE_Z[1] - 1.0).moved(bd.Location((h[0], h[1], 0)))
    for p in stand:
        plate += parts.disc(STANDOFF_D, CARRIER_BACK - PAWL_PLATE_Z[1] + 0.01, z0=PAWL_PLATE_Z[1] - 0.01).moved(bd.Location((p[0], p[1], 0)))
        plate -= parts.disc(4.0, 5.0, z0=CARRIER_BACK - 5.0).moved(bd.Location((p[0], p[1], 0)))
    plate += parts.disc(2.6, PAWL_Z[1] - PAWL_PLATE_Z[1] + 0.01, z0=PAWL_PLATE_Z[1] - 0.01).moved(bd.Location((an[0], an[1], 0)))
    for q in (Q, jp):
        plate -= parts.disc(1.45, 10, z0=PAWL_PLATE_Z[0] - 1).moved(bd.Location((q[0], q[1], 0)))
    plate -= parts.disc(4.4, 1.6, z0=PAWL_PLATE_Z[1] - 1.5).moved(bd.Location((hall[0], hall[1], 0)))
    out.append(("e6_bracket", plate, dict(material="PETG", group="station", print_up=(0, 0, 1),
                                          note="variant pawl: gearmotor (2 x M1.6), fulcrum and jumper pins, wire post, Hall; 3 x M3")))
    out.append(("e6_hall", parts.disc(4.0, 1.5, z0=PAWL_PLATE_Z[1] - 1.5).moved(bd.Location((hall[0], hall[1], 0))),
                dict(material="green", printed=False, group="station", note="DRV5032 Hall switch: E6 home")))
    return out


PAWL_ALLOW = [("e6_crank", "E6_gearmotor"), ("e6_crank", "e6_magnet"), ("e6_crank", "e6_crank_pin"),
              ("e6_pawl", "e6_crank_pin"), ("e6_fulcrum", "e6_bracket"), ("E6_gearmotor", "e6_bracket"),
              ("ring_jumper", "ring_jumper_pivot"), ("ring_jumper_pivot", "e6_bracket"),
              ("ring_jumper", "ring_jumper_spring"), ("ring_jumper_spring", "e6_bracket"), ("e6_bracket", "e6_hall")]


def pawl_carrier_cuts():
    o, xh, yh = _frame_a()
    g = ring_jumper_geometry()
    K, Q, jp, an = _wa(PAWL_K), _wa(PAWL_Q), _wa(g["pivot"]), _wa(g["anchor"])
    cut = parts.disc(6.0, 10, z0=-15).moved(bd.Location((K[0], K[1], 0)))
    for q, dd in ((Q, 2.0), (jp, 2.0), (an, 3.2)):
        cut += parts.disc(dd, 10, z0=-15).moved(bd.Location((q[0], q[1], 0)))
    for p in (_wa((PAWL_K[0] - 10.5, PAWL_K[1] + 2.0)), _wa((PAWL_K[0] + 8.0, PAWL_K[1] + 6.0)),
              _wa((g["anchor"][0] + 3.0, g["anchor"][1] + 3.0))):
        cut += parts.disc(3.4, 10, z0=-15).moved(bd.Location((p[0], p[1], 0)))
    return cut


def station_parts(pointer: int, drive: str = None):
    """(parts, allowances, carrier cuts) of the chosen E6 variant."""
    drive = drive or E6_DRIVE
    if drive == "star":
        return star_parts(pointer), STAR_ALLOW, carrier_cuts()
    if drive == "pawl":
        return pawl_parts(pointer), PAWL_ALLOW, pawl_carrier_cuts()
    raise ValueError(drive)


# --- loads on the ring's mesh [E] ----------------------------------------------------------------------
# Tangential force at the ring's pitch circle (r 169.58) for each kind of step, from the loads worked
# out in docs/m2-design.md §6 (setter and counter) and the stop lever's spring above.
FRICTION_N = 0.08                  # stop lever on the rim (0.2 N x 0.3 at r 152) + six ball rollers [E]
COUNTER_N = {"normal": 1.1, "leap": 1.9}            # at the counter pin, r 156.25 (m2-design §6) [E]


def mesh_loads() -> dict:
    """Tangential force at the ring's mesh (N) for: a daily step, New Year (the stop lever climbs S),
    the counter's step in an ordinary year, and in a year before a leap year."""
    from cad.modules.m2_main_dial import setter as S
    R = RING.pitch_radius
    sl = stop_spring()
    climb = sl["F_tip_max"] * math.tan(math.radians(45.0) + math.atan(S.MU)) * 152.5 / R
    out = {"daily": FRICTION_N, "new_year": FRICTION_N + climb}
    for k, f in COUNTER_N.items():
        out[f"counter_{k}"] = FRICTION_N + f * S.COUNTER_PIN_R / R
    return out


def pinion_safety() -> dict:
    """Lewis bending safety factor of the pinion (the weaker wheel) for each load, against the
    project's allowable stress (9.75 MPa: PLA's 39 MPa / 4; tools/ratios/strength.py)."""
    from tools.ratios.strength import lewis_y
    b = MESH_Z[1] - MESH_Z[0]
    cap = b * M_RING * lewis_y(PINION.teeth)
    return {k: 9.75 / (f / cap) for k, f in mesh_loads().items()}
