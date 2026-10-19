"""``varag gpu-day``: the GPU session's runs in one command (docs/GPU_HANDOFF.md).

Order, per model (one model on the GPU at a time): start the server unless one already answers;
``serve check`` (stop on any problem: the numbers would not be ours); the serving-noise check (the
committed 20-instance dev subset, twice, each with a run-private cache); one run of every method
per user arm on the requested split, each followed by its report; stop the server if it was
started here. Then the 50-output audit sample from the primary model's ``knows`` run, and a
summary in ``runs/gpu-day-<stamp>.json``.

Before anything starts it prints the plan and a runtime estimate from the newest finished run of
each model (seconds per instance and method), or from ``configs/models.yaml``
(``seconds_per_answer``) when there is none. Resumption: ``--resume`` skips a (model, arm) whose
newest run has the same split, methods, git commit, config hash and task manifest; anything
interrupted is redone, and its generations come back from the response cache, so an interruption
loses only execution time. Results are flushed after each method.

The test split is refused while the decision-rule thresholds are not frozen (``varag run``) and
while its concepts are not validated (the task manifest).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from varag.config import config_hash, load_models, project_root, sha256_file

DEFAULT_MODELS = ("primary", "vllm_large")
ARMS = ("knows", "unsure")
NOISE_SUBSET = "configs/noise_subset_dev.txt"


def noise_ids() -> list[str]:
    text = (project_root() / NOISE_SUBSET).read_text(encoding="utf-8")
    return [line.strip() for line in text.splitlines() if line.strip() and not line.startswith("#")]


def _finished_runs(model: str) -> list[tuple[Path, dict]]:
    from varag.eval.run import runs_dir

    out = []
    for run_json in sorted(runs_dir().glob(f"*-{model}-*/run.json")):
        try:
            out.append((run_json.parent, json.loads(run_json.read_text(encoding="utf-8"))))
        except json.JSONDecodeError:
            continue
    return out


def seconds_per_answer(model: str) -> tuple[float, str]:
    """Measured wall seconds per (instance, method) from the newest full run of ``model``."""
    for run_dir, meta in reversed(_finished_runs(model)):
        timings = meta.get("timings") or {}
        total = sum(t["seconds"] for t in timings.values())
        answers = sum(t["instances"] for t in timings.values())
        serving = meta.get("serving") or {}
        mostly_cached = serving.get("cache_hits", 0) > serving.get("calls", 0)    # replayed runs understate the time
        if answers >= 50 and not meta.get("instance_ids") and not mostly_cached:
            return total / answers, f"measured in {run_dir.name}"
    return float(load_models()["backends"][model].get("seconds_per_answer", 2.0)), "configs/models.yaml"


def plan(split: str, models: list[str], arms: list[str], methods: str) -> dict:
    from varag.bench.instances import build_instances
    from varag.bench.schema import load_concepts
    from varag.eval.run import library_versions
    from varag.methods.registry import get_methods

    concepts = load_concepts(split=None if split == "all" else split)
    instances = len(build_instances(concepts, library_versions())) if concepts else 0
    n_methods = len(get_methods(methods))
    rows = []
    for model in models:
        per, source = seconds_per_answer(model)
        answers = instances * n_methods * len(arms) + 2 * len(noise_ids())
        rows.append({"model": model, "answers": answers, "seconds_per_answer": round(per, 2), "estimate_min": round(answers * per / 60, 1),
                     "source": source})
    return {"split": split, "concepts": len(concepts), "instances": instances, "methods": n_methods, "arms": arms, "models": rows,
            "total_min": round(sum(r["estimate_min"] for r in rows), 1)}


def format_plan(p: dict) -> str:
    lines = [f"gpu-day: split {p['split']}, {p['concepts']} concepts, {p['instances']} instances, {p['methods']} methods, arms {', '.join(p['arms'])}"]
    for r in p["models"]:
        lines.append(f"  {r['model']:12} {r['answers']:5} answers x {r['seconds_per_answer']} s = about {r['estimate_min']} min ({r['source']}),"
                     " plus server start (1 to 5 min)")
    lines.append(f"  total about {p['total_min']} min of runs")
    return "\n".join(lines)


def refusals(split: str) -> list[str]:
    """Reasons not to start: unfrozen thresholds for a test run, no concepts, or concepts that are
    not validated or changed since validation. Checked before any server is started."""
    from varag.bench.schema import load_concepts
    from varag.bench.validate import manifest_entries_for
    from varag.pipeline.thresholds import frozen

    problems = []
    if split in ("test", "all") and frozen() is None:
        problems.append("decision-rule thresholds are not frozen (configs/experiment.yaml thresholds.frozen_on)")
    concepts = load_concepts(split=None if split == "all" else split)
    if not concepts:
        problems.append(f"no concepts in split {split!r}: author and validate them first")
    else:
        try:
            manifest_entries_for(concepts)
        except RuntimeError as exc:
            problems.append(str(exc))
    return problems


def _same_setup(meta: dict, split: str, methods: list[str], arm: str) -> bool:
    from varag.bench.schema import manifest_path
    from varag.eval.run import git_commit

    return (meta.get("split") == split and meta.get("methods") == methods and meta.get("user_arm") == arm and not meta.get("instance_ids")
            and meta.get("git_commit") == git_commit() and meta.get("config_hash") == config_hash()
            and meta.get("task_manifest_sha256") == sha256_file(manifest_path()))


def gpu_day(split: str = "test", models: list[str] | None = None, arms: list[str] | None = None, methods: str = "all",
            resume: bool = False, dry_run: bool = False, log: Callable[[str], None] = print) -> dict:
    from varag.eval.audit import audit_sample
    from varag.eval.compare import format_noise, noise
    from varag.eval.report import write_report
    from varag.eval.run import run, runs_dir
    from varag.eval.serve import format_report, serve_check
    from varag.methods.registry import get_methods
    from varag.preflight import format_checks, preflight
    from varag.serving import reachable, start, stop

    models = list(models or DEFAULT_MODELS)
    arms = list(arms or ARMS)
    method_ids = [m.id for m in get_methods(methods)]
    p = plan(split, models, arms, methods)
    log(format_plan(p))
    record: dict = {"split": split, "plan": p, "started_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "models": {}, "ok": True}
    refused = refusals(split)
    for problem in refused:
        log(f"REFUSED: {problem}")
    if refused:
        record.update(ok=False, error="; ".join(refused))
        return record
    if dry_run:
        return record
    checks = preflight()
    log(format_checks(checks))
    if any(c.status == "fail" for c in checks):
        record["ok"] = False
        record["error"] = "preflight failed"
        return record

    for model in models:
        entry: dict = {"runs": {}}
        record["models"][model] = entry
        started_here = False
        try:
            if not reachable(model):
                entry["serve"] = start(model, log=log)
                started_here = True
            report = serve_check(model)
            log(format_report(report))
            entry["serve_check"] = {k: v for k, v in report.items() if k != "rendered_prompt"}
            if report["problems"]:
                raise RuntimeError(f"serve check failed for {model}: {report['problems']}")
            ids_file = project_root() / NOISE_SUBSET
            first = run("plain_rag,va_rag", model, "dev", "knows", log=lambda _: None, instance_ids=noise_ids(), fresh_cache=True)
            second = run("plain_rag,va_rag", model, "dev", "knows", log=lambda _: None, instance_ids=noise_ids(), fresh_cache=True)
            entry["noise"] = {"runs": [first.name, second.name], **noise(first, second), "subset": str(ids_file.relative_to(project_root()))}
            log(f"[{model}] " + format_noise(entry["noise"]))
            for arm in arms:
                done = next((d for d, meta in reversed(_finished_runs(model)) if resume and _same_setup(meta, split, method_ids, arm)), None)
                if done is not None:
                    log(f"[{model}] {arm}: resumed from {done.name}")
                    entry["runs"][arm] = done.name
                    continue
                run_dir = run(methods, model, split, arm, log=log)
                write_report(run_dir)
                entry["runs"][arm] = run_dir.name
                log(f"[{model}] {arm}: {run_dir.name}")
        except Exception as exc:  # noqa: BLE001
            entry["error"] = f"{type(exc).__name__}: {exc}"[:600]
            record["ok"] = False
            log(f"[{model}] FAILED: {entry['error']}")
        finally:
            if started_here:
                stop(model, log=log)
    primary = record["models"].get(models[0], {}).get("runs", {}).get("knows")
    if primary:
        path = audit_sample(runs_dir() / primary, 50, 1234)
        record["audit_sample"] = str(path.relative_to(project_root()))
        log(f"audit sample: {path}")
    record["finished_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    out = runs_dir() / f"gpu-day-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8", newline="\n")
    log(f"gpu-day {'done' if record['ok'] else 'FAILED'}; summary in {out}")
    return record
