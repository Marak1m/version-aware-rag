"""``varag report``: metrics.json and report.md for one run (handoff, "Metrics", "Statistics")."""

from __future__ import annotations

import json
from pathlib import Path

from varag.eval.metrics import PRIMARY_CONTRASTS, compute


def pct(x: float | None, digits: int = 1) -> str:
    return "n/a" if x is None else f"{100 * x:.{digits}f}%"


def ci(interval: dict | None) -> str:
    if not interval or interval.get("estimate") is None:
        return "n/a"
    low, high = interval["bootstrap"]
    wl, wh = interval["wilson_concepts"]
    return f"{pct(interval['estimate'])} [{pct(low)}, {pct(high)}] (Wilson {pct(wl)}, {pct(wh)})"


def num(x: float | None, digits: int = 2) -> str:
    return "n/a" if x is None else f"{x:.{digits}f}"


def table(headers: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out)


def render(metrics: dict, run_json: dict) -> str:
    methods = metrics["methods"]
    backend = run_json.get("backend", {})
    lines = [f"# VA-RAG run report: {metrics['run_id']}", ""]
    if not metrics.get("reportable", True):
        lines += ["**Not for reporting.** This backend is marked `report: false` (parsing checks only).", ""]
    lines += [
        f"- Model: `{metrics['model']}` = {backend.get('model', 'mock')}" + (f" @ {backend['revision'][:12]}" if backend.get("revision") else "")
        + (f", quantization {backend['quantization']}" if backend.get("quantization") else ""),
        f"- Split: {metrics['split']}; user arm: {metrics['user_arm']}; instances: {run_json.get('instances')}; concepts: {len(run_json.get('concepts', {}))}"
        + (f"; limit {run_json['limit']}" if run_json.get("limit") else ""),
        f"- Scoring of deprecation concepts: primary {metrics.get('scoring', {}).get('deprecation', {}).get('primary', 'strict')} (both reported)",
        f"- Commit {str(run_json.get('git_commit'))[:12]}, config {str(run_json.get('config_hash'))[:12]}, created {run_json.get('created_at')}",
        "",
    ]
    concepts = len(run_json.get("concepts", {}))
    if concepts < 60:
        lines += [f"> {concepts} concepts: below the 60-concept benchmark, so method comparisons here are smoke-test readings, not results.", ""]

    serving = run_json.get("serving") or {}
    if serving.get("server") == "openrouter":
        lines += [f"- OpenRouter: `{serving.get('model')}` pinned to provider `{serving.get('provider_pin')}` "
                  f"(no fallbacks, parameters required)"
                  + (f", served as {backend['quantization_reported']}" if backend.get("quantization_reported") else "")
                  + f"; session `{run_json.get('session')}`; "
                  f"{serving.get('calls')} paid calls, {serving.get('cache_hits')} cache hits, ${serving.get('cost_usd', 0):.4f}"
                  + (f"; providers reported {run_json.get('providers_reported')}" if run_json.get("providers_reported") else "")]
        if backend.get("provider_note"):
            lines += [f"- Provider choice: {backend['provider_note']}"]
        lines += [""]
    repeats = run_json.get("repeats") or [0]
    if len(repeats) > 1:
        lines += [f"- Repeats: every (instance, method) answered under repeat indices {repeats} in one session; an instance's score is the mean "
                  "over its repeats, rates are means of instance scores, and intervals resample concepts.", ""]
    if run_json.get("stopped"):
        lines += [f"> **Stopped early: {run_json['stopped']}.** Instance-major order: every method has the same {run_json.get('instances_completed')} completed instances.", ""]

    lines += ["## Primary metrics", ""]
    rows = []
    for m, v in methods.items():
        rows.append([m, ci(v["intended_pass_rate"]), pct(v.get("intended_pass_rate_defined")), pct(v["intended_pass_rate_strict"]), pct(v["intended_pass_rate_lenient"]),
                     pct(v["outcomes"]["wrong_version"]), pct(v["outcomes"]["portable"]), pct(v["outcomes"]["broken"]),
                     pct(v["outcomes"].get("no_entry_point")), pct(v["outcomes"]["no_code"]), pct(v.get("second_question_rate")), pct(v["soft_fail_rate"])])
    lines += [table(["Method", "Intended-version pass (bootstrap, Wilson)", "pass among answers defining the entry point", "strict", "lenient",
                     "wrong_version", "portable", "broken", "no_entry_point", "no_code", "second question", "soft-fail"], rows), ""]
    if "oracle_docs" in methods:
        lines += ["> `oracle_docs` gives target-version documents with no version statement and no guard, so it is not an upper bound for `va_rag`.", ""]

    lines += ["## Blending, asking, hedging, cost", ""]
    rows = []
    for m, v in methods.items():
        rows.append([m, ci(v["blend_static"]), ci(v["blend_exec"]), pct(v["guarded_portable"]), pct(v["ask_recall"]), pct(v["ask_precision"]),
                     pct(v["over_ask_rate"]), pct(v.get("ask_rate_contradiction")), pct(v["over_hedge_rate"]),
                     ", ".join(f"c={c}: {pct(u)}" for c, u in v["utility"].items()),
                     f"{num(v['cost']['calls_per_instance'])} calls, {num(v['cost']['answers_per_instance'])} answers"])
    lines += [table(["Method", "blend_static", "blend_exec", "guarded_portable", "ask recall", "ask precision", "over-ask", "ask on contradiction", "over-hedge", "utility", "cost / instance"], rows), ""]

    lines += ["## Commit direction, clue following, order", ""]
    rows = []
    for m, v in methods.items():
        d = v["silent_commit_direction"]
        direction = ", ".join(f"{k} {pct(d[k])}" for k in ("old", "new", "both", "neither") if k in d) + f" (n={d.get('n', 0)})"
        rows.append([m, direction, pct(v["clue_following"]), num(v["order_sensitivity"], 3), pct(v.get("both_correct_rate"))])
    lines += [table(["Method", "silent commits on no-clue instances", "clue following", "order sensitivity (first - last)", "both_correct"], rows), ""]

    inference = {m: v for m, v in methods.items() if "inference_precision" in v}
    if inference:
        lines += ["## Inference and guard (VA-RAG family)", ""]
        rows = []
        for m, v in inference.items():
            g = v["guard"]
            rows.append([m, pct(v["inference_precision"]), pct(v["inference_coverage"]), json.dumps(v["decisions"]), json.dumps(v.get("answered_by", {})),
                         num(v["auroc_abs_margin"], 3), str(g["flagged"]), pct(g["precision"]), pct(g["recall"]), pct(g["fix_rate"]), pct(g["harm_rate"])])
        lines += [table(["Method", "inference precision", "coverage on clue instances", "decisions", "answered by (answers)", "AUROC |margin|",
                         "guard flags (answers)", "guard precision", "guard recall", "fix rate", "harm rate"], rows), ""]
        drafts = {m: v["portable_draft"] for m, v in inference.items() if v.get("portable_draft")}
        for m, d in drafts.items():
            lines += [f"Portable-first drafts (`{m}`): {d['drafts']} drafts, {d['accepted']} returned without a question "
                      f"({pct(d['accepted'] / d['drafts'] if d['drafts'] else None)}); rejected: {json.dumps(d['rejected_reasons'])}.", ""]
        curve = inference.get("va_rag", {}).get("risk_coverage") or []
        if curve:
            picks = sorted({0, len(curve) // 4, len(curve) // 2, 3 * len(curve) // 4, len(curve) - 1})
            lines += ["Risk-coverage sweep on |margin| for `va_rag` (coverage = answered without a question, risk = wrong-version commits among them):", "",
                      table(["threshold", "coverage", "risk"], [[num(curve[i]["threshold"]), pct(curve[i]["coverage"]), pct(curve[i]["risk"])] for i in picks]), ""]

    if metrics["comparisons"]:
        lines += ["## Primary contrasts: va_rag against each baseline", "",
                  "Paired bootstrap on per-concept differences of instance scores (va_rag minus baseline); exact McNemar on the repeat-0 instance pairs, "
                  "Holm-adjusted across the contrasts.", ""]
        rows = []
        for base, entry in metrics["comparisons"].items():
            for metric in ("intended_pass", "blend_exec"):
                e = entry[metric]
                rows.append([base, metric, f"{100 * e['difference']:+.1f} pts" if e["difference"] is not None else "n/a",
                             f"[{100 * e['bootstrap'][0]:+.1f}, {100 * e['bootstrap'][1]:+.1f}]" if e["bootstrap"][0] is not None else "n/a",
                             f"{e['discordant']['reference_only']} / {e['discordant']['baseline_only']}", num(e["mcnemar_p"], 4), num(e.get("mcnemar_p_holm"), 4)])
        lines += [table(["Baseline", "Metric", "Difference", "95% bootstrap", "discordant (va_rag only / baseline only)", "McNemar p", "Holm p"], rows), ""]

    lines += ["## Slices", "", "Intended-version pass by slice, for va_rag and the primary baselines. gold_examples and change_type overlap (every keyword-level concept is `neither`), so they are read together in the cross-table.", ""]
    for m in [x for x in ("va_rag", *PRIMARY_CONTRASTS) if x in methods]:
        v = methods[m]
        lines += [f"### {m}", ""]
        for key, cells in v["slices"].items():
            if not cells:
                continue
            lines += [f"**{key}**: " + "; ".join(f"{k} {pct(c['intended_pass_rate'])} (n={c['n']})" for k, c in cells.items()), ""]

    de = metrics.get("detectable_effect") or {}
    if de:
        lines += ["## What size of difference this run can show", "",
                  f"{de['n_instances']} targeted instances over {de['concepts']} concepts ({de['per_concept']:.1f} per concept)"
                  + (f", {de['repeats']} repeats averaged per instance" if de.get("repeats", 1) > 1 else "") + ". "
                  f"Measured within-concept correlation rho = {num(de['rho_estimated'], 3)} (ICC of instance scores, mean over methods); "
                  f"observed discordance against va_rag = {num(de['discordant_observed'], 3)} (mean squared difference of paired instance scores). "
                  "Miller's formula at 80% power, two-sided 5%:", "",
                  table(["discordance", "rho", "detectable difference", "basis"],
                        [[num(r["discordant"], 3), num(r["rho"], 3), f"{r['points']:.1f} points",
                          "observed" if r.get("observed") else ("measured rho" if r.get("measured_rho") else "handoff assumption")] for r in de["rows"]]), ""]
    rd = metrics.get("repeat_disagreement") or {}
    if rd.get("pairs"):
        lines += ["## Repeat disagreement (within this session)", "",
                  f"{rd['pairs']} (instance, method) pairs answered under {rd['repeats']} repeats: response text differs on {pct(rd['text_differs'])}, "
                  f"outcome on {pct(rd['outcome_differs'])}, intended-version pass on {pct(rd['pass_differs'])}.", "",
                  table(["Method", "pairs", "text differs", "outcome differs"],
                        [[m, str(v["pairs"]), pct(v["text"]), pct(v["outcome"])] for m, v in rd["by_method"].items()]), ""]
    return "\n".join(lines)


def write_report(run_dir: Path) -> Path:
    run_json = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    metrics = compute(run_dir)
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    path = run_dir / "report.md"
    path.write_text(render(metrics, run_json), encoding="utf-8", newline="\n")
    return path
