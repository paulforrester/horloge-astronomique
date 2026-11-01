"""Command line: python -m tools.ratios {search,check,report} ...

Examples
--------
  # most accurate 3-stage trains for one turn per tropical year from a daily arbor
  python -m tools.ratios search --period 365.24219 --stages 3

  # sidereal globe as 1 + X (differential), X searched with 3 stages, wheels <= 200 mm at m 1.0
  python -m tools.ratios search --ratio "1+1/365.24219" --differential 1 1 --stages 3 --max-diameter 200

  # 2-stage reverted (coaxial) trains with a fixed tooth sum
  python -m tools.ratios search --ratio 4.151991 --coaxial --tooth-sum 202

  # verify every train in spec/clock.yaml (exit 1 on any failure)
  python -m tools.ratios check

  # regenerate the tables in docs/gear-trains.md
  python -m tools.ratios report --write docs/gear-trains.md
"""
from __future__ import annotations

import argparse
import sys

from .search import search_coaxial, search_compound, search_differential
from .spec import DEFAULT_SPEC, check_spec, load_spec, report_markdown, safe_eval, write_report


def _cmd_search(a) -> int:
    if (a.ratio is None) == (a.period is None):
        print("give exactly one of --ratio or --period", file=sys.stderr)
        return 2
    ip = safe_eval(a.input_period, {})
    target = safe_eval(a.ratio, {}) if a.ratio is not None else ip / safe_eval(a.period, {})
    kw = dict(input_period=ip, zmin=a.zmin, zmax=a.zmax, module=a.module,
              max_diameter=a.max_diameter, max_stage_ratio=a.max_stage_ratio)
    if a.coaxial:
        res = search_coaxial(target, tooth_sum=a.tooth_sum, top=a.top, **kw)
    elif a.differential:
        base, coef = (safe_eval(x, {}) for x in a.differential)
        res = search_differential(target, base, coef, a.stages, top=a.top, **kw)
    else:
        res = search_compound(target, a.stages, top=a.top, **kw)
    if not res:
        print("no train satisfies the constraints (try more stages, a larger --zmax or --max-stage-ratio)")
        return 1
    print(f"target ratio {target:.12g} (output turns per input turn), input period {ip:g} d, module {a.module}")
    print(f"{'train':40s} {'rel. error':>11s} {'period err':>12s} {'drift °/cent':>13s} {'max tip':>8s}  centre distances")
    for r in res:
        e = r.evaluation
        label = r.train.describe() if r.kind != "differential" else f"{r.base} + {r.coef}·({r.train.describe()})"
        cds = ", ".join(f"{s.centre_distance:.1f}" for s in r.train.stages)
        print(f"{label:40s} {e.rel_error:+11.3e} {e.period_error_s:+11.4f}s {e.drift_deg_per_century:+13.5f} "
              f"{r.train.max_tip_diameter:7.1f}  [{cds}] mm")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="python -m tools.ratios", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="search gear trains for a target")
    s.add_argument("--ratio", help="target output turns per input turn (expression)")
    s.add_argument("--period", help="target output period in days (expression)")
    s.add_argument("--input-period", default="1", help="input arbor period in days (default 1)")
    s.add_argument("--stages", type=int, default=2)
    s.add_argument("--zmin", type=int, default=12)
    s.add_argument("--zmax", type=int, default=160)
    s.add_argument("--module", type=float, default=1.0)
    s.add_argument("--max-diameter", type=float, default=None, help="max tip diameter, mm")
    s.add_argument("--max-stage-ratio", type=float, default=10.0)
    s.add_argument("--coaxial", action="store_true", help="2-stage reverted train")
    s.add_argument("--tooth-sum", type=int, default=None, help="fixed d+n per mesh for --coaxial")
    s.add_argument("--differential", nargs=2, metavar=("BASE", "COEF"), help="ratio = BASE + COEF * X")
    s.add_argument("--top", type=int, default=10)
    c = sub.add_parser("check", help="verify spec/clock.yaml")
    c.add_argument("spec", nargs="?", default=str(DEFAULT_SPEC))
    r = sub.add_parser("report", help="print or write the gear-train tables")
    r.add_argument("spec", nargs="?", default=str(DEFAULT_SPEC))
    r.add_argument("--write", metavar="DOC", help="replace the generated block in DOC")
    a = p.parse_args(argv)
    if a.cmd == "search":
        return _cmd_search(a)
    spec = load_spec(a.spec)
    if a.cmd == "check":
        problems = check_spec(spec)
        for x in problems:
            print("FAIL", x)
        print(f"{len(spec['trains'])} trains checked, {len(problems)} problem(s)")
        return 1 if problems else 0
    if a.write:
        changed = write_report(a.write, spec)
        print(("updated " if changed else "unchanged ") + a.write)
    else:
        print(report_markdown(spec))
    return 0


if __name__ == "__main__":
    sys.exit(main())
