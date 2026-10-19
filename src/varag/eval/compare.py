"""Run-to-run comparisons for the GPU session's checks (handoff, "Serving configuration" and L7).

- ``noise``: the same instances and methods run twice with a fresh cache each time; the share of
  (instance, method) pairs whose response text changed, and whose outcome changed. Differences of
  that size between methods are treated as noise.
- ``l1``: ``plain_rag`` under our pinned sampling against the model's own generation config; pass
  rates, outcome shifts and how many responses differ (handoff L1, recorded in docs/DECISIONS.md).
- ``leak``: the leak-audit arm (every question replaced by an irrelevant one) against the
  ``unsure`` arm, whose reply carries no version either. Per method that can ask, the leak-arm pass
  rate must not exceed the uninformative-reply rate by more than the measured serving noise.
  ``va_rag_no_ask`` is printed beside them as the policy's no-question reference.

Every comparison pairs rows by (method, instance_id) and reads only results.jsonl and run.json.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from varag.eval.metrics import load_run
from varag.eval.outcomes import intended_pass

ASKING_METHODS = ("no_retrieval", "plain_rag", "mind_version", "oracle_docs", "always_ask", "va_rag", "va_rag_no_infer", "va_rag_no_guard")


def _rows(run_dir: Path) -> tuple[dict, dict[tuple[str, str], dict]]:
    run_json, rows, _ = load_run(run_dir)
    return run_json, {(r["method"], r["instance_id"]): r for r in rows}


def _passed(row: dict) -> bool:
    return intended_pass(row["outcome"]) if row.get("target") else row["outcome"] == "pass_both"


def _rate(rows: list[dict]) -> float | None:
    return sum(_passed(r) for r in rows) / len(rows) if rows else None


def noise(run_a: Path, run_b: Path) -> dict:
    _, a = _rows(run_a)
    _, b = _rows(run_b)
    keys = sorted(set(a) & set(b))
    text_changed = [k for k in keys if a[k].get("response_text") != b[k].get("response_text")]
    outcome_changed = [k for k in keys if a[k]["outcome"] != b[k]["outcome"]]
    return {"pairs": len(keys), "text_changed": len(text_changed), "outcome_changed": len(outcome_changed),
            "text_changed_share": len(text_changed) / len(keys) if keys else None,
            "outcome_changed_share": len(outcome_changed) / len(keys) if keys else None,
            "changed": [f"{m} {i}" for m, i in text_changed][:20]}


def l1(run_pinned: Path, run_genconfig: Path, method: str = "plain_rag") -> dict:
    meta_a, a = _rows(run_pinned)
    meta_b, b = _rows(run_genconfig)
    keys = sorted(k for k in set(a) & set(b) if k[0] == method)
    rows_a, rows_b = [a[k] for k in keys], [b[k] for k in keys]
    flips = Counter((_passed(a[k]), _passed(b[k])) for k in keys)
    return {"method": method, "instances": len(keys),
            "pinned": {"model": meta_a["model"], "pass_rate": _rate(rows_a), "outcomes": dict(Counter(r["outcome"] for r in rows_a)),
                       "questions": sum(1 for r in rows_a if r.get("question"))},
            "genconfig": {"model": meta_b["model"], "pass_rate": _rate(rows_b), "outcomes": dict(Counter(r["outcome"] for r in rows_b)),
                          "questions": sum(1 for r in rows_b if r.get("question"))},
            "responses_differ": sum(1 for k in keys if a[k].get("response_text") != b[k].get("response_text")),
            "pass_to_fail": flips[(True, False)], "fail_to_pass": flips[(False, True)]}


def leak(run_leak: Path, run_unsure: Path, tolerance: float = 0.0, run_noask: Path | None = None) -> dict:
    meta_l, l_rows = _rows(run_leak)
    meta_u, u_rows = _rows(run_unsure)
    if meta_l.get("user_arm") != "leak_audit":
        raise ValueError(f"{run_leak.name} is not a leak_audit run (user_arm {meta_l.get('user_arm')})")
    noask = _rows(run_noask)[1] if run_noask else {}
    out = {"tolerance": tolerance, "methods": {}, "passed": True}
    for method in sorted({m for m, _ in l_rows} & set(ASKING_METHODS)):
        keys = sorted(k for k in set(l_rows) & set(u_rows) if k[0] == method)
        if not keys:
            continue
        leak_rate, unsure_rate = _rate([l_rows[k] for k in keys]), _rate([u_rows[k] for k in keys])
        asked = sum(1 for k in keys if l_rows[k].get("question"))
        noask_keys = [("va_rag_no_ask", i) for _, i in keys if ("va_rag_no_ask", i) in noask]
        entry = {"instances": len(keys), "questions_in_leak_arm": asked, "leak_pass_rate": leak_rate,
                 "unsure_pass_rate": unsure_rate, "excess": (leak_rate - unsure_rate) if None not in (leak_rate, unsure_rate) else None,
                 "no_ask_pass_rate": _rate([noask[k] for k in noask_keys]) if noask_keys else None}
        entry["ok"] = entry["excess"] is None or entry["excess"] <= tolerance + 1e-9
        out["passed"] &= entry["ok"]
        out["methods"][method] = entry
    return out


def _pct(x: float | None) -> str:
    return "n/a" if x is None else f"{x:.1%}"


def format_noise(r: dict) -> str:
    return (f"serving noise: {r['text_changed']}/{r['pairs']} responses changed ({_pct(r['text_changed_share'])}), "
            f"{r['outcome_changed']}/{r['pairs']} outcomes changed ({_pct(r['outcome_changed_share'])})"
            + ("".join(f"\n  changed: {c}" for c in r["changed"]) if r["changed"] else ""))


def format_l1(r: dict) -> str:
    p, g = r["pinned"], r["genconfig"]
    return (f"L1 ({r['method']}, {r['instances']} instances): pinned {_pct(p['pass_rate'])} vs model generation config {_pct(g['pass_rate'])} "
            f"(difference {_pct((g['pass_rate'] or 0) - (p['pass_rate'] or 0))}); responses differ on {r['responses_differ']}; "
            f"pass->fail {r['pass_to_fail']}, fail->pass {r['fail_to_pass']}\n"
            f"  pinned outcomes {p['outcomes']}, questions {p['questions']}\n  genconfig outcomes {g['outcomes']}, questions {g['questions']}")


def format_leak(r: dict) -> str:
    lines = [f"leak audit (tolerance {_pct(r['tolerance'])}): {'PASS' if r['passed'] else 'FAIL'}",
             f"  {'method':18} {'n':>3} {'asked':>5} {'leak arm':>9} {'unsure':>8} {'excess':>8} {'no_ask':>8}"]
    for method, e in r["methods"].items():
        lines.append(f"  {method:18} {e['instances']:3} {e['questions_in_leak_arm']:5} {_pct(e['leak_pass_rate']):>9} {_pct(e['unsure_pass_rate']):>8} "
                     f"{_pct(e['excess']):>8} {_pct(e['no_ask_pass_rate']):>8}" + ("" if e["ok"] else "  EXCEEDS"))
    return "\n".join(lines)
