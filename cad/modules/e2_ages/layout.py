"""E2, the four ages and Death: the layout and the walk's selection logic (detail design, part 1).

Settled at the concept gate (docs/e2-design.md §9, Paul, PR #15, 6 Nov 2026):
- the ages ride a turntable, four 90° apart, its centre behind the back wall; each show turns it a
  quarter turn: in from the right doorway, strike, on past Death, out by the left doorway;
- the state train picks the age; three event motors (walk, quarters, hours);
- Death 78 mm at 1:8; the youth, man and old man as tall; the child ≈ ¾ of them.

Frame: X to the viewer's right, Y away from the viewer, Z up. Origin on Death's axis, on the top of
the hall's floor. Angles φ on the ring are measured at the ring's centre C from the front (−Y),
positive to the viewer's right; the ring turns with φ decreasing (right to left at the front, which
is clockwise seen from above).

Every number is tagged as in docs/reference-notes.md: [S] sourced, [D] derived, [E] estimate.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

# --- the hall [E: envelope §3; the 2011 photograph, docs/e2-design.md §2] -------------------------------
W = 183.0                                   # hall opening at 1:8 [E: 1.46 m on the plate]
FLOOR_T = 3.0
FLOOR_FRONT = -45.0                         # the floor's front edge (y) [E]
BACK_WALL = dict(y=(12.0, 16.0), x=64.0, h=72.0)          # [E: 0.92 of Death's height to the vault, photo]
PIER = dict(x=(W / 2, W / 2 + 10.0), y=(FLOOR_FRONT, -5.0), h=100.0)   # [E]
PEDESTAL = (24.0, 18.0, 6.0)                # x, y, z [E: 0.133 W wide, photo]

# --- the figures [S/E: e2-design §2, §9] ------------------------------------------------------------------
DEATH_H = 78.0                              # decided, Paul, PR #15
ADULT_H = 78.0                              # youth, man, old man: about as tall as Death [E: photo, Paul]
CHILD_H = 0.75 * ADULT_H                    # [E: Paul, "about ¾ the height of the old man"]
AGES = (("child", CHILD_H), ("youth", ADULT_H), ("man", ADULT_H), ("old_man", ADULT_H))   # quarter order
BASE_D = 14.0                               # a figure's base on the ring

# --- the bells [E: 0.113 W across, centres ±0.133 W, photo] ------------------------------------------------
BELL = dict(d=21.0, h=15.0, x=24.0, y=0.0, rim_z=16.0)   # ages' bell at +x (viewer's right), Death's at -x

# --- the ring (turntable) [D: through both doorways and 0.15 W in front of Death, e2-design §2] -----------
C = (0.0, 94.0)                             # the ring's centre, behind the back wall
R_PATH = 121.0                              # the figures' path
ANNULUS = (110.0, 134.0)                    # walking surface, flush with the floor (z -3 .. 0)
FLOOR_GAP = 0.5                             # between the ring and the static floor, each side
INNER_SKIRT = (108.0, 110.0, -16.0)         # r_in, r_out, z_bottom: the guide rollers run inside it
OUTER_BODY = (127.0, 131.0, -30.0)          # r_in, r_out, z_bottom: carries the teeth and the pegs
TEETH = dict(z=264, m=1.0, face=(-8.0, -3.0))   # external teeth at the top of the outer body
PEG = dict(d=2.5, r=(131.0, 135.0))         # radial pegs out of the outer body, one per age
PEG_Z = (-12.0, -16.0, -20.0, -24.0)        # selection pegs: one height per age (child .. old man), 4 mm apart
# Each age also has a waiting peg, as long as the selection pegs but below them all, about 35° behind it: when the
# age stands at the waiting position (φ 45°) its waiting peg is at the waiting stop, next to the bell stop. So both
# stops stand together at the bell station (part 2a, e2-design §10.8), on two shafts geared 1:1 in opposite senses:
# each arm swings out downstream, so a held peg's own push helps its release.
WAIT_PEG = dict(d=2.5, r=(131.0, 135.0), z=-28.0)

# --- the stations (φ, degrees) ----------------------------------------------------------------------------
PHI_WAIT = 45.0                             # the next age waits at the right doorway [S: photo]
PHI_BELL = 15.0                             # the age strikes here, just right of the ages' bell [D: x ≈ 32]
PHI_SPACING = 90.0                          # four ages
PHI_REST = tuple(PHI_WAIT + PHI_SPACING * k for k in range(4))   # at rest, the next age (k = 0) waits
# the stops (part 2a): two vertical shafts at R 141, the bell shaft upstream; each arm reaches in to R 132.2
STOP = dict(r=141.0, tip=132.2, w=2.0, h=2.5, wait_z=(-30.0, -26.0), swing=70.0, gear_teeth=12, gap=0.2)


def stop_delta() -> float:
    """Degrees by which a caught peg rests upstream of its arm's centreline [D]."""
    return math.degrees((PEG["d"] / 2 + STOP["w"] / 2 + STOP["gap"]) / STOP["tip"])


def stop_spacing() -> float:
    """The two stop shafts' centre distance: a pair of 12-tooth gears at m 1 with the library's shifts [D]."""
    from cad.lib.gears import Gear, centre_distance, pair_shifts
    s1, s2 = pair_shifts(STOP["gear_teeth"], STOP["gear_teeth"])
    return centre_distance(Gear(STOP["gear_teeth"], 1.0, shift=s1), Gear(STOP["gear_teeth"], 1.0, shift=s2))


def stop_phis() -> dict:
    """φ of each stop arm's centreline, and of the station where its peg rests [D]."""
    d = stop_delta()
    bell = PHI_BELL - d
    wait = bell - 2 * math.degrees(math.asin(stop_spacing() / 2 / STOP["r"]))
    return {"bell_arm": bell, "wait_arm": wait, "bell_station": PHI_BELL, "wait_station": wait + d}


WAIT_PEG_OFFSET = stop_phis()["wait_station"] - PHI_WAIT    # a waiting peg trails its age by this (deg, < 0)

# --- the walk [S: Paul's observation, 6 Nov 2026; D: below] ------------------------------------------------
WALK_ON_S = 10.0                            # [S] from the last stroke past Death to the left doorway
RING_SPEED = (PHI_BELL - (PHI_WAIT - PHI_SPACING)) / WALK_ON_S   # [D] 60° in 10 s = 6°/s = 1 rpm
PHASE_TRAVEL = dict(A=40.0, B=70.0)         # the most the ring can turn in each phase [D: program.ring_travel_limits]


def polar(phi_deg: float, r: float, centre=C) -> tuple[float, float]:
    """A point on the ring's plan at angle φ (0 = front, + = right) and radius r from C."""
    a = math.radians(phi_deg)
    return (centre[0] + r * math.sin(a), centre[1] - r * math.cos(a))


def phi_of(xy) -> float:
    """φ of a point in plan."""
    return math.degrees(math.atan2(xy[0] - C[0], -(xy[1] - C[1])))


# --- the walk program and its selection (e2-design §4.2-4.3) -----------------------------------------------
# Each show is one turn of the walk train's program cam: phase A (walk out: waiting finger out, bell finger in
# at the due age's peg height) and phase B (walk on: bell finger out, waiting finger in). Through its slip
# clutch the ring turns at most PHASE_TRAVEL in each phase. If no age is caught at the bell in phase A, the
# controller skips the strikes and runs the program again: each turn moves the ring one quarter.

@dataclass
class WalkResult:
    cycles: int                             # program turns run
    struck: int                             # the age caught at the bell (index) or -1
    waiting: int                            # the age caught at the waiting finger afterwards
    travel: float                           # total ring travel (deg)


def _first_arrival(phis: list[float], target: float, limit: float, candidates) -> tuple[int, float] | None:
    """The first of `candidates` whose φ comes down to `target` within `limit` degrees of travel."""
    best = None
    for k in candidates:
        d = (phis[k] - target) % 360.0
        if d <= limit + 1e-9 and (best is None or d < best[1]):
            best = (k, d)
    return best


def simulate_walk(waiting: int, due: int, max_cycles: int = 6) -> WalkResult:
    """Ring at rest with age `waiting` at PHI_WAIT; the state train says `due`. Run the program until the due
    age is caught at the bell, then the walk on."""
    phis = [(PHI_WAIT + PHI_SPACING * ((k - waiting) % 4)) % 360.0 for k in range(4)]
    travel = 0.0
    for cycle in range(1, max_cycles + 1):
        hit = _first_arrival(phis, PHI_BELL, PHASE_TRAVEL["A"], [due])          # phase A: only the due peg
        step = hit[1] if hit else PHASE_TRAVEL["A"]
        phis = [(p - step) % 360.0 for p in phis]
        travel += step
        caught = hit[0] if hit else -1
        hit_b = _first_arrival(phis, PHI_WAIT, PHASE_TRAVEL["B"], range(4))      # phase B: any peg
        if hit_b is None:
            raise AssertionError("no age reached the waiting finger in phase B")
        phis = [(p - hit_b[1]) % 360.0 for p in phis]
        travel += hit_b[1]
        if caught >= 0:
            return WalkResult(cycle, caught, hit_b[0], travel)
    raise AssertionError("the due age was never caught")


def walk_timing() -> dict:
    """Seconds for the normal show's walk out and walk on at RING_SPEED, and per program turn."""
    out = (PHI_WAIT - PHI_BELL) / RING_SPEED
    on = (PHI_BELL - (PHI_WAIT - PHI_SPACING)) / RING_SPEED
    return {"walk_out_s": out, "walk_on_s": on,
            "program_turn_s": (PHASE_TRAVEL["A"] + PHASE_TRAVEL["B"]) / RING_SPEED,
            "slip_A_deg": PHASE_TRAVEL["A"] - (PHI_WAIT - PHI_BELL),
            "slip_B_deg": PHASE_TRAVEL["B"] - (PHI_BELL - (PHI_WAIT - PHI_SPACING))}


def depth() -> dict:
    """The module's extent in plan from the floor's front edge to the ring's back [D]."""
    back = C[1] + max(ANNULUS[1], TEETH["z"] * TEETH["m"] / 2 + TEETH["m"])
    return {"front": FLOOR_FRONT, "ring_back": back, "depth": back - FLOOR_FRONT}
