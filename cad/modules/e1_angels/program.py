"""E1 detail design, part 1: the count-wheel program, the follower lever and the glass drive (docs/e1-design.md §16).
Pure geometry and timing, no CAD.

One forward-only gearmotor turns the bell shaft B. The bell shaft carries the snail (one stroke per turn) and the
bell lock (one notch). Through 12/48 and 12/60 it turns the count wheel W once in 20 turns:

    W   0 .. 180°   ten stroke turns: 1 + 2 + 3 + 4 strokes of the hour, one per E2 cue
    W 180 .. 360°   ten silent turns: the silencing cam holds the follower lever off the snail, and the mutilated
                    gear (18 teeth over 180°) turns the cross shaft C half a turn: the crank, yoke, rack and
                    pinion at the far genie turn the glass half a turn
    W 360°          the home switch's notch: the hour's work is done

Angles in the bell tower are in its (y, z) plane, measured from +y towards +z (right-handed about +X). The bell
shaft's angle u is measured from its rest (the lock notch); the count wheel's angle c from home.

Frame: M1's (docs/m1-design.md §9.2): origin at the dial's centre on its face, +X right, +Y up, +Z towards the
viewer.
"""
from __future__ import annotations

import math

from cad.lib.gears import Gear, centre_distance, pair_shifts

M = 1.0                                   # module (CLAUDE.md: a parameter; 1.0 with the 0.4 mm nozzle)
BACKLASH = 0.15
MOTOR_RPM = 200.0                         # [E] the gearmotor's speed under load; PWM trims it
TURNS_PER_HOUR = 20                       # bell-shaft turns per count-wheel turn
STROKES_PER_HOUR = 10                     # [D] 1 + 2 + 3 + 4
QUARTER_STROKES = (1, 2, 3, 4)            # :15, :30, :45, :00

# --- the trains (teeth) ------------------------------------------------------------------------------------------
Z_B, Z_I1 = 12, 48                        # bell shaft 12 -> intermediate 48
Z_I2, Z_W = 12, 60                        # intermediate 12 -> count wheel 60
Z_SECTOR, Z_C = 36, 36                    # the mutilated gear on W (18 teeth kept) -> cross shaft 36
SECTOR_TEETH = 18
Z_PINION = 12                             # the glass arbor's pinion, driven by the rack

# --- the bell tower's axes, (y, z) -------------------------------------------------------------------------------
B = (-7.0, -46.0)                         # bell shaft
W = (-41.0, -80.0)                        # count wheel
THETA_WC = 228.0                          # direction W -> C; ≡ 8 (mod 10) so the sector keeps 18 lattice teeth
PF = (-20.0, -62.0)                       # the follower lever's pivot pin

# --- the snail on B: rest in the dwell, drop at U_DROP, rise from U_RISE[0] to U_RISE[1] -------------------------
R_MIN, R_MAX = 7.0, 11.0
U_DROP = 30.0                             # [deg] the stroke comes this far after the rest: latency
U_RISE = (60.0, 280.0)
ROLLER_D = 4.0
BANK_CLEAR = 0.4                          # the arm banks this far (at the roller) before the roller meets R_MIN

# --- the follower lever: roller, wire tip and silencing pin, all on one straight lever along z ---------------
A_ROLLER, A_TIP, A_PIN = 16.0, 36.0, 18.0   # distances from PF: roller and tip forward (+z), pin behind (-z)
PIN_D = 2.0
SILENCE_LIFT = 0.5                        # the silencing cam holds the roller this far beyond R_MAX
SILENCE_RAMPS = ((176.5, 179.0), (356.0, 358.5))   # c: up in the 10th turn's high dwell; down in the 20th's
CAM_CLEAR = 0.3

# --- the sceptre arm ---------------------------------------------------------------------------------------------
COCK_DEG = 30.0                           # the arm's swing from cocked (rest) to the bell

# --- the home switch: a notch on W, wide enough for exactly one bell-lock stop -----------------------------------
HOME_NOTCH = (351.0, 369.0)               # c, degrees (mod 360)


def gears() -> dict:
    sb, si = pair_shifts(Z_B, Z_I1)
    si2, sw = pair_shifts(Z_I2, Z_W)
    g = {"b12": Gear(Z_B, M, shift=sb, backlash=BACKLASH), "i48": Gear(Z_I1, M, shift=si, backlash=BACKLASH),
         "i12": Gear(Z_I2, M, shift=si2, backlash=BACKLASH), "w60": Gear(Z_W, M, shift=sw, backlash=BACKLASH),
         "sector": Gear(Z_SECTOR, M, backlash=BACKLASH), "c36": Gear(Z_C, M, backlash=BACKLASH)}
    sp, _ = pair_shifts(Z_PINION, 60)                      # the pinion's own anti-undercut shift (rack: any)
    g["pinion"] = Gear(Z_PINION, M, shift=sp, backlash=BACKLASH)
    return g


def ratio() -> float:
    """Count-wheel turns per bell-shaft turn [D]."""
    return (Z_B / Z_I1) * (Z_I2 / Z_W)


def _polar(o, r, deg):
    return (o[0] + r * math.cos(math.radians(deg)), o[1] + r * math.sin(math.radians(deg)))


def axes() -> dict:
    """B, I, W, C in the (y, z) plane. I is where the 12/48 and 12/60 centre distances meet (the solution behind
    the line B-W); C is 36 from W at THETA_WC."""
    g = gears()
    d1, d2 = centre_distance(g["b12"], g["i48"]), centre_distance(g["i12"], g["w60"])
    dx, dy = W[0] - B[0], W[1] - B[1]
    d = math.hypot(dx, dy)
    a = (d1 ** 2 - d2 ** 2 + d ** 2) / (2 * d)
    h = math.sqrt(d1 ** 2 - a ** 2)
    mx, my = B[0] + a * dx / d, B[1] + a * dy / d
    cands = [(mx + h * dy / d, my - h * dx / d), (mx - h * dy / d, my + h * dx / d)]
    i = min(cands, key=lambda p: p[1])                     # the one further back (more negative z)
    c = _polar(W, centre_distance(g["sector"], g["c36"]), THETA_WC)
    return {"B": B, "I": i, "W": W, "C": c, "d_BI": d1, "d_IW": d2}


# ------------------------------------------------------------------------------------------------ the snail
def _harmonic(t):
    return 0.5 - 0.5 * math.cos(math.pi * t)


def snail_radius(u: float) -> float:
    """The snail's radius under the roller, the bell shaft at u degrees from rest."""
    u %= 360.0
    if u < U_DROP or u >= U_RISE[1]:
        return R_MAX
    if u < U_RISE[0]:
        return R_MIN
    return R_MIN + (R_MAX - R_MIN) * _harmonic((u - U_RISE[0]) / (U_RISE[1] - U_RISE[0]))


def snail_pressure_angle(samples: int = 3600) -> float:
    """Largest pressure angle (deg) on the rise, a radial roller follower [D]."""
    worst = 0.0
    for k in range(samples):
        u = U_RISE[0] + (U_RISE[1] - U_RISE[0]) * k / samples
        du = 1e-3
        dr = (snail_radius(u + du) - snail_radius(u - du)) / math.radians(2 * du)
        worst = max(worst, math.degrees(math.atan2(abs(dr), snail_radius(u) + ROLLER_D / 2)))
    return worst


# ------------------------------------------------------------------------------------------------ the count wheel
def count_angle(turns: float) -> float:
    """The count wheel's angle (deg) after this many bell-shaft turns from home."""
    return 360.0 * turns * ratio()


def silencing(c: float) -> float:
    """0..1: how far the silencing cam has lifted the lever (1 = the roller SILENCE_LIFT beyond R_MAX)."""
    c %= 360.0
    (u0, u1), (d0, d1) = SILENCE_RAMPS
    if c < u0:
        return 0.0
    if c < u1:
        return _harmonic((c - u0) / (u1 - u0))
    if c < d0:
        return 1.0
    return 1.0 - _harmonic((c - d0) / (d1 - d0))


def roller_radius(u: float, c: float) -> float:
    """The radius the roller sits at about B. The snail sets it; after the drop the spring flicks the arm to its
    bank, so the roller stops BANK_CLEAR short of R_MIN; the silencing cam can hold the lever further out."""
    s = silencing(c)
    r = snail_radius(u)
    if s > 0.0:
        return max(r, R_MAX + SILENCE_LIFT * s)
    return max(r, R_MIN + BANK_CLEAR) if r < R_MAX else r


def lever_angle(r_roller: float) -> float:
    """The lever's angle (deg, + = roller moves +y), the roller at radius r_roller from B (0 when cocked)."""
    return math.degrees(math.asin((R_MAX - r_roller) / A_ROLLER))


def silencing_cam_radius(c: float) -> float:
    """The silencing cam's radius under the pin at count angle c [D]. 'Off', it stays CAM_CLEAR clear of the pin
    even with the arm at its bank; 'on', it holds the roller SILENCE_LIFT beyond R_MAX."""
    pin_y_rest = PF[0]                                        # the lever along z: roller cocked at R_MAX
    w_to_pin = pin_y_rest - W[0]                             # the pin is straight above W in y (same z)
    s_bank = (R_MAX - (R_MIN + BANK_CLEAR)) / A_ROLLER       # sin of the lever angle at the bank
    r_off = w_to_pin - A_PIN * s_bank - PIN_D / 2 - CAM_CLEAR
    r_on = w_to_pin + A_PIN * SILENCE_LIFT / A_ROLLER - PIN_D / 2
    return r_off + (r_on - r_off) * silencing(c)


def silencing_cam_profile(a: float, window: float = 12.0, steps: int = 241) -> float:
    """The silencing cam's radius at its local angle a (deg; material at a meets the pin at c = -a): the envelope
    that keeps it PIN_D / 2 from the pin's centre at every nearby count angle [D]. Where silencing is on, the pin's
    centre is where the cam holds it; where off, the pin may be as low as the arm's bank, so the cam clears that."""
    rp = PIN_D / 2
    r_off = silencing_cam_radius(0.0)
    best = float("inf")
    for k in range(steps):
        d = -window + 2 * window * k / (steps - 1)            # the material's angle from the pin's direction
        c = (-a + d) % 360.0
        rho = silencing_cam_radius(c) + rp if silencing(c) > 0 else r_off + rp + CAM_CLEAR
        dr = math.radians(d)
        h = rho * math.sin(dr)
        if abs(h) >= rp:
            continue
        best = min(best, rho * math.cos(dr) - math.sqrt(rp * rp - h * h) - (CAM_CLEAR if silencing(c) == 0 else 0.0))
    return best


def strikes_in_turn(k: int) -> bool:
    """Bell-shaft turn k (0-based from home) drops the arm onto the bell."""
    return (k % TURNS_PER_HOUR) < STROKES_PER_HOUR


def cross_shaft_turn(c: float) -> float:
    """Degrees the cross shaft has turned in a count-wheel turn, c in 0..360: still until 180°, then 1:1 [D]."""
    return min(max(c - 180.0, 0.0), 180.0)


# ------------------------------------------------------------------------------------------------ the glass
def pinion_pitch_radius() -> float:
    return M * Z_PINION / 2


def crank_radius() -> float:
    """Half a pinion turn of rack is π·r_p; the Scotch yoke's stroke is 2r, so r = π·r_p / 2 [D]."""
    return math.pi * pinion_pitch_radius() / 2


def glass_angle(cross_deg: float) -> float:
    """The glass's turn (deg) for a cross-shaft turn from a dead centre: 90 (1 − cos θ) [D]."""
    return 90.0 * (1 - math.cos(math.radians(cross_deg)))


def overrun_error(deg: float) -> float:
    """The glass's error (deg) if the crank stops this far past a dead centre [D]."""
    return 90.0 * (1 - math.cos(math.radians(deg)))


# ------------------------------------------------------------------------------------------------ timing
def timing(rpm: float = MOTOR_RPM) -> dict:
    turn = 60.0 / rpm
    return {"turn_s": turn, "latency_s": U_DROP / 360.0 * turn,
            "glass_s": (TURNS_PER_HOUR - STROKES_PER_HOUR) * turn,
            "pair_period_s": 3.0, "e2_age_after_cue_s": 1.0}


def simulate(shows, start_turns: int = 0, makeup: bool = True) -> dict:
    """The firmware's view (§15.3–15.4). ``shows`` is a list of quarters (1..4) that run, in order; None is a show
    skipped (fault, power cut, catch-up). Each run show strikes its n cues; at :00 the controller then runs to home.
    Before each show (E2's resync), if the count wheel is behind, the controller runs the missing turns alone (B).
    Returns the bell strokes heard, glass turns and the final count position (bell-shaft turns from home)."""
    k = start_turns % TURNS_PER_HOUR
    log = {"strokes": 0, "makeup_strokes": 0, "glass_turns": 0, "in_step": True}
    for q in shows:
        if q is None:
            continue
        before = sum(QUARTER_STROKES[:q - 1])               # strokes the count should already show this hour
        if k != before and not makeup:
            log["in_step"] = False
        while makeup and k != before:                       # run on alone: strokes, and the glass if passing home
            if strikes_in_turn(k):
                log["makeup_strokes"] += 1
            k += 1
            if k == TURNS_PER_HOUR:
                log["glass_turns"] += 1
                k = 0
        for _ in range(QUARTER_STROKES[q - 1]):
            if strikes_in_turn(k):
                log["strokes"] += 1
            k += 1
        if q == 4:                                          # the hour: run on to home, silently, turning the glass
            if k == STROKES_PER_HOUR:
                log["glass_turns"] += 1
                k = 0
            else:
                log["in_step"] = False
    log["final_turns"] = k
    return log


def tip_travel() -> float:
    """The wire's pull (mm) at the follower lever's tip, from the bank to cocked [D]."""
    return (R_MAX - (R_MIN + BANK_CLEAR)) * A_TIP / A_ROLLER
