"""``varag run``: generate with a method and backend, execute every answer in both
environments, classify, and write runs/{run_id}/results.jsonl and run.json.

Check 7 of the verification table: a run refuses unvalidated or changed concepts and
records the task-manifest hash, git commit, config hash and environment manifest.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from varag.bench.instances import Instance, build_instances
from varag.bench.schema import load_concepts, manifest_path
from varag.bench.validate import manifest_entries_for
from varag.config import SIDES, config_hash, env_name, library_names, load_experiment, other_side, project_root, sha256_file
from varag.envs.build import read_manifest
from varag.envs.verify import require_verified
from varag.config import load_models
from varag.eval.execute import ExecResult, execute, isolation_status
from varag.eval.outcomes import classify, classify_control, intended_pass
from varag.llm.client import make_backend
from varag.methods.registry import Method, MethodResult, get_methods


def require_isolation_for(model: str) -> None:
    """Real-model output runs only where the memory limit and network isolation apply
    (WSL2 or a container; docs/DECISIONS.md). Mock backends return reference code and are exempt."""
    if load_models()["backends"][model]["type"] == "mock":
        return
    status = isolation_status()
    missing = [name for name, ok in status.items() if not ok]
    if missing:
        raise SystemExit(
            f"refusing to execute output from {model}: this host cannot apply {', '.join(missing)}. "
            "Run the harness under WSL2 or a container (docs/DECISIONS.md, 2026-10-08)."
        )


def git_commit() -> str | None:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=project_root(), capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() or None


def runs_dir() -> Path:
    return project_root() / "runs"


def library_versions() -> dict[str, dict[str, str]]:
    manifest = read_manifest()
    return {lib: {side: manifest[env_name(lib, side)]["library_version"] for side in SIDES} for lib in library_names()}


def execute_instance(instance: Instance, result: MethodResult, concept, versions: dict) -> dict:
    row: dict = {
        **instance.to_dict(),
        "method": result.method,
        "code_version": "final",
        "response_kind": result.extraction.kind,
        "multi_block": result.extraction.multi_block,
        "answers_returned": result.answers_returned,
        "question": result.question,
        "calls": result.calls,
        "code": result.code,
        "response_text": result.response_text,
        "trace": result.trace,
        "exec": {},
    }
    if result.code is None:
        row["outcome"] = "no_code"
        row["soft_fail"] = False
        row["intended_pass"] = False
        return row
    runs: dict[str, ExecResult] = {
        side: execute(env_name(instance.library, side), result.code, concept.test_path, concept.warnings_as_errors)
        for side in SIDES
    }
    row["exec"] = {side: r.to_dict() for side, r in runs.items()}
    if instance.target:
        outcome = classify(runs[instance.target], runs[other_side(instance.target)])
        row["soft_fail"] = runs[instance.target].soft_fail
    else:
        outcome = classify_control(runs["old"], runs["new"])
        row["soft_fail"] = any(r.soft_fail for r in runs.values())
    row["outcome"] = outcome
    row["intended_pass"] = intended_pass(outcome) if instance.target else outcome == "pass_both"
    return row


def summarize(rows: list[dict]) -> dict[str, dict]:
    summary: dict[str, dict] = {}
    for method in sorted({r["method"] for r in rows}):
        mine = [r for r in rows if r["method"] == method]
        targeted = [r for r in mine if r["target"]]
        controls = [r for r in mine if not r["target"]]
        summary[method] = {
            "targeted": len(targeted),
            "intended_pass_rate": (sum(r["intended_pass"] for r in targeted) / len(targeted)) if targeted else None,
            "outcomes": dict(Counter(r["outcome"] for r in targeted)),
            "soft_fail": sum(1 for r in targeted if r["soft_fail"]),
            "controls": len(controls),
            "control_outcomes": dict(Counter(r["outcome"] for r in controls)),
        }
    return summary


def run(methods_spec: str, model: str, split: str, user_arm: str | None = None, log: Callable[[str], None] = print) -> Path:
    require_verified()
    concepts = load_concepts(split=None if split == "all" else split)
    if not concepts:
        raise RuntimeError(f"no concepts for split {split!r}")
    entries = manifest_entries_for(concepts)
    versions = library_versions()
    instances = build_instances(concepts, versions)
    by_id = {c.id: c for c in concepts}
    methods: list[Method] = get_methods(methods_spec)
    require_isolation_for(model)
    backend = make_backend(model)
    experiment = load_experiment()
    user_arm = user_arm or experiment.get("user_arm", "knows")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    digest = hashlib.sha256(f"{stamp}{model}{methods_spec}{split}".encode()).hexdigest()[:8]
    run_id = f"{stamp}-{model}-{digest}"
    run_dir = runs_dir() / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    with open(run_dir / "results.jsonl", "w", encoding="utf-8", newline="\n") as fh:
        for method in methods:
            log(f"[{method.id}] {len(instances)} instances on {model}")
            for instance in instances:
                result = method.answer(instance, backend, versions)
                row = execute_instance(instance, result, by_id[instance.concept_id], versions)
                row["model"] = model
                row["user_arm"] = user_arm
                rows.append(row)
                fh.write(json.dumps(row, sort_keys=True) + "\n")
                log(f"  {instance.instance_id:40} {row['outcome']}" + ("  soft_fail" if row["soft_fail"] else ""))

    summary = summarize(rows)
    (run_dir / "run.json").write_text(json.dumps({
        "run_id": run_id,
        "model": model,
        "methods": [m.id for m in methods],
        "split": split,
        "user_arm": user_arm,
        "instances": len(instances),
        "task_manifest_sha256": sha256_file(manifest_path()),
        "concepts": entries,
        "git_commit": git_commit(),
        "config_hash": config_hash(),
        "env_manifest": read_manifest(),
        "summary": summary,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    for method, s in summary.items():
        rate = f"{s['intended_pass_rate']:.1%}" if s["intended_pass_rate"] is not None else "n/a"
        log(f"[{method}] intended-version pass {rate} over {s['targeted']} targeted instances; outcomes {s['outcomes']}; controls {s['control_outcomes']}")
    log(f"run written to {run_dir}")
    return run_dir
