"""E2, the four ages and Death: detail design, parts 1 and 2a (docs/e2-design.md §10).

Part 1 modelled the hall, the ring (turntable) with its rollers, teeth and pegs, and the walk pinion. Part 2a
(drives.py, program.py) adds the two stops with their gears, crank and push rod, the walk drive (gearmotor, slip
clutch, program gear, program and lock cams, lock switch, the bell-station Hall) and the state module (the arbor
with the age cam, the quarter snail, the index, the 12:1 motion work with the hour snail, the NEMA 17 on its D16
adapter). Part 2b (the quarter and hour trains, Death's arm, the ages' arms) and part 3 (the figures) follow; the
figures are placeholders, at their decided heights.

The model shows the rest state at 12:10: the child waits at the right doorway, held by its waiting peg; the old
man (who struck at 12:00) stands at the left doorway. The age cam selects the child; the program is at rest
(state B: the waiting arm in, the bell arm swung out).

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
from cad.modules.e2_ages import drives as D
from cad.modules.e2_ages import layout as L
from cad.modules.e2_ages import program as G
from cad.modules.e2_ages import strikers as K
from cad.modules.e2_ages.drives import age_cam_radius  # noqa: F401

DECK = D.DECK                               # the module's deck plate (z)
DECK_XY = (-145.0, 150.0, -62.0, 235.0)     # x0, x1, y0, y1
SUPPORT_R, SUPPORT_THETA = 118.0, (0.0, 90.0, 180.0, 270.0)     # 688ZZ under the ring (standard angles)
GUIDE_R, GUIDE_THETA = 100.0, (-30.0, 90.0, 210.0)              # 688ZZ inside the inner skirt
ISLAND_POSTS = ((0.0, 34.0), (52.0, 124.0), (-52.0, 124.0))
FLOOR_POSTS = ((60.0, -42.5), (-60.0, -42.5), (96.5, -25.0), (-96.5, -25.0))
MODEL_TIME = D.MODEL_TIME                   # the rest state shown (legal time)
MODEL_THETA = 0.0                           # the program at rest


def at(shape, xy, z=0.0):
    return shape.moved(bd.Location((xy[0], xy[1], z)))


def theta_of(phi: float) -> float:
    """Standard plan angle (from +X, anticlockwise) of ring angle φ."""
    return phi - 90.0


def annulus(r_in, r_out, z0, z1):
    return parts.disc(2 * r_out, z1 - z0, bore=2 * r_in, z0=z0)


def peg_at(phi, z, r0, r1, d):
    """A radial peg from r0 to r1 at ring angle φ and height z."""
    return D.peg_shape(phi, z, r0, r1, d)


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
        ring += peg_at(L.PHI_REST[k] + L.WAIT_PEG_OFFSET, L.WAIT_PEG["z"], L.WAIT_PEG["r"][0] - 0.5,
                       L.WAIT_PEG["r"][1], L.WAIT_PEG["d"])
        mp = L.polar(L.PHI_REST[k], D.MAGNET_R)
        ring -= at(parts.disc(D.MAGNET[0] + 0.2, D.MAGNET[1] + 0.2, z0=-L.FLOOR_T - 0.01), mp)
        a.add(f"ring_magnet_{k}", at(parts.disc(D.MAGNET[0], D.MAGNET[1], z0=-L.FLOOR_T + 0.1), mp), material="silver",
              printed=False, group="ring", note=f"Ø5 x 2 magnet under the {name.replace('_', ' ')}: the bell Hall sees it")
        a.allow(f"ring_magnet_{k}", "ring")
    a.add("ring", ring, material="PLA", group="ring", print_up=(0, 0, -1),
          note=f"turntable Ø{2 * L.ANNULUS[1]:.0f}: walking surface flush with the floor, {L.TEETH['z']} teeth; "
               "per age a selection peg at its own height and a waiting peg below them all")
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

    # ------------------------------------------------------------------ the walk pinion (on the walk shaft)
    pp = G.plan()["walk"]
    th_p = G.WALK_THETA
    pin_face = (L.TEETH["face"][0], -L.FLOOR_T - 0.4)
    pin = spur_gear(g_pin, pin_face[1] - pin_face[0]).moved(bd.Location((0, 0, pin_face[0])))
    pin = pin.rotate(bd.Axis.Z, mesh_rotation(g_ring, g_pin, th_p)) - parts.disc(5.0 + parts.FITS.press, 30, z0=-20)
    a.add("walk_pinion_16", at(pin, pp), group="drive", note="pressed on the top of the walk shaft: turns the ring")
    data["walk"] = {"pinion_xy": [round(v, 2) for v in pp], "ring_speed_deg_s": L.RING_SPEED, **L.walk_timing(),
                    "travel_limits": {k: round(v, 3) for k, v in G.ring_travel_limits().items()},
                    "timing": {k: round(v, 2) for k, v in G.timing().items()}}

    # ------------------------------------------------------------------ part 2a: stops, walk drive, state module
    k_sel = 0                                         # 12:10: the age cam selects the child
    adds, cuts = [], []
    d_stops, ad, cu = D.add_stops(a, MODEL_THETA, k_sel, MODEL_TIME[1])
    adds += ad; cuts += cu
    d_walk, ad, cu = D.add_walk_drive(a, MODEL_THETA)
    adds += ad; cuts += cu
    sb = G.plan()["bell_shaft"]
    d_state, ad, cu = D.add_state_module(a, MODEL_TIME[1], MODEL_TIME[0] + MODEL_TIME[1] / 60.0, sb[1], sb[0])
    adds += ad; cuts += cu
    data["stops"], data["drive"], data["state"] = d_stops, d_walk, d_state
    data["strike"] = K.add_strike_trains(a, MODEL_TIME[1], MODEL_TIME[0] + MODEL_TIME[1] / 60.0)
    for s_ in adds:
        deck = deck + s_
    for c_ in cuts:
        deck = deck - c_
    a.add("deck", deck, material="PETG", group="hall", note="the module's deck: rollers, posts, stops and drives "
          "stand on it; the state module hangs under it")
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
    a.render(out / "e2_front.png", elev=12, azim=-90, title="E2: the hall from the front (rest, 12:10)",
             tolerance=0.3, size=(9, 7))
    a.render(out / "e2_plan.png", elev=89, azim=-90, title="E2: plan (floors and deck hidden: the ring, the stops, the drives)",
             hide=("figures", "hall"), tolerance=0.3, size=(8, 9))
    a.render(out / "e2_three_quarter.png", elev=22, azim=-60, title="E2: three-quarter (hall hidden)",
             hide=("hall",), tolerance=0.3, size=(9, 8))
    a.render(out / "e2_drives.png", elev=18, azim=-62, title="E2 part 2a: the stops, the walk drive and the state "
             "module (hall, ring and figures hidden)", hide=("hall", "ring", "figures"), tolerance=0.2, size=(10, 8))
    a.render(out / "e2_stops.png", elev=28, azim=-48, title="E2 part 2a: the stops and the walk drive (state module, "
             "hall, ring and figures hidden; rest state B)", hide=("hall", "ring", "figures", "state"), tolerance=0.15,
             size=(10, 8))


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
