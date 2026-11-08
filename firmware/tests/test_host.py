"""Build and run the firmware core's host tests, and check the C++ time law against sim/timelaw.py.

docs/firmware-design.md §12.1 and §11.6. Needs a C++17 compiler (g++ or clang++); skips without one.
"""

import random
import shutil
import subprocess
import zoneinfo
from datetime import datetime, timezone
from pathlib import Path

import pytest

from sim import timelaw

FW = Path(__file__).resolve().parents[1]
CXX = shutil.which("g++") or shutil.which("clang++")
FLAGS = ["-std=c++17", "-Wall", "-Wextra", "-Werror", "-O1"]

pytestmark = pytest.mark.skipif(CXX is None, reason="no C++ compiler found")


def build(out: Path, sources) -> Path:
    cmd = [CXX, *FLAGS, *map(str, sources), "-o", str(out)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, res.stderr
    return out


@pytest.fixture(scope="module")
def law_cli(tmp_path_factory):
    out = tmp_path_factory.mktemp("fw") / "law_cli"
    core = sorted((FW / "core").glob("*.cpp"))
    return build(out, [*core, FW / "tests" / "law_cli.cpp"])


def query(exe: Path, lines):
    res = subprocess.run([str(exe)], input="\n".join(lines) + "\n", capture_output=True, text=True)
    assert res.returncode == 0, res.stderr
    return res.stdout.split("\n")[: len(lines)]


def test_host_unit_tests(tmp_path):
    core = sorted((FW / "core").glob("*.cpp"))
    tests = sorted((FW / "tests").glob("test_*.cpp")) + [FW / "tests" / "main.cpp"]
    exe = build(tmp_path / "host_tests", [*core, *tests])
    res = subprocess.run([str(exe)], capture_output=True, text=True)
    print(res.stdout)
    assert res.returncode == 0, res.stdout


def change_instants():
    out = []
    for y in range(2026, 2101):
        for spring in (True, False):
            s = timelaw.eu_change_unix_s(y, spring)
            out += [s - 1, s, s + 1]
    return out


def test_summer_time_matches_zoneinfo():
    """The Python rule agrees with the IANA database for Europe/Paris, 2026-2100."""
    paris = zoneinfo.ZoneInfo("Europe/Paris")
    for s in change_instants():
        off = datetime.fromtimestamp(s, timezone.utc).astimezone(paris).utcoffset().total_seconds()
        assert timelaw.legal_offset_s(s) == off, s


def test_cpp_law_equals_python(law_cli):
    rng = random.Random(7)
    span = 100 * 366 * 86400
    times = [timelaw.EPOCH_UNIX_S + rng.randrange(-span // 10, span) for _ in range(3000)]
    times += change_instants()
    times += [int(datetime(y, 12, 31, 23, 59, 59, tzinfo=timezone.utc).timestamp()) for y in range(2026, 2101)]
    times += [int(datetime(y, 2, 29, 12, tzinfo=timezone.utc).timestamp()) for y in range(2028, 2101, 4) if y != 2100]

    lines, want = [], []
    for s in times:
        us = s * 1_000_000 + rng.randrange(1_000_000)
        j = timelaw.summer_time_j(s)
        p = rng.randrange(-10**6, 10**6)
        for kind in ("mean", "legal"):
            lines.append(f"T {kind} {us} {j} {p}")
            want.append(str(timelaw.target_usteps(kind, us, j, p)))
        lines.append(f"J {s}")
        want.append(str(timelaw.summer_time_j(s)))
        lines.append(f"O {s}")
        want.append(str(timelaw.legal_offset_s(s)))
    got = query(law_cli, lines)
    bad = [(l, g, w) for l, g, w in zip(lines, got, want) if g != w]
    assert not bad, bad[:10]


def test_cpp_quarters_follow_legal_time(law_cli):
    """Every quarter the firmware schedules is :00/:15/:30/:45 of Europe/Paris time (D14)."""
    paris = zoneinfo.ZoneInfo("Europe/Paris")
    rng = random.Random(3)
    starts = [s - 600 for s in change_instants()]
    starts += [timelaw.EPOCH_UNIX_S + rng.randrange(0, 100 * 365 * 86400) for _ in range(2000)]
    got = query(law_cli, [f"Q {s}" for s in starts])
    for s, line in zip(starts, got):
        unix_s, n, hour12, noon, minute = map(int, line.split())
        assert s <= unix_s < s + 900
        local = datetime.fromtimestamp(unix_s, timezone.utc).astimezone(paris)
        assert local.minute % 15 == 0 and local.second == 0
        assert n == (local.minute // 15 or 4)
        assert minute == local.hour * 60 + local.minute
        if n == 4:
            assert hour12 == (local.hour % 12 or 12)
            assert bool(noon) == (local.hour == 12)
        else:
            assert hour12 == 0 and not noon


def test_spec_header_is_up_to_date():
    from firmware.spec_gen import gen_spec

    assert gen_spec.main(["--check"]) == 0, "run: python -m firmware.spec_gen.gen_spec"
