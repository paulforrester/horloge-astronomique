"""M2 calendar ring (inventory I8) and its New Year station: the 3-D design.

The logic is ``calendar_logic.py`` (checked day by day over four centuries). This module gives it
parts, at 1:8 [S: ELS i4: Ø 2.73 m outer, 21 cm wide, 368 divisions → Ø 341, 26 mm wide]:

- **Ring**, 4 printed segments joined at day boundaries: the visible face (z -3 … 0), a rear skirt
  riding on 6 rollers (688ZZ), and a thin rear lip with 368 ratchet teeth (one per division).
- **Feature band** behind the face (r 148 … 162, z -8.3 … -5.8): fixed bumps S at d = 0, 1; the
  sector's lug and tab (through slots); the counter pin at d = 0; the 1 March witness flag.
- **Movable sector** (1 Jan … 28 Feb), sliding one division in a recess of the face.
- **Carrier** (4 printed segments) holding the rollers, with openings where readers reach the band:
  the **stop lever** and the **witness opto** at the pointer (3 o'clock), and the **station** at
  6 o'clock: E6 gearmotor + crank + pawl, jumper, 10-point counter star, wheel C (100 T) with its
  24 leap bumps, the satellite, the follower and the sector setter switch.

The ring turns clockwise seen from the front; ring division d sits at world angle
(d - pointer) x 360/368 degrees, so the pointer is at 0° and the station sees pointer - 92 at -90°.
"""
from __future__ import annotations

import math

import build123d as bd
import numpy as np

from cad.lib import parts
from cad.lib.assembly import Assembly
from cad.lib.gears import Gear, centre_distance, mesh_rotation, pair_shifts, spur_gear
from cad.lib.hardware import BEARINGS
from cad.modules.m2_main_dial import calendar_logic as L
from cad.modules.m2_main_dial import feasibility as F

R_OUT, R_IN = F.RING_OD / 2, F.RING_OD / 2 - F.RING_W        # 170.5, 144.5
DIV = 360.0 / L.N
FACE_Z = (-3.0, 0.0)
SKIRT = (144.5, 147.5, -8.5)                                 # r_in, r_out, z_back
LIP = (163.0, 170.5, -5.5)                                   # r_in, r_tip, z_back (teeth on the outer edge)
BAND = (148.0, 162.0, -8.3, -5.8)                            # feature band behind the face
# radial tracks in the band (each is read by one reader only) and the two depth layers
TRACK_WITNESS = (148.0, 149.5)                                # 1 March flag, opto at the pointer
TRACK_S = (150.0, 154.0)                                      # rim + bumps + sector lug, stop lever
R_PIN = 156.25                                                # counter pin, star at the station
TRACK_TAB = (159.0, 162.0)                                    # sector tab, setter at the station
LAYER_A = (-5.8, -3.0)                                        # shallow: tab
LAYER_B = (-8.3, -6.0)                                        # deep: star, lever tip, flag
RIM_Z = -6.5                                                  # S-track rim face; bumps reach -8.3
CARRIER = (133.0, 178.0, -10.9, -8.8)                        # r_in, r_out, z0, z1 (in front of the M2 front plate)
ROLLER_R = SKIRT[0] - BEARINGS["688ZZ"].od / 2               # 136.5
STATION_ANGLE = L.STATION_OFFSET * DIV                       # -90°
M_C = 0.8                                                    # wheel C module (hidden, light load)
STATION_R_MAX = 195.0          # nothing below 195 mm under the dial centre: ~18 mm above the floor [E]
C_CENTRE_Y = -150.0            # wheel C raised beside the station, behind the M2 front plate


def ring_angle(d: int, pointer: int) -> float:
    return (d - pointer) * DIV


def _wedge(a0: float, a1: float, r0: float, r1: float, z0: float, z1: float, n: int = 24):
    """Annular sector between angles a0..a1 (degrees)."""
    th = np.radians(np.linspace(a0, a1, n))
    pts = [(r1 * math.cos(t), r1 * math.sin(t)) for t in th] + [(r0 * math.cos(t), r0 * math.sin(t)) for t in th[::-1]]
    face = bd.Face(bd.Wire.make_polygon([bd.Vector(x, y, 0) for x, y in pts], close=True))
    return bd.extrude(face, amount=z1 - z0, dir=(0, 0, 1)).moved(bd.Location((0, 0, z0)))


def _ratchet_lip(pointer: int):
    """Lip with 368 sawtooth teeth on its outer edge, pushed clockwise."""
    r_root, r_tip = LIP[1] - 2.0, LIP[1]
    pts = []
    for k in range(L.N):
        a0 = math.radians(ring_angle(k, pointer) - DIV / 2)
        a1 = math.radians(ring_angle(k, pointer) + DIV / 2 - 0.15 * DIV)
        pts += [(r_root * math.cos(a0), r_root * math.sin(a0)), (r_tip * math.cos(a1), r_tip * math.sin(a1))]
    outer = bd.Face(bd.Wire.make_polygon([bd.Vector(x, y, 0) for x, y in pts], close=True))
    inner = bd.Face(bd.Wire.make_circle(LIP[0]))
    return bd.extrude(outer - inner, amount=FACE_Z[0] - LIP[2], dir=(0, 0, 1)).moved(bd.Location((0, 0, LIP[2])))


def ring_and_sector(pointer: int, sector_leap: bool):
    """(ring, sector, ring features dict). Positions for the given pointer division."""
    sector_start = L.SECTOR_COMMON_START - (1 if sector_leap else 0)
    a_sec0 = ring_angle(L.SECTOR_COMMON_START - 1, pointer) - DIV / 2         # recess spans 60 divisions
    a_sec1 = ring_angle(L.SECTOR_COMMON_START + L.SECTOR_DAYS - 1, pointer) + DIV / 2
    face = _wedge(0, 360, R_IN, R_OUT, FACE_Z[0], FACE_Z[1], n=368)
    recess = _wedge(a_sec0, a_sec1, R_IN + 1.0, R_OUT - 1.0, FACE_Z[1] - 2.4, FACE_Z[1] + 1, n=40)
    ring = face - recess
    ring = ring + _wedge(0, 360, SKIRT[0], SKIRT[1], SKIRT[2], FACE_Z[0], n=368) + _ratchet_lip(pointer)
    # slots for the sector's lug (S track) and tab, two divisions long
    lug_slot_r = ((TRACK_S[0] + TRACK_S[1]) / 2, 1.6)
    tab_slot_r = ((TRACK_TAB[0] + TRACK_TAB[1]) / 2, 1.6)
    for d_, (r_mid, hw) in ((L.SECTOR_COMMON_START - 1, lug_slot_r),
                            (L.SECTOR_TAB + L.SECTOR_COMMON_START - 1, tab_slot_r)):
        a = ring_angle(d_, pointer)
        ring -= _wedge(a - DIV / 2, a + DIV * 1.5, r_mid - hw, r_mid + hw, FACE_Z[0] - 1, FACE_Z[1] - 2.0, n=6)
    # S track rim (continuous, the stop lever rests on its face at RIM_Z), except under the lug slot
    rim = _wedge(0, 360, TRACK_S[0], TRACK_S[1], RIM_Z, FACE_Z[0], n=368)
    a = ring_angle(L.SECTOR_COMMON_START - 1, pointer)
    rim -= _wedge(a - DIV / 2, a + DIV * 1.5, TRACK_S[0] - 1, TRACK_S[1] + 1, RIM_Z - 1, FACE_Z[0] + 1, n=6)
    ring = ring + rim
    feats = {}
    for d_ in L.S_BUMPS:                                                       # fixed projection S
        a = ring_angle(d_, pointer)
        feats[f"S_bump_{d_}"] = _wedge(a - DIV * 0.45, a + DIV * 0.45, TRACK_S[0], TRACK_S[1], BAND[2], RIM_Z, n=4)
    a = ring_angle(L.COUNTER_PIN, pointer)
    feats["counter_pin"] = parts.rod(2.5, FACE_Z[0] - BAND[2]).moved(
        bd.Location((R_PIN * math.cos(math.radians(a)), R_PIN * math.sin(math.radians(a)), BAND[2])))
    a = ring_angle(L.MARCH1, pointer)
    feats["witness_flag_1_March"] = _wedge(a - DIV * 0.4, a + DIV * 0.4, TRACK_WITNESS[0], TRACK_WITNESS[1],
                                           BAND[2], FACE_Z[0], n=4)
    # sector: visible arc in the recess, with lug and tab through the slots
    s0 = ring_angle(sector_start, pointer) - DIV / 2
    s1 = ring_angle(sector_start + L.SECTOR_DAYS - 1, pointer) + DIV / 2
    sector = _wedge(s0 + 0.05, s1 - 0.05, R_IN + 1.2, R_OUT - 1.2, FACE_Z[1] - 2.3, FACE_Z[1] - 0.1, n=40)
    a_lug = ring_angle(sector_start - 1, pointer)
    sector += _wedge(a_lug - DIV * 0.4, a_lug + DIV * 0.4, TRACK_S[0] + 0.5, TRACK_S[1] - 0.5, BAND[2],
                     FACE_Z[1] - 2.2, n=4)
    a_tab = ring_angle(L.SECTOR_TAB + sector_start - L.SECTOR_COMMON_START, pointer)
    sector += _wedge(a_tab - DIV * 0.4, a_tab + DIV * 0.4, TRACK_TAB[0] + 0.5, TRACK_TAB[1] - 0.5, LAYER_A[0],
                     FACE_Z[1] - 2.2, n=4)
    return ring, sector, feats


def segments(ring, pointer: int, n: int = 4):
    """Split the ring at day boundaries into n printable arcs."""
    out = []
    for k in range(n):
        a0 = ring_angle(k * L.N // n, pointer) - DIV / 2
        a1 = ring_angle((k + 1) * L.N // n, pointer) - DIV / 2
        out.append(ring & _wedge(a0, a1, R_IN - 5, R_OUT + 5, -20, 5, n=60))
    return out


def build(pointer: int | None = None, sector_leap: bool = False):
    import datetime as dt
    if pointer is None:                                   # 3 Nov 2026
        pointer = L.initial_state(dt.date(2026, 11, 3)).pointer
    a = Assembly("m2_calendar")
    ring, sector, feats = ring_and_sector(pointer, sector_leap)
    for k, seg in enumerate(segments(ring, pointer)):
        a.add(f"ring_segment_{k}", seg, material="PLA", group="ring", note="two-colour print, dates in relief")
    a.add("sector_jan_feb", sector, material="PLA", group="ring", note="slides one division: leap / common")
    for nm, shp in feats.items():
        a.add(nm, shp, material="PLA" if "pin" not in nm else "steel", printed="pin" not in nm, group="ring")
        for k in range(4):
            a.allow(nm, f"ring_segment_{k}")
    for k in range(4):
        for j in range(k + 1, 4):
            a.allow(f"ring_segment_{k}", f"ring_segment_{j}")
        a.allow(f"ring_segment_{k}", "sector_jan_feb")
    # carrier with openings at the pointer and the station
    carrier = _wedge(0, 360, CARRIER[0], CARRIER[1], CARRIER[2], CARRIER[3], n=180)
    for ang_ in (0.0, STATION_ANGLE):
        carrier -= _wedge(ang_ - 6, ang_ + 6, BAND[0] - 1, CARRIER[1] + 1, CARRIER[2] - 1, CARRIER[3] + 1, n=8)
    station_ext = _wedge(STATION_ANGLE - 22, STATION_ANGLE + 22, CARRIER[1] - 2, STATION_R_MAX, CARRIER[2], CARRIER[3],
                         n=24)
    carrier = carrier + station_ext - _wedge(STATION_ANGLE - 6, STATION_ANGLE + 6, BAND[0] - 1, 190.0,
                                             CARRIER[2] - 1, CARRIER[3] + 1, n=8)
    for k in range(4):
        piece = carrier & _wedge(45 + 90 * k, 135 + 90 * k, 0, 230, -30, 10, n=40)
        a.add(f"carrier_segment_{k}", piece, material="PETG", group="carrier",
              note="mounted on the M2 front plate and, where it overhangs, on the case")
    for k in range(4):
        for j in range(k + 1, 4):
            a.allow(f"carrier_segment_{k}", f"carrier_segment_{j}")
    # rollers on studs
    b = BEARINGS["688ZZ"]
    for k, ang_ in enumerate((30, 90, 150, 210, 270 + 25, 330)):
        p = (ROLLER_R * math.cos(math.radians(ang_)), ROLLER_R * math.sin(math.radians(ang_)))
        a.add(f"roller_{k}", parts.bearing(b, SKIRT[2]).moved(bd.Location((p[0], p[1], 0))), material="bearing",
              printed=False, group="carrier")
        a.add(f"roller_stud_{k}", parts.rod(8.0, SKIRT[2] - CARRIER[2] + b.width).moved(
            bd.Location((p[0], p[1], CARRIER[2]))), material="steel", printed=False, group="carrier")
        a.allow(f"roller_{k}", f"roller_stud_{k}")
        for j in range(4):
            a.allow(f"roller_stud_{k}", f"carrier_segment_{j}")
            a.allow(f"roller_{k}", f"ring_segment_{j}")

    # ---------------------------------------------------------------- station (6 o'clock)
    st = STATION_ANGLE
    def P(r, da=0.0):
        t = math.radians(st + da)
        return (r * math.cos(t), r * math.sin(t))
    z_back = CARRIER[2]
    # counter star: 10 points, its tips sweep the pin's circle (r 157)
    star_c = P(R_PIN + 0.75 + 9.5)                       # star tips reach r 155.5, inside the pin's path
    th = np.radians(np.arange(20) * 18.0)
    star_pts = [((9.5 if k % 2 == 0 else 5.0) * math.cos(t), (9.5 if k % 2 == 0 else 5.0) * math.sin(t))
                for k, t in enumerate(th)]
    star = bd.extrude(bd.Face(bd.Wire.make_polygon([bd.Vector(x, y, 0) for x, y in star_pts], close=True)),
                      amount=2.0, dir=(0, 0, 1)).moved(bd.Location((star_c[0], star_c[1], BAND[2] + 0.2)))
    a.add("counter_star_10", star, group="station", note="one point per year (pin at d = 0)")
    star_shaft_len = BAND[2] + 0.2 - (z_back - 22.0)
    a.add("counter_star_shaft", parts.rod(3.0, star_shaft_len).moved(bd.Location((star_c[0], star_c[1], z_back - 22.0))),
          material="steel", printed=False, group="station")
    a.allow("counter_star_10", "counter_star_shaft")
    # pinion 10 on the star shaft drives wheel C (100 T): one tooth per year
    x10, x100 = pair_shifts(10, 100)
    g10, g100 = Gear(10, M_C, shift=x10), Gear(100, M_C, shift=x100)
    cd = centre_distance(g10, g100)
    theta_c = math.degrees(math.asin(min(1.0, (C_CENTRE_Y - star_c[1]) / cd)))
    c_xy = (star_c[0] + cd * math.cos(math.radians(theta_c)), star_c[1] + cd * math.sin(math.radians(theta_c)))
    zc = (z_back - 20.0, z_back - 17.0)
    a.add("pinion_10", spur_gear(g10, 3.0).moved(bd.Location((star_c[0], star_c[1], zc[0]))) -
          parts.disc(3.0, 20, z0=zc[0] - 5).moved(bd.Location((star_c[0], star_c[1], 0))), group="station")
    a.allow("pinion_10", "counter_star_shaft")
    rot_c = mesh_rotation(g10, g100, theta_c)
    wheel_c = spur_gear(g100, 3.0).rotate(bd.Axis.Z, rot_c) - parts.disc(3.3, 20, z0=-5)
    # 24 leap bumps on its front face at r 30 (positions 4, 8, ..., 96)
    for pos in range(4, 100, 4):
        t = math.radians(pos * 3.6 + 90)
        wheel_c += parts.disc(2.0, 1.5, z0=3.0).moved(bd.Location((30 * math.cos(t), 30 * math.sin(t), 0)))
    a.add("wheel_C_100", wheel_c.moved(bd.Location((c_xy[0], c_xy[1], zc[0]))), group="station",
          note="year in the century; 24 leap bumps")
    a.add("wheel_C_arbor", parts.rod(3.0, 26.0).moved(bd.Location((c_xy[0], c_xy[1], zc[0] - 6))), material="steel",
          printed=False, group="station")
    a.allow("wheel_C_100", "wheel_C_arbor")
    sat_xy = (c_xy[0] + 51.0 * math.cos(math.radians(-30)), c_xy[1] + 51.0 * math.sin(math.radians(-30)))
    a.add("satellite_4", parts.disc(28.0, 2.0, bore=3.3, z0=zc[1] + 0.5).moved(bd.Location((sat_xy[0], sat_xy[1], 0))),
          group="station", note="advanced 1/4 turn per century by a pin on C; one bump for x00 % 400 == 0")
    a.add("leap_follower", bd.Box(36.0, 4.0, 2.0, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN)).moved(
        bd.Location((c_xy[0] - 18.0, c_xy[1] + 30.0, zc[1] + 3.0))), group="station",
          note="reads C (and the satellite), positions the setter switch")
    setter = bd.Box(3.0, 8.0, LAYER_A[0] - (CARRIER[2] - 4.0), align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
                    ).rotate(bd.Axis.Z, st).moved(bd.Location((*P((TRACK_TAB[0] + TRACK_TAB[1]) / 2, 6.0),
                                                                CARRIER[2] - 4.0)))
    a.add("sector_setter_switch", setter, group="station",
          note="railway-switch guide: steers the passing tab to the leap or common side")
    # E6 drive: gearmotor, crank disc, pawl and jumper at the ratchet lip
    e6 = bd.Box(12.0, 10.0, 36.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).moved(
        bd.Location((*P(185.0, -10.0), z_back)))
    a.add("E6_gearmotor", e6, material="black", printed=False, group="station", note="Pololu micro-metal 100:1 class")
    a.add("E6_crank", parts.disc(14.0, 3.0, z0=CARRIER[3] + 0.4).moved(bd.Location((*P(184.0, -9.0), 0))),
          group="station")
    def link(p0, p1, w=3.0, t=2.5, z0=LIP[2] + 0.2):
        L_ = math.dist(p0, p1)
        ang_ = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
        return bd.Box(L_, w, t, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.Z, ang_).moved(
            bd.Location((p0[0], p0[1], z0)))
    pawl = link(P(184.0, -7.0), P(171.0, -2.5))
    a.add("E6_pawl", pawl, group="station", note="one crank turn = one ratchet tooth = one division")
    jumper = link(P(184.0, 8.0), P(171.0, 3.5))
    a.add("ring_jumper", jumper, group="station", note="detent between strokes")
    for nm in ("E6_pawl", "ring_jumper"):          # they rest in the ratchet's tooth gaps by design
        for kk in range(4):
            a.allow(nm, f"ring_segment_{kk}")
    a.add("E6_lock_switch", bd.Box(13.0, 6.0, 6.0).moved(bd.Location((*P(186.0, -17.0), z_back - 3.0))),
          material="green", printed=False, group="station")
    for nm in ("E6_gearmotor", "E6_lock_switch", "E6_crank"):
        for k in range(4):
            a.allow(nm, f"carrier_segment_{k}")
    for nm in ("counter_star_shaft", "sector_setter_switch", "leap_follower", "E6_pawl", "ring_jumper"):
        for k in range(4):
            a.allow(nm, f"carrier_segment_{k}")

    # ---------------------------------------------------------------- pointer side (3 o'clock)
    lever = bd.Box(3.0, 20.0, RIM_Z - (CARRIER[2] - 3.0), align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN)).moved(
        bd.Location(((TRACK_S[0] + TRACK_S[1]) / 2, -2.0, CARRIER[2] - 3.0)))
    a.add("stop_lever", lever, group="pointer", note="held up by S, the sector lug: keeps E6 running")
    a.add("stop_switch", bd.Box(13.0, 6.0, 6.0).moved(bd.Location((153.0, 24.0, CARRIER[2] - 3.0))),
          material="green", printed=False, group="pointer")
    a.add("witness_opto_1_March", bd.Box(2.2, 4.0, 2.0, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MAX)).moved(
        bd.Location((147.8, -13.0, -8.6))),
          material="green", printed=False, group="pointer", note="fires each 1 March (fixed part of the ring)")
    arrow = bd.extrude(bd.Face(bd.Wire.make_polygon([bd.Vector(176, 0, 0), bd.Vector(196, 5, 0), bd.Vector(196, -5, 0)],
                                                    close=True)), amount=2.0, dir=(0, 0, 1)).moved(bd.Location((0, 0, 0.5)))
    a.add("apollo_arrow", arrow, material="silver", group="pointer", note="Apollo's arrow (figure in E-module design)")
    for nm in ("stop_lever", "stop_switch", "witness_opto_1_March"):
        for k in range(4):
            a.allow(nm, f"carrier_segment_{k}")
    return a, {"pointer": pointer, "sector_leap": sector_leap, "wheel_C_centre": [round(c_xy[0], 1), round(c_xy[1], 1)],
               "station_angle": round(STATION_ANGLE, 2), "roller_radius": ROLLER_R}
