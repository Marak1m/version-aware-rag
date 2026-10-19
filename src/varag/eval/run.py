"""``varag run``: generate with a method and backend, execute every answer in both
environments, classify, and write runs/{run_id}/results.jsonl and run.json.

Check 7 of the verification table: a run refuses unvalidated or changed concepts and
records the task-manifest hash, git commit, config hash and environment manifest.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import shutil
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from varag.bench.instances import Instance, build_instances
from varag.bench.schema import class_cap_problems, load_concepts, manifest_path
from varag.bench.validate import manifest_entries_for, recorded_gold_examples, reference_baseline
from varag.config import SIDES, config_hash, env_name, library_names, load_experiment, load_models, other_side, project_root, sha256_file
from varag.envs.build import read_manifest
from varag.envs.verify import require_verified
from varag.eval.execute import ExecResult, execute, isolation_status
from varag.eval.outcomes import classify_control, classify_flags, intended_pass
from varag.inventory.build import load_diff
from varag.pipeline.guard import BlendGuard, blend_static, guarded_both_sides
from varag.pipeline.signals import static_usages
from varag.llm.client import make_backend
from varag.methods.registry import Method, MethodResult, RunContext, get_methods


def retrieval_for(instances: list[Instance], concepts: dict) -> dict[str, "RetrievedSet"]:
    """The v0 retrieved set per instance, method-independent, with the counterbalanced order.
    Targeted instances are balanced per concept; controls are balanced across a library's controls."""
    from varag.corpus.retrieve import order_assignment, retrieve

    groups: dict[str, list[Instance]] = {}
    for inst in instances:
        key = inst.concept_id if inst.target else f"controls:{inst.library}"
        groups.setdefault(key, []).append(inst)
    first: dict[str, bool] = {}
    for key, members in groups.items():
        anchor = concepts[members[0].concept_id]
        if not members[0].target:
            anchor = type(anchor)(**{**anchor.__dict__, "id": key})
        first.update(order_assignment(anchor, [m.instance_id for m in members]))
    return {inst.instance_id: retrieve(inst, concepts[inst.concept_id], first[inst.instance_id]) for inst in instances}


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


EXCLUSIVE_ERRORS = ("AttributeError", "ImportError", "ModuleNotFoundError", "TypeError")


def names_exclusive_symbol(run_: ExecResult, usages) -> bool:
    """The run failed with an error whose last line names one of the code's exclusive usages."""
    if run_.exc_type not in EXCLUSIVE_ERRORS or not run_.last_line:
        return False
    names = {u.symbol.split("(")[0].rsplit(".", 1)[-1] for u in usages.usages} | {u.symbol.split("(")[-1].rstrip(")").split("=")[0] for u in usages.usages if "(" in u.symbol}
    return any(name and name in run_.last_line for name in names)


def execute_code(code: str, instance: Instance, concept, scoring: str) -> dict:
    """Both environments for one piece of code, scored lenient (pass) and strict (pass with no
    solution-attributed soft warning net of the reference). The primary outcome follows ``scoring``."""
    runs = {side: execute(env_name(instance.library, side), code, concept.test_path, warnings_as_errors=False) for side in SIDES}
    baselines = {side: reference_baseline(concept, side) for side in SIDES}
    lenient = {side: runs[side].passed for side in SIDES}
    strict = {side: runs[side].passed and not runs[side].soft_fail_against(baselines[side]) for side in SIDES}
    infra = any(runs[side].status == "infra_error" for side in SIDES)
    out = {"exec": {side: r.to_dict() for side, r in runs.items()},
           "net_soft_warnings": {side: runs[side].net_soft_signatures(baselines[side]) for side in SIDES}}
    if instance.target:
        other = other_side(instance.target)
        out["outcome_lenient"] = classify_flags(lenient[instance.target], lenient[other], infra)
        out["outcome_strict"] = classify_flags(strict[instance.target], strict[other], infra)
        out["soft_fail"] = runs[instance.target].soft_fail_against(baselines[instance.target])
    else:
        out["outcome_lenient"] = classify_control(runs["old"], runs["new"])
        out["outcome_strict"] = out["outcome_lenient"] if not any(runs[s].soft_fail_against(baselines[s]) for s in SIDES) else (
            "pass_one" if sum(strict.values()) == 1 else ("pass_both" if sum(strict.values()) == 2 else "broken"))
        out["soft_fail"] = any(runs[side].soft_fail_against(baselines[side]) for side in SIDES)
    out["outcome"] = out["outcome_strict"] if scoring == "strict" else out["outcome_lenient"]
    out["runs"] = runs
    return out


def execute_instance(instance: Instance, result: MethodResult, concept, versions: dict) -> dict:
    scoring = load_experiment().get("scoring", {}).get("deprecation", {}).get("primary", "strict") if concept.exclusivity == "deprecation" else "lenient"
    row: dict = {
        "scoring": scoring,
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
        row.update(outcome="no_code", outcome_lenient="no_code", outcome_strict="no_code", soft_fail=False, intended_pass=False,
                   blend_static=False, blend_exec=False, guarded_portable=False)
        return row
    scored = execute_code(result.code, instance, concept, scoring)
    runs: dict[str, ExecResult] = scored.pop("runs")
    row.update(scored)
    # Blend metrics (handoff, "How blending is measured") on the final code.
    usages = static_usages(result.code, load_diff(instance.library))
    row["blend_static"] = blend_static(usages) if usages.parsed else False
    row["blend_exec"] = bool(row["blend_static"] and all(runs[s].failed_by_code for s in SIDES) and any(names_exclusive_symbol(runs[s], usages) for s in SIDES))
    row["guarded_portable"] = bool(usages.parsed and guarded_both_sides(usages) and all(runs[s].passed for s in SIDES))
    # The pre-guard code runs too, so the guard's fix and harm rates cost no model call.
    if result.pre_guard_code and result.pre_guard_code != result.code:
        before = execute_code(result.pre_guard_code, instance, concept, scoring)
        before.pop("runs")
        row["pre_guard"] = {"code": result.pre_guard_code, **before}
    # A two-answer response: the other block runs in the other environment, so both_correct is
    # "the old block passes in old and the new block passes in new" (handoff, outcome additions).
    if len(result.labelled) == 2 and instance.target:
        other = other_side(instance.target)
        other_run = execute(env_name(instance.library, other), result.labelled[other], concept.test_path, concept.warnings_as_errors)
        row["both_correct"] = runs[instance.target].passed and other_run.passed
        row["exec"][f"{other}_block"] = other_run.to_dict()
    row["intended_pass"] = intended_pass(row["outcome"]) if instance.target else row["outcome"] == "pass_both"
    return row


def _pass_rate(rows: list[dict]) -> float | None:
    return (sum(r["intended_pass"] for r in rows) / len(rows)) if rows else None


def summarize(rows: list[dict]) -> dict[str, dict]:
    summary: dict[str, dict] = {}
    for method in sorted({r["method"] for r in rows}):
        mine = [r for r in rows if r["method"] == method]
        targeted = [r for r in mine if r["target"]]
        controls = [r for r in mine if not r["target"]]
        slices = {label: [r for r in targeted if r.get("gold_examples") == label] for label in ("both", "neither")}
        classes = {cls: [r for r in targeted if r.get("exclusivity") == cls] for cls in sorted({r.get("exclusivity") for r in targeted} - {None})}
        summary[method] = {
            "targeted": len(targeted),
            "intended_pass_rate": _pass_rate(targeted),
            "intended_pass_rate_lenient": (sum(intended_pass(r.get("outcome_lenient", r["outcome"])) for r in targeted) / len(targeted)) if targeted else None,
            "intended_pass_rate_strict": (sum(intended_pass(r.get("outcome_strict", r["outcome"])) for r in targeted) / len(targeted)) if targeted else None,
            "blend_static": sum(1 for r in targeted if r.get("blend_static")),
            "blend_exec": sum(1 for r in targeted if r.get("blend_exec")),
            "questions": sum(1 for r in mine if r.get("question")),
            "calls": sum(r.get("calls", 0) for r in mine),
            "outcomes": dict(Counter(r["outcome"] for r in targeted)),
            "soft_fail": sum(1 for r in targeted if r["soft_fail"]),
            "controls": len(controls),
            "control_outcomes": dict(Counter(r["outcome"] for r in controls)),
            "control_outcomes_by_kind": {kind: dict(Counter(r["outcome"] for r in controls if r.get("concept_kind") == kind))
                                         for kind in sorted({r.get("concept_kind", "no_conflict") for r in controls})},
            "control_questions_by_kind": {kind: sum(1 for r in controls if r.get("concept_kind") == kind and r.get("question"))
                                          for kind in sorted({r.get("concept_kind", "no_conflict") for r in controls})},
            "by_gold_examples": {label: {"targeted": len(s), "intended_pass_rate": _pass_rate(s)} for label, s in slices.items() if s},
            # one_directional concepts are reported separately (user decision 2026-10-15).
            "by_exclusivity": {cls: {"targeted": len(s), "intended_pass_rate": _pass_rate(s)} for cls, s in classes.items()},
        }
    return summary


def run(methods_spec: str, model: str, split: str, user_arm: str | None = None, log: Callable[[str], None] = print,
        limit: int | None = None) -> Path:
    require_verified()
    cap_problems = class_cap_problems(load_concepts())
    if cap_problems:
        raise RuntimeError("concept class caps exceeded: " + "; ".join(cap_problems))
    concepts = load_concepts(split=None if split == "all" else split)
    if not concepts:
        raise RuntimeError(f"no concepts for split {split!r}")
    entries = manifest_entries_for(concepts)
    versions = library_versions()
    instances = build_instances(concepts, versions)
    if limit:
        instances = instances[:limit]
    by_id = {c.id: c for c in concepts}
    methods: list[Method] = get_methods(methods_spec)
    require_isolation_for(model)
    retrieved = retrieval_for(instances, by_id)
    # Results are sliced by gold_examples as validation recorded it; a corpus that changed since
    # then must be re-validated first.
    gold_examples = {c.id: recorded_gold_examples(c) for c in concepts}
    stale = sorted({i.concept_id for i in instances if retrieved[i.instance_id].gold_examples != gold_examples[i.concept_id]})
    if stale:
        raise RuntimeError(f"gold_examples changed since validation for {', '.join(stale)}; re-run `varag bench validate`")
    backend = make_backend(model)
    experiment = load_experiment()
    user_arm = user_arm or experiment.get("user_arm", "knows")
    ctx = RunContext(user_arm=user_arm, retrieved=retrieved, concepts=by_id, guard=BlendGuard(backend, versions))
    reportable = bool(load_models()["backends"][model].get("report", True))

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    digest = hashlib.sha256(f"{stamp}{model}{methods_spec}{split}".encode()).hexdigest()[:8]
    run_id = f"{stamp}-{model}-{digest}"
    run_dir = runs_dir() / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    with open(run_dir / "results.jsonl", "w", encoding="utf-8", newline="\n") as fh, \
            open(run_dir / "traces.jsonl", "w", encoding="utf-8", newline="\n") as traces:
        for method in methods:
            log(f"[{method.id}] {len(instances)} instances on {model}")
            for instance in instances:
                result = method.answer(instance, backend, versions, ctx)
                row = execute_instance(instance, result, by_id[instance.concept_id], versions)
                row["model"] = model
                row["user_arm"] = user_arm
                row["gold_examples"] = gold_examples[instance.concept_id]
                row["exclusivity"] = by_id[instance.concept_id].exclusivity
                row["change_type"] = by_id[instance.concept_id].change_type
                row["concept_kind"] = by_id[instance.concept_id].kind      # no_conflict and portable_control controls are reported apart
                rows.append(row)
                fh.write(json.dumps(row, sort_keys=True) + "\n")
                traces.write(json.dumps({"instance_id": instance.instance_id, "method": method.id,
                                         "retrieval": retrieved[instance.instance_id].trace(),
                                         "method_trace": result.trace}, sort_keys=True) + "\n")
                log(f"  {instance.instance_id:40} {row['outcome']}" + ("  soft_fail" if row["soft_fail"] else ""))

    with open(run_dir / "results.jsonl", "rb") as src, gzip.open(run_dir / "results.jsonl.gz", "wb") as dst:
        shutil.copyfileobj(src, dst)                      # the committed form of a run's results
    summary = summarize(rows)
    (run_dir / "run.json").write_text(json.dumps({
        "run_id": run_id,
        "model": model,
        "backend": load_models()["backends"][model],   # model id, revision, quantization, serving settings
        "sampling": load_models()["sampling"],
        "methods": [m.id for m in methods],
        "split": split,
        "limit": limit,
        "reportable": reportable,
        "scoring": load_experiment().get("scoring", {}),
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
        for name in ("by_gold_examples", "by_exclusivity"):
            log(f"[{method}] {name.replace('_', ' ')}: " + ", ".join(
                f"{label} {v['intended_pass_rate']:.1%} over {v['targeted']}" for label, v in s[name].items()))
    log(f"run written to {run_dir}")
    return run_dir
