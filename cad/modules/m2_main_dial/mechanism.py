"""M2 main-dial mechanism, detailed design (v1 built, v1.5 provisions reserved).

Built on the accepted feasibility layout (docs/main-dial-feasibility.md) and Paul's decisions of
3 Nov 2026: spur differentials with **60:1 worm** correction inputs, all of M2 in one design,
two-colour printed dial.

Kinematic chain (signs: + = counter-clockwise seen from the front):

    motor --12/48--> R1 --12/72--> I (daily arbor, 1 rev per mean day)
    I --80/80--> S --[Sun differential: sun A on S, carrier = worm wheel, sun B on the S sleeve]
        sleeve --48/48--> Sun tube (Sun hand + disc)
        sleeve --48/48--> shadow tube (Earth-shadow arm), in step with the Sun
    I --154/169--> J --[Moon differential on J]--> J sleeve --88/83--> Moon tube (Moon hand)
    I --12/84--> W (weekday output to M7, 1 rev per 7 days)

Both hands get an even number of reversals from I, so they turn the same way (checked below).
The motor's direction is set in firmware so the hands turn clockwise.

v1.5 provisions present in v1: all six centre tubes and their wheels (cam, sunrise and sunset tubes
held by lock pins); bearing seats for lay shafts C (cam, node differential) and R (sunrise/sunset);
space for the year train and node differential; worm inputs for M3.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import build123d as bd

from cad.lib import parts
from cad.lib.assembly import BED_DUAL, BED_SINGLE, Assembly, write_dae
from cad.lib.differential import SpurDifferential
from cad.lib.gears import Gear, centre_distance, mesh_rotation, pair_shifts, spur_gear
from cad.lib.hardware import BEARINGS, tube_stack
from cad.lib.worm import Worm, place_worm, worm_centre_distance, worm_solid, worm_wheel
from cad.modules.m2_main_dial import feasibility as F

M = F.M
FACE = 4.0
FACE_MOTOR = 6.0            # D4: motor stages
M_MOTOR = 1.25              # D4: 1.0–1.25 in the motor reductions
GAP = 2.0
WORM = Worm()               # m 1, d1 12, single start: 4.76° lead, self-locking
WORM_TEETH = 60

# --- arbor positions (front view, mm) -------------------------------------------------------------
O = (0.0, 0.0)
S = F.polar(48.0, 150.0)                       # Sun lay shaft (48/48 to the Sun and shadow tubes)
J = F.polar(85.5, -30.0)                       # Moon intermediate (88/83)
C_V15 = F.polar(48.0, 60.0)                    # cam lay shaft (v1.5), seat reserved
R_V15 = F.polar(48.0, 100.0)                   # sunrise/sunset lay shaft (v1.5), seat reserved


def _circle_intersection(p, rp, q, rq, pick_lower=True):
    d = math.dist(p, q)
    a = (rp ** 2 - rq ** 2 + d ** 2) / (2 * d)
    h = math.sqrt(rp ** 2 - a ** 2)
    ex = ((q[0] - p[0]) / d, (q[1] - p[1]) / d)
    m = (p[0] + a * ex[0], p[1] + a * ex[1])
    c1 = (m[0] + h * ex[1], m[1] - h * ex[0])
    c2 = (m[0] - h * ex[1], m[1] + h * ex[0])
    return min(c1, c2, key=lambda c: c[1]) if pick_lower else max(c1, c2, key=lambda c: c[1])


I = _circle_intersection(J, centre_distance(Gear(154), Gear(169)), S, centre_distance(Gear(84), Gear(84)))
W = (S[0] + 48.0 * math.cos(math.radians(135)), S[1] + 48.0 * math.sin(math.radians(135)))
R1 = (I[0] + 52.5 * math.cos(math.radians(250)), I[1] + 52.5 * math.sin(math.radians(250)))
MOTOR = (R1[0] + 37.5 * math.cos(math.radians(200)), R1[1] + 37.5 * math.sin(math.radians(200)))

# --- levels (z, mm; dial face = 0) ----------------------------------------------------------------
FP = (-15.0, -11.0)
POINTER_WINDOW = (168.0, 192.0, 140.0, 177.0)  # front-plate cut-out (a0, a1, r0, r1) for the calendar readers
CENTRE = {}                                   # tube -> wheel level, outermost tube first
_z = FP[0] - GAP
for _n in ["sunset", "sunrise", "sun", "cam", "moon", "shadow"]:
    CENTRE[_n] = (_z - FACE, _z)
    _z -= FACE + GAP
BRIDGE = (_z - 3.0, _z)                       # (-56, -53)
DIFF = SpurDifferential(plate=3.0)
DIFF_TOTAL = DIFF.levels()["total"][1] - 3.0 + 6.0   # plate 2 is the 6 mm worm wheel
DIFF_FRONT = BRIDGE[0] - 1.0                  # diff ends just behind the bridge plane
DIFF_Z0 = DIFF_FRONT - DIFF_TOTAL
BIG = (DIFF_Z0 - GAP - FACE, DIFF_Z0 - GAP)   # 154/169
L80 = (BIG[0] - GAP - FACE, BIG[0] - GAP)     # 84/84 (I -> S)
RED2 = (L80[0] - GAP - FACE_MOTOR, L80[0] - GAP)    # 12/72 (R1 -> I)
RED1 = (RED2[0] - GAP - FACE_MOTOR, RED2[0] - GAP)  # 12/48 (motor -> R1)
BP = (RED1[0] - GAP - 4.0, RED1[0] - GAP)     # back plate
BRIDGE_DIR = 20.0                             # bridge pillars clear S, C, R and J
WEEKDAY = RED2                                # 12 on S, 84 on W, beside the reduction


def at(shape, xy, z=0.0):
    return shape.moved(bd.Location((xy[0], xy[1], z)))


def ang(p, q):
    return math.degrees(math.atan2(q[1] - p[1], q[0] - p[0]))


def gear_at(g: Gear, xy, level, rot=0.0, bore=5.0, fit="press"):
    part = spur_gear(g, level[1] - level[0]) - parts.disc(bore + getattr(parts.FITS, fit), 50, z0=-20)
    return at(part.rotate(bd.Axis.Z, rot), xy, level[0])


def build():
    a = Assembly("m2_main_dial")
    rep = {"positions": {}, "levels": {}, "meshes": [], "directions": {}, "notes": [], "v15_reserved": []}
    rep["positions"] = {k: [round(v[0], 2), round(v[1], 2)] for k, v in
                        dict(O=O, S=S, J=J, I=I, W=W, R1=R1, motor=MOTOR, C_v15=C_V15, R_v15=R_V15).items()}
    rep["levels"] = {"front_plate": FP, **{f"centre_{k}": v for k, v in CENTRE.items()}, "bridge": BRIDGE,
                     "differentials": (round(DIFF_Z0, 2), round(DIFF_FRONT, 2)), "154_169": BIG, "80_80": L80,
                     "reduction_12_72": RED2, "reduction_12_48": RED1, "back_plate": BP}

    def mesh(z1, z2, p1, p2, rot1=0.0, m=M, x=(0.0, 0.0), label=""):
        g1, g2 = Gear(z1, m, shift=x[0]), Gear(z2, m, shift=x[1])
        cd = centre_distance(g1, g2)
        assert abs(math.dist(p1, p2) - cd) < 1e-6, (label, math.dist(p1, p2), cd)
        r2 = mesh_rotation(g1, g2, ang(p1, p2), rot1)
        rep["meshes"].append({"pair": label, "teeth": f"{z1}/{z2}", "centre_distance": round(cd, 3)})
        return g1, g2, r2

    # ------------------------------------------------------------------ dial, hemisphere, centre stack
    a.add("dial_field", parts.disc(F.DIAL_D, 3.0, bore=10.5, z0=-3.0), material="dial", group="front",
          note="two-colour print: azure field; the silver hour ring is dial.py")
    names = ["shadow", "moon", "cam", "sun", "sunrise", "sunset"]
    tubes = dict(zip(names, tube_stack(3.0, len(names))))
    th = {"sunset": F.HAND_T, "sunrise": F.HAND_T, "sun": F.HAND_T, "cam": 2.0,
          "moon": max(3.0, F.MOON_DISC + 0.6), "shadow": F.HAND_T}
    front = {}
    z = 0.0
    for n in ["sunset", "sunrise", "sun", "cam", "moon", "shadow"]:
        front[n] = (z + F.LEVEL_GAP, z + F.LEVEL_GAP + th[n])
        z = front[n][1]
    hemi_z0 = z + F.LEVEL_GAP
    hemi_d = 2 * (F.CAM_MEAN_R + F.LAT_EXCURSION / 2 + 4)
    a.add("hemisphere_dome", F.shallow_dome(hemi_d, F.HEMI_H, hemi_z0), material="silver", group="front")
    a.add("fixed_arbor", parts.rod(3.0, hemi_z0 - BRIDGE[0]).moved(bd.Location((0, 0, BRIDGE[0]))),
          material="steel", printed=False, group="centre")
    a.allow("fixed_arbor", "hemisphere_dome")
    centre_teeth = {"sunset": 48, "sunrise": 48, "sun": 48, "cam": 48, "moon": 83, "shadow": 48}
    for n, t in tubes.items():
        z_back = CENTRE[n][0]
        a.add(f"tube_{n}", at(parts.tube(t, front[n][1] - z_back), O, z_back), material="brass", printed=False,
              group="centre")
        a.allow(f"tube_{n}", "fixed_arbor")
        a.allow(f"tube_{n}", "dial_field")
        a.allow(f"tube_{n}", "front_plate")
    for i_, n1 in enumerate(names):
        for n2 in names[i_ + 1:]:
            a.allow(f"tube_{n1}", f"tube_{n2}")
    a.allow("fixed_arbor", "dial_field")
    a.allow("fixed_arbor", "front_plate")

    # Sun lay shaft S: input from I (80/80) behind; sun A of the differential on S; output sleeve
    g_i80, g_s80, r_s80 = mesh(84, 84, I, S, label="I -> S, mean Sun")
    sleeve_t = tube_stack(5.0, 1)[0]
    sun_rot = {}
    g_sl48, g_c48, r_c48 = mesh(48, 48, S, O, label="S sleeve -> Sun tube (and shadow tube)")
    for n in ("sun", "shadow"):
        a.add(f"wheel_{n}", gear_at(g_c48, O, CENTRE[n], rot=r_c48, bore=tubes[n].od), group="centre_wheels",
              explode=(0, 0, -30))
        a.add(f"S_sleeve_{n}_48", gear_at(g_sl48, S, CENTRE[n], bore=sleeve_t.od), group="trains")
        a.allow(f"wheel_{n}", f"tube_{n}")
        a.allow(f"S_sleeve_{n}_48", "S_sleeve")
    # J: 88/83 to the Moon tube; 169 from I's 154
    g_j88, g_m83, r_m83 = mesh(88, 83, J, O, label="J sleeve -> Moon tube")
    a.add("wheel_moon", gear_at(g_m83, O, CENTRE["moon"], rot=r_m83, bore=tubes["moon"].od), group="centre_wheels",
          explode=(0, 0, -30))
    a.allow("wheel_moon", "tube_moon")
    a.add("J_sleeve_88", gear_at(g_j88, J, CENTRE["moon"], bore=sleeve_t.od), group="trains")
    a.allow("J_sleeve_88", "J_sleeve")
    g_i154, g_j169, r_j169 = mesh(154, 169, I, J, label="I -> J (Moon train stage 1)")
    a.add("I_154", gear_at(g_i154, I, BIG), group="trains", explode=(0, 0, -60))
    a.add("J_169", gear_at(g_j169, J, BIG, rot=r_j169), group="trains", explode=(0, 0, -60))
    a.add("I_84", gear_at(g_i80, I, L80), group="trains", explode=(0, 0, -70))
    a.add("S_84", gear_at(g_s80, S, L80, rot=r_s80), group="trains", explode=(0, 0, -70))
    # idle centre wheels (v1.5 tubes), held by lock pins in v1
    for n in ("cam", "sunrise", "sunset"):
        a.add(f"wheel_{n}", gear_at(Gear(48), O, CENTRE[n], bore=tubes[n].od), group="centre_wheels",
              explode=(0, 0, -30), note="v1: locked by a pin; v1.5: driven")
        a.allow(f"wheel_{n}", f"tube_{n}")
        p = F.polar(14.0, 45.0 + 40.0 * names.index(n))
        a.add(f"lock_pin_{n}", at(parts.rod(2.0, (FP[0] + 2.0) - (CENTRE[n][0] - 1.0)), p, CENTRE[n][0] - 1.0),
              material="steel", printed=False, group="centre",
              note="v1 lock pin through the idle wheel into the front plate")
        a.allow(f"lock_pin_{n}", f"wheel_{n}")
        a.allow(f"lock_pin_{n}", "front_plate")
        for other in ("sunset", "sunrise", "sun", "cam"):
            if other != n:
                a.allow(f"lock_pin_{n}", f"wheel_{other}")
    for n in names:
        for m_ in names:
            if names.index(m_) < names.index(n):      # inner tubes pass through outer wheels' bores
                a.allow(f"wheel_{n}", f"tube_{m_}")
    for n in names:
        a.allow(f"wheel_{n}", "fixed_arbor")

    # ------------------------------------------------------------------ differentials with worm inputs
    def differential(tag, xy, input_name, output_sleeve_front_z, worm_side_angle):
        d = DIFF
        lv = d.levels(DIFF_Z0)
        dp = d.parts(z0=DIFF_Z0, sun_bore=5.0)
        for nm, shp in dp.items():
            a.add(f"{tag}_{nm}", at(shp, xy), group="differentials", explode=(0, 0, -45))
        a.allow(f"{tag}_sun_A", f"shaft_{tag}")
        a.allow(f"{tag}_sun_B", f"{tag}_sleeve")
        a.allow(f"{tag}_sun_B", f"shaft_{tag}")
        pins = d.pin_positions()
        p1 = parts.disc(2 * d.outer_radius + 2, lv["plate1"][1] - lv["plate1"][0], bore=5.0 + parts.FITS.running,
                        z0=lv["plate1"][0])
        ww_z0 = lv["plate2"][0]
        ww = worm_wheel(WORM_TEETH, WORM, 6.0, bore=sleeve_t.od + parts.FITS.running).moved(bd.Location((0, 0, ww_z0)))
        for (px, py) in pins:
            p1 -= parts.disc(3.0 + parts.FITS.press, 10, z0=lv["plate1"][0] - 2).moved(bd.Location((px, py, 0)))
            ww -= parts.disc(3.0 + parts.FITS.press, 10, z0=ww_z0 - 2).moved(bd.Location((px, py, 0)))
        a.add(f"{tag}_carrier_plate", at(p1, xy), group="differentials", explode=(0, 0, -55))
        a.add(f"{tag}_carrier_worm_wheel", at(ww, xy), group="differentials", explode=(0, 0, -35),
              note="60 T worm wheel = carrier (correction input)")
        for k, (px, py) in enumerate(pins):
            pin = parts.rod(3.0, ww_z0 + 6.0 - lv["plate1"][0]).moved(bd.Location((px, py, lv["plate1"][0])))
            a.add(f"{tag}_pin_{k}", at(pin, xy), material="steel", printed=False, group="differentials")
            a.allow(f"{tag}_pin_{k}", f"{tag}_carrier_plate")
            a.allow(f"{tag}_pin_{k}", f"{tag}_carrier_worm_wheel")
            for pl in dp:
                if pl.startswith("planet"):
                    a.allow(f"{tag}_pin_{k}", f"{tag}_{pl}")
        a.allow(f"{tag}_carrier_plate", f"shaft_{tag}")
        a.allow(f"{tag}_carrier_worm_wheel", f"{tag}_sleeve")
        # output sleeve: brass tube from sun B forward to the output gears
        z_s0 = lv["level3"][0]
        a.add(f"{tag}_sleeve", at(parts.tube(sleeve_t, output_sleeve_front_z - z_s0), xy, z_s0), material="brass",
              printed=False, group="differentials")
        a.allow(f"{tag}_sleeve", f"shaft_{tag}")
        a.allow(f"{tag}_sleeve", "front_plate")
        # worm on its own Ø5 shaft, in the plane of the worm wheel, pointing to the right (M3)
        worm = worm_solid(WORM, 24.0, bore=5.0).moved(bd.Location((0, 0, -12)))
        wp = place_worm(worm, WORM_TEETH, WORM, 6.0, wheel_axis_xy=xy, z0=ww_z0, side_angle=worm_side_angle)
        a.add(f"{tag}_worm", wp, group="differentials", print_up=(1, 0, 0), nozzle=0.2,
              note="60:1, self-locking: the v1 lock. Prints axis vertical; the thread's lower flank is a "
                   "70° overhang 2 mm deep, so use fine layers (0.1 mm) and check it on a test print")
        wa = worm_centre_distance(WORM_TEETH, WORM)
        cx = xy[0] + wa * math.cos(math.radians(worm_side_angle))
        cy = xy[1] + wa * math.sin(math.radians(worm_side_angle))
        x_end = 135.0
        shaft = bd.Cylinder(2.5, x_end - (cx - 25), align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(
            bd.Axis.Y, 90).moved(bd.Location((cx - 25, cy, ww_z0 + 3.0)))
        a.add(f"{tag}_worm_shaft", shaft, material="steel", printed=False, group="interfaces",
              note=f"M3 correction input: dog coupling at x = {x_end:.0f}")
        a.allow(f"{tag}_worm_shaft", f"{tag}_worm")
        for k, bx in enumerate((cx - 19, cx + 19)):
            blk = bd.Box(10, 12, 12, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).moved(
                bd.Location((bx, cy, ww_z0 + 3.0)))
            blk -= bd.Cylinder(2.5, 12).rotate(bd.Axis.Y, 90).moved(bd.Location((bx, cy, ww_z0 + 3.0)))
            a.add(f"{tag}_worm_block_{k}", blk, material="PETG", group="differentials", print_up=(1, 0, 0),
                  note="pillow block with an MR85ZZ, bolted to a standoff from the back plate")
            a.allow(f"{tag}_worm_block_{k}", f"{tag}_worm_shaft")
        rep["notes"].append(f"{tag} worm axis at ({cx:.1f}, {cy:.1f}), z {ww_z0 + 3:.1f}; shaft to x = {x_end:.0f}")
        return lv

    a.add("shaft_S", at(parts.rod(5.0, FP[1] - BP[0]), S, BP[0]), material="steel", printed=False, group="shafts")
    a.add("shaft_J", at(parts.rod(5.0, FP[1] - BP[0]), J, BP[0]), material="steel", printed=False, group="shafts")
    a.add("shaft_I", at(parts.rod(5.0, FP[1] - BP[0]), I, BP[0]), material="steel", printed=False, group="shafts")
    a.add("shaft_W", at(parts.rod(5.0, FP[1] - (BP[0] - 25.0)), W, BP[0] - 25.0), material="steel", printed=False,
          group="shafts", note="weekday output: keyed coupling to M7 behind the back plate")
    a.add("shaft_R1", at(parts.rod(5.0, RED2[1] + 2 - BP[0]), R1, BP[0]), material="steel", printed=False,
          group="shafts")
    lv_s = differential("S", S, "S_84", CENTRE["sun"][1], 90.0)
    lv_j = differential("J", J, "J_169", CENTRE["moon"][1], -90.0)
    for g_, sh in (("S_84", "shaft_S"), ("J_169", "shaft_J"), ("I_84", "shaft_I"), ("I_154", "shaft_I")):
        a.allow(g_, sh)
    for g_ in ("S_sleeve_sun_48", "S_sleeve_shadow_48"):
        a.allow(g_, "shaft_S")
    a.allow("J_sleeve_88", "shaft_J")
    # the sun A gears are fixed to their shafts (they are the differential inputs)
    rep["notes"].append("Sun A of each differential is pinned to its shaft (input); sun B is pressed on the sleeve")

    # ------------------------------------------------------------------ reduction, motor, weekday
    sx, sy = pair_shifts(12, 72)
    g12b, g72, r72 = mesh(12, 72, R1, I, m=M_MOTOR, x=(sx, sy), label="R1 -> I (reduction 2)")
    a.add("I_72", gear_at(g72, I, RED2, rot=r72), group="drive", explode=(0, 0, -80))
    a.add("R1_12", gear_at(g12b, R1, RED2), group="drive", explode=(0, 0, -80))
    sx, sy = pair_shifts(12, 48)
    g12a, g48, r48 = mesh(12, 48, MOTOR, R1, m=M_MOTOR, x=(sx, sy), label="motor -> R1 (reduction 1)")
    a.add("R1_48", gear_at(g48, R1, RED1, rot=r48), group="drive", explode=(0, 0, -90))
    a.add("motor_pinion_12", gear_at(g12a, MOTOR, RED1), group="drive", explode=(0, 0, -90))
    for g_, sh in (("I_72", "shaft_I"), ("R1_12", "shaft_R1"), ("R1_48", "shaft_R1")):
        a.allow(g_, sh)
    motor = bd.Box(42.3, 42.3, 48.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
    a.add("motor_nema17", at(motor, MOTOR, BP[0]), material="black", printed=False, group="drive")
    a.add("motor_shaft", at(parts.rod(5.0, RED1[1] - BP[0] + 1), MOTOR, BP[0]), material="steel", printed=False,
          group="drive")
    a.allow("motor_shaft", "motor_pinion_12")
    a.allow("motor_shaft", "back_plate")
    a.allow("motor_shaft", "motor_nema17")
    sx, sy = pair_shifts(12, 84)
    g12w, g84, r84 = mesh(12, 84, S, W, x=(sx, sy), label="S -> W (weekday)")
    a.add("S_12_weekday", gear_at(g12w, S, (WEEKDAY[0], WEEKDAY[0] + FACE)), group="trains")
    a.add("W_84", gear_at(g84, W, (WEEKDAY[0], WEEKDAY[0] + FACE), rot=r84), group="trains")
    a.allow("S_12_weekday", "shaft_S")
    a.allow("W_84", "shaft_W")

    # ------------------------------------------------------------------ hands (v1) with collet hubs
    def hand(name, tube_name, length, deg, width, mat, tail=12.0):
        t = tubes[tube_name]
        z0 = front[tube_name][0]
        h = parts.hand(length, width, F.HAND_T if tube_name != "moon" else 2.0, t.od + 5, t.od, tail=tail,
                       z0=z0).rotate(bd.Axis.Z, deg)
        a.add(name, h, material=mat, group="hands", explode=(0, 0, 30),
              note="split-collet hub: friction clutch on the tube (architecture §7)")
        a.allow(name, f"tube_{tube_name}")
        for inner in names[: names.index(tube_name)]:
            a.allow(name, f"tube_{inner}")
        a.allow(name, "fixed_arbor")
        return z0

    sun_deg, moon_deg = 60.0, 150.0
    z_sun = hand("hand_sun", "sun", F.SUN_HAND, sun_deg, 3.0, "dial")
    a.add("sun_disc", at(parts.disc(F.SUN_DISC, F.HAND_T), F.polar(F.SUN_HAND, sun_deg), z_sun), material="PLA",
          group="hands", explode=(0, 0, 30))
    a.allow("sun_disc", "hand_sun")
    z_moon = hand("hand_moon", "moon", F.SUN_HAND + 6, moon_deg, 4.0, "silver")
    ball = bd.Sphere(F.MOON_DISC / 2).moved(bd.Location((*F.polar(F.SUN_HAND, moon_deg), z_moon + th["moon"] / 2)))
    a.add("moon_ball", ball, material="silver", group="hands", explode=(0, 0, 30))
    a.allow("moon_ball", "hand_moon")
    z_sh = hand("arm_shadow", "shadow", F.SUN_HAND, sun_deg + 180, 2.5, "black")
    a.add("shadow_disc", at(parts.disc(F.SHADOW_DISC, F.HAND_T), F.polar(F.SUN_HAND, sun_deg + 180), z_sh),
          material="black", group="hands", explode=(0, 0, 30))
    a.allow("shadow_disc", "arm_shadow")

    # ------------------------------------------------------------------ sensors
    a.add("magnet_index_I154", at(parts.disc(5.0, 2.0, z0=BIG[1] - 1.5), (I[0] + 30.0, I[1])), material="silver",
          printed=False, group="sensors", note="index: local mean midnight")
    a.allow("magnet_index_I154", "I_154")
    a.add("hall_index", at(bd.Box(8, 6, 3, align=(bd.Align.CENTER,) * 3), (I[0] + 30.0, I[1]), BIG[1] + 2.5),
          material="green", printed=False, group="sensors")
    a.add("magnet_witness_moon", at(parts.disc(5.0, 2.0, z0=CENTRE["moon"][0] + 1.0), F.polar(32.0, 200.0)),
          material="silver", printed=False, group="sensors", note="witness: once per lunar day")
    a.allow("magnet_witness_moon", "wheel_moon")
    a.add("hall_witness_moon", at(bd.Box(8, 6, 3, align=(bd.Align.CENTER,) * 3), F.polar(32.0, 200.0),
                                  CENTRE["moon"][0] - 2.0), material="green", printed=False, group="sensors")

    # ------------------------------------------------------------------ v1.5 space claims
    for nm, xy, zr, d_, note in (
            ("v15_cam_drive_C", C_V15, CENTRE["cam"], 50.0, "48/48 to the cam tube (v1.5)"),
            ("v15_sunrise_sectors_R", R_V15, (CENTRE["sunrise"][0], CENTRE["sunset"][1]), 50.0,
             "sunrise/sunset 48/48 + reversing idler (v1.5)")):
        claim = at(parts.disc(d_, zr[1] - zr[0], z0=zr[0]), xy)
        a.add(nm, claim, material="ghost", printed=False, group="v15", note=note)
        rep["v15_reserved"].append(nm)
        a.allow(nm, "front_plate")
        a.allow(nm, f"wheel_{'cam' if 'cam' in nm else 'sunset'}")
        a.allow(nm, f"wheel_{'cam' if 'cam' in nm else 'sunrise'}")
    a.allow("v15_cam_drive_C", "wheel_cam")
    a.allow("v15_sunrise_sectors_R", "wheel_sunset")
    a.allow("v15_sunrise_sectors_R", "wheel_sunrise")

    # ------------------------------------------------------------------ plates, bridge, pillars
    seat = BEARINGS["MR85ZZ"]
    union_pts = [O, S, J, I, W, R1, C_V15, R_V15, (MOTOR[0] - 22, MOTOR[1] - 22), (MOTOR[0] + 22, MOTOR[1] + 22)]
    xs = [p[0] for p in union_pts]
    ys = [p[1] for p in union_pts]
    pad = 22.0
    fw, fh = max(xs) - min(xs) + 2 * pad, max(ys) - min(ys) + 2 * pad
    fc = ((max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2)
    fp = at(parts.plate((fw, fh), FP[1] - FP[0], z0=FP[0], corner_radius=8), fc)
    fp -= parts.disc(tubes["sunset"].od + 0.4, 10, z0=FP[0] - 1)            # centre stack passes through
    for p in (S, J, I, W):
        fp -= at(parts.disc(seat.od + parts.FITS.bearing_seat, seat.width + 1, z0=FP[0] - 1), p)
        fp -= at(parts.disc(seat.od - 2, 10, z0=FP[0] - 1), p)
    for p in (C_V15, R_V15):                                                 # reserved, drilled undersize
        fp -= at(parts.disc(3.0, 10, z0=FP[0] - 1), p)
    # window for the calendar pointer's readers (stop lever and its opto, 1 March witness), which sit
    # at 9 o'clock on the carrier and reach back through the plate (calendar.py, POINTER_ANGLE)
    a0, a1, r0, r1 = POINTER_WINDOW
    th = [math.radians(a0 + (a1 - a0) * k / 8) for k in range(9)]
    win = [(r1 * math.cos(t), r1 * math.sin(t)) for t in th] + [(r0 * math.cos(t), r0 * math.sin(t)) for t in th[::-1]]
    fp -= bd.extrude(bd.Face(bd.Wire.make_polygon([bd.Vector(x, y, FP[0] - 1) for x, y in win], close=True)),
                     amount=FP[1] - FP[0] + 2, dir=(0, 0, 1))
    # notch in the lower edge for E6's star-jumper wire holder at the station: its glued length runs
    # back across the plate's edge (calendar.py, e6.py)
    from shapely.geometry import Polygon as _Poly
    from cad.modules.m2_main_dial import e6 as _E6, setter as _ST
    jg = _E6.jumper_geometry()
    notch = _Poly(_ST.clamp_outline(jg["anchor"], jg["contact"], 3.0)).buffer(0.6, join_style=2)
    fp -= bd.extrude(bd.Face(bd.Wire.make_polygon([bd.Vector(x, y, FP[0] - 1) for x, y in list(notch.exterior.coords)[:-1]],
                                                  close=True)), amount=FP[1] - FP[0] + 2, dir=(0, 0, 1))
    a.add("front_plate", fp, material="PETG", group="plates", explode=(0, 0, 15))
    bw, bh, bc = fw, fh, fc                                                  # same outline as the front plate
    bp = at(parts.plate((bw, bh), BP[1] - BP[0], z0=BP[0], corner_radius=8), bc)
    for p in (S, J, I, W, R1):
        bp -= at(parts.disc(seat.od + parts.FITS.bearing_seat, seat.width + 1, z0=BP[1] - seat.width), p)
        bp -= at(parts.disc(seat.od - 2, 10, z0=BP[0] - 1), p)
    bp -= at(parts.disc(22.5, 10, z0=BP[0] - 1), MOTOR)                     # NEMA 17 boss
    for dx in (-15.5, 15.5):
        for dy in (-15.5, 15.5):
            bp -= at(parts.disc(3.4, 10, z0=BP[0] - 1), (MOTOR[0] + dx, MOTOR[1] + dy))
    a.add("back_plate", bp, material="PETG", group="plates", explode=(0, 0, -110))
    bridge = parts.plate((150.0, 14.0), BRIDGE[1] - BRIDGE[0], z0=BRIDGE[0]).rotate(bd.Axis.Z, BRIDGE_DIR)
    bridge -= parts.disc(3.0 + parts.FITS.press, 10, z0=BRIDGE[0] - 1)
    a.add("bridge", bridge, material="PETG", group="plates", explode=(0, 0, -50))
    a.allow("bridge", "fixed_arbor")
    for k, p in enumerate((F.polar(70, BRIDGE_DIR), F.polar(70, BRIDGE_DIR + 180))):
        a.add(f"bridge_pillar_{k}", at(parts.standoff(FP[0] - BRIDGE[1], od=8.0), p, BRIDGE[1]), material="PETG",
              group="plates")
        a.allow(f"bridge_pillar_{k}", "bridge")
        a.allow(f"bridge_pillar_{k}", "front_plate")
    # main pillars: free points near the plate edges, clear of every gear, shaft, worm and block
    obstacles = []
    for it in a.items:
        if it.group in ("plates", "front", "hands", "centre") or it.name.startswith(("tube_", "lock_pin")):
            continue
        bb = it.shape.bounding_box()
        if bb.max.Z < BP[1] - 0.1 or bb.min.Z > FP[0] + 0.1:
            continue
        cx_, cy_ = (bb.min.X + bb.max.X) / 2, (bb.min.Y + bb.max.Y) / 2
        if it.name.endswith("worm_shaft"):
            obstacles.append(("line", bb.min.X, bb.max.X, cy_, 3.0))
        else:
            obstacles.append(("disc", cx_, cy_, max(bb.size.X, bb.size.Y) / 2))
    obstacles.append(("disc", 0.0, 0.0, 44.0))                    # centre wheels incl. the 83 T

    def clearance(p):
        best = 1e9
        for ob in obstacles:
            if ob[0] == "disc":
                best = min(best, math.dist(p, (ob[1], ob[2])) - ob[3])
            else:
                dx = 0.0 if ob[1] <= p[0] <= ob[2] else min(abs(p[0] - ob[1]), abs(p[0] - ob[2]))
                best = min(best, math.hypot(dx, p[1] - ob[3]) - ob[4])
        return best

    x0, x1 = max(fc[0] - fw / 2, bc[0] - bw / 2) + 7, min(fc[0] + fw / 2, bc[0] + bw / 2) - 7
    y0, y1 = max(fc[1] - fh / 2, bc[1] - bh / 2) + 7, min(fc[1] + fh / 2, bc[1] + bh / 2) - 7
    cands = [(x0 + (x1 - x0) * i / 60, y0 + (y1 - y0) * j / 45) for i in range(61) for j in range(46)]
    cands = [p for p in cands if clearance(p) > 5.5]
    rep["notes"].append(f"pillar search: {len(cands)} free grid points in x {x0:.0f}..{x1:.0f}, y {y0:.0f}..{y1:.0f}")
    chosen = []
    for target in ((x0, y0), (x1, y0), (x0, y1), (x1, y1), ((x0 + x1) / 2, y0), ((x0 + x1) / 2, y1),
                   (x0, (y0 + y1) / 2), (x1, (y0 + y1) / 2)):
        if cands:
            p = min(cands, key=lambda c: math.dist(c, target))
            if all(math.dist(p, q) > 60 for q in chosen) and len(chosen) < 6:
                chosen.append(p)
    rep["notes"].append(f"{len(chosen)} main pillars at {[(round(x, 1), round(y, 1)) for x, y in chosen]}")
    for k, p in enumerate(chosen):
        a.add(f"pillar_{k}", at(parts.standoff(FP[0] - BP[1], od=9.0), p, BP[1]), material="PETG", group="plates")
        a.allow(f"pillar_{k}", "front_plate")
        a.allow(f"pillar_{k}", "back_plate")
    for sh in ("shaft_S", "shaft_J", "shaft_I", "shaft_W", "shaft_R1"):
        a.allow(sh, "front_plate")
        a.allow(sh, "back_plate")
    for tag in ("S", "J"):
        a.allow(f"{tag}_sleeve", "back_plate")

    # ------------------------------------------------------------------ rotation senses (+ = CCW from the front)
    sense = {"motor": 1}
    sense["R1"] = -sense["motor"]
    sense["I"] = -sense["R1"]
    sense["S"] = -sense["I"]
    sense["S_sleeve"] = -sense["S"]            # differential, carrier still: B = -A
    sense["sun_tube"] = -sense["S_sleeve"]
    sense["shadow_tube"] = -sense["S_sleeve"]
    sense["J"] = -sense["I"]
    sense["J_sleeve"] = -sense["J"]
    sense["moon_tube"] = -sense["J_sleeve"]
    sense["W"] = -sense["I"]
    rep["directions"] = sense
    assert sense["sun_tube"] == sense["moon_tube"] == sense["shadow_tube"], "hands must turn the same way"
    rep["notes"].append("Sun, shadow and Moon tubes all turn with sense "
                        f"{sense['sun_tube']:+d} x motor: run the motor so that this is clockwise")
    return a, rep


def check(a: Assembly, rep: dict) -> dict:
    env = a.envelope()
    return {
        "interference": [{"a": x, "b": y, "volume_mm3": round(v, 3)} for x, y, v in a.interference()],
        "bed_fit_single": [r for r in a.bed_fit(BED_SINGLE) if not r["fits"]],
        "bed_fit_dual": [r for r in a.bed_fit(BED_DUAL) if not r["fits"]],
        "envelope": {"x": [round(env.min.X, 1), round(env.max.X, 1)], "y": [round(env.min.Y, 1), round(env.max.Y, 1)],
                     "z": [round(env.min.Z, 1), round(env.max.Z, 1)]},
        "parts": len(a.items),
        "printed": sorted(i.name for i in a.items if i.printed),
        "bought": sorted(i.name for i in a.items if not i.printed and i.group != "v15"),
        **rep,
    }


def main(out_dir="export/m2_main_dial"):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    a, rep = build()
    res = check(a, rep)
    (out / "m2_mechanism.json").write_text(json.dumps(res, indent=2, default=str))
    print(json.dumps({k: res[k] for k in ("interference", "bed_fit_single", "envelope", "parts")}, indent=2))
    renders(a, out)
    return a, res


def renders(a: Assembly, out: Path):
    out.mkdir(parents=True, exist_ok=True)
    a.render(out / "m2_front.png", elev=0, azim=-90, up="y", title="M2, front (hands at a sample time)",
             hide=("v15",), tolerance=0.3)
    a.render(out / "m2_rear.png", elev=18, azim=60, up="y", title="M2, rear three-quarter (plates and dial hidden)",
             hide=("plates", "front", "v15"), tolerance=0.3)
    a.render(out / "m2_exploded.png", exploded=True, elev=14, azim=-140, up="y",
             title="M2, exploded along the arbors (plates hidden)", hide=("plates", "v15"), tolerance=0.3)


if __name__ == "__main__":
    main(*sys.argv[1:])
