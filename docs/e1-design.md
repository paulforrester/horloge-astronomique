# E1 the two genies: concept gate

Phase 2, module E1: the two genies (angels) seated either side of the mean-time dial in the lion
gallery. The genie on the left (A1) strikes his hand bell with his sceptre, once before each of
the age's strokes. The genie on the right (A2) turns his hourglass each hour, half a turn,
alternately right and left.

**Status: concept for review.** Nothing is modelled yet. The decisions Paul is asked for are in
§10. Tags as in `docs/reference-notes.md`: [S] sourced, [D] derived, [E] estimate, [?] unclear.

<p align="center"><img src="img/e1/original_genies.jpg" width="640" alt="The original lion gallery on 30 Oct 2026 at 10:10 CET: on the left the genie with his hand bell held up and the striker low in his other hand; in the middle the mean-time dial; on the right the genie holding the hourglass upright in both hands"></p>

*The two genies on 30 Oct 2026, 10:10 CET. Left: the bell genie, the bell held up by its handle in
his left hand, the striker low in his right. Right: the hourglass genie, the glass upright in both
hands. Crop of Paul's photograph IMG_0766 (`docs/img/m1/original_gallery.jpg`).*

<p align="center"><img src="img/e1/e1_concept.png" width="980" alt="Schematic: 1, the gallery at 1:8 with the two genies either side of M1's dial and their modules behind; 2, the bell genie's sceptre cocked by a cam and flicked up at the bell by a spring; 3, the hourglass turned by a Scotch yoke, rack and pinion, half a crank turn per event, alternating; 4, the timeline on the hour"></p>

*Schematic only, not to final dimensions. Positions are scaled on Paul's photograph [E ±20 %]. The
script is `cad/modules/e1_angels/concept_schematic.py`.*

## 1. What E1 does

- **A1, the bell genie** [S: DA p. 50; `docs/mechanism-inventory.md` A1].
  - "Le génie placé à la gauche du spectateur, tient d'une main un sceptre et porte dans l'autre
    un timbre, sur lequel il frappe le premier coup de chaque quart d'heure, le second étant
    répété ... par l'un des quatre âges." (The genie on the spectator's left holds a sceptre in
    one hand and a bell in the other. He strikes the first stroke of each quarter on it; one of
    the four ages repeats the second.)
  - **Observed** [S: Paul's observation of the clock in action, 30 Oct 2026]: at the n-th quarter
    the genie and the age strike **n pairs**. The genie's bell sounds first. The age strikes 1 s
    later, then there is a 2 s pause [S: Paul, PR #15, 6 Nov 2026].
  - So the genie strikes 1, 2, 3 or 4 times a quarter, 10 times an hour [D: 1 + 2 + 3 + 4].
- **A2, the hourglass genie** [S: DA p. 51, checked on the page image].
  - "[Il] tient des deux mains un clepsydre rempli de sable rouge, qu'il retourne chaque heure
    tantôt d'un demi tour à droite, tantôt d'un demi tour à gauche ... chaque fois au dernier coup
    des quatre quarts, un instant avant que la Mort ne sonne les heures." (He holds in both hands
    a glass of red sand. He turns it each hour, half a turn to the right, then half a turn to the
    left, at the last stroke of the four quarters, a moment before Death strikes the hours.)
  - Paul saw it turn during the noon show [S: Paul's observation, 30 Oct 2026].
- **Both are events** (CLAUDE.md rule 4). They hold no state that must match the time:
  - A1's count is decided by E2's quarter rack, which cues A1 once per pair (architecture §5);
  - A2 has no count. If a turn is missed, the glass simply waits; with the drive proposed in §4.3
    the next turn still goes the other way.

## 2. What is known, and what is not

Sizes are scaled on Paul's photograph IMG_0766, on the dial's pearled ring. That ring is ≈ 0.83 m
on the original and Ø 104 mm in M1's model (`docs/m1-design.md` §9.7). It spans ≈ 256 px in the
640 px copy, so **1 px ≈ 0.406 mm at 1:8** [D: 104 / 256]. The dial's own scale is ±15 %. The
figures sit on ledges a little in front of the dial, so they may read a few per cent large.
Hence ±20 % on every figure size below [E].

| Item | Value at 1:8 | Tag |
|---|---|---|
| Where | lion gallery, either side of M1's dial, centre ≈ 567 mm above the floor | [E: envelope §2] |
| Genies' centrelines | **≈ 85 mm left and 88 mm right** of the case centreline | [E: 210 and 217 px from the dial's centre] |
| Seat (top of the ledge) | ≈ 14 mm (left) and 20 mm (right) above the dial's centre | [E: 35 and 50 px] |
| Bell genie, seated | **≈ 78 mm head to soles**; 62 mm head to seat | [E: 193 and 153 px] |
| Hourglass genie, seated | **≈ 81 mm head to soles**; 72 mm head to seat | [E: 200 and 178 px] |
| Earlier figure | 78 mm: "seated height ≈ 0.63 of the bezel's diameter" | [E: `docs/m1-design.md` §2]. Agrees with the head-to-soles values. |
| Wings | span ≈ 80 mm (left); ≥ 85 mm (right, cut off by the frame) | [E: 197 and ≥ 210 px] |
| Hand bell | **≈ Ø 20 mm**, held up near the chin by its handle, mouth down | [E: 50 px]. About the size of E2's bells (Ø ≈ 21 mm, `docs/e2-design.md` §2). |
| Striker ("sceptre") | ≈ 20 mm, held low in the right hand, pointing up at the bell | [E: ≈ 48 px] |
| Hourglass | **≈ 19 mm tall × 9 mm wide**, upright in both hands at the chest | [E: 48 × 22 px] |
| Glass centre | ≈ 83 mm right of the centreline, ≈ 59 mm above the dial's centre | [E] |
| Genies' heads | ≈ 76 mm (left) and 92 mm (right) above the dial's centre, so ≈ 643–659 mm above the floor | [E]; [D: 567 + 76, 567 + 92] |
| Cadence of a pair | genie, then the age 1 s later, then a 2 s pause | [S: Paul, PR #15, 6 Nov 2026] |
| Hourglass: when | each hour, at the last stroke of the four quarters, before Death | [S: DA p. 51] |
| Hourglass: how far | half a turn, alternately right and left | [S: DA p. 51] |

**Not known:**

| Item | Why it matters | How to resolve |
|---|---|---|
| Does the genie's sceptre arm move, or is the bell struck by a hidden hammer? | Decision 2 (§6) | Paul's video of the noon show |
| Does the hourglass genie's forearms turn with the glass, or does the glass turn between still hands? In which plane: in the facade plane (seen turning clockwise, then anticlockwise), or tipping forwards? | Decision 3 (§7). DA's "à droite … à gauche" suggests the facade plane [?] | Paul's video |
| How long the half turn takes | The drive's ratio (§4.3); a parameter in any case | Paul's video. Assumed ≈ 3 s [E]. |
| Whether the genies work at night in the original | §8, question 1 | DA says only that the ages are suspended at night [S: DA p. 58, 65]. The books (Ungerer 1922; Bach et al. 1992) may say. |
| How the original drives either genie | Faithfulness of the mechanism | Not in DA. The books, still to obtain. |
| The ledges' depth, and how far the figures stand in front of the planetary dial | Depth of each module | The case design (depth still TBD) |

## 3. Boundary and interfaces

As everywhere: **pass timing electrically and position mechanically** (architecture §4). E1 has
no mechanical link to any other module.

| To | What | Link |
|---|---|---|
| M0 controller | two event motors (A1, A2); two lock switches. No trigger sensor of its own | one connector per genie (two small cassettes, §4.1) |
| E2 quarter train | **A1:** a cue before each of the age's strokes. E2 cues at the start of each pair's cam turn; the age's lifter drops 1 s later; "E1 must strike within that second" (`docs/e2-design.md` §7, item 2) | electrical, through the controller (architecture §4, E2 → E1) |
| E2 quarter train (on the hour) | **A2:** start at the old man's last stroke. The quarter train's lock switch closing on the hour is that moment | electrical, through the controller |
| M1b hour flag | **A2** when the ages are silent (quiet hours, §8): the controller turns the glass just before Death | electrical (architecture §5, E1 hourglass row) |
| E2 Death | Death starts after E2's walk on, ≈ 13.8 s after the old man's last stroke. The glass must have finished by then | timing only; ≈ 3 s needed [E] |
| M1 cassette | none mechanical. E1's cassettes sit outboard of M1's frame (±82 mm, `docs/m1-design.md` §9.2) and must clear it | geometry: checked in the detail design |
| M5 planetary dial | the genies' heads and wings reach ≈ 643–659 mm, above the bottom of M5's band at ≈ 639 mm [D: 810 − 343 / 2, envelope §3]. On the original they stand in front of it (photograph) | geometry: the figures stand in front of M5's dial plane |
| Case | the gallery's cornice and ledges. The figures sit on **printed plinths that belong to E1**; the wooden cornice fits round them with a gap. The works never stand on the case (D12 R5) | where the plinth ends and the case begins: detail design |

**Event order on the hour** (architecture §5; DA p. 64–66), in seconds from the genie's first
stroke [D: Paul's cadence and `docs/e2-design.md` §11.3 at ≈ 32 rpm [E]]:

| t (s) | What |
|---|---|
| −8.7 | E2's walk out starts (the controller starts it early, from the RTC) |
| 0, 3, 6, 9 | A1 strikes (cued by E2) |
| 1, 4, 7, 10 | the old man strikes |
| 10 | E2's quarter train locks → **A2 turns the glass** (≈ 3 s [E]) |
| 10 – 23.8 | E2 holds 1.8 s, walks on 10.3 s, slips 1.7 s |
| ≈ 23.8 | Death starts the hour |

The glass has ≈ 10.8 s of margin before Death [D: 23.8 − 10 − 3].

## 4. Proposed concept

**4.1 Two small cassettes, one per genie.**
- The genies are ≈ 173 mm apart [D: 85 + 88], with M1's cassette between them. M1's gate already
  set them as separate modules (`docs/m1-design.md` §6, confirmed by Paul).
- Each cassette is a small printed frame behind its figure, on the internal frame, outboard of
  M1's frame. It carries the figure on its plinth, one gearmotor, one cam train and one lock
  switch.
- Each arbor that moves a figure runs front to back through the figure's back from the cassette.
  The figure hides it.
- Service: the figure lifts off its arbor to the front; the cassette comes out to the back with
  its connector. The gearmotor drops out of a bracket with two screws, as in E2 (`docs/e2-design.md` §11.4).

**4.2 A1: the sceptre flicks up at the bell.**
- **The bell** is a real small brass bell, Ø ≈ 20 mm, the same part as E2's two bells if one can
  be found in that size. The figure's left hand holds it by its handle, as in the photograph. A
  bell held at its crown rings freely.
- **The sceptre arm** turns on a shoulder arbor (front to back). Behind the figure a lever on the
  same arbor rests on a snail cam, so at rest the sceptre is low, as in the photograph.
- **One stroke per cam turn**, as a striking train's hammer:
  1. the cue starts the motor;
  2. the cam draws the lever a little further, against a steel spring (D13);
  3. at the snail's step the lever drops off: the spring flicks the sceptre up, its tip strikes
     the bell's rim and rebounds off a banking stop, so the bell rings free;
  4. the lever falls back onto the cam, and the lock switch stops the motor at rest.
- **Speed.** A micro metal gearmotor at ≈ 200 rpm under load [E] turns the cam once in ≈ 0.3 s.
  With the step a third of the way round, the stroke comes ≈ 0.1 s after the cue [D: 1/3 × 0.3 s].
  So **cue to stroke ≤ 0.3 s [E]**, inside E2's one second. The cycle is done long before the
  next cue, 3 s later.
- The count stays mechanical: one turn per cue, and E2's rack decides the cues.

**4.3 A2: the glass turns by a Scotch yoke, rack and pinion.**
- **The glass** is a bought miniature hourglass with red sand, ≈ 20 mm tall [E], held in a
  printed frame between the figure's hands (decision 4, §8).
- **The glass's arbor** runs front to back through the figure's chest, at the glass's centre, so
  the glass turns in the facade plane: clockwise one hour, anticlockwise the next.
- **The drive**, behind the figure:
  - the gearmotor turns a crank **half a turn per event, always forwards**;
  - the crank pin runs in a slotted yoke, which slides a rack;
  - the rack turns a pinion on the glass's arbor through half a turn.
- **Sizes [D].** A 12-tooth pinion at module 0.8 has a pitch Ø 9.6 mm. Half a turn is π × 9.6 / 2
  = 15.1 mm of rack, so the crank's radius is 7.5 mm. At module 1.0 the same is 18.8 mm and
  9.4 mm. The module stays a parameter.
- **It alternates by itself.** The glass's angle is 90° × (1 − cos θ) for crank angle θ [D: a
  Scotch yoke's stroke is r (1 − cos θ); 2r is half a turn]. From θ = 0 to 180° the glass goes
  0 → 180°; from 180° to 360° it goes back 180 → 0°. The motor never reverses.
- **It stops softly and exactly.** Both rest positions are at the crank's dead centres. There the
  glass hardly moves with the crank: a 5° overrun of the motor moves the glass by 0.34° [D:
  90° × (1 − cos 5°)]. The speed follows a sine, so the glass starts and stops gently.
- **The lock cam** has two notches, 180° apart, one at each dead centre.
- **Speed.** The 1000:1 micro gearmotor of E2's walk (≈ 32 rpm [E]) with a 3:1 pair gives a half
  turn in ≈ 2.8 s [D: 0.5 × 3 / 32 × 60]. PWM trims it once the original's time is known.
- **Missed turns are harmless.** If one is skipped, the glass rests where it was and the next turn
  still goes the other way. After an odd number of skips the glass rests "upside down"; an
  hourglass looks the same either way up.

**4.4 The controller.**
- **A1:** on E2's cue, run the A1 motor until its lock switch closes. Fault if it has not closed
  within 1.5 s, or if a cue arrives while it is still running.
- **A2:** on the hour, at E2's quarter-train lock; or, when the ages are silent, straight after
  M1b's hour flag. Run the A2 motor until its lock switch closes (timeout ≈ 6 s). Then Death may
  start, after E2's walk on as now.
- **Catch-up and night:** skip both (architecture §5). Nothing needs restoring.

## 5. Decision 1: one event motor or two

The architecture allows E1 one or two motors (§10). The BOM already counts two.

| Option | For | Against |
|---|---|---|
| **A. Two motors, one per genie, in two small cassettes** | Each genie is a small, separate, simple train with its own lock. Each speed suits its job: fast for the bell, slow for the glass. Nothing crosses M1. A fault in one stops only that one. Matches M1's gate ("E1's genies separate"). | One more motor and H-bridge channel than B. Already in the BOM. |
| B. One motor and a selector | One motor fewer | The genies are 173 mm apart with M1's cassette between them, so a shaft would have to cross behind or under M1. The two jobs need different speeds and different counts (n strokes, then one half turn), so a clutch or selector is needed. |

**Recommended: A, two motors.** B saves one small motor at the cost of a shaft across M1 and a
selector.

## 6. Decision 2: how the sceptre strikes

| Option | How | For | Against |
|---|---|---|---|
| **A. The sceptre strikes the hand bell** (§4.2) | A cam cocks the arm against a spring and lets it go; the sceptre's tip strikes the bell in the genie's hand and rebounds off a stop | Faithful to DA ("un timbre, sur lequel il frappe"). One moving part you can see doing the work. Same kind of bell as E2's (one purchase). | A 20 mm bell is quiet. The sceptre's tip is small (≈ 20 mm long), so the stop must be set finely. |
| B. The arm gestures, a hidden hammer strikes | The same cam moves the arm and, through a second lever, a hammer on a bigger bell hidden in the plinth | Louder and easy to adjust. The arm need not touch the bell. | Less faithful; the sound does not come from the bell you see. A bigger bell to find and hide. |
| C. A solenoid | — | — | Excluded by D8: "not a mechanical event train; clicky". |

**Recommended: A**, with B as the fallback if the test bell is too quiet. This is the same rule as
E2's strike (`docs/e2-design.md` §7, item 4). It is soft, which suits the living room (D8).

## 7. Decision 3: how the glass turns and alternates

| Option | How | For | Against |
|---|---|---|---|
| **A. Scotch yoke, rack and pinion** (§4.3) | Half a crank turn per event; the rack turns the glass 0 → 180°, then 180 → 0° | Forward-only motor (architecture §10). Alternates mechanically, even after skips. Rests at dead centres, so the stop is exact (0.34° per 5° of overrun). Gentle, sine-shaped motion. Small: a 15 mm stroke. | A sliding yoke and a rack to print and guide; a little backlash at the pinion, which does not matter at the rests. |
| B. Crank and rocker with a 2:1 step-up | A crank rocks a lever ±45° to ±60°; a gear pair doubles it | No sliding parts | A rocker's swing is not symmetric in time. Getting exactly 180° needs fiddly link lengths. |
| C. Reversing motor with two end switches | The H-bridge reverses the motor each hour; a 2:1 gear and a switch at each end | Simplest mechanism | The motor runs both ways, against the architecture's "DC gearmotors, one direction". The alternation lives in firmware, and the glass stops wherever the motor coasts. |
| D. Half turns, always the same way | A Geneva or 2-notch lock | Simple | **Not faithful**: DA says alternately right and left. |

**Recommended: A.** It is the only option where the alternation and the end positions are both
mechanical, with a forward-only motor.

**Which parts turn** depends on Paul's video (§2): the glass alone between still hands, or the
glass with the forearms. Both work with A: the turning part is either the glass's frame or one
print of the frame and the forearms. **Recommended until Paul has checked:** the glass and its
frame turn, between hands that are cupped round the frame's pivots.

## 8. Decision 4: figure size, the bell and the glass

1. **Figure size.** Measured on the photograph: 78 mm (bell genie) and 81 mm (hourglass genie)
   head to soles, ±20 % [E, §2]. M1's earlier 78 mm agrees.
   - **Recommended: 78 mm for both, parametric.** The 3 mm difference is inside the error, and
     may come from the right genie sitting a little nearer the camera.
   - The figures themselves (sculpted, painted prints) go with E2's figures in a later part.
     Until then the CAD has simple placeholders of the right size, with the arbors in place.
2. **The bell: one part for E1 and E2.** Ø ≈ 20 mm [E] here, ≈ 21 mm for E2. **Recommended:**
   buy three of one bell (plus a spare) if the pitches please Paul together. The local phase
   tries them.
3. **The glass.**
   - **A. A bought miniature hourglass** with red sand, ≈ 20 mm tall (sold as charms or
     pendants) ⚠ to source. The sand runs after each turn, as on the original. **Recommended.**
   - B. A printed glass in clear PETG with painted sand. No sourcing, but the sand never moves,
     so after each turn it would sit at the top. Fallback only.

**Smaller questions:**

1. **Night (D10).** A1 is cued by E2, so it is silent whenever the ages are. For A2 DA says only
   "chaque heure". **Recommended:** the glass turns every hour that Death strikes, day and night.
   It makes no sound, and it comes "un instant avant que la Mort ne sonne". A firmware setting
   can silence it too.
2. **The gap between the genie and the age.** E2's age strikes 1 s after the cue; A1 strikes
   ≈ 0.1–0.3 s after it [E]. So the gap is ≈ 0.7–0.9 s, not 1 s.
   - **Recommended:** accept it now. If Paul wants 1.0 s, E2 can delay its age's lifter by A1's
     measured latency (a parameter in E2's quarter cam). That would be an interface change for
     E2, so it is listed in §10.
3. **Depth.** Each cassette needs roughly 40–60 mm behind its figure [E: a gearmotor of 34.5 mm
   lies across, plus the cam and plates]. That is within M1's ≈ 112 mm. Checked when the case
   depth is fixed.

## 9. BOM impact

Nothing changes in `docs/bom.md` at this gate. If the recommendations are accepted, the detail
design will add these E1 rows [E]:

| Item | Qty | Note |
|---|---|---|
| DC gearmotors | 2 | **Already counted** (Batch 2: "E1 ×2 (bell, glass)"). Bell: a ≈ 200 rpm micro metal gearmotor (e.g. the 100:1 HP 6 V of Batch 1); glass: the 1000:1 HP 6 V of E2's walk. Same families, so one order. |
| H-bridge channels | 2 | Already counted (4 dual H-bridges for 8 motors). |
| Lock switches | 2 subminiature roller-lever microswitches | Within Batch 2's 10 microswitches. |
| Bell | +1 | The genie's hand bell. With E2's two: **3 (+ 1 spare)** of one bell, ⚠ not yet found. |
| Miniature hourglass, red sand, ≈ 20 mm | 1 (+ 1 spare) | **New** ⚠ to source (EU). |
| Steel spring for the sceptre | 1 (+ spares) | **New**; small extension or torsion spring (D13). |
| Rods, small bearings, screws, inserts | small | From the model, e.g. Ø3 or Ø4 rod and MR-series bearings. |
| Connectors | 2 | The BOM's "~12" lists E1 once; two cassettes need two. Within its spares. |

No stepper, no Hall sensor and no new controller channel type.

## 10. Decisions needed from Paul

1. **Motors (§5):** A, two motors, one per genie, in two small cassettes. *Recommended.*
2. **The strike (§6):** A, the sceptre strikes the hand bell; B, a hidden hammer, as the fallback.
   *Recommended: A.*
3. **The glass's drive (§7):** A, Scotch yoke, rack and pinion, forward-only and alternating
   mechanically. *Recommended.*
4. **Sizes and parts (§8):** both figures 78 mm, parametric; one bell type for E1 and E2; a bought
   miniature hourglass with red sand. *Recommended.*
5. **Night (§8, question 1):** the glass turns with Death, day and night. *Recommended.*
6. **Interface with E2 (§8, question 2):** accept a genie–age gap of ≈ 0.7–0.9 s, or ask E2 to
   delay its age's lifter by A1's latency. *Recommended: accept for now.* (An E2 interface
   change; nothing in E2 is touched by this PR.)
7. **From Paul's video, if he can:** does the sceptre arm move; do the forearms turn with the
   glass, and in which plane; how long the half turn takes.

## 11. After the gate: the detail design

- **CAD:** `cad/modules/e1_angels/`: the two cassettes, cams, the yoke, rack and pinion, the
  plinths, the bell and glass mounts, placeholder figures with their arbors.
- **Checks** (`cad/tests/test_e1*.py`): interference; every mesh engaged; the glass's travel
  exactly 180° and its error at the rests; the cam's pressure angle; the sceptre's banking
  clearance; the timing (cue to stroke, the half turn against Death's start); clearance to M1's
  frame; the gearmotor drops out (D16's rule for access); bed fit and print poses.
- **Files:** print files (`export/print/e1_angels/`), SketchUp files with an exploded view
  (`export/sketchup/e1_*.dae`), BOM rows, and a decision record ("D-next (E1)") if Paul wants one.
