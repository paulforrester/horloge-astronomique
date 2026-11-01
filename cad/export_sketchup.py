"""Write a SketchUp file (COLLADA .dae, named nodes, millimetres, Z up) for every CAD model.

Paul asked for SketchUp files of all CAD (PR #4). Output: export/sketchup/<model>.dae, committed
deliberately (git add -f), like released STL/3MF. In SketchUp: File > Import > COLLADA (*.dae).

    python -m cad.export_sketchup [out_dir]
"""
from __future__ import annotations

import sys
from pathlib import Path

from cad.lib import samples
from cad.lib.assembly import write_dae
from cad.modules.m2_main_dial import feasibility

MODELS = {
    "cad_lib_samples": lambda: samples.build(),
    "m2_main_dial_feasibility": lambda: feasibility.build()[0],
}


def main(out_dir: str = "export/sketchup") -> list[Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for name, make in MODELS.items():
        path = out / f"{name}.dae"
        write_dae(make(), path)
        written.append(path)
        print(f"{path}  {path.stat().st_size / 1e6:.2f} MB")
    return written


if __name__ == "__main__":
    main(*sys.argv[1:])
