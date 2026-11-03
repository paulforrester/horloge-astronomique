# M2 main dial: detailed design

Phase 2, module M2: the main (apparent-time) dial, its hands and trains, the calendar ring and its
New Year station.

- **Built on:** the accepted feasibility layout ([`main-dial-feasibility.md`](main-dial-feasibility.md),
  PR #4).
- **Paul's decisions of 3 Nov 2026:**
  - **60:1 worm** correction inputs;
  - **all of M2** in one design;
  - **two-colour printed dial**.
- **Model:** [`cad/modules/m2_main_dial/`](../cad/modules/m2_main_dial/)
  - `mechanism.py`: trains, differentials, centre stack, plates, motor;
  - `calendar.py` and `calendar_logic.py`: the calendar ring;
  - `dial.py`: the dial face;
  - `full.py`: everything together.
- **Tests:** `cad/tests/test_m2_design.py`, `test_calendar_logic.py`, `test_worm_diff.py`.
- **SketchUp:** `export/sketchup/m2_main_dial.dae`.

**Status: Proposed** (Phase 2 gate). The decisions needed are in §11.

## 1. Result

| Check | Result |
|---|---|
| Interference, all 141 parts, exact B-rep | **0** |
| Fixed parts inside the path of the turning calendar ring (other than its designed readers) | **0** |
| Rotating hands: any two parts on different tubes that could touch at some angle | 0 (feasibility study; same front stack) |
| Calendar logic, day by day, 2026–2426, five different start dates | **0 wrong days**. Every New Year jump is 4 divisions (common) or 3 (leap), including 2100, 2200, 2300 and 2400. |
| Bed fit, single and dual nozzle | every printed part fits. The largest are the plates, 281 × 232 mm. |
| Envelope | x −185 … +196, y −195 … +178, z −162 … +24 mm: inside the M2 bay. Nothing comes within about 18 mm of the floor. **Depth 185 mm.** |
| Parts | 141 in the model: 87 printed, 52 bought (plus 2 v1.5 space claims) |
| Motor torque | ≈ 2.9 mN·m at the motor, **≈ 50×** margin at 0.5 A [E, §9] |

<p align="center"><img src="img/m2/m2_front.png" width="420" alt="M2 front"> <img src="img/m2/m2_three_quarter.png" width="420" alt="M2 three-quarter"></p>
<p align="center"><img src="img/m2/m2_differentials.png" width="420" alt="Differentials and worms"> <img src="img/m2/m2_calendar_station.png" width="420" alt="Calendar station"></p>
<p align="center"><img src="img/m2/m2_rear.png" width="420" alt="M2 rear"> <img src="img/m2/dial.png" width="420" alt="Two-colour dial"></p>

## 2. Kinematics

Signs: + is counter-clockwise seen from the front. An external mesh reverses; a differential with
its carrier still reverses.

```
motor --12/48--> R1 --12/72--> I  (daily arbor, 1 rev per mean day; module 1.25, 6 mm faces)
I --84/84--> S --[Sun differential]--> S sleeve --48/48--> Sun tube    (Sun hand + disc)
                                                  --48/48--> shadow tube (shadow arm, in step)
I --154/169--> J --[Moon differential]--> J sleeve --88/83--> Moon tube  (Moon hand)
S --12/84--> W  (weekday output to M7, 1 rev per 7 days)
```

- **Senses.** The Sun, shadow and Moon tubes all turn with sense −1 × motor (the model checks
  this). Firmware sets the motor direction so that the hands turn clockwise.
- **Trains from `spec/clock.yaml`:** `M2.moon_hand` 154/169 × 88/83, and `M2.weekday` 12/84 (exact).
- **New 1:1 pairs** (exact): I→S 84/84 and the two 48/48 pairs.
- **The 24:1 reduction** is 12/48 × 12/72 (exact, architecture §3).
- **Positions** (mm, dial centre = 0):

| Arbor | Position | Why there |
|---|---|---|
| S, Sun lay shaft | (−41.6, 24.0), 48 from the centre at 150° | 48/48 to the tubes; its differential lies behind the bridge |
| J, Moon intermediate | (74.0, −42.8), 85.5 at −30° | 88/83 to the Moon tube |
| I, daily arbor | (−87.4, −46.4) | 161.5 from J (154/169) and 84 from S (84/84). The 84/84, rather than 80/80, keeps S's arbor clear of the 154-tooth wheel. |
| W, weekday | (−75.5, 57.9) | 48 from S; its arbor leaves the back plate at the top left, towards M7 |
| R1, motor | (−105.4, −95.7), (−140.6, −108.6) | lower left, behind the back plate |
| C, R (v1.5 lay shafts) | 48 at 60° and 100° | clear of the big wheels and the Sun worm; bearing holes are drilled undersize now |

**Depth stack** (dial face = 0):

| Level | z (mm) |
|---|---|
| Hands and hemisphere dome | +0.8 … +23.8 |
| Dial (two-colour) | −3 … 0 |
| Calendar ring, rollers, carrier | −8.5 … 0 (ring); carrier −10.9 … −8.8 |
| Front plate | −15 … −11 |
| Centre wheels: sunset, sunrise, Sun, cam, Moon (83 T), shadow | −21 … −47 |
| Bridge (fixed centre arbor) | −56 … −53 |
| Differentials (Sun on S, Moon on J), worm wheels at the front | −80 … −57 |
| 154/169 | −86 … −82 |
| 84/84 | −92 … −88 |
| Reduction 12/72; weekday 12/84 | −100 … −94 |
| Reduction 12/48 | −108 … −102 |
| Back plate | −114 … −110 |
| NEMA 17 | −162 … −114 |

## 3. Changes from the feasibility layout and the spec

1. **The latitude (node) cam is driven directly from the daily arbor**, not referenced to the Sun
   hand.
   - The node's position on the dial follows sidereal time (mean time), as the Moon's does. Taking
     it from the Sun hand would wrongly add the equation of time once the Sun is corrected in v1.5,
     about ±4°.
   - A three-mesh train does it: **98/99 × 71/79 × 62/55** = 1 + 1/eclipse year turns per mean
     day, **+0.004°/century** [D: `tools/ratios`].
   - That removes a third differential. `spec/clock.yaml` `M2.node_cam` is updated (v1.5, with
     train routing in the v1.5 M2 update).
2. **The weekday output** is a horizontal Ø5 arbor turning once per 7 days. M7 turns it upward
   with its own right-angle drive, which keeps bevel gears out of M2. Architecture §4 is updated.
3. The daily arbor I and the lay shafts were placed to clear the 154/169 wheels and the worm
   shafts. The bridge turned to 20° so its pillars clear S, C, R and J.
4. Both plates share one 281 × 232 mm outline, with six pillars at points the model found clear of
   every gear.

## 4. Differentials and the M3 interface (architecture §13)

**Differential** (`cad/lib/differential.py`): spur gears only.
- Two 20-tooth suns, and two pairs of 18-tooth planets that mesh with each other in a middle level.
- Output = 2 × carrier − input.
- Planets on Ø3 pins in the carrier. The carrier's front plate is a **60-tooth worm wheel**.
- The input sun is pinned to the shaft (S, J); the output sun is pressed on a brass sleeve (OD 6)
  that carries the output gears forward.
- **Checks:** no interference; every mesh engaged.

**Worm** (`cad/lib/worm.py`): module 1, Ø12 pitch, single start.
- Lead angle 4.76°, tan = 0.083. It self-locks for any PLA friction coefficient above that
  (typically 0.2–0.35 [E]), so **in v1 the still worm is the lock**: no key.
- The wheel is helical (4.76°) with a throat cut by the worm's tip torus.
- Tested at four worm angles: no interference, and engaged.

**Gain:**
- 1 worm turn = 1 tooth = 6° of carrier = **12° at the Sun hand**, and 12 × 88/83 = **12.72° at
  the Moon hand**.
- M3 therefore turns its shaft by at most ±0.34 turn for the Sun's ±4.1° [D].
- 0.3° of play in the shaft is 0.01° at the hand [D].
- Recorded in `spec/clock.yaml` → `interfaces`.

**Worm shafts.** Ø5, along +X at z −60, y +60 (Sun) and y −78.8 (Moon). Each runs in two pillow
blocks (MR85ZZ) and ends in a keyed dog coupling at x = 135, facing the equations bay.

**Torque on the worm [E]:**
- The carrier carries twice the output torque.
- With 10–20 N·mm at the output sun and about 0.25 worm efficiency [E], M3 needs about 2–3 N·mm
  at the shaft.

## 5. Centre stack and hands

- Six brass tubes (OD 4–9) on a fixed Ø3 arbor held by the bridge, levels as in the feasibility
  study.
- **v1 builds** the Sun hand with its disc and the shadow arm with its disc (k = 4 sizes: 4.7 and
  12.2 mm), the Moon hand with its ball (4.5 mm), and the dome.
- **Hand hubs** are split collets on their tubes: a friction clutch for setting (architecture
  §7). The grip is set by the collet interference, which the tolerance coupons give.
- **The idle v1.5 tubes** (cam, sunrise, sunset) are in the stack from v1 with their 48-tooth
  wheels. Each is held by a Ø2 **lock pin** through its wheel into the front plate, so v1.5 adds
  drives without dismantling the stack.
- **v1.5 still to add:** the cam plate, the Moon-hand slide with its 4:1 lever, the phase ball's
  drive, and the sunrise/sunset hands with their sectors and yearly cam. The space is reserved.

## 6. Calendar ring and New Year station

**Ring** [S: ELS i4 at 1:8]:
- Ø 341 × 26 mm, 368 divisions, in 4 printed segments joined at day boundaries.
- It runs on 6 rollers (688ZZ on Ø8 studs) from a rear skirt.
- A thin rear lip carries **368 ratchet teeth, one per division**.
- Ring and sector together are about 150 g of PLA at 100 % infill [D: model volume 122 cm³].

**Layout of the 368 divisions** (`calendar_logic.py`):

| Divisions | Content |
|---|---|
| 0, 1, 2 | "COMMENCEMENT DE L'ANNÉE" … "commune" (on d = 2) |
| 3 … 61 | movable sector, 1 Jan … 28 Feb, in its common-year position |
| 61 | "29 Feb", printed on the fixed ring, covered by the sector in common years |
| 62 … 367 | fixed, 1 Mar … 31 Dec |

- **In a leap year** the sector slides back one division. It covers "commune" and uncovers 29 Feb,
  as Ungerer describes [S: ELS i4].

**Each midnight:**
1. The index sensor on the daily arbor (the time train) releases E6 (rule 4).
2. E6 is a small gearmotor with a crank and pawl. One crank turn is one ratchet tooth, one
   division. A jumper holds the ring between strokes, and a lock switch stops E6 at the crank's
   home.
3. **The stop lever at the pointer** keeps E6 running while it is held up:
   - fixed bumps (Ungerer's projection S) at d = 0 and 1;
   - **a lug on the sector**, one division before its first day. It sits at d = 2 in common years
     (jump 4) and at d = 1 in leap years (jump 3).
   - So **the sector's position alone decides 3 or 4**. Ungerer's separate cam E is not needed.

**Year counter (station at 6 o'clock, fixed on the carrier):**
- **Wheel C** (100 positions, one per year; 100-tooth gear at module 0.8) is advanced each April by
  a pin on the ring at d = 0. The pin pushes a 10-point star, and a 10-tooth pinion on the star's
  arbor turns C. This is Ungerer's star-and-rake principle with a fixed counter.
- **24 leap bumps** sit at positions 4 … 96.
- **A 4-position satellite**, turned a quarter turn per century by a pin on C, supplies the leap
  bump at x00 when x00 is divisible by 400.
- **The follower** reads C and the satellite.
- **In May the sector's tab passes the setter**, a railway-switch guide steered by the follower. It
  puts the sector in the leap or common position for the coming year.
- Everything acts between 1 March and 31 December, so it never disturbs a date being shown (the
  test checks the timing).

**Radial tracks behind the ring.** Each track has one reader, so nothing triggers the wrong reader.

| Track | r (mm) | Depth | Reader |
|---|---|---|---|
| 1 March witness flag | 148–149.5 | deep | reflective opto at the pointer (architecture §6, updated) |
| Stop-lever track: rim, bumps S, sector lug | 150–154 | rim at −6.5, bumps to −8.3 | stop lever at the pointer |
| Counter pin | 156.25 | full depth | 10-point star at the station (deep layer) |
| Sector tab | 159–162 | shallow layer only | setter at the station. It passes over the star. |

- **Station position.** The station sits 92 divisions (90°) after the pointer. It and wheel C are
  kept at least 195 mm below the dial centre, about 18 mm above the floor [E].
- **Setting** (architecture §7): turn the ring to the date (lift the jumper), set the sector, and
  set wheel C and the satellite to the year, as `calendar_logic.initial_state` does.

## 7. Dial (two-colour print)

- **Field (azure):** the Ø 287.5 disc with raised inlays.
- **Hour ring (silver):** r 128–143.75, 0.8 mm, with the 24 Roman numerals (I–XII twice, 7 mm
  tall, 1 mm strokes) and the ticks cut through it.
- **Ticks:** quarter hours long, 5 minutes short. The azure inlays fill the cuts flush, so the
  numerals read azure on silver [S: DA "peint en azur … cercle en argent"].
- **No font is needed:** the numerals are built from straight strokes.
- **Noon is at the top** [E: convention, to be confirmed on a photo].

## 8. Print and parts notes

**Orientation:**
- plates, carrier segments, ring segments (face down), the dial (face up, two filaments) and the
  hands lie flat;
- gears lie flat, hub up;
- differential planets stand on end;
- the worm stands vertical on its end (no supports; the 4.76° thread overhang is fine);
- the worm wheel lies flat.

**Materials:**
- PETG: plates, bridge, pillars, carrier, pillow blocks;
- PLA: gears, dial, ring, hands;
- nylon is an option for the worm and worm wheel if wear shows on the test rig.

**Bought:**
- Ø5 rod: S, J, I, W, R1, the motor shaft and 2 worm shafts;
- Ø3 rod: fixed arbor, differential pins, C and star arbors;
- Ø8 studs for the rollers; Ø2 lock pins;
- brass tubes OD 4–9 for the stack, plus OD 6 sleeves;
- MR85ZZ bearings: 9 in the plates, 4 in the worm blocks;
- 6 × 688ZZ rollers;
- NEMA 17;
- E6 gearmotor;
- 2 microswitches (E6 lock, stop lever), 1 reflective opto, 2 Hall sensors and magnets.

`bom.md` has the rows.

## 9. Loads [E]

**M2 stepper:**
- Input friction 5 N·mm at I.
- The Sun, shadow and Moon tubes at 10 N·mm each, each through 5 meshes (η 0.9 each).
- The weekday output at 10 N·mm through 2 meshes.
- Total ≈ 57 N·mm at I, so ≈ 2.9 mN·m at the motor through 24:1 (η 0.81).
- **The margin is about 50× at 0.5 A.**
- **Tooth strength** [D: Lewis as in `tools/ratios/strength.py`, allowable 9.75 MPa]. Every
  safety factor is above the accepted minimum of 4:

| Mesh | Running load | Root stress | Safety factor |
|---|---|---|---|
| 84/84, I → S (Sun and shadow loads) | ≈ 30 N·mm | 0.4 MPa | 24 |
| 12/72 at module 1.25, 6 mm (reduction into I) | ≈ 57 N·mm | 0.7 MPa | 14 |
| Differential sun 20 T / planet 18 T | ≈ 20 N·mm at the output | 1.6 MPa | 6 |
| Worm wheel (carrier, 2 × output) | ≈ 40 N·mm | 0.5 MPa | 18 |

**E6:** the ring turns on six ball bearings, so the jumper's spring sets the pawl force. The
gearmotor class from D3 is chosen after the event-motor noise test (BOM Batch 1).

## 10. Not modelled yet

These are reserved or simplified:
- v1.5 drives (cam train routing, sunrise/sunset sectors and yearly cam, Moon slide and lever, phase
  ball);
- the setter switch's guide profile and the follower geometry (they are blocks in the model; the
  logic is proven in `calendar_logic.py`);
- the ring's printed dates;
- the dominical-letter dial (I10: set by hand in v1);
- the v2 feasts arc;
- Apollo's figure.

## 11. Decisions needed from Paul

1. **Approve the M2 design** (§1–§9), including the two changes in §3:
   - the latitude cam driven directly from mean time;
   - the weekday output handed to M7 as a horizontal arbor.
2. **Calendar ring face: what to print and how.**
   - Each division is 2.9 mm wide at the outer edge, so saints' names are out at 1:8.
   - **Recommended:** a two-colour print with day numbers (2 mm), month names in the sector and on
     the fixed part, and the dominical letters. This wants the 0.2 mm nozzle.
   - Alternatives: day numbers every 5 days only (0.4 mm nozzle); or a printed paper band glued on
     (finest, not "object-like").
3. **Dial orientation:** noon at the top? (Assumed; a photo will confirm.)
4. **Wood or print for the carrier's outer support?** The carrier overhangs the M2 front plate at
   the top and right. It needs two brackets from the case (wood holds, never sets geometry: D12),
   or a printed frame. Recommended: brackets from the case.
