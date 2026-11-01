# tools/ratios: gear-ratio engineering

The Phase 1 tool. It searches gear trains for a target period or ratio under printable
constraints, checks every train in [`spec/clock.yaml`](../../spec/clock.yaml), and generates the
tables in [`docs/gear-trains.md`](../../docs/gear-trains.md).

## What it does

| Function | Purpose |
|---|---|
| `search_compound(target, stages, ...)` | Exhaustive search of 1–3 stage compound trains. For every product of driven wheels it tries the nearest numerators that factor into driver gears, so the result is the *most accurate* train for the constraints. |
| `search_coaxial(target, tooth_sum=None, ...)` | 2-stage reverted trains (output coaxial with input), optionally with a fixed tooth sum, i.e. intermediate arbors on a given circle. |
| `search_differential(target, base, coef, stages, ...)` | Differential or epicyclic form `base + coef·X`. Near-unity targets get very accurate, because the error of X is scaled down. |
| `choose_train(target, max_drift_deg_per_century=..., ...)` | The simplest train meeting an accuracy target: fewest stages, then smallest wheels. |
| `epicyclic.schwilgue_sidereal`, `schwilgue_lunar_turns_per_year` | Schwilgué's two epicyclic and differential relations (LEF, CLEA). |

**Constraints** (all keyword arguments):
- `zmin`, `zmax`, or an explicit `allowed` set of tooth counts;
- `max_stage_ratio`;
- `module` and `max_diameter` (tip diameter limit, e.g. the bed or the module footprint);
- `coaxial`.

**Every result reports:**
- the exact ratio (`Fraction`) and relative error;
- the output-period error;
- the drift in degrees per year and per century (needs `input_period`);
- stages, tip diameters and centre distances.

## Command line

Run from the repository root.

Most accurate 3-stage trains for one turn per tropical year from a daily arbor:

```bash
python -m tools.ratios search --period 365.24219 --stages 3
```

A sidereal globe as a differential, 1 + X:

```bash
python -m tools.ratios search --ratio "1+1/365.24219" --differential 1 1 --stages 3
```

Reverted planet train with intermediate arbors on a 133-tooth-sum circle:

```bash
python -m tools.ratios search --ratio "365.24219/224.695" --coaxial --tooth-sum 133
```

Check every train in `spec/clock.yaml` (exit code 1 on any failure):

```bash
python -m tools.ratios check
```

Regenerate the tables in `docs/gear-trains.md`:

```bash
python -m tools.ratios report --write docs/gear-trains.md
```

## Tests

```bash
python -m pytest
```

| File | What it checks |
|---|---|
| `tests/test_schwilgue.py` | Reproduces Schwilgué's published ratios exactly: the year train (the year in hours), the five planet trains and CLEA factors, the synodic-month differential, the exact sidereal epicyclic, the approximate lunar train, and the five lunar-equation periods. It also shows that the search rediscovers or beats his trains under his own tooth limits. |
| `tests/test_search.py` | Constraints, coaxial trains, metrics, chooser. |
| `tests/test_spec.py` | Every train in `spec/clock.yaml` meets its constraints and accuracy target; the shared year trains are identical; `docs/gear-trains.md` is in sync. |
