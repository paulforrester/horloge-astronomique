"""Behaviour of the search functions: constraints, coaxial trains, metrics."""
from fractions import Fraction as F

import pytest

from tools.ratios import Train, evaluate, max_teeth_for_diameter, search_coaxial, search_compound
from tools.ratios.search import choose_train


def test_constraints_are_respected():
    res = search_compound(1 / 365.24219, 3, zmin=14, zmax=120, max_stage_ratio=8, top=20)
    assert res
    for r in res:
        assert all(14 <= z <= 120 for z in r.train.teeth)
        assert r.train.max_stage_ratio <= 8 + 1e-12


def test_max_diameter_limits_teeth():
    assert max_teeth_for_diameter(320, 1.0) == 318
    assert max_teeth_for_diameter(320, 0.8) == 398
    res = search_compound(1 / 29.5305888531, 2, max_diameter=100, module=1.0, top=5)
    assert all(r.train.max_tip_diameter <= 100 for r in res)


def test_results_are_sorted_by_error():
    res = search_compound(1 / 87.968, 3, top=10)
    errs = [abs(r.evaluation.rel_error) for r in res]
    assert errs == sorted(errs)


def test_exact_motion_work():
    res = search_coaxial(F(1, 12), zmax=96, top=5)
    exact = [r for r in res if r.ratio == F(1, 12)]
    assert exact and all(r.train.is_coaxial() for r in exact)


def test_coaxial_tooth_sum():
    res = search_coaxial(1.6255, tooth_sum=133, top=5)
    assert res
    for r in res:
        a, b = r.train.stages
        assert a.driver + a.driven == 133 == b.driver + b.driven
        assert r.train.is_coaxial()


def test_no_solution_returns_empty():
    # 1/365 cannot be reached in 2 meshes of at most 10:1
    assert search_compound(1 / 365.24219, 2, max_stage_ratio=10) == []


def test_metrics():
    e = evaluate(F(1, 365), 1 / 365.24219, input_period=1.0)
    assert e.output_period == pytest.approx(365.0)
    assert e.period_error_s == pytest.approx((365.0 - 365.24219) * 86400)
    # turns per century drift: 36525 * (1/365 - 1/365.24219) * 360 degrees
    assert e.drift_deg_per_century == pytest.approx(36525 * (1 / 365 - 1 / 365.24219) * 360)


def test_choose_train_prefers_fewest_stages():
    r = choose_train(1 / 7, max_drift_deg_per_century=1e-12, zmax_options=(96,))
    assert r.train.n_stages == 1 and r.ratio == F(1, 7)


def test_train_geometry():
    t = Train.of([(12, 48), (15, 45)], module=1.0)
    assert t.ratio == F(1, 12)
    assert [s.centre_distance for s in t.stages] == [30.0, 30.0]
    assert t.is_coaxial()
    assert t.max_tip_diameter == 50.0
