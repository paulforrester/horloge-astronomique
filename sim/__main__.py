"""Command line for the simulator (docs/firmware-design.md §11).

    python -m sim validate [--years 100] [--sky] [--write]    # the checks; --write: sim/report.md
    python -m sim sheet --at 2027-01-01T10:00:00Z [--sky]     # the setting sheet for T_set
"""

import argparse
import datetime as dt
import sys
from pathlib import Path

from sim import validate

REPORT = Path(__file__).with_name("report.md")


def _parse_utc(s: str) -> int:
    return int(dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp())


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m sim")
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate")
    v.add_argument("--years", type=float, default=100)
    v.add_argument("--start", default="2027-01-01T00:00:00Z")
    v.add_argument("--sky", action="store_true", help="also compute the sky gaps (Skyfield, DE440s)")
    v.add_argument("--write", action="store_true", help=f"write {REPORT.name}")
    sh = sub.add_parser("sheet")
    sh.add_argument("--at", required=True)
    sh.add_argument("--sky", action="store_true")
    a = ap.parse_args(argv)

    if a.cmd == "validate":
        t0 = _parse_utc(a.start)
        results = validate.run_all(t0, a.years)
        gaps = validate.sky_gaps() if a.sky else None
        text = validate.report_markdown(results, gaps, t0, a.years)
        if a.write:
            REPORT.write_text(text, encoding="utf-8")
        print(text)
        return 0 if all(r.passed for r in results) else 1

    from sim import sheet
    print(sheet.setting_sheet(_parse_utc(a.at), sky=a.sky))
    return 0


if __name__ == "__main__":
    sys.exit(main())
