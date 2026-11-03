"""Write a SketchUp file (COLLADA .dae, named nodes, millimetres, Z up) for every CAD model.

Paul asked for SketchUp files of all CAD (PR #4), with exploded views where possible (PR #5).
Output: export/sketchup/<model>.dae and, for assemblies, <model>_exploded.dae, committed
deliberately (git add -f), like released STL/3MF. In SketchUp: File > Import > COLLADA (*.dae).
Import both into one SketchUp file to see the assembly beside its exploded view.

Parts with flush inlays (the calendar dates) are shown filled, without the inlay bodies: thousands
of 2 mm glyphs would triple the files for no gain at SketchUp's viewing scale. The dates are in the
print files and in ``docs/img/m2/calendar_dates.png``.

The exploded copies pull the parts apart along the arbor axis (``cad.lib.assembly.exploded``). The
coupons lift each gear off its board. ``cad_lib_samples`` is already laid out flat, part by part,
so it has no exploded copy.

    python -m cad.export_sketchup [out_dir]
"""
from __future__ import annotations

import sys
from pathlib import Path

from cad.lib import samples
from cad.lib.assembly import Assembly, Item, exploded, write_dae
from cad.modules.m2_main_dial import feasibility
from cad.modules.m2_main_dial import full as m2_full
from cad.modules.test_rig import coupons, rig

MODELS = {
    "cad_lib_samples": lambda: samples.build(),
    "m2_main_dial_feasibility": lambda: feasibility.build()[0],
    "m2_main_dial": lambda: m2_full.build()[0],
    "test_rig": lambda: rig.build()[0],
    "tolerance_coupons": lambda: coupons.build(),
}
TOLERANCE = {"m2_main_dial": 0.3}      # mm chord error; the whole module is large
_M2_MECH = ("centre", "centre_wheels", "trains", "shafts", "differentials", "interfaces", "drive", "sensors",
            "v15", "plates")
EXPLODE = {                             # model -> exploded() arguments (front of the clock is +Z)
    "m2_main_dial": dict(offsets={"hands": 120.0, "front": 70.0, "ring": 30.0, "pointer": 30.0,
                                  **{g: -40.0 for g in _M2_MECH}},
                         item_offsets={"hemisphere_dome": 170.0}, spread=1.2, spread_groups=_M2_MECH,
                         use_item_explode=False),
    "m2_main_dial_feasibility": dict(offsets={"hands": 60.0, "front": 30.0}, spread=1.2, use_item_explode=False),
    "test_rig": dict(offsets={"hands": 50.0, "front": 25.0}, spread=1.5, use_item_explode=False),
    "tolerance_coupons": dict(spread=0.0),     # gears lift off the board by their own explode vectors
}


def for_display(asm: Assembly) -> Assembly:
    """The assembly as SketchUp shows it: inlaid parts filled, inlay bodies left out."""
    out = Assembly(asm.name, contact_ok=set(asm.contact_ok))
    for i in asm.items:
        if i.inside:
            continue
        out.items.append(Item(i.name, i.filled if i.filled is not None else i.shape, i.material, i.printed, i.group,
                              i.explode, i.note, i.print_up, i.print_set, i.nozzle))
    return out


def main(out_dir: str = "export/sketchup") -> list[Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for name, make in MODELS.items():
        asm = for_display(make())
        versions = [(name, asm)]
        if name in EXPLODE:
            versions.append((f"{name}_exploded", exploded(asm, **EXPLODE[name])))
        for fname, model in versions:
            path = out / f"{fname}.dae"
            write_dae(model, path, tolerance=TOLERANCE.get(name, 0.1))
            written.append(path)
            print(f"{path}  {path.stat().st_size / 1e6:.2f} MB")
    return written


if __name__ == "__main__":
    main(*sys.argv[1:])
