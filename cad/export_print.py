"""Print files for every printed part, ready for Bambu Studio.

Paul, PR #5: "All 3d printer parts should include either a 3mf file or an STL file that can be
imported into BambuStudio." Output, per model, in export/print/<model>/:

- ``<part>.stl``: one per distinct single-colour printed part, in its print pose (the assembly direction in
  ``Item.print_up`` faces up), centred on the origin and standing on z = 0, so it drops straight
  onto the plate. Identical parts (same volume, surface area, height and material) are written once
  and counted.
- ``<set>.3mf``: the bodies of one multi-colour print (``Item.print_set``) in register, and only
  there (no separate STLs, which would duplicate them). In Bambu
  Studio, open it, answer "Yes" to loading it as one object with several parts, then give each part
  its filament.
- ``README.md``: the manifest. It lists quantity, material, nozzle, size on the bed, the fit on the
  H2D, overhang area and notes.

These are design-stage files: the press, slide and bearing fits (``cad/lib/parts.FITS``) and the
minimum module are still waiting for the tolerance coupons, so print the coupons first and
regenerate after ``FITS`` is updated.

    python -m cad.export_print [out_dir]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from cad.lib.assembly import BED_DUAL, BED_SINGLE, overhang_area, print_pose

STL_TOLERANCE = 0.02          # mm chord error: far below what a 0.2 mm nozzle resolves
STL_ANGULAR = 0.3             # rad


def _models():
    from cad.modules.e2_ages import mechanism as e2
    from cad.modules.m1_time import mechanism as m1
    from cad.modules.m2_main_dial import e6
    from cad.modules.m2_main_dial import full as m2_full
    from cad.modules.m7_weekdays import mechanism as m7
    from cad.modules.test_rig import coupons, rig
    return {
        "tolerance_coupons": lambda: coupons.build(),
        "test_rig": lambda: rig.build()[0],
        "m1_time": lambda: m1.build()[0],
        "e2_ages": lambda: e2.build()[0],
        "m2_main_dial": lambda: m2_full.build()[0],
        "m2_e6_fallback_pawl": lambda: e6.fallback_assembly(),    # Paul: keep design A (crank and pawl)
        "m7_weekdays": lambda: m7.build()[0],
    }


def mesh_ok(shape) -> bool:
    """True if the part meshes as a closed, manifold, oriented mesh (lib3mf's check, as Bambu Studio
    expects); STL export alone never checks this."""
    import build123d as bd
    try:
        bd.Mesher().add_shape(shape, linear_deflection=STL_TOLERANCE, angular_deflection=STL_ANGULAR)
        return True
    except RuntimeError:
        return False


def _fits(size, bed) -> bool:
    x, y, z = size
    return z <= bed[2] and ((x <= bed[0] and y <= bed[1]) or (y <= bed[0] and x <= bed[1]))


def _same(a: dict, b: dict) -> bool:
    return (a["material"] == b["material"] and a["nozzle"] == b["nozzle"] and not a["set"] and not b["set"]
            and abs(a["volume"] - b["volume"]) <= 5e-4 * max(a["volume"], 1.0)
            and abs(a["area"] - b["area"]) <= 5e-4 * max(a["area"], 1.0)
            and abs(a["size"][2] - b["size"][2]) <= 0.01)


def export_model(name: str, asm, out_dir: Path) -> dict:
    import build123d as bd
    out = Path(out_dir) / name
    out.mkdir(parents=True, exist_ok=True)
    for old in list(out.glob("*.stl")) + list(out.glob("*.3mf")):
        old.unlink()
    items = [i for i in asm.items if i.printed]
    posed = {}
    set_overhang = {}
    for s in sorted({i.print_set for i in items if i.print_set}):          # multi-body prints, posed together
        members = [i for i in items if i.print_set == s]
        fill = next((m.filled for m in members if m.filled is not None), None)
        shapes = print_pose([m.shape for m in members] + ([fill] if fill is not None else []), members[0].print_up)
        for i, shp in zip(members, shapes):
            posed[i.name] = shp
        if fill is not None:                       # the bodies support each other: check the whole print
            union = shapes[-1]
        else:
            union = shapes[0]
            for b in shapes[1:len(members)]:
                union = union + b
        set_overhang[s] = overhang_area(union)
    for i in items:
        if i.name in posed:
            continue
        if i.print_up is not None:
            posed[i.name] = print_pose([i.shape], i.print_up)[0]
        else:                                     # +Z or -Z up, whichever leaves less to support
            up, down = print_pose([i.shape], (0, 0, 1))[0], print_pose([i.shape], (0, 0, -1))[0]
            posed[i.name] = down if overhang_area(down) < overhang_area(up) - 1.0 else up
    rows = []
    for i in items:
        shp = posed[i.name]
        bb = shp.bounding_box()
        row = {"names": [i.name], "material": i.material, "nozzle": i.nozzle, "set": i.print_set,
               "volume": shp.volume, "area": shp.area, "size": (bb.size.X, bb.size.Y, bb.size.Z),
               "note": i.note, "shape": shp}
        twin = next((r for r in rows if _same(r, row)), None)
        if twin:
            twin["names"].append(i.name)
        else:
            rows.append(row)
    for r in rows:
        if r["set"]:                                # a multi-colour body ships inside its set's 3MF only
            r["file"] = f"{r['set']}.3mf"
        else:
            r["file"] = f"{r['names'][0]}.stl"
            bd.export_stl(r["shape"], str(out / r["file"]), tolerance=STL_TOLERANCE, angular_tolerance=STL_ANGULAR)
        r["overhang_mm2"] = round(set_overhang[r["set"]] if r["set"] else overhang_area(r["shape"]), 0)
        r["fits_single"] = _fits(r["size"], BED_SINGLE)
        r["fits_dual"] = _fits(r["size"], BED_DUAL)
        r["mesh_ok"] = mesh_ok(r["shape"])
    sets = {}
    for s in sorted({r["set"] for r in rows if r["set"]}):
        mesher = bd.Mesher()
        for r in rows:
            if r["set"] == s:
                mesher.add_shape(r["shape"], linear_deflection=STL_TOLERANCE, angular_deflection=STL_ANGULAR,
                                 part_number=r["names"][0])
        mesher.write(str(out / f"{s}.3mf"))
        sets[s] = [r["names"][0] for r in rows if r["set"] == s]
    manifest = {
        "model": name,
        "unique_parts": len(rows),
        "printed_parts": sum(len(r["names"]) for r in rows),
        "sets": sets,
        "parts": [{k: (round(v, 1) if isinstance(v, float) else
                       [round(e, 1) for e in v] if k == "size" else v)
                   for k, v in r.items() if k not in ("shape", "volume", "area")} for r in rows],
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1))
    (out / "README.md").write_text(_readme(name, manifest))
    return manifest


def _readme(name: str, m: dict) -> str:
    lines = [
        f"# Print files: {name}",
        "",
        "Generated by `python -m cad.export_print`; do not edit by hand.",
        "",
        f"{m['unique_parts']} distinct parts, {m['printed_parts']} prints in all. Each STL is already in its print "
        "pose, centred and standing on the bed (z = 0): drag it into Bambu Studio and it lands on the plate.",
        "",
        "- **Down-facing** is the area (mm²) facing down more steeply than 45° and not on the bed: overhangs "
        "*and* bridges. Under about 100 mm² it is bridged holes, seats and slots that print without support; "
        "larger values are explained in the notes. Each part is posed to keep it small.",
        "- **Fit** is checked against the H2D build volume, single nozzle (325 × 320 × 325) and dual nozzle "
        "(300 × 320 × 325).",
        "- **Nozzle 0.2** marks parts with module 0.8 teeth or 2 mm lettering.",
        "- **Mesh** is lib3mf's check that the part meshes closed and manifold, as Bambu Studio expects.",
        "- **Fits not final.** The press, slide and bearing fits wait for the tolerance coupons, so print "
        "`tolerance_coupons` first and regenerate after `FITS` is updated.",
        "",
    ]
    for s, members in m["sets"].items():
        lines += [f"**Multi-colour print `{s}.3mf`**: {', '.join(members)}. Open it, answer *Yes* to loading it as "
                  "one object with several parts, then give each part its filament.", ""]
    lines += ["| File | Qty | Also used as | Material | Nozzle | Size on bed (mm) | Fits | Down-facing (mm²) | Mesh | Notes |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    for p in m["parts"]:
        x, y, z = p["size"]
        fit = "both" if p["fits_dual"] else ("single only" if p["fits_single"] else "**no**")
        also = ", ".join(p["names"][1:]) or "—"
        lines.append(f"| `{p['file']}` | {len(p['names'])} | {also} | {p['material']} | {p['nozzle']} | "
                     f"{x:.0f} × {y:.0f} × {z:.1f} | {fit} | {p['overhang_mm2']:.0f} | "
                     f"{'ok' if p.get('mesh_ok', True) else '**bad**'} | {p['note'] or ''} |")
    return "\n".join(lines) + "\n"


def main(out_dir: str = "export/print", only: str | None = None) -> dict:
    res = {}
    for name, make in _models().items():
        if only and name != only:
            continue
        m = export_model(name, make(), Path(out_dir))
        size = sum(f.stat().st_size for f in (Path(out_dir) / name).iterdir()) / 1e6
        bad = [p["file"] for p in m["parts"] if not p["mesh_ok"]]
        print(f"{name}: {m['unique_parts']} files for {m['printed_parts']} prints, {size:.1f} MB"
              + (f"; MESH NOT MANIFOLD: {bad}" if bad else ""))
        res[name] = m
    return res


if __name__ == "__main__":
    main(*sys.argv[1:])
