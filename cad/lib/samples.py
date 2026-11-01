"""Library showcase: real tooth geometry for inspection in SketchUp (Paul, PR #4).

Meshing pairs at their true centre distances and phases, an internal gear, a rack, a radial cam,
a telescoping tube stack and bearings. Run through ``cad/export_sketchup.py``.
"""
from __future__ import annotations

import math

import build123d as bd

from . import parts
from .assembly import Assembly
from .gears import Gear, centre_distance, mesh_phase, pair_shifts, rack, spur_gear, internal_gear
from .hardware import tube_stack


def _at(shape, x, y, z=0.0):
    return shape.moved(bd.Location((x, y, z)))


def build() -> Assembly:
    a = Assembly("cad_lib_samples")
    # 1. year-train mesh with a profile-shifted 12-tooth pinion (pair_shifts keeps the centre distance)
    x1, x2 = pair_shifts(12, 89)
    g1, g2 = Gear(12, shift=x1), Gear(89, shift=x2)
    a.add("pinion_12_shifted", spur_gear(g1, 4, bore=3.0))
    a.add("wheel_89", _at(spur_gear(g2, 4, bore=5.0).rotate(bd.Axis.Z, mesh_phase(g1, g2)), centre_distance(g1, g2), 0))
    # 2. the Moon train's largest pair, 25/169 (module 1.0, accepted in Phase 1)
    g3, g4 = Gear(25), Gear(169)
    y = -150.0
    a.add("pinion_25", _at(spur_gear(g3, 4, bore=5.0), 0, y))
    a.add("wheel_169", _at(spur_gear(g4, 4, bore=5.0).rotate(bd.Axis.Z, mesh_phase(g3, g4)), centre_distance(g3, g4), y))
    # 3. internal gear with an 18-tooth pinion
    ring, pin = Gear(60, internal=True), Gear(18)
    a.add("ring_60_internal", _at(internal_gear(ring, 4), -90, 0))
    a.add("pinion_18_in_ring", _at(spur_gear(pin, 4, bore=3.0), -90 + centre_distance(ring, pin), 0))
    # 4. rack and pinion
    g5 = Gear(20)
    p = math.pi * g5.module
    a.add("rack_10", _at(rack(1.0, 10, 4), -140, 60))
    a.add("pinion_20_on_rack", _at(spur_gear(g5, 4, bore=3.0).rotate(bd.Axis.Z, -90), -140 + 4 * p, 60 + g5.pitch_radius))
    # 5. radial cam and the telescoping tube stack on a 3 mm arbor
    a.add("cam_eccentric", _at(parts.radial_cam(lambda t: 18 + 3 * math.sin(t), 4, 5), -60, 80))
    for k, t in enumerate(tube_stack(3.0, 6)):
        a.add(f"tube_od{int(t.od)}", _at(parts.tube(t, 30 - 4 * k), 40, 90), material="brass", printed=False)
    a.add("arbor_3", _at(parts.rod(3.0, 40), 40, 90, -5), material="steel", printed=False)
    a.add("bearing_688ZZ", _at(parts.bearing("688ZZ"), 80, 90), material="bearing", printed=False)
    a.add("bearing_MR85ZZ", _at(parts.bearing("MR85ZZ"), 100, 90), material="bearing", printed=False)
    return a
