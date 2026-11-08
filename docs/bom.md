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
| Flexible shaft coupling **(test rig)** | 5 mm to 5 mm, jaw or bellows, ≈ Ø19 × 25 mm | 1 + 1 spare | 3D-printer parts sellers (3DJake, RS FR) | — | Motor to minute arbor (`docs/test-rig.md` §5) |
| Shaft collar **(test rig)** | Ø5 bore, with grub screw | 2 | RS FR / Accu | — | Clutch preload behind the cannon pinion |
| Standoffs **(test rig)** | M3 × 30 mm, female-female | 4 | RS FR / Accu | — | NEMA 17 behind the back plate |

## Batch 2 — v1 clock (quantities from the architecture; refine per module)

| Item | Spec | Qty [E] | How the quantity was counted | Candidate supplier / link |
|---|---|---|---|---|
| ESP32-S3 dev board (clock controller) | as Batch 1 | 1 | one controller (D3) | Mouser FR |
| NEMA 17 steppers | as Batch 1 | 6 + 1 spare | M1, M2, M5, M6, M1b (D9) and E2's state arbor (M1 gate, decision 1); the Batch 1 motor becomes one of them | StepperOnline ⚠ |
| TMC2209 stepsticks | as Batch 1 | 6 + 1 spare (Batch 1 supplies 2) | one per stepper | 3DJake / West3D |
| Driver carrier | 6-socket carrier, off-the-shelf or custom PCB (Phase 3) | 1 | — | TBD |
| MCP23017 I/O expander | I²C | 2 | about 27 inputs (architecture §10) | Mouser FR |
| Hall switches + magnets | as Batch 1 | 20 + 30 | ~6 index + ~8 witness + ~6 trigger sensors | as Batch 1 |
| Opto forks / microswitches | as Batch 1 | 6 / 10 | ~6 event locks + door + spares | Gotronic |
| DC gearmotors | as Batch 1 | 7 + 1 spare | E1 ×1 (bell and glass on one motor, a count wheel: `docs/e1-design.md` §15), E2 ×3 (walk, quarters, hours: `docs/e2-design.md` §6), E3, E4, E6 (calendar advance, as in the original) | Gotronic (Pololu) |
| H-bridges | DRV8833-class dual | 4 | 2 motors each (8 motors) | Gotronic / Mouser FR |
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

### Batch 2 — M2 rows from the detailed design [E]

Quantities from `cad/modules/m2_main_dial/` (`docs/m2-design.md` §8). They replace the feasibility
rows and count towards the "ground rod, brass tube, bearings" row above.

| Item | Spec | Qty [E] | How the quantity was counted | Supplier |
|---|---|---|---|---|
| Brass tube, 0.45 mm wall | OD 4, 5, 6, 7, 8, 9 mm | 1 length (≈ 300 mm) of each, plus 1 extra OD 6 | centre stack; OD 6 also for the two differential sleeves | as Batch 1 |
| Ground rod Ø3 | DIN 175 h9 | 0.5 m | fixed centre arbor, 8 differential pins, studs for wheel C, the counting lever and E6's star | as Batch 1 |
| Ground rod Ø5 | DIN 175 h9 | 1.5 m | S, J, I, W, R1 (≈ 100 mm each), 2 worm shafts (≈ 170 mm) | as Batch 1 |
| Rod Ø8 | DIN 175 h9 | 0.1 m | 6 roller studs | as Batch 1 |
| Rod Ø2 | steel pin | 0.1 m | 3 lock pins for the idle v1.5 tubes; the setter rocker's pivot pin | as Batch 1 |
| Silver steel rod Ø1.5 | DIN 175 h9 | 0.2 m | calendar station: counting-lever pin (24 mm), stop and spring-anchor pins (16 mm each), click pivot (8 mm), satellite pin and step pin; E6: star jumper pivot (9 mm), stop-lever pivot (7 mm) (m2-design §6) | Ameco, as Batch 1 (⚠ verify Ø1.5 in stock) |
| Compression spring, stainless AISI 302 (inch-based size, accepted: D13) | **Sodemann C01800120500S**: d 0.30, De 4.57, Di 3.97, L0 12.70, R 0.25 N/mm | 1 (+ 2 spares) | set-ramp plunger: 0.13 N at rest, 0.48 N lifted (m2-design §6, *Steel springs*) | [ressorts-sodemann.fr](https://www.ressorts-sodemann.fr/c01800120500s), ships to FR (⚠ pack size and price: check when ordering) |
| Extension spring, stainless AISI 302 (inch-based size, accepted: D13) | **Sodemann E00940110500S**: d 0.28, De 2.39, L0 12.70, F0 0.22 N, R 0.17 N/mm | 1 (+ 2 spares) | counting-lever return: 0.73 N at rest, 1.03 N at full stroke | [ressorts-sodemann.fr](https://www.ressorts-sodemann.fr/e00940110500s) (⚠ check that L0 is inside the hooks) |
| Spring wire, EN 10270-1 DH, straight | Ø0.4 and Ø0.5, 1 m bars | 1 bar of each | Ø0.4: rocker detent, satellite detent, E6 stop lever. Ø0.5: wheel C click, E6 star jumper (and the fallback's ring jumper). | Gutekunst 23514 / 23516 ([federnshop.com](https://www.federnshop.com/en/products/steel-wire-bars.html), ⚠ not verified: the site refused this session) or Boley 538805 / 538807 ([boley.de](https://www.boley.de/en/shop/1906.spring-steel-wires), 5 m bundles) |
| Cyanoacrylate glue + Ø0.6 drill, pin vice | — | 1 | to fix the wire springs in their printed blocks | local |
| Push-on lock washers for Ø3 shafts | Starlock type, steel | 4 (+ spares) | axial retention on the wheel C and counting-lever studs | [Bossard Starlock 6110](https://www.bossard.com/eshop/ch-fr/outils-et-pour-elements-de-securite-et-antidesserrage/starlock-6110/p/38905) (⚠ verify the Ø3 size) |
| Bearing MR85ZZ | 5 × 8 × 2.5 | 13 | 9 plate seats + 4 worm pillow blocks | as Batch 1 |
| Bearing 688ZZ | 8 × 16 × 5 | 6 | calendar-ring rollers | as Batch 1 |
| Slotted opto switch | **Vishay TCST1202**: 3.1 mm gap, 0.5 mm slit, phototransistor, through-hole (TCST1103 fits the same pocket, with less margin) | 1 (+ 1 spare) | calendar stop lever (m2-design §6, *E6*) | RS 145-2215 (about €0.83 each by the tube of 85, on [RS Benelux](https://benl.rs-online.com/web/p/slotted-optical-switches/1452215)) or Farnell 1470058 (⚠ single-unit price and FR stock: check when ordering) |
| Resistors, metal film 0.25 W | 100 Ω and 10 kΩ | 1 + 1 | the stop opto's LED and its pull-up to 3.3 V | local / RS FR |
| Screws | M1.6 × 4, ISO 7045 pan head, A2 | 2 (+ spares) | E6 gearmotor to its bracket (Pololu face holes) | Accu / RS FR |
| Reflective opto | TCRT5000-class | 1 | 1 March witness | Gotronic |
| Hall + magnet | DRV5032 + 5 × 2 mm | 3 + 3 | index (daily arbor), Moon-tube witness, E6 home | as Batch 1 |
| NEMA 17 + TMC2209; E6 gearmotor | as above; E6 is the **298:1** HP 6 V (#994), not the 100:1 | (already counted) | M2 stepper; calendar advance (Paul, 4 Nov 2026) | Gotronic (Pololu) |
| Screws, countersunk | M3 × 10, ISO 10642, A2 | 3 + 12 + 5 | carrier to the M2 front plate (3); carrier splice plates (3 × 4) (PR #5 frame); E6 bracket (3) and the stop lever's bridge (2) | 3DJake / RS FR |
| Heat-set inserts M3 | ruthex | 20 | in the front plate, carrier segments, E6 bracket and the stop lever's bridge, for the screws above | as Batch 1 |
| Screws + washers M5 | M5 × 16, ISO 7380, A2 | 3 | carrier tabs to the works' internal frame (D12 R5) | as Batch 1 |
| Motor mount (D16) | M3 × 6 ISO 7380 × 4 (motor to adapter); M3 × 8 × 2 (adapter to back plate); M3 heat-set inserts no longer than 4 mm × 2 | 1 set | the NEMA 17 plugs in from behind (`docs/m2-design.md` §2) | as the M1 rows |
| Wall restraint brackets + anchors for stone | per fixing design | TBD | D6; wall material TBD | TBD |
| Clock oil | horological | 1 | brass tube stacks | TBD |
| Filament | PLA (gears, display), PETG (structure) | TBD | from slicer estimates per module | TBD |

### Batch 2 — M1 rows from the detailed design [E]

Quantities from `cad/modules/m1_time/` (`docs/m1-design.md` §9). They count towards the "ground
rod, brass tube, bearings, fasteners" and "Hall switches + magnets" rows above. The motors plug in
from behind on adapter plates (D16, `docs/m1-design.md` §10).

| Item | Spec | Qty [E] | How the quantity was counted | Supplier |
|---|---|---|---|---|
| Ground rod Ø3 | DIN 175 h9 | 0.2 m | centre arbor 51 mm, GM 46 mm, SM 19 mm, studs X 19 mm and N 13 mm [D: model] | as Batch 1 |
| Brass tube, 0.45 mm wall | OD 4, 5, 6 mm | 35 / 20 / 8 mm | silver minute, silver hour, gilt hour [D: model]; cut from the Batch 1 lengths | as Batch 1 |
| Bearing MR63ZZ | 3 × 6 × 2.5 | 1 | the centre arbor's rear bearing, in a back-plate boss | as Batch 1 |
| Shaft collar with grub screw | bore Ø3 and Ø4, OD ≤ 9, about 2 mm wide | 1 + 1 | the clutches' preload (`docs/m1-design.md` §9.5) | ⚠ not yet found in these small sizes: Accu / RS FR to check; otherwise a printed collar with an M2 grub screw |
| Wave washer | for Ø3 and Ø4 shafts, OD ≤ 8, 1.7–7.5 N at working height | 2 + spares | one per clutch | Accu FR (wave washers, Batch 1 link) ⚠ load to check |
| Push-on lock washer for Ø3 | Starlock type | 2 (+ spares) | the noon wheels' forward stops | as the M2 row (Bossard Starlock 6110, ⚠ verify the Ø3 size) |
| Hall switch DRV5032 | on a small board, as Batch 1 | 6 | quarters, hour (M1b index), noon, M1 index, two witnesses | as Batch 1 |
| Magnets | NdFeB disc 5 × 2 mm | 17 | 9 in the mechanism; 8 for the dial mount (4 feet, 4 bezel) | as Batch 1 |
| NEMA 17 + TMC2209 | as Batch 1 | (already counted) | M1 and M1b | as Batch 1 |
| Screws | M3 × 6, ISO 7380 (button head), A2 | 8 | each motor to its adapter plate, heads in counterbores (D16) | as Batch 1 |
| Screws | M3 × 8, ISO 7380 or 4762, A2 | 4 | each adapter to the back plate, from behind (D16) | as Batch 1 |
| Heat-set inserts M3 | **no longer than 4 mm** (the back plate is 4 mm thick) | 4 | the adapter screws (D16) | ⚠ ruthex or CNC Kitchen short M3: check the length and the hole size |
| Screws + nuts | M3 × 40, ISO 4762, A2, with nuts and washers | 4 | the pillars, through both plates | as Batch 1 |
| Screws + washers M5 | M5 × 16, ISO 7380, A2 | 2 | the cassette's tabs to the works' internal frame (D12 R5) | as Batch 1 |
| Glue | epoxy or cyanoacrylate | — | the dial into its bezel; the magnets into their pockets | local |

### Batch 2 — E2 rows, detail design part 1 [E]

Quantities from `cad/modules/e2_ages/` (`docs/e2-design.md` §10). Part 2a updates the two rod rows
and adds the drives' parts below.

| Item | Spec | Qty [E] | How the quantity was counted | Supplier |
|---|---|---|---|---|
| Bearing 688ZZ | 8 × 16 × 5 | 7 | the ring: 4 support rollers, 3 guide rollers | as Batch 1 |
| Rod Ø8 | DIN 175 h9 | 0.15 m | 7 roller studs | as Batch 1 |
| Rod Ø3 | DIN 175 h9 | 0.05 m | the waiting stop's shaft, 25 mm (part 2a) [D: model] | as Batch 1 |
| Rod Ø5 | DIN 175 h9 | 0.25 m | the walk shaft 48 mm, the program shaft 22 mm, the state arbor 110.5 mm (part 2a) [D: model] | as Batch 1 |
| Bells | small brass bowl bells, Ø ≈ 21 mm, about 15 mm deep, mouth down | 2 (+ 1 spare) | the ages' bell and Death's bell [E: photo] | ⚠ not yet found; to source |

### Batch 2 — E2 rows, detail design part 2a [E]

From `cad/modules/e2_ages/drives.py` (`docs/e2-design.md` §11): the stops, the walk drive and the
state module. Rows marked "counted" are already in the Batch 2 totals above.

| Item | Spec | Qty [E] | How the quantity was counted | Supplier |
|---|---|---|---|---|
| Bearing MR85ZZ | 5 × 8 × 2.5 | 6 | the walk shaft 2, the program shaft 2, the state arbor 2 | as Batch 1 |
| Rod Ø4 | DIN 175 h9 | 0.05 m | the lay stud, 20 mm | as Batch 1 |
| Brass square rod | 3 × 3 mm | 0.1 m | the bell stop's shaft, 50 mm (it slides in a keyed sleeve) | ⚠ model-making suppliers stock it (e.g. Albion Alloys); to source in France |
| Steel pins | Ø2 × 6 and Ø2.5 × 6, ISO 2338 m6 (or cut from silver steel) | 1 + 1 | the crank pin; the push rod's follower pin | as Batch 1 |
| Push-on lock washers | Starlock type for Ø5 / for Ø4 | 2 / 1 (+ spares) | the walk shaft and the state arbor / the lay stud | as the M2 row (Bossard Starlock 6110, ⚠ verify the sizes) |
| Wave washer | for Ø5, OD ≤ 10 | 1 (+ spares) | the walk clutch's preload | Accu FR (as the M1 row) ⚠ load to set on the test rig |
| Micro metal gearmotor | 12 × 10 mm, Ø3 D-shaft, ≈ 32 rpm under load (1000:1 HP 6 V class) | counted (one of the 8 DC gearmotors) | E2's walk | Gotronic (Pololu) ⚠ check its length (34.5 mm modelled) and shaft (9 mm) |
| Subminiature roller-lever microswitch | about 12.8 × 5.8 × 6.5 mm | counted (Batch 2 microswitches) | the walk program's lock | Gotronic ⚠ choose |
| Hall switch DRV5032 | on a small board, as Batch 1 | counted (3 of Batch 2's Halls) | the bell station, the state index, the hour witness | as Batch 1 |
| Magnets | NdFeB disc 5 × 2 mm | 6 | 4 in the ring (one under each age), the index, the witness | as Batch 1 |
| NEMA 17, TMC2209, D16 mount set | as the D16 row | counted | E2's state arbor | as Batch 1 |
| Screws M2 × 6 + M2 heat-set inserts | A2 | 12 + 12 | the walk and program bearing blocks 2 + 2, the gearmotor bracket 2, the rod guides 4, the lock switch's bracket 2 | as Batch 1 |
| Screws M3 × 8 + M3 heat-set inserts | A2 | 6 + 6 | the state module's left plate, right block and motor plate, 2 each, under the deck | as Batch 1 |

### Batch 2 — E2 rows, detail design part 2b [E]

From `cad/modules/e2_ages/strikers.py` (`docs/e2-design.md` §12): the quarter and hour counting trains.
Rows marked "counted" are already in the Batch 2 totals above.

| Item | Spec | Qty [E] | How the quantity was counted | Supplier |
|---|---|---|---|---|
| Bearing MR85ZZ | 5 × 8 × 2.5 | 4 | two per strike shaft | as Batch 1 |
| Rod Ø5 | DIN 175 h9 | 0.1 m | the two strike shafts, ≈ 41 mm each | as Batch 1 |
| Rod Ø3 | DIN 175 h9 | 0.15 m | the racks' common stud (≈ 51 mm), two hook studs (≈ 12 mm), the quarter release shaft (≈ 33 mm; PR #21 review) | as Batch 1 |
| Rod Ø2 (or pins ISO 2338) | silver steel | 0.15 m | two feed-lever pins, two guard pins, two spring pins (≈ 54 mm); the hour trip shaft (≈ 37 mm), its stop pin, the quarter rack's trip pin and the release follower's pin (≈ 25 mm; PR #21 review) | as Batch 1 |
| Micro metal gearmotor | 12 × 10 mm, Ø3 D-shaft, ≈ 40 rpm under load | counted (E2's quarter and hour trains) | one per strike shaft, through 12/24 | Gotronic (Pololu) ⚠ choose the ratio (e.g. 380:1 at reduced voltage) |
| Subminiature roller-lever microswitch | as part 2a | counted (Batch 2 microswitches) | two lock switches, one cue switch | Gotronic ⚠ choose |
| Slotted opto Vishay TCST1202 | as M2's E6 | counted (Batch 2 opto forks) | one per rack: home (gathered) | as the M2 row |
| Screws M1.6 × 4 | A2 | 4 | the gearmotors' faces to their plates | ⚠ check the motor's face threads |
| Extension spring Sodemann E00940110500S | as the M2 row (D13) | 2 (+ 1 spare) | one rack spring per counting train | Sodemann (as the M2 row) |
| Screws M3 × 8 + M3 heat-set inserts | A2 | 8 + 8 | the middle and right strike plates and the two motor plates, 2 each, under the deck | as Batch 1 |

### Batch 2 — controller rows from the Phase 3 gate [E]

From `docs/firmware-design.md` §3–4 (decisions F2–F5, accepted 8 Nov 2026, PR #19). Where a row
below gives a different quantity from a row above, this one is newer: MCP23017 3, not 2; DRV8833
5, not 4. F1 (accepted): a carrier PCB, ordered after the bench prototype; its row is added with the KiCad PR.

| Item | Spec | Qty [E] | How the quantity was counted | Supplier |
|---|---|---|---|---|
| MCP23017 I/O expander | I²C, 16 I/O, breakout | 3 (supersedes 2) | 31 inputs in v1, 37 by v2, plus spares (firmware-design §3.5) | Mouser FR ⚠ |
| PCA9685 PWM expander | I²C, 16 channels, breakout | 1 | one channel per event motor, 9 by v2 (§3.4) | Mouser FR / Gotronic ⚠ |
| DRV8833 dual H-bridge | breakout; check it uses the PWP package (1.5 A RMS per bridge [S: TI SLVSAR1E p. 1]) | 5 (supersedes 4) | 9 motors by v2, 2 per board, 1 spare channel | Gotronic / Mouser FR ⚠ |
| Buck converter 24 → 6 V | ≥ 5 A | 1 | event-motor rail (F5) | ⚠ to choose |
| Buck converter 24 → 5 V | ≥ 2 A | (counted: Batch 1 row) | logic rail | as Batch 1 |
| RTC | RV-3028-C7 breakout with supercapacitor | 1 | F3 (replaces the "or DS3231" choice in Batch 1) | Mouser FR / Melopero ⚠ |
| FRAM | MB85RC256V, 32 KB I²C, breakout (Adafruit #1895 class) | 1 (+ the Batch 1 one for the rig) | state record (firmware-design §9.4) | Mouser FR ⚠ |
| Hall switch variant | **DRV5032FC**: omnipolar, open drain, 20 Hz [S: TI SLVSDC7H Table 4-1] | — | names the variant for the Batch 1 and 2 Hall rows | as Batch 1 |
| Comparator + divider | 24 V power-fail detect, threshold ≈ 20 V | 1 | firmware-design §3.7 | ⚠ to choose |
| Electrolytic capacitor | 35 V, 470 µF (fit); footprint for 2 × 2200 µF (fallback, F4) | 1 (+ 2 if the fallback is needed) | power-fail hold-up | local / RS FR |
| Module connectors | Molex Micro-Fit 3.0 dual-row pairs (JST-XH for small counts), keyed per module | ≈ 10 pairs, 4–22 pins | per-module table, firmware-design §4 | ⚠ to choose; check the current rating |

### Batch 2 — E1 rows, detail design part 1 [E]

From `cad/modules/e1_angels/mechanism.py` (`docs/e1-design.md` §16): the bell tower, the cross shaft, the glass
tower. Rows marked "counted" are already in the Batch 2 totals above. E1 now needs one gearmotor, not two. The
H-bridge row's four duals keep a spare channel.

| Item | Spec | Qty [E] | How the quantity was counted | Supplier |
|---|---|---|---|---|
| Bearing MR85ZZ | 5 × 8 × 2.5 | 10 | the bell tower's four arbors 2 each; the crank's stub 2 | as Batch 1 |
| Bearing MR63ZZ | 3 × 6 × 2.5 | 4 | the shoulder arbor 2; the glass arbor 2 | as Batch 1 |
| Rod Ø5 | DIN 175 h9 | 0.35 m | bell shaft 38, intermediate 38, count arbor 38, left stub 43, cross shaft 166, right stub 15.5 mm [D: model] | as Batch 1 |
| Rod Ø4 | DIN 175 h9 | 0.2 m | the slider rod, 192 mm [D: model] | as Batch 1 |
| Rod Ø3 | DIN 175 h9 | 0.2 m | the glass arbor 120, the shoulder arbor 49, the lever's pivot pin 9 mm [D: model] | as Batch 1 |
| Steel pin | Ø3 × 7.5, ISO 2338 m6 (or cut from silver steel) | 1 | the crank pin | as Batch 1 |
| Steel wire | Ø0.5, stainless or piano wire | 0.2 m | the follower lever to the shoulder lever (≈ 70 mm) | model shops ⚠ |
| Extension spring | small steel, Ø ≈ 2.4, ≈ 9 mm long (D13) | 1 (+ 2 spares) | the sceptre's flick; rate set on the test bell | Sodemann / Accu FR ⚠ choose |
| Leaf spring | thin spring steel strip, 0.2–0.3 × 2 mm | 1 (+ spares) | the cross shaft's detent | ⚠ to choose |
| Bell | small brass bell, Ø ≈ 20–25, **a little lower in pitch than E2's** (`docs/e1-design.md` §12) | 1 (+ 1 spare) | the genie's hand bell. Buy a few candidates with E2's and choose by ear | ⚠ not yet found; to source |
| Miniature hourglass | red sand, ≈ 19–20 mm tall, ≈ 9 mm wide | 1 (+ 1 spare) | the glass genie's glass | ⚠ to source (charm or pendant sellers, EU) |
| Micro metal gearmotor | ≈ 200 rpm under load (100:1 HP 6 V class) | counted (one of the 7 DC gearmotors) | E1, bell and glass | Gotronic (Pololu) ⚠ check the speed under load |
| Subminiature roller-lever microswitch | as E2's | counted (2 of Batch 2's microswitches) | the bell lock, the count wheel's home | Gotronic ⚠ choose |
| Screws M3 × 30 + nuts | A2 | 4 + 4 | the bell tower's four pillars | as Batch 1 |
| Screws M2 × 6 + M2 heat-set inserts | A2 | 12 + 12 | the gearmotor's saddle 4 (on the plates' top edges), the two switches 4, the slider's guides 4 | as Batch 1 |
| Screws M3 × 8 + M3 heat-set inserts | A2 | 8 + 8 | the shoulder bracket 2, the crank block 2, the glass arbor's arms 4 | as Batch 1 |

### Batch 2 — M7 rows from the detailed design [E]

Quantities from `cad/modules/m7_weekdays/` (`docs/m7-design.md` §13). They count towards the
"ground rod, brass tube, bearings, fasteners" and "Hall switches + magnets" rows above. M7 has no
motor: it is driven by M2's arbor W.

| Item | Spec | Qty [E] | How the quantity was counted | Supplier |
|---|---|---|---|---|
| Ground rod Ø5 | DIN 175 h9 | 0.16 m | stub 49 mm, lay shaft 109 mm [D: model] | as Batch 1 |
| Bearing MR85ZZ | 5 × 8 × 2.5 | 4 | stub ×2, lay shaft ×2 | as Batch 1 |
| Bearing 61806 | 30 × 42 × 7, thin section | 1 | the turntable, on the deck's Ø30 post | as the D4 set (123roulement / RS FR ⚠ check) |
| Hall switch DRV5032 + magnet 5 × 2 | as Batch 1 | 1 + 1 | the Sunday witness (counted in Batch 2's 20 + 30) | as Batch 1 |
| Screws + washers M5 | M5 × 16, ISO 7380, A2 | 2 | the bracket's tabs to the works' internal frame (D12 R5) | as Batch 1 |
| Screws M3 + heat-set inserts | M3 × 10, ISO 7380 | 4 + 4 | the deck to the spine [E: not yet modelled as holes] | as Batch 1 |
| Filament | PETG (deck, bracket), PLA (gears, turntable, rail, figures) | ≈ 0.3 kg | [E: 546 cm³ of printed parts in the model × 1.25 g/cm³ = 0.68 kg if solid; about 40–50 % of that with walls and 20 % infill] | as Batch 1 |

## Batch 3 — v1.5 / v2

| Item | Qty [E] | Note |
|---|---|---|
| NEMA 17 + TMC2209 for M3 (equations) | 1 + 1 | D5 v1.5 |
| DC gearmotor + H-bridge channel for E5 (computus) | 1 | D5 v2 |
| Sensors for M3 / M4 witnesses and locks | ~6 | — |
| Computus visible frame: brass or steel plate and pillars, metric | TBD | D12 R4. v2. Plates cut and drilled to drawings from `cad/modules/M4`. |
