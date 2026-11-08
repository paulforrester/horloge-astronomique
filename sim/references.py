"""Reference values the clock's indications are checked against (docs/firmware-design.md §11.2-11.4).

Two kinds:
- **mean** references (this module, no dependencies): what each v1 train is built to show.
  Meeus, *Astronomical Algorithms*, 2nd ed. (1998): mean solar longitude (25.2), the Moon's mean
  longitude (47.1) and mean elongation (47.2), mean sidereal time (12.4). Planets: the JPL long-term
  mean-longitude rates plus general precession, from spec/clock.yaml.
- **true** references (sim/ephemeris.py, Skyfield + DE440s): the real sky, for the "sky gap".

Time arguments are Unix seconds (UTC). The clock runs on UTC, which leap seconds keep within 0.9 s
of UT1, so UT1 = UTC here. Meeus' T is in TT; ΔT's growth over a run is a real error of a
UT-driven clock and is carried in the budgets (validate.py).
"""

import datetime as dt
import zoneinfo

from sim import timelaw

JD_UNIX_EPOCH = 2440587.5
PARIS = zoneinfo.ZoneInfo("Europe/Paris")
STRASBOURG_LON_DEG = 7.7506      # docs/reference-notes.md §Location
BORDEAUX_LON_DEG = -0.57         # docs/reference-notes.md §Location data (D2: the globe's sky)


def jd(unix_s: float) -> float:
    return unix_s / 86400.0 + JD_UNIX_EPOCH


def centuries(unix_s: float) -> float:
    return (jd(unix_s) - 2451545.0) / 36525.0


# ---- time on the dials (degrees) ----

def mean_time_hours(unix_s: float) -> float:
    """Strasbourg mean time, as the clock defines it: UTC + 1860 s (D2)."""
    return ((unix_s + timelaw.MEAN_TIME_OFFSET_S) / 3600.0) % 24.0


def legal_time_hours(unix_s: float) -> float:
    """CET/CEST from the IANA database (independent of the firmware's own rule)."""
    t = dt.datetime.fromtimestamp(unix_s, dt.timezone.utc).astimezone(PARIS)
    return (t.hour + t.minute / 60 + (t.second + t.microsecond / 1e6) / 3600) % 24.0


# ---- mean astronomy (degrees) ----

def sun_mean_longitude(unix_s: float) -> float:
    T = centuries(unix_s)
    return (280.46646 + 36000.76983 * T + 0.0003032 * T * T) % 360.0          # Meeus 25.2


def moon_mean_longitude(unix_s: float) -> float:
    T = centuries(unix_s)
    return (218.3164477 + 481267.88123421 * T - 0.0015786 * T * T) % 360.0  # Meeus 47.1


def moon_mean_elongation(unix_s: float) -> float:
    T = centuries(unix_s)
    return (297.8501921 + 445267.1114034 * T - 0.0018819 * T * T) % 360.0  # Meeus 47.2


def gmst_deg(unix_s: float) -> float:
    d = jd(unix_s) - 2451545.0
    T = d / 36525.0
    return (280.46061837 + 360.98564736629 * d + 0.000387933 * T * T) % 360.0  # Meeus 12.4


def planet_mean_rate_deg_per_day(spec: dict, planet: str) -> float:
    """Tropical mean-longitude rate: JPL sidereal rate + general precession (spec/clock.yaml)."""
    t = spec["targets"]
    ldot = float(t[f"jpl_ldot_{planet}"]["value"])                 # deg per Julian century
    prec = float(t["precession_arcsec_per_century"]["value"]) / 3600.0
    return (ldot + prec) / 36525.0
