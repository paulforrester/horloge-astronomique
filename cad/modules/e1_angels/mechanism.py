"""E1, the two genies: detail design, part 1 (docs/e1-design.md §16).

Settled at the concept gate (PR #18, Paul, 7–8 Nov 2026):
- one forward-only gearmotor, in the bell genie's tower (left); a count wheel (1:20) makes the hour's ten strokes
  and then ten silent turns, during which a mutilated gear turns the cross shaft half a turn (§15);
- the bell genie's arm, holding the striker, moves and strikes a real bell in the genie's hand: a snail cocks it
  through a follower lever and a wire, a spring flicks it (§4.2, §12);
- a rigid Ø5 cross shaft behind M1 (§13.2) to the hourglass genie's tower (right): a crank, a Scotch yoke, a
  rack and a pinion turn the forearms and the glass half a turn in the facade plane, alternately (§4.3, §12).

The model shows the rest state at home: the arm cocked (low), the count wheel at 0, the crank at its lower dead
centre, the glass upright.

Frame: M1's (docs/m1-design.md §9.2): origin at the dial's centre on its face, +X right, +Y up, +Z towards the
viewer. The bell tower's arbors run along X; parts on them are built about local +Z and turned onto X so that
local (x, y, z) -> global (y, z, x) (``onx``).
Run:  python -m cad.modules.e1_angels.mechanism [out_dir]
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import build123d as bd

from cad.lib import parts
from cad.lib.assembly import BED_DUAL, BED_SINGLE, Assembly, write_dae
from cad.lib.gears import centre_distance, mesh_rotation, rack, spur_gear
from cad.lib.hardware import BEARINGS
from cad.modules.e1_angels import program as P

FACE = 3.0
FIG_H = 78.0                                   # head to soles (Paul, PR #18)
SEAT_Y = {"bell": 14.0, "glass": 20.0}         # [E] docs/e1-design.md §2
FIG_X = {"bell": -85.0, "glass": 88.0}
SHOULDER = (-101.0, 47.0)                      # the sceptre arm's pivot (x, y) [E]
BELL = dict(x=-84.0, y=47.5, z=19.0, d=20.0, h=15.0)   # Ø20 bell, mouth down [E]; E1's tone: §12 item 4
GLASS = dict(x=83.0, y=59.0, z=16.0, h=19.0, d=9.0)    # bought miniature hourglass [E]
STRIKE_GAP = 0.5                               # the striker's tip stops this far from the bell (banking)
WIRE_D = 0.5
GEARMOTOR = dict(w=12.0, d=10.0, length=34.5, shaft_d=3.0, shaft_l=9.0)   # [E] ⚠ as E2's: check the chosen motor
SWITCH = dict(l=12.8, w=5.8, h=6.5)            # [E] subminiature roller-lever microswitch

# --- planes along X in the bell tower (x0, x1), inner to outer ---------------------------------------------------
X_INNER = (-91.0, -88.0)
X_LEVER = (-94.5, -92.0)
X_SNAIL = (-98.5, -95.5)                       # the snail on B and the silencing cam on W
X_P3 = (-102.5, -99.5)                         # the mutilated sector (W) and the cross shaft's 36 (C)
X_P2 = (-106.5, -103.5)                        # W's 60 and I's 12
X_P1 = (-110.5, -107.5)                        # I's 48 and B's 12
X_LOCK = (-114.5, -111.5)                      # B's lock cam, W's home cam, C's detent disc
X_DRIVE = (-121.5, -118.5)                     # the 20/20 pair: the gearmotor's pinion and the bell shaft's gear
X_OUTER = (-126.0, -123.0)
MOTOR_FACE = -117.5                            # the gearmotor's face; its body runs +x above the plates to -83
TOWER_YZ = (-76.0, 4.0, -120.0, -22.0)         # the bell tower's plates: y0, y1, z0, z1

# --- the glass tower --------------------------------------------------------------------------------------------
GX_BOSS = (88.0, 94.0)                         # the cross shaft's two bearings
GX_CRANK = (95.5, 98.5)
GX_PIN = (98.5, 106.0)
GX_YOKE = (99.3, 108.5)
GX_ROD = 111.0                                 # the slider rod's axis (x); z = C's z
GX_OUTER = (116.0, 119.0)
G_PINION_Z = (-109.0, -105.0)
G_REAR_BRG_Z = -101.0                          # MR63ZZ, its rear face
G_FRONT_BRG_Z = -24.0
COUPLING = (-87.0, -79.0, 79.0, 87.0)          # the cross shaft's two dog couplings (x ranges)


def onx(shape, x0):
    """A shape built about local +Z from z = 0, laid along +X from x0: local (x, y, z) -> global (y, z, x) [x0 +]."""
    return shape.rotate(bd.Axis((0, 0, 0), (1, 1, 1)), 120).moved(bd.Location((x0, 0, 0)))


def at_yz(local_shape, yz, x0):
    """A local part about +Z (z from 0), centred at (y, z) in the tower's plane, its local z from x0 along +X."""
    return onx(local_shape.moved(bd.Location((yz[0], yz[1], 0))), x0)


def zdisc(d, z0, z1, bore=0.0):
    return parts.disc(d, z1 - z0, bore=bore, z0=z0)


def box(sx, sy, sz, c=(0, 0, 0)):
    return bd.Box(sx, sy, sz).moved(bd.Location(c))


def span(xr):
    return xr[1] - xr[0]


def gear_local(g, t, bore, rot=0.0, fit="press"):
    return spur_gear(g, t).rotate(bd.Axis.Z, rot) - zdisc(bore + getattr(parts.FITS, fit), -1, t + 1)


def profile(radius_of_angle, t, bore, samples=720):
    pts = [bd.Vector(radius_of_angle(360.0 * i / samples) * math.cos(2 * math.pi * i / samples),
                     radius_of_angle(360.0 * i / samples) * math.sin(2 * math.pi * i / samples), 0)
           for i in range(samples)]
    part = bd.extrude(bd.Face(bd.Wire.make_polygon(pts, close=True)), amount=t, dir=(0, 0, 1))
    return part - zdisc(bore, -1, t + 1) if bore else part


def rod_between(p, q, d):
    """A round rod of diameter d from point p to point q."""
    v = bd.Vector(*q) - bd.Vector(*p)
    cyl = bd.Cylinder(d / 2, v.length, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    z = bd.Vector(0, 0, 1)
    ax = z.cross(v)
    ang = math.degrees(math.acos(max(-1.0, min(1.0, z.dot(v) / v.length))))
    if ax.length > 1e-9:
        cyl = cyl.rotate(bd.Axis((0, 0, 0), (ax.X, ax.Y, ax.Z)), ang)
    return cyl.moved(bd.Location(p))


def bearing_x(name, yz, x0):
    return at_yz(parts.bearing(name), yz, x0)


def mutilated(g, t, bore, a0, a1):
    """The sector: gear g keeping only its teeth whose centre lies between local angles a0 and a1 (deg, a0 < a1);
    elsewhere cut to the root circle."""
    pitch = 360.0 / g.teeth
    lo, hi = a0 - pitch / 2, a1 + pitch / 2
    n = 72
    pts = [bd.Vector(0, 0, 0)] + [bd.Vector(2 * g.tip_radius * math.cos(math.radians(lo + (hi - lo) * k / n)),
                                            2 * g.tip_radius * math.sin(math.radians(lo + (hi - lo) * k / n)), 0)
                                  for k in range(n + 1)]
    fan = bd.extrude(bd.Face(bd.Wire.make_polygon(pts, close=True)), amount=t + 2, dir=(0, 0, 1)).moved(
        bd.Location((0, 0, -1)))
    part = (spur_gear(g, t) & fan) + zdisc(2 * g.root_radius - 0.1, 0, t)    # 0.05 under the root: one clean solid
    return part - zdisc(bore + parts.FITS.press, -1, t + 1)


def _figure(kind):
    """A placeholder seated genie, FIG_H head to soles: legs over the plinth's front, torso, head, wings."""
    x, seat = FIG_X[kind], SEAT_Y[kind]
    sole = seat - 16.0
    torso = bd.Cylinder(10.0, 40.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(
        bd.Axis.X, -90).moved(bd.Location((x, seat, -2.0)))
    head = bd.Sphere(9.0).moved(bd.Location((x, sole + FIG_H - 9.0, -2.0)))
    thighs = box(18.0, 7.0, 20.0, (x, seat + 3.5, 12.0))
    shins = box(16.0, 16.0, 6.0, (x, sole + 8.0, 25.0))
    wings = [box(26.0, 22.0, 2.0, (x + s * 22.0, seat + 36.0, -10.0)).rotate(
        bd.Axis((x, seat + 30, 0), (0, 0, 1)), s * 25.0) for s in (-1, 1)]
    return torso + head + thighs + shins + wings[0] + wings[1]


def build():
    a = Assembly("e1_angels")
    g = P.gears()
    ax = P.axes()
    B, I, W, C = ax["B"], ax["I"], ax["W"], ax["C"]
    b85, b63 = BEARINGS["MR85ZZ"], BEARINGS["MR63ZZ"]
    data = {"axes": {k: [round(v, 2) for v in ax[k]] for k in "BIWC"}}

    # ------------------------------------------------------------------ the bell tower's plates
    y0, y1, z0, z1 = TOWER_YZ
    for nm, xr in (("tower_inner_plate", X_INNER), ("tower_outer_plate", X_OUTER)):
        pl = onx(parts.plate([(y0, z0), (y1, z0), (y1, z1), (y0, z1)], span(xr)), xr[0])
        for yz in (B, I, W, C):
            pl -= at_yz(zdisc(b85.od + parts.FITS.bearing_seat, -1, span(xr) + 1), yz, xr[0])
        if nm == "tower_inner_plate":
            pl -= onx(box(10.0, 30.0, span(X_INNER) + 2, (0.0, -26.0, span(X_INNER) / 2)), X_INNER[0])  # wire slot
            pl -= at_yz(zdisc(3.0 + parts.FITS.press, -1, span(xr) + 1), P.PF, xr[0])
        else:
            for yz in ((-70.0, -114.0), (-70.0, -28.0)):            # M5 tabs to the works' internal frame
                pl -= at_yz(zdisc(5.5, -1, span(xr) + 1), yz, xr[0])
        a.add(nm, pl, material="PETG", group="tower", print_up=(1, 0, 0) if nm == "tower_inner_plate" else (-1, 0, 0),
              note="carries the bell shaft, the intermediate, the count wheel and the cross shaft (MR85ZZ seats)")
    spacers = []
    for yz in ((2.0, -32.0), (-72.0, -26.0), (-30.0, -117.0), (2.0, -110.0)):
        sp = at_yz(zdisc(7.0, 0, X_INNER[0] - X_OUTER[1], bore=3.4), yz, X_OUTER[1])
        spacers.append(sp)
    a.add("tower_pillars", spacers[0] + spacers[1] + spacers[2] + spacers[3], material="PETG", group="tower",
          note="four pillars between the plates (M3 through)")
    for nm in ("tower_inner_plate", "tower_outer_plate"):
        a.allow("tower_pillars", nm)

    # ------------------------------------------------------------------ arbors and bearings
    arbors = {"bell_shaft": (B, X_OUTER[0], X_INNER[1]), "intermediate_arbor": (I, X_OUTER[0], X_INNER[1]),
              "count_arbor": (W, X_OUTER[0], X_INNER[1]), "cross_stub_left": (C, X_OUTER[0], COUPLING[0] + 4.0)}
    for nm, (yz, xa, xb) in arbors.items():
        a.add(nm, at_yz(parts.rod(5.0, xb - xa), yz, xa), material="steel", printed=False, group="trains",
              note="Ø5 ground rod")
        for side, xr in (("inner", X_INNER), ("outer", X_OUTER)):
            bn = f"{nm}_bearing_{side}"
            a.add(bn, bearing_x("MR85ZZ", yz, xr[0] + 0.25), material="bearing", printed=False, group="trains",
                  note="MR85ZZ")
            a.allow(bn, nm); a.allow(bn, f"tower_{side}_plate")
    # ------------------------------------------------------------------ the gears (rest: home, u = 0, c = 0)
    def place(nm, shape, yz, xr, note, **kw):
        a.add(nm, at_yz(shape, yz, xr[0]), group=kw.pop("group", "trains"), note=note, **kw)

    th_bi = math.degrees(math.atan2(I[1] - B[1], I[0] - B[0]))
    th_iw = math.degrees(math.atan2(W[1] - I[1], W[0] - I[0]))
    rot_i48 = mesh_rotation(g["b12"], g["i48"], th_bi)
    rot_w60 = mesh_rotation(g["i12"], g["w60"], th_iw)
    place("bell_pinion_12", gear_local(g["b12"], span(X_P1), 5.0), B, X_P1, "pressed on the bell shaft")
    dz2 = X_P2[0] - X_P1[0]
    comp = gear_local(g["i48"], span(X_P1), 5.0, rot_i48) + zdisc(10.0, span(X_P1) - 0.01, dz2 + 0.01, bore=5.05)
    comp += gear_local(g["i12"], span(X_P2), 5.0).moved(bd.Location((0, 0, dz2)))
    place("intermediate_48_12", comp, I, X_P1, "48 + 12 in one print, pressed on the intermediate arbor")
    place("count_wheel_60", gear_local(g["w60"], span(X_P2), 5.0, rot_w60) + zdisc(12.0, span(X_P2), X_P3[0] - X_P2[0],
                                                                                    bore=5.0 + parts.FITS.press),
          W, X_P2, "the count wheel: one turn per hour's work (1:20)")
    pitch_s = 360.0 / g["sector"].teeth
    first = math.ceil((P.THETA_WC + 2.0) / pitch_s) * pitch_s          # the first lattice tooth after c = 358°
    sector = mutilated(g["sector"], span(X_P3), 5.0, first, first + (P.SECTOR_TEETH - 1) * pitch_s)
    data["sector"] = {"first_tooth_deg": first, "teeth": P.SECTOR_TEETH}
    place("sector_36", sector, W, X_P3, f"mutilated gear: {P.SECTOR_TEETH} teeth over 180° turn the cross shaft "
          "half a turn while the count wheel makes its silent half", print_up=(1, 0, 0))
    rot_c = mesh_rotation(g["sector"], g["c36"], P.THETA_WC, 0.0)
    place("cross_gear_36", gear_local(g["c36"], span(X_P3), 5.0, rot_c), C, X_P3, "pressed on the cross shaft's stub")
    for x_, y_ in (("bell_pinion_12", "bell_shaft"), ("intermediate_48_12", "intermediate_arbor"),
                   ("count_wheel_60", "count_arbor"), ("sector_36", "count_arbor"), ("cross_gear_36", "cross_stub_left")):
        a.allow(x_, y_)
    a.allow("count_wheel_60", "sector_36")
    data["mesh"] = {"BI": round(math.dist(B, I), 3), "IW": round(math.dist(I, W), 3), "WC": round(math.dist(W, C), 3)}

    # ------------------------------------------------------------------ the snail, the silencing cam, the lever
    # The snail turns with u (+ about +X); its material at local angle a meets the roller (direction 180°) at u:
    def snail_local(a_):
        return P.snail_radius(180.0 - a_)
    place("snail", profile(snail_local, span(X_SNAIL), 5.0 + parts.FITS.press), B, X_SNAIL,
          "one stroke per turn: rest in the high dwell, the drop 30° on, the rise 60–280° (pressure angle ≤ 9°)")

    def sil_local(a_):                                  # the pin is straight above W (direction 0°): c = -a
        return P.silencing_cam_profile(a_)
    place("silencing_cam", profile(sil_local, span(X_SNAIL), 5.0 + parts.FITS.press), W, X_SNAIL,
          "holds the follower lever off the snail for the ten silent turns (count wheel 180–360°)")
    a.allow("snail", "bell_shaft"); a.allow("silencing_cam", "count_arbor")
    # the lever: straight along z at y = PF_y (cocked); bar in X_LEVER, roller and pin reach into X_SNAIL
    pf = P.PF
    bar = box(span(X_LEVER), 4.0, P.A_TIP + P.A_PIN + 6.0,
              (sum(X_LEVER) / 2, pf[0] - 2.5, pf[1] + (P.A_TIP - P.A_PIN) / 2))
    bar += at_yz(zdisc(6.0, 0, span(X_LEVER)), pf, X_LEVER[0])
    bar -= at_yz(zdisc(3.0 + parts.FITS.running, -1, span(X_LEVER) + 1), pf, X_LEVER[0])
    bar -= at_yz(zdisc(1.0, -1, span(X_LEVER) + 1), (pf[0], pf[1] + P.A_TIP), X_LEVER[0])     # the wire's hole
    roller_yz, pin_yz = (pf[0], pf[1] + P.A_ROLLER), (pf[0], pf[1] - P.A_PIN)
    axle = at_yz(zdisc(2.0, 0, X_LEVER[0] - X_SNAIL[0]), roller_yz, X_SNAIL[0])
    pin = at_yz(zdisc(P.PIN_D, 0, X_LEVER[0] - X_SNAIL[0]), pin_yz, X_SNAIL[0])
    a.add("follower_lever", bar + axle + pin, group="lever", print_up=(1, 0, 0),
          note="pivots on a Ø3 pin in the inner plate: roller on the snail, pin on the silencing cam, wire at the tip")
    a.add("follower_roller", at_yz(zdisc(P.ROLLER_D, 0, span(X_SNAIL), bore=2.2), roller_yz, X_SNAIL[0]),
          group="lever", note="printed sleeve, free on the lever's axle")
    a.add("lever_pivot_pin", at_yz(parts.rod(3.0, X_INNER[1] - X_LEVER[0] + 0.5), pf, X_LEVER[0] - 0.5),
          material="steel", printed=False, group="lever", note="Ø3 × 9 steel pin, pressed in the inner plate")
    for x_, y_ in (("follower_lever", "follower_roller"), ("follower_lever", "lever_pivot_pin"),
                   ("lever_pivot_pin", "tower_inner_plate"), ("follower_roller", "snail")):
        a.allow(x_, y_)

    # ------------------------------------------------------------------ lock, home and detent cams; switches
    def lock_local(a_):                                 # the switch reads at direction 180° (-y): u = 180 - a
        u = (180.0 - a_) % 360.0
        return 8.5 if (u < 6.0 or u > 354.0) else 10.0
    place("bell_lock_cam", profile(lock_local, span(X_LOCK), 5.0 + parts.FITS.press), B, X_LOCK,
          "one notch: the bell lock (the switch opens at rest)")

    def home_local(a_):                                 # read at direction 90°: c = 90 - a
        c = (90.0 - a_) % 360.0
        lo, hi = P.HOME_NOTCH
        return 10.5 if (c >= lo or c < hi - 360.0) else 12.0
    place("home_cam", profile(home_local, span(X_LOCK), 5.0 + parts.FITS.press), W, X_LOCK,
          "one notch 18° wide: only the twentieth turn's lock falls in it (home)")

    def detent_local(a_):                               # two V notches at the crank's dead centres
        d = min(abs(((a_ - k) + 180.0) % 360.0 - 180.0) for k in (0.0, 180.0))
        return 7.5 + min(d, 8.0) / 8.0 * 1.5
    place("detent_disc", profile(detent_local, span(X_LOCK), 5.0 + parts.FITS.press), C, X_LOCK,
          "two notches 180° apart: holds the cross shaft at a dead centre between hours")
    for x_, y_ in (("bell_lock_cam", "bell_shaft"), ("home_cam", "count_arbor"), ("detent_disc", "cross_stub_left")):
        a.allow(x_, y_)
    sw_x = (X_DRIVE[1] + 0.2, X_DRIVE[1] + 0.2 + SWITCH["w"])
    for nm, yz in (("bell_lock_switch", (B[0] - 10.0 - 1.0 - SWITCH["h"] / 2, B[1])),
                   ("home_switch", (W[0] + 2.0, W[1] + 12.0 + 1.0 + SWITCH["l"] / 2))):
        body = onx(box(SWITCH["h"], SWITCH["l"], span(sw_x), (yz[0], yz[1], span(sw_x) / 2)), sw_x[0])
        a.add(nm, body, material="black", printed=False, group="tower",
              note="subminiature roller-lever microswitch [E]; screwed to the outer plate (2 × M2)")
        a.allow(nm, "tower_outer_plate")
    data["switches"] = "bell lock on B; home on W"
    a.add("detent_spring", onx(box(2.0, 1.2, span(X_LOCK), (C[0] + 9.6, C[1] - 6.0, span(X_LOCK) / 2)), X_LOCK[0]),
          material="steel", printed=False, group="tower", note="leaf spring with a nose in the detent's notch [E]")

    # ------------------------------------------------------------------ the gearmotor, folded inside (Paul, PR #23)
    # It lies along X above the plates' top edge, behind the plinth, and drives the bell shaft through a 20/20 pair
    # in its own plane between the lock plane and the outer plate. To change it, undo the saddle's screws and lift
    # the saddle, the motor and its pinion straight up.
    gm, Mx = GEARMOTOR, ax["M"]
    place("bell_drive_gear_20", gear_local(g["drive"], span(X_DRIVE), 5.0), B, X_DRIVE, "pressed on the bell shaft")
    rot_m = mesh_rotation(g["drive"], g["drive"], P.DRIVE_DIR)
    a.add("motor_pinion_20", at_yz(gear_local(g["drive"], span(X_DRIVE), gm["shaft_d"], rot_m), Mx, X_DRIVE[0]),
          group="motor", note="pressed on the gearmotor's Ø3 D-shaft; 1:1 with the bell shaft")
    motor = onx(box(gm["d"], gm["w"], gm["length"], (Mx[0], Mx[1], gm["length"] / 2)), MOTOR_FACE)
    motor += at_yz(parts.rod(gm["shaft_d"], gm["shaft_l"]), Mx, MOTOR_FACE - gm["shaft_l"])
    a.add("gearmotor", motor, material="black", printed=False, group="motor",
          note="micro metal gearmotor ≈ 200 rpm under load [E] ⚠ choose; forward only; inside the tower")
    y_top = TOWER_YZ[1]
    base = onx(box(4.0, 16.0, X_INNER[1] - X_OUTER[0], (y_top + 2.0, Mx[1], (X_INNER[1] - X_OUTER[0]) / 2)), X_OUTER[0])
    base -= at_yz(zdisc(2 * (g["drive"].tip_radius + 1.0), -0.5, span(X_DRIVE) + 1.0), Mx, X_DRIVE[0])
    base -= at_yz(zdisc(2 * (g["i48"].tip_radius + 1.0), -0.5, span(X_P1) + 1.0), I, X_P1[0])     # the 48's relief
    cheek_len = X_INNER[1] + 4.0 - MOTOR_FACE
    for dz in (-(gm["w"] / 2 + 1.2), gm["w"] / 2 + 1.2):
        base += onx(box(gm["d"] + 1.0, 2.0, cheek_len, (Mx[0] + 0.5, Mx[1] + dz, cheek_len / 2)), MOTOR_FACE)
    a.add("gearmotor_bracket", base, material="PETG", group="motor", print_up=(0, -1, 0),
          note="a saddle on the plates' top edges (4 × M2): its cheeks hold the gearmotor; lift it out upwards")
    for x_, y_ in (("gearmotor_bracket", "gearmotor"), ("gearmotor_bracket", "tower_inner_plate"),
                   ("gearmotor_bracket", "tower_outer_plate"), ("motor_pinion_20", "gearmotor"),
                   ("bell_drive_gear_20", "bell_shaft"), ("motor_pinion_20", "bell_drive_gear_20"),
                   ("bell_shaft", "bell_shaft_bearing_outer")):
        a.allow(x_, y_)
    data["drive"] = {"pair": f"{P.Z_DRIVE}/{P.Z_DRIVE}", "motor_axis_yz": [round(v, 2) for v in Mx]}

    # ------------------------------------------------------------------ plinths and figures
    plinths = {"bell": (-116.0, -70.0, TOWER_YZ[1]), "glass": (72.0, GX_OUTER[0], 8.0)}
    for kind, (xa, xb, yb) in plinths.items():
        pl = box(xb - xa, SEAT_Y[kind] - yb, 52.0, ((xa + xb) / 2, (SEAT_Y[kind] + yb) / 2, -4.0))
        if kind == "bell":
            pl -= box(6.0, 30.0, 6.0, (-89.5, 10.0, -25.5))         # the wire's slot
        a.add(f"plinth_{kind}", pl, material="PLA", group="figures", note="printed, painted: the ledge the genie "
              "sits on; it belongs to E1, the wooden cornice fits round it with a gap (D12 R5)")
    a.allow("plinth_bell", "tower_inner_plate"); a.allow("plinth_bell", "tower_outer_plate")
    a.allow("plinth_bell", "tower_pillars")
    for kind in ("bell", "glass"):
        a.add(f"figure_{kind}", _figure(kind), material="ghost", printed=False, group="figures",
              note=f"placeholder: {FIG_H:.0f} mm head to soles (Paul, PR #18); the sculpted figure comes later")
        a.allow(f"figure_{kind}", f"plinth_{kind}")

    # ------------------------------------------------------------------ the sceptre arm (front) and its drive (back)
    sx, sy = SHOULDER
    brk = box(10.0, 52.0 - SEAT_Y["bell"], 8.0, (sx, (52.0 + SEAT_Y["bell"]) / 2, -18.0))
    brk -= zdisc(BEARINGS["MR63ZZ"].od + parts.FITS.bearing_seat, -23.0, -13.0).moved(bd.Location((sx, sy, 0)))
    brk += box(18.0, 4.0, 5.0, (sx + 9.0, 60.0, -24.5)) + box(4.0, 8.0, 5.0, (sx + 16.0, 56.0, -24.5))
    a.add("shoulder_bracket", brk, material="PETG", group="sceptre", note="on the plinth: the shoulder arbor's two "
          "MR63ZZ, the spring's post and the banking stop")
    a.allow("shoulder_bracket", "plinth_bell")
    for nm, zb in (("shoulder_bearing_front", -16.5), ("shoulder_bearing_rear", -22.0)):
        a.add(nm, parts.bearing("MR63ZZ", zb).moved(bd.Location((sx, sy, 0))), material="bearing", printed=False,
              group="sceptre", note="MR63ZZ")
        a.allow(nm, "shoulder_bracket")
    a.add("shoulder_arbor", parts.rod(3.0, BELL["z"] + 2.0 + 27.5, -27.5).moved(bd.Location((sx, sy, 0))),
          material="steel", printed=False, group="sceptre", note="Ø3 ground rod, front to back through the shoulder")
    for nm in ("shoulder_bearing_front", "shoulder_bearing_rear", "shoulder_bracket"):
        a.allow("shoulder_arbor", nm)
    a.allow("shoulder_arbor", "figure_bell")
    # the shoulder lever behind the bracket: pointing +x, pulled down by the wire to cock (CW)
    ls = P.tip_travel() / math.radians(P.COCK_DEG)
    lev = box(ls + 4.0, 4.0, 2.5, (sx + ls / 2, sy, -25.75)) + zdisc(7.0, -27.0, -24.5).moved(bd.Location((sx, sy, 0)))
    lev -= zdisc(3.0 + parts.FITS.press, -28.0, -23.0).moved(bd.Location((sx, sy, 0)))
    a.add("shoulder_lever", lev, group="sceptre", note=f"{ls:.1f} mm lever: the wire's {P.tip_travel():.1f} mm pull "
          f"cocks the arm {P.COCK_DEG:.0f}°", print_up=(0, 0, 1))
    a.allow("shoulder_lever", "shoulder_arbor")
    tip_l = (sx + ls, sy - 1.0, -25.75)
    a.add("sceptre_spring", rod_between((sx + ls - 3.0, sy + 2.0, -25.75), (sx + ls - 3.0, 58.0, -25.75), 2.4),
          material="steel", printed=False, group="sceptre",
          note="small extension spring (D13): pulls the lever up, flicking the arm to the bell [E]")
    a.allow("sceptre_spring", "shoulder_lever"); a.allow("sceptre_spring", "shoulder_bracket")
    tip_f = (sum(X_LEVER) / 2, pf[0], pf[1] + P.A_TIP)
    a.add("wire", rod_between(tip_f, tip_l, WIRE_D), material="steel", printed=False, group="sceptre",
          note="Ø0.5 steel wire, follower lever to shoulder lever: pulls only (cocking)")
    for nm in ("follower_lever", "shoulder_lever", "tower_inner_plate", "plinth_bell"):
        a.allow("wire", nm)
    # the arm (front): strike pose with the tip STRIKE_GAP from the bell; shown cocked (CW by COCK_DEG)
    tip = (BELL["x"] - BELL["d"] / 2 - STRIKE_GAP - 1.0, BELL["y"] - 4.0)
    hand = (sx - 12.0, sy - 17.0)
    arm2d = [(sx, sy), hand, tip]
    arm_shape = bd.Part()
    for p_, q_ in zip(arm2d, arm2d[1:]):
        arm_shape += rod_between((p_[0], p_[1], BELL["z"] - 1.5), (q_[0], q_[1], BELL["z"] - 1.5), 3.0) + \
            bd.Sphere(1.5).moved(bd.Location((q_[0], q_[1], BELL["z"] - 1.5)))
    arm_shape += zdisc(6.0, BELL["z"] - 3.0, BELL["z"]).moved(bd.Location((sx, sy, 0)))
    arm_shape -= zdisc(3.0 + parts.FITS.press, BELL["z"] - 4.0, BELL["z"] + 1.0).moved(bd.Location((sx, sy, 0)))
    arm_rest = arm_shape.rotate(bd.Axis((sx, sy, 0), (0, 0, 1)), -P.COCK_DEG)
    a.add("sceptre_arm", arm_rest, group="sceptre", print_up=(0, 0, 1),
          note="the arm and the striker in one print, pressed on the shoulder arbor; painted with the figure")
    a.allow("sceptre_arm", "shoulder_arbor"); a.allow("sceptre_arm", "figure_bell")
    data["sceptre"] = {"strike_gap": STRIKE_GAP, "lever_mm": round(ls, 2), "tip_travel": round(P.tip_travel(), 2)}
    bell = bd.Cone(BELL["d"] / 2, BELL["d"] / 2 - 3.0, BELL["h"], align=(bd.Align.CENTER, bd.Align.CENTER,
                                                                       bd.Align.MIN)).rotate(bd.Axis.X, -90)
    bell -= bd.Cone(BELL["d"] / 2 - 1.0, BELL["d"] / 2 - 4.0, BELL["h"] - 1.0,
                    align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.X, -90).moved(
        bd.Location((0, -0.01, 0)))
    bell += zdisc(2.0, 0, 6.0).rotate(bd.Axis.X, -90).moved(bd.Location((0, BELL["h"], 0)))
    a.add("bell", bell.moved(bd.Location((BELL["x"], BELL["y"] - BELL["h"] / 2, BELL["z"]))), material="brass",
          printed=False, group="figures", note="small brass bell, Ø≈20, mouth down; a little lower than E2's (§12) ⚠")
    a.allow("bell", "figure_bell")

    # ------------------------------------------------------------------ the cross shaft and couplings
    cy, cz = C
    a.add("cross_shaft", parts.rod(5.0, COUPLING[2] + 4.0 - (COUPLING[1] - 4.0)).rotate(bd.Axis.Y, 90).moved(
        bd.Location((COUPLING[1] - 4.0, cy, cz))), material="steel", printed=False, group="cross",
          note="Ø5 ground rod behind M1, below its motor adapters (they draw out backwards past it)")
    for nm, (xa, xb) in (("coupling_left", (COUPLING[0], COUPLING[1])), ("coupling_right", (COUPLING[2], COUPLING[3]))):
        cp = zdisc(12.0, 0, xb - xa, bore=5.0 + parts.FITS.press).rotate(bd.Axis.Y, 90).moved(bd.Location((xa, cy, cz)))
        cp -= box(0.6, 3.0, 12.0, (xa + (xb - xa) / 2, cy + 3.5, cz))            # the single dog's split, shown
        a.add(nm, cp, group="cross", print_up=(1, 0, 0),
              note="single-dog coupling (two halves; one way round only: the glass's phase)")
    a.allow("coupling_left", "cross_shaft"); a.allow("coupling_left", "cross_stub_left")
    a.allow("coupling_right", "cross_shaft")
    a.add("cross_stub_right", parts.rod(5.0, GX_CRANK[1] - (COUPLING[2] + 4.0)).rotate(bd.Axis.Y, 90).moved(
        bd.Location((COUPLING[2] + 4.0, cy, cz))), material="steel", printed=False, group="glass_drive",
          note="Ø5 ground rod: the crank's stub")
    a.allow("coupling_right", "cross_stub_right")

    # ------------------------------------------------------------------ the glass tower
    r = P.crank_radius()
    boss = zdisc(16.0, 0, span(GX_BOSS)).rotate(bd.Axis.Y, 90).moved(bd.Location((GX_BOSS[0], cy, cz)))
    for xb_ in (GX_BOSS[0], GX_BOSS[1] - b85.width):
        boss -= zdisc(b85.od, 0, b85.width).rotate(bd.Axis.Y, 90).moved(bd.Location((xb_, cy, cz)))
    boss -= zdisc(6.0, -1, span(GX_BOSS) + 1).rotate(bd.Axis.Y, 90).moved(bd.Location((GX_BOSS[0], cy, cz)))
    # the frame: an L from the boss to the outer plate (below the slider's travel)
    frame = boss + box(GX_OUTER[0] - GX_BOSS[0], 6.0, 16.0, ((GX_OUTER[0] + GX_BOSS[0]) / 2, cy - 39.0, cz))
    frame += box(4.0, 36.0, 16.0, (GX_BOSS[0] + 2.0, cy - 39.0 + 18.0, cz))
    a.add("glass_crank_block", frame, material="PETG", group="glass_drive", print_up=(0, 0, 1),
          note="two MR85ZZ for the crank's stub; screwed to the glass tower's plate")
    for k, xb_ in enumerate((GX_BOSS[0], GX_BOSS[1] - b85.width)):
        nm = f"crank_bearing_{k}"
        a.add(nm, parts.bearing("MR85ZZ").rotate(bd.Axis.Y, 90).moved(bd.Location((xb_, cy, cz))),
              material="bearing", printed=False, group="glass_drive", note="MR85ZZ")
        a.allow(nm, "glass_crank_block"); a.allow(nm, "cross_stub_right")
    a.allow("cross_stub_right", "glass_crank_block")
    # crank at its lower dead centre: the pin straight below the stub
    crank = zdisc(2 * r + 7.0, 0, span(GX_CRANK), bore=5.0 + parts.FITS.press).rotate(bd.Axis.Y, 90)
    crank = crank.moved(bd.Location((GX_CRANK[0], cy, cz)))
    pin_c = (cy - r, cz)
    crank_pin = parts.rod(3.0, span(GX_PIN)).rotate(bd.Axis.Y, 90).moved(bd.Location((GX_PIN[0], pin_c[0], pin_c[1])))
    a.add("crank", crank, group="glass_drive", print_up=(1, 0, 0), note=f"r {r:.3f} = π·r_p / 2 [D]: its 2r stroke "
          "is half a turn of the pinion")
    a.add("crank_pin", crank_pin, material="steel", printed=False, group="glass_drive", note="Ø3 × 7.5 steel pin")
    a.allow("crank", "cross_stub_right"); a.allow("crank", "crank_pin")
    # the slider: rod, yoke (bottom), rack block (top)
    y_low = pin_c[0]                                   # the yoke's slot centre at rest
    rod_y = (y_low - 26.0, GLASS["y"] + 32.0)
    a.add("slider_rod", parts.rod(4.0, rod_y[1] - rod_y[0]).rotate(bd.Axis.X, -90).moved(
        bd.Location((GX_ROD, rod_y[0], cz))), material="steel", printed=False, group="glass_drive",
          note="Ø4 ground rod: slides up and down in two guides")
    yoke = box(GX_ROD + 3.5 - GX_YOKE[0], 9.0, 2 * r + 12.0, ((GX_ROD + 3.5 + GX_YOKE[0]) / 2, y_low, cz))
    yoke -= box(GX_YOKE[1] - GX_YOKE[0] + 1.0, 3.0 + parts.FITS.running, 2 * r + 5.0,
                ((GX_YOKE[0] + GX_YOKE[1]) / 2 - 0.5, y_low, cz))
    yoke -= zdisc(4.0 + parts.FITS.press, -1, 12).rotate(bd.Axis.X, -90).moved(bd.Location((GX_ROD, y_low - 6, cz)))
    a.add("yoke", yoke, group="glass_drive", print_up=(0, 1, 0), note="Scotch yoke: the crank pin runs in its slot")
    a.allow("yoke", "slider_rod"); a.allow("yoke", "crank_pin")
    gp = g["pinion"]
    pitch_x = GLASS["x"] + gp.pitch_radius + gp.shift * P.M
    n_rack = 12
    p_ = math.pi * P.M
    rk = rack(P.M, n_rack, span(G_PINION_Z))           # local: along +x, teeth +y, pitch line y = 0, z 0..t
    # rack: local x -> global y (up), local y -> global -x (teeth towards the pinion), local z -> global z
    rk = rk.rotate(bd.Axis.Z, 90)
    y_rack0 = GLASS["y"] - 2 * r - (n_rack * p_ - 2 * r) / 2      # [D] = GLASS_y - 9p: a gap faces tooth 0 at rest
    rk = rk.moved(bd.Location((pitch_x, y_rack0, G_PINION_Z[0])))
    rk_bb = rk.bounding_box()
    arm_r = box(GX_ROD + 3.5 - rk_bb.max.X + 0.5, rk_bb.size.Y, (cz + 3.0) - G_PINION_Z[0],
                ((GX_ROD + 3.5 + rk_bb.max.X - 0.5) / 2, (rk_bb.min.Y + rk_bb.max.Y) / 2,
                 (cz + 3.0 + G_PINION_Z[0]) / 2))
    rack_part = rk + arm_r
    rack_part -= zdisc(4.0 + parts.FITS.press, -1, rk_bb.size.Y + 2).rotate(bd.Axis.X, -90).moved(
        bd.Location((GX_ROD, rk_bb.min.Y - 1, cz)))
    a.add("rack", rack_part, group="glass_drive", print_up=(0, 0, -1),
          note=f"{n_rack} teeth, module {P.M}: pressed on the slider rod; turns the glass's pinion")
    a.allow("rack", "slider_rod")
    rot_p = 0.0
    pin_g = gear_local(gp, span(G_PINION_Z), 3.0, rot_p).moved(bd.Location((GLASS["x"], GLASS["y"], G_PINION_Z[0])))
    a.add("glass_pinion_12", pin_g, group="glass_drive", note="pressed on the glass arbor")
    a.allow("glass_pinion_12", "rack")
    data["glass"] = {"crank_r": round(r, 4), "stroke": round(2 * r, 4), "half_turn_arc": round(math.pi *
                                                                                               gp.pitch_radius, 4),
                     "rack_pitch_x": round(pitch_x, 3)}
    # the slider's guides and the glass arbor's bearings hang on the glass tower's plate
    g_plate = box(span(GX_OUTER), rod_y[1] + 4.0 - (cy - 45.0), (-20.0) - (cz - 14.0),
                  (sum(GX_OUTER) / 2, (rod_y[1] + 4.0 + cy - 45.0) / 2, ((-20.0) + (cz - 14.0)) / 2))
    for yz in ((cy - 24.0, cz - 8.0), (GLASS["y"] + 28.0, -28.0)):
        g_plate -= zdisc(5.5, -1, span(GX_OUTER) + 1).rotate(bd.Axis.Y, 90).moved(bd.Location((GX_OUTER[0], *yz)))
    a.add("glass_tower_plate", g_plate, material="PETG", group="glass_tower", print_up=(1, 0, 0),
          note="the glass tower's plate: guides, arms and the crank block screw to it; M5 tabs to the internal frame")
    a.allow("glass_crank_block", "glass_tower_plate")
    for nm, yc in (("guide_low", y_low - 20.0), ("guide_high", 22.0)):
        gd = box(GX_OUTER[0] - GX_ROD + 4.0, 6.0, 10.0, ((GX_OUTER[0] + GX_ROD - 4.0) / 2, yc, cz))
        gd -= zdisc(4.0 + parts.FITS.running, -1, 8).rotate(bd.Axis.X, -90).moved(bd.Location((GX_ROD, yc - 4, cz)))
        a.add(nm, gd, material="PETG", group="glass_tower", print_up=(0, 1, 0), note="the slider rod's guide")
        a.allow(nm, "glass_tower_plate"); a.allow(nm, "slider_rod")
    for nm, zb in (("glass_arm_rear", G_REAR_BRG_Z), ("glass_arm_front", G_FRONT_BRG_Z)):
        t_ = 5.0
        arm_g = box(GX_OUTER[0] - (GLASS["x"] - 6.0), 10.0, t_, ((GX_OUTER[0] + GLASS["x"] - 6.0) / 2, GLASS["y"],
                                                               zb + t_ / 2 - 1.0))
        arm_g -= zdisc(b63.od + parts.FITS.bearing_seat, zb - 0.01, zb + b63.width).moved(
            bd.Location((GLASS["x"], GLASS["y"], 0)))
        arm_g -= zdisc(3.6, zb - 3, zb + 8).moved(bd.Location((GLASS["x"], GLASS["y"], 0)))
        a.add(nm, arm_g, material="PETG", group="glass_tower", print_up=(0, 0, 1),
              note="carries one MR63ZZ of the glass arbor")
        a.allow(nm, "glass_tower_plate")
        bn = nm.replace("arm", "bearing")
        a.add(bn, parts.bearing("MR63ZZ", zb).moved(bd.Location((GLASS["x"], GLASS["y"], 0))), material="bearing",
              printed=False, group="glass_tower", note="MR63ZZ")
        a.allow(bn, nm)
    a.allow("glass_arm_rear", "rack")
    gz0 = G_PINION_Z[0]
    a.add("glass_arbor", parts.rod(3.0, GLASS["z"] - 5.0 - gz0, gz0).moved(bd.Location((GLASS["x"], GLASS["y"], 0))),
          material="steel", printed=False, group="glass_tower", note="Ø3 ground rod, front to back through the chest")
    for nm in ("glass_bearing_rear", "glass_bearing_front", "glass_pinion_12", "figure_glass"):
        a.allow("glass_arbor", nm)
    a.allow("glass_tower_plate", "plinth_glass")
    # the forearms and the glass's frame, in one print, on the arbor's front end
    gx, gy, gzc = GLASS["x"], GLASS["y"], GLASS["z"]
    frame_g = box(GLASS["d"] + 4.0, GLASS["h"] + 3.0, 2.0, (gx, gy, gzc - GLASS["d"] / 2 - 2.0))
    frame_g += box(GLASS["d"] + 4.0, 1.5, GLASS["d"] + 2.0, (gx, gy + GLASS["h"] / 2 + 0.75, gzc - 0.5))
    frame_g += box(GLASS["d"] + 4.0, 1.5, GLASS["d"] + 2.0, (gx, gy - GLASS["h"] / 2 - 0.75, gzc - 0.5))
    for s in (-1, 1):                                  # the forearms, reaching back to the figure's sides
        frame_g += rod_between((gx + s * (GLASS["d"] / 2 + 2.0), gy - 3.0, gzc - 2.0),
                               (gx + s * 12.0, gy - 10.0, gzc - 9.0), 4.0)
    frame_g += zdisc(6.0, gzc - GLASS["d"] / 2 - 5.0, gzc - GLASS["d"] / 2 - 1.0).moved(bd.Location((gx, gy, 0)))
    frame_g -= zdisc(3.0 + parts.FITS.press, gzc - GLASS["d"] / 2 - 6.0, gzc - GLASS["d"] / 2 - 0.5).moved(
        bd.Location((gx, gy, 0)))
    a.add("forearms_and_frame", frame_g, group="figures", print_up=(0, 0, -1),
          note="the forearms and the glass's frame in one print (Paul: the forearms turn the glass)")
    a.allow("forearms_and_frame", "glass_arbor"); a.allow("forearms_and_frame", "figure_glass")
    hg = bd.Cone(GLASS["d"] / 2, 0.8, GLASS["h"] / 2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    hg = (hg + hg.mirror(bd.Plane.XY)).rotate(bd.Axis.X, -90).moved(bd.Location((gx, gy, gzc)))
    a.add("hourglass", hg, material="ghost", printed=False, group="figures",
          note="bought miniature hourglass, red sand, ≈ 20 mm ⚠ to source")
    a.allow("hourglass", "forearms_and_frame")
    return a, data


def check(a: Assembly, data: dict) -> dict:
    env = a.envelope()
    return {
        "interference": [{"a": x, "b": y, "volume_mm3": round(v, 3)} for x, y, v in a.interference()],
        "bed_fit_single": [r for r in a.bed_fit(BED_SINGLE) if not r["fits"]],
        "bed_fit_dual": [r for r in a.bed_fit(BED_DUAL) if not r["fits"]],
        "envelope": {"x": [round(env.min.X, 1), round(env.max.X, 1)], "y": [round(env.min.Y, 1), round(env.max.Y, 1)],
                     "z": [round(env.min.Z, 1), round(env.max.Z, 1)]},
        "parts": len(a.items), "printed": len([i for i in a.items if i.printed]), "timing": P.timing(), **data,
    }


def renders(a: Assembly, out: Path):
    out.mkdir(parents=True, exist_ok=True)
    a.render(out / "e1_front.png", elev=0, azim=-90, up="y", title="E1: the two genies from the front (rest, home)",
             tolerance=0.3, size=(11, 6))
    a.render(out / "e1_three_quarter.png", elev=20, azim=-125, up="y", title="E1: from behind (figures hidden)",
             hide=("figures",), tolerance=0.3, size=(11, 8))
    a.render(out / "e1_bell_tower.png", elev=15, azim=35, up="y", title="E1: the bell tower from inside (plates and "
             "figures hidden): snail, lever, silencing cam, count wheel, sector", hide=("figures", "tower", "glass_drive",
                                                                                     "glass_tower", "cross"),
             tolerance=0.15, size=(10, 8))
    a.render(out / "e1_glass_drive.png", elev=12, azim=200, up="y", title="E1: the glass drive from inside (crank, "
             "yoke, rack, pinion; its plate hidden)", hide=("figures", "tower", "trains", "lever", "motor", "sceptre",
                                                             "glass_tower"), tolerance=0.15, size=(9, 8))


def main(out_dir="export/e1_angels"):
    out = Path(out_dir)
    a, data = build()
    res = check(a, data)
    out.mkdir(parents=True, exist_ok=True)
    (out / "e1_angels.json").write_text(json.dumps(res, indent=2, default=str))
    print(json.dumps({k: res[k] for k in ("interference", "bed_fit_single", "envelope", "parts", "printed")},
                     indent=2))
    renders(a, out)
    write_dae(a, out / "e1_angels.dae")
    return a, res


if __name__ == "__main__":
    main(*sys.argv[1:])
