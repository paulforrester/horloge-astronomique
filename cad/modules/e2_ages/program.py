"""E2 part 2a: the walk train's program (docs/e2-design.md §10.8). Pure geometry, no CAD.

One program turn per show. The program shaft (gear 72, driven by the walk compound's 12') carries the grooved
program cam and the lock cam. The cam's follower is a push rod to the crank on the waiting stop's shaft; a pair of
12-tooth gears turns the bell stop's sleeve the other way:

    state A (walk out):  the bell arm in,  the waiting arm swung out 70° downstream
    state B (walk on):   the waiting arm in, the bell arm swung out 70° downstream

    program  0 .. 45     BA: the bell arm swings in, then the waiting arm lets the waiting age go
            45 .. N      A: the motor stops at the lock notch N; the age is at the bell (the strikes)
             N .. N+45   AB: the waiting arm swings in, then the bell arm lets the struck age go
          N+45 .. 360    B: the walk on; the motor stops at the lock notch 360 (rest)

Frame as in layout.py: X to the viewer's right, Y away from the viewer, Z up; φ at the ring's centre C.
"""
from __future__ import annotations

import math

from cad.lib.gears import Gear, centre_distance, pair_shifts
from cad.modules.e2_ages import layout as L

PROG_RATIO = 6                               # 12' : 72 (one program turn = 6 turns of the walk shaft)
WALK_PINION = 16
WALK_THETA = -60.0                           # the walk pinion's direction from C (plan angle from +X)
PROG_DIR = 110.0                             # the program shaft's direction from the walk shaft (plan angle)
TRANSITION = 45.0                            # program degrees per change of state [D: pressure angle, below]
LOCK_N = 138.75                              # program degrees: the lock notch at the end of phase A [D: below]
LOCK_NOTCHES = (LOCK_N, 360.0)
CRANK = 5.0                                  # the waiting shaft's crank radius
CRANK_SIDE = -1                              # the crank's pin lies on the side of the rod away from the bell shaft
R_GROOVE_A = 20.0                            # the groove's radius in state A [D: pressure angle ≤ 36°, below]
CATCH_MARGIN = 1.0                           # an arm holds a peg with at least this radial overlap
CLEAR_MARGIN = 0.5                           # an arm swung out clears the peg ends by at least this


def ring_deg_per_program_deg() -> float:
    return PROG_RATIO * WALK_PINION / L.TEETH["z"]


def swing(theta: float) -> float:
    """The stops' swing ψ (deg): 0 in state A, STOP['swing'] in state B, a harmonic ramp in each change."""
    t, w, sw = theta % 360.0, TRANSITION, L.STOP["swing"]
    if t < w:                                           # BA
        return sw * (0.5 + 0.5 * math.cos(math.pi * t / w))
    if t < LOCK_N:
        return 0.0
    if t < LOCK_N + w:                                  # AB
        return sw * (0.5 - 0.5 * math.cos(math.pi * (t - LOCK_N) / w))
    return sw


def arms(theta: float) -> dict:
    """Each arm's swing out from its radial (holding) position, degrees."""
    psi = swing(theta)
    return {"bell": psi, "wait": L.STOP["swing"] - psi}


def tip_radius(alpha: float) -> float:
    """Distance from C of an arm's tip swung out by alpha [D: the triangle C, shaft, tip]."""
    rs, lt = L.STOP["r"], L.STOP["r"] - L.STOP["tip"]
    return math.sqrt(rs * rs + lt * lt - 2 * rs * lt * math.cos(math.radians(alpha)))


def _alpha_for_radius(r: float) -> float:
    rs, lt = L.STOP["r"], L.STOP["r"] - L.STOP["tip"]
    return math.degrees(math.acos((rs * rs + lt * lt - r * r) / (2 * rs * lt)))


def alpha_catch() -> float:
    """An arm swung out by less than this still holds a peg with CATCH_MARGIN of overlap."""
    return _alpha_for_radius(L.PEG["r"][1] - CATCH_MARGIN)


def alpha_clear() -> float:
    """An arm swung out by more than this lets every peg by."""
    return _alpha_for_radius(L.PEG["r"][1] + CLEAR_MARGIN)


def _crossing(f, lo: float, hi: float) -> float:
    """The program angle in [lo, hi] where the monotonic f changes sign (bisection)."""
    a, b = lo, hi
    for _ in range(60):
        m = (a + b) / 2
        if (f(a) > 0) == (f(m) > 0):
            a = m
        else:
            b = m
    return (a + b) / 2


def events() -> dict:
    """Program angles where each arm becomes able to hold or lets go (BA and AB) [D]."""
    ac, ak, w = alpha_clear(), alpha_catch(), TRANSITION
    return {
        "bell_holds": _crossing(lambda t: arms(t)["bell"] - ak, 0.0, w),          # BA: the bell arm is in
        "wait_lets_go": _crossing(lambda t: arms(t)["wait"] - ac, 0.0, w),        # BA: the waiting age walks
        "wait_holds": _crossing(lambda t: arms(t)["wait"] - ak, LOCK_N, LOCK_N + w),   # AB
        "bell_lets_go": _crossing(lambda t: arms(t)["bell"] - ac, LOCK_N, LOCK_N + w),
    }


def ring_travel_limits() -> dict:
    """The most the ring can turn in each phase (deg) [D]:
    A: from the waiting arm's release in BA to the motor's stop at the lock notch N;
    B: from the bell arm's release in AB to the stop at 360;
    free: in a skipped show, from the waiting release until the waiting arm can hold again;
    turn: from the waiting release to the end of the program turn."""
    k, e = ring_deg_per_program_deg(), events()
    return {"deg_per_program_deg": k,
            "A": k * (LOCK_N - e["wait_lets_go"]),
            "B": k * (360.0 - e["bell_lets_go"]),
            "free": k * (e["wait_holds"] - e["wait_lets_go"]),
            "turn": k * (360.0 - e["wait_lets_go"])}


def lock_closed(theta: float, width: float = 2.0) -> bool:
    """The lock switch closes (its roller drops into a notch) at the end of each phase."""
    t = theta % 360.0
    return any(abs(((t - n + 180.0) % 360.0) - 180.0) <= width / 2 for n in LOCK_NOTCHES)


# ------------------------------------------------------------------------------------------------ plan positions
def gears() -> dict:
    """The walk train's gears: motor pinion 12 -> compound 24 + 12' -> program 72; walk pinion 16 -> ring."""
    s12, s24 = pair_shifts(12, 24)
    s12p, s72 = pair_shifts(12, 12 * PROG_RATIO)
    sr, sp = pair_shifts(L.TEETH["z"], WALK_PINION)
    sg = pair_shifts(L.STOP["gear_teeth"], L.STOP["gear_teeth"])
    g = {"m12": Gear(12, 1.0, shift=s12), "g24": Gear(24, 1.0, shift=s24), "g12p": Gear(12, 1.0, shift=s12p),
         "g72": Gear(12 * PROG_RATIO, 1.0, shift=s72), "ring": Gear(L.TEETH["z"], L.TEETH["m"], shift=sr),
         "p16": Gear(WALK_PINION, L.TEETH["m"], shift=sp), "stop_b": Gear(L.STOP["gear_teeth"], 1.0, shift=sg[0]),
         "stop_w": Gear(L.STOP["gear_teeth"], 1.0, shift=sg[1])}
    return g


def plan() -> dict:
    """Plan positions (x, y) of the walk shaft, the program shaft and the two stop shafts [D]."""
    g = gears()
    cd = centre_distance(g["ring"], g["p16"])
    pp = (L.C[0] + cd * math.cos(math.radians(WALK_THETA)), L.C[1] + cd * math.sin(math.radians(WALK_THETA)))
    cdp = centre_distance(g["g12p"], g["g72"])
    pr = (pp[0] + cdp * math.cos(math.radians(PROG_DIR)), pp[1] + cdp * math.sin(math.radians(PROG_DIR)))
    ph = L.stop_phis()
    return {"walk": pp, "program": pr, "bell_shaft": L.polar(ph["bell_arm"], L.STOP["r"]),
            "wait_shaft": L.polar(ph["wait_arm"], L.STOP["r"]), "walk_cd": cd, "program_cd": cdp}


def _unit(v):
    n = math.hypot(*v)
    return (v[0] / n, v[1] / n)


def radial_dir(shaft) -> float:
    """Plan angle (deg) from a stop shaft toward C: its arm's holding direction."""
    return math.degrees(math.atan2(L.C[1] - shaft[1], L.C[0] - shaft[0]))


def crank() -> dict:
    """The push rod and the crank on the waiting shaft [D].

    The rod is a radial translating follower: its line passes through the program shaft P. Its far end is a yoke
    (a slot across the rod) round the crank pin. The crank's two positions (states A and B, 70° apart) are
    symmetric about the normal to the rod, so the pin's lateral travel in the yoke is least; the rod's line passes
    CRANK·cos(35°)·0.9 to the side of the waiting shaft away from the bell shaft."""
    p = plan()
    P, S, B = p["program"], p["wait_shaft"], p["bell_shaft"]
    u0 = _unit((S[0] - P[0], S[1] - P[1]))                     # P toward S
    n0 = (-u0[1], u0[0])
    side = 1 if (B[0] - S[0]) * n0[0] + (B[1] - S[1]) * n0[1] < 0 else -1     # +n0 if B lies on the -n0 side
    lat = CRANK * (1 + math.sin(math.radians(90 - L.STOP["swing"] / 2))) / 2  # the pin's mean lateral offset
    target = (S[0] + side * lat * n0[0], S[1] + side * lat * n0[1])
    u = _unit((target[0] - P[0], target[1] - P[1]))
    n = (-u[1], u[0])
    # crank angles (plan, deg) for A and B: the pin on the `side`, symmetric about the normal to u
    beta = math.degrees(math.atan2(side * n[1], side * n[0]))
    # the waiting arm swings out CCW (positive) from B to A, so the crank turns CCW from B to A
    g_b, g_a = beta - L.STOP["swing"] / 2, beta + L.STOP["swing"] / 2

    def pin(gam):
        return (S[0] + CRANK * math.cos(math.radians(gam)), S[1] + CRANK * math.sin(math.radians(gam)))

    def along(q):
        return (q[0] - P[0]) * u[0] + (q[1] - P[1]) * u[1]

    rod_len = along(pin(g_a)) - R_GROOVE_A                    # the follower pin to the crank pin, along u
    r_b = along(pin(g_b)) - rod_len
    return {"P": P, "S": S, "u": u, "n": n, "side": side, "gamma_A": g_a, "gamma_B": g_b, "pin": pin,
            "along": along, "rod_len": rod_len, "r_A": R_GROOVE_A, "r_B": r_b, "lat_range": (
                min(abs((pin(g)[0] - P[0]) * n[0] + (pin(g)[1] - P[1]) * n[1]) for g in (g_a, beta, g_b)),
                max(abs((pin(g)[0] - P[0]) * n[0] + (pin(g)[1] - P[1]) * n[1]) for g in (g_a, beta, g_b)))}


def groove_radius(theta: float, cg: dict | None = None) -> float:
    """The groove's radius under the follower at program angle theta [D: the crank's position for the swing]."""
    cg = cg or crank()
    gam = cg["gamma_A"] - arms(theta)["bell"]                 # ψ = 0 in A; the crank turns CW from A to B
    return cg["along"](cg["pin"](gam)) - cg["rod_len"]


def pressure_angle_max(samples: int = 3600) -> float:
    """The program cam's largest pressure angle (deg) for the radial translating follower [D]."""
    cg = crank()
    worst = 0.0
    h = 360.0 / samples
    for i in range(samples):
        t = i * h
        r = groove_radius(t, cg)
        dr = (groove_radius(t + h / 2, cg) - groove_radius(t - h / 2, cg)) / math.radians(h)
        worst = max(worst, math.degrees(math.atan2(abs(dr), r)))
    return worst


MOTOR_RPM = 32.0                             # [E] the walk gearmotor's speed under load ⚠ (trimmed by PWM, §11.8)


def timing(motor_rpm: float = MOTOR_RPM) -> dict:
    """Seconds of one show's walk at a given gearmotor speed [D]: the motor pinion 12 drives the compound 24, which
    turns the walk shaft (pinion 16 on the ring 264) and, through 12'/72, the program."""
    walk_rpm = motor_rpm * 12 / 24
    prog_dps = walk_rpm / PROG_RATIO * 6.0                    # program degrees per second
    ring_dps = walk_rpm * WALK_PINION / L.TEETH["z"] * 6.0
    e = events()
    walk_out = (L.PHI_WAIT - L.PHI_BELL) / ring_dps
    walk_on = (L.PHI_BELL - (L.PHI_WAIT - L.PHI_SPACING)) / ring_dps
    hold_ba = e["wait_lets_go"] / prog_dps
    hold_ab = (e["bell_lets_go"] - LOCK_N) / prog_dps
    a_run = LOCK_N / prog_dps
    b_run = (360.0 - LOCK_N) / prog_dps
    return {"ring_deg_s": ring_dps, "program_deg_s": prog_dps, "hold_before_walk_out_s": hold_ba,
            "walk_out_s": walk_out, "slip_before_strikes_s": a_run - hold_ba - walk_out, "phase_A_s": a_run,
            "hold_before_walk_on_s": hold_ab, "walk_on_s": walk_on, "slip_at_rest_s": b_run - hold_ab - walk_on,
            "phase_B_s": b_run, "program_turn_s": a_run + b_run}
