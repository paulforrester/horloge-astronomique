# Reference notes — Schwilgué's Strasbourg astronomical clock

Facts gathered before the repo existed (31 Oct 2026). Each entry gives a source. Tags:
**[S]** sourced, **[D]** derived (calculation shown), **[E]** estimate, **[?]** conflicting or
unclear. Add to this file as research continues; never remove a source.

## Sources

| Key | Source |
|---|---|
| ELS | Description of the current clock, early 1920s lecture to the Société astronomique de France — https://www.elsolieltemps.com/pdf/gnomonica/157.pdf (site blocks automated fetch; facts below are from search snippets only — **read the full PDF**) |
| CLEA | Paturel & Dubois, "L'horloge astronomique de la cathédrale de Strasbourg revisitée", Cahiers Clairaut n°102 (2003), based on Bach & Rieb — http://clea-astro.eu/archives/cahiers-clairaut/CLEA_CahiersClairaut_102_02.pdf |
| LEF | Jean Lefort, "L'horloge astronomique de la cathédrale de Strasbourg" (gear mathematics, after Ungerer 1922) — https://bibnum.publimath.fr/IST/IST93039.pdf |
| WIKI | https://en.wikipedia.org/wiki/Strasbourg_astronomical_clock |
| TS | https://www.techno-science.net/fr/definitions/horloge-astronomique-de-strasbourg (mirror of French Wikipedia) |
| LOC | https://local-fr-public.s3.eu-west-3.amazonaws.com/prod/webtool/userfiles/27520/Horloge_astronomique.pdf |
| ENS | https://www.ens-lyon.fr/RELIE/Cadrans/Musee/HorlogesAstro/General/PagesGr/StrasbourgGr.htm |
| AMIS | https://www.amis-cathedrale-strasbourg.eu/2023/03/04/gunther-oestmann-lhorloge-astronomique-de-la-cathedrale-de-strasbourg/ |
| ODY | https://odysseum.eduscol.education.fr/lhorloge-de-strasbourg-decrite-par-frischlin |
| MERP | https://aulavirtual.cui.edu.ar/blog/merpmonde/754105609878700032-the-best-timepiece-in-the-world-imo-strasbourg (visitor blog) |
| PH | Powerhouse Museum Strasburg Clock model — https://artsandculture.google.com/story/EQVhvcQV07ffKQ |
| TELL | Fully printed tellurium — https://www.printables.com/model/288152-mechanical-orrery |
| H2D | https://bambulab.com/es/h2d/tech-specs |

## Overall dimensions

- Case kept from the 16th-century clock: **18 m tall, 7.70 m wide at the base** [S: ELS]. The case
  is three storeys with a spiral staircase, 18 m tall [S: AMIS].
- **[?]** ODY gives 18 m × **8.60 m** for the second clock. Using 7.70 m (ELS describes the current
  clock specifically). Resolve with Bach/Rieb if possible.
- Main apparent-time dial: the Sun hand travels on a dial **2.30 m** in diameter [S: ELS].
- Apostle figures about **18 inches** (~46 cm) tall [S: WIKI, citing an 1896 source].
- Second clock's celestial globe (now in a museum, *not* the current one): 83 cm [S: ODY]. The
  current globe's diameter is **unknown**.
- At 1:8 [D]: height 2.25 m; width 0.9625 m; main dial 287.5 mm; Apostles 57 mm. Day-of-year ring
  on the main dial ≈ π × 287.5 / 365 ≈ 2.5 mm per day.

## Layout, bottom to top [S: CLEA unless noted]

- **Left tower:** contains the drive weights — five weights of 50 kg each. Topped by the rooster
  automaton, which crows at noon while flapping its wings, using a mechanical and pneumatic system.
  It crows and flaps at the passage of the 4th, 8th and 12th Apostles [S: LOC].
- **Celestial globe**, at floor level in front of the case: positions of constellations and main
  stars; includes precession of the equinoxes (one turn in about 26,000 years); sidereal time is
  shown [S: CLEA].
- **Computus** mechanism at the bottom left of the clock [S: TS]; the **solar and lunar equations**
  vitrine is on the other side of the base [S: MERP says the two modules are on either side of the
  base; CLEA names the "Equations solaires et lunaires" vitrine].
- **Main (lower) dial:** apparent motion of the Sun and Moon around the Earth at the centre; sunrise
  and sunset times; solar and lunar eclipses; days of the week; the date of Easter. A black disc
  opposite the Sun represents Earth's shadow. The Moon's rod has variable length so the Moon can
  eclipse the Sun or enter the shadow only when appropriate. Around the edge: every day of the
  year, each preceded by its dominical letter. A dial on the left shows the current year's
  dominical letter. A mechanism behind the dial inserts the day marked "Pâques" in the right place
  and adds a day in leap years.
- **Computus displays:** epact, dominical letter, indiction, solar cycle (28 years), golden number
  (19 years).
- **Weekday carousel** above the main dial: Apollo (Sunday), Diana (Monday), Mars, Mercury,
  Jupiter, Venus, Saturn (Saturday).
- **Mean solar time dial** for Strasbourg (about 30 min different from legal time). Beside it, one
  cherub turns an hourglass **[?]** "every hour (or every quarter)", and the other rings a bell
  every quarter. TS: one angel rings a bell while the second turns an hourglass.
- **Heliocentric planetary dial:** Mercury, Venus, Earth (with Moon), Mars, Jupiter, Saturn.
- **Moon-phase globe** above the planetary dial.
- **Top stages:** the four ages (child, adolescent, adult, old man) pass before Death every quarter
  hour; ENS assigns quarter→child, half→adolescent, three-quarters→man, hour→old man. At noon the
  twelve Apostles pass before Christ and the rooster crows three times.
- Gold hands show mean solar time; silver hands show Central European Time [S: WIKI]. The automata
  run on the clock's own (local mean) time, so the noon show happens at 12:30 legal winter time
  [S: TS, LOC]. Strasbourg mean time is about 31 min ahead of Greenwich [S: ELS snippet].
- A meridian line inside the cathedral, lit through an opening in a side door, is used to check the
  clock against true solar noon [S: CLEA].

## Drive and regulation [S: CLEA]

- Seconds-beating pendulum; drift claimed not to exceed 40 s per year.
- Temperature-compensated pendulum; a compensating spring mechanism keeps torque at the escape
  wheel almost constant.
- Tooth profiles designed to roll rather than rub.

## Schwilgué's gear data

### Yearly motion and planets [S: CLEA; D: arithmetic verified in Python]

- Year: P = (156 × 188 × 269) / (9 × 10 × 10) — source states 365.2422.
  **Note [D]:** as printed, the expression evaluates to 8,765.813, which is 365.2422 × 24. So it
  appears to count turns of an arbor turning once per hour, or a factor of 24 is missing in the
  source. Verify.
- Planet periods = P × factor:

| Planet | Factor | Period [D] | Accepted (CLEA) |
|---|---|---|---|
| Mercury | (44×134)/(240×102) | 87.97 d | 87.97 d |
| Venus | (17×221)/(197×31) | 224.70 d | 224.70 d |
| Mars | (95×213)/(203×53) | 686.93 d | 686.98 d |
| Jupiter | (157×232)/(96×32) | 11.857 yr | 11.86 yr |
| Saturn | (161×212)/(58×20) | 29.424 yr | 29.46 yr |

### Moon [S: CLEA; D: verified]

- Lunar turns per year = (312/24) × [1 − (83×14)/(122×196)] = 12.368267, via a differential.
  Synodic month = P / 12.368267 = 29.53059 d.
- The tilt of the lunar orbit is handled by an inclined toothed wheel [S: CLEA].

### Sidereal motion [S: LEF; D: verified]

- Schwilgué's tropical year: 365 d 5 h 48 min 48 s = 31,556,928 s. Required ratio
  R = 164,359 / 164,809 (164,359 = 13 × 47 × 269; 164,809 is prime-heavy and awkward).
- **Exact method (celestial sphere):** epicyclic train with a/A = 45/72, b/B = 18/270,
  c/C = 18/269, d/D = 26/100, e/E = 18/94. Output per turn of B =
  1 + (100/26)(18/94)[(270/18)(18/269) − 1] = 1 + 450/164,359 = 1/R exactly.
  (Reconstructed from garbled PDF text; arithmetic checks exactly.)
- **Approximate method (Moon motion):** 271,375 / 272,118 ≈ R (error ~1 s per century per LEF),
  realised ×12 because the driving arbor turns once in 2 h:
  (334/28) × (65/341) × (300/57) = 11.96723 = 12 × 271,375/272,118 (verified exactly).

### Solar and lunar equations [S: LEF, CLEA]

- Each periodic correction is a cylinder carrying its curve traced over two periods; a horizontal
  crossbar rides on it. The cylinders are stacked, each resting on the crossbar below, so the top
  crossbar's height equals the sum of all corrections. Largest corrections at the top. Pinions get
  longer the higher their cylinder sits, to allow for the vertical movement [S: LEF].
- The summed movement reaches the Sun or Moon motion through pulleys/rods to a pivoting frame
  (a differential arrangement) [S: LEF], or by raising/lowering a pinion with oblique teeth that
  speeds up or slows the wheel [S: CLEA].
- The Sun needs three corrections; the Moon uses five [S: LEF]. Lunar terms, driven by an arbor
  turning once per mean day (86,400 s):

| Term | Target period | Ratio used | Period obtained [D verified] |
|---|---|---|---|
| Anomaly | 27 d 13 h 18 m 34 s | 70209/2548 | 27 d 13 h 18 m 33.3 s |
| Evection | 31 d 19 h 29 m 11.453 s | 74090/2329 | 31 d 19 h 29 m 11.3 s |
| Variation | 29 d 12 h 44 m 3 s | 51649/1749 | 29 d 12 h 44 m 2.9 s |
| Annual equation | 365 d 6 h 13 m 57 s | 226461/620 | 365 d 6 h 13 m 56.1 s |
| Nodes (draconitic) | 27 d 5 h 5 m 35.8 s | 49880/1833 | 27 d 5 h 5 m 35.8 s |

- **Eclipses:** a cam turning in about 18.6 years lengthens or shortens the Moon hand so it passes
  in front of the Sun disc or not; a similar mechanism handles lunar eclipses [S: LEF].

### Tooth-count practice [S: LEF]

- Wheels limited to about 500 teeth for weight and strength; largest found 420. Largest prime tooth
  count 281 (also 269); composites such as 382, 341, 334, 327, 318. Minimum 6 teeth; smallest prime
  used alone 17.
- Schwilgué chose rational approximations whose factors are small primes (≤ 269), using continued
  fractions and Farey sequences.

## Computus [S: TS, LEF, WIKI]

- Probably the first mechanical Gregorian computus: designed 1816, model presented 1821.
- At the end of each year it determines the movable feasts for the coming year.
- Frédéric Klinghammer built a reduced replica of the computus in the 1970s.
- **Detailed mechanism not yet documented here** — research needed.

## Precedents

- Richard Bartholomew Smith built a working 1:5 model (1887–1889), now at the Powerhouse Museum,
  Sydney; he worked from a postcard and a book and localized dials to Sydney [S: WIKI, PH].
- A fully printed, crank-driven tellurium on Printables shows date with a mechanical year counter,
  Moon phases, apogee/perigee and the lunar nodes. Synodic month 29.5313 d vs 29.5306 d; nodal and
  apsidal cycles (18.5 and 8.8 yr modelled) from near-equal tooth pairs 39/37 and 39/44. Its
  instructions say to approach any date from the same direction to cancel play [S: TELL].

## Printing constraints

- H2D build volume 325×320×325 mm single nozzle; 300×320×325 dual; nozzles 0.2–0.8 mm [S: H2D].
- FDM with 0.4 mm nozzle struggles below module 1.0
  [S: https://www.sovol3d.com/blogs/news/3d-printing-gears-that-actually-work-backlash-orientation-and-material-tips].
- Rule of thumb: module ≈ 4 × nozzle diameter; backlash 0.1–0.3 mm, 0.15 mm a good first guess
  [S: https://makerworld.com/en/models/3276583-parametric-internal-ring-gear-generator].
- Gear tolerance test card, modules 0.5–1.5, 0.4 and 0.2 mm nozzle versions
  [S: https://makerworld.com/models/2221699].
- PLA clock gears reported running ~10 months (~40 M ticks) without noticeable wear
  [S: https://forum.prusa3d.com/forum/original-prusa-i3-mk3s-mk3-how-do-i-print-this-printing-help/printing-tiny-gears-3mm-1cm-from-nylon].

## Location data

- Bordeaux house ≈ 44.83° N, 0.57° W. Local mean time ≈ 2.3 min behind UTC [D], so local mean noon
  is about 13:02 CET in winter and 14:02 CEST in summer.

## Open items / unknowns (research before designing the related module)

- Current celestial globe diameter; planetary dial diameter; Moon-phase globe diameter; diameters
  of the mean-time and other dials.
- Size and layout of the computus and equations vitrines.
- Case depth and the globe's projection in front of it.
- Heights of the other figures (Christ, Death, the four ages, angels, weekday deities); rooster
  size.
- How sunrise and sunset are displayed mechanically on the main dial.
- How the day-of-year ring, Easter insertion and leap-year day work mechanically.
- The computus mechanism in detail.
- Rooster mechanism (mechanical + pneumatic) in detail.
- Resolve: hourglass turned hourly or quarter-hourly.
- Resolve: case width 7.70 m vs 8.60 m.
- Whether the full ELS PDF and the Ungerer / Bach-Rieb books are obtainable (BnF lists the Ungerer
  work; editions of 1949 and 1954 exist).
