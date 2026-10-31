# Architecture

Phase 0 deliverable. This file covers:

- module boundaries;
- the steppers and the clockwork rate each one outputs;
- how motion passes between modules;
- event triggering for the automata;
- homing and witness sensing;
- the setting mechanism;
- catch-up after a power cut;
- the time base;
- the electronics platform.

Tags as in `docs/reference-notes.md`. Derived numbers come from `tools/phase0/derivations.py`.
Decisions referenced as D# are in `docs/decisions.md`.

## 1. Principles

The rules in `CLAUDE.md` (hybrid build, steppers replace only the weights and pendulum, all
astronomical ratios mechanical, events powered by their own motors, forward-only running) are
taken as given. This architecture adds five working principles:

- **P1 — Steppers follow absolute time.**
  - Each stepper's commanded position is a pure function of time:
    `target_k(t) = floor((t − t0_k) · N_k / D_k)` µsteps.
  - `N_k/D_k` is the module's exact rational rate. Integer arithmetic only, so there is no
    floating-point drift over decades.
  - Normal running, catch-up and setting are all "move forward until `position = target`".
- **P2 — State lives in the trains; events are stateless shows.**
  - Anything whose *position* must match the date or time is driven continuously or indexed by a
    gear train: the ages carousel, the weekday carousel, the calendar ring.
  - An event motor only performs a motion that starts and ends in a rest state: striking, a
    procession, a crow.
  - Skipping a show (night silence, catch-up, fault) can then never leave a display wrong.
  - The one exception is the computus run (E5), which changes state. It is treated as a *stateful
    event* (§7).
- **P3 — One stepper per module, forward-only**, all following the same time base (rule 3).
- **P4 — Modules are removable cassettes.**
  - Each module has its own plates, its own stepper, one electrical connector and mechanical
    couplings that part when it is withdrawn.
  - A coupling that carries a *position* is single-position (keyed), so re-inserting a module
    cannot lose phase.
- **P5 — One source of truth.**
  - Rates, ratios, sensor positions and setting data are kept in one machine-readable file
    (`spec/clock.yaml`, created in Phase 1).
  - The ratio tool, CAD, firmware and simulator all read it, so they cannot disagree.

## 2. Modules

| ID | Module | Contents (inventory IDs) | Location (envelope §2) | Drive | Version |
|---|---|---|---|---|---|
| M0 | Controller and time base | MCU, RTC, FRAM, drivers, PSU | left (weight) tower bay | 24 V PSU | v1 |
| M1 | Time and release | I1 mean-time hands; I2 legal-time hands; quarter, hour and noon release cams; ages-carousel index drive | gallery (mean-time dial) | stepper, 1 rev/h | v1 |
| M1b | Legal-time hands (only if summer time is followed, D9) | I2 | gallery, coaxial with M1 | stepper, 1 rev/h | optional |
| M2 | Main dial | I3 Sun; I4 Moon; I5 eclipse arm; I6 shadow; I7 sunrise/sunset; I8 calendar ring; I9 feasts arc and leap gate; I10 dominical-letter dial; year-end trigger | lower centre | stepper, 1 rev/mean day | v1 (v1.5 parts provisioned) |
| M3 | Equations | I13 solar and lunar cam stacks; two correction output shafts | base, right | stepper, 1 rev/mean day | v1.5 |
| M4 | Computus | I12; transfer to I9 and I10 | base, left | event motor E5 | v2 |
| M5 | Planets and Moon phase | I14 planetary dial; I15 Moon globe | upper centre | stepper, 1 rev/mean day | v1 |
| M6 | Celestial globe | I16 sidereal rotation; I17 precession | floor level, front | stepper, 1 rev/mean day | v1 |
| M7 | Weekday carousel | I11 | above the main dial | shaft from M2 (7:1 in M7) | v1 |
| E1 | Angels | A1 bell, A2 hourglass | either side of the mean-time dial | event motor(s) | v1 |
| E2 | Ages and Death | A3 quarters, A4 hours | upper stage | event motor | v1 |
| E3 | Apostles and Christ | A5 | top stage | event motor | v1 |
| E4 | Rooster | A6 | top of the left tower | event motor | v1 |
| E5 | Computus run | A7 | in M4 | event motor | v2 |

## 3. Steppers and clockwork rates

Each module stepper drives a fixed, integer reduction to the module's **input arbor**. The input
arbor turns at a plain clockwork rate, and every other ratio inside the module is gearing.

| Stepper | Input-arbor rate | Motor → input | µstep interval | Resolution at the input arbor [D] |
|---|---|---|---|---|
| M1 | 1 rev/h (minute arbor) | 1:1 (or 4:1 for torque; Phase 2) | 1.125 s | 0.1125°, i.e. 1.1 s of displayed time |
| M2, M3, M5, M6 | 1 rev per mean solar day | 24:1 integer reduction (motor 1 rev/h) | 1.125 s | 0.0047°, i.e. 1.1 s of displayed time |
| M1b (optional) | 1 rev/h | 1:1 | 1.125 s | as M1 |

Basis: a 200-step motor at 1/16 microstep is 3200 µsteps/rev. The TMC2209 interpolates to 1/256
internally [Sn: TMC2209 datasheet]. NEMA 17 is the default; Phase 2 sizes each motor from its
torque estimate.

- **Why 24:1 and not a 1 rev/day motor.** An integer reduction keeps the rate exactly rational. It
  gives about 24× the motor torque at the input. Every stepper then has the same 1.125 s cadence,
  so they share firmware and sound alike.
- **Avoid geared motors with non-integer ratios.** The "5:1" planetary NEMA 17 is really 5.18:1,
  and the 28BYJ-48 is about 63.684:1 [Sn: hardware research]. As time-base motors they would force
  the firmware to carry awkward ratios. Use a plain motor with our own printed integer reduction.
- **v1 stepper count:** M1, M2, M5 and M6 make 4; add M3 in v1.5 (5) and optionally M1b (6). This
  fits one 8-driver board or two 4-driver boards (D3).

## 4. Motion between modules

The rule: **pass timing electrically and position mechanically.** A link that only says *when*
goes through a switch and the controller. A link that carries an angle is a shaft.

| From → To | What | Link | Coupling at the module boundary |
|---|---|---|---|
| M3 → M2 | Solar correction (Sun differential, third member) | Rotating shaft Ø5, rack-and-pinion output in M3 | Keyed single-dog coupling (position-carrying) |
| M3 → M2 | Lunar correction (Moon differential, third member) | Rotating shaft Ø5 | Keyed single-dog coupling |
| M2 → M7 | Daily rotation for the weekday carousel | Vertical shaft Ø5, 1 rev/day | Keyed single-dog coupling |
| M2 → M4 | Year-end trigger | Switch on the M2 year train → controller | Connector |
| M4 → M2 | Easter position (feasts arc), dominical letter, century leap exception (v2) | Push-rod or rack, or a shaft. **TBD** in the v2 design; the original's transfer is unknown | Keyed |
| M1 → E1, E2, E3 | Quarter, hour and noon releases | Switches on M1 cams → controller → event motors | Connector |
| M1 → E2 | Ages-carousel index (state, P2) | Shaft from the M1 quarter arbor, indexed by Geneva | Keyed |
| M1 → E2 | Hour count (snail for Death's strokes) | Snail on the M1 hour arbor read by the E2 rack (as in rack striking) | Mechanical contact across the boundary. Keep M1 and E2 in one cassette, or move the snail into E2 on its own index (Phase 2). |
| E3 → E4 | Rooster cue at Apostles 4, 8 and 12 | Cam switches on the E3 train → controller → E4 | Connector |

- **Backlash in the correction shafts adds directly to the indicated error.** Mitigations: keep the
  correction amplitude large at the shaft (gear it up in M3 and down again at M2), use
  anti-backlash springs, and keep forward-biased loading. Phase 1 sets the gearing so that 0.3°
  of shaft backlash is less than 0.05° at the hand.
- **Why M3 has its own stepper** rather than a shaft from M2: it keeps M3 self-contained and
  removable. The cost is one more driver, and both modules follow the same time law (P1).

## 5. Event triggering for the automata

This follows rule 4. A cam on the time train decides *when*; the event's own motor supplies the
energy; the event's own locking cam decides when it *ends*. This is the analogue of a striking
train's warning, release and locking.

| Event | Trigger (cam on…) | Event motor runs until… | How many strokes, decided by | Policy during catch-up / night silence |
|---|---|---|---|---|
| E1 bell angel (A1) | M1 quarter cam, 4 lobes per rev of the minute arbor | E1 locking cam | one stroke per event | skip |
| E1 hourglass (A2) | M1 hour flag | E1 locking cam (180° turn) | — | skip; the glass may end up inverted, which is harmless |
| E2 ages (A3) | M1 quarter cam | E2 locking cam | quarter count from the ages carousel index (state from M1) | skip |
| E2 Death (A4) | M1 hour flag, after A3 | E2 rack locked | hour snail on M1 (1–12) | skip |
| E3 Apostles (A5) | M1 noon flag (24 h cam) | E3 locking cam (one procession cycle) | — | skip |
| E4 rooster (A6) | E3 cue switches at Apostles 4, 8 and 12 | E4 locking cam | three crows (one per cue) | skip with E3 |
| E5 computus (A7) | M2 year-end cam (night of 31 Dec) | E5 locking cam (one computus cycle) | — | **must run**: it is stateful. Catch-up pauses while E5 completes. |

- **Sensors.**
  - Triggers: Hall-effect switches with magnets on the cams. There is no mechanical load on the
    time train, so no ratio or torque disturbance. DRV5032-class parts are recommended over the
    obsolete A3144 [Sn].
  - Locking positions: microswitches or opto forks.
- **Controller role.** It turns a trigger into "run motor k until its lock switch closes", with:
  - a timeout (fault detection);
  - a quiet-hours schedule (D10);
  - a suppression flag during catch-up;
  - priority ordering when triggers coincide (on the hour: A1, then A3 old man, then A4 Death,
    then A2 glass; at noon: then A5).
- **Faithful ordering.** At the hour, the old man strikes the fourth quarter, then Death strikes
  the hours [Sn], and the hourglass turns at the last stroke of the fourth quarter [Sn: BDM].
  Phase 2 reproduces this order, either with chained lock-switch cues or mechanically as in the
  original (TBD).

## 6. Homing and zero sensing

Forward-only trains cannot be homed by driving them to an end stop. The slow outputs (Saturn
29.4 yr, precession, the node cam) cannot even be run round in a reasonable time. So:

- **Index sensors** (one per stepper module, on the input arbor) give the controller the arbor's
  phase. That is enough to restart after a power cut and to detect missed steps: at each index
  pass the controller compares the step count with the expected one.
- **Witness sensors** sit on chosen slow outputs. They fire at a known state, and the controller
  logs the *time* of each pass. P5's model predicts when that should be. A drift means a slip
  clutch has slipped or a train has jumped a tooth. They check the clock; they do not drive it.

| Output | Sensor | Fires | Kind |
|---|---|---|---|
| M1 minute arbor | Hall | each hour at :00 local mean time | index |
| M1 hour train (12 h) | Hall | 12:00 | witness (checks the hand clutch) |
| M2 input arbor | Hall | local mean midnight | index |
| M2 calendar ring | opto on the 1 January sector | yearly | witness |
| M2 mean-Moon arbor (inside the module) | Hall | once per synodic month (mean new moon) | witness |
| M2 node arbor | Hall | once per 18.6 yr cycle (or a finer flag set) | witness (optional) |
| M3 each cam arbor | Hall | once per period | witness (optional; recommended on the two largest terms) |
| M5 input arbor | Hall | daily | index |
| M5 Earth arm | Hall | at a reference longitude | witness |
| M6 input arbor | Hall | daily | index |
| M6 globe | Hall | once per sidereal day | witness: checks the epicyclic train every day |
| M7 carousel | Hall | Sunday noon | witness |
| E1–E5 | lock switch | rest position | lock (each event) |

## 7. Setting mechanism

When the clock is assembled, or a module has been serviced, every output must show "now" without
running decades of motion. The design rule: **every output whose position matters is
independently settable, by turning it forward, against a scale.**

| Output | Setting method | Scale used for setting |
|---|---|---|
| Hands: I1, I2, I3, I4, planet arms (I14) | Friction-clutched hub, like a cannon pinion: a printed hub with a wave washer or disc spring on a brass tube. Turned forward by hand. | The dial itself; printed setting rings |
| Moon-phase globe (I15); celestial globe (I16) | Friction coupling between train and output | Globe phase or hour-circle marks |
| Cams whose phase sets a calculation: equations (I13), sunrise/sunset (I7), node cam (I5) | **Indexed dog clutch**: spring-loaded, pulled axially to free it, turned to an index mark, re-engaged. Resolution is one tooth of its wheel; e.g. 1/200 rev of a 27.5-day cam is 3.3 h, below what the display can show. | Engraved index on the cam and plate |
| Calendar ring (I8); 4-year leap count | A lever lifts the day jumper or pawl; the ring is turned to the date; the leap wheel is set to the year in the cycle | Ring sectors; leap-wheel numbers |
| Weekday carousel (I11); ages carousel (A3) | Dog clutch at the drive | The carousel itself |
| Computus wheels (I12) | Each count wheel on a jumper, turned by hand | The computus dials |
| Precession (I17) | Turned by hand (it moves about 1.4° per century [D]) | Globe scale |
| Slip-clutch torque | Must exceed the train's running torque and stay below finger torque. Phase 2 calculates it per output. A commercial adjustable clutch for 6 mm shafts exists (Huco Vari-Tork) [Sn]. | — |

**Setting procedure (firmware plus simulator):**

1. Choose a setting instant T_set a few minutes ahead.
2. The simulator writes a **setting sheet** for T_set: for each output, the angle to set and the
   dial mark to align.
3. Set each module's outputs by hand, turning forward only.
4. At T_set, the controller records `t0_k` and `position_k` for every module and starts following
   P1.
5. Fast motions (a module's input arbor, the Sun and Moon hands within a day) can instead be set
   by letting the controller run forward. At catch-up speed, 1 day of motion takes 24 s [D].

## 8. Catch-up after a power cut

- **Persisted state.** For each module: `t0_k`, the commanded µstep count, and the driver's
  microstep phase. They go in **FRAM** (I²C), written at least once per second. Flash would wear
  out at that rate. FRAM endurance is 10¹²–10¹⁴ writes per byte depending on the part; cite the
  chosen part's datasheet in the BOM. One write per second for 50 years is 1.6 × 10⁹ writes [D],
  well inside that range.
- **Power-fail handling (recommended).**
  - The controller watches the 24 V rail.
  - On loss it stops new events, steps each motor *forward* to its next microstep-phase zero (at
    most 4 full steps, 64 µsteps, a few milliseconds at speed), writes FRAM, then de-energises.
  - Bulk capacitance on 24 V (sized in Phase 3) holds the rail long enough.
  - Result: the motor re-energises at exactly the phase it stopped at.
  - Without this, a TMC2209 restarts at its power-on phase. That can jump up to ±2 full steps,
    which is 0.15° at a 1 rev/day arbor, or 36 s of time [D].
- **On power-up.**
  1. Read the RTC (time survives the outage).
  2. Compute `target_k(now)`.
  3. Run each module forward at catch-up speed until `position_k = target_k`.
  4. At 60 rpm motor speed that is 3600× real time: a 1-day outage is caught up in 24 s, a 30-day
     outage in 12 min [D].
  5. Show events found during catch-up are suppressed (P2). The stateful E5 computus event runs
     when its trigger is reached; catch-up pauses until E5 locks.
  6. On the next index pass, the controller checks the phase.
- **Never reverse.** If the controller ever finds `position > target` (for example the RTC jumped
  backwards), that module **waits** until time catches up; it never runs backwards. A time jump
  larger than a threshold (e.g. 10 min) is not acted on without confirmation from the UI.
- **Long outages** (more than a configurable limit, e.g. 60 days): catch-up asks for confirmation,
  because re-setting from a fresh setting sheet may be quicker.

## 9. Time base

- **Reference: UTC from NTP over Wi-Fi**, disciplining a battery-backed RTC that keeps time with no
  network and through outages.
  - DS3231: ±2 ppm, 0–40 °C [Sn: ADI], i.e. about ±1 min/yr free-running [D: 2e-6 × 31.6e6 s].
  - RV-3028-C7: about ±1 ppm at room temperature, with a trickle charger suited to a supercapacitor
    [Sn].
  - D3 picks one.
- **Clock time.**
  - Mean solar time is UTC plus the longitude offset (D2): Strasbourg +31.00 min, Bordeaux
    −2.28 min [D].
  - UT1 − UTC is under 0.9 s (IERS policy), which is negligible here.
  - Leap seconds are ignored (POSIX time).
- **Summer time** affects only the optional M1b legal-time hands (D9). The automata follow mean
  time, as in the original [Sn: CATH].
- **Accuracy split** (rule 5): long-term timekeeping is NTP-grade. Each indication's error is then
  only its gear-ratio error, which Phase 1 reports per train.

## 10. Electronics platform (summary; decision D3)

**I/O budget for the full clock [E: counted from the tables above].**

| Item | Count | I/O needed |
|---|---|---|
| Steppers | 4 (v1) to 6 | STEP + DIR each = 8–12 GPIO, plus ENABLE. TMC2209 UART: 4 addresses per bus, so 2 buses for 6 drivers. |
| Event motors | 5–6 (E1×1–2, E2, E3, E4, E5), DC gearmotors, one direction | 6 PWM channels through H-bridges or MOSFETs |
| Inputs | ~6 index, ~8 witness, ~6 trigger, ~6 lock, 1 door = **~27** | 2 × MCP23017 I²C expanders with interrupt |
| I²C devices | RTC, FRAM, 2 expanders, optional current monitor | 1 bus |
| Sound (if D8 chooses a speaker) | DFPlayer Mini-class module | 1 UART |
| Local UI | status LEDs plus a few buttons, or a small display and encoder | a few GPIO |
| Network UI | web page and MQTT (Home Assistant) | Wi-Fi |

**Recommended (D3).** An **ESP32-S3** as the single controller (Wi-Fi/NTP, MQTT, Arduino or
PlatformIO; Paul knows it), with **TMC2209 stepsticks in UART mode** on a carrier board.

- Phase 3 picks between an off-the-shelf multi-driver board and a custom carrier PCB.
- For the Phase 2 test rig, reuse Paul's **Arduino Mega + RAMPS 1.4 + TMC2209**: no purchase.
- Write the firmware so the motion core is board-independent.

## 11. Power, wiring and serviceability

- **Power.**
  - 24 V supply sized in Phase 3. Candidate: Mean Well LRS-100-24, 24 V 4.5 A [Sn].
  - The steppers run at low hold current (TMC2209 IHOLD) in StealthChop: quiet and cool.
  - A 5 V buck regulator feeds logic, sensors and the event motors.
- **One connector per module.** Locking, keyed connectors such as JST-XH or Micro-Fit. All the
  module's motor, sensor and switch wires go through it, so a module unplugs in one action.
- **Wiring route.** Wiring runs in a riser in the staircase tower, with channels behind each stage.
  The controller and PSU sit in the left (weight) tower behind a removable panel (envelope §2).
- **Access.**
  - Each stage's glazing opens.
  - Each module slides out forward or rearward on rails (direction chosen in Phase 2 per module).
  - Motors are reachable without removing gears.

## 12. Repository layout (refines `CLAUDE.md`)

```
docs/                    spec (this file, inventory, envelope, decisions, bom, gear-trains)
spec/clock.yaml          single source of truth: modules, rates, ratios, sensors, setting data (Phase 1)
tools/phase0/            Phase 0 derivations
tools/toolchain-check/   CAD toolchain smoke tests
tools/ratios/            gear-ratio search + tests (Phase 1)
cad/lib/                 shared parametric parts (build123d, if D1 is approved)
cad/modules/<module>/    one folder per module: M1…M7, E1…E5
export/                  generated STL/3MF/DAE/PNG (git-ignored except released files)
firmware/                PlatformIO project (ESP32-S3) + board-independent motion core
sim/                     accelerated-time simulator, ephemeris validation, setting-sheet generator
```
