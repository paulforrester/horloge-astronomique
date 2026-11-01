# cad: parametric CAD (Phase 2)

All geometry is Python code on [build123d](https://github.com/gumyr/build123d) (decision D1). The
CAD has its own venv; never install it together with CadQuery (OCP conflict, D1).

```bash
python3 -m venv .venv-cad && .venv-cad/bin/pip install -r cad/requirements.txt
```

```bash
.venv-cad/bin/python -m pytest cad
```

```bash
.venv-cad/bin/python -m cad.modules.m2_main_dial.feasibility export/m2
```

## Library (`cad/lib`)

| Module | Contents |
|---|---|
| `gears.py` | Involute spur gears (20°, ISO 53 rack). **Backlash** is a parameter: the total gap of a mesh, applied as tooth thinning split between the mates (D4). **Profile shift**: `auto_shift` (no undercut) and `pair_shifts` (keeps the standard centre distance). Internal gears, racks, operating centre distance for shifted pairs, mesh phasing. Module is always a parameter. Flanks are B-splines (4 edges per tooth), so a 169-tooth wheel builds in about a second. |
| `hardware.py` | Bought parts from D4: Ø3/5/8 rods, 0.45 mm-wall brass tubes in 1 mm steps (`tube_stack` telescopes them with 0.10 mm clearance), the bearing set, M2–M5 screws and heat-set inserts. Nominal sizes until the parts are measured. |
| `parts.py` | Rods, tubes, bearings, hubs, gears on hubs, bearing-seat cuts, plates, discs, standoffs, hands, radial cams and cam pressure angle. Printed fits live in one place (`FITS`, [E] until the tolerance test). |
| `assembly.py` | Named-part assemblies with the checks every module must report: exact **interference** volumes (pairs declared as intended contact are skipped), **bed fit** against the H2D (single and dual nozzle), export to **STL / 3MF / STEP / DAE** (named nodes, mm, Z up, for SketchUp), and **PNG renders** (assembly and exploded). |

## Validation

- `cad/tests/test_gears.py`:
  - radii, shift rules, pitch thickness (includes half the backlash);
  - zero interference for conjugate meshes at several angles, and a clash when 0.5 mm short;
  - backlash equals the angular play;
  - internal gear and rack meshing.
- `cad/tests/test_gears_bosl2.py`: outlines against BOSL2 `spur_gear2d`, which D1 named as the
  reference.
  - Working flanks, undercut and tips agree to a mean deviation under 10 µm; area within 0.5 %.
  - BOSL2 rounds the root corner and ours is sharp; the nozzle rounds it anyway.
  - Needs `openscad` and `BOSL2_PARENT=<dir containing BOSL2>`; skipped otherwise.
- `cad/tests/test_parts_assembly.py`: tube stacks, bearings, cams, assembly checks, export, render.
- `cad/tests/test_m2_feasibility.py`: the main-dial layout's checks, plus Schwilgué's latitude-cam
  design point.
- `cad/tests/test_test_rig.py`: the rig's checks, every mesh engaged, the coupon matrix.
- `cad/tests/test_sketchup_export.py`: every model writes a `.dae` with named nodes.

## Modules (`cad/modules`)

| Module | Status |
|---|---|
| `m2_main_dial/feasibility.py` | Layout study, accepted: [`docs/main-dial-feasibility.md`](../docs/main-dial-feasibility.md) |
| `test_rig/rig.py`, `test_rig/coupons.py` | Test rig and tolerance coupons, proposed: [`docs/test-rig.md`](../docs/test-rig.md). `python -m cad.modules.test_rig.rig` writes the 3MF print files to `export/test_rig/` |

## SketchUp files

Paul asked for SketchUp files of every CAD model (PR #4).

```bash
.venv-cad/bin/python -m cad.export_sketchup
```

- It writes one COLLADA file per model to `export/sketchup/`: one named node per part, millimetres,
  Z up. In SketchUp, use File > Import > COLLADA (*.dae).
- Every new module is added to `MODELS` in `cad/export_sketchup.py`.
- The files are committed with each PR (`git add -f`).

| File | Contents |
|---|---|
| `export/sketchup/cad_lib_samples.dae` | Library showcase with real teeth: shifted 12/89 pair, 25/169 pair, internal 60/18, rack and pinion, cam, tube stack, bearings |
| `export/sketchup/m2_main_dial_feasibility.dae` | The main-dial layout model (gears as blanks) |
| `export/sketchup/test_rig.dae` | The test rig, real teeth |
| `export/sketchup/tolerance_coupons.dae` | Fit, bearing-seat and gear coupons |

Other generated files go to `export/` (git-ignored). Released STL/3MF are added deliberately.
