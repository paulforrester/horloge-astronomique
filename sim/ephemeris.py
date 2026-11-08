"""The true sky from Skyfield and JPL DE440s (docs/firmware-design.md §11.2), for the sky gaps.

Optional: everything else in sim/ runs without it. The kernel (32 MB, 1849-2150) is cached in
$HORLOGE_KERNELS, default sim/.kernels/ (git-ignored). Times are built as UT1 = UTC (references.py).
"""

import os
from functools import lru_cache
from pathlib import Path

import numpy as np

from sim.references import JD_UNIX_EPOCH, STRASBOURG_LON_DEG

KERNELS = Path(os.environ.get("HORLOGE_KERNELS", Path(__file__).with_name(".kernels")))
KERNEL = "de440s.bsp"


def available(download: bool = False) -> bool:
    try:
        import skyfield  # noqa: F401
    except ImportError:
        return False
    return download or (KERNELS / KERNEL).exists()


@lru_cache(maxsize=1)
def _sky():
    from skyfield.api import Loader

    load = Loader(str(KERNELS))
    return load.timescale(), load(KERNEL)


def times(unix_s):
    ts, _ = _sky()
    return ts.ut1_jd(np.asarray(unix_s, dtype=float) / 86400.0 + JD_UNIX_EPOCH)


def apparent_solar_time_hours(unix_s, lon_deg=STRASBOURG_LON_DEG):
    """Local apparent solar time: the Sun's hour angle + 12 h."""
    _, eph = _sky()
    t = times(unix_s)
    ra, _, _ = eph["earth"].at(t).observe(eph["sun"]).apparent().radec(epoch="date")
    return (t.gast + lon_deg / 15.0 - ra.hours + 12.0) % 24.0


def ecliptic_longitude(unix_s, body: str, center: str = "earth"):
    """Ecliptic longitude of date, degrees; heliocentric if center == 'sun'."""
    from skyfield.framelib import ecliptic_frame

    _, eph = _sky()
    t = times(unix_s)
    if center == "earth":
        pos = eph["earth"].at(t).observe(eph[body]).apparent()
    else:
        pos = (eph[body] - eph["sun"]).at(t)
    _, lon, _ = pos.frame_latlon(ecliptic_frame)
    return lon.degrees


def elongation(unix_s):
    """The Moon's elongation from the Sun in ecliptic longitude (the phase angle), degrees."""
    return (ecliptic_longitude(unix_s, "moon") - ecliptic_longitude(unix_s, "sun")) % 360.0


def gast_deg(unix_s):
    return (times(unix_s).gast * 15.0) % 360.0
