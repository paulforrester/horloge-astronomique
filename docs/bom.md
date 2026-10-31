# Running hardware list (BOM)

One list for the whole project, so purchases can be consolidated into a few orders. Quantities
are filled in as modules are designed. Nothing here needs buying yet. Batch 1 (§1) is proposed for
the local tolerance tests and the Phase 2 test rig.

**About the supplier data.** Supplier facts were gathered from search snippets only (retailer
sites were blocked in the Phase 0 session). They are marked **⚠ verify**. Prices change; open each
link before ordering.

- Metric sizes only. Prefer suppliers in France or the EU.
- UK suppliers mean customs and VAT on delivery to France (post-Brexit).

## 0. Already owned (Paul: please confirm quantities)

| Item | Qty | Use |
|---|---|---|
| Arduino Mega 2560 + RAMPS 1.4 | ? | Phase 2 test-rig controller (D3, option C) |
| TMC2209 stepstick drivers | ? | All steppers |
| NEMA 17 steppers | ? | Module steppers (Phase 2 sizes each one) |
| ESP32 boards | ? | Check whether one is an ESP32-S3 (D3) |
| Bambu Lab H2D, 0.4 mm nozzle | 1 | — |

## 1. Batch 1 — tolerance tests and test rig (proposed; order after the Phase 2 test-rig design)

| Item | Spec | Qty (est.) | Candidate supplier | Link | Notes |
|---|---|---|---|---|---|
| 0.2 mm nozzle for the H2D | Bambu H2D hotend, 0.2 mm | 1 | Bambu Lab EU store | — | Already planned (`CLAUDE.md`) |
| Ground rod Ø3, Ø5, Ø8 | Silver steel DIN 175 (h9) | 1 m each | Ameco (CZ) | https://eshop.ameco.cz/products/en/1630/559/g1433/64720400/ | ⚠ verify sizes in stock |
| Brass tube set, 0.45 mm wall | OD 4, 5, 6, 7, 8, 9, 10 mm (nests over Ø3 rod, 0.10 mm clearance [D]) | 1 of each | Albion Alloys BTxM via Chronos (UK), Conrad (6, 7, 9 mm) | https://www.chronos.ltd.uk/product-category/round-square-tube-sheet-metal-ptfe-nylon/albion-alloys-precision-metals/albion-alloys-standard-brass-round-tube-metric/ · https://www.conrad.com/en/p/brass-tube-rail-x-l-6-mm-x-500-mm-inside-diameter-51-mm-297321.html | ⚠ no French Albion stockist found |
| Bearings, sample set | MR63ZZ, MR85ZZ, 685ZZ, 688ZZ, 6701ZZ | 10 each | 3DJake (AT), RS FR, kugellager-express (DE) | https://www.3djake.ch/fr-CH/3djake/roulements-a-billes?sai=33685 · https://fr.rs-online.com/web/p/roulements-a-billes/0313140 | Measure real ODs to set seat sizes (D4) |
| Sintered-bronze and igus bushes | Bore 3 and 5 mm | assortment | RS FR (528-238, 528-923); igus free sample box | https://docs.rs-online.com/1a4c/A700000015780986.pdf | ⚠ verify |
| Heat-set inserts | ruthex M2, M2.5, M3, M4 | assortment | 3DJake | https://www.3djake.ch/fr-CH/ruthex/inserts-filetes-m2-m3-m4-m5 | |
| Screws A2-70 | M2–M5, ISO 4762, 14580, 7380 | assortment | 3DJake, RS FR, Accu | https://fabory.com/fr/Norme/Normes-DIN/DIN-912/c/DIN912 | |
| Wave / disc spring washers | for slip-clutch tests on Ø3, Ø5, Ø8 | assortment | Accu FR | https://accu-components.com/fr/shop/composants-de-precision/rondelles-et-entretoises/rondelles-a-ressorts/rondelles-ondulees | Setting mechanism (architecture §7) |
| Hall switches | DRV5032 (or TLE4905L); **not** A3144, which is obsolete [Sn] | 10 | Mouser FR, Gotronic | https://www.ti.com/product/DRV5032 · https://www.gotronic.fr/art-capteur-a-effet-hall-st054-26119.htm | |
| Magnets | NdFeB disc 5 × 2 mm | 20 | supermagnete | https://www.supermagnete.de/eng/disc-magnets-neodymium/disc-magnet-5mm-2mm_S-05-02-N52N | |
| Opto fork | ITR9608-class module | 4 | Gotronic | https://www.gotronic.fr/art-module-capteur-a-fourche-st056-26120.htm | Lock and witness sensing |
| Microswitches | small lever type | 10 | Gotronic / RS | — | Event lock switches |
| DC gearmotor | Pololu micro-metal HP 6 V 100:1 (#1101) | 2 | Gotronic (FR distributor) | https://www.pololu.com/product/1101 | Event-motor noise test (D3) |
| H-bridge | DRV8833-class dual | 2 | Gotronic / Mouser FR | — | |

## 2. Electronics for the clock (Phase 3; candidates)

| Item | Spec | Qty (est.) | Candidate supplier | Link | Notes |
|---|---|---|---|---|---|
| ESP32-S3 dev board | ESP32-S3-DevKitC-1-N8R8 | 1 (+1 spare) | Mouser FR | https://www.mouser.fr/c/semiconductors/?q=esp32-s3 | D3 |
| TMC2209 stepsticks | UART, StealthChop | 6 (+1 spare) | 3DJake (BTT), West3D (FYSETC) | https://www.3djake.ch/fr-CH/bigtreetech/pilote-de-moteur-pas-a-pas | Some may be owned already |
| I/O expander | MCP23017 | 2 | Mouser FR | — | about 27 inputs (architecture §10) |
| RTC | RV-3028-C7 breakout + supercap, **or** DS3231 module | 1 | Mouser FR / Melopero (IT); Gotronic GT584 | https://www.gotronic.fr/art-module-rtc-i2c-ds3231-gt584-36063.htm | DS3231 module: mind the charging diode with a CR2032 [Sn] |
| FRAM | I²C, 32–256 kbit | 1 | Mouser FR | — | Cite the endurance from the datasheet (architecture §8) |
| PSU | Mean Well LRS-100-24 (24 V, 4.5 A) | 1 | Gotronic | https://www.gotronic.fr/art-alimentation-lrs100-24-26283.htm | Sized in Phase 3 |
| Buck 24 → 5 V | ≥ 3 A | 1 | — | — | Logic, sensors, event motors |
| Sound (if D8) | DFPlayer-Mini-class module + small speaker | 1 | — | — | Rooster crow |
| Connectors | JST-XH or Micro-Fit, keyed, one per module | ~12 | — | — | architecture §11 |

## 3. Mechanics for the clock (Phase 2; candidates)

| Item | Spec | Qty | Candidate supplier | Link | Notes |
|---|---|---|---|---|---|
| Thin-section bearings | 61806 (30×42×7), 61808 (40×52×7) | TBD | Rubix, RS | https://ie.rs-online.com/web/p/ball-bearings/2076966 | Large coaxial outputs |
| Adjustable friction clutch | Huco Vari-Tork, 6 mm bore | TBD | RS BE-FR | https://befr.rs-online.com/web/p/friction-clutches/8903033 | Only if a printed clutch is not enough |
| Small bells | for the angel, the ages and Death | TBD | TBD | — | D8; size and pitch TBD |
| Aluminium extrusion | 20 × 20 / 20 × 40 metric slot profile, cut to length | TBD | TBD | — | D6 rack |
| Glazing | 3 mm acrylic (or glass), about 2.25 m² | TBD | TBD | — | D6 |
| Clock oil | horological | 1 | TBD | — | Brass tube stacks |
