# firmware: the controller (M0)

The ESP32-S3 controller's firmware. The design is in
[`docs/firmware-design.md`](../docs/firmware-design.md); the decisions are F1–F10 there (accepted,
PR #19).

## Layout

| Folder | What it holds |
|---|---|
| `core/` | Plain C++17, no Arduino headers. Built for the ESP32 and for the host |
| `hal/` | The interfaces the core is driven through: clock, steppers, motors, inputs, storage |
| `spec_gen/` | `spec_gen.h`, generated from `spec/clock.yaml` (P5), and its generator |
| `tests/` | Host unit tests, a minimal harness, fakes, and the cross-check with `sim/timelaw.py` |
| `test_rig/` | The Phase 2 test-rig sketch |

Still to come: `board/` (the ESP32-S3 implementations of `hal/`) and `clock/` (the sketch), with
the bench prototype.

## What `core/` does today

| File | Design section | What |
|---|---|---|
| `time_law.h` | §6.1 | Each stepper's target as an integer function of UTC: mean or legal time, J, calibration |
| `civil.h` | — | Gregorian date arithmetic, with no C-library time zone |
| `summer_time.*` | §8.2 | The EU rule, J (+1 in spring, +23 in autumn), the legal offset, a freeze setting |
| `follower.*` | §6.2 | Forward-only following: one µstep at once in normal running, trapezoidal catch-up |
| `event_motor.*` | §7.1 | One event motor: release, lock, timeouts, faults, learned run time; counting trains stop on home opto then lock |
| `e6.*` | §7.4 | E6's night: one division per turn, the stop-lever opto, the cap at four |
| `schedule.*` | §7.3, §8.3 | The quarters in legal time, Death's count, noon; quiet hours; the E2 ring's ages |
| `show_chain.*` | §7.3 | One quarter's chain in DA's order, gated by the release windows |
| `persist.*` | §9.4 | The FRAM record: fixed little-endian layout, CRC-32, two slots, torn-write safe |

## Build and test (host)

From the repository root, with the project's venv (`requirements.txt`):

```bash
.venv/bin/python -m pytest firmware
```

This compiles `core/` and `tests/` with g++ or clang++ (C++17, warnings as errors), runs the unit
tests, checks the C++ time law against `sim/timelaw.py` for thousands of instants to 2100, checks
the summer-time rule against the IANA time-zone database, and checks that `spec_gen.h` is up to
date. Without a C++ compiler those tests are skipped.

By hand:

```bash
g++ -std=c++17 -Wall -Wextra -Werror firmware/core/*.cpp firmware/tests/test_*.cpp firmware/tests/main.cpp -o /tmp/host_tests && /tmp/host_tests
```

After editing `spec/clock.yaml`:

```bash
.venv/bin/python -m firmware.spec_gen.gen_spec
```
