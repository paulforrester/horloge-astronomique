"""Tooth strength (Lewis), load reflection through shared trains, and the motor budget."""
import copy

import pytest

from tools.ratios.core import Stage
from tools.ratios.spec import (evaluate_spec, load_spec, motor_budget, output_loads, strength_problems,
                               strength_rows)
from tools.ratios.strength import LEWIS_TABLE, lewis_y, mesh_force_capacity, train_strength

SPEC = load_spec()


def test_lewis_table_rows_are_exact():
    # Shigley Table 14-2 rows used as printed
    assert lewis_y(12) == 0.245
    assert lewis_y(17) == 0.303
    assert lewis_y(50) == 0.409
    assert lewis_y(150) == 0.460


def test_lewis_interpolates_between_rows():
    assert lewis_y(23) == pytest.approx((0.331 + 0.337) / 2)          # between 22 and 24
    assert lewis_y(89) == pytest.approx(0.435 + (0.447 - 0.435) * 14 / 25)
    ys = [lewis_y(z) for z in range(12, 400)]
    assert ys == sorted(ys)                                           # never decreases


def test_lewis_rejects_untabulated_pinions():
    with pytest.raises(ValueError):
        lewis_y(11)
    assert LEWIS_TABLE[0][0] == 12


def test_mesh_capacity_is_lewis_on_the_weaker_gear():
    # sigma * b * m * Y(min): 9.75 MPa x 4 mm x 1.0 x Y(12) = 9.555 N
    assert mesh_force_capacity(12, 89, 1.0, 4, 9.75) == pytest.approx(9.75 * 4 * 1.0 * 0.245)
    assert mesh_force_capacity(89, 12, 1.0, 4, 9.75) == mesh_force_capacity(12, 89, 1.0, 4, 9.75)


def test_single_mesh_capacity_and_stress():
    (c,) = train_strength([Stage(12, 89, 1.0)], face=4, sigma=9.75, output_load_nm=0.01)
    r = 89 / 2 / 1000                                                 # pitch radius of the 89T, m
    assert c.output_torque_capacity_nm == pytest.approx(9.75 * 4 * 0.245 * r)
    assert c.running_stress_mpa == pytest.approx(0.01 / r / (4 * 0.245))


def test_earlier_mesh_sees_the_later_reduction():
    # 15/99 then 12/89: torque at the 99T arbor is T_out x 12/89
    a, b = train_strength([Stage(15, 99, 1.0), Stage(12, 89, 1.0)], face=4, sigma=9.75, output_load_nm=0.01)
    down = 12 / 89
    assert a.output_torque_capacity_nm == pytest.approx(9.75 * 4 * 0.290 * 99 / 2000 / down)
    assert a.running_force_n == pytest.approx(0.01 * down / (99 / 2000))
    assert b.output_torque_capacity_nm < a.output_torque_capacity_nm


def test_worm_meshes_are_skipped():
    assert train_strength([Stage(1, 160, 1.0), Stage(1, 161, 1.0)], face=4, sigma=9.75,
                          output_load_nm=0.01) == []


def test_child_loads_reflect_onto_the_shared_train():
    res = evaluate_spec(SPEC)
    loads = output_loads(SPEC, res)
    eta = SPEC["strength"]["mesh_efficiency"]
    own = SPEC["strength"]["running_output_load_nm"]
    expect = own
    for r in res.values():
        if r.spec.get("via") == "M5.earth":
            ratio = float(r.train.ratio)
            factor = 1 + ratio if r.spec.get("epicyclic") else ratio
            expect += loads[r.id] * factor / eta ** r.train.n_stages
    assert loads["M5.earth"] == pytest.approx(expect)
    assert loads["M2.year"] == pytest.approx(own)                     # no children


def test_every_train_has_margin_and_a_clutch_window():
    assert strength_problems(SPEC) == []
    need = SPEC["strength"]["min_safety_factor"]
    for row in strength_rows(SPEC):
        assert row.safety >= need, row
        assert row.window and row.window[0] < row.window[1], row


def test_narrow_faces_on_the_planetarium_trunk_are_caught():
    s = copy.deepcopy(SPEC)
    for t in s["trains"]:
        if t["id"] == "M5.earth":
            t.pop("face_width_mm")
    assert any(p.startswith("M5.earth: running safety factor") for p in strength_problems(s))


def test_motor_has_margin_on_every_module():
    rows = motor_budget(SPEC)
    assert {m for m, *_ in rows} == {t["id"].split(".")[0] for t in SPEC["trains"]}
    for mod, red, t_in, t_m, margin in rows:
        assert margin > 10, mod
        if red > 1:
            assert t_m < t_in, mod                                    # a reduction lowers motor torque
