"""M2 main-dial feasibility study (Phase 2, step 2 of the brief).

Question: does everything the main dial shows, including the v1.5 and v2 provisions (D5), fit
behind and in front of the 287.5 mm dial at 1:8?

This is a *layout* model, not the final design:
- gears are modelled as blanks at their tip diameter (conservative for clearances), placed at
  their true centre distances from ``cad/lib/gears.py``;
- differentials, the motor and the E6 calendar motor are space claims (blocks);
- tubes, rods, plates, hands, the cam and the calendar ring are modelled at their real sizes.

Coordinates: origin at the dial centre on the dial's front face; +X right, +Y up, +Z towards the
viewer. Everything behind the dial has negative Z.

Run:  python -m cad.modules.m2_main_dial.feasibility [out_dir]
"""
from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path

import build123d as bd

from cad.lib import parts
from cad.lib.assembly import BED_DUAL, BED_SINGLE, Assembly
from cad.lib.gears import Gear, centre_distance
from cad.lib.hardware import BEARINGS, tube_stack

M = 1.0              # module (D4 parameter)
FACE = 4.0           # gear face width (D4)
GAP = 2.0            # axial gap between gear levels
HAND_T = 1.5         # hand thickness
LEVEL_GAP = 0.8      # axial gap between hands

# --- 1:8 sizes [S: ELS via envelope.md] -----------------------------------------------------------
DIAL_D = 287.5
RING_OD, RING_W = 341.0, 26.0
SUN_HAND = 125.0                    # "exactement de 1 mètre" / 8
BAY = (-232.0, 232.0, -213.0, 217.0)  # M2 bay [E]: central body 465 mm wide, floor to the weekday rail

# Eclipse display: k = enlargement of the Sun/Moon/shadow discs over true 1:8 scale; the latitude
# excursion is enlarged by the same k so eclipses happen exactly when they should (§ report).
K_DISC = 4.0
SUN_DISC = 9.3 / 8 * K_DISC         # 4.65 mm at k = 4
MOON_DISC = 9.1 / 8 * K_DISC
SHADOW_DISC = 24.3 / 8 * K_DISC
LAT_EXCURSION = 40.4 / 8            # R - r of Schwilgué's latitude cam at true 1:8 (5.05 mm) [S: ELS]
CAM_MEAN_R = 16.75                  # 134 mm / 8: his mean radius keeps the slope at 5/6 x 45° [S: ELS]
LEVER = K_DISC                      # lever on the Moon hand multiplies the cam motion by k


def blank(teeth: int, face: float = FACE, z_back: float = 0.0, bore: float = 5.0):
    """Gear blank: disc at the tip diameter, from z_back to z_back + face."""
    return parts.disc(M * teeth + 2 * M, face, bore=bore, z0=z_back)


def at(shape, xy, z=0.0):
    return shape.moved(bd.Location((xy[0], xy[1], z)))


def polar(r, deg):
    return (r * math.cos(math.radians(deg)), r * math.sin(math.radians(deg)))


@dataclass
class Report:
    tubes: list = field(default_factory=list)
    front_levels: list = field(default_factory=list)
    rear_levels: list = field(default_factory=list)
    shafts: dict = field(default_factory=dict)
    meshes: list = field(default_factory=list)
    notes: list = field(default_factory=list)


def build() -> tuple[Assembly, Report]:
    a = Assembly("m2_main_dial_feasibility")
    rep = Report()

    # ---------------------------------------------------------------- dial, ring, hemisphere
    a.add("dial", parts.disc(DIAL_D, 3.0, bore=10.5, z0=-3.0), material="dial", group="front")
    ring = parts.disc(RING_OD, 3.0, bore=RING_OD - 2 * RING_W, z0=-3.0)
    a.add("calendar_ring", ring, material="PLA", group="ring", note="printed as 4 x 90° segments")
    # ring rides on 6 rollers on a rear flange (688ZZ bearings), at the ring's inner edge
    flange = parts.disc(RING_OD - 2 * RING_W + 8, 6.0, bore=RING_OD - 2 * RING_W, z0=-9.0)
    a.add("ring_flange", flange, group="ring")
    a.allow("calendar_ring", "ring_flange")
    for k, ang in enumerate((210, 270, 330, 30, 90, 150)):
        b = BEARINGS["688ZZ"]
        pos = polar((RING_OD - 2 * RING_W) / 2 - b.od / 2, ang)
        a.add(f"ring_roller_{k}", at(parts.bearing(b), pos, -8.5), material="bearing", printed=False, group="ring")
        a.allow(f"ring_roller_{k}", "ring_flange")
    rep.notes.append("Calendar ring: 6 rollers (688ZZ) bear on a rear flange inside the ring; dial-to-ring radial gap "
                     f"{((RING_OD - 2 * RING_W) - DIAL_D) / 2:.2f} mm")

    # ---------------------------------------------------------------- centre stack
    names = ["shadow", "moon", "cam", "sun", "sunrise", "sunset"]       # inner -> outer
    tubes = dict(zip(names, tube_stack(3.0, len(names))))
    rep.tubes = [{"tube": n, "od": t.od, "id": round(t.id, 2)} for n, t in tubes.items()]

    # front levels, from the dial face outwards (outermost tube = closest to the dial)
    # the Moon level is deep enough to hold the (v1.5 phase) ball centred on the hand
    thickness = {"sunset": HAND_T, "sunrise": HAND_T, "sun": HAND_T, "cam": 2.0,
                 "moon": max(3.0, MOON_DISC + 0.6), "shadow": HAND_T}
    z = 0.0
    front_top = {}
    for n in ["sunset", "sunrise", "sun", "cam", "moon", "shadow"]:
        z0 = z + LEVEL_GAP
        front_top[n] = (z0, z0 + thickness[n])
        rep.front_levels.append({"level": n, "z_from": round(z0, 1), "z_to": round(z0 + thickness[n], 1)})
        z = z0 + thickness[n]
    hemi_z0 = z + LEVEL_GAP
    hemi_d = 2 * (CAM_MEAN_R + LAT_EXCURSION / 2 + 4)               # hides the cam, as in the original
    a.add("hemisphere", parts.disc(hemi_d, 3.0, z0=hemi_z0), material="silver", group="front")
    rep.front_levels.append({"level": "hemisphere", "z_from": round(hemi_z0, 1), "z_to": round(hemi_z0 + 3, 1),
                             "diameter": round(hemi_d, 1)})
    front_depth = hemi_z0 + 3.0

    # rear: movement front plate, then one wheel level per tube (outermost first), then a bridge
    FP = (-15.0, -11.0)
    rear = {}
    zb = FP[0] - GAP
    for n in ["sunset", "sunrise", "sun", "cam", "moon", "shadow"]:
        rear[n] = (zb - FACE, zb)
        rep.rear_levels.append({"level": n, "z_from": rear[n][0], "z_to": rear[n][1]})
        zb -= FACE + GAP
    BRIDGE = (zb - 3.0, zb)          # fixed-arbor bridge just behind the last centre wheel
    BP = (-99.0, -95.0)              # back plate
    BIG = (BRIDGE[0] - GAP - FACE, BRIDGE[0] - GAP)   # big-wheel level behind the bridge

    a.add("fixed_arbor", parts.rod(3.0, hemi_z0 - BRIDGE[0], BRIDGE[0]), material="steel", printed=False, group="centre")
    a.allow("fixed_arbor", "hemisphere")
    centre_teeth = {"sunset": 48, "sunrise": 48, "sun": 48, "cam": 48, "moon": 83, "shadow": 48}
    for n, t in tubes.items():
        z_front = front_top[n][1]
        z_back = rear[n][0]
        a.add(f"tube_{n}", parts.tube(t, z_front - z_back, z_back), material="brass", printed=False, group="centre")
        a.allow(f"tube_{n}", "fixed_arbor")
        wheel = blank(centre_teeth[n], z_back=rear[n][0], bore=t.od)
        a.add(f"wheel_{n}", wheel, group="centre_wheels", explode=(0, 0, -40))
        a.allow(f"wheel_{n}", f"tube_{n}")
    # telescoping tubes touch each other by design (0.10 mm clearance)
    for i, n1 in enumerate(names):
        for n2 in names[i + 1:]:
            a.allow(f"tube_{n1}", f"tube_{n2}")
    for n in names:                                   # every tube passes through the dial and front plate
        a.allow(f"tube_{n}", "dial")
    a.allow("fixed_arbor", "dial")

    # hands and front parts
    def boss_hand(name, length, ang, tube_name, width=3.0, tail=0.0, thick=HAND_T, mat="PLA"):
        t = tubes[tube_name]
        z0 = front_top[tube_name][0]
        h = parts.hand(length, width, thick, t.od + 5, t.od, tail=tail).rotate(bd.Axis.Z, ang)
        a.add(name, at(h, (0, 0), z0), material=mat, group="hands", explode=(0, 0, 25))
        a.allow(name, f"tube_{tube_name}")
        for inner in names[: names.index(tube_name)]:
            a.allow(name, f"tube_{inner}")
        a.allow(name, "fixed_arbor")
        return z0

    sun_ang, moon_ang = 60.0, 150.0
    boss_hand("hand_sunset", 138, -90 + 112.5, "sunset", width=2.0, mat="silver")
    boss_hand("hand_sunrise", 138, -90 - 112.5, "sunrise", width=2.0, mat="silver")
    z_sun = boss_hand("hand_sun", SUN_HAND, sun_ang, "sun", mat="dial")
    a.add("sun_disc", at(parts.disc(SUN_DISC, HAND_T), polar(SUN_HAND, sun_ang), z_sun), material="PLA", group="hands",
          explode=(0, 0, 25))
    a.allow("sun_disc", "hand_sun")
    # latitude cam: concentric plate, R and r around Schwilgué's mean radius (scaled)
    cam_t = tubes["cam"]
    cam = parts.radial_cam(lambda th: CAM_MEAN_R + LAT_EXCURSION / 2 * math.sin(th), 2.0, cam_t.od)
    a.add("latitude_cam", at(cam, (0, 0), front_top["cam"][0]), group="hands", explode=(0, 0, 25))
    a.allow("latitude_cam", "tube_cam")
    for inner in names[: names.index("cam")]:
        a.allow("latitude_cam", f"tube_{inner}")
    a.allow("latitude_cam", "fixed_arbor")
    # Moon hand with radial slide and amplifying lever (k x cam motion at the ball)
    z_moon = boss_hand("hand_moon", SUN_HAND + 6, moon_ang, "moon", width=5.0, thick=3.0, mat="silver")
    ball = bd.Sphere(MOON_DISC / 2).moved(bd.Location((*polar(SUN_HAND, moon_ang), z_moon + thickness["moon"] / 2)))
    a.add("moon_ball", ball, material="silver", group="hands", explode=(0, 0, 25))
    a.allow("moon_ball", "hand_moon")
    # shadow arm: on the innermost tube, in front of the Moon, opposite the Sun
    z_sh = boss_hand("arm_shadow", SUN_HAND, sun_ang + 180, "shadow", width=2.5, mat="black")
    a.add("shadow_disc", at(parts.disc(SHADOW_DISC, HAND_T), polar(SUN_HAND, sun_ang + 180), z_sh),
          material="black", group="hands", explode=(0, 0, 25))
    a.allow("shadow_disc", "arm_shadow")

    # ---------------------------------------------------------------- plates and bridge
    fp_outline = (2 * 128.0, 2 * 128.0)
    a.add("front_plate", parts.plate(fp_outline, FP[1] - FP[0], z0=FP[0], holes=[(0, 0, 10.5)]),
          material="PETG", group="plates", explode=(0, 0, -10))
    for n in names:
        a.allow(f"tube_{n}", "front_plate")
    a.allow("fixed_arbor", "front_plate")
    bridge_dir = 105.0
    p1, p2 = polar(70, bridge_dir), polar(70, bridge_dir + 180)
    bridge = parts.plate((150.0, 14.0), BRIDGE[1] - BRIDGE[0], z0=BRIDGE[0]).rotate(bd.Axis.Z, bridge_dir)
    a.add("bridge", bridge, material="PETG", group="plates", explode=(0, 0, -60))
    a.allow("bridge", "fixed_arbor")
    for k, p in enumerate((p1, p2)):
        a.add(f"bridge_pillar_{k}", at(parts.standoff(FP[0] - BRIDGE[1], od=8.0), p, BRIDGE[1]),
              material="PETG", group="plates")
        a.allow(f"bridge_pillar_{k}", "bridge")
        a.allow(f"bridge_pillar_{k}", "front_plate")

    # ---------------------------------------------------------------- lay shafts
    def shaft(name, xy, z_from, z_to, d=5.0):
        a.add(f"shaft_{name}", at(parts.rod(d, z_to - z_from), xy, z_from), material="steel", printed=False,
              group="shafts")
        rep.shafts[name] = {"xy": [round(xy[0], 1), round(xy[1], 1)], "z": [z_from, z_to]}
        for plate_name in ("front_plate", "back_plate", "bridge"):
            a.allow(f"shaft_{name}", plate_name)

    def gear_on(shaft_name, xy, teeth, level, name, explode=(0, 0, -40)):
        a.add(name, at(blank(teeth, z_back=level[0]), xy), group="rear_gears", explode=explode)
        a.allow(name, f"shaft_{shaft_name}")

    def mesh(n1, z1, n2, z2):
        cd = centre_distance(Gear(z1, M), Gear(z2, M))
        rep.meshes.append({"driver": n1, "driven": n2, "teeth": f"{z1}/{z2}", "centre_distance": cd})
        return cd

    # Sun: lay shaft S drives the Sun tube and the shadow tube 1:1 (equal 48/48 pairs keep them in step);
    # the Sun differential (v1 keyed, v1.5 fed by M3) sits on S in the front levels.
    S = polar(mesh("S", 48, "sun", 48), 60)
    shaft("S", S, BP[1], FP[0])
    gear_on("S", S, 48, rear["sun"], "S_sun_48")
    gear_on("S", S, 48, rear["shadow"], "S_shadow_48")
    a.allow("S_sun_48", "wheel_sun"); a.allow("S_shadow_48", "wheel_shadow")
    diff_s = at(parts.disc(40.0, 2 * FACE + 2 * GAP, z0=rear["sunrise"][0]), S)
    a.add("diff_sun", diff_s, group="rear_gears", note="spur differential, space claim; keyed in v1")
    a.allow("diff_sun", "shaft_S")

    # latitude cam drive (v1.5): lay shaft C, 1:1 to the cam tube, node differential (Sun + eclipse-year term)
    C = polar(mesh("C", 48, "cam", 48), 150)
    shaft("C", C, BP[1], FP[0])
    gear_on("C", C, 48, rear["cam"], "C_cam_48")
    a.allow("C_cam_48", "wheel_cam")
    a.add("diff_node", at(parts.disc(40.0, 2 * FACE + 2 * GAP, z0=rear["sunrise"][0]), C), group="rear_gears",
          note="node differential, v1.5 space claim")
    a.allow("diff_node", "shaft_C")

    # Moon: M2.moon_hand = 154/169 x 88/83. 83 on the Moon tube; 88 + 169 on J; 154 on the daily arbor I.
    J = polar(mesh("J", 88, "moon", 83), -30)
    cd_ij = mesh("I", 154, "J", 169)
    # place I on the circle of radius cd_ij around J, towards the lower left
    phi = math.radians(207.0)
    I = (J[0] + cd_ij * math.cos(phi), J[1] + cd_ij * math.sin(phi))
    shaft("J", J, BP[1], FP[0])
    shaft("I", I, BP[1], FP[0])
    gear_on("J", J, 88, rear["moon"], "J_88")
    a.allow("J_88", "wheel_moon")
    gear_on("J", J, 169, BIG, "J_169", explode=(0, 0, -80))
    gear_on("I", I, 154, BIG, "I_154", explode=(0, 0, -80))
    a.allow("J_169", "I_154")
    a.add("diff_moon", at(parts.disc(44.0, 2 * FACE + 2 * GAP, z0=rear["sun"][0]), J), group="rear_gears",
          note="Moon differential on J between the 169 and the 88, space claim; keyed in v1")
    a.allow("diff_moon", "shaft_J")

    # sunrise / sunset: year train 15/99 x 13/97 x 12/89 from I to the year arbor Y3, which carries the
    # yearly cam; a follower turns sector shaft R, which drives the two hand tubes in opposite senses.
    R = polar(mesh("R", 48, "sunset", 48), 240)
    shaft("R", R, BP[1], FP[0])
    gear_on("R", R, 48, rear["sunset"], "R_sunset_48")
    gear_on("R", R, 48, rear["sunrise"], "R_sunrise_48")
    a.allow("R_sunset_48", "wheel_sunset"); a.allow("R_sunrise_48", "wheel_sunrise")
    lv = (BP[1] + GAP, BP[1] + GAP + FACE)              # deep levels near the back plate
    lv2 = (lv[1] + GAP, lv[1] + GAP + FACE)
    lv3 = (lv2[1] + GAP, lv2[1] + GAP + FACE)
    Y1 = (I[0] - mesh("I", 15, "Y1", 99), I[1])
    Y2 = (Y1[0] + 10.0, Y1[1] + math.sqrt(mesh("Y1", 13, "Y2", 97) ** 2 - 10.0 ** 2))
    cd_y3 = mesh("Y2", 12, "Y3", 89)
    Y3 = (Y2[0] + cd_y3 * math.cos(math.radians(60)), Y2[1] + cd_y3 * math.sin(math.radians(60)))
    for nm, p in (("Y1", Y1), ("Y2", Y2)):
        shaft(nm, p, BP[1], BIG[0] - GAP)
    # Y3 is a stub arbor on a cock: a full-length arbor would pass through Y2's 97-tooth wheel
    shaft("Y3", Y3, lv3[0] - 1.0, BIG[0] - GAP)
    rep.notes.append("Year arbor Y3 is a stub arbor on a cock (a through arbor would cross Y2's 97-tooth wheel)")
    gear_on("I", I, 15, lv, "I_15")
    gear_on("Y1", Y1, 99, lv, "Y1_99"); gear_on("Y1", Y1, 13, lv2, "Y1_13")
    gear_on("Y2", Y2, 97, lv2, "Y2_97"); gear_on("Y2", Y2, 12, lv3, "Y2_12")
    gear_on("Y3", Y3, 89, lv3, "Y3_89")
    for p, q in (("I_15", "Y1_99"), ("Y1_13", "Y2_97"), ("Y2_12", "Y3_89")):
        a.allow(p, q)
    yc = parts.radial_cam(lambda th: 26 + 6 * math.cos(th), 4.0, 5.0)
    a.add("year_cam", at(yc, Y3, lv3[1] + GAP), group="rear_gears", note="sunrise/sunset cam (Bordeaux), v1.5")
    a.allow("year_cam", "shaft_Y3")

    # weekday output to M7 (12/84 from I) and the M3 correction inputs (two Ø5 shafts, right side)
    M3S, M3M = (110.0, 45.0), (110.0, -10.0)
    a.add("M3_input_sun", at(parts.rod(5.0, 40.0), M3S, BP[0] - 30.0), material="steel", printed=False,
          group="interfaces", note="v1.5 Sun correction input: keyed dog coupling on the back plate, right side")
    a.add("M3_input_moon", at(parts.rod(5.0, 40.0), M3M, BP[0] - 30.0), material="steel", printed=False,
          group="interfaces", note="v1.5 Moon correction input")

    # motor (NEMA 17, 42 x 42 x 48) behind the back plate, 24:1 printed reduction to I between plates
    motor = bd.Box(42.3, 42.3, 48.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
    MOT = (I[0] - 60.0, I[1] + 10.0)
    a.add("motor", at(motor, MOT, BP[0]), material="black", printed=False, group="drive")
    a.add("E6_calendar_motor", at(bd.Box(25, 25, 40, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)),
                                  polar(160, 245), -12.0), material="black", printed=False, group="ring",
          note="E6 event motor, space claim")

    # back plate: shaft footprint + margin (it must hold bearing seats, so it is printed, not wood: D12)
    xs = [v["xy"][0] for v in rep.shafts.values()] + [MOT[0] - 21.2, MOT[0] + 21.2, M3S[0], M3M[0]]
    ys = [v["xy"][1] for v in rep.shafts.values()] + [MOT[1] - 21.2, MOT[1] + 21.2, M3S[1], M3M[1]]
    mx = 14.0
    w, h = max(xs) - min(xs) + 2 * mx, max(ys) - min(ys) + 2 * mx
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    a.add("back_plate", at(parts.plate((w, h), BP[1] - BP[0], z0=BP[0]), (cx, cy)), material="PETG",
          group="plates", explode=(0, 0, -120))
    for n in rep.shafts:
        a.allow(f"shaft_{n}", "back_plate")
    a.allow("M3_input_sun", "back_plate"); a.allow("M3_input_moon", "back_plate")
    rep.notes.append(f"Back plate {w:.0f} x {h:.0f} mm (printed PETG; holds bearing seats)")
    rep.notes.append(f"Front of dial: {front_depth:.1f} mm to the hemisphere face")
    rep.notes.append(f"Behind dial: back plate rear face at {BP[0]} mm; motor rear at {BP[0] - 48:.0f} mm")
    rep.notes.append(f"Overall depth, hemisphere face to motor rear: {front_depth - (BP[0] - 48):.0f} mm")
    rep.notes.append(f"Bridge at z {BRIDGE}; big-wheel level {BIG}")
    return a, rep


def check(a: Assembly, rep: Report) -> dict:
    env = a.envelope()
    clashes = a.interference()
    bay_ok = env.min.X >= BAY[0] and env.max.X <= BAY[1] and env.min.Y >= BAY[2] and env.max.Y <= BAY[3]
    return {
        "interference": [{"a": x, "b": y, "volume_mm3": round(v, 2)} for x, y, v in clashes],
        "bed_fit_single": [r for r in a.bed_fit(BED_SINGLE) if not r["fits"]],
        "bed_fit_dual": [r for r in a.bed_fit(BED_DUAL) if not r["fits"]],
        "envelope": {"x": [round(env.min.X, 1), round(env.max.X, 1)], "y": [round(env.min.Y, 1), round(env.max.Y, 1)],
                     "z": [round(env.min.Z, 1), round(env.max.Z, 1)]},
        "inside_bay": bay_ok,
        "parts": len(a.items),
        "printed_parts": sum(1 for i in a.items if i.printed),
        "sweep_conflicts": sweep_conflicts(a, moon_excursion=LAT_EXCURSION / 2 * LEVER),
        "eclipse_options": eclipse_options(),
        "schwilgue_cam_check": {"rho": 134, "R_minus_r": 40.4,
                                "max_slope_deg": round(parts.cam_pressure_angle(latitude_profile(134, 40.4), 36000), 2),
                                "inclination_deg": round(math.degrees(INCL), 3)},
        "report": rep.__dict__,
    }


def main(out_dir="export/m2_main_dial_feasibility"):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    a, rep = build()
    res = check(a, rep)
    (out / "feasibility.json").write_text(json.dumps(res, indent=2))
    print(json.dumps({k: v for k, v in res.items() if k != "report"}, indent=2))
    renders(a, out)
    return a, res


# --- rotating-hand sweep check -------------------------------------------------------------------
SWEEP = {  # front item -> what it rotates with
    "dial": "fixed", "hemisphere": "fixed", "calendar_ring": "ring",
    "hand_sunset": "sunset", "hand_sunrise": "sunrise", "hand_sun": "sun", "sun_disc": "sun",
    "latitude_cam": "cam", "hand_moon": "moon", "moon_ball": "moon", "arm_shadow": "shadow",
    "shadow_disc": "shadow",
}


def _rz_ranges(shape, tol=0.3):
    import numpy as np
    verts, _ = shape.tessellate(tol, 0.5)
    v = np.array([(p.X, p.Y, p.Z) for p in verts])
    r = np.hypot(v[:, 0], v[:, 1])
    return (float(r.min()), float(r.max())), (float(v[:, 2].min()), float(v[:, 2].max()))


def sweep_conflicts(a: Assembly, margin: float = 0.3, moon_excursion: float = 0.0) -> list:
    """Pairs of front items that turn relative to each other and could touch at some angle.

    Each item sweeps an annulus [r_min, r_max] x [z_min, z_max] about the dial axis. Two items on
    different tubes conflict if both their radial and axial ranges overlap (plus ``margin``). The
    Moon ball's radial range is widened by the eclipse excursion.
    """
    rz = {}
    for name, grp in SWEEP.items():
        (r0, r1), (z0, z1) = _rz_ranges(a[name].shape)
        if name == "moon_ball":
            r0, r1 = r0 - moon_excursion, r1 + moon_excursion
        rz[name] = (grp, r0, r1, z0, z1)
    out = []
    names = list(rz)
    for i, n1 in enumerate(names):
        for n2 in names[i + 1:]:
            g1, a0, a1, b0, b1 = rz[n1]
            g2, c0, c1, d0, d1 = rz[n2]
            if g1 == g2:
                continue
            if a0 < c1 + margin and c0 < a1 + margin and b0 < d1 + margin and d0 < b1 + margin:
                out.append({"a": n1, "b": n2, "r": [round(max(a0, c0), 1), round(min(a1, c1), 1)],
                            "z": [round(max(b0, d0), 2), round(min(b1, d1), 2)]})
    return out


# --- eclipse display options (envelope §5) ---------------------------------------------------------
B13 = math.radians(1 + 9 / 60 + 23 / 3600)                # latitude at 13° from the node [S: ELS]
INCL = math.asin(math.sin(B13) / math.sin(math.radians(13)))   # 5.147° [D], modern mean 5.145°


def latitude_profile(rho: float, delta: float):
    """Schwilgué's latitude cam: radius vs argument of latitude F, curve limited to ±13° of each
    node and flat between [S: ELS]. ``delta`` = R - r, ``rho`` = mean radius."""
    def r(F):
        Fd = math.degrees(F) % 360
        if Fd <= 13 or Fd >= 347 or 167 <= Fd <= 193:
            b = math.asin(math.sin(INCL) * math.sin(F))
        else:
            b = B13 if Fd < 180 else -B13
        return rho + delta / 2 * b / B13
    return r


def rho_for_slope(delta: float, limit: float = 37.5) -> float:
    lo, hi = 1.0, 1000.0
    for _ in range(50):
        mid = (lo + hi) / 2
        if parts.cam_pressure_angle(latitude_profile(mid, delta), 7200) > limit:
            lo = mid
        else:
            hi = mid
    return hi


def eclipse_options(ks=(1, 4, 8)) -> list[dict]:
    rows = []
    for k in ks:
        delta = 40.4 / 8 * k
        rows.append({
            "k": k,
            "sun_disc_mm": round(9.3 / 8 * k, 1), "moon_disc_mm": round(9.1 / 8 * k, 1),
            "shadow_disc_mm": round(24.3 / 8 * k, 1),
            "moon_radial_excursion_mm": round(delta / 2, 1),
            "direct_cam_mean_radius_mm": round(rho_for_slope(delta), 1),
            "direct_cam_diameter_mm": round(2 * (rho_for_slope(delta) + delta / 2), 0),
            "lever_cam_mean_radius_mm": 16.75, "lever_ratio": k,
            "max_slope_deg_lever_cam": round(parts.cam_pressure_angle(latitude_profile(16.75, 40.4 / 8), 36000), 2),
        })
    return rows


def half_section(a: Assembly, keep_below_y: float = 0.0) -> Assembly:
    """Copy of the assembly cut by the plane y = keep_below_y, keeping y <= that value."""
    cut = bd.Box(2000, 1000, 2000, align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.CENTER)).moved(
        bd.Location((0, keep_below_y, 0)))
    s = Assembly(a.name + "_section")
    for i in a.items:
        piece = i.shape & cut
        if piece.volume > 1e-6:
            s.add(i.name, piece, material=i.material, printed=i.printed, group=i.group)
    return s


def renders(a: Assembly, out: Path):
    out.mkdir(parents=True, exist_ok=True)
    a.render(out / "front.png", elev=90, azim=-90, title="M2 main dial, front (hands at a sample time)",
             hide=("plates",), tolerance=0.4)
    a.render(out / "rear_three_quarter.png", elev=-30, azim=-120,
             title="M2 main dial, rear three-quarter (plates, ring and dial hidden)",
             hide=("ring", "plates", "front"), tolerance=0.4)
    a.render(out / "exploded.png", exploded=True, elev=18, azim=-62,
             title="M2 main dial, exploded along the dial axis (ring hidden)",
             hide=("ring", "interfaces"), tolerance=0.4)
    sec = half_section(a, 0.0)
    sec.render(out / "section.png", elev=0, azim=-90, title="Half section at y = 0, seen from below (depth stack)",
               tolerance=0.3)


if __name__ == "__main__":
    main(*sys.argv[1:])
