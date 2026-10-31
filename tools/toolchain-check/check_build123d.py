#!/usr/bin/env python3
"""Toolchain smoke test for the recommended CAD stack (build123d + bd_warehouse + trimesh + pycollada).

What it proves (headless, no GUI):
  1. a parametric involute gear pair can be generated (module, tooth counts are parameters);
  2. an exact B-rep interference check works (intersection volume of two parts);
  3. STL, 3MF (Bambu Studio) and STEP export work;
  4. a COLLADA .dae with named nodes in millimetres can be written for SketchUp.

Setup (Python 3.11-3.14; macOS arm64 and Linux x86_64 wheels exist on PyPI):
  python3 -m venv .venv && .venv/bin/pip install build123d bd_warehouse trimesh pycollada
Run:
  .venv/bin/python tools/toolchain-check/check_build123d.py [outdir]
"""
import sys
import time
from pathlib import Path

import numpy as np

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "export/toolchain-check")
OUT.mkdir(parents=True, exist_ok=True)

MODULE = 1.0      # parameter, never hard-coded in real parts
BACKLASH = 0.15   # mm; here applied as extra centre distance (bd_warehouse has no backlash arg)
Z1, Z2, FACE = 60, 15, 5.0

t0 = time.time()
from build123d import Compound, Cylinder, Mesher, Pos, export_step, export_stl  # noqa: E402
from bd_warehouse.gear import SpurGear  # noqa: E402

print(f"import build123d: {time.time() - t0:.1f} s")

t = time.time()
wheel = SpurGear(module=MODULE, tooth_count=Z1, pressure_angle=20, root_fillet=0.2, thickness=FACE)
pinion = SpurGear(module=MODULE, tooth_count=Z2, pressure_angle=20, root_fillet=0.2, thickness=FACE)
wheel = wheel - Cylinder(2.5, 3 * FACE)
centre = MODULE * (Z1 + Z2) / 2 + BACKLASH
pinion = Pos(centre, 0, 0) * (pinion - Cylinder(1.5, 3 * FACE))
print(f"gear pair z={Z1}/{Z2} m={MODULE}: {time.time() - t:.1f} s")

common = wheel & pinion
inter = common.volume if common else 0.0
print(f"interference volume: {inter:.4f} mm^3 ({'OK' if inter < 1e-6 else 'INTERFERENCE'})")

export_stl(wheel, str(OUT / "wheel.stl"))
export_stl(pinion, str(OUT / "pinion.stl"))
mesher = Mesher()
mesher.add_shape(wheel, part_number="wheel")
mesher.add_shape(pinion, part_number="pinion")
mesher.write(str(OUT / "pair.3mf"))
export_step(Compound([wheel, pinion]), str(OUT / "pair.step"))

# COLLADA with named nodes, millimetre units, Z up (SketchUp import)
import trimesh  # noqa: E402
from collada import Collada, asset, geometry, material, scene, source  # noqa: E402

dae = Collada()
dae.assetInfo.unitname, dae.assetInfo.unitmeter = "millimeter", 0.001
dae.assetInfo.upaxis = asset.UP_AXIS.Z_UP
eff = material.Effect("eff0", [], "phong", diffuse=(0.85, 0.7, 0.2))
mat = material.Material("mat0", "brass", eff)
dae.effects.append(eff)
dae.materials.append(mat)
nodes = []
for name in ("wheel", "pinion"):
    m = trimesh.load(OUT / f"{name}.stl")
    m.merge_vertices()
    assert m.is_watertight, name
    v = source.FloatSource(f"{name}-v", np.asarray(m.vertices, float).ravel(), ("X", "Y", "Z"))
    n = source.FloatSource(f"{name}-n", np.asarray(m.vertex_normals, float).ravel(), ("X", "Y", "Z"))
    g = geometry.Geometry(dae, f"{name}-geom", name, [v, n])
    il = source.InputList()
    il.addInput(0, "VERTEX", f"#{name}-v")
    il.addInput(0, "NORMAL", f"#{name}-n")
    g.primitives.append(g.createTriangleSet(np.asarray(m.faces).ravel(), il, "mat0"))
    dae.geometries.append(g)
    nodes.append(scene.Node(name, children=[scene.GeometryNode(g, [scene.MaterialNode("mat0", mat, inputs=[])])]))
dae.scenes.append(scene.Scene("scene", nodes))
dae.scene = dae.scenes[0]
dae.write(str(OUT / "pair.dae"))
print("DAE nodes:", [nd.id for nd in Collada(str(OUT / "pair.dae")).scenes[0].nodes])
print(f"wrote {sorted(p.name for p in OUT.iterdir())} in {time.time() - t0:.1f} s total")
