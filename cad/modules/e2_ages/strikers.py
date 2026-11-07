"""E2 part 2b: the quarter and hour counting trains in CAD (docs/e2-design.md §12). Geometry: striking.py.

Each train, at rest (rack gathered, the strike shaft at its lock angle):
- the rack on the common stud, its tail finger above the snail, its teeth rim on the far side;
- the feed lever on the same stud, its gathering pawl lifted by the guard, the strap from the eccentric;
- the hook in the hooked tooth's space; the release lever riding on the release cam on the state arbor;
- the strike shaft (Ø5, two MR85ZZ) with its eccentric, lock cam, lifter cam (part 2c takes the lift on), and
  (quarters) the cue cam; a gearmotor drives it through 12/36;
- the lock, home and cue microswitches.

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
ARM_RISE = 5.0                               # the racks' tail arms run this far above the stud (clear of the snails)
MIDDLE_X = (2.0, 5.0)                        # the middle strike plate
RIGHT_X = (27.6, 30.6)                       # the right strike plate
GEAR_TEETH = (12, 36)                        # gearmotor pinion : strike shaft gear
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
    return Point(c).buffer(r, resolution=n // 4)


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
    body = unary_union([arm, finger, weight, spoke, hub]).difference(disc(p, (STUD_D + parts.FITS.running) / 2))
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
    return yz_solid(body, *x_of(t, "rack")) + yz_solid(rim, *x_of(t, "rim"))


def hook_solid(t: S.TrainSpec, lift: float = 0.0):
    """The hook (engaged, or turned out by `lift` radians): body and hub beside the rim, tip finger in the rim's
    right half; a counterweight tail past the pivot keeps it in the teeth."""
    hk = S.hook_geometry(t)
    q, tip = hk["pivot"], hk["tip"]
    tail = S._add(q, (q[0] - tip[0], q[1] - tip[1]), 0.6)
    body = unary_union([bar(q, tip, 2.4), disc(q, 3.0), disc(tail, 2.5), bar(q, tail, 2.4)])
    body = body.difference(disc(q, (STUD_D + parts.FITS.running) / 2))
    finger = disc(tip, 0.6).union(bar(tip, S._add(tip, (q[0] - tip[0], q[1] - tip[1]), 0.25), 1.2))
    body, finger = rot_about(body, q, lift), rot_about(finger, q, lift)
    return yz_solid(body, *x_of(t, "hook")) + yz_solid(finger, x_of(t, "hook_tip")[0], x_of(t, "hook")[0] + 0.01)


def pawl_solid(t: S.TrainSpec, lift: float):
    """The gathering pawl on the feed lever's pin, turned out by `lift` (at rest the guard holds it out)."""
    fg = S.feed_geometry(t)
    q, tip = fg["pin"], fg["tip"]
    tail = S._add(q, (q[0] - tip[0], q[1] - tip[1]), 0.6)
    body = unary_union([bar(q, tip, 2.4), disc(q, 2.8), disc(tail, 2.4), bar(q, tail, 2.4)])
    body = body.difference(disc(q, (PIN_D + parts.FITS.running) / 2))
    finger = disc(tip, 0.6).union(bar(tip, S._add(tip, (q[0] - tip[0], q[1] - tip[1]), 0.25), 1.2))
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


def release_lever_solid(t: S.TrainSpec):
    rg = S.release_geometry(t)
    front, press, stud = rg["front"], rg["press"], rg["stud"]
    nose_f = (front[0], front[1] + 1.2)                     # rides on the cam's base circle
    nose_b = (press[0], press[1] + 1.2 + 0.4)               # 0.4 above the hook's press point at rest
    body = unary_union([path([nose_f, (front[0] + 4.0, front[1] + 4.0), stud, (press[0] - 6.0, press[1] + 1.6),
                              nose_b], 2.4), disc(stud, 3.0), disc(nose_f, 1.2), disc(nose_b, 1.2)])
    body = body.difference(disc(stud, (STUD_D + parts.FITS.running) / 2))
    return yz_solid(body, *x_of(t, "release"))


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
        a.add(f"{tag}_rack", rack_solid(t, th[0]), group="strike",
              note=f"{tag} rack, gathered: its tail falls onto the {tag} snail; {t.counts} teeth of pitch {S.PITCH}")
        a.add(f"{tag}_feed_lever", feed_lever_solid(t), group="strike", note="rocked by the eccentric: gathers one "
              "tooth per turn of the strike shaft")
        pawl_lift = 0.25                                       # held out by the guard at rest [rad]
        a.add(f"{tag}_pawl", pawl_solid(t, pawl_lift), group="strike", note="gathering pawl, on the feed lever's pin")
        a.add(f"{tag}_hook", hook_solid(t, 0.0), group="strike", note="rack hook: holds each gathered tooth")
        a.add(f"{tag}_strap", strap_solid(t), group="strike", note="strap from the eccentric to the feed lever's pin")
        a.add(f"{tag}_eccentric", eccentric_solid(t), group="strike", note=f"throw {S.feed_geometry(t)['eccentric']:.2f} mm")
        a.add(f"{tag}_release_lever", release_lever_solid(t), group="strike",
              note="its nose rides the release cam; the lobe tips it and it presses the hook out")
        fg, hk, rg = S.feed_geometry(t), S.hook_geometry(t), S.release_geometry(t)
        k = fg["shaft"]
        data[tag] = {"shaft_yz": [round(v, 2) for v in k], "hook_pivot": [round(v, 2) for v in hk["pivot"]],
                     "feed_pin": [round(v, 2) for v in fg["pin"]], "release_stud": [round(v, 2) for v in rg["stud"]],
                     "snail_radii": [round(r, 3) for r in S.snail_radii(t)],
                     "rack_angles_deg": [round(math.degrees(v), 2) for v in th]}
        # pins and studs
        a.add(f"{tag}_feed_pin", x_rod(PIN_D, x_of(t, "link")[0], x_of(t, "pawl")[1], fg["pin"]), material="steel",
              printed=False, group="strike", note="Ø2 steel pin pressed in the feed lever")
        hx = (x_of(t, "hook")[0], MIDDLE_X[0] if t is S.HOUR else RIGHT_X[0])
        a.add(f"{tag}_hook_stud", x_rod(STUD_D, hx[0], hx[1], hk["pivot"]), material="steel", printed=False,
              group="strike")
        a.add(f"{tag}_release_stud", x_rod(STUD_D, x_of(t, "release")[0], hx[1], rg["stud"]), material="steel",
              printed=False, group="strike")
        for x_, y_ in ((f"{tag}_pawl", f"{tag}_feed_pin"), (f"{tag}_feed_lever", f"{tag}_feed_pin"),
                       (f"{tag}_strap", f"{tag}_feed_pin"), (f"{tag}_strap", f"{tag}_eccentric"),
                       (f"{tag}_hook", f"{tag}_hook_stud"), (f"{tag}_release_lever", f"{tag}_release_stud"),
                       (f"{tag}_hook", f"{tag}_rack"), (f"{tag}_rack", "rack_stud"), (f"{tag}_feed_lever", "rack_stud"),
                       (f"{tag}_release_lever", f"release_cam_{tag}"), (f"{tag}_release_lever", f"{tag}_hook"),
                       (f"{tag}_rack", f"{tag}_feed_lever"), (f"{tag}_pawl", f"{tag}_feed_lever"),
                       (f"{tag}_strap", f"{tag}_feed_lever")):
            a.allow(x_, y_)
    a.add("rack_stud", x_rod(STUD_D, x_of(S.HOUR, "feed")[0] - 0.5, RIGHT_X[1], p), material="steel", printed=False,
          group="strike", note="Ø3 ground rod: both racks and both feed levers turn on it")
    data["pivot"] = [round(v, 2) for v in p]
    return data
