"""M2 calendar ring (inventory I8) and its New Year station: the 3-D design.

The logic is ``calendar_logic.py`` (checked day by day over four centuries). This module gives it
parts, at 1:8 [S: ELS i4: Ø 2.73 m outer, 21 cm wide, 368 divisions → Ø 341, 26 mm wide]:

- **Ring**, 4 printed segments joined at day boundaries: the visible face (z -3 … 0), a rear skirt
  riding on 6 rollers (688ZZ), and a thin rear lip with 368 ratchet teeth (one per division).
- **Feature band** behind the face (r 148 … 162, z -8.3 … -5.8): fixed bumps S at d = 0, 1; the
  sector's lug and tab (through slots); the counter pin at d = 0; the 1 March witness flag.
  The stop-lever track is split in two halves read by the one lever: the fixed bumps on the inner
  half, the sector's lug on the outer half, so the lug never meets a bump in either position.
- **Movable sector** (1 Jan … 28 Feb), sliding one division in a recess of the face. Its foot goes
  through a slot under its first day; behind the face, a short arm carries the lug one division
  back (where the logic wants it), on a 45°-ish chamfer so the face-down print needs no support.
- **Dates** (Paul, PR #5: sizes approved; layout from Paul's photograph of the original, PR #6): each
  day reads inwards along its division, day number then dominical letter, 2.2 mm capitals (≈ 9 pt),
  the letters in one straight column; month names 4 mm (≈ 16 pt) round the outer edge, reading
  clockwise with their tops outwards; "COMMENCEMENT", "DE L'ANNÉE", "COMMUNE" on divisions 0–2
  [S: ELS i4] and "29 F" on
  d = 61, both on the recess floor where the sector uncovers them. Letters A … G from A on
  1 January [S: ELS i4: "Au 1er janvier correspond la lettre A"]; 29 February carries F, as on the
  original (Paul, PR #6), the letter of the Roman bissextile day (the doubled 24 February). All
  flush two-colour inlays, 0.4 mm deep,
  black on gold ("sur un fond doré" [S: DA p. 27]; the letter colour is [E]), except the dominical
  letters, which are gold in a black column, as on the original (Paul's photograph; Paul, PR #6).
- **Carrier** (4 printed segments) holding the rollers, with openings where readers reach the band:
  the **stop lever** and the **witness opto** at the pointer (9 o'clock), and the **station** at
  6 o'clock: E6 gearmotor + crank + pawl, jumper, 10-point counter star, wheel C (100 T) with its
  24 leap bumps, the satellite, the follower and the sector setter switch.

**Pointer on the viewer's left** [S: ELS i4: "le jour qui commence venant alors sur la gauche de
l'anneau, en face de la flèche"; DA p. 27: Apollo "se tient à la droite du calendrier", the
calendar's own right, i.e. the viewer's left]. **The ring turns clockwise** seen from the front, so
the year runs counter-clockwise round it and tomorrow sits just below the arrow (Paul's photograph of
the original, PR #6). Ring division d sits at world angle 180° + (d - pointer) x 360/368, and the
station (pointer + 92) is at 270°, the bottom. The geometry is built in a canonical frame (pointer at
0°, ring turning clockwise) and turned 180° about the dial axis, which gives exactly that mapping.
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
from cad.modules.m2_main_dial import setter as S

R_OUT, R_IN = F.RING_OD / 2, F.RING_OD / 2 - F.RING_W        # 170.5, 144.5
DIV = 360.0 / L.N
FACE_Z = (-3.0, 0.0)
SKIRT = (144.5, 147.5, -8.5)                                 # r_in, r_out, z_back
LIP = (163.0, 170.5, -5.5)                                   # r_in, r_tip, z_back (teeth on the outer edge)
BAND = (148.0, 162.0, -8.3, -5.8)                            # feature band behind the face
# radial tracks in the band (each is read by one reader only) and the two depth layers
TRACK_WITNESS = (148.0, 149.5)                                # 1 March flag, opto at the pointer
TRACK_S = (150.0, 154.0)                                      # rim + bumps + sector lug, stop lever
S_INNER = (150.2, 151.8)                                      # its inner half: the fixed bumps S
S_OUTER = (152.2, 153.8)                                      # its outer half: the sector's lug, arm, foot
ARM_Z = (-6.3, -5.5)                                          # the lug's arm: in front of the lever's plane
R_PIN = 156.25                                                # counter pin, star at the station
TRACK_TAB = (159.0, 162.0)                                    # sector tab, setter at the station
LAYER_A = (-5.8, -3.0)                                        # shallow: tab
LAYER_B = (-8.3, -6.0)                                        # deep: star, lever tip, flag
RIM_Z = -6.5                                                  # S-track rim face; bumps reach -8.3
CARRIER = (133.0, 178.0, -10.9, -8.8)                        # r_in, r_out, z0, z1 (in front of the M2 front plate)
ROLLER_R = SKIRT[0] - BEARINGS["688ZZ"].od / 2               # 136.5
STATION_ANGLE_C = L.STATION_OFFSET * DIV                     # +90° in the canonical frame
STATION_ANGLE = STATION_ANGLE_C + 180.0 - 360.0              # -90° in the world: 6 o'clock
POINTER_ANGLE = 180.0                                        # the viewer's left (canonical 0° turned 180°)
M_C = 0.8                                                    # wheel C module (hidden, light load)
# dates (flush inlays, depth TEXT_DEPTH): (cap height, stroke, letter spacing) in mm
TEXT_DEPTH = 0.4
DAY_TEXT = (2.2, 0.35, 0.35)           # dominical letters and day numbers (Paul, PR #5)
MONTH_TEXT = (4.0, 0.6, 0.8)           # month names (Paul, PR #5)
WORD_TEXT = (1.6, 0.3, 0.3)            # "COMMENCEMENT", "DE L'ANNÉE", "COMMUNE": long words in one division
# across the band, outside in, as on the original (Paul's photograph, PR #6): month name, day number,
# dominical letter (then the saints, left out at 1:8)
MONTH_R = 163.7                        # month-name baseline, tops outward: capitals to 168.0, accents to 169.0
LETTER_R0 = 158.0                      # dominical letters: one straight column, reading inwards from here
DAY_GAP = 0.9                          # between a day number and its letter
NUMBER_END = LETTER_R0 + DAY_GAP       # day numbers end here (right-aligned on the letter column)
WORD_R0 = 168.6                        # "COMMENCEMENT" … start at the outer edge (no month name there)
STRIPE_PAD = 0.4                       # the letter column is a black stripe this much wider than the letters,
                                       # with the letters left gold, as on the original (Paul, PR #6)
MONTHS = ("JANVIER", "FÉVRIER", "MARS", "AVRIL", "MAI", "JUIN", "JUILLET", "AOÛT", "SEPTEMBRE", "OCTOBRE",
          "NOVEMBRE", "DÉCEMBRE")
MONTH_DAYS = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
FEB29_LETTER = "F"                     # as on the original (Paul, PR #6): the Roman bissextile day's letter
RIM_SPAN = (-55.0, 150.0)      # rim where the carrier overhangs the M2 front plate (world angles, CCW)
RIM_BACK_Z = -40.0             # L-section depth
CARRIER_BOLTS = (165.0, 195.0, 225.0)     # countersunk M3 into the M2 front plate, where they overlap
CASE_TABS = (20.0, 90.0, 120.0)           # M5 tabs (clear of the carrier splits): the frame is held, never set
STATION_R_MAX = 195.0          # nothing below 195 mm under the dial centre: ~18 mm above the floor [E]
C_CENTRE_Y = -150.0            # wheel C raised beside the station, behind the M2 front plate


def ring_angle(d: int, pointer: int) -> float:
    return (d - pointer) * DIV


def _wedge(a0: float, a1: float, r0: float, r1: float, z0: float, z1: float, n: int = 24):
    """Annular sector between angles a0..a1 (degrees); a full turn is a true annulus (outer polygon
    with an inner hole), not a polygon that runs out and back, whose zero-width slit leaves two
    coincident faces in the solid and a non-manifold seam in its mesh."""
    if a1 - a0 >= 360.0 - 1e-9:
        th = np.radians(np.linspace(a0, a0 + 360.0, n, endpoint=False))
        ring_ = lambda r: bd.Wire.make_polygon([bd.Vector(r * math.cos(t), r * math.sin(t), 0) for t in th], close=True)
        face = bd.Face(ring_(r1), [ring_(r0)]) if r0 > 0 else bd.Face(ring_(r1))
    else:
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
    # slots through the recess floor, each over its part's travel (common position and one division
    # back): the sector's foot (under its first day, outer half of the S track) and its tab
    for d0, d1, r0, r1 in ((L.SECTOR_COMMON_START - 1, L.SECTOR_COMMON_START, S_OUTER[0] - 0.2, S_OUTER[1] + 0.2),
                           (L.SECTOR_TAB - 1, L.SECTOR_TAB, TRACK_TAB[0] - 0.6, TRACK_TAB[1] + 0.1)):
        ring -= _wedge(ring_angle(d0, pointer) - DIV / 2, ring_angle(d1, pointer) + DIV / 2, r0, r1,
                       FACE_Z[0] - 1, FACE_Z[1] - 2.0, n=6)
    # S track rim: the stop lever rests on its face at RIM_Z. Its outer half is cut away where the
    # sector's lug and arm travel (d 0.5 … 3.5); the inner half stays continuous under the lever.
    rim = _wedge(0, 360, TRACK_S[0], TRACK_S[1], RIM_Z, FACE_Z[0], n=368)
    rim -= _wedge(ring_angle(L.SECTOR_COMMON_START - 2, pointer) - DIV / 2,
                  ring_angle(L.SECTOR_COMMON_START, pointer) + DIV / 2,
                  S_OUTER[0] - 0.2, TRACK_S[1] + 1.0, RIM_Z - 1, FACE_Z[0] + 0.5, n=8)
    ring = ring + rim
    feats = {}
    for d_ in L.S_BUMPS:                                       # fixed projection S, inner half of the track
        a = ring_angle(d_, pointer)
        feats[f"S_bump_{d_}"] = _wedge(a - DIV * 0.45, a + DIV * 0.45, S_INNER[0], S_INNER[1], BAND[2], RIM_Z, n=4)
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
    # foot under the first day, through the floor slot; arm back one division; the lug on its end
    a_foot = ring_angle(sector_start, pointer)
    sector += _wedge(a_foot - DIV * 0.4, a_foot + DIV * 0.4, S_OUTER[0], S_OUTER[1], ARM_Z[0], FACE_Z[1] - 2.2, n=4)
    sector += _wedge(a_foot - DIV * 1.4, a_foot, S_OUTER[0], S_OUTER[1], ARM_Z[0], ARM_Z[1], n=6)
    sector += _wedge(a_foot - DIV * 1.4, a_foot - DIV * 0.6, S_OUTER[0], S_OUTER[1], BAND[2], ARM_Z[1], n=4)
    r_m = (S_OUTER[0] + S_OUTER[1]) / 2                    # chamfer under the arm (prints face down unsupported)
    t0, t1 = -0.4 * math.radians(DIV) * r_m, -1.4 * math.radians(DIV) * r_m
    tri = bd.Face(bd.Wire.make_polygon([bd.Vector(S_OUTER[0], y_, z_) for y_, z_ in (
        (t0 + 0.05, FACE_Z[0] - 0.3), (t0 + 0.05, ARM_Z[1] - 0.01), (t1, ARM_Z[1] - 0.01))], close=True))
    sector += bd.extrude(tri, amount=S_OUTER[1] - S_OUTER[0], dir=(1, 0, 0)).rotate(bd.Axis.Z, a_foot)
    sector += S.tab_pin(pointer, sector_start)          # the tab: a pin the setter's rocker holds
    return ring, sector, feats


def _grow(points, d):
    from shapely.geometry import Polygon
    return list(Polygon(points).buffer(d, join_style=2).exterior.coords)[:-1]


def world_angle(d: float, pointer: int) -> float:
    """Angle (degrees, world frame) of division d's centre line: canonical turned by 180°."""
    return 180.0 + ring_angle(d, pointer)


def _day_of_month(n: int) -> int:
    for m, days in enumerate(MONTH_DAYS):
        if n <= days:
            return n
        n -= days
    raise ValueError(n)


def date_inlays(pointer: int, sector_leap: bool):
    """The dates as inlay solids in the world frame: (ring face, recess floor, sector face)."""
    from cad.lib import lettering as T
    sector_start = L.SECTOR_COMMON_START - (1 if sector_leap else 0)
    groups = {"face": [], "floor": [], "sector": []}
    letters = {"face": [], "floor": [], "sector": []}       # cut out of the black stripe: they stay gold

    def entry(group, d, number, letter):                   # day number, then its dominical letter
        th = world_angle(d, pointer)
        h, w, sp = DAY_TEXT
        _, n_len, _ = T.layout(number, h, w, sp)
        groups[group].append((T.radial(number, th, NUMBER_END + n_len, h, w, sp), w))
        letters[group].append((T.radial(letter, th, LETTER_R0, h, w, sp), w))

    def day(group, d, n):
        entry(group, d, str(_day_of_month(n)), "ABCDEFG"[(n - 1) % 7])

    for j in range(L.SECTOR_DAYS):                         # 1 Jan … 28 Feb on the sector
        day("sector", sector_start + j, j + 1)
    for d in range(L.MARCH1, L.N):                         # 1 Mar … 31 Dec on the ring
        day("face", d, d - L.MARCH1 + 60)
    h, w, sp = WORD_TEXT
    for d, word, group in ((0, "COMMENCEMENT", "face"), (1, "DE L'ANNÉE", "face"), (2, "COMMUNE", "floor")):
        groups[group].append((T.radial(word, world_angle(d, pointer), WORD_R0, h, w, sp), w))
    entry("floor", L.FEB29, "29", FEB29_LETTER)            # 29 Feb: F, as on the original (Paul, PR #6)
    h, w, sp = MONTH_TEXT
    n0 = 1
    for m, (name, days) in enumerate(zip(MONTHS, MONTH_DAYS)):
        n_mid = n0 + (days - 1) / 2
        d_mid = sector_start + n_mid - 1 if m < 2 else L.MARCH1 + n_mid - 60
        groups["sector" if m < 2 else "face"].append(
            (T.along_arc(name, world_angle(d_mid, pointer), MONTH_R, h, w, sp, clockwise=True), w))
        n0 += days

    # the letter column: a black stripe over the days of each part, the letters cut out of it
    from shapely.geometry import Polygon
    h, w, sp = DAY_TEXT
    l_len = max(T.layout(c, h, w, sp)[1] for c in "ABCDEFG")
    r0, r1 = LETTER_R0 - l_len - STRIPE_PAD, LETTER_R0 + STRIPE_PAD

    def stripe(d0, d1):
        a = np.radians(np.linspace(world_angle(d0, pointer), world_angle(d1, pointer), max(8, int((d1 - d0) * 4))))
        return Polygon([(r1 * math.cos(t), r1 * math.sin(t)) for t in a] +
                       [(r0 * math.cos(t), r0 * math.sin(t)) for t in a[::-1]])

    stripes = {"face": stripe(L.MARCH1 - 0.5, L.N - 0.5),                      # 1 Mar … 31 Dec
               "sector": stripe(sector_start - 0.5, sector_start + L.SECTOR_DAYS - 0.5),
               "floor": stripe(L.FEB29 - 0.48, L.FEB29 + 0.48)}                # 29 Feb, inside the recess
    out = {}
    for g, items in groups.items():
        cut = stripes[g].difference(T.merge([T.outline(lines, w_) for lines, w_ in letters[g]]))
        out[g] = T.clean(T.merge([T.outline(lines, w_) for lines, w_ in items] + [cut]))
    return out


def _top_polygon(face):
    """Shapely polygon of a planar build123d face (outer wire and holes), sampling curved edges."""
    from shapely.geometry import Polygon

    def ring(wire):
        pts = []
        for e in wire.order_edges():
            n = 1 if e.geom_type == bd.GeomType.LINE else 12
            pts += [(v.X, v.Y) for v in (e.position_at(t / n) for t in range(n))]
        return pts
    return Polygon(ring(face.outer_wire()), [ring(w) for w in face.inner_wires()])


def _glue(a, b):
    """Fuse two solids that only touch on (partly) coinciding faces: OCCT's glue mode skips the
    face-face intersections that make a plain boolean with thousands of glyph edges so slow."""
    from OCP.BOPAlgo import BOPAlgo_GlueShift
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
    from OCP.collections import List_TopoDS_Shape as _List
    args, tools = _List(), _List()
    args.Append(a.wrapped)
    tools.Append(b.wrapped)
    op = BRepAlgoAPI_Fuse()
    op.SetArguments(args)
    op.SetTools(tools)
    op.SetGlue(BOPAlgo_GlueShift)
    op.Build()
    if not op.IsDone():
        raise RuntimeError("glue fuse failed")
    return bd.Part(bd.Shape.cast(op.Shape()))


def with_inlay(body, text_geom, z_top: float):
    """(base, text): ``body`` with a flush inlay ``text_geom`` (Shapely, plane XY) sunk TEXT_DEPTH
    into its top face at ``z_top``. The top layer is rebuilt in 2D and glued back, so no boolean
    ever meets the glyphs."""
    from cad.lib import lettering as T
    cut = bd.Box(1000, 1000, 50, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(
        bd.Location((0, 0, z_top - TEXT_DEPTH)))
    from shapely.ops import unary_union
    layer = body & cut
    tops = [f for f in layer.faces() if abs(f.center().Z - z_top) < 1e-6 and abs(f.normal_at().Z) > 0.999]
    poly = unary_union([_top_polygon(f) for f in tops])     # several faces where the ring's seam crosses
    gold, ink = poly.difference(text_geom), poly.intersection(text_geom)
    ext = lambda g: bd.extrude(bd.Compound(T.faces(g, z_top)), amount=TEXT_DEPTH, dir=(0, 0, -1))
    return _glue(body - cut, ext(gold)), ext(ink)


def segments(ring, pointer: int, n: int = 4):
    """Split the ring at day boundaries into n printable arcs."""
    out = []
    for k in range(n):
        a0 = ring_angle(k * L.N // n, pointer) - DIV / 2
        a1 = ring_angle((k + 1) * L.N // n, pointer) - DIV / 2
        out.append(ring & _wedge(a0, a1, R_IN - 5, R_OUT + 5, -20, 5, n=60))
    return out


def build(pointer: int | None = None, sector_leap: bool = False, dates: bool = True,
          set_engaged: bool | None = None):
    import datetime as dt
    m0 = L.initial_state(dt.date(2026, 11, 3))           # the model's date: 3 Nov 2026
    if pointer is None:
        pointer = m0.pointer
    c_now, sat_now = m0.c, m0.satellite                 # wheel C already set for 2027
    if set_engaged is None:
        set_engaged = L.leap_from_counter(c_now, sat_now)
    a = Assembly("m2_calendar")
    ring, sector, feats = ring_and_sector(pointer, sector_leap)
    mirror = lambda shp: shp.rotate(bd.Axis.Z, 180.0)     # canonical (pointer at 0°) -> world (pointer at 180°)
    sector = mirror(sector)
    feats = {k: mirror(v) for k, v in feats.items()}
    geoms = date_inlays(pointer, sector_leap) if dates else None
    for k, seg in enumerate(mirror(sg) for sg in segments(ring, pointer)):
        whole = seg
        note = "gold, face down: the dates are a flush black inlay on the bed side (0.2 mm nozzle)"
        if k == 0:
            note += ("; the Jan-Feb sector's seat is a pocket open to the bed: support from the bed inside it, "
                     "ideally with a support-interface filament on the second nozzle")
        if dates:
            seg, text = with_inlay(seg, geoms["face"], FACE_Z[1])
            if k == 0:                                     # "COMMUNE" and "F 29" on the recess floor
                from cad.lib import lettering as T
                floor_in = bd.extrude(bd.Compound(T.faces(geoms["floor"], FACE_Z[1] - 2.4)), amount=TEXT_DEPTH,
                                      dir=(0, 0, -1))
                text = text + (seg & floor_in)
                seg = seg - floor_in
            a.add(f"ring_text_{k}", text, material="black", group="ring", print_up=(0, 0, -1), print_set=f"ring_{k}",
                  nozzle=0.2, inside=f"ring_segment_{k}", note=f"dates, second filament of ring_{k}.3mf")
            a.allow(f"ring_text_{k}", f"ring_segment_{k}")
        a.add(f"ring_segment_{k}", seg, material="PLA", group="ring", print_up=(0, 0, -1), nozzle=0.2,
              print_set=f"ring_{k}" if dates else "", note=note, filled=whole if dates else None)
    sector_whole = sector
    if dates:
        sector, sector_text = with_inlay(sector, geoms["sector"], FACE_Z[1] - 0.1)
        a.add("sector_text", sector_text, material="black", group="ring", print_up=(0, 0, -1),
              print_set="sector", nozzle=0.2, inside="sector_jan_feb",
              note="1 Jan … 28 Feb, second filament of sector.3mf")
        a.allow("sector_text", "sector_jan_feb")
    a.add("sector_jan_feb", sector, material="PLA", group="ring", print_up=(0, 0, -1), nozzle=0.2,
          print_set="sector" if dates else "", filled=sector_whole if dates else None, note="slides one division: leap / common; foot, arm and lug grow up "
          "from the face-down plate on a chamfer, no support")
    for nm, shp in feats.items():
        a.add(nm, shp, material="PLA" if "pin" not in nm else "steel", printed="pin" not in nm, group="ring")
        for k in range(4):
            a.allow(nm, f"ring_segment_{k}")
    for k in range(4):                     # the segments touch at their joints; the sector clears the ring
        for j in range(k + 1, 4):
            a.allow(f"ring_segment_{k}", f"ring_segment_{j}")
    # carrier with openings at the pointer and the station
    carrier = _wedge(0, 360, CARRIER[0], CARRIER[1], CARRIER[2], CARRIER[3], n=180)
    for ang_ in (0.0, STATION_ANGLE_C):
        carrier -= _wedge(ang_ - 6, ang_ + 6, BAND[0] - 1, CARRIER[1] + 1, CARRIER[2] - 1, CARRIER[3] + 1, n=8)
    station_ext = _wedge(STATION_ANGLE_C - 22, STATION_ANGLE_C + 22, CARRIER[1] - 2, STATION_R_MAX, CARRIER[2], CARRIER[3],
                         n=24)
    carrier = carrier + station_ext - _wedge(STATION_ANGLE_C - 6, STATION_ANGLE_C + 6, BAND[0] - 1, 190.0,
                                             CARRIER[2] - 1, CARRIER[3] + 1, n=8)
    carrier = mirror(carrier)
    window = bd.extrude(bd.Face(bd.Wire.make_polygon(
        [bd.Vector(x, y, CARRIER[2] - 1) for x, y in _grow(S.ramp_outlines()["set"], 0.25)], close=True)),
        amount=CARRIER[3] - CARRIER[2] + 2, dir=(0, 0, 1))
    carrier = carrier - window                            # the set ramp drops into it when not needed
    # --- a self-supporting printed frame (Paul, PR #5: the works are printed and independent of the
    # case). Where the carrier overhangs the M2 front plate (top and right) a rear rim stiffens it
    # into an L-section; where it overlaps the plate, countersunk M3 screws bolt it to the plate.
    rim = _wedge(RIM_SPAN[0], RIM_SPAN[1], CARRIER[1] - 4.0, CARRIER[1], RIM_BACK_Z, CARRIER[2] + 0.01, n=80)
    carrier = carrier + rim
    for ang_ in CARRIER_BOLTS:
        p_ = (172.0 * math.cos(math.radians(ang_)), 172.0 * math.sin(math.radians(ang_)))
        carrier -= parts.disc(3.4, 10, z0=CARRIER[2] - 1).moved(bd.Location((p_[0], p_[1], 0)))
        carrier -= parts.disc(6.4, 1.8, z0=CARRIER[3] - 1.7).moved(bd.Location((p_[0], p_[1], 0)))   # countersink
    for k, ang_ in enumerate(CASE_TABS):
        # a straight tab off the back of the rim, M5 clearance hole; two 45° gussets at its edges, clear
        # of the screw head and washer, make it print without support (the carrier prints face down)
        tab = bd.Box(CARRIER[1] + 14.0 - (CARRIER[1] - 4.0), 18.0, 4.0, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN)
                     ).moved(bd.Location((CARRIER[1] - 4.0, 0, RIM_BACK_Z)))
        prof = bd.Face(bd.Wire.make_polygon([bd.Vector(x_, 0, z_) for x_, z_ in (
            (CARRIER[1] - 1.0, RIM_BACK_Z + 3.9), (CARRIER[1] + 14.0, RIM_BACK_Z + 3.9),
            (CARRIER[1] - 1.0, RIM_BACK_Z + 18.9))], close=True))
        for y_ in (-9.0, 5.5):
            tab = tab + bd.extrude(prof, amount=3.5, dir=(0, 1, 0)).moved(bd.Location((0, y_, 0)))
        tab -= parts.disc(5.5, 10, z0=RIM_BACK_Z - 2).moved(bd.Location((CARRIER[1] + 7.0, 0, 0)))
        carrier = carrier + tab.rotate(bd.Axis.Z, ang_)
    # splits: three where the carrier is clear of the front plate (spliced) and one at 225° where it
    # sits on the plate (both ends bolted to it). 330°, not 315°, keeps that splice off the plate's corner.
    split = (45.0, 135.0, 225.0, 330.0)
    for k in range(4):
        a1_ = split[(k + 1) % 4] + (360.0 if k == 3 else 0.0)
        piece = carrier & _wedge(split[k], a1_, 0, 230, -60, 10, n=40)
        a.add(f"carrier_segment_{k}", piece, material="PETG", group="carrier", print_up=(0, 0, -1),
              note="printed frame segment, face down; L-section rim where it overhangs the front plate")
    for k in range(4):
        for j in range(k + 1, 4):
            a.allow(f"carrier_segment_{k}", f"carrier_segment_{j}")
    for k, ang_ in enumerate(s_ for s_ in split if not (150.0 <= s_ <= 240.0)):   # the plate joins the 225° split
        joint = _wedge(ang_ - 9, ang_ + 9, 150.0, CARRIER[1] - 4.2, CARRIER[2] - 2.5, CARRIER[2], n=10)
        for d_ in (-5.0, 5.0):
            q = (163.0 * math.cos(math.radians(ang_ + d_)), 163.0 * math.sin(math.radians(ang_ + d_)))
            joint -= parts.disc(3.4, 10, z0=CARRIER[2] - 5).moved(bd.Location((q[0], q[1], 0)))
        a.add(f"carrier_joint_{k}", joint, material="PETG", group="carrier", note="splice plate, 2 x M3 each side")
        for j in range(4):
            a.allow(f"carrier_joint_{k}", f"carrier_segment_{j}")
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
    # setter and year counter (setter.py): rocker on the ring, reset and set ramps, counting lever,
    # wheel C with its leap bumps and Ungerer's satellite, the plunger that carries the set ramp
    for nm, shp in S.rocker_parts(pointer, sector_leap).items():
        a.add(nm, mirror(shp), material="steel" if nm.endswith("pivot") else ("PETG" if "spring" in nm else "PLA"),
              printed=not nm.endswith("pivot"), group="ring",
              note={"setter_rocker": "flip-flop: holds the sector's tab pin; its tip pins meet the station's ramps",
                    "setter_rocker_pivot": "Ø2 pin pressed into the ratchet lip",
                    "setter_detent_spring": "printed leaf glued under the lip: holds the rocker in either position"}[nm])
    a.allow("setter_rocker", "setter_rocker_pivot")
    a.allow("setter_rocker", "setter_detent_spring")
    for k in range(4):
        a.allow("setter_rocker_pivot", f"ring_segment_{k}")
        a.allow("setter_detent_spring", f"ring_segment_{k}")
    for nm, shp, kw in S.station_parts(c_now, sat_now, set_engaged):
        a.add(nm, shp, **kw)
    for x, y in (("wheel_C_100", "wheel_C_arbor"), ("wheel_C_100", "satellite_4"), ("wheel_C_100", "satellite_pin"),
                 ("satellite_4", "satellite_pin"), ("satellite_step_pin", "station_bracket"),
                 ("wheel_C_100", "counting_lever"), ("wheel_C_100", "wheel_C_jumper"),
                 ("wheel_C_jumper", "station_bracket"), ("counting_lever", "counting_lever_stud"),
                 ("setter_set_ramp", "wheel_C_100"), ("setter_set_ramp", "setter_plunger_spring"),
                 ("setter_plunger_spring", "station_bracket"), ("setter_set_ramp", "satellite_4")):
        a.allow(x, y)
    for k in range(4):
        a.allow("setter_reset_ramp", f"carrier_segment_{k}")
        a.allow("station_bracket", f"carrier_segment_{k}")
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
    a.add("E6_pawl", pawl, group="station",
          note="pulls the ring clockwise: one crank turn = one ratchet tooth = one division")
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
    for nm in ("E6_pawl", "ring_jumper"):
        for k in range(4):
            a.allow(nm, f"carrier_segment_{k}")

    # ---------------------------------------------------------------- pointer side (9 o'clock: built at 0°, turned 180°)
    lever = bd.Box(3.0, 20.0, RIM_Z - (CARRIER[2] - 3.0), align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN)).moved(
        bd.Location(((TRACK_S[0] + TRACK_S[1]) / 2, -2.0, CARRIER[2] - 3.0)))
    a.add("stop_lever", mirror(lever), group="pointer", print_up=(1, 0, 0),
          note="held up by S, the sector lug: keeps E6 running")
    a.add("stop_switch", mirror(bd.Box(13.0, 6.0, 6.0).moved(bd.Location((153.0, 24.0, CARRIER[2] - 3.0)))),
          material="green", printed=False, group="pointer")
    a.add("witness_opto_1_March", mirror(bd.Box(2.2, 4.0, 2.0, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MAX)).moved(
        bd.Location((147.8, -13.0, -8.6)))),
          material="green", printed=False, group="pointer", note="fires each 1 March (fixed part of the ring)")
    arrow = bd.extrude(bd.Face(bd.Wire.make_polygon([bd.Vector(176, 0, 0), bd.Vector(196, 5, 0), bd.Vector(196, -5, 0)],
                                                    close=True)), amount=2.0, dir=(0, 0, 1)).moved(bd.Location((0, 0, 0.5)))
    a.add("apollo_arrow", mirror(arrow), material="silver", group="pointer",
          note="Apollo's arrow, viewer's left (figure in E-module design)")
    for nm in ("stop_lever", "stop_switch", "witness_opto_1_March"):
        for k in range(4):
            a.allow(nm, f"carrier_segment_{k}")
    return a, {"pointer": pointer, "sector_leap": sector_leap, "wheel_C_centre": list(S.C_XY),
               "wheel_C_position": c_now, "satellite": sat_now, "set_ramp_engaged": set_engaged,
               "station_angle": round(STATION_ANGLE, 2), "pointer_angle": POINTER_ANGLE, "roller_radius": ROLLER_R}
