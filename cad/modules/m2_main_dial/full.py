"""The whole M2 module: mechanism + calendar ring + two-colour dial, checked together.

    python -m cad.modules.m2_main_dial.full [out_dir]

Writes ``m2.json`` (all checks), renders and ``m2_main_dial.dae`` (SketchUp).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import build123d as bd

from cad.lib import parts
from cad.lib.assembly import BED_DUAL, BED_SINGLE, Assembly, write_dae
from cad.modules.m2_main_dial import calendar as CAL
from cad.modules.m2_main_dial import dial as DIAL
from cad.modules.m2_main_dial import mechanism as MECH

READERS = {"stop_lever", "witness_opto_1_March", "counting_lever_pin", "setter_reset_ramp", "setter_set_ramp",
           "e6_pinion", "e6_pawl", "ring_jumper"}          # fixed parts that reach the ring on purpose


def build():
    mech, rep = MECH.build()
    cal, cinfo = CAL.build()
    field, hour_ring = DIAL.build()
    a = Assembly("m2_main_dial")
    for it in mech.items:
        if it.name == "dial_field":
            continue
        a.items.append(it)
    a.contact_ok |= {p for p in mech.contact_ok if "dial_field" not in p}
    a.add("dial_field", field, material="dial", group="front", print_up=(0, 0, -1), print_set="dial", nozzle=0.2,
          note="two-colour print, body 1 (azure); face down")
    a.add("dial_hour_ring", hour_ring, material="silver", group="front", print_up=(0, 0, -1), print_set="dial",
          nozzle=0.2, note="two-colour print, body 2 (silver); face down")
    a.allow("dial_field", "dial_hour_ring")
    for it in mech.items:                        # whatever passed through the old placeholder passes here
        if frozenset((it.name, "dial_field")) in mech.contact_ok:
            a.allow(it.name, "dial_field")
    for it in cal.items:
        a.items.append(it)
    a.contact_ok |= cal.contact_ok
    # dial feet: from the front plate to the back of the dial, clear of the stack, rollers and carrier
    for k, ang in enumerate((90.0, 210.0, 330.0)):
        p = (112.0 * math.cos(math.radians(ang)), 112.0 * math.sin(math.radians(ang)))
        a.add(f"dial_foot_{k}", parts.standoff(MECH.FP[1] * -1 - 3.0, od=7.0, z0=MECH.FP[1]).moved(
            bd.Location((p[0], p[1], 0))), material="PETG", group="plates")
        a.allow(f"dial_foot_{k}", "dial_field")
        a.allow(f"dial_foot_{k}", "front_plate")
    for k in range(4):                           # the carrier sits on the front plate where they overlap
        a.allow(f"carrier_segment_{k}", "front_plate")
    a.allow("wheel_C_arbor", "front_plate")      # wheel C's arbor is a stud pressed into the M2 front plate
    for nm in ("counting_lever_stud", "counting_lever_stop", "counting_lever_spring_anchor"):
        a.allow(nm, "front_plate")                # studs and pins pressed into the M2 front plate
    return a, rep, cinfo


def ring_sweep_conflicts(a: Assembly) -> list:
    """Fixed parts inside the volume the turning ring sweeps (other than its designed readers)."""
    sweep = parts.disc(2 * (CAL.R_OUT + 1.5), 8.6 + 0.1, bore=2 * (CAL.SKIRT[0] - 0.3), z0=CAL.BAND[2] - 0.3)
    ring_names = {i.name for i in a.items if i.group == "ring"} | {f"roller_{k}" for k in range(6)} | READERS
    out = []
    for it in a.items:
        if it.name in ring_names or it.name.startswith(("dial_", "roller_stud")):
            continue
        bb = it.shape.bounding_box()
        if bb.max.Z < CAL.BAND[2] - 0.3 or bb.min.Z > 0.1:
            continue
        v = (it.shape & sweep).volume
        if v > 1e-3:
            out.append({"part": it.name, "volume_mm3": round(v, 2)})
    return out


def check(a: Assembly, rep: dict, cinfo: dict) -> dict:
    env = a.envelope()
    return {
        "interference": [{"a": x, "b": y, "volume_mm3": round(v, 3)} for x, y, v in a.interference()],
        "ring_sweep_conflicts": ring_sweep_conflicts(a),
        "bed_fit_single": [r for r in a.bed_fit(BED_SINGLE) if not r["fits"]],
        "bed_fit_dual": [r for r in a.bed_fit(BED_DUAL) if not r["fits"]],
        "envelope": {"x": [round(env.min.X, 1), round(env.max.X, 1)], "y": [round(env.min.Y, 1), round(env.max.Y, 1)],
                     "z": [round(env.min.Z, 1), round(env.max.Z, 1)]},
        "parts": len(a.items),
        "printed": len([i for i in a.items if i.printed]),
        "bought": len([i for i in a.items if not i.printed and i.group != "v15"]),
        "mechanism": rep,
        "calendar": cinfo,
    }


def renders(a: Assembly, out: Path):
    out.mkdir(parents=True, exist_ok=True)
    a.render(out / "m2_front.png", elev=0, azim=-90, up="y", title="M2 main dial, front", hide=("v15",),
             tolerance=0.3)
    a.render(out / "m2_three_quarter.png", elev=16, azim=-120, up="y", title="M2, three-quarter from the front",
             hide=("v15",), tolerance=0.3)
    a.render(out / "m2_rear.png", elev=16, azim=60, up="y",
             title="M2, rear three-quarter (plates, carrier and dial hidden)",
             hide=("plates", "front", "v15", "carrier"), tolerance=0.3)
    detail = Assembly("detail")
    for it in a.items:
        if it.group in ("differentials", "interfaces"):
            detail.items.append(it)
    detail.render(out / "m2_differentials.png", elev=20, azim=-130, up="y",
                  title="Sun (left) and Moon (right) differentials with their 60:1 worms", tolerance=0.15)
    station = Assembly("station")
    for it in a.items:
        if it.group in ("station", "pointer") or it.name.startswith("ring_segment_2"):
            station.items.append(it)
    station.render(out / "m2_calendar_station.png", elev=-25, azim=-70, up="y",
                   title="Calendar New Year station (behind the ring, 6 o'clock)", tolerance=0.15)


def main(out_dir="export/m2_main_dial"):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    a, rep, cinfo = build()
    res = check(a, rep, cinfo)
    (out / "m2.json").write_text(json.dumps(res, indent=2, default=str))
    print(json.dumps({k: res[k] for k in ("interference", "ring_sweep_conflicts", "bed_fit_single", "envelope",
                                          "parts", "printed", "bought")}, indent=2))
    renders(a, out)
    write_dae(a, out / "m2_main_dial.dae")
    return a, res


if __name__ == "__main__":
    main(*sys.argv[1:])
