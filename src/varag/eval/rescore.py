"""``varag rescore``: re-derive stored outcomes under the current outcome rules, without running
anything (no model call, no execution).

The one rule it applies so far (2026-10-21, a metric correction made after the final sweep):
"test failed, then pytest crashed while reporting it" (exit code 3 with a failed test in the
summary) is a failure (`error`), not `infra_error` (``varag.eval.execute.reclassify``). Each
changed row keeps ``outcome_before_rescore`` and its execution record ``reclassified``; run.json
gets a ``rescored`` entry, and results, summary, metrics and report are rewritten.
"""

from __future__ import annotations

import gzip
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

RULE = "crashed_after_failure: exit code 3 after a failed test is a failure, not infra_error (2026-10-21)"


def rescore_run(run_dir: Path) -> dict:
    from varag.bench.schema import load_concepts
    from varag.eval.metrics import load_run
    from varag.eval.report import write_report
    from varag.eval.run import rescore_row, summarize

    run_json, rows, _ = load_run(run_dir)
    concepts = {c.id: c for c in load_concepts()}
    changes = []
    for row in rows:
        before = row["outcome"]
        sides = rescore_row(row, concepts[row["concept_id"]])
        if sides:
            changes.append({"instance_id": row["instance_id"], "method": row["method"], "repeat": row.get("repeat", 0), "sides": sides,
                            "from": before, "to": row["outcome"], "intended_pass": row["intended_pass"]})
    if changes:
        text = "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows)
        if (run_dir / "results.jsonl").exists():
            (run_dir / "results.jsonl").write_text(text, encoding="utf-8", newline="\n")
        with gzip.open(run_dir / "results.jsonl.gz", "wt", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        run_json["summary"] = summarize(rows)
        run_json.setdefault("rescored", []).append({"at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "rule": RULE,
                                                    "changed_rows": len(changes),
                                                    "outcomes": {f"{a} -> {b}": n for (a, b), n in Counter((c["from"], c["to"]) for c in changes).items()},
                                                    "rows": changes})
        (run_dir / "run.json").write_text(json.dumps(run_json, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(run_dir)
    return {"run_id": run_json.get("run_id"), "changed_rows": len(changes), "changes": changes}


def rescore_runs(run_dirs: list[Path], log=print) -> list[dict]:
    out = []
    for run_dir in run_dirs:
        result = rescore_run(run_dir)
        log(f"{result['run_id']}: {result['changed_rows']} rows rescored"
            + (": " + ", ".join(f"{c['instance_id']} {c['method']} r{c['repeat']} {c['from']} -> {c['to']}" for c in result["changes"]) if result["changes"] else ""))
        out.append(result)
    return out

