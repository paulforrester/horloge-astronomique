# Gear trains

Phase 1 deliverable. This file gives the chosen gear train for every indication, its error, and
the accuracy target that justifies it.

- The trains themselves live in [`spec/clock.yaml`](../spec/clock.yaml), the single source of
  truth (architecture P5).
- The tables in §6 are **generated** from that file by `tools/ratios`. A test fails if they drift
  apart.
- Tags as in `docs/reference-notes.md`.

**Status: Proposed** (Phase 1 gate). The decisions needed from Paul are in §7.

## 1. How to read the numbers

- **Ratio** = output turns per input turn, as an exact fraction. "Exact" means it equals the
  target exactly.
- **Period error** is the achieved output period minus the target period.
- **Drift** is the error the displayed angle accumulates per Julian century, in degrees. It is
  the figure that matters for a display: 1° is 2.2 mm at the tip of the 125 mm Sun hand [D: 1 m
  hand at 1:8, ELS].
- **Target value ±** is the drift equivalent to the rounding of the *sourced* target value. A
  train whose drift is inside that band is as accurate as our knowledge of the target. Example:
  NASA quotes Mercury's period to 0.001 d, which alone is worth ±0.85°/century.
- Every ratio is computed with Python `Fraction`s, so nothing is lost to floating-point rounding.
  Errors are against modern values (§6 Targets), not Schwilgué's 19th-century ones.

## 2. Constraints used (D4)

| Constraint | Value | Why |
|---|---|---|
| Tooth profile | involute 20° | D4 |
| Module | 1.0 by default (sizes below); 0.8 scales every diameter by 0.8 | D4; the real minimum comes from the local tolerance test |
| Smallest pinion | 12 teeth (profile-shifted below 17) | D4 |
| Largest wheel | 160 teeth (162 mm tip at m 1.0); 200 where a train says so | Keeps wheels well inside the 320 mm bed and the module footprints |
| Largest single mesh | 10:1 | Printable pinions, smooth running |
| Stages | as few as meet the accuracy target (1, then 2, then 3) | Brief: "prefer fewer stages" |

Worms (driver = 1) are used only for the v2 precession drive.

## 3. Accuracy targets (proposed)

| Class | Target | Applies to | Justification |
|---|---|---|---|
| Clock and calendar functions | **exact** | hour hands, 24 h cam, weekday | Integer ratios exist, so there is no reason to accept any error |
| Displayed astronomical angles | **≤ 1° per century** | year arbor, main-dial Moon, planets, Moon arm, Moon globe | 1° is the smallest readable unit at 1:8 (2.2 mm at the Sun-hand tip; 2.4 mm at the 137.5 mm planetary radius). Under 1° per century is invisible in a lifetime, and the setting mechanism (architecture §7) can always re-zero. |
| Sidereal globe | **≤ 0.25° per century** | M6 | Its hour circle *reads* sidereal time: 0.25° is 1 minute. |
| Correction-cam arguments (v1.5) | **≤ 2° per century** | equation cams, eclipse node cam | A phase error φ in a cam of amplitude A gives about A·φ (rad). For the largest lunar term (6.3°) and φ = 2°, that is 0.2° after a full century. |
| Precession (v2) | ≤ 0.002° per century (about 0.05 % in rate) | M6 | It moves about 1.4° per century in total [D]. Any rate within 1 % is invisible. |

## 4. What the search found

**A. One year train for everything.**
- 15/99 × 13/97 × 12/89 = 260/94963. That is one turn per 365 d 5 h 48 min 45.2 s, against
  365.24219 d: +10.2 s per year, −0.012°/century.
- The same three meshes serve M2 (main-dial year arbor), M3 (solar reduction), M5 (Earth arm) and
  M6 (precession feed). One design, printed four times; a test enforces that they stay identical.

**B. No differentials needed for the mean motions.**
- Plain compound trains reach every target:
  - sidereal globe: 3 stages, +0.15°/century;
  - main-dial Moon: 2 stages, −0.94°/century;
  - Moon globe: 2 stages, +0.94°/century.
- Schwilgué used an exact epicyclic train for the sphere [S: LEF] and differentials for the Moon
  [S: CLEA]. They are not needed at this accuracy, which saves parts in the densest modules.
- The tool can still design differentials (`search_differential`). It reproduces Schwilgué's exact
  sidereal ratio 164809/164359.

**C. Planets: Schwilgué's arrangement.**
- Each planet is driven from the central Earth tube through a **reverted (coaxial) pair**, so every
  arm's tube is concentric with the Sun.
- Jupiter and Saturn cannot be reached from a daily arbor in 3 meshes of ≤ 10:1; via the Earth
  tube they need 2.
- A *common* tooth sum for all five planets (every intermediate arbor on one circle) gives at best
  4.2°/century [D: exhaustive search over sums 60–320]. So each planet gets its own
  intermediate-arbor radius: 101, 66.5, 41.5, 35.5 and 46 mm.
- Every planet is within 1°/century **including the Earth train's error**.

**D. Planetarium Moon.**
- The Moon on the Earth arm is an epicyclic by nature: a fixed 78-tooth sun wheel, a compound
  planet 23/62 on the Earth arm, and a 17-tooth pinion on the Moon arm.
- Its rate relative to the Earth arm is the synodic rate, +0.58°/century.

**E. Schwilgué's own trains, checked against modern values** [D: `tools/ratios`]:

| Train | His period | Modern | Drift vs modern |
|---|---|---|---|
| Year | 365.242222 d | 365.24219 | −0.003°/century |
| Mercury | 87.968 d | 87.968 | −0.80°/century |
| Venus | 224.695 d | 224.695 | −0.11°/century |
| Mars | **686.930 d** | **686.972** | **+1.18°/century** (his target value was off) |
| Jupiter | 4330.593 d | 4330.595 | +0.001°/century |
| Saturn | 10746.938 d | 10746.940 | 0.000°/century |
| Synodic month | 29.530590 d | 29.5305889 | −0.02°/century |

- **Under his own limits** (17–250 teeth, 2 stages), the exhaustive search finds that his Venus,
  Mars, Jupiter and Saturn ratios are **the best possible**. It returns exactly his fractions.
- Only his Mercury could have been about 12× more accurate (245/183 × 245/79).

## 5. Proposed changes to earlier documents

- **M5 input: 1 rev per mean day instead of 1 rev/h** (architecture §2).
  - The hourly input was chosen to keep Schwilgué's Earth train 9/156 × 10/188 × 10/269.
  - Its 9-tooth pinion is below our printable minimum, and the 269-tooth wheel is 271 mm at
    module 1.0.
  - From a daily arbor the shared year train (A) does the job in 3 small stages, and every
    stepper module except M1 then runs at the same rate.
- **M3 cams: one turn per period** in these trains.
  - Schwilgué traced *two* periods on each cylinder so that opposite points are level
    [S: LEF].
  - If Phase 2 keeps that, each M3 output halves. The tool re-runs in seconds.

## 6. Generated tables

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
| `mercury_tropical` | 87.968 d | [S] | Tropical orbit period, NASA Mercury fact sheet, https://nssdc.gsfc.nasa.gov/planetary/factsheet/mercuryfact.html (retrieved 2026-11-01) |
| `venus_tropical` | 224.695 d | [S] | Tropical orbit period, NASA Venus fact sheet, https://nssdc.gsfc.nasa.gov/planetary/factsheet/venusfact.html (retrieved 2026-11-01) |
| `mars_tropical` | 686.972 d | [S] | Tropical orbit period, NASA Mars fact sheet, https://nssdc.gsfc.nasa.gov/planetary/factsheet/marsfact.html (retrieved 2026-11-01) |
| `jupiter_tropical` | 4330.595 d | [S] | Tropical orbit period, NASA Jupiter fact sheet, https://nssdc.gsfc.nasa.gov/planetary/factsheet/jupiterfact.html (retrieved 2026-11-01) |
| `saturn_tropical` | 10746.94 d | [S] | Tropical orbit period, NASA Saturn fact sheet, https://nssdc.gsfc.nasa.gov/planetary/factsheet/saturnfact.html (retrieved 2026-11-01) |
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
| `M3.year` | v1.5 | 15/99 × 13/97 × 12/89 | 3 | 260/94963 | 365 d 5 h 48 min 45.22 s | +10.169 s | -0.0116 | ±0.0005 | ≤ 2.0°/c | 101 mm (m 1) | OK |
| `M3.anomalistic_year` | v1.5 | 13/96 × 14/108 × 17/109 | 3 | 1547/565056 | 365 d 6 h 13 min 52.55 s | -36.687 s | +0.0418 | ±0.0000 | ≤ 2.0°/c | 111 mm (m 1) | OK |
| `M3.lunar_anomaly` | v1.5 | 13/82 × 19/83 | 2 | 247/6806 | 27 d 13 h 18 min 33.21 s | +9.061 s | -1.8162 | ±0.0087 | ≤ 2.0°/c | 85 mm (m 1) | OK |
| `M3.evection` | v1.5 | 31/122 × 12/97 | 2 | 186/5917 | 31 d 19 h 29 min 11.59 s | -9.650 s | +1.4513 | — | ≤ 2.0°/c | 124 mm (m 1) | OK |
| `M3.variation` | v1.5 | 25/113 × 15/98 | 2 | 375/11074 | 29 d 12 h 44 min 2.88 s | +6.723 s | -1.1733 | ±0.0000 | ≤ 2.0°/c | 115 mm (m 1) | OK |
| `M3.lunar_node` | v1.5 | 23/112 × 17/95 | 2 | 391/10640 | 27 d 5 h 5 min 35.81 s | +4.857 s | -0.9982 | ±0.0089 | ≤ 2.0°/c | 114 mm (m 1) | OK |
| `M5.earth` | v1 | 15/99 × 13/97 × 12/89 | 3 | 260/94963 | 365 d 5 h 48 min 45.22 s | +10.169 s | -0.0116 | ±0.0005 | ≤ 1.0°/c | 101 mm (m 1) | OK |
| `M5.mercury` | v1 | [`M5.earth`] × 135/67 × 136/66 | 2 | 795600/69987731 | 87 d 23 h 13 min 55.20 s | +42.375 s | -0.8334 | ±0.8496 | ≤ 1.0°/c | 138 mm (m 1) | OK |
| `M5.venus` | v1 | [`M5.earth`] × 70/63 × 79/54 | 2 | 102700/23076009 | 224 d 16 h 40 min 48.00 s | -2.35 min | +0.4248 | ±0.1302 | ≤ 1.0°/c | 81 mm (m 1) | OK |
| `M5.mars` | v1 | [`M5.earth`] × 35/48 × 35/48 | 2 | 79625/54698688 | 686 d 23 h 19 min 40.80 s | -26.36 min | +0.5100 | ±0.0139 | ≤ 1.0°/c | 50 mm (m 1) | OK |
| `M5.jupiter` | v1 | [`M5.earth`] × 15/56 × 17/54 | 2 | 5525/23930676 | 4330 d 14 h 16 min 48.00 s | +17.98 h | -0.5251 | ±0.0004 | ≤ 1.0°/c | 58 mm (m 1) | OK |
| `M5.saturn` | v1 | [`M5.earth`] × 17/75 × 12/80 | 2 | 221/2374075 | 10746 d 22 h 33 min 36.00 s | -108.46 h | +0.5147 | ±0.0001 | ≤ 1.0°/c | 82 mm (m 1) | OK |
| `M5.moon_arm` | v1 | [`M5.earth`] × 78/23 × 62/17 | 2 | 1257360/37130533 | 29 d 12 h 44 min 2.88 s | -3.312 s | +0.5780 | — | ≤ 1.0°/c | 80 mm (m 1) | OK |
| `M5.moon_globe` | v1 | 19/83 × 25/169 | 2 | 475/14027 | 29 d 12 h 44 min 2.88 s | -5.403 s | +0.9429 | ±0.0000 | ≤ 1.0°/c | 171 mm (m 1) | OK |
| `M6.sidereal` | v1 | 34/37 × 44/39 × 59/61 | 3 | 88264/88023 | 0 d 23 h 56 min 4.09 s | -9.83e-04 s | +0.1504 | — | ≤ 0.25°/c | 63 mm (m 1) | OK |
| `M6.year` | v2 | 15/99 × 13/97 × 12/89 | 3 | 260/94963 | 365 d 5 h 48 min 45.22 s | +10.169 s | -0.0116 | ±0.0005 | ≤ 2.0°/c | 101 mm (m 1) | OK |
| `M6.precession` | v2 | [`M6.year`] × 1/160 × 1/161 | 2 | 13/122312344 | 25,771 yr | +0.045 % (rate) | +0.0006 | — | ≤ 0.002°/c | 163 mm (m 1) | OK |

<!-- END GENERATED -->

## 7. Decisions needed from Paul

1. **Accuracy targets** (§3): accept?
2. **M5 input at 1 rev/day** (§5): accept? It updates architecture §2/§3.
3. **Large wheels.** At module 1.0 the main-dial Moon train and the Moon-globe train each have a
   169-tooth wheel (171 mm).
   - Accept, or use module 0.8 there (137 mm)?
   - Either way the module stays a parameter and the ratio is unchanged.
4. **M3 cam convention**: one turn per period, or Schwilgué's two periods per cylinder (§5)?
   This can wait until the Phase 2 equations design.

## 8. Reproduce

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
