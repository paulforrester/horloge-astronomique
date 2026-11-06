# E2 the four ages and Death: concept gate

Phase 2, module E2: the lower hall of the automata. At each quarter one of the four ages of life
walks out in front of Death and strikes the quarter, answering the genie's strokes (E1). Each hour
Death strikes the hour.

**Status: Concept accepted (Paul, PR #15, 6 Nov 2026).** The decisions are in §9. Nothing is
modelled yet; the detail design is next (§8). Tags as in `docs/reference-notes.md`.

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
| The ages' heights | the old man as tall as Death, though stooped; the man appears about 0.8 of Death, but he is turned away in the doorway; the youth and the child are not in the photograph | [E: same photograph]; [?] for the child and the youth |
| Bells | **≈ 0.17 m across, so ≈ 21 mm at 1:8**, their centres ≈ 24 mm either side of Death's axis | [E: 0.113 and 0.133 of the hall's width; widths are not foreshortened; ±11 %] |
| Which way the ages walk | **in from the right doorway, strike at the right-hand bell, on past Death, out by the left doorway** | [S: 2011 photograph and Paul's observation] |
| Rest state | the last age stands at the left doorway, the next waits at the right; both in view | [S: 2011 photograph, 12:24 CET = 11:55 mean time, between the 11:45 and 12:00 shows] |
| Turntable that fits these positions | four ages 90° apart on a ring of R ≈ 121 mm, its centre ≈ 94 mm behind Death; the front of the ring ≈ 27 mm in front of Death; **≈ 243 mm deep in all** | [D: a circle through both doorways (±0.42 of the hall's width, at Death's depth) and 0.15 of the width in front of Death; the photograph's rest positions (±0.41 and −0.46 of the width) fall at ±45° on it] |
| Stroke cadence | **the genie strikes, the age strikes 1 s later, then a 2 s pause; repeated n times.** So a pair every 3 s, and the old man's four pairs take ≈ 10 s from the genie's first stroke to his last | [S: Paul's observation, 6 Nov 2026]; [D: 3 × 3 s + 1 s] |
| Walk duration | not recorded | [?]: parametric in the detail design |
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
  3. The walk train walks the age on past Death to the left doorway. The turntable stops when
     the next due age reaches the waiting position: a quarter turn in all.
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
   - The man, youth and old man are about as tall; the child is smaller.
   - All are parametric, so the books can still correct them.
   - The 57 mm Apostles in `CLAUDE.md` came from the same 18-inch source. E3 will need the same
     check against a photograph.
2. **The walk and the strokes.**
   - The direction is settled: in from the right, out by the left (§1).
   - **The cadence** (Paul): the genie strikes, the age strikes 1 s later, then a 2 s pause, and
     the pair repeats; four times for the old man.
   - So the quarter train turns its strike cam once per pair, every 3 s. The cue to E1 comes at the
     start of each turn, and the age's lifter drops 1 s later. E1 must strike within that second.
   - The walk's duration was not recorded [?]. It is a parameter in the detail design.
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
3. **Figures: Death 78 mm at 1:8**, the adult ages about as tall, the child smaller; all
   parametric (§7.1).
4. **Cadence:** genie, the age 1 s later, then 2 s, repeated n times (§7.2).
5. **The strike:** the age's own attribute strikes the bell, with a hidden hammer only as a fallback.
   Death's bone strikes directly (§7.4).
6. **Depth:** the faithful ring (≈ 243 mm deep), to be checked against the case in the detail
   design (§7.3).
