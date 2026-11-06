"""E2, the four ages and Death: detail design, part 1 (docs/e2-design.md §10).

Part 1 models the hall, the ring (turntable) with its rollers, teeth and selection pegs, the two stop
fingers, the walk pinion, and the age cam that sets the bell finger's height. The drives that part 2
details (the walk train's clutch and program cam, the state module, the quarter and hour trains) are
placeholders here, at their true places, so the space they need is held. The figures are placeholders
too (part 3); their heights are the decided ones.

The model shows the rest state at 12:10: the child waits at the right doorway, the old man (who struck
at 12:00) stands at the left doorway. The age cam selects the child; the bell finger is withdrawn and
the waiting finger is in.

Frame: X to the viewer's right, Y away from the viewer, Z up; origin on Death's axis, on the floor.
Run:  python -m cad.modules.e2_ages.mechanism [out_dir]
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import build123d as bd

from cad.lib import motor_mount as MM
from cad.lib import parts
from cad.lib.assembly import BED_DUAL, BED_SINGLE, Assembly, write_dae
from cad.lib.gears import Gear, centre_distance, mesh_rotation, pair_shifts, spur_gear
from cad.lib.hardware import BEARINGS
from cad.modules.e2_ages import layout as L

DECK = (-44.0, -40.0)                       # the module's deck plate (z)
DECK_XY = (-145.0, 150.0, -62.0, 235.0)     # x0, x1, y0, y1
R_FINGER_SHAFT = 141.0                      # both stop fingers pivot here, outside the pegs
FINGER = dict(w=2.0, tip_r=132.2, h=2.5)    # the arm's tangential width, its tip radius, its height
WITHDRAW_DEG = 70.0                         # a finger swings this far about its shaft to let the pegs by
AGE_CAM = dict(axis_z=-80.0, r0=20.0, step=4.0, x=None, t=5.0)   # on the state arbor; x set below
STATE_ARBOR_Y = None                        # set below: under the bell finger's shaft
SUPPORT_R, SUPPORT_THETA = 118.0, (0.0, 90.0, 180.0, 270.0)     # 688ZZ under the ring (standard angles)
GUIDE_R, GUIDE_THETA = 100.0, (-30.0, 90.0, 210.0)              # 688ZZ inside the inner skirt
ISLAND_POSTS = ((0.0, 34.0), (52.0, 124.0), (-52.0, 124.0))
FLOOR_POSTS = ((60.0, -42.5), (-60.0, -42.5), (96.5, -25.0), (-96.5, -25.0))
MODEL_TIME = (12, 10)                       # the rest state shown (legal time)


def at(shape, xy, z=0.0):
    return shape.moved(bd.Location((xy[0], xy[1], z)))


def theta_of(phi: float) -> float:
    """Standard plan angle (from +X, anticlockwise) of ring angle φ."""
    return phi - 90.0


def annulus(r_in, r_out, z0, z1):
    return parts.disc(2 * r_out, z1 - z0, bore=2 * r_in, z0=z0)


def peg_at(phi, z, r0, r1, d):
    """A radial peg from r0 to r1 at ring angle φ and height z."""
    rod = bd.Cylinder(d / 2, r1 - r0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    rod = rod.rotate(bd.Axis.Y, 90).moved(bd.Location((r0, 0, z)))      # along +X from r0
    return rod.rotate(bd.Axis.Z, theta_of(phi)).moved(bd.Location((L.C[0], L.C[1], 0)))


def finger(phi_station, z_mid, z_lo=None, z_hi=None, engaged=True):
    """A stop finger: a vertical shaft at R_FINGER_SHAFT and an arm reaching in to FINGER['tip_r'], just
    downstream (φ smaller) of the station so a caught peg stops with its age at the station."""
    delta = math.degrees((L.PEG["d"] / 2 + FINGER["w"] / 2 + 0.2) / FINGER["tip_r"])
    phi_f = phi_station - delta
    z_lo = z_mid - FINGER["h"] / 2 if z_lo is None else z_lo
    z_hi = z_mid + FINGER["h"] / 2 if z_hi is None else z_hi
    arm = bd.Box(R_FINGER_SHAFT - FINGER["tip_r"] + 1.5, FINGER["w"], z_hi - z_lo,
                 align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((FINGER["tip_r"], 0, z_lo)))
    arm += bd.Cylinder(2.5, z_hi - z_lo, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(
        bd.Location((R_FINGER_SHAFT, 0, z_lo)))
    if not engaged:                         # swing outward about the shaft
        arm = arm.moved(bd.Location((-R_FINGER_SHAFT, 0, 0))).rotate(bd.Axis.Z, WITHDRAW_DEG).moved(
            bd.Location((R_FINGER_SHAFT, 0, 0)))
    arm = arm - bd.Cylinder(1.5 + 0.15, 200, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).moved(
        bd.Location((R_FINGER_SHAFT, 0, 0)))
    return arm.rotate(bd.Axis.Z, theta_of(phi_f)).moved(bd.Location((L.C[0], L.C[1], 0))), phi_f


def age_cam_radius(minutes: float) -> float:
    """The age cam's radius under the bell finger at a given minute of the legal hour (e2-design §4.2):
    child from :07.5, youth from :22.5, man from :37.5, old man from :52.5; the old man to child rise is a
    ramp from :01 to :07 so the riding shaft is lifted, not struck."""
    m = minutes % 60.0
    r0, s = AGE_CAM["r0"], AGE_CAM["step"]
    if 7.5 <= m < 22.5:
        return r0
    if 22.5 <= m < 37.5:
        return r0 - s
    if 37.5 <= m < 52.5:
        return r0 - 2 * s
    if m >= 52.5 or m < 1.0:
        return r0 - 3 * s
    return r0 - 3 * s + 3 * s * (m - 1.0) / 6.0 if m < 7.0 else r0


def age_cam(t: float):
    """The cam as a plate turning about X: 1 rev/h. Its angle under the follower (the top) is the minute."""
    import numpy as np
    pts = []
    for a in np.linspace(0, 360, 721)[:-1]:
        m = a / 6.0                         # cam angle a (deg) passes the top at minute a/6
        r = age_cam_radius(m)
        pts.append((r * math.cos(math.radians(90 - a)), r * math.sin(math.radians(90 - a))))
    face = bd.Face(bd.Wire.make_polygon([bd.Vector(x, y, 0) for x, y in pts], close=True))
    cam = bd.extrude(face, amount=t, dir=(0, 0, 1)) - bd.Cylinder(2.5 + 0.0, 3 * t)
    return cam                              # in its local frame: axis along Z, the top (y+) under the follower


def build():
    a = Assembly("e2_ages")
    data = {"notes": []}
    # ------------------------------------------------------------------ hall: floors, wall, piers
    x0, x1, y0, y1 = DECK_XY
    deck = at(parts.plate((x1 - x0, y1 - y0), DECK[1] - DECK[0], z0=DECK[0], corner_radius=8),
              ((x0 + x1) / 2, (y0 + y1) / 2))
    island = at(parts.disc(2 * (L.INNER_SKIRT[0] - L.FLOOR_GAP), L.FLOOR_T, z0=-L.FLOOR_T), L.C)
    front = bd.Box(2 * L.PIER["x"][1], L.BACK_WALL["y"][1] - L.FLOOR_FRONT, L.FLOOR_T,
                   align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN)).moved(bd.Location((0, L.FLOOR_FRONT, -L.FLOOR_T)))
    front -= at(parts.disc(2 * (L.ANNULUS[1] + L.FLOOR_GAP), 10, z0=-8), L.C)
    a.add("floor_island", island, material="PETG", group="hall", note="the static floor inside the ring: Death, "
          "the bells and the back wall stand on it")
    a.add("floor_front", front, material="PETG", group="hall", note="the static floor in front of the ring")
    wall = bd.Box(2 * L.BACK_WALL["x"], L.BACK_WALL["y"][1] - L.BACK_WALL["y"][0], L.BACK_WALL["h"],
                  align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN)).moved(bd.Location((0, L.BACK_WALL["y"][0], 0)))
    a.add("back_wall", wall, material="PETG", group="hall", note="the back wall; the doorways are the gaps at its "
          "ends [E: h 72]")
    for s in (-1, 1):
        px = L.PIER["x"]
        pier = bd.Box(px[1] - px[0], L.PIER["y"][1] - L.PIER["y"][0], L.PIER["h"],
                      align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN)).moved(
            bd.Location((px[0] if s > 0 else -px[1], L.PIER["y"][0], 0)))
        a.add(f"pier_{'right' if s > 0 else 'left'}", pier, material="PETG", group="hall")
    for k, p in enumerate(ISLAND_POSTS):
        a.add(f"island_post_{k}", at(parts.standoff(-L.FLOOR_T - DECK[1], od=8.0), p, DECK[1]), material="PETG",
              group="hall")
        a.allow(f"island_post_{k}", "deck"); a.allow(f"island_post_{k}", "floor_island")
    for k, p in enumerate(FLOOR_POSTS):
        a.add(f"floor_post_{k}", at(parts.standoff(-L.FLOOR_T - DECK[1], od=5.0, screw="M2"), p, DECK[1]),
              material="PETG", group="hall")
        a.allow(f"floor_post_{k}", "deck"); a.allow(f"floor_post_{k}", "floor_front")
    for nm in ("back_wall", "pier_left", "pier_right"):
        a.allow(nm, "floor_island" if nm == "back_wall" else "floor_front")

    # ------------------------------------------------------------------ Death, pedestal, bells (bought)
    px, py, pz = L.PEDESTAL
    a.add("pedestal", bd.Box(px, py, pz, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)), material="PETG",
          group="hall")
    a.allow("pedestal", "floor_island")
    a.add("death_placeholder", _figure(L.DEATH_H, (0.0, 0.0), pz), material="ghost", printed=False, group="figures",
          note=f"Death, {L.DEATH_H:.0f} mm (decided); the sculpted figure and its arm are parts 2-3")
    a.allow("death_placeholder", "pedestal")
    for s, nm in ((1, "ages_bell"), (-1, "deaths_bell")):
        b = L.BELL
        bell = bd.Sphere(b["d"] / 2).moved(bd.Location((0, 0, 0))) & bd.Box(40, 40, b["h"], align=(
            bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        bell = bell - (bd.Sphere(b["d"] / 2 - 1.0) & bd.Box(40, 40, b["h"], align=(bd.Align.CENTER, bd.Align.CENTER,
                                                                                    bd.Align.MIN)))
        a.add(nm, at(bell, (s * b["x"], b["y"]), b["rim_z"]), material="gold", printed=False, group="hall",
              note="small brass bowl bell, Ø21 [E]; sourcing open")
        post = at(parts.rod(4.0, b["rim_z"] + b["h"] + 4.0), (s * b["x"], b["y"] + 8.0))
        arm = bd.Box(4.0, 8.0, 3.0, align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.MIN)).moved(
            bd.Location((s * b["x"], b["y"] + 10.0, b["rim_z"] + b["h"] + 1.0)))
        hanger = at(parts.rod(3.0, 1.2), (s * b["x"], b["y"]), b["rim_z"] + b["h"] - 0.2)
        a.add(f"{nm}_bracket", post + arm + hanger, material="PETG", group="hall",
              note="bell bracket on the island floor")
        a.allow(f"{nm}_bracket", "floor_island"); a.allow(f"{nm}_bracket", nm)

    # ------------------------------------------------------------------ the ring
    sx, sp = pair_shifts(L.TEETH["z"], 16)
    g_ring, g_pin = Gear(L.TEETH["z"], L.TEETH["m"], shift=sx), Gear(16, L.TEETH["m"], shift=sp)
    cd = centre_distance(g_ring, g_pin)
    ring = annulus(L.ANNULUS[0], L.ANNULUS[1], -L.FLOOR_T, 0.0)
    ring += annulus(L.INNER_SKIRT[0], L.INNER_SKIRT[1], L.INNER_SKIRT[2], 0.0)   # up to the surface: prints flat
    ring += annulus(L.OUTER_BODY[0], L.OUTER_BODY[1], L.OUTER_BODY[2], -L.FLOOR_T + 0.01)
    teeth = spur_gear(g_ring, L.TEETH["face"][1] - L.TEETH["face"][0]).moved(bd.Location((0, 0, L.TEETH["face"][0])))
    teeth -= parts.disc(2 * L.OUTER_BODY[0], 20, z0=-15)
    ring = ring.moved(bd.Location((L.C[0], L.C[1], 0))) + teeth.moved(bd.Location((L.C[0], L.C[1], 0)))
    # the ring as modelled: the child (k = 0) at PHI_WAIT
    for k, (name, h) in enumerate(L.AGES):
        ring += peg_at(L.PHI_REST[k], L.PEG_Z[k], L.PEG["r"][0] - 0.5, L.PEG["r"][1], L.PEG["d"])
    a.add("ring", ring, material="PLA", group="ring", print_up=(0, 0, -1),
          note=f"turntable Ø{2 * L.ANNULUS[1]:.0f}: walking surface flush with the floor, {L.TEETH['z']} teeth, "
               "one peg per age at its own height (the selection)")
    data["ring"] = {"centre": L.C, "r_path": L.R_PATH, "od": 2 * L.ANNULUS[1], "teeth": L.TEETH["z"],
                    "pinion": 16, "centre_distance": round(cd, 3), "shifts": [round(sx, 3), round(sp, 3)]}

    # ------------------------------------------------------------------ rollers (688ZZ)
    b688 = BEARINGS["688ZZ"]
    for k, th in enumerate(SUPPORT_THETA):          # horizontal axes, radial; the ring rests on their tops
        zc = -L.FLOOR_T - b688.od / 2
        brg = parts.bearing(b688, -b688.width / 2).rotate(bd.Axis.Y, 90)
        stud = parts.rod(8.0, 12.0, z0=-b688.width / 2 - 1.0).rotate(bd.Axis.Y, 90)
        post = bd.Box(5.5, 8.0, zc - DECK[1] + 4.0, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN)).moved(
            bd.Location((b688.width / 2 + 0.6, 0, DECK[1] - zc)))
        for nm, shp, mat, pr in ((f"support_roller_{k}", brg, "bearing", False), (f"support_stud_{k}", stud, "steel", False),
                                 (f"support_post_{k}", post, "PETG", True)):
            shp = shp.moved(bd.Location((SUPPORT_R, 0, zc))).rotate(bd.Axis.Z, th).moved(bd.Location((L.C[0], L.C[1], 0)))
            a.add(nm, shp, material=mat, printed=pr, group="ring")
        a.allow(f"support_roller_{k}", f"support_stud_{k}"); a.allow(f"support_stud_{k}", f"support_post_{k}")
        a.allow(f"support_post_{k}", "deck"); a.allow(f"support_roller_{k}", "ring")
    for k, th in enumerate(GUIDE_THETA):            # vertical axes, inside the inner skirt
        p = (L.C[0] + GUIDE_R * math.cos(math.radians(th)), L.C[1] + GUIDE_R * math.sin(math.radians(th)))
        z0 = L.INNER_SKIRT[2] + 1.0
        a.add(f"guide_roller_{k}", at(parts.bearing(b688, z0), p), material="bearing", printed=False, group="ring")
        a.add(f"guide_stud_{k}", at(parts.rod(8.0, z0 + b688.width + 1.0 - DECK[0]), p, DECK[0]), material="steel",
              printed=False, group="ring")
        a.allow(f"guide_roller_{k}", f"guide_stud_{k}"); a.allow(f"guide_stud_{k}", "deck")
        a.allow(f"guide_roller_{k}", "ring")

    # ------------------------------------------------------------------ the ages (placeholders) on the ring
    for k, (name, h) in enumerate(L.AGES):
        xy = L.polar(L.PHI_REST[k], L.R_PATH)
        a.add(f"age_{name}_placeholder", _figure(h, xy, 0.0), material="ghost", printed=False, group="figures",
              note=f"the {name.replace('_', ' ')}, {h:.1f} mm; sculpted in part 3, its arm and push pin in part 2")
        a.allow(f"age_{name}_placeholder", "ring")

    # ------------------------------------------------------------------ the walk pinion and the walk drive (part 2)
    th_p = -60.0
    pp = (L.C[0] + cd * math.cos(math.radians(th_p)), L.C[1] + cd * math.sin(math.radians(th_p)))
    pin_face = (L.TEETH["face"][0], -L.FLOOR_T - 0.4)
    pin = spur_gear(g_pin, pin_face[1] - pin_face[0]).moved(bd.Location((0, 0, pin_face[0])))
    pin = pin.rotate(bd.Axis.Z, mesh_rotation(g_ring, g_pin, th_p)) - parts.disc(5.0 + parts.FITS.press, 30, z0=-20)
    a.add("walk_pinion_16", at(pin, pp), group="drive", note="walk pinion on the clutch shaft (the clutch is part 2)")
    a.add("walk_shaft", at(parts.rod(5.0, pin_face[1] - DECK[0]), pp, DECK[0]), material="steel", printed=False,
          group="drive")
    a.allow("walk_pinion_16", "walk_shaft"); a.allow("walk_shaft", "deck")
    reserve = at(parts.disc(30.0, L.OUTER_BODY[2] - 0.5 - DECK[1] - 0.1, z0=DECK[1] + 0.1), pp)
    a.add("walk_drive_reserve", reserve - at(parts.disc(5.4, 60, z0=-60), pp), material="ghost", printed=False,
          group="placeholders", note="part 2: the slip clutch, the program cam's gearing")
    a.allow("walk_drive_reserve", "walk_shaft")
    wm = (pp[0] + 18.0 * math.cos(math.radians(50.0)), pp[1] + 18.0 * math.sin(math.radians(50.0)))   # clear of the
    #                                                                    state arbor's line
    a.add("walk_motor_placeholder", at(bd.Box(12.0, 10.0, 31.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)),
                                       wm, DECK[0]), material="black", printed=False, group="placeholders",
          note="micro metal gearmotor, ≈ 33 rpm [E]; part 2 places it on its bracket")
    data["walk"] = {"pinion_xy": [round(v, 2) for v in pp], "ring_speed_deg_s": L.RING_SPEED, **L.walk_timing()}

    # ------------------------------------------------------------------ stop fingers
    k_sel = 0                                         # 12:10: the age cam selects the child
    z_sel = L.PEG_Z[k_sel]
    bell_f, phi_bf = finger(L.PHI_BELL, z_sel, engaged=False)
    wait_f, phi_wf = finger(L.PHI_WAIT, None, z_lo=L.PEG_Z[-1] - 2.0, z_hi=L.PEG_Z[0] + 2.0, engaged=True)
    a.add("bell_finger", bell_f, group="stops", note="at the selected age's peg height; swung in for the walk out "
          "only (program cam, part 2)")
    a.add("waiting_finger", wait_f, group="stops", note="spans every peg height; in at rest and for the walk on")
    sh_b = L.polar(phi_bf, R_FINGER_SHAFT)
    sh_w = L.polar(phi_wf, R_FINGER_SHAFT)
    cam_x = sh_b[0]
    r_now = age_cam_radius(MODEL_TIME[1])
    shaft_bottom = AGE_CAM["axis_z"] + r_now
    a.add("bell_finger_shaft", at(parts.rod(3.0, z_sel + 6.0 - shaft_bottom), sh_b, shaft_bottom), material="steel",
          printed=False, group="stops", note="rides on the age cam: its height is the selection")
    a.add("waiting_finger_shaft", at(parts.rod(3.0, L.PEG_Z[0] + 6.0 - DECK[0]), sh_w, DECK[0]), material="steel",
          printed=False, group="stops")
    for f_, s_ in (("bell_finger", "bell_finger_shaft"), ("waiting_finger", "waiting_finger_shaft")):
        a.allow(f_, s_); a.allow(s_, "deck")
    data["stops"] = {"bell_finger_phi": round(phi_bf, 3), "waiting_finger_phi": round(phi_wf, 3),
                     "bell_shaft_xy": [round(v, 2) for v in sh_b], "waiting_shaft_xy": [round(v, 2) for v in sh_w]}

    # ------------------------------------------------------------------ the state module (part 2) and its age cam
    cam = age_cam(AGE_CAM["t"]).rotate(bd.Axis.Z, -6.0 * MODEL_TIME[1])   # the minute under the follower
    cam = cam.rotate(bd.Axis.Y, 90).moved(bd.Location((cam_x - AGE_CAM["t"] / 2, sh_b[1], AGE_CAM["axis_z"])))
    a.add("age_cam", cam, group="state", note="on the state arbor, 1 rev/h legal time: sets the bell finger's height "
          "(4 steps of 4 mm, a ramp back from the old man to the child)")
    arbor_x = (cam_x - 20.0, 100.0)
    a.add("state_arbor", parts.rod(5.0, arbor_x[1] - arbor_x[0]).rotate(bd.Axis.Y, 90).moved(
        bd.Location((arbor_x[0], sh_b[1], AGE_CAM["axis_z"]))), material="steel", printed=False, group="state")
    a.allow("age_cam", "state_arbor"); a.allow("bell_finger_shaft", "age_cam")
    motor = MM.motor_body(0.0).rotate(bd.Axis.Y, -90).moved(bd.Location((arbor_x[1] + MM.ADAPTER["t"], sh_b[1],
                                                                          AGE_CAM["axis_z"])))
    a.add("state_motor_placeholder", motor, material="black", printed=False, group="placeholders",
          note="E2's state stepper, NEMA 17 on its D16 adapter, withdrawn to the right; the snails and 12:1 are "
               "part 2")
    a.add("state_module_reserve", bd.Box(arbor_x[1] - 2.0 - (cam_x + AGE_CAM["t"] + 3.0), 40.0, 40.0,
                                         align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER)).moved(
        bd.Location((cam_x + AGE_CAM["t"] + 3.0, sh_b[1] + 0.0, AGE_CAM["axis_z"]))) - bd.Cylinder(
        3.0, 300, rotation=(0, 90, 0)).moved(bd.Location((0, sh_b[1], AGE_CAM["axis_z"]))),
          material="ghost", printed=False, group="placeholders",
          note="part 2: the quarter snail, the 12:1 motion work and the hour snail, the index and witness Halls")
    a.allow("state_module_reserve", "state_arbor")
    data["state"] = {"age_cam_radius_now": r_now, "arbor_y": round(sh_b[1], 2), "axis_z": AGE_CAM["axis_z"]}
    a.add("deck", deck - at(parts.disc(3.6, 10, z0=DECK[0] - 1), sh_b) - at(bd.Box(13.0, 11.0, 10.0), wm),
          material="PETG", group="hall", note="the module's deck: rollers, posts and drives stand on it")
    return a, data


def _figure(h, xy, z0):
    """A placeholder figure: base, body, head."""
    base = parts.disc(L.BASE_D, 2.0, z0=z0)
    body = bd.Cylinder(5.5, 0.82 * h - 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(
        bd.Location((0, 0, z0 + 2.0)))
    head = bd.Sphere(0.07 * h).moved(bd.Location((0, 0, z0 + h - 0.07 * h)))
    return at(base + body + head, xy)


def check(a: Assembly, data: dict) -> dict:
    env = a.envelope()
    return {
        "interference": [{"a": x, "b": y, "volume_mm3": round(v, 3)} for x, y, v in a.interference()],
        "bed_fit_single": [r for r in a.bed_fit(BED_SINGLE) if not r["fits"]],
        "bed_fit_dual": [r for r in a.bed_fit(BED_DUAL) if not r["fits"]],
        "envelope": {"x": [round(env.min.X, 1), round(env.max.X, 1)], "y": [round(env.min.Y, 1), round(env.max.Y, 1)],
                     "z": [round(env.min.Z, 1), round(env.max.Z, 1)]},
        "parts": len(a.items), "printed": len([i for i in a.items if i.printed]),
        "bought_or_placeholder": len([i for i in a.items if not i.printed]),
        "depth": L.depth(), **data,
    }


def renders(a: Assembly, out: Path):
    out.mkdir(parents=True, exist_ok=True)
    a.render(out / "e2_front.png", elev=12, azim=-90, title="E2 part 1: the hall from the front (rest, 12:10)",
             tolerance=0.3, size=(9, 7))
    a.render(out / "e2_plan.png", elev=89, azim=-90, title="E2 part 1: plan (the ring, its rollers, the stops)",
             hide=("placeholders",), tolerance=0.3, size=(8, 9))
    a.render(out / "e2_three_quarter.png", elev=22, azim=-60, title="E2 part 1: three-quarter (hall hidden)",
             hide=("hall",), tolerance=0.3, size=(9, 8))


def main(out_dir="export/e2_ages"):
    out = Path(out_dir)
    a, data = build()
    res = check(a, data)
    out.mkdir(parents=True, exist_ok=True)
    (out / "e2_ages.json").write_text(json.dumps(res, indent=2, default=str))
    print(json.dumps({k: res[k] for k in ("interference", "bed_fit_single", "envelope", "parts", "printed")}, indent=2))
    renders(a, out)
    write_dae(a, out / "e2_ages.dae")
    return a, res


if __name__ == "__main__":
    main(*sys.argv[1:])
