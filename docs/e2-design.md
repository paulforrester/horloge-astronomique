# E2 the four ages and Death: concept gate

Phase 2, module E2: the lower hall of the automata. At each quarter one of the four ages of life
walks out in front of Death and strikes the quarter, answering the genie's strokes (E1). Each hour
Death strikes the hour.

**Status: Concept for review (this PR).** Nothing is modelled yet. Two decisions are needed (§5 and
§6); smaller questions are in §7. Tags as in `docs/reference-notes.md`.

<p align="center"><img src="img/e2/e2_concept.png" width="980" alt="Schematic: the hall in plan with the four ages on a turntable round Death and the two bells; the trains and where the state lives; the order of one show on the hour"></p>

*Schematic only, not to final dimensions. The hall's width is from `docs/envelope.md` §3 [E].*

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
    - a bell on each side of Death;
    - **no age in view**: between quarters every age is hidden.
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
| Figure heights (ages, Death) | **[?] ≈ 57 mm or ≈ 88 mm at 1:8**: 0.46 m in one source, ≈ 0.70 m as drawn on the plate | [S: WIKI] vs [E: plate]; envelope §3 says "resolve with a photo" (§7, question 1) |
| Bells | two, either side of Death, each about 0.44 of Death's visible height wide, so **≈ 25–40 mm at 1:8** if Death is 0.46–0.70 m | [E: measured on IMG_0770, ±25 %] |
| Which way the ages walk | in front of Death to the bell at the viewer's right, then on past Death; the side they enter from is not recorded | [S: Paul's observation]; the entry side is [?] (§7, question 2) |
| Stroke cadence | not recorded | [?] (§7, question 2) |
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
- Between shows every age is hidden, so a skipped show (quiet hours, catch-up, a fault) can never
  leave anything visibly wrong.

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
- **The same fall also picks the age.** The rack positions a stop finger at one of four radii.
  - Each age has a peg at its own radius on the turntable (option A, §5).
  - So only the due age's peg meets the finger.
- Each stroke cycle closes a cue switch. The controller fires E1's genie, and the age's stroke
  follows a moment later on the cam.
- The age strikes the ages' bell with its attribute. A lifter at the bell station raises the arm
  of whichever age stands there, and the arm falls onto the bell.

**4.3 The walk.**
- The walk train turns the turntable through a slip clutch until the due age's peg meets the stop
  finger. That puts the age at the bell.
- After the strikes, the walk train lifts the finger and runs on to the rest position: the next
  quarter turn, with all ages hidden behind the lodge screens.
- **If shows were skipped**, the turntable simply runs further at the next show. The skipped ages
  pass without striking, until the due age meets the finger. So it corrects itself, as a rack on a
  snail does.

**4.4 The hour train.**
- A rack falls onto the hour snail (1–12).
- A gathering pallet counts the strokes. A lifter raises Death's forearm, and the bone falls onto
  Death's bell, as DA describes.
- The train locks when the rack is gathered, then closes the "last stroke" switch. At noon that
  starts E3.

**4.5 Night, catch-up and setting.**
- Quiet hours are firmware (D10). The minimal faithful setting silences the ages at night, while
  Death strikes day and night [S: DA p. 58, 65].
- After quiet hours or a power cut, the first show catches the turntable up by itself (4.3).
- No hands to set: the state arbor's phase is the stepper's (P1). The hour snail is meshed at its
  mark at commissioning, and its witness checks it.

## 5. Decision 1: how the ages move

All three options keep the state in the state train. They differ in how the age reaches the bell.

| Option | How | For | Against |
|---|---|---|---|
| **A. Turntable round Death, stopped by the state** (4.2–4.3) | The four ages stand 90° apart on a ring round Death's fixed pedestal. Each show turns it a quarter turn in two moves: out to the bell, then on behind the right-hand lodge screen. | Matches what Paul saw: out in front of Death, strike, walk on. One rigid, printable part on one bearing. It corrects itself after skipped shows. | Two stops to design (the selected stop and the rest stop) and a slip clutch. The depth needed is about the ring's diameter. |
| B. Turntable geared to the state arbor | The ring turns continuously at 1 rev/h. Each age reaches the bell at its own quarter. | The simplest: no walk motor, no stops, no clutch. Nothing can get out of step. | The ages creep all the time. With a visible arc of ≈ 80°, an age is in view for ≈ 13 min each hour, so one is in view ≈ 53 min of every hour [D: 80/360 × 60 × 4]. Not what Paul saw. |
| C. Four lodges, one slide per age (DA's "sort de sa loge, fait deux pas") | The state arbor turns a selector that couples the walk train to the due age's slide. The age steps out two paces, strikes, and steps back. | Follows DA's wording. Each show starts and ends at rest. | Four slides and a selector. The age goes back rather than on past Death, against Paul's observation. Four lodges take up the hall's width. |

**Recommendation: A.**
- It is the only option that matches both DA ("sort de sa loge … disparaît") and Paul's
  observation ("walks on past Death").
- It stays self-correcting.
- The cost is the two stops and the clutch, which the detail design proves on paper first, with a
  test over every pair of resting age and due age.

## 6. Decision 2: how many event motors

| Option | For | Against |
|---|---|---|
| One motor and one long cam program (walk, quarters, hours) | Fewest motors | A long, intricate cam train; the hours wait on the quarters mechanically; one fault stops everything |
| Two: walk and quarters on one cam program, hours separate | One fewer motor than three | The walk and strike motions still share a cam program, and the walk's slip clutch shares the strike train's motor |
| **Three: walk, quarters, hours, as Schwilgué** | Each train is a simple, classic one with its own locking. The controller chains them in DA's order (walk out, quarters, walk on, hourglass, Death). A fault in one does not jam the others. | Two more DC gearmotors and two more H-bridge channels than the BOM's one for E2 |

**Recommendation: three.**
- It is faithful to the original's separate trains, and it gives the simplest mechanisms.
- The BOM would go from 6 + 1 to 8 + 1 gearmotors, and from 3 to 4 dual H-bridges
  (architecture §10 then has 9 event channels, not 7).

## 7. Smaller questions

1. **Figure heights.** The detail design needs one height for the ages and one for Death; both are
   [?] (57 or 88 mm, §2).
   - **Paul, have you a photo or video frame showing the whole lower hall with an age at the bell?**
     I can scale the figures on the hall's opening [E, ±20 %].
   - Otherwise the figures are parametric, and I start at 70 mm until the books settle it.
2. **The walk.** From your video, which side does the age come from: left or right of Death?
   Roughly how many seconds are there between strokes?
3. **The strike.**
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
