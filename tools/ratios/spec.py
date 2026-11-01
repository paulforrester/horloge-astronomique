"""Load, check and report the gear trains in spec/clock.yaml (the single source of truth, P5).

Each train in the spec states:
* ``input_period``: days per input turn (an expression, e.g. "1/24" or "1");
* ``output_period``: days per output turn (an expression over targets/derived values), or
  ``target_ratio``: output turns per input turn;
* ``stages``: [[driver, driven], ...] tooth counts;
* optional ``kind: differential`` with ``base`` and ``coef`` (ratio = base + coef * stages);
* optional ``via``: the id of the train whose output is this train's input (ratios multiply,
  errors compound);
* ``accuracy``: ``exact: true`` or ``max_drift_deg_per_century: <deg>``.

``check_spec`` returns a list of problems (empty means every train meets its constraints and
accuracy target). ``report_markdown`` renders the tables used in docs/gear-trains.md.
"""
from __future__ import annotations

import ast
import operator
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

import yaml

from .core import Stage, Train, evaluate, format_period

REPO = Path(__file__).resolve().parents[2]
DEFAULT_SPEC = REPO / "spec" / "clock.yaml"
BED_MM = 320.0   # H2D single-nozzle limiting axis (CLAUDE.md)

_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg}


def safe_eval(expr, names: dict) -> float:
    """Evaluate +, -, *, /, ** and parentheses over numbers and known names only."""
    if isinstance(expr, (int, float)):
        return float(expr)

    def ev(node):
        if isinstance(node, ast.Expression):
            return ev(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.Name):
            if node.id not in names:
                raise KeyError(f"unknown name {node.id!r} in {expr!r}")
            return float(names[node.id])
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](ev(node.left), ev(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](ev(node.operand))
        raise ValueError(f"unsupported expression {expr!r}")

    return ev(ast.parse(str(expr), mode="eval"))


def load_spec(path=DEFAULT_SPEC) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def names_of(spec: dict) -> dict:
    """Target values plus derived values (evaluated in file order)."""
    names = {k: float(v["value"]) for k, v in spec.get("targets", {}).items()}
    for k, v in spec.get("derived", {}).items():
        names[k] = safe_eval(v["expr"], names)
    return names


@dataclass
class TrainResult:
    id: str
    spec: dict
    train: Train
    achieved: Fraction          # overall ratio relative to the root input (after 'via' chain)
    target: float               # overall target ratio relative to the root input
    input_period: float         # days per turn of the root input
    output_period_target: float
    problems: list

    @property
    def evaluation(self):
        return evaluate(self.achieved, self.target, self.input_period)


def evaluate_spec(spec: dict) -> dict[str, TrainResult]:
    names = names_of(spec)
    defaults = spec.get("defaults", {})
    out: dict[str, TrainResult] = {}
    for t in spec["trains"]:
        problems = []
        m = float(t.get("gear_module", defaults.get("module", 1.0)))
        stages = tuple(Stage(int(d), int(n), m) for d, n in t["stages"])
        train = Train(stages)
        own = train.ratio
        if t.get("kind") == "differential":
            own = Fraction(str(t.get("base", 1))) + Fraction(str(t.get("coef", 1))) * own
        input_period = safe_eval(t["input_period"], names)
        if "output_period" in t:
            own_target = input_period / safe_eval(t["output_period"], names)
        else:
            own_target = safe_eval(t["target_ratio"], names)
        achieved, target, root_period = own, own_target, input_period
        if "via" in t:
            parent = out[t["via"]]
            achieved = parent.achieved * own
            target = parent.target * own_target
            root_period = parent.input_period
        output_period_target = root_period / target
        # --- constraints
        zmin = int(t.get("zmin", defaults.get("zmin", 12)))
        zmax = int(t.get("zmax", defaults.get("zmax", 160)))
        msr = float(t.get("max_stage_ratio", defaults.get("max_stage_ratio", 10)))
        for z in train.teeth:
            if not (zmin <= z <= zmax):
                problems.append(f"tooth count {z} outside [{zmin}, {zmax}]")
        if train.max_stage_ratio > msr + 1e-12:
            problems.append(f"mesh ratio {train.max_stage_ratio:.2f} exceeds {msr}")
        if t.get("coaxial") and not train.is_coaxial():
            problems.append("declared coaxial but stage pairs have unequal centre distances")
        if train.max_tip_diameter > BED_MM:
            problems.append(f"largest wheel {train.max_tip_diameter:.1f} mm exceeds the {BED_MM:.0f} mm bed")
        acc = t.get("accuracy", {})
        ev = evaluate(achieved, target, root_period)
        if acc.get("exact"):
            if achieved != Fraction(target).limit_denominator(10**9) and abs(ev.rel_error) > 1e-12:
                problems.append(f"declared exact but relative error is {ev.rel_error:.3e}")
        elif "max_drift_deg_per_century" in acc:
            lim = float(acc["max_drift_deg_per_century"])
            if abs(ev.drift_deg_per_century) > lim:
                problems.append(f"drift {ev.drift_deg_per_century:+.3f}°/century exceeds ±{lim}")
        else:
            problems.append("no accuracy target declared")
        out[t["id"]] = TrainResult(t["id"], t, train, achieved, target, root_period,
                                   output_period_target, problems)
    return out


def check_spec(spec: dict) -> list[str]:
    return [f"{r.id}: {p}" for r in evaluate_spec(spec).values() for p in r.problems]


def _fmt_err_s(x: float) -> str:
    if x == 0:
        return "0"
    a = abs(x)
    if a < 1e-3:
        return f"{x:+.2e} s"
    if a < 60:
        return f"{x:+.3f} s"
    if a < 3600:
        return f"{x / 60:+.2f} min"
    return f"{x / 3600:+.2f} h"


def source_drift(spec: dict, r: "TrainResult") -> str:
    """Drift (°/century) equivalent to the rounding of the sourced target value.

    Only for trains whose output period is a single sourced target with a declared precision.
    """
    name = str(r.spec.get("output_period", "")).strip()
    tgt = spec.get("targets", {}).get(name)
    if not tgt or "precision" not in tgt:
        return "—"
    rel = float(tgt["precision"]) / float(tgt["value"])
    turns_per_century = 36525.0 / r.output_period_target
    return f"±{360.0 * turns_per_century * rel:.4f}"


def report_markdown(spec: dict) -> str:
    names = names_of(spec)
    res = evaluate_spec(spec)
    lines = []
    lines.append("### Targets\n")
    lines.append("| Name | Value | Tag | Source |")
    lines.append("|---|---|---|---|")
    for k, v in spec["targets"].items():
        lines.append(f"| `{k}` | {v['value']} {v.get('unit', '')} | [{v.get('tag', 'S')}] | {v['source']} |")
    for k, v in spec.get("derived", {}).items():
        lines.append(f"| `{k}` | {names[k]:.10g} {v.get('unit', '')} | [D] | `{v['expr']}` |")
    lines.append("\n### Trains\n")
    lines.append("Errors are against the target value. Drift is the accumulated error of the "
                 "displayed angle per Julian century. \"Exact\" means the ratio equals the target "
                 "as a fraction.\n")
    lines.append("| Train | Ver. | Teeth (driver/driven per mesh) | Stages | Ratio | Target period | "
                 "Period error | Drift °/century | Target value ± (°/century) | Accuracy target | "
                 "Largest wheel | Check |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in res.values():
        t = r.spec
        e = r.evaluation
        kind = t.get("kind", "compound")
        teeth = r.train.describe()
        if kind == "differential":
            teeth = f"{t.get('base', 1)} {'+' if Fraction(str(t.get('coef', 1))) >= 0 else '−'} ({teeth})"
        if "via" in t:
            teeth = f"[`{t['via']}`] × {teeth}"
        acc = t.get("accuracy", {})
        acc_s = "exact" if acc.get("exact") else f"≤ {acc.get('max_drift_deg_per_century')}°/c"
        exact = abs(e.rel_error) < 1e-15
        ratio_s = f"{r.achieved.numerator}/{r.achieved.denominator}"
        if len(ratio_s) > 24:
            ratio_s = f"{float(r.achieved):.10g}"
        mod = r.train.stages[0].module
        huge = r.output_period_target >= 1e6
        per_err = "0" if exact else (f"{e.rel_error * 100:+.3f} % (rate)" if huge else _fmt_err_s(e.period_error_s))
        lines.append(
            f"| `{r.id}` | {t.get('version', 'v1')} | {teeth} | {r.train.n_stages} | {ratio_s} | "
            f"{format_period(r.output_period_target) if not huge else f'{r.output_period_target / 365.25:,.0f} yr'} | "
            f"{per_err} | "
            f"{'0' if exact else f'{e.drift_deg_per_century:+.4f}'} | {source_drift(spec, r)} | {acc_s} | "
            f"{r.train.max_tip_diameter:.0f} mm (m {mod:g}) | {'OK' if not r.problems else 'FAIL'} |")
    return "\n".join(lines) + "\n"


BEGIN = "<!-- BEGIN GENERATED: python -m tools.ratios report --write docs/gear-trains.md -->"
END = "<!-- END GENERATED -->"


def write_report(doc_path, spec: dict) -> bool:
    """Replace the generated block in doc_path. Returns True if the file changed."""
    p = Path(doc_path)
    text = p.read_text(encoding="utf-8")
    i, j = text.index(BEGIN), text.index(END)
    new = text[:i] + BEGIN + "\n\n" + report_markdown(spec) + "\n" + text[j:]
    if new != text:
        p.write_text(new, encoding="utf-8")
        return True
    return False
