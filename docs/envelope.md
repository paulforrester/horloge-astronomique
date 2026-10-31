# Envelope — 1:8 layout

Phase 0 deliverable. This file gives the overall case outline at 1:8 and the size and position of
every dial, vitrine and automaton stage. Tags as in `docs/reference-notes.md`. Derived numbers come
from `tools/phase0/derivations.py`.

> **Status: partial.** Positions were meant to come from scaling a frontal photograph against a
> known dimension.
>
> - In the first pass, the network policy blocked all image hosts.
> - After Paul widened access, Wikimedia answered "429 Too many requests" for every download in
>   this session.
>
> So **no photo has been measured yet**. Section 4 has the verified photo set (Commons API: sizes
> and licences confirmed) and the method. I have not filled the gaps with guessed positions.
>
> The stage *order* and the calendar ring's size now come from Schwilgué's own *Description
> abrégée* (DA, 1844).

## 1. Overall case

| Dimension | Original | 1:8 | Tag | Note |
|---|---|---|---|---|
| Height | 18 m | **2250 mm** | [S: ELS, AMIS] | AMIS describes the current case (three storeys, spiral staircase). DA confirms the stone cabinet is the one cut for the 1547 project, "le cabinet qui sert encore à l'horloge actuelle" [S: DA p. 9]. |
| Width at base | 7.70 m **or** 8.60 m | **962.5 mm or 1075 mm** | [?] | 7.70 m [S: ELS, snippet] may be the *first* clock's width [Sn: WIKI]. 8.60 m [S: ODY] is for the second (Dasypodius) clock, whose case is the current one. **Unresolved, and it changes the wall space by 112.5 mm.** |
| Depth | TBD | TBD | — | No source found. Measure from a three-quarter photo, or find it in Bach/Rieb. |
| Globe projection in front of the case | TBD | TBD | — | Same. |

**Replica depth budget (design estimate, not a measurement of the original) [E].** The case depth
behind the main dial must hold:

| Item | Depth |
|---|---|
| Dial plate | ~3 mm |
| Coaxial hand stack | ~25 mm |
| Two-plate gear module | ~60–80 mm |
| NEMA 17 body | 48 mm (standard length for a mid-size NEMA 17; varies by model) |
| Connectors and wiring | ~20 mm |
| **Total** | **~150–180 mm** |

Method: sum of the stack. Uncertainty: about ±30%, until the Phase 2 main-dial feasibility study
gives a real stack. The planetary and equation modules are expected to be thinner. Plan the case
around **≥ 200 mm interior depth** until Phase 2 confirms it.

## 2. Stage order, bottom to top (sourced)

From the layout notes [S: CLEA unless marked]. Heights are TBD.

```
 ┌──────────────────────────────────────────────┐   ← top of case, 2250 mm
 │  Dome: Isaiah, evangelists, seraphim         │   decoration [S: DA p. 60]
 │  Upper hall: Apostles pass before Christ     │   E3        [S: DA p. 56, 58]
 │  Lower hall: four ages (4 lodges) + Death    │   E2        [S: DA p. 56–57]
 │  Moon-phase globe (inclined)                 │   M5        [S: DA p. 53]
 │  Copernican planetary dial                   │   M5        [S: DA p. 51]
 │  Lion gallery: genie (bell) · mean-time      │   M1 + E1   [S: DA p. 49–51]
 │    dial (small) · genie (hourglass)          │
 │  Weekday chariots on a circular rail         │   M7        [S: DA p. 46–47]
 │  Calendar ring (25 cm × >9 m circ.) around   │   M2        [S: DA p. 27, 30]
 │    the apparent-time dial Ø287.5 mm          │   (+ dominical-letter dial, left)
 │  Computus (left)        Equations (right)    │   M4 / M3   [S: TS, MERP]
 └──────────────────────────────────────────────┘   ← base
        Celestial sphere at floor level, in front, on four metal columns  M6  [S: DA p. 24–25]
        (the calendar compartment is "immédiatement derrière la sphère céleste" [S: DA p. 27])
 Left tower: drive weights (5 × 50 kg), rooster on top (E4)
 Right: spiral staircase tower [S: AMIS]
```

**Replica proposal: use the towers for services.**

- The **left (weight) tower** becomes the electronics and power bay. The controller and PSU replace
  the weights, as the stepper motors replace them functionally. It gets a removable door and
  ventilation slots.
- The **staircase tower** becomes the vertical wiring riser, with an access panel.

This follows the serviceability rule in `CLAUDE.md`. See `architecture.md` §9.

## 3. Elements: size at 1:8 and position

Every element is listed. "Position" means the height of its centre above the case base and its
horizontal offset from the case centreline, at 1:8.

| Element | Module | Original size | 1:8 size | Position | Tag / status |
|---|---|---|---|---|---|
| Main (apparent-time) dial | M2 | Ø 2.30 m | **Ø 287.5 mm** | TBD | [S: ELS]; [D] |
| Calendar ring | M2 | **25 cm wide, circumference "passé 9 mètres"** [S: DA p. 27, checked on the page image], so Ø > 2.86 m [D] | **Ø > 358 mm, 31.25 mm wide** [D] | around the main dial [S: DA p. 30] | **Exceeds the 320 mm bed: print in 4 × 90° segments** (chord 253 mm [D]) |
| Dominical-letter dial | M2 | TBD | TBD | left of the main dial [S: CLEA] | photo |
| Weekday carousel | M7 | TBD | TBD | above the main dial [S: CLEA] | photo |
| Mean-time dial | M1 | "petit cadran" (small dial); diameter TBD [S: DA p. 49] | TBD | middle of the lion gallery, above the weekday chariots [S: DA p. 49] | photo |
| Angels (bell, hourglass) | E1 | TBD | TBD | either side of the mean-time dial [S: CLEA] | photo |
| Planetary dial | M5 | "grand cadran" (large dial); diameter TBD [S: DA p. 51] | TBD | storey above the lion gallery [S: DA p. 51] | photo |
| Moon-phase globe | M5 | TBD; inclined globe on a starry sky [S: DA p. 53] | TBD | above the planetary dial [S: CLEA, DA] | photo |
| Ages and Death stage | E2 | lower hall with ogival arcades; Death on a central pedestal; four lodges [S: DA p. 56–57]. Sizes TBD | TBD | above the Moon globe [S: CLEA] | photo |
| Apostles and Christ stage | E3 | figures ~18 in (457 mm) [S: WIKI; Sn: WIKI for Christ] | **figures ~57 mm** | top stage [S: CLEA] | [D] |
| Rooster | E4 | "exécuté d'après nature" (life-size) [S: DA p. 59]; no number | TBD | top of the weight tower [S: DA p. 59] | photo |
| Computus vitrine | M4 | TBD (the 1821 *model* is 15 × 20 × 6 cm [Sn: EXO]; the clock's computus is an enlarged version [S: RGL]) | TBD | bottom left [S: TS] | photo |
| Equations vitrine | M3 | TBD | TBD | bottom right [S: MERP, CLEA] | photo |
| Celestial globe | M6 | **TBD**: copper sphere on four metal columns [S: DA p. 25] (83/86 cm is the *second* clock's globe [Sn]) | TBD | floor level, in front [S: CLEA, DA] | photo |
| Left weight tower | — | TBD | TBD | left [S: CLEA] | photo |
| Staircase tower | — | TBD | TBD | [S: AMIS] | photo |

**Bed-fit checks that are already possible [D]:**

| Part | Check | Result |
|---|---|---|
| Main dial disc, 287.5 mm | H2D single-nozzle (325 × 320) | Fits, 32.5 mm spare on the 320 mm axis |
| Main dial disc, 287.5 mm | Dual-nozzle (300 × 320) | Fits, 12.5 mm spare |
| Apostles (~57 mm) | Fine detail | Print with the 0.2 mm nozzle |
| Largest single gear at module 1.0 | Fits the 320 mm axis | ≤ 318 teeth (≤ 298 on the dual-nozzle 300 mm axis), before brim margin |

## 4. Photo-scaling method (ready to run when the hosts are allowed)

### Candidate photographs

Sizes and licences below are checked through the Commons API. The image downloads themselves were
rate-limited (429) in this session.
`https://commons.wikimedia.org/wiki/Special:FilePath/<filename>` always redirects to the original.

| # | File (Wikimedia Commons) | Size / author / licence (Commons API, 31 Oct 2026) | Notes |
|---|---|---|---|
| P1 | `Strasbourg_Cathedral_Astronomical_Clock_-_Diliff.jpg` | 1754 × 2886, Diliff, 2014-02-08, CC BY-SA 3.0 | First choice: a careful architectural photographer |
| P2 | `Horloge_astronomique_de_la_cathédrale_de_Strasbourg.jpg` | 3864 × 5152, Balwina54, CC BY-SA 3.0 | Highest resolution |
| P3 | `Astronomical_Clock_in_Cathedral_Strasbourg_France.jpg` | 3024 × 4032, amanderson2, 2019-02-15, CC BY 2.0 | |
| P4 | `00_1012_Straßburger_Münster_-_Astronomische_Uhr.jpg` | 1733 × 2600, W. Bulach, 2012-06-26, CC BY-SA 4.0 | |
| P5 | `Strasbourg_Astronomical_clock_Comput_ecclesiastique.jpg` | 3312 × 4416, Tangopaso, 2009-12-05, public domain | Close-up of the computus |
| — | Category `Strasbourg_Astronomical_clock_(present)` (about 194 files) | | For close-ups of the main dial, planetary dial and equations vitrine |
| — | Period frontal prints: Gallica `btv1b10202446r`; Numistral `btv1b10202448n` (1845); 1842 Grieshaber lithograph (Nancy archives) | | No perspective, but drawn. Use as a cross-check of proportions, not as the primary measurement. |

### Method

1. **Choose a near-frontal photo** of the whole case taken from far back (least keystone).
2. **Rectify the perspective.**
   - Fit an ellipse to the main dial's rim. The minor/major axis ratio gives the vertical tilt:
     cos θ = b/a, for a dial plane assumed vertical.
   - Use the case's vertical edges (assumed parallel) to remove keystone, with a projective
     homography from four points.
3. **Scale.** Use the main-dial diameter (2.30 m [S]) for elements near the dial, and the case
   height (18 m [S]) as a second, independent reference. Report both scales. A disagreement
   between them is the residual perspective error.
4. **Measure** each element's bounding box and centre in rectified pixels. Convert to metres, then
   divide by 8.
5. **Cross-check** with a second photo and one period print.
6. **Uncertainty for each value** = pixel-picking error ⊕ residual perspective ⊕ reference
   uncertainty. Expected: about ±3–5% near the main dial, about ±10% at the top stages. These
   figures are an estimate, to be replaced by the measured residuals.
7. **Output:** the table in §3 filled with **[E: photo P#, method §4, ±x%]** entries. Keep the
   script (`tools/envelope/measure.py`) and a downscaled annotated image (not the full-resolution
   original) in the repo.

## 5. Consequences for the build

- **Width:** decide (D11) whether the 0.96 m target in `CLAUDE.md` stands. If the true base width
  is 8.60 m, a 1:8 replica is 1075 mm wide. **Paul: what wall width, height and ceiling height are
  available on the terrasse?**
- **Glazing:** the front is about 2.25 m × 1.0 m (2.25 m²). As 4 mm glass it weighs about 22.5 kg;
  as 3 mm acrylic about 8 kg [D]. Hinged glazed doors per stage give access. See decisions D6.
- **Mass:** about 78–103 kg in total [E: 12 mm birch-ply panel areas × 680 kg/m³ + glazing +
  10–20 kg prints + ~5 kg metal; ±40%]. This drives the mounting decision (D6).
