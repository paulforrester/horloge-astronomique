"""E2 part 2b: the quarter and hour counting trains, geometry and logic only (docs/e2-design.md §12).

Each train is a classic rack and snail (concept gate §4.2, §4.4), adapted for printing:
- the **rack** is a lever on a stud behind the state arbor. Its tail finger falls onto the snail; its teeth
  are on an arc at a larger radius, so a fine snail step becomes a printable tooth (pitch 2.5 mm);
- the **gathering pawl** rides on a feed lever, coaxial with the rack, which an eccentric on the strike shaft
  rocks once per stroke. Each rock gathers one tooth; the rack hook catches it;
- the **rack hook** holds the rack between strokes. A release cam on the state arbor (the time train, rule 4)
  lifts it a minute before each show, and the rack falls onto the snail: that sets the count;
- the strike shaft turns once per stroke (3 s). Its cams close the cue switch (E1's genie, quarters only), lift
  the striking figure (part 2c), and stop the train at the lock switch when the rack is home.

Frame as in layout.py: X to the viewer's right, Y away from the viewer, Z up. Angles in the YZ plane are
measured from +Y, positive towards +Z.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from cad.modules.e2_ages import program as G

ARBOR_Z = -81.0                              # the state arbor's axis (z)
PITCH = 2.5                                  # the racks' tooth pitch on their pitch arcs [E: the 0.2 mm nozzle, CLAUDE.md]
TOOTH = 1.2                                  # tooth depth
TAIL = 24.0                                  # rack pivot to tail finger tip
TAIL_PIN = 1.0                               # the tail finger's tip radius
RACK_PIVOT_Z = -67.0                         # both racks share one stud
HOME_GAP = 1.0                               # a gathered rack's tail clears the snail by about one step
FEED_OVERSHOOT = 1.4                         # the gathering pawl's stroke, in teeth
CYCLE_S = 3.0                                # one strike-shaft turn: a genie-and-age pair [S: Paul, 6 Nov 2026]
DEATH_CYCLE_S = 3.0                          # one turn per hour stroke [E: Paul to time it from his video]
RELEASE_LEAD_MIN = 1.0                       # the release cams drop the racks this long before each show
RELEASE_WIDTH_MIN = 0.5                      # each release lobe holds the hook up this long


def arbor_yz():
    return (G.plan()["bell_shaft"][1], ARBOR_Z)


@dataclass(frozen=True)
class TrainSpec:
    name: str
    counts: int                              # 4 pairs, or 12 strokes
    r_teeth: float                           # the rack's pitch-arc radius
    r_first: float                           # the snail's radius for a count of 1
    x_rack: float                            # the rack's (and snail's) mid-plane


QUARTER = TrainSpec("quarter", 4, 30.0, 14.0, 16.0)
HOUR = TrainSpec("hour", 12, 48.0, 20.0, -10.5)
TRAINS = (QUARTER, HOUR)


def pivot():
    ys, _ = arbor_yz()
    return (ys + TAIL, RACK_PIVOT_Z)


def tooth_angle(t: TrainSpec) -> float:
    """Radians the rack turns per tooth [D: pitch / pitch-arc radius]."""
    return PITCH / t.r_teeth


def tail_tip(theta: float):
    """The tail finger's tip at rack angle theta (0: the tail arm level; + : the tail falls)."""
    py, pz = pivot()
    return (py - TAIL * math.cos(theta), pz - TAIL * math.sin(theta))


def snail_radius_under_tail(theta: float) -> float:
    """The snail radius the tail rests on at rack angle theta [D]."""
    ay, az = arbor_yz()
    ty, tz = tail_tip(theta)
    return math.hypot(ty - ay, tz - az) - TAIL_PIN


def _solve_theta(t: TrainSpec, r: float) -> float:
    lo, hi = -0.8, 0.8                        # radius falls as theta rises
    for _ in range(80):
        m = (lo + hi) / 2
        if snail_radius_under_tail(m) > r:
            lo = m
        else:
            hi = m
    return (lo + hi) / 2


def rack_angles(t: TrainSpec) -> list[float]:
    """Rack angles for counts 0 (home, gathered) .. N: count 1 rests on r_first, each further count one tooth
    lower [D]."""
    d = tooth_angle(t)
    th1 = _solve_theta(t, t.r_first)
    return [th1 + (n - 1) * d for n in range(t.counts + 1)]


def snail_radii(t: TrainSpec) -> list[float]:
    """The snail's radius for each count 1..N, derived from the rack [D]."""
    return [snail_radius_under_tail(th) for th in rack_angles(t)[1:]]


def home_clearance(t: TrainSpec) -> float:
    """How far a gathered rack's tail stands above the count-1 step [D]."""
    return snail_radius_under_tail(rack_angles(t)[0]) - t.r_first


# ------------------------------------------------------------------------------------------------ the snails
def quarter_count(minutes: float) -> int:
    """Pairs due at the next quarter: 1 at :15, 2 at :30, 3 at :45, 4 at :00; each step centred on its show."""
    m = (minutes + 7.5) % 60.0
    return (int(m // 15.0) - 1) % 4 + 1


def hour_count(hours: float) -> int:
    """Strokes due: H from H - 0.5 h to H + 0.5 h (1 .. 12)."""
    return int(math.floor((hours + 0.5) % 12.0)) or 12


QUARTER_RAMP = (7.5, 12.0)                   # minutes: the 4 -> 1 rise is a ramp, not a step
HOUR_RAMP = (0.5, 0.85)                      # hours: the 12 -> 1 rise is a ramp


def quarter_snail_radius(minutes: float) -> float:
    """The quarter snail under its tail. Falls are steps; the one rise (4 pairs -> 1) is a ramp, so a rack left
    down (quiet hours, a fault) is lifted, never blocked."""
    r = snail_radii(QUARTER)
    m = minutes % 60.0
    a, b = QUARTER_RAMP
    if a <= m < b:
        return r[3] + (r[0] - r[3]) * (m - a) / (b - a)
    return r[quarter_count(m) - 1]


def hour_snail_radius(hours: float) -> float:
    r = snail_radii(HOUR)
    h = hours % 12.0
    a, b = HOUR_RAMP
    if a <= h < b:
        return r[11] + (r[0] - r[11]) * (h - a) / (b - a)
    return r[hour_count(h) - 1]


# ------------------------------------------------------------------------------------------------ the releases
RELEASE_R = (10.0, 13.0)                     # the release cams' base and lobe radii
RELEASE_RISE_MIN = 0.5                       # the lobe's rise is a ramp: the riding follower is lifted, not struck


def _release_radius(m: float, period: float) -> float:
    start = period - RELEASE_LEAD_MIN
    r0, r1 = RELEASE_R
    t = m % period
    if start - RELEASE_RISE_MIN <= t < start:
        return r0 + (r1 - r0) * (t - start + RELEASE_RISE_MIN) / RELEASE_RISE_MIN
    if start <= t < start + RELEASE_WIDTH_MIN:
        return r1
    return r0


def quarter_release_radius(minutes: float) -> float:
    """The quarter release cam under its follower: four lobes, one before each quarter."""
    return _release_radius(minutes, 15.0)


def hour_release_radius(minutes: float) -> float:
    """The hour release cam: one lobe, before the hour."""
    return _release_radius(minutes, 60.0)


def quarter_release_lift(minutes: float) -> bool:
    """The quarter release cam (4 lobes on the state arbor) holds the hook up for RELEASE_WIDTH_MIN, starting
    RELEASE_LEAD_MIN before each quarter."""
    m = minutes % 15.0
    start = 15.0 - RELEASE_LEAD_MIN
    return start <= m < start + RELEASE_WIDTH_MIN


def hour_release_lift(minutes: float) -> bool:
    m = minutes % 60.0
    start = 60.0 - RELEASE_LEAD_MIN
    return start <= m < start + RELEASE_WIDTH_MIN


# ------------------------------------------------------------------------------------------------ one show
# strike-shaft angles (degrees) in one turn; 0 is the rest (lock) angle
CUE = (5.0, 35.0)                            # E1's cue switch closed (quarters)
LIFT = (20.0, 110.0, 120.0)                  # lifter: rise from, top at, drop at (the stroke)
FEED = (150.0, 330.0)                        # the eccentric's gathering half-turn
LOCK = (350.0, 360.0)                        # the lock switch closed


def eccentric_phase() -> float:
    """The eccentric's phase: its forward (gathering) stroke spans FEED; it rests at the end of its return,
    where the guard holds the gathering pawl clear of the teeth (the rack can fall)."""
    return (FEED[0] + FEED[1]) / 2


def stroke_time_s(cycle_s: float = CYCLE_S) -> float:
    """Seconds from the shaft's start to the figure's stroke (the lifter's drop)."""
    return LIFT[2] / 360.0 * cycle_s


@dataclass
class ShowResult:
    turns: int
    strokes: int
    rack_home: bool


def simulate_show(t: TrainSpec, count: int, start_tooth: int | None = None) -> ShowResult:
    """A rack released onto the snail at `count`, gathered one tooth per turn by the pawl; the hook catches each
    tooth; the controller stops at the lock angle once the home switch is closed.
    `start_tooth` lets a test start from a rack left part-gathered."""
    tooth = count if start_tooth is None else start_tooth
    turns = strokes = 0
    for _ in range(40):
        turns += 1
        strokes += 1                         # each turn lifts and drops the figure once
        if tooth > 0:
            tooth -= 1                       # the pawl pushes 1.4 teeth; the hook catches the next tooth
        if tooth == 0:                       # home switch closed -> stop at the lock angle
            return ShowResult(turns, strokes, True)
    return ShowResult(turns, strokes, False)
