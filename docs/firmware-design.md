# Firmware and simulator: Phase 3 design gate

Phase 3 deliverable, part 1. It covers the cloud work of Phase 3:
- the electronics around the controller (M0);
- the structure of the controller firmware;
- the accelerated-time simulator and how it is validated against an ephemeris;
- the test strategy;
- the decisions needed from Paul.

There is no large code yet. The firmware skeleton and the simulator follow in later PRs, once Paul
has approved this gate (§12).

Tags as in `docs/reference-notes.md`: [S] sourced (with link), [D] derived (calculation shown),
[E] estimate (method and uncertainty), [Sn] snippet only. Decisions D1–D16 are in
`docs/decisions.md`. New decisions are written **F1, F2, …** here; each becomes "D-next
(firmware)" when it is accepted.

**What is binding here** (`CLAUDE.md`, architecture):
- Timekeeping comes from the controller: RTC disciplined by NTP (rule 5, architecture §9).
- Steppers output only clockwork rates and turn forward only (rules 2 and 3, P1, P3).
- A cam on the time train decides *when* a show happens; a small event motor supplies the energy
  (rule 4, architecture §5).
- State lives in the trains; shows are stateless, except E5 and E6 (P2).
- One source of truth: `spec/clock.yaml` (P5).
- The controller is an ESP32-S3 with TMC2209 drivers in UART mode, and DC gearmotors for the
  events (D3, accepted).

## Contents

1. Summary of the recommendations
2. What has changed since architecture §10
3. Controller hardware
4. Connectors and wiring per module
5. Firmware structure: tasks and timing
6. The step scheduler (clockwork steppers)
7. The event motors and the show chain
8. Time: NTP, RTC, summer time, quiet hours
9. Setting, homing, catch-up and faults
10. Network: MQTT, Home Assistant, OTA
11. The simulator and its validation
12. Test strategy and the PR plan
13. Interface questions for other modules
14. Decisions needed from Paul

## 1. Summary of the recommendations

| Topic | Recommendation | Section |
|---|---|---|
| MCU | ESP32-S3-DevKitC-1-N8R8, as in D3 and BOM Batch 1 | §3.1 |
| Board | A carrier PCB with sockets: the DevKit, 8 stepsticks and breakout modules plug in. Prototype first on the bench with the same modules (F1) | §3.2 |
| Stepper drivers | 7 TMC2209 in v1.5 (6 in v1) on two UART buses, 4 addresses each; 8 sockets. STEP per driver; DIR fixed in hardware, direction set by the driver's `shaft` bit | §3.3 |
| Event motors | 9 channels in v2 (8 in v1). DRV8833 H-bridges switched by one PCA9685, one line per motor; E2's walk on a native PWM pin (F2) | §3.4 |
| Inputs | 37 by v2 (31 in v1): three MCP23017 (48 inputs), not two (BOM change, §13) | §3.5 |
| RTC | RV-3028-C7 with a supercapacitor, trimmed from NTP (F3) | §3.6 |
| Storage | I²C FRAM, MB85RC256V class, two alternating records with CRC | §3.6, §9.4 |
| Power | Mean Well LRS-100-24 (Batch 1); 24 → 5 V for logic; a separate 24 → 6 V buck for the event motors (F5); power-fail detection and bulk capacitance | §3.7 |
| Firmware | Arduino-ESP32 core on FreeRTOS. A board-independent core in plain C++17, unit-tested on the host. Arduino IDE 2 for Paul, `arduino-cli` for headless builds (F7) | §5 |
| Motion | One law for every stepper: target = f(time), forward only, a trapezoidal follower at catch-up speed | §6 |
| Shows | One state machine per event motor (lock switch, timeouts), and a sequencer that chains them in DA's order | §7 |
| Simulator | Python. It reads `spec/clock.yaml` through `tools/ratios`, runs the same time law, and checks every indication against Skyfield with DE440s | §11 |

## 2. What has changed since architecture §10

Architecture §10 was written in Phase 0. The module designs since then change the counts:

- **Steppers: 6 in v1, not 4.** M1, M1b, M2, M5, M6 and E2's state arbor (BOM Batch 2;
  `docs/e2-design.md` §4.1). M3 makes 7 in v1.5.
- **Event motors: 8 in v1** (BOM Batch 2): E1 × 2 (bell, hourglass), E2 × 3 (walk, quarters,
  hours), E3, E4, E6. E5 makes 9 in v2.
- **Inputs: 37 by v2**, not 27 (§3.5).
- **The releases are on legal time** (D14), on M1b. Architecture §9's sentence "The automata follow
  mean time" predates D14; D14 governs.
- **E2's walk runs in two phases** around the strokes, and the controller starts phase A
  ≈ 8.7 s before the quarter (`docs/e2-design.md` §11.3).
- **E6 runs every mean midnight** and is stateful (`docs/m2-design.md` §6).

These are not interface changes; they are counts. §13 lists the BOM rows this affects.

## 3. Controller hardware

### 3.1 MCU: ESP32-S3 (D3, accepted)

D3 chose the ESP32-S3. This section only checks that it has enough resources.

| Resource | Needed | ESP32-S3 has | Source |
|---|---|---|---|
| UARTs | 2 for the TMC2209 buses; 1 spare (a DFPlayer only if the rooster needs the speaker fallback, D8) | 3 (UART0–2) | [S: [ESP32-S3 datasheet v2.2](https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf), Features p. 4, §4.2.1.1 p. 51] |
| GPIO | 23 (pin plan below) | 45 in all; about 27 free on the DevKitC-1 N8R8 once the reserved pins are left out [D: list below] | [S: [ESP32-S3 datasheet v2.2](https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf), Features p. 4, §4.2.1.1 p. 51]; [S: [WROOM-1 datasheet v1.8](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf) Table 3-1 note b, p. 12; [ESP32-S3 datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf) §2.3.5, p. 26] |
| Wi-Fi | NTP, MQTT, OTA | 2.4 GHz 802.11 b/g/n | [S: ESP32-S3 datasheet, Features] |
| Cores | 2: the clock on one, the network on the other | 2 × Xtensa LX7 | [S: ESP32-S3 datasheet, Features] |
| Flash | two OTA app slots | 8 MB on N8R8 | BOM Batch 1 |

**Pin plan [E: counted; final assignment in the skeleton PR].**

| Function | Pins |
|---|---|
| STEP, one per driver | 8 (7 used, 1 spare socket) |
| EN, shared by all drivers | 1 |
| TMC2209 UART bus 1 and bus 2 (TX, RX) | 4 |
| I²C (SDA, SCL): RTC, FRAM, 3 × MCP23017, PCA9685 | 2 |
| MCP23017 interrupt lines (mirrored A/B, one per chip) | 3 |
| PCA9685 output enable (a hardware kill for every event motor) | 1 |
| DRV8833 nSLEEP, shared (all bridges off) | 1 |
| Power-fail comparator | 1 |
| Status LED, one button | 2 (the DevKit's RGB LED counts as one) |
| E2 walk motor, ultrasonic PWM (§3.4) | 1 |
| **Total** | **24** |

- DIR needs no pin: every stepper turns one way. The DIR input is tied in hardware, and the
  direction is set per motor by the driver's `shaft` bit over UART (GCONF bit 3, "1: Inverse motor direction") [S: [TMC2209 datasheet Rev 1.08](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/696/TMC2209_Rev.1.08.pdf) (DigiKey copy; analog.com refused the download) §5.1, p. 23]. A motor mounted the other
  way round is fixed in the configuration, not the wiring.
- Disabling one driver is done over UART (TOFF = 0), so one EN pin is enough.
- **Pins to avoid** on the N8R8 module [S: [WROOM-1 datasheet v1.8](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf) Table 3-1 note b, p. 12; [ESP32-S3 datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf) §2.3.5, p. 26]:
  - strapping pins GPIO0, 3, 45, 46;
  - USB GPIO19, 20; UART0 GPIO43, 44 (the DevKit's USB-to-UART console);
  - flash and PSRAM GPIO26–32, and GPIO35–37 (octal PSRAM);
  - JTAG GPIO39–42 are usable if JTAG debugging is not needed.
  - That leaves GPIO1, 2, 4–18, 21, 33, 34, 38–42, 47, 48: 27 pins [D: count]. The DevKitC-1 v1.1's
    RGB LED is on GPIO38 [S: [DevKitC-1 user guide v1.1](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/user_guide_v1.1.html)].

### 3.2 How the controller is built (F1)

| Option | For | Against |
|---|---|---|
| **A. Carrier PCB with sockets** (recommended). The DevKit, the stepsticks and small breakout boards (RTC, FRAM, MCP23017, PCA9685, DRV8833, bucks) plug into headers. The PCB holds only sockets, connectors, pull-ups, filters and the bulk capacitors | Tidy; one keyed connector per module on the board edge; every active part is a plug-in, so a dead part is swapped in a minute (serviceability); low design risk, as the PCB has no fine-pitch parts | A PCB to design (KiCad; a cloud task) and order; one re-spin is likely |
| B. The same modules on stripboard, hand-wired | No PCB | About 200 hand-made joints; hard to service; error-prone |
| C. A 3D-printer mainboard (8 drivers) plus the ESP32-S3 | Drivers, power stage and connectors done | Two MCUs and two firmwares (D3 option D, rejected); the printer board's MOSFET outputs do not suit nine braked DC motors |
| D. A full custom PCB with the chips soldered on | Smallest; cheapest in quantity | Fine-pitch soldering; a dead chip means a new board; most design risk |

**Recommendation: A**, in two steps.
1. **Bench prototype** (local phase): the test rig's DevKit and drivers, plus the breakouts, on a
   breadboard or jumper wires. It proves every circuit and the firmware before a PCB is ordered.
2. **Carrier PCB**: drawn in KiCad in a later cloud PR, after the bench prototype works. Made in
   the EU (for example Aisler, Germany) or by JLCPCB, at Paul's choice.

**What making the PCB involves (F1, accepted).**

| Step | Who | What |
|---|---|---|
| Schematic | cloud | KiCad (free). Drawn from the working bench prototype. Paul reviews a PDF |
| Layout | cloud | Sockets, connectors and tracks; KiCad's design-rule check run headless. Paul reviews a 3D render and a 1:1 print |
| Fabrication files | cloud | Gerber and drill files in one zip, committed with the PR, like the print files |
| Order | Paul | Upload the zip; check the maker's online viewer; standard options (2 layers, 1.6 mm, lead-free finish) |
| Assembly | Paul | About 200 through-hole joints [E]: sockets, connectors, resistors, capacitors. No surface-mount parts |
| Bring-up | Paul, with a checklist and a test sketch | One module at a time |

**Fabricators that take small batches** [Sn: from general knowledge, not checked in this session;
prices, minimums, delivery and VAT handling to be checked when ordering ⚠]:

| Maker | Where | Small batch | For | Against |
|---|---|---|---|---|
| **Aisler** | Germany | 3 boards | EU: VAT included, no customs; fast post to France; checks the files on upload | Dearer per board |
| Eurocircuits | Belgium | from 1 board (pooled prototypes) | EU; strong design checks | Dearer still; aimed at professionals |
| Multi-CB | Germany | small runs | EU | Fewer hobby conveniences |
| **JLCPCB** | China | 5 boards | Cheapest; KiCad plug-in to export the files | Shipping and VAT to add; 1–2 weeks with fast post |
| PCBWay | China | 5 boards | Cheap; good hobby support | as JLCPCB |

**Recommendation: Aisler for the first board.** It is in the EU (rule: source in France/EU where
possible), with no customs, and it checks the files on upload. JLCPCB is a cheaper alternative
for a re-spin, if one is needed. The KiCad files suit every maker, so the choice can wait until
the board is drawn.

### 3.3 Stepper drivers

- **TMC2209 stepsticks in UART mode** (D3). StealthChop, 1/16 microstepping with the driver's
  interpolation to 1/256 (CHOPCONF `intpol`, default on) [S: [TMC2209 datasheet Rev 1.08](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/696/TMC2209_Rev.1.08.pdf) §5.5.1, p. 33], run current 0.5 A (`spec/clock.yaml` `motor.run_current_a`).
- **Count: 7 by v1.5**: M1, M1b, M2, M5, M6, E2 state, M3. The carrier has **8 sockets**, so one
  is a spare.
- **Two UART buses of 4 addresses each.** The TMC2209 takes 4 addresses, set by its MS1/MS2 pins
  [S: [TMC2209 datasheet Rev 1.08](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/696/TMC2209_Rev.1.08.pdf) §4.1, p. 18]. Bus 1: M1, M1b, E2 state, M2. Bus 2: M5, M6, M3, spare. A bus is one TX line, one RX line
  and a 1 kΩ resistor, as on the test rig (`docs/test-rig.md` §7).
- **What the firmware uses the UART for:** run and hold current, microsteps, StealthChop, the
  `shaft` bit, reading `DRV_STATUS` (over-temperature, short, open load) and `MSCNT`, the
  microstep counter (read-only, 0–1023) [S: [TMC2209 datasheet Rev 1.08](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/696/TMC2209_Rev.1.08.pdf) §5.4, p. 31].
- **Open load as presence detection.** A module unplugged for service shows as open load on its
  driver. The firmware then stops that axis and re-homes it when it comes back (§9.2). No extra
  pin is needed.
- **Decoupling:** 100 µF per driver (BOM Batch 1) on the carrier.

### 3.4 Event-motor drive (F2)

Nine DC gearmotors by v2, all one direction (architecture §5), each stopped by its lock switch.
The E2 walk needs its speed trimmed by PWM (`docs/e2-design.md` §11.8). The others benefit from a
soft start and a braked stop (quieter; D3 noise test).

| Option | For | Against |
|---|---|---|
| **A. One PCA9685 (16 channels on I²C) driving DRV8833 bridges, one channel per motor; the E2 walk on a native ultrasonic PWM pin** (recommended) | Frees the GPIO; 7 channels to spare; a hardware kill line | The one-channel scheme needs care (below); a stop goes through I²C (≈ 1 ms, which is 0.016° of E2's program at 16°/s [D: 16°/s × 1 ms]) |
| B. The ESP32's own PWM (LEDC), two GPIO per motor | No extra chip; fastest stop | 18 GPIO for 9 motors: does not fit beside the steppers |
| C. Two PCA9685, two channels per motor | Full DRV8833 control (coast and reverse too) | One more chip; reverse is never needed |

**The one-channel scheme (A).** Each motor's DRV8833 input pair is wired IN1 = high, IN2 = the
PCA9685 channel. From the DRV8833 truth table [S: [DRV8833 SLVSAR1E](https://www.ti.com/lit/ds/symlink/drv8833.pdf) §7.3.2, Tables 1–2, p. 9: "to use slow decay, one xIN pin is held high"]:
- IN2 low: forward, full speed;
- IN2 high: brake (both low-side switches on, slow decay);
- IN2 PWM at duty d: forward at about (1 − d) of full speed, with slow-decay current recirculation.

So one channel gives forward, speed and brake.
- **Safe at power-up.** IN2 has a pull-up, so a channel that is not yet driven reads "brake".
  All DRV8833 nSLEEP pins share one line with a pull-down: every bridge is off until the firmware
  has configured the PCA9685 and raises nSLEEP.
- **The kill line.** The PCA9685's output-enable pin is on a GPIO. With the pull-ups, OE high is
  "brake everything" at once, without I²C. The firmware's fault handler and the power-fail handler
  use it.
- **PWM whine.** The PCA9685's PWM runs at 24–1526 Hz [S: [PCA9685 Rev. 4](https://www.nxp.com/docs/en/data-sheet/PCA9685.pdf), §1–2, p. 1–2], which is audible. So:
  - motors that need no speed trim use the PCA9685 only as on (0 %) or brake (100 %), with no PWM;
  - **E2's walk**, the one motor whose speed is trimmed (`docs/e2-design.md` §11.8), takes its IN2
    from a native LEDC pin at ≥ 20 kHz [E: above hearing], one GPIO (24 in the pin plan). The ESP32-S3
    has 8 LEDC channels [S: ESP32-S3 datasheet, Features p. 4].
  - A soft start, if the noise test wants one, can be a few PWM steps over 0.1 s, too short to hear
    as a tone.
- **To confirm on the bench prototype** (local phase): the walk motor's speed under slow-decay PWM,
  and whether on/brake without PWM is quiet enough for the others. That is part of the D3 noise test.

**Bridges:** DRV8833 duals, 2 motors each: **5 boards** for 9 motors plus a spare channel
(BOM says 4; §13).

### 3.5 Inputs

All sensors are switches: DRV5032 Hall switches (open drain), microswitches, and the two optos
with a pull-up. They are read by MCP23017 expanders with interrupt outputs (INTA/INTB, mirrorable, open-drain option; 400 kHz I²C at 3.3 V) [S: [MCP23017 DS20001952C](https://ww1.microchip.com/downloads/en/devicedoc/20001952c.pdf), p. 1 and Table 1-3].

**Count [E: from the module docs].**

| Module | Inputs | v1 | v2 |
|---|---|---|---|
| M1 cassette (M1 and M1b) | quarters, hour (M1b index), noon, M1 index, gilt witness, silver witness (`docs/m1-design.md` §9.4) | 6 | 6 |
| M2 | index, Moon-tube witness, E6 home, E6 stop-lever opto, 1 March opto (`docs/m2-design.md` §8) | 5 | 7 (+ node witness, year-end trigger) |
| E2 | state index, hour-snail witness, bell-station Hall, walk lock, quarter lock, hour lock, E1 cue, quarter-rack home opto, hour-rack home opto (`docs/e2-design.md` §3, §11; §12 on PR #21) | 9 | 9 |
| E1 | bell lock, hourglass lock | 2 | 2 |
| E3 | lock, cue (figures 4, 8, 12) | 2 | 2 |
| E4 | lock | 1 | 1 |
| M5 | index, Earth-arm witness | 2 | 2 |
| M6 | index, globe witness | 2 | 2 |
| M7 | carousel witness | 1 | 1 |
| M3 (v1.5) | index, two witnesses (architecture §6) | — | 3 |
| M4 / E5 (v2) | E5 lock | — | 1 |
| Case | door switch | 1 | 1 |
| **Total** | | **31** | **37** |

- E2 part 2b and E1, E3, E4 are not designed yet, so their counts may grow. **Three MCP23017
  give 48 inputs**: 11 to spare at v2. Two (BOM Batch 2) would leave 1 in v1 and too few in v2.
- **Which DRV5032:** the **FC** variant: omnipolar (either magnet face works), open drain, 20 Hz
  sampling, 1.65–5.5 V [S: [DRV5032 SLVSDC7H](https://www.ti.com/lit/ds/symlink/drv5032.pdf), Table 4-1, p. 2]. BOM to
  name it (§13). Its 20 Hz sampling means an edge is seen up to 50 ms late [D: 1/20 Hz]. That is
  0.04 µsteps in normal running, but 160 µsteps at catch-up speed [D: 0.05 s × 3200 µsteps/s], so
  index checks are made only in normal running (§6.3). The 80 Hz DG variant is push-pull, so it
  cannot share the open-drain wiring.
- **Power-fail** goes to a native GPIO with an interrupt (§3.7), not to an expander.
- **Wiring is a star.** Every sensor wire runs home to the controller in its module's cable. No
  I²C leaves the controller: an I²C bus 2–3 m long through a case beside stepper cables is a
  known source of faults. Inputs have a pull-up on the carrier and an RC filter; the firmware
  debounces (§7.2).
- **Opto LEDs.** The two optos (TCST1202, reflective) draw ≈ 20 mA each [D: `docs/m2-design.md`
  §6]. They can be switched on only while read, from a spare PCA9685 channel. That is optional.

### 3.6 RTC and storage (F3)

| Option | Accuracy | For | Against |
|---|---|---|---|
| **A. RV-3028-C7 + supercapacitor** (recommended) | ±1 ppm at 25 °C, factory calibrated; **not temperature compensated**: −0.035 × (T − 25)² ppm, so −0.9 ppm at 20 °C and −1.7 ppm at 18 °C [D]; first-year ageing ±3 ppm [S: [RV-3028-C7 datasheet](https://www.microcrystal.com/fileadmin/Media/Products/RTC/Datasheet/RV-3028-C7.pdf)] | An offset register in 0.95 ppm steps that the firmware can trim from NTP [S: [application manual](https://www.microcrystal.com/fileadmin/Media/Products/RTC/App.Manual/RV-3028-C7_App-Manual.pdf) §4.15]; very low backup current, so a supercapacitor lasts through long outages with nothing to replace; trickle charger built in | Fewer ready-made breakouts ⚠ (BOM: Mouser FR / Melopero) |
| B. DS3231 module | ±2 ppm, 0–40 °C, temperature compensated [Sn: architecture §9; the datasheet could not be opened in this session] | Cheap, common (Gotronic GT584) | A CR2032 to replace; the module's charging diode must be removed with a non-rechargeable cell [Sn, D3] |

**Recommendation: A, by a small margin.** The room is climate controlled, so the RV-3028's
missing temperature compensation costs under 2 ppm between 18 and 28 °C [D: 0.035 × 7²], and the
firmware trims its ageing out from NTP each month. Its supercapacitor never needs replacing. B is a
good fallback. With NTP the RTC matters only through outages and network loss: a week without NTP
at ±2 ppm is ±1.2 s [D: 2e-6 × 604 800 s].

**FRAM.** MB85RC256V class (32 KB, I²C, 1 MHz, 2.7–5.5 V) [S: [MB85RC256V datasheet](https://www.ramxeed.com/assets/images/products/datasheet/FeRAM/i3/MB85RC256V-DS11v3-E.pdf), p. 1], on a breakout (Adafruit #1895 class ⚠). The
architecture's endurance check stands: one write per second for 50 years is 1.6 × 10⁹ writes per
byte [D, architecture §8], against an endurance of 10¹² writes per byte [S: same, p. 1].

### 3.7 Power (F5)

**Loads [E].**

| Load | Running | Peak | Method |
|---|---|---|---|
| 7 steppers at 0.5 A run current | ≈ 7 W | ≈ 10 W during catch-up | [E] 2 phases × (0.5 A)² × ≈ 1.5 Ω winding ⚠ ×7, plus driver losses; ±50 %. Measured on the rig |
| Event motors, 6 V | 0 | ≈ 4 running at once on the hour (E2 walk, quarters, E1 bell, hourglass): ≈ 10 W running, ≈ 30 W at stall | [E] Pololu HP 6 V micro gearmotors, stall ≈ 1.5 A each [Sn] ⚠ |
| ESP32-S3 with Wi-Fi, expanders, sensors, optos | ≈ 1.5 W | ≈ 2.5 W | [E] |
| **Total** | **≈ 9 W** | **≈ 45 W** | |

- **PSU: the Mean Well LRS-100-24** from Batch 1 (24 V, 4.5 A, 108 W [S: [LRS-100 spec](https://www.meanwell.com/Upload/PDF/LRS-100/LRS-100-SPEC.PDF), p. 1]) covers the peak twice over.
- **Energy in use:** ≈ 9 W all year is ≈ 80 kWh [D: 9 W × 8766 h]. Reducing the steppers' current
  between steps (TMC2209 IHOLD) can cut most of the stepper share; the rig measures it.
- **Two buck converters (F5):**
  - 24 → 5 V, ≥ 2 A: the DevKit (its own 3.3 V regulator), sensors, expanders;
  - 24 → 6 V, ≥ 5 A: the event motors, through the DRV8833s (VM 2.7–10.8 V [S: [DRV8833 SLVSAR1E](https://www.ti.com/lit/ds/symlink/drv8833.pdf), p. 1]).
  - The alternative is the architecture's single 5 V rail for both. It costs the motors about
    1/6 of their speed [D: 5 V / 6 V] and puts motor noise on the logic rail. Separate rails are
    recommended.
- **Power-fail detection.** A divider and comparator on the 24 V rail, threshold ≈ 20 V, to a
  GPIO interrupt.
- **Hold-up.** On power-fail the firmware brakes the event motors, finishes the steppers' phase
  handling (§9.4) and writes FRAM.
  - The PSU's own hold-up is 55 ms at 230 V AC and full load [S: LRS-100 spec, p. 1]; longer at our ≈ 9 W [E].
  - With the architecture's method (step each motor forward to its phase zero, up to 63 µsteps)
    at 1600 µsteps/s that takes ≤ 40 ms [D: 63 / 1600]. At ≈ 8 W, letting 24 V fall to 16 V needs
    C = 2 × 8 W × 0.04 s / (24² − 16²) = **2.0 mF** [D], e.g. 2 × 2200 µF, 35 V.
  - With method B (§9.4, the datasheet's own method) only the FRAM write must fit: ≈ 470 µF is
    ample [E].
  - The PSU's hold-up alone (55 ms) may cover either method; the carrier keeps footprints for both.

## 4. Connectors and wiring per module

Architecture §11: one keyed, locking connector per module. **Recommendation: Molex Micro-Fit 3.0
dual-row** (or JST-VH/XH where the pin count is small). Micro-Fit takes a stepper's current
easily and comes in 2–24 pins ⚠ (rating to check against the part chosen).

| Module | Pins [E] | Contents |
|---|---|---|
| M1 (M1 + M1b) | 16 | 2 steppers (8), 6 Hall signals, 3.3 V, GND |
| M2 | 14 (v1.5: 16) | stepper (4), E6 motor (2), 5 sensor signals, opto LED supply, 3.3 V, GND |
| E2 | 24 | state stepper (4), 3 gearmotors (6), 9 signals, opto LED supply, 3.3 V, GND, 2 spare |
| E1 | 8 | 2 gearmotors (4), 2 locks, 3.3 V, GND |
| E3 + E4 | 10 | 2 gearmotors (4), 3 signals, 3.3 V, GND, 1 spare (speaker pair if D8's fallback is used: +2) |
| M5 | 8 | stepper (4), 2 signals, 3.3 V, GND |
| M6 | 8 | stepper (4), 2 signals, 3.3 V, GND |
| M7 | 4 | 1 signal, 3.3 V, GND, 1 spare |
| M3 (v1.5) | 10 | stepper (4), 3 signals, 3.3 V, GND, 1 spare |
| M4 / E5 (v2) | 6 | gearmotor (2), 1 lock, 3.3 V, GND, 1 spare |

- **Cables:** the stepper pairs twisted, in their own sleeve; sensor wires in another. Both meet
  at the module's connector. The riser runs up the staircase tower to the controller in the left
  tower (architecture §11).
- **E3 and E4 share one connector** because the rooster sits on the tower top beside the
  procession's stage; this is a proposal for the E3/E4 design (§13).
- At the controller every module has the **same connector type and its own keying**, so a cable
  cannot go into the wrong socket.

## 5. Firmware structure: tasks and timing

### 5.1 Layers

```
firmware/
  core/        plain C++17, no Arduino headers: time law, summer time, quiet hours, the step
               follower, event state machines, the show sequencer, catch-up, persistence records,
               faults. Built for the ESP32 and for the host.
  hal/         interfaces the core calls: Clock, Steppers, Motors, Inputs, Store, Log
  board/       ESP32-S3 implementations of hal/ (TMC2209, PCA9685, MCP23017, RV-3028, FRAM, Wi-Fi)
  clock/       the Arduino sketch (clock.ino): wiring and tasks only
  spec_gen/    a header generated from spec/clock.yaml (rates, sensors, windows, timings)
  tests/       host unit tests of core/ (§12)
  test_rig/    the existing rig sketch, unchanged
```

- **The core never reads the hardware.** It receives inputs and the time, and returns commands.
  That is what makes it testable on the host and usable by the simulator.
- **`spec_gen/`** carries a hash of `spec/clock.yaml`. The firmware reports it over MQTT, and the
  simulator checks it, so the two cannot drift apart (P5).

### 5.2 Tasks

FreeRTOS, as the Arduino-ESP32 core provides. The clock runs on core 1, the network on core 0.

| Task | Core | Priority | Period / trigger | Job |
|---|---|---|---|---|
| Step ISR | 1 | hardware timer | 20 kHz (50 µs) | Issues STEP pulses (§6). Runs from IRAM, so flash writes (OTA) cannot stall it |
| Power-fail ISR | 1 | interrupt | 24 V comparator edge | Kill line for event motors, then wakes the shutdown task |
| Shutdown | 1 | highest | on power-fail | Phase handling, FRAM write, drivers off (§9.4) |
| Motion | 1 | high | 1 kHz | Computes each stepper's target from the time; sets each axis's speed for the ISR |
| Events | 1 | high | 1 kHz, and woken by expander interrupts | Debounces inputs; runs the event-motor state machines and the show sequencer (§7) |
| Time | 1 | medium | 1 Hz | Keeps UTC from the monotonic timer; disciplines it from NTP; reads and sets the RTC (§8.1) |
| Persist | 1 | medium | 1 Hz, and on state changes | Writes the FRAM record (§9.4) |
| Supervisor | 1 | low | 1 Hz | Index and witness checks, driver status, faults, the watchdog |
| Network | 0 | normal | — | Wi-Fi, SNTP, MQTT, the web page, OTA (§10) |

**Timing budget [E].**
- The ISR does a few comparisons per axis: ≈ 1–2 µs per call, so 2–4 % of one core at 20 kHz.
  Measured on the bench prototype.
- 20 kHz gives up to 10 kHz of steps per axis (one tick high, one low), three times the catch-up
  rate of 3200 µsteps/s [D: 60 rpm × 3200 µsteps/rev / 60 s, architecture §8].
- Step latency in normal running is ≤ 1 ms (the motion task's period). Against the 1.125 s step
  interval it is invisible.

## 6. The step scheduler (clockwork steppers)

### 6.1 One law for every stepper (P1)

Every module stepper turns its motor at 1 rev/h: 3200 µsteps/h, one µstep every 1.125 s
(architecture §3). The law is the same for all of them:

```
target_k(t) = P_k + floor( (τ_k(t) − τ_ref) × 3200 / 3600 s )   µsteps
```

- `τ_k(t)` is the module's **own time**, in integer microseconds:
  - **mean-time modules** (M1, M2, M3, M5, M6): τ = UTC + 1860 s. That is Strasbourg mean time,
    UT + 31.00 min (D2) [D: 7.7506° × 240 s/° = 1860.1 s, `docs/reference-notes.md` §Location].
    UT1 − UTC is below 0.9 s and is ignored (architecture §9).
  - **legal-time modules** (M1b, E2 state): τ = UTC + 3600 s + 3600 s × J(t), where J counts the
    hours added by summer-time changes since the epoch: +1 in spring, **+23 in autumn** (D14).
    So legal modules run 24 h ahead per year, which their 12 h and 24 h trains cannot see.
- `τ_ref` is a fixed epoch (2026-01-01 00:00 UTC). `P_k` is the module's calibration: the µstep
  count at which its index fires, from homing (§9.2).
- **Integers only.** 100 years is 3.2 × 10¹⁵ µs; × 3200 is 1.0 × 10¹⁹, which overflows int64
  [D]. So the law is computed as `q = Δτ / 9 000 000 µs` and `r = Δτ mod 9 000 000`, giving
  `8q + floor(8r / 9 000 000)` [D: 3200/3600 = 8/9 µsteps per second]. There is no
  floating-point drift over any span.
- **One µstep per 1.125 s is exact** for every module, because every motor reduction is an
  integer (1:1 or 24:1, `spec/clock.yaml` `motor.reduction`).

### 6.2 The follower

Each axis follows its target, forward only:
- `error = target − position`.
- `error ≤ 0`: the axis **waits** (it never reverses; architecture §8).
- `error = 1` in normal running: one step, at once.
- `error > 1`: a trapezoidal move. Accelerate at `a_max`, cruise at `v_catch` (3200 µsteps/s,
  60 rpm), decelerate to land on the target. Since the target keeps moving at 0.89 µsteps/s, the
  follower re-plans every millisecond.
- **Catch-up is the same code** as normal running: after a power cut, a summer-time change or a
  homing run, the error is simply large.
- `a_max` and `v_catch` per module are set on the rig. A 24:1 module turns its input arbor at
  2.5 rpm at catch-up speed [D: 60 / 24], gently enough for every train.
- **Simultaneous catch-up.** All axes catch up at once. Peak stepper power is ≈ 10 W (§3.7).

### 6.3 Index checks

At each index edge the supervisor compares the position with the expected one:
`e = position − (P_k + n × N_rev_k)`, where `N_rev_k` is µsteps per input-arbor turn:
- 3200 for M1, M1b and E2 state (1 rev/h);
- 76 800 for M2, M3, M5 and M6 (1 rev/day) [D: 24 × 3200].

- Checks run only in normal running: at catch-up speed the Hall's 20 Hz sampling blurs the edge by
  up to 160 µsteps (§3.5).
- |e| above a tolerance (initially ±16 µsteps, 18 s of time [E: to set from the rig's index
  repeatability]) is a **missed-step fault** (§9.5).
- A slow, steady drift of e without a step-count error means the magnet or sensor has moved:
  logged, not acted on.

### 6.4 Witness checks

A witness sits after a slip clutch or a long train (architecture §6). Its expected passes follow
from the train's exact ratio in `spec/clock.yaml`: a witness on an output with ratio p/q fires
every 76 800 × q/p µsteps of a daily arbor. That is a rational number, kept exact by the
generated table. The supervisor logs each pass time and its offset from the expected one. It
checks the clock; it never drives it.

## 7. The event motors and the show chain

### 7.1 One state machine per event motor

Each event motor is a striking train: released, it runs until its lock switch closes again.

```
IDLE ──release──▶ LEAVING ──lock opens──▶ RUNNING ──lock closes──▶ BRAKING ──▶ IDLE
                     │ t > t_leave              │ t > t_run_max
                     ▼                          ▼
                FAULT_STUCK                FAULT_TIMEOUT
```

- **LEAVING:** the motor starts (soft start); the lock switch must open within `t_leave`.
  Otherwise the motor is jammed or the switch is stuck.
- **RUNNING:** the lock must close within `t_run_max`. A close earlier than `t_run_min` is logged
  as a warning (a lost part, a bouncing switch).
- **BRAKING:** brake (IN2 high) for a fixed time, then release.
- **Times come from each module's design.** For example E2's walk, phase A ≈ 8.7 s and phase B
  ≈ 13.8 s [D: `docs/e2-design.md` §11.3]. The firmware sets `t_run_max` at 2 × the nominal time
  [E] and learns the real time (a running mean) so the sequencer's lead times adapt.
- **Multi-stop trains.** E2's walk stops twice per program turn (at 138.75° and 360°). Its state
  machine knows which phase it is in, and FRAM records it.
- **E2's counting trains** (quarters, hours) stop on two conditions: the rack's home opto is
  blocked (the count is gathered), and then the lock switch closes (`docs/e2-design.md` §12.1,
  PR #21). The state machine waits for the opto first, so the lock's closings during the count
  pass through.
- **E6** is a variant (§7.4).

### 7.2 Inputs and debouncing

- Expander interrupts wake the events task. It reads the chip (≈ 0.1 ms at 400 kHz I²C [E]) and
  timestamps the change.
- A switch must hold its new state for 5 ms [E: microswitch bounce; set on the rig] before it
  counts. Halls need no debounce but get the same filter.
- **The worst-case stop latency** is debounce + I²C read + PCA9685 write ≈ 6 ms [E]. At E2's
  program speed (16°/s) that is 0.1° of the program [D]. Each lock notch is 16° flat
  (`docs/e2-design.md` §11.3), so the margin is large. If a module needs less, its lock can move
  to a native GPIO.

### 7.3 The show sequencer (DA's order)

**Release windows (rule 4).** Each show has a release flag on the time train: the quarters, hour
and noon Halls on M1b (`docs/m1-design.md` §9.4), the midnight index on M2. The controller starts
a show at the exact second on its own clock, and only if that flag's window is open. A show whose
window is not open is skipped and reported: the cam, not the controller, decides *when*.

**The chain on the hour, at noon (the longest).** Times are from the module docs; TBD where those
modules are not designed yet.

| t (s) [D/E] | Step | Starts when | Source |
|---|---|---|---|
| −8.7 | **E2 walk, phase A** (the stops change over, the age walks out) | the quarter is due in 8.7 s (learned, §7.1) and the quarter window is open | `docs/e2-design.md` §11.3 |
| 0 | **E2 quarter train** (4 pairs at :00) | the quarter instant, and the walk has locked at 138.75° | D14; e2 §4.2 |
| 0 … ≈ 10 | **E1 bell genie**, one stroke per cue | each closing of E2's cue switch | architecture §4; e2 §4.2 |
| ≈ 10 | **E1 hourglass** (half turn) | E2's quarter train locks, at the hour only | DA p. 51 |
| ≈ 10 | **E2 walk, phase B** (the age walks on) | E2's quarter train locks | e2 §11.3 |
| ≈ 24 | **E2 hour train** (Death, 12 strokes) | the walk locks at 360°, and the hourglass has locked | architecture §5; Paul, 6 Nov 2026 |
| TBD | **E3 procession** | Death's train locks, and the noon window is open | DA p. 58–59 |
| TBD | **E4 rooster**, one crow per cue | each E3 cue (figures 4, 8, 12) | D15; architecture §4 |

- **At :15, :30 and :45** the chain stops after phase B.
- **Why Death also waits for the hourglass:** DA has the glass turn "un instant avant que la Mort
  ne sonne les heures" [S: DA p. 51]. The hourglass is short, so in practice Death starts when the
  walk ends, as Paul observed. If the hourglass runs long, Death waits for it.
- **The cue to the genie needs a short latency.** The age strikes ≈ 1 s after the genie
  (`docs/e2-design.md` §2), so E1's bell must strike well within that after its cue. That is an
  E1 design target (§13).
- **A coincidence that cannot happen:** E6 runs at mean midnight, 23:29 CET or 00:29 CEST. That is
  never on a quarter of legal time [D: 29 min is not a multiple of 15]. The sequencer still
  queues events rather than assuming it.
- **The sequencer is data-driven.** Each step is a row: which motor, what starts it, what it waits
  for. Changing the order is a configuration change and a test, not new code.

### 7.4 E6, the calendar advance

From `docs/m2-design.md` §6:
1. The M2 index (mean midnight) releases E6.
2. E6's motor runs until its home Hall fires (one turn, one division).
3. The firmware reads the stop-lever opto. **Beam clear** (the lever held back) means step again.
   **Beam blocked** means rest: the night is done.
4. **A night is capped at 4 divisions** in firmware. A fifth request is a fault.
5. Expected counts: 1 on ordinary nights; 4 into 1 January in a common year, 3 in a leap year
   (`docs/m2-design.md` §6). The simulator checks the count every night (§11.4).
- E6 is **stateful**: it always runs, in quiet hours, during catch-up (once per mean midnight
  passed) and after a fault is cleared.

### 7.5 Shows that must not run, and the E2 resync

| Situation | Sound shows | E2 walk | E6 | E5 (v2) |
|---|---|---|---|---|
| Quiet hours (§8.3) | skipped, per show class | skipped | runs | runs |
| Catch-up, summer-time change | skipped | resync after | runs per midnight | runs; catch-up pauses until it locks |
| Show fault | the faulted show is off until acknowledged | — | — | — |
| Door open (F8) | skipped | skipped | runs | runs |

**E2 resync (P2).** The next age waits in view between shows (`docs/e2-design.md` §3). After
skipped shows the wrong age would be waiting, so the controller runs the walk train alone:
- at the end of quiet hours, and after catch-up, a minute before the next quarter;
- as many program turns as there are skipped ages, modulo 4;
- without strikes.

**E2's racks after a silent walk.** If the walk runs without a show, a rack it releases stays
down on its snail. The snails are ramped, so nothing jams, and the next show strikes the count due
then (`docs/e2-design.md` §12, PR #21). The firmware does nothing special.

The firmware knows how many: it records in FRAM which age the ring holds at the waiting
position, and the bell-station Hall confirms each age's arrival. One question is open for E2
part 2b: how the firmware finds the ring's age if FRAM is lost (§13).

## 8. Time: NTP, RTC, summer time, quiet hours

### 8.1 The time base

- **The clock's time** is UTC, from the ESP32's monotonic microsecond timer, disciplined:
  `UTC = UTC_sync + (mono − mono_sync) × (1 + k)`. k is the timer's frequency error, learned
  from successive NTP syncs.
- **NTP** (SNTP, every hour [E]). An NTP offset under 2 s is **slewed**: k is nudged so UTC
  converges over minutes, never jumping. The steppers see a smooth time.
- **Larger offsets:**
  - forward, up to 10 min: applied; the steppers catch up;
  - backward: applied, and the steppers wait (never reverse);
  - over 10 min either way: not applied until confirmed from Home Assistant or the web page
    (architecture §8).
- **The RTC** is read at boot. It is set from NTP once a day, and its drift is logged.
- **Boot with no NTP and an invalid RTC** (oscillator-stop flag set): the steppers do not move
  until a time is confirmed. The clock reports it and waits.

### 8.2 Summer time

- **Rule:** EU, the last Sunday of March and of October at 01:00 GMT, i.e. UTC [S: [Directive 2000/84/EC](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32000L0084), Arts. 2–3]. It is a firmware
  function, not the C library's time zone, so the host tests cover it and J (§6.1) is exact.
- **It is a setting.** If the EU abolishes the changes, a setting stops J from changing, and the
  legal modules stay where they are.
- **The change.** At 01:00 UTC J increases by 1 (spring) or 23 (autumn). M1b's and E2's targets
  jump by 3200 or 73 600 µsteps, run at catch-up speed in ≈ 1 s or ≈ 23 s [D: 73 600 / 3200].
  The shows they pass are suppressed (D14). Then the E2 resync runs (§7.5).
- **The show at the change.** At 01:00 UTC legal time becomes 03:00 CEST (spring) or 02:00 CET
  (autumn). The jump runs first, then that hour's show, ≈ 23 s late on the autumn night. It falls
  in quiet hours anyway.
- **The mean-time modules never change.**

### 8.3 Quiet hours (D10)

- **In legal time**, the house's time (D14).
- **Per show class:** the ages and the bell genie; the hourglass; Death; the noon show (it never
  falls in a night window, but the setting exists); the rooster.
- **The faithful minimum** is the ages silenced at night while Death strikes day and night
  [S: DA p. 58, 65].
- **E2 goes silent as a whole.** E2's racks are released by its walk train (Paul, PR #21,
  8 Nov 2026, as reported by the E2 session; `docs/e2-design.md` §12). With the walk stopped at night,
  nothing releases Death's rack, so **Death cannot strike while the ages are silent**. The
  E2 classes (the ages and genie, Death) are therefore one setting. Paul: "I'm okay with Death not
  striking during the quiet time at night". The faithful minimum above is not available.
- **The default** is F6: 22:00–07:00, E2 silent.
- **From Home Assistant:** the window, the classes, and a "quiet now" switch until the next
  morning.

## 9. Setting, homing, catch-up and faults

### 9.1 Commissioning (architecture §7)

1. The simulator writes the **setting sheet** for an instant T_set a few minutes ahead (§11.5):
   each output's angle and its dial mark.
2. The firmware is put in **setting mode**. Each stepper homes (§9.2), then holds.
3. Paul sets each output by hand, forward only, to the sheet: the hands, the globes, the cams'
   dog clutches, the calendar ring, the E2 ring's waiting age.
4. At T_set the firmware leaves setting mode. Every axis now follows its law. It writes FRAM.

### 9.2 Homing

- A forward-only train is homed by **running forward to its index**: at most one input-arbor
  turn, ≤ 1 s for a 1 rev/h module and ≤ 24 s for a daily one at catch-up speed [D: 3200 and
  76 800 µsteps at 3200 µsteps/s].
- The index fires at a known module time (for example M1 at :00 mean time), so the position at
  the edge is known absolutely. `P_k` (§6.1) is fixed by it, and the axis then runs on to its
  target. No hand setting is needed for any input arbor.
- **After service.** A module taken out shows open load (§3.3). The firmware stops that axis.
  When it comes back, the axis re-homes and catches up. The outputs past the keyed couplings keep
  their phase (P4).

### 9.3 Catch-up after a power cut (architecture §8)

On power-up:
1. Read the RTC, and the FRAM record (§9.4).
2. Restore each driver's microstep phase (§9.4).
3. Compute J and every target; the axes catch up together (§6.2).
4. E6 runs at each M2 index passed (one per mean midnight), as the M2 axis passes them.
5. E5 (v2) runs when its trigger passes; catch-up pauses until it locks.
6. Sound shows are suppressed. Then the E2 resync runs.
7. Each axis checks its next index pass.

- **Times [D, architecture §8]:** 1 day out is caught up in ≈ 24 s, 30 days in ≈ 12 min.
- **Over 60 days** [E: architecture §8] the firmware asks for confirmation first.

### 9.4 Persistence and the motor phase

**The FRAM record** (written each second and on every change of state):
- per axis: position (int64), `P_k`, the driver's microstep phase;
- J, the summer-time count;
- each event motor's state (E2's walk phase, E6's divisions tonight, E5's progress);
- the E2 ring's waiting age;
- quiet-hour and show settings, fault flags;
- a sequence number and a CRC-32.

Two records alternate. The newer one with a valid CRC wins, so a write cut by power loss can never
corrupt the state.

**The motor phase.** A TMC2209 powers up at its own initial phase, so a motor de-energised
elsewhere can jump up to ±2 full steps when power returns: 0.15° at a daily arbor, or 36 s of time
[D: architecture §8]. Two methods:

| Method | How | For | Against |
|---|---|---|---|
| A. Step to phase zero on power-fail (architecture §8) | On power-fail each motor steps forward, ≤ 63 µsteps, until its phase is the power-up phase (read as `MSCNT`); then FRAM is written | Uses only documented behaviour | Needs ≈ 2 mF of hold-up (§3.7); leaves each axis up to 63 µsteps (71 s) ahead, so it waits after power-up |
| B. Restore the phase at power-up | At power-up, with ENN high (bridges off), pulse each driver's STEP until its `MSCNT` equals the stored value, then enable | **This is the datasheet's own method**: "Apply a number of steps to restore MSCNT to the stored value prior to enabling the motor driver"; `MSCNT` is 0 after power-up [S: [TMC2209 datasheet Rev 1.08](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/696/TMC2209_Rev.1.08.pdf), §3.6.1, p. 15–16, "Methods for position recovery"]. No hold-up beyond the FRAM write; no lead | Documented for the ENN pin only, not for TOFF = 0, so all drivers share EN and are restored together. Confirm on the rig |

**Recommendation (F4): B**, confirmed on the rig. The FRAM record then carries each driver's
`MSCNT` as read in the last second. The carrier keeps a footprint for A's capacitors as a
fallback. The PSU's own 55 ms hold-up (§3.7) already exceeds A's ≈ 40 ms, so even A may need no
extra capacitance; the rig measures it.

### 9.5 Faults

| Class | Examples | What the firmware does |
|---|---|---|
| Axis | missed steps at the index; driver over-temperature or short; open load | Stops that axis (a short or open load) or only reports (missed steps; the axis keeps following its law). Re-homes when cleared |
| Show | a lock that never opens or closes; a release window not open at the due time; E6 asking for a fifth division | Brakes the motor (kill line if needed); turns that show off until acknowledged (F8); the rest of the chain goes on where it can: Death still strikes if the ages fault. **Timekeeping never stops for a show fault** |
| Time | NTP lost; RTC invalid; a large time jump | NTP lost: keep running on the RTC and warn. RTC invalid and no NTP: hold the steppers (§8.1). Large jump: wait for confirmation |
| Power | power-fail; brown-out reset | §9.4; a reset is treated as a power cut |
| Software | task watchdog | Reset, then as a power cut. Every reset's cause is logged in FRAM |

Each fault has an ID, a time, a count, and an MQTT message. The status LED shows the worst
active fault.

## 10. Network: MQTT, Home Assistant, OTA

- **MQTT with Home Assistant's discovery**, to Paul's broker. Entities:
  - sensors: each axis's error at its last index, witness offsets, the NTP offset, RTC drift,
    24 V, uptime, the spec hash (§5.1), the firmware version;
  - binary sensors: each fault class, the door;
  - settings: quiet-hour start and end, show classes on or off, "quiet now";
  - buttons: acknowledge faults, confirm a time jump, run a show now (test; refused in quiet hours
    and during catch-up), E2 resync, reboot.
- **A small web page** on the controller shows the same, for use without Home Assistant.
- **OTA over Wi-Fi**, with two app slots and roll-back if the new firmware does not report healthy
  within a minute.
  - Allowed only when no show is due in the next 5 min [E].
  - The steppers keep running during the download. The step ISR runs from IRAM, so flash writes do
    not stop it.
  - The reboot is a short power cut: FRAM first, then catch-up of a few seconds.
- **Secrets stay out of the repository:** Wi-Fi, MQTT and OTA passwords live in a git-ignored
  `secrets.h`, or are entered once on the web page.
- **Without a network the clock runs normally** on its RTC. Only the network features stop.

## 11. The simulator and its validation

### 11.1 What it is

A Python package in `sim/`. It does not simulate 1.125 s steps for decades. Because the law is
closed-form (P1), every output's angle at any instant follows directly from time:

```
angle_out(t) = phase_out + 360° × (target_k(t) / N_rev_k) × ratio_train
```

- **target_k(t)** is the firmware's own law (§6.1), including J and the mean-time offset.
- **ratio_train** is the exact `Fraction` from `spec/clock.yaml`, read through `tools/ratios`
  (its spec loader and train evaluation). The simulator adds no ratio of its own.
- **phase_out** is the output's phase at T_set, from the setting sheet (§11.5).
- **The events** are a discrete-event simulation: the release windows, the chain (§7.3) with
  nominal durations from the module docs, quiet hours, summer-time changes, power cuts.
- **Accelerated time:** a century of daily samples is 36 525 evaluations, seconds of CPU.

### 11.2 The reference: Skyfield with a JPL kernel

- **Skyfield 1.55** [S: [PyPI](https://pypi.org/project/skyfield/), released 7 Aug 2026]. It installs in the cloud session (checked). It has `find_risings`/`find_settings`, `moon_phases`, `eclipselib.lunar_eclipses` and `Time.gast` [S: [Skyfield docs](https://rhodesmill.org/skyfield/almanac.html)].
- **Kernel: DE440s**, 32 MB, covering 1849–2150 [S: [Skyfield, Planets](https://rhodesmill.org/skyfield/planets.html)]. It downloads from NAIF in the cloud session (checked)
  and is cached in `sim/.kernels/`, which is git-ignored.
- **Beyond the kernel's range** the simulator checks drift against mean elements: JPL's
  long-term Keplerian table (3000 BC–3000 AD), already in `spec/clock.yaml`.
- **Easter** is checked against the Gregorian algorithm (Meeus, *Astronomical Algorithms* ch. 8),
  cross-checked with `dateutil.easter`.

### 11.3 What v1 shows, and what that costs against the true sky

v1 shows steady (mean) motion for the Sun and Moon (D5). So two numbers matter for each check:
- **the train check:** the indication against the *mean* quantity it is built to show. This is
  what tests the design: the trains, the law, the setting.
- **the sky gap:** the indication against the *true* sky. In v1 it is mostly the equations that
  v1.5 adds. It is reported, not failed.

The sky gaps for v1, from `sim/probe_v1_deviations.py` (2026–2045, DE440s) [D]:
- equation of time: **−14.2 to +16.5 min**;
- the Moon's true minus mean longitude: **±8.0°**;
- true minus mean new moons: **−13.7 to +14.1 h**.

### 11.4 The checks and their error budgets

**The budget for a train check** is the sum of:
1. the train's ratio drift over the run, from `docs/gear-trains.md` §8 [D];
2. the quantisation: one µstep of the input arbor, carried through the train [D];
3. the model's own approximation: zero for exact ratios; for the mean-element references, their
   stated precision.

Setting error (Paul's hand on the dial) and backlash are physical; they are not in the sim. The sim
sets every output exactly at T_set from the ephemeris.

| # | Indication | Reference | Train check: accepts | Sky gap: reported | Version |
|---|---|---|---|---|---|
| 1 | Mean-time hands (I1) | UTC + 1860 s | ≤ 1 µstep: 1.125 s [D] | the 0.9 s of UT1 − UTC | v1 |
| 2 | Legal-time hands (I2), with every summer-time change 2026–2100 | Europe/Paris rule (§8.2) | ≤ 1 µstep, except during a change's catch-up run (≤ 23 s) [D] | — | v1 |
| 3 | Calendar ring: date, including 29 Feb | Python's Gregorian calendar | **exact every day, 2026–2099**. 2100 is not a leap year and needs the computus (architecture §4, v2) | — | v1 |
| 4 | E6 divisions per night | the ring's layout (m2-design §6) | **exact**: 1, or 4 / 3 into 1 January | — | v1 |
| 5 | Weekday (I11) | Python's calendar | **exact** | — | v1 |
| 6 | Sun hand (I3), mean | mean Sun = mean time | ≤ 1.125 s | equation of time, −14.2 … +16.5 min [D, §11.3] | v1 |
| 7 | Year arbor (M2.year): the Sun's mean longitude | Meeus 25.2 mean longitude | ≤ 0.012° per century + 1 µstep [D: −0.0116°/c] | the equation of centre (sim) | v1 |
| 8 | Moon hand (I4), mean | Meeus 47.1 mean longitude | ≤ 0.95° per century [D: −0.9429°/c] | ±8.0° [D, §11.3] | v1 |
| 9 | Moon-phase globe (I15) | Meeus 49.1 mean new moons; Skyfield phase | ≤ 0.95° per century [D: +0.9429°/c], i.e. ≤ 1.9 h of phase per century [D: 0.95/360 × 29.53 d] | −13.7 … +14.1 h at new moon [D, §11.3] | v1 |
| 10 | Planets (I14): Mercury to Saturn, heliocentric | JPL Table 2a mean longitudes; Skyfield heliocentric ecliptic longitudes | each train's drift per century, `gear-trains.md` (Venus +0.54°, Mars −0.67°, …) + 0.01° | each planet's equation of centre (sim) | v1 |
| 11 | Moon arm of the planetarium (M5.moon_arm) | mean elongation | ≤ 0.58° per century [D: +0.5780°/c] | as row 9 | v1 |
| 12 | Celestial globe (I16), set to Bordeaux sidereal time (D2) | Skyfield GAST + longitude −0.57° | ≤ 0.15° per century = 0.6 min of sidereal time [D: 0.1504°/c; 0.15/360 × 1436 min] | nutation in right ascension (≈ 1 s; sim) | v1 |
| 13 | Shows: every quarter, hour and noon start | the schedule (D14) and quiet hours | **exact**: at the legal second, in DA's order, none in quiet hours, none during catch-up | — | v1 |
| 14 | Catch-up: outages of 1 h, 1 day, 30 days, across New Year and across a summer-time change | the uninterrupted run | after catch-up every axis is **exact**, E6's count is **exact**, the E2 ring holds the due age | — | v1 |
| 15 | Equation of time (I3 apparent, with M3) | Skyfield apparent Sun | **TBD with M3's design**; proposed ≤ 1 min [E] | — | v1.5 |
| 16 | Moon equations (I4 true, with M3) | Skyfield apparent Moon | **TBD with M3's design**; proposed ≤ 0.5° [E] | — | v1.5 |
| 17 | Sunrise and sunset for Bordeaux (I7), 44.83° N, −0.57° (D2 (ii)) | Skyfield `find_risings` / `find_settings`, standard refraction | **TBD with the mobile horizon's design**; proposed ±3 min [E] | — | v1.5 |
| 18 | Eclipses (I5) | Skyfield `eclipselib.lunar_eclipses`; solar eclipses from the Sun–Moon separation at each new moon (Skyfield 1.55 has no solar-eclipse finder [S: its docs and source]) | **no eclipse missed**, 2026–2126; false alarms counted and reported; node cam ≤ 0.004° per century [D: +0.0038°/c] | — | v1.5 |
| 19 | Easter, dominical letter, epact (I9, I10, I12) | Meeus ch. 8; `dateutil.easter` | **exact**, 1583–4099 | — | v2 |
| 20 | Precession (I17) | IAU 2006 rate (`spec/clock.yaml`) | ≤ 0.002° per century [D: +0.0006°/c] | — | v2 |

- **Runs.** A one-year run at 6-hour steps for the fine checks; 2026–2126 at daily steps for
  drift (Skyfield inside the kernel's range, mean elements beyond).
- **Output:** a generated report, `sim/report.md`, with one table row per check: pass or fail,
  the worst value and when it occurred, and the sky gap. It is regenerated, like
  `docs/gear-trains.md`.

### 11.5 The setting sheet

For an instant T_set the simulator prints, for each output: its angle, the dial mark to set it
to, and how to set it (architecture §7). It includes the correction inputs' phase (zero in v1),
the E2 ring's waiting age, the calendar ring's division, and Bordeaux sidereal time for the globe.

### 11.6 One law in two languages

The time law and summer-time rule exist twice: in C++ (`firmware/core`) and in Python (`sim`).
They are kept equal by a test: a small host binary of the C++ core reads (module, time) pairs and
prints targets and J; pytest feeds it thousands of random and edge-case times (every summer-time
change to 2100, year ends, leap days) and compares with the Python. Any difference fails.

## 12. Test strategy and the PR plan

### 12.1 Host unit tests of the firmware core

- **Built with the system's g++** (C++17), no Arduino. A minimal test harness kept in the repo, so
  there is nothing to download.
- **Run from pytest:** `firmware/tests/test_host.py` compiles and runs them, and skips with a
  message if no compiler is found. `pytest.ini` gains `sim firmware` in `testpaths`
  (append-only); the ephemeris tests skip if Skyfield or the kernel is missing, so the existing
  `.venv` keeps passing.
- **What they cover:**

| Area | Tests |
|---|---|
| Time law | integer exactness over 100 years; one µstep per 1.125 s; no overflow; mean and legal offsets |
| Summer time | every change 2026–2100; J after +1 and +23; abolition setting |
| Follower | forward only; waits when ahead; trapezoid lands exactly; catch-up times |
| Event state machines | normal run; lock never opens; never closes; closes early; braking |
| Sequencer | the hour and noon chains in DA's order; lead time for phase A; cue to genie; a fault mid-chain; coincident events queued |
| E6 | 1, 3 and 4 divisions; the cap at 4; opto failing "blocked" stops after one step |
| Quiet hours | windows across midnight; per class; "quiet now"; E2 resync at the end |
| Catch-up | outages across midnight, New Year and summer-time changes; E6 count; E5 pause |
| Persistence | record encode and decode; CRC; a torn write falls back to the older record |
| Faults | each class; acknowledge; the show stays off |
| Time | slew under 2 s; jumps forward and back; confirmation over 10 min; RTC invalid |

- **Fake hardware.** The tests drive the core through the `hal/` interfaces with fakes: a fake
  clock that can run at any speed, fake axes, fake motors whose lock switch closes after a set
  time or never, fake inputs.

### 12.2 On the target

- `arduino-cli` builds the sketch for the ESP32-S3 in CI or in the cloud session, so a compile
  error is caught before Paul flashes it (F7).
- **Bench tests (local phase):** the D3 noise test, the event-motor PWM, the power-fail hold-up,
  method B of §9.4, the index repeatability, the step ISR's CPU load.

### 12.3 PR plan after this gate

1. **Firmware core and host tests** (`firmware/core`, `hal`, `tests`), and the sketch that wires
   it to the rig's hardware. No PCB yet.
2. **The simulator** (`sim/`), the train and event checks, the report and the setting sheet.
3. **The carrier PCB** in KiCad, after the bench prototype (F1).
4. v1.5 checks (rows 15–18) when M3 and the v1.5 M2 parts are designed.

## 13. Interface questions for other modules

The tables in `docs/architecture.md` are the contract. These need an answer or a small
change; each is listed again in the PR's "Decisions needed".

1. **BOM Batch 2 (append-only rows):** MCP23017 × 3, not 2 (§3.5); DRV8833 × 5, not 4 (§3.4);
   PCA9685 × 1; a 24 → 6 V buck (F5); RV-3028-C7 breakout (F3); FRAM; bulk capacitors (§3.7);
   Micro-Fit connector pairs (§4). Added only once the decisions are made.
2. **E2 part 2b:** how does the controller learn which age the ring holds if FRAM is lost? For
   example, a second Hall at the bell station reading a code magnet under one age only. Today the
   four magnets are alike (`docs/e2-design.md` §11.4).
3. **E2 part 2b:** answered on PR #21 (`docs/e2-design.md` §12.4): a pair every 3 s, the age 1 s
   after the cue; Death one stroke per 3 s [E: Paul to time it]. The sequencer's timeouts follow
   those.
4. **E1:** the genie's stroke must land well within ≈ 1 s of E2's cue (`docs/e2-design.md` §2),
   and E1's lock must close before the next cue (3 s later). Proposed target: stroke within
   0.5 s of the cue [E].
5. **E3/E4:** one shared connector (§4), and the procession's and rooster's durations for their
   timeouts.
6. **`spec/clock.yaml` (P5):** add `sensors:` (each sensor's module, type and window) and
   `events:` (each event motor's nominal times and lock positions), append-only, so the firmware's
   generated header and the simulator read them from one place (F9).
7. **Architecture §12** says the firmware is a PlatformIO project; F7 proposes Arduino IDE /
   `arduino-cli`. If accepted, that line changes when this merges.

## 14. Decisions (Paul, PR #19, 8 Nov 2026)

**All accepted as recommended.** F2–F10 on PR #19; F1 in chat the same day, after he asked what a
PCB involves (§3.2). They are
recorded as "D-next (firmware)" in `docs/decisions.md`; the number is given when this PR merges.

**F1. How the controller is built.**
- Options: A, a carrier PCB with sockets for plug-in modules; B, hand-wired stripboard; C, a
  printer board plus the ESP32; D, a full custom PCB (§3.2).
- **Recommendation: A**, after a bench prototype with the same modules.
- **Status: accepted: A** (Paul, chat, 8 Nov 2026: "Lets plan for your approach of you drawing the
  board in KiCad"). Hobby perfboard stays the fallback (Paul, PR #19). The bench prototype
  comes first.

**F2. Event-motor drive.**
- Options: A, one PCA9685 with one channel per motor through DRV8833s; B, the ESP32's own PWM;
  C, two PCA9685s (§3.4).
- **Recommendation: A.** It fits nine motors with seven channels spare, keeps a hardware kill
  line, and is safe at power-up. The PCA9685's PWM is audible (≤ 1.5 kHz), so it only switches
  motors on and brakes them; E2's walk, which needs its speed trimmed, gets a native PWM pin at
  ≥ 20 kHz.
- **Status: accepted** (Paul, PR #19, 8 Nov 2026).

**F3. RTC.**
- Options: A, RV-3028-C7 with a supercapacitor; B, a DS3231 module (§3.6).
- **Recommendation: A**, by a small margin: in a heated room its error is close to the DS3231's,
  the firmware trims it from NTP, and it needs no battery.
- **Status: accepted**: RV-3028-C7 (Paul, PR #19, 8 Nov 2026).

**F4. The motor phase through a power cut.**
- Options: A, step to phase zero on power-fail (≈ 2 mF, or the PSU's 55 ms hold-up); B, restore
  the phase at power-up by stepping with the bridges off, the TMC2209 datasheet's own method (§9.4).
- **Recommendation: B**, confirmed on the rig, with A's capacitor footprint kept as a fallback.
- **Status: accepted**: B, confirmed on the rig (Paul, PR #19, 8 Nov 2026).

**F5. Power rails.**
- Options: one 5 V rail for logic and event motors (architecture §11), or a separate 6 V rail for
  the motors (§3.7).
- **Recommendation: separate 6 V**, for the motors' rated speed and a quiet logic rail.
- **Status: accepted**: a separate 6 V rail (Paul, PR #19, 8 Nov 2026).

**F6. Quiet hours.**
- What window (legal time), and which shows go silent? The faithful minimum silences only the
  ages and the genie; Death strikes day and night [S: DA p. 58, 65].
- **Recommendation:** 22:00–07:00 [E: a common night], silencing the ages, the genie and Death,
  with the faithful setting one switch away in Home Assistant. Paul to choose the hours.
- **Status: accepted**: 22:00–07:00 legal time, the ages, the genie and Death silent; settable
  from Home Assistant (Paul, PR #19, 8 Nov 2026). Since PR #21 Death is silent whenever the ages
  are, so the "faithful setting" no longer exists (§8.3).

**F7. Firmware toolchain.**
- Options: Arduino IDE 2 with the Arduino-ESP32 core, and `arduino-cli` for headless builds; or
  PlatformIO (architecture §12).
- **Recommendation: Arduino IDE / `arduino-cli`.** It is Paul's tool, and the same sketch builds
  in both. The board-independent core does not depend on either.
- **Status: accepted**: Arduino IDE / `arduino-cli` (Paul, PR #19, 8 Nov 2026).

**F8. When a show faults, and the door.**
- Options for a fault: the show stays off until acknowledged, or it retries at its next time.
- Options for the door switch: an open door skips the shows (fingers near the figures), or it is
  only reported.
- **Recommendation:** off until acknowledged; an open door skips the shows (E6 and E5 still run:
  they are slow and stateful).
- **Status: accepted** (Paul, PR #19, 8 Nov 2026).

**F9. Where the sensor and event data live.**
- Options: new append-only `sensors:` and `events:` sections in `spec/clock.yaml` (P5), or a
  firmware-only configuration file.
- **Recommendation: `spec/clock.yaml`**, so the firmware, the simulator and the CAD read the same
  numbers.
- **Status: accepted** (Paul, PR #19, 8 Nov 2026). The sections are added in the firmware-core
  PR, append-only.

**F10. Approve the simulator plan and its error budgets (§11)**, including DE440s as the
reference and the v1.5 rows left TBD until M3 and the mobile horizon are designed.

**Status: accepted** (Paul, PR #19, 8 Nov 2026).
