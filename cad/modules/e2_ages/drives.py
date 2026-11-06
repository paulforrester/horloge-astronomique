"""E2 part 2a: the walk drive and the state module (docs/e2-design.md §10.8).

Walk drive (one DC gearmotor, decided: three event motors, §9.2; a program cam, §9.7):
- the gearmotor's 12-tooth pinion drives the input compound (24 + 12'), free on the walk shaft; a wave washer
  and a collar press the compound's friction boss against a hub fixed on the shaft (the slip clutch); the
  walk pinion 16 at the top of the shaft turns the ring;
- the compound's 12' drives the program gear 60 (1:5): one program turn per show. The program shaft carries,
  below the deck, a grooved program cam and a lock cam with two notches (a microswitch stops the motor at the
  end of each phase);
- the program cam's follower is a push rod to a crank on the stop sleeve, which turns the stop shaft 70°
  between state A (bell arm in) and state B (waiting arm in); the shaft slides through the sleeve on a cross
  pin, so the age cam can set its height;
- a Hall under the ring at the bell station sees a magnet under each age: an age was caught.

State module (E2's own stepper, 1 rev/h legal time, decided at the M1 gate; D16 plug-in from the right):
- the state arbor (along X under the front of the hall) carries the age cam (under the stop shaft), the
  quarter snail (part 2b's quarter rack falls on it), the index disc, and the 12-tooth pinion of the 12:1
  motion work (12/48 · 15/45, as M1); the hour wheel carries the hour snail on a tube; a witness Hall reads
  the hour snail at 12:00.

Frame as in mechanism.py: X right, Y away from the viewer, Z up.
"""
from __future__ import annotations

import math

import build123d as bd

from cad.lib import motor_mount as MM
from cad.lib import parts
from cad.lib.gears import Gear, centre_distance, mesh_rotation, pair_shifts, spur_gear
from cad.lib.hardware import BEARINGS
from cad.modules.e2_ages import layout as L

M = 1.0
PROG_RATIO = 5                               # 12' / 60
PROG_DIR_DEG = 110.0                         # the program shaft, seen from the walk shaft
PROG_PHASES = dict(BA=(0.0, 5.0), A=(5.0, 132.0), AB=(132.0, 137.0), B=(137.0, 360.0))   # program degrees
LOCK_NOTCHES = (132.0, 360.0)
CRANK = 6.0                                  # the stop sleeve's crank radius
HALL = (8.0, 6.0, 3.0)                       # DRV5032 on a small board
MAGNET = (5.0, 2.0)
STATE_Z = -80.0                              # the state arbor's axis
SNAIL_Q = (14.0, 12.0, 10.0, 8.0)            # quarter snail radii for 1..4 pairs (part 2b's rack reads it)
SNAIL_H = tuple(20.0 - 0.9 * k for k in range(12))   # hour snail radii for 1..12 strokes [D: 0.9 mm per hour]


def at(shape, xy, z=0.0):
    return shape.moved(bd.Location((xy[0], xy[1], z)))


def along_x(shape, x0, y, z):
    """A shape built along +Z, laid along +X starting at x0, its axis at (y, z)."""
    return shape.rotate(bd.Axis.Y, 90).moved(bd.Location((x0, y, z)))


def polar_xy(origin, r, deg):
    return (origin[0] + r * math.cos(math.radians(deg)), origin[1] + r * math.sin(math.radians(deg)))


# ------------------------------------------------------------------------------------------------ program
def program_state(theta: float) -> float:
    """0 in state A (bell arm in), 1 in state B (waiting arm in); a cosine ramp in each transition."""
    t = theta % 360.0
    (a0, a1), (b0, b1) = PROG_PHASES["BA"], PROG_PHASES["AB"]
    if a0 <= t < a1:
        return 0.5 + 0.5 * math.cos(math.pi * (t - a0) / (a1 - a0))
    if PROG_PHASES["A"][0] <= t < PROG_PHASES["A"][1]:
        return 0.0
    if b0 <= t < b1:
        return 0.5 - 0.5 * math.cos(math.pi * (t - b0) / (b1 - b0))
    return 1.0


def ring_travel_limits() -> dict:
    """Ring degrees per program degree, and the most the ring can turn in each phase [D]."""
    # one program turn = 5 turns of the compound (12'/60) = 5 turns of the walk shaft while the clutch holds
    deg = PROG_RATIO * 16 / L.TEETH["z"]            # ring degrees per program degree
    a = (PROG_PHASES["A"][1] - PROG_PHASES["BA"][0]) * deg
    b = (360.0 - PROG_PHASES["AB"][0]) * deg
    return {"ring_deg_per_program_deg": deg, "A": a, "B": b}


def lock_closed(theta: float, width: float = 2.0) -> bool:
    """The lock switch closes (the follower drops into a notch) at the end of each phase."""
    t = theta % 360.0
    return any(abs(((t - n + 180.0) % 360.0) - 180.0) <= width / 2 for n in LOCK_NOTCHES)


# ------------------------------------------------------------------------------------------------ geometry
def levels(deck):
    """Heights (z) of the walk drive's parts above the deck, and below it."""
    d0, d1 = deck
    lv = {}
    lv["collar"] = (d1 + 0.3, d1 + 1.9)
    lv["washer"] = (lv["collar"][1], lv["collar"][1] + 0.5)
    lv["g24"] = (lv["washer"][1], lv["washer"][1] + 2.5)
    lv["neck"] = (lv["g24"][1], lv["g24"][1] + 0.4)
    lv["g12p"] = (lv["neck"][1], lv["neck"][1] + 2.5)
    lv["boss"] = (lv["g12p"][1], lv["g12p"][1] + 0.6)
    lv["hub"] = (lv["boss"][1], lv["boss"][1] + 2.0)
    lv["crank"] = (d0 - 2.5, d0 - 0.5)          # the stop sleeve's crank, below the deck
    lv["pin"] = (d0 - 8.0, lv["crank"][0])       # its pin, down into the rod
    lv["prog_cam"] = (d0 - 3.6, d0 - 0.6)        # grooved underneath
    lv["groove"] = 1.5
    lv["rod"] = (lv["prog_cam"][0] - 2.0, lv["prog_cam"][0] - 0.5)
    lv["lock_cam"] = (lv["rod"][0] - 3.5, lv["rod"][0] - 0.5)
    lv["hanger"] = (lv["lock_cam"][0] - 2.5, lv["lock_cam"][0] - 0.5)
    return lv


def gears():
    s12, s24 = pair_shifts(12, 24)
    s12p, s60 = pair_shifts(12, PROG_RATIO * 12)
    g = {"m12": Gear(12, M, shift=s12), "g24": Gear(24, M, shift=s24), "g12p": Gear(12, M, shift=s12p),
         "g60": Gear(PROG_RATIO * 12, M, shift=s60)}
    g["cd_motor"] = centre_distance(g["m12"], g["g24"])
    g["cd_prog"] = centre_distance(g["g12p"], g["g60"])
    return g


def crank_geometry(S, P):
    """The stop sleeve's crank angles for states A and B (symmetric about the perpendicular to the rod), and
    the rod's length so the program cam's groove runs at radii r_A = 8 and r_B = 8 + travel."""
    rho = math.degrees(math.atan2(P[1] - S[1], P[0] - S[0]))     # from S toward P
    gam_a, gam_b = rho + 90.0 - L.STOP["swing"] / 2, rho + 90.0 + L.STOP["swing"] / 2
    proj = lambda g: CRANK * math.cos(math.radians(g - rho))    # pin along S->P
    D = math.dist(S, P)
    r_a = 8.0
    rod_len = D - proj(gam_a) - r_a                                 # pin-to-follower length
    r_b = D - proj(gam_b) - rod_len
    return {"rho": rho, "gam_a": gam_a, "gam_b": gam_b, "rod_len": rod_len, "r_a": r_a, "r_b": r_b,
            "travel": r_b - r_a, "D": D}
