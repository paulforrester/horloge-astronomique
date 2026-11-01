# Running hardware list (BOM)

One list for the whole project, so purchases can be consolidated into a few orders.

- **Everything is bought new.** No parts come from Paul's other projects (Paul, PR #1 comment,
  31 Oct 2026).
- **Quantities** are counted from `docs/architecture.md` [E: method in each row]. They are firmed
  up as each module is designed.
- **Nothing needs buying yet.** Batch 1 is proposed for the local tolerance tests and the Phase 2
  test rig, to be ordered once the test-rig design is approved.

**About the supplier data.** It was gathered from search snippets only (retailer sites were
blocked in the Phase 0 session) and is marked **⚠ verify**. Prices change; open each link before
ordering.

- Metric sizes only. Prefer suppliers in France or the EU.
- UK suppliers mean customs and VAT on delivery to France (post-Brexit).

## Batch plan

| Batch | When | Purpose |
|---|---|---|
| 1 | After the Phase 2 test-rig design is approved | Tolerance tests, slip-clutch and bearing-seat tests, test rig (one stepper driving hour/day motion work), event-motor noise test |
| 2 | After the v1 module designs | Everything for v1 (D5) |
| 3 | After the v1.5 / v2 designs | Equations module, computus, extras |

## Batch 1 — tolerance tests and test rig

| Item | Spec | Qty | Candidate supplier | Link | Notes |
|---|---|---|---|---|---|
| 0.2 mm nozzle for the H2D | Bambu H2D hotend, 0.2 mm | 1 | Bambu Lab EU store | — | Already planned (`CLAUDE.md`) |
| ESP32-S3 dev board | ESP32-S3-DevKitC-1-N8R8 | 1 | Mouser FR | https://www.mouser.fr/c/semiconductors/?q=esp32-s3 | Test rig; later the development spare |
| TMC2209 stepstick | UART, StealthChop | 2 | 3DJake (BTT), West3D (FYSETC) | https://www.3djake.ch/fr-CH/bigtreetech/pilote-de-moteur-pas-a-pas | Move to the clock afterwards |
| Stepstick breakout / carrier | Single-driver breakout with motor and power terminals, or a 2-socket expansion board | 2 | — | — | ⚠ choose in the test-rig design; final carrier in Phase 3 |
| NEMA 17 stepper | 1.8°, about 40–48 mm body, ≤ 1.7 A, 5 mm shaft. **No built-in gearbox** (architecture §3) | 1 | StepperOnline (EU warehouse claimed ⚠) | https://www.ebay.de/str/destepperonline | Final size from the Phase 2 torque estimate |
| 24 V PSU | Mean Well LRS-100-24 (24 V, 4.5 A) | 1 | Gotronic | https://www.gotronic.fr/art-alimentation-lrs100-24-26283.htm | Becomes the clock PSU if Phase 3 sizing agrees |
| Buck converter 24 → 5 V | ≥ 3 A | 1 | — | — | |
| Electrolytic capacitor | 100 µF, 35 V, one per driver | 4 | — | — | Driver supply decoupling |
| RTC | RV-3028-C7 breakout + supercap, **or** DS3231 module | 1 | Mouser FR / Melopero (IT); Gotronic GT584 | https://www.gotronic.fr/art-module-rtc-i2c-ds3231-gt584-36063.htm | DS3231 module: mind the charging diode with a CR2032 [Sn] |
| FRAM | I²C, 32–256 kbit breakout | 1 | Mouser FR | — | Prove the persistence and catch-up logic on the rig |
| Hall switches | DRV5032 (or TLE4905L); **not** A3144, which is obsolete [Sn] | 10 | Mouser FR, Gotronic | https://www.ti.com/product/DRV5032 · https://www.gotronic.fr/art-capteur-a-effet-hall-st054-26119.htm | |
| Magnets | NdFeB disc 5 × 2 mm | 20 | supermagnete | https://www.supermagnete.de/eng/disc-magnets-neodymium/disc-magnet-5mm-2mm_S-05-02-N52N | |
| Opto fork | ITR9608-class module | 4 | Gotronic | https://www.gotronic.fr/art-module-capteur-a-fourche-st056-26120.htm | Lock and witness sensing |
| Microswitches | small lever type | 10 | Gotronic / RS | — | Event lock switches |
| DC gearmotor | Pololu micro-metal HP 6 V 100:1 (#1101) | 2 | Gotronic (FR distributor) | https://www.pololu.com/product/1101 | Event-motor noise test (D3) |
| H-bridge | DRV8833-class dual | 1 | Gotronic / Mouser FR | — | |
| Ground rod Ø3, Ø5, Ø8 | Silver steel DIN 175 (h9) | 1 m each | Ameco (CZ) | https://eshop.ameco.cz/products/en/1630/559/g1433/64720400/ | ⚠ verify sizes in stock |
| Brass tube set, 0.45 mm wall | OD 4, 5, 6, 7, 8, 9, 10 mm (nests over Ø3 rod, 0.10 mm clearance [D]) | 1 of each | Albion Alloys BTxM via Chronos (UK); Conrad (6, 7, 9 mm) | https://www.chronos.ltd.uk/product-category/round-square-tube-sheet-metal-ptfe-nylon/albion-alloys-precision-metals/albion-alloys-standard-brass-round-tube-metric/ · https://www.conrad.com/en/p/brass-tube-rail-x-l-6-mm-x-500-mm-inside-diameter-51-mm-297321.html | ⚠ no French Albion stockist found |
| Bearings, sample set | MR63ZZ, MR85ZZ, 685ZZ, 688ZZ, 6701ZZ | 10 each | 3DJake (AT), RS FR, kugellager-express (DE) | https://www.3djake.ch/fr-CH/3djake/roulements-a-billes?sai=33685 · https://fr.rs-online.com/web/p/roulements-a-billes/0313140 | Measure real ODs to set seat sizes (D4) |
| Sintered-bronze and igus bushes | Bore 3 and 5 mm | assortment | RS FR (528-238, 528-923); igus free sample box | https://docs.rs-online.com/1a4c/A700000015780986.pdf | ⚠ verify |
| Heat-set inserts | ruthex M2, M2.5, M3, M4 | assortment | 3DJake | https://www.3djake.ch/fr-CH/ruthex/inserts-filetes-m2-m3-m4-m5 | |
| Screws A2-70 | M2–M5, ISO 4762, 14580, 7380 | assortment | 3DJake, RS FR, Accu | https://fabory.com/fr/Norme/Normes-DIN/DIN-912/c/DIN912 | |
| Wave / disc spring washers | for slip-clutch tests on Ø3, Ø5, Ø8 | assortment | Accu FR | https://accu-components.com/fr/shop/composants-de-precision/rondelles-et-entretoises/rondelles-a-ressorts/rondelles-ondulees | Setting mechanism (architecture §7) |
| Hook-up wire, Dupont / JST-XH kit, crimper | — | 1 kit | — | — | |
| Multimeter | basic | 1 | — | — | Only if Paul has none dedicated to this project |

## Batch 2 — v1 clock (quantities from the architecture; refine per module)

| Item | Spec | Qty [E] | How the quantity was counted | Candidate supplier / link |
|---|---|---|---|---|
| ESP32-S3 dev board (clock controller) | as Batch 1 | 1 | one controller (D3) | Mouser FR |
| NEMA 17 steppers | as Batch 1 | 5 + 1 spare | M1, M2, M5, M6 + M1b (D9); the Batch 1 motor becomes one of them | StepperOnline ⚠ |
| TMC2209 stepsticks | as Batch 1 | 5 + 1 spare (Batch 1 supplies 2) | one per stepper | 3DJake / West3D |
| Driver carrier | 6-socket carrier, off-the-shelf or custom PCB (Phase 3) | 1 | — | TBD |
| MCP23017 I/O expander | I²C | 2 | about 27 inputs (architecture §10) | Mouser FR |
| Hall switches + magnets | as Batch 1 | 20 + 30 | ~6 index + ~8 witness + ~6 trigger sensors | as Batch 1 |
| Opto forks / microswitches | as Batch 1 | 6 / 10 | ~6 event locks + door + spares | Gotronic |
| DC gearmotors | as Batch 1 | 6 + 1 spare | E1 ×2 (bell, glass), E2, E3, E4, E6 (calendar advance, as in the original) | Gotronic (Pololu) |
| H-bridges | DRV8833-class dual | 3 | 2 motors each (6 motors) | Gotronic / Mouser FR |
| Sound (D8) | DFPlayer-Mini-class module + small speaker | 1 | rooster crow | TBD |
| Bells | small, for the angel, the ages and Death | TBD (≥ 2) | strokes and bells TBD (inventory A3/A4) | TBD |
| Connectors | JST-XH or Micro-Fit, keyed, one per module | ~12 | M1, M1b, M2, M5, M6, M7, E1–E4 + spares | TBD |
| Thin-section bearings | 61806 (30×42×7), 61808 (40×52×7) | TBD | large coaxial outputs | Rubix, RS: https://ie.rs-online.com/web/p/ball-bearings/2076966 |
| Ground rod, brass tube, bearings, fasteners | as Batch 1 | TBD per module | summed from each module's BOM rows (Phase 2) | as Batch 1 |
| Adjustable friction clutch | Huco Vari-Tork, 6 mm bore | only if printed clutches fail | — | RS BE-FR: https://befr.rs-online.com/web/p/friction-clutches/8903033 |
| Aluminium extrusion | 20 × 20 / 20 × 40 metric slot profile | **only if D12 option A** | module rack (D6, under revision) | TBD |
| Birch plywood (contreplaqué bouleau) | structural carcass, shelves, plinth; thicknesses from the case design (e.g. 12 / 18 mm) | TBD | case design (D12) | local timber merchant (négoce bois) or a panel supplier |
| MDF | painted flat parts, routed profiles | TBD | D12 | as above |
| Hardwood | face frame, pilasters, door frames, frame-and-panel. **One species** from D12 R3: tulipier, sapelli or sipo preferred; oak acceptable. Planed all round ("raboté 4 faces") if available; quarter- or rift-sawn where width matters | TBD (cut list from `cad/case/`) | D12 | Bordeaux timber merchant (Paul to confirm stock) |
| Stock mouldings | simple profiles to combine with table-saw-made ones (no router) | TBD | D12 R1 | timber merchant / DIY store |
| Lime (tilleul) | only if any details are carved by hand | small | D12 R3 | timber merchant |
| Threaded inserts for wood | M4 / M5, for the module mounts and removable panels | TBD | D12 rule 2 | TBD |
| Locating pins | Ø4 / Ø5 dowel pins, round and slotted mounts | TBD | D12 rule 2 | TBD |
| Wood glue, finish | PVA / hide glue; finish per D12 question 2 | TBD | D12 | TBD |
| Hinges, catches | for the glazed doors and the service doors | TBD | D6 / D12 | TBD |
| Glazing | 3 mm acrylic, about 2.25 m² | TBD | D6 | TBD |

### Batch 2 — M2 rows from the feasibility layout [E]

Quantities from `cad/modules/m2_main_dial/feasibility.py`. The M2 detailed design refines them.
They count towards the "ground rod, brass tube, bearings" row above.

| Item | Spec | Qty [E] | How the quantity was counted | Supplier |
|---|---|---|---|---|
| Brass tube, 0.45 mm wall | OD 4, 5, 6, 7, 8, 9 mm | 1 length (≈ 300 mm) of each | centre stack: shadow, Moon, cam, Sun, sunrise, sunset tubes (`docs/main-dial-feasibility.md` §2) | as Batch 1 |
| Ground rod Ø3 | DIN 175 h9 | 0.1 m | fixed centre arbor | as Batch 1 |
| Ground rod Ø5 | DIN 175 h9 | 1 m | 8 lay shafts × ≈ 85 mm, plus the M3 input and weekday shafts | as Batch 1 |
| Bearing 688ZZ | 8 × 16 × 5 | 6 | calendar-ring rollers | as Batch 1 |
| Bearing MR85ZZ (or bronze bushes) | 5 × 8 × 2.5 | 16 | 8 lay shafts × 2 seats | as Batch 1 |
| NEMA 17 + TMC2209 | as above | (already counted) | the M2 stepper | — |
| Wall restraint brackets + anchors for stone | per fixing design | TBD | D6; wall material TBD | TBD |
| Clock oil | horological | 1 | brass tube stacks | TBD |
| Filament | PLA (gears, display), PETG (structure) | TBD | from slicer estimates per module | TBD |

## Batch 3 — v1.5 / v2

| Item | Qty [E] | Note |
|---|---|---|
| NEMA 17 + TMC2209 for M3 (equations) | 1 + 1 | D5 v1.5 |
| DC gearmotor + H-bridge channel for E5 (computus) | 1 | D5 v2 |
| Sensors for M3 / M4 witnesses and locks | ~6 | — |
| Computus visible frame: brass or steel plate and pillars, metric | TBD | D12 R4. v2. Plates cut and drilled to drawings from `cad/modules/M4`. |
