# Decisions

Phase 0 deliverable. One record per decision Paul needs to make. Each record gives the options,
the trade-offs and a recommendation. Status is **Proposed** until Paul approves; then it becomes
**Accepted** with the date, and the record is kept, never deleted. Tags as in
`docs/reference-notes.md`.

## Summary

| ID | Decision | Recommendation | Needed before |
|---|---|---|---|
| D1 | CAD toolchain | **build123d** (Python, pinned), own gear library; OpenSCAD + BOSL2 as fallback | Phase 2 |
| D2 | Strasbourg-faithful vs Bordeaux-localized | **Time: Strasbourg (accepted, PR #1)**, so the noon show is at 12:29 CET / 13:29 CEST. Sky: **Strasbourg too** (awaiting Paul) | v1.5 (sky parts) |
| D3 | Controller, drivers, RTC, event motors | **ESP32-S3 + TMC2209 (UART)** for the clock *and* the test rig, all bought new; DC gearmotors for events | Phase 2 test rig / Phase 3 |
| D4 | Tooth profile, module, arbors, tubes, bearings | **Involute 20°**, module 1.0 / 0.8 as parameters; Ø3/5/8 ground rod; 0.45 mm-wall brass tubes in 1 mm steps; small standard bearing set | Phase 1 |
| D5 | Scope of v1 vs deferred | **v1** time, main dial (steady-speed Sun and Moon), calendar, planets, Moon globe, sidereal globe, all automata; **v1.5** equations, eclipses, sunrise/sunset; **v2** computus. The question is rephrased in the D5 record. | Phase 1 |
| D6 | Case construction and mounting | **Aluminium-extrusion module rack inside a birch-ply/MDF case**, printed ornament, hinged glazing; **floor-bearing plinth plus wall restraint** | Phase 2 |
| D7 | Computus: faithful vs own design | Defer to v2; gather sources; design our own if Schwilgué's stays undocumented | v2 |
| D8 | Sound | **Real small bells struck mechanically**; rooster crow through a small speaker in v1 | Phase 2 (E-modules) |
| D9 | Legal-time hands and summer time | **Separately driven legal-time hands that follow CET/CEST** (M1b) | Phase 2 (M1) |
| D10 | Night silence | **Quiet hours in firmware** (skip sound shows) | Phase 3 |
| D11 | Case width (7.70 vs 8.60 m) and wall space | **1:8 accepted (PR #1)**; width (962.5 or 1075 mm) follows the source; wall dimensions to follow from Paul | Phase 2 (case) |

Plus **Blockers** at the end: the network allowlist and the documents to obtain.

---

## D1 — CAD toolchain

**Context.** CAD must be code-based and parametric, run headless in the cloud, export STL/3MF for
Bambu Studio, and produce something SketchUp can open (Paul's trimesh/pycollada → `.dae`
pipeline). Each was verified in this environment on 31 Oct 2026; full results are in
`tools/toolchain-check/README.md`.

| Criterion | A. OpenSCAD + BOSL2 | B. CadQuery | C. build123d |
|---|---|---|---|
| Installs and runs headless here | ✔ apt 2021.01; BOSL2 via git | ✔ pip (CadQuery 2.8) | ✔ pip (0.13, OCP 8.0.1) |
| Installs on an Apple Silicon Mac | ✔ (official macOS builds) | probably: `cadquery-ocp` 8.0.1 has arm64 wheels, but the OCP version CadQuery 2.8 pins was not checked | ✔: `cadquery-ocp-novtk` arm64 wheels on PyPI for Python 3.11–3.14 (checked) |
| STL / 3MF | ✔ / ✔ | ✔ / single shape only | ✔ / ✔ (several named parts) |
| STEP (for CNC or laser-cut case parts, sharing) | ✘ | ✔ | ✔ |
| Exact interference check (rule: "report intersecting volumes") | mesh only | ✔ B-rep | ✔ B-rep: 0.0000 mm³ when correct, 19.78 mm³ when the centre distance is 1 mm short |
| `.dae` with named nodes | via STL + Python | ✔ Python | ✔ Python (verified) |
| Gear library | **BOSL2 gears: mature; backlash, profile shift, racks, worms, bevels, ring gears** | none in core (`cq_gears` is not on PyPI) | `bd_warehouse` spur gears, **no backlash parameter**, so we write our own |
| Speed (60/15 gear pair) | 7.8 s (CGAL) | — | 1.6 s |
| Speed (269 teeth + 6 holes) | 16 s | — | 27 s |
| Same language as the ratio tool, simulator and DAE pipeline | ✘ | ✔ | ✔ |
| Paul's experience | ✔ (word clock) | Python ✔ | Python ✔ |
| Maturity | stable but slow release cycle | stable | active; 0.x API still changes, so pin versions |

**Recommendation: C (build123d)**, pinned in `requirements.txt`, Python 3.12+.

- **Why.** One Python codebase reads `spec/clock.yaml`, generates the parts, runs the exact
  interference and bed-fit checks, and writes STL, 3MF, STEP and DAE. The ratio tool and simulator
  live in the same language.
- **The cost.** We write `cad/lib/gears.py`: involute with backlash as tooth thinning, profile
  shift, internal and rack forms; about a day's work in Phase 2. It is validated tooth-by-tooth
  against BOSL2's output, which is installed here for exactly that.
- **Never install CadQuery and build123d in the same environment.** Their OCP builds conflict
  (`ImportError: TColgp_HArray1OfPnt`, verified).
- **Fallback: A.** OpenSCAD + BOSL2 is the quickest route to good gears and Paul knows it. It loses
  STEP and exact interference volumes and splits the codebase in two languages.

---

## D2 — Strasbourg-faithful vs Bordeaux-localized

**Context.** The gear trains are identical either way. Localization changes only:

1. **The mean-time offset.** A firmware constant (the stepper phase). Strasbourg: LMT = UT +
   31.00 min, so mean noon is 12:29 CET. Bordeaux: UT − 2.28 min, so mean noon is 13:02 CET /
   14:02 CEST [D].
2. **When the automata run.** They follow mean time, so this follows (1). The original runs on
   Strasbourg mean time [Sn: CATH].
3. **The sunrise/sunset cam profile.** A printed part made from latitude φ: Strasbourg about
   48.58° N, Bordeaux 44.83° N.
4. **The celestial globe's horizon ring tilt.** A printed part, or an adjustable one.
5. **The legal-time offset.** Mean time to CET is 29.0 min for Strasbourg, 62.3 min for Bordeaux
   [D].

| Option | For | Against |
|---|---|---|
| A. Faithful Strasbourg | The famous "12:30" noon show; replica in the strict sense | Sunrise/sunset and globe are wrong for the room; the local sky is the point of the instrument |
| **B. Bordeaux-localized** | Shows the truth where it hangs. Precedent: R. B. Smith localized his 1:5 model to Sydney [S: WIKI, PH]. | Noon show at 13:02 CET / 14:02 CEST, not 12:30 |
| C. Mixed (Strasbourg times, Bordeaux sky) | — | Inconsistent; not recommended |

**Recommendation: B.**

- The dial lettering and appearance follow the original.
- Items 3 and 4 are swappable printed parts generated from φ, so a Strasbourg set can be printed
  later.
- Item 1 is a single firmware constant.

**Question for Paul:** is the 12:30-ish noon show important to you? If so, choose A for time and
consider B for the sky (which is C).

**Paul's input (PR #1 comment, 31 Oct 2026):** "The noon show is important."

Read as: keep the show at Strasbourg's time. **Items 1, 2 and 5 are therefore Strasbourg.**

- Mean time = UT + 31.00 min.
- Noon show at 12:29 CET / 13:29 CEST.
- Legal-time offset 29.0 min [D].

**Revised recommendation for items 3 and 4: A (fully Strasbourg).** Once the dials run on
Strasbourg mean time, sunrise/sunset times and a globe horizon for Bordeaux on those dials would be
a mixture (option C). That is harder to read and to validate.

- Both parts stay swappable printed parts generated from φ.
- Status: **Accepted for items 1, 2 and 5. Items 3 and 4 await Paul's confirmation of A**; they
  are not needed before v1.5.

---

## D3 — Controller platform, stepper drivers, RTC, event motors

**Context.**

- 4 steppers in v1, up to 6 later (architecture §3).
- 5–6 one-direction event motors.
- About 27 digital inputs.
- RTC, FRAM, Wi-Fi/NTP, and MQTT for Home Assistant.

Step rates are very low (about 1 Hz running, a few kHz catching up).

| Option | For | Against |
|---|---|---|
| **A. ESP32-S3 + TMC2209 stepsticks (UART) on a carrier**, with 2 × MCP23017 I/O expanders | One MCU; Wi-Fi, NTP and MQTT built in; Paul knows ESP32; plenty of capacity; low power | Needs a carrier board: off-the-shelf or a custom PCB (Phase 3). TMC2209 UART has 4 addresses per bus, so 6 drivers need 2 buses. |
| B. Raspberry Pi + motion board (BTT SKR Pico: RP2040, 4 × TMC2209; or Octopus: 8 drivers) with custom firmware | Robust 24 V power stages, connectors, MOSFET outputs; Linux for UI and logging | Two computers to maintain; SD-card wear; STM32duino has no stock Octopus variant, so a custom one is needed [Sn] |
| C. Arduino Mega + RAMPS 1.4 + TMC2209 | 5 driver sockets; endstop inputs; 3 MOSFETs | No network (no NTP or Home Assistant); 8-bit; awkward TMC2209 UART wiring on RAMPS; only 5 drivers. Its only advantage, reusing parts Paul already owns, is dropped: the BOM buys everything new (PR #1). |
| D. Printer board standalone (Octopus / Spider / Manta, 8 drivers) + ESP32 for the network | 8 drivers and a power stage on one board | Same two-MCU complexity as B; firmware support for a non-printer use is DIY |

**Recommendation.**

- **A for the clock.** Firmware has a board-independent motion core (P1 time law, events, FRAM
  state) plus a thin board layer.
- **The Phase 2 test rig uses the same platform.** An ESP32-S3 dev board and one or two TMC2209s
  from Batch 1 of the BOM. Those parts later move into the clock, so the firmware is exercised on
  the real target from the first print.
  - The earlier "Mega + RAMPS for the test rig" recommendation is withdrawn after Paul's PR #1
    comment: no parts from other projects.
- **Drivers:** TMC2209 in StealthChop, with low hold current (quiet in a living space).
- **RTC:** RV-3028-C7 with a supercapacitor (about ±1 ppm [Sn]), or a DS3231 (±2 ppm [Sn]). If a
  DS3231 module is used, remove or disable its charging diode when fitting a non-rechargeable
  CR2032 [Sn].
- **FRAM:** I²C, 32–256 kbit.
- **Event motors:** small DC gearmotors (Pololu micro-metal class, e.g. 100:1 [Sn]), each with a
  locking-cam microswitch and a DRV8833-class H-bridge. This is the electrical analogue of a
  striking train.
  - Alternative: 28BYJ-48 steppers on TMC2209. They are smoother and quieter but use 6 more
    drivers.
  - Decide per show in Phase 2 after a noise test.

---

## D4 — Gear tooth profile, default module, arbors, coaxial tubes, bearings

**Tooth profile.**

| Option | For | Against |
|---|---|---|
| **Involute 20° (ISO 53 basic rack)** | Tolerant to centre-distance error (printed plates); standard; BOSL2 reference for validation; works in both driving directions | Undercut below 17 teeth without profile shift |
| Cycloidal (horological, e.g. NIHS / BS 978) | Traditional; good for wheel-drives-pinion step-ups with low-count pinions | Sensitive to centre distance; little printed-gear precedent; harder to validate |

**Recommendation: involute 20°**, with these parameters:

- profile shift for z < 17;
- minimum pinion 10–12 teeth (shifted);
- backlash 0.15 mm as a parameter, applied as tooth thinning split between the mates;
- face width 4 mm by default and 6 mm in the motor stages, as parameters.

**Default module.** Use `CLAUDE.md`'s working defaults as parameters: **1.0** with the 0.4 mm nozzle,
**0.8** with the 0.2 mm nozzle.

- Use 0.8 where density demands it (main dial, planetary coaxials) and 1.0–1.25 in the motor
  reductions.
- The real minimum comes from the local tolerance test.
- Largest wheel that fits the bed [D], before brim margin:

| Bed axis | Module 1.0 | Module 0.8 |
|---|---|---|
| 320 mm (single nozzle) | 318 teeth | 398 teeth |
| 300 mm (dual nozzle) | 298 teeth | 373 teeth |

- Schwilgué's 269- and 270-tooth wheels fit at 1.0: 271–272 mm tip.
- 382- and 420-tooth wheels need module ≤ 0.8 or a segmented rim.

**Arbors** (metric ground rod; few sizes, to consolidate purchases).

- **Ø3** for light and dial trains, **Ø5** general, **Ø8** for motor reductions and large outputs.
- Silver steel to DIN 175 is ground to **h9** [Sn: DIN]; that is fine for plain bearings and
  printed hubs.
- Where a tighter fit is needed, use linear shafting: g6 below 6 mm, h6 from 6 mm [Sn: MISUMI].
- EU source: Ameco (CZ) [Sn]. The UK sellers (Thomas Graham) add post-Brexit customs.

**Coaxial tubes.** Brass tube with **0.45 mm wall in 1 mm OD steps** (e.g. Albion Alloys BT3M…BT10M
[Sn]; Conrad 6, 7 and 9 mm [Sn]). Each tube's ID is n − 0.9 mm, so the next size down slides inside
with **0.10 mm diametral clearance** [D].

- So a Ø3 arbor carries up to 7 coaxial tubes, out to Ø10 mm.
- Brass on brass with clock oil at these speeds is the traditional clockmaking practice.
- Larger coaxial groups (calendar ring, planet arms beyond 7) run on thin-section bearings with
  printed hubs.
- Albion has no French stockist yet, only UK and one DE eBay seller [Sn]. Confirm EU supply before
  Phase 2.

**Bearings** (standard set).

| Use | Bearings |
|---|---|
| Ø3 arbors | MR63ZZ, 3×6×2.5 |
| Ø5 arbors | MR85ZZ (5×8×2.5) or 685ZZ (5×11×5) |
| Ø8 arbors | 688ZZ, 8×16×5 |
| Large coaxial outputs | 6700-series (10×15×4 … 20×27×4) or thin-section 61806 (30×42×7) and 61808 (40×52×7) [Sn] |
| Slow arbors | Plain bearings: sintered bronze to ISO 2795 [Sn], igus iglidur sleeves [Sn], or brass tube on steel |

- Design bearing seats from **measured** parts: cheap MR85s have measured 7.93 mm OD rather than
  8.00 [Sn]. This goes into the local tolerance phase.

**Fasteners.**

- Stainless A2, M3 by default; M2 and M2.5 for small parts; M4 and M5 for structure.
- Screws to ISO 4762, 14580 and 7380.
- Brass heat-set inserts (ruthex M2–M5 [Sn]).
- Hubs on rods: clamping hubs with an insert and screw. Press-fit and retaining-compound variants
  go into the tolerance test.

---

## D5 — Scope: v1 vs deferred

| Version | Contents | Why |
|---|---|---|
| **v1** | M1 time and releases (I1, I2); M2 main dial with **mean** Sun and Moon, shadow disc, calendar ring with automatic leap day (4-year rule), weekday carousel; M5 planets and Moon globe; M6 sidereal globe; all automata E1–E4 | A complete, running clock with every visible motion |
| **v1.5** | M3 equations vitrine → apparent Sun and true Moon; eclipse arm (I5); sunrise/sunset (I7) | They depend on M3 and the main-dial feasibility study. The v1 main dial *provisions* them: differentials locked, tubes reserved, cam positions free. |
| **v2** | M4 computus + E5; movable feasts arc (I9); dominical-letter drive (I10); Gregorian century leap exception (next one in 2100); precession drive (I17) | The computus mechanism is undocumented (D7) and is the biggest single design task. The precession is nearly static (about 1.4° per century [D]). |

**Recommendation:** as above.

- The **main-dial feasibility study** (Phase 2) must still include every v1.5 and v2 element, so
  nothing is designed out.
- **Question for Paul (rephrased after PR #1):**

  **Background.** The real Sun and Moon do not move across the sky at a steady speed. A sundial
  runs up to about 16 minutes fast or 14 minutes slow over the year (the "equation of time"). The
  real Moon can be about 6° ahead of or behind its average position. Schwilgué corrects both with
  the cams in the "equations" vitrine, so his main dial shows the *true* Sun and Moon.

  **The choice:**
  - **(a) Corrections in the first working version.** The main dial is right from day one, but
    the first working clock arrives later, because the equations vitrine (M3) must be designed and
    printed first.
  - **(b) Steady (average) speeds first.** The first working version has the Sun and Moon hands
    moving at steady speeds. The main dial is built from the start with the slots for the
    corrections, and the equations vitrine is added in v1.5 without rebuilding anything. The
    first working clock comes sooner.

  **Recommendation: (b).** Which do you prefer?

---

## D6 — Case construction and mounting

**Context.**

- Estimated envelope 2.25 × ~1.0 × ~0.25 m. Depth TBD: at least 200 mm interior planned
  (envelope §1).
- Mass about 78–103 kg [E, envelope §5].
- Stone wall; enclosed, climate-controlled room; glazed front.

**Structure.**

| Option | For | Against |
|---|---|---|
| A. Birch-ply box, modules screwed to shelves | Cheap, classic woodwork | Module alignment depends on the woodwork; less serviceable |
| **B. Aluminium-extrusion module rack (20 × 20 / 20 × 40 metric profile) inside a birch-ply / MDF case**, with printed ornament | Precise, square, adjustable mounting for modules (P4); the wood is decorative and can be built later; wiring clips onto the slots | Two structures; extrusion cost |
| C. Fully printed case tiles | All in-house | Hundreds of print-hours, weaker, joint lines; wasteful for flat panels |

**Mounting.**

| Option | For | Against |
|---|---|---|
| (i) Wall-hung on a French cleat with chemical anchors in stone | "Wall art"; floor free | About 100 kg in shear and pull-out on anchors in stone of unknown quality; needs a fixing-design check |
| **(ii) Floor-bearing plinth + wall restraint brackets** | The floor carries the weight; the anchors only prevent tipping; easy to level | Uses floor space (a plinth about the case footprint) |

**Recommendation: B + (ii).**

- MDF for painted flat surfaces, birch ply for structure.
- Printed PLA ornament; PETG for clamped or structural printed parts.
- Hinged glazed doors per stage. Acrylic (about 8 kg) rather than glass (about 22.5 kg) for the
  front [D], with brush or foam dust seals.
- **Question for Paul:** what is the wall made of (e.g. Bordeaux limestone, rubble), and is a
  plinth acceptable?

---

## D7 — Computus: faithful reconstruction vs our own mechanical design

**Context.**

- Schwilgué's computus is an enlarged version of his 1821 prototype [S: RGL]. The prototype is
  about 300 parts [Sn: EXO].
- Its full study is unpublished [S: RGL].
- How it makes the Gregorian corrections and finds Easter is undocumented in every source reached
  so far.

| Option | For | Against |
|---|---|---|
| A. Faithful reconstruction | Authentic | Needs sources not yet available (Roegel's study, Flores 2007, Bach/Rieb); may never be complete |
| B. Our own mechanical Gregorian computus (count wheels, century wheels, rack-and-snail Easter finder), same displays | Can start any time; validated against a standard algorithm over 400 years in the simulator; still fully mechanical (rule 2) | Not Schwilgué's mechanism |

**Recommendation:** defer to v2 (D5) and buy or borrow the Flores 2007 book in the meantime.

- If, when v2 starts, the mechanism is still undocumented, choose **B**, with the same displays
  and the same once-a-year New Year's Eve operation.
- In both cases, design the v1 calendar ring with the feasts-arc groove and the leap gate
  (inventory I8, I9).

---

## D8 — Sound

**Context.** The original strikes real bells, and the rooster is mechanical and pneumatic
[S: CLEA]. The replica is in a living space.

| Option | For | Against |
|---|---|---|
| **Real small bells, cam-lifted hammers (bell angel, ages, Death)** | Faithful; mechanical; pleasant | Bell sourcing and tuning; volume set by the hammer |
| Bells via solenoids | Simple | Not a mechanical event train; clicky |
| Rooster: bellows and reed driven by the E4 train | Faithful in spirit | Hard to make sound like a rooster; development time |
| **Rooster: speaker plus a recording (DFPlayer-class), cued by the E4 train switch** | Convincing, volume-controllable | Not mechanical |
| No sound | Silent | Loses much of the charm |

**Recommendation:** mechanical bells; speaker crow in v1; a bellows experiment in v2 if wanted.
Quiet hours apply to both (D10).

---

## D9 — Legal-time hands and summer time

**Context.** The original's silver hands show CET [S: WIKI]. Whether they follow summer time is
unresolved [?]. A forward-only drive can still follow summer time: +1 h in spring, +11 h in autumn
on a 12 h dial, run at catch-up speed in seconds.

| Option | For | Against |
|---|---|---|
| A. Fixed CET (offset hands on M1) | Simplest; no extra motor | Wrong by 1 h for 7 months a year |
| **B. Own stepper M1b following CET/CEST** | Always right; useful as the house clock | One more stepper and a coaxial drive on the mean-time dial |
| C. No legal-time hands | Simplest | Less useful; less faithful |

**Recommendation: B.** The automata stay on mean time regardless.

---

## D10 — Night silence

| Option | For | Against |
|---|---|---|
| A. Always strike | Faithful | Quarter strikes all night in a living space |
| **B. Configurable quiet hours: the controller skips sound shows** | Simple. P2 (state lives in the trains) makes skipping safe. | Figures do not move at night |
| C. Mechanical strike/silent levers (figures move, hammers held off) | Figures still move | One actuator per bell train |

**Recommendation: B**, configurable from Home Assistant, with C as a later option.

---

## D11 — Case width and wall space

**Context.** `CLAUDE.md` targets 0.96 m (7.70 m ÷ 8). New evidence [Sn: WIKI] suggests 7.70 m may
be the *first* clock's width. ODY's 8.60 m is given for the second clock, whose case is the
current one (reference-notes, Phase 0 additions).

| Option | Size |
|---|---|
| A. 1:8, 7.70 m | 2250 × 962.5 mm |
| B. 1:8, 8.60 m | 2250 × 1075 mm |
| C. Keep the width at 0.96 m by changing the scale to 1:9 (if 8.60 m is right) | 2000 × 956 mm; main dial 255.6 mm |

**Recommendation.**

1. Resolve the source first: read ELS and check Bach/Rieb.
2. Make **scale a parameter** in `spec/clock.yaml`, so no module design depends on it.
3. **Paul gives the available wall width, height and ceiling height.**

The choice can then wait until case design (Phase 2) without blocking anything.

**Paul's input (PR #1 comment, 31 Oct 2026):** "1:8th scale is not a problem." Wall dimensions
to follow.

- **Status: Accepted. The scale is fixed at 1:8.** Option C (1:9) is dropped.
- The case width will be 962.5 mm or 1075 mm, whichever the primary source supports.
- Scale stays a parameter in `spec/clock.yaml` for tidiness, but no module needs to allow for
  another scale.

---

## Blockers (not decisions, but they need Paul)

**1. Network access for research.** This session could reach only package registries and GitHub.
Only Paul can change this, in the environment settings; a PR comment or chat message cannot.
The fix is in the cloud environment settings: environment menu → Edit → Network access, either a
broader level or these hosts added under *Allowed domains*, with "Allow package managers" left
ticked. Docs: https://code.claude.com/docs/en/cloud-environments#network-access.

| Purpose | Hosts |
|---|---|
| Key PDFs | `clea-astro.eu`, `bibnum.publimath.fr`, `www.elsolieltemps.com` |
| Primary books and prints | `books.google.com`, `play.google.com`, `gallica.bnf.fr`, `numistral.fr`, `archive.org`, `web.archive.org`, `babel.hathitrust.org`, `www.digitale-sammlungen.de` |
| Photos for envelope scaling | `commons.wikimedia.org`, `upload.wikimedia.org`, `en.wikipedia.org`, `fr.wikipedia.org`, `de.wikipedia.org` |
| Official data | `www.cathedrale-strasbourg.fr`, `pop.culture.gouv.fr` (Palissy PM67000355) |
| Computus study | `comput1821.github.io`, `roegeld.github.io` |
| Purchasing checks | `fr.rs-online.com`, `www.gotronic.fr`, `www.3djake.fr`, `fr.misumi-ec.com`, `www.123roulement.com`, `www.chronos.ltd.uk`, `eshop.ameco.cz` |

**2. Documents to obtain, in priority order.**

1. Ch. Schwilgué, *Description abrégée…* (public domain; Google Books id `LGYEyPW9ZWQC`).
2. The full ELS, CLEA and LEF PDFs. Paul could download them on the Mac and commit them under
   `docs/sources/`, if their licences allow.
3. Flores 2007 (Klinghammer computus).
4. Bach, Rieb & Wilhelm 1992.
5. Ungerer (1920s–1954 editions).
