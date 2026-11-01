"""Every CAD model exports a SketchUp file, and the showcase gears mesh cleanly."""
import pytest

bd = pytest.importorskip("build123d")

from cad import export_sketchup  # noqa: E402
from cad.lib import samples  # noqa: E402


def test_samples_have_no_interference():
    a = samples.build()
    metal = [i.name for i in a.items if i.name.startswith("tube_") or i.name == "arbor_3"]
    for x in metal:
        for y in metal:
            if x != y:
                a.allow(x, y)
    assert a.interference() == []


def test_every_model_writes_a_dae_with_named_nodes(tmp_path):
    from collada import Collada
    paths = export_sketchup.main(str(tmp_path))
    assert {p.stem for p in paths} == set(export_sketchup.MODELS)
    for p in paths:
        assert len(Collada(str(p)).scenes[0].nodes) > 5, p
