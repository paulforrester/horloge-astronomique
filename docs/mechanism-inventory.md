# Mechanism inventory

Phase 0 deliverable. This file lists every indication and automaton of Schwilgué's clock. Each
entry says what it shows and its period(s), how the original does it (with source), the proposed
approach for the replica, its difficulty, and what it depends on.

Tags and source keys are those of `docs/reference-notes.md`. **DA** is Charles Schwilgué's
*Description abrégée de l'horloge astronomique de la cathédrale de Strasbourg*, 2nd edition, 1844.
It is the builder's son's own description, read in full in the Phase 0 research pass; page numbers
refer to its printed pages. **ELS** is now identified as Alfred Ungerer's 1920 lecture, published in
*L'Astronomie* in 1921 in five instalments, cited i1–i5. Ungerer was Schwilgué's successor and
maintained the clock. LEF's gear table reproduces Ungerer's 1922 figure.

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
| Precession of the equinoxes | **25,804 years** "environ" [S: DA p. 26, checked on the page image]; about 26,000 [S: CLEA]; 25,806 [Sn: CATH] | [S] |
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
| I4b | Moon phase on the main-dial Moon (globe silver on one side, black on the other) [S: DA p. 32] | M2 | synodic month | The Moon ball turns on the hand, geared from the Sun–Moon difference | 4 | v1.5 |
| I5 | Eclipse indication (variable-length Moon arm) | M2 | draconitic month; 18.6 yr; eclipse year | Node cam plus a radial slide on the Moon arm | 4 | v1.5 |
| I6 | Earth-shadow disc | M2 | apparent solar day | Rigid with the Sun hand, 180° opposite | 1 | v1 |
| I7 | Sunrise and sunset times | M2 | tropical year | Two hands moved symmetrically by a cam turning once a year [S: ELS i1] (DA's "horizon mobile"); cam cut for Bordeaux (D2) | 3 | v1.5 |
| I8 | Annual calendar ring | M2 + E6 | civil year (365/366 d) | Copy Schwilgué [S: ELS i4]: 368-division ring on rollers, advanced each midnight by its own event motor; a projection and cam give 3 or 4 divisions at New Year; the century wheel applies the 4/100/400 rules | 3 | v1 |
| I9 | Movable feasts / Easter and leap day on the ring | M2 ← M4 | yearly | Sliding feasts arc set by the computus; leap gate from the 4-year count | 4–5 | v1 leap, v2 feasts |
| I10 | Dominical letter of the year | M2 ← M4 | yearly | Seven-position dial set by the computus | 2 | v2 (v1: set by hand) |
| I11 | Weekday carousel (seven deities) | M7 (driven by M2) | 7 d | 7:1 from the daily arbor; continuous on a circular rail [S: DA p. 47] | 2 | v1 |
| I12 | Computus: solar cycle, golden number, indiction, dominical letter, epact (+ year?) | M4 | 28 / 19 / 15 yr; Gregorian 100/400 yr corrections | Mechanical computus with count wheels plus rack-and-snail Easter finder, run as an event on 31 Dec | 5 | v2 |
| I13 | Equations vitrine (cams visible) | M3 | 8 periods (above) | Stacked cams with summing crossbars (Schwilgué principle) | 4 | v1.5 |
| I14 | Planetary dial (heliocentric) | M5 | 88 d … 29.4 yr | Schwilgué's published ratios from a year arbor | 2–3 | v1 |
| I15 | Moon-phase globe | M5 | synodic month | Ratio train or differential (Schwilgué) | 2 | v1 |
| I16 | Celestial globe: sidereal rotation | M6 | sidereal day | Schwilgué's exact epicyclic train | 3 | v1 |
| I17 | Celestial globe: precession | M6 | 25,804 yr [S: DA p. 26] | Worm-reduced train; nearly static | 2 | v2 (provisioned in v1) |
| I18 | Exterior Gothic dial over the portal (mean time and weekday; circumference about 16 m) [S: DA p. 62–63] | — | — | **Out of scope**: it is on the cathedral façade, not part of the clock case | — | — |
| A1 | Angel with bell (first stroke of each quarter) | E1 | 15 min | Event motor plus cam-lifted arm and bell | 2 | v1 |
| A2 | Angel turning the hourglass | E1 | 1 h | Event motor turns the glass 180° | 2 | v1 |
| A3 | Four ages strike the quarters | E2 | 15 min (one cycle per hour) | Ages carousel indexed by the time train; event motor strikes | 3 | v1 |
| A4 | Death strikes the hours | E2 | 1 h (1–12 strokes) | Rack or count wheel on the event train | 2 | v1 |
| A5 | Apostles pass before Christ, who blesses | E3 | daily, at mean noon | Event motor turns the procession once; blessing arm on a cam | 3 | v1 |
| A6 | Rooster crows three times and flaps its wings | E4 | daily, during A5 | Event motor plus wing and head cams; sound per D8 | 3 | v1 |
| A7 | Computus run | E5 = M4 | yearly, night of 31 Dec | Trigger cam on the year train; motor powers the computus cycle | 5 | v2 |
| A8 | Calendar advance at midnight | E6 | daily (3 or 4 divisions at New Year) | Event motor released by the time train; the stop lever is held by the ring's projection [S: ELS i4]. Stateful: must run during catch-up. | 3 | v1 |

## 3. Details

### I1 Local mean time (gold hands) — M1

- **Shows:** local mean time [S: WIKI]. "In 1842 the dial showed only Strasbourg mean time" [Sn: CATH].
- **Periods:** minute hand 1 h. **TBD:** whether the hour hand is on a 12 h or a 24 h dial.
  Resolve from a frontal photo or Schwilgué's *Description abrégée*.
- **Original:** driven from the going train regulated by the seconds pendulum [S: CLEA]. Details TBD.
- **Schwilgué's description [S: DA p. 49–50]:**
  - "un petit cadran destiné à l'indication du temps moyen" (a small mean-time dial) in the middle
    of the "galerie aux lions". The two wooden lions come from the old clock and never moved.
  - "Le moteur central de l'horloge communique directement aux aiguilles du temps moyen le
    mouvement qui les anime". The sidereal and apparent times go through "mécanismes particuliers
    propres à modifier la vitesse" (special mechanisms that modify the speed).
  - The single central motor is wound once every 8 days.
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
- **Ungerer [S: ELS i1]:** "les aiguilles argentées, ajoutées en Mars 1919, donnent l'heure
  légale". The legal-time hands are a **1919 addition**, not Schwilgué's.
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
- **Schwilgué's description [S: DA p. 30–32, 44–46]:**
  - The area inside the calendar ring "est uniquement destinée aux indications du temps apparent".
  - "Le cadran du temps apparent, peint en azur, est entouré d'un cercle en argent sur lequel on
    voit deux fois les heures de 1 à 12 avec leurs subdivisions en minutes" (azure dial, silver
    ring, twice 1–12 hours with minute divisions).
  - The Sun hand is azure like the dial and ends in a gilded rayed disc. The Sun and Moon discs
    are sized to the mean apparent diameters, so they can show eclipses.
  - A northern hemisphere at the centre is oriented with the Strasbourg meridian vertical (Paris
    passes about 22 min later, Vienna about 34 min earlier).
  - The solar part of the equations works "par l'anomalie pour obtenir la longitude vraie, laquelle
    à son tour est convertie en ascension droite vraie" (from the anomaly to the true longitude,
    then converted to true right ascension).
- **Ungerer [S: ELS i1–i2]:**
  - The dial is 2.30 m, "divisé en 2 fois 12 heures, qui représente le plan de l'équateur".
  - The Sun hand is "exactement de 1 mètre", so 1° = 17.45 mm.
  - The equation cams use "6mm de déplacement vertical pour un degré de correction".
  - The conversion to right ascension uses a helical pinion with a 12°13′ lead.
- **Replica:**
  - Mean Sun = the M2 input arbor (1 rev per mean day on a 24 h dial).
  - A differential (printed spur or bevel) sits between the mean-Sun arbor and the Sun hand. Its
    third member is turned by the M3 solar-correction output (range ±4.1° at the hand).
  - Two terms, the equation of centre (±7.7 min, anomalistic year) and the reduction to the
    equator (±9.9 min, half year) [D], account for most of the equation of time. With two terms
    the residual is under about 1 min (estimated from the neglected terms of MEEUS eq. 28.3; to
    confirm in Phase 1). A third term brings the residual down further.
  - In v1 the differential's third member is locked by a removable key, so the hand shows mean
    solar time. The upgrade path is in architecture §13 (D5 accepted: steady speeds first).
- **Difficulty:** 3.
- **Depends on:** M3; the tropical/anomalistic-year arbor; D5.

### I4 Moon (main dial) — M2 + M3

- **Shows:** the Moon around the Earth [S: CLEA]. The rod's length varies (see I5) [S: CLEA].
- **Periods:** one turn per lunar day (24 h 50.47 min [D]); synodic month 29.53059 d. Five
  periodic corrections [S: LEF] (periods in §1).
- **Original:** lunar turns per year = (312/24) × [1 − (83×14)/(122×196)] = 12.368267 via a
  differential [S: CLEA]. The tilt of the lunar orbit uses an inclined toothed wheel [S: CLEA].
  The corrections come from the equations vitrine [S: LEF].
- **Schwilgué's description [S: DA p. 31–32, 44–45]:**
  - The dial shows "le mouvement diurne vrai de la lune autour de la terre, ou son ascension droite
    vraie, et son passage au méridien" (the Moon's true diurnal motion, i.e. its true right
    ascension, and its meridian passage), and "les phases de la lune".
  - The Moon hand ends in "un petit globe à couleur argentine d'un côté et noir de l'autre" (a small
    globe, silver on one side, black on the other), so the phase shows on the main dial too (I4b).
  - Lunar equations: centre, evection, variation, annual equation, reduction, plus "l'Equation
    relative aux nœuds". A further mechanism inside the clock "convertir en ascension droite de la
    lune, la longitude vraie".
- **Ungerer/Lefort:**
  - The five lunar cams (reduction, annual equation, variation, evection, centre) sum to "102mm,7"
    of travel [S: ELS i2]; evection follows Burckhardt's tables.
  - The Moon's daily motion comes from an arbor turning once in 2 h, through
    334/28 × 65/341 × 300/57 [S: LEF].
- **Replica:**
  - Mean Moon: reproduce Schwilgué's differential, or an equivalent compound train (Phase 1
    compares them).
  - True Moon: a second differential fed by the M3 lunar-correction output.
  - Amplitudes the replica needs (standard lunar theory, MEEUS ch. 47; to be confirmed in Phase 1):
    equation of centre ≈ 6.3°, evection ≈ 1.3°, variation ≈ 0.7°.
  - In v1 the Moon hand shows the mean Moon, through the same keyed-differential provision
    (architecture §13).
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
- **Schwilgué's description [S: DA p. 33–36]:**
  - The Moon's latitude is shown "par la position de la lune, selon qu'elle se trouvera placée
    au-delà ou en-deçà du soleil" (by the Moon being placed beyond or short of the Sun), i.e. a
    radial offset.
  - A lunar eclipse is the occultation of the Moon globe "par un disque représentant une section du
    cône d'ombre de la terre" (by a disc representing a section of the Earth's shadow cone); it can
    be partial or total, northern or southern.
  - The clock shows all eclipses, visible at Strasbourg or not. The hemisphere at the centre shows
    where they are visible.
- **Ungerer [S: ELS i2]:**
  - Latitude cam: mean radius 134 mm, "R = 154mm,2 et r = 113mm,8" (19.3 / 14.2 mm at 1:8 [D]).
  - Disc diameters: Sun 9.3 mm, Moon 9.1 mm, Earth-shadow 24.3 mm, all at 17.45 mm per degree. At
    1:8 these are about 1.2 mm [D], too small to see: see `envelope.md` §5 for the enlargement
    options. Choose in the Phase 2 main-dial study.
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

- **Shows:** sunrise and sunset times [S: CLEA].
- **Original [S: DA p. 31–32]:**
  - "Les heures du lever et du coucher du soleil sont indiquées à l'aide d'un horizon mobile qui
    divise en deux le cercle parcouru par le soleil" (a *mobile horizon* that divides the Sun's
    circle in two), from which the lengths of day and night can be read.
  - About 6 h / 6 h at the equinoxes, 4 h / 8 h at the summer solstice, 8 h / 4 h at the winter
    solstice.
  - The times are "exprimées en temps vrai ou apparent" and "se rapportent au méridien de
    Strasbourg", with refraction taken into account.
  - **TBD:** the mechanism that moves the horizon.
- **Periods:** tropical year. The amplitude depends on latitude.
- **Replica:**
  - A cam on the continuous tropical-year arbor. Its profile is the semi-diurnal arc H0(δ), with
    cos H0 = (sin h0 − sin φ sin δ)/(cos φ cos δ), h0 = −0.833°, φ = chosen latitude.
  - **Ungerer [S: ELS i1]:** "Deux aiguilles (11) portant les inscriptions « Lever du Soleil » et
    « Coucher du Soleil » sont actionnées symétriquement par une courbe décrivant un tour en une
    année". So DA's "horizon mobile" is a pair of hands.
  - The replica copies this: a scissor linkage moves the two hands symmetrically, from a yearly
    cam.
  - **Bordeaux latitude** (D2, accepted): φ = 44.83°. The cam is a swappable printed part.
  - The horizon is turned by the longitude difference (33.3 min of time, i.e. 8.32° on the 24 h
    dial [D]), so the Sun hand crosses it at the real Bordeaux sunrise and sunset (D2, accepted).
- **Difficulty:** 3.
- **Depends on:** the tropical-year arbor; D2; I3 (if the dial is in apparent time).

### I8 Annual calendar ring — M2

- **Shows:** every day of the year, each preceded by its dominical letter [S: CLEA]. "Une bande
  métallique, en forme d'anneau, n'ayant que 25 centimètres de largeur sur une circonférence de
  passé 9 mètres, porte, sur un fond doré, toutes les indications d'un calendrier perpétuel: le
  mois, les quantièmes, les lettres dominicales, les noms des Saints et des Saintes, ainsi que les
  fêtes fixes" [S: DA p. 27; width and circumference checked on the page image].
  - **Apollo points**: he stands to the right of the calendar and shows the day "avec une flèche".
    Diana is on the other side "seulement pour servir de pendant" (only as a counterpart)
    [S: DA p. 27]. This resolves the Apollo/Diana conflict.
- **Periods:** the civil year, 365 or 366 days.
- **Original:**
  - **It jumps daily at midnight:** "Cet anneau, qui est mobile, avance chaque jour d'une
    division, le passage d'un jour à un autre s'effectuant instantanément à minuit" [S: DA p. 27].
  - It turns in 365 or 366 days and "reproduit en outre l'irrégularité connue sous le nom de
    bissextiles séculaires, c'est-à-dire qu'il opère de lui-même ... la suppression de 3 jours en
    400 années" (it applies the Gregorian century rule by itself) [S: DA p. 27–28].
  - Between 31 Dec and 1 Jan the ring carries the words "commencement de l'année commune". In leap
    years "le mot de « commune » disparaît, et un nouveau jour s'intercale entre le 28 février et
    le 1er mars" [S: DA p. 28]. **TBD:** the mechanism.
  - Size [?]: DA gives a circumference over 9 m (Ø > 2.86 m) and a width of 25 cm. **Ungerer
    gives "2m,73 de diamètre extérieur et de 21 centimètres de large, divisé en 368 fuseaux"**
    [S: ELS i4], and the forged rings were machined at 2.73 m. The design uses Ungerer's figures.
  - **Ungerer's mechanism [S: ELS i4]:**
    - The ring sits on two rollers. It "avance chaque jour à minuit d'un fuseau, sous l'action d'un
      moteur spécial déclanché par le rouage de temps moyen" (it has its own motor, released by the
      time train).
    - 1 Jan – 28 Feb are on a movable sector. Three divisions read "COMMENCEMENT DE L'ANNÉE
      commune". In leap years the sector covers "commune" and uncovers 29 Feb.
    - The New Year advance is 4 divisions (common years) or 3 (leap years). A projection S holds the
      stop lever L up; a cam E lengthens S in common years.
    - E is set by wheel C, which turns 1/100 of a turn per year through a 6-point star and a fixed
      3-tooth rake. C carries 24 projections for years 4, 8, …; a satellite wheel brings in the
      25th projection every 400 years.
    - The sector is moved by a connecting rod from a second star-and-rake pair.
- **Replica:**
  - **Copy Schwilgué's mechanism** (above).
    - It matches rule 4: the time train releases the event, an event motor (E6) supplies the
      energy, and the ring's projection decides when it stops.
    - It also matches rule 2: the 4/100/400 logic is entirely in wheel C and its satellite.
  - The ring runs on rollers (printed or bearing-backed), with a 368-division scale.
  - Because the century logic is self-contained, **include it in v1**. This revises D5, which had
    deferred the 2100 exception.
  - E6 is *stateful*: it must run during catch-up (architecture §5, §8).
  - **Bed fit: the ring must be segmented.** At 1:8 it is 341 mm across and 26 mm wide (ELS
    figures [D]), larger than the 320 mm bed.
    - Four 90° segments (chord 241 mm [D]) on a carrier ring fit easily.
    - Join the segments at day boundaries.
  - Gregorian century rule: DA confirms the original applies it automatically. It stays v2 in the
    replica (D5); the next exception is 2100.
- **Difficulty:** 3.
- **Depends on:** the M2 daily arbor; I9.

### I9 Movable feasts and leap day on the ring — M2 ← M4

- **Shows:** the day marked "Pâques" is inserted in the right place and a day is added in leap
  years [S: CLEA]. Ascension, Pentecost and the other dependent feasts are placed on the calendar
  each 31 December [Sn].
- **Original [S: DA p. 28–29, 43]:**
  - Movable feasts shown: "la Septuagésime, le Mercredi des cendres, le Dimanche de la Passion,
    celui des Rameaux, le Vendredi-saint, la fête de Pâques, celle de l'Ascension, la Pentecôte, la
    Trinité, la Fête-Dieu et deux des Quatre-Temps, etc."
  - They "se placent d'elles-mêmes chaque année, le 31 décembre, à minuit" and keep their position
    for the year.
  - Easter "est immédiatement transmise au calendrier, où elle sert de véhicule aux autres époques
    variables de l'année qui sont dans sa dépendance". Easter is the *carrier* of its dependent
    feasts, which supports the feasts-arc approach below.
  - Separate mechanisms show the first Sunday of Advent (and the Ember days that depend on it) and
    the feast of St Arbogast, "un dimanche dans la dernière quinzaine du mois de juillet".
  - **TBD:** the transfer mechanism. The 1821 model has no transfer train [Sn: WSC].
- **Replica (proposal):**
  - **Confirmed as the original's method:** "Celles de ces fêtes qui dépendent de Pâques sont
    réunies par un cercle en fer qui peut glisser sur des galets sur le bord intérieur du
    calendrier" [S: ELS i4] (the Easter-dependent feasts are joined by an iron circle sliding on
    rollers along the ring's inner edge).
  - All Easter-dependent feasts sit at fixed day offsets from Easter. Examples, from the Gregorian
    rules: Ash Wednesday −46, Ascension +39, Pentecost +49.
  - So one rigid "feasts arc" sliding in a groove of the ring can carry all of them.
  - The computus positions this arc once a year, over a 35-day range (22 March–25 April)
    [S: DA p. 42–43].
  - Advent and St Arbogast are Sunday-dependent, not Easter-dependent. They need their own small
    sliders, set from the dominical letter (v2).
  - The leap-day function is in I8.
- **Difficulty:** 4 (transfer) to 5 (the computus itself).
- **Depends on:** M4; I8.

### I10 Dominical letter of the year — M2 ← M4

- **Shows:** the current year's dominical letter, on a small dial on the left [S: CLEA].
- **Original:** leap years have two dominical letters, "dont la première sert depuis le
  commencement de l'année jusqu'à la fin du mois de février, et dont l'autre est en fonctions
  depuis le 1er mars" [S: DA p. 41]. **TBD:** how the dial shows them.
- **Replica:** a seven-position dial with a jumper.
  - v1: set by hand each 1 January.
  - v2: driven by the computus.
- **Difficulty:** 2.
- **Depends on:** M4.

### I11 Weekday carousel — M7

- **Shows:** Apollo (Sunday), Diana, Mars, Mercury, Jupiter, Venus, Saturn [S: CLEA], on chariots
  [Sn].
- **Original [S: DA p. 46–48]:** the chariots, drawn by each deity's animals with wheels bearing
  the deity's and the day's names, "roulent sur un chemin de fer circulaire, en suivant un
  mouvement continu" (run on a circular rail in continuous motion). The noon phasing is still only
  [Sn].
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
- **Schwilgué's description [S: DA p. 36–43]:**
  - The computus "sert à régler: 1. le Millésime; 2. le Cycle solaire; 3. le Nombre d'or ou Cycle
    lunaire; 4. l'Indiction romaine; 5. la Lettre dominicale; 6. les Epactes; 7. la Fête de
    Pâques".
  - The four-digit year is on four circles of ten digits: units, tens, hundreds, thousands.
  - The mechanism contains "toutes les modifications introduites par le calendrier grégorien et
    toutes les équations lunaires nécessaires à leur rectification".
  - "Chaque année, le 31 décembre, à minuit, le comput ecclésiastique se trouvera dégagé par
    l'horloge, pour se mettre en mouvement et déterminer toutes les indications des cycles relatifs
    à la nouvelle année". Those indications then "régler d'elles-mêmes le mécanisme principal du
    comput" to fix Easter, which is passed to the calendar (I9).
  - In other words: released by the clock, then a two-stage computation (cycles first, then
    Easter). This matches E5's trigger-and-run design.
- **Ungerer [S: ELS i4–i5]:**
  - The epact disc carries "un limaçon à degrés", a stepped snail whose steps cover the dates of the
    Paschal 14th day, 21 March–18 April, at "4 millimètres" per step.
  - Piece N and cam x, on the golden-number arbor, apply the epact XXV/25 rule.
  - "Un grand rateau R" rests on the snail with its heel; each step moves it one day. In the 1821
    model this rack carries the Easter hand. It matches Roegel's "grand râteau".
  - The full description (more figures and counts) is in ELS i4–i5. **Use it as the v2 design
    basis**, so that D7 can be "faithful" after all.
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
- **Schwilgué's description [S: DA p. 43–46]:** the vitrine is labelled "équations solaires
  et lunaires". It does three things:
  - converts mean time to true time for the Sun;
  - converts the Moon's mean longitude to its true longitude;
  - corrects the lunar nodes to obtain the Moon's latitude.

  The mechanisms are "visibles derrière une belle glace" (behind glass). The longitude-to-right-
  ascension converter for the Moon is inside the clock, not in the vitrine.
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
- **Schwilgué's description [S: DA p. 51–53]:**
  - A Copernican "planétaire" on the storey above the lion gallery, on a large azure dial.
  - The gilded Sun disc in the centre "n'est soutenu par aucun support" (has no visible support).
  - Twelve rays from the Sun lead to the zodiac signs painted on the circumference.
  - "Sept petites sphères dorées" (seven small gilded spheres) are sized to the planets' apparent
    dimensions.
  - Stated periods: about 88 d, 225 d, 365 d 5 h 48 min 48 s (Earth), 687 d, 4330 d, 10747 d.
    These agree with the CLEA factors [D].
  - The Moon goes round the Earth "dans l'espace du mois lunaire".
- **Ungerer/Lefort:**
  - "Autour d'un cercle de 2m,20 de diamètre sont peints les douze signes du Zodiaque"
    [S: ELS i2]. The band is about 2.75 m outer [E, plate], so it prints in segments.
  - Planet arbors stand on a crown of 20 cm radius, with intermediate wheels of ≤ 250 teeth
    [S: ELS, agent extraction].
  - Gear table [S: LEF, Ungerer's fig. 49, page image checked]:
    - Earth: A = A′; 9/156, 10/188, 10/269.
    - Mercury: 44/240, 102/134.
    - Venus: 17/197, 31/221.
    - Mars: 95/203, 53/213.
    - Jupiter: 96/157, 32/232.
    - Saturn: 58/161, 20/212.
  - The Earth train's product equals the year in hours, so the input A turns **once per hour**
    [D, inference]. Our M5 input rate (1 rev/day) must add a 24:1 stage, or the module can take
    an hourly input.
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
- **Schwilgué's description [S: DA p. 53–55]:** "un globe spécialement destiné à rendre
  visibles les phases de la lune. En tournant sur son axe, ce globe, qui est incliné, s'éclaire et
  s'obscurcit" (an *inclined* globe on a starry sky, turning on its axis).
- **Ungerer/Lefort:**
  - "un globe de 40 centimètres de diamètre, mi-partie doré, mi-partie noir", axis tilted about 40°
    [S: ELS i3]. That is 50 mm at 1:8.
  - Gear table "Lune: k/K = 83/122; l/L = 14/196; J/j = 312/24" [S: LEF]. This is the differential
    CLEA describes: the planetarium and Moon-globe train.
- **Replica:** a half-dark sphere turned once per synodic month by its own train from the M5 input.
  Phase 1 compares it with Schwilgué's lunar differential.
  - **TBD:** the globe diameter.
- **Difficulty:** 2.
- **Depends on:** M5.

### I16–I17 Celestial globe — M6

- **Shows [S: DA p. 24–26]:**
  - "Au bas du monument est placée une sphère céleste, indiquant sur un cadran le temps sidéral"
    (sidereal time on a dial).
  - The sphere is "construite en cuivre et supportée par quatre belles colonnes en métal, est
    disposée pour la latitude de Strasbourg".
  - All stars of the first six magnitudes, "au nombre de passé 5000", grouped in **110**
    constellations (checked on the page image; the OCR reads "1 1").
  - The equator, ecliptic and colures turn with the sphere. The meridian and horizon circles stay
    fixed, showing the rising, setting and meridian passage of every naked-eye star.
- **Periods:**
  - Sidereal day = 164,359/164,809 mean days exactly [S: LEF; D].
  - Precession: the moving circles complete their retrograde turn in "environ 25,804 années"
    [S: DA p. 26; checked on the page image, the OCR reads 26,804]. DA's footnote says periods are
    given only to their main units.
- **Original:**
  - Exact epicyclic train a/A = 45/72, b/B = 18/270, c/C = 18/269, d/D = 26/100, e/E = 18/94,
    whose output is exactly 1 + 450/164,359 turns per mean-day input turn [S: LEF; D].
  - **TBD:** the precession gearing and the sphere's diameter (the 83/86 cm figure is the
    *second* clock's globe [Sn]). The second clock's globe was papier-mâché, weighed about 50 kg
    and showed 1020 stars in 48 constellations [S: DA p. 14].
- **Ungerer [S: ELS i3]:**
  - "une sphère en cuivre de 0m,84 de diamètre, peinte en bleu" (105 mm at 1:8). The polar axis is
    "incliné de 48°35 sur l'horizon", i.e. Strasbourg's latitude.
  - Precession "25 806 ans … fournie par la constante de Bessel (50″,22)" (DA: 25,804).
  - For the Bordeaux sky (D2) the axis is set at 44°50′.
- **Replica:**
  - Reproduce the exact epicyclic train. The 270- and 269-tooth wheels fit the bed at module 1.0
    (tip ≤ 272 mm) [D].
  - Precession: a worm-reduced train. It moves about 1.4° per century [D: 360°/25,804 yr], so it
    is nearly static over the clock's life. v1 provides the drive point and leaves it set by hand.
  - **Bordeaux sky** (D2, accepted): horizon ring at 44.83° N. The globe's phase is set to
    Bordeaux local sidereal time (Strasbourg − 33.3 min [D]) through M6's own setting offset.
- **Difficulty:** 3 (sidereal), 2 (precession).
- **Depends on:** M6 input; D2.

### A1 Angel with bell — E1

- **Behaviour [S: DA p. 50]:** "Le génie placé à la gauche du spectateur, tient d'une main un
  sceptre et porte dans l'autre un timbre, sur lequel il frappe le premier coup de chaque quart
  d'heure, le second étant répété ... par l'un des quatre âges". He gives the ages their signal.
  (The genie is on the spectator's left, with a sceptre in one hand and a bell in the other.)
- **Replica:** E1 event motor; a cam lifts the arm, which drops onto a small bell. Triggered by the
  quarter cam on M1.
- **Difficulty:** 2.
- **Depends on:** M1 quarter trigger; D8 (sound).

### A2 Angel turning the hourglass — E1

- **Behaviour [S: DA p. 51, checked on the page image]:** "tient des deux mains un clepsydre
  rempli de sable rouge, qu'il retourne chaque heure tantôt d'un demi tour à droite, tantôt d'un
  demi tour à gauche ... chaque fois au dernier coup des quatre quarts, un instant avant que la
  Mort ne sonne les heures".
  - **Hourly: resolved.**
  - The glass holds red sand and turns half a turn alternately right and left.
- **Replica:** the same E1 motor or a second one. It turns the glass 180°, alternating direction,
  e.g. a crank and rocker giving ±180°. Missed events only swap the direction parity, which is
  harmless.
- **Difficulty:** 2.
- **Depends on:** M1 hour trigger.

### A3 Four ages — E2

- **Behaviour [S: DA p. 56–58]:**
  - "Quatre figurines ... paraissent alternativement pour sonner les quarts d'heure, dont ils ne
    font entendre que le second coup, le premier étant frappé par le génie au sceptre".
  - The child strikes the first quarter with a thyrsus, the youth (a hunter) the half with an
    arrow, the man (a warrior in armour) the three-quarters with a sword, and the old man the four
    quarters with his crutch, "un instant avant que l'heure sonne".
  - Each "en sortant de sa loge, fait deux pas pour s'approcher d'un timbre suspendu tout auprès";
    it stays to strike "le nombre de coups voulu", then disappears for the next.
  - **The ages work only by day:** they "ne fonctionnent que pendant la durée du jour"; the central
    motor produces "la suspension des fonctions des quatre âges pendant la nuit" [S: DA p. 58, 65].
    Night silence is original behaviour (D10).
  - **[?]** How the strokes split between genie and age (e.g. paired strokes per quarter). Read the
    full text closely, or watch a video.
- **Replica:**
  - The original has four separate lodges with figures that step out, not a carousel. Which age
    appears is *state*, so it is selected by the M1 time train (a quarter cam picks the lodge), not
    by counting events.
  - The E2 event motor powers only the striking and figure motion.
  - This keeps the display right after skipped shows (night silence, catch-up); see architecture §6.
- **Difficulty:** 3.
- **Depends on:** M1; E2; D8.

### A4 Death strikes the hours — E2

- **Behaviour [S: DA p. 57–58]:** "La Mort, armée d'une faulx, se tient sur un socle au milieu
  de la salle réservée aux quatre âges". At each hour it lets "tomber sur le timbre à sa droite
  l'os qu'elle porte à la main" (drops the bone it holds onto the bell at its right). It strikes
  day and night.
- **Replica:** a classical rack-and-snail (or count wheel) on the E2 train, from a snail on the M1
  hour arbor, gives 1–12 strokes. The count is decided mechanically; the controller only switches
  the motor.
- **Difficulty:** 2.
- **Depends on:** M1; E2.

### A5 Apostles and Christ — E3

- **Behaviour [S: DA p. 58–59]:**
  - "Chaque jour, à l'instant où la Mort a frappé le dernier coup de midi", the twelve Apostles pass
    before Christ: Pierre, Jean, Jacques majeur, André, Barthélemi, Philippe, Simon, Jacques mineur,
    Matthieu, Thomas, Jude, Mathias.
  - Each "se retourne vers lui et incline sa tête en signe de salutation" and leaves after
    receiving the blessing. "Ce n'est qu'après le départ du dernier apôtre que le Christ donne la
    bénédiction en forme de croix."
  - Christ holds "la bannière de la rédemption" and extends the other hand to bless.
  - Figures about 18 in high [S: WIKI], so 57 mm at 1:8 [D].
  - Duration: **TBD** (time the Commons video).
- **Replica:** the E3 event motor turns the procession track one full cycle and stops on a locking
  cam. Christ's blessing arm is cam-operated from the same train.
- **Difficulty:** 3: small figures and a reliable track.
- **Depends on:** M1 noon trigger; D2 (whose noon).

### A6 Rooster — E4

- **Behaviour:**
  - "Durant la marche des apôtres, le coq, perché au sommet de la tourelle aux poids, entonne son
    chant de victoire; mais, avant de se faire entendre, il bat des ailes, sa tête, sa queue,
    s'agitent et son cou se gonfle" [S: DA p. 59].
  - "tous les jours, à midi, il chante trois fois" [S: DA p. 60].
  - At the 4th, 8th and 12th Apostles [S: LOC; Sn: TS]. DA does not say which Apostles.
  - Size: "exécuté d'après nature, il est aussi grand que celui qui a figuré aux deux anciennes
    horloges" (made from nature, as large as the earlier clocks' rooster) [S: DA p. 59–60].
    **TBD:** a number in centimetres.
  - The mechanism is mechanical and pneumatic [S: CLEA]. **TBD:** details.
- **Sound mechanism [S: ELS i5]:** "L'appareil qui produit le chant du coq est placé sous le
  couronnement de l'horloge".
  - A bellows is inflated when a wire lifts weight b. At the crow the wire is "subitement lâché"
    and the weight drives the air out.
  - The air vibrates "une anche g … constituée par une bandelette de papier tendu, … par le
    ressort l" (a reed made of a tensioned paper strip).
  - A trumpet f aimed at the rooster amplifies the sound.
  - A cam d, driven from a rack on the bellows' moving wall, works the exhaust valve, so the crow
    starts "clair et strident" and falls "de plus en plus grave".
  - This is a buildable, fully mechanical design (D8).
- **Replica:**
  - The E4 event motor drives wing and head cams.
  - The crow is triggered from cams on the E3 procession train (synchronised with Apostles 4, 8
    and 12), so the controller does not need to time it.
  - Sound: decision D8 (bellows and reed vs speaker).
- **Difficulty:** 3.
- **Depends on:** E3; D8.

### A7 Computus run — E5

- **Behaviour:** released by the clock at midnight on 31 Dec; it sets the cycles, then Easter,
  then the feasts on the calendar [S: DA p. 43].
- **Replica:** a trigger cam on the M2 year train closes a switch at the end of 31 Dec; the E5
  motor powers one computus cycle. This is a *stateful* event: it must also run during catch-up
  (architecture §7).
- **Difficulty:** 5. It is part of I12.
- **Depends on:** M2, M4.

## 4. Items still unknown and how to resolve them

| Unknown | Resolve by |
|---|---|
| Sizes and positions of all dials, the globe, vitrines and figures | Photo scaling (envelope.md §4). Commons is reachable now, but it rate-limited this session. |
| How the mobile horizon, the leap-day insertion and the Easter transfer are driven (DA gives what they show, not how) | The fuller description with ten plates that DA announces (p. 5); Schweighaeuser 1876; Bach/Rieb |
| Gregorian corrections and Easter logic of the computus | Flores 2007 (Klinghammer replica); Roegel's study when published; Bach/Rieb |
| The solar terms in detail (DA: anomaly → true longitude → right ascension) | LEF and CLEA in full (LEF refuses automated download; CLEA does not resolve). Paul to download them. |
| How strokes split between genie and age; show durations | Close reading of DA; time the Commons video |
| Rooster pneumatics | Ungerer; Bach/Rieb |
| Original's behaviour in summer time | Cathedral site; Œuvre Notre-Dame; ask the cathedral |
