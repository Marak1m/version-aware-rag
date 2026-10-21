"""``varag audit sample``: export outputs with the detector's verdict for hand labelling (handoff,
"Detector audit"): precision and recall of the blend detector on natural model output.

The population is every targeted answer with code, one repeat per (instance, method): the lowest
repeat index. Several runs can be pooled (the final sweep pools the three models' test runs).
``stratify`` draws half the sample from answers the detector flags (``blend_static`` or a guard
flag) and half from the rest, because blending is rare and a uniform draw of 50 holds almost no
positives. Each record carries its stratum and weight (stratum population over stratum sample),
so recall is estimated with the weights and precision read directly from the flagged stratum.
Within a stratum the draw rotates over (model, method) so every method appears.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from varag.eval.metrics import first_repeat, load_run, trace_of


def _guard(trace: dict | None, target: str | None) -> dict:
    answers = ((trace or {}).get("method_trace") or {}).get("answers") or []
    return next((a.get("guard") for a in answers if a.get("side") in (target, None)), (answers[0].get("guard") if answers else None)) or {}


def _draw(pool: list[dict], k: int, rng: random.Random) -> list[dict]:
    by_cell: dict[tuple[str, str], list[dict]] = {}
    for r in pool:
        by_cell.setdefault((r["model"], r["method"]), []).append(r)
    picked: list[dict] = []
    while len(picked) < min(k, len(pool)):
        for cell in sorted(by_cell):
            if by_cell[cell] and len(picked) < k:
                picked.append(by_cell[cell].pop(rng.randrange(len(by_cell[cell]))))
    return picked


def audit_sample(run_dirs: Path | list[Path], n: int = 50, seed: int = 1234, out_dir: Path | None = None,
                 stratify: bool = False) -> Path:
    run_dirs = [run_dirs] if isinstance(run_dirs, Path) else list(run_dirs)
    population: list[dict] = []
    run_ids = []
    for run_dir in run_dirs:
        run_json, rows, traces = load_run(run_dir)
        run_ids.append(run_json.get("run_id"))
        for r in first_repeat([r for r in rows if r.get("target") and r.get("code")]):
            guard = _guard(trace_of(traces, r["method"], r), r["target"])
            population.append({**r, "model": r.get("model") or run_json.get("model"), "run_id": run_json.get("run_id"), "_guard": guard,
                               "_flagged": bool(r.get("blend_static")) or bool(guard.get("flagged"))})
    rng = random.Random(seed)
    if stratify:
        strata = {"detector_flagged": [r for r in population if r["_flagged"]], "detector_clean": [r for r in population if not r["_flagged"]]}
        first = min(n // 2, len(strata["detector_flagged"]))
        sizes = {"detector_flagged": first, "detector_clean": n - first}
    else:
        strata = {"all": population}
        sizes = {"all": n}
    out = []
    for name, pool in strata.items():
        picked = _draw(list(pool), sizes[name], rng)
        weight = len(pool) / len(picked) if picked else None
        for r in picked:
            guard = r["_guard"]
            out.append({
                "run_id": r["run_id"], "model": r["model"], "instance_id": r["instance_id"], "method": r["method"], "repeat": r.get("repeat", 0),
                "library": r["library"], "target": r["target"], "code": r["code"],
                "stratum": name, "stratum_population": len(pool), "stratum_sample": len(picked), "weight": weight,
                "detector": {"flagged": r["_flagged"], "blend_static": r.get("blend_static"), "blend_exec": r.get("blend_exec"),
                             "guard_flagged": guard.get("flagged"), "guard_violations": guard.get("violations", [])},
                "execution": {side: {"status": e.get("status"), "last_line": e.get("last_line")} for side, e in (r.get("exec") or {}).items() if isinstance(e, dict)},
                "outcome": r["outcome"],
                "label": {"mixes_versions": None, "notes": ""},
            })
    target_dir = out_dir or run_dirs[0]
    target_dir.mkdir(parents=True, exist_ok=True)
    jsonl = target_dir / "audit_sample.jsonl"
    jsonl.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in out) + "\n", encoding="utf-8", newline="\n")
    strata_line = "; ".join(f"{name}: {sum(1 for x in out if x['stratum'] == name)} of {len(pool)}" for name, pool in strata.items())
    md = [f"# Audit sample: {len(out)} outputs from {', '.join(str(i) for i in run_ids)}", "",
          "For each output, record whether the code mixes APIs of the two versions (`mixes_versions`: yes/no) in audit_sample.jsonl. "
          "The detector's verdict is shown so precision and recall can be computed afterwards"
          + (": precision from the flagged stratum, recall with each record's `weight` (stratum population over stratum sample)." if stratify else "."), "",
          f"Population: targeted answers with code, repeat 0, {len(population)} in all. Strata: {strata_line}.", ""]
    for i, x in enumerate(out, 1):
        md += [f"## {i}. {x['model']} / {x['method']} on {x['instance_id']}", "",
               f"Stratum {x['stratum']}; detector: blend_static={x['detector']['blend_static']}, guard_flagged={x['detector']['guard_flagged']}"
               + (f" ({', '.join(v['symbol'] for v in x['detector']['guard_violations'])})" if x["detector"]["guard_violations"] else "")
               + f"; outcome={x['outcome']}", "",
               "```python", x["code"].rstrip(), "```", ""]
    (target_dir / "audit_sample.md").write_text("\n".join(md), encoding="utf-8", newline="\n")
    return jsonl
