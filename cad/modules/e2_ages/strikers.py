"""E2 part 2b: the quarter and hour counting trains in CAD (docs/e2-design.md §12). Geometry: striking.py.

Each train, at rest (rack gathered, the strike shaft at its lock angle):
- the rack on the common stud, its tail finger above the snail, its teeth rim on the far side;
- the feed lever on the same stud, its gathering pawl lifted by the guard, the strap from the eccentric;
- the hook in the hooked tooth's space, its weighted tail held in; the release arms clear of it;
- the strike shaft (Ø5, two MR85ZZ) with its eccentric, lock cam, lifter cam (part 2c takes the lift on), and
  (quarters) the cue cam; a gearmotor drives it through 12/36;
- the lock, home and cue microswitches.

The releases (Paul, PR #21, decision 1: the walk train releases the racks):
- the quarter release shaft (Ø3, along X) carries a follower whose nub runs in the release disc's groove under the
  walk's program shaft, and an arm beside the quarter hook. In phase A of every show the groove rocks the shaft and
  the arm pushes the hook's weighted tail: the hook turns out and the quarter rack falls onto its snail;
- the hour trip shaft (Ø3, along X): a pin in the quarter rack lifts its arm A only when the rack falls past three
  pairs (the fourth quarter); its arm B then pushes a tab on the hour hook, which turns out, and the hour rack
  falls. The first pair gathered lowers the pin again and the hour hook drops back in.

Shapes are drawn in the YZ plane (local x -> global Y, local y -> global Z) and extruded along X.
"""
from __future__ import annotations

import math

import build123d as bd
import numpy as np
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

from cad.lib import parts
from cad.lib.gears import Gear, centre_distance, mesh_rotation, pair_shifts, spur_gear
from cad.lib.hardware import BEARINGS
from cad.modules.e2_ages import drives as D
from cad.modules.e2_ages import striking as S

SHAFT_D = 5.0                                # strike shafts, Ø5 ground rod in MR85ZZ
STUD_D = 3.0                                 # rack, hook and release studs
PIN_D = 2.0                                  # the feed lever's pin (pawl and strap)
ECC_D = 12.0                                 # the eccentric disc
LOCK_R = 9.0                                 # lock cams
CUE_R = 9.0
LIFT_R = (7.0, 13.0)                         # lifter cams: base and top radii (part 2c sets the lift it needs)
PLATE_T = 3.0
TAIL_LEN = 1.0                               # the hook's tail, as a fraction of its arm
SPRING_X = 3.0                               # the rack spring hangs this far to the -X side of the rack's mid-plane
TAIL_LUMP = 3.0                              # the lump at the end of the hook's and the pawl's tails (radius)
PAWL_TAIL = 1.0                              # the pawl's tail, as a fraction of its arm: its lump keeps it in the teeth,
#                                              and the guard lifts it clear of the feed lever's and strap's bosses
ARM_RISE = 5.0                               # the racks' tail arms run this far above the stud (clear of the snails)
MIDDLE_X = (2.0, 5.0)                        # the middle strike plate
RIGHT_X = (27.6, 30.6)                       # the right strike plate
GEAR_TEETH = (12, 24)                        # gearmotor pinion : strike shaft gear (≈ 40 rpm -> 20 rpm)
SWITCH = dict(l=12.8, w=5.8, h=6.5)          # subminiature microswitch [E]


# ------------------------------------------------------------------------------------------------ helpers
def yz_solid(poly, x0: float, x1: float):
    """Extrude a shapely polygon in (y, z) along X from x0 to x1."""
    polys = list(poly.geoms) if hasattr(poly, "geoms") else [poly]
    out = None
    for pg in polys:
        pts = [bd.Vector(float(x), float(y), 0) for x, y in list(pg.exterior.coords)[:-1]]
        face = bd.Face(bd.Wire.make_polygon(pts, close=True))
        for hole in pg.interiors:
            hp = [bd.Vector(float(x), float(y), 0) for x, y in list(hole.coords)[:-1]]
            face = face - bd.Face(bd.Wire.make_polygon(hp, close=True))
        sol = bd.extrude(face, amount=x1 - x0, dir=(0, 0, 1))
        out = sol if out is None else out + sol
    return D.on_x(out, x0, 0.0, 0.0)


def bar(p, q, w):
    return LineString([p, q]).buffer(w / 2, cap_style=1, join_style=1)


def path(pts, w):
    return LineString(pts).buffer(w / 2, cap_style=1, join_style=1)


def disc(c, r, n=64):
    return Point(c).buffer(r, quad_segs=n // 4)


def rot_about(poly, centre, ang_rad):
    from shapely import affinity
    return affinity.rotate(poly, ang_rad, origin=centre, use_radians=True)


def x_of(t: S.TrainSpec, key: str):
    a, b = S.X_PLANES[key]
    return (t.x_rack + a, t.x_rack + b)


def x_rod(d, x0, x1, yz):
    return D.on_x(parts.rod(d, x1 - x0), x0, yz[0], yz[1])


# ------------------------------------------------------------------------------------------------ the parts
def rack_poly_body(t: S.TrainSpec):
    """The rack's body in the rack frame (theta = 0): hub, tail arm and finger, weight, spoke."""
    p = S.pivot()
    ys, _ = S.arbor_yz()
    top = p[1] + ARM_RISE                                    # the tail arm runs above the snail
    tip = (ys, p[1])
    arm = path([p, (p[0] - 4.0, top), (ys + 2.0, top), (ys, top - 2.0), (tip[0], tip[1] + S.TAIL_PIN)], 3.0)
    finger = disc(tip, S.TAIL_PIN) .union(bar((tip[0], tip[1]), (tip[0], top - 2.0), 2 * S.TAIL_PIN))
    weight = disc((p[0] - 13.0, top - 0.5), 3.5)            # tail-heavy: the rack falls onto the snail by itself
    d = S.tooth_angle(t)
    th = S.rack_angles(t)
    g_mid = S.ALPHA_H - (th[0] + th[-1]) / 2                # the teeth's middle, in the rack frame
    spoke_end = S._add(p, S.unit(g_mid), t.r_teeth - 3.0)
    spoke = bar(p, spoke_end, 4.0)
    hub = disc(p, 4.0)
    parts_ = [arm, finger, weight, spoke, hub]
    if t is S.QUARTER:
        parts_.append(trip_lobe_poly(t))
    body = unary_union(parts_).difference(disc(p, (STUD_D + parts.FITS.running) / 2))
    if t is S.QUARTER:
        body = body.difference(disc(trip_pin_centre(S.rack_angles(t)[0], frame=True), (PIN_D + parts.FITS.press) / 2))
    return body


def rack_poly_rim(t: S.TrainSpec):
    """The teeth rim (rack frame): ratchet teeth, radial face CCW, slope CW."""
    p = S.pivot()
    d = S.tooth_angle(t)
    th = S.rack_angles(t)
    gam = [S.ALPHA_H - (th[0] + k * d) for k in range(-1, t.counts + 2)]   # tooth k's radial face
    rr, rt = S.r_root(t), S.r_tip(t)
    r_in = t.r_teeth - 3.5
    pts = []
    for g in gam:
        pts.append(S._add(p, S.unit(g), rr))
        pts.append(S._add(p, S.unit(g), rt))
    g_end = gam[-1] - d
    pts.append(S._add(p, S.unit(g_end), rr))
    for g in np.linspace(g_end, gam[0], 40):
        pts.append(S._add(p, S.unit(g), r_in))
    return Polygon(pts).buffer(0)


def rack_solid(t: S.TrainSpec, theta: float):
    """The rack at rack angle theta (radians; striking.rack_angles gives home and the counts)."""
    p = S.pivot()
    body = rot_about(rack_poly_body(t), p, theta)
    rim = rot_about(rack_poly_rim(t), p, theta)
    th0 = S.rack_angles(t)[0]
    vane = rot_about(vane_poly(t), p, theta - th0)
    pin, _ = S.spring_points(t, theta)
    boss = disc(pin, 2.2).difference(disc(pin, (PIN_D + parts.FITS.press) / 2))
    vx = (t.x_rack - VANE["t"] / 2, t.x_rack + VANE["t"] / 2)
    return (yz_solid(body.union(boss), *x_of(t, "rack")) + yz_solid(rim, *x_of(t, "rim"))
            + yz_solid(vane, *vx))


def tip_finger(t: S.TrainSpec, tip):
    """The part of a hook or pawl that reaches into the rim's half: a rounded tip and a radial stem out past the
    teeth, so nothing of it lies along the next tooth's slope."""
    p = S.pivot()
    a = math.atan2(tip[1] - p[1], tip[0] - p[0])
    out = S._add(p, S.unit(a), S.r_tip(t) + 1.5)
    return disc(tip, S.TIP_R).union(bar(tip, out, 2 * S.TIP_R))


def hook_solid(t: S.TrainSpec, lift: float = 0.0):
    """The hook (engaged, or turned out by `lift` radians): body and hub beside the rim, tip finger in the rim's
    right half; a counterweight tail past the pivot keeps it in the teeth."""
    body = hook_poly(t)
    hk = S.hook_geometry(t)
    q, tip = hk["pivot"], hk["tip"]
    body = body.difference(disc(q, (STUD_D + parts.FITS.running) / 2))
    finger = tip_finger(t, tip)
    body, finger = rot_about(body, q, lift), rot_about(finger, q, lift)
    return yz_solid(body, *x_of(t, "hook")) + yz_solid(finger, x_of(t, "hook_tip")[0], x_of(t, "hook")[0] + 0.01)


def pawl_solid(t: S.TrainSpec, lift: float):
    """The gathering pawl on the feed lever's pin, turned out by `lift` (at rest the guard holds it out)."""
    body = pawl_poly(t)
    fg = S.feed_geometry(t)
    q, tip = fg["pin"], fg["tip"]
    body = body.difference(disc(q, (PIN_D + parts.FITS.running) / 2))
    finger = tip_finger(t, tip)
    body, finger = rot_about(body, q, lift), rot_about(finger, q, lift)
    return yz_solid(body, *x_of(t, "pawl")) + yz_solid(finger, x_of(t, "pawl")[1] - 0.01, x_of(t, "pawl_tip")[1])


def feed_lever_solid(t: S.TrainSpec):
    p = S.pivot()
    fg = S.feed_geometry(t)
    q = fg["pin"]
    body = unary_union([disc(p, 4.0), bar(p, q, 3.5), disc(q, 2.8)])
    body = body.difference(disc(p, (STUD_D + parts.FITS.running) / 2)).difference(disc(q, (PIN_D + parts.FITS.press) / 2))
    return yz_solid(body, *x_of(t, "feed"))


def eccentric_centre(t: S.TrainSpec, phase_deg: float):
    """The eccentric's centre: at rest (phase 0) its throw points away from the strap's pin (the strap is longest)."""
    fg = S.feed_geometry(t)
    k, q = fg["shaft"], fg["pin"]
    a0 = math.atan2(k[1] - q[1], k[0] - q[0])
    a = a0 + math.radians(phase_deg)
    return S._add(k, S.unit(a), fg["eccentric"])


def strap_solid(t: S.TrainSpec):
    fg = S.feed_geometry(t)
    c = eccentric_centre(t, 0.0)
    q = fg["pin"]
    ring = disc(c, ECC_D / 2 + 1.8).difference(disc(c, (ECC_D + parts.FITS.running) / 2))
    body = unary_union([ring, bar(S._add(c, S.unit(math.atan2(q[1] - c[1], q[0] - c[0])), ECC_D / 2 + 1.0), q, 3.0),
                        disc(q, 2.8)]).difference(disc(q, (PIN_D + parts.FITS.running) / 2))
    return yz_solid(body, *x_of(t, "link"))


def eccentric_solid(t: S.TrainSpec):
    fg = S.feed_geometry(t)
    c = eccentric_centre(t, 0.0)
    k = fg["shaft"]
    body = disc(c, ECC_D / 2).difference(disc(k, (SHAFT_D + parts.FITS.press) / 2))
    return yz_solid(body, *x_of(t, "link"))


def cam_solid(radius_of_deg, x0, x1, centre, rot_deg=0.0, bore=SHAFT_D + parts.FITS.press, n=360):
    pts = []
    for i in range(n):
        a = 360.0 * i / n
        r = radius_of_deg(a)
        aa = math.radians(a + rot_deg)
        pts.append((centre[0] + r * math.cos(aa), centre[1] + r * math.sin(aa)))
    poly = Polygon(pts).buffer(0).difference(disc(centre, bore / 2))
    return yz_solid(poly, x0, x1)


def lock_radius(a):
    """Lock cam: a notch around the rest angle (the switch's roller drops in)."""
    d = ((a + 180.0) % 360.0) - 180.0
    return LOCK_R - 1.5 if -6.0 <= d <= 6.0 else LOCK_R


def cue_radius(a):
    return CUE_R + 1.5 if S.CUE[0] <= a <= S.CUE[1] else CUE_R


def lift_radius(a):
    """Lifter cam (shaft angle a): rises from LIFT[0] to LIFT[1], holds to LIFT[2], drops (the stroke)."""
    r0, r1 = LIFT_R
    a0, a1, a2 = S.LIFT
    if a0 <= a < a1:
        return r0 + (r1 - r0) * (a - a0) / (a1 - a0)
    if a1 <= a < a2:
        return r1
    return r0


def switch_solid(centre_yz, x0, axis_deg=0.0):
    """A subminiature microswitch: body only [E], its long side along axis_deg in the YZ plane."""
    poly = Polygon([(-SWITCH["l"] / 2, -SWITCH["h"] / 2), (SWITCH["l"] / 2, -SWITCH["h"] / 2),
                    (SWITCH["l"] / 2, SWITCH["h"] / 2), (-SWITCH["l"] / 2, SWITCH["h"] / 2)])
    from shapely import affinity
    poly = affinity.translate(affinity.rotate(poly, axis_deg, origin=(0, 0)), *centre_yz)
    return yz_solid(poly, x0, x0 + SWITCH["w"])


# ------------------------------------------------------------------------------------------------ assembly
def add_strike_trains(a, minutes: float, hours: float):
    """Both counting trains at rest: racks gathered, hooks in, pawls held out, strike shafts at their lock angle."""
    data = {}
    p = S.pivot()
    ys, zs = S.arbor_yz()
    s12, s36 = pair_shifts(*GEAR_TEETH)
    g12, g36 = Gear(GEAR_TEETH[0], 1.0, shift=s12), Gear(GEAR_TEETH[1], 1.0, shift=s36)
    cd = centre_distance(g12, g36)
    b85 = BEARINGS["MR85ZZ"]
    for t in S.TRAINS:
        tag = t.name
        th = S.rack_angles(t)
        a.add(f"{tag}_rack", rack_solid(t, th[0]), group="strike", print_up=(-1, 0, 0), nozzle=0.2,
              note=f"{tag} rack, gathered: its tail falls onto the {tag} snail; {t.counts} teeth of pitch {S.PITCH}")
        a.add(f"{tag}_feed_lever", feed_lever_solid(t), group="strike", print_up=(1, 0, 0), note="rocked by the eccentric: gathers one "
              "tooth per turn of the strike shaft")
        pawl_lift = 0.25                                       # held out by the guard at rest [rad]
        a.add(f"{tag}_pawl", pawl_solid(t, pawl_lift), group="strike", print_up=(1, 0, 0), nozzle=0.2, note="gathering pawl, on the feed lever's pin")
        a.add(f"{tag}_hook", hook_solid(t, 0.0), group="strike", print_up=(-1, 0, 0), nozzle=0.2, note="rack hook: holds each gathered tooth")
        a.add(f"{tag}_strap", strap_solid(t), group="strike", print_up=(1, 0, 0), note="strap from the eccentric to the feed lever's pin")
        a.add(f"{tag}_eccentric", eccentric_solid(t), group="strike", print_up=(1, 0, 0), note=f"throw {S.feed_geometry(t)['eccentric']:.2f} mm")
        fg, hk = S.feed_geometry(t), S.hook_geometry(t)
        k = fg["shaft"]
        data[tag] = {"shaft_yz": [round(v, 2) for v in k], "hook_pivot": [round(v, 2) for v in hk["pivot"]],
                     "feed_pin": [round(v, 2) for v in fg["pin"]],
                     "snail_radii": [round(r, 3) for r in S.snail_radii(t)],
                     "rack_angles_deg": [round(math.degrees(v), 2) for v in th]}
        # pins and studs
        a.add(f"{tag}_feed_pin", x_rod(PIN_D, x_of(t, "link")[0], x_of(t, "pawl")[1], fg["pin"]), material="steel",
              printed=False, group="strike", note="Ø2 steel pin pressed in the feed lever")
        hx = (x_of(t, "hook")[0], MIDDLE_X[0] if t is S.HOUR else RIGHT_X[0])
        a.add(f"{tag}_hook_stud", x_rod(STUD_D, hx[0], hx[1], hk["pivot"]), material="steel", printed=False,
              group="strike")
        for x_, y_ in ((f"{tag}_pawl", f"{tag}_feed_pin"), (f"{tag}_feed_lever", f"{tag}_feed_pin"),
                       (f"{tag}_strap", f"{tag}_feed_pin"), (f"{tag}_strap", f"{tag}_eccentric"),
                       (f"{tag}_hook", f"{tag}_hook_stud"),
                       (f"{tag}_hook", f"{tag}_rack"), (f"{tag}_rack", "rack_stud"), (f"{tag}_feed_lever", "rack_stud"),
                       (f"{tag}_rack", f"{tag}_feed_lever"), (f"{tag}_pawl", f"{tag}_feed_lever"),
                       (f"{tag}_strap", f"{tag}_feed_lever")):
            a.allow(x_, y_)
    for t in S.TRAINS:
        th0 = S.rack_angles(t)[0]
        pin, anc = S.spring_points(t, th0)
        xs = t.x_rack - SPRING_X
        a.add(f"{t.name}_spring_pin", x_rod(PIN_D, xs - S.RACK_SPRING["De"] / 2 - 0.3, t.x_rack + 1.5, pin),
              material="steel", printed=False, group="strike", note="Ø2 pin in the rack's spoke: the spring's lower hook")
        sp = bd.Cylinder(S.RACK_SPRING["De"] / 2, math.dist(pin, anc) - 3.0,
                         align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(
            bd.Location((xs, pin[0], pin[1] + 1.5)))
        a.add(f"{t.name}_rack_spring", sp, material="steel", printed=False, group="strike",
              note=f"{S.RACK_SPRING['part']}: pulls the spoke up, so the tail falls onto the snail")
        plate_x = MIDDLE_X[0] if t is S.HOUR else RIGHT_X[0]
        blk = Polygon([(anc[0] - 3, anc[1] - 1.5), (anc[0] + 3, anc[1] - 1.5), (anc[0] + 3, anc[1] + 4),
                       (anc[0] - 3, anc[1] + 4)])
        x0, x1 = sorted((t.x_rack - 4.0, plate_x))
        a.add(f"{t.name}_spring_anchor", yz_solid(blk, x0, x1), material="PETG", group="strike", print_up=(1, 0, 0),
              note="the spring's upper hook catches its pin; screwed to the strike plate")
        for x_, y_ in ((f"{t.name}_spring_pin", f"{t.name}_rack"), (f"{t.name}_rack_spring", f"{t.name}_spring_pin"),
                       (f"{t.name}_rack_spring", f"{t.name}_spring_anchor")):
            a.allow(x_, y_)
    pin = trip_pin_centre(S.rack_angles(S.QUARTER)[0])
    a.add("quarter_trip_pin", x_rod(PIN_D, x_of(S.QUARTER, "rack")[0], TRIP_X_A[1] - 0.2, pin), material="steel",
          printed=False, group="strike", note="Ø2 pin pressed in the quarter rack's lobe: past three pairs it lifts "
                                              "the hour trip's arm A")
    a.allow("quarter_trip_pin", "quarter_rack")
    a.add("rack_stud", x_rod(STUD_D, x_of(S.HOUR, "feed")[0] - 0.5, RIGHT_X[1], p), material="steel", printed=False,
          group="strike", note="Ø3 ground rod: both racks and both feed levers turn on it")
    data["pivot"] = [round(v, 2) for v in p]
    return data


# ------------------------------------------------------------------------------------------------ frame, shafts, drive
OPTO = dict(L=11.9, W=6.3, H=10.8, gap=3.1, slit_h=3.8)    # Vishay TCST1202 [S: as M2's E6, e6.py]
VANE = dict(r=19.0, t=1.5, out=10.0)                        # the home vane on each rack's spoke
SLIT_IN = 0.5                                               # the opto's slit lies this far inside the vane's end
HOUR_MOTOR_PLATE_X = (-39.0, -36.0)
QUARTER_MOTOR_PLATE_X = (46.0, 49.0)
GEARMOTOR = dict(w=12.0, d=10.0, length=34.5, shaft_d=3.0, shaft_l=9.0)   # [E] ⚠ as the walk's, ≈ 40 rpm


def spoke_angle_home(t: S.TrainSpec) -> float:
    th = S.rack_angles(t)
    return S.ALPHA_H - (th[0] + th[-1]) / 2 + th[0]


def vane_poly(t: S.TrainSpec):
    """A tab on the spoke's CW side, at home inside the opto's gap; the rack only ever turns away (CCW) from it."""
    p = S.pivot()
    a = spoke_angle_home(t)
    base = S._add(p, S.unit(a), VANE["r"])
    cw = (math.sin(a), -math.cos(a))
    tip = S._add(base, cw, VANE["out"])
    return bar(base, tip, 4.0)


def opto_solid(t: S.TrainSpec):
    """The TCST1202 straddling the vane: its gap across X at the rack's mid-plane, its slit 2 mm in from the vane's
    edge at home."""
    p = S.pivot()
    a = spoke_angle_home(t)
    cw = (math.sin(a), -math.cos(a))
    base = S._add(p, S.unit(a), VANE["r"])
    end = S._add(base, cw, VANE["out"] + 2.0)
    centre = S._add(end, cw, -SLIT_IN - OPTO["slit_h"] / 2 + OPTO["L"] / 2 - 1.0)   # the slit just inside the end
    from shapely import affinity
    body = Polygon([(-OPTO["L"] / 2, -OPTO["H"] / 2), (OPTO["L"] / 2, -OPTO["H"] / 2), (OPTO["L"] / 2, OPTO["H"] / 2),
                    (-OPTO["L"] / 2, OPTO["H"] / 2)])
    body = affinity.translate(affinity.rotate(body, math.degrees(a), origin=(0, 0)), *centre)
    xm = t.x_rack
    g = OPTO["gap"] / 2
    arms = yz_solid(body, xm - OPTO["W"] / 2, xm - g) + yz_solid(body, xm + g, xm + OPTO["W"] / 2)
    # the arms' far ends join behind the vane's sweep (the floor of the U), away from the rack
    floor = affinity.translate(affinity.rotate(Polygon([(-OPTO["L"] / 2, -OPTO["H"] / 2), (OPTO["L"] / 2, -OPTO["H"] / 2),
                                                        (OPTO["L"] / 2, -OPTO["H"] / 2 + 2.0), (-OPTO["L"] / 2, -OPTO["H"] / 2 + 2.0)]),
                                               math.degrees(a), origin=(0, 0)), *centre)
    return arms, centre


def guard_point(t: S.TrainSpec, lift: float = 0.25):
    """Where the guard pin sits: just under the pawl's tail when the pawl is held out at rest."""
    fg = S.feed_geometry(t)
    q, tip = fg["pin"], fg["tip"]
    tail = S._add(q, (q[0] - tip[0], q[1] - tip[1]), PAWL_TAIL)
    c, s_ = math.cos(lift), math.sin(lift)
    d = (tail[0] - q[0], tail[1] - q[1])
    tail_l = (q[0] + c * d[0] - s_ * d[1], q[1] + s_ * d[0] + c * d[1])
    return (tail_l[0], tail_l[1] - TAIL_LUMP - 1.0)


def strike_layout():
    """Shaft positions and the x ranges along each strike shaft."""
    kh, kq = S.feed_geometry(S.HOUR)["shaft"], S.feed_geometry(S.QUARTER)["shaft"]
    s12, s24 = pair_shifts(*GEAR_TEETH)
    cd = centre_distance(Gear(GEAR_TEETH[0], 1.0, shift=s12), Gear(GEAR_TEETH[1], 1.0, shift=s24))
    return {
        "hour": dict(shaft=kh, x=(-35.8, MIDDLE_X[1] + 0.5), gear=(-33.2, -30.7), lock=(-35.5, -33.5),
                     lift=(-3.4, -0.9), motor=(kh[0] + cd, kh[1]), motor_face=HOUR_MOTOR_PLATE_X[0],
                     motor_dir=+1, bearings=((-30.0, -27.5), (MIDDLE_X[1] - 2.5, MIDDLE_X[1]))),
        "quarter": dict(shaft=kq, x=(MIDDLE_X[0] - 0.5, 42.0), gear=(39.2, 41.7), cue=(31.0, 33.0), lock=(33.3, 35.3),
                        lift=(35.6, 38.6), motor=(kq[0] + cd, kq[1]), motor_face=QUARTER_MOTOR_PLATE_X[1],
                        motor_dir=-1, bearings=((MIDDLE_X[0], MIDDLE_X[0] + 2.5), (RIGHT_X[1] - 2.5, RIGHT_X[1]))),
        "cd": cd}


def plate_solid(x, outline_yz, holes=()):
    poly = Polygon(outline_yz)
    for c, d in holes:
        poly = poly.difference(disc(c, d / 2))
    return yz_solid(poly, *x)


def add_strike_frame(a):
    """Strike shafts, cams, gears, gearmotors, plates, guards, switches and optos."""
    lay = strike_layout()
    p = S.pivot()
    b85 = BEARINGS["MR85ZZ"]
    s12, s24 = pair_shifts(*GEAR_TEETH)
    g12, g24 = Gear(GEAR_TEETH[0], 1.0, shift=s12), Gear(GEAR_TEETH[1], 1.0, shift=s24)
    seat = b85.od + parts.FITS.bearing_seat
    data = {"gear": f"{GEAR_TEETH[0]}/{GEAR_TEETH[1]}", "cd": round(lay["cd"], 3)}
    for t in S.TRAINS:
        tag, L = t.name, lay[t.name]
        k = L["shaft"]
        a.add(f"{tag}_strike_shaft", x_rod(SHAFT_D, L["x"][0], L["x"][1], k), material="steel", printed=False,
              group="strike", note="Ø5 ground rod, one turn per stroke (3 s)")
        for i, (x0, x1) in enumerate(L["bearings"]):
            a.add(f"{tag}_strike_bearing_{i}", D.on_x(parts.bearing(b85), x0, k[0], k[1]), material="bearing",
                  printed=False, group="strike", note="MR85ZZ")
            a.allow(f"{tag}_strike_bearing_{i}", f"{tag}_strike_shaft")
        a.allow(f"{tag}_eccentric", f"{tag}_strike_shaft")
        # cams
        a.add(f"{tag}_lock_cam", cam_solid(lock_radius, *L["lock"], k), group="strike", print_up=(1, 0, 0),
              note="its notch lets the lock switch's roller drop at the rest angle")
        a.add(f"{tag}_lifter_cam", cam_solid(lift_radius, *L["lift"], k), group="strike", print_up=(1, 0, 0),
              note="lifts the striking figure and drops it at 1 s (part 2c takes the lift on)")
        for nm in (f"{tag}_lock_cam", f"{tag}_lifter_cam"):
            a.allow(nm, f"{tag}_strike_shaft")
        if "cue" in L:
            a.add(f"{tag}_cue_cam", cam_solid(cue_radius, *L["cue"], k), group="strike", print_up=(1, 0, 0),
                  note="closes E1's cue switch at the start of each pair: the genie strikes first")
            a.allow(f"{tag}_cue_cam", f"{tag}_strike_shaft")
        # gear and gearmotor (its pinion on the motor's D-shaft; the motor slides out along X)
        ang_m = math.degrees(math.atan2(L["motor"][1] - k[1], L["motor"][0] - k[0]))
        gear24 = spur_gear(g24, L["gear"][1] - L["gear"][0]) - parts.disc(SHAFT_D + parts.FITS.press, 20, z0=-5)
        a.add(f"{tag}_strike_gear", D.on_x(gear24, L["gear"][0], k[0], k[1]), group="strike", print_up=(1, 0, 0),
              note=f"{GEAR_TEETH[1]} teeth, pressed on the strike shaft")
        r12 = mesh_rotation(g24, g12, ang_m, 0.0)
        pin12 = spur_gear(g12, L["gear"][1] - L["gear"][0]).rotate(bd.Axis.Z, r12) - parts.disc(
            GEARMOTOR["shaft_d"] + parts.FITS.press, 20, z0=-5)
        a.add(f"{tag}_motor_pinion", D.on_x(pin12, L["gear"][0], L["motor"][0], L["motor"][1]), group="strike",
              print_up=(1, 0, 0),
              note="pressed on the gearmotor's Ø3 D-shaft")
        a.allow(f"{tag}_strike_gear", f"{tag}_strike_shaft")
        gm = GEARMOTOR
        face = L["motor_face"]
        dirx = L["motor_dir"]                                  # +1: the shaft points +X (body on the -X side)
        body = bd.Box(gm["length"], gm["w"], gm["d"], align=(bd.Align.MAX if dirx > 0 else bd.Align.MIN,
                                                               bd.Align.CENTER, bd.Align.CENTER))
        body = body.moved(bd.Location((face, L["motor"][0], L["motor"][1])))
        shaft = x_rod(gm["shaft_d"], *(sorted((face, face + dirx * gm["shaft_l"]))), L["motor"])
        a.add(f"{tag}_motor", body + shaft, material="black", printed=False, group="strike",
              note="micro metal gearmotor ≈ 40 rpm [E] ⚠; slides out along X after two M2")
        a.allow(f"{tag}_motor_pinion", f"{tag}_motor")
        mp_x = HOUR_MOTOR_PLATE_X if t is S.HOUR else QUARTER_MOTOR_PLATE_X
        my, mz = L["motor"]
        if t is S.HOUR:
            outline = [(my - 13, mz - 9), (my + 13, mz - 9), (my + 13, -47.0), (my - 13, -47.0)]
        else:
            outline = [(my - 13, mz - 9), (my + 13, mz - 9), (my + 13, -47.0), (36.0, -47.0), (36.0, -53.0),
                       (27.5, -53.0), (27.5, -63.5), (my - 13, -63.5)]       # under the walk's lock and release cams
        holes = [((my, mz), gm["shaft_d"] + 1.0)]
        if t is S.QUARTER:
            holes.append((qrel_shaft(), STUD_D + parts.FITS.running))      # the quarter release shaft
        mplate = plate_solid(mp_x, outline, holes=holes)
        for dz in (-4.5, 4.5):
            mplate -= x_rod(1.8, mp_x[0] - 1, mp_x[1] + 1, (my, mz + dz))
        a.add(f"{tag}_motor_plate", mplate, material="PETG", group="strike", print_up=(1, 0, 0),
              note="the gearmotor's face screws to it (2 × M1.6); it hangs from the deck")
        for x_, y_ in ((f"{tag}_motor", f"{tag}_motor_plate"), (f"{tag}_motor_plate", "deck")):
            a.allow(x_, y_)
        # lock switch outside the shaft's largest cam or gear, its roller lever reaching in to the lock cam
        if t is S.HOUR:
            ls_c, ls_a = (k[0] - 14.5 - SWITCH["h"] / 2, k[1]), 90.0
        else:
            ls_c, ls_a = (k[0], k[1] + 14.5 + SWITCH["h"] / 2), 0.0
        ls_x = L["lock"][0] - 0.4 if t is S.HOUR else L["lock"][0]
        a.add(f"{tag}_lock_switch", switch_solid(ls_c, ls_x, ls_a), material="black", printed=False,
              group="strike", note="subminiature roller microswitch [E]: its roller drops into the lock cam's notch "
                                   "at the rest angle")
        # home opto and the rack's vane
        arms, oc = opto_solid(t)
        a.add(f"{tag}_home_opto", arms, material="black", printed=False, group="strike",
              note="Vishay TCST1202: the rack's vane blocks it only when the rack is home (gathered)")
        data[tag] = {"shaft": [round(v, 2) for v in k], "motor": [round(v, 2) for v in L["motor"]],
                     "opto": [round(v, 2) for v in oc]}
    # the cue switch (quarters)
    Lq = lay["quarter"]
    kq = Lq["shaft"]
    a.add("quarter_cue_switch", switch_solid((kq[0], kq[1] - 14.5 - SWITCH["h"] / 2), Lq["cue"][0]),
          material="black", printed=False, group="strike", note="E1's cue: closed once per pair [E]")
    # plates: the middle and right strike plates
    kh = lay["hour"]["shaft"]
    hk_h = S.hook_geometry(S.HOUR)
    mid = [(-25.0, -108.0), (36.0, -108.0), (36.0, -47.0), (-25.0, -47.0)]
    a.add("strike_plate_middle", plate_solid(MIDDLE_X, mid, holes=[(kh, seat), (kq, seat), (p, STUD_D + parts.FITS.press),
                                                                   (hk_h["pivot"], STUD_D + parts.FITS.press),
                                                                   (TRIP["shaft"], TRIP_D + parts.FITS.running),
                                                                   (trip_stop_centre(), PIN_D + parts.FITS.press)]),
          material="PETG", group="strike", print_up=(1, 0, 0),
          note="hangs from the deck: the shafts' bearings, the hour train's studs, the hour trip shaft and its stop")
    hk_q = S.hook_geometry(S.QUARTER)
    right = [(-24.0, -108.0), (24.0, -108.0), (24.0, -79.0), (28.5, -79.0), (28.5, -65.0), (24.0, -65.0), (24.0, -47.0),
             (-14.0, -47.0), (-14.0, -59.0), (-24.0, -59.0)]
    a.add("strike_plate_right", plate_solid(RIGHT_X, right, holes=[(kq, seat), (p, STUD_D + parts.FITS.press),
                                                                   (hk_q["pivot"], STUD_D + parts.FITS.press),
                                                                   (TRIP["shaft"], TRIP_D + parts.FITS.running),
                                                                   (qrel_shaft(), STUD_D + parts.FITS.running)]),
          material="PETG", group="strike", print_up=(1, 0, 0),
          note="hangs from the deck: the quarter shaft's bearing, the quarter studs and both release shafts")
    for nm in ("strike_plate_middle", "strike_plate_right"):
        a.allow(nm, "deck"); a.allow(nm, "rack_stud")
    # the guards: a fixed pin under each pawl's tail lifts the pawl at the end of the return stroke
    for t, plate_x, plate in ((S.HOUR, -26.0, "state_plate_left"), (S.QUARTER, MIDDLE_X[1], "strike_plate_middle")):
        g = guard_point(t)
        x1 = x_of(t, "pawl")[1]
        a.add(f"{t.name}_guard", x_rod(2.0, min(plate_x, x1), max(plate_x, x1), g), material="steel", printed=False,
              group="strike", note="Ø2 pin: holds the gathering pawl out of the teeth at rest, so the rack can fall")
        a.allow(f"{t.name}_guard", plate); a.allow(f"{t.name}_guard", f"{t.name}_pawl")
    # the witness Hall's bracket, from the middle plate, under the hour snail's back
    ys, zs = S.arbor_yz()
    wb = Polygon([(-25.0, zs - 15.0), (-21.0, zs - 15.0), (-21.0, zs - 11.0), (-25.0, zs - 11.0)])
    a.add("witness_bracket", yz_solid(wb, -18.5, MIDDLE_X[0]) + yz_solid(
        Polygon([(ys - 4.0, zs - 15.0), (-21.0, zs - 15.0), (-21.0, zs - 11.0), (ys - 4.0, zs - 11.0)]), -18.5, -16.0),
          material="PETG", group="strike", note="carries the witness Hall beside the hour snail")
    a.allow("witness_bracket", "strike_plate_middle"); a.allow("witness_bracket", "witness_hall")
    for t in S.TRAINS:
        tag = t.name
        plate = "strike_plate_middle" if t is S.HOUR else "strike_plate_right"
        a.allow(f"{tag}_hook_stud", plate)
    for i, plate in ((0, "state_plate_left"), (1, "strike_plate_middle")):
        a.allow(f"hour_strike_bearing_{i}", plate)
    for i, plate in ((0, "strike_plate_middle"), (1, "strike_plate_right")):
        a.allow(f"quarter_strike_bearing_{i}", plate)
    a.allow("hour_strike_shaft", "state_plate_left"); a.allow("hour_strike_shaft", "strike_plate_middle")
    a.allow("quarter_strike_shaft", "strike_plate_middle"); a.allow("quarter_strike_shaft", "strike_plate_right")
    return data


# ------------------------------------------------------------------------------------------------ the releases
REL_GAP = 0.4                                # each release arm clears its hook (or the hook's tab) by this at rest
REL_W = 2.5                                  # the release arms' width
SLEEVE_R = 2.4                               # the release arms' hub sleeves (they locate the shafts along X)
QREL_Z = -72.0                               # the quarter release shaft's height
FOLLOWER = dict(t=5.0, block=(5.0, 4.0), pin_in=3.0)   # the follower: thickness (X), its top block (Y, Z), and
#                                                        how deep its Ø2 pin is pressed in
TRIP = dict(shaft=(19.0, -67.0),             # the hour trip shaft (y, z)
            pin_r=28.0, pin_deg=-13.0,       # the quarter rack's trip pin: radius and angle at home (from +Y)
            gap3=0.6,                        # at three pairs the pin clears arm A by this
            shoe=(6.5, 12.0),                # arm A's level shoe over the pin's path (y range)
            b_len=8.5,                       # arm B, along the line from the shaft to the hour hook's pivot
            tab_len=7.5, tab_w=2.4,          # the hour hook's tab, toward the trip shaft
            stop_at=4.5)                     # the rest stop's place along arm B
TRIP_X_A = (21.8, 24.0)                      # arm A, beside the quarter rack (its +X face is at x_rack + 1.5)
TRIP_D = 2.0                                 # the trip shaft: Ø2, light, so its weight's friction stays small
TRIP_LUMP = 3.8                              # arm A's counterweight (radius): the shaft's rest bias
HOUR_TAIL_LUMP = 4.0                         # the hour hook's tail lump: it also balances the tab


def _rot(pt, centre, ang):
    c, s_ = math.cos(ang), math.sin(ang)
    d = (pt[0] - centre[0], pt[1] - centre[1])
    return (centre[0] + c * d[0] - s_ * d[1], centre[1] + s_ * d[0] + c * d[1])


def qrel_shaft():
    """The quarter release shaft (y, z): the follower's arm stands upright half way through its stroke [D]."""
    P = S.G.plan()["program"]
    r0, r1 = S.RELEASE_GROOVE_R
    return (P[1] + (r0 + r1) / 2, QREL_Z)


def qrel_pin_ref():
    """The follower pin's centre at rest (y, z), half way up the groove, under its rest radius."""
    P = S.G.plan()["program"]
    return (P[1] + S.RELEASE_GROOVE_R[0], S.RELEASE_DISC_Z[0] + S.RELEASE_GROOVE["depth"] / 2)


def qrel_rest_tilt() -> float:
    """The follower's lean at rest (rad, toward +Y): it stands upright half way through its stroke."""
    q, b = qrel_shaft(), qrel_pin_ref()
    return math.asin((b[0] - q[0]) / math.dist(q, b))


def qrel_turn(theta: float) -> float:
    """The quarter release shaft's turn (rad, CCW seen from +X, from rest) at program angle theta [D]."""
    P = S.G.plan()["program"]
    q, b = qrel_shaft(), qrel_pin_ref()
    arm = math.dist(q, b)
    a_rest = math.asin((b[0] - q[0]) / arm)
    a_now = math.asin((P[1] + S.release_groove_radius(theta) - q[0]) / arm)
    return a_rest - a_now


def qrel_arm_poly():
    """The release arm beside the quarter hook (rest pose): up from the shaft, then a finger toward -Y whose end
    stands REL_GAP off the hook's weighted tail, at the tail's height."""
    q = qrel_shaft()
    hk = S.hook_geometry(S.QUARTER)
    tail = S._add(hk["pivot"], (hk["pivot"][0] - hk["tip"][0], hk["pivot"][1] - hk["tip"][1]), TAIL_LEN)
    face_y = tail[0] + TAIL_LUMP + REL_GAP
    return unary_union([disc(q, 3.0), path([q, (q[0], tail[1]), (face_y + REL_W / 2, tail[1])], REL_W)])


def qrel_follower_solids():
    """The follower and its Ø2 steel pin, at rest: drawn upright (the pin straight up into the groove, half way
    through the stroke), then leaned to the rest radius. The pin is round, so the groove's slope never pinches it."""
    P = S.G.plan()["program"]
    q, b = qrel_shaft(), qrel_pin_ref()
    up = (q[0], q[1] + math.dist(q, b))                       # the pin's reference point, upright
    bw, bh = FOLLOWER["block"]
    top = S.RELEASE_DISC_Z[0] - 0.5                           # the block's top, under the disc
    block = Polygon([(up[0] - bw / 2, top - bh), (up[0] + bw / 2, top - bh), (up[0] + bw / 2, top),
                     (up[0] - bw / 2, top)])
    body = unary_union([disc(q, 3.0), bar(q, (up[0], top - bh + 1.0), REL_W), block])
    fx = (P[0] - FOLLOWER["t"] / 2, P[0] + FOLLOWER["t"] / 2)
    sol = yz_solid(body, *fx)
    pin_top = S.RELEASE_DISC_Z[0] + S.RELEASE_GROOVE["depth"] - 0.2
    pin_z0 = top - FOLLOWER["pin_in"]
    pin = bd.Cylinder(PIN_D / 2, pin_top - pin_z0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(
        bd.Location((P[0], up[0], pin_z0)))
    hole = bd.Cylinder((PIN_D + parts.FITS.press) / 2, pin_top - pin_z0, align=(bd.Align.CENTER, bd.Align.CENTER,
                                                                                 bd.Align.MIN)).moved(
        bd.Location((P[0], up[0], pin_z0)))
    axis = bd.Axis((0, q[0], q[1]), (1, 0, 0))
    lean = -math.degrees(qrel_rest_tilt())                     # CW: the rest radius is the larger one
    return (sol - hole).rotate(axis, lean), pin.rotate(axis, lean)


def trip_pin_centre(theta: float, frame: bool = False):
    """The quarter rack's trip pin (y, z) with the rack at angle theta; frame=True gives it in the rack's own frame
    (theta = 0), as the rack's outline is drawn."""
    p = S.pivot()
    th0 = S.rack_angles(S.QUARTER)[0]
    a = math.radians(TRIP["pin_deg"]) + ((0.0 if frame else theta) - th0)
    return S._add(p, S.unit(a), TRIP["pin_r"])


def trip_lobe_poly(t: S.TrainSpec):
    """The quarter rack's lobe for the trip pin (rack frame): from the rim's CCW end (its spare tooth) on to the
    pin. Only CCW of the rim, so the hook and the pawl never meet it."""
    p = S.pivot()
    th0 = S.rack_angles(t)[0]
    g0 = S.ALPHA_H - th0 + S.tooth_angle(t)                    # the spare tooth's face, rack frame
    pin = trip_pin_centre(th0, frame=True)
    gp = math.atan2(pin[1] - p[1], pin[0] - p[0])
    r0, r1 = TRIP["pin_r"] - 2.4, TRIP["pin_r"] + 2.2
    arc = [S._add(p, S.unit(g), r1) for g in np.linspace(g0, gp, 12)]
    arc += [S._add(p, S.unit(g), r0) for g in np.linspace(gp, g0, 12)]
    return Polygon(arc).buffer(0).union(disc(pin, 2.6))


def trip_axis():
    """The unit vector from the trip shaft to the hour hook's pivot, and its CCW normal (the side arm B lies on)."""
    sh, h = TRIP["shaft"], S.hook_geometry(S.HOUR)["pivot"]
    d = math.dist(sh, h)
    u = ((h[0] - sh[0]) / d, (h[1] - sh[1]) / d)
    return u, (-u[1], u[0])


def trip_arm_a_poly():
    """Arm A (rest pose): from the shaft to a level shoe over the trip pin's path, its underside gap3 above the pin
    at three pairs; a lump on the shoe keeps the shaft on its stop."""
    sh = TRIP["shaft"]
    c3 = trip_pin_centre(S.rack_angles(S.QUARTER)[3])
    zc = c3[1] + PIN_D / 2 + TRIP["gap3"] + REL_W / 2
    y0, y1 = TRIP["shoe"]
    lump = disc(((y0 + y1) / 2, zc + REL_W / 2 + TRIP_LUMP - 1.3), TRIP_LUMP)
    return unary_union([disc(sh, 3.0), path([sh, (y1, zc), (y0, zc)], REL_W), lump])


def trip_arm_b_off() -> float:
    """Arm B runs parallel to the shaft-to-pivot line, this far to its CCW-normal side: REL_GAP off the tab."""
    return TRIP["tab_w"] / 2 + REL_W / 2 + REL_GAP


def trip_arm_b_poly():
    """Arm B (rest pose): a short dog-leg out of the hub, then along the shaft-to-pivot line, beside the hour hook's
    tab (on its CCW-normal side); its end is the contact."""
    u, n = trip_axis()
    sh = TRIP["shaft"]
    off = trip_arm_b_off()
    knee = S._add(S._add(sh, u, 2.0), n, off)
    tip = S._add(S._add(sh, u, TRIP["b_len"]), n, off)
    return unary_union([disc(sh, 3.0), path([sh, knee, tip], REL_W)])


def trip_tab_poly():
    """The hour hook's tab: from its pivot toward the trip shaft."""
    u, _ = trip_axis()
    h = S.hook_geometry(S.HOUR)["pivot"]
    return bar(h, S._add(h, u, -TRIP["tab_len"]), TRIP["tab_w"])


def trip_stop_centre():
    """The trip shaft's rest stop (a Ø2 pin): arm B leans on it, the shaft's weight turning it CCW."""
    u, n = trip_axis()
    return S._add(S._add(TRIP["shaft"], u, TRIP["stop_at"]), n, trip_arm_b_off() + REL_W / 2 + PIN_D / 2)


def _push_turn(pusher, hook_poly_, centre, hi=0.6):
    """The least CCW turn of a hook (about centre) that clears a pusher: where the pusher leaves it [D]."""
    lo = 0.0
    if not pusher.intersects(hook_poly_):
        return 0.0
    for _ in range(50):
        m = (lo + hi) / 2
        if pusher.intersects(rot_about(hook_poly_, centre, m)):
            lo = m
        else:
            hi = m
    return hi


def qrel_hook_turn(theta: float) -> float:
    """How far the quarter release arm turns the quarter hook out at program angle theta [D]."""
    q = qrel_shaft()
    arm = rot_about(qrel_arm_poly(), q, qrel_turn(theta))
    return _push_turn(arm, hook_poly(S.QUARTER), S.hook_geometry(S.QUARTER)["pivot"])


def trip_turn(theta_q: float) -> float:
    """How far (rad, CW seen from +X) the quarter rack's pin, the rack at angle theta_q, turns the trip shaft [D]."""
    sh = TRIP["shaft"]
    pin = disc(trip_pin_centre(theta_q), PIN_D / 2)
    arm = trip_arm_a_poly()
    if not arm.intersects(pin):
        return 0.0
    lo, hi = 0.0, 0.6
    for _ in range(50):
        m = (lo + hi) / 2
        if rot_about(arm, sh, -m).intersects(pin):
            lo = m
        else:
            hi = m
    return hi


def trip_hook_turn(theta_q: float) -> float:
    """How far the trip turns the hour hook out with the quarter rack at angle theta_q [D]."""
    arm = rot_about(trip_arm_b_poly(), TRIP["shaft"], -trip_turn(theta_q))
    return _push_turn(arm, hook_poly(S.HOUR), S.hook_geometry(S.HOUR)["pivot"])


def trip_balance() -> dict:
    """The trip shaft's rest bias [D]: its printed arms' weight moment about the shaft (PLA; negative turns it CCW,
    onto its stop), against the friction of its whole weight (arms and Ø2 steel shaft) in the plates' holes
    [E: μ 0.3 on the shaft's radius]. N·mm."""
    sh = TRIP["shaft"]
    moment = mass = 0.0
    for poly, tk in ((trip_arm_a_poly(), TRIP_X_A[1] - TRIP_X_A[0]), (trip_arm_b_poly(), S.X_PLANES["hook"][1] - S.X_PLANES["hook"][0])):
        moment += poly.area * tk * (poly.centroid.x - sh[0]) * 1.24e-3          # g·mm
        mass += poly.area * tk * 1.24e-3
    shaft_len = RIGHT_X[1] - (S.HOUR.x_rack + S.X_PLANES["hook"][0])
    mass += math.pi * TRIP_D ** 2 / 4 * shaft_len * 7.85e-3                      # g
    g = 9.81e-3                                                                   # N per g
    return {"torque": -moment * g, "friction": 0.3 * mass * g * TRIP_D / 2, "mass_g": mass}


def add_releases(a):
    """The quarter release (from the walk's program shaft) and the hour trip (from the quarter rack)."""
    P = S.G.plan()["program"]
    q = qrel_shaft()
    hx = x_of(S.QUARTER, "hook")
    fx = (P[0] - FOLLOWER["t"] / 2, P[0] + FOLLOWER["t"] / 2)
    a.add("quarter_release_shaft", x_rod(STUD_D, hx[0], fx[1], q), material="steel", printed=False, group="strike",
          note="Ø3 ground rod in the right strike plate and the quarter motor plate: the walk's release groove "
               "rocks it")
    arm = yz_solid(qrel_arm_poly(), *hx) + yz_solid(disc(q, SLEEVE_R), hx[1] - 0.01, RIGHT_X[0] - 0.4)
    a.add("quarter_release_arm", arm - x_rod(STUD_D + parts.FITS.press, hx[0] - 1, RIGHT_X[0], q), group="strike",
          print_up=(1, 0, 0), note="pressed on the release shaft: in phase A it pushes the quarter hook's weighted "
                                    "tail, and the hook turns out")
    mpx = QUARTER_MOTOR_PLATE_X
    fol, fpin = qrel_follower_solids()
    fol = fol + yz_solid(disc(q, SLEEVE_R), mpx[1] + 0.4, fx[0] + 0.01)
    a.add("quarter_release_follower", fol - x_rod(STUD_D + parts.FITS.press, mpx[1], fx[1] + 1, q), group="strike",
          print_up=(-1, 0, 0), note="pressed on the release shaft: its Ø2 pin runs in the release disc's groove")
    a.add("quarter_release_follower_pin", fpin, material="steel", printed=False, group="strike",
          note="Ø2 steel pin pressed upright in the follower's block: it runs in the release groove")
    for x_, y_ in (("quarter_release_arm", "quarter_release_shaft"),
                   ("quarter_release_follower", "quarter_release_shaft"),
                   ("quarter_release_follower_pin", "quarter_release_follower"),
                   ("quarter_release_shaft", "strike_plate_right"), ("quarter_release_shaft", "quarter_motor_plate")):
        a.allow(x_, y_)
    # the hour trip
    sh = TRIP["shaft"]
    bx = x_of(S.HOUR, "hook")
    a.add("hour_trip_shaft", x_rod(TRIP_D, bx[0], RIGHT_X[1], sh), material="steel", printed=False, group="strike",
          note="Ø2 steel rod turning in the middle and right strike plates: the quarter rack's pin rocks it at the "
               "fourth quarter")
    arm_a = yz_solid(trip_arm_a_poly(), *TRIP_X_A) + yz_solid(disc(sh, SLEEVE_R), TRIP_X_A[1] - 0.01, RIGHT_X[0] - 0.4)
    a.add("hour_trip_arm_a", arm_a - x_rod(TRIP_D + parts.FITS.press, TRIP_X_A[0] - 1, RIGHT_X[0], sh), group="strike",
          print_up=(1, 0, 0), note="pressed on the trip shaft: the quarter rack's pin lifts its shoe past three pairs")
    arm_b = yz_solid(trip_arm_b_poly(), *bx) + yz_solid(disc(sh, SLEEVE_R), bx[1] - 0.01, MIDDLE_X[0] - 0.4)
    a.add("hour_trip_arm_b", arm_b - x_rod(TRIP_D + parts.FITS.press, bx[0] - 1, MIDDLE_X[0], sh), group="strike",
          print_up=(1, 0, 0), note="pressed on the trip shaft: pushes the hour hook's tab, and the hook turns out")
    a.add("hour_trip_stop", x_rod(PIN_D, bx[0], MIDDLE_X[1], trip_stop_centre()), material="steel", printed=False,
          group="strike", note="Ø2 pin pressed in the middle plate: arm B rests on it")
    for x_, y_ in (("hour_trip_arm_a", "hour_trip_shaft"), ("hour_trip_arm_b", "hour_trip_shaft"),
                   ("hour_trip_shaft", "strike_plate_middle"), ("hour_trip_shaft", "strike_plate_right"),
                   ("hour_trip_stop", "strike_plate_middle"), ("hour_trip_stop", "hour_trip_arm_b")):
        a.allow(x_, y_)
    return {"quarter_release_shaft": [round(v, 2) for v in q], "hour_trip_shaft": list(sh),
            "trip_pin_home": [round(v, 2) for v in trip_pin_centre(S.rack_angles(S.QUARTER)[0])]}


# ------------------------------------------------------------------------------------------------ for the tests
def snail_solid(t: S.TrainSpec, when: float):
    """The snail at a given time: minutes (quarter snail) or hours (hour snail)."""
    ys, zs = S.arbor_yz()
    if t is S.QUARTER:
        fn, period, rot, bore = S.quarter_snail_radius, 60.0, D.ARBOR_SENSE * 6.0 * when, 5.0 + parts.FITS.press
    else:
        fn, period, rot, bore = S.hour_snail_radius, 12.0, D.ARBOR_SENSE * 30.0 * when, 7.0 + parts.FITS.press
    shape = D.arbor_cam(fn, period, 4.0, bore).rotate(bd.Axis.Z, rot)
    return D.on_x(shape, t.x_rack - 2.0, ys, zs)


def centroid_offset(poly, pivot_yz):
    """(dy, dz) of a polygon's centroid from a pivot: dy > 0 puts its weight on the +Y side."""
    c = poly.centroid
    return (c.x - pivot_yz[0], c.y - pivot_yz[1])


def hook_poly(t: S.TrainSpec):
    """The hook's outline: arm to the tip, hub, and a weighted tail past the pivot (its weight turns the tip into
    the teeth)."""
    hk = S.hook_geometry(t)
    q, tip = hk["pivot"], hk["tip"]
    tail = S._add(q, (q[0] - tip[0], q[1] - tip[1]), TAIL_LEN)
    lump = HOUR_TAIL_LUMP if t is S.HOUR else TAIL_LUMP
    parts_ = [bar(q, tip, 2.4), disc(q, 3.0), disc(tail, lump), bar(q, tail, 2.4)]
    if t is S.HOUR:
        parts_.append(trip_tab_poly())                       # the hour trip's arm B pushes it
    return unary_union(parts_)


def pawl_poly(t: S.TrainSpec):
    fg = S.feed_geometry(t)
    q, tip = fg["pin"], fg["tip"]
    tail = S._add(q, (q[0] - tip[0], q[1] - tip[1]), PAWL_TAIL)
    return unary_union([bar(q, tip, 2.4), disc(q, 2.8), disc(tail, TAIL_LUMP), bar(q, tail, 2.4)])


def yz_plot(path):
    """Both trains seen along X: each rack at home and at its full count, the snail's largest step, the hook, the
    pawl, the strike shaft and its largest cam; the release arm (quarters) or the trip's arms (hours), at rest and
    released."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(14, 6.5))
    for ax, t in zip(axes, S.TRAINS):
        ys, zs = S.arbor_yz()
        p = S.pivot()

        def draw(poly, **kw):
            polys = list(poly.geoms) if hasattr(poly, "geoms") else [poly]
            for pg in polys:
                x, y = pg.exterior.xy
                ax.fill(x, y, alpha=kw.pop("alpha", 0.35), **kw)

        ax.add_patch(plt.Circle((ys, zs), max(S.snail_radii(t)), fill=False, ls="--", lw=0.8))
        th = S.rack_angles(t)
        for ang, col, lab in ((th[0], "tab:blue", "home"), (th[-1], "tab:cyan", f"count {t.counts}")):
            draw(rot_about(rack_poly_body(t), p, ang).union(rot_about(rack_poly_rim(t), p, ang)), color=col)
            ax.plot([], [], color=col, lw=6, alpha=0.4, label=f"rack, {lab}")
        draw(hook_poly(t), color="tab:red")
        draw(rot_about(pawl_poly(t), S.feed_geometry(t)["pin"], 0.25), color="tab:purple")
        k = S.feed_geometry(t)["shaft"]
        ax.add_patch(plt.Circle(k, LIFT_R[1], fill=False, color="k", lw=0.8))
        ax.plot(*k, "k+")
        if t is S.QUARTER:
            q = qrel_shaft()
            turn = max(qrel_turn(a_) for a_ in range(0, 360, 2))
            draw(qrel_arm_poly(), color="tab:green")
            draw(rot_about(qrel_arm_poly(), q, turn), color="tab:olive", alpha=0.25)
            ax.plot([], [], color="tab:green", lw=6, alpha=0.4, label="release arm (rest; olive: releasing)")
            draw(disc(trip_pin_centre(th[0]), PIN_D / 2), color="k")
            draw(disc(trip_pin_centre(th[-1]), PIN_D / 2), color="k")
            draw(trip_arm_a_poly(), color="tab:orange")
            ax.plot([], [], color="tab:orange", lw=6, alpha=0.4, label="hour trip arm A, the trip pin (black)")
        else:
            sh = TRIP["shaft"]
            draw(trip_arm_b_poly(), color="tab:orange")
            draw(rot_about(trip_arm_b_poly(), sh, -trip_turn(S.rack_angles(S.QUARTER)[-1])), color="tab:brown",
                 alpha=0.25)
            draw(disc(trip_stop_centre(), PIN_D / 2), color="k")
            ax.plot([], [], color="tab:orange", lw=6, alpha=0.4, label="hour trip arm B (rest; brown: tripped), stop")
        ax.axhline(-47, color="k", lw=1)
        ax.set_title(f"{t.name} train (x {t.x_rack:+.1f}): the hook red, the pawl purple (held out)")
        ax.set_xlabel("y (mm)"); ax.set_ylabel("z (mm)")
        ax.set_aspect("equal"); ax.grid(True, lw=0.3); ax.set_xlim(-60, 60); ax.set_ylim(-115, -42)
        ax.legend(fontsize=7, loc="lower left")
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)
