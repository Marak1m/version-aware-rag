"""``varag sweep``: the model runs in one command, on OpenRouter (docs/RUNBOOK.md).

Stage ``dev`` (the default): preflight; an endpoint check per model (stop on any problem); the
smoke (mock anchors, then ten dev instances through every method on each model); every method on
the dev split for each model and user arm, each run followed by its report; the serving-noise
check per model (the committed 20-instance subset, all methods, twice with a run-private cache,
compared with each other and with the model's dev run); then STOP for review. Stage ``test`` runs
the endpoint checks and the test-split runs only; it is refused while the thresholds or the prompts
are not frozen, or while the test concepts are not validated.

Runs are instance-major and carry their session id (provider plus run start time) on every row;
methods are compared only within one session. ``--max-usd`` caps the whole sweep: each run gets
what is left, its estimate is printed before it starts, and the sweep stops once the money is
spent. ``--resume`` skips a (model, arm) whose newest run has the same split, methods, commit,
configs and tasks and was not stopped. Generations are cached, so a rerun after an interruption
pays only for requests that never completed.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from varag.config import config_hash, load_experiment, load_models, project_root, sha256_file

ARMS = ("knows", "unsure")
NOISE_SUBSET = "configs/noise_subset_dev.txt"


def default_models() -> list[str]:
    return [k for k, v in load_models()["backends"].items() if v.get("type") == "openrouter" and v.get("active", True)]


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
    """Measured wall seconds per (instance, method) from the newest uncached full run of ``model``."""
    for run_dir, meta in reversed(_finished_runs(model)):
        serving = meta.get("serving") or {}
        mostly_cached = serving.get("cache_hits", 0) > serving.get("calls", 0)    # replayed runs understate the time
        answers = sum(t["instances"] for t in (meta.get("timings") or {}).values())
        if answers >= 50 and not meta.get("instance_ids") and not mostly_cached and meta.get("wall_seconds"):
            return meta["wall_seconds"] / answers, f"measured in {run_dir.name}"
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
        answers = instances * n_methods * len(arms) + (2 * len(noise_ids()) * n_methods if split == "dev" else 0)
        rows.append({"model": model, "answers": answers, "seconds_per_answer": round(per, 2), "estimate_min": round(answers * per / 60, 1),
                     "source": source})
    return {"split": split, "concepts": len(concepts), "instances": instances, "methods": n_methods, "arms": arms, "models": rows,
            "total_min": round(sum(r["estimate_min"] for r in rows), 1)}


def format_plan(p: dict) -> str:
    lines = [f"sweep: split {p['split']}, {p['concepts']} concepts, {p['instances']} instances, {p['methods']} methods, arms {', '.join(p['arms'])}"]
    for r in p["models"]:
        lines.append(f"  {r['model']:8} {r['answers']:5} answers x {r['seconds_per_answer']} s = about {r['estimate_min']} min ({r['source']})")
    lines.append(f"  total about {p['total_min']} min; the cost estimate is printed before each run")
    return "\n".join(lines)


def refusals(split: str) -> list[str]:
    """Reasons not to start, checked before any paid call."""
    from varag.bench.schema import load_concepts
    from varag.bench.validate import manifest_entries_for
    from varag.pipeline.thresholds import frozen

    problems = []
    if split in ("test", "all"):
        if frozen() is None:
            problems.append("decision-rule thresholds are not frozen (configs/experiment.yaml thresholds.frozen_on)")
        if not (load_experiment().get("prompts") or {}).get("frozen_on"):
            problems.append("the prompts are not frozen (configs/experiment.yaml prompts.frozen_on)")
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
            and not meta.get("limit") and not meta.get("stopped") and meta.get("git_commit") == git_commit()
            and meta.get("config_hash") == config_hash() and meta.get("task_manifest_sha256") == sha256_file(manifest_path()))


def sweep(stage: str = "dev", models: list[str] | None = None, arms: list[str] | None = None, methods: str = "all",
          max_usd: float | None = None, resume: bool = False, dry_run: bool = False, log: Callable[[str], None] = print) -> dict:
    from varag import logbook
    from varag.eval.compare import format_noise, noise
    from varag.eval.report import write_report
    from varag.eval.run import run, runs_dir
    from varag.eval.serve import endpoint_check, format_endpoint_report
    from varag.methods.registry import get_methods
    from varag.preflight import format_checks, preflight

    split = "dev" if stage == "dev" else "test"
    models = list(models or default_models())
    arms = list(arms or ARMS)
    method_ids = [m.id for m in get_methods(methods)]
    p = plan(split, models, arms, methods)
    log(format_plan(p))
    record: dict = {"stage": stage, "split": split, "plan": p, "max_usd": max_usd, "started_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "models": {}, "ok": True, "spent_usd": 0.0}
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
        record.update(ok=False, error="preflight failed")
        return record

    def remaining() -> float | None:
        return None if max_usd is None else max(0.0, max_usd - record["spent_usd"])

    def spend(run_dir: Path) -> None:
        meta = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
        record["spent_usd"] = round(record["spent_usd"] + float(meta.get("cost_usd") or 0), 6)
        if meta.get("stopped"):
            raise RuntimeError(f"{run_dir.name} stopped: {meta['stopped']}")

    for model in models:
        report = endpoint_check(model)
        log(format_endpoint_report(report))
        record["spent_usd"] = round(record["spent_usd"] + float(report.get("cost_usd") or 0), 6)
        record["models"][model] = {"endpoint_check": {k: v for k, v in report.items() if k not in ("response",)}, "runs": {}}
        if report["problems"]:
            record.update(ok=False, error=f"endpoint check failed for {model}")
            return _finish(record, log)
    try:
        if stage == "dev":
            from varag.eval.smoke import smoke

            smoked = smoke(offline=True, log=log)
            record["smoke_offline"] = smoked["ok"]
            if not smoked["ok"]:
                raise RuntimeError("the offline smoke failed")
            for model in models:
                run_dir = run(methods, model, "dev", "knows", log=lambda _: None, limit=10, max_usd=remaining())
                spend(run_dir)
                write_report(run_dir)
                record["models"][model]["smoke_run"] = run_dir.name
                log(f"[{model}] smoke: 10 dev instances through every method: {run_dir.name}")
        for model in models:
            entry = record["models"][model]
            for arm in arms:
                done = next((d for d, meta in reversed(_finished_runs(model)) if resume and _same_setup(meta, split, method_ids, arm)), None)
                if done is not None:
                    log(f"[{model}] {arm}: resumed from {done.name}")
                    entry["runs"][arm] = done.name
                    continue
                run_dir = run(methods, model, split, arm, log=log, max_usd=remaining())
                spend(run_dir)
                write_report(run_dir)
                entry["runs"][arm] = run_dir.name
                log(f"[{model}] {arm}: {run_dir.name}; sweep spent ${record['spent_usd']:.4f}")
            if stage == "dev":
                first = run(methods, model, "dev", "knows", log=lambda _: None, instance_ids=noise_ids(), fresh_cache=True, max_usd=remaining())
                spend(first)
                second = run(methods, model, "dev", "knows", log=lambda _: None, instance_ids=noise_ids(), fresh_cache=True, max_usd=remaining())
                spend(second)
                within = noise(first, second)
                across = noise(first, runs_dir() / entry["runs"]["knows"]) if "knows" in entry["runs"] else None
                entry["noise"] = {"runs": [first.name, second.name], "within_session": within, "against_dev_run": across}
                log(f"[{model}] noise within one session: " + format_noise(within))
                if across:
                    log(f"[{model}] noise, fresh run against the dev run: " + format_noise(across).splitlines()[0])
                logbook.write_check(f"noise-{model}", entry["noise"])
    except Exception as exc:  # noqa: BLE001
        record.update(ok=False, error=f"{type(exc).__name__}: {exc}"[:800])
        log(f"FAILED: {record['error']}")
    return _finish(record, log)


def _finish(record: dict, log: Callable[[str], None]) -> dict:
    from varag import logbook
    from varag.eval.run import runs_dir

    record["finished_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    out = runs_dir() / f"sweep-{record['stage']}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    out.write_text(json.dumps(record, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
    logbook.write_check(f"sweep-{record['stage']}", record)
    log(f"sweep {record['stage']} {'done' if record['ok'] else 'FAILED'}; spent ${record['spent_usd']:.4f}; summary in {out}")
    if record["ok"] and record["stage"] == "dev":
        log("STOP: dev results are ready for review. The test stage waits for the review and for frozen prompts.")
    return record
