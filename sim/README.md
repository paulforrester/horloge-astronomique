# sim: the accelerated-time simulator

The design is `docs/firmware-design.md` §11 (accepted as F10, PR #19). The latest run is in
[`report.md`](report.md).

| File | What it holds |
|---|---|
| `timelaw.py` | The stepper time law and EU summer time: the Python copy of `firmware/core/time_law.h`, kept equal by `firmware/tests/test_host.py` |
| `model.py` | The clock: each module's axis follows the law; each output turns at its train's exact ratio from `spec/clock.yaml` (through `tools/ratios`) |
| `references.py` | Mean references (Meeus 1998; JPL rates from the spec). No dependencies |
| `ephemeris.py` | The true sky: Skyfield with JPL DE440s. Optional |
| `calendar_ring.py` | The calendar ring and E6 (`docs/m2-design.md` §6) |
| `validate.py` | The checks, their error budgets, the sky gaps, and the report |
| `sheet.py` | The setting sheet for an instant T_set (architecture §7) |
| `probe_v1_deviations.py` | The Phase 3 gate's probe of v1's sky gaps |

## Run

```bash
.venv/bin/python -m sim validate --years 100            # train checks only (about 40 s)
.venv/bin/python -m sim validate --years 100 --sky --write   # + sky gaps, rewrites report.md
.venv/bin/python -m sim sheet --at 2027-01-01T10:00:00Z --sky
.venv/bin/python -m pytest sim
```

`--sky` needs Skyfield (`requirements.txt`) and downloads DE440s (32 MB) into `sim/.kernels/`
(git-ignored), or uses `$HORLOGE_KERNELS`. Without them the sky test is skipped.

## How a check works

Each output is set exactly at T_set, as the setting sheet says. The simulator then computes,
exactly, how far the law and the train turn it, and compares that with the mean quantity the
train is built to show. The budget is the train's drift from `tools/ratios`, plus one µstep of
the input, plus the reference's own uncertainty (and ΔT for the Moon). The sky gap is v1's mean
motion against the true sky: it is reported, not failed. Most of it is what v1.5's equations add.
