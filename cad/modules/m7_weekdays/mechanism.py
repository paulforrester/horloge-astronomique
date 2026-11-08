"""M7, the weekday carousel: detail design (docs/m7-design.md).

Settled in the concept gate (PR #20, Paul, 7-8 Nov 2026):
- drive A, the lay shaft: M2's arbor W (1 rev per 7 days, `M2.weekday` 12/84, exact) -> single-dog
  coupling -> a 1:1 straight bevel pair -> a vertical Ø5 lay shaft -> a 1:1 spur pair -> the
  turntable. M7 adds no ratio: the carousel turns once in 7 mean days exactly;
- chariots fixed to the turntable, on a decorative rail;
- the faithful size: R ≈ 100 mm, chariots ≈ 62 mm long and ≈ 60 mm tall, their floor ≈ 390 mm above
  the floor (Paul's photograph IMG_0766, m7-design §12) [E];
- each chariot centred at Bordeaux mean noon (D-next (M5-M7)); the setting clutch is an 84-tooth
  spline under the turntable (one tooth = 2 h of carousel).

Coordinates: M2's frame. Origin at the main dial's centre on its face; +X right, +Y up, +Z towards
the viewer. The main dial's centre is ≈ 213 mm above the floor [E: envelope §2].
Parts on the deck are built in a "deck frame" (x = X, y = -Z, z = Y) and turned up with ``up()``.
Run:  python -m cad.modules.m7_weekdays.mechanism [out_dir]
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import build123d as bd

from cad.lib import parts
from cad.lib.assembly import BED_DUAL, BED_SINGLE, Assembly, write_dae
from cad.lib.bevel import Bevel, bevel_gear
from cad.lib.gears import Gear, centre_distance, mesh_rotation, spur_gear
from cad.lib.hardware import BEARINGS, SCREWS
from cad.modules.m2_main_dial import mechanism as M2

# --- parameters ------------------------------------------------------------------------------------
DIAL_CENTRE_ABOVE_FLOOR = 213.0           # [E] envelope §2
W_XY = M2.W                               # (-75.5, 57.9): M2's weekday arbor
W_END = M2.BP[0] - 25.0                   # z of W's rear end (-139)
BACKLASH = 0.15
E = 0.3                                   # endshake [E]

BEVEL = Bevel(20, 20, module=1.0, face_width=4.5)
BEVEL_PHASE = 9.0                         # B's spin that meshes with A (half a pitch; test_m7 checks it)
SPUR_Z, SPUR_M, SPUR_FACE = 85, 1.0, 4.0  # 1:1 under the turntable
SPLINE = Gear(84, 0.7, backlash=0.2)      # setting clutch: 84 positions, 2 h of carousel each

R = 100.0                                 # carousel radius [E ±15 %, m7-design §12]
N_CHARIOTS = 7
CHARIOT_L, CHARIOT_W, CHARIOT_H = 62.0, 22.0, 60.0   # [E] m7-design §12
WHEEL_D, WHEEL_T = 27.0, 3.0
FLOOR_ABS = 390.0                         # chariots' floor above the floor [E]
Y_FLOOR = FLOOR_ABS - DIAL_CENTRE_ABOVE_FLOOR       # 177

# levels (Y), bottom up
SPIDER = (Y_FLOOR - 4.0, Y_FLOOR)                    # 173 ... 177
SPUR = (SPIDER[0] - 2.0 - SPUR_FACE, SPIDER[0] - 2.0)  # 167 ... 171
DECK = (SPUR[0] - 2.0 - 4.0, SPUR[0] - 2.0)          # 161 ... 165
RAIL_R, RAIL_SECTION = R + 12.0, 3.0

# stub, bevel and lay shaft
Z_APEX = -166.0                                     # the bevels' common apex, on W's axis
A_BACK = Z_APEX + BEVEL.apex_z                      # A's large end (z), -156
SLEEVE = (W_END - 1.0 - 7.0, W_END - 1.0)           # dog sleeve on the stub, -147 ... -140
FRONT_WALL = (A_BACK + 3.5 + E, SLEEVE[0] - E)      # bracket wall holding the stub's front bearing
REAR_WALL = (Z_APEX - BEVEL.pitch_radius - 13.0, Z_APEX - BEVEL.pitch_radius - 9.0)   # behind B
STUB = (REAR_WALL[0], SLEEVE[1])
B_BACK_Y = W_XY[1] + BEVEL.apex_z                   # B's large end (Y), 67.9
BRIDGE = (B_BACK_Y + 6.0 + E, B_BACK_Y + 10.0 + E)  # bracket bridge holding the lay shaft's lower bearing
LAY = (B_BACK_Y - 3.6, SPUR[1])                     # lay shaft, Y
SPINE_Z = (REAR_WALL[0] - 4.0, REAR_WALL[0])

# the turntable's axis: on the centreline, 85 mm (the 1:1 spur pair) from the lay shaft
_CD = centre_distance(Gear(SPUR_Z, SPUR_M), Gear(SPUR_Z, SPUR_M))
Z_AXIS = Z_APEX + math.sqrt(_CD ** 2 - W_XY[0] ** 2)  # ≈ -127
POST_D = 30.0                                        # fixed post, inside a 61806 (30 x 42 x 7)
HUB_OD = 48.0

# the moment the model shows: Paul's photograph, Friday 30 Oct 2026 10:08 CET (Venus in the centre);
# Bordeaux mean time = UT - 2.28 min (D-next (M5-M7)), so 09:05.7 mean time, 2.9 h before mean noon
DAYS = ["Apollo (Sunday)", "Diana (Monday)", "Mars (Tuesday)", "Mercury (Wednesday)",
        "Jupiter (Thursday)", "Venus (Friday)", "Saturn (Saturday)"]
PHOTO_DAY, PHOTO_HOURS_TO_NOON = 5, (12.0 - (9.0 + 5.7 / 60))


# --- helpers -------------------------------------------------------------------------------------------
def up(shape):
    """Deck frame (x, y = -Z, z = Y) -> M2 frame."""
    return shape.rotate(bd.Axis.X, -90)


def at_deck(shape, X, Z, Y0=0.0):
    """Place a shape built along +z (deck frame) with its axis at world (X, Z), from height Y0."""
    return up(shape.moved(bd.Location((X, -Z, Y0))))


def chariot_angle(k: int, day: int, hours_to_noon: float = 0.0) -> float:
    """Plan angle (deg, counter-clockwise from above, 0 = towards the viewer) of chariot k on weekday
    ``day`` (0 = Sunday), ``hours_to_noon`` hours before that day's mean noon. The carousel turns
    +360/7 per day, so the day's chariot is still short of the front before noon, and tomorrow's
    chariot waits one place behind it (on the viewer's left)."""
    return -(k - day) * 360.0 / N_CHARIOTS - hours_to_noon * 360.0 / (N_CHARIOTS * 24)


def plan_xyz(angle_deg: float, r: float):
    """World (X, Z) of a point at radius r and plan angle from the axis (0 = front, CCW from above)."""
    a = math.radians(angle_deg)
    return r * math.sin(a), Z_AXIS + r * math.cos(a)


def chariot(k: int):
    """Placeholder chariot and deity (parametric; likenesses are a later step). Built at the front."""
    body = bd.Box(CHARIOT_L - 16, CHARIOT_W - 8, 14, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    body = body.moved(bd.Location((0, 0, 4)))
    base = bd.Box(CHARIOT_L - 10, CHARIOT_W - 10, 4, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    wheel = parts.disc(WHEEL_D, WHEEL_T).rotate(bd.Axis.X, 90)
    w_in = wheel.moved(bd.Location((-6, CHARIOT_W / 2 - WHEEL_T / 2 - 0.0, WHEEL_D / 2 + 0.5)))
    w_out = wheel.moved(bd.Location((-6, -CHARIOT_W / 2 + WHEEL_T / 2 + 0.0, WHEEL_D / 2 + 0.5)))
    axle = parts.rod(3.0, CHARIOT_W).rotate(bd.Axis.X, 90).moved(bd.Location((-6, CHARIOT_W / 2, WHEEL_D / 2 + 0.5)))
    figure = parts.rod(12.0, CHARIOT_H - 18 - 9).moved(bd.Location((-4, 0, 18)))
    head = bd.Sphere(4.5).moved(bd.Location((-4, 0, CHARIOT_H - 4.5)))
    beast = bd.Box(16, 8, 14, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(
        bd.Location((CHARIOT_L / 2 - 8, 0, 4)))
    shape = base + body + w_in + w_out + axle + figure + head + beast
    # deck frame: x along the front (tangent), y = -Z (the outer wheel nearest the viewer), z up
    return shape


# --- the build -----------------------------------------------------------------------------------------
def build(hours_to_noon: float = PHOTO_HOURS_TO_NOON, day: int = PHOTO_DAY):
    a = Assembly("m7_weekdays")
    rep = {"notes": [], "meshes": []}
    wx, wy = W_XY
    run = parts.FITS.running
    brg = BEARINGS["MR85ZZ"]

    # ---- neighbours (for interference only): M2's W end and back plate, the calendar ring ----
    a.add("M2_W_end", parts.rod(5.0, M2.BP[0] - W_END + 5.0).moved(bd.Location((wx, wy, W_END))),
          material="ghost", printed=False, group="neighbours", note="M2's arbor W (not part of M7)")
    a.add("M2_back_plate_zone", bd.Box(281, 232, 4, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(
        bd.Location((0, 0, M2.BP[0]))), material="ghost", printed=False, group="neighbours",
        note="M2's back plate outline (281 x 232) [D: docs/m2-design.md §3 item 4]")
    a.add("M2_calendar_ring_zone", parts.disc(341.0, 11.0, bore=275.0, z0=-11.0), material="ghost", printed=False,
          group="neighbours", note="calendar ring and carrier, z -11 ... 0 [D: docs/m2-design.md §2]")
    a.allow("M2_W_end", "M2_back_plate_zone")

    # ---- the coupling: a dog hub on W (supplied with M7, pressed on W's end) and the sliding sleeve ----
    dog_hub = parts.hub(5.0, 12.0, 8.0, fit="press", z0=W_END) + bd.Box(3, 5, 3, align=(
        bd.Align.CENTER, bd.Align.MIN, bd.Align.MAX)).moved(bd.Location((0, 3.5, W_END)))
    a.add("dog_hub_on_W", dog_hub.moved(bd.Location((wx, wy, 0))), group="drive",
          note="pressed on M2's arbor W; its single dog keys the carousel's phase (P4)")
    a.allow("dog_hub_on_W", "M2_W_end")
    sleeve = parts.hub(5.0, 12.0, SLEEVE[1] - SLEEVE[0], fit="sliding", z0=SLEEVE[0])
    sleeve -= bd.Box(3.6, 6, 3.4, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MAX)).moved(
        bd.Location((0, 3.0, SLEEVE[1] + 0.01)))                                   # the dog's slot
    a.add("dog_sleeve", sleeve.moved(bd.Location((wx, wy, 0))), group="drive",
          note="slides on the stub's flat; pull it back to free M7, push it on to key it (one position)")

    # ---- the stub and bevel A ----
    a.add("stub_5", parts.rod(5.0, STUB[1] - STUB[0]).moved(bd.Location((wx, wy, STUB[0]))), material="steel",
          printed=False, group="drive")
    a.allow("stub_5", "dog_sleeve")
    ga = bevel_gear(BEVEL, bore=5.0, hub_len=3.5, hub_od=11.0, fit_allowance=parts.FITS.press)
    ga = ga.rotate(bd.Axis.X, 180).moved(bd.Location((wx, wy, A_BACK)))
    a.add("bevel_A_20", ga, group="drive", note="on the stub; 1:1 to bevel B")
    a.allow("bevel_A_20", "stub_5")

    # ---- bevel B and the lay shaft (vertical) ----
    gb = bevel_gear(BEVEL.mate(), bore=5.0, hub_len=6.0, hub_od=11.0, fit_allowance=parts.FITS.press)
    gb = gb.rotate(bd.Axis.Z, BEVEL_PHASE).rotate(bd.Axis.X, 90).moved(bd.Location((wx, B_BACK_Y, Z_APEX)))
    a.add("bevel_B_20", gb, print_up=(0, 1, 0), group="drive", note="on the lay shaft")
    lay = at_deck(parts.rod(5.0, LAY[1] - LAY[0] + 2.0), wx, Z_APEX, LAY[0])
    a.add("lay_shaft_5", lay, material="steel", printed=False, group="drive")
    a.allow("bevel_B_20", "lay_shaft_5")

    # ---- bearings ----
    def brg_on_stub(z0, name):
        a.add(name, parts.bearing(brg, z0=z0).moved(bd.Location((wx, wy, 0))), material="bearing", printed=False,
              group="drive")
        a.allow(name, "stub_5")
    brg_on_stub(FRONT_WALL[0] + (FRONT_WALL[1] - FRONT_WALL[0] - brg.width) / 2, "brg_stub_front")
    brg_on_stub(REAR_WALL[0] + (REAR_WALL[1] - REAR_WALL[0] - brg.width) / 2, "brg_stub_rear")
    for nm, y0 in (("brg_lay_lower", BRIDGE[0] + 0.75), ("brg_lay_upper", DECK[0] + 0.75)):
        a.add(nm, at_deck(parts.bearing(brg), wx, Z_APEX, y0), material="bearing", printed=False, group="drive")
        a.allow(nm, "lay_shaft_5")

    # ---- the lower bracket: front and rear walls, the bridge, the spine up to the deck ----
    def wall(z0, z1):
        w = bd.Box(26, 24, z1 - z0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(
            bd.Location((wx, wy, z0)))
        return w - parts.bearing_seat_cut(brg, depth=z1 - z0 + 0.02, z0=z0 - 0.01).moved(bd.Location((wx, wy, 0)))
    bracket = wall(*FRONT_WALL) + wall(*REAR_WALL)
    bridge = bd.Box(26, BRIDGE[1] - BRIDGE[0], FRONT_WALL[1] - REAR_WALL[0],
                    align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN)).moved(bd.Location((wx, BRIDGE[0], REAR_WALL[0])))
    bridge -= at_deck(parts.bearing_seat_cut(brg, depth=BRIDGE[1] - BRIDGE[0] + 0.02), wx, Z_APEX, BRIDGE[0] - 0.01)
    side = lambda x0: bd.Box(4, BRIDGE[1] - (wy - 12), FRONT_WALL[1] - REAR_WALL[0],
                             align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN)).moved(bd.Location((x0, wy - 12, REAR_WALL[0])))
    bracket = bracket + bridge + side(wx - 17) + side(wx + 13)
    spine = bd.Box(40, DECK[0] - (wy - 12), SPINE_Z[1] - SPINE_Z[0], align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN)).moved(
        bd.Location((wx, wy - 12, SPINE_Z[0])))
    tabs = bd.Box(70, 14, 4, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN)).moved(bd.Location((wx, wy - 12, SPINE_Z[0])))
    for dx in (-28, 28):
        tabs -= parts.rod(SCREWS["M5"].clearance, 10, z0=SPINE_Z[0] - 3).moved(bd.Location((wx + dx, wy - 5, 0)))
    a.add("bracket", bracket + spine + tabs, material="PETG", group="frame",
          note="stub bearings, lay shaft's lower bearing; the spine carries the deck; tabs: 2 x M5 to the works' frame (D12 R5)")
    for nm in ("brg_stub_front", "brg_stub_rear", "brg_lay_lower"):
        a.allow("bracket", nm)

    # ---- the deck ----
    deck_outline = [(-125, 15), (125, 15), (125, 250), (-125, 250)]     # deck frame (x, y = -Z)
    deck = parts.plate(deck_outline, DECK[1] - DECK[0], z0=DECK[0])
    deck -= parts.bearing_seat_cut(brg, depth=DECK[1] - DECK[0] + 0.02, z0=DECK[0] - 0.01).moved(
        bd.Location((wx, -Z_APEX, 0)))
    for x, yv in ((0, -Z_AXIS + 70), (-100, 35), (100, 35), (0, 228)):
        deck -= parts.rod(18, 10, z0=DECK[0] - 1).moved(bd.Location((x, yv, 0)))         # lightening holes
    post = parts.disc(POST_D, SPIDER[1] + 2.0 - DECK[1], z0=DECK[1]).moved(bd.Location((0, -Z_AXIS, 0)))
    rail_post_shapes = []
    for ang in (60, 180, 300):                                      # behind the visible arc
        x, z = plan_xyz(ang, RAIL_R)
        rail_post_shapes.append(parts.disc(6, SPIDER[1] - RAIL_SECTION - 0.5 - DECK[1], z0=DECK[1]).moved(
            bd.Location((x, -z, 0))))
    deck_all = deck + post
    for p in rail_post_shapes:
        deck_all = deck_all + p
    a.add("deck", up(deck_all), material="PETG", print_up=(0, 1, 0), group="deck",
          note="carries the turntable's post, the lay shaft's upper bearing, the rail and the Hall")
    a.allow("deck", "brg_lay_upper")
    a.allow("deck", "lay_shaft_5")
    a.allow("deck", "bracket")                                      # the spine is glued/screwed under the deck
    a.allow("bracket", "lay_shaft_5")
    a.allow("bracket", "stub_5")

    # ---- the spur pair and the turntable hub ----
    g_lay = Gear(SPUR_Z, SPUR_M, backlash=BACKLASH)
    g_tt = Gear(SPUR_Z, SPUR_M, backlash=BACKLASH)
    # deck-frame plan positions: lay shaft (wx, -Z_APEX), axis (0, -Z_AXIS)
    theta = math.degrees(math.atan2(-Z_AXIS - (-Z_APEX), 0 - wx))
    rot_tt = mesh_rotation(g_lay, g_tt, theta)
    lay_gear = parts.gear_on_hub(g_lay, SPUR_FACE, 5.0, hub_od=11, hub_len=0.0)
    lay_gear -= parts.rod(5.0 + parts.FITS.press, 20, z0=-5)
    a.add("lay_gear_85", at_deck(lay_gear, wx, Z_APEX, SPUR[0]), print_up=(0, 1, 0), group="drive")
    a.allow("lay_gear_85", "lay_shaft_5")
    hub_h = SPIDER[1] + 2.0 - SPUR[0]
    tt = spur_gear(g_tt, SPUR_FACE).rotate(bd.Axis.Z, rot_tt) + parts.disc(HUB_OD, hub_h - SPUR_FACE, z0=SPUR_FACE)
    # a seat as wide as the spline under it: the turntable rests on it, and the spline prints without overhang
    tt += parts.disc(2 * SPLINE.tip_radius, SPIDER[0] - SPUR[0] - SPUR_FACE, z0=SPUR_FACE)
    tt += spur_gear(SPLINE, SPIDER[1] - SPIDER[0]).moved(bd.Location((0, 0, SPIDER[0] - SPUR[0])))
    tt -= parts.disc(POST_D + 2.0, hub_h + 2, z0=-1)                                      # clears the post
    tt -= parts.disc(BEARINGS["61806"].od + parts.FITS.bearing_seat, 7.0, z0=hub_h - 7.0 - 1.0)
    a.add("turntable_hub", at_deck(tt, 0, Z_AXIS, SPUR[0]), print_up=(0, 1, 0), group="carousel",
          note="85-tooth wheel, the 61806 seat and the 84-tooth setting spline, one print")
    brg_tt = parts.bearing("61806", z0=SPUR[0] + hub_h - 8.0)
    a.add("brg_turntable_61806", at_deck(brg_tt, 0, Z_AXIS, 0), material="bearing", printed=False, group="carousel")
    a.allow("brg_turntable_61806", "deck")
    a.allow("brg_turntable_61806", "turntable_hub")
    rep["meshes"].append({"pair": "lay 85 / turntable 85", "centre_distance": round(_CD, 3), "ratio": "1"})
    rep["meshes"].append({"pair": "bevel A 20 / B 20", "shaft_angle": BEVEL.shaft_angle,
                          "cone_distance": round(BEVEL.cone_distance, 3), "ratio": "1"})

    # ---- the turntable (spider) on the spline ----
    spin = chariot_angle(0, day, hours_to_noon)     # the turntable's turn: Apollo's chariot's plan angle
    rim_in, rim_out = R - 15.0, R + 5.0
    spider = parts.disc(2 * rim_out, SPIDER[1] - SPIDER[0]) - parts.disc(2 * rim_in, 10, z0=-1)
    hub_ring = parts.disc(SPLINE.tip_radius * 2 + 12, SPIDER[1] - SPIDER[0])
    spider = spider + hub_ring
    for k in range(N_CHARIOTS):
        ang = math.radians(90 + k * 360 / N_CHARIOTS)
        spoke = bd.Box(rim_in, 8, SPIDER[1] - SPIDER[0], align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN))
        spider = spider + spoke.rotate(bd.Axis.Z, math.degrees(ang))
    spider -= bd.extrude(_spline_hole(), amount=SPIDER[1] - SPIDER[0] + 2).moved(bd.Location((0, 0, -1)))
    spider_world = at_deck(spider.rotate(bd.Axis.Z, spin), 0, Z_AXIS, SPIDER[0])
    a.add("turntable", spider_world, print_up=(0, 1, 0), group="carousel",
          note="lift it off the spline, turn it, drop it back: one spline tooth = 2 h of carousel (setting)")
    a.allow("turntable", "turntable_hub")

    # ---- chariots ----
    for k in range(N_CHARIOTS):
        ang = chariot_angle(k, day, hours_to_noon)
        x, z = plan_xyz(ang, R)
        # built facing +x (its direction of travel at the front), turned tangent to the circle
        c = chariot(k).rotate(bd.Axis.Z, ang)
        a.add(f"chariot_{k}", at_deck(c, x, z, SPIDER[1]), print_up=(0, 1, 0), group="figures",
              note=DAYS[k] + " — placeholder group, likeness to come")
        a.allow(f"chariot_{k}", "turntable")

    # ---- the rail (decorative) ----
    rail = parts.disc(2 * RAIL_R + RAIL_SECTION, RAIL_SECTION) - parts.disc(2 * RAIL_R - RAIL_SECTION, 10, z0=-1)
    a.add("rail", at_deck(rail, 0, Z_AXIS, SPIDER[1] - RAIL_SECTION - 0.5), print_up=(0, 1, 0), group="frame",
          note="decorative: the outer wheels stand 0.5 mm above it")
    a.allow("rail", "deck")

    # ---- the witness: a magnet under Apollo's chariot, a Hall at the front ----
    hx, hz = plan_xyz(0.0, R - 5.0)
    a.add("hall_sunday", at_deck(bd.Box(8, 6, 3, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)), hx, hz,
                                 SPIDER[0] - 1.0 - 3.0), material="green", printed=False, group="frame",
          note="DRV5032 on a small board, on a printed post from the deck")
    a.add("hall_post", at_deck(bd.Box(10, 8, SPIDER[0] - 4.0 - DECK[1], align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)),
                               hx, hz, DECK[1]), print_up=(0, 1, 0), group="frame")
    a.allow("hall_post", "deck")
    a.allow("hall_post", "hall_sunday")
    mx, mz = plan_xyz(spin, R - 5.0)
    a.add("magnet_sunday", at_deck(parts.disc(5.0, 2.0), mx, mz, SPIDER[0]), material="steel", printed=False,
          group="carousel", inside="turntable", note="5 x 2 mm, pressed into the turntable under Apollo")

    rep["sense"] = senses()
    rep["ratio"] = {"W_to_carousel": "20/20 x 85/85 = 1 (exact)", "M2.weekday": "12/84 = 1/7 (exact)",
                    "carousel_period_days": 7, "error": 0}
    rep["positions"] = {"W": W_XY, "apex_z": Z_APEX, "lay_shaft": (wx, Z_APEX), "axis_z": round(Z_AXIS, 2),
                        "deck_y": DECK, "floor_y": Y_FLOOR}
    rep["shown"] = {"day": DAYS[day], "hours_to_mean_noon": round(hours_to_noon, 2), "plan_angle_deg": round(spin, 2)}
    return a, rep


def _spline_hole():
    """Internal spline of the turntable: the spline's gear face, opened by the backlash."""
    from cad.lib.gears import gear_face
    return gear_face(SPLINE.with_(backlash=-0.25, shift=0.15))


def senses() -> dict:
    """Rotation senses, derived from the geometry (+1 = counter-clockwise looking down the axis's + end).

    - M2: the Sun tube turns clockwise from the front (-1). The Sun tube = -S sleeve (48/48), the S sleeve
      = -S (differential, carrier still), so S = Sun tube = -1. W meshes with S (12/84): W = +1, i.e.
      counter-clockwise from the front, about +Z. (M2's own report says W = -I, which is the same sign
      only if W were driven from I; its model meshes W from S. Flagged in docs/m7-design.md §13.)
    - Bevels: A spins about +Z with W; its body is on the +Z side of the common apex, B's on the +Y side.
      At the pitch point P ∝ (0, 1, 1): ω_A × P = (-ω_A, 0, 0) and ω_B × P = (ω_B, 0, 0), so ω_B = -ω_A.
    - The spur pair reverses once more.
    """
    sun = -1
    S = sun
    W = -S
    lay = -W
    carousel = -lay
    return {"sun_tube_from_front": sun, "W_about_+Z": W, "lay_shaft_about_+Y": lay, "carousel_about_+Y": carousel,
            "carousel": "counter-clockwise seen from above" if carousel > 0 else "clockwise seen from above"}


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
    a.render(out / "m7_front.png", elev=8, azim=-90, up="y", title="M7 weekday carousel, front (M2 ghosts hidden)",
             hide=("neighbours",), tolerance=0.2)
    a.render(out / "m7_three_quarter.png", elev=28, azim=-125, up="y", title="M7, three-quarter",
             hide=("neighbours",), tolerance=0.2)
    a.render(out / "m7_drive.png", elev=18, azim=-150, up="y", title="M7, the drive (turntable and figures hidden)",
             hide=("neighbours", "figures", "carousel", "deck"), tolerance=0.1)


def main(out_dir="export/m7_weekdays"):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    a, data = build()
    res = check(a, data)
    (out / "m7_weekdays.json").write_text(json.dumps(res, indent=2, default=str))
    print(json.dumps({k: res[k] for k in ("interference", "bed_fit_single", "envelope", "parts", "printed", "bought")},
                     indent=2))
    renders(a, out)
    write_dae(a, out / "m7_weekdays.dae")
    return a, res


if __name__ == "__main__":
    main(*sys.argv[1:])
