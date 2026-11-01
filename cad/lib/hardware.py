"""Bought hardware used by the CAD: rods, brass tubes, bearings, fasteners (decision D4).

Nominal catalogue dimensions only. D4: design seats from *measured* parts; the local tolerance
phase replaces these numbers with measured ones (``cad/lib/fits.py`` holds the fit allowances).
"""
from __future__ import annotations

from dataclasses import dataclass

# --- arbors: silver steel / ground rod, D4 -------------------------------------------------------
ROD_DIAMETERS = (3.0, 5.0, 8.0)          # mm: light/dial trains, general, motor reductions


# --- coaxial brass tubes, D4: 0.45 mm wall in 1 mm OD steps (e.g. Albion BT3M ... BT10M) -----------
TUBE_WALL = 0.45
TUBE_OD_RANGE = range(3, 11)             # 3 ... 10 mm OD


@dataclass(frozen=True)
class Tube:
    od: float
    wall: float = TUBE_WALL

    @property
    def id(self) -> float:
        return self.od - 2 * self.wall


def tube_stack(arbor: float, n: int) -> list[Tube]:
    """``n`` telescoping tubes over an arbor of diameter ``arbor``.

    Each tube's ID is its OD - 0.9 mm, so the next size down slides inside with 0.10 mm diametral
    clearance (D4). The first tube is the smallest whose ID clears the arbor by at least 0.1 mm.
    """
    ods = [od for od in TUBE_OD_RANGE if od - 2 * TUBE_WALL >= arbor + 0.1 - 1e-9]
    if len(ods) < n:
        raise ValueError(f"only {len(ods)} catalogue tubes fit over a {arbor} mm arbor (asked {n})")
    return [Tube(float(od)) for od in ods[:n]]


# --- bearings, D4 ---------------------------------------------------------------------------------
@dataclass(frozen=True)
class Bearing:
    name: str
    bore: float
    od: float
    width: float


BEARINGS = {b.name: b for b in [
    Bearing("MR63ZZ", 3, 6, 2.5),
    Bearing("MR85ZZ", 5, 8, 2.5),
    Bearing("685ZZ", 5, 11, 5),
    Bearing("688ZZ", 8, 16, 5),
    Bearing("6700ZZ", 10, 15, 4),
    Bearing("6701ZZ", 12, 18, 4),
    Bearing("6702ZZ", 15, 21, 4),
    Bearing("6703ZZ", 17, 23, 4),
    Bearing("6704ZZ", 20, 27, 4),
    Bearing("61806", 30, 42, 7),
    Bearing("61808", 40, 52, 7),
]}


def bearing_for_bore(d: float) -> Bearing:
    """Smallest catalogue bearing whose bore equals d (mm)."""
    for b in sorted(BEARINGS.values(), key=lambda b: b.od):
        if abs(b.bore - d) < 1e-9:
            return b
    raise KeyError(f"no catalogue bearing with a {d} mm bore")


# --- fasteners, D4: stainless A2, M3 default; brass heat-set inserts --------------------------------
@dataclass(frozen=True)
class Screw:
    size: str
    d: float            # nominal diameter
    clearance: float    # clearance hole (ISO 273 medium)
    head_d: float       # ISO 4762 socket head
    head_h: float
    insert_hole: float  # hole for a brass heat-set insert (ruthex-type) [Sn]
    insert_len: float


SCREWS = {s.size: s for s in [
    Screw("M2", 2.0, 2.4, 3.8, 2.0, 3.2, 4.0),
    Screw("M2.5", 2.5, 2.9, 4.5, 2.5, 3.6, 5.7),
    Screw("M3", 3.0, 3.4, 5.5, 3.0, 4.0, 5.7),
    Screw("M4", 4.0, 4.5, 7.0, 4.0, 5.6, 8.1),
    Screw("M5", 5.0, 5.5, 8.5, 5.0, 6.4, 9.5),
]}
