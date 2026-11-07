"""E2 part 2a: the stops, the walk drive and the state module (docs/e2-design.md §10.8).

The stops (Paul, PR #16: the program cam on the walk train swings them):
- two vertical shafts at R 141 by the bell station, 12.5 mm apart, geared 1:1 below the deck so they turn in
  opposite senses. The bell arm rides on a 3 mm square brass rod that slides in a keyed sleeve: the age cam sets
  its height (the selection). The waiting arm sits on a Ø3 steel shaft at a fixed height, level with the waiting
  pegs. Each arm swings out 70° downstream, so a held peg's own push helps its release;
- the waiting shaft's crank is driven by the push rod, the program cam's radial translating follower.

Walk drive (one DC gearmotor; three event motors, §9.2):
- the gearmotor's 12-tooth pinion drives the input compound (24 + 12'), free on the walk shaft. A wave washer
  presses the compound's friction boss up against a hub pressed on the shaft (the slip clutch). The walk pinion
  16 is pressed on the top of the shaft and turns the ring;
- the compound's 12' drives the program gear 72 (1:6): one program turn per show. Below the deck the program
  shaft carries the grooved program cam and the lock cam with two notches; a microswitch stops the motor at the
  end of each phase;
- a Hall under the ring at the bell station sees a magnet under each age: an age was caught.

State module (E2's own stepper, 1 rev/h legal time, decided at the M1 gate; D16: it plugs in from the right):
- the state arbor, along X under the stops, carries the age cam (under the bell rod), the quarter snail (part
  2b's quarter rack falls on it), the index disc, and the 12-tooth pinion of the 12:1 motion work (12/48 ·
  15/45, as M1). The hour wheel carries the hour snail on its tube; a witness Hall reads the snail at 12:00.

Frame as in mechanism.py: X right, Y away from the viewer, Z up. Every [E] is listed in e2-design §10.8.
"""
from __future__ import annotations

import math

import build123d as bd

from cad.lib import motor_mount as MM
from cad.lib import parts
from cad.lib.gears import Gear, centre_distance, mesh_rotation, pair_shifts, spur_gear
from cad.lib.hardware import BEARINGS
from cad.modules.e2_ages import layout as L
from cad.modules.e2_ages import program as G
from cad.modules.e2_ages import striking as S

DECK = (-47.0, -43.0)                        # the module's deck plate (z); lowered 3 mm in part 2a
STATE_Z = S.ARBOR_Z                          # the state arbor's axis
AGE_CAM = dict(r0=20.0, step=4.0, t=5.0)     # 4 steps of 4 mm (the selection pegs' spacing)
SNAIL_Q = tuple(S.snail_radii(S.QUARTER))     # quarter snail radii for 1..4 pairs [D: from the rack, striking.py]
SNAIL_H = tuple(S.snail_radii(S.HOUR))        # hour snail radii for 1..12 strokes [D: from the rack]
quarter_snail_radius = S.quarter_snail_radius
hour_snail_radius = S.hour_snail_radius
HALL = (8.0, 6.0, 3.0)                       # [E] DRV5032 on a small board: long side, short side, thickness
MAGNET = (5.0, 2.0)                          # [E] Ø5 x 2 NdFeB disc
MAGNET_R = 123.5                             # magnets under the ages: clear of the support rollers' track
WITNESS_R = 9.0                              # the hour snail's magnet, on its 6 o'clock step: under the snail at 12:00
STARLOCK = {5.0: (11.0, 0.4), 4.0: (9.0, 0.4)}   # push-on lock washers (OD, thickness) [E: check the chosen part]
WAVE = (10.0, 0.6)                           # wave washer for Ø5, compressed height [E]
SQUARE = 3.0                                 # the bell stop's brass square rod
GEARMOTOR = dict(w=12.0, d=10.0, length=34.5, shaft_d=3.0, shaft_l=9.0)   # [E] ⚠ check the chosen gearmotor
MOTOR_DIR = 50.0                             # the gearmotor, seen from the walk shaft (plan angle)
SWITCH = dict(l=12.8, w=5.8, h=6.5, r=30.0)  # [E] subminiature roller microswitch, its centre's distance from P
LOCK_R, NOTCH = 12.0, (1.5, 4.0, 16.0)       # the lock cam's radius; a notch's depth, its ramp and its flat (deg)
MODEL_TIME = (12, 10)                        # the rest state shown (legal time)


def at(shape, xy, z=0.0):
    return shape.moved(bd.Location((xy[0], xy[1], z)))


def on_x(shape, x0, y, z):
    """A shape built about the +Z axis (z from 0), laid along +X from x0 on the axis (y, z); its local +y
    points up (+Z) and its local +x points to +Y."""
    return shape.rotate(bd.Axis.Y, 90).rotate(bd.Axis.X, 90).moved(bd.Location((x0, y, z)))


def polar_xy(origin, r, deg):
    return (origin[0] + r * math.cos(math.radians(deg)), origin[1] + r * math.sin(math.radians(deg)))


def zdisc(d, z0, z1, bore=0.0):
    return parts.disc(d, z1 - z0, bore=bore, z0=z0)


def box(sx, sy, z0, z1, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)):
    return bd.Box(sx, sy, z1 - z0, align=align).moved(bd.Location((0, 0, z0)))


def gear(g, z0, z1, bore, fit="press", rot=0.0):
    part = spur_gear(g, z1 - z0).rotate(bd.Axis.Z, rot).moved(bd.Location((0, 0, z0)))
    return part - zdisc(bore + getattr(parts.FITS, fit), z0 - 1, z1 + 1)


def profile_plate(radius_of_angle, t, bore, samples=720):
    """A plate (local, about +Z, z 0..t) whose radius at local angle a (deg) is radius_of_angle(a)."""
    pts = []
    for i in range(samples):
        a = 360.0 * i / samples
        r = radius_of_angle(a)
        pts.append(bd.Vector(r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), 0))
    face = bd.Face(bd.Wire.make_polygon(pts, close=True))
    part = bd.extrude(face, amount=t, dir=(0, 0, 1))
    return part - zdisc(bore, -1, t + 1) if bore > 0 else part


# ------------------------------------------------------------------------------------------------ the state cams
def age_cam_radius(minutes: float) -> float:
    """The age cam's radius under the bell rod at a minute of the legal hour (e2-design §4.2): child from :07.5,
    youth from :22.5, man from :37.5, old man from :52.5; the old man to child rise is a ramp from :01 to :07, so
    the riding rod is lifted, not struck."""
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


def arbor_cam(radius_of_time, period, t, bore=5.0 + parts.FITS.press):
    """A cam on an arbor turning +360°/period: the local angle a passes the top (local +y) at time
    (90 - a) / 360 · period, which is when its radius is radius_of_time(that time)."""
    return profile_plate(lambda a: radius_of_time(((90.0 - a) % 360.0) / 360.0 * period), t, bore)


# ------------------------------------------------------------------------------------------------ the stops
def stop_arm(shaft_xy, z0, z1, swing_deg, hub_d=6.0, hub_z=None, bore=None, square=False):
    """A stop arm: a blade from the shaft toward C to the tip at R STOP['tip'], width STOP['w'], between z0 and
    z1, on a hub; swung out swing_deg (CCW = downstream) about its shaft."""
    reach = math.dist(shaft_xy, L.C) - L.STOP["tip"]
    blade = box(reach, L.STOP["w"], z0, z1, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN))
    h0, h1 = hub_z or (z0, z1)
    arm = blade + zdisc(hub_d, h0, h1)
    if bore is not None:
        if square:
            arm -= box(bore + parts.FITS.press, bore + parts.FITS.press, h0 - 1, h1 + 1)
        else:
            arm -= zdisc(bore + parts.FITS.press, h0 - 1, h1 + 1)
    return at(arm.rotate(bd.Axis.Z, G.radial_dir(shaft_xy) + swing_deg), shaft_xy)


def peg_shape(phi, z, r0, r1, d):
    """A radial peg from r0 to r1 at ring angle φ and height z."""
    rod = bd.Cylinder(d / 2, r1 - r0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    rod = rod.rotate(bd.Axis.Y, 90).moved(bd.Location((r0, 0, z)))      # along +X from r0
    return rod.rotate(bd.Axis.Z, phi - 90.0).moved(bd.Location((L.C[0], L.C[1], 0)))


def below_levels():
    d0 = DECK[0]
    return dict(stop_gear=(d0 - 2.5, d0 - 0.3), crank=(d0 - 4.3, d0 - 2.5), crank_pin=(d0 - 8.6, d0 - 3.0),
                rod=(d0 - 8.2, d0 - 6.0), prog_cam=(d0 - 4.6, d0 - 0.3), groove=1.8, follower=(d0 - 6.0, d0 - 3.0),
                lock_cam=(d0 - 11.0, d0 - 9.0), prog_brg=(d0, d0 + 2.5), guide=(d0 - 10.0, d0))


def bell_rod_bottom(minutes):
    return STATE_Z + age_cam_radius(minutes)


def add_stops(a, theta: float, k_sel: int, minutes: float):
    """The two stop shafts, their arms, the stop gears, the crank and the push rod, at program angle theta with
    the age cam at `minutes` (the selected age k_sel)."""
    pl, lv, g = G.plan(), below_levels(), G.gears()
    sb, sw = pl["bell_shaft"], pl["wait_shaft"]
    arms = G.arms(theta)
    z_sel = L.PEG_Z[k_sel]
    data = {"bell_shaft": [round(v, 2) for v in sb], "wait_shaft": [round(v, 2) for v in sw],
            "spacing": round(math.dist(sb, sw), 3), "swing": arms}
    # bell stop: square brass rod riding on the age cam; arm at the selected height; keyed sleeve in the deck
    z_bot = bell_rod_bottom(minutes)
    z_top = z_sel + L.STOP["h"] / 2
    rot_b = G.radial_dir(sb) + arms["bell"]
    rod = box(SQUARE, SQUARE, z_bot, z_top).rotate(bd.Axis.Z, rot_b)
    a.add("bell_rod", at(rod, sb), material="brass", printed=False, group="stops",
          note="3 x 3 brass square rod: rides on the age cam (its height is the selection), turns with its sleeve")
    a.add("bell_arm", stop_arm(sb, z_sel - L.STOP["h"] / 2, z_top, arms["bell"], hub_d=7.0, bore=SQUARE, square=True),
          group="stops", note="pressed on the square rod: catches only the selected age's peg")
    sleeve_z = (lv["stop_gear"][0], -28.0)
    sleeve_parts = zdisc(6.0, *sleeve_z)
    sleeve_parts -= box(SQUARE + parts.FITS.running, SQUARE + parts.FITS.running, sleeve_z[0] - 1, sleeve_z[1] + 1)
    collar = zdisc(10.0, DECK[1] + 0.3, DECK[1] + 1.5, bore=6.0 + parts.FITS.press)
    a.add("bell_collar", at(collar, sb), group="stops", note="pressed on the sleeve above the deck: it rests on the deck")
    # waiting stop: Ø3 steel shaft, arm level with the waiting pegs, its hub down to the deck
    wz = L.STOP["wait_z"]
    a.add("wait_shaft", at(parts.rod(3.0, wz[1] - lv["crank"][0], z0=lv["crank"][0]), sw), material="steel",
          printed=False, group="stops", note="Ø3 ground rod, turns in the deck")
    a.add("wait_arm", stop_arm(sw, wz[0], wz[1], arms["wait"], hub_d=6.0, hub_z=(DECK[1] + 0.3, wz[1]), bore=3.0),
          group="stops", note="pressed on its shaft: catches any waiting peg; its hub rests on the deck")
    # the gears (1:1, opposite senses) and the crank, under the deck
    cg = G.crank()
    gam = cg["gamma_A"] - arms["bell"]                        # the crank's plan angle now
    wg = gear(g["stop_w"], *lv["stop_gear"], 3.0)
    lever = (box(G.CRANK, 5.0, lv["crank"][0], lv["crank"][1], align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN))
             + zdisc(5.0, *lv["crank"]).moved(bd.Location((G.CRANK, 0, 0))) + zdisc(7.0, *lv["crank"]))
    lever -= zdisc(3.0 + parts.FITS.press, lv["crank"][0] - 1, lv["crank"][1] + 1)
    lever -= zdisc(2.0 + parts.FITS.press, lv["crank"][0] - 1, lv["crank"][1] + 1).moved(bd.Location((G.CRANK, 0, 0)))
    a.add("wait_gear_crank", at((wg + lever).rotate(bd.Axis.Z, gam), sw), group="stops",
          note="12 teeth and the crank (r 5) in one print, pressed on the waiting shaft", print_up=(0, 0, -1))
    a.add("crank_pin", at(parts.rod(2.0, lv["crank_pin"][1] - lv["crank_pin"][0], z0=lv["crank_pin"][0]),
                         cg["pin"](gam)), material="steel", printed=False, group="stops",
          note="Ø2 steel pin, pressed in the crank, runs in the push rod's yoke")
    th_bw = math.degrees(math.atan2(sb[1] - sw[1], sb[0] - sw[0]))
    rb = mesh_rotation(g["stop_w"], g["stop_b"], th_bw, gam)
    sleeve = sleeve_parts.rotate(bd.Axis.Z, rot_b) + gear(g["stop_b"], *lv["stop_gear"], 3.0, rot=rb)
    sleeve -= box(SQUARE + parts.FITS.running, SQUARE + parts.FITS.running, sleeve_z[0] - 1,
                  sleeve_z[1] + 1).rotate(bd.Axis.Z, rot_b)
    a.add("bell_sleeve", at(sleeve, sb), group="stops", note="12 teeth and the keyed sleeve in one print: turns in the "
          "deck, opposite to the waiting shaft; the square rod slides in it")
    for x, y in (("bell_arm", "bell_rod"), ("bell_sleeve", "bell_rod"), ("bell_collar", "bell_sleeve"),
                 ("bell_collar", "deck"),
                 ("wait_arm", "wait_shaft"), ("wait_gear_crank", "wait_shaft"), ("crank_pin", "wait_gear_crank"),
                 ("bell_sleeve", "deck"), ("wait_shaft", "deck"), ("wait_arm", "deck"), ("bell_rod", "age_cam"),
                 ("bell_sleeve", "wait_gear_crank")):
        a.allow(x, y)
    # the push rod: a flat bar along u through P, the follower pin near P, the yoke round the crank pin
    P, u, n = cg["P"], cg["u"], cg["n"]
    r_now = G.groove_radius(theta, cg)
    s0, s1 = r_now - 3.5, r_now + cg["rod_len"] + 4.0
    ang_u = math.degrees(math.atan2(u[1], u[0]))
    bar = box(s1 - s0, 5.0, *lv["rod"], align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN)).moved(
        bd.Location((s0, 0, 0)))
    pin_now = cg["pin"](gam)
    lat = (pin_now[0] - P[0]) * n[0] + (pin_now[1] - P[1]) * n[1]
    s_pin = cg["along"](pin_now)
    bar += box(8.0, 9.0, *lv["rod"]).moved(bd.Location((s_pin, 0, 0)))
    bar -= box(2.0 + parts.FITS.running, 4.0, lv["rod"][0] - 1, lv["rod"][1] + 1).moved(bd.Location((s_pin, 0, 0)))
    a.add("push_rod", at(bar.rotate(bd.Axis.Z, ang_u), P), material="PETG", group="stops",
          note="the program cam's follower: slides in two guides; its yoke turns the crank")
    fol = parts.rod(2.5, lv["follower"][1] - lv["follower"][0], z0=lv["follower"][0])
    a.add("follower_pin", at(fol, (P[0] + r_now * u[0], P[1] + r_now * u[1])), material="steel", printed=False,
          group="stops", note="Ø2.5 steel pin pressed in the rod; runs in the program cam's groove")
    a.allow("follower_pin", "push_rod")
    for k, s in enumerate((30.0, 45.0)):
        gd = box(8.0, 11.0, *lv["guide"]) - box(10.0, 5.0 + parts.FITS.running, lv["rod"][0] - 0.2,
                                                lv["rod"][1] + 0.2)
        a.add(f"rod_guide_{k}", at(gd.rotate(bd.Axis.Z, ang_u), (P[0] + s * u[0], P[1] + s * u[1])), material="PETG",
              group="stops", note="hangs from the deck (two M2 into inserts)")
        a.allow(f"rod_guide_{k}", "deck")
    data.update({"crank_gamma": round(gam, 2), "groove_r": round(r_now, 3), "rod_len": round(cg["rod_len"], 3),
                 "pin_lateral": round(lat, 3), "bell_rod_z": [round(z_bot, 2), round(z_top, 2)]})
    cuts = [at(zdisc(6.0 + parts.FITS.running, DECK[0] - 1, DECK[1] + 1), sb),
            at(zdisc(3.0 + parts.FITS.running, DECK[0] - 1, DECK[1] + 1), sw)]
    return data, [], cuts


# ------------------------------------------------------------------------------------------------ walk drive
def walk_levels():
    d0, d1 = DECK
    lv = {"spacer": (d1, d1 + 1.0)}
    lv["washer"] = (lv["spacer"][1], lv["spacer"][1] + WAVE[1])
    lv["g24"] = (lv["washer"][1], lv["washer"][1] + 2.5)
    lv["neck"] = (lv["g24"][1], lv["g24"][1] + 0.4)
    lv["g12p"] = (lv["neck"][1], lv["neck"][1] + 2.5)
    lv["boss"] = (lv["g12p"][1], lv["g12p"][1] + 0.6)
    lv["hub"] = (lv["boss"][1], lv["boss"][1] + 2.0)
    lv["walk_boss"] = (d0 - 4.0, d0)
    lv["brg_top"] = (d1 - 2.5, d1)
    lv["brg_bot"] = (d0 - 4.0, d0 - 1.5)
    lv["starlock"] = (d0 - 4.0 - STARLOCK[5.0][1], d0 - 4.0)
    lv["prog_boss"] = (d1, lv["g12p"][0] - 0.3)
    lv["prog_brg_top"] = (lv["prog_boss"][1] - 2.5, lv["prog_boss"][1])
    return lv


def add_walk_drive(a, theta: float):
    """The walk shaft and its clutch, the gearmotor, the program shaft with its cams, the lock switch."""
    pl, lv, lb, g = G.plan(), walk_levels(), below_levels(), G.gears()
    pp, P = pl["walk"], pl["program"]
    b85 = BEARINGS["MR85ZZ"]
    adds, cuts = [], []
    # walk shaft: two MR85ZZ (deck top; the boss under the deck), a Starlock under, the pinion on top
    shaft_z = (lv["starlock"][0], L.TEETH["face"][1] - 0.4)
    a.add("walk_shaft", at(parts.rod(5.0, shaft_z[1] - shaft_z[0], z0=shaft_z[0]), pp), material="steel",
          printed=False, group="drive", note="Ø5 ground rod")
    for nm, (z0, _) in (("walk_bearing_top", lv["brg_top"]), ("walk_bearing_bottom", lv["brg_bot"])):
        a.add(nm, at(parts.bearing(b85, z0), pp), material="bearing", printed=False, group="drive", note="MR85ZZ")
        a.allow(nm, "walk_shaft"); a.allow(nm, "deck")
    a.add("walk_starlock", at(zdisc(STARLOCK[5.0][0], *lv["starlock"], bore=5.0), pp), material="steel",
          printed=False, group="drive", note="Starlock for Ø5: holds the shaft down against the clutch's preload")
    a.allow("walk_starlock", "walk_shaft"); a.allow("walk_starlock", "walk_bearing_bottom")
    blk = zdisc(18.0, *lv["walk_boss"]) - zdisc(b85.od + parts.FITS.bearing_seat, lv["brg_bot"][0] - 1, lv["brg_bot"][1])
    blk -= zdisc(6.5, lv["walk_boss"][0] - 1, lv["walk_boss"][1] + 1)
    for dx in (-6.5, 6.5):
        blk -= zdisc(2.4, lv["walk_boss"][0] - 1, lv["walk_boss"][1] + 1).moved(bd.Location((dx, 0, 0)))
    a.add("walk_bearing_block", at(blk.rotate(bd.Axis.Z, G.PROG_DIR + 90.0), pp), material="PETG", group="drive",
          note="the walk shaft's lower bearing: screwed under the deck (2 x M2)")
    a.allow("walk_bearing_block", "deck"); a.allow("walk_bearing_block", "walk_bearing_bottom")
    cuts += [at(zdisc(b85.od + parts.FITS.bearing_seat, lv["brg_top"][0], lv["brg_top"][1] + 1), pp),
             at(zdisc(6.5, DECK[0] - 1, DECK[1] + 1), pp)]
    # the clutch: spacer | wave washer | compound (free) | hub (pressed)
    a.add("walk_spacer", at(zdisc(7.5, *lv["spacer"], bore=5.0 + parts.FITS.running), pp), group="drive",
          note="on the top bearing's inner race")
    a.add("walk_wave_washer", at(zdisc(WAVE[0], *lv["washer"], bore=5.3), pp), material="steel", printed=False,
          group="drive", note="wave washer for Ø5: the clutch's preload [E]")
    comp = gear(g["g24"], *lv["g24"], 5.0, "running") + gear(g["g12p"], *lv["g12p"], 5.0, "running")
    comp += zdisc(10.0, lv["neck"][0] - 0.01, lv["neck"][1] + 0.01, bore=5.3) + zdisc(8.0, *lv["boss"], bore=5.3)
    a.add("walk_compound", at(comp, pp), group="drive",
          note="24 + 12' in one print, free on the walk shaft: the clutch's driven member")
    a.add("walk_hub", at(zdisc(12.0, *lv["hub"], bore=5.0 + parts.FITS.press), pp), group="drive",
          note="pressed on the walk shaft: the clutch's friction face")
    for x, y in (("walk_spacer", "walk_bearing_top"), ("walk_wave_washer", "walk_spacer"),
                 ("walk_wave_washer", "walk_compound"), ("walk_compound", "walk_hub"), ("walk_hub", "walk_shaft"),
                 ("walk_spacer", "walk_shaft"), ("walk_wave_washer", "walk_shaft"), ("walk_compound", "walk_shaft"),
                 ("walk_shaft", "walk_pinion_16")):
        a.allow(x, y)
    # the gearmotor below the deck, its pinion through a Ø16 hole, in a bracket screwed under the deck
    wm = polar_xy(pp, centre_distance(g["m12"], g["g24"]), MOTOR_DIR)
    gm = GEARMOTOR
    face, d0 = DECK[0] - 1.0, DECK[0]                        # the gearbox face 1 mm under the deck
    motor = box(gm["w"], gm["d"], face - gm["length"], face).rotate(bd.Axis.Z, MOTOR_DIR)
    motor += parts.rod(gm["shaft_d"], gm["shaft_l"], z0=face)
    a.add("walk_motor", at(motor, wm), material="black", printed=False, group="drive",
          note="micro metal gearmotor, 12 x 10 mm, ≈ 32 rpm [E] ⚠ check the chosen motor's length and shaft")
    rm = mesh_rotation(g["g24"], g["m12"], MOTOR_DIR, 0.0)
    pin12 = gear(g["m12"], *lv["g24"], gm["shaft_d"], rot=rm)
    a.add("walk_motor_pinion_12", at(pin12, wm), group="drive", note="pressed on the gearmotor's Ø3 D-shaft")
    a.allow("walk_motor_pinion_12", "walk_motor")
    wall = 1.6
    sleeve = box(gm["w"] + 0.4 + 2 * wall, gm["d"] + 0.4 + 2 * wall, face - gm["length"] - 2.0, d0 - 2.0)
    sleeve -= box(gm["w"] + 0.4, gm["d"] + 0.4, face - gm["length"], d0)
    sleeve -= box(gm["w"] - 3.0, gm["d"] - 3.0, face - gm["length"] - 3.0, d0)          # wires out of the bottom
    flange = box(24.0, 16.0, d0 - 2.0, d0, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN)).moved(
        bd.Location((-8.0, 0, 0))) - box(gm["w"] + 0.4, gm["d"] + 0.4, d0 - 3.0, d0 + 1.0)
    for dy in (-5.5, 5.5):
        flange -= zdisc(2.4, d0 - 3.0, d0 + 1.0).moved(bd.Location((12.5, dy, 0)))
    a.add("walk_motor_bracket", at((sleeve + flange).rotate(bd.Axis.Z, MOTOR_DIR), wm), material="PETG", group="drive",
          print_up=(0, 0, -1),
          note="holds the gearmotor; two M2 screws under the deck: undo them and the motor drops out with its pinion")
    a.allow("walk_motor_bracket", "walk_motor"); a.allow("walk_motor_bracket", "deck")
    cuts.append(at(zdisc(16.0, DECK[0] - 1, DECK[1] + 1), wm))
    # the program shaft: gear 72 above the deck, the program cam and the lock cam below; two MR85ZZ
    a.add("program_shaft", at(parts.rod(5.0, lv["g12p"][1] - lb["lock_cam"][0], z0=lb["lock_cam"][0]), P),
          material="steel", printed=False, group="drive", note="Ø5 ground rod")
    r72 = mesh_rotation(g["g12p"], g["g72"], G.PROG_DIR, 0.0)
    a.add("program_gear_72", at(gear(g["g72"], *lv["g12p"], 5.0, rot=r72) + zdisc(10.0, lv["g12p"][0], lv["g12p"][1],
                                                                                    bore=5.0 + parts.FITS.press), P),
          group="drive", note="pressed on the program shaft: one turn per show")
    for nm, z0 in (("program_bearing_top", lv["prog_brg_top"][0]), ("program_bearing_bottom", lb["prog_brg"][0])):
        a.add(nm, at(parts.bearing(b85, z0), P), material="bearing", printed=False, group="drive", note="MR85ZZ")
        a.allow(nm, "program_shaft"); a.allow(nm, "deck")
    pblk = zdisc(18.0, *lv["prog_boss"]) - zdisc(b85.od + parts.FITS.bearing_seat, lv["prog_brg_top"][0],
                                                   lv["prog_brg_top"][1] + 1)
    pblk -= zdisc(6.5, lv["prog_boss"][0] - 1, lv["prog_boss"][1] + 1)
    for dx in (-6.5, 6.5):
        pblk -= zdisc(2.4, lv["prog_boss"][0] - 1, lv["prog_boss"][1] + 1).moved(bd.Location((dx, 0, 0)))
    a.add("program_bearing_block", at(pblk, P), material="PETG", group="drive",
          note="the program shaft's upper bearing: screwed on the deck (2 x M2)")
    a.allow("program_bearing_block", "deck"); a.allow("program_bearing_block", "program_bearing_top")
    cuts += [at(zdisc(b85.od + parts.FITS.bearing_seat, lb["prog_brg"][0] - 1, lb["prog_brg"][1]), P),
             at(zdisc(6.5, DECK[0] - 1, DECK[1] + 1), P)]
    cg = G.crank()
    ang_u = math.degrees(math.atan2(cg["u"][1], cg["u"][0]))
    rot_c = -theta                                             # the program shaft turns CW seen from above
    gw = 2.5 + parts.FITS.running

    def groove_r(a_local):                                     # local angle -> radius of the groove's centre
        return G.groove_radius(a_local - ang_u, cg)

    z0c, z1c = lb["prog_cam"]
    cam = zdisc(47.0, z0c, z1c, bore=5.0 + parts.FITS.press)
    outer = profile_plate(lambda a_: groove_r(a_) + gw / 2, lb["groove"] + 0.01, 0.0)
    inner = profile_plate(lambda a_: groove_r(a_) - gw / 2, lb["groove"] + 0.02, 0.0)
    cam -= (outer - inner).moved(bd.Location((0, 0, z0c - 0.01)))
    a.add("program_cam", at(cam.rotate(bd.Axis.Z, rot_c), P), group="drive", print_up=(0, 0, -1),
          note="grooved underneath: the push rod's follower runs in it (pressure angle ≤ 36° [D])")
    ang_sw = ang_u + 180.0

    def lock_r(a_local):
        t = a_local - ang_sw                                    # the program angle at which a_local is at the roller
        dep, ramp, flat = NOTCH
        for nch in G.LOCK_NOTCHES:                              # the switch has closed by the stop angle
            d = ((t - nch + 180.0) % 360.0) - 180.0
            if -ramp <= d < 0:
                return LOCK_R - dep * (d + ramp) / ramp
            if 0 <= d <= flat:
                return LOCK_R - dep
            if flat < d <= flat + ramp:
                return LOCK_R - dep * (1 - (d - flat) / ramp)
        return LOCK_R

    lk = profile_plate(lock_r, lb["lock_cam"][1] - lb["lock_cam"][0], 5.0 + parts.FITS.press).moved(
        bd.Location((0, 0, lb["lock_cam"][0])))
    a.add("lock_cam", at(lk.rotate(bd.Axis.Z, rot_c), P), group="drive",
          note="two notches (end of phase A, end of the show): the microswitch stops the walk motor")
    for nm in ("program_gear_72", "program_cam", "lock_cam"):
        a.allow(nm, "program_shaft")
    a.allow("program_cam", "follower_pin")
    # the lock microswitch: its roller in the notch at rest
    sw_c = polar_xy(P, SWITCH["r"], ang_sw)
    zc = sum(lb["lock_cam"]) / 2
    body = box(SWITCH["l"], SWITCH["w"], zc - SWITCH["h"] / 2, zc + SWITCH["h"] / 2)
    lever = box(SWITCH["r"] - SWITCH["l"] / 2 - (LOCK_R - NOTCH[0] + 2.0), 1.0, zc - 1.5, zc + 1.5,
                align=(bd.Align.MAX, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((-SWITCH["l"] / 2, 0, 0)))
    roller = zdisc(4.0, zc - 1.0, zc + 1.0).moved(bd.Location((-(SWITCH["r"] - (LOCK_R - NOTCH[0] + 2.0)), 0, 0)))
    a.add("lock_switch", at((body + lever + roller).rotate(bd.Axis.Z, ang_sw), sw_c), material="black",
          printed=False, group="drive", note="subminiature roller-lever microswitch [E]")
    hang = box(8.0, SWITCH["w"] + 4.0, zc + SWITCH["h"] / 2, DECK[0], align=(bd.Align.MIN, bd.Align.CENTER,
                                                                             bd.Align.MIN)).moved(
        bd.Location((-2.0, 0, 0)))
    a.add("lock_switch_bracket", at(hang.rotate(bd.Axis.Z, ang_sw), sw_c), material="PETG", group="drive",
          note="hangs from the deck; the switch screws to it (2 x M2)")
    a.allow("lock_switch_bracket", "deck"); a.allow("lock_switch_bracket", "lock_switch"); a.allow("lock_switch", "lock_cam")
    # the bell-station Hall under the ring, on a post from the deck
    hp = L.polar(L.PHI_BELL, MAGNET_R)
    board_z = (-3.5 - HALL[2], -3.5)
    board = box(HALL[0], HALL[1], *board_z).rotate(bd.Axis.Z, L.PHI_BELL)
    a.add("bell_hall", at(board, hp), material="green", printed=False, group="drive",
          note="Hall switch: a magnet under each age passes over it; on at the bell = an age was caught")
    a.add("bell_hall_post", at(zdisc(6.0, DECK[1], board_z[0]), hp), material="PETG", group="drive")
    a.allow("bell_hall_post", "deck"); a.allow("bell_hall_post", "bell_hall")
    data = {"walk_xy": [round(v, 2) for v in pp], "program_xy": [round(v, 2) for v in P],
            "motor_xy": [round(v, 2) for v in wm], "levels": {k: [round(v, 2) for v in z] for k, z in lv.items()
                                                                  if isinstance(z, tuple)}}
    return data, adds, cuts


# ------------------------------------------------------------------------------------------------ state module
def add_state_module(a, minutes: float, hours: float, arbor_y: float, cam_x: float):
    """The state arbor and everything on it, its frame plates, the NEMA 17 on its D16 adapter (to the right)."""
    z = STATE_Z
    b85 = BEARINGS["MR85ZZ"]
    rot = 6.0 * minutes                                       # the arbor's angle (local, about +X)
    rot_h = 30.0 * hours
    x_l, x_r = -31.0, 79.5                                    # the arbor's ends
    xp = dict(plate_l=(-30.0, -26.0), p12=(-25.7, -23.2), lay_hub=(-23.2, -22.9), hour_wheel=(-22.9, -20.4),
              lay_stud=(-30.0, -19.4), tube=(-22.9, -8.5), witness=(-15.8, -12.8),
              snail_h=(S.HOUR.x_rack - 2.0, S.HOUR.x_rack + 2.0), release_h=(-6.2, -3.2),
              snail_q=(S.QUARTER.x_rack - 2.0, S.QUARTER.x_rack + 2.0), release_q=(20.3, 23.3),
              age_cam=(cam_x - AGE_CAM["t"] / 2, cam_x + AGE_CAM["t"] / 2),
              index=(45.5, 48.5), index_hall=(49.0, 52.0), block=(52.3, 56.3), coupling=(56.6, 95.5),
              plate_r=(96.0, 100.0))
    lay_y = arbor_y + 30.0
    a.add("state_arbor", on_x(parts.rod(5.0, x_r - x_l), x_l, arbor_y, z), material="steel", printed=False,
          group="state", note="Ø5 ground rod; 1 rev/h legal time")

    def ox(shape, xr):                                        # a local part (about +Z, z from 0) at x range xr
        return on_x(shape, xr[0], arbor_y, z)

    t_cam = xp["age_cam"][1] - xp["age_cam"][0]
    a.add("age_cam", ox(arbor_cam(age_cam_radius, 60.0, t_cam).rotate(bd.Axis.Z, rot), xp["age_cam"]), group="state",
          print_up=(1, 0, 0), note="sets the bell rod's height: 4 steps of 4 mm, a ramp back from the old man to the child")
    a.add("quarter_snail", ox(arbor_cam(quarter_snail_radius, 60.0, xp["snail_q"][1] - xp["snail_q"][0]).rotate(
        bd.Axis.Z, rot), xp["snail_q"]), group="state", print_up=(1, 0, 0),
          note="part 2b's quarter rack falls on it: 1 to 4 pairs")
    for nm, fn, xr in (("release_cam_hour", S.hour_release_radius, xp["release_h"]),
                       ("release_cam_quarter", S.quarter_release_radius, xp["release_q"])):
        a.add(nm, ox(arbor_cam(fn, 60.0, xr[1] - xr[0]).rotate(bd.Axis.Z, rot), xr), group="state", print_up=(1, 0, 0),
              note="trips its rack hook a minute before each show (part 2b): the time train decides when (rule 4)")
        a.allow(nm, "state_arbor")
    idx = zdisc(24.0, 0.0, 3.0, bore=5.0 + parts.FITS.press) - zdisc(MAGNET[0] + 0.2, 3.0 - MAGNET[1] - 0.2, 3.1).moved(
        bd.Location((0, 9.0, 0)))
    a.add("index_disc", ox(idx.rotate(bd.Axis.Z, rot), xp["index"]), group="state", print_up=(1, 0, 0),
          note="its magnet passes the index Hall at minute 0")
    mag = zdisc(MAGNET[0], 3.0 - MAGNET[1], 3.0).moved(bd.Location((0, 9.0, 0)))
    a.add("index_magnet", ox(mag.rotate(bd.Axis.Z, rot), xp["index"]), material="silver", printed=False,
          group="state")
    a.add("index_hall", on_x(box(HALL[1], HALL[0], 0.0, HALL[2]), xp["index_hall"][0], arbor_y, z + 9.0),
          material="green", printed=False, group="state", note="index Hall on the right block: the arbor at minute 0")
    # bearings: the left plate and the right block, MR85ZZ; a Starlock at the left end
    a.add("state_bearing_left", ox(parts.bearing(b85), (xp["plate_l"][0], 0)), material="bearing", printed=False,
          group="state", note="MR85ZZ")
    a.add("state_bearing_right", ox(parts.bearing(b85), (xp["block"][1] - b85.width, 0)), material="bearing",
          printed=False, group="state", note="MR85ZZ")
    a.add("state_starlock", ox(zdisc(STARLOCK[5.0][0], 0, STARLOCK[5.0][1], bore=5.0), (xp["plate_l"][0] - 0.7, 0)),
          material="steel", printed=False, group="state", note="Starlock for Ø5: the arbor's left end")
    # the 12:1 motion work (12/48 · 15/45), the lay compound on a fixed Ø4 stud
    s12, s48 = pair_shifts(12, 48)
    s15, s45 = pair_shifts(15, 45)
    g12, g48, g15, g45 = Gear(12, 1.0, shift=s12), Gear(48, 1.0, shift=s48), Gear(15, 1.0, shift=s15), Gear(
        45, 1.0, shift=s45)
    assert abs(centre_distance(g12, g48) - 30.0) < 1e-6 and abs(centre_distance(g15, g45) - 30.0) < 1e-6
    pw = xp["p12"][1] - xp["p12"][0]
    a.add("state_pinion_12", ox(gear(g12, 0.0, pw, 5.0, rot=rot), xp["p12"]), group="state", print_up=(1, 0, 0),
          note="pressed on the state arbor: the 12:1 motion work's input")
    r_lay = mesh_rotation(g12, g48, 0.0, rot)
    x0 = xp["p12"][0]
    lay = gear(g48, 0.0, xp["p12"][1] - x0, 4.0, "running", rot=r_lay)
    lay += gear(g15, xp["hour_wheel"][0] - x0, xp["hour_wheel"][1] - x0, 4.0, "running", rot=r_lay)
    lay += zdisc(12.0, xp["lay_hub"][0] - x0 - 0.01, xp["lay_hub"][1] - x0 + 0.01, bore=4.0 + parts.FITS.running)
    a.add("lay_compound", on_x(lay, x0, lay_y, z), group="state", print_up=(1, 0, 0),
          note="48 + 15 in one print, free on its stud")
    a.add("lay_stud", on_x(parts.rod(4.0, xp["lay_stud"][1] - xp["lay_stud"][0]), xp["lay_stud"][0], lay_y, z),
          material="steel", printed=False, group="state", note="Ø4 ground rod pressed in the left plate")
    a.add("lay_starlock", on_x(zdisc(STARLOCK[4.0][0], 0, STARLOCK[4.0][1], bore=4.0), xp["hour_wheel"][1] + 0.3, lay_y, z),
          material="steel", printed=False, group="state", note="Starlock for Ø4")
    r45 = mesh_rotation(g15, g45, 180.0, r_lay)
    hw = gear(g45, xp["hour_wheel"][0] - xp["tube"][0], xp["hour_wheel"][1] - xp["tube"][0], 5.0, "running", rot=r45)
    hw += zdisc(7.0, 0.0, xp["tube"][1] - xp["tube"][0], bore=5.0 + parts.FITS.running)
    a.add("hour_wheel_45", ox(hw, xp["tube"]), group="state", print_up=(1, 0, 0),
          note="the hour wheel on its tube, free on the state arbor (1 turn in 12 h)")
    hs = arbor_cam(hour_snail_radius, 12.0, xp["snail_h"][1] - xp["snail_h"][0], bore=7.0 + parts.FITS.press)
    hs -= zdisc(MAGNET[0] + 0.2, -0.1, MAGNET[1] + 0.2).moved(bd.Location((0, -WITNESS_R, 0)))
    a.add("hour_snail", ox(hs.rotate(bd.Axis.Z, rot_h), xp["snail_h"]), group="state", print_up=(-1, 0, 0),
          note="pressed on the hour wheel's tube; the hour rack falls on it: 1 to 12 strokes")
    a.add("witness_magnet", ox(zdisc(MAGNET[0], 0.0, MAGNET[1]).moved(bd.Location((0, -WITNESS_R, 0))).rotate(
        bd.Axis.Z, rot_h), xp["snail_h"]), material="silver", printed=False, group="state")
    a.add("witness_hall", on_x(box(HALL[1], HALL[0], 0.0, HALL[2]).rotate(bd.Axis.Z, 90), xp["witness"][0], arbor_y,
                               z - WITNESS_R), material="green", printed=False, group="state",
          note="witness Hall under the hour snail, on the strike frame: the snail's magnet passes it at 12:00")
    for x, y in (("age_cam", "state_arbor"), ("quarter_snail", "state_arbor"), ("index_disc", "state_arbor"),
                 ("index_magnet", "index_disc"), ("state_pinion_12", "state_arbor"), ("lay_compound", "lay_stud"),
                 ("lay_starlock", "lay_stud"), ("hour_wheel_45", "state_arbor"), ("hour_snail", "hour_wheel_45"),
                 ("witness_magnet", "hour_snail"), ("state_bearing_left", "state_arbor"),
                 ("state_bearing_right", "state_arbor"), ("state_starlock", "state_arbor"),
                 ("state_starlock", "state_bearing_left"), ("lay_stud", "state_plate_left"),
                 ("state_bearing_left", "state_plate_left"), ("state_bearing_right", "state_block"),
                 ("index_hall", "state_block"),
                 ("state_plate_left", "deck"), ("state_block", "deck"), ("state_motor_plate", "deck")):
        a.allow(x, y)
    # the frame: the left plate, the right block, the motor plate, each hanging from the deck
    def yz_plate(xr, y0, y1, z0, z1, flange=(-3.0, 3.0)):
        """A plate across X hanging from the deck, with a top flange (screwed under the deck) from xr[0] + flange[0]
        to xr[1] + flange[1]."""
        pl_ = bd.Box(xr[1] - xr[0], y1 - y0, z1 - z0, align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN)).moved(
            bd.Location((xr[0], y0, z0)))
        fx0, fx1 = xr[0] + flange[0], xr[1] + flange[1]
        pl_ += bd.Box(fx1 - fx0, y1 - y0, 3.0, align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MAX)).moved(
            bd.Location((fx0, y0, z1)))
        return pl_

    left = yz_plate(xp["plate_l"], arbor_y - 10.0, lay_y + 7.0, z - 9.0, DECK[0])
    left -= ox(zdisc(b85.od + parts.FITS.bearing_seat, -0.01, b85.width), (xp["plate_l"][0], 0))
    left -= ox(zdisc(6.5, -1, 6), (xp["plate_l"][0], 0))
    left -= on_x(zdisc(4.0 + parts.FITS.press, -1, 6), xp["plate_l"][0], lay_y, z)
    a.add("state_plate_left", left, material="PETG", group="state", print_up=(0, 0, -1),
          note="carries the arbor's left bearing and the lay stud")
    block = yz_plate(xp["block"], arbor_y - 10.0, arbor_y + 10.0, z - 9.0, DECK[0])
    block -= ox(zdisc(b85.od + parts.FITS.bearing_seat, xp["block"][1] - b85.width, xp["block"][1] + 0.01) , (0, 0))
    block -= ox(zdisc(6.5, xp["block"][0] - 1, xp["block"][1] + 1), (0, 0))
    a.add("state_block", block, material="PETG", group="state", print_up=(0, 0, -1),
          note="the arbor's right bearing and the index Hall")
    # the coupling: the arbor's right end in a press bore, the motor's D-shaft in a D socket (D16)
    xf = xp["plate_r"][1]                                     # the adapter's front face (global x)
    zf = -MM.ADAPTER["t"]                                     # the motor's face in the motor's local frame
    def motor_local(shape):                                   # motor frame: +Z toward -X, +Y up (global +Z)
        return shape.rotate(bd.Axis.Y, -90).rotate(bd.Axis.X, 0).moved(bd.Location((xf, arbor_y, z)))

    def mx(shape):                                            # motor-local shape -> global, with local y up
        return motor_local(shape.rotate(bd.Axis.Z, 90))

    c0, c1 = xf - xp["coupling"][1], xf - xp["coupling"][0]   # the coupling in motor-local z
    coup = zdisc(12.0, c0, c1)
    tip = zf + MM.SHAFT["length"]
    coup -= zdisc(5.0 + parts.FITS.running, c0 - 1, tip + 0.3)
    coup += MM.d_key(zf, c0, tip + 0.3, fit=parts.FITS.running)        # a slip fit: the motor slides out
    coup -= zdisc(5.0 + parts.FITS.press, xf - x_r, c1 + 1)
    a.add("state_coupling", mx(coup), group="state", print_up=(1, 0, 0),
          note="pressed on the arbor; the NEMA 17's D-shaft slides into its D socket (D16: plugs in from the right)")
    a.add("state_motor_shaft", mx(MM.shaft(zf)), material="steel", printed=False, group="state")
    a.add("state_motor", mx(MM.motor_body(zf)), material="black", printed=False, group="state",
          note="E2's state stepper, NEMA 17: withdraw to the right after undoing two M3")
    a.add("state_motor_adapter", mx(MM.adapter(0.0, boss_d=24.0, boss_h=3.0)), group="state", print_up=(-1, 0, 0),
          note="D16 adapter: screwed to the motor at the bench")
    mplate = yz_plate(xp["plate_r"], arbor_y - MM.NEMA17["body"] / 2, arbor_y + MM.NEMA17["body"] / 2,
                      z - MM.ADAPTER["h"] / 2 + 2.5, DECK[0], flange=(-7.0, 0.0))
    mplate -= on_x(zdisc(24.0 + parts.FITS.running, -1, 6), xp["plate_r"][0], arbor_y, z)
    for dz in (-MM.ADAPTER["ears"], MM.ADAPTER["ears"]):
        mplate -= on_x(zdisc(MM.INSERT_HOLE, -0.01, xp["plate_r"][1] - xp["plate_r"][0] + 0.01), xp["plate_r"][0],
                       arbor_y, z + dz)
    a.add("state_motor_plate", mplate, material="PETG", group="state", print_up=(0, 0, -1),
          note="the motor's plate: its adapter's boss locates in it; two M3 heat-set inserts")
    for x, y in (("state_coupling", "state_arbor"), ("state_coupling", "state_motor_shaft"),
                 ("state_motor_shaft", "state_motor"), ("state_motor", "state_motor_adapter"),
                 ("state_motor_adapter", "state_motor_plate"), ("state_motor_shaft", "state_motor_adapter")):
        a.allow(x, y)
    data = {"arbor_y": round(arbor_y, 2), "axis_z": z, "age_cam_radius_now": age_cam_radius(minutes),
            "quarter_snail_now": quarter_snail_radius(minutes), "hour_snail_now": hour_snail_radius(hours),
            "motion_work": "12/48 x 15/45 = 1/12", "x": {k: [round(v, 2) for v in r] for k, r in xp.items()}}
    return data, [], []
