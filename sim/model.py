"""The clock as the simulator sees it (docs/firmware-design.md §11.1).

Every module stepper follows the firmware's time law (sim/timelaw.py, the same law as
firmware/core/time_law.h). Every output turns at its train's exact ratio from spec/clock.yaml,
read through tools/ratios. So an output's angle at any instant is closed-form: there is no
stepping through 1.125 s steps for decades.

    angle(t) = angle(T_set) + 360° × Δturns_input(T_set → t) × ratio

Δturns_input is exact: (µsteps commanded between the two instants) / (µsteps per input turn).
"""

from dataclasses import dataclass
from fractions import Fraction
from functools import cached_property

from sim import timelaw
from tools.ratios.spec import evaluate_spec, load_spec

US = 1_000_000

# Which stepper drives each train, by its id prefix (architecture §2-3).
_AXIS_OF_PREFIX = {"M1": "M1", "M1b": "M1b", "M2": "M2", "M3": "M3", "M5": "M5", "M6": "M6"}


@dataclass(frozen=True)
class Axis:
    id: str
    time: str        # "mean" or "legal"
    reduction: int   # motor turns per input-arbor turn

    @property
    def usteps_per_input_turn(self) -> int:
        return timelaw.USTEPS_PER_MOTOR_REV * self.reduction

    def usteps(self, unix_us: int, p_k: int = 0) -> int:
        j = timelaw.summer_time_j(unix_us // US) if self.time == "legal" else 0
        return timelaw.target_usteps(self.time, unix_us, j, p_k)

    def input_turns(self, t0_us: int, t1_us: int) -> Fraction:
        """Exact input-arbor turns commanded between two instants."""
        return Fraction(self.usteps(t1_us) - self.usteps(t0_us), self.usteps_per_input_turn)


class Clock:
    def __init__(self, spec: dict | None = None):
        self.spec = spec if spec is not None else load_spec()

    @cached_property
    def trains(self):
        return evaluate_spec(self.spec)

    @cached_property
    def axes(self) -> dict[str, Axis]:
        red = self.spec["motor"]["reduction"]
        out = {}
        for a in self.spec["controller"]["axes"]:
            out[a["id"]] = Axis(a["id"], a["time"], int(red.get(a["id"], 1)))
        return out

    def axis_of(self, train_id: str) -> Axis:
        return self.axes[_AXIS_OF_PREFIX[train_id.split(".")[0]]]

    def ratio(self, train_id: str) -> Fraction:
        """Output turns per input-arbor turn of the module (through any 'via' chain)."""
        return Fraction(self.trains[train_id].achieved)

    def delta_deg(self, train_id: str, t0_us: int, t1_us: int, axis: str | None = None) -> Fraction:
        """Exact output rotation in degrees between two instants. `axis` overrides the driver."""
        ax = self.axes[axis] if axis else self.axis_of(train_id)
        return 360 * ax.input_turns(t0_us, t1_us) * self.ratio(train_id)

    def quantum_deg(self, train_id: str, axis: str | None = None) -> float:
        """One µstep of the input arbor, at the output, in degrees."""
        ax = self.axes[axis] if axis else self.axis_of(train_id)
        return float(360 * self.ratio(train_id) / ax.usteps_per_input_turn)

    def drift_deg_per_century(self, train_id: str) -> float:
        return self.trains[train_id].evaluation.drift_deg_per_century


def wrap180(x: float) -> float:
    return (x + 180.0) % 360.0 - 180.0
