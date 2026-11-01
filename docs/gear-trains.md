# Gear trains

Phase 1 deliverable. This file gives the chosen gear train for every indication, its error, the
accuracy target that justifies it, and the tooth-strength and motor-torque check.

- The trains themselves live in [`spec/clock.yaml`](../spec/clock.yaml), the single source of
  truth (architecture P5).
- The tables in §8 are **generated** from that file by `tools/ratios`. A test fails if they drift
  apart.
- Tags as in `docs/reference-notes.md`.

**Status: in review** (Phase 1 gate). Every decision in §9 is now taken (Paul, PR #3, 1 Nov
2026):

- accuracy targets accepted (§3);
- planets designed on NASA/JPL data, all five (§4F; no tooth counts changed);
- torque and tooth strength verified, strength rules accepted (§5);
- M3 cam convention B planned, and the M3 trains re-run for it, following Schwilgué's half turn per period (§6);
- M5 input at 1 rev per mean day accepted (§7);
- 169-tooth wheels kept at module 1.0 (§9).

## 1. How to read the numbers

- **Ratio** = output turns per input turn, as an exact fraction. "Exact" means it equals the
  target exactly.
- **Period error** is the achieved output period minus the target period.
- **Drift** is the error the displayed angle accumulates per Julian century, in degrees. It is
  the figure that matters for a display: 1° is 2.2 mm at the tip of the 125 mm Sun hand [D: 1 m
  hand at 1:8, ELS].
- **Target value ±** is the drift equivalent to the uncertainty of the target value itself. A train
  whose drift is inside that band is as accurate as our knowledge of the target.
  - For a value quoted to a fixed number of digits, it is half a unit of the last digit.
  - For the planets (§4F), it is the difference between JPL's two published fits. Examples:
    ±0.0007°/century for Mercury, ±0.16°/century for Jupiter (Jupiter and Saturn perturb each
    other, so their mean rates depend on the time span fitted).
- Every ratio is computed with Python `Fraction`s, so nothing is lost to floating-point rounding.
  Errors are against modern values (§8 Targets), not Schwilgué's 19th-century ones.

## 2. Constraints used (D4)

| Constraint | Value | Why |
|---|---|---|
| Tooth profile | involute 20° | D4 |
| Module | 1.0 by default (sizes below); 0.8 scales every diameter by 0.8 | D4; the real minimum comes from the local tolerance test |
| Smallest pinion | 12 teeth (profile-shifted below 17) | D4 |
| Largest wheel | 160 teeth (162 mm tip at m 1.0); 200 where a train says so | Keeps wheels well inside the 320 mm bed and the module footprints |
| Largest single mesh | 10:1 | Printable pinions, smooth running |
| Stages | as few as meet the accuracy target (1, then 2, then 3) | Brief: "prefer fewer stages" |
| Face width | 4 mm; 8 mm on `M5.earth` and `M5.moon_arm` | D4; §5 |
| Tooth strength | running safety factor ≥ 4; a slip-clutch window on every output | §5 |

Worms (driver = 1) are used only for the v2 precession drive.

## 3. Accuracy targets (accepted)

**Accepted by Paul** (PR #3 review, 1 Nov 2026).

| Class | Target | Applies to | Justification |
|---|---|---|---|
| Clock and calendar functions | **exact** | hour hands, 24 h cam, weekday | Integer ratios exist, so there is no reason to accept any error |
| Displayed astronomical angles | **≤ 1° per century** | year arbor, main-dial Moon, planets, Moon arm, Moon globe | 1° is the smallest readable unit at 1:8 (2.2 mm at the Sun-hand tip; 2.4 mm at the 137.5 mm planetary radius). Under 1° per century is invisible in a lifetime, and the setting mechanism (architecture §7) can always re-zero. |
| Sidereal globe | **≤ 0.25° per century** | M6 | Its hour circle *reads* sidereal time: 0.25° is 1 minute. |
| Correction-cam arguments (v1.5) | **≤ 2° per century** in the argument | equation cams, eclipse node cam | A phase error φ in a cam of amplitude A gives about A·φ (rad). For the largest lunar term (6.3°) and φ = 2°, that is 0.2° after a full century. With convention B (§6) a cam turn is two periods, so the M3 trains are held to ≤ 1° per century of cam turn. |
| Precession (v2) | ≤ 0.002° per century (about 0.05 % in rate) | M6 | It moves about 1.4° per century in total [D]. Any rate within 1 % is invisible. |

## 4. What the search found

**A. One year train for everything.**
- 15/99 × 13/97 × 12/89 = 260/94963. That is one turn per 365 d 5 h 48 min 45.2 s, against
  365.24219 d: +10.2 s per year, −0.012°/century.
- The same three meshes serve M2 (main-dial year arbor), M3 (solar reduction), M5 (Earth arm) and
  M6 (precession feed). One design, printed four times; a test enforces that the tooth counts stay
  identical. The M5 copy has 8 mm faces because it carries the whole planetarium (§5).

**B. No differentials needed for the mean motions.**
- Plain compound trains reach every target:
  - sidereal globe: 3 stages, +0.15°/century;
  - main-dial Moon: 2 stages, −0.94°/century;
  - Moon globe: 2 stages, +0.94°/century.
- Schwilgué used an exact epicyclic train for the sphere [S: LEF] and differentials for the Moon
  [S: CLEA]. They are not needed at this accuracy, which saves parts in the densest modules.
- The tool can still design differentials (`search_differential`). It reproduces Schwilgué's exact
  sidereal ratio 164809/164359.

**C. Planets: Schwilgué's arrangement, NASA/JPL rates.**
- Each planet is driven from the central Earth tube through a **reverted (coaxial) pair**, so every
  arm's tube is concentric with the Sun.
- Jupiter and Saturn cannot be reached from a daily arbor in 3 meshes of ≤ 10:1; via the Earth
  tube they need 2.
- A *common* tooth sum for all five planets (every intermediate arbor on one circle) gives at best
  4.2°/century [D: exhaustive search over sums 60–320]. So each planet gets its own
  intermediate-arbor radius: 101, 66.5, 41.5, 35.5 and 46 mm.
- Every planet is within 1°/century of the JPL rates (§4F), **including the Earth train's error**.
  Mercury −0.10, Venus +0.54, Mars −0.67, Jupiter −0.52, Saturn +0.51°/century (§8).

**D. Planetarium Moon.**
- The Moon on the Earth arm is an epicyclic by nature: a fixed 78-tooth sun wheel, a compound
  planet 23/62 on the Earth arm, and a 17-tooth pinion on the Moon arm.
- Its rate relative to the Earth arm is the synodic rate, +0.58°/century.

**E. Schwilgué's own trains, checked against modern values** [D: `tools/ratios`; his periods from
the LEF gear table, his year 365 d 5 h 48 min 48 s]:

| Train | His period | Modern | Drift vs modern |
|---|---|---|---|
| Year | 365.242222 d | 365.24219 d | −0.003°/century |
| Mercury | 87.968470 d | 87.968434 d (JPL) | −0.061°/century |
| Venus | 224.695436 d | 224.695437 d (JPL) | 0.000°/century |
| Mars | 686.929674 d | 686.929718 d (JPL) | +0.001°/century |
| Jupiter | 4330.5933 d | 4330.5989 d ± 0.22 (JPL) | +0.004°/century, inside JPL's own band |
| Saturn | 10746.9375 d | 10746.9332 d ± 3.3 (JPL) | 0.000°/century, inside JPL's own band |
| Synodic month | 29.530590 d | 29.5305889 d | −0.02°/century |

- His planet periods agree with the modern mean motions to a few hundredths of a degree per
  century or better.
- **Correction to the first draft of this PR.** It compared his trains with NASA's planetary fact
  sheets and reported his Mars at +1.18°/century, "his target value was off". That was wrong.
  - The fact sheet gives Mars a sidereal period of 686.980 d and a "tropical orbit period" of
    686.972 d, flagged "\* Mean value … can vary from this by up to 0.004 days depending on the
    initial point of the orbit" [S: https://nssdc.gsfc.nasa.gov/planetary/factsheet/marsfact.html,
    retrieved 2026-11-01].
  - A mean tropical period must be shorter than the sidereal one by about P²/P_precession:
    686.980² / (25,771.6 × 365.24219) = 0.050 d, so 686.930 d [D]. The fact sheet's Mercury and
    Jupiter rows pass this check; its Mars row does not.
  - So the fact-sheet Mars value is not a mean tropical period, and Schwilgué's 686.930 d is right.
  - The planets now use JPL's mean motions (§4F), which avoids the fact sheets altogether.
- **Under his own limits** (17–250 teeth, 2 stages), the exhaustive search finds that his Venus,
  Mars, Jupiter and Saturn ratios are **the best possible**. It returns exactly his fractions.
- His Mercury could have matched *his own target figure* (7,600,475 s) about 12× more closely with
  245/183 × 245/79. Against JPL the gain mostly disappears: −0.044 instead of −0.061°/century,
  because his target figure is itself 0.045°/century from JPL.

**F. Planet targets: NASA/JPL mean elements** (review point 1 and open question).
- Paul asked to design around NASA's Mercury data, even where that departs from the original. The
  planets now use NASA/JPL's mean-longitude rates, all five for consistency:
  - source: E. M. Standish, *Keplerian Elements for Approximate Positions of the Major Planets*,
    JPL Solar System Dynamics, Table 2a (3000 BC – 3000 AD)
    [S: https://ssd.jpl.nasa.gov/planets/approx_pos.html, retrieved 2026-11-01];
  - the rates are in degrees per Julian century against the fixed J2000 equinox, so they are
    sidereal;
  - the dial shows tropical motion (the Sun hand and the zodiac follow the equinox), so each rate
    gets the general precession added, 5028.796195″/century (IAU 2006) [S: §8 Targets];
  - **P_tropical = 360 × 36525 / (L̇ + 5028.796195/3600)** days [D].
- Cross-check: the same formula on JPL's Earth–Moon rate gives 365.2421884 d against the sourced
  365.24219 d [D].
- Uncertainty: the difference between JPL's Table 1 (1800–2050 fit) and Table 2a [E]. It is
  negligible for the inner planets. For Jupiter and Saturn it is ±0.16 and ±0.38°/century, from
  their mutual perturbation.
- **What the "12×" was.** It was the gear search beating Schwilgué's Mercury *ratio* against his
  own target figure (E above). It was not a different NASA model.
- **Mercury result.** The Mercury target is now 87.968434 d [D]. The chosen train 135/67 × 136/66
  from the Earth tube gives **−0.096°/century**, which is 0.23 mm at the 137.5 mm planetary radius
  after 100 years [D].
  - It is the best reverted two-mesh pair with 12–200 teeth and ≤ 10:1 per mesh [D: exhaustive
    search].
  - Matching Schwilgué's −0.061°/century would need a third mesh or larger wheels. That is not
    recommended: both errors are far below the 1° target.
- The planet trains are no longer Schwilgué's tooth counts (they could not be: his use 240- and
  9-tooth wheels). Only his arrangement is kept: reverted pairs from the Earth tube.
- **Effect on the trains already computed** (Paul's follow-up question): **no tooth count
  changed.**
  - All five planet trains already met ≤ 1°/century against the JPL targets.
  - Re-running the chooser against the JPL targets (fewest stages, then smallest wheels) returns
    the same five pairs [D: `tools/ratios`].
  - Only the reported drifts moved, because the targets moved:

| Planet | Train (from the Earth tube) | Drift vs NASA fact sheet (first draft) | Drift vs JPL (now) |
|---|---|---|---|
| Mercury | 135/67 × 136/66 | −0.83°/century (±0.85 from the 3-decimal value) | −0.096°/century |
| Venus | 70/63 × 79/54 | +0.42°/century | +0.54°/century |
| Mars | 35/48 × 35/48 | +0.51°/century | −0.67°/century |
| Jupiter | 15/56 × 17/54 | −0.53°/century | −0.52°/century |
| Saturn | 17/75 × 12/80 | +0.51°/century | +0.51°/century |

- The Earth train, the Moon trains, the sidereal globe and every non-planet train do not depend on
  the planet targets, so they are unchanged.

## 5. Torque and tooth strength (review point 2)

Paul asked whether the motor has enough torque to drive M5 at 1 rev per day rather than 1 rev per
hour, and whether that torque stays within part strength.

**Short answer.** The motor has 150 to 480 times more torque than these modules need. Every
printed tooth runs at a safety factor of at least 6 on top of the factor 4 already in the
allowable stress. The real risk is the opposite one: in a jam, the motor is far stronger than the
teeth. Slip clutches at the outputs protect against that, and they are already in the setting
design.

**1. The motor does not slow down.**
- It still turns at 1 rev/h. A printed 24:1 reduction (architecture §3) makes the 1 rev/day input
  arbor.
- A reduction multiplies torque, so the daily arbor gets about 19 times the motor's torque
  [D: 24 × 0.9² mesh efficiency].
- The torque reaching an output depends only on the *total* reduction from motor to output, not on
  where it sits.
  - The motor turns once an hour and the Earth arm once a year in both schemes, so the reduction is
    8,766:1 either way [D: 365.24 × 24].
  - Schwilgué's hourly train and our daily arbor plus year train therefore put the same torque on
    the Earth arm, apart from small differences in mesh losses.

**2. Motor torque is ample** (generated table "Motor torque budget", §8).
- Motor 17HS19-2004S1: 0.59 N·m holding torque at 2.0 A [S: datasheet in `spec/clock.yaml`].
- At a quiet 0.5 A run current that is about 148 mN·m [E: torque roughly proportional to current].
- Need versus supply: M5 needs about 0.31 mN·m at the motor, a **483×** margin.
  - The other 24:1 modules have 150× to 420×.
  - M1, with no reduction, has 23×.
- The need is mostly friction at each module's own input [E: 5 N·mm per module]. The slow outputs
  add almost nothing once reflected back through their large ratios.

**3. Teeth in normal running** (generated table "Tooth strength", §8).
- Model: Lewis bending stress at the tooth root, σ = F / (b · m · Y). Y comes from Shigley Table
  14-2 [S: link in `tools/ratios/strength.py`].
- Allowable stress 9.75 MPa: Bambu Lab PLA Basic, 39 ± 2 MPa X-Y tensile [S: TDS, link in
  `spec/clock.yaml`], divided by 4 [E]. The factor 4 covers print variation, creep over years,
  fatigue and root stress concentration.
- Each output's running load is estimated at 10 N·mm [E]. Shared trains add their children's
  loads, reflected through the ratios.
- **Result:** every train has a running safety factor of **25 to 113**, except the planetarium's
  Earth train at **6**, which carries the whole planetarium.
- Lewis is a simple model. The local tolerance and strength test (Phase 2 test rig) replaces the
  allowable-stress estimate, and `check` re-runs with the measured value.

**4. Jams: the motor is stronger than the teeth.**
- If an output is held (a finger on a hand, something fallen into the case), the motor keeps
  stepping. Its torque times the reduction is then far more than the teeth can carry.
  - Example [D]: 0.148 N·m × 24 × 365.24 × 0.9⁵ ≈ **760 N·m** at a held Earth arm, about 900× the
    0.85 N·m that the Earth train's weakest tooth carries.
  - The same is true at 1 rev/h input, or at the lowest usable motor current. A stepper behind a
    large reduction cannot be made weak enough to stall before a printed tooth breaks.
- **So protection must be mechanical, at the outputs.** The setting design already gives every
  hand and arm a friction-clutched hub (architecture §7).
  - Each clutch must hold 3× its running load and slip below half its train's capacity.
  - The table gives this window for every output, and every output has one. For example the Moon
    arm 9–41 N·mm and Mercury 30–136 N·mm.
  - Phase 2 designs the clutches to these windows.
- **Shared trains.** On M5 the planet trains take off from the Earth tube.
  - A held planet arm loads the Earth train through that arm's clutch.
  - The Earth train survives every clutch on it slipping at once: 3 × 139 = 417 N·mm against its
    850 N·mm capacity [D].
  - `check` enforces this.
- **Jams inside a train** (debris between two teeth) are not stopped by a clutch at either end.
  This is true of any clockwork.
  - Mitigation: the glazed, dust-tight case; no loose parts above the trains; cheap printed gears
    in removable modules.
  - The index and witness sensors (architecture §6) reveal a stopped or slipped train at their
    next pass, so the controller can stop that motor and report. They limit the damage; they
    cannot prevent it.

**5. Two changes made by this check** (decision 5 in §9).
- **`M5.earth` gets 8 mm faces** instead of 4 mm. It carries 139 N·mm against 10 N·mm elsewhere
  (Mercury alone reflects 51 N·mm because it turns 4.15× faster than the Earth tube). At 4 mm its
  safety factor would be 3, below the minimum of 4. The tooth counts are unchanged.
- **`M5.moon_arm` gets 8 mm faces.** It is a step-up: the Moon arm turns 13.4× faster than the
  Earth arm, and its driven gears are small pinions (23 and 17 teeth). At 4 mm it has the lowest
  capacity in the clock (41 N·mm). At 8 mm its clutch window is 9–41 N·mm instead of 9–20.
- Its running load is set at **3 N·mm** instead of 10 [E]. Method: the same 1.5 N·mm of hub
  friction as the default, × 2 margin. The default's extra margin is meant for trains driven from
  an output, and the Moon arm drives none.
  - Sensitivity: at 10 N·mm the Earth train would need about 10 mm faces.
  - Phase 2 recomputes every load from CAD masses, and `check` fails if a train drops below the
    limits.
- The 24:1 motor reductions are designed in Phase 2 with the same check (6 mm faces, D4).

## 6. M3 cam convention: what is needed and the trade-offs (review point 4)

**What M3 does.**
- M3 (v1.5) adds Schwilgué's solar and lunar equations. The Sun and Moon hands do not move at a
  steady rate; their true positions swing either side of the mean by periodic corrections.
- Each correction is a cam whose profile is the correction curve. The cams are summed, and the sum
  is added to the mean motion through a differential [S: LEF, CLEA].
- The Moon uses five terms: anomaly, evection, variation, annual equation and nodes. The Sun uses
  three [S: LEF].

**How Schwilgué built it** [S: LEF; reference-notes "Solar and lunar equations"].
- Each cam is an upright cylinder whose top edge carries the curve.
- A horizontal crossbar lies across the cylinder and touches the edge at two opposite points.
- The next cylinder up stands on that crossbar, so the top crossbar's height is the sum of every
  correction.
- For a crossbar to stay level, the edge must be equally high at the two opposite points. So he
  traced each curve **twice** around its cylinder, and each cylinder turns once every two periods.

**The question.** Our M3 trains (§8) currently turn each cam **once per period**. Before the
Phase 2 M3 design we need to choose between three layouts. The choice changes the M3 ratios and
the cam sizes; nothing else in the clock depends on it.

| | A. One period per turn, single follower | B. Two periods per turn, crossbar (Schwilgué) | C. Flat plate cams, lever summing |
|---|---|---|---|
| How it reads | One roller follower on a guided vertical slide | A crossbar resting on two opposite points, as in the original | Followers on levers; a whiffletree or a cord over pulleys adds them |
| M3 ratios | as in §8 now | every M3 cam turns at half the rate; the tool re-runs in seconds | as A |
| Cam size | 1× | about 2× the diameter for the same slope (below) | small, flat |
| Guiding and friction | contact on one side pushes the slide sideways: guide bushings, more friction | contact forces balance on the two sides: light guides, self-levelling | lever pivots, low friction |
| Gear accuracy needed | ≤ 2°/century (accepted) | ≤ 1°/century per cam turn, since one cam turn is two periods; the same error in the argument | as A |
| Faithful to the visible vitrine (I13) | partly: cylinders yes, crossbars no | **yes** | no |
| Depth and height | a tall stack with slide guides | a tall stack, as the original | compact |

**Cam size** [S: ELS for Schwilgué's figures; D for the scaling].
- Schwilgué's scale was 6 mm of crossbar travel per degree of correction.
  - His steepest curve is the Moon's equation of centre: 75.6 mm of total travel, steepest slope
    30°12′.
  - He set himself a limit of 45° for the slopes.
- Scaled uniformly to 1:8, every slope stays the same, so B at 1:8 is exactly his geometry.
- But the travel becomes 0.75 mm per degree, and his smallest term (the Moon's reduction, 1.4 mm
  in total) shrinks to 0.18 mm, which is below print precision.
- So M3 keeps a larger cam scale behind its output gearing (architecture §13). The cylinder
  diameters then follow from that scale and the 45° slope limit.
- For the same scale and slope, B needs about twice A's diameter: the steepest slope of a curve
  with n periods per turn is about A·n/R.
- Phase 2 sets the scale together with the vitrine size, which is still TBD.

**Recommendation: B, Schwilgué's convention.**
- The equations vitrine is one of the few places where the mechanism itself is on show, and the
  crossbar stack is its signature.
- Self-levelling crossbars need lighter guides and have less friction than A's one-sided
  followers.
- The cost is cams about twice the diameter and halved ratios, both cheap at this stage.

**Decision: B** (Paul, PR #3, 1 Nov 2026): "Lets plan on that for now and revisit if it becomes
difficult to implement."

**The M3 trains re-run for B.**
- **Rule, now sourced.** Ungerer (1921) gives every equation arbor of the original as making **a
  half turn per period** [S: ELS]:
  - Sun's equation of centre, "demi-tour en 365 jours 6 heures 13 minutes 56 secondes";
  - Sun's reduction to the equator, "demi-tour en 365 jours 5 heures 48 minutes 48 secondes",
    with the sinusoid "répétée 4 fois sur le pourtour";
  - the Moon's reduction to the ecliptic, annual equation, variation, evection and equation of
    centre, each "fait un demi-tour" in its period.
  - So each cylinder turns once per **two** periods.
  - This also settles the LEF table: it lists the periods themselves, and each cylinder turns at
    half that rate.
- **Accuracy.** Because one cam turn is two periods, an angle error on the cam counts twice in the
  argument. So all M3 cam trains are held to ≤ 1°/century of cam angle, which keeps ≤ 2°/century
  in the argument (§3).
- **Changes.** All six cams now turn at half their former rate:
  - the Sun's reduction gets one exact 20/40 mesh after the shared year train (new train
    `M3.solar_reduction`);
  - the others were re-chosen with the standing rule (fewest meshes, then smallest wheels).

| Train | Term (Schwilgué's period) | Cam turns once per | Before | Now (§8) |
|---|---|---|---|---|
| `M3.solar_reduction` (new) | Sun's reduction to the equator (tropical year) | **2 tropical years** | on `M3.year`, 1 turn per year | `M3.year` × 20/40, −0.006°/century |
| `M3.anomalistic_year` | Sun's centre and Moon's annual equation (anomalistic year) | **2 anomalistic years** | 13/96 × 14/108 × 17/109 | 12/110 × 12/111 × 13/112, +0.16°/century |
| `M3.lunar_anomaly` | Moon's centre (anomalistic month) | **2 anomalistic months** | 13/82 × 19/83 | 19/137 × 14/107, +0.34°/century |
| `M3.evection` | evection (31.8 d) | **2 evection periods** | 31/122 × 12/97 | 37/82 × 12/78 × 12/53, +0.018°/century |
| `M3.variation` | variation with the parallactic inequality (synodic month) | **2 synodic months** | 25/113 × 15/98 | 37/91 × 12/38 × 12/91, −0.032°/century |
| `M3.lunar_node` | Moon's reduction to the ecliptic (draconic month) | **2 draconic months** | 23/112 × 17/95 | 23/152 × 17/140, −0.50°/century |

- **Wheel sizes.** Evection has a two-mesh solution, but it needs a 178-tooth wheel (180 mm). M3 is
  a dense stack in a vitrine of unknown size, so the default limit of 160 teeth is kept and a third
  mesh used instead. The largest M3 wheel is now 154 mm.
- **For the cam profiles (Phase 2)** [S: ELS]:
  - the variation curve includes the parallactic inequality, so its period is one synodic month,
    not half;
  - the Moon's equation of centre carries its second harmonic (13′ sin 2M′) as well as the main
    term.

## 7. Changes to earlier documents

- **M5 input: 1 rev per mean day instead of 1 rev/h.** **Accepted** (decision 2 in §9; torque in
  §5). Architecture §2 is updated.
  - The hourly input was chosen to keep Schwilgué's Earth train 9/156 × 10/188 × 10/269.
  - Its 9-tooth pinion is below our printable minimum, and the 269-tooth wheel is 271 mm at
    module 1.0.
  - From a daily arbor the shared year train (A) does the job in 3 small stages, and every
    stepper module except M1 then runs at the same rate.
- **M3 cams:** convention B, applied in §6. Architecture §6 (witness sensors) and §13 are
  updated.

## 8. Generated tables

<!-- BEGIN GENERATED: python -m tools.ratios report --write docs/gear-trains.md -->

### Targets

| Name | Value | Tag | Source |
|---|---|---|---|
| `tropical_year` | 365.24219 d | [S] | Mean tropical year 2000, Wikipedia 'Tropical year', https://en.wikipedia.org/wiki/Tropical_year (retrieved 2026-11-01) |
| `anomalistic_year` | 365.259636 d | [S] | Epoch J2011.0, Wikipedia 'Year', https://en.wikipedia.org/wiki/Year (retrieved 2026-11-01) |
| `synodic_month` | 29.5305888531 d | [S] | Mean synodic month at J2000 (Chapront-Touzé & Chapront 1988), via Wikipedia 'Lunar month', https://en.wikipedia.org/wiki/Lunar_month (retrieved 2026-11-01) |
| `anomalistic_month` | 27.554551 d | [S] | Wikipedia 'Lunar month', https://en.wikipedia.org/wiki/Lunar_month (retrieved 2026-11-01) |
| `draconic_month` | 27.21222 d | [S] | Wikipedia 'Lunar month', https://en.wikipedia.org/wiki/Lunar_month (retrieved 2026-11-01) |
| `nodal_period_years` | 18.612958 tropical years | [S] | Revolution of the lunar nodes relative to the equinox, Wikipedia 'Lunar node', https://en.wikipedia.org/wiki/Lunar_node (retrieved 2026-11-01) |
| `precession_years` | 25771.57534 years | [S] | 5028.796195″/century (Capitaine et al. 2003), via Wikipedia 'Axial precession', https://en.wikipedia.org/wiki/Axial_precession (retrieved 2026-11-01) |
| `jpl_ldot_mercury` | 149472.67486623 deg/century | [S] | Mean-longitude rate, J2000 ecliptic and equinox, 3000 BC-3000 AD (Table 2a), E. M. Standish, 'Keplerian Elements for Approximate Positions of the Major Planets', NASA/JPL SSD, https://ssd.jpl.nasa.gov/planets/approx_pos.html (retrieved 2026-11-01) |
| `jpl_ldot_venus` | 58517.8156026 deg/century | [S] | Mean-longitude rate, J2000 ecliptic and equinox, 3000 BC-3000 AD (Table 2a), E. M. Standish, 'Keplerian Elements for Approximate Positions of the Major Planets', NASA/JPL SSD, https://ssd.jpl.nasa.gov/planets/approx_pos.html (retrieved 2026-11-01) |
| `jpl_ldot_mars` | 19140.29934243 deg/century | [S] | Mean-longitude rate, J2000 ecliptic and equinox, 3000 BC-3000 AD (Table 2a), E. M. Standish, 'Keplerian Elements for Approximate Positions of the Major Planets', NASA/JPL SSD, https://ssd.jpl.nasa.gov/planets/approx_pos.html (retrieved 2026-11-01) |
| `jpl_ldot_jupiter` | 3034.90371757 deg/century | [S] | Mean-longitude rate, J2000 ecliptic and equinox, 3000 BC-3000 AD (Table 2a), E. M. Standish, 'Keplerian Elements for Approximate Positions of the Major Planets', NASA/JPL SSD, https://ssd.jpl.nasa.gov/planets/approx_pos.html (retrieved 2026-11-01) |
| `jpl_ldot_saturn` | 1222.11494724 deg/century | [S] | Mean-longitude rate, J2000 ecliptic and equinox, 3000 BC-3000 AD (Table 2a), E. M. Standish, 'Keplerian Elements for Approximate Positions of the Major Planets', NASA/JPL SSD, https://ssd.jpl.nasa.gov/planets/approx_pos.html (retrieved 2026-11-01) |
| `jpl_ldot_earth_moon` | 35999.37306329 deg/century | [S] | Mean-longitude rate, J2000 ecliptic and equinox, 3000 BC-3000 AD (Table 2a), E. M. Standish, 'Keplerian Elements for Approximate Positions of the Major Planets', NASA/JPL SSD, https://ssd.jpl.nasa.gov/planets/approx_pos.html (retrieved 2026-11-01) |
| `precession_arcsec_per_century` | 5028.796195 arcsec/century | [S] | General precession in longitude (Capitaine et al. 2003, IAU 2006), via Wikipedia 'Axial precession', https://en.wikipedia.org/wiki/Axial_precession (retrieved 2026-11-01) |
| `mercury_tropical` | 87.96843389 d | [D] | `360 * 36525 / (jpl_ldot_mercury + precession_arcsec_per_century / 3600)` |
| `venus_tropical` | 224.6954366 d | [D] | `360 * 36525 / (jpl_ldot_venus + precession_arcsec_per_century / 3600)` |
| `mars_tropical` | 686.9297183 d | [D] | `360 * 36525 / (jpl_ldot_mars + precession_arcsec_per_century / 3600)` |
| `jupiter_tropical` | 4330.59888 d | [D] | `360 * 36525 / (jpl_ldot_jupiter + precession_arcsec_per_century / 3600)` |
| `saturn_tropical` | 10746.93323 d | [D] | `360 * 36525 / (jpl_ldot_saturn + precession_arcsec_per_century / 3600)` |
| `tropical_year_jpl` | 365.2421884 d | [D] | `360 * 36525 / (jpl_ldot_earth_moon + precession_arcsec_per_century / 3600)` |
| `lunar_day` | 1.0350501 d | [D] | `1 / (1 - 1/synodic_month)` |
| `sidereal_day` | 0.9972695663 d | [D] | `tropical_year / (tropical_year + 1)` |
| `evection_period` | 31.81193965 d | [D] | `1 / (2/synodic_month - 1/anomalistic_month)` |
| `eclipse_year` | 346.6196961 d | [D] | `1 / (1/tropical_year + 1/(nodal_period_years * tropical_year))` |

### Trains

Errors are against the target value. Drift is the accumulated error of the displayed angle per Julian century. "Exact" means the ratio equals the target as a fraction.

| Train | Ver. | Teeth (driver/driven per mesh) | Stages | Ratio | Target period | Period error | Drift °/century | Target value ± (°/century) | Accuracy target | Largest wheel | Check |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `M1.hour_hand` | v1 | 12/48 × 15/45 | 2 | 1/12 | 0 d 12 h 0 min 0.00 s | 0 | 0 | — | exact | 50 mm (m 1) | OK |
| `M1.noon_cam` | v1 | 12/54 × 12/64 | 2 | 1/24 | 1 d 0 h 0 min 0.00 s | 0 | 0 | — | exact | 66 mm (m 1) | OK |
| `M1b.legal_hour_hand` | v1 | 12/48 × 15/45 | 2 | 1/12 | 0 d 12 h 0 min 0.00 s | 0 | 0 | — | exact | 50 mm (m 1) | OK |
| `M2.moon_hand` | v1 | 154/169 × 88/83 | 2 | 13552/14027 | 1 d 0 h 50 min 28.33 s | +0.007 s | -0.9429 | — | ≤ 1.0°/c | 171 mm (m 1) | OK |
| `M2.year` | v1 | 15/99 × 13/97 × 12/89 | 3 | 260/94963 | 365 d 5 h 48 min 45.22 s | +10.169 s | -0.0116 | ±0.0005 | ≤ 1.0°/c | 101 mm (m 1) | OK |
| `M2.weekday` | v1 | 12/84 | 1 | 1/7 | 7 d 0 h 0 min 0.00 s | 0 | 0 | — | exact | 86 mm (m 1) | OK |
| `M2.node_cam` | v1.5 | 15/109 × 12/81 × 15/106 | 3 | 50/17331 | 346 d 14 h 52 min 21.75 s | +26.254 s | -0.0333 | — | ≤ 2.0°/c | 111 mm (m 1) | OK |
| `M3.year` | v1.5 | 15/99 × 13/97 × 12/89 | 3 | 260/94963 | 365 d 5 h 48 min 45.22 s | +10.169 s | -0.0116 | ±0.0005 | ≤ 1.0°/c | 101 mm (m 1) | OK |
| `M3.solar_reduction` | v1.5 | [`M3.year`] × 20/40 | 1 | 130/94963 | 730 d 11 h 37 min 30.43 s | +20.337 s | -0.0058 | — | ≤ 1.0°/c | 42 mm (m 1) | OK |
| `M3.anomalistic_year` | v1.5 | 12/110 × 12/111 × 13/112 | 3 | 39/28490 | 730 d 12 h 27 min 45.10 s | -9.29 min | +0.1590 | — | ≤ 1.0°/c | 114 mm (m 1) | OK |
| `M3.lunar_anomaly` | v1.5 | 19/137 × 14/107 | 2 | 266/14659 | 55 d 2 h 37 min 6.41 s | -6.864 s | +0.3440 | — | ≤ 1.0°/c | 139 mm (m 1) | OK |
| `M3.evection` | v1.5 | 37/82 × 12/78 × 12/53 | 3 | 444/28249 | 63 d 14 h 58 min 23.17 s | -0.469 s | +0.0176 | — | ≤ 1.0°/c | 84 mm (m 1) | OK |
| `M3.variation` | v1.5 | 37/91 × 12/38 × 12/91 | 3 | 2664/157339 | 59 d 1 h 28 min 5.75 s | +0.733 s | -0.0320 | — | ≤ 1.0°/c | 93 mm (m 1) | OK |
| `M3.lunar_node` | v1.5 | 23/152 × 17/140 | 2 | 391/21280 | 54 d 10 h 11 min 11.62 s | +9.714 s | -0.4991 | — | ≤ 1.0°/c | 154 mm (m 1) | OK |
| `M5.earth` | v1 | 15/99 × 13/97 × 12/89 | 3 | 260/94963 | 365 d 5 h 48 min 45.22 s | +10.169 s | -0.0116 | ±0.0005 | ≤ 1.0°/c | 101 mm (m 1) | OK |
| `M5.mercury` | v1 | [`M5.earth`] × 135/67 × 136/66 | 2 | 795600/69987731 | 87 d 23 h 14 min 32.69 s | +4.886 s | -0.0961 | ±0.0007 | ≤ 1.0°/c | 138 mm (m 1) | OK |
| `M5.venus` | v1 | [`M5.earth`] × 70/63 × 79/54 | 2 | 102700/23076009 | 224 d 16 h 41 min 25.72 s | -2.98 min | +0.5385 | ±0.0003 | ≤ 1.0°/c | 81 mm (m 1) | OK |
| `M5.mars` | v1 | [`M5.earth`] × 35/48 × 35/48 | 2 | 79625/54698688 | 686 d 22 h 18 min 47.66 s | +34.53 min | -0.6681 | ±0.0033 | ≤ 1.0°/c | 50 mm (m 1) | OK |
| `M5.jupiter` | v1 | [`M5.earth`] × 15/56 × 17/54 | 2 | 5525/23930676 | 4330 d 14 h 22 min 23.20 s | +17.88 h | -0.5224 | ±0.1576 | ≤ 1.0°/c | 58 mm (m 1) | OK |
| `M5.saturn` | v1 | [`M5.earth`] × 17/75 × 12/80 | 2 | 221/2374075 | 10746 d 22 h 23 min 51.24 s | -108.30 h | +0.5139 | ±0.3786 | ≤ 1.0°/c | 82 mm (m 1) | OK |
| `M5.moon_arm` | v1 | [`M5.earth`] × 78/23 × 62/17 | 2 | 1257360/37130533 | 29 d 12 h 44 min 2.88 s | -3.312 s | +0.5780 | — | ≤ 1.0°/c | 80 mm (m 1) | OK |
| `M5.moon_globe` | v1 | 19/83 × 25/169 | 2 | 475/14027 | 29 d 12 h 44 min 2.88 s | -5.403 s | +0.9429 | ±0.0000 | ≤ 1.0°/c | 171 mm (m 1) | OK |
| `M6.sidereal` | v1 | 34/37 × 44/39 × 59/61 | 3 | 88264/88023 | 0 d 23 h 56 min 4.09 s | -9.83e-04 s | +0.1504 | — | ≤ 0.25°/c | 63 mm (m 1) | OK |
| `M6.year` | v2 | 15/99 × 13/97 × 12/89 | 3 | 260/94963 | 365 d 5 h 48 min 45.22 s | +10.169 s | -0.0116 | ±0.0005 | ≤ 2.0°/c | 101 mm (m 1) | OK |
| `M6.precession` | v2 | [`M6.year`] × 1/160 × 1/161 | 2 | 13/122312344 | 25,771 yr | +0.045 % (rate) | +0.0006 | — | ≤ 0.002°/c | 163 mm (m 1) | OK |

### Tooth strength (Lewis)

Allowable root stress 9.75 MPa; face width 4 mm unless the train sets its own; running load 10 N·mm at each output unless the train sets its own (parameters in `spec/clock.yaml` → `strength`).

- **Output capacity**: the torque at the train's output that brings its weakest tooth to the allowable stress.
- **Running load**: the output's own load plus, for a shared train such as `M5.earth`, the loads of every train driven from it, reflected through their ratios. The epicyclic `M5.moon_arm` reflects (1 + ratio) times its load onto the Earth arm.
- **Clutch window**: a slip clutch at the output must hold 3× the load behind it and slip below half the capacity. On a shared train the planet trains take off from the tube before the Earth arm's clutch, so that clutch carries only the Earth arm and the Moon arm riding on it. The shared train must also survive every clutch on it slipping at once (capacity above 3× the running load); `check` enforces both, and a running safety factor of at least 4.
- Worm meshes are not Lewis meshes and are skipped.

| Train | Face | Weakest mesh | Output capacity | Running load | Highest running stress | Safety factor | Clutch window |
|---|---|---|---|---|---|---|---|
| `M1.hour_hand` | 4 mm | 15/45 | 254 N·mm | 10.0 N·mm | 0.38 MPa | 25 | 30 … 127 N·mm |
| `M1.noon_cam` | 4 mm | 12/64 | 306 N·mm | 10.0 N·mm | 0.32 MPa | 31 | 30 … 153 N·mm |
| `M1b.legal_hour_hand` | 4 mm | 15/45 | 254 N·mm | 10.0 N·mm | 0.38 MPa | 25 | 30 … 127 N·mm |
| `M2.moon_hand` | 4 mm | 88/83 | 710 N·mm | 10.0 N·mm | 0.14 MPa | 71 | 30 … 355 N·mm |
| `M2.year` | 4 mm | 12/89 | 425 N·mm | 10.0 N·mm | 0.23 MPa | 43 | 30 … 213 N·mm |
| `M2.weekday` | 4 mm | 12/84 | 401 N·mm | 10.0 N·mm | 0.24 MPa | 40 | 30 … 201 N·mm |
| `M2.node_cam` | 4 mm | 15/106 | 599 N·mm | 10.0 N·mm | 0.16 MPa | 60 | 30 … 300 N·mm |
| `M3.year` | 4 mm | 12/89 | 425 N·mm | 15.6 N·mm | 0.36 MPa | 27 | 30 … 213 N·mm |
| `M3.solar_reduction` | 4 mm | 20/40 | 251 N·mm | 10.0 N·mm | 0.39 MPa | 25 | 30 … 126 N·mm |
| `M3.anomalistic_year` | 4 mm | 13/112 | 570 N·mm | 10.0 N·mm | 0.17 MPa | 57 | 30 … 285 N·mm |
| `M3.lunar_anomaly` | 4 mm | 14/107 | 578 N·mm | 10.0 N·mm | 0.17 MPa | 58 | 30 … 289 N·mm |
| `M3.evection` | 4 mm | 12/53 | 253 N·mm | 10.0 N·mm | 0.39 MPa | 25 | 30 … 127 N·mm |
| `M3.variation` | 4 mm | 12/91 | 435 N·mm | 10.0 N·mm | 0.22 MPa | 43 | 30 … 217 N·mm |
| `M3.lunar_node` | 4 mm | 17/140 | 827 N·mm | 10.0 N·mm | 0.12 MPa | 83 | 30 … 414 N·mm |
| `M5.earth` | 8 mm | 12/89 | 850 N·mm | 138.9 N·mm | 1.59 MPa | 6 | 179 … 425 N·mm |
| `M5.mercury` | 4 mm | 135/67 | 271 N·mm | 10.0 N·mm | 0.36 MPa | 27 | 30 … 136 N·mm |
| `M5.venus` | 4 mm | 70/63 | 357 N·mm | 10.0 N·mm | 0.27 MPa | 36 | 30 … 178 N·mm |
| `M5.mars` | 4 mm | 35/48 | 350 N·mm | 10.0 N·mm | 0.28 MPa | 35 | 30 … 175 N·mm |
| `M5.jupiter` | 4 mm | 17/54 | 319 N·mm | 10.0 N·mm | 0.31 MPa | 32 | 30 … 160 N·mm |
| `M5.saturn` | 4 mm | 12/80 | 382 N·mm | 10.0 N·mm | 0.26 MPa | 38 | 30 … 191 N·mm |
| `M5.moon_arm` | 8 mm | 78/23 | 82 N·mm | 3.0 N·mm | 0.36 MPa | 27 | 9 … 41 N·mm |
| `M5.moon_globe` | 4 mm | 25/169 | 1125 N·mm | 10.0 N·mm | 0.09 MPa | 113 | 30 … 563 N·mm |
| `M6.sidereal` | 4 mm | 34/37 | 245 N·mm | 10.0 N·mm | 0.40 MPa | 25 | 30 … 123 N·mm |
| `M6.year` | 4 mm | 12/89 | 425 N·mm | 10.0 N·mm | 0.23 MPa | 43 | 30 … 213 N·mm |

### Motor torque budget

Motor 17HS19-2004S1 (NEMA 17, 1.8°): holding torque 0.59 N·m at 2.0 A [S: datasheet]. At the proposed run current of 0.5 A it gives about **148 mN·m** [E: torque roughly proportional to current]. The required torque is the module's own input friction plus every output's running load reflected back through its ratio, with mesh efficiency 0.9 per mesh [E].

| Module | Motor → input reduction | Torque needed at input arbor | Torque needed at motor | Margin at run current |
|---|---|---|---|---|
| M1 | 1:1 | 6.54 mN·m | 6.543 mN·m | 23× |
| M1b | 1:1 | 6.03 mN·m | 6.029 mN·m | 24× |
| M2 | 24:1 | 18.59 mN·m | 0.956 mN·m | 154× |
| M3 | 24:1 | 5.98 mN·m | 0.307 mN·m | 480× |
| M5 | 24:1 | 5.94 mN·m | 0.306 mN·m | 483× |
| M6 | 24:1 | 18.79 mN·m | 0.967 mN·m | 153× |

<!-- END GENERATED -->

## 9. Decisions

| # | Decision | Status |
|---|---|---|
| 1 | Accuracy targets (§3) | **Accepted** (Paul, PR #3 review, 1 Nov 2026) |
| 2 | M5 input at 1 rev/day (§7). Torque verified in §5 | **Accepted** (Paul, PR #3). Architecture §2 updated |
| 3 | Large wheels: keep the 169-tooth wheels at module 1.0 (171 mm) on the main-dial Moon and Moon-globe trains. The module stays a parameter and the ratio is unchanged | **Accepted** (Paul, PR #3 review) |
| 4 | M3 cam convention (§6): A, B or C | **B planned** (Paul, PR #3): revisit if it proves difficult to build. M3 trains re-run for B |
| 5 | Strength rules (§5): running safety factor ≥ 4; a clutch window (3× load … ½ capacity) on every output; 8 mm faces on `M5.earth` and `M5.moon_arm`; Moon-arm load 3 N·mm | **Accepted** (Paul, PR #3). To revisit if the Earth-arm torque proves too high in practice or its clutch slips too readily; Phase 2 recomputes the loads from CAD masses |
| 6 | Planet targets from NASA/JPL mean elements, all five planets (§4F) | **Accepted** (Paul, PR #3). No tooth counts changed (§4F) |

## 10. Reproduce

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

```bash
.venv/bin/python -m pytest
```

```bash
.venv/bin/python -m tools.ratios check
```

```bash
.venv/bin/python -m tools.ratios report --write docs/gear-trains.md
```

```bash
.venv/bin/python -m tools.ratios search --period 365.24219 --stages 3
```
