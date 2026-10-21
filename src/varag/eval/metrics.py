"""The metric table (handoff, "Metrics") from a run's results and traces, with slices, intervals,
the primary comparisons, the detectable-effect table and the risk-coverage curve.

Every metric is a plain function of the rows in results.jsonl (one per instance, method and
repeat) and the records in traces.jsonl. Repeats (user decision 2026-10-21): an instance's score is
the mean over its repeats, and every rate is a mean of instance scores, so a repeat never counts
as an instance. Intervals: a cluster bootstrap that resamples concepts (repeats nested inside
instances, instances inside concepts) and a Wilson interval on the concept-level proportion.
Comparisons: paired bootstrap on per-concept differences of instance scores, exact McNemar on the
repeat-0 instance pairs, Holm across the baselines compared with va_rag.
"""

from __future__ import annotations

import gzip
import json
from collections import Counter, defaultdict
from functools import lru_cache
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
    traces: dict[tuple[str, str, int], dict] = {}
    path = run_dir / "traces.jsonl"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                t = json.loads(line)
                traces[(t["method"], t["instance_id"], int(t.get("repeat") or 0))] = t
    return run_json, rows, traces


# --- helpers ----------------------------------------------------------------------------------


def trace_of(traces: dict, method: str, row: dict) -> dict | None:
    return traces.get((method, row["instance_id"], int(row.get("repeat") or 0)))


def instance_scores(rows: list[dict], predicate) -> dict[tuple[str, str], float]:
    """(method, instance_id) -> the mean of the indicator over that instance's repeats."""
    groups: dict[tuple[str, str], list[float]] = defaultdict(list)
    for r in rows:
        groups[(r["method"], r["instance_id"])].append(1.0 if predicate(r) else 0.0)
    return {k: sum(v) / len(v) for k, v in groups.items()}


def n_instances(rows: list[dict]) -> int:
    return len({(r["method"], r["instance_id"]) for r in rows})


def share(rows: list[dict], predicate) -> float | None:
    """The mean of instance scores (each the mean over the instance's repeats)."""
    return mean(list(instance_scores(rows, predicate).values()))


def by_concept(rows: list[dict], predicate) -> dict[str, list[float]]:
    """concept_id -> the scores of its instances (repeats averaged inside each instance)."""
    concept = {(r["method"], r["instance_id"]): r["concept_id"] for r in rows}
    out: dict[str, list[float]] = defaultdict(list)
    for key, score in instance_scores(rows, predicate).items():
        out[concept[key]].append(score)
    return dict(out)


def first_repeat(rows: list[dict]) -> list[dict]:
    """Rows of the lowest repeat index per (method, instance): for counts of things that do not
    depend on the model's output (the decision rule's verdicts)."""
    low: dict[tuple[str, str], int] = {}
    for r in rows:
        key = (r["method"], r["instance_id"])
        low[key] = min(low.get(key, 1 << 30), int(r.get("repeat") or 0))
    return [r for r in rows if int(r.get("repeat") or 0) == low[(r["method"], r["instance_id"])]]


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
    """The decision rule's verdicts, which depend on the instance text only: read on one repeat."""
    decisions = []
    answered_by: Counter = Counter()
    drafts: list[dict] = []
    for r in first_repeat(rows):
        t = trace_of(traces, method, r)
        mt = (t or {}).get("method_trace") or {}
        d = mt.get("decision")
        if d:
            decisions.append((r, d))
    for r in rows:
        mt = (trace_of(traces, method, r) or {}).get("method_trace") or {}
        if mt.get("by"):
            answered_by[mt["by"]] += 1
        if mt.get("portable"):
            drafts.append(mt["portable"])
    if not decisions:
        return {}
    inferred = [(r, d) for r, d in decisions if d["kind"] == "INFER"]
    precision = mean([1.0 if d["side"] == r["target"] else 0.0 for r, d in inferred if r.get("target")])
    clue_rows = [(r, d) for r, d in decisions if r.get("condition") == "clue"]
    coverage = mean([1.0 if d["kind"] == "INFER" else 0.0 for r, d in clue_rows])
    margins = [abs(d["margin"]) for r, d in inferred if r.get("target")]
    correct = [d["side"] == r["target"] for r, d in inferred if r.get("target")]
    portable = {"drafts": len(drafts), "accepted": sum(1 for d in drafts if d.get("accepted")),
                "rejected_reasons": dict(Counter(d.get("reason") for d in drafts if not d.get("accepted")))} if drafts else None
    return {"inference_precision": precision, "inference_coverage": coverage,
            "decisions": dict(Counter(d["kind"] for _, d in decisions)),
            "answered_by": dict(answered_by), "portable_draft": portable,
            "risk_coverage": risk_coverage(margins, correct) if margins else [],
            "auroc_abs_margin": auroc(margins, correct) if margins else None}


def names_exclusive(exec_record: dict, code: str | None, library: str) -> bool:
    if not exec_record or exec_record.get("exc_type") not in EXCLUSIVE_ERRORS or not exec_record.get("last_line") or not code:
        return False
    old, new = usage_sides(code, library)
    names = {s.split("(")[0].rsplit(".", 1)[-1] for s in old | new} | {s.split("(")[-1].rstrip(")").split("=")[0] for s in old | new if "(" in s}
    return any(n and n in exec_record["last_line"] for n in names)


@lru_cache(maxsize=1)
def _gold() -> dict:
    from varag.bench.schema import load_concepts

    return {c.id: c.gold for c in load_concepts()}


@lru_cache(maxsize=65536)
def _conflicting(code: str | None, library: str, target: str) -> tuple[str, ...]:
    from varag.eval.oracle import conflicting_usages

    return tuple(conflicting_usages(code, library, target))


def guard_metrics(rows: list[dict], traces: dict, method: str) -> dict:
    """Guard verdict against the execution oracle, plus fix and harm rates. The top-level precision
    and recall use the M7 oracle (``exclusive_error``); ``strict_named`` holds the corrected oracle
    of 2026-10-21 (``varag.eval.oracle``), which also sees rejected values and strict deprecation
    failures. Counts are answers (instances x repeats)."""
    from varag.eval.oracle import pre_guard_evidence, strict_named

    tp = fp = fn = fixes = harms = flagged_total = 0
    new = {"flagged": 0, "tp": 0, "positives": 0, "caught": 0}
    by_change: dict[str, dict] = defaultdict(lambda: {"flagged": 0, "tp": 0, "positives": 0, "caught": 0})
    guarded_method = False
    for r in rows:
        if not r.get("target"):
            continue
        t = trace_of(traces, method, r)
        answers = ((t or {}).get("method_trace") or {}).get("answers") or []
        guard = next((a.get("guard") for a in answers if a.get("side") in (r["target"], None)), (answers[0].get("guard") if answers else None)) or {}
        guarded_method = guarded_method or bool(guard)
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
        if not guard or not oracle_code:
            continue
        code, ev = pre_guard_evidence(r)
        other = "new" if r["target"] == "old" else "old"
        own = [v["symbol"] for v in guard.get("violations", []) if v.get("side") == other or (r["target"] == "new" and v.get("side") == "deprecated_in_new")]
        own_hit = flagged and strict_named(ev, own)
        gold = _gold().get(r["concept_id"]) or {}
        # The other version's gold is a version-exclusive usage, except for a behaviour concept (the
        # same API on both sides) and a symbol the target version's gold also uses.
        gold_other = [] if r.get("exclusivity") == "behavior" else [g for g in gold.get(other, []) if g not in set(gold.get(r["target"], []))]
        positive = ev.failed and strict_named(ev, own + list(_conflicting(code, r["library"], r["target"])) + gold_other)
        for cell in (new, by_change[str(r.get("change_type"))]):
            cell["flagged"] += flagged
            cell["tp"] += own_hit
            cell["positives"] += positive
            cell["caught"] += flagged and positive
    out = {"flagged": flagged_total, "precision": tp / (tp + fp) if tp + fp else None, "recall": tp / (tp + fn) if tp + fn else None,
           "fix_rate": fixes / flagged_total if flagged_total else None, "harm_rate": harms / flagged_total if flagged_total else None,
           "exclusive_error": {"tp": tp, "fp": fp, "fn": fn}}
    if guarded_method:
        def rates(c: dict) -> dict:
            return {**c, "precision": c["tp"] / c["flagged"] if c["flagged"] else None, "recall": c["caught"] / c["positives"] if c["positives"] else None}

        out["strict_named"] = {**rates(new), "by_change_type": {k: rates(v) for k, v in sorted(by_change.items())}}
    return out


def order_sensitivity(rows: list[dict], traces: dict, method: str) -> float | None:
    first, last = [], []
    for r in rows:
        if not r.get("target"):
            continue
        t = trace_of(traces, method, r)
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
        "n_targeted": n_instances(tgt), "n_controls": n_instances(controls), "n_rows": len(mine),
        "repeats": sorted({int(r.get("repeat") or 0) for r in mine}),
        "intended_pass_rate": intervals(tgt, lambda r: bool(r.get("intended_pass")), seed),
        "intended_pass_rate_strict": share(tgt, lambda r: intended_pass(r.get("outcome_strict", r["outcome"]))),
        "intended_pass_rate_lenient": share(tgt, lambda r: intended_pass(r.get("outcome_lenient", r["outcome"]))),
        "outcomes": {k: share(tgt, lambda r, k=k: r["outcome"] == k) for k in ("target_only", "portable", "wrong_version", "broken", "no_entry_point", "no_code", "infra_error")},
        # Prompt review (2026-10-19): the pass rate among answers that define the entry point, and
        # questions given as the final reply after a user reply or against a "do not ask" line.
        "intended_pass_rate_defined": share([r for r in tgt if r.get("defines_entry_point")], lambda r: bool(r.get("intended_pass"))),
        "no_entry_point_rate": share(mine, lambda r: r["outcome"] == "no_entry_point"),
        "second_question_rate": share(mine, lambda r: bool(r.get("second_question"))),
        "final_question_rate": share(mine, lambda r: bool(r.get("final_question"))),
        "ask_rate_contradiction": share([r for r in tgt if r.get("condition") == "contradiction"], asked),
        "control_outcomes": dict(Counter(r["outcome"] for r in controls)),      # answers (instances x repeats)
        "control_pass_both": share(controls, lambda r: r["outcome"] == "pass_both"),
        "soft_fail_rate": share(passing, lambda r: bool(r.get("soft_fail"))),
        "blend_static": intervals(tgt, lambda r: bool(r.get("blend_static")), seed),
        "blend_exec": intervals(tgt, lambda r: bool(r.get("blend_exec")), seed),
        "guarded_portable": share(tgt, lambda r: bool(r.get("guarded_portable"))),
        "ask_recall": share(no_clue, lambda r: relevant_question(r, trace_of(traces, method, r))),
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
        out["slices"][key] = {v: {"n": n_instances(s), "concepts": len({r["concept_id"] for r in s}),
                                  "intended_pass_rate": share(s, lambda r: bool(r.get("intended_pass"))),
                                  "intended_pass_rate_lenient": share(s, lambda r: intended_pass(r.get("outcome_lenient", r["outcome"]))),
                                  "blend_exec": share(s, lambda r: bool(r.get("blend_exec")))}
                              for v in values for s in [[r for r in tgt if str(r.get(key)) == v]]}
    cross: dict[str, list[dict]] = defaultdict(list)
    for r in tgt:
        cross[f"{r.get('gold_examples')} / {r.get('change_type')}"].append(r)
    out["slices"]["gold_examples_x_change_type"] = {k: {"n": n_instances(v), "intended_pass_rate": share(v, lambda r: bool(r.get("intended_pass")))}
                                                    for k, v in sorted(cross.items())}
    return out


# --- comparisons and power ---------------------------------------------------------------------


def comparisons(rows: list[dict], reference: str = "va_rag", baselines: tuple[str, ...] = PRIMARY_CONTRASTS, seed: int = 1234) -> dict:
    present = {r["method"] for r in rows}
    if reference not in present:
        return {}
    tgt = targeted(rows)
    ref_ids = {r["instance_id"] for r in tgt if r["method"] == reference}
    out: dict = {}
    p_values: dict[str, float] = {}
    for base in baselines:
        if base not in present:
            continue
        shared = sorted(ref_ids & {r["instance_id"] for r in tgt if r["method"] == base})
        keep = set(shared)
        ref_rows = [r for r in tgt if r["method"] == reference and r["instance_id"] in keep]
        base_rows = [r for r in tgt if r["method"] == base and r["instance_id"] in keep]
        entry: dict = {"n_instances": len(shared)}
        for metric in ("intended_pass", "blend_exec"):
            a = by_concept(ref_rows, lambda r: bool(r.get(metric)))
            b = by_concept(base_rows, lambda r: bool(r.get(metric)))
            diff = paired_bootstrap(a, b, seed=seed)
            # McNemar needs one binary pair per instance: the repeat-0 answers.
            ref0 = {r["instance_id"]: bool(r.get(metric)) for r in first_repeat(ref_rows)}
            base0 = {r["instance_id"]: bool(r.get(metric)) for r in first_repeat(base_rows)}
            only_ref = sum(1 for i in shared if ref0[i] and not base0[i])
            only_base = sum(1 for i in shared if base0[i] and not ref0[i])
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
    """Miller's formula with the within-concept correlation measured on this run: rho is the
    one-way ANOVA ICC of instance scores (repeats averaged), averaged over methods; the observed
    discordance is the mean squared difference of paired instance scores against ``reference``
    (the discordant share when there is one repeat). Rows: discordance 0.1, 0.2, 0.3 at the
    measured rho, the observed (discordance, rho), and the handoff's planning assumptions."""
    tgt = targeted(rows)
    methods = sorted({r["method"] for r in tgt})
    if not tgt:
        return {}
    pass_ = lambda r: bool(r.get("intended_pass"))  # noqa: E731
    per_method = {m: [r for r in tgt if r["method"] == m] for m in methods}
    n = n_instances(per_method[methods[0]])
    concepts = {r["concept_id"] for r in per_method[methods[0]]}
    per_concept = n / len(concepts) if concepts else 1.0
    rhos = {m: intraclass_correlation(by_concept(per_method[m], pass_)) for m in methods}
    rho_est = mean([v for v in rhos.values() if v is not None])
    discordant = []
    if reference in per_method:
        ref = {i: v for (_, i), v in instance_scores(per_method[reference], pass_).items()}
        for m in methods:
            if m == reference:
                continue
            other = {i: v for (_, i), v in instance_scores(per_method[m], pass_).items()}
            shared = set(ref) & set(other)
            if shared:
                discordant.append(sum((ref[i] - other[i]) ** 2 for i in shared) / len(shared))
    repeats = sorted({int(r.get("repeat") or 0) for r in tgt})
    table = {"n_instances": n, "concepts": len(concepts), "per_concept": per_concept, "repeats": len(repeats), "rho_estimated": rho_est,
             "rho_by_method": rhos, "discordant_observed": mean(discordant), "rows": []}
    if rho_est is not None:
        for d in (0.1, 0.2, 0.3):
            table["rows"].append({"discordant": d, "rho": rho_est, "points": 100 * detectable_difference(n, per_concept, d, rho_est), "measured_rho": True})
        if table["discordant_observed"]:
            table["rows"].append({"discordant": table["discordant_observed"], "rho": rho_est,
                                  "points": 100 * detectable_difference(n, per_concept, table["discordant_observed"], rho_est), "observed": True})
    for d, rho in ((0.2, 0.25), (0.2, 0.5)):
        table["rows"].append({"discordant": d, "rho": rho, "points": 100 * detectable_difference(n, per_concept, d, rho), "assumed": True})
    return table


def repeat_disagreement(rows: list[dict]) -> dict:
    """Within-session repeat disagreement: among (instance, method) pairs answered under two or
    more repeat indices, the share whose response texts differ and whose outcomes differ."""
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in rows:
        groups[(r["method"], r["instance_id"])].append(r)
    multi = {k: v for k, v in groups.items() if len({int(x.get("repeat") or 0) for x in v}) >= 2}
    if not multi:
        return {"pairs": 0}
    text = [k for k, v in multi.items() if len({x.get("response_text") for x in v}) > 1]
    outcome = [k for k, v in multi.items() if len({x["outcome"] for x in v}) > 1]
    passed = [k for k, v in multi.items() if len({bool(x.get("intended_pass")) for x in v}) > 1]
    by_method = {}
    for m in sorted({k[0] for k in multi}):
        keys = [k for k in multi if k[0] == m]
        by_method[m] = {"pairs": len(keys), "text": sum(k in set(text) for k in keys) / len(keys),
                        "outcome": sum(k in set(outcome) for k in keys) / len(keys)}
    return {"pairs": len(multi), "repeats": max(len(v) for v in multi.values()),
            "text_differs": len(text) / len(multi), "outcome_differs": len(outcome) / len(multi),
            "pass_differs": len(passed) / len(multi), "by_method": by_method}


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
        "repeat_disagreement": repeat_disagreement(rows),
    }
