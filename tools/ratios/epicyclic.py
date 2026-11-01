"""Epicyclic and differential relations, including the two used by Schwilgué.

Willis's formula for an epicyclic train with carrier c, first wheel f and last wheel l:

    (w_l - w_c) / (w_f - w_c) = e

where e is the train value (product of driver/driven, signed) with the carrier held still.
"""
from __future__ import annotations

from fractions import Fraction


def willis_last(w_first, w_carrier, e) -> Fraction:
    """Speed of the last wheel, given the first wheel's and the carrier's speeds."""
    return Fraction(w_carrier) + Fraction(e) * (Fraction(w_first) - Fraction(w_carrier))


def schwilgue_sidereal(b, B, c, C, d, D, e, E) -> Fraction:
    """Turns of wheel E per turn of carrier B in Schwilgué's exact sidereal train (LEF, fig. 11).

    1 + (D/d)(e/E)[(B/b)(c/C) - 1]. With b/B = 18/270, c/C = 18/269, d/D = 26/100 and
    e/E = 18/94 this is exactly 164809/164359 [S: LEF].
    """
    return 1 + Fraction(D, d) * Fraction(e, E) * (Fraction(B, b) * Fraction(c, C) - 1)


def schwilgue_lunar_turns_per_year(N, n, k, K, l, L) -> Fraction:
    """Moon turns per Earth turn in the planetarium's lunar train (CLEA fig. 6; LEF table).

    (N/n) * [1 - (k*l)/(K*L)]. With J/j = 312/24, k/K = 83/122 and l/L = 14/196 this gives
    12.368267 turns per year, i.e. a synodic month of Y/12.368267.
    """
    return Fraction(N, n) * (1 - Fraction(k * l, K * L))
