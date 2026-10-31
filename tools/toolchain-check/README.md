# Toolchain check (Phase 0)

Smoke tests that prove a CAD stack installs and runs headlessly, so a cloud agent can generate and
check geometry without a GUI. Decision record: `docs/decisions.md` → D1.

| Script | Stack |
|---|---|
| `check_build123d.py` | build123d + bd_warehouse + trimesh + pycollada (recommended) |
| `check_openscad.scad` | OpenSCAD + BOSL2 (alternative) |

## Results in the cloud container (31 Oct 2026)

Environment: Ubuntu 24.04, Python 3.13, 4 vCPU. Packages from PyPI and the Ubuntu archive. BOSL2
cloned from GitHub (commit `e3d614a`, 30 Oct 2026).

| Test | OpenSCAD 2021.01 + BOSL2 | build123d 0.13.0 + bd_warehouse 0.4.0 (OCP 8.0.1) | CadQuery 2.8.0 (OCP 7.9.3) |
|---|---|---|---|
| Installs headless | yes (`apt install openscad`) | yes (`pip`, wheels only) | yes (`pip`) |
| Gear pair 60/15, m 1.0: generate + export | 7.8 s (CGAL) | 1.6 s | not tested: core CadQuery has no involute gear; `cq_gears` is not on PyPI |
| 269-tooth wheel (m 0.8) with 6 holes | 16 s | 27 s | — |
| STL export | yes | yes | yes |
| 3MF export | yes | yes (`Mesher`, several named parts) | single shape only; `Assembly.export` rejected `.3mf` |
| STEP export | no | yes | yes |
| Exact interference volume | no (mesh only) | yes: 0.0000 mm³ at the correct centre distance, 19.78 mm³ when 1 mm short | yes (same OCC kernel) |
| Headless PNG render | yes (`xvfb-run`, 13 s) | not tested here (needs a renderer, e.g. trimesh + pyrender, or a VTK build) | — |
| `.dae` with named nodes (trimesh + pycollada 0.9.3) | via STL | yes: nodes `wheel`, `pinion`, millimetres, Z up | via STL |
| Built-in gear backlash parameter | yes (`backlash=`) | no: we write our own involute generator in `cad/lib` (Phase 2) | no |

Notes:

- CadQuery and build123d pull different OCP builds (`cadquery-ocp` 7.9 vs `cadquery-ocp-novtk` 8.0).
  Installed into one venv they conflict: `ImportError: TColgp_HArray1OfPnt`. Use one or the
  other, never both in one environment.
- PyPI ships `cadquery-ocp-novtk` 8.0.1 wheels for macOS 11+ arm64 (Python 3.11–3.14), so the same
  stack installs on Paul's Apple Silicon Mac. Checked on pypi.org, 31 Oct 2026.
- trimesh 5.2 has no scene-level `.dae` export. `check_build123d.py` writes the COLLADA with
  pycollada directly, as Paul's existing pipeline does.
- The Ubuntu OpenSCAD 2021.01 uses the slow CGAL kernel. The OpenSCAD development snapshots add
  the much faster Manifold backend. The snapshot download host was blocked in this session, so it
  is untested here.

## Run

```bash
python3 -m venv .venv && .venv/bin/pip install build123d bd_warehouse trimesh pycollada
```

```bash
.venv/bin/python tools/toolchain-check/check_build123d.py export/toolchain-check
```

The outputs (`wheel.stl`, `pinion.stl`, `pair.3mf`, `pair.step`, `pair.dae`) are throwaway. Do
not commit them.
