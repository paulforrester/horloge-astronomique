"""The setting sheet (architecture §7, docs/firmware-design.md §11.5).

For an instant T_set it lists what each output must show, so each can be set by hand, turning
forward only, and the controller then follows the law from T_set. v1 shows mean motion, so the
sheet gives mean positions. With --sky, it adds what needs the ephemeris: the planets' mean
longitudes (the train's best-fit phase against DE440s over 20 years around T_set) and Bordeaux
apparent sidereal time for the globe.
"""

import datetime as dt

from sim import calendar_ring, references as ref, timelaw

DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


def _hm(hours: float) -> str:
    tenths = round(hours * 36000) % (24 * 36000)  # whole tenths of a second, so 59.96 s cannot print as 60.0
    h, rem = divmod(tenths, 36000)
    m, t = divmod(rem, 600)
    return f"{h:02d}:{m:02d}:{t / 10:04.1f}"


def setting_sheet(t_set: int, sky: bool = False) -> str:
    when = dt.datetime.fromtimestamp(t_set, dt.timezone.utc)
    mean_h = ref.mean_time_hours(t_set)
    legal_h = ref.legal_time_hours(t_set)
    mean_date = dt.datetime.fromtimestamp(t_set + timelaw.MEAN_TIME_OFFSET_S, dt.timezone.utc).date()
    rows = [
        ("I1 gilt hands (Strasbourg mean time)", _hm(mean_h), "hour hand %.2f°, minute hand %.2f°" % (
            30 * (mean_h % 12), 6 * (mean_h * 60 % 60))),
        ("I2 silver hands (legal time, CET/CEST)", _hm(legal_h), "hour hand %.2f°, minute hand %.2f°" % (
            30 * (legal_h % 12), 6 * (legal_h * 60 % 60))),
        ("M1b 24 h noon wheel", _hm(legal_h), "%.2f° from 00:00" % (15 * legal_h)),
        ("I3 Sun hand (mean, v1)", _hm(mean_h), "%.3f° from midnight on the 24 h dial" % (15 * mean_h)),
        ("I4 Moon hand (mean, v1)", "", "%.3f° from midnight" % ((15 * mean_h - ref.moon_mean_elongation(t_set)) % 360)),
        ("I15 Moon globe / M5 Moon arm: mean elongation", "", "%.3f° (0 = new Moon)" % ref.moon_mean_elongation(t_set)),
        ("Year arbor: Sun's mean longitude", "", "%.3f°" % ref.sun_mean_longitude(t_set)),
        ("I8 calendar ring", mean_date.isoformat(), "division %d at the pointer" % calendar_ring.division_of(mean_date)),
        ("I11 weekday carousel", DAYS[(mean_date.weekday() + 1) % 7], "%.2f of the day gone (mean time)" % ((mean_h) / 24)),
        ("Correction inputs (v1.5)", "", "0: the worms stay at their index marks"),
        ("E2 ring", "", "any age: one silent walk after the start brings the due one (e2-design §10.3)"),
    ]
    if sky:
        rows += _sky_rows(t_set)
    out = [f"# Setting sheet for {when:%Y-%m-%d %H:%M:%S} UTC", "",
           "| Output | Reading | Set to |", "|---|---|---|"]
    out += [f"| {a} | {b} | {c} |" for a, b, c in rows]
    return "\n".join(out) + "\n"


def _sky_rows(t_set: int):
    import numpy as np

    from sim import ephemeris as eph
    from sim.model import Clock

    clock = Clock()
    s = np.arange(t_set - 10 * 365 * 86400, t_set + 10 * 365 * 86400, 86400, dtype=float)
    rows = []
    for name, body, train in [("Mercury", "mercury barycenter", "M5.mercury"), ("Venus", "venus barycenter", "M5.venus"),
                              ("Earth", "earth", "M5.earth"), ("Mars", "mars barycenter", "M5.mars"),
                              ("Jupiter", "jupiter barycenter", "M5.jupiter"), ("Saturn", "saturn barycenter", "M5.saturn")]:
        true = eph.ecliptic_longitude(s, body, center="sun")
        shown = np.array([float(clock.delta_deg(train, t_set * 1_000_000, int(x) * 1_000_000)) for x in s])
        d = np.radians(true - shown)
        phase = np.degrees(np.arctan2(np.sin(d).mean(), np.cos(d).mean())) % 360
        rows.append((f"I14 {name} arm: mean heliocentric longitude", "", "%.2f°" % phase))
    lst = (eph.gast_deg([float(t_set)])[0] + ref.BORDEAUX_LON_DEG) % 360
    rows.append(("I16 celestial globe: Bordeaux apparent sidereal time", _hm(lst / 15), "%.3f°" % lst))
    return rows
