"""spec/clock.yaml: every train meets its constraints and accuracy target; docs stay in sync."""
from pathlib import Path

from tools.ratios.spec import BEGIN, END, REPO, check_spec, evaluate_spec, load_spec, report_markdown

SPEC = load_spec()


def test_every_train_passes():
    assert check_spec(SPEC) == []


def test_shared_year_trains_are_identical():
    res = evaluate_spec(SPEC)
    ids = ["M2.year", "M3.year", "M5.earth", "M6.year"]
    stages = {i: res[i].spec["stages"] for i in ids}
    assert all(s == stages["M2.year"] for s in stages.values()), stages


def test_v1_trains_present():
    ids = {t["id"] for t in SPEC["trains"]}
    for required in ["M1.hour_hand", "M1.noon_cam", "M2.moon_hand", "M2.year", "M2.weekday",
                     "M5.earth", "M5.mercury", "M5.venus", "M5.mars", "M5.jupiter", "M5.saturn",
                     "M5.moon_arm", "M5.moon_globe", "M6.sidereal"]:
        assert required in ids, required


def test_gear_trains_doc_is_in_sync():
    doc = (REPO / "docs" / "gear-trains.md").read_text(encoding="utf-8")
    i, j = doc.index(BEGIN) + len(BEGIN), doc.index(END)
    assert doc[i:j].strip() == report_markdown(SPEC).strip(), (
        "docs/gear-trains.md is stale: run python -m tools.ratios report --write docs/gear-trains.md")
