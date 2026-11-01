"""Tooth bending strength (Lewis) and torque budget for printed spur trains.

Lewis bending stress at the tooth root: sigma = Ft / (b * m * Y), with Ft the tangential force
(N), b the face width (mm), m the module (mm) and Y the Lewis form factor. Stress comes out in
MPa (N/mm²).

Y for 20° full-depth involute teeth comes from Shigley's *Mechanical Engineering Design*,
Table 14-2, as reproduced in KSU lecture notes (ch. 14, p. 8):
https://faculty.ksu.edu.sa/sites/default/files/chapter14-spur_and_helical-esam-revise-part1.pdf
(retrieved 2026-11-01). Values between table rows are linearly interpolated.

Allowable stress comes from the spec (``defaults.allowable_stress_mpa``). The default is
Bambu Lab PLA Basic X-Y tensile strength, 39 ± 2 MPa (TDS v2.0), divided by a safety factor of 4
[E]. The factor covers print variability, creep under a load sustained for years, fatigue, and
root stress concentration, which plain Lewis ignores. The local tolerance and strength test
replaces this estimate.

Two questions are answered for each train:

* **Capacity:** the largest torque that may act at the train's OUTPUT arbor before any tooth
  exceeds the allowable stress. This is the ceiling for the output's slip clutch, which limits
  the torque a jammed hand or arm can put back into the train.
* **Running load:** the stress in every tooth for an estimated output load torque, and the
  resulting safety factor.

Worm stages (driver = 1) are skipped: a worm mesh is not a Lewis spur mesh.
"""
from __future__ import annotations

from bisect import bisect_left
from dataclasses import dataclass

# Shigley Table 14-2: (teeth, Y); the last row stands for a rack.
LEWIS_TABLE = [(12, 0.245), (13, 0.261), (14, 0.277), (15, 0.290), (16, 0.296), (17, 0.303),
               (18, 0.309), (19, 0.314), (20, 0.322), (21, 0.328), (22, 0.331), (24, 0.337),
               (26, 0.346), (28, 0.353), (30, 0.359), (34, 0.371), (38, 0.384), (43, 0.397),
               (50, 0.409), (60, 0.422), (75, 0.435), (100, 0.447), (150, 0.460), (300, 0.472),
               (400, 0.480), (10**9, 0.485)]


def lewis_y(z: int) -> float:
    """Lewis form factor for z teeth (20° full depth). Below 12 teeth: not tabulated."""
    if z < 12:
        raise ValueError(f"Lewis table starts at 12 teeth (got {z})")
    zs = [t for t, _ in LEWIS_TABLE]
    i = bisect_left(zs, z)
    if zs[i] == z:
        return LEWIS_TABLE[i][1]
    (z0, y0), (z1, y1) = LEWIS_TABLE[i - 1], LEWIS_TABLE[i]
    return y0 + (y1 - y0) * (z - z0) / (z1 - z0)


def mesh_force_capacity(driver: int, driven: int, module: float, face: float, sigma: float) -> float:
    """Largest tangential force (N) the weaker gear of a mesh can carry."""
    return sigma * face * module * min(lewis_y(driver), lewis_y(driven))


@dataclass
class MeshCheck:
    index: int
    driver: int
    driven: int
    force_capacity_n: float
    output_torque_capacity_nm: float   # torque at the train output that loads this mesh to its limit
    running_force_n: float
    running_stress_mpa: float


def train_strength(stages, *, face: float, sigma: float, output_load_nm: float) -> list[MeshCheck]:
    """Per-mesh capacity, expressed as a torque at the output arbor, and running stress.

    ``stages`` is a sequence of objects with ``driver``, ``driven`` and ``module``. Torque at the
    driven arbor of mesh i, given output torque T_out, is T_out * prod_{j>i}(d_j / n_j) (losses
    ignored, which is conservative).
    """
    spur = [s for s in stages if s.driver > 1 and s.driven > 1]
    out = []
    for i, s in enumerate(spur):
        down = 1.0
        for t in spur[i + 1:]:
            down *= t.driver / t.driven          # torque at this driven arbor = T_out * down
        r_driven = s.module * s.driven / 2.0 / 1000.0   # m
        f_cap = mesh_force_capacity(s.driver, s.driven, s.module, face, sigma)
        t_out_cap = f_cap * r_driven / down
        f_run = output_load_nm * down / r_driven
        sigma_run = f_run / (face * s.module * min(lewis_y(s.driver), lewis_y(s.driven)))
        out.append(MeshCheck(i + 1, s.driver, s.driven, f_cap, t_out_cap, f_run, sigma_run))
    return out
