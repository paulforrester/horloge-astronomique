"""Reproduce Schwilgué's published ratios (docs/reference-notes.md: CLEA, LEF, ELS).

Every assertion is exact (Fraction arithmetic) or tolerance-bounded by the precision the source
prints. If any of these fail, either the tool or our reading of the source is wrong.
"""
from fractions import Fraction as F

import pytest

from tools.ratios import Train, format_period, search_compound, search_differential
from tools.ratios.epicyclic import schwilgue_lunar_turns_per_year, schwilgue_sidereal

# Schwilgué's tropical year: 365 d 5 h 48 min 48 s = 31,556,928 s [S: LEF; DA p. 52]
YEAR_S = F(31556928)
YEAR_D = YEAR_S / 86400
YEAR_H = YEAR_S / 3600


def seconds(d=0, h=0, m=0, s=0.0):
    return ((d * 24 + h) * 60 + m) * 60 + s


def test_year_train_is_the_year_in_hours():
    # LEF gear table (Ungerer fig. 49): Terre b/B = 9/156, c/C = 10/188, d/D = 10/269
    earth = Train.of([(9, 156), (10, 188), (10, 269)])
    assert earth.ratio == F(900, 7889232)
    # CLEA prints P = (156*188*269)/(9*10*10) "= 365,2422 tours": it is the year in HOURS
    assert 1 / earth.ratio == YEAR_H
    assert float(YEAR_D) == pytest.approx(365.242222, abs=1e-6)


@pytest.mark.parametrize("name, train, target_s, obtained", [
    # LEF table: (gear ratio relative to the Earth arbor, period to realise, period obtained)
    ("Mercury", [(240, 44), (102, 134)], 7600475, seconds(87, 23, 14, 35.79)),
    ("Venus", [(197, 17), (31, 221)], 19413685, seconds(224, 16, 41, 25.68)),
    ("Mars", [(203, 95), (53, 213)], 59350724, seconds(686, 22, 18, 43.87)),
    ("Jupiter", [(96, 157), (32, 232)], 374163250, seconds(4330, 14, 14, 23.5)),
    ("Saturn", [(58, 161), (20, 212)], 928535410, seconds(10746, 22, 30, 2.15)),
])
def test_planet_trains(name, train, target_s, obtained):
    t = Train.of(train)
    period_s = float(YEAR_S / t.ratio)
    assert period_s == pytest.approx(obtained, abs=0.05), name   # LEF prints 0.01–0.1 s
    assert abs(period_s / target_s - 1) < 1e-5, name


@pytest.mark.parametrize("name, factor, printed, unit", [
    # CLEA: planet period = P x factor, printed to 0.01 d (inner planets, Mars) or 0.01 yr
    ("Mercury", F(44 * 134, 240 * 102), 87.97, "d"),
    ("Venus", F(17 * 221, 197 * 31), 224.70, "d"),
    ("Mars", F(95 * 213, 203 * 53), 686.93, "d"),
    ("Jupiter", F(157 * 232, 96 * 32), 11.86, "yr"),
    ("Saturn", F(161 * 212, 58 * 20), 29.42, "yr"),
])
def test_clea_planet_factors(name, factor, printed, unit):
    value = float(YEAR_D * factor) if unit == "d" else float(factor)   # in years: P = 1 yr
    assert value == pytest.approx(printed, abs=0.005 + 1e-9), name


def test_synodic_month_differential():
    # CLEA: (312/24) x [1 - (83x14)/(122x196)] = 12.368267 lunar turns per year
    turns = schwilgue_lunar_turns_per_year(312, 24, 83, 122, 14, 196)
    assert turns == F(21125, 1708)
    assert float(turns) == pytest.approx(12.368267, abs=5e-7)
    assert float(YEAR_D / turns) == pytest.approx(29.53059, abs=5e-6)


def test_exact_sidereal_epicyclic():
    # LEF fig. 11: b/B = 18/270, c/C = 18/269, d/D = 26/100, e/E = 18/94
    out = schwilgue_sidereal(18, 270, 18, 269, 26, 100, 18, 94)
    assert out == F(164809, 164359)
    assert out == 1 + F(450, 164359)
    # exactly (Y+1)/Y for Schwilgué's year in days
    assert out == (YEAR_D + 1) / YEAR_D


def test_approximate_lunar_train():
    # LEF: 334/28 x 65/341 x 300/57 = 12 x 271375/272118 (arbor turning once in 2 h)
    assert Train.of([(334, 28), (65, 341), (300, 57)]).ratio == 12 * F(271375, 272118)


@pytest.mark.parametrize("name, ratio, printed", [
    # LEF lunar-equation table: chosen ratio (days) and the period it gives
    ("anomaly", F(70209, 2548), seconds(27, 13, 18, 33.34)),
    ("evection", F(74090, 2329), seconds(31, 19, 29, 11.3)),
    ("variation", F(51649, 1749), seconds(29, 12, 44, 2.881)),
    ("annual equation", F(226461, 620), seconds(365, 6, 13, 56.13)),
    ("nodes (draconic)", F(49880, 1833), seconds(27, 5, 5, 35.84)),
])
def test_lunar_equation_periods(name, ratio, printed):
    assert float(ratio) * 86400 == pytest.approx(printed, abs=0.06), name
    assert format_period(float(ratio)).startswith(format_period(printed / 86400)[:16])


def test_search_rediscovers_the_year_exactly():
    # Under Schwilgué's limits (min 6 teeth, wheels up to 300), the exact year ratio exists.
    res = search_compound(1 / YEAR_H, 3, input_period=F(1, 24), zmin=6, zmax=300,
                          max_stage_ratio=30, top=1)
    assert res and res[0].ratio == F(900, 7889232)


@pytest.mark.parametrize("name, his, target_s", [
    ("Mercury", F(240 * 102, 44 * 134), 7600475),
    ("Venus", F(197 * 31, 17 * 221), 19413685),
    ("Mars", F(203 * 53, 95 * 213), 59350724),
    ("Jupiter", F(96 * 32, 157 * 232), 374163250),
    ("Saturn", F(58 * 20, 161 * 212), 928535410),
])
def test_search_matches_or_beats_schwilgue_planets(name, his, target_s):
    target = YEAR_S / target_s              # planet turns per Earth turn
    his_err = abs(float(his / target) - 1)
    res = search_compound(target, 2, zmin=17, zmax=250, max_stage_ratio=15, top=1)
    assert res, name
    # equal ratios give equal errors up to floating-point noise (~1e-16 absolute)
    assert abs(res[0].evaluation.rel_error) <= his_err + 1e-12, name


def test_differential_search_reproduces_exact_sidereal():
    # 1 + X with X = 450/164359 found exactly with Schwilgué-like limits
    res = search_differential(F(164809, 164359), 1, 1, 3, zmin=6, zmax=300, max_stage_ratio=16, top=1)
    assert res and res[0].ratio == F(164809, 164359)
