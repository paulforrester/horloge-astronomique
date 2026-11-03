"""Validate cad/lib/gears.py outlines against BOSL2 spur_gear2d (decision D1).

Needs OpenSCAD on PATH and BOSL2: set BOSL2_PARENT to the directory that contains the BOSL2
checkout (git clone https://github.com/BelfrySCAD/BOSL2.git). Skipped otherwise.
"""
import math
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from cad.lib.gears import Gear, auto_shift, gear_face

bd = pytest.importorskip("build123d")
PARENT = os.environ.get("BOSL2_PARENT", "")
pytestmark = pytest.mark.skipif(not (shutil.which("openscad") and PARENT and Path(PARENT, "BOSL2").is_dir()),
                                reason="needs openscad and BOSL2_PARENT")

SCAD = """include <BOSL2/std.scad>
include <BOSL2/gears.scad>
spur_gear2d(mod={m}, teeth={z}, backlash={b}, profile_shift={x}, pressure_angle=20);
"""


def bosl2_face(m, z, backlash_per_gear, x):
    with tempfile.TemporaryDirectory() as d:
        scad, svg = Path(d, "g.scad"), Path(d, "g.svg")
        scad.write_text(SCAD.format(m=m, z=z, b=backlash_per_gear, x=x))
        subprocess.run(["openscad", "-o", str(svg), str(scad)], check=True, capture_output=True,
                       env={**os.environ, "OPENSCADPATH": PARENT}, timeout=120)
        nums = re.findall(r"(-?[\d.]+(?:e-?\d+)?),(-?[\d.]+(?:e-?\d+)?)", svg.read_text())
    pts = [bd.Vector(float(a), -float(b), 0) for a, b in nums]      # SVG y points down
    return bd.Face(bd.Wire.make_polygon(pts, close=True))


def _ring(r_in, r_out):
    return bd.Face(bd.Wire.make_circle(r_out)) - bd.Face(bd.Wire.make_circle(r_in))


@pytest.mark.parametrize("z, x", [(12, auto_shift(12)), (12, 0.0), (17, 0.0), (40, 0.0), (89, -auto_shift(12))])
def test_outline_matches_bosl2(z, x):
    """Working flanks, undercut and tips agree; the root corner differs by design.

    BOSL2 rounds the concave corner where the flank meets the root circle; ours is sharp. The
    printed root is rounded by the nozzle anyway (about 0.2 mm radius with a 0.4 mm nozzle), so the
    comparison masks the bottom quarter-module above the root circle.
    """
    g = Gear(z, module=1.0, shift=x, backlash=0.15)
    mine = gear_face(g)
    # BOSL2 thins each tooth by its whole `backlash` argument, so pass half of ours
    ref = bosl2_face(1.0, z, g.backlash / 2, x)
    zone = _ring(g.root_radius + 0.25 * g.module, g.tip_radius + 1)
    a = mine & zone
    sym, _ = min((((a - r).area + (r - a).area), ang) for ang in (0, 90, 180 / z, 90 + 180 / z)
                 for r in [ref.rotate(bd.Axis.Z, ang) & zone])
    # mean normal deviation over the flanks: symmetric-difference area / total flank length
    flank_len = 2 * z * (g.tip_radius - g.root_radius - 0.25 * g.module)
    assert sym / flank_len < 0.01, f"mean flank deviation {sym / flank_len * 1000:.1f} µm"
    # whole outline, root corners included: still within 0.5 % in area
    assert abs(mine.area - ref.area) / ref.area < 0.005, (mine.area, ref.area)
