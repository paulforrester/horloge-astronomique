"""Search for gear trains that approximate a target ratio.

Three searches:

* ``search_compound``: k-stage compound trains (k = 1..3). For every product q of k driven
  wheels it tries the best numerators p = floor/ceil(target*q) that are themselves products of
  k driver gears. The search is exhaustive over the allowed tooth counts, so it finds the most
  accurate train for those constraints, not just a good one.
* ``search_coaxial``: 2-stage *reverted* trains whose output arbor is coaxial with the input
  (both meshes have the same centre distance), with an optional fixed tooth sum, e.g. for
  intermediate arbors on a common circle.
* ``search_differential``: trains of the form ``base + coef * X``, where X is a compound train,
  i.e. a differential or epicyclic combination. Schwilgué's sidereal and lunar trains use this
  form. When the target is close to ``base``, an error in X is scaled down by ``coef*X/target``,
  so very accurate ratios come from small trains.

All results carry exact ``Fraction`` ratios. Constraints: minimum and maximum teeth (or an
explicit allowed set), the maximum single-mesh ratio, the module, and the maximum tip diameter
(the bed or space limit).
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import permutations

import numpy as np

from .core import Evaluation, Stage, Train, as_fraction, evaluate, max_teeth_for_diameter


@dataclass
class Result:
    train: Train
    ratio: Fraction            # overall ratio (for differentials: base + coef * train ratio)
    evaluation: Evaluation
    kind: str = "compound"     # compound | coaxial | differential
    base: Fraction = Fraction(0)
    coef: Fraction = Fraction(1)

    def row(self) -> dict:
        e = self.evaluation
        return {
            "kind": self.kind,
            "train": self.train.describe(),
            "stages": self.train.n_stages,
            "ratio": f"{self.ratio.numerator}/{self.ratio.denominator}",
            "rel_error": e.rel_error,
            "period_error_s": e.period_error_s,
            "drift_deg_per_century": e.drift_deg_per_century,
            "max_tip_mm": self.train.max_tip_diameter,
            "max_stage_ratio": self.train.max_stage_ratio,
            "centre_distances_mm": [s.centre_distance for s in self.train.stages],
        }


def _teeth(zmin, zmax, allowed, module, max_diameter) -> tuple[int, ...]:
    if max_diameter is not None:
        zmax = min(zmax, max_teeth_for_diameter(max_diameter, module))
    teeth = sorted(set(allowed)) if allowed is not None else list(range(zmin, zmax + 1))
    teeth = [z for z in teeth if zmin <= z <= zmax]
    if not teeth:
        raise ValueError("no tooth counts satisfy the constraints")
    return tuple(teeth)


@lru_cache(maxsize=16)
def _products(teeth: tuple[int, ...], k: int) -> np.ndarray:
    """Sorted unique products of k tooth counts (with repetition)."""
    t = np.asarray(teeth, dtype=np.int64)
    if k == 1:
        return np.unique(t)
    p2 = np.unique(np.multiply.outer(t, t)[np.triu_indices(len(t))])
    if k == 2:
        return p2
    if k == 3:
        return np.unique(np.multiply.outer(p2, t).ravel())
    raise ValueError("compound search supports 1 to 3 stages; use search_differential or split the train")


def _factorizations(n: int, k: int, teeth: tuple[int, ...], start: int = 0, limit: int = 64):
    """Non-decreasing k-tuples of tooth counts whose product is n."""
    out = []
    if k == 1:
        return [(n,)] if n in teeth[start:] else []
    for i in range(start, len(teeth)):
        a = teeth[i]
        if a ** k > n:
            break
        if n % a:
            continue
        for rest in _factorizations(n // a, k - 1, teeth, i, limit):
            out.append((a,) + rest)
            if len(out) >= limit:
                return out
    return out


def _best_pairing(drivers, driveds, max_stage_ratio, coaxial):
    """Pair drivers with driven gears so that no single mesh exceeds max_stage_ratio.

    Returns the pairing with the smallest worst-case mesh ratio, or None.
    """
    best = None
    for perm_d in set(permutations(drivers)):
        for perm_n in set(permutations(driveds)):
            pairs = list(zip(perm_d, perm_n))
            worst = max(max(d / n, n / d) for d, n in pairs)
            if worst > max_stage_ratio:
                continue
            if coaxial and len(pairs) % 2 == 0:
                if any(a[0] + a[1] != b[0] + b[1] for a, b in zip(pairs[0::2], pairs[1::2])):
                    continue
            elif coaxial:
                continue
            key = (worst, max(perm_n))
            if best is None or key < best[0]:
                best = (key, pairs)
    return None if best is None else best[1]


def search_compound(target, stages=2, *, input_period=1.0, zmin=12, zmax=160, allowed=None,
                    module=1.0, max_diameter=None, max_stage_ratio=10.0, coaxial=False,
                    top=10, candidates=4000) -> list[Result]:
    """Most accurate k-stage compound trains for ``target`` (output turns per input turn)."""
    t = float(as_fraction(target))
    teeth = _teeth(zmin, zmax, allowed, module, max_diameter)
    prods = _products(teeth, stages)
    q = prods.astype(np.float64)
    results: list[Result] = []
    seen = set()
    for rounding in (np.floor, np.ceil):
        p = rounding(t * q).astype(np.int64)
        ok = p > 0
        idx = np.searchsorted(prods, p)
        idx = np.clip(idx, 0, len(prods) - 1)
        ok &= prods[idx] == p
        qs, ps = prods[ok], p[ok]
        err = np.abs(ps / qs.astype(np.float64) - t)
        order = np.argsort(err, kind="stable")[:candidates]
        for i in order:
            pq = (int(ps[i]), int(qs[i]))
            frac = Fraction(*pq)
            if frac in seen:
                continue
            seen.add(frac)
            # among all factorizations, keep the pairing with the smallest largest wheel,
            # then the gentlest worst mesh
            pairing, pkey = None, None
            for dr in _factorizations(pq[0], stages, teeth):
                for dn in _factorizations(pq[1], stages, teeth):
                    pr = _best_pairing(dr, dn, max_stage_ratio, coaxial)
                    if pr:
                        key = (max(max(d, n) for d, n in pr), max(max(d / n, n / d) for d, n in pr))
                        if pkey is None or key < pkey:
                            pairing, pkey = pr, key
            if not pairing:
                continue
            train = Train(tuple(Stage(d, n, module) for d, n in pairing))
            results.append(Result(train, train.ratio, evaluate(train.ratio, t, input_period),
                                  "coaxial" if coaxial else "compound"))
    results.sort(key=lambda r: (abs(r.evaluation.rel_error), r.train.max_tip_diameter))
    return results[:top]


def search_coaxial(target, *, input_period=1.0, zmin=12, zmax=160, allowed=None, module=1.0,
                   max_diameter=None, max_stage_ratio=10.0, tooth_sum=None, top=10) -> list[Result]:
    """2-stage reverted trains: d1+n1 == d2+n2 (== tooth_sum if given), same module."""
    t = float(as_fraction(target))
    teeth = _teeth(zmin, zmax, allowed, module, max_diameter)
    tset = set(teeth)
    sums = [tooth_sum] if tooth_sum else range(2 * teeth[0], 2 * teeth[-1] + 1)
    best = []
    for S in sums:
        ds = np.array([d for d in teeth if (S - d) in tset], dtype=np.int64)
        if len(ds) == 0:
            continue
        ns = S - ds
        r1 = ds / ns
        ok1 = np.maximum(r1, 1 / r1) <= max_stage_ratio
        ds, ns, r1 = ds[ok1], ns[ok1], r1[ok1]
        if len(ds) == 0:
            continue
        r = np.multiply.outer(r1, r1)
        err = np.abs(r - t)
        k = min(top, err.size)
        flat = np.argpartition(err.ravel(), k - 1)[:k]
        for f in flat:
            i, j = divmod(int(f), len(ds))
            train = Train((Stage(int(ds[i]), int(ns[i]), module), Stage(int(ds[j]), int(ns[j]), module)))
            best.append(Result(train, train.ratio, evaluate(train.ratio, t, input_period), "coaxial"))
    best.sort(key=lambda r: (abs(r.evaluation.rel_error), r.train.max_tip_diameter))
    out, seen = [], set()
    for r in best:
        if r.ratio not in seen:
            seen.add(r.ratio)
            out.append(r)
        if len(out) >= top:
            break
    return out


def search_differential(target, base=1, coef=1, stages=2, *, input_period=1.0, **kw) -> list[Result]:
    """Trains of the form base + coef * X; X is searched as a compound train.

    Example: a sidereal globe from a mean-day arbor is 1 + 1 * X with X ≈ 1/365.24219.
    """
    t = as_fraction(target)
    b, c = as_fraction(base), as_fraction(coef)
    x_target = (t - b) / c
    sub = search_compound(x_target, stages, input_period=input_period, **kw)
    out = []
    for r in sub:
        overall = b + c * r.train.ratio
        out.append(Result(r.train, overall, evaluate(overall, float(t), input_period),
                          "differential", b, c))
    out.sort(key=lambda r: (abs(r.evaluation.rel_error), r.train.max_tip_diameter))
    return out


def choose_train(target, *, input_period=1.0, max_drift_deg_per_century=1.0, max_stages=3,
                 kinds=("compound",), zmax_options=(160, 200), base=1, coef=1,
                 tooth_sum=None, **kw) -> Result | None:
    """Simplest train meeting the accuracy target.

    Preference order: fewest stages, then the smaller zmax option, then the smallest maximum tip
    diameter, then the smallest error. ``kinds`` may include 'compound', 'coaxial' (2 stages)
    and 'differential' (base + coef * X).
    """
    for k in range(1, max_stages + 1):
        for zmax in zmax_options:
            found = []
            for kind in kinds:
                try:
                    if kind == "compound":
                        rs = search_compound(target, k, input_period=input_period, zmax=zmax, top=40, **kw)
                    elif kind == "coaxial" and k == 2:
                        rs = search_coaxial(target, input_period=input_period, zmax=zmax,
                                            tooth_sum=tooth_sum, top=40, **kw)
                    elif kind == "differential":
                        rs = search_differential(target, base, coef, k, input_period=input_period,
                                                 zmax=zmax, top=40, **kw)
                    else:
                        continue
                except ValueError:
                    continue
                found += [r for r in rs
                          if abs(r.evaluation.drift_deg_per_century) <= max_drift_deg_per_century]
            if found:
                found.sort(key=lambda r: (r.train.max_tip_diameter,
                                          abs(r.evaluation.drift_deg_per_century)))
                return found[0]
    return None
