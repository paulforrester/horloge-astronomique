"""Phase 3 gate probe: how far v1's mean motions sit from the true sky (docs/firmware-design.md §9.3).

v1 shows steady (mean) motion for the Sun and the Moon (D5). This probe measures, over
2026-2045, the gaps the simulator will later report as "expected v1 deviation":

- the equation of time (apparent minus mean solar time);
- the Moon's true longitude minus its mean longitude;
- true new moons minus mean new moons.

Reference: Skyfield with the JPL DE440s kernel. The mean Moon and mean new moon are Meeus,
*Astronomical Algorithms* (2nd ed., 1998), eqs. 47.1 and 49.1.

Run:  python sim/probe_v1_deviations.py      (needs skyfield; downloads de440s.bsp, 32 MB)
Kernel cache: $HORLOGE_KERNELS, default sim/.kernels (git-ignored).
"""

import os

import numpy as np
from skyfield import almanac
from skyfield.api import Loader
from skyfield.framelib import ecliptic_frame

KERNELS = os.environ.get("HORLOGE_KERNELS", os.path.join(os.path.dirname(__file__), ".kernels"))


def main():
    load = Loader(KERNELS)
    ts = load.timescale()
    eph = load("de440s.bsp")
    earth, sun, moon = eph["earth"], eph["sun"], eph["moon"]

    t = ts.utc(2026, 1, 1 + np.arange(0, 20 * 365.25, 0.25))

    # Equation of time at Greenwich: apparent solar time (GAST - RA + 12 h) minus UT1.
    ra, _, _ = earth.at(t).observe(sun).apparent().radec(epoch="date")
    ast = (t.gast - ra.hours + 12) % 24
    ut1h = ((t.ut1 - 0.5) % 1) * 24
    eot_min = ((ast - ut1h + 12) % 24 - 12) * 60
    print(f"equation of time, min: {eot_min.min():+.2f} … {eot_min.max():+.2f}")

    # Moon: apparent ecliptic longitude of date minus the mean longitude L' (Meeus 47.1).
    _, lon, _ = earth.at(t).observe(moon).apparent().frame_latlon(ecliptic_frame)
    T = (t.tt - 2451545.0) / 36525
    mean_l = (218.3164477 + 481267.88123421 * T - 0.0015786 * T**2) % 360
    d = (lon.degrees - mean_l + 180) % 360 - 180
    print(f"Moon true - mean longitude, deg: {d.min():+.2f} … {d.max():+.2f}")

    # New moons: Skyfield's true instants minus Meeus 49.1 mean instants.
    tt, ph = almanac.find_discrete(ts.utc(2026, 1, 1), ts.utc(2046, 1, 1), almanac.moon_phases(eph))
    nm = tt[ph == 0]
    k = np.round((nm.tt - 2451550.09766) / 29.530588861)
    jde = 2451550.09766 + 29.530588861 * k + 0.00015437 * (k / 1236.85) ** 2
    dh = (nm.tt - jde) * 24
    print(f"true - mean new moon, h: {dh.min():+.2f} … {dh.max():+.2f} ({len(nm)} new moons)")


if __name__ == "__main__":
    main()
