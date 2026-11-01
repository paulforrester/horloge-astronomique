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
BEGIN = "<!-- BEGIN GENERATED: python -m tools.ratios report --write docs/gear-trains.md -->"
END = "<!-- END GENERATED -->"
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
    res = evaluate_spec(spec)
    out = [f"{r.id}: {p}" for r in res.values() for p in r.problems]
    if "strength" in spec:
        out += strength_problems(spec, res)
    return out


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
    if tgt and "precision" in tgt:
        rel = float(tgt["precision"]) / float(tgt["value"])
    elif name in spec.get("derived", {}) and "uncertainty" in spec["derived"][name]:
        rel = float(spec["derived"][name]["uncertainty"]) / names_of(spec)[name]
    else:
        return "—"
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


def output_loads(spec: dict, res: dict) -> dict:
    """Running torque (N·m) at each train's output: its own hub load plus the loads of every
    train driven from it, reflected through their ratios and mesh losses.

    A child's load T at its output reaches the parent's output as T * ratio / eta**stages. For an
    epicyclic child (a fixed sun wheel, the parent's output as carrier) the output's absolute
    speed is (1 + ratio) times the carrier's, so the factor is (1 + ratio).
    """
    return _loads(spec, res)[0]


def _loads(spec: dict, res: dict) -> tuple[dict, dict]:
    """(total load at each output, load behind each output's slip clutch), both in N·m.

    Trains driven from a shared output take off from its tube *before* the output's own clutch,
    except an epicyclic child, which rides on the output (the Moon arm on the Earth arm) and so
    loads that clutch too.
    """
    st = spec["strength"]
    eta = float(st["mesh_efficiency"])
    default = float(st["running_output_load_nm"])
    total = {rid: float(r.spec.get("running_output_load_nm", default)) for rid, r in res.items()}
    clutch = dict(total)
    for rid in reversed(list(res)):            # spec lists parents before children
        r = res[rid]
        if "via" in r.spec:
            ratio = abs(float(r.train.ratio))
            factor = (1 + ratio) if r.spec.get("epicyclic") else ratio
            reflected = total[rid] * factor / eta ** r.train.n_stages
            total[r.spec["via"]] += reflected
            if r.spec.get("epicyclic"):
                clutch[r.spec["via"]] += reflected
    return total, clutch


@dataclass
class StrengthRow:
    id: str
    face_mm: float
    weakest: str                 # "driver/driven" of the mesh that limits the output torque
    capacity_nm: float           # output torque that brings that mesh to the allowable stress
    load_nm: float               # running torque carried at the output (children included)
    clutch_load_nm: float        # the part of it behind the output's own slip clutch
    shared: bool                 # other trains are driven from this output
    stress_mpa: float            # highest running root stress in the train
    safety: float                # allowable / highest running stress
    window: tuple | None         # slip-clutch window (3 x clutch load, capacity / 2) in N·m, or None


def strength_rows(spec: dict, res: dict | None = None) -> list[StrengthRow]:
    """Lewis check of each train's own meshes at the load its output carries."""
    from .strength import train_strength
    st = spec["strength"]
    sigma = float(st["allowable_stress_mpa"])
    res = res or evaluate_spec(spec)
    loads, clutch = _loads(spec, res)
    parents = {r.spec["via"] for r in res.values() if "via" in r.spec}
    rows = []
    for r in res.values():
        face = float(r.spec.get("face_width_mm", st["face_width_mm"]))
        checks = train_strength(r.train.stages, face=face, sigma=sigma, output_load_nm=loads[r.id])
        if not checks:
            continue
        weakest = min(checks, key=lambda c: c.output_torque_capacity_nm)
        worst = max(checks, key=lambda c: c.running_stress_mpa)
        cap = weakest.output_torque_capacity_nm
        low, high = 3 * clutch[r.id], cap / 2
        rows.append(StrengthRow(r.id, face, f"{weakest.driver}/{weakest.driven}", cap, loads[r.id],
                                clutch[r.id], r.id in parents, worst.running_stress_mpa,
                                sigma / worst.running_stress_mpa, (low, high) if low < high else None))
    return rows


def strength_problems(spec: dict, res: dict | None = None) -> list[str]:
    """Trains below the minimum running safety factor, or with no slip-clutch window."""
    need = float(spec["strength"].get("min_safety_factor", 1))
    out = []
    for row in strength_rows(spec, res):
        if row.safety < need:
            out.append(f"{row.id}: running safety factor {row.safety:.1f} < {need:g}")
        if row.window is None:
            out.append(f"{row.id}: no slip-clutch window (3 x clutch load {3 * row.clutch_load_nm * 1000:.0f}"
                       f" N·mm >= half capacity {row.capacity_nm / 2 * 1000:.0f} N·mm)")
        if row.shared and 3 * row.load_nm >= row.capacity_nm:
            out.append(f"{row.id}: every clutch driven from it slipping at once (3 x {row.load_nm * 1000:.0f}"
                       f" N·mm) would exceed its capacity {row.capacity_nm * 1000:.0f} N·mm")
    return out


def motor_budget(spec: dict, res: dict | None = None) -> list[tuple]:
    """(module, reduction, torque at input arbor, torque at motor, margin) per module, in N·m."""
    st, mot = spec["strength"], spec["motor"]
    eta = float(st["mesh_efficiency"])
    res = res or evaluate_spec(spec)
    loads = output_loads(spec, res)
    t_motor = float(mot["holding_torque_nm"]) * float(mot["run_current_a"]) / float(mot["rated_current_a"])
    per_module: dict = {}
    for r in res.values():
        mod = r.id.split(".")[0]
        per_module.setdefault(mod, float(st["input_friction_nm"]))
        if "via" not in r.spec:                 # children are already inside their root's load
            per_module[mod] += loads[r.id] * abs(float(r.train.ratio)) / eta ** r.train.n_stages
    rows = []
    for mod, t_in in per_module.items():
        red = float(mot["reduction"].get(mod, 1))
        t_m = t_in / (red * eta ** (2 if red > 1 else 0))     # a printed 24:1 is two meshes
        rows.append((mod, red, t_in, t_m, t_motor / t_m))
    return rows


def strength_markdown(spec: dict) -> str:
    st, mot = spec["strength"], spec["motor"]
    sigma = float(st["allowable_stress_mpa"])
    eta = float(st["mesh_efficiency"])
    res = evaluate_spec(spec)
    t_motor = float(mot["holding_torque_nm"]) * float(mot["run_current_a"]) / float(mot["rated_current_a"])
    lines = [
        "### Tooth strength (Lewis)",
        "",
        f"Allowable root stress {sigma:g} MPa; face width {float(st['face_width_mm']):g} mm unless "
        f"the train sets its own; running load {float(st['running_output_load_nm']) * 1000:g} N·mm "
        "at each output unless the train sets its own (parameters in `spec/clock.yaml` → "
        "`strength`).",
        "",
        "- **Output capacity**: the torque at the train's output that brings its weakest tooth to "
        "the allowable stress.",
        "- **Running load**: the output's own load plus, for a shared train such as `M5.earth`, the "
        "loads of every train driven from it, reflected through their ratios. The epicyclic "
        "`M5.moon_arm` reflects (1 + ratio) times its load onto the Earth arm.",
        "- **Clutch window**: a slip clutch at the output must hold 3× the load behind it and slip "
        "below half the capacity. On a shared train the planet trains take off from the tube "
        "before the Earth arm's clutch, so that clutch carries only the Earth arm and the Moon arm "
        "riding on it. The shared train must also survive every clutch on it slipping at once "
        "(capacity above 3× the running load); `check` enforces both, and a running safety factor "
        f"of at least {float(st.get('min_safety_factor', 1)):g}.",
        "- Worm meshes are not Lewis meshes and are skipped.",
        "",
        "| Train | Face | Weakest mesh | Output capacity | Running load | Highest running stress | "
        "Safety factor | Clutch window |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in strength_rows(spec, res):
        win = (f"{row.window[0] * 1000:.0f} … {row.window[1] * 1000:.0f} N·mm" if row.window
               else "**none**")
        lines.append(f"| `{row.id}` | {row.face_mm:g} mm | {row.weakest} | {row.capacity_nm * 1000:.0f} N·mm | "
                     f"{row.load_nm * 1000:.1f} N·mm | {row.stress_mpa:.2f} MPa | {row.safety:.0f} | {win} |")
    lines += [
        "",
        "### Motor torque budget",
        "",
        f"Motor {mot['model']}: holding torque {mot['holding_torque_nm']} N·m at "
        f"{mot['rated_current_a']} A [S: datasheet]. At the proposed run current of "
        f"{mot['run_current_a']} A it gives about **{t_motor * 1000:.0f} mN·m** [E: torque roughly "
        "proportional to current]. The required torque is the module's own input friction plus "
        "every output's running load reflected back through its ratio, with mesh efficiency "
        f"{eta:g} per mesh [E].",
        "",
        "| Module | Motor → input reduction | Torque needed at input arbor | Torque needed at motor | Margin at run current |",
        "|---|---|---|---|---|",
    ]
    for mod, red, t_in, t_m, margin in motor_budget(spec, res):
        lines.append(f"| {mod} | {red:g}:1 | {t_in * 1000:.2f} mN·m | {t_m * 1000:.3f} mN·m | {margin:,.0f}× |")
    return "\n".join(lines) + "\n"


def full_report(spec: dict) -> str:
    out = report_markdown(spec)
    if "strength" in spec and "motor" in spec:
        out += "\n" + strength_markdown(spec)
    return out


def write_report(doc_path, spec: dict) -> bool:
    """Replace the generated block in doc_path. Returns True if the file changed."""
    p = Path(doc_path)
    text = p.read_text(encoding="utf-8")
    i, j = text.index(BEGIN), text.index(END)
    new = text[:i] + BEGIN + "\n\n" + full_report(spec) + "\n" + text[j:]
    if new != text:
        p.write_text(new, encoding="utf-8")
        return True
    return False
