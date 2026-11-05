"""D16: a NEMA 17 that plugs into a module's back plate from behind, on a printed adapter plate.

Paul chose this in PR #13 (5 Nov 2026), after `docs/m1-design.md` §10: "Motors are reachable without removing
gears" (architecture §11). The motor is screwed to the adapter at the bench (4 x M3 x 6, ISO 7380, heads in
counterbores in the adapter's front face). A boss on the adapter's front face locates it in the back plate.
Two M3 x 8 screws from behind, above and below the motor, hold it, into heat-set inserts in the plate. To
change a motor, undo those two and draw it straight out.

M1 builds the same adapter in `cad/modules/m1_time/mechanism.py` (its boss is a 1 mm locating ring, because
its drive parts stay in the cassette). Later modules use this module.

All shapes are in the motor's local frame: its axis on x = y = 0, +Z towards the dial.
"""
from __future__ import annotations

import build123d as bd

from cad.lib import parts

NEMA17 = dict(body=42.3, length=48.0, pilot=(22.0, 2.0), screws=15.5, shaft=5.0)   # [E] check the motor's drawing
SHAFT = dict(length=24.0, flat=(2.0, 15.0))   # [E] Ø5 x 24 from the face; flat 4.5 across, 15 mm from the tip
ADAPTER = dict(w=42.3, h=66.0, t=4.0, ears=27.0, corner=4.0)
INSERT_HOLE = 4.0                             # [E] M3 heat-set insert no longer than the plate: hole per datasheet
HEAD_COUNTERBORE = (6.2, 2.0)                 # M3 ISO 7380 head (Ø5.7 x 1.65), recessed in the adapter's front face


def motor_body(z_face: float):
    """The NEMA 17's body and its pilot boss, its face at z_face."""
    body = bd.Box(NEMA17["body"], NEMA17["body"], NEMA17["length"],
                  align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).moved(bd.Location((0, 0, z_face)))
    return body + parts.disc(NEMA17["pilot"][0], NEMA17["pilot"][1], z0=z_face)


def flat_side(x0: float, z0: float, z1: float):
    """The half-space x >= x0 between z0 and z1: the part of a Ø5 bore that the shaft's flat leaves free."""
    return bd.Box(10, 10, z1 - z0, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN)).moved(bd.Location((x0, 0, z0)))


def shaft(z_face: float):
    """The motor's own Ø5 D-shaft."""
    tip = z_face + SHAFT["length"]
    return parts.rod(NEMA17["shaft"], SHAFT["length"], z0=z_face) - flat_side(SHAFT["flat"][0], tip - SHAFT["flat"][1],
                                                                              tip + 1)


def d_key(z_face: float, z0: float, z1: float, fit: float = parts.FITS.press):
    """The key that fills a part's Ø5 bore against the shaft's flat, between z0 and z1 (clipped to the flat)."""
    tip = z_face + SHAFT["length"]
    lo = max(z0, tip - SHAFT["flat"][1])
    return parts.disc(NEMA17["shaft"] + 0.4, z1 - lo, z0=lo) & flat_side(SHAFT["flat"][0] + fit / 2, lo, z1)


def adapter(z_front: float, boss_d: float, boss_h: float):
    """The adapter plate, its front face at z_front (against the back plate's rear face), with a locating boss
    boss_d x boss_h forward of it, a Ø6 hole for the shaft, the pilot's counterbore behind, the motor's four
    screws in counterbores, and the two ear holes."""
    ad_, run = ADAPTER, parts.FITS.running
    z_face = z_front - ad_["t"]
    part = parts.plate((ad_["w"], ad_["h"]), ad_["t"], z0=z_face, corner_radius=ad_["corner"])
    part += parts.disc(boss_d, boss_h, z0=z_front)
    part -= parts.disc(6.0, ad_["t"] + boss_h + 10, z0=z_face - 5)
    part -= parts.disc(NEMA17["pilot"][0] + run, NEMA17["pilot"][1] + 0.2, z0=z_face - 0.01)
    s = NEMA17["screws"]
    for dx in (-s, s):
        for dy in (-s, s):
            part -= parts.disc(3.4, ad_["t"] + 10, z0=z_face - 5).moved(bd.Location((dx, dy, 0)))
            part -= parts.disc(HEAD_COUNTERBORE[0], HEAD_COUNTERBORE[1] + 0.01,
                               z0=z_front - HEAD_COUNTERBORE[1]).moved(bd.Location((dx, dy, 0)))
    for dy in (-ad_["ears"], ad_["ears"]):
        part -= parts.disc(3.4, ad_["t"] + 10, z0=z_face - 5).moved(bd.Location((0, dy, 0)))
    return part


def insert_holes(z_back: float, depth: float):
    """The two heat-set insert holes in the back plate, from its rear face at z_back."""
    up, down = (parts.disc(INSERT_HOLE, depth + 0.02, z0=z_back - 0.01).moved(bd.Location((0, dy, 0)))
                for dy in (ADAPTER["ears"], -ADAPTER["ears"]))
    return up + down
