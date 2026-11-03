"""M2 calendar: the sector setter (flip-flop rocker and ramps) and the year counter's follower.

Concept approved by Paul (3 Nov 2026; `docs/m2-design.md` §6, `docs/img/m2/setter_concept.png`).

**On the ring (moves with it):**
- the **rocker** pivots on a pin in the ratchet lip, beside the sector. Its fork holds the sector's
  tab pin, so its two positions are the sector's two positions, one division apart;
- its two **tip pins** hang into the deep layer behind the ring, at the bottom, where the ramps can
  reach them:
  - in common, the set pin is out and the reset pin is in;
  - in leap, it is the other way;
- a printed **detent spring** holds the rocker in either position.

**At the station (fixed, 6 o'clock):**
- the **reset ramp** is fixed on the carrier. It catches a protruding reset pin and pushes it
  outward, which puts the sector in the common position;
- the **set ramp** sits on a spring **plunger** that rides on wheel C. Where C carries a leap bump,
  the plunger lifts the ramp into the set pin's lane. The ramp then pushes a protruding set pin
  inward, which puts the sector in the leap position. Without a bump the ramp sits down in a window
  of the carrier, clear of the pin;
- the rocker passes the reset ramp first and the set ramp a week later (logic: RESET_OFFSET,
  SET_OFFSET);
- the **counting lever** has a steel pin in the counter pin's lane (r 155–157.5). Once a year
  (1 October) the counter pin on the ring pushes it aside, and the hook on the lever's flexible
  finger pulls **wheel C** (a 100-tooth ratchet) round by 1.5 pitches; C's jumper then settles it at
  exactly one tooth. A spring brings the lever back to its stop. This replaces the 10-point star,
  which filled the band where the rocker must pass;
- **wheel C** carries 24 leap bumps (years 4 … 96). At position 0 it carries Ungerer's **satellite**
  [S: ELS i4], a 4-point star wheel turned a quarter turn per turn of C by a fixed pin, whose single
  arm supplies the leap bump only once in four centuries.

The ring parts are built in the calendar's canonical frame (pointer at 0°) and turned 180° with the
rest of the ring by ``calendar.build``. The station parts are built in the world frame.
"""
from __future__ import annotations

import math

import build123d as bd

from cad.lib import parts
from cad.modules.m2_main_dial import calendar_logic as L

DIV = 360.0 / L.N

# --- the rocker on the ring -------------------------------------------------------------------
TAB_R = 160.5                      # the sector's tab pin (radius on the ring)
TAB_PIN_D = 2.2
TAB_PIN_Z = (-6.9, -2.2)           # from the sector's back down into the rocker's layer
ROCKER_D = L.SECTOR_TAB - 0.5      # pivot between the tab's common (30) and leap (29) places
ROCKER_R = 165.5                   # pivot radius: under the ratchet lip
RHO = ROCKER_R - TAB_R             # pivot to tab
ARM_A, ARM_T = 2.5, 7.7            # tip pins: radial offset (set out, reset in), tangential offset
PIN_D = 1.6
BAR_Z = (-7.0, -5.6)               # the rocker's bars, under the lip (lip back at -5.5)
PIN_Z = (-8.3, -7.0)               # tip pins hang down into the ramps' layer
RAMP_TOP = -7.4                    # both ramps stay below the bars (0.4 mm)
CARRIER_FRONT = -8.8
HALF_DIV_AT_TAB = 0.5 * math.radians(DIV) * TAB_R
THETA0 = math.degrees(math.asin(HALF_DIV_AT_TAB / RHO))     # rocker swing either side of centre
HUB_R = 2.6
DETENT_NOTCH = THETA0              # notches on the hub at ±THETA0: under the wire in either position
DETENT_DEPTH, DETENT_FLANK = 0.3, 40.0             # notch depth (mm) and flank angle to the tangent (°)
DETENT_WIRE_D, DETENT_WIRE_L, DETENT_PRELOAD = 0.4, 10.0, 0.65
# the wire runs along the ring (local -y), just outside the hub; in a notch its centre is at
# HUB_R - DETENT_DEPTH + d/2, which bends it DETENT_PRELOAD outward from its clamped line
DETENT_CONTACT = (HUB_R - DETENT_DEPTH + DETENT_WIRE_D / 2, 0.0)
DETENT_ANCHOR = (DETENT_CONTACT[0], -DETENT_WIRE_L)


def _notch(a_deg):
    """A V-notch in the hub's rim at angle a (rocker frame), DETENT_DEPTH deep."""
    a = math.radians(a_deg)
    w = (DETENT_DEPTH + 0.3) / math.tan(math.radians(DETENT_FLANK))     # half-width at HUB_R + 0.3
    r_out, r_in = HUB_R + 0.3, HUB_R - DETENT_DEPTH
    da = w / r_out
    return [(r_in * math.cos(a), r_in * math.sin(a)), (r_out * math.cos(a - da), r_out * math.sin(a - da)),
            (r_out * math.cos(a + da), r_out * math.sin(a + da))]


def rocker_angle(leap: bool) -> float:
    """Rocker angle (degrees, CCW in the ring's frame) for each sector position: the tab moves
    -RHO sin(phi) along the ring, +1/2 division in common (d = 30), -1/2 in leap (d = 29)."""
    return THETA0 if leap else -THETA0


def _rot(x, y, phi):
    c, s = math.cos(math.radians(phi)), math.sin(math.radians(phi))
    return x * c - y * s, x * s + y * c


def pin_radii(leap: bool) -> dict:
    """Ring radius of each tip pin's centre, and of the tab, in either state (for the checks)."""
    phi = rocker_angle(leap)
    out = {}
    for name, (x, y) in (("set", (ARM_A, ARM_T)), ("reset", (-ARM_A, ARM_T))):
        xr, yr = _rot(x, y, phi)
        out[name] = math.hypot(ROCKER_R + xr, yr)    # ring radius of the pin centre
        out[name + "_along"] = yr
    xr, yr = _rot(-RHO, 0.0, phi)
    out["tab_along"] = yr
    return out


def _to_ring(points, a_deg):
    """Local rocker frame (x radial from the pivot, y along the ring) -> canonical XY at angle a."""
    a = math.radians(a_deg)
    ux, uy = math.cos(a), math.sin(a)
    vx, vy = -math.sin(a), math.cos(a)
    return [(ROCKER_R * ux + x * ux + y * vx, ROCKER_R * uy + x * uy + y * vy) for x, y in points]


def _prism(points, z0, z1):
    face = bd.Face(bd.Wire.make_polygon([bd.Vector(x, y, z0) for x, y in points], close=True))
    return bd.extrude(face, amount=z1 - z0, dir=(0, 0, 1))


def _bar(p, q, w):
    (x0, y0), (x1, y1) = p, q
    L_ = math.hypot(x1 - x0, y1 - y0)
    nx, ny = -(y1 - y0) / L_ * w / 2, (x1 - x0) / L_ * w / 2
    return [(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)]


def _circle(c, r, n=24):
    return [(c[0] + r * math.cos(2 * math.pi * k / n), c[1] + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def rocker_parts(pointer: int, leap: bool) -> dict:
    """{name: solid} of the ring-side parts in the canonical frame: rocker, pivot pin, detent spring."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    from cad.lib import lettering as T
    a_p = (ROCKER_D - pointer) * DIV
    phi = rocker_angle(leap)
    hub = Polygon(_circle((0, 0), HUB_R, 48))
    stem = Polygon(_bar((0, 0), (0, ARM_T), 2.0))
    cross = Polygon(_bar((-ARM_A, ARM_T), (ARM_A, ARM_T), 2.0))
    ends = [Polygon(_circle((sx * ARM_A, ARM_T), 1.0)) for sx in (-1, 1)]
    # an open fork (tines towards the dial centre): it holds the tab pin along the ring, and keeps
    # the rocker outside r 158.8, clear of the counting lever's pin
    fork_bar = Polygon(_bar((0, 0), (-RHO + 2.0, 0), 2.4))
    fork_end = Polygon([(-RHO - 1.3, -2.1), (-RHO + 2.2, -2.1), (-RHO + 2.2, 2.1), (-RHO - 1.3, 2.1)])
    slot = Polygon([(-RHO - 2.5, -(TAB_PIN_D / 2 + 0.1)), (-RHO + 1.3, -(TAB_PIN_D / 2 + 0.1)),
                    (-RHO + 1.3, TAB_PIN_D / 2 + 0.1), (-RHO - 2.5, TAB_PIN_D / 2 + 0.1)])
    body = unary_union([hub, stem, cross, fork_bar, fork_end] + ends).difference(slot)
    body = body.difference(Polygon(_circle((0, 0), 1.1)))                 # Ø2.2 bore for the Ø2 pin
    for a_n in (DETENT_NOTCH, -DETENT_NOTCH):                             # the detent's two notches
        body = body.difference(Polygon(_notch(a_n)))
    outline = [(_rot(x, y, phi)) for x, y in body.exterior.coords[:-1]]
    holes = [[_rot(x, y, phi) for x, y in r.coords[:-1]] for r in body.interiors]
    to3 = lambda pts, z: [bd.Vector(x, y, z) for x, y in _to_ring(pts, a_p)]
    face = bd.Face(bd.Wire.make_polygon(to3(outline, BAR_Z[0]), close=True),
                   [bd.Wire.make_polygon(to3(h, BAR_Z[0]), close=True) for h in holes])
    rocker = bd.extrude(face, amount=BAR_Z[1] - BAR_Z[0], dir=(0, 0, 1))
    for sx in (-1, 1):                                                     # the two tip pins
        c = _to_ring([_rot(sx * ARM_A, ARM_T, phi)], a_p)[0]
        rocker = rocker + parts.disc(PIN_D, PIN_Z[1] - PIN_Z[0] + 0.01, z0=PIN_Z[0]).moved(bd.Location((c[0], c[1], 0)))
    pc = _to_ring([(0, 0)], a_p)[0]
    pivot = parts.rod(2.0, -3.6 - BAR_Z[0]).moved(bd.Location((pc[0], pc[1], BAR_Z[0])))     # flush under the hub
    # detent: a steel wire along the ring, clamped in a block glued under the lip; its free length
    # presses on the hub's outer side, in the common notch or the leap notch
    w0, w1 = _to_ring([DETENT_ANCHOR, DETENT_CONTACT], a_p)
    anchor = _prism(_to_ring(_square(DETENT_ANCHOR, 3.0), a_p), BAR_Z[0], -5.5 + 0.01)
    wire = _wire(w0, w1, DETENT_WIRE_D, (BAR_Z[0] + BAR_Z[1]) / 2, overrun=0.5)
    return {"setter_rocker": rocker, "setter_rocker_pivot": pivot, "setter_detent_anchor": anchor,
            "setter_detent_spring": wire}


ROCKER_PART_INFO = {
    "setter_rocker": dict(material="PLA", note="flip-flop: holds the sector's tab pin; its tip pins meet the station's ramps"),
    "setter_rocker_pivot": dict(material="steel", printed=False, note="Ø2 pin pressed into the ratchet lip"),
    "setter_detent_anchor": dict(material="PETG", note="glued under the lip: clamps the detent wire"),
    "setter_detent_spring": dict(material="steel", printed=False,
                                 note="Ø0.4 spring wire: holds the rocker, so the sector, in either position"),
}


def tab_pin(pointer: int, sector_start: int):
    """The sector's tab: a Ø2.2 pin at its division, through the floor slot into the rocker's fork."""
    a = (L.SECTOR_TAB + sector_start - L.SECTOR_COMMON_START - pointer) * DIV
    x, y = TAB_R * math.cos(math.radians(a)), TAB_R * math.sin(math.radians(a))
    return parts.disc(TAB_PIN_D, TAB_PIN_Z[1] - TAB_PIN_Z[0], z0=TAB_PIN_Z[0]).moved(bd.Location((x, y, 0)))


# --- the station --------------------------------------------------------------------------------
ST = -90.0                                        # station angle, world
RESET_DELTA = (L.RESET_OFFSET - L.STATION_OFFSET) * DIV     # degrees beyond the station: about 18.6
SET_DELTA = (L.SET_OFFSET - L.STATION_OFFSET) * DIV         # about 11.7
STROKE = 1.4                                       # set-ramp lift = leap bump height: up, the ramp
                                                   # overlaps the set pin by 0.9; down, it is 0.5 under it
# a leap bump, along C's bump circle (s in mm, + = anticlockwise, the side that reaches the plunger
# first): a ramp from the foot up to the top, a short top, then a sheer drop on the leaving side, so the
# plunger climbs on only when C steps onto that year and drops off when it steps on
BUMP_FOOT, BUMP_TOP0, BUMP_DROP = 1.5, 0.25, -0.35
BUMP_HALF_W = 1.0                                  # radial half-width
TIP_R = 0.4                                        # the plunger's ball tip
COLLAR_D, COLLAR_T = 5.0, 0.8                      # the plunger's collar: the spring pushes it towards C
POCKET_D, GUIDE_D = 5.4, 3.25                      # bracket: spring pocket (the collar slides in it), guide
CEILING = -17.0                                    # the pocket's ceiling: the spring's fixed end
PLUNGER_SPRING = dict(De=4.4, Di=3.6)              # envelope of the steel compression spring (docs §6)
C_XY = (34.0, -140.0)                              # wheel C's centre (its stud is in the M2 front plate)
C_Z = (-30.9, -27.9)
C_TEETH, C_R_TIP, C_R_ROOT = 100, 31.5, 30.5      # ratchet teeth 1.0 deep
C_UNDERCUT = 0.1                                   # drive faces lean back 0.1 pitch: they pull the hook in
LEVER_PIVOT = (-8.0, -146.0)
LEVER_Z = C_Z                                      # the counting lever lies in C's layer: one flat print
COUNTER_PIN_R, COUNTER_PIN_D = 156.25, 2.5         # the ring's counter pin (calendar.R_PIN, Ø2.5)
LEVER_PIN_R, LEVER_PIN_D = 156.55, 1.5             # the lever's steel pin at rest: 1.7 mm overlap
HOOK_R = 31.0                                      # the hook's drive point, 0.5 mm above C's root
HOOK_GAP = 0.1                                     # hook to drive face at rest (mm)
FINGER_DEG, FINGER_T = 18.0, 0.6                   # the hook's flexible finger (pulled, never pushed)
PLATE_BACK = -15.0                                 # M2 front plate's back face: studs and pins pressed in


def _world(delta_deg, r):
    t = math.radians(ST + delta_deg)
    return r * math.cos(t), r * math.sin(t)


def _c_polar(psi_deg, r):
    """World XY of the point at angle psi (degrees, CCW) and radius r about wheel C's centre."""
    t = math.radians(psi_deg)
    return C_XY[0] + r * math.cos(t), C_XY[1] + r * math.sin(t)


def lever_turn() -> float:
    """Lever turn (radians, clockwise) when the counter pin slips past the lever pin: the lever pin
    is then one sum of radii outside the counter pin's circle."""
    piv, pin = LEVER_PIVOT, _world(0.0, LEVER_PIN_R)
    L_ = math.dist(piv, pin)
    a0 = math.atan2(pin[1] - piv[1], pin[0] - piv[0])
    clear = COUNTER_PIN_R + (COUNTER_PIN_D + LEVER_PIN_D) / 2
    lo, hi = 0.0, math.radians(60.0)
    for _ in range(60):
        mid = (lo + hi) / 2
        r = math.hypot(piv[0] + L_ * math.cos(a0 - mid), piv[1] + L_ * math.sin(a0 - mid))
        lo, hi = (mid, hi) if r < clear else (lo, mid)
    return hi


def hook_home():
    """The hook's drive point at rest and at full stroke: the two points of C's radius HOOK_R that
    the hook's circle about the lever pivot crosses, one lever turn apart. The stroke is then
    symmetric about the line of centres, so the hook stays within 0.15 mm of HOOK_R."""
    beta = lever_turn()
    P = LEVER_PIVOT
    n = math.dist(P, C_XY)
    cb = math.cos(beta / 2)
    rho = n * cb - math.sqrt((n * cb) ** 2 - n * n + HOOK_R ** 2)
    u = math.atan2(C_XY[1] - P[1], C_XY[0] - P[0])                 # pivot to C
    home = (P[0] + rho * math.cos(u + beta / 2), P[1] + rho * math.sin(u + beta / 2))   # above the line
    end = (P[0] + rho * math.cos(u - beta / 2), P[1] + rho * math.sin(u - beta / 2))
    return home, end, rho


def _psi(p):
    return math.degrees(math.atan2(p[1] - C_XY[1], p[0] - C_XY[0]))


def hook_face_root() -> float:
    """Root angle (degrees about C) of the drive face just ahead of the hook at rest: the face is
    HOOK_GAP ahead of the hook's drive point, measured at HOOK_R along the undercut face."""
    home, _, _ = hook_home()
    lean = C_UNDERCUT * 360.0 / C_TEETH * (HOOK_R - C_R_ROOT) / (C_R_TIP - C_R_ROOT)
    return _psi(home) + math.degrees(HOOK_GAP / HOOK_R) + lean


def tooth_phase() -> float:
    """C's tooth phase (degrees): drive face j has its root at phase + 3.6 j."""
    return hook_face_root() % (360.0 / C_TEETH)


def hook_travel() -> float:
    """Arc (mm, at HOOK_R) that the hook carries C in one pass of the counter pin."""
    home, end, _ = hook_home()
    return math.radians((_psi(end) - _psi(home)) % 360.0) * HOOK_R


def _ramp_points(delta, r_entry, r_exit, r_back, run_mm, lead_mm, dwell_mm, r_mid):
    """Ramp outline in the world: the pin arrives from larger angles (the ring turns clockwise),
    meets the face at r_entry and leaves it at r_exit; r_back is the body's far edge."""
    k = math.degrees(1.0 / r_mid)                  # degrees per mm along the ring at r_mid
    d_in = delta + (run_mm / 2 + lead_mm) * k
    d_face0 = delta + run_mm / 2 * k
    d_face1 = delta - run_mm / 2 * k
    d_out = d_face1 - dwell_mm * k
    pts = [(d_in, r_back), (d_in, r_entry), (d_face0, r_entry), (d_face1, r_exit), (d_out, r_exit), (d_out, r_back)]
    return [_world(d, r) for d, r in pts]


def ramp_outlines() -> dict:
    """World XY outlines: reset (inner lane, pushes the reset pin out) and set (outer lane, in)."""
    rr = pin_radii(True)["reset"], pin_radii(False)["reset"]      # reset pin: leap (in) .. common
    sr = pin_radii(True)["set"], pin_radii(False)["set"]          # set pin: leap .. common (out)
    reset = _ramp_points(RESET_DELTA, rr[0] - PIN_D / 2 - 0.5, rr[1] - PIN_D / 2 - 0.25, 158.6,
                         run_mm=7.6, lead_mm=1.2, dwell_mm=1.5, r_mid=162.5)
    set_ = _ramp_points(SET_DELTA, sr[1] + PIN_D / 2 + 0.5, sr[0] + PIN_D / 2 + 0.25, 174.2,
                        run_mm=7.6, lead_mm=1.2, dwell_mm=1.5, r_mid=169.5)
    return {"reset": reset, "set": set_}


PLUNGER_D = 3.0


def plunger_xy():
    return _world(SET_DELTA, 172.0)                # inside the set ramp's footprint, clear of its face


def bump_radius() -> float:
    p = plunger_xy()
    return math.dist(p, C_XY)


def read_angle() -> float:
    """C-centred angle (degrees) at which the plunger reads C's bump circle."""
    p = plunger_xy()
    return math.degrees(math.atan2(p[1] - C_XY[1], p[0] - C_XY[0]))


def position_angle(k: int, c_now: int) -> float:
    """World angle (about C) of C's position k while C stands at c_now; C turns 3.6° CCW a year."""
    return read_angle() - 3.6 * (k - c_now)


def bump_profile():
    """A leap bump's section along the bump circle: [(s, height)], s anticlockwise from the bump's
    centre (position k sits under the plunger when C stands at k)."""
    return [(BUMP_FOOT, 0.0), (BUMP_TOP0, STROKE), (BUMP_DROP, STROKE), (BUMP_DROP, 0.0)]


def _bump_height(x: float) -> float:
    """Height of a bump's top surface at x (mm along the bump circle from its centre)."""
    if x > BUMP_FOOT or x < BUMP_DROP:
        return 0.0
    if x <= BUMP_TOP0:
        return STROKE
    return STROKE * (BUMP_FOOT - x) / (BUMP_FOOT - BUMP_TOP0)


def plunger_lift(offset: float) -> float:
    """Lift of the plunger's ball tip (radius TIP_R) when the bump's centre is `offset` mm from the
    plunger along the bump circle (+: the bump is anticlockwise of the plunger): the ball rests on
    the highest point of the surface under it."""
    n = 400
    lift = 0.0
    for i in range(n + 1):
        u = -TIP_R + 2 * TIP_R * i / n                    # across the ball
        sag = TIP_R - math.sqrt(max(TIP_R * TIP_R - u * u, 0.0))
        lift = max(lift, _bump_height(u - offset) - sag)
    return lift


def pressure_angle() -> float:
    """Slope of the bump's ramp (degrees): the plunger's pressure angle when C steps onto a bump."""
    return math.degrees(math.atan2(STROKE, BUMP_FOOT - BUMP_TOP0))


def _bump_solid(theta_deg, r_mid, profile, z0, length=None, r0=None):
    """A bump: `profile` [(s, h)] across, extruded radially (r0 .. r0 + length about C's centre, or
    r_mid ± BUMP_HALF_W), turned to `theta_deg`, in C's own frame (centre at the origin)."""
    pts = [bd.Vector(0, x, z0 + h) for x, h in profile]
    face = bd.Face(bd.Wire.make_polygon(pts, close=True))
    if length is None:
        r0, length = r_mid - BUMP_HALF_W, 2 * BUMP_HALF_W
    sol = bd.extrude(face, amount=length, dir=(1, 0, 0)).moved(bd.Location((r0, 0, 0)))
    return sol.rotate(bd.Axis.Z, theta_deg)


def plunger_z(engaged: bool) -> dict:
    """The plunger's heights: ball-tip bottom, collar, and the spring's installed length."""
    tip = C_Z[1] + (STROKE if engaged else 0.0)
    collar0 = C_Z[1] + STROKE + 0.3 + (STROKE if engaged else 0.0)     # clears the bumps by 0.3 at rest
    return {"tip": tip, "collar": (collar0, collar0 + COLLAR_T), "spring": (collar0 + COLLAR_T, CEILING),
            "boss_bottom": C_Z[1] + STROKE + 0.3}


TAIL = 7.0                                         # the lever's spring tail, straight up from the pivot
STOP_XY = (LEVER_PIVOT[0] - 1.3 - 0.75, LEVER_PIVOT[1] + 5.0)   # the tail rests on it (left side)
ANCHOR_XY = (LEVER_PIVOT[0] - 13.0, LEVER_PIVOT[1] + TAIL)


def _square(c, s):
    return [(c[0] - s / 2, c[1] - s / 2), (c[0] + s / 2, c[1] - s / 2), (c[0] + s / 2, c[1] + s / 2), (c[0] - s / 2, c[1] + s / 2)]


def _face_psi(a_root, r):
    """Angle of a drive face at radius r: radial at the root, leaning back by the undercut at the tip."""
    return a_root - C_UNDERCUT * 360.0 / C_TEETH * (r - C_R_ROOT) / (C_R_TIP - C_R_ROOT)


def c_outline():
    """Wheel C's tooth outline (world XY). Each tooth: a drive face at phase + 3.6 j facing
    clockwise (the hook pulls it anticlockwise), then a gradual flank down to the next root."""
    pitch = 360.0 / C_TEETH
    ph = tooth_phase()
    pts = []
    for j in range(C_TEETH):
        a = ph + pitch * j
        pts += [_c_polar(a, C_R_ROOT), _c_polar(_face_psi(a, C_R_TIP), C_R_TIP)]
    return pts


def _arc(psi0, psi1, r, step=1.0):
    n = max(2, int(abs(psi1 - psi0) / step) + 1)
    return [_c_polar(psi0 + (psi1 - psi0) * k / (n - 1), r) for k in range(n)]


def hook_outline():
    """Hook and finger (world XY), at rest. The hook's front follows the drive face HOOK_GAP behind
    it; its back is a 45° ramp that rides up the next tooth's flank on the way back; the finger runs
    round C, outside its tips, to a root block ahead of the hook."""
    a = hook_face_root()
    front = lambda r: _face_psi(a, r) - math.degrees(HOOK_GAP / r)
    r_tip, r_in = C_R_ROOT + 0.3, C_R_TIP + 0.8
    r_out = r_in + FINGER_T
    back_tip = front(r_tip) - math.degrees(0.35 / r_tip)
    back_top = back_tip - math.degrees((r_out - r_tip) / r_tip)
    root0 = front(r_in) + FINGER_DEG
    pts = [_c_polar(front(r_tip), r_tip), _c_polar(front(r_in), r_in)]
    pts += _arc(front(r_in), root0, r_in)[1:]
    pts += [_c_polar(root0 + 3.0, r_in), _c_polar(root0 + 3.0, r_in + 3.2), _c_polar(root0, r_in + 3.2)]
    pts += _arc(root0, back_top, r_out)
    pts += [_c_polar(back_tip, r_tip)]
    return pts


def lever_outline():
    """The counting lever (world XY): hub, pin arm, spring tail, arm to the finger's root, and the
    hook on its finger. The finger is joined to the rest only at its root."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    P = LEVER_PIVOT
    pin = _world(0.0, LEVER_PIN_R)
    hook = Polygon(hook_outline())
    root_c = _c_polar(hook_face_root() + FINGER_DEG + 1.0, C_R_TIP + 0.8 + 2.2)
    body = unary_union([Polygon(_circle(P, 3.0)), Polygon(_bar(P, pin, 2.6)), Polygon(_circle(pin, 1.7)),
                        Polygon(_bar(P, (P[0], P[1] + TAIL), 2.6)), Polygon(_circle((P[0], P[1] + TAIL), 1.5)),
                        Polygon(_bar(P, root_c, 2.6)), Polygon(_bar(root_c, pin, 2.6)), hook])
    return list(body.exterior.coords)[:-1]


CLICK_ARM = 11.0                                   # click: nose to pivot
CLICK_WIRE_D, CLICK_WIRE_L, CLICK_WIRE_TILT = 0.5, 18.0, 7.0     # its wire spring (mm, mm, degrees)
SAT_WIRE_D, SAT_WIRE_L = 0.4, 10.0                 # the satellite's detent wire
SAT_IN = 6.6                                       # satellite centre this far inside the bump circle


def _wire(p0, p1, d, z, overrun=0.8):
    """A straight spring wire of diameter d from p0 (its clamped end) to just past p1 (its contact)."""
    L_ = math.dist(p0, p1) + overrun
    ang = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
    return parts.rod(d, L_).rotate(bd.Axis.Y, 90).rotate(bd.Axis.Z, ang).moved(bd.Location((p0[0], p0[1], z)))


def _click_frame():
    pitch = 360.0 / C_TEETH
    ph = tooth_phase()
    m = round((270.0 - ph) / pitch)
    a = ph + pitch * m                                      # the drive face nearest the bottom
    r_n = C_R_ROOT + 0.72
    psi_n = _face_psi(a, r_n) - math.degrees(0.42 / r_n)    # nose just behind it (face leans back)
    t = math.radians(psi_n)
    tang = (-math.sin(t), math.cos(t))                       # anticlockwise along C's rim (+x here)
    s0 = _c_polar(psi_n, C_R_TIP + 1.1)
    s1 = (s0[0] + CLICK_ARM * tang[0], s0[1] + CLICK_ARM * tang[1])
    return psi_n, s0, s1


def click_geometry():
    """The click's nose, arm end, pivot, and its wire spring (clamped end, contact on the arm)."""
    psi_n, s0, s1 = _click_frame()
    t = math.radians(psi_n)
    tang, out = (-math.sin(t), math.cos(t)), (math.cos(t), math.sin(t))
    q = (s0[0] + 1.5 * tang[0] + (0.7 + CLICK_WIRE_D / 2) * out[0],
         s0[1] + 1.5 * tang[1] + (0.7 + CLICK_WIRE_D / 2) * out[1])      # wire centre at the contact
    g = math.radians(CLICK_WIRE_TILT)
    u = (tang[0] * math.cos(g) + out[0] * math.sin(g), tang[1] * math.cos(g) + out[1] * math.sin(g))
    anchor = (q[0] + CLICK_WIRE_L * u[0], q[1] + CLICK_WIRE_L * u[1])
    return {"nose": _c_polar(psi_n, C_R_ROOT + 0.72), "arm0": s0, "pivot": s1, "contact": q, "anchor": anchor}


def click_outline():
    """The click (world XY): nose in the gap, a 1.4 mm arm outside C's tips, hub on its pivot."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    g = click_geometry()
    body = unary_union([Polygon(_circle(g["nose"], 0.35, 16)), Polygon(_bar(g["nose"], g["arm0"], 0.6)),
                        Polygon(_bar(g["arm0"], g["pivot"], 1.4)), Polygon(_circle(g["arm0"], 0.7, 12)),
                        Polygon(_circle(g["pivot"], 1.5, 20))])
    return list(body.exterior.coords)[:-1]


def satellite_geometry(c_now: int, satellite: int) -> dict:
    """Satellite centre (on C at position 0), its arm direction, and its detent wire (on C)."""
    rb = bump_radius()
    rs = rb - SAT_IN
    t0 = math.radians(position_angle(0, c_now))
    u_r, t_cw = (math.cos(t0), math.sin(t0)), (math.sin(t0), -math.cos(t0))
    sc = (C_XY[0] + rs * u_r[0], C_XY[1] + rs * u_r[1])
    contact = (sc[0] - (1.7 + SAT_WIRE_D / 2) * u_r[0], sc[1] - (1.7 + SAT_WIRE_D / 2) * u_r[1])
    anchor = (contact[0] + SAT_WIRE_L * t_cw[0], contact[1] + SAT_WIRE_L * t_cw[1])
    return {"rs": rs, "centre": sc, "arm_dir": t0 + math.radians(90.0 * satellite),
            "wire": (anchor, contact), "anchor": anchor}


# --- steel springs (Paul, PR #8: steel, not printed) ------------------------------------------------
E_WIRE = 206000.0      # N/mm², patented-drawn spring steel wire EN 10270-1 (EN 13906-1)
SECTOR_MASS = 0.0103   # kg: the Jan–Feb sector, 8268 mm³ of PLA at 1.24 g/cm³ (model volume)
MU = 0.3               # printed PLA/PETG on steel or on itself [E]
CLICK_F_NOSE0 = 0.30   # N at the click's nose, at rest: enough to settle C against its friction [E]
WIRE_RM_MIN = {}       # {d: minimum tensile strength, MPa} from the chosen wire's supplier (sourcing pending)


def _cantilever(d, L, delta):
    """Straight round wire, clamped at one end, tip deflected by delta: (force N, bending stress MPa)."""
    I = math.pi * d ** 4 / 64
    return 3 * E_WIRE * I * delta / L ** 3, 3 * E_WIRE * d * delta / (2 * L * L)


def wire_springs() -> dict:
    """Forces and stresses of the three wire springs, at rest and at their largest deflection."""
    out = {}
    # rocker detent: in a notch (preload), on the rim between notches (+ notch depth)
    d, L = DETENT_WIRE_D, DETENT_WIRE_L
    f0, _ = _cantilever(d, L, DETENT_PRELOAD)
    f1, s1 = _cantilever(d, L, DETENT_PRELOAD + DETENT_DEPTH)
    r_c = HUB_R - DETENT_DEPTH / 2
    hold = f0 * math.tan(math.radians(DETENT_FLANK) + math.atan(MU)) * r_c
    need = SECTOR_MASS * 9.81 * RHO                    # sector's weight on the tab, ring at 3 or 9 o'clock
    out["rocker_detent"] = dict(d=d, L=L, F_rest=f0, F_max=f1, stress_max=s1, hold_Nmm=hold, need_Nmm=need)
    # click: contact 1.5 mm from the arm's nose end; the nose lifts one tooth depth
    g = click_geometry()
    arm_nose = math.dist(g["pivot"], g["nose"])
    arm_c = math.dist(g["pivot"], g["arm0"]) - 1.5
    d, L = CLICK_WIRE_D, CLICK_WIRE_L
    f0_c = CLICK_F_NOSE0 * arm_nose / arm_c
    k = _cantilever(d, L, 1.0)[0]
    d0 = f0_c / k
    lift = (C_R_TIP - C_R_ROOT) * arm_c / arm_nose
    f1, s1 = _cantilever(d, L, d0 + lift)
    out["click"] = dict(d=d, L=L, preload=d0, F_rest=f0_c, F_max=f1, F_nose_max=f1 * arm_c / arm_nose,
                        stress_max=s1)
    # satellite detent: on a flat (preload), on a corner of the square hub
    d, L = SAT_WIRE_D, SAT_WIRE_L
    f0, _ = _cantilever(d, L, 0.4)
    f1, s1 = _cantilever(d, L, 0.4 + 1.7 * (math.sqrt(2) - 1))
    out["satellite_detent"] = dict(d=d, L=L, preload=0.4, F_rest=f0, F_max=f1, stress_max=s1)
    return out


def station_parts(c_now: int, satellite: int, engaged: bool) -> list:
    """[(name, solid, add() kwargs)] of the station's setter and counter parts, world frame."""
    out = []
    ro = ramp_outlines()
    out.append(("setter_reset_ramp", _prism(ro["reset"], CARRIER_FRONT, RAMP_TOP),
                dict(material="PETG", group="station", note="fixed: puts the sector in its common position")))
    z_top = RAMP_TOP if engaged else RAMP_TOP - STROKE
    px, py = plunger_xy()
    pz = plunger_z(engaged)
    ramp = _prism(ro["set"], z_top - 1.7, z_top)
    ramp -= parts.disc(2.2, 1.3, z0=z_top - 1.7 - 0.01).moved(bd.Location((px, py, 0)))       # socket
    out.append(("setter_set_ramp", ramp,
                dict(material="PETG", group="station", print_up=(0, 0, 1),
                     note="glued on the plunger's peg; the carrier window keeps it square")))
    # the plunger: ball tip on C, a collar the spring pushes towards C, a peg into the ramp
    tip = pz["tip"]
    plunger = bd.Sphere(TIP_R).moved(bd.Location((px, py, tip + TIP_R)))
    k45 = TIP_R * math.sqrt(0.5)
    cone_z0, cone_z1 = tip + TIP_R - k45, tip + TIP_R - k45 + (PLUNGER_D / 2 - k45)
    plunger += bd.Cone(k45, PLUNGER_D / 2, cone_z1 - cone_z0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(
        bd.Location((px, py, cone_z0)))
    plunger += parts.disc(PLUNGER_D, (z_top - 1.7) - cone_z1 + 0.01, z0=cone_z1 - 0.01).moved(bd.Location((px, py, 0)))
    plunger += parts.disc(2.0, 1.2, z0=z_top - 1.7).moved(bd.Location((px, py, 0)))            # peg
    plunger += parts.disc(COLLAR_D, COLLAR_T, z0=pz["collar"][0]).moved(bd.Location((px, py, 0)))
    out.append(("setter_plunger", plunger,
                dict(material="PETG", group="station", nozzle=0.2, print_up=(1, 0, 0),
                     note="follower: ball tip on wheel C; printed lying down")))
    sz = pz["spring"]
    out.append(("setter_plunger_spring",
                parts.disc(PLUNGER_SPRING["De"], sz[1] - sz[0], bore=PLUNGER_SPRING["Di"], z0=sz[0]).moved(
                    bd.Location((px, py, 0))),
                dict(material="steel", printed=False, group="station",
                     note="compression spring: from the pocket's ceiling, pushes the collar, so the tip, onto C")))
    # bracket behind the carrier: plunger guide and spring pocket (in a boss that hangs down to just
    # above the bumps), click pivot and spring anchor, and the satellite's stepping pin
    br = [(26.0, -177.0), (54.5, -177.0), (54.5, -157.0), (26.0, -157.0)]
    bracket = _prism(br, -23.0, -10.9)
    bracket += parts.disc(POCKET_D + 1.4, -23.0 - pz["boss_bottom"] + 0.01, z0=pz["boss_bottom"]).moved(
        bd.Location((px, py, 0)))
    bracket -= parts.disc(GUIDE_D, 20, z0=-30).moved(bd.Location((px, py, 0)))
    bracket -= parts.disc(POCKET_D, CEILING - pz["boss_bottom"] + 0.01, z0=pz["boss_bottom"] - 0.01).moved(
        bd.Location((px, py, 0)))
    clk = click_geometry()
    bracket += parts.disc(2.6, -23.0 - (C_Z[1] + 0.2) + 0.01, bore=1.5, z0=C_Z[1] + 0.2).moved(
        bd.Location((clk["pivot"][0], clk["pivot"][1], 0)))                                     # sleeve over the pin
    bracket += _prism(_square(clk["anchor"], 2.6), C_Z[0], -23.0 + 0.01)                          # wire anchor
    out.append(("station_bracket", bracket, dict(material="PETG", group="station",
                                                  note="screwed under the carrier's station extension")))
    # wheel C: a 100-tooth ratchet (radial drive faces, slightly undercut) with 24 leap bumps
    wheel = _prism(c_outline(), C_Z[0], C_Z[1]).moved(bd.Location((-C_XY[0], -C_XY[1], 0)))
    wheel -= parts.disc(3.3, 10, z0=C_Z[0] - 1)
    rb = bump_radius()
    for k in range(4, 100, 4):
        wheel += _bump_solid(position_angle(k, c_now), rb, bump_profile(), C_Z[1] - 0.01)
    sat_g = satellite_geometry(c_now, satellite)
    sc = sat_g["centre"]
    wheel += _prism(_square(sat_g["anchor"], 2.4), C_Z[1] - 0.01, C_Z[1] + STROKE).moved(
        bd.Location((-C_XY[0], -C_XY[1], 0)))                                                    # detent wire's boss
    wheel = wheel.moved(bd.Location((C_XY[0], C_XY[1], 0)))
    out.append(("wheel_C_100", wheel, dict(group="station", nozzle=0.2,
                                           note="year in the century: 100-tooth ratchet, 24 leap bumps")))
    out.append(("wheel_C_arbor", parts.rod(3.0, -15.0 - (C_Z[0] - 1.0)).moved(bd.Location((C_XY[0], C_XY[1], C_Z[0] - 1.0))),
                dict(material="steel", printed=False, group="station", note="stud pressed into the M2 front plate")))
    # Ungerer's satellite on C at position 0: a square hub (its detent), an arm that is a leap bump
    # when it points out (satellite == 0), and a 4-point star that the step pin turns
    arm_dir = sat_g["arm_dir"]
    hub = [(sc[0] + 1.7 * math.sqrt(2) * math.cos(arm_dir + math.pi / 4 + k * math.pi / 2),
            sc[1] + 1.7 * math.sqrt(2) * math.sin(arm_dir + math.pi / 4 + k * math.pi / 2)) for k in range(4)]
    sat = _prism(hub, C_Z[1], C_Z[1] + STROKE)
    arm = _bump_solid(math.degrees(arm_dir), 0.0, bump_profile(), C_Z[1], length=rb + BUMP_HALF_W - sat_g["rs"], r0=0.0)
    sat += arm.moved(bd.Location((sc[0], sc[1], 0)))
    star = []
    for k in range(8):
        t = arm_dir + math.pi / 4 * k
        r = 2.6 if k % 2 == 0 else 1.1
        star.append((sc[0] + r * math.cos(t), sc[1] + r * math.sin(t)))
    sat = sat + _prism(star, C_Z[1] + STROKE - 0.01, C_Z[1] + STROKE + 1.5)
    sat -= parts.disc(1.7, 10, z0=C_Z[0]).moved(bd.Location((sc[0], sc[1], 0)))
    out.append(("satellite_4", sat, dict(group="station", nozzle=0.2,
                                         note="Ungerer's satellite: ¼ turn per turn of C, one bump in 400 years")))
    w0, w1 = sat_g["wire"]
    out.append(("satellite_detent_spring", _wire(w0, w1, SAT_WIRE_D, C_Z[1] + STROKE / 2),
                dict(material="steel", printed=False, group="station",
                     note=f"Ø{SAT_WIRE_D} spring wire, glued in C's boss; presses a flat of the satellite's square hub")))
    out.append(("satellite_pin", parts.rod(1.5, C_Z[1] + STROKE + 1.5 - (C_Z[1] - 2.0)).moved(
        bd.Location((sc[0], sc[1], C_Z[1] - 2.0))), dict(material="steel", printed=False, group="station")))
    tq = math.radians(read_angle() - 6.0)
    sp = (C_XY[0] + (sat_g["rs"] - 1.6) * math.cos(tq), C_XY[1] + (sat_g["rs"] - 1.6) * math.sin(tq))
    out.append(("satellite_step_pin", parts.rod(1.5, -23.0 - (C_Z[1] + STROKE + 0.3)).moved(
        bd.Location((sp[0], sp[1], C_Z[1] + STROKE + 0.3))),
                dict(material="steel", printed=False, group="station",
                     note="fixed: turns the satellite a quarter turn as C goes from 97 to 0")))
    # counting lever (one flat PETG print in C's layer): the counter pin pushes its steel pin once a
    # year; its hook, on a flexible finger, pulls C one tooth; a spring brings it back to its stop
    lever = _prism(lever_outline(), *LEVER_Z)
    lever -= parts.disc(3.2, 10, z0=LEVER_Z[0] - 1).moved(bd.Location((LEVER_PIVOT[0], LEVER_PIVOT[1], 0)))
    pin_xy = _world(0.0, LEVER_PIN_R)
    lever -= parts.disc(LEVER_PIN_D, 10, z0=LEVER_Z[0] - 1).moved(bd.Location((pin_xy[0], pin_xy[1], 0)))
    tail = (LEVER_PIVOT[0], LEVER_PIVOT[1] + TAIL)
    lever -= parts.disc(1.0, 10, z0=LEVER_Z[0] - 1).moved(bd.Location((tail[0], tail[1], 0)))
    out.append(("counting_lever", lever, dict(material="PETG", group="station", nozzle=0.2,
                                              note="pin arm, hook on a flexible finger, spring tail; flat print")))
    out.append(("counting_lever_pin", parts.rod(LEVER_PIN_D, -6.6 - LEVER_Z[0]).moved(
        bd.Location((pin_xy[0], pin_xy[1], LEVER_Z[0]))),
                dict(material="steel", printed=False, group="station",
                     note="Ø1.5 pin pressed into the lever; reaches the counter pin's lane on the ring")))
    out.append(("counting_lever_stud", parts.rod(3.0, PLATE_BACK - (LEVER_Z[0] - 1.0)).moved(
        bd.Location((LEVER_PIVOT[0], LEVER_PIVOT[1], LEVER_Z[0] - 1.0))),
                dict(material="steel", printed=False, group="station", note="stud pressed into the M2 front plate")))
    for nm, xy, note in (("counting_lever_stop", STOP_XY, "the lever rests on it between years"),
                         ("counting_lever_spring_anchor", ANCHOR_XY, "holds the return spring's far hook")):
        out.append((nm, parts.rod(1.5, PLATE_BACK - (LEVER_Z[0] - 0.5)).moved(bd.Location((xy[0], xy[1], LEVER_Z[0] - 0.5))),
                    dict(material="steel", printed=False, group="station", note=note)))
    z_mid = (LEVER_Z[0] + LEVER_Z[1]) / 2
    x0, x1 = ANCHOR_XY[0] + 0.75, tail[0] - 2.2
    spring = parts.rod(2.5, x1 - x0).rotate(bd.Axis.Y, 90).moved(bd.Location((x0, tail[1], z_mid)))
    out.append(("counting_lever_spring", spring, dict(material="steel", printed=False, group="station",
                                                      note="extension spring OD 2.5, hooks not modelled")))
    # C's click: a printed click on a steel pivot pin, pressed into the tooth gap by a steel wire spring
    clk = click_geometry()
    click = _prism(click_outline(), *C_Z) - parts.disc(1.6, 10, z0=C_Z[0] - 1).moved(
        bd.Location((clk["pivot"][0], clk["pivot"][1], 0)))
    out.append(("wheel_C_click", click, dict(material="PETG", group="station", nozzle=0.2,
                                             note="click: lets C turn forward, stops it turning back, sets each yearly step")))
    out.append(("wheel_C_click_pivot", parts.rod(1.5, -23.0 - (C_Z[0] - 0.3)).moved(
        bd.Location((clk["pivot"][0], clk["pivot"][1], C_Z[0] - 0.3))),
                dict(material="steel", printed=False, group="station", note="Ø1.5 pin pressed into the bracket")))
    out.append(("wheel_C_click_spring", _wire(clk["anchor"], clk["contact"], CLICK_WIRE_D, (C_Z[0] + C_Z[1]) / 2),
                dict(material="steel", printed=False, group="station",
                     note=f"Ø{CLICK_WIRE_D} spring wire, glued in the bracket; presses the click towards C")))
    return out
