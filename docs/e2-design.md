# E2 the four ages and Death: concept gate

Phase 2, module E2: the lower hall of the automata. At each quarter one of the four ages of life
walks out in front of Death and strikes the quarter, answering the genie's strokes (E1). Each hour
Death strikes the hour.

**Status: Detail design, part 1 for review (§10).** The concept was accepted (Paul, PR #15, 6 Nov
2026; the decisions are in §9). Tags as in `docs/reference-notes.md`.

<p align="center"><img src="img/e2/e2_concept.png" width="980" alt="Schematic: the hall in plan with the four ages on a turntable round Death and the two bells; the trains and where the state lives; the order of one show on the hour"></p>

*Schematic only, not to final dimensions. The hall's width is from `docs/envelope.md` §3 [E]. The
hall's plan is scaled from the 2011 photograph below [E].*

<p align="center"><img src="img/e2/original_lower_hall_2011.jpg" width="760" alt="The original lower hall on 7 December 2011 at 12:24 CET: Death on its pedestal between two bells; the man (third quarter) going into the left doorway, back turned; the old man (fourth quarter) waiting at the right with his crutch"></p>

*The lower hall at rest, 7 Dec 2011, 12:24 CET, which is 11:55 Strasbourg mean time [D: mean =
CET − 29 min]. The man struck at 11:45 and stands at the left doorway, back turned. The old man,
who strikes at 12:00, waits at the right. Photograph: Tangopaso, Wikimedia Commons,
"Death_and_old_man_of_the_astronomical_clock_of_Strasbourg.jpg", released into the public domain
(crop, downscaled). Found by Paul.*

## 1. What E2 does

- **The four ages strike the quarters** [S: DA p. 56–58; mechanism-inventory A3].
  - Each age has its own quarter and attribute:
    - the child strikes the first quarter with a thyrsus;
    - the youth (a hunter) strikes the half with an arrow;
    - the man (a warrior) strikes the three-quarters with a sword;
    - the old man strikes the four quarters with his crutch, "un instant avant que l'heure sonne".
  - Each age "en sortant de sa loge, fait deux pas pour s'approcher d'un timbre suspendu tout
    auprès", strikes, and disappears for the next.
  - They strike only the second stroke of each pair; "le premier [est] frappé par le génie au
    sceptre" (E1).
  - **Observed** [S: Paul's observation of the clock in action, 30 Oct 2026, his video and YouTube
    videos]:
    - At the n-th quarter the genie and the age strike **n pairs**: genie, age, genie, age, and
      so on.
    - The age walks out in front of Death and strikes the bell at the **viewer's right of Death**.
      Then it walks on past Death.
  - **By day only** in the original: the central motor suspends the ages at night [S: DA p. 58,
    65].
- **Death strikes the hours** [S: DA p. 57–58; mechanism-inventory A4].
  - Death stands on a pedestal in the middle of the hall. It drops the bone in its right hand onto
    the bell at its right, which is the **viewer's left**, 1 to 12 times, day and night.
  - Paul's photographs IMG_0769 and IMG_0770 (10:10 CET) show:
    - Death with the bone raised in its right hand and the scythe in its left;
    - a bell on each side of Death.
  - Those two photographs frame only the centre of the hall, so they do not show the doorways.
- **The hall at rest** [S: the 2011 photograph above; its clock agrees with the shows' schedule].
  - **Two ages are in view between shows.** The one that struck last stands at the left doorway
    with its back turned. The next one waits at the right, facing Death.
  - **They walk from right to left.** Each comes in from the right doorway, strikes the bell at the
    viewer's right of Death, walks on in front of Death, and goes out by the left doorway. That
    matches Paul's "walks on past Death".
  - The bells hang mouth down from curved brackets on posts, one either side of Death at about its
    waist.
  - The doorways sit at the two ends of the back wall. The hall's front is convex, a shallow bay.
- **The order of the trains** [S: DA p. 64–66, quoted in `docs/architecture.md` §5].
  - Schwilgué gave E2's work to **three separate trains**:
    1. the "rouage des quatre âges" moves the age out;
    2. the "sonnerie des quarts" strikes the quarters;
    3. the ages' train moves the automata on;
    4. the "sonnerie des heures" strikes the hours.
  - At noon the hour train hands on to the Apostles and rooster (E3, E4).
- **In the replica:**
  - The shows follow legal time: the quarters at :15, :30, :45 and :00, and Death's count is the
    legal hour (D14).
  - E2's state comes from **its own 1 rev/h state stepper** on legal time. It carries a four-step
    quarter snail, and a twelve-step hour snail through 12:1 (M1 gate, decision 1: B, Paul, 4 Nov
    2026).
  - The bells are real bells, struck mechanically (D8). Quiet hours are a controller setting (D10).

## 2. What is known, and what is not

| Item | Value | Tag |
|---|---|---|
| Height of the hall | ≈ 1324 mm above the floor at 1:8; E3's hall ≈ 149 mm above it | [E: envelope §2]; [D: 1473 − 1324] |
| Hall opening | ≈ 1.46 m wide, so **≈ 183 mm at 1:8** | [E: envelope §3] |
| Depth available | TBD: the case depth is still open | `docs/reference-notes.md`, open items |
| Death's height | **≈ 0.62 m, so ≈ 78 mm at 1:8** (range 0.52–0.74 m, 65–92 mm) | [E: 2011 photograph. Death is 0.349 of the hall's width as seen, corrected by 1/cos 35° for the upward view; 0.349 × 1.46 m / 0.82. The view angle comes from the bells' rim ellipses (axis ratio 0.58–0.64, so 35–40°; 30° allowed for tilt). The hall's width is ±11 % (envelope §3)] |
| The ages' heights | the old man as tall as Death, though stooped. The man appears about 0.8 of Death, but he is turned away in the doorway. **The child is about ¾ of the old man**, so ≈ 58 mm at 1:8. The youth and the man are not much different from the old man. They are told apart by their costumes and attributes more than by size | [E: same photograph]; [E: Paul's estimate from his video, 6 Nov 2026]; [D: ¾ × 78 mm] |
| Bells | **≈ 0.17 m across, so ≈ 21 mm at 1:8**, their centres ≈ 24 mm either side of Death's axis | [E: 0.113 and 0.133 of the hall's width; widths are not foreshortened; ±11 %] |
| Which way the ages walk | **in from the right doorway, strike at the right-hand bell, on past Death, out by the left doorway** | [S: 2011 photograph and Paul's observation] |
| Rest state | the last age stands at the left doorway, the next waits at the right; both in view | [S: 2011 photograph, 12:24 CET = 11:55 mean time, between the 11:45 and 12:00 shows] |
| Turntable that fits these positions | four ages 90° apart on a ring of R ≈ 121 mm, its centre ≈ 94 mm behind Death; the front of the ring ≈ 27 mm in front of Death; **≈ 243 mm deep in all** | [D: a circle through both doorways (±0.42 of the hall's width, at Death's depth) and 0.15 of the width in front of Death; the photograph's rest positions (±0.41 and −0.46 of the width) fall at ±45° on it] |
| Stroke cadence | **the genie strikes, the age strikes 1 s later, then a 2 s pause; repeated n times.** So a pair every 3 s, and the old man's four pairs take ≈ 10 s from the genie's first stroke to his last | [S: Paul's observation, 6 Nov 2026]; [D: 3 × 3 s + 1 s] |
| Walk duration | **the walk on takes ≈ 10 s**: from the old man's last stroke, past Death to the left doorway. The next age comes into view at the right during the same move. The walk out, from the right doorway to the bell, was not timed; at the same speed it would take ≈ 6 s | [S: Paul's observation, 6 Nov 2026]; [E: 34° of the ring's 56° walk on, at its 5.6°/s (§2 geometry), 34/56 × 10 s] |
| What follows the walk | **Death starts the hour as soon as the walk ends.** The hourglass turns "au dernier coup des quatre quarts", so it runs during the walk | [S: Paul, 6 Nov 2026; DA p. 51] |
| How the original moves the ages | not described in DA; Ungerer 1922 and Bach et al. 1992 may show it | [?]: the books are still to obtain |
| State arbor | 1 rev/h, legal time; quarter snail 1:1; hour snail through 12:1 (12/48 · 15/45, as M1's motion work) | [S: M1 gate, decision 1; architecture §3] |

## 3. Boundary and interfaces

As everywhere: **pass timing electrically and position mechanically** (architecture §4).

| To | What | Link |
|---|---|---|
| M0 controller | the state stepper; the event motors (§6); sensors: the state arbor's index, a witness on the hour snail, a lock switch per event train, the walk stops, E1's cue switch, "last stroke" | one connector |
| M1b | quarter and hour releases, in legal time (D14) | electrical, through the controller |
| E1 genies | a cue before each of the age's strokes (the genie strikes first); after the fourth quarter, the hourglass before Death strikes | electrical, through the controller |
| E3 procession | at noon, after Death's last stroke | electrical, through the controller |
| Case | the hall's architecture in front (arcade, lodge screens, balustrade, vault) | the works stand on the internal frame, never on the case (D12 R5); where E2's stage ends and the case begins is for the detail design |

**State and events (P2).**
- What must match the time is in the state train: which age is due, how many pairs, and Death's
  count.
- The event motors only supply the energy for each show.
- **Between shows the next age is in view**, waiting at the right. So a skipped show (quiet
  hours, catch-up, a fault) would leave the wrong age waiting. The walk train therefore always
  stops on an age chosen by the state train (4.2), and the controller runs it alone, silently,
  after any skip (4.5).

## 4. Proposed concept

**4.1 The state module.**
- E2's own NEMA 17 turns the state arbor at 1 rev/h on legal time.
  - It plugs in from behind on the D16 adapter (`cad/lib/motor_mount.py`).
  - It follows P1, like M1b, including the +1 h and +23 h summer-time changes (D14).
- The arbor carries the **four-step quarter snail**. A 12:1 motion work carries the **twelve-step
  hour snail**.
- An index Hall reads the arbor each hour; a witness Hall reads the hour snail at 12:00.
- The snails turn continuously with the arbor. A rack falls at the middle of a step:
  - at :15 the quarter snail is 7.5 min from each step edge [D: a step is 15 min];
  - at :00 the hour snail is 30 min from each edge [D: a step is 1 h].
  - The controller starts each show at the exact minute, so the margin is large.

**4.2 The quarter train: the count and the choice of age.**
- When released, a rack falls onto the quarter snail. Its fall (1–4 steps) sets the number of pairs,
  as in rack quarter-striking.
- **The state train picks the age.** A four-step age cam on the state arbor sets a stop finger at
  one of four radii.
  - Each age has a peg at its own radius on the turntable (option A, §5).
  - So only the age that is due next can stop at the waiting position, at the right doorway.
  - The age cam steps just after each show starts, a quarter ahead of the quarter snail.
    Whenever the walk train stops, the next due age is waiting.
- Each stroke cycle closes a cue switch. The controller fires E1's genie, and the age's stroke
  follows a moment later on the cam.
- The age strikes the ages' bell with its attribute. A lifter at the bell station raises the arm
  of whichever age stands there, and the arm falls onto the bell.

**4.3 The walk.**
- At rest the due age waits at the right doorway, held by the age cam's stop, and the last one
  stands at the left doorway.
- **The show.**
  1. The walk train lifts the stop and turns the turntable through a slip clutch. A fixed cam
     brings the waiting age to the bell, a short move.
  2. The quarter train strikes.
  3. The walk train walks the age on past Death to the left doorway, in about 10 s [S: Paul]. The
     turntable stops when the next due age reaches the waiting position: a quarter turn in all.
     At the 1:8 ring that is ≈ 12 mm/s at the figures [D: 56° of R 121 mm in 10 s].
  4. On the hour, the walk train's lock starts the hour train at once. E1's hourglass has already
     started, at the quarter train's last stroke.
- **If shows were skipped**, running the walk train simply turns on until the age cam's stop
  catches the age now due. The skipped ages pass without striking. So it corrects itself, as a
  rack on a snail does.

**4.4 The hour train.**
- A rack falls onto the hour snail (1–12).
- A gathering pallet counts the strokes. A lifter raises Death's forearm, and the bone falls onto
  Death's bell, as DA describes.
- The train locks when the rack is gathered, then closes the "last stroke" switch. At noon that
  starts E3.

**4.5 Night, catch-up and setting.**
- Quiet hours are firmware (D10). The minimal faithful setting silences the ages at night, while
  Death strikes day and night [S: DA p. 58, 65].
- At the end of quiet hours, and after a power cut, the controller runs the walk train alone,
  silently (4.3). Then the right age waits in view. Nothing else needs catching up: the snails
  are on the state arbor.
- No hands to set: the state arbor's phase is the stepper's (P1). The hour snail is meshed at its
  mark at commissioning, and its witness checks it.

## 5. Decision 1: how the ages move — A (Paul, PR #15, 6 Nov 2026)

All three options keep the state in the state train. They differ in how the age reaches the bell.

| Option | How | For | Against |
|---|---|---|---|
| **A. Turntable, stopped by the state** (4.2–4.3) | The four ages stand 90° apart on a ring whose centre is behind the back wall. Only its front arc, between the two doorways, is in view. Each show turns it a quarter turn: in from the right, strike, out by the left. | Matches the 2011 photograph and Paul's observation, including the two ages in view at rest. One rigid, printable ring (Ø ≈ 243 mm, within the bed) on one bearing. It corrects itself after skipped shows. | **About 243 mm of depth** at the original's geometry [E]. A smaller ring, with the doorways moved in, needs less depth but spoils the look. Two stops and a slip clutch to design. |
| B. Turntable geared to the state arbor | The ring turns continuously at 1 rev/h. Each age reaches the bell at its own quarter. | The simplest: no walk motor, no stops, no clutch. Nothing can get out of step. | The ages creep all the time. With a visible arc of ≈ 80°, an age is in view for ≈ 13 min each hour, so one is in view ≈ 53 min of every hour [D: 80/360 × 60 × 4]. Not what Paul saw. |
| C. Four lodges, one slide per age (DA's "sort de sa loge, fait deux pas") | The state arbor turns a selector that couples the walk train to the due age's slide. The age steps out two paces, strikes, and steps back. | Follows DA's wording. Each show starts and ends at rest. | Four slides and a selector. The age goes back rather than on past Death, against Paul's observation. Four lodges take up the hall's width. |

**Decided: A** (Paul: "go with A"). It was recommended because:
- It is the only option that matches DA ("sort de sa loge … disparaît"), Paul's observation
  ("walks on past Death") and the 2011 photograph (two ages in view at rest).
- It stays self-correcting.
- The cost is the two stops and the clutch, which the detail design proves on paper first, with a
  test over every pair of resting age and due age.

## 6. Decision 2: how many event motors — three (Paul, PR #15, 6 Nov 2026)

| Option | For | Against |
|---|---|---|
| One motor and one long cam program (walk, quarters, hours) | Fewest motors | A long, intricate cam train; the hours wait on the quarters mechanically; one fault stops everything |
| Two: walk and quarters on one cam program, hours separate | One fewer motor than three | The walk and strike motions still share a cam program, and the walk's slip clutch shares the strike train's motor |
| **Three: walk, quarters, hours, as Schwilgué** | Each train is a simple, classic one with its own locking. The controller chains them in DA's order (walk out, quarters, walk on, hourglass, Death). A fault in one does not jam the others. | Two more DC gearmotors and two more H-bridge channels than the BOM's one for E2 |

**Decided: three** (Paul: "three motors"). It was recommended because it is faithful to the
original's separate trains, and it gives the simplest mechanisms.
- The BOM now has 8 + 1 gearmotors, up from 6 + 1, and 4 dual H-bridges, up from 3.
- Architecture §10 now has 9 event channels, up from 7.

## 7. Smaller questions (answered, Paul, PR #15, 6 Nov 2026)

1. **Figure heights.** The 2011 photograph gives Death ≈ 78 mm at 1:8 (65–92 mm) [E, §2]. That is
   nearer the plate's 88 mm than the 57 mm source.
   - **Decided: 78 mm** (Paul: "78mm is fine").
   - The man, youth and old man are about as tall. The child is about ¾ of the old man, so ≈ 58 mm
     (Paul's estimate from his video). They are told apart by costume and attribute more than by
     size.
   - All are parametric, so the books can still correct them.
   - The 57 mm Apostles in `CLAUDE.md` came from the same 18-inch source. E3 will need the same
     check against a photograph.
2. **The walk and the strokes.**
   - The direction is settled: in from the right, out by the left (§1).
   - **The cadence** (Paul): the genie strikes, the age strikes 1 s later, then a 2 s pause, and
     the pair repeats; four times for the old man.
   - So the quarter train turns its strike cam once per pair, every 3 s. The cue to E1 comes at the
     start of each turn, and the age's lifter drops 1 s later. E1 must strike within that second.
   - **The walk** (Paul, 6 Nov 2026): after the old man's fourth stroke he walks on past Death.
     That takes about 10 s, while the next age comes into view at the right.
   - Death starts the hour immediately after the walk.
   - The walk out was not timed; it is a parameter, ≈ 6 s at the same speed [E].
3. **Depth.** With A at the original's geometry, the turntable needs about 243 mm of depth at E2's
   level (§2). The case depth is still open. The detail design carries 243 mm into the envelope
   and reports back if the case cannot give it; a shallower ring is the fallback.
4. **The strike.** Taken as recommended ("for the rest, go with…"):
   - **Recommended:** the age's own attribute strikes the bell, as in the original. It is soft,
     which suits a living room (D8).
   - **Fallback:** a hidden hammer moved with the arm, if the test bells sound too weak.
   - Death's bone strikes its bell directly.

## 8. After the gate: the detail design

- **CAD:** `cad/modules/e2_ages/`:
  - the state module (stepper, snails, 12:1, sensors);
  - the turntable and its stops;
  - the walk, quarter and hour trains;
  - the bells, Death, the four ages (parametric figures) and the stage.
- **Checks:**
  - interference;
  - every mesh engaged;
  - the stop selection over all sixteen cases of resting age and due age;
  - the rack counts 1–4 and 1–12;
  - the strike timing;
  - endshake;
  - motor access (D16);
  - bed fit and print poses.
- **Files:** print files, SketchUp files with an exploded view, BOM rows, and `spec/clock.yaml`
  entries for E2's state rates.

## 9. Decisions (settled, Paul, PR #15, 6 Nov 2026)

1. **How the ages move: A.**
   - A turntable carries the four ages 90° apart, with its centre behind the back wall.
   - Each show turns it a quarter turn: in from the right doorway, strike, out by the left.
   - An age cam on the state arbor sets the stop, so the next due age always waits at the right
     (§4.2–4.3, §5).
2. **Event motors: three**, for the walk, the quarters and the hours, chained by the controller in
   DA's order (§6).
3. **Figures: Death 78 mm at 1:8**, the youth, the man and the old man about as tall, the child
   ≈ ¾ of that (≈ 58 mm); all parametric (§7.1).
4. **Cadence:** genie, the age 1 s later, then 2 s, repeated n times. The walk on takes ≈ 10 s,
   and Death starts at once after it (§7.2).
5. **The strike:** the age's own attribute strikes the bell, with a hidden hammer only as a fallback.
   Death's bone strikes directly (§7.4).
6. **Depth:** the faithful ring (≈ 243 mm deep), to be checked against the case in the detail
   design (§7.3).
7. **The stop fingers are swung by a program cam on the walk train** (Paul, 6 Nov 2026, choosing A
   over two micro servos).
   - The cam turns once per show, through a 1:5 pair; a rocker and two rods swing both fingers.
   - Two notches on the cam stop the walk motor at the end of each phase.
   - A Hall at the bell station, with a magnet in each age's base, tells the controller whether an
     age was caught, so it knows whether to strike or run another turn (§10.3).

## 10. Detail design, part 1: the layout, the ring and the selection

The detail design comes in three parts, so each can be checked before the next:
1. **This part:**
   - the hall's layout;
   - the ring (turntable) on its rollers, with its teeth and the four selection pegs;
   - the two stop fingers, and the age cam that sets the bell finger's height;
   - a simulation of the walk over every case.

   The drives that part 2 details are placeholders, at their true places, so their space is held.
2. **The drives:**
   - the walk train's slip clutch and program cam, and the fingers' linkages;
   - the state module: the quarter snail, the 12:1 motion work, the hour snail and the sensors;
   - the quarter and hour striking trains, with the figures' arms and push pins.
3. **The figures:** sculpted to the decided heights.

Model: `cad/modules/e2_ages/` (`layout.py` for the numbers and the simulation, `mechanism.py` for the
CAD). Tests: `cad/tests/test_e2.py`. Frame: X to the viewer's right, Y away from the viewer, Z up,
with the origin on Death's axis on the floor. The model shows the rest state at 12:10: the child
waits at the right doorway, and the old man stands at the left one.

<p align="center"><img src="img/e2/e2_front.png" width="440" alt="E2 part 1 from the front: the hall's floor and piers, the back wall, Death between the bells, two ages at the doorways and two behind the wall, the ring below the floor, the drive placeholders"> <img src="img/e2/e2_plan.png" width="380" alt="E2 part 1 in plan: the ring centred behind the back wall, the four ages 90° apart, Death and the bells on the static island inside the ring"></p>

<p align="center"><img src="img/e2/e2_three_quarter.png" width="520" alt="E2 part 1 three-quarter with the hall hidden: the ring with its teeth, the rollers, the walk pinion, the fingers, the age cam and the state module's placeholders"></p>

### 10.1 The layout

| Item | Value | Tag |
|---|---|---|
| Hall opening | 183 mm; piers at ±91.5–101.5, 100 mm high | [E: envelope §3] |
| Back wall | x ±64, y 12–16, 72 mm high; the doorways are the gaps at its ends | [E: photo, e2-design §2] |
| Death | on a 24 × 18 × 6 pedestal at the origin; 78 mm | [S: decided] |
| Bells | Ø21 × 15 brass bowls, mouth down, at x ±24, y 0, rims at z 16, each on a printed bracket | [E: photo] |
| The ring's centre C | (0, 94): 94 mm behind Death | [D: §2] |
| The figures' path | R 121 | [D: §2] |
| Waiting positions | φ ±45°: (±85.6, 8.4), in the doorways | [D] |
| Bell station | φ 15°: (31.3, −22.9), just right of the ages' bell, 8 mm from it | [D] |
| Floors | static island inside the ring (R < 107.5) and a static front floor outside it (R > 134.5), both flush with the ring | [D] |

### 10.2 The ring and its rollers

| Item | Value |
|---|---|
| Walking surface | annulus R 108–134, z −3 to 0, flush with the floor, 0.5 mm gap each side |
| Inner skirt | R 108–110, from the surface down to z −16; the guide rollers run inside it |
| Outer body | R 127–131, down to z −28; it carries the teeth and the pegs |
| Teeth | 264, module 1, z −8 to −3 |
| Walk pinion | 16, at C + 140 mm at −60° (under the front floor, right); profile shifts −0.064/+0.064 |
| Selection pegs | one per age, Ø2.5, radial from R 131 to 135, at its own height: child −12, youth −16, man −20, old man −24 |
| Support rollers | 4 × 688ZZ, horizontal radial axes at R 118, every 90°; the ring rests on their tops |
| Guide rollers | 3 × 688ZZ, vertical axes at R 100, at −30°, 90° and 210° (clear of Death's axis) |
| Print | one piece, Ø268, face down, within the bed |

### 10.3 The selection and the walk

- **The bell finger** pivots on a vertical shaft at R 141, just downstream of the bell station.
  - **Its height is the selection.** The shaft rides on the age cam, so its arm sits at the due
    age's peg height. Only that peg can run into it.
  - The walk train's program cam swings it in for the walk out only (part 2).
- **The waiting finger** spans all four peg heights, so it catches whichever age comes next. It is
  in at rest and during the walk on, and out during the walk out.
- **The age cam** sits on the state arbor (1 rev/h, legal time), right under the bell finger's
  shaft.
  - Its radii are 20, 16, 12 and 8 mm: the child from :07.5, the youth from :22.5, the man from
    :37.5 and the old man from :52.5.
  - It rises back from the old man to the child as a ramp between :01 and :07, so the riding shaft
    is lifted, never struck.
  - Each quarter's show falls in the middle of its step.
- **The program.** Each show is one turn of the walk train's program cam.
  - **Phase A, the walk out:** the waiting finger is out and the bell finger in. The ring turns at
    most 40°: 30° to the bell, then 10° of clutch slip.
  - **Phase B, the walk on:** the bell finger is out and the waiting finger in. The ring turns at
    most 70°: 60° to the next waiting age, then 10° of slip.
  - If no age is caught at the bell in phase A, the controller skips the strikes and runs another
    turn.
- **The simulation** (`layout.simulate_walk`), over all 16 pairs of waiting age and due age:
  - the due age is always the one struck, and the next one is left waiting;
  - it takes (due − waiting) mod 4 + 1 program turns, each exactly a quarter turn of the ring.
  - So skipped shows correct themselves, with the skipped ages walking past silently.
- **Timing** [D: from Paul's 10 s walk on]:
  - the ring turns at 6°/s (1 rpm);
  - the walk out takes 5 s and the walk on 10 s; a program turn takes 18.3 s.
  - The pinion turns at 16.5 rpm. A walk gearmotor of ≈ 33 rpm through 12/24 gives that. Part 2
    chooses the motor (⚠ a micro metal gearmotor of the 1000:1 HP 6 V class, about 32 rpm [E]).

### 10.4 What is a placeholder

These hold space at their true places; part 2 replaces them.
- **Walk drive:** below the pinion, the space for the slip clutch and the program cam's gearing;
  below the deck, the walk gearmotor.
- **State module:** under the front of the hall, along X at z −80, next to the age cam (the
  quarter snail, the 12:1 motion work and the hour snail).
- **State motor:** the NEMA 17 on its D16 adapter at the right-hand end. It is withdrawn to the
  right, from the module's side.
- **Figures:** Death and the four ages, at the decided heights (part 3).

### 10.5 Size

The model's envelope [D] is:
- **x:** −145 to 152, 297 mm. That is wider than the hall's 183 mm opening: the ring and the
  deck run on behind the piers.
- **y:** −64 to 235, about 299 mm deep from the stage's front to the deck's back. The ring alone
  is 273 mm deep.
- **z:** −101 to 100, from the state motor's bottom to the piers' tops. The vault above the hall is
  not modelled.

**Check the depth against the case** when the case design fixes it (still TBD).

### 10.6 Checks

`cad/tests/test_e2.py`, 26 tests:
- the walk over all 16 cases;
- the timing against Paul's 10 s;
- the layout against the 2011 photograph: both doorways, the bell station's reach to the bell;
- the decided heights;
- the age cam against the peg heights at each quarter, and its ramp;
- the bell finger catches only the selected peg at each of the four heights, and none when
  withdrawn;
- the waiting finger catches every peg, and each rests against it;
- no interference, and every part fits the bed.

### 10.7 Open items for part 2

- The walk train (decided: a program cam, §9.7): the gearmotor (⚠ choose from the maker's table),
  the slip clutch, the program cam with its two lock notches, the rocker and rods to the fingers,
  and the Hall that says an age was caught at the bell.
- The state module: the snails, the 12:1, and the index and witness Halls.
- The quarter and hour trains: racks, gathering pallets, lifters, E1's cue switch, the lock
  switches, and Death's arm.
- The figures' arms and push pins, which are lifted at the bell station from below the ring.
- **The bells ⚠:** Ø21 brass bowl bells, to source.
- The hall's vault and side walls, and where E2 ends and the case begins (D12 R5).
