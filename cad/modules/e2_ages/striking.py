"""E2 part 2b: the quarter and hour counting trains, geometry and logic only (docs/e2-design.md §12).

Each train is a classic rack and snail (concept gate §4.2, §4.4), adapted for printing:
- the **rack** is a lever on a stud behind the state arbor. Its tail finger falls onto the snail; its teeth
  are on an arc at a larger radius, so a fine snail step becomes a printable tooth (pitch 2.5 mm);
- the **gathering pawl** rides on a feed lever, coaxial with the rack, which an eccentric on the strike shaft
  rocks once per stroke. Each rock gathers one tooth; the rack hook catches it;
- the **rack hook** holds the rack between strokes. The walk train releases it (Paul, PR #21): a groove on the
  program shaft rocks a release shaft in phase A of every show, its arm turns the quarter hook out, and the quarter
  rack falls onto its snail: that sets the count. At the fourth quarter the quarter rack falls far enough for a pin
  on it to rock the hour trip shaft, which turns the hour hook out: the hour rack falls too. A show that does not
  walk (quiet hours) strikes nothing, Death included;
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


def arbor_yz():
    return (G.plan()["bell_shaft"][1], ARBOR_Z)


@dataclass(frozen=True)
class TrainSpec:
    name: str
    counts: int                              # 4 pairs, or 12 strokes
    r_teeth: float                           # the rack's pitch-arc radius
    r_first: float                           # the snail's radius for a count of 1
    x_rack: float                            # the rack's (and snail's) mid-plane


QUARTER = TrainSpec("quarter", 4, 30.0, 14.0, 20.0)
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


# ------------------------------------------------------------------------------------------------ the release
# Paul, PR #21 (8 Nov 2026), decision 1: the walk train releases the racks. A grooved disc under the program shaft's
# lock cam moves the follower of the quarter release shaft once per program turn, inside phase A (the walk out),
# and back before the lock notch at LOCK_N, where the strikes begin.
RELEASE_WINDOW = (30.0, 65.0, 80.0, 115.0)   # program degrees: the groove leaves its rest radius, reaches its release
#                                              radius, holds it, and is back [D: the margins in test_e2]
RELEASE_GROOVE_R = (13.2, 11.0)              # the groove's radius under the follower: at rest, and releasing
RELEASE_DISC_Z = (-62.0, -59.0)              # the release disc, on the program shaft under its lock cam
RELEASE_GROOVE = dict(depth=1.6, width=2.4)  # cut into the disc's underside; the follower's nub is 2.0 wide
RELEASE_CLEAR = 0.3                          # a released hook's tip clears the teeth's tips by at least this


def release_groove_radius(theta: float) -> float:
    """The release groove's radius under its follower at program angle theta [D]: harmonic rise and fall, so the
    follower is eased, never struck."""
    a, b, c, d = RELEASE_WINDOW
    r0, r1 = RELEASE_GROOVE_R
    t = theta % 360.0
    if a <= t < b:
        f = 0.5 - 0.5 * math.cos(math.pi * (t - a) / (b - a))
    elif b <= t < c:
        f = 1.0
    elif c <= t < d:
        f = 0.5 + 0.5 * math.cos(math.pi * (t - c) / (d - c))
    else:
        f = 0.0
    return r0 + (r1 - r0) * f


def release_pressure_angle_max(samples: int = 3600) -> float:
    """The release groove's largest pressure angle (deg) for its follower, which moves along the radius [D]."""
    worst, h = 0.0, 360.0 / samples
    for i in range(samples):
        t = i * h
        r = release_groove_radius(t)
        dr = (release_groove_radius(t + h / 2) - release_groove_radius(t - h / 2)) / math.radians(h)
        worst = max(worst, math.degrees(math.atan2(abs(dr), r)))
    return worst


def release_times_s(motor_rpm: float = G.MOTOR_RPM) -> dict:
    """Seconds from the start of a show's walk (phase A): the follower starts to move, the hook is out, the hook
    starts back, the hook is in, and the program stops at LOCK_N (the strikes start) [D: program.timing]."""
    dps = G.timing(motor_rpm)["program_deg_s"]
    a, b, c, d = RELEASE_WINDOW
    return {"lift": a / dps, "out": b / dps, "drop": c / dps, "back": d / dps, "strikes": G.LOCK_N / dps}


def hook_tip_turned(t: TrainSpec, turn: float):
    """The hook tip's centre with the hook turned out (CCW) by `turn` radians."""
    hk = hook_geometry(t)
    q, tip = hk["pivot"], hk["tip"]
    c, s = math.cos(turn), math.sin(turn)
    d = (tip[0] - q[0], tip[1] - q[1])
    return (q[0] + c * d[0] - s * d[1], q[1] + s * d[0] + c * d[1])


def hook_turn_to_clear(t: TrainSpec) -> float:
    """The least turn (rad) that lifts the hook's tip RELEASE_CLEAR above the teeth's tips [D]."""
    lo, hi = 0.0, 0.6
    for _ in range(60):
        m = (lo + hi) / 2
        if math.dist(pivot(), hook_tip_turned(t, m)) - TIP_R >= r_tip(t) + RELEASE_CLEAR:
            hi = m
        else:
            lo = m
    return hi


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


# ------------------------------------------------------------------------------------------------ layout (YZ)
ALPHA_H = math.radians(-24.0)                # where the hook and the gathering pawl meet the teeth, seen from the pivot
HOOK_ARM = 10.0                              # hook tip to hook pivot, along the teeth's motion
PAWL_ARM = 9.0                               # gathering pawl tip to its pivot on the feed lever
FEED_STROKE = 1.6                            # the feed lever's rock, in teeth (gathers 1, overshoots 0.3 each way)
FEED_REST = 0.3                              # the pawl rests this many teeth before the hooked face, lifted by the guard
LINK = 20.0                                  # the eccentric's strap: strike shaft to the feed lever's pin
TIP_R = 0.6                                  # the hook's and the pawl's rounded tips
TIP_GAP = 0.65                               # the hook's tip centre, before the hooked face (along the pitch arc)
TIP_LIFT = 1.0                               # the tips' centres above the tooth roots: clear of the next tooth's slope
X_PLANES = dict(                             # x ranges relative to each rack's mid-plane
    rack=(-1.5, 1.5), rim=(-4.0, 1.5),       # the teeth rim is wider than the rack, flush with its +X face (it prints
    pawl_tip=(-4.0, -1.6), hook_tip=(-1.3, 1.5),  # flat): the pawl works its -X part, the hook its +X part; their
    #                                              bodies lie beside the rim
    pawl=(-6.7, -4.2), feed=(-9.5, -7.0), link=(-12.3, -9.8), hook=(4.3, 6.8))


def _add(p, q, s=1.0):
    return (p[0] + s * q[0], p[1] + s * q[1])


def unit(a: float):
    return (math.cos(a), math.sin(a))


def ccw(a: float):
    """The direction a point at angle a (about the pivot) moves when the rack turns CCW (its tail falls)."""
    return (-math.sin(a), math.cos(a))


def r_tip(t: TrainSpec) -> float:
    return t.r_teeth + TOOTH / 2


def r_root(t: TrainSpec) -> float:
    return t.r_teeth - TOOTH / 2


def hook_geometry(t: TrainSpec) -> dict:
    """The hook: its tip sits just before the hooked tooth's radial face, its pivot along the teeth's motion
    (the face pushes the tip toward the pivot: it locks)."""
    p = pivot()
    a_tip = ALPHA_H + TIP_GAP / t.r_teeth
    tip = _add(p, unit(a_tip), r_root(t) + TIP_LIFT)
    q = _add(tip, ccw(ALPHA_H), HOOK_ARM)
    return {"tip": tip, "pivot": q, "a_tip": a_tip}


def feed_geometry(t: TrainSpec) -> dict:
    """The feed lever (coaxial with the rack) and its gathering pawl, at rest (the end of the return stroke)."""
    p = pivot()
    d = tooth_angle(t)
    a_rest = ALPHA_H + FEED_REST * d
    tip = _add(p, unit(a_rest), r_root(t) + TIP_LIFT)
    q = _add(tip, ccw(a_rest), PAWL_ARM)              # the pawl's pivot pin on the feed lever (and the strap's pin)
    rq = math.dist(p, q)
    a_q = math.atan2(q[1] - p[1], q[0] - p[0])
    k = _add(q, ccw(a_q), -LINK)                       # the strike shaft: the strap pulls the pin along its arc
    stroke = FEED_STROKE * d
    return {"tip": tip, "pin": q, "r_pin": rq, "a_pin": a_q, "shaft": k, "stroke": stroke,
            "eccentric": rq * stroke / 2, "a_rest": a_rest}


# ------------------------------------------------------------------------------------------------ the rack springs
# Each rack's toothed side outweighs its tail, so a spring pulls the spoke up (the tail down) [D: test_e2]. M2's
# counting-lever return spring, accepted by Paul (D13): Sodemann E00940110500S, AISI 302, d 0.28, De 2.39,
# L0 12.70 (inside the hooks), F0 0.22 N, R 0.17 N/mm, Ln 26.16 [S: ressorts-sodemann.fr/e00940110500s].
RACK_SPRING = dict(part="Sodemann E00940110500S", L0=12.70, F0=0.22, R=0.17, Ln=26.16, De=2.39)
SPRING_PIN_R = 10.0                          # the spring's pin on the spoke, from the rack's pivot
SPRING_LENGTH_HOME = 20.0                    # hook to hook at home (gathered): stretched 7.3 mm


def spring_points(t: TrainSpec, theta: float):
    """(pin, anchor) of the rack spring with the rack at angle theta; the anchor lies straight above the pin at
    home, so the spring stays nearly vertical."""
    p = pivot()
    th = rack_angles(t)
    g_mid = ALPHA_H - (th[0] + th[-1]) / 2                  # the spoke's direction in the rack frame
    pin = _add(p, unit(g_mid + theta), SPRING_PIN_R)
    pin_home = _add(p, unit(g_mid + th[0]), SPRING_PIN_R)
    anchor = (pin_home[0], pin_home[1] + SPRING_LENGTH_HOME)
    return pin, anchor


def spring_torque(t: TrainSpec, theta: float) -> float:
    """N·mm the spring turns the rack CCW (tail down) at rack angle theta [D: F = F0 + R·stretch]."""
    p = pivot()
    pin, anc = spring_points(t, theta)
    length = math.dist(pin, anc)
    f = RACK_SPRING["F0"] + RACK_SPRING["R"] * (length - RACK_SPRING["L0"])
    u = ((anc[0] - pin[0]) / length, (anc[1] - pin[1]) / length)
    r = (pin[0] - p[0], pin[1] - p[1])
    return f * (r[0] * u[1] - r[1] * u[0])


def spring_stretch(t: TrainSpec, theta: float) -> float:
    pin, anc = spring_points(t, theta)
    return math.dist(pin, anc) - RACK_SPRING["L0"]
