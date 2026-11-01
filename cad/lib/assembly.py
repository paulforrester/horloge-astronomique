"""Assemblies of named parts, with the checks every module must report (Phase 2 brief).

- ``interference()``: exact B-rep intersection volume for every pair of parts whose bounding boxes
  overlap, minus pairs declared as intended contact (e.g. a tube pressed into a hub).
- ``bed_fit()``: each printed part against the Bambu Lab H2D build volume (CLAUDE.md).
- ``export()``: STL per printed part, 3MF, STEP and a COLLADA ``.dae`` with named nodes for
  SketchUp (Paul's pipeline: millimetres, Z up).
- ``render()``: assembly and exploded PNG views (matplotlib, headless).
"""
from __future__ import annotations

import itertools
import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

# Bambu Lab H2D build volume (CLAUDE.md): single nozzle 325 x 320 x 325, dual 300 x 320 x 325
BED_SINGLE = (325.0, 320.0, 325.0)
BED_DUAL = (300.0, 320.0, 325.0)

PALETTE = {
    "PLA": (0.92, 0.80, 0.35), "PETG": (0.55, 0.75, 0.90), "brass": (0.80, 0.62, 0.20),
    "steel": (0.62, 0.64, 0.68), "bearing": (0.45, 0.47, 0.52), "dial": (0.25, 0.45, 0.80),
    "wood": (0.70, 0.52, 0.35), "black": (0.15, 0.15, 0.17), "silver": (0.85, 0.86, 0.88),
    "red": (0.85, 0.30, 0.25), "green": (0.40, 0.70, 0.40), "ghost": (0.80, 0.80, 0.85),
}


@dataclass
class Item:
    name: str
    shape: object                 # build123d Part / Solid / Compound, already located
    material: str = "PLA"         # PLA, PETG, brass, steel, bearing, ...
    printed: bool = True
    group: str = ""               # for exploded views and reports
    explode: tuple = (0.0, 0.0, 0.0)
    note: str = ""


@dataclass
class Assembly:
    name: str
    items: list = field(default_factory=list)
    contact_ok: set = field(default_factory=set)   # frozenset({a, b}) pairs allowed to touch/overlap

    def add(self, name, shape, **kw) -> Item:
        if any(i.name == name for i in self.items):
            raise ValueError(f"duplicate part name {name}")
        it = Item(name, shape, **kw)
        self.items.append(it)
        return it

    def allow(self, a: str, b: str):
        self.contact_ok.add(frozenset((a, b)))

    def __getitem__(self, name) -> Item:
        return next(i for i in self.items if i.name == name)

    # --- checks -------------------------------------------------------------------------------
    def interference(self, tol: float = 1e-3) -> list[tuple[str, str, float]]:
        """(a, b, volume mm³) for every pair that intersects by more than ``tol``."""
        out = []
        boxes = {i.name: i.shape.bounding_box() for i in self.items}
        for a, b in itertools.combinations(self.items, 2):
            if frozenset((a.name, b.name)) in self.contact_ok:
                continue
            ba, bb = boxes[a.name], boxes[b.name]
            if (ba.max.X < bb.min.X or bb.max.X < ba.min.X or ba.max.Y < bb.min.Y or bb.max.Y < ba.min.Y
                    or ba.max.Z < bb.min.Z or bb.max.Z < ba.min.Z):
                continue
            v = (a.shape & b.shape).volume
            if v > tol:
                out.append((a.name, b.name, v))
        return out

    def bed_fit(self, bed=BED_SINGLE) -> list[dict]:
        """Printed parts: extents as modelled (lay-flat orientation) against the bed."""
        rows = []
        for i in self.items:
            if not i.printed:
                continue
            bb = i.shape.bounding_box()
            ext = sorted([bb.size.X, bb.size.Y, bb.size.Z])
            fits = all(e <= d for e, d in zip(ext, sorted(bed)))
            rows.append({"part": i.name, "extents": tuple(round(e, 1) for e in
                                                          (bb.size.X, bb.size.Y, bb.size.Z)),
                         "fits": fits, "margin": round(min(d - e for e, d in zip(ext, sorted(bed))), 1)})
        return rows

    def envelope(self):
        import build123d as bd
        return bd.Compound([i.shape for i in self.items]).bounding_box()

    # --- export -------------------------------------------------------------------------------
    def export(self, out_dir: str | Path, stl: bool = True, step: bool = True, dae: bool = True,
               threemf: bool = True):
        import build123d as bd
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        if stl:
            for i in self.items:
                if i.printed:
                    bd.export_stl(i.shape, str(out / f"{i.name}.stl"))
        if threemf:
            mesher = bd.Mesher()
            for i in self.items:
                if i.printed:
                    mesher.add_shape(i.shape, part_number=i.name)
            mesher.write(str(out / f"{self.name}.3mf"))
        if step:
            bd.export_step(bd.Compound([i.shape for i in self.items]), str(out / f"{self.name}.step"))
        if dae:
            write_dae(self, out / f"{self.name}.dae")
        return out

    # --- render -------------------------------------------------------------------------------
    def render(self, path: str | Path, exploded: bool = False, elev: float = 22, azim: float = -58,
               tolerance: float = 0.25, title: str | None = None, hide: tuple = (), size=(9, 8),
               xlim=None, ylim=None, zlim=None, up: str = "z"):
        render(self, path, exploded=exploded, elev=elev, azim=azim, tolerance=tolerance,
               title=title, hide=hide, size=size, xlim=xlim, ylim=ylim, zlim=zlim, up=up)


def _mesh(shape, tolerance):
    verts, tris = shape.tessellate(tolerance, 0.5)
    v = np.array([(p.X, p.Y, p.Z) for p in verts], float)
    return v, np.array(tris, int)


def write_dae(asm: Assembly, path: Path):
    """COLLADA with one named node per part, millimetres, Z up (SketchUp import)."""
    from collada import Collada, asset, geometry, material, scene, source
    dae = Collada()
    dae.assetInfo.unitname, dae.assetInfo.unitmeter = "millimeter", 0.001
    dae.assetInfo.upaxis = asset.UP_AXIS.Z_UP
    mats = {}
    nodes = []
    for i in asm.items:
        if i.material not in mats:
            eff = material.Effect(f"eff-{i.material}", [], "phong", diffuse=PALETTE.get(i.material, (0.7,) * 3))
            mat = material.Material(f"mat-{i.material}", i.material, eff)
            dae.effects.append(eff)
            dae.materials.append(mat)
            mats[i.material] = mat
        v, t = _mesh(i.shape, 0.1)
        if not len(t):
            continue
        vs = source.FloatSource(f"{i.name}-v", v.ravel(), ("X", "Y", "Z"))
        g = geometry.Geometry(dae, f"{i.name}-geom", i.name, [vs])
        il = source.InputList()
        il.addInput(0, "VERTEX", f"#{i.name}-v")
        g.primitives.append(g.createTriangleSet(t.ravel(), il, f"mat-{i.material}"))
        dae.geometries.append(g)
        mat = mats[i.material]
        nodes.append(scene.Node(i.name, children=[scene.GeometryNode(g, [scene.MaterialNode(f"mat-{i.material}", mat, inputs=[])])]))
    dae.scenes.append(scene.Scene("scene", nodes))
    dae.scene = dae.scenes[0]
    dae.write(str(path))


def render(asm: Assembly, path, exploded=False, elev=22, azim=-58, tolerance=0.25, title=None,
           hide=(), size=(9, 8), xlim=None, ylim=None, zlim=None, up="z"):
    """PNG view. ``up="y"`` draws the model's +Y as the vertical (a wall-mounted dial standing up,
    +Z towards the viewer at azim = -90, elev = 0)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    fig = plt.figure(figsize=size, dpi=110)
    ax = fig.add_subplot(111, projection="3d")
    light = np.array([0.4, -0.5, 0.75])
    light /= np.linalg.norm(light)
    allv = []
    for i in asm.items:
        if i.name in hide or i.group in hide:
            continue
        v, t = _mesh(i.shape, tolerance)
        if not len(t):
            continue
        if exploded:
            v = v + np.array(i.explode, float)
        if up == "y":
            v = np.column_stack([v[:, 0], -v[:, 2], v[:, 1]])
        tri = v[t]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
        shade = 0.45 + 0.55 * np.abs(n @ light)
        base = np.array(PALETTE.get(i.material, (0.7, 0.7, 0.7)))
        cols = np.clip(base[None, :] * shade[:, None], 0, 1)
        pc = Poly3DCollection(tri, facecolors=cols, edgecolors="none", linewidths=0)
        ax.add_collection3d(pc)
        allv.append(v)
    V = np.vstack(allv)
    lo, hi = V.min(0), V.max(0)
    c, r = (lo + hi) / 2, (hi - lo).max() / 2
    ax.set_xlim(*(xlim or (c[0] - r, c[0] + r)))
    ax.set_ylim(*(ylim or (c[1] - r, c[1] + r)))
    ax.set_zlim(*(zlim or (c[2] - r, c[2] + r)))
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("depth, -z (mm)" if up == "y" else "y (mm)")
    ax.set_zlabel("y (mm)" if up == "y" else "z (mm)")
    ax.set_title(title or (asm.name + (" (exploded)" if exploded else "")))
    fig.tight_layout()
    fig.savefig(str(path))
    plt.close(fig)
