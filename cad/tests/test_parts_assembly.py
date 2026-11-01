"""Shared parts, checks, export and render (cad/lib)."""
import math

import pytest

from cad.lib import parts
from cad.lib.assembly import BED_DUAL, BED_SINGLE, Assembly
from cad.lib.gears import Gear, centre_distance, mesh_phase, spur_gear
from cad.lib.hardware import BEARINGS, tube_stack

bd = pytest.importorskip("build123d")


def test_tube_stack_telescopes_with_d4_clearance():
    st = tube_stack(3.0, 7)
    assert [t.od for t in st] == [4, 5, 6, 7, 8, 9, 10]
    for inner, outer in zip(st, st[1:]):
        assert outer.id - inner.od == pytest.approx(0.10)
    with pytest.raises(ValueError):
        tube_stack(3.0, 8)


def test_tube_and_bearing_solids():
    t = tube_stack(5.0, 1)[0]
    v = parts.tube(t, 10).volume
    assert v == pytest.approx(math.pi / 4 * (t.od ** 2 - t.id ** 2) * 10, rel=1e-6)
    b = BEARINGS["MR85ZZ"]
    assert parts.bearing(b).volume == pytest.approx(math.pi / 4 * (8 ** 2 - 5 ** 2) * 2.5, rel=1e-6)


def test_cam_pressure_angle():
    r0, e = 20.0, 2.0
    prof = lambda t: r0 + e * math.sin(t)
    # max of atan(e cos t / (r0 + e sin t)) for an eccentric: about atan(e / sqrt(r0² - e²))
    assert parts.cam_pressure_angle(prof) == pytest.approx(math.degrees(math.atan(e / math.sqrt(r0**2 - e**2))), abs=0.05)
    cam = parts.radial_cam(prof, 3, 5)
    assert cam.is_valid and cam.volume > 0


def test_assembly_checks_find_a_clash_and_respect_allowed_contact():
    g1, g2 = Gear(15), Gear(45)
    a = Assembly("pair")
    a.add("pinion", spur_gear(g1, 4))
    a.add("wheel", spur_gear(g2, 4).rotate(bd.Axis.Z, mesh_phase(g1, g2)).moved(bd.Location((centre_distance(g1, g2), 0, 0))))
    a.add("rod", parts.rod(3, 20, -5), material="steel", printed=False)
    a.allow("rod", "pinion")
    assert a.interference() == []
    a.add("intruder", parts.disc(10, 2, z0=1).moved(bd.Location((centre_distance(g1, g2), 0, 0))))
    clash = {frozenset(p[:2]) for p in a.interference()}
    assert frozenset(("wheel", "intruder")) in clash


def test_bed_fit_flags_oversize():
    a = Assembly("bed")
    a.add("ok", parts.disc(287.5, 3))
    a.add("ring", parts.disc(341, 3))
    rows = {r["part"]: r for r in a.bed_fit(BED_SINGLE)}
    assert rows["ok"]["fits"] and not rows["ring"]["fits"]
    assert {r["part"]: r for r in a.bed_fit(BED_DUAL)}["ok"]["fits"]


def test_export_and_render(tmp_path):
    a = Assembly("demo")
    a.add("hub", parts.hub(5, 12, 6))
    a.add("rod", parts.rod(5, 20, -7), material="steel", printed=False, explode=(0, 0, -15))
    a.allow("hub", "rod")
    out = a.export(tmp_path)
    for f in ["hub.stl", "demo.3mf", "demo.step", "demo.dae"]:
        assert (out / f).stat().st_size > 0, f
    from collada import Collada
    assert {n.id for n in Collada(str(out / "demo.dae")).scenes[0].nodes} == {"hub", "rod"}
    a.render(tmp_path / "a.png")
    a.render(tmp_path / "b.png", exploded=True)
    assert (tmp_path / "a.png").stat().st_size > 5000
