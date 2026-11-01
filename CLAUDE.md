# Strasbourg Astronomical Clock — 1:8 Hybrid Replica

Standing context for every Claude Code session on this repo (cloud and local). Read this file and
`docs/reference-notes.md` before doing anything else.

## What this is

Paul's project to build a working 1:8 scale replica of Jean-Baptiste Schwilgué's astronomical clock
(built 1838–1843) in Strasbourg Cathedral. It will hang as wall art on a fully enclosed, heated and
air-conditioned terrasse in his house in Bordeaux.

Target envelope at 1:8: about **2.25 m tall × 0.96 m wide** (original case: 18 m tall, 7.70 m wide
at the base). Depth is not yet known — see the open items in `docs/reference-notes.md`.

## Core design rules (do not relax without Paul's approval)

1. **Hybrid build.** Do as much as possible with 3D-printed gears, cams, differentials and
   linkages. Metal rods, tubes, bearings, screws and springs are allowed wherever strength or
   precision needs them. No cast or machined metal gears.
2. **Steppers replace the weights and pendulum — nothing more.** A stepper may only output a
   plain "clockwork" rate derived from the time base (for example one turn per hour or one turn
   per mean solar day). Every astronomical or calendar ratio — year, months, planets, sidereal day,
   precession, solar and lunar equations, eclipses, calendar, computus — must be produced
   mechanically by gears, cams or differentials.
3. **One stepper per module is fine**, as long as all of them are driven from the same time base.
   In normal running, steppers turn forward only (this keeps gear backlash taken up in one
   direction).
4. **Automata are events.** A cam or count wheel on the time train decides *when* a show happens
   (it closes a switch or trips a lever); a small dedicated motor per show supplies the energy,
   like a traditional striking train. Event motors may run at any speed.
5. **Accuracy split.** Timekeeping accuracy comes from the controller (RTC + NTP). Gear accuracy
   means ratio fidelity. Every gear train must report its ratio error.

## Hard constraints

- **Scale 1:8.** Main (apparent-time) dial ≈ 287.5 mm diameter; Apostle figures ≈ 57 mm tall.
- **Printer: Bambu Lab H2D.** Build volume 325 × 320 × 325 mm single-nozzle, 300 × 320 × 325 mm
  dual-nozzle. Nozzles 0.2 / 0.4 / 0.6 / 0.8 mm supported; 0.4 mm installed, 0.2 mm to be bought.
- **Gear module is a parameter, never hard-coded.** Working defaults: module 1.0 with the 0.4 mm
  nozzle, 0.8 with the 0.2 mm nozzle. The real minimum will be set later by a physical tolerance
  test (local phase).
- **Backlash allowance is a parameter**, default 0.15 mm.
- **Materials:** PLA by default for gears and display parts; PETG for structural or clamped parts;
  nylon optional for the fastest, highest-wear gears near the motors. The room is climate
  controlled, so no UV or weather design is needed. Plan a glazed front to keep dust out.
- **Wood (fine woodworking) for the case and frame.** Sheet goods (birch plywood, MDF) and
  hardwood are both acceptable (Paul, 1 Nov 2026). 3D printing stays for the internal mechanism
  and for selected visible parts such as ornament and figures. The wood holds the modules but
  never sets gear geometry; see `docs/decisions.md` D12.
  - Finish: painted to resemble the original.
  - Species: one species from a single movement class (D12 R3).
  - **Metal frame elements are hidden where possible**; the exception is the computus (Easter
    calculator), which gets a visible metal frame.
- **Hardware must be sourceable in France/EU in metric sizes** (rods, tubes, bearings, fasteners,
  springs). Avoid US-only parts and imperial sizes.
- **Units: millimetres.**

## How Paul works — follow this

- **Do not guess.** If a fact is not in `docs/reference-notes.md` or a source you can cite,
  research it. If it is still unknown, say so, mark it TBD, and propose how to resolve it.
- Every number written into the docs must be one of: **sourced** (with link), **derived** (show the
  calculation), or **estimate** (state the method and the uncertainty).
- **Iterative and gated.** Discuss and confirm decisions before heavy modelling or coding. Present
  options with trade-offs and a recommendation, then wait for approval at each phase gate.
- Paul checks figures against primary sources himself; make that easy with links and calculations.
- **Serviceability matters:** removable modules, wiring channels, access to motors and boards.
- **Consolidate purchases:** keep one running hardware list so parts can be ordered in as few
  batches as possible.
- Cloud credits are limited. Prefer work that needs no physical hardware, avoid long render loops,
  and keep each session focused on its phase.

## Workflow

- GitHub PR-based. One feature branch per phase or module. Each PR has a summary, what changed,
  open questions, and the decisions needed from Paul. Do not merge; Paul reviews, merges and pulls.
- **Cloud sessions:** research, specification, ratio engineering, parametric CAD (including the
  wooden case: joinery, cut lists, sheet layouts, templates), simulation, electronics architecture
  and firmware skeletons.
- **Local sessions (later):** anything that needs physical measurement — gear tolerance tests,
  print calibration, hardware bring-up, flashing, tuning, building the wooden case.
- CAD source is code (parametric). Generated exports go in `export/`. Don't commit large binaries
  except released STL/3MF files.

## Paul's tools and experience (for context)

- Mac (Apple Silicon). Bambu Studio for slicing.
- SketchUp Pro for viewing and arranging models; he has a Python trimesh/pycollada pipeline that
  exports COLLADA (.dae) with named nodes for SketchUp.
- OpenSCAD experience (a 3D-printed French word clock).
- Electronics: ESP32, Raspberry Pi, Arduino Mega + RAMPS 1.4 + TMC2209 stepper drivers, NEMA17
  steppers, Arduino IDE. Home Assistant and MQTT at home.
- Woodworking: fine woodworking for the case. Workshop: table saw, track saw, drill press,
  planer, drum sander, mitre saw, hand tools and chisels. **No router, jointer, bandsaw, CNC or
  lathe.** Design joinery and mouldings for these tools (D12 R1). Ornament and finials are
  3D-printed. Hardwood is sourced from local vendors in Bordeaux.

## Repo layout (refined in Phase 0; see README.md and docs/architecture.md §12)

```
CLAUDE.md
README.md               project overview
docs/                   reference-notes, spec, inventory, envelope, architecture, decisions, gear-trains
tools/ratios/           gear-ratio search tool + tests
spec/clock.yaml         single source of truth for rates, ratios, sensors (Phase 1)
cad/lib/                shared parametric parts (gears, arbors, bearing seats, tube stacks, cams)
cad/modules/<module>/   one folder per mechanism module
cad/case/               parametric wooden case: joinery, cut lists, sheet layouts
export/                 STL/3MF/DAE and renders
firmware/               controller code
sim/                    accelerated-time simulator and validation against an ephemeris
```

## Key references

- `docs/reference-notes.md` — every fact gathered so far, with sources and confidence. Start here.
- Primary sources read in Phase 0: Ch. Schwilgué, *Description abrégée* (1844, public domain), and
  A. Ungerer's 1920 lecture (*L'Astronomie* 1921; private copy, not in the repo).
- Primary technical books still to obtain: Ungerer & Ungerer (1922, later editions 1949/1954);
  Bach, Rieb & Wilhelm, *Les trois horloges astronomiques de la cathédrale de Strasbourg* (1992).
