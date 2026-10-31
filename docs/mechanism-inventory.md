# Mechanism inventory

Phase 0 deliverable. This file lists every indication and automaton of Schwilgué's clock. Each
entry says what it shows and its period(s), how the original does it (with source), the proposed
approach for the replica, its difficulty, and what it depends on.

Tags and source keys are those of `docs/reference-notes.md`:

- **[S]** sourced;
- **[Sn]** search snippet only, page not opened, verify;
- **[D]** derived (the calculations are in `tools/phase0/derivations.py`);
- **[E]** estimate;
- **[?]** conflicting or unclear;
- **TBD** not known; the entry says how to resolve it.

Module IDs (M…, E…) are defined in `docs/architecture.md`. The version column follows the
recommendation in `docs/decisions.md` → D5:

- **v1** is the first working clock;
- **v1.5** is the equations, eclipses and sunrise/sunset;
- **v2** is the computus and other deferred work.

**Difficulty** is rated 1–5:

1. plain gearing;
2. a standard clock mechanism;
3. a custom mechanism with a known principle;
4. dense or partly unknown;
5. the original is undocumented *and* complex.

## 1. Period reference

| Quantity | Value | Tag |
|---|---|---|
| Mean solar day | 86,400 s | definition |
| Tropical year (Schwilgué) | 365 d 5 h 48 min 48 s = 365.242222 d | [S: LEF]; [D] |
| Sidereal day | 86,164.0906 s = 23 h 56 min 4.09 s, i.e. Y/(Y+1) mean days = 164,359/164,809 exactly | [D] from LEF's year |
| Mean lunar day (Moon returns to the meridian) | 24 h 50.47 min = 24 h × S/(S−1) | [D] |
| Synodic month (Schwilgué's gearing) | 29.530590 d | [D] from CLEA |
| Anomalistic month (target) | 27 d 13 h 18 min 34 s | [S: LEF] |
| Evection (target) | 31 d 19 h 29 min 11.453 s | [S: LEF] |
| Variation (target) | 29 d 12 h 44 min 3 s | [S: LEF] |
| Annual equation (target) | 365 d 6 h 13 min 57 s | [S: LEF] |
| Draconitic month (target) | 27 d 5 h 5 min 35.8 s | [S: LEF] |
| Lunar node regression | about 18.6 years | [S: LEF] |
| Eclipse year | about 346.6 d = 1/(1/365.2422 + 1/(18.6 × 365.2422)) | [D] |
| Precession of the equinoxes | about 26,000 years [S: CLEA]; "a turn in 25,806 years" [Sn: CATH] | [?] |
| Mercury, Venus, Mars, Jupiter, Saturn | 87.968 d; 224.695 d; 686.930 d; 11.857 yr; 29.424 yr (Schwilgué's gearing) | [S: CLEA]; [D] |
| Week | 7 d | — |
| Solar cycle; golden number (Metonic); Roman indiction | 28 yr; 19 yr; 15 yr | [S: CLEA, RGL] |
| Gregorian calendar cycle | 400 yr (146,097 d) | definition (Gregorian rule) |
| Equation of time | −14.3 to +16.5 min, i.e. −3.6° to +4.1° of a 24 h hand | [D] from MEEUS eq. 28.3 |

Scale aids [D]:

- On the 287.5 mm main dial, 1° of hand angle is 2.51 mm of arc at the rim.
- One day on a 366-sector ring of that diameter is 2.47 mm.

## 2. Summary

| ID | Indication / automaton | Module | Period(s) | Replica approach (short) | Diff. | Ver. |
|---|---|---|---|---|---|---|
| I1 | Local mean time, gold hands | M1 | 1 h, 12 h (24 h? TBD) | Motion work from a 1 rev/h stepper arbor | 1 | v1 |
| I2 | Legal time, silver hands | M1 (or M1b) | 1 h, 12 h | Fixed-offset hands; DST needs its own drive (D9) | 1–2 | v1 |
| I3 | Apparent Sun on the main dial | M2 + M3 | apparent solar day | Mean-Sun arbor plus a differential fed by the solar equation | 3 | v1 mean, v1.5 apparent |
| I4 | Moon on the main dial | M2 + M3 | lunar day; month | Mean-Moon differential (Schwilgué); second differential for the lunar equation | 4 | v1 mean, v1.5 true |
| I5 | Eclipse indication (variable-length Moon arm) | M2 | draconitic month; 18.6 yr; eclipse year | Node cam plus a radial slide on the Moon arm | 4 | v1.5 |
| I6 | Earth-shadow disc | M2 | apparent solar day | Rigid with the Sun hand, 180° opposite | 1 | v1 |
| I7 | Sunrise and sunset times | M2 | tropical year | Latitude cam on the year arbor drives two hands | 3 | v1.5 |
| I8 | Annual calendar ring | M2 | civil year (365/366 d) | 366 sectors, one sector per day at midnight, double step on 28 Feb in common years | 3 | v1 |
| I9 | Movable feasts / Easter and leap day on the ring | M2 ← M4 | yearly | Sliding feasts arc set by the computus; leap gate from the 4-year count | 4–5 | v1 leap, v2 feasts |
| I10 | Dominical letter of the year | M2 ← M4 | yearly | Seven-position dial set by the computus | 2 | v2 (v1: set by hand) |
| I11 | Weekday carousel (seven deities) | M7 (driven by M2) | 7 d | 7:1 from the daily arbor, continuous [Sn] | 2 | v1 |
| I12 | Computus: solar cycle, golden number, indiction, dominical letter, epact (+ year?) | M4 | 28 / 19 / 15 yr; Gregorian 100/400 yr corrections | Mechanical computus with count wheels plus rack-and-snail Easter finder, run as an event on 31 Dec | 5 | v2 |
| I13 | Equations vitrine (cams visible) | M3 | 8 periods (above) | Stacked cams with summing crossbars (Schwilgué principle) | 4 | v1.5 |
| I14 | Planetary dial (heliocentric) | M5 | 88 d … 29.4 yr | Schwilgué's published ratios from a year arbor | 2–3 | v1 |
| I15 | Moon-phase globe | M5 | synodic month | Ratio train or differential (Schwilgué) | 2 | v1 |
| I16 | Celestial globe: sidereal rotation | M6 | sidereal day | Schwilgué's exact epicyclic train | 3 | v1 |
| I17 | Celestial globe: precession | M6 | ~25,800 yr | Worm-reduced train; nearly static | 2 | v2 (provisioned in v1) |
| A1 | Angel with bell (first stroke of each quarter) | E1 | 15 min | Event motor plus cam-lifted arm and bell | 2 | v1 |
| A2 | Angel turning the hourglass | E1 | 1 h | Event motor turns the glass 180° | 2 | v1 |
| A3 | Four ages strike the quarters | E2 | 15 min (one cycle per hour) | Ages carousel indexed by the time train; event motor strikes | 3 | v1 |
| A4 | Death strikes the hours | E2 | 1 h (1–12 strokes) | Rack or count wheel on the event train | 2 | v1 |
| A5 | Apostles pass before Christ, who blesses | E3 | daily, at mean noon | Event motor turns the procession once; blessing arm on a cam | 3 | v1 |
| A6 | Rooster crows three times and flaps its wings | E4 | daily, during A5 | Event motor plus wing and head cams; sound per D8 | 3 | v1 |
| A7 | Computus run | E5 = M4 | yearly, night of 31 Dec | Trigger cam on the year train; motor powers the computus cycle | 5 | v2 |

## 3. Details

### I1 Local mean time (gold hands) — M1

- **Shows:** local mean time [S: WIKI]. "In 1842 the dial showed only Strasbourg mean time" [Sn: CATH].
- **Periods:** minute hand 1 h. **TBD:** whether the hour hand is on a 12 h or a 24 h dial.
  Resolve from a frontal photo or Schwilgué's *Description abrégée*.
- **Original:** driven from the going train regulated by the seconds pendulum [S: CLEA]. Details TBD.
- **Replica:**
  - The M1 stepper drives the minute arbor at 1 rev/h. 12:1 motion work (cannon pinion, minute
    wheel and hour wheel) drives the hour hand.
  - The quarter, hour and noon release cams also sit on this train (see architecture).
- **Difficulty:** 1.
- **Depends on:** M0 time base; D2 (whose mean time).

### I2 Legal time (silver hands) — M1

- **Shows:** Central European Time [S: WIKI].
  - **[?]** Whether the original follows summer time is unresolved: "12 h 30 en heure d'hiver"
    (FR Wikipedia) vs "tous les jours, à 12 h 30 précises" [Sn: CATH].
- **Replica:** standard time is a fixed angular offset from mean time. For Strasbourg it is
  29.0 min [D]; for Bordeaux 62.3 min [D].
  - The offset can be set once on a slip-clutched hand.
  - Following summer time needs a separately driven pair of hands, so the stepper can advance
    them +1 h in spring and +11 h in autumn while staying forward-only.
  - Decision: D9.
- **Difficulty:** 1, or 2 with summer time.
- **Depends on:** D2, D9.

### I3 Apparent Sun (main dial) — M2 + M3

- **Shows:** the Sun's apparent motion around the Earth at the centre [S: CLEA]. The Sun hand runs
  on a 2.30 m dial [S: ELS], and a photo record labels the dial "Apparent Time" [Sn].
- **Periods:** one turn per apparent solar day. The mean day is corrected by the equation of time
  (−14.3 to +16.5 min [D]).
- **Original:** the solar equation is the sum of three periodic corrections from cams in the
  equations vitrine [S: LEF]. The sum reaches the Sun motion by pulleys or rods to a pivoting frame
  (a differential) [S: LEF], or by an oblique-toothed pinion moved axially [S: CLEA].
  **TBD:** which three terms.
- **Replica:**
  - Mean Sun = the M2 input arbor (1 rev per mean day on a 24 h dial).
  - A differential (printed spur or bevel) sits between the mean-Sun arbor and the Sun hand. Its
    third member is turned by the M3 solar-correction output (range ±4.1° at the hand).
  - Two terms, the equation of centre (±7.7 min, anomalistic year) and the reduction to the
    equator (±9.9 min, half year) [D], account for most of the equation of time. With two terms
    the residual is under about 1 min (estimated from the neglected terms of MEEUS eq. 28.3; to
    confirm in Phase 1). A third term brings the residual down further.
  - In v1 the differential's third member is locked, so the hand shows mean solar time.
- **Difficulty:** 3.
- **Depends on:** M3; the tropical/anomalistic-year arbor; D5.

### I4 Moon (main dial) — M2 + M3

- **Shows:** the Moon around the Earth [S: CLEA]. The rod's length varies (see I5) [S: CLEA].
- **Periods:** one turn per lunar day (24 h 50.47 min [D]); synodic month 29.53059 d. Five
  periodic corrections [S: LEF] (periods in §1).
- **Original:** lunar turns per year = (312/24) × [1 − (83×14)/(122×196)] = 12.368267 via a
  differential [S: CLEA]. The tilt of the lunar orbit uses an inclined toothed wheel [S: CLEA].
  The corrections come from the equations vitrine [S: LEF].
- **Replica:**
  - Mean Moon: reproduce Schwilgué's differential, or an equivalent compound train (Phase 1
    compares them).
  - True Moon: a second differential fed by the M3 lunar-correction output.
  - Amplitudes the replica needs (standard lunar theory, MEEUS ch. 47; to be confirmed in Phase 1):
    equation of centre ≈ 6.3°, evection ≈ 1.3°, variation ≈ 0.7°.
  - In v1 the Moon hand shows the mean Moon.
- **Difficulty:** 4, because of coaxial density on the main dial.
- **Depends on:** M3; I5; I3 (shared tube stack).

### I5 Eclipse indication — M2

- **Shows:** solar and lunar eclipses. The Moon hand's length changes so the Moon can cover the Sun
  or enter the shadow disc only near a node [S: CLEA, LEF].
- **Periods:** draconitic month (27.21 d [S: LEF]); node regression about 18.6 yr [S: LEF]. Relative
  to the Sun, the node line returns once per eclipse year (346.6 d [D]).
- **Original:** "a cam turning in about 18.6 years lengthens or shortens the Moon hand"; a similar
  mechanism handles lunar eclipses [S: LEF]. A dragon (node) hand is mentioned only for other
  clocks [?].
- **Replica:**
  - A node cam on its own coaxial arbor, with a follower on a radial slide in the Moon arm.
  - The arm length becomes f(Moon longitude − node longitude).
  - Two kinematic options for Phase 2:
    - (a) the cam rotates in the dial frame at sidereal rate minus regression;
    - (b) the cam is carried on the Sun-hand frame and turns relative to it once per eclipse year.
  - Option (b) needs one fewer full-speed coaxial tube [D, kinematics]. Choose in the Phase 2
    main-dial feasibility study.
- **Difficulty:** 4.
- **Depends on:** I3, I4; ratio for the node regression (Phase 1).
- **Validation:** the simulator compares indicated eclipses against an ephemeris (Phase 3).

### I6 Earth-shadow disc — M2

- **Shows:** a black disc opposite the Sun represents the Earth's shadow [S: CLEA].
- **Replica:** an arm rigid with the Sun hand at 180°. It adds no tube.
- **Difficulty:** 1.
- **Depends on:** I3.

### I7 Sunrise and sunset — M2

- **Shows:** sunrise and sunset times [S: CLEA]. A pointer labelled "COUCHER DU SOLEIL" [Sn]
  suggests two labelled hands.
- **Original mechanism:** **TBD**. Not in any source reached this session. Resolve from
  *Description abrégée* or Bach/Rieb.
- **Periods:** tropical year. The amplitude depends on latitude.
- **Replica:**
  - A cam on the continuous tropical-year arbor. Its profile is the semi-diurnal arc H0(δ), with
    cos H0 = (sin h0 − sin φ sin δ)/(cos φ cos δ), h0 = −0.833°, φ = chosen latitude.
  - A scissor linkage sets two hands symmetric about apparent noon.
  - The cam is a swappable printed part, so Strasbourg or Bordeaux is a print choice (D2).
- **Difficulty:** 3.
- **Depends on:** the tropical-year arbor; D2; I3 (if the dial is in apparent time).

### I8 Annual calendar ring — M2

- **Shows:** every day of the year, each preceded by its dominical letter [S: CLEA]. "Un anneau
  extérieur doré qui fait un tour par an … gradué en 366 secteurs" (a gilded outer ring, one turn a
  year, 366 sectors); a figure (Apollo [Sn], or Diana [?]) points to the current day.
- **Periods:** the civil year, 365 or 366 days.
- **Original:**
  - **TBD:** whether it moves continuously or jumps daily, and its diameter.
  - For comparison, the second clock's ring was 2.92 m across with 366 sectors, and the leap sector
    was moved by hand every four years [Sn: PH-H]. Schwilgué automated this [S: CLEA].
- **Replica:**
  - A 366-sector ring advanced one sector per day at local midnight by a star wheel or Geneva drive
    on the M2 daily arbor.
  - In common years, a gate from a 4-year count wheel (turned by the ring) makes the ring step two
    sectors on the night of 28 Feb, skipping 29 Feb. That is mechanical, as rule 2 requires.
  - The Gregorian century exception (2100) is v2, from the computus; until then it needs a manual
    note.
  - **Bed fit:**
    - If the ring's outer diameter is ≤ 2.56 m it fits the 320 mm bed at 1:8 [D];
    - if it is ≤ 2.40 m it also fits the 300 mm dual-nozzle limit [D];
    - if it is larger, it is printed in segments on a printed or metal carrier ring.
- **Difficulty:** 3.
- **Depends on:** the M2 daily arbor; I9.

### I9 Movable feasts and leap day on the ring — M2 ← M4

- **Shows:** the day marked "Pâques" is inserted in the right place and a day is added in leap
  years [S: CLEA]. Ascension, Pentecost and the other dependent feasts are placed on the calendar
  each 31 December [Sn].
- **Original:** set by the computus on New Year's Eve [Sn: CATH]. The transfer mechanism is
  **TBD**; the 1821 model has no transfer train [Sn: WSC].
- **Replica (proposal):**
  - All Easter-dependent feasts sit at fixed day offsets from Easter. Examples, from the Gregorian
    rules: Ash Wednesday −46, Ascension +39, Pentecost +49.
  - So one rigid "feasts arc" sliding in a groove of the ring can carry all of them.
  - The computus positions this arc once a year, over a 35-day range (22 March–25 April) [Sn: EXO].
  - The leap-day function is in I8.
- **Difficulty:** 4 (transfer) to 5 (the computus itself).
- **Depends on:** M4; I8.

### I10 Dominical letter of the year — M2 ← M4

- **Shows:** the current year's dominical letter, on a small dial on the left [S: CLEA].
- **Replica:** a seven-position dial with a jumper. Leap years have two letters (one before
  29 Feb, one after): **TBD** how the original shows this.
  - v1: set by hand each 1 January.
  - v2: driven by the computus.
- **Difficulty:** 2.
- **Depends on:** M4.

### I11 Weekday carousel — M7

- **Shows:** Apollo (Sunday), Diana, Mars, Mercury, Jupiter, Venus, Saturn [S: CLEA], on chariots
  [Sn].
- **Original:** **[?]** "le carrousel tourne de façon continue et laisse apparaître devant, à midi,
  le char de la planète du jour courant" (it turns continuously; the day's chariot is in front at
  noon) [Sn, unconfirmed].
- **Replica:** a 7:1 reduction from the M2 daily arbor, phased so each day's chariot is centred at
  noon. It is a continuous mechanical drive, not an event.
- **Difficulty:** 2.
- **Depends on:** M2. The case layout puts the carousel directly above the main dial [S: CLEA].

### I12 Computus — M4

- **Shows:** golden number, solar cycle, indiction, dominical letter, epact and the Easter date
  [S: RGL]. Possibly also a four-digit year [Sn: WCC]. Bottom left of the clock [S: TS].
- **Periods:** advances one year at a time. Cycles of 28, 19 and 15 years. Gregorian century
  corrections: 100/400-year leap rule; solar and lunar equations of the epact.
- **Original:** an enlarged version of the 1821 prototype [S: RGL]. The prototype is about 300
  parts, mostly wheels and complex cams, in a 15 × 20 × 6 cm frame [Sn: EXO], and includes a large
  rack [S: RGL, 3D excerpt]. **TBD:** the Gregorian-correction mechanism, the Easter-finding
  logic and gear counts.
  - Roegel's full study is unpublished [S: RGL].
  - The Klinghammer reduced replica and its 2007 book (with Augereau's gear ratios) are the most
    promising accessible description [Sn: KLH].
- **Replica (v2):**
  - Design our own mechanical Gregorian computus from count wheels:
    - 28-, 19- and 15-position wheels stepped once a year;
    - a century wheel and a 400-year wheel feeding the epact and dominical-letter corrections;
    - a rack-and-snail Easter finder: the epact gives the Paschal full moon, the dominical letter
      gives the following Sunday.
  - It runs as an event (E5) on 31 Dec.
  - Every state is validated against a standard Gregorian Easter algorithm (MEEUS ch. 8) in the
    simulator for at least 2000–2400.
  - Following Schwilgué's exact mechanism needs the sources above.
- **Difficulty:** 5.
- **Depends on:** E5 trigger from the year train (M2); I9; I10.

### I13 Equations vitrine — M3

- **Shows:** the solar and lunar correction cylinders, visible in the vitrine on the right of the
  base [S: CLEA, MERP].
- **Original:**
  - Each correction is a cylinder carrying its curve, traced over two periods, with a horizontal
    crossbar riding on it.
  - The cylinders are stacked, each resting on the crossbar below, so the top crossbar's height is
    the sum of all corrections.
  - Pinions are longer the higher their cylinder sits [S: LEF].
  - Three solar terms and five lunar terms [S: LEF].
  - The lunar terms are driven by an arbor turning once per mean day [S: LEF], with the ratios in
    reference-notes (anomaly 70209/2548, etc.).
- **Replica:**
  - Keep the stacked-cam summing principle. It is faithful and visible, and it adds linearly with
    no differential gears.
  - Printed cams, ground-rod crossbar guides, and a rack and pinion at the top turning the summed
    lift into a rotating output shaft for each of the Sun and the Moon. Those shafts feed the M2
    differentials (architecture §4).
  - Cam profiles come from the simulator, i.e. the same formulae the validation uses.
- **Difficulty:** 4.
- **Depends on:** a daily input (own stepper, or a shaft from M2: see architecture); Phase 1 ratios.

### I14 Planetary dial — M5

- **Shows:** heliocentric Mercury, Venus, Earth (with Moon), Mars, Jupiter and Saturn [S: CLEA].
- **Original:** planet periods = year × factor, with factors (44×134)/(240×102), (17×221)/(197×31),
  (95×213)/(203×53), (157×232)/(96×32) and (161×212)/(58×20) [S: CLEA]. That gives 87.968 d …
  29.424 yr [D].
- **Replica:**
  - Reproduce these ratios from a year arbor (itself geared from the M5 1 rev/day input), with
    coaxial tubes for the six arms.
  - Large wheels (221, 232, 212 teeth) fit the bed at module 1.0: tip diameter ≤ 234 mm [D].
  - Earth arm: a small synodic-month train for the Moon.
  - **TBD:** the dial diameter (photo scaling).
- **Difficulty:** 2–3. Six coaxial outputs.
- **Depends on:** M5 input; Phase 1.

### I15 Moon-phase globe — M5

- **Shows:** the Moon's phase on a globe above the planetary dial [S: CLEA].
- **Replica:** a half-dark sphere turned once per synodic month by its own train from the M5 input.
  Phase 1 compares it with Schwilgué's lunar differential.
  - **TBD:** the globe diameter.
- **Difficulty:** 2.
- **Depends on:** M5.

### I16–I17 Celestial globe — M6

- **Shows:** constellations and main stars (more than 5000 stars, down to magnitude 6 [Sn: AHN]);
  sidereal time; precession [S: CLEA]. It sits at floor level in front of the case [S: CLEA].
- **Periods:**
  - Sidereal day = 164,359/164,809 mean days exactly [S: LEF; D].
  - Precession: about 26,000 yr [S: CLEA], or a turn in 25,806 yr [Sn: CATH] [?].
- **Original:**
  - Exact epicyclic train a/A = 45/72, b/B = 18/270, c/C = 18/269, d/D = 26/100, e/E = 18/94,
    whose output is exactly 1 + 450/164,359 turns per mean-day input turn [S: LEF; D].
  - **TBD:** the precession gearing; the current globe's diameter (the 83/86 cm figure is the
    *second* clock's globe [Sn]); the horizon latitude (the old globe was "set for the meridian of
    Strasbourg" [Sn: EQX]).
- **Replica:**
  - Reproduce the exact epicyclic train. The 270- and 269-tooth wheels fit the bed at module 1.0
    (tip ≤ 272 mm) [D].
  - Precession: a worm-reduced train. It moves about 1.4° per century [D: 360°/25,806 yr], so it
    is nearly static over the clock's life. v1 provides the drive point and leaves it set by hand.
  - Horizon ring at the chosen latitude (D2).
- **Difficulty:** 3 (sidereal), 2 (precession).
- **Depends on:** M6 input; D2.

### A1 Angel with bell — E1

- **Behaviour:** "avec un sceptre et une clochette, sonne le premier coup des quarts de l'heure"
  (strikes the first stroke of each quarter on a hand bell, with a sceptre) [Sn: BDM].
- **Replica:** E1 event motor; a cam lifts the arm, which drops onto a small bell. Triggered by the
  quarter cam on M1.
- **Difficulty:** 2.
- **Depends on:** M1 quarter trigger; D8 (sound).

### A2 Angel turning the hourglass — E1

- **Behaviour:** turns the glass at the last stroke of the fourth quarter, i.e. hourly
  [Sn: BDM, VDK, BFA]. Provisionally resolved as hourly; "every quarter" appears only on tourist
  pages.
- **Replica:** the same E1 motor or a second one. It turns the glass 180° per event. Missed events
  only invert the glass, which is harmless.
- **Difficulty:** 2.
- **Depends on:** M1 hour trigger.

### A3 Four ages — E2

- **Behaviour:** child at the first quarter, youth at the half, adult at the third quarter, old man
  on the hour. They pass before Death [S: ENS; Sn: TS].
  - Strokes of 1–4 per age are documented only for the 16th-century clock [Sn].
  - **TBD for the current clock:** strokes and bells.
- **Replica:**
  - The ages carousel's position (which age faces Death) is *state*, so it is indexed by the M1
    time train (a quarter step per quarter), not by counting events.
  - The E2 event motor powers only the striking and figure motion.
  - This keeps the display right after skipped shows (night silence, catch-up); see architecture §6.
- **Difficulty:** 3.
- **Depends on:** M1; E2; D8.

### A4 Death strikes the hours — E2

- **Behaviour:** strikes the hours [Sn], after the old man's quarter.
- **Replica:** a classical rack-and-snail (or count wheel) on the E2 train, from a snail on the M1
  hour arbor, gives 1–12 strokes. The count is decided mechanically; the controller only switches
  the motor.
- **Difficulty:** 2.
- **Depends on:** M1; E2.

### A5 Apostles and Christ — E3

- **Behaviour:** at noon (local mean time), the twelve Apostles pass before Christ, who blesses
  them [S: CLEA; Sn: CATH].
  - **[?]** How often Christ blesses: "raising his hand" [Sn, 19th-c. newspaper].
  - Figures about 18 in high [S: WIKI], so 57 mm at 1:8 [D].
  - Duration: **TBD** (time the Commons video).
- **Replica:** the E3 event motor turns the procession track one full cycle and stops on a locking
  cam. Christ's blessing arm is cam-operated from the same train.
- **Difficulty:** 3: small figures and a reliable track.
- **Depends on:** M1 noon trigger; D2 (whose noon).

### A6 Rooster — E4

- **Behaviour:** crows and flaps its wings at the passage of the 4th, 8th and 12th Apostles
  [S: LOC; Sn: TS], three times [Sn: CATH]. **[?]** One source says at St Peter's passage.
  - The mechanism is mechanical and pneumatic [S: CLEA]. **TBD:** details.
  - The rooster is "life-size" [Sn: WIKI]; **TBD:** a number in centimetres.
- **Replica:**
  - The E4 event motor drives wing and head cams.
  - The crow is triggered from cams on the E3 procession train (synchronised with Apostles 4, 8
    and 12), so the controller does not need to time it.
  - Sound: decision D8 (bellows and reed vs speaker).
- **Difficulty:** 3.
- **Depends on:** E3; D8.

### A7 Computus run — E5

- **Behaviour:** runs on New Year's Eve and sets the movable feasts on the calendar [Sn: CATH].
- **Replica:** a trigger cam on the M2 year train closes a switch at the end of 31 Dec; the E5
  motor powers one computus cycle. This is a *stateful* event: it must also run during catch-up
  (architecture §7).
- **Difficulty:** 5. It is part of I12.
- **Depends on:** M2, M4.

## 4. Items still unknown and how to resolve them

| Unknown | Resolve by |
|---|---|
| Sizes and positions of all dials, the globe, vitrines and figures | Photo scaling (envelope.md §4) once Commons is reachable; or Schwilgué's *Description abrégée* / Bach-Rieb |
| Sunrise/sunset mechanism; calendar-ring drive (continuous vs jump); transfer of Easter to the ring | *Description abrégée* (Google Books, public domain); Schweighaeuser 1876; Bach/Rieb |
| Gregorian corrections and Easter logic of the computus | Flores 2007 (Klinghammer replica); Roegel's study when published; Bach/Rieb |
| The three solar equation terms | Read LEF and CLEA in full (hosts blocked this session) |
| Strokes per age; bells; show durations | *Description abrégée*; time the Commons video |
| Rooster pneumatics | *Description abrégée*; Ungerer |
| Original's behaviour in summer time | Cathedral site; Œuvre Notre-Dame; ask the cathedral |
