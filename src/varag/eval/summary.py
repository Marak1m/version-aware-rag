"""The combined summary of the final sweep (user decision 2026-10-21) and one report per model.

Written to ``docs/results/final-<stamp>/``:

  summary.md, summary.json   every model side by side: the strict (primary) and lenient
                             intended-version pass with concept-clustered 95% bootstrap intervals
                             (repeats averaged inside instances, concepts resampled), asking and
                             cost, the contrasts against va_rag, portable-first against va_rag, the
                             detectable-effect table with the measured within-concept correlation,
                             slices by library, class, change type, clue type and user arm, the
                             within-session repeat disagreement, costs and anything that failed
  <model>.md                 the model's runs (dev and test, both arms), each run's full report
  audit_sample.jsonl, .md    the 50-output guard audit sample over the three models' test runs,
                             drawn once and never overwritten; its hand labels, when filled in,
                             give the detector's precision and recall in summary.md

Strict is the primary score: a deprecation concept's answer that uses the deprecated API fails;
every other concept is scored on its tests alone. Lenient lets deprecated usage pass (soft_fail).
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Callable

from varag.config import project_root
from varag.eval.metrics import (PRIMARY_CONTRASTS, comparisons, intervals, load_run, n_instances, repeat_disagreement,
                                share, targeted)
from varag.eval.outcomes import intended_pass

METHOD_ORDER = ("va_rag", "va_rag_portable_first", "va_rag_no_infer", "va_rag_no_ask", "va_rag_no_guard", "plain_rag", "mind_version",
                "assume_state", "two_branch", "always_ask", "oracle_docs", "no_retrieval")
SLICE_METHODS = ("va_rag", "va_rag_portable_first", "plain_rag", "two_branch", "always_ask", "oracle_docs")
SLICE_KEYS = (("library", "library"), ("exclusivity", "class"), ("change_type", "change type"), ("clue", "clue type"))


def results_dir(stamp: str) -> Path:
    return project_root() / "docs" / "results" / f"final-{stamp}"


def pct(x: float | None, digits: int = 1) -> str:
    return "n/a" if x is None else f"{100 * x:.{digits}f}"


def cell(iv: dict) -> str:
    if not iv or iv.get("estimate") is None:
        return "n/a"
    low, high = iv["bootstrap"]
    return f"{pct(iv['estimate'])} [{pct(low)}, {pct(high)}]"


def table(headers: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    return "\n".join(out + ["| " + " | ".join(r) + " |" for r in rows])


def clue_of(r: dict) -> str:
    return f"clue-{r.get('clue_type')}" if r.get("condition") == "clue" else str(r.get("condition"))


def strict_pass(r: dict) -> bool:
    return bool(r.get("intended_pass"))


def lenient_pass(r: dict) -> bool:
    return intended_pass(r.get("outcome_lenient", r["outcome"])) if r.get("target") else r["outcome"] == "pass_both"


class Loaded:
    """One run: run.json, metrics.json, rows and traces."""

    def __init__(self, run_dir: Path):
        self.dir = run_dir
        self.meta, self.rows, self.traces = load_run(run_dir)
        path = run_dir / "metrics.json"
        if not path.exists():
            from varag.eval.report import write_report

            write_report(run_dir)
        self.metrics = json.loads(path.read_text(encoding="utf-8"))

    def methods(self) -> list[str]:
        present = {r["method"] for r in self.rows}
        return [m for m in METHOD_ORDER if m in present] + sorted(present - set(METHOD_ORDER))

    def of(self, method: str) -> list[dict]:
        return [r for r in self.rows if r["method"] == method]


def load_sweep(record: dict) -> dict[str, dict[str, Loaded]]:
    from varag.eval.run import runs_dir

    out: dict[str, dict[str, Loaded]] = {}
    for model, entry in record["models"].items():
        out[model] = {name: Loaded(runs_dir() / run_id) for name, run_id in (entry.get("runs") or {}).items()
                      if (runs_dir() / run_id / "run.json").exists()}
    return out


def ledger_costs(sessions: list[str], backends: list[str], since: str | None, until: str | None) -> dict:
    """Paid calls from logs/costs.jsonl: per session, and every call of the sweep's backends in its
    time window (endpoint checks and outage probes included, which carry no session)."""
    from varag import logbook

    path = logbook.logs_dir() / "costs.jsonl"
    wanted = set(sessions)
    by_session: dict[str, float] = {}
    window = 0.0
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            usd = float(rec.get("cost_usd") or 0)
            if rec.get("session") in wanted:
                by_session[rec["session"]] = by_session.get(rec["session"], 0.0) + usd
            ts = str(rec.get("ts", ""))[:19]
            if rec.get("backend") in backends and since and ts >= since[:19] and (until is None or ts <= until[:19]):
                window += usd
    return {"by_session": {k: round(v, 6) for k, v in by_session.items()}, "window": round(window, 6)}


def compute_summary(record: dict, runs: dict[str, dict[str, Loaded]]) -> dict:
    seed = 1234
    out: dict = {"stamp": record["stamp"], "git_commit": record.get("git_commit"), "models": {}, "failures": list(record.get("failures", []))}
    for model, by_name in runs.items():
        entry = record["models"][model]
        m: dict = {"session": entry["session"], "runs": {}, "acceptance": {}, "repeat_disagreement": {}}
        answers = [r for name, run in by_name.items() if name != "dev-noise-repeat" for r in run.rows]
        m["acceptance"] = {"answers": len(answers),
                           "no_entry_point": sum(r["outcome"] == "no_entry_point" for r in answers) / len(answers) if answers else None,
                           "second_question": sum(bool(r.get("second_question")) for r in answers) / len(answers) if answers else None,
                           "infra_error": sum(r["outcome"] == "infra_error" for r in answers),
                           "no_code": sum(r["outcome"] == "no_code" for r in answers),
                           "provider_mismatch": sum(1 for r in answers if (r.get("openrouter") or {}).get("provider_match") is False),
                           "truncated": sum(1 for r in answers for f in (r.get("openrouter") or {}).get("finish_reasons", []) if f == "length"),
                           "providers": dict(Counter(p for r in answers for p in (r.get("openrouter") or {}).get("providers", []))),
                           "models_reported": dict(Counter(x for r in answers for x in (r.get("openrouter") or {}).get("models", [])))}
        for name, run in by_name.items():
            if name == "dev-noise-repeat":
                continue
            per_method = {}
            for method in run.methods():
                mine = run.of(method)
                tgt = targeted(mine)
                mm = run.metrics["methods"][method]
                per_method[method] = {
                    "n_instances": n_instances(tgt), "concepts": len({r["concept_id"] for r in tgt}),
                    "strict": intervals(tgt, strict_pass, seed), "lenient": intervals(tgt, lenient_pass, seed),
                    "questions_per_instance": mm["cost"]["questions_per_instance"], "calls_per_instance": mm["cost"]["calls_per_instance"],
                    "answers_per_instance": mm["cost"]["answers_per_instance"], "ask_recall": mm["ask_recall"], "over_ask": mm["over_ask_rate"],
                    "ask_on_contradiction": mm.get("ask_rate_contradiction"), "over_hedge": mm["over_hedge_rate"],
                    "portable": mm["outcomes"].get("portable"), "wrong_version": mm["outcomes"].get("wrong_version"),
                    "broken": mm["outcomes"].get("broken"), "no_entry_point": mm["outcomes"].get("no_entry_point"),
                    "blend_exec": (mm.get("blend_exec") or {}).get("estimate"),
                    "controls_pass_both": share([r for r in mine if not r.get("target")], lambda r: r["outcome"] == "pass_both"),
                    "portable_draft": mm.get("portable_draft"), "answered_by": mm.get("answered_by"),
                    "guard": mm.get("guard"), "utility": mm.get("utility"),
                }
            portable_vs = comparisons(run.rows, reference="va_rag_portable_first", baselines=("va_rag",), seed=seed) if "va_rag_portable_first" in per_method else {}
            m["runs"][name] = {"run_id": run.meta["run_id"], "split": run.meta["split"], "user_arm": run.meta["user_arm"], "repeats": run.meta.get("repeats"),
                               "instances": run.meta["instances"], "cost_usd": run.meta.get("cost_usd"), "wall_seconds": run.meta.get("wall_seconds"),
                               "stopped": run.meta.get("stopped"), "methods": per_method, "contrasts": run.metrics.get("comparisons", {}),
                               "portable_vs_va_rag": portable_vs.get("va_rag"), "detectable_effect": run.metrics.get("detectable_effect"),
                               "slices": slices(run), "repeat_disagreement": run.metrics.get("repeat_disagreement") or repeat_disagreement(run.rows)}
            if (m["runs"][name]["repeat_disagreement"] or {}).get("pairs"):
                m["repeat_disagreement"][name] = m["runs"][name]["repeat_disagreement"]
        if "dev-noise-repeat" in by_name and "dev-knows" in by_name:
            ids = {r["instance_id"] for r in by_name["dev-noise-repeat"].rows}
            pooled = [r for r in by_name["dev-knows"].rows if r["instance_id"] in ids] + by_name["dev-noise-repeat"].rows
            m["repeat_disagreement"]["dev noise subset (repeat 0 and 1)"] = repeat_disagreement(pooled)
        m["runs_cost_usd"] = round(sum(float(r.meta.get("cost_usd") or 0) for r in by_name.values()), 6)
        m["wall_seconds"] = round(sum(float(r.meta.get("wall_seconds") or 0) for r in by_name.values()), 1)
        if "dev-noise-repeat" in by_name:
            meta = by_name["dev-noise-repeat"].meta
            m["noise_run"] = {"run_id": meta["run_id"], "cost_usd": meta.get("cost_usd"), "wall_seconds": meta.get("wall_seconds"), "repeats": meta.get("repeats")}
        out["models"][model] = m
    # Costs from the ledger: a run that failed before writing run.json (an interrupted attempt) is
    # still in it, so the per-session total is the true spend; run.json costs are per finished run.
    ledger = ledger_costs([m["session"] for m in out["models"].values()], list(out["models"]), record.get("started_at"), record.get("finished_at"))
    for model, m in out["models"].items():
        m["cost_usd"] = ledger["by_session"].get(m["session"], m["runs_cost_usd"])
    out["cost_usd"] = round(sum(m["cost_usd"] for m in out["models"].values()), 6)
    out["cost_window_usd"] = ledger["window"]
    out["history"] = record.get("history") or []
    out["interruptions"] = record.get("interruptions") or []
    return out


def slices(run: Loaded) -> dict:
    out: dict = {}
    for method in [m for m in SLICE_METHODS if m in run.methods()]:
        tgt = targeted(run.of(method))
        out[method] = {}
        for key, _ in SLICE_KEYS:
            value = clue_of if key == "clue" else (lambda r, k=key: str(r.get(k)))
            groups: dict[str, list[dict]] = {}
            for r in tgt:
                groups.setdefault(value(r), []).append(r)
            out[method][key] = {v: {"n": n_instances(g), "concepts": len({r["concept_id"] for r in g}), "strict": share(g, strict_pass),
                                    "lenient": share(g, lenient_pass)} for v, g in sorted(groups.items())}
    return out


# --- rendering ---------------------------------------------------------------------------------


def _models_block(record: dict, summary: dict) -> list[str]:
    from varag.config import load_models

    backends = load_models()["backends"]
    rows = []
    for model, m in summary["models"].items():
        spec = backends[model]
        acc = m["acceptance"]
        rows.append([model, f"`{spec['model']}`", f"{spec.get('provider_name', spec['provider'])} (`{spec['provider']}`)" + (f", {spec['quantization_reported']}" if spec.get("quantization_reported") else ""),
                     str(len(record["models"][model]["items"][0]["repeats"])), f"`{m['session']}`", f"${m['cost_usd']:.4f}", f"{m['wall_seconds'] / 3600:.1f} h",
                     ", ".join(f"{k} {v}" for k, v in acc["providers"].items())])
    lines = [table(["Role", "OpenRouter model", "Provider (pin)", "Repeats", "Session", "Cost", "Run time", "Providers reported (answers)"], rows), ""]
    for model in summary["models"]:
        if backends[model].get("provider_note"):
            lines.append(f"- {model}: {backends[model]['provider_note']}.")
    return lines + [""]


def _pass_table(summary: dict, split: str, score: str) -> list[str]:
    models = list(summary["models"])
    arms = [a for a in ("knows", "unsure") if any(f"{split}-{a}" in summary["models"][m]["runs"] for m in models)]
    headers = ["Method"] + [f"{m} / {a}" for m in models for a in arms]
    methods: list[str] = []
    for m in models:
        for a in arms:
            for method in (summary["models"][m]["runs"].get(f"{split}-{a}") or {}).get("methods", {}):
                if method not in methods:
                    methods.append(method)
    rows = []
    for method in methods:
        row = [method]
        for m in models:
            for a in arms:
                v = ((summary["models"][m]["runs"].get(f"{split}-{a}") or {}).get("methods") or {}).get(method)
                row.append(cell(v[score]) if v else "n/a")
        rows.append(row)
    return [table(headers, rows), ""]


def _instances_line(summary: dict, split: str) -> str:
    for m in summary["models"].values():
        run = m["runs"].get(f"{split}-knows")
        if run:
            va = run["methods"].get("va_rag") or next(iter(run["methods"].values()))
            return f"{va['n_instances']} targeted instances over {va['concepts']} concepts"
    return ""


def render_summary(record: dict, summary: dict) -> str:
    from varag.config import load_experiment
    from varag.pipeline.prompts import frozen_prompts

    exp = load_experiment()
    prompts = frozen_prompts() or {}
    lines = [f"# VA-RAG final sweep: combined summary ({record['stamp']})", "",
             f"- Commit `{str(record.get('git_commit'))[:12]}`; prompts sha256 `{str(prompts.get('sha256'))[:12]}` (frozen {prompts.get('frozen_on')}); "
             f"thresholds tau_commit {exp['thresholds']['tau_commit']}, tau_noise {exp['thresholds']['tau_noise']} (frozen {exp['thresholds']['frozen_on']}).",
             f"- Test split: {_instances_line(summary, 'test')}; dev split: {_instances_line(summary, 'dev')}. Instance-major runs; one session per model "
             "(one session id and one session-private response cache); the three models ran side by side.",
             "- Scores: **strict** (primary; a deprecation concept's answer that uses the deprecated API fails) and **lenient** (deprecated usage passes). "
             "Each cell is the intended-version pass in percent with its 95% bootstrap interval; an instance's score is the mean over its repeats and "
             "the bootstrap resamples concepts (repeats nested in instances, instances in concepts).",
             f"- Cost: ${summary['cost_usd']:.4f} over the three sessions (the cost ledger, interrupted attempts included); "
             f"${summary.get('cost_window_usd', 0):.4f} for every paid call of the three backends while the sweep ran, endpoint checks and outage probes "
             f"included (cap ${record.get('max_usd') or 0:.2f}).",
             "- The unsure arm: when the user cannot name the version, va_rag and its asking ablations fall back to both labelled answers and the "
             "score reads the target's block. That block is the same request as the knows arm's committed answer, served from the session cache, "
             "so their rows match the knows arm exactly (they pay with a second answer: see over-hedging in the per-model reports). two_branch, "
             "assume_state and va_rag_no_ask never ask, so the arm cannot change them; always_ask and the methods where the model decides to ask "
             "are the ones whose unsure scores drop.",
             "- va_rag_no_infer equals va_rag on every pass rate: inference is right on every committed clue instance, so asking reaches the same "
             "committed prompt; it differs in over-asking (see the asking table).", ""]
    lines += ["## Models", ""] + _models_block(record, summary)

    failed = list(summary["failures"])
    for attempt in summary.get("history") or []:
        for f in attempt.get("failures") or []:
            failed.append(f"attempt ended {attempt.get('finished_at')}: {f[:300]}")
    lines += ["## What failed or was interrupted", ""]
    lines += [f"- {f}" for f in failed] + [f"- {note}" for note in summary.get("interruptions") or []]
    if not failed and not summary.get("interruptions"):
        lines += ["- Nothing."]
    lines += [""]
    lines += ["## Limitations", "",
              "- Inference accuracy is 100% by construction: validation step 6 keeps a concept only if each of its clues, alone, makes the "
              "extractor infer the clue's version, so every clue instance is one the extractor reads correctly. The inference precision and "
              "coverage of 1.0 here measure nothing beyond that; clues written by real users would not be filtered this way.",
              "- In the unsure arm va_rag's fallback returns both labelled answers and is scored on the target's block, like two_branch; its "
              "pass rate there is not comparable with a single answer. Compare it with two_branch and on cost-penalised utility "
              "(pass rate minus c times the share of instances with a question or a second answer):", ""]
    rows = []
    for model, m in summary["models"].items():
        run = m["runs"].get("test-unsure")
        if not run:
            continue
        for method in ("va_rag", "va_rag_portable_first", "two_branch", "always_ask", "plain_rag"):
            v = run["methods"].get(method)
            if v and v.get("utility"):
                rows.append([model, method, pct(v["strict"]["estimate"]), pct(v["utility"].get("0.1")), pct(v["utility"].get("0.3")),
                             pct(v["questions_per_instance"]), f"{v['answers_per_instance']:.2f}" if v.get("answers_per_instance") is not None else "n/a"])
    lines += [table(["Model", "Method (test, unsure)", "strict pass %", "utility c=0.1 %", "utility c=0.3 %", "questions %", "answers per instance"], rows), "",
              "- The small model is the general `qwen/qwen-2.5-7b-instruct`, not the coder 7B the handoff names (no live endpoint on "
              "2026-10-19); small-versus-mid mixes scale with code specialisation.",
              "- Large is served as fp4 by DeepInfra, a quantization the provider chose; the full-precision model may score differently.",
              "- The simulated user is idealised: the knowing user always names the right version when asked about it, the unsure user never "
              "does, and both answer only questions that mention the library or the word \"version\". Real users fall between and can be wrong.",
              "- Serving is not deterministic at temperature 0 on Phala and DeepInfra (repeat disagreement below); small and large average three "
              "repeats, mid answers once.", ""]
    lines += ["## Acceptance checks (all answers, dev and test, both arms)", ""]
    rows = []
    for model, m in summary["models"].items():
        a = m["acceptance"]
        rows.append([model, str(a["answers"]), pct(a["no_entry_point"]), pct(a["second_question"]), str(a["no_code"]), str(a["infra_error"]),
                     str(a["provider_mismatch"]), str(a["truncated"])])
    lines += [table(["Model", "answers", "no_entry_point %", "second question %", "no_code", "infra_error", "provider mismatch", "cut at max_tokens"], rows), ""]

    for split in ("test", "dev"):
        lines += [f"## {split.capitalize()} split: intended-version pass, strict (primary)", ""] + _pass_table(summary, split, "strict")
        lines += [f"## {split.capitalize()} split: intended-version pass, lenient", ""] + _pass_table(summary, split, "lenient")

    lines += ["## Asking, hedging and cost (test, knows arm)", "",
              "Per method: questions per instance, ask recall on no-clue instances, over-ask on clue, stated and control instances, ask on "
              "contradiction instances, two-answer (hedged) rate, model calls per instance, portable outcomes.", ""]
    for model, m in summary["models"].items():
        run = m["runs"].get("test-knows")
        if not run:
            continue
        rows = [[method, pct(v["questions_per_instance"]), pct(v["ask_recall"]), pct(v["over_ask"]), pct(v["ask_on_contradiction"]), pct(v["over_hedge"]),
                 f"{v['calls_per_instance']:.2f}" if v["calls_per_instance"] is not None else "n/a", pct(v["portable"])] for method, v in run["methods"].items()]
        lines += [f"### {model}", "", table(["Method", "questions %", "ask recall %", "over-ask %", "ask on contradiction %", "hedged %", "calls", "portable %"], rows), ""]

    lines += ["## Contrasts on test: va_rag minus each primary baseline (strict)", "",
              "Paired bootstrap on per-concept differences of instance scores, 95% interval, points; McNemar on repeat-0 pairs, Holm-adjusted.", ""]
    rows = []
    for model, m in summary["models"].items():
        for arm in ("knows", "unsure"):
            run = m["runs"].get(f"test-{arm}")
            for base in PRIMARY_CONTRASTS:
                e = ((run or {}).get("contrasts") or {}).get(base, {}).get("intended_pass")
                if e and e["difference"] is not None:
                    rows.append([model, arm, base, f"{100 * e['difference']:+.1f}", f"[{100 * e['bootstrap'][0]:+.1f}, {100 * e['bootstrap'][1]:+.1f}]",
                                 f"{e['mcnemar_p_holm']:.4f}" if e.get("mcnemar_p_holm") is not None else "n/a"])
    lines += [table(["Model", "Arm", "Baseline", "Difference", "95% bootstrap", "Holm p"], rows), ""]

    lines += ["## Portable first (L16) against va_rag", "",
              "Where va_rag would ask, `va_rag_portable_first` first drafts an answer from the `shared_same` chunks with \"Use only APIs that exist in "
              "both ...\" and returns it without a question when the guard finds no exclusive or deprecated usage. Success would be fewer questions "
              "at the same pass rate, with more portable outcomes.", ""]
    rows = []
    for model, m in summary["models"].items():
        for split in ("test", "dev"):
            for arm in ("knows", "unsure"):
                run = m["runs"].get(f"{split}-{arm}")
                if not run or "va_rag_portable_first" not in run["methods"]:
                    continue
                pf, va = run["methods"]["va_rag_portable_first"], run["methods"]["va_rag"]
                d = pf.get("portable_draft") or {}
                diff = (run.get("portable_vs_va_rag") or {}).get("intended_pass") or {}
                rows.append([model, split, arm, f"{d.get('accepted', 0)}/{d.get('drafts', 0)}", f"{pct(va['questions_per_instance'])} -> {pct(pf['questions_per_instance'])}",
                             f"{pct(va['strict']['estimate'])} -> {pct(pf['strict']['estimate'])}",
                             (f"{100 * diff['difference']:+.1f} [{100 * diff['bootstrap'][0]:+.1f}, {100 * diff['bootstrap'][1]:+.1f}]" if diff.get("difference") is not None else "n/a"),
                             f"{pct(va['portable'])} -> {pct(pf['portable'])}", f"{pct(va['controls_pass_both'])} -> {pct(pf['controls_pass_both'])}"])
    lines += [table(["Model", "Split", "Arm", "drafts kept (answers)", "questions % va_rag -> pf", "strict pass % va_rag -> pf", "pf minus va_rag, points (95%)",
                     "portable outcomes %", "controls pass both %"], rows), ""]

    lines += ["## Guard and detector accuracy (test, knows arm)", "",
              "The guard's verdict against execution, for the guarded methods, on the pre-guard answers (counts are answers: instances x "
              "repeats). Exclusive-error oracle (M7): the answer fails in the committed version with an AttributeError, ImportError or "
              "TypeError whose message names an exclusive symbol. Strict-named oracle (2026-10-21 correction): the answer fails in the "
              "committed version under the strict score, and the usage (symbol, keyword or value) appears in the error or traceback, in a "
              "warning the strict score counts, or on the failing line; precision counts the guard's own flagged usages, recall's positives "
              "also take the extractor's conflicting usages and the concept's other-version gold (behaviour concepts excluded).", ""]
    rows = []
    for model, m in summary["models"].items():
        run = m["runs"].get("test-knows")
        if not run:
            continue
        for method in ("va_rag", "va_rag_portable_first", "va_rag_no_ask"):
            g = (run["methods"].get(method) or {}).get("guard") or {}
            if not g:
                continue
            old, new = g.get("exclusive_error") or {}, g.get("strict_named") or {}
            rows.append([model, method, str(g.get("flagged")),
                         f"{pct(g.get('precision'))} ({old.get('tp', 0)}/{old.get('tp', 0) + old.get('fp', 0)})",
                         f"{pct(g.get('recall'))} ({old.get('tp', 0)}/{old.get('tp', 0) + old.get('fn', 0)})",
                         f"{pct(new.get('precision'))} ({new.get('tp', 0)}/{new.get('flagged', 0)})",
                         f"{pct(new.get('recall'))} ({new.get('caught', 0)}/{new.get('positives', 0)})"])
    lines += [table(["Model", "Method", "flags", "precision, exclusive-error", "recall, exclusive-error", "precision, strict-named", "recall, strict-named"], rows), ""]
    pooled: dict[str, dict] = {}
    for m in summary["models"].values():
        g = ((m["runs"].get("test-knows") or {}).get("methods", {}).get("va_rag") or {}).get("guard") or {}
        for change, c in ((g.get("strict_named") or {}).get("by_change_type") or {}).items():
            acc = pooled.setdefault(change, {"flagged": 0, "tp": 0, "positives": 0, "caught": 0})
            for k in acc:
                acc[k] += c.get(k, 0)
    if pooled:
        lines += ["Strict-named oracle by change type, va_rag, the three models pooled:", "",
                  table(["change type", "flags", "precision", "positives", "recall"],
                        [[k, str(c["flagged"]), f"{pct(c['tp'] / c['flagged']) if c['flagged'] else 'n/a'} ({c['tp']}/{c['flagged']})", str(c["positives"]),
                          f"{pct(c['caught'] / c['positives']) if c['positives'] else 'n/a'} ({c['caught']}/{c['positives']})"] for k, c in sorted(pooled.items())]), ""]
    audit = summary.get("audit") or {}
    if audit.get("labelled"):
        lines += [f"Hand labels of the blend detector (`audit_sample.jsonl`, {audit['labelled']} of {audit['records']} labelled"
                  + ("" if audit.get("complete") else ", incomplete") + "): precision on the flagged stratum "
                  + (f"{pct(audit['precision'])} [{pct(audit['precision_wilson'][0])}, {pct(audit['precision_wilson'][1])}] (n={audit.get('precision_n')})"
                     if audit.get("precision") is not None else "n/a")
                  + "; stratum-weighted recall " + (f"{pct(audit['recall'])} (about {audit.get('estimated_positives')} mixing answers estimated in the population)"
                                                    if audit.get("recall") is not None else "n/a")
                  + ". The labels judge whether the code mixes versions (the detector's question); the execution oracles above judge whether a "
                  "flagged usage made the answer fail.", ""]
    else:
        lines += ["Hand labels of the blend detector: `audit_sample.jsonl` is not labelled yet. Fill `label.mixes_versions` (yes/no) and run "
                  "`uv run varag summary` to add the detector's precision (flagged stratum) and stratum-weighted recall here.", ""]

    lines += ["## What size of difference the test split can show", "",
              "Miller's formula at 80% power, two-sided 5%, with the within-concept correlation measured on each run (one-way ICC of instance "
              "scores, mean over methods) and the observed discordance against va_rag (mean squared difference of paired instance scores).", ""]
    rows = []
    for model, m in summary["models"].items():
        for arm in ("knows", "unsure"):
            de = (m["runs"].get(f"test-{arm}") or {}).get("detectable_effect") or {}
            if not de:
                continue
            measured = {round(r["discordant"], 3): r["points"] for r in de["rows"] if r.get("measured_rho")}
            observed = next((r for r in de["rows"] if r.get("observed")), None)
            rows.append([model, arm, str(de["n_instances"]), str(de["concepts"]), str(de.get("repeats", 1)), f"{de['rho_estimated']:.3f}" if de.get("rho_estimated") is not None else "n/a",
                         *[f"{measured[d]:.1f}" if d in measured else "n/a" for d in (0.1, 0.2, 0.3)],
                         f"{observed['discordant']:.3f} -> {observed['points']:.1f}" if observed else "n/a"])
    lines += [table(["Model", "Arm", "instances", "concepts", "repeats", "measured rho", "points at d=0.1", "d=0.2", "d=0.3", "observed d -> points"], rows), ""]

    lines += ["## Slices (test, knows arm, strict)", "", "Intended-version pass in percent (instances in brackets).", ""]
    for key, label in SLICE_KEYS:
        lines += [f"### By {label}", ""]
        for model, m in summary["models"].items():
            run = m["runs"].get("test-knows")
            if not run:
                continue
            values = sorted({v for method in run["slices"].values() for v in method.get(key, {})})
            methods = list(run["slices"])
            rows = [[v] + [f"{pct(run['slices'][meth][key][v]['strict'])} ({run['slices'][meth][key][v]['n']})" if v in run["slices"][meth][key] else "n/a"
                           for meth in methods] for v in values]
            lines += [f"**{model}**", "", table([label] + methods, rows), ""]
    lines += ["### By user arm (test, strict)", ""]
    rows = []
    for model, m in summary["models"].items():
        for method in SLICE_METHODS:
            k, u = (m["runs"].get("test-knows") or {}).get("methods", {}).get(method), (m["runs"].get("test-unsure") or {}).get("methods", {}).get(method)
            if k or u:
                rows.append([model, method, cell(k["strict"]) if k else "n/a", cell(u["strict"]) if u else "n/a"])
    lines += [table(["Model", "Method", "knows", "unsure"], rows), ""]

    lines += ["## Within-session repeat disagreement", "",
              "Among (instance, method) pairs answered under two or more repeat indices in the same session: the share whose response text, "
              "outcome, or intended-version pass differs across repeats.", ""]
    rows = []
    for model, m in summary["models"].items():
        for name, rd in m["repeat_disagreement"].items():
            rows.append([model, name, str(rd["pairs"]), str(rd.get("repeats")), pct(rd["text_differs"]), pct(rd["outcome_differs"]), pct(rd["pass_differs"])])
    lines += [table(["Model", "Run", "pairs", "repeats", "text differs %", "outcome differs %", "pass differs %"], rows), ""]

    lines += ["## Runs and cost", ""]
    rows = []
    for model, m in summary["models"].items():
        for name, run in m["runs"].items():
            rows.append([model, name, f"`{run['run_id']}`", str(run["instances"]), str(run["repeats"]), f"${run['cost_usd'] or 0:.4f}", f"{(run['wall_seconds'] or 0) / 60:.0f} min",
                         run["stopped"] or ""])
        noise = m.get("noise_run")
        if noise:
            rows.append([model, "dev-noise-repeat", f"`{noise['run_id']}`", "20", str(noise["repeats"]), f"${noise['cost_usd'] or 0:.4f}",
                         f"{(noise['wall_seconds'] or 0) / 60:.0f} min", ""])
    lines += [table(["Model", "Run", "Run id", "instances", "repeats", "cost", "run time", "stopped"], rows), "",
              "The guard audit sample (50 outputs over the three models' test runs, knows arm, stratified by the detector's verdict) is in "
              "`audit_sample.md` and `audit_sample.jsonl` beside this file. Per-model reports: " + ", ".join(f"`{m}.md`" for m in summary["models"]) + ".", ""]
    return "\n".join(lines)


def render_model(model: str, record: dict, summary: dict, by_name: dict[str, Loaded]) -> str:
    from varag.eval.report import render

    m = summary["models"][model]
    lines = [f"# VA-RAG final sweep: {model} ({record['stamp']})", "", f"Session `{m['session']}`; cost ${m['cost_usd']:.4f}; "
             f"run time {m['wall_seconds'] / 3600:.1f} h. Each section below is one run's full report.", ""]
    for name, run in by_name.items():
        text = render(run.metrics, run.meta)
        lines += [f"# {name}", ""] + ["#" + line if line.startswith("#") else line for line in text.splitlines()] + [""]
    return "\n".join(lines)


def write_final(record: dict, log: Callable[[str], None] = print) -> Path:
    from varag.eval.audit import audit_sample

    from varag.eval.audit import score_labels

    out_dir = results_dir(record["stamp"])
    out_dir.mkdir(parents=True, exist_ok=True)
    runs = load_sweep(record)
    # The audit sample is drawn once; a later summary keeps it (and the hand labels in it).
    test_runs = [run.dir for by_name in runs.values() for name, run in by_name.items() if name == "test-knows"]
    if test_runs and not (out_dir / "audit_sample.jsonl").exists():
        audit_sample(test_runs, n=50, seed=1234, out_dir=out_dir, stratify=True)
    summary = compute_summary(record, runs)
    if (out_dir / "audit_sample.jsonl").exists():
        summary["audit"] = score_labels(out_dir / "audit_sample.jsonl")
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8", newline="\n")
    for model, by_name in runs.items():
        (out_dir / f"{model}.md").write_text(render_model(model, record, summary, by_name), encoding="utf-8", newline="\n")
    path = out_dir / "summary.md"
    path.write_text(render_summary(record, summary), encoding="utf-8", newline="\n")
    log(f"combined summary: {path}")
    return path
