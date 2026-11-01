"""Phase 2 test rig: one stepper driving hour/day motion work (brief, Phase 2 step 3).

The first thing printed. It runs the real M1 trains from ``spec/clock.yaml`` and tries, before the
clock depends on them:

1. printed involute gears at module 1.0 with 0.15 mm backlash (D4), running for weeks;
2. **M1 motion work** (``M1.hour_hand`` 12/48 x 15/45, reverted, 30 mm centres) under a 12 h dial;
3. the **friction-clutched cannon pinion** (architecture §7): the minute hand is set by turning it;
   the friction is adjustable with a shaft collar and a wave washer;
4. the **noon train** (``M1.noon_cam`` 12/54 x 12/64, 1 turn per day) to a 24 h arbor;
5. the **two-tube Sun drive** of the main dial (docs/main-dial-feasibility.md §2): the 24 h arbor
   turns an outer "Sun" tube and an inner "shadow" tube through two equal 48/48 pairs, with a free
   middle tube between them, as on M2. The phase between the two hands measures the backlash;
6. Hall **index** (minute arbor) and **witness** (24 h arbor) sensing, and the D3 electronics
   (ESP32-S3 + TMC2209, UART, StealthChop) on a tray.

Coordinates: origin at the 12 h dial centre on the dial face; +X right, +Y up, +Z towards the viewer.

Run:  python -m cad.modules.test_rig.rig [out_dir]
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import build123d as bd

from cad.lib import parts
from cad.lib.assembly import BED_DUAL, BED_SINGLE, Assembly, write_dae
from cad.lib.gears import Gear, centre_distance, mesh_rotation, pair_shifts, spur_gear
from cad.lib.hardware import BEARINGS, SCREWS, tube_stack

M = 1.0
BACKLASH = 0.15
FACE = 3.0            # motion work face
FACE_T = 4.0          # train face behind the front plate (D4 default)
GAP = 1.0

# --- planes (z) -----------------------------------------------------------------------------------
DIAL = (-2.0, 0.0)
MW1 = (-7.0, -4.0)            # motion work level 1: minute pinion 15 + hour wheel 45
MW2 = (-10.5, -7.5)           # motion work level 2: cannon pinion 12 + minute wheel 48
FP = (-18.0, -14.0)           # front plate (clutch collar and washer in front of it)
Q1 = (-23.0, -19.0)           # Sun pair 48/48
Q2 = (-29.0, -25.0)           # noon train stage 2: 12 (X) / 64 (B)
Q3 = (-35.0, -31.0)           # noon train stage 1: 12 (A) / 54 (X)
Q4 = (-41.0, -37.0)           # shadow pair 48/48; index flag on A
BP = (-46.0, -42.0)           # back plate
MOTOR_FACE = BP[0] - 30.0     # motor flange 30 mm behind the back plate (coupling in between)


def at(shape, xy, z=0.0):
    return shape.moved(bd.Location((xy[0], xy[1], z)))


def polar(xy, r, deg):
    return (xy[0] + r * math.cos(math.radians(deg)), xy[1] + r * math.sin(math.radians(deg)))


def _hub(od, z0, z1):
    return parts.disc(od, z1 - z0, z0=z0)


def gear_part(g: Gear, level, bore, fit="running", hub=None, rot=0.0):
    """Spur gear on a level (z0, z1) with a bore; optional extra hub (od, z0, z1). Rotation in degrees."""
    part = spur_gear(g, level[1] - level[0]).moved(bd.Location((0, 0, level[0])))
    if hub:
        part = part + _hub(*hub)
    zlo = min(level[0], hub[1] if hub else level[0]) - 1
    zhi = max(level[1], hub[2] if hub else level[1]) + 1
    part = part - parts.disc(bore + getattr(parts.FITS, fit), zhi - zlo, z0=zlo)
    return part.rotate(bd.Axis.Z, rot)


def build():
    a = Assembly("test_rig")
    data = {"meshes": [], "positions": {}, "notes": []}

    def mesh(z1, z2, x1=0.0, x2=0.0, label=""):
        g1, g2 = Gear(z1, M, shift=x1, backlash=BACKLASH), Gear(z2, M, shift=x2, backlash=BACKLASH)
        cd = centre_distance(g1, g2)
        data["meshes"].append({"pair": label or f"{z1}/{z2}", "centre_distance": round(cd, 3),
                               "shifts": [round(x1, 3), round(x2, 3)]})
        return g1, g2, cd

    # ------------------------------------------------------------------ positions
    A = (0.0, 0.0)                                              # minute arbor (motor axis)
    # motion work: cannon 12 -> minute wheel 48 (stud), minute pinion 15 -> hour wheel 45 (coaxial on A)
    sx12, sx48 = pair_shifts(12, 48)
    g_c, g_mw, cd1 = mesh(12, 48, sx12, sx48, "cannon 12 / minute wheel 48")
    sx15, sx45 = pair_shifts(15, 45)
    g_mp, g_hw, cd2 = mesh(15, 45, sx15, sx45, "minute pinion 15 / hour wheel 45")
    assert abs(cd1 - cd2) < 1e-9, "reverted motion work needs equal centre distances"
    MS = polar(A, cd1, 90)                                      # minute-wheel stud, above the centre
    # noon train: 12 (A) -> 54 (X); 12 (X) -> 64 (B)
    nx12, nx54 = pair_shifts(12, 54)
    g_a12, g_x54, cd3 = mesh(12, 54, nx12, nx54, "noon 12 / 54")
    mx12, mx64 = pair_shifts(12, 64)
    g_x12, g_b64, cd4 = mesh(12, 64, mx12, mx64, "noon 12 / 64")
    X = polar(A, cd3, -20)
    B = polar(X, cd4, 10)
    g_s1, g_s2, cd5 = mesh(48, 48, label="Sun pair 48 / 48 (and shadow pair)")
    C = polar(B, cd5, 20)                                       # 24 h dial centre
    data["positions"] = {k: [round(v[0], 2), round(v[1], 2)] for k, v in
                         {"A_minute": A, "minute_stud": MS, "X_noon": X, "B_24h": B, "C_24h_dial": C}.items()}

    # ------------------------------------------------------------------ arbors, tubes, bearings
    a.add("arbor_A", at(parts.rod(5.0, 7.0 - (BP[0] - 12)), A, BP[0] - 12), material="steel",
          printed=False, group="shafts")
    for nm, p in (("arbor_X", X), ("arbor_B", B)):
        a.add(nm, at(parts.rod(5.0, FP[1] - BP[0] + 2), p, BP[0] - 1), material="steel", printed=False, group="shafts")
    a.add("stud_minute_wheel", at(parts.rod(3.0, MW1[1] + 0.5 - FP[0]), MS, FP[0]), material="steel",
          printed=False, group="shafts")
    a.add("arbor_C_fixed", at(parts.rod(3.0, 6.5 - (BP[0] - 1)), C, BP[0] - 1), material="steel", printed=False,
          group="shafts")
    for nm, p, plate in (("brg_A_front", A, FP), ("brg_A_back", A, BP), ("brg_X_front", X, FP),
                         ("brg_X_back", X, BP), ("brg_B_front", B, FP), ("brg_B_back", B, BP)):
        b = BEARINGS["MR85ZZ"]
        z0 = plate[1] - b.width if plate is FP else plate[0]
        a.add(nm, at(parts.bearing(b, z0), p), material="bearing", printed=False, group="bearings")
        a.allow(nm, "arbor_" + nm.split("_")[1])

    # cannon tube (OD 6 over the Ø5 arbor) carries the minute hand; hour tube (OD 7) carries the hour hand
    t_cannon, t_hour = tube_stack(5.0, 2)
    a.add("tube_cannon", at(parts.tube(t_cannon, 4.6 - MW2[0]), A, MW2[0]), material="brass", printed=False, group="tubes")
    a.add("tube_hour", at(parts.tube(t_hour, 2.1 - MW1[0]), A, MW1[0]), material="brass", printed=False, group="tubes")
    # 24 h stack on the fixed Ø3 arbor: inner OD4 shadow, middle OD5 free ("Moon"), outer OD6 Sun
    t_shadow, t_mid, t_sun = tube_stack(3.0, 3)
    a.add("tube_shadow", at(parts.tube(t_shadow, 5.8 - Q4[0]), C, Q4[0]), material="brass", printed=False, group="tubes")
    a.add("tube_middle", at(parts.tube(t_mid, 3.9 - (Q1[0] - 2)), C, Q1[0] - 2), material="brass", printed=False, group="tubes")
    a.add("tube_sun", at(parts.tube(t_sun, 2.0 - Q1[0]), C, Q1[0]), material="brass", printed=False, group="tubes")
    metal = ["arbor_A", "tube_cannon", "tube_hour", "arbor_C_fixed", "tube_shadow", "tube_middle", "tube_sun"]
    for i, x in enumerate(metal):
        for y in metal[i + 1:]:
            a.allow(x, y)

    # ------------------------------------------------------------------ motion work (front of the front plate)
    # cannon pinion 12 on level MW2, with a friction hub towards the plate (clutch: wave washer + collar)
    a.add("cannon_pinion_12", at(gear_part(g_c, MW2, t_cannon.od, "press", hub=(10.0, MW2[0], MW2[1])), A),
          group="motion_work", explode=(0, 0, 18))
    # minute wheel 48 (MW2) + minute pinion 15 (MW1), one printed compound part on the stud
    mw = gear_part(g_mw, MW2, 3.0, "running", rot=mesh_rotation(g_c, g_mw, 90.0)) + \
        gear_part(g_mp, MW1, 3.0, "running") + _hub(12.0, MW2[1] - 0.1, MW1[0] + 0.1)
    mw = mw - parts.disc(3.0 + parts.FITS.running, 20, z0=MW2[0] - 5)
    a.add("minute_wheel_48_15", at(mw, MS), group="motion_work", explode=(0, 0, 24))
    a.add("hour_wheel_45", at(gear_part(g_hw, MW1, t_hour.od, "press", rot=mesh_rotation(g_mp, g_hw, 270.0)), A),
          group="motion_work", explode=(0, 0, 30))
    for g_ in ("cannon_pinion_12", "hour_wheel_45"):
        for t_ in ("tube_cannon", "tube_hour", "arbor_A"):
            a.allow(g_, t_)
    a.allow("minute_wheel_48_15", "stud_minute_wheel")
    a.add("clutch_collar", at(parts.hub(5.0, 10.0, 2.5, "press", FP[1] + 0.5), A), material="steel", printed=False,
          group="motion_work", note="Ø5 shaft collar with grub screw; sets the clutch preload")
    a.add("clutch_wave_washer", at(parts.disc(10.0, 0.3, bore=5.2, z0=FP[1] + 3.0), A), material="steel",
          printed=False, group="motion_work")
    a.add("clutch_front_collet", at(parts.hub(5.0, 9.0, 2.3, "sliding", 4.7), A), group="motion_work",
          explode=(0, 0, 60), note="printed collet with an M3 grub screw in a heat-set insert; holds the stack")
    a.allow("clutch_front_collet", "arbor_A")
    a.allow("clutch_collar", "arbor_A")
    a.allow("clutch_wave_washer", "arbor_A")
    a.allow("clutch_wave_washer", "clutch_collar")
    a.allow("clutch_wave_washer", "cannon_pinion_12")

    # ------------------------------------------------------------------ noon train and Sun pairs (between plates)
    a.add("noon_pinion_12_A", at(gear_part(g_a12, Q3, 5.0, "press", hub=(9.0, Q3[1], Q3[1] + 3)), A), group="train")
    a.allow("noon_pinion_12_A", "arbor_A")
    x_part = gear_part(g_x54, Q3, 5.0, "press", rot=mesh_rotation(g_a12, g_x54, -20.0)) + \
        gear_part(g_x12, Q2, 5.0, "press") + _hub(10.0, Q3[1], Q2[0]) - parts.disc(5.0 - 0.05, 20, z0=Q3[0] - 5)
    a.add("noon_wheel_54_12_X", at(x_part, X), group="train", explode=(0, 0, -10))
    a.allow("noon_wheel_54_12_X", "arbor_X")
    b_part = gear_part(g_b64, Q2, 5.0, "press", rot=mesh_rotation(g_x12, g_b64, 10.0))
    a.add("day_wheel_64_B", at(b_part, B), group="train", explode=(0, 0, -16))
    a.add("sun_drive_48_B", at(gear_part(g_s1, Q1, 5.0, "press", hub=(10.0, Q1[0] - 2, Q1[0])), B), group="train")
    a.add("shadow_drive_48_B", at(gear_part(g_s1, Q4, 5.0, "press", hub=(10.0, Q4[1], Q4[1] + 2)), B), group="train")
    for g_ in ("day_wheel_64_B", "sun_drive_48_B", "shadow_drive_48_B"):
        a.allow(g_, "arbor_B")
    rot_c = mesh_rotation(g_s1, g_s2, 20.0)
    a.add("sun_wheel_48_C", at(gear_part(g_s2, Q1, t_sun.od, "press", rot=rot_c), C), group="train")
    a.add("shadow_wheel_48_C", at(gear_part(g_s2, Q4, t_shadow.od, "press", rot=rot_c), C), group="train")
    for g_, tubes in (("sun_wheel_48_C", ("tube_sun", "tube_middle", "tube_shadow", "arbor_C_fixed")),
                      ("shadow_wheel_48_C", ("tube_shadow", "arbor_C_fixed"))):
        for t_ in tubes:
            a.allow(g_, t_)

    # index flag on A (magnet 5 x 2) and the sensors
    a.add("index_flag_A", at(parts.hub(5.0, 22.0, 2.5, "press", Q4[0] + 0.5), A), group="sensors")
    a.allow("index_flag_A", "arbor_A")
    a.add("magnet_index", at(parts.disc(5.0, 2.0, z0=Q4[0] + 0.75), polar(A, 8.0, 180)), material="silver",
          printed=False, group="sensors")
    a.allow("magnet_index", "index_flag_A")
    a.add("hall_index", at(bd.Box(8, 6, 3, align=(bd.Align.CENTER,) * 3), polar(A, 8.0, 180), Q4[0] - 2.5),
          material="green", printed=False, group="sensors", note="DRV5032 on a small PCB, bracket to the back plate")
    a.add("magnet_witness", at(parts.disc(5.0, 2.0, z0=Q2[0] + 1.0), polar(B, 20.0, 90)), material="silver",
          printed=False, group="sensors")
    a.allow("magnet_witness", "day_wheel_64_B")
    a.add("hall_witness", at(bd.Box(8, 6, 3, align=(bd.Align.CENTER,) * 3), polar(B, 20.0, 90), Q2[0] - 2.5),
          material="green", printed=False, group="sensors")

    # ------------------------------------------------------------------ plates, standoffs, feet
    xs = [A[0], MS[0], X[0], B[0], C[0]]
    ys = [A[1], MS[1], X[1], B[1], C[1]]
    pad = 62.0
    pw, ph = max(xs) - min(xs) + 2 * pad, max(ys) - min(ys) + 2 * pad
    pc = ((max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2)
    holes_fp = [(C[0] - pc[0], C[1] - pc[1], t_sun.od + 0.4), (MS[0] - pc[0], MS[1] - pc[1], 3.0 + parts.FITS.press)]
    holes_bp = [(C[0] - pc[0], C[1] - pc[1], 3.0 + parts.FITS.press)]
    fp = at(parts.plate((pw, ph), FP[1] - FP[0], holes=holes_fp, z0=FP[0], corner_radius=6), pc)
    bp = at(parts.plate((pw, ph), BP[1] - BP[0], holes=holes_bp, z0=BP[0], corner_radius=6), pc)
    b = BEARINGS["MR85ZZ"]
    seat = b.od + parts.FITS.bearing_seat
    for p in (A, X, B):       # MR85ZZ pockets with a 1 mm shoulder; the pocket opens on the outer face
        fp -= at(parts.disc(seat, b.width + 1.0, z0=FP[1] - b.width), p) + \
            at(parts.disc(b.od - 2.0, FP[1] - FP[0], z0=FP[0] - 1.0), p)
        bp -= at(parts.disc(seat, b.width + 1.0, z0=BP[0] - 1.0), p) + \
            at(parts.disc(b.od - 2.0, BP[1] - BP[0], z0=BP[0] + b.width - 0.5), p)
    a.add("front_plate", fp, material="PETG", group="plates", explode=(0, 0, -8))
    a.add("back_plate", bp, material="PETG", group="plates", explode=(0, 0, -60))
    corners = [(pc[0] + sx * (pw / 2 - 8), pc[1] + sy * (ph / 2 - 8)) for sx in (-1, 1) for sy in (-1, 1)]
    for k, p in enumerate(corners):
        a.add(f"pillar_{k}", at(parts.standoff(FP[0] - BP[1], od=8.0), p, BP[1]), material="PETG", group="plates")
        a.allow(f"pillar_{k}", "front_plate"); a.allow(f"pillar_{k}", "back_plate")
    for nm in ("arbor_A", "arbor_X", "arbor_B", "arbor_C_fixed", "stud_minute_wheel", "tube_sun", "tube_middle"):
        a.allow(nm, "front_plate"); a.allow(nm, "back_plate")
    for nm in ("brg_A_front", "brg_X_front", "brg_B_front"):
        a.allow(nm, "front_plate")
    for nm in ("brg_A_back", "brg_X_back", "brg_B_back"):
        a.allow(nm, "back_plate")
    a.allow("hall_index", "back_plate")
    # feet: two L-brackets under the plates
    for k, sx in enumerate((-1, 1)):
        foot = bd.Box(14, 6, 90, align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.CENTER))
        a.add(f"foot_{k}", at(foot, (pc[0] + sx * (pw / 2 - 20), pc[1] - ph / 2), (FP[1] + BP[0]) / 2 - 10),
              material="PETG", group="plates")
        a.allow(f"foot_{k}", "front_plate"); a.allow(f"foot_{k}", "back_plate")
        for j in range(4):
            a.allow(f"foot_{k}", f"pillar_{j}")

    # ------------------------------------------------------------------ dials and hands
    a.add("dial_12h", at(parts.disc(112.0, DIAL[1] - DIAL[0], bore=t_hour.od + 1.0, z0=DIAL[0]), A),
          material="silver", group="front", explode=(0, 0, 40))
    a.add("dial_24h", at(parts.disc(100.0, DIAL[1] - DIAL[0], bore=t_sun.od + 1.0, z0=DIAL[0]), C),
          material="dial", group="front", explode=(0, 0, 40))
    for nm in ("tube_cannon", "tube_hour", "arbor_A"):
        a.allow(nm, "dial_12h")
    for nm in ("tube_sun", "tube_middle", "tube_shadow", "arbor_C_fixed"):
        a.allow(nm, "dial_24h")
    a.allow("stud_minute_wheel", "dial_12h")

    def hand(name, centre, tube_od, length, z0, ang, width=2.5, mat="black", tail=8.0):
        h = parts.hand(length, width, 1.5, tube_od + 5, tube_od, tail=tail, z0=z0).rotate(bd.Axis.Z, ang)
        a.add(name, at(h, centre), material=mat, group="hands", explode=(0, 0, 55))
        return name

    hand("hand_hour", A, t_hour.od, 32, 0.5, 60, width=3.5)
    hand("hand_minute", A, t_cannon.od, 48, 2.6, -30, width=2.5)
    hand("hand_sun", C, t_sun.od, 44, 0.5, 120, mat="red")
    hand("hand_middle", C, t_mid.od, 40, 2.4, 200, mat="silver")
    hand("arm_shadow", C, t_shadow.od, 44, 4.3, 300, mat="black")
    for hnm, own, inner in (("hand_hour", "tube_hour", ("tube_cannon", "arbor_A")),
                            ("hand_minute", "tube_cannon", ("arbor_A",)),
                            ("hand_sun", "tube_sun", ("tube_middle", "tube_shadow", "arbor_C_fixed")),
                            ("hand_middle", "tube_middle", ("tube_shadow", "arbor_C_fixed")),
                            ("arm_shadow", "tube_shadow", ("arbor_C_fixed",))):
        a.allow(hnm, own)
        for t_ in inner:
            a.allow(hnm, t_)

    # ------------------------------------------------------------------ motor, coupling, electronics
    motor = bd.Box(42.3, 42.3, 48.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
    a.add("motor_nema17", at(motor, A, MOTOR_FACE), material="black", printed=False, group="drive")
    a.add("coupling_5x5", at(parts.disc(19.0, 25.0, z0=MOTOR_FACE + 2.5), A), material="steel", printed=False,
          group="drive", note="flexible jaw/bellows coupling, 5 mm to 5 mm")
    a.allow("coupling_5x5", "arbor_A")
    for k, (dx, dy) in enumerate(((-15.5, -15.5), (15.5, -15.5), (-15.5, 15.5), (15.5, 15.5))):
        a.add(f"motor_standoff_{k}", at(parts.standoff(BP[0] - MOTOR_FACE, od=6.0), (A[0] + dx, A[1] + dy), MOTOR_FACE),
              material="steel", printed=False, group="drive")
        a.allow(f"motor_standoff_{k}", "back_plate"); a.allow(f"motor_standoff_{k}", "motor_nema17")
    tray_xy = (pc[0], pc[1] - ph / 2 - 6 - 45)
    tray = bd.Box(150, 6, 90, align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.CENTER))
    a.add("electronics_tray", at(tray, (tray_xy[0], pc[1] - ph / 2), MOTOR_FACE - 10), material="PETG",
          group="electronics", note="ESP32-S3 DevKitC-1, TMC2209 breakout, buck 24->5 V, terminals")
    for nm, size, off in (("esp32_s3_devkit", (69, 26, 12), (-35, 0)), ("tmc2209_breakout", (35, 25, 15), (25, 10)),
                          ("buck_24_5", (22, 17, 10), (25, -25))):
        a.add(nm, at(bd.Box(size[0], size[2], size[1], align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.CENTER)),
                     (tray_xy[0] + off[0], pc[1] - ph / 2), MOTOR_FACE - 10 + off[1]),
              material="green", printed=False, group="electronics")
        a.allow(nm, "electronics_tray")

    data["plate_size"] = [round(pw, 1), round(ph, 1)]
    data["notes"].append(f"Motion work centres {cd1:.3f} and {cd2:.3f} mm (reverted); shifts 12/48 {sx12:.3f}/{sx48:.3f}")
    return a, data


def check(a: Assembly, data: dict) -> dict:
    env = a.envelope()
    return {
        "interference": [{"a": x, "b": y, "volume_mm3": round(v, 3)} for x, y, v in a.interference()],
        "bed_fit_single": [r for r in a.bed_fit(BED_SINGLE) if not r["fits"]],
        "bed_fit_dual": [r for r in a.bed_fit(BED_DUAL) if not r["fits"]],
        "envelope": {"x": [round(env.min.X, 1), round(env.max.X, 1)], "y": [round(env.min.Y, 1), round(env.max.Y, 1)],
                     "z": [round(env.min.Z, 1), round(env.max.Z, 1)]},
        "parts": len(a.items),
        "printed_parts": [i.name for i in a.items if i.printed],
        "bought_parts": [i.name for i in a.items if not i.printed],
        **data,
    }


def renders(a: Assembly, out: Path):
    a.render(out / "rig_front.png", elev=0, azim=-90, up="y", title="Test rig, front", tolerance=0.2)
    a.render(out / "rig_three_quarter.png", elev=18, azim=-125, up="y",
             title="Test rig, three-quarter (plates hidden)", hide=("plates",), tolerance=0.2)
    a.render(out / "rig_rear.png", elev=15, azim=55, up="y", title="Test rig, rear three-quarter (plates hidden)",
             hide=("plates", "electronics"), tolerance=0.2)
    a.render(out / "rig_exploded.png", exploded=True, elev=12, azim=-150, up="y",
             title="Test rig, exploded along the arbors (plates hidden)", hide=("electronics", "plates"), tolerance=0.2)


def main(out_dir="export/test_rig"):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    a, data = build()
    res = check(a, data)
    (out / "test_rig.json").write_text(json.dumps(res, indent=2))
    print(json.dumps({k: res[k] for k in ("interference", "bed_fit_single", "envelope", "parts")}, indent=2))
    renders(a, out)
    write_dae(a, out / "test_rig.dae")
    # print files: every printed part of the rig, and the tolerance coupons (Bambu Studio: Arrange)
    a.export(out, stl=False, step=False, dae=False, threemf=True)
    from cad.modules.test_rig import coupons
    c = coupons.build()
    c.export(out, stl=False, step=False, dae=True, threemf=True)
    c.render(out / "coupons.png", exploded=True, elev=55, azim=-90, tolerance=0.15,
             title="Tolerance coupons (gears lifted off their board)")
    return a, res


if __name__ == "__main__":
    main(*sys.argv[1:])
