"""Core objects for gear-ratio engineering: stages, trains, error metrics and geometry.

Conventions
-----------
* A *stage* is one mesh: a ``driver`` gear (on the input side) turning a ``driven`` gear.
  Its ratio is driver / driven (output turns per input turn). Idler gears are not modelled:
  they change direction, not ratio.
* A *train* is a sequence of stages. Its ratio is the product of the stage ratios.
* Ratios are exact ``fractions.Fraction`` objects, so a ratio's error is never hidden by
  floating-point rounding.
* Periods are in days unless stated otherwise. ``input_period`` is the period of the input
  arbor, for example 1 for an arbor turning once per mean solar day, or 1/24 for once per hour.
* Geometry follows the standard spur-gear relations: pitch diameter = m*z, tip diameter =
  m*(z + 2), centre distance = m*(z1 + z2)/2 (no profile shift).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from math import floor, prod

DAYS_PER_YEAR = 365.25          # Julian year, used only to express drift "per year"
DAYS_PER_CENTURY = 36525.0      # Julian century


def as_fraction(x) -> Fraction:
    """Exact Fraction for ints, Fractions and strings like '1/24'; floats via limit_denominator."""
    if isinstance(x, Fraction):
        return x
    if isinstance(x, int):
        return Fraction(x)
    if isinstance(x, str):
        return Fraction(x)
    return Fraction(x).limit_denominator(10**15)


def max_teeth_for_diameter(max_tip_diameter: float, module: float) -> int:
    """Largest tooth count whose tip diameter m*(z+2) fits within max_tip_diameter."""
    return floor(max_tip_diameter / module - 2 + 1e-9)


@dataclass(frozen=True)
class Stage:
    driver: int
    driven: int
    module: float = 1.0

    @property
    def ratio(self) -> Fraction:
        return Fraction(self.driver, self.driven)

    @property
    def centre_distance(self) -> float:
        return self.module * (self.driver + self.driven) / 2

    def pitch_diameters(self) -> tuple[float, float]:
        return self.module * self.driver, self.module * self.driven

    def tip_diameters(self) -> tuple[float, float]:
        return self.module * (self.driver + 2), self.module * (self.driven + 2)


@dataclass(frozen=True)
class Train:
    stages: tuple[Stage, ...]

    @classmethod
    def of(cls, pairs, module: float = 1.0) -> "Train":
        """Build from [(driver, driven), ...] with one module for every stage."""
        return cls(tuple(Stage(int(d), int(n), module) for d, n in pairs))

    @property
    def ratio(self) -> Fraction:
        return prod((s.ratio for s in self.stages), start=Fraction(1))

    @property
    def n_stages(self) -> int:
        return len(self.stages)

    @property
    def teeth(self) -> list[int]:
        return [z for s in self.stages for z in (s.driver, s.driven)]

    @property
    def max_tip_diameter(self) -> float:
        return max(max(s.tip_diameters()) for s in self.stages)

    @property
    def max_stage_ratio(self) -> float:
        """Largest step-up or step-down of any single mesh (>= 1)."""
        return max(max(s.driver / s.driven, s.driven / s.driver) for s in self.stages)

    def is_coaxial(self) -> bool:
        """True if the output arbor can be coaxial with the input (reverted train).

        Stages are taken in pairs (1-2, 3-4, ...): each pair must have equal centre distances.
        A train with an odd number of stages is never coaxial by this rule.
        """
        if self.n_stages % 2:
            return False
        return all(abs(a.centre_distance - b.centre_distance) < 1e-9
                   for a, b in zip(self.stages[0::2], self.stages[1::2]))

    def describe(self) -> str:
        return " × ".join(f"{s.driver}/{s.driven}" for s in self.stages)


@dataclass
class Evaluation:
    """Error metrics of an achieved ratio against a target, for a given input period."""
    achieved: Fraction
    target: float
    input_period: float                      # days per input turn
    rel_error: float = field(init=False)
    output_period: float = field(init=False)  # days per output turn (achieved)
    period_error_s: float = field(init=False)  # achieved - target output period, seconds
    drift_deg_per_year: float = field(init=False)
    drift_deg_per_century: float = field(init=False)

    def __post_init__(self):
        a = float(self.achieved)
        t = float(self.target)
        self.rel_error = a / t - 1.0
        self.output_period = self.input_period / a if a else float("inf")
        target_period = self.input_period / t if t else float("inf")
        self.period_error_s = (self.output_period - target_period) * 86400.0
        turns_error_per_day = (a - t) / self.input_period
        self.drift_deg_per_year = 360.0 * turns_error_per_day * DAYS_PER_YEAR
        self.drift_deg_per_century = 360.0 * turns_error_per_day * DAYS_PER_CENTURY


def evaluate(achieved, target, input_period=1.0) -> Evaluation:
    return Evaluation(as_fraction(achieved), float(target), float(input_period))


def format_period(days: float) -> str:
    """'27 d 13 h 18 min 33.34 s' style."""
    sign = "-" if days < 0 else ""
    s = abs(days) * 86400.0
    d, s = divmod(s, 86400.0)
    h, s = divmod(s, 3600.0)
    m, s = divmod(s, 60.0)
    return f"{sign}{int(d)} d {int(h)} h {int(m)} min {s:.2f} s"
