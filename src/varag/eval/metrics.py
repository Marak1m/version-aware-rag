"""The metric table (handoff, "Metrics") from a run's results and traces, with slices, intervals,
the primary comparisons, the detectable-effect table and the risk-coverage curve.

Every metric is a plain function of the rows in results.jsonl (one per instance and method) and
the records in traces.jsonl. Intervals: a cluster bootstrap over concepts and a Wilson interval
on the concept-level proportion. Comparisons: paired bootstrap on per-concept differences, exact
McNemar on instance pairs, Holm across the baselines compared with va_rag.
"""

from __future__ import annotations

import gzip
import json
from collections import Counter, defaultdict
from pathlib import Path

from varag.eval.outcomes import intended_pass
from varag.eval.stats import (Interval, auroc, cluster_bootstrap, detectable_difference, holm, intraclass_correlation,
                              mcnemar_exact, mean, paired_bootstrap, risk_coverage, wilson)
from varag.inventory.build import load_diff
from varag.pipeline.signals import static_usages

PRIMARY_CONTRASTS = ("plain_rag", "mind_version", "two_branch", "always_ask")
COSTS = (0.0, 0.1, 0.3)
SLICES = ("library", "target", "condition", "clue_type", "exclusivity", "change_type", "user_arm", "gold_examples")
EXCLUSIVE_ERRORS = ("AttributeError", "ImportError", "ModuleNotFoundError", "TypeError")


# --- loading --------------------------------------------------------------------------------


def load_run(run_dir: Path) -> tuple[dict, list[dict], dict[tuple[str, str], dict]]:
    run_json = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    results = run_dir / "results.jsonl"
    if results.exists():
        text = results.read_text(encoding="utf-8")
    else:
        with gzip.open(run_dir / "results.jsonl.gz", "rt", encoding="utf-8") as fh:
            text = fh.read()
    rows = [json.loads(line) for line in text.splitlines() if line.strip()]
    traces: dict[tuple[str, str], dict] = {}
    path = run_dir / "traces.jsonl"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                t = json.loads(line)
                traces[(t["method"], t["instance_id"])] = t
    return run_json, rows, traces


# --- helpers ----------------------------------------------------------------------------------


def share(rows: list[dict], predicate) -> float | None:
    return mean([1.0 if predicate(r) else 0.0 for r in rows])


def by_concept(rows: list[dict], predicate) -> dict[str, list[float]]:
    out: dict[str, list[float]] = defaultdict(list)
    for r in rows:
        out[r["concept_id"]].append(1.0 if predicate(r) else 0.0)
    return dict(out)


def intervals(rows: list[dict], predicate, seed: int = 1234) -> dict:
    grouped = by_concept(rows, predicate)
    boot = cluster_bootstrap(grouped, seed=seed)
    means = [sum(v) / len(v) for v in grouped.values() if v]
    wil = wilson(sum(means), len(means)) if means else Interval(None, None, None, 0)
    return {"estimate": boot.estimate, "bootstrap": [boot.low, boot.high], "wilson_concepts": [wil.low, wil.high], "n": boot.n, "concepts": len(means)}


def targeted(rows: list[dict]) -> list[dict]:
    return [r for r in rows if r.get("target")]


def asked(r: dict) -> bool:
    return bool(r.get("question"))


def relevant_question(r: dict, trace: dict | None) -> bool:
    if not asked(r):
        return False
    mt = (trace or {}).get("method_trace", {})
    return mt.get("question_relevant") is not False


def hedged(r: dict) -> bool:
    return r.get("answers_returned", 1) == 2


def passed_without_question(r: dict) -> bool:
    return not asked(r) and r.get("code") is not None


# --- per-method metrics ------------------------------------------------------------------------


def usage_sides(code: str | None, library: str) -> tuple[set[str], set[str]]:
    if not code:
        return set(), set()
    usages = static_usages(code, load_diff(library))
    return (usages.old, usages.new) if usages.parsed else (set(), set())


def silent_commit_direction(rows: list[dict]) -> dict:
    """Among no-clue instances answered without a question: only old-side, only new-side, both or neither exclusive symbols."""
    counts: Counter = Counter()
    for r in rows:
        if r.get("condition") != "no-clue" or not passed_without_question(r):
            continue
        old, new = usage_sides(r.get("code"), r["library"])
        counts["both" if old and new else "old" if old else "new" if new else "neither"] += 1
    total = sum(counts.values())
    return {k: counts.get(k, 0) / total for k in ("old", "new", "both", "neither")} | {"n": total} if total else {"n": 0}


def clue_following(rows: list[dict]) -> float | None:
    """Among clue instances answered without a question: share whose exclusive symbols match the clue's version."""
    hits = []
    for r in rows:
        if r.get("condition") != "clue" or not passed_without_question(r):
            continue
        old, new = usage_sides(r.get("code"), r["library"])
        target_side = old if r["target"] == "old" else new
        other_side_ = new if r["target"] == "old" else old
        hits.append(1.0 if target_side and not other_side_ else 0.0)
    return mean(hits)


def inference_metrics(rows: list[dict], traces: dict, method: str) -> dict:
    decisions = []
    for r in rows:
        t = traces.get((method, r["instance_id"]))
        d = ((t or {}).get("method_trace") or {}).get("decision")
        if d:
            decisions.append((r, d))
    if not decisions:
        return {}
    inferred = [(r, d) for r, d in decisions if d["kind"] == "INFER"]
    precision = mean([1.0 if d["side"] == r["target"] else 0.0 for r, d in inferred if r.get("target")])
    clue_rows = [(r, d) for r, d in decisions if r.get("condition") == "clue"]
    coverage = mean([1.0 if d["kind"] == "INFER" else 0.0 for r, d in clue_rows])
    margins = [abs(d["margin"]) for r, d in inferred if r.get("target")]
    correct = [d["side"] == r["target"] for r, d in inferred if r.get("target")]
    return {"inference_precision": precision, "inference_coverage": coverage,
            "decisions": dict(Counter(d["kind"] for _, d in decisions)),
            "risk_coverage": risk_coverage(margins, correct) if margins else [],
            "auroc_abs_margin": auroc(margins, correct) if margins else None}


def names_exclusive(exec_record: dict, code: str | None, library: str) -> bool:
    if not exec_record or exec_record.get("exc_type") not in EXCLUSIVE_ERRORS or not exec_record.get("last_line") or not code:
        return False
    old, new = usage_sides(code, library)
    names = {s.split("(")[0].rsplit(".", 1)[-1] for s in old | new} | {s.split("(")[-1].rstrip(")").split("=")[0] for s in old | new if "(" in s}
    return any(n and n in exec_record["last_line"] for n in names)


def guard_metrics(rows: list[dict], traces: dict, method: str) -> dict:
    """Guard verdict against the execution oracle, plus fix and harm rates."""
    tp = fp = fn = fixes = harms = flagged_total = 0
    for r in rows:
        if not r.get("target"):
            continue
        t = traces.get((method, r["instance_id"]))
        answers = ((t or {}).get("method_trace") or {}).get("answers") or []
        guard = next((a.get("guard") for a in answers if a.get("side") in (r["target"], None)), (answers[0].get("guard") if answers else None)) or {}
        flagged = bool(guard.get("flagged"))
        before = r.get("pre_guard") or {}
        oracle_code = before.get("code") or r.get("code")
        oracle_exec = (before.get("exec") or r.get("exec") or {}).get(r["target"], {})
        oracle = names_exclusive(oracle_exec, oracle_code, r["library"])
        tp += flagged and oracle
        fp += flagged and not oracle
        fn += (not flagged) and oracle
        if flagged:
            flagged_total += 1
            if before:
                pre_pass = intended_pass(before.get("outcome", ""))
                post_pass = bool(r.get("intended_pass"))
                fixes += (not pre_pass) and post_pass
                harms += pre_pass and not post_pass
    return {"flagged": flagged_total, "precision": tp / (tp + fp) if tp + fp else None, "recall": tp / (tp + fn) if tp + fn else None,
            "fix_rate": fixes / flagged_total if flagged_total else None, "harm_rate": harms / flagged_total if flagged_total else None}


def order_sensitivity(rows: list[dict], traces: dict, method: str) -> float | None:
    first, last = [], []
    for r in rows:
        if not r.get("target"):
            continue
        t = traces.get((method, r["instance_id"]))
        flag = ((t or {}).get("retrieval") or {}).get("target_gold_first")
        if flag is None:
            continue
        (first if flag else last).append(1.0 if r.get("intended_pass") else 0.0)
    a, b = mean(first), mean(last)
    return None if a is None or b is None else a - b


def method_metrics(rows: list[dict], traces: dict, method: str, seed: int = 1234) -> dict:
    mine = [r for r in rows if r["method"] == method]
    tgt = targeted(mine)
    controls = [r for r in mine if not r.get("target")]
    no_clue = [r for r in tgt if r.get("condition") == "no-clue"]
    non_ambiguous = [r for r in mine if r.get("condition") in ("clue", "stated", "control")]
    passing = [r for r in tgt if r.get("intended_pass")]
    questions = [r for r in mine if asked(r)]
    out: dict = {
        "method": method,
        "n_targeted": len(tgt), "n_controls": len(controls),
        "intended_pass_rate": intervals(tgt, lambda r: bool(r.get("intended_pass")), seed),
        "intended_pass_rate_strict": share(tgt, lambda r: intended_pass(r.get("outcome_strict", r["outcome"]))),
        "intended_pass_rate_lenient": share(tgt, lambda r: intended_pass(r.get("outcome_lenient", r["outcome"]))),
        "outcomes": {k: share(tgt, lambda r, k=k: r["outcome"] == k) for k in ("target_only", "portable", "wrong_version", "broken", "no_code", "infra_error")},
        "control_outcomes": dict(Counter(r["outcome"] for r in controls)),
        "soft_fail_rate": share(passing, lambda r: bool(r.get("soft_fail"))),
        "blend_static": intervals(tgt, lambda r: bool(r.get("blend_static")), seed),
        "blend_exec": intervals(tgt, lambda r: bool(r.get("blend_exec")), seed),
        "guarded_portable": share(tgt, lambda r: bool(r.get("guarded_portable"))),
        "ask_recall": share(no_clue, lambda r: relevant_question(r, traces.get((method, r["instance_id"])))),
        "ask_precision": share(questions, lambda r: r.get("condition") == "no-clue") if questions else None,
        "over_ask_rate": share(non_ambiguous, asked),
        "over_hedge_rate": share(non_ambiguous, hedged),
        "utility": {str(c): (mean([1.0 if r.get("intended_pass") else 0.0 for r in tgt]) or 0.0) - c * (share(tgt, lambda r: asked(r) or hedged(r)) or 0.0) for c in COSTS} if tgt else {},
        "silent_commit_direction": silent_commit_direction(tgt),
        "clue_following": clue_following(tgt),
        "order_sensitivity": order_sensitivity(mine, traces, method),
        "cost": {"calls_per_instance": mean([float(r.get("calls", 0)) for r in mine]),
                 "questions_per_instance": share(mine, asked),
                 "answers_per_instance": mean([float(r.get("answers_returned", 1)) for r in mine])},
        "both_correct_rate": share([r for r in tgt if "both_correct" in r], lambda r: bool(r["both_correct"])),
    }
    out.update(inference_metrics(mine, traces, method))
    out["guard"] = guard_metrics(mine, traces, method)
    out["slices"] = {}
    for key in SLICES:
        values = sorted({str(r.get(key)) for r in tgt if r.get(key) is not None})
        out["slices"][key] = {v: {"n": len(s), "intended_pass_rate": share(s, lambda r: bool(r.get("intended_pass"))),
                                  "blend_exec": share(s, lambda r: bool(r.get("blend_exec")))}
                              for v in values for s in [[r for r in tgt if str(r.get(key)) == v]]}
    cross: dict[str, dict] = {}
    for r in tgt:
        cell = cross.setdefault(f"{r.get('gold_examples')} / {r.get('change_type')}", {"n": 0, "passed": 0})
        cell["n"] += 1
        cell["passed"] += int(bool(r.get("intended_pass")))
    out["slices"]["gold_examples_x_change_type"] = {k: {"n": v["n"], "intended_pass_rate": v["passed"] / v["n"]} for k, v in sorted(cross.items())}
    return out


# --- comparisons and power ---------------------------------------------------------------------


def comparisons(rows: list[dict], reference: str = "va_rag", baselines: tuple[str, ...] = PRIMARY_CONTRASTS, seed: int = 1234) -> dict:
    present = {r["method"] for r in rows}
    if reference not in present:
        return {}
    ref_rows = {r["instance_id"]: r for r in targeted(rows) if r["method"] == reference}
    out: dict = {}
    p_values: dict[str, float] = {}
    for base in baselines:
        if base not in present:
            continue
        base_rows = {r["instance_id"]: r for r in targeted(rows) if r["method"] == base}
        shared = sorted(set(ref_rows) & set(base_rows))
        entry: dict = {"n_instances": len(shared)}
        for metric in ("intended_pass", "blend_exec"):
            a = by_concept([ref_rows[i] for i in shared], lambda r: bool(r.get(metric)))
            b = by_concept([base_rows[i] for i in shared], lambda r: bool(r.get(metric)))
            diff = paired_bootstrap(a, b, seed=seed)
            only_ref = sum(1 for i in shared if ref_rows[i].get(metric) and not base_rows[i].get(metric))
            only_base = sum(1 for i in shared if base_rows[i].get(metric) and not ref_rows[i].get(metric))
            p = mcnemar_exact(only_ref, only_base)
            entry[metric] = {"difference": diff.estimate, "bootstrap": [diff.low, diff.high], "concepts": diff.n,
                             "discordant": {"reference_only": only_ref, "baseline_only": only_base}, "mcnemar_p": p}
            p_values[f"{base}:{metric}"] = p
        out[base] = entry
    adjusted = holm(p_values)
    for key, p in adjusted.items():
        base, metric = key.split(":")
        out[base][metric]["mcnemar_p_holm"] = p
    return out


def detectable_effect_table(rows: list[dict], reference: str = "va_rag") -> dict:
    tgt = targeted(rows)
    methods = sorted({r["method"] for r in tgt})
    if not tgt:
        return {}
    per_method = {m: [r for r in tgt if r["method"] == m] for m in methods}
    n = len(per_method[methods[0]])
    concepts = {r["concept_id"] for r in per_method[methods[0]]}
    per_concept = n / len(concepts) if concepts else 1.0
    rhos = [v for v in (intraclass_correlation(by_concept(per_method[m], lambda r: bool(r.get("intended_pass")))) for m in methods) if v is not None]
    rho_est = mean(rhos)
    discordant = []
    if reference in per_method:
        ref = {r["instance_id"]: bool(r.get("intended_pass")) for r in per_method[reference]}
        for m in methods:
            if m == reference:
                continue
            other = {r["instance_id"]: bool(r.get("intended_pass")) for r in per_method[m]}
            shared = set(ref) & set(other)
            if shared:
                discordant.append(sum(ref[i] != other[i] for i in shared) / len(shared))
    table = {"n_instances": n, "concepts": len(concepts), "per_concept": per_concept, "rho_estimated": rho_est,
             "discordant_observed": mean(discordant), "rows": []}
    for d, rho in ((0.2, 0.25), (0.2, 0.5), (0.3, 0.5)):
        table["rows"].append({"discordant": d, "rho": rho, "points": 100 * detectable_difference(n, per_concept, d, rho)})
    if rho_est is not None and table["discordant_observed"]:
        table["rows"].append({"discordant": table["discordant_observed"], "rho": rho_est, "points": 100 * detectable_difference(n, per_concept, table["discordant_observed"], rho_est), "observed": True})
    return table


def compute(run_dir: Path) -> dict:
    run_json, rows, traces = load_run(run_dir)
    seed = int(run_json.get("seed", 1234))
    methods = sorted({r["method"] for r in rows})
    return {
        "run_id": run_json.get("run_id"), "model": run_json.get("model"), "split": run_json.get("split"),
        "user_arm": run_json.get("user_arm"), "reportable": run_json.get("reportable", True), "scoring": run_json.get("scoring", {}),
        "methods": {m: method_metrics(rows, traces, m, seed) for m in methods},
        "comparisons": comparisons(rows, seed=seed),
        "detectable_effect": detectable_effect_table(rows),
    }
