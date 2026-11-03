"""Print files (PR #5): poses on the bed, overhang measure, identical parts counted once, two-colour sets."""
import json

import pytest

bd = pytest.importorskip("build123d")

from cad import export_print  # noqa: E402
from cad.lib.assembly import Assembly, exploded, overhang_area, print_pose  # noqa: E402
from cad.lib.gears import Gear, spur_gear  # noqa: E402


def _tee():
    """A 4 mm post under a 30 x 30 plate: the plate's underside is a cantilever."""
    post = bd.Box(4, 4, 10, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    top = bd.Box(30, 30, 2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((0, 0, 10)))
    return (post + top).moved(bd.Location((50, -20, 7)))


def test_pose_centres_the_part_on_the_bed():
    up, = print_pose([_tee()])
    bb = up.bounding_box()
    assert bb.min.Z == pytest.approx(0, abs=1e-6)
    assert (bb.min.X + bb.max.X) / 2 == pytest.approx(0, abs=1e-6)
    assert (bb.min.Y + bb.max.Y) / 2 == pytest.approx(0, abs=1e-6)
    down, = print_pose([_tee()], (0, 0, -1))
    assert down.bounding_box().size.Z == pytest.approx(12)
    side, = print_pose([_tee()], (1, 0, 0))                 # the X direction now points up
    assert side.bounding_box().size.Z == pytest.approx(30)


def test_overhang_measures_the_cantilever_and_flipping_removes_it():
    up, = print_pose([_tee()])
    assert overhang_area(up) == pytest.approx(30 * 30 - 4 * 4, rel=0.01)
    down, = print_pose([_tee()], (0, 0, -1))
    assert overhang_area(down) < 1.0


def test_export_counts_identical_parts_once_and_writes_sets(tmp_path):
    a = Assembly("mini")
    g = spur_gear(Gear(20, 1.0), 4.0)
    a.add("gear_a", g)
    a.add("gear_b", g.rotate(bd.Axis.Z, 7.0).moved(bd.Location((40, 0, -9))))   # same part, other place
    a.add("tee", _tee())                                                           # auto pose: flips it
    field = bd.Cylinder(20, 2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
    inlay = bd.Cylinder(8, 0.6, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
    a.add("face_field", field - inlay, print_up=(0, 0, -1), print_set="face", nozzle=0.2)
    a.add("face_inlay", inlay, material="silver", print_up=(0, 0, -1), print_set="face", nozzle=0.2)
    a.add("rod", bd.Cylinder(2.5, 30), material="steel", printed=False)
    m = export_print.export_model("mini", a, tmp_path)
    out = tmp_path / "mini"
    assert m["printed_parts"] == 5 and m["unique_parts"] == 4
    gear = next(p for p in m["parts"] if p["names"][0] == "gear_a")
    assert gear["names"] == ["gear_a", "gear_b"]
    tee = next(p for p in m["parts"] if p["names"][0] == "tee")
    assert tee["overhang_mm2"] < 1.0 and tee["size"][2] == pytest.approx(12.0)
    face = [p for p in m["parts"] if p["set"] == "face"]
    assert all(p["overhang_mm2"] < 1.0 for p in face)              # the inlay supports the field
    assert (out / "face.3mf").stat().st_size > 0
    assert sorted(f.name for f in out.glob("*.stl")) == ["face_field.stl", "face_inlay.stl", "gear_a.stl", "tee.stl"]
    assert json.loads((out / "manifest.json").read_text())["sets"] == {"face": ["face_field", "face_inlay"]}
    readme = (out / "README.md").read_text()
    assert "| `gear_a.stl` | 2 | gear_b |" in readme and "face.3mf" in readme


def test_exploded_view_keeps_the_order_along_the_axis():
    a = Assembly("stack")
    for k in range(4):
        a.add(f"plate_{k}", bd.Box(10, 10, 2).moved(bd.Location((0, 0, -10.0 * k))), group="mech")
    a.add("dial", bd.Box(10, 10, 1).moved(bd.Location((0, 0, 5))), group="front")
    e = exploded(a, offsets={"front": 30.0}, spread=1.0, spread_groups={"mech"})
    z = {i.name: i.shape.bounding_box().max.Z for i in e.items}
    assert z["dial"] > z["plate_0"] > z["plate_1"] > z["plate_2"] > z["plate_3"]
    assert z["plate_2"] - z["plate_3"] == pytest.approx(20.0)        # gaps doubled by spread = 1
    assert [i.name for i in e.items] == [i.name for i in a.items]
