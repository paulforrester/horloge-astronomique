"""M1 + M1b, the lion gallery's mean-time dial: detail design (docs/m1-design.md).

Settled in the concept gate (PR #11, Paul, 4 Nov 2026):
- one cassette for M1 (gilt hands, Strasbourg mean time) and M1b (silver hands, legal time);
- four hands on one centre, front to back: gilt minute (Ø3 arbor), silver minute (OD 4 tube), silver
  hour (OD 5), gilt hour (OD 6);
- each system on its own NEMA 17 at 1:1 through a 45/45 pair; every release on M1b's shaft (D14):
  four quarters, the hour, and a 24 h noon wheel (12/54 · 12/64);
- the motion work 12/48 · 15/45 (`M1.hour_hand`, `M1b.legal_hour_hand`) as on the test rig.

Detail-design layout (the concept's §4 refined):
- **Both cannon pinions and both clutches are between the plates.** The silver minute tube covers
  the Ø3 arbor back to its own clutch, so the gilt cannon pinion can only sit behind it. Each motion
  work runs on its own arbor through the front plate: the minute wheel 48 behind it, meshing its
  cannon pinion; the minute pinion 15 in front, meshing its hour wheel on its hour tube.
- **Each clutch** is the minute member's 45-tooth drive gear, free on its tube or arbor, pressed by a
  wave washer and a collar against the cannon pinion fixed in front of it. The hands set by turning
  their minute hand; the releases, on the motor side of the clutch, never move.
- **Motors plug in from behind** (option A, Paul, PR #13; D16): each on a printed adapter plate held by 2 x M3
  into heat-set inserts; its drive part slides on the D-shaft, held by the adapter's boss and a front-plate post.

Coordinates: origin at the dial centre on the dial face; +X right, +Y up, +Z towards the viewer.
Run:  python -m cad.modules.m1_time.mechanism [out_dir]
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
from cad.modules.m1_time import dial as D
from cad.modules.m1_time import hands as H

M = 1.0
BACKLASH = 0.15
FACE = 3.0
G = 0.4                                    # axial gap between neighbouring levels that never touch
E = 0.3                                    # endshake at each designed thrust face [E: the tolerance coupons set it]

# --- the moment the model shows: Paul's photograph, 30 Oct 2026 10:10 CET (mean time 9:41) --------
LEGAL_HM, MEAN_HM = (10, 10), (9, 41)

# --- planes (z, mm) ---------------------------------------------------------------------------------
HANDS = {"gilt_hour": (0.6, 1.6), "silver_hour": (2.0, 3.0), "silver_minute": (3.4, 4.4), "gilt_minute": (4.8, 5.8)}
CAP_Z = 6.1
L2 = (-9.5, -6.5)                          # silver hour wheel 45 (OD 5) + silver minute pinion 15 (arbor SM)
L1 = (L2[1] + E, L2[1] + E + FACE)         # gilt hour wheel 45 (OD 6) + gilt minute pinion 15 (arbor GM)
FP = (-21.0, -17.0)                        # front plate
S_CANNON = (FP[0] - E - FACE, FP[0] - E)   # silver cannon 12 (OD 4) + silver minute wheel 48 (SM); thrust on the FP
S_DRIVE = (S_CANNON[0] - G - FACE, S_CANNON[0] - G)    # silver drive 45, free on OD 4 (the clutch): clear of SM's
#                                                         wheel; its Ø8 friction face bridges the gap to the cannon
S_WASHER = (S_DRIVE[0] - 0.5, S_DRIVE[0])
S_COLLAR = (S_WASHER[0] - 2.0, S_WASHER[0])
G_CANNON = (S_COLLAR[0] - E - FACE, S_COLLAR[0] - E)   # gilt cannon 12 (Ø3) + gilt minute wheel 48 (GM); thrust
#                                                         on the silver collar
G_DRIVE = (G_CANNON[0] - G - FACE, G_CANNON[0] - G)    # gilt drive 45, free on Ø3 (the clutch), the same way
G_WASHER = (G_DRIVE[0] - 0.5, G_DRIVE[0])
G_COLLAR = (G_WASHER[0] - 2.0, G_WASHER[0])
N1 = G_DRIVE                               # noon train stage 1: 12 (TB) / 54 (X), clear of SM's wheel
N2 = (G_COLLAR[0] - G - FACE + 0.5, G_COLLAR[0] - G + 0.5)   # stage 2: 12 (X) / 64 (N)
FLAGS = (N2[0] - G - 2.0, N2[0] - G)       # flag discs (TA index; TB quarters and hour; GM witness)
HALL = (8.0, 6.0, 3.0)                     # DRV5032 on a small PCB (as on the test rig)
HALL_POCKET, HALL_GAP = 1.6, 1.0           # pocket depth in the back plate; gap to the magnet's face
BP = (FLAGS[0] - HALL_GAP - (HALL[2] - HALL_POCKET) - 4.0, FLAGS[0] - HALL_GAP - (HALL[2] - HALL_POCKET))
# option A (Paul, PR #13, 5 Nov 2026; D16): each motor plugs in from behind on a printed adapter plate
ADAPTER = dict(w=42.3, h=66.0, t=4.0, boss=(26.0, 1.0), pilot=(22.0, 2.0), ears=27.0, screws=15.5)
INSERT_HOLE = 4.0                          # [E] M3 heat-set insert no longer than 4 mm: hole per its datasheet
POST_D = 10.0                              # the front-plate posts that stop the drive parts from the front
MOTOR_FACE = BP[0] - ADAPTER["t"]
SPIGOT_END = BP[0] + ADAPTER["boss"][1] + E  # the drive parts' spigots end E in front of the adapter's boss
S_HOUR_HUB = FP[1] + E                     # the silver hour wheel's rear hub ends E in front of the FP
BRG_Z0 = G_COLLAR[0] - E - 2.5             # MR63ZZ (width 2.5) in a back-plate boss: its face is the gilt collar's stop
BRG_BOSS = 10.0
CLUTCH_D = 8.0                             # the drive gears' raised friction face (mean radius ≈ R_FRICTION)
STARLOCK = (8.0, 0.4)                      # push-on lock washer for Ø3 (OD, thickness) [E: check the chosen part]
MOTOR_SHAFT = 24.0                         # [E] NEMA 17 shaft length from the face: check the motor's drawing
FLAT = (2.0, 15.0)                         # [E] the D-shaft's flat: 4.5 across (2.0 from the axis), 15 mm from the tip

# --- positions (x, y) ---------------------------------------------------------------------------------
C = (0.0, 0.0)
DRIVE_CD = 45.0                            # 45/45 at module 1, no shift
TA = (DRIVE_CD * math.cos(math.radians(210)), DRIVE_CD * math.sin(math.radians(210)))   # M1 motor
TB = (DRIVE_CD * math.cos(math.radians(330)), DRIVE_CD * math.sin(math.radians(330)))   # M1b motor
# dial feet, printed with the front plate; one is off the 90° pattern, so the dial fits only one way round
FEET_R, FEET_ANG, FOOT_D = 55.6, (45, 135, 225, 330), 7.6
FEET = [(FEET_R * math.cos(math.radians(a)), FEET_R * math.sin(math.radians(a))) for a in FEET_ANG]
PILLARS = [(-55.0, 34.0), (55.0, 34.0), (-60.0, -60.0), (64.0, -2.0)]   # M3 x 40 through both plates, nut in front
SPIGOT = 8.0                               # Ø of the drive parts' rear spigot that carries the flag discs
ARBOR_BOSS = (8.0, -12.5)                  # Ø and front face of the front-plate bosses for GM and SM (an 8.5 mm bore)
PLATE = (-67.0, 69.0, -68.0, 44.0)          # x0, x1, y0, y1

# release flags on TB (M1b, legal time): radii from TB
R_QUARTER, R_HOUR, R_INDEX_A, R_NOON, R_WITNESS = 13.0, 19.0, 9.0, 26.0, 7.0   # the hour Hall clear of the spigot
MAGNET = (5.0, 2.0)
# angles (deg, as built, at the modelled moment) at which each Hall sits
HALL_ANG = {"quarter": 90.0, "hour": 270.0, "index_A": 90.0, "noon": 90.0, "witness_G": 0.0, "witness_S": 180.0}


def at(shape, xy, z=0.0):
    return shape.moved(bd.Location((xy[0], xy[1], z)))


def polar(xy, r, deg):
    return (xy[0] + r * math.cos(math.radians(deg)), xy[1] + r * math.sin(math.radians(deg)))


def ang(p, q):
    return math.degrees(math.atan2(q[1] - p[1], q[0] - p[0]))


def gear_part(g: Gear, level, bore, fit="running", hub=None, rot=0.0):
    part = spur_gear(g, level[1] - level[0]).moved(bd.Location((0, 0, level[0])))
    if hub:
        part = part + parts.disc(hub[0], hub[2] - hub[1], z0=hub[1])
    zlo = min(level[0], hub[1] if hub else level[0]) - 1
    zhi = max(level[1], hub[2] if hub else level[1]) + 1
    part = part - parts.disc(bore + getattr(parts.FITS, fit), zhi - zlo, z0=zlo)
    return part.rotate(bd.Axis.Z, rot)


SHAFT_TIP = MOTOR_FACE + MOTOR_SHAFT


def d_side(x0, z0, z1):
    """The half-space x >= x0 between z0 and z1 (in a motor's local frame): cut from the shaft for its flat."""
    return bd.Box(10, 10, z1 - z0, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((x0, 0, z0)))


def d_key(z_top):
    """The key that fills a drive part's Ø5 bore against the shaft's flat (a slip fit), from 1 mm inside the flat's
    start to z_top, so the drive part slides off the shaft's tip when the motor is withdrawn."""
    z0 = SHAFT_TIP - FLAT[1] + 1.0
    return parts.disc(5.0 + 0.4, z_top - z0, z0=z0) & d_side(FLAT[0] + parts.FITS.running / 2, z0, z_top)


def magnet_pocket(xy, z_face, into=+1):
    """A 5 x 2 magnet pocket in a face at z_face, opening towards -into (into = +1: the part is in front)."""
    d, t = MAGNET
    z0 = z_face if into > 0 else z_face - t
    return at(parts.disc(d + 0.1, t + 0.01, z0=z0 - (0.005 if into > 0 else 0)), xy)


def magnet(xy, z_face, into=+1):
    d, t = MAGNET
    return at(parts.disc(d, t, z0=z_face if into > 0 else z_face - t), xy)


def hall_box(xy, z0, z1):
    return at(bd.Box(HALL[0], HALL[1], z1 - z0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)), xy, z0)


# Directions as seen from the front: the minute members turn clockwise, so each 45-tooth drive (TA, TB)
# turns anticlockwise, as does each motion-work arbor (GM, SM: 1 turn in 4 h); X turns clockwise and the
# 24 h wheel N anticlockwise. A flag sits under its Hall at its moment; elsewhere it has moved on.
def flag_angle(hall_deg, minutes_since, period_min, ccw=True):
    """Angle (deg, in the part's frame as placed) of a magnet that passed its Hall `minutes_since` ago."""
    d = 360.0 * (minutes_since % period_min) / period_min
    return hall_deg + (d if ccw else -d)


def hand_angles(hm):
    h, m = hm
    return {"minute": 6.0 * m, "hour": 30.0 * (h % 12) + 0.5 * m}


def build():
    a = Assembly("m1_time")
    data = {"meshes": [], "positions": {}, "levels": {}, "notes": []}

    def mesh(z1, z2, label, shift=True):
        x1, x2 = pair_shifts(z1, z2) if shift else (0.0, 0.0)
        g1, g2 = Gear(z1, M, shift=x1, backlash=BACKLASH), Gear(z2, M, shift=x2, backlash=BACKLASH)
        cd = centre_distance(g1, g2)
        data["meshes"].append({"pair": label, "centre_distance": round(cd, 3), "shifts": [round(x1, 3), round(x2, 3)]})
        return g1, g2, cd

    g_c12, g_mw48, cd_a = mesh(12, 48, "cannon 12 / minute wheel 48 (each system)")
    g_mp15, g_hw45, cd_b = mesh(15, 45, "minute pinion 15 / hour wheel 45 (each system)")
    assert abs(cd_a - cd_b) < 1e-9
    g_d45a, g_d45b, cd_d = mesh(45, 45, "drive 45 / 45 (each system)", shift=False)
    assert abs(cd_d - DRIVE_CD) < 1e-6
    g_n12, g_n54, cd_n1 = mesh(12, 54, "noon 12 / 54 (TB -> X)")
    g_x12, g_n64, cd_n2 = mesh(12, 64, "noon 12 / 64 (X -> N)")
    GM = polar(C, cd_a, 90)                # gilt motion-work arbor, above the centre
    SM = polar(C, cd_a, 270)               # silver motion-work arbor, below
    X = polar(TB, cd_n1, 270)
    N = polar(X, cd_n2, 180)
    pos = {"centre": C, "TA_M1_motor": TA, "TB_M1b_motor": TB, "GM_gilt_motion_work": GM, "SM_silver_motion_work": SM,
           "X_noon": X, "N_24h": N}
    data["positions"] = {k: [round(v[0], 2), round(v[1], 2)] for k, v in pos.items()}
    data["levels"] = {k: [round(v[0], 2), round(v[1], 2)] for k, v in
                      {"L1": L1, "L2": L2, "FP": FP, "S_cannon": S_CANNON, "S_drive": S_DRIVE, "G_cannon": G_CANNON,
                       "G_drive": G_DRIVE, "N1": N1, "N2": N2, "flags": FLAGS, "BP": BP}.items()}
    mean, legal = hand_angles(MEAN_HM), hand_angles(LEGAL_HM)

    # ------------------------------------------------------------------ the coaxial stack (centre)
    t4, t5, t6 = tube_stack(3.0, 3)
    arbor_rear = BRG_Z0 - 0.5
    a.add("arbor_gilt_minute_3", parts.rod(3.0, CAP_Z + 1.6 - arbor_rear, z0=arbor_rear), material="steel",
          printed=False, group="centre", note="Ø3 ground rod: gilt minute hand; gilt cannon and clutch between the plates")
    a.add("tube_silver_minute_4", parts.tube(t4, HANDS["silver_minute"][1] - S_COLLAR[0], z0=S_COLLAR[0]),
          material="brass", printed=False, group="centre", note="OD 4 brass tube: silver minute hand; its cannon and clutch")
    a.add("tube_silver_hour_5", parts.tube(t5, HANDS["silver_hour"][1] - S_HOUR_HUB, z0=S_HOUR_HUB), material="brass",
          printed=False, group="centre")
    a.add("tube_gilt_hour_6", parts.tube(t6, HANDS["gilt_hour"][1] - L1[0], z0=L1[0]), material="brass",
          printed=False, group="centre")
    metal = ["arbor_gilt_minute_3", "tube_silver_minute_4", "tube_silver_hour_5", "tube_gilt_hour_6"]
    for i, x in enumerate(metal):
        for y in metal[i + 1:]:
            a.allow(x, y)
    a.add("bearing_MR63ZZ", parts.bearing("MR63ZZ", BRG_Z0), material="bearing", printed=False,
          group="centre")
    a.allow("bearing_MR63ZZ", "arbor_gilt_minute_3")

    # clutches: cannon (fixed) | drive 45 (free) | wave washer | collar (fixed)
    rot_s_cannon = 0.0
    a.add("silver_cannon_12", gear_part(g_c12, S_CANNON, t4.od, "press", rot=rot_s_cannon), group="clutch",
          note="pressed on the OD 4 tube; the clutch's front face")
    a.add("silver_drive_45", gear_part(g_d45b, S_DRIVE, t4.od, "running", hub=(CLUTCH_D, S_DRIVE[1], S_CANNON[0]),
                                       rot=mesh_rotation(g_d45a, g_d45b, ang(TB, C))), group="clutch",
          note="free on the OD 4 tube: M1b drives the silver hands through it")
    a.add("silver_wave_washer", parts.disc(8.0, S_WASHER[1] - S_WASHER[0], bore=t4.od + 0.2, z0=S_WASHER[0]),
          material="steel", printed=False, group="clutch", note="wave washer for Ø4: the clutch's preload")
    a.add("silver_collar", parts.hub(t4.od, 9.0, S_COLLAR[1] - S_COLLAR[0], "press", S_COLLAR[0]), material="steel",
          printed=False, group="clutch", note="Ø4 shaft collar with grub screw: sets the preload")
    a.add("gilt_cannon_12", gear_part(g_c12, G_CANNON, 3.0, "press"), group="clutch",
          note="pressed on the Ø3 arbor; the clutch's front face")
    a.add("gilt_drive_45", gear_part(g_d45b, G_DRIVE, 3.0, "running", hub=(CLUTCH_D, G_DRIVE[1], G_CANNON[0]),
                                      rot=mesh_rotation(g_d45a, g_d45b, ang(TA, C))),
          group="clutch", note="free on the Ø3 arbor: M1 drives the gilt hands through it")
    a.add("gilt_wave_washer", parts.disc(7.0, G_WASHER[1] - G_WASHER[0], bore=3.2, z0=G_WASHER[0]), material="steel",
          printed=False, group="clutch", note="wave washer for Ø3")
    a.add("gilt_collar", parts.hub(3.0, 8.0, G_COLLAR[1] - G_COLLAR[0], "press", G_COLLAR[0]), material="steel",
          printed=False, group="clutch", note="Ø3 shaft collar with grub screw")
    for p_, m_ in (("silver_cannon_12", "tube_silver_minute_4"), ("silver_drive_45", "tube_silver_minute_4"),
                   ("silver_wave_washer", "tube_silver_minute_4"), ("silver_collar", "tube_silver_minute_4"),
                   ("gilt_cannon_12", "arbor_gilt_minute_3"), ("gilt_drive_45", "arbor_gilt_minute_3"),
                   ("gilt_wave_washer", "arbor_gilt_minute_3"), ("gilt_collar", "arbor_gilt_minute_3"),
                   ("silver_wave_washer", "silver_drive_45"), ("silver_wave_washer", "silver_collar"),
                   ("gilt_wave_washer", "gilt_drive_45"), ("gilt_wave_washer", "gilt_collar"),
                   ("silver_drive_45", "silver_cannon_12"), ("gilt_drive_45", "gilt_cannon_12")):
        a.allow(p_, m_)

    # ------------------------------------------------------------------ the two motion works
    for tag, arbor_xy, cannon_lvl, hour_lvl, hour_tube, hour_name, wheel_rot_line in (
            ("gilt", GM, G_CANNON, L1, "tube_gilt_hour_6", "gilt_hour_wheel_45", 90.0),
            ("silver", SM, S_CANNON, L2, "tube_silver_hour_5", "silver_hour_wheel_45", 270.0)):
        z_back = BP[1] - 1.5 if tag == "gilt" else cannon_lvl[0] - 0.5      # GM: E short of its blind pivot
        z_front = hour_lvl[1] + 0.3
        a.add(f"arbor_{tag}_motion_work", at(parts.rod(3.0, z_front - z_back, z0=z_back), arbor_xy), material="steel",
              printed=False, group="motion_work", note="Ø3 rod running in the front plate" +
              (" and the back plate" if tag == "gilt" else ""))
        wheel_hub = (7.0, cannon_lvl[1], FP[0] - E) if tag == "gilt" else None   # GM's forward stop, on the FP
        a.add(f"{tag}_minute_wheel_48", at(gear_part(g_mw48, cannon_lvl, 3.0, "press", hub=wheel_hub,
                                                     rot=mesh_rotation(g_c12, g_mw48, wheel_rot_line)), arbor_xy),
              group="motion_work")
        a.add(f"{tag}_minute_pinion_15", at(gear_part(g_mp15, hour_lvl, 3.0, "press",
                                                      hub=(7.0, hour_lvl[0] - 2.0, hour_lvl[0])), arbor_xy),
              group="motion_work")
        tube_od = t6.od if tag == "gilt" else t5.od
        # the silver hour wheel's rear hub stops on the FP; the gilt one's front hub on the dial's back
        hour_hub = (9.0, hour_lvl[1], -D.FIELD_T - E) if tag == "gilt" else (8.0, S_HOUR_HUB, hour_lvl[0])
        a.add(hour_name, gear_part(g_hw45, hour_lvl, tube_od, "press", hub=hour_hub,
                                   rot=mesh_rotation(g_mp15, g_hw45, (wheel_rot_line + 180.0) % 360)),
              group="motion_work", explode=(0, 0, 12))
        for p_ in (f"{tag}_minute_wheel_48", f"{tag}_minute_pinion_15"):
            a.allow(p_, f"arbor_{tag}_motion_work")
        a.allow(hour_name, hour_tube)
        for inner in metal:
            if metal.index(inner) < metal.index(hour_tube):
                a.allow(hour_name, inner)

    # ------------------------------------------------------------------ motors and their drive parts
    for tag, xy, own in (("M1", TA, "gilt"), ("M1b", TB, "silver")):
        motor = bd.Box(42.3, 42.3, 48.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
        motor += parts.disc(22.0, 2.0, z0=0.0)                    # pilot boss
        a.add(f"motor_{tag}", at(motor, xy, MOTOR_FACE), material="black", printed=False, group="drive",
              note="NEMA 17, 1:1 (17HS19-2004S1 class, as the rest of the clock)")
        a.add(f"shaft_{tag}", at(parts.rod(5.0, MOTOR_SHAFT, z0=MOTOR_FACE) - d_side(FLAT[0], SHAFT_TIP - FLAT[1],
                                                                                     SHAFT_TIP + 1), xy),
              material="steel", printed=False, group="drive", note="the motor's own Ø5 D-shaft")
        a.allow(f"shaft_{tag}", f"motor_{tag}")
    # M1 (TA): drive 45 at the gilt drive level; M1b (TB): drive 45 at the silver level and the noon pinion 12.
    # Each flag disc is its own print, pressed on its drive's Ø8 spigot: its phase on the shaft does not matter,
    # because its own magnets are the index, and printed in one piece it would overhang its hub.
    press, run = parts.FITS.press, parts.FITS.running
    spigot = parts.disc(SPIGOT, FLAGS[1] - SPIGOT_END, bore=5.0 + run, z0=SPIGOT_END)   # through the back plate
    pa = gear_part(g_d45a, G_DRIVE, 5.0, "running", hub=(10.0, FLAGS[1], G_DRIVE[0])) + d_key(G_DRIVE[1]) + spigot
    a.add("M1_drive_45", at(pa, TA), group="drive", note="slides on M1's D-shaft; held between the adapter's boss "
          "and a front-plate post; the index disc is pressed on its spigot")
    ia = polar((0, 0), R_INDEX_A, flag_angle(HALL_ANG["index_A"], MEAN_HM[1], 60))
    da = parts.disc(2 * (R_INDEX_A + 4.0), FLAGS[1] - FLAGS[0], bore=SPIGOT + press, z0=FLAGS[0])
    da -= magnet_pocket(ia, FLAGS[0], into=+1)
    a.add("M1_index_disc", at(da, TA), group="drive", note="M1's hourly index: one magnet; pressed on the "
          "drive's spigot in any phase")
    a.add("magnet_M1_index", at(magnet(ia, FLAGS[0]), TA), material="silver", printed=False, group="sensors")
    pb = gear_part(g_d45a, S_DRIVE, 5.0, "running", hub=(10.0, FLAGS[1], S_DRIVE[0]))
    pb += gear_part(g_n12, N1, 5.0, "running") + d_key(S_DRIVE[1]) + spigot
    a.add("M1b_drive_45_noon_12", at(pb, TB), group="drive",
          note="slides on M1b's D-shaft: drive 45 and noon pinion 12; held between the adapter's boss and a "
               "front-plate post; the flag disc is pressed on its spigot")
    q_pts = [polar((0, 0), R_QUARTER, flag_angle(HALL_ANG["quarter"], LEGAL_HM[1], 60) + 90.0 * k) for k in range(4)]
    h_pt = polar((0, 0), R_HOUR, flag_angle(HALL_ANG["hour"], LEGAL_HM[1], 60))
    db = parts.disc(2 * (max(R_QUARTER, R_HOUR) + 4.0), FLAGS[1] - FLAGS[0], bore=SPIGOT + press, z0=FLAGS[0])
    for p_ in q_pts + [h_pt]:
        db -= magnet_pocket(p_, FLAGS[0], into=+1)
    a.add("M1b_flag_disc", at(db, TB), group="drive",
          note="the release flags: four quarter magnets and the hour magnet (M1b's index); pressed on the drive's "
               "spigot in any phase")
    for k, p_ in enumerate(q_pts):
        a.add(f"magnet_quarter_{k}", at(magnet(p_, FLAGS[0]), TB), material="silver", printed=False, group="sensors")
        a.allow(f"magnet_quarter_{k}", "M1b_flag_disc")
    a.add("magnet_hour", at(magnet(h_pt, FLAGS[0]), TB), material="silver", printed=False, group="sensors")
    a.allow("magnet_hour", "M1b_flag_disc")
    a.allow("magnet_M1_index", "M1_index_disc")
    a.allow("M1_index_disc", "M1_drive_45")
    a.allow("M1b_flag_disc", "M1b_drive_45_noon_12")
    # the adapters (motor screwed on at the bench, 4 x M3 x 6 in counterbores; 2 x M3 x 8 from behind into inserts)
    ad_ = ADAPTER
    for tag, xy in (("M1", TA), ("M1b", TB)):
        ad = parts.plate((ad_["w"], ad_["h"]), ad_["t"], z0=MOTOR_FACE, corner_radius=4.0)
        ad += parts.disc(ad_["boss"][0], ad_["boss"][1], z0=BP[0])
        ad -= parts.disc(6.0, 20, z0=MOTOR_FACE - 5)                                     # the shaft
        ad -= parts.disc(ad_["pilot"][0] + run, ad_["pilot"][1] + 0.2, z0=MOTOR_FACE - 0.01)  # the motor's pilot boss
        for dx in (-ad_["screws"], ad_["screws"]):
            for dy in (-ad_["screws"], ad_["screws"]):
                ad -= parts.disc(3.4, 20, z0=MOTOR_FACE - 5).moved(bd.Location((dx, dy, 0)))
                ad -= parts.disc(6.2, 2.01, z0=BP[0] - 2.0).moved(bd.Location((dx, dy, 0)))   # head counterbore
        for dy in (-ad_["ears"], ad_["ears"]):
            ad -= parts.disc(3.4, 20, z0=MOTOR_FACE - 5).moved(bd.Location((0, dy, 0)))
        a.add(f"adapter_{tag}", at(ad, xy), material="PETG", group="drive",
              note="motor adapter: screwed to the motor at the bench, it plugs into the back plate from behind "
                   "(2 x M3 x 8 into heat-set inserts); its boss locates it and stops the drive part")
    # the front stops: posts pressed into the front plate's rear face
    for tag, xy, front in (("TA", TA, G_DRIVE[1]), ("TB", TB, S_DRIVE[1])):
        z0 = front + E
        post = parts.disc(POST_D, FP[0] - z0, z0=z0) + parts.disc(4.0, 3.0, z0=FP[0])
        if SHAFT_TIP > z0:
            post -= parts.disc(6.0, SHAFT_TIP + 1.5 - z0 + 0.01, z0=z0 - 0.01)         # clears the shaft's tip
        a.add(f"stop_post_{tag}", at(post, xy), material="PETG", group="drive",
              note="the drive part's front stop; its Ø4 peg is pressed into the front plate")
        a.allow(f"stop_post_{tag}", "front_plate")

    # ------------------------------------------------------------------ noon train (between the plates)
    xp = gear_part(g_n54, N1, 3.0, "running", rot=mesh_rotation(g_n12, g_n54, 270.0)) + \
        gear_part(g_x12, N2, 3.0, "running", hub=(7.0, BP[1] + E, N2[0])) + \
        parts.disc(9.0, N1[0] - N2[1], bore=3.0 + parts.FITS.running, z0=N2[1])
    a.add("noon_wheel_54_12_X", at(xp, X), group="train")
    npart = gear_part(g_n64, N2, 3.0, "running", hub=(7.0, BP[1] + E, N2[0]), rot=mesh_rotation(g_x12, g_n64, 180.0))
    noon_pt = polar((0, 0), R_NOON, flag_angle(HALL_ANG["noon"], (LEGAL_HM[0] - 12) * 60 + LEGAL_HM[1], 1440))
    npart -= magnet_pocket(noon_pt, N2[0], into=+1)
    a.add("noon_wheel_64_N", at(npart, N), group="train",
          note="24 h wheel: its magnet marks the noon window; set by meshing it to its mark (±½ tooth = ±11 min)")
    a.add("magnet_noon", at(magnet(noon_pt, N2[0]), N), material="silver", printed=False, group="sensors")
    a.allow("magnet_noon", "noon_wheel_64_N")
    for nm, xy, face, wheel in (("X", X, N1[1], "noon_wheel_54_12_X"), ("N", N, N2[1], "noon_wheel_64_N")):
        top = face + E + STARLOCK[1] + 0.6
        a.add(f"stud_{nm}", at(parts.rod(3.0, top - BP[0], z0=BP[0]), xy), material="steel", printed=False,
              group="train", note="Ø3 stud pressed into the back plate")
        a.add(f"starlock_{nm}", at(parts.disc(STARLOCK[0], STARLOCK[1], bore=3.0, z0=face + E), xy), material="steel",
              printed=False, group="train", note="push-on lock washer for Ø3: the wheel's forward stop (set with a "
              "0.3 mm shim)")
        a.allow(wheel, f"stud_{nm}")
        a.allow(f"starlock_{nm}", f"stud_{nm}")

    # ------------------------------------------------------------------ witnesses (after the clutches)
    # gilt: a disc on GM's rear end, read through the back plate's pocket; silver: SM's wheel front face
    wg = parts.disc(2 * (R_WITNESS + 4.0), FLAGS[1] - FLAGS[0], z0=FLAGS[0])
    wg_pt = polar((0, 0), R_WITNESS, flag_angle(HALL_ANG["witness_G"], (MEAN_HM[0] % 4) * 60 + MEAN_HM[1], 240))
    wg -= magnet_pocket(wg_pt, FLAGS[0], into=+1)
    wg -= parts.disc(3.0 + parts.FITS.press, 10, z0=FLAGS[0] - 1)
    a.add("gilt_witness_disc", at(wg, GM), group="sensors", note="pressed on the gilt motion-work arbor: 1 turn in 4 h")
    a.add("magnet_gilt_witness", at(magnet(wg_pt, FLAGS[0]), GM), material="silver", printed=False, group="sensors")
    a.allow("magnet_gilt_witness", "gilt_witness_disc")
    a.allow("gilt_witness_disc", "arbor_gilt_motion_work")
    ws_pt = polar((0, 0), 14.0, flag_angle(HALL_ANG["witness_S"], (LEGAL_HM[0] % 4) * 60 + LEGAL_HM[1], 240))
    a["silver_minute_wheel_48"].shape = a["silver_minute_wheel_48"].shape - at(
        magnet_pocket(ws_pt, S_CANNON[1], into=-1), SM)
    a.add("magnet_silver_witness", at(magnet(ws_pt, S_CANNON[1], into=-1), SM), material="silver", printed=False,
          group="sensors")
    a.allow("magnet_silver_witness", "silver_minute_wheel_48")

    # ------------------------------------------------------------------ plates, pillars, dial feet
    x0, x1, y0, y1 = PLATE
    outline = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    fp = parts.plate(outline, FP[1] - FP[0], z0=FP[0], corner_radius=6)
    bp = parts.plate(outline, BP[1] - BP[0], z0=BP[0], corner_radius=6)
    # the arbor bosses: SM runs in the front plate only (the 24 h wheel lies behind it); its boss is SM's rear stop
    for xy, front in ((GM, ARBOR_BOSS[1]), (SM, L2[0] - 2.0 - E)):
        fp += at(parts.disc(ARBOR_BOSS[0], front - FP[1], z0=FP[1]), xy)
    for k, xy in enumerate(FEET):          # the dial feet, each with a magnet in its top
        fp += at(parts.disc(FOOT_D, D.BEZEL["z0"] - FP[1], z0=FP[1]), xy)
        fp -= magnet_pocket(xy, D.BEZEL["z0"], into=-1)
        a.add(f"magnet_foot_{k}", magnet(xy, D.BEZEL["z0"], into=-1), material="silver", printed=False,
              group="front", note="5 x 2 magnet in a dial foot's top; holds the bezel's magnet")
        a.allow(f"magnet_foot_{k}", "front_plate")
    clear = SCREWS["M3"].clearance
    for xy in PILLARS:
        fp -= at(parts.disc(clear, 20, z0=FP[0] - 5), xy)
        bp -= at(parts.disc(clear, 20, z0=BP[0] - 5), xy)
    fp -= parts.disc(t4.od + parts.FITS.running, 20, z0=FP[0] - 5)                     # the OD 4 tube runs here
    for xy in (GM, SM):
        fp -= at(parts.disc(3.0 + parts.FITS.running, 20, z0=FP[0] - 5), xy)          # motion-work arbors
    bp += parts.disc(BRG_BOSS, BRG_Z0 + BEARINGS["MR63ZZ"].width - BP[1] + 0.01, z0=BP[1] - 0.01)  # bearing boss
    bp -= parts.bearing_seat_cut("MR63ZZ", z0=BRG_Z0) + parts.disc(4.0, BRG_Z0 - BP[0] + 1.01, z0=BP[0] - 1)
    bp -= at(parts.disc(3.0 + parts.FITS.running, 1.6 + E, z0=BP[1] - 1.5 - E), GM)   # GM's rear pivot (blind)
    for xy in (X, N):
        bp -= at(parts.disc(3.0 + parts.FITS.press, 10, z0=BP[0] - 1), xy)
    for xy in (TA, TB):
        bp -= at(parts.disc(ADAPTER["boss"][0] + parts.FITS.running, ADAPTER["boss"][1] + 0.11, z0=BP[0] - 0.01), xy)
        bp -= at(parts.disc(SPIGOT + parts.FITS.running, 10, z0=BP[0] - 1), xy)       # the drive part's spigot
        for dy in (-ADAPTER["ears"], ADAPTER["ears"]):
            bp -= at(parts.disc(INSERT_HOLE, 10, z0=BP[0] - 1), (xy[0], xy[1] + dy))  # M3 heat-set inserts
    for xy in (TA, TB):
        fp -= at(parts.disc(4.0 + parts.FITS.press, 3.01, z0=FP[0] - 0.01), xy)      # the stop posts' pegs
    for k, p_ in enumerate(PILLARS):
        a.add(f"pillar_{k}", at(parts.standoff(FP[0] - BP[1], od=8.0), p_, BP[1]), material="PETG", group="plates")
        a.allow(f"pillar_{k}", "front_plate"); a.allow(f"pillar_{k}", "back_plate")
    # Halls: back-plate pockets for TA index, TB quarter, TB hour, N noon, GM witness; a front-plate pocket for SM
    halls = {"hall_M1_index": polar(TA, R_INDEX_A, HALL_ANG["index_A"]),
             "hall_quarters": polar(TB, R_QUARTER, HALL_ANG["quarter"]),
             "hall_hour": polar(TB, R_HOUR, HALL_ANG["hour"]),
             "hall_noon": polar(N, R_NOON, HALL_ANG["noon"]),
             "hall_gilt_witness": polar(GM, R_WITNESS, HALL_ANG["witness_G"])}
    noon_hall_z0 = N2[0] - HALL_GAP - HALL[2]
    bp += at(bd.Box(HALL[0] + 3, HALL[1] + 3, noon_hall_z0 - BP[1] + 0.01,
                    align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)), halls["hall_noon"], BP[1] - 0.01)
    for nm, xy in halls.items():
        z0 = noon_hall_z0 if nm == "hall_noon" else BP[1] - HALL_POCKET
        if nm == "hall_noon":
            bp -= hall_box(xy, z0 - 0.01, z0 + HALL[2] + 0.01) & bd.Box(100, 100, 0.5, align=(bd.Align.CENTER,
                bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((0, 0, z0 - 0.01)))
        else:
            bp -= hall_box(xy, z0 - 0.01, BP[1] + 0.01)
        a.add(nm, hall_box(xy, z0, z0 + HALL[2]), material="green", printed=False, group="sensors",
              note="DRV5032 on a small PCB, " + ("on a boss of the back plate" if nm == "hall_noon" else
                                                  "in a back-plate pocket"))
        a.allow(nm, "back_plate")
    s_hall_xy = polar(SM, 14.0, HALL_ANG["witness_S"])
    fp -= hall_box(s_hall_xy, FP[0] - 0.01, FP[0] + HALL[2] + 0.2)          # recessed 0.2: the plate is the stop
    a.add("hall_silver_witness", hall_box(s_hall_xy, FP[0] + 0.2, FP[0] + HALL[2] + 0.2), material="green", printed=False,
          group="sensors", note="DRV5032, in a front-plate pocket facing the silver minute wheel")
    a.allow("hall_silver_witness", "front_plate")
    # frame tabs: the cassette hangs on the works' internal frame (D12 R5), 2 x M5
    for sx in (-1, 1):
        tab = at(parts.plate([(0, -10), (14, -10), (14, 10), (0, 10)], BP[1] - BP[0], z0=BP[0], corner_radius=3),
                 (x1 if sx > 0 else x0 - 14, 20.0))
        tab -= at(parts.disc(5.5, 10, z0=BP[0] - 1), ((x1 + 8) if sx > 0 else (x0 - 8), 20.0))
        bp += tab
    a.add("front_plate", fp, material="PETG", group="plates", explode=(0, 0, 10),
          note="the four dial feet (a magnet in each top) and the two arbor bosses print upwards, without support")
    a.add("back_plate", bp, material="PETG", group="plates", explode=(0, 0, -40),
          note="printed rear face down: the two Ø 22 motor pilot pockets are bridged (the down-facing area)")
    for nm in ("tube_silver_minute_4", "arbor_gilt_motion_work", "arbor_silver_motion_work"):
        a.allow(nm, "front_plate")
    for nm in ("bearing_MR63ZZ", "arbor_gilt_minute_3", "stud_X", "stud_N", "arbor_gilt_motion_work",
               "motor_M1", "motor_M1b", "shaft_M1", "shaft_M1b"):
        a.allow(nm, "back_plate")

    # ------------------------------------------------------------------ dial, bezel, hands, cap
    field, gilt = D.build()
    a.add("dial_field", field, material="black", group="front", explode=(0, 0, 20), print_set="dial",
          print_up=(0, 0, -1), nozzle=0.2, note="two-colour print with dial_gilt, face down, 0.2 mm nozzle")
    a.add("dial_gilt", gilt, material="gold", group="front", explode=(0, 0, 20), print_set="dial",
          print_up=(0, 0, -1), nozzle=0.2)
    a.allow("dial_field", "dial_gilt")
    bz = D.bezel()
    for k, xy in enumerate(FEET):
        bz -= magnet_pocket(xy, D.BEZEL["z0"], into=+1)
        a.add(f"magnet_bezel_{k}", magnet(xy, D.BEZEL["z0"], into=+1), material="silver", printed=False, group="front",
              explode=(0, 0, 24))
        a.allow(f"magnet_bezel_{k}", "bezel")
    a.add("bezel", bz, material="gold", group="front", explode=(0, 0, 24), print_up=(0, 0, 1),
          note="pearled gilt bezel; the dial is glued in its seat; four magnets hold it on the dial feet, so "
               "it pulls straight off once the hands are off. Printed face up: the lip's 1.7 mm ledge over the dial "
               "seat is most of the down-facing area and prints without support")
    a.allow("bezel", "dial_field"); a.allow("bezel", "dial_gilt")
    for nm in metal:
        a.allow(nm, "dial_field")
    specs = (("hand_gilt_hour", "gilt_hour", t6.od, "tube_gilt_hour_6", mean["hour"]),
             ("hand_silver_hour", "silver_hour", t5.od, "tube_silver_hour_5", legal["hour"]),
             ("hand_silver_minute", "silver_minute", t4.od, "tube_silver_minute_4", legal["minute"]),
             ("hand_gilt_minute", "gilt_minute", 3.0, "arbor_gilt_minute_3", mean["minute"]))
    for nm, kind, bore, own, angle in specs:
        a.add(nm, H.hand(kind, bore, HANDS[kind][0], angle), material="gold" if kind.startswith("gilt") else "silver",
              group="hands", explode=(0, 0, 30), print_up=(0, 0, 1), nozzle=0.2, note=f"{kind.replace('_', ' ')} hand, flat print, pressed on its "
                                                      f"{'arbor' if bore == 3.0 else 'tube'}")
        a.allow(nm, own)
        for inner in metal:
            if metal.index(inner) < metal.index(own):
                a.allow(nm, inner)
    a.add("centre_cap", H.cap(CAP_Z), material="gold", group="hands", explode=(0, 0, 34), print_up=(0, 0, 1),
          nozzle=0.2)
    a.allow("centre_cap", "arbor_gilt_minute_3")
    data["hands"] = {"mean (gilt)": "%d:%02d" % MEAN_HM, "legal (silver)": "%d:%02d" % LEGAL_HM}
    data["notes"].append(f"motion work centres {cd_a:.3f} (12/48) and {cd_b:.3f} (15/45) mm; noon train "
                         f"{cd_n1:.3f} and {cd_n2:.3f} mm; drives 45/45 at {cd_d:.3f} mm")
    return a, data


# --- release windows and the clutch [E] --------------------------------------------------------------
# A Hall switch stays on while the magnet is within about HALL_RANGE of it, sideways, at a 1 mm gap
# [E: DRV5032 with a 5 x 2 magnet; the test rig measures it, question 5]. So each flag opens a window;
# the controller starts the show at the exact minute on its own clock, inside that window, and reports
# a fault if the window does not contain it (CLAUDE.md: timekeeping accuracy comes from the controller).
HALL_RANGE = 4.0
NOON_SET_ERR = 0.5 * 1440 / 64            # ± half a tooth of the 24 h wheel when it is meshed to its mark (min)


def release_windows() -> dict:
    """Half-widths (minutes) of the quarter, hour and noon windows."""
    w = lambda r, period: HALL_RANGE / (2 * math.pi * r) * period
    return {"quarter": w(R_QUARTER, 60.0), "hour": w(R_HOUR, 60.0), "noon": w(R_NOON, 1440.0),
            "noon_setting_error": NOON_SET_ERR}


# The clutch: the drive gear's face against the cannon's, pressed by the wave washer [E].
MU_CLUTCH = 0.3                            # printed PLA/PETG on itself (as setter.MU) [E]
R_FRICTION = 3.0                           # mean radius of the gear-on-cannon contact (mm) [E]
T_RUN = 1.0                                # running torque of a hand set and its motion work (N·mm) [E]
T_SET = 0.3 * 45.0                         # what a finger applies at the minute hand's tip: 0.3 N at 45 mm [E]
T_MOTOR = 148.0                            # NEMA 17 at 0.5 A run current (docs/gear-trains.md §5) [E]


def clutch_window() -> dict:
    """The slip torque must carry 3 times the running torque and stay below a finger's torque;
    returns that window (N·mm) and the washer preload that gives it (N), with two friction faces."""
    lo, hi = 3.0 * T_RUN, T_SET
    to_f = lambda t: t / (2 * MU_CLUTCH * R_FRICTION)
    return {"slip_min": lo, "slip_max": hi, "preload_min": to_f(lo), "preload_max": to_f(hi),
            "motor_margin": T_MOTOR / hi}


def check(a: Assembly, data: dict) -> dict:
    env = a.envelope()
    return {
        "interference": [{"a": x, "b": y, "volume_mm3": round(v, 3)} for x, y, v in a.interference()],
        "bed_fit_single": [r for r in a.bed_fit(BED_SINGLE) if not r["fits"]],
        "bed_fit_dual": [r for r in a.bed_fit(BED_DUAL) if not r["fits"]],
        "envelope": {"x": [round(env.min.X, 1), round(env.max.X, 1)], "y": [round(env.min.Y, 1), round(env.max.Y, 1)],
                     "z": [round(env.min.Z, 1), round(env.max.Z, 1)]},
        "parts": len(a.items),
        "printed": len([i for i in a.items if i.printed]),
        "bought": len([i for i in a.items if not i.printed]),
        **data,
    }


def renders(a: Assembly, out: Path):
    out.mkdir(parents=True, exist_ok=True)
    a.render(out / "m1_front.png", elev=0, azim=-90, up="y", title="M1 mean-time dial, front", tolerance=0.1,
             size=(8, 8))
    a.render(out / "m1_three_quarter.png", elev=18, azim=-125, up="y", title="M1, three-quarter (dial and plates hidden)",
             hide=("front", "plates"), tolerance=0.15)
    a.render(out / "m1_rear.png", elev=15, azim=55, up="y", title="M1, rear three-quarter (plates hidden)",
             hide=("plates",), tolerance=0.15)


def main(out_dir="export/m1_time"):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    a, data = build()
    res = check(a, data)
    (out / "m1_time.json").write_text(json.dumps(res, indent=2, default=str))
    print(json.dumps({k: res[k] for k in ("interference", "bed_fit_single", "envelope", "parts", "printed", "bought")},
                     indent=2))
    renders(a, out)
    write_dae(a, out / "m1_time.dae")
    return a, res


if __name__ == "__main__":
    main(*sys.argv[1:])
