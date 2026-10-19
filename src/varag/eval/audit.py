"""``varag audit sample``: export outputs with the detector's verdict for hand labelling (handoff,
"Detector audit"): precision and recall of the blend detector on natural model output."""

from __future__ import annotations

import json
import random
from pathlib import Path

from varag.eval.metrics import load_run


def audit_sample(run_dir: Path, n: int = 50, seed: int = 1234) -> Path:
    run_json, rows, traces = load_run(run_dir)
    candidates = [r for r in rows if r.get("target") and r.get("code")]
    rng = random.Random(seed)
    by_method: dict[str, list[dict]] = {}
    for r in candidates:
        by_method.setdefault(r["method"], []).append(r)
    picked: list[dict] = []
    while len(picked) < min(n, len(candidates)):
        for method in sorted(by_method):
            pool = by_method[method]
            if pool and len(picked) < n:
                picked.append(pool.pop(rng.randrange(len(pool))))
    out = []
    for r in picked:
        t = traces.get((r["method"], r["instance_id"]), {})
        answers = (t.get("method_trace") or {}).get("answers") or []
        guard = (answers[0].get("guard") if answers else None) or {}
        out.append({
            "instance_id": r["instance_id"], "method": r["method"], "library": r["library"], "target": r["target"],
            "code": r["code"],
            "detector": {"blend_static": r.get("blend_static"), "blend_exec": r.get("blend_exec"),
                         "guard_flagged": guard.get("flagged"), "guard_violations": guard.get("violations", [])},
            "execution": {side: {"status": e.get("status"), "last_line": e.get("last_line")} for side, e in (r.get("exec") or {}).items() if isinstance(e, dict)},
            "outcome": r["outcome"],
            "label": {"mixes_versions": None, "notes": ""},
        })
    jsonl = run_dir / "audit_sample.jsonl"
    jsonl.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in out) + "\n", encoding="utf-8", newline="\n")
    md = [f"# Audit sample: {run_json.get('run_id')} ({len(out)} outputs)", "",
          "For each output, record whether the code mixes APIs of the two versions (`mixes_versions`: yes/no) in audit_sample.jsonl. "
          "The detector's verdict is shown so precision and recall can be computed afterwards.", ""]
    for i, x in enumerate(out, 1):
        md += [f"## {i}. {x['method']} on {x['instance_id']}", "",
               f"Detector: blend_static={x['detector']['blend_static']}, guard_flagged={x['detector']['guard_flagged']}, outcome={x['outcome']}", "",
               "```python", x["code"].rstrip(), "```", ""]
    (run_dir / "audit_sample.md").write_text("\n".join(md), encoding="utf-8", newline="\n")
    return jsonl
