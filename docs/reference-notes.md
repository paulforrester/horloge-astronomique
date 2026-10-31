# Reference notes — Schwilgué's Strasbourg astronomical clock

Facts gathered before the repo existed (31 Oct 2026). Each entry gives a source. Tags:
**[S]** sourced, **[D]** derived (calculation shown), **[E]** estimate, **[?]** conflicting or
unclear. Add to this file as research continues; never remove a source.

**[Sn]** (added in Phase 0) means *search-snippet only*. The wording came back from a web-search
tool, but the page itself could not be opened because the cloud session's network policy blocked
the host. Treat [Sn] facts as leads: confirm them on the page before any design depends on them.
Phase 0 additions are in the section "Phase 0 additions" at the end of this file.

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

---

## Phase 0 additions (31 Oct 2026)

### How this research was done (read first)

The cloud session's network policy allowed only package registries and GitHub. Every other
source host was refused, both from the shell and from the fetch tool:

- the three key PDFs (`clea-astro.eu`, `bibnum.publimath.fr`, `www.elsolieltemps.com`);
- Wikipedia and Wikimedia Commons;
- `gallica.bnf.fr`, `archive.org`, `books.google.com`, `numistral.fr`;
- `pop.culture.gouv.fr`, `cathedrale-strasbourg.fr`;
- retailer sites.

So, apart from **RGL** below (read in full through its GitHub repository), every new fact in this
section is **[Sn]**. The hosts to allow for a follow-up research session are listed in
`docs/decisions.md` → "Blockers".

### New sources

| Key | Source |
|---|---|
| RGL | Denis Roegel, "Le comput ecclésiastique de Schwilgué (1821) — Étude et description complète", web page dated 21 Mar 2025 — https://comput1821.github.io/ (read in full from its source repo https://github.com/comput1821/comput1821.github.io, commit `45171af`) |
| CATH | Cathedral official site — https://www.cathedrale-strasbourg.fr/horloge-astronomique [Sn] |
| WCC | Wikipedia "Computus clock" — https://en.wikipedia.org/wiki/Computus_clock [Sn] |
| WSC | Wikipedia FR "Modèle de comput de Schwilgué" — https://fr.wikipedia.org/wiki/Mod%C3%A8le_de_comput_de_Schwilgu%C3%A9 [Sn] |
| KLH | Wikipedia "Klinghammer's computus" — https://en.wikipedia.org/wiki/Klinghammer's_computus [Sn] |
| EXO | Page on the 1821 computus model — https://exopuce.fr/comput/ [Sn] |
| BDM | Travel description — http://www.bouts-du-monde.com/1eu/htm/france/grand-est/horloge-astro.htm [Sn] |
| VDK | VdK Bayern trip programme (German) — https://bayern.vdk.de/uploads/user_uploads/events/5/2/698c35f53cd29-1770796533/Programm%204%20Tage%20Schwarzwald.pdf [Sn] |
| BFA | *Das Buch für Alle*, 1867, "Die astronomische Uhr in Straßburg" — https://epilog.de/die-astronomische-uhr-in-strassburg.buch-fuer-alle.1867 [Sn] |
| EQX | Review of G. Oestmann, *The Astronomical Clock of Strasbourg Cathedral*, J. Skyscape Archaeology 7(1), 2021, pp. 157–160 — https://journal.equinoxpub.com/JSA/article/view/19440 [Sn] |
| AHN | Astronomical Heritage entry — https://web.astronomicalheritage.net/show-entity?identity=33&idsubentity=1 [Sn] |
| PH-H | patrimoine-horloge.fr — https://www.patrimoine-horloge.fr/as-strasbourgcathedrale.html [Sn] |
| ASP | astroaspach PDF "Les trois horloges astronomiques de la Cathédrale de Strasbourg" — http://astroaspach.fr/astroaspachV2/wp-content/uploads/2015/12/les-trois-horloges-astronomiques-de-la-Cathedrale-de-Strasbourg.pdf [Sn] |
| MEEUS | J. Meeus, *Astronomical Algorithms*, 2nd ed., Willmann-Bell, 1998, ISBN 0-943396-61-1. Standard reference, used only for textbook formulae (equation of time, eq. 28.3). |

Bibliographic leads to obtain (not yet read):

- **Charles Schwilgué (son), *Description abrégée de l'horloge astronomique de la cathédrale de
  Strasbourg*.** This is the primary description.
  - First edition 1842; German edition 1844 [Sn: https://www.deutsche-biographie.de/sfz79786.html].
  - 5th edition 1852, held by the History of Science Museum, Oxford [Sn].
  - 7th edition, Dannbach 1854, 66 pp, on Google Books:
    https://books.google.com/books/about/Description_abr%C3%A9g%C3%A9e_de_l_horloge_astro.html?id=LGYEyPW9ZWQC [Sn].
  - 1844 edition: https://play.google.com/store/books/details?id=moADAAAAQAAJ [Sn].
  - **Highest-value document to read next. The 19th-century editions are public domain.**
- Th. Schweighaeuser, *Historische Notizen über die Astronomische Münsteruhr zu Strassburg nebst
  einer ausführlichen Beschreibung des mechanischen Werkes*, Strassburg, Hubert & Haberer, 1876,
  64 pp [Sn: antiquarian listing]. Its title promises a detailed description of the mechanism.
- F.-G. Edel, *Die astronomische Münsteruhr in Strassburg*, 1843 [Sn].
- Ungerer, *L'horloge astronomique de la cathédrale de Strasbourg*: BnF lists 1920 and 1926
  [Sn: https://data.bnf.fr/10380008/alfred_ungerer/de.pdf]. Oxford holds a 1949 printing and a 7th
  edition of 1954, revised by Ch. Ungerer and L. Leclerc
  [Sn: https://www.mhs.ox.ac.uk/collections/library/catalogue-simple/titles/?id=1937257].
  **[?]** The "1922" date in this file is so far supported only by a Scribd upload.
- Bach, Rieb & Wilhelm (1992), on Google Books (probably snippet view only):
  https://books.google.com/books/about/Les_trois_horloges_astronomiques_de_la_C.html?id=uu4fAQAAIAAJ [Sn].
- J. Flores, *Le comput ecclésiastique de Frédéric Klinghammer*, AFAHA, Besançon, 2007, 160 pp
  plus a CD, with contributions by D. Kleinknecht and M. Augereau (gear ratios). Reviewed by
  D. Roegel, *NAWCC Bulletin* 50/4, no. 375, Aug 2008 [Sn: KLH].
- Lefort's article (LEF) appeared in *L'Ouvert* n°70 (1993), pp. 27–47
  [Sn: https://wp.publimath.fr/auteur/lefort-jean].
- 1842 lithograph by Grieshaber from the Schwilgué workshop, 52 × 34.5 cm, Nancy municipal
  archives (Bach collection): https://recherche-archives.nancy.fr/printDoc/FRAC054395_2-3-102-103Fi_de-310 [Sn].
  - Michel Grieshaber reportedly made the detailed drawings for Schwilgué's clock
    [Sn: Roegel 2025, https://roegeld.github.io/stimmer/roegel2025stimmer-astronomy.pdf]. Archive lead.
- Period frontal prints: https://gallica.bnf.fr/ark:/12148/btv1b10202446r ("construite par J.B.
  Schwilgué. 1838 à 1842"), https://www.numistral.fr/ark:/12148/btv1b10202448n.item (1845) [Sn].
- Notes from a 2008 visit guided by J.-P. Rieb:
  https://association-philomathique.u-strasbg.fr/utilisateur/pages/references/sorties%202008/Horloge%20astronomique.pdf [Sn].
- https://cadranssolaires.com/wp-content/uploads/2025/10/horloge-astronomique-strasbourg.pdf (2025) [Sn].

### Dimensions

- **[?] The 7.70 m width may belong to the first clock, not the current case.** English Wikipedia
  (snippet), on the first clock (1352–54): "on the wall opposite the current clock … Supports for
  former balconies can still be seen today, and suggest that the height of the clock was about
  18 m (59'), with a width of about 7.70 m (25') at the base" [Sn: WIKI].
  - The current case is the second (Dasypodius, 1547–74) clock's case, which Schwilgué reused
    [S: ELS, per the "Overall dimensions" entry above].
  - ODY gives 18 m × **8.60 m** for that second clock.
  - So 8.60 m may be the relevant width for the current case. At 1:8 that is 1075 mm, not 962.5 mm [D].
  - **Unresolved.** Read ELS in full and check against Bach/Rieb.
  - Consequence: the 0.96 m envelope width in `CLAUDE.md` is at risk.
- LEF (snippet), on the early clock: "D'une hauteur totale de 11,70 m, l'horloge était installée
  dans une grande cage en bois scellée au mur. La partie inférieure présentait une façade carrée
  d'environ 4 m. de côté" [Sn: LEF]. This conflicts with Wikipedia's 18 m for the first clock [?].
- Wikidata Q2716513 gives the height as 28 m [Sn]. Probably an error. The same record gives the
  clock's Palissy ID **PM67000355**; that Monuments Historiques record may hold official
  dimensions (not yet opened).
- Second clock's globe:
  - 86 cm [Sn: WIKI];
  - "860 mm in diameter and set for the meridian of Strasbourg" [Sn: EQX];
  - enlarged to 83 cm [Sn: Roegel 2025].
  - **The current (Schwilgué) globe's diameter is still unknown.**
- Precession: "one of its gears completes a turn in 25,806 years" [Sn: CATH, tool paraphrase].
  CLEA says about 26,000 years.
- Celestial globe: "more than 5000 stars, extending down to faint sixth magnitude ones" [Sn: AHN].
- Figures: "18-inch high figures of Christ and Apostles process; a life-size rooster crows three
  times" [Sn: WIKI]. So Christ is also about 18 in, which is about 57 mm at 1:8 [D].
- **Old calendar ring (probably the second clock).**
  - About 2.92 m outer diameter, 30 cm wide, 366 sectors; the leap-year sector was moved by hand
    every four years [Sn: PH-H].
  - A "secular disc" about 2.32 m across, with 100 annual sectors [Sn: ASP].
  - The current ring's diameter is unknown. If it is as large as 2.92 m, its 1:8 size is 365 mm,
    which exceeds the H2D bed [D].
- 1821 computus model: "La cage du comput fait 15 cm de large sur 20 cm de haut pour une épaisseur
  de 6 cm. Il comporte environ 300 pièces dont la plupart sont des rouages dentés et des cames aux
  découpes complexes" (the frame is 15 × 20 × 6 cm, with about 300 parts, mostly toothed wheels
  and complex cams) [Sn: EXO].
- **Still not found:**
  - case depth and how far the globe projects;
  - diameters of the planetary dial, the Moon-phase globe, the mean-time dial and the computus and
    equation displays;
  - size of the weekday carousel;
  - heights of Death, the four ages, the angels and the weekday deities;
  - rooster size in centimetres.

### Automata

- **Hourglass: hourly (provisionally resolved).**
  - "L'un, avec un sceptre et une clochette, sonne le premier coup des quarts de l'heure ;
    l'autre, son vis-à-vis, retourne le sablier au dernier coup du quatrième quart" (one angel,
    with a sceptre and a hand bell, strikes the first stroke of each quarter; the other turns the
    hourglass at the last stroke of the fourth quarter) [Sn: BDM].
  - Agrees: "Jede Viertelstunde wird von einem Engel angeläutet, zur vollen Stunde dreht der
    Engel rechts neben ihm ein Stundenglas um" [Sn: VDK]; also [Sn: BFA].
  - Only tourist pages say "every quarter".
  - Confirm in Schwilgué's *Description abrégée*.
- **Four ages:** "un enfant au 1er quart d'heure, un jeune homme à la demi, un adulte au 3e quart
  d'heure et un vieillard à l'heure juste" (child at the first quarter, youth at the half, adult at
  the third quarter, old man on the hour) [Sn: TS]. This agrees with ENS.
  - Strokes per age of 1, 2, 3 and 4 are documented only for the 16th-century clock [Sn: Cambridge
    print PR-M-00005-00049-00014].
  - **TBD for the current clock:** strokes per age and which bells are used.
- **Death strikes the hours with a bone** [Sn: low-grade blog, https://ljgolden.substack.com/p/strasbourgs-astronomical-clock].
  Confirm.
- **Noon show.**
  - "le chant du coq rappelle, par trois fois le reniement de l'apôtre saint Pierre" (the cock
    crows three times, recalling St Peter's denial); the Apostles pass before Christ, who blesses
    them [Sn: CATH].
  - **[?]** The rooster crows at the 4th, 8th and 12th Apostle [S: LOC; Sn: TS], but one blog says
    "au passage de St Pierre" [Sn].
  - The rooster's pneumatic mechanism is not found. The only rooster mechanism described is the
    *medieval* rooster's, now in the Musée des Arts décoratifs. A hollow wooden body; one rod
    lifts the head, opens the beak, pushes out the tongue and lowers the tail; a second rod spreads
    the wings [Sn: https://www.fg-art.org/users_uploads/oeuvre_oeuvre_documents/60a630522eebc.pdf].
  - Show duration: no authoritative figure. The Commons video
    `File:Animation_of_the_astronomical_clock_of_Strasbourg.ogv` could be timed.
- **Weekday carousel [?, unconfirmed]:** "le carrousel tourne de façon continue et laisse
  apparaître devant, à midi, le char de la planète du jour courant" (the carousel turns
  continuously, bringing the current day's chariot to the front at noon) [Sn: source not
  identified].
- **Local mean time vs legal time.**
  - "All astronomical indications and chimes are set to local time"; in 1842 the dial showed only
    Strasbourg mean time [Sn: CATH, tool paraphrase].
  - **[?] Summer-time behaviour unresolved.** French Wikipedia says the noon show is "12 h 30 en
    heure d'hiver", but CATH says "tous les jours, à 12 h 30 précises".

### Computus

- **[S: RGL, read]** "l'horloge astronomique de la cathédrale de Strasbourg comporte aussi un
  comput ecclésiastique construit par Jean-Baptiste Schwilgué entre 1838 et 1842. Ce mécanisme
  ingénieux permet de déterminer les éléments du comput ecclésiastique (nombre d'or, cycle solaire,
  indiction, lettre dominicale et épacte) ainsi que la date de Pâques d'année en année. Ce mécanisme
  est en fait une version agrandie d'un prototype que Schwilgué avait construit en 1821". In
  English: the clock's computus (1838–42) determines the golden number, solar cycle, indiction,
  dominical letter, epact and the Easter date year by year, and is an enlarged version of
  Schwilgué's 1821 prototype.
- **[S: RGL] The 1821 prototype and its study.**
  - It was lost about 1945 and given to the cathedral's Fabrique at the end of 2021.
  - It was dismantled, measured, drawn, photographed and XRF-surveyed between December 2022 and
    April 2023 (Roegel, with J.-P. Rieb and L. Faullimmel).
  - Roegel's full documentation is **unfinished and unpublished**.
  - The page shows a 3D-model excerpt of one part, a large rack ("grand râteau"; repo files
    `xxx.gltf` and `img/comput1821-grand-rateau.jpg`).
- **When it runs: 31 December.**
  - The central calendar is perpetual, "automatically incorporating the leap day and all moveable
    feasts, including the complex calculation of Easter's date, which is performed on New Year's
    Eve by the ecclesiastical computus on the left" [Sn: CATH, tool translation].
  - "chaque année au 31 décembre, ... les dates de Pâques et des autres fêtes qui lui sont liées
    (Ascension, Pentecôte...) se placent sur le calendrier" (each 31 December, Easter and its
    dependent feasts take their places on the calendar) [Sn: AFP-type press story, attribution
    unclear].
- **What it shows.** Five ecclesiastical functions plus a four-digit year indicator [Sn: WCC]. The
  indiction is the Roman indiction [Sn: CATH].
- **The 1821 model** is advanced one year per turn of a hand crank at the back. Its seven dials
  are: Easter date (22 March–25 April), year, solar cycle 1–28, golden number 1–19, indiction 1–15,
  dominical letter and epact [Sn: EXO].
- The 1821 model lacks the parts that transfer the result to the clock's calendar. On the clock
  the Easter date is transferred to the central calendar ring [Sn: WSC]. This gives a natural
  split: core computus plus transfer train.
- **Klinghammer replica (1970s):** "nearly a reduced model of the computus found on the Strasbourg
  cathedral astronomical clock", restored by J. Flores in 2006–07 [Sn: KLH].
- **Not found:**
  - how the Gregorian solar and lunar equations (metemptosis, proemptosis) and the century
    leap-year rule are made mechanically;
  - the Easter-finding logic;
  - gear counts;
  - the drive from the computus to the calendar ring;
  - how the dominical-letter dial is set.

### Main dial

- **Calendar ring [?].** "Le calendrier est un anneau extérieur doré qui fait un tour par an.
  Apollon pointe avec sa lance le jour en cours … gradué en 366 secteurs" (a gilded outer ring
  turning once a year; Apollo points to the current day with his spear; 366 sectors) [Sn,
  attribution unclear].
  - Some sources have Diana pointing instead [?].
  - Unknown: whether the ring moves continuously or jumps at midnight.
- **Sunrise and sunset.** A photo record's metadata reads "Apparent Time; Sunrise; Sunset" and
  shows a pointer labelled "COUCHER DU SOLEIL" (sunset) [Sn: https://sourcelibrary.org/book/cathedrale-de-strasbourg-img-1241].
  This suggests labelled hands or sectors.
  - **Mechanism unknown.** Also unknown: which latitude it is set for.
- **Equations.** They "parfois accélèrent, ou parfois ralentissent la marche des aiguilles du
  soleil et de la lune" (sometimes speed up, sometimes slow down the Sun and Moon hands); they are
  in the right-hand case [Sn: ASP].
- **[?] An eclipse the clock reportedly showed.** "a, par exemple, indiqué clairement une éclipse
  de lune le 28 mars 2006" (the clock clearly showed a lunar eclipse on 28 March 2006) [Sn].
  Check this against the NASA/Espenak eclipse catalogue before using it as a validation case:
  there was a total *solar* eclipse on 29 Mar 2006 and a penumbral *lunar* eclipse on
  14 Mar 2006, so the snippet may be garbled.

### Location

- **Strasbourg Cathedral: about 48°34′55″ N, 7°45′02″ E (48.582° N, 7.7506° E).** These are the
  standard published coordinates (Wikipedia infobox), recalled rather than re-opened in this
  session, so verify them.
  - They give LMT − UT = +31.00 min [D], which agrees with ELS's "about 31 min" [S: ELS, snippet].
  - Used in `tools/phase0/derivations.py`.

### Open items — status after Phase 0

Status of each item in "Open items / unknowns" above, in the same order:

| Item | Status |
|---|---|
| Globe, planetary dial, Moon-globe and other dial diameters | Open. The 83/86 cm figure is the second clock's globe. Needs photo scaling (hosts blocked) or a primary source. |
| Computus and equations vitrine size and layout | Open. |
| Case depth; how far the globe projects | Open. |
| Figure heights; rooster size | Partly answered: Christ is also 18 in [Sn]; the rooster is "life-size" [Sn], no number found. |
| Sunrise/sunset display mechanism | Open. Labelled hands are likely [Sn]. |
| Day-of-year ring, Easter insertion, leap day | Partly answered: 366 sectors, one turn a year [Sn]; set by the computus on 31 Dec [Sn]. Mechanism open. |
| Computus mechanism in detail | Open. Best lead is RGL (unpublished), then the Klinghammer book and Bach/Rieb. |
| Rooster mechanism | Open. |
| Hourglass hourly or quarter-hourly | **Provisionally hourly** [Sn ×4]. |
| Case width 7.70 vs 8.60 m | **Worse than thought**: 7.70 m may be the first clock's width [Sn: WIKI]. Open. |
| ELS PDF and the Ungerer / Bach-Rieb books | ELS host blocked. Schwilgué's *Description abrégée* (public domain, Google Books) is now the top target. |

---

## Phase 0 research pass 2 (31 Oct 2026, after Paul widened network access)

### New primary sources

| Key | Source |
|---|---|
| **DA** | Charles Schwilgué (the builder's son), *Description abrégée de l'horloge astronomique de la cathédrale de Strasbourg*, 2nd edition, Strasbourg, Ph.-Alb. Dannbach, 1844, 70 pp. Public domain (archive.org: NOT_IN_COPYRIGHT; Google scan). https://archive.org/details/descriptionabrg00schwgoog. **Read in full** from the OCR text. Numbers that matter were checked against the page images (PDF page = printed page + 11). Page numbers below are the printed ones. |
| SCH | Charles Schmidt, *Bericht über das astronomische Uhrwerk des Straßburger Münsters, verfaßt bei Gelegenheit das Hrn. Schwilgué, Vater, durch seine Mitbürger gegebenen Feste*, Strasbourg, Dannbach, 1842, 27 pp. https://archive.org/details/bub_gb_cSlBAAAAcAAJ. The Fraktur OCR is unreadable; it needs proper OCR or a human reader. **Not yet used.** |

DA announces "une description complète, qui sera enrichie de dix planches" (a complete
description with ten plates) [S: DA p. 5]. **Lead:** find it.

### Facts from DA (verbatim; page)

**Case and history**

- First clock (1352–54): in the south transept "en face de l'horloge actuelle; on voit encore
  aujourd'hui, dans le mur, les consoles en pierre, qui ont servi à la soutenir" [p. 7–8]. This
  agrees with WIKI on where the first clock stood. DA gives no dimensions.
- Second clock: in 1547 the stonecutters were finishing "le cabinet qui sert encore à l'horloge
  actuelle" [p. 9]. So the current case is the 16th-century stone cabinet. DA gives no case
  dimensions.
- New clock begun 24 June 1838; first ran Sunday 2 October 1842; inaugurated 31 December 1842
  [p. 22]. "Entièrement de l'invention de mon père", reusing only some statuettes [p. 23].
- **"Il n'entre dans la construction de l'horloge aucune pièce de bois"** (no wooden parts) [p. 67].

**Celestial sphere** [p. 24–26]

- Sidereal time on a dial; copper sphere on four metal columns; "disposée pour la latitude de
  Strasbourg".
- More than 5000 stars of the first six magnitudes in **110** constellations (page image; the OCR
  reads "1 1").
- Turns east to west in a sidereal day, about 3 min 56 s shorter than the mean solar day.
- Equator, ecliptic and colures turn with it. Meridian and horizon stay fixed.
- **Precession: "environ 25,804 années"** (page image; the OCR reads 26,804). Footnote: periods are
  given only to their main units.
- The second clock's globe: papier-mâché, about 50 kg, 1020 stars, 48 constellations [p. 14].

**Calendar** [p. 27–29]

- "Une bande métallique, en forme d'anneau, n'ayant que **25 centimètres** de largeur sur une
  circonférence de **passé 9 mètres**" (page image; the OCR reads 26).
- "Avance chaque jour d'une division, le passage d'un jour à un autre s'effectuant
  instantanément à minuit".
- Apollo, on the right, points "avec une flèche"; Diana is only a counterpart.
- Turns in 365 or 366 days and suppresses 3 days in 400 years by itself.
- "Commencement de l'année commune" between 31 Dec and 1 Jan; in leap years "commune" disappears
  and a day is inserted between 28 Feb and 1 Mar.
- Movable feasts placed at midnight on 31 Dec. Advent and St Arbogast have their own mechanisms.

**Apparent-time dial** [p. 30–36]

- Azure dial, silver ring with 1–12 twice.
- Shows: sunrise and sunset by a **"horizon mobile"**; true time; the Moon's true right ascension
  and meridian passage; the Moon's phases (Moon globe silver and black); eclipses.
- Sunrise and sunset in apparent time, for the Strasbourg meridian, with refraction.
- Northern hemisphere at the centre.
- Lunar eclipses shown by a disc representing a section of the Earth's shadow cone.
- The Moon's latitude is shown by its radial position relative to the Sun.

**Computus** [p. 36–43]

- Shows: millésime (four digit circles), solar cycle, golden number, Roman indiction, dominical
  letter, epacts, Easter.
- Contains all the Gregorian modifications and the lunar equations.
- Released by the clock at midnight on 31 Dec. It first determines the cycles, which then set "le
  mécanisme principal" to fix Easter. Easter is transmitted to the calendar as the "véhicule" of
  the dependent feasts.

**Equations** [p. 43–46]

- Sun: mean time to true time, "par l'anomalie pour obtenir la longitude vraie, laquelle à son tour
  est convertie en ascension droite vraie".
- Moon: centre, evection, variation, annual equation, reduction, plus the equation of the nodes
  (for latitude).
- Visible behind glass. The Moon's longitude-to-right-ascension converter is inside the clock.

**Weekday** [p. 46–48]

- Chariots "roulent sur un chemin de fer circulaire, en suivant un mouvement continu".

**Mean time** [p. 49–50]

- Small dial in the "galerie aux lions" (the two lions are from the old clock and never moved).
- Driven directly by the single central motor, which is wound every 8 days.

**Genies** [p. 50–51]

- The left genie (sceptre and bell) strikes the first stroke of each quarter and signals the ages.
- The right genie turns the red-sand glass **each hour**, alternately half a turn right and half a
  turn left, at the last stroke of the four quarters, just before Death strikes.

**Planetary** [p. 51–53]

- Copernican, on a large azure dial. The Sun disc has no visible support; twelve rays lead to the
  zodiac.
- Seven small gilded spheres.
- Periods: ~88 d, ~225 d, Earth 365 d 5 h 48 min 48 s, ~687 d, ~4330 d, 10747 d.
- The Moon goes round the Earth in a lunar month.

**Moon globe** [p. 53–55]

- An inclined globe turning on its axis.

**Automata** [p. 56–60]

- Two halls with ogival arcades: ages and Death below, Christ above.
- The ages strike only the second stroke of each quarter: child (thyrsus), youth (hunter, arrow),
  man (warrior, sword), old man (crutch).
- Each steps two paces out of its lodge to a bell.
- **The ages work only by day.**
- Death with a scythe on a central pedestal drops a bone on the bell to its right, day and night.
- At Death's last stroke of noon the twelve Apostles pass (named, in order). Each turns, bows and
  receives the blessing. After the last, Christ blesses with the sign of the cross.
- Rooster: during the Apostles' march it flaps its wings, moves its head and tail and swells its
  neck. It is "d'après nature", the same size as the earlier clocks' rooster, and crows three times
  daily at noon.

**Motors** [p. 64–66]

- One central motor, with a seconds regulator, compensated pendulum and jewelled escapement, wound
  weekly. It drives:
  - the mean-time dial;
  - the exterior dial;
  - the planetary dial;
  - the Moon phases;
  - the weekday figures;
  - the apparent-time dial;
  - the equations;
  - the sphere.
- It also suspends the ages at night.
- "Les autres moteurs, au nombre de cinq" drive the automata and striking, chained in order: ages
  → quarters → ages → hours; at noon, Apostles and rooster from the hour train. **[?]** Five
  motors are counted but only four trains are named.

**Other** [p. 62–64]

- Exterior Gothic dial over the portal, circumference about 16 m, showing mean time and the
  weekday.
- A meridian line inside the church, lit through a gnomon over the door, for checking the clock.

### Resolved by DA (supersedes the [Sn] entries above)

| Item | Resolution |
|---|---|
| Hourglass hourly or quarter-hourly | **Hourly**, alternating direction [S: DA p. 51] |
| Apollo or Diana points to the day | **Apollo** [S: DA p. 27] |
| Calendar ring continuous or jumping | **Jumps at midnight** [S: DA p. 27] |
| Calendar ring size | **25 cm wide, circumference over 9 m** [S: DA p. 27] |
| Sunrise/sunset display | **Mobile horizon** [S: DA p. 31]. Its drive is still TBD. |
| Weekday carousel motion | **Continuous**, on a circular rail [S: DA p. 47] |
| Precession period | **25,804 years** [S: DA p. 26] (CATH's 25,806 [Sn] is close) |
| Rooster size | **Life-size** [S: DA p. 59–60]. Still no number. |
| Night behaviour | **The ages are silent at night; Death strikes day and night** [S: DA p. 58, 65] |

### Still open after pass 2

- Case width (7.70 vs 8.60 m) and depth, and every dial diameter except the calendar ring. DA gives
  none.
- The drive of the mobile horizon; the mechanisms for leap-day insertion and Easter transfer; the
  computus internals.
- LEF, CLEA and ELS: not downloadable automatically (403 or no DNS). **Paul to download them.**
- Photos: Wikimedia rate-limited this session.
