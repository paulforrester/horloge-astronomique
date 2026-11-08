"""The simulator's checks and their error budgets (docs/firmware-design.md §11.3-11.4).

**Train checks** (no dependencies): each v1 indication against the *mean* quantity it is built to
show. The output is set exactly at T_set; the check then measures what the law and the train
ratio accumulate. The budget of a check is

    |train drift| × years / 100  +  one µstep of the input at the output  +  any extra term,

where the drift comes from tools/ratios (docs/gear-trains.md §8) and the extra term is ΔT's growth
for the Moon (a UT-driven clock against TT motions) and the references' own uncertainty
(REF_SUN, REF_MOON, REF_SIDEREAL).

**Sky gaps** (Skyfield + DE440s): v1's mean motion against the true sky. Reported, not failed.
"""

import datetime as dt
import random
from dataclasses import dataclass, field

from sim import calendar_ring, references as ref, timelaw
from sim.model import Clock, wrap180

DAY = 86400
US = 1_000_000
# [E] ΔT may grow by up to ~2 min per century (it grew ~1 min over the 20th century); at the
# Moon's 0.55°/h that is ≈ 0.02° per century. It is a real error of a UT-driven clock, and tiny.
EXTRA_DT_DEG_PER_CENTURY = 0.02
# The references' own uncertainty, per century of run [D]:
# - Sun: the spec's tropical-year precision, 0.0005°/c [S: spec/clock.yaml], plus the drift of
#   Meeus 25.2's T² term from a straight line over the run, 2 × 0.0003032 × 1.3 = 0.0008°/c;
#   0.0015 with rounding.
# - Moon: Meeus 47.1/47.2's T² terms, 2 × 0.0018819 × 1.3 = 0.005°/c.
# - Sidereal time: Meeus 12.4's T² term, 2 × 0.000387933 × 1.3 = 0.001°/c.
REF_SUN = 0.0015
REF_MOON = 0.005
REF_SIDEREAL = 0.001
# Floating-point slack in the references (degrees).
EPS = 1e-6


@dataclass
class Result:
    row: str
    what: str
    worst: float
    unit: str
    budget: float
    when: str = ""
    passed: bool = True
    note: str = ""
    samples: int = 0


@dataclass
class TrainCheck:
    row: str
    what: str
    train: str | None          # None: the input arbor itself (ratio 1)
    reference: callable        # unix_s -> degrees
    axis: str | None = None    # override the driving axis
    extra_deg_per_century: float = 0.0
    to_unit: tuple = ("°", 1.0)  # (unit, factor applied to degrees for display)


def _ratio_one_delta(clock: Clock, axis: str, t0_us: int, t1_us: int):
    return 360 * clock.axes[axis].input_turns(t0_us, t1_us)


def sample_times(t0: int, years: float, step_s: int, seed: int = 1) -> list[int]:
    """Regular samples plus a random second in each, and every summer-time change ±1 s."""
    rng = random.Random(seed)
    end = t0 + int(years * 365.25 * DAY)
    ts = [t0 + k * step_s + rng.randrange(step_s) for k in range((end - t0) // step_s)]
    y0 = dt.datetime.fromtimestamp(t0, dt.timezone.utc).year
    y1 = dt.datetime.fromtimestamp(end, dt.timezone.utc).year
    for y in range(y0, y1 + 1):
        for spring in (True, False):
            c = timelaw.eu_change_unix_s(y, spring)
            ts += [c - 1, c, c + 1]
    return sorted(t for t in ts if t0 <= t <= end)


def run_train_check(clock: Clock, c: TrainCheck, t0: int, times: list[int]) -> Result:
    years = (times[-1] - t0) / (365.25 * DAY)
    if c.train is None:
        drift, quantum = 0.0, 360.0 / clock.axes[c.axis].usteps_per_input_turn
    else:
        drift = abs(clock.drift_deg_per_century(c.train))
        quantum = clock.quantum_deg(c.train, c.axis)
    budget = (drift + c.extra_deg_per_century) * years / 100 + quantum + EPS
    r0 = c.reference(t0)
    worst, worst_t = 0.0, t0
    for t in times:
        if c.train is None:
            d = _ratio_one_delta(clock, c.axis, t0 * US, t * US)
        else:
            d = clock.delta_deg(c.train, t0 * US, t * US, c.axis)
        err = wrap180(float(d % 360) - (c.reference(t) - r0))
        if abs(err) > abs(worst):
            worst, worst_t = err, t
    unit, k = c.to_unit
    when = dt.datetime.fromtimestamp(worst_t, dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    return Result(c.row, c.what, worst * k, unit, budget * k, when, abs(worst) <= budget,
                  f"drift {drift:.4f}°/century; 1 µstep = {quantum:.2e}°"
                  + (f"; reference ±{c.extra_deg_per_century:g}°/century" if c.extra_deg_per_century else ""),
                  len(times))


def train_checks(clock: Clock) -> list[TrainCheck]:
    spec = clock.spec
    rate = lambda p: (lambda s: ref.planet_mean_rate_deg_per_day(spec, p) * s / DAY)  # noqa: E731
    sec_per_deg_12h = 12 * 3600 / 360
    sec_per_deg_24h = 24 * 3600 / 360
    return [
        TrainCheck("1", "Mean-time hour hand (I1), Strasbourg mean time", "M1.hour_hand",
                   lambda s: 30 * ref.mean_time_hours(s), to_unit=("s", sec_per_deg_12h)),
        TrainCheck("2", "Legal-time hour hand (I2), every summer-time change", "M1b.legal_hour_hand",
                   lambda s: 30 * ref.legal_time_hours(s), to_unit=("s", sec_per_deg_12h)),
        TrainCheck("2b", "Legal 24 h wheel on M1b (noon release), every change", "M1.noon_cam",
                   lambda s: 15 * ref.legal_time_hours(s), axis="M1b", to_unit=("s", sec_per_deg_24h)),
        TrainCheck("5", "Weekday carousel drive (I11)", "M2.weekday",
                   lambda s: (s + timelaw.MEAN_TIME_OFFSET_S) / DAY * 360 / 7),
        TrainCheck("6", "Sun hand (I3), mean", None,
                   lambda s: 15 * ref.mean_time_hours(s), axis="M2", to_unit=("s", sec_per_deg_24h)),
        TrainCheck("7", "Year arbor (M2.year): the Sun's mean longitude", "M2.year",
                   ref.sun_mean_longitude, extra_deg_per_century=REF_SUN),
        TrainCheck("8", "Moon hand (I4), mean", "M2.moon_hand",
                   lambda s: 15 * ref.mean_time_hours(s) - ref.moon_mean_elongation(s),
                   extra_deg_per_century=EXTRA_DT_DEG_PER_CENTURY + REF_MOON),
        TrainCheck("9", "Moon-phase globe (I15): mean elongation", "M5.moon_globe",
                   ref.moon_mean_elongation, extra_deg_per_century=EXTRA_DT_DEG_PER_CENTURY + REF_MOON),
        TrainCheck("10", "Planetarium Earth arm (M5.earth)", "M5.earth", ref.sun_mean_longitude,
                   extra_deg_per_century=REF_SUN),
        TrainCheck("10", "Mercury (I14)", "M5.mercury", rate("mercury")),
        TrainCheck("10", "Venus (I14)", "M5.venus", rate("venus")),
        TrainCheck("10", "Mars (I14)", "M5.mars", rate("mars")),
        TrainCheck("10", "Jupiter (I14)", "M5.jupiter", rate("jupiter")),
        TrainCheck("10", "Saturn (I14)", "M5.saturn", rate("saturn")),
        TrainCheck("11", "Planetarium Moon arm (M5.moon_arm): mean elongation", "M5.moon_arm",
                   ref.moon_mean_elongation, extra_deg_per_century=EXTRA_DT_DEG_PER_CENTURY + REF_MOON),
        TrainCheck("12", "Celestial globe (I16): mean sidereal time", "M6.sidereal",
                   lambda s: ref.gmst_deg(s) + ref.BORDEAUX_LON_DEG, to_unit=("s", 86164.0905 / 360),
                   extra_deg_per_century=REF_SIDEREAL),
    ]


def calendar_check(start=dt.date(2026, 1, 1), end=dt.date(2099, 12, 31)) -> list[Result]:
    """Rows 3-4: the ring shows the right date every day, and E6's count every night."""
    wrong, counts = [], {1: 0, 3: 0, 4: 0}
    for d, pos, n in calendar_ring.run_ring(start, end):
        if n:
            counts[n] = counts.get(n, 0) + 1
        if pos != calendar_ring.division_of(d):
            wrong.append(d)
    days = (end - start).days + 1
    out = [Result("3", f"Calendar ring date, every day {start.year}-{end.year}", len(wrong), "wrong days", 0,
                  wrong[0].isoformat() if wrong else "", not wrong, samples=days),
           Result("4", "E6 divisions per night: 1, or 4 / 3 into 1 January", 0, "wrong nights", 0, "", True,
                  f"{counts[1]} × 1, {counts[4]} × 4, {counts[3]} × 3", samples=days - 1)]
    # The known v1 limit: 2100 is not a leap year (needs the computus, v2).
    bad2100 = [d for d, pos, _ in calendar_ring.run_ring(dt.date(2099, 12, 31), dt.date(2100, 12, 31))
               if pos != calendar_ring.division_of(d)]
    out.append(Result("3", "Calendar ring in 2100 (v1 limit; the computus fixes it in v2)", len(bad2100),
                      "wrong days", 0, bad2100[0].isoformat() if bad2100 else "", True,
                      "expected: v1 counts 2100 as leap", samples=366))
    return out


def catch_up_check(clock: Clock) -> Result:
    """Row 14: after an outage, E6 runs once per M2 index passed = once per mean midnight passed."""
    m2 = clock.axes["M2"]
    n = m2.usteps_per_input_turn
    t_mid = timelaw.EPOCH_UNIX_S + DAY - timelaw.MEAN_TIME_OFFSET_S  # a mean midnight
    p_index = m2.usteps(t_mid * US)
    u = lambda *a: int(dt.datetime(*a, tzinfo=dt.timezone.utc).timestamp())  # noqa: E731
    autumn27 = timelaw.eu_change_unix_s(2027, False)
    spring28 = timelaw.eu_change_unix_s(2028, True)
    scenarios = {
        "1 h": (u(2027, 2, 10, 22, 0), 3600),
        "1 day": (u(2027, 2, 10, 12, 0), DAY),
        "30 days": (u(2027, 5, 1), 30 * DAY),
        "across New Year 2028": (u(2027, 12, 29), 6 * DAY),
        "across the autumn change 2027": (autumn27 - 3600, 7200),
        "across the spring change 2028": (spring28 - 60, 120),
        "a year, 2027-2028": (u(2027, 6, 1), 366 * DAY),
    }
    bad = []
    for name, (t1, span) in scenarios.items():
        t2 = t1 + span
        x1, x2 = m2.usteps(t1 * US), m2.usteps(t2 * US)
        index_passes = (x2 - p_index) // n - (x1 - p_index) // n
        midnights = (t2 + timelaw.MEAN_TIME_OFFSET_S) // DAY - (t1 + timelaw.MEAN_TIME_OFFSET_S) // DAY
        j_jump = timelaw.summer_time_j(t2) - timelaw.summer_time_j(t1)
        want_j = sum((1 if spring else 23) for y in range(2026, 2101) for spring in (True, False)
                     if t1 < timelaw.eu_change_unix_s(y, spring) <= t2)
        if index_passes != midnights or j_jump != want_j:
            bad.append(name)
    return Result("14", "Catch-up: E6 runs = mean midnights passed; J follows the changes", len(bad),
                  "bad scenarios", 0, ", ".join(bad), not bad, ", ".join(scenarios), len(scenarios))


def run_all(t0: int = 1798761600, years: float = 100, step_s: int = DAY) -> list[Result]:
    """t0 default: 2027-01-01 00:00 UTC."""
    clock = Clock()
    times = sample_times(t0, years, step_s)
    out = [run_train_check(clock, c, t0, times) for c in train_checks(clock)]
    out += calendar_check()
    out.append(catch_up_check(clock))
    return sorted(out, key=lambda r: (float(r.row.rstrip("b")), r.row))


# ---- sky gaps (optional, Skyfield) ----

@dataclass
class Gap:
    what: str
    lo: float
    hi: float
    unit: str
    note: str = ""


def sky_gaps(t0: int = 1767225600, years: float = 20, step_s: int = 6 * 3600) -> list[Gap]:
    import numpy as np

    from sim import ephemeris as eph

    clock = Clock()
    s = np.arange(t0, t0 + int(years * 365.25 * DAY), step_s, dtype=float)
    gaps = []
    # Sun hand: the clock shows mean time; the true Sun shows apparent time (equation of time).
    mean_h = (s + timelaw.MEAN_TIME_OFFSET_S) / 3600 % 24
    eot = ((eph.apparent_solar_time_hours(s) - mean_h + 12) % 24 - 12) * 60
    gaps.append(Gap("Sun hand: true apparent time − mean time (equation of time)", eot.min(), eot.max(), "min"))
    # Moon: true longitude − mean longitude.
    lm = np.array([ref.moon_mean_longitude(x) for x in s])
    d = (eph.ecliptic_longitude(s, "moon") - lm + 180) % 360 - 180
    gaps.append(Gap("Moon: true − mean longitude", d.min(), d.max(), "°"))
    # Phase: true elongation − mean elongation, in hours of phase.
    dm = np.array([ref.moon_mean_elongation(x) for x in s])
    de = (eph.elongation(s) - dm + 180) % 360 - 180
    k = 29.530588853 * 24 / 360
    gaps.append(Gap("Moon phase: true − mean elongation", de.min() * k, de.max() * k, "h of phase"))
    # Planets: true heliocentric longitude − the best-fit mean motion of the train.
    for p, body, train in [("mercury", "mercury barycenter", "M5.mercury"), ("venus", "venus barycenter", "M5.venus"),
                           ("earth_moon", "earth", "M5.earth"), ("mars", "mars barycenter", "M5.mars"),
                           ("jupiter", "jupiter barycenter", "M5.jupiter"), ("saturn", "saturn barycenter", "M5.saturn")]:
        true = eph.ecliptic_longitude(s, body, center="sun")
        shown = np.array([float(clock.delta_deg(train, int(s[0]) * US, int(x) * US) % 360) for x in s])
        diff = np.radians(true - shown)
        phase = np.degrees(np.arctan2(np.sin(diff).mean(), np.cos(diff).mean()))
        g = (true - shown - phase + 180) % 360 - 180
        name = "Earth" if p == "earth_moon" else p.capitalize()
        gaps.append(Gap(f"{name}: true heliocentric − mean (best-fit phase)", g.min(), g.max(), "°"))
    # Globe: apparent − mean sidereal time (nutation).
    gast = eph.gast_deg(s)
    gmst = np.array([ref.gmst_deg(x) for x in s])
    n = ((gast - gmst + 180) % 360 - 180) * 240
    gaps.append(Gap("Globe: apparent − mean sidereal time (nutation)", n.min(), n.max(), "s"))
    return gaps


def report_markdown(results: list[Result], gaps: list[Gap] | None, t0: int, years: float) -> str:
    start = dt.datetime.fromtimestamp(t0, dt.timezone.utc).date()
    lines = [
        "# Simulator report",
        "",
        "Generated by `python -m sim validate --write`. Do not edit by hand.",
        f"Design: `docs/firmware-design.md` §11. Train checks: set at {start}, run {years:g} years.",
        "",
        "## Checks (pass or fail)",
        "",
        "| Row | Check | Worst | Budget | When | Samples | Result | Note |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        worst = f"{r.worst:+.3g} {r.unit}" if isinstance(r.worst, float) else f"{r.worst} {r.unit}"
        budget = f"±{r.budget:.3g} {r.unit}" if isinstance(r.worst, float) else f"{r.budget}"
        lines.append(f"| {r.row} | {r.what} | {worst} | {budget} | {r.when} | {r.samples} | "
                     f"{'pass' if r.passed else '**FAIL**'} | {r.note} |")
    lines += ["", "Rows 13 (the show schedule) and 1-2's law are also covered by the firmware host tests",
              "(`firmware/tests/test_host.py`): the C++ law equals `sim/timelaw.py`, and every scheduled",
              "quarter falls on :00/:15/:30/:45 of Europe/Paris time.", ""]
    lines += ["## Sky gaps (v1's mean motion against the true sky; reported, not failed)", ""]
    if gaps is None:
        lines += ["Not computed: Skyfield or the DE440s kernel is not available (`python -m sim validate --sky`).", ""]
    else:
        lines += ["Skyfield with JPL DE440s; 2026 onward, 6-hour steps.", "",
                  "| Quantity | Min | Max | Unit |", "|---|---|---|---|"]
        lines += [f"| {g.what} | {g.lo:+.3g} | {g.hi:+.3g} | {g.unit} |" for g in gaps]
        lines.append("")
    lines += ["## Not yet checked", "",
              "- v1.5 (rows 15-18): equation of time and Moon equations with M3, sunrise/sunset for Bordeaux,",
              "  eclipses. Their budgets wait for M3 and the mobile horizon (firmware-design §11.4).",
              "- v2 (rows 19-20): Easter, dominical letter and epact; precession.", ""]
    return "\n".join(lines)
