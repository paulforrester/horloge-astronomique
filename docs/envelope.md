# Envelope — 1:8 layout

Phase 0 deliverable. This file gives the overall case outline at 1:8 and the size and position of
every dial, vitrine and automaton stage. Tags as in `docs/reference-notes.md`. Derived numbers come
from `tools/phase0/derivations.py`; plate estimates come from `tools/envelope/plate_measurements.py`.

> **Status.**
>
> - **Sizes** now come mostly from primary sources, chiefly Alfred Ungerer's 1920 lecture (ELS),
>   Ungerer being Schwilgué's successor.
> - **Positions** are **estimates [E]**, scaled from the lithograph made in Schwilgué's own
>   workshop (bound into DA). The drawing was first checked against five sourced dimensions: it
>   agrees to within ±3.3 % (§4).
> - **Photo measurement** is still pending as an independent cross-check: Wikimedia answered
>   "429 Too many requests" to every image download.

## 1. Overall case

| Dimension | Original | 1:8 | Tag | Note |
|---|---|---|---|---|
| Height | **18 m**, "le couronnement gothique compris" | **2250 mm** | [S: ELS, instalment 1] | See the height note below the table. |
| Width at base | **7.70 m**: "l'ancien édifice, construit en pierres de taille, de 7m,70 de largeur à la base" | **962.5 mm** | [S: ELS, instalment 1] | **Resolved.** See the width note below the table. |
| Depth | TBD | TBD | — | No source gives it. Measure from a three-quarter photo, or find it in Bach/Rieb. |
| Sphere projection in front of the case | TBD | TBD | — | As above. |

**Height note.**

- The case is the 1574 stone case, which Schwilgué kept [S: ELS; DA p. 9]. AMIS agrees.
- **[?]** DA says its "élévation … n'est pas moindre de 20 mètres" (checked on the page image). That
  is a rough lower bound, seen from the staircase balcony.
- ELS's explicit 18 m is used. The plate's scale check agrees with it.

**Width note.**

- ELS gives 7.70 m for the current case, so the Wikipedia snippet that tied 7.70 m to the first
  clock was wrong, or describes a different figure.
- ODY's 8.60 m [?] is still unexplained. On the plate, the base stage measures about 8.0–8.2 m
  including the plinth and the tower bases [E].

**Replica depth budget (design estimate, not a measurement of the original) [E].** The case depth
behind the main dial must hold:

| Item | Depth |
|---|---|
| Dial plate | ~3 mm |
| Coaxial hand stack | ~25 mm |
| Two-plate gear module | ~60–80 mm |
| NEMA 17 body | ~48 mm (typical; varies by model) |
| Connectors and wiring | ~20 mm |
| **Total** | **~150–180 mm** |

Method: sum of the stack, ±30 %, until the Phase 2 main-dial study. Plan the case around
**≥ 200 mm interior depth**.

## 2. Stage order and heights

The order is sourced [S: DA, CLEA]. Heights of centres above the floor are **[E]** from the plate,
at 1:8, each ±(3 % + 15 mm).

```
 ┌──────────────────────────────────────────────┐ 2250  crown apex (18 m [S])
 │  Dome / Gothic crown: Isaiah, evangelists    │
 │  Upper hall: Apostles pass before Christ     │ 1473  E3
 │  Lower hall: four ages (4 lodges) + Death    │ 1324  E2
 │  Moon-phase globe (Ø 50 mm [S])              │ 1074  M5
 │  Copernican planetary dial                   │  810  M5
 │  Lion gallery: genie · mean-time dial · genie│  567  M1 + E1  (top of the base stage)
 │  Weekday chariots on a circular rail         │  453  M7
 │  Calendar ring around the apparent-time dial │  213  M2  (+ dominical-letter dial, left)
 │  Computus (left)        Equations (right)    │       M4 / M3
 └──────────────────────────────────────────────┘    0  floor
   Celestial sphere (Ø 105 mm [S]) at floor level, in front, on four columns   M6
   Left weight tower, top ≈ 1729 incl. rooster (E4) · Right staircase tower, top ≈ 1409
```

**Replica proposal: use the towers for services.**

- The **left (weight) tower**, about 215 mm wide [E], becomes the electronics and power bay. The
  controller and PSU replace the weights, as the steppers replace them functionally.
- The **staircase tower**, about 256 mm wide [E], becomes the wiring riser.

See `architecture.md` §11.

## 3. Elements: size at 1:8 and position

Columns:

- **Height** is the height of the element's centre above the floor at 1:8.
- **x** is the offset from the case centreline.
- Plate estimates are [E] ±(3 % + 15 mm at 1:8). Sizes marked [S] are from the sources.

| Element | Module | Original size | 1:8 size | Height (1:8) | Tag / note |
|---|---|---|---|---|---|
| Main (apparent-time) dial | M2 | **Ø 2.30 m**, 2 × 12 h | **Ø 287.5 mm** | ~213 mm; x ≈ 0 | [S: ELS]; height [E] |
| Sun hand | M2 | "exactement de 1 mètre" | 125 mm | — | [S: ELS]. Scale: 1° = 17.45 mm, i.e. 2.18 mm at 1:8 |
| Sun / Moon / Earth-shadow discs | M2 | 9.3 / 9.1 / 24.3 mm | 1.16 / 1.14 / 3.04 mm | — | [S: ELS; OCR "g" read as 9, checked against 32′ × 17.45 mm/° [D]]. **Too small at true scale; see §5.** |
| Eclipse (latitude) cam | M2 | R 154.2 mm, r 113.8 mm | R 19.3, r 14.2 mm | — | [S: ELS] |
| Calendar ring | M2 | **Ø 2.73 m outer, 21 cm wide, 368 divisions** | **Ø 341 mm, 26 mm wide** | concentric with the main dial | See the calendar-ring note below the table. |
| Dominical-letter dial | M2 | TBD | TBD | left of the main dial [S: CLEA] | photo |
| Weekday chariots | M7 | visible band ~1.70 m wide | ~212 mm | ~453 mm | [E] |
| Mean-time dial | M1 | ~0.78 m | **~98 mm** | ~567 mm; x ≈ 0 | [E]. DA calls it a "petit cadran". Silver legal-time hands were added in March 1919 [S: ELS]. |
| Genies (bell, hourglass) | E1 | TBD | TBD | ~567 mm, either side of the mean-time dial | [S: DA]; size TBD |
| Planetary dial | M5 | **zodiac painted around a circle of Ø 2.20 m**; band outer ~2.75 m | **inner Ø 275 mm; band ~343 mm** | ~810 mm | [S: ELS] inner; [E] band. **The band exceeds the bed: print it in segments.** Planet arbors stand on a 20 cm-radius crown (25 mm at 1:8); intermediate wheels have ≤ 250 teeth [S: ELS]. |
| Moon-phase globe | M5 | **Ø 0.40 m**, half gilt, half black; axis tilted ~40° | **Ø 50 mm** | ~1074 mm | [S: ELS]; height [E] |
| Lower hall (four ages, Death) | E2 | opening ~1.46 m wide | ~183 mm | ~1324 mm | [E] |
| Upper hall (Christ, Apostles) | E3 | opening ~1.46 m wide | ~183 mm | ~1473 mm | [E] |
| Figures (Apostles, Christ, Death) | E2, E3 | **[?]** ~18 in (0.46 m) [S: WIKI], but drawn at ~0.70 m on the plate [E] | 57 mm or 88 mm | — | Resolve with a photo; this matters for E2/E3 sizing |
| Rooster | E4 | "d'après nature" (life-size) [S: DA] | TBD | top of the weight tower, ~1729 mm [E] | — |
| Left (weight) tower | — | ~1.72 m wide; top ~13.8 m incl. rooster | ~215 mm; ~1729 mm | left | [E] |
| Staircase tower | — | ~2.05 m wide; top ~11.3 m | ~256 mm; ~1409 mm | right | [E] |
| Central body | — | ~3.72 m wide | ~465 mm | — | [E] |
| Computus vitrine | M4 | TBD | TBD | bottom left [S: TS, DA] | photo |
| Equations vitrine | M3 | TBD | TBD | bottom right [S: MERP, DA] | photo |
| Celestial sphere | M6 | **Ø 0.84 m, copper, painted blue**; axis 48°35′ to the horizon (Strasbourg) | **Ø 105 mm** | floor level, in front [S]; height TBD | [S: ELS]. Bordeaux sky (D2): axis at 44°50′. |

**Calendar-ring note.**

- ELS gives Ø 2.73 m outer, 21 cm wide, 368 divisions. The forged-iron ring bands were machined at
  that diameter.
- DA (1844) gives "25 cm … circonférence de passé 9 mètres", i.e. Ø > 2.86 m [?].
- **Design value: ELS**, the maintainer's measurement.
- At 1:8 the ring is larger than the 320 mm bed, so it prints in 4 × 90° segments (chord 241 mm
  [D]).

**Bed-fit checks [D]:**

| Part (1:8) | Result |
|---|---|
| Main dial disc, 287.5 mm | Fits the 320 mm axis (32.5 mm spare) and the 300 mm dual-nozzle limit (12.5 mm spare) |
| Calendar ring, 341 mm | **Does not fit**: 4 segments |
| Planetary dial: inner 275 mm, band ~343 mm | Inner disc fits; **band in segments** |
| Mean-time dial ~98 mm; Moon globe 50 mm; sphere 105 mm | Fit easily |
| Largest single gear at module 1.0 | ≤ 318 teeth (≤ 298 on the dual-nozzle 300 mm axis), before brim margin |

## 4. Methods

### 4a. Plate scaling (done) [E]

**Source.** The lithograph "Horloge astronomique de la Cathédrale de Strasbourg, construite par
J.B. Schwilgué, 1838 à 1842". It is captioned "Des. & Lith. dans les Ateliers de M. Schwilgué"
(drawn and lithographed in Schwilgué's workshop) and bound into DA (1844 and 1854 editions). Public
domain.

**Annotated, downscaled copy:** [`docs/img/plate_annotated.jpg`](img/plate_annotated.jpg).

**Checking the drawing.** It is a drawing, so its proportions were checked against five sourced
dimensions before any estimate was made from it:

| Sourced dimension | Drawn | Scale |
|---|---|---|
| Case height 18 m | 1542 px | 85.7 px/m |
| Base width 7.70 m | 680 px | 88.3 px/m |
| Calendar ring 2.73 m | 232.6 px (Hough circle fit) | 85.2 px/m |
| Apparent-time dial 2.30 m | 196 px | 85.2 px/m |
| Planetary circle 2.20 m | 183 px | 83.2 px/m |

Mean scale 85.5 px/m; largest deviation 3.3 %.

**Estimates.** Unsourced positions and sizes = pixels ÷ 85.5 px/m. Uncertainty ±3 % (scale spread)
plus ±10 px reading error (±0.12 m, i.e. ±15 mm at 1:8). The pixel data and the arithmetic are in
`tools/envelope/plate_measurements.py`.

**Limits.** The engraver may have simplified details. Figure sizes in particular disagree with the
"18 in" source [?]. A photo is the independent check.

### 4b. Photo scaling (pending; Wikimedia rate-limited this session)

**Candidate photographs.** Sizes and licences were checked through the Commons API.
`https://commons.wikimedia.org/wiki/Special:FilePath/<filename>` redirects to the original.

| # | File (Wikimedia Commons) | Size / author / licence | Notes |
|---|---|---|---|
| P1 | `Strasbourg_Cathedral_Astronomical_Clock_-_Diliff.jpg` | 1754 × 2886, Diliff, 2014-02-08, CC BY-SA 3.0 | First choice |
| P2 | `Horloge_astronomique_de_la_cathédrale_de_Strasbourg.jpg` | 3864 × 5152, Balwina54, CC BY-SA 3.0 | Highest resolution |
| P3 | `Astronomical_Clock_in_Cathedral_Strasbourg_France.jpg` | 3024 × 4032, amanderson2, 2019-02-15, CC BY 2.0 | |
| P4 | `00_1012_Straßburger_Münster_-_Astronomische_Uhr.jpg` | 1733 × 2600, W. Bulach, 2012-06-26, CC BY-SA 4.0 | |
| P5 | `Strasbourg_Astronomical_clock_Comput_ecclesiastique.jpg` | 3312 × 4416, Tangopaso, 2009-12-05, public domain | Computus close-up |

**Method.**

1. Choose a near-frontal photo taken from far back.
2. Rectify the perspective: fit an ellipse to the main-dial rim to get the tilt, and use a
   four-point homography on the case's vertical edges.
3. Scale against the main dial (2.30 m) and the height (18 m).
4. Measure the elements; report each value with its uncertainty.
5. Compare with §4a, and replace any plate estimate that disagrees by more than its uncertainty.

## 5. Consequences for the build

- **Width: 962.5 mm** (7.70 m ÷ 8). This agrees with `CLAUDE.md`. **Height: 2250 mm.**
- **Bed limits.** The calendar ring and the planetary zodiac band print in segments. Every other
  dial disc fits.
- **Sun and Moon disc size.**
  - At true 1:8 scale the discs would be about 1.2 mm across, which is invisible.
  - They must be enlarged for legibility, for example to 8–10 mm.
  - Enlarged discs would overlap far more often than the real bodies, so the "eclipse" geometry
    no longer works by itself.
  - Options for the Phase 2 main-dial study:
    - (a) keep true-scale discs inside larger decorative ones;
    - (b) scale the latitude cam to match the enlarged discs, accepting that eclipses would be
      shown too often;
    - (c) show eclipses with a separate indicator.
- **Glazing:** the front is about 2.25 m × 0.96 m (2.2 m²). As 4 mm glass about 22 kg, as 3 mm
  acrylic about 8 kg [D]. See D6.
- **Mass:** about 78–103 kg in total [E: panel areas × density + glazing + prints + metal; ±40 %].
  See D6.
  It assumes a ply-only case. Re-estimate it from the case model if D12 (hardwood framing) is
  accepted.
