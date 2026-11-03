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
- the **counting lever** has a pin in the counter pin's lane (r 155–157.5). Once a year (1 October)
  the counter pin on the ring pushes it aside, and the lever's pawl steps **wheel C** (a 100-tooth
  ratchet) by one tooth. This replaces the 10-point star, which filled the band where the rocker must
  pass;
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
RAMP_TOP = -7.3                    # both ramps stay below the bars
CARRIER_FRONT = -8.8
HALF_DIV_AT_TAB = 0.5 * math.radians(DIV) * TAB_R
THETA0 = math.degrees(math.asin(HALF_DIV_AT_TAB / RHO))     # rocker swing either side of centre


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
    hub = Polygon(_circle((0, 0), 2.6))
    stem = Polygon(_bar((0, 0), (0, ARM_T), 2.0))
    cross = Polygon(_bar((-ARM_A, ARM_T), (ARM_A, ARM_T), 2.0))
    ends = [Polygon(_circle((sx * ARM_A, ARM_T), 1.0)) for sx in (-1, 1)]
    fork_bar = Polygon(_bar((0, 0), (-RHO + 1.0, 0), 2.4))
    fork_end = Polygon([(-RHO - 2.2, -2.1), (-RHO + 1.6, -2.1), (-RHO + 1.6, 2.1), (-RHO - 2.2, 2.1)])
    slot = Polygon([(-RHO - 1.3, -(TAB_PIN_D / 2 + 0.1)), (-RHO + 1.3, -(TAB_PIN_D / 2 + 0.1)),
                    (-RHO + 1.3, TAB_PIN_D / 2 + 0.1), (-RHO - 1.3, TAB_PIN_D / 2 + 0.1)])
    body = unary_union([hub, stem, cross, fork_bar, fork_end] + ends).difference(slot)
    body = body.difference(Polygon(_circle((0, 0), 1.1)))                 # Ø2.2 bore for the Ø2 pin
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
    # detent: a printed leaf from a block glued under the lip, its nose on the hub (two notches)
    anchor = _prism(_to_ring([(3.3, -7.4), (5.0, -7.4), (5.0, -4.0), (3.3, -4.0)], a_p), BAR_Z[0], -5.5)
    nose = (2.65 * math.cos(math.radians(-60.0)), 2.65 * math.sin(math.radians(-60.0)))     # on the hub
    leaf = _prism(_to_ring(_bar((3.4, -5.6), nose, 0.7), a_p), BAR_Z[0], BAR_Z[1])
    return {"setter_rocker": rocker, "setter_rocker_pivot": pivot, "setter_detent_spring": anchor + leaf}


def tab_pin(pointer: int, sector_start: int):
    """The sector's tab: a Ø2.2 pin at its division, through the floor slot into the rocker's fork."""
    a = (L.SECTOR_TAB + sector_start - L.SECTOR_COMMON_START - pointer) * DIV
    x, y = TAB_R * math.cos(math.radians(a)), TAB_R * math.sin(math.radians(a))
    return parts.disc(TAB_PIN_D, TAB_PIN_Z[1] - TAB_PIN_Z[0], z0=TAB_PIN_Z[0]).moved(bd.Location((x, y, 0)))


# --- the station --------------------------------------------------------------------------------
ST = -90.0                                        # station angle, world
RESET_DELTA = (L.RESET_OFFSET - L.STATION_OFFSET) * DIV     # degrees beyond the station: about 18.6
SET_DELTA = (L.SET_OFFSET - L.STATION_OFFSET) * DIV         # about 11.7
STROKE = 1.8                                       # set-ramp lift = leap bump height
C_XY = (34.0, -140.0)                              # wheel C's centre (its stud is in the M2 front plate)
C_Z = (-30.9, -27.9)
C_TEETH, C_R_TIP, C_R_ROOT = 100, 32.0, 30.5
LEVER_PIVOT = (-8.0, -146.0)
LEVER_Z = (-23.5, -21.5)
COUNTER_PIN_R = 156.25


def _world(delta_deg, r):
    t = math.radians(ST + delta_deg)
    return r * math.cos(t), r * math.sin(t)


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


def station_parts(c_now: int, satellite: int, engaged: bool) -> list:
    """[(name, solid, add() kwargs)] of the station's setter and counter parts, world frame."""
    out = []
    ro = ramp_outlines()
    out.append(("setter_reset_ramp", _prism(ro["reset"], CARRIER_FRONT, RAMP_TOP),
                dict(material="PETG", group="station", note="fixed: puts the sector in its common position")))
    z_top = RAMP_TOP if engaged else RAMP_TOP - STROKE
    ramp = _prism(ro["set"], z_top - 1.7, z_top)
    px, py = plunger_xy()
    z_c = C_Z[1] + (STROKE if engaged else 0.0)                      # tip on a bump, or on C's face
    plunger = parts.disc(PLUNGER_D, (z_top - 1.7) - z_c + 0.01, z0=z_c).moved(bd.Location((px, py, 0)))
    out.append(("setter_set_ramp", ramp + plunger,
                dict(material="PETG", group="station", print_up=(0, 0, 1),
                     note="set ramp and its plunger in one print; the plunger rides on wheel C")))
    out.append(("setter_plunger_spring", parts.disc(4.4, 5.0, bore=3.4, z0=-16.4).moved(bd.Location((px, py, 0))),
                dict(material="steel", printed=False, group="station", note="Ø4 compression spring, presses the plunger onto C")))
    # bracket behind the carrier: plunger guide and the satellite's stepping pin
    br = [(26.0, -175.5), (43.5, -175.5), (43.5, -157.0), (26.0, -157.0)]
    bracket = _prism(br, -23.0, -10.9) - parts.disc(PLUNGER_D + 0.4, 20, z0=-30).moved(bd.Location((px, py, 0)))
    bracket -= parts.disc(5.0, 7.0, z0=-17.0).moved(bd.Location((px, py, 0)))                  # spring seat
    out.append(("station_bracket", bracket, dict(material="PETG", group="station",
                                                  note="screwed under the carrier's station extension")))
    # wheel C: a 100-tooth ratchet with 24 leap bumps, the satellite at position 0
    pts = []
    for k in range(C_TEETH):
        a0 = 2 * math.pi * k / C_TEETH
        a1 = 2 * math.pi * (k + 0.8) / C_TEETH
        pts += [(C_R_ROOT * math.cos(a0), C_R_ROOT * math.sin(a0)), (C_R_TIP * math.cos(a1), C_R_TIP * math.sin(a1))]
    wheel = _prism(pts, C_Z[0], C_Z[1]) - parts.disc(3.3, 10, z0=C_Z[0] - 1)
    rb = bump_radius()
    for k in range(4, 100, 4):
        t = math.radians(position_angle(k, c_now))
        wheel += parts.disc(2.2, STROKE, z0=C_Z[1] - 0.01).moved(bd.Location((rb * math.cos(t), rb * math.sin(t), 0)))
    wheel = wheel.moved(bd.Location((C_XY[0], C_XY[1], 0)))
    out.append(("wheel_C_100", wheel, dict(group="station", nozzle=0.2,
                                           note="year in the century: 100-tooth ratchet, 24 leap bumps")))
    out.append(("wheel_C_arbor", parts.rod(3.0, -15.0 - (C_Z[0] - 1.0)).moved(bd.Location((C_XY[0], C_XY[1], C_Z[0] - 1.0))),
                dict(material="steel", printed=False, group="station", note="stud pressed into the M2 front plate")))
    # Ungerer's satellite on C at position 0: hub, one arm out to the bump circle when satellite == 0
    t0 = math.radians(position_angle(0, c_now))
    rs = rb - 5.6
    sc = (C_XY[0] + rs * math.cos(t0), C_XY[1] + rs * math.sin(t0))
    arm_dir = t0 + math.radians(90.0 * satellite)
    tip = (sc[0] + 5.6 * math.cos(arm_dir), sc[1] + 5.6 * math.sin(arm_dir))
    sat = _prism(_circle(sc, 2.0), C_Z[1], C_Z[1] + STROKE) + _prism(_bar(sc, tip, 2.2), C_Z[1], C_Z[1] + STROKE)
    star = []
    for k in range(8):
        t = arm_dir + math.pi / 4 * k
        r = 2.6 if k % 2 == 0 else 1.1
        star.append((sc[0] + r * math.cos(t), sc[1] + r * math.sin(t)))
    sat = sat + _prism(star, C_Z[1] + STROKE - 0.01, C_Z[1] + STROKE + 1.5)
    sat -= parts.disc(1.7, 10, z0=C_Z[0]).moved(bd.Location((sc[0], sc[1], 0)))
    out.append(("satellite_4", sat, dict(group="station", nozzle=0.2,
                                         note="Ungerer's satellite: ¼ turn per turn of C, one bump in 400 years")))
    out.append(("satellite_pin", parts.rod(1.5, C_Z[1] + STROKE + 1.5 - (C_Z[1] - 2.0)).moved(
        bd.Location((sc[0], sc[1], C_Z[1] - 2.0))), dict(material="steel", printed=False, group="station")))
    tq = math.radians(read_angle() - 6.0)
    sp = (C_XY[0] + (rs - 1.6) * math.cos(tq), C_XY[1] + (rs - 1.6) * math.sin(tq))
    out.append(("satellite_step_pin", parts.rod(1.5, -23.0 - (C_Z[1] + STROKE + 0.3)).moved(
        bd.Location((sp[0], sp[1], C_Z[1] + STROKE + 0.3))),
                dict(material="steel", printed=False, group="station",
                     note="fixed: turns the satellite a quarter turn as C goes from 97 to 0")))
    # counting lever: pin in the counter pin's lane, pawl on C's rim
    pin_xy = _world(0.0, COUNTER_PIN_R)
    d = (LEVER_PIVOT[0] - C_XY[0], LEVER_PIVOT[1] - C_XY[1])
    n = math.hypot(*d)
    pawl_xy = (C_XY[0] + (C_R_ROOT + 0.9) * d[0] / n, C_XY[1] + (C_R_ROOT + 0.9) * d[1] / n)
    lever = (_prism(_circle(LEVER_PIVOT, 3.0), *LEVER_Z) + _prism(_bar(LEVER_PIVOT, pin_xy, 2.6), *LEVER_Z) +
             _prism(_bar(LEVER_PIVOT, pawl_xy, 2.6), *LEVER_Z))
    lever -= parts.disc(3.2, 10, z0=LEVER_Z[0] - 1).moved(bd.Location((LEVER_PIVOT[0], LEVER_PIVOT[1], 0)))
    lever += parts.disc(1.6, -6.6 - LEVER_Z[1], z0=LEVER_Z[1] - 0.01).moved(bd.Location((pin_xy[0], pin_xy[1], 0)))
    lever += _prism(_circle(pawl_xy, 0.9), C_Z[0] + 0.3, LEVER_Z[0] + 0.01)
    out.append(("counting_lever", lever, dict(group="station",
                                              note="the counter pin pushes its pin once a year; its pawl steps C one tooth")))
    out.append(("counting_lever_stud", parts.rod(3.0, -15.0 - (LEVER_Z[0] - 1.0)).moved(
        bd.Location((LEVER_PIVOT[0], LEVER_PIVOT[1], LEVER_Z[0] - 1.0))),
                dict(material="steel", printed=False, group="station", note="stud pressed into the M2 front plate")))
    # C's jumper: a printed leaf from the bracket, its nose in a tooth gap at C's bottom
    jx, jy = C_XY[0], C_XY[1] - (C_R_ROOT + 0.8)
    jumper = (_prism(_circle((jx, jy), 0.8), *C_Z) + _prism(_bar((jx, jy), (jx + 6.0, jy - 3.5), 0.9), *C_Z) +
              _prism([(jx + 5.0, jy - 5.0), (jx + 8.0, jy - 5.0), (jx + 8.0, jy - 2.0), (jx + 5.0, jy - 2.0)], C_Z[0], -23.0))
    out.append(("wheel_C_jumper", jumper, dict(material="PETG", group="station",
                                               note="detent: holds C between its yearly steps")))
    return out
