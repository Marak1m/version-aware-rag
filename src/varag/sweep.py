"""``varag sweep``: the model runs in one command, on OpenRouter (docs/RUNBOOK.md).

Stage ``dev`` (the default): preflight; an endpoint check per model (stop on any problem); the
smoke (mock anchors, then ten dev instances through every method on each model); every method on
the dev split for each model and user arm, each run followed by its report; the serving-noise
check per model (the committed 20-instance subset, all methods, twice with a run-private cache,
compared with each other and with the model's dev run); then STOP for review. Stage ``test`` runs
the endpoint checks and the test-split runs only; it is refused while the thresholds or the prompts
are not frozen, or while the test concepts are not validated.

Stage ``final`` (user decision 2026-10-21) is the reported sweep: frozen code (nothing under src/,
configs/, data/, scripts/ or envs/ differs from the commit), frozen prompts and thresholds, then
preflight, endpoint checks, the offline smoke, and for each model, in its own thread so the three
providers serve side by side, the dev and test splits in both user arms with the model's repeats
(small and large 3, mid 1). Each model is one session: one session id on every row and one
session-private response cache, so no response comes from another session and the unsure arm's
first turns are the knows arm's. Mid, with one repeat, also answers the committed 20-instance
noise subset under repeat index 1, which measures its within-session repeat disagreement. The
whole sweep is priced before the first paid call and refused above the cap; the cap is one budget
shared by the three threads. Then the per-run reports, the combined summary and the per-model
reports under docs/results/, the 50-output guard audit sample, and STOP.

Runs are instance-major and carry their session id (provider plus run start time) on every row;
methods are compared only within one session. ``--max-usd`` caps the whole sweep: each run gets
what is left, its estimate is printed before it starts, and the sweep stops once the money is
spent. ``--resume`` skips a (model, arm) whose newest run has the same split, methods, commit,
configs and tasks and was not stopped. Generations are cached, so a rerun after an interruption
pays only for requests that never completed.
"""

from __future__ import annotations

import json
import subprocess
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from varag.config import config_hash, load_experiment, load_models, project_root, sha256_file

ARMS = ("knows", "unsure")
NOISE_SUBSET = "configs/noise_subset_dev.txt"
FROZEN_PATHS = ("src", "configs", "data", "scripts", "envs")


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
    record.setdefault("spent_usd", record.get("spent_before_usd", 0.0))
    if record["stage"] == "final":
        out = runs_dir() / f"sweep-final-{record['stamp']}.json"
        _write_state(record)
    else:
        out = runs_dir() / f"sweep-{record['stage']}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
        out.write_text(json.dumps(record, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
    logbook.write_check(f"sweep-{record['stage']}", record)
    log(f"sweep {record['stage']} {'done' if record['ok'] else 'FAILED'}; spent ${record['spent_usd']:.4f}; record in {out}")
    if record["ok"] and record["stage"] == "dev":
        log("STOP: dev results are ready for review. The test stage waits for the review and for frozen prompts.")
    if record["stage"] == "final":
        log("STOP: the final sweep is done. Post the combined summary, the cost and the failures; change nothing after seeing test results.")
    return record


# --- the final sweep (user decision 2026-10-21) ------------------------------------------------


def code_changes() -> list[str]:
    """Files under the frozen paths that differ from the commit, untracked ones included."""
    try:
        out = subprocess.run(["git", "status", "--porcelain", "--", *FROZEN_PATHS], cwd=project_root(), capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError) as exc:
        return [f"git unavailable ({exc}): cannot show the code is committed"]
    return [line[3:] for line in out.stdout.splitlines() if line.strip()] if out.returncode == 0 else ["git status failed"]


def final_refusals() -> list[str]:
    from varag.pipeline.prompts import frozen_prompts, prompts_sha256

    problems = refusals("all")
    pinned = frozen_prompts()
    if pinned and pinned.get("sha256") != prompts_sha256():
        problems.append(f"the live prompt hash {prompts_sha256()[:12]} differs from the frozen {pinned.get('sha256', '')[:12]}")
    changed = code_changes()
    if changed:
        problems.append(f"code is not frozen: {len(changed)} changed or untracked file(s) under {', '.join(FROZEN_PATHS)} "
                        f"({', '.join(changed[:5])}{', ...' if len(changed) > 5 else ''}); commit first")
    return problems


def final_items(model: str, arms: list[str]) -> list[dict]:
    """A model's runs in order. Mid (one repeat) adds the noise subset under repeat index 1 right
    after its dev knows run, so its within-session repeat disagreement is measured too."""
    from varag.eval.run import model_repeats

    repeats = model_repeats(model)
    items = [{"name": "dev-knows", "split": "dev", "arm": "knows", "repeats": repeats}] if "knows" in arms else []
    if len(repeats) == 1 and "knows" in arms:
        items.append({"name": "dev-noise-repeat", "split": "dev", "arm": "knows", "repeats": [repeats[-1] + 1], "instance_ids": noise_ids()})
    items += [{"name": f"dev-{arm}", "split": "dev", "arm": arm, "repeats": repeats} for arm in arms if arm != "knows"]
    items += [{"name": f"test-{arm}", "split": "test", "arm": arm, "repeats": repeats} for arm in arms]
    return items


def final_plan(models: list[str], arms: list[str], methods: str) -> dict:
    from varag.bench.instances import build_instances
    from varag.bench.schema import load_concepts
    from varag.eval.run import library_versions
    from varag.methods.registry import get_methods

    versions = library_versions()
    counts = {split: len(build_instances(load_concepts(split=split), versions)) for split in ("dev", "test")}
    n_methods = len(get_methods(methods))
    rows = []
    for model in models:
        per, source = seconds_per_answer(model)
        answers = sum((len(item["instance_ids"]) if item.get("instance_ids") else counts[item["split"]]) * n_methods * len(item["repeats"])
                      for item in final_items(model, arms))
        rows.append({"model": model, "runs": [i["name"] for i in final_items(model, arms)], "answers": answers,
                     "seconds_per_answer": round(per, 2), "estimate_min": round(answers * per / 60, 1), "source": source})
    return {"split": "dev+test", "instances": counts, "methods": n_methods, "arms": arms, "models": rows,
            "concepts": len(load_concepts(split="dev")) + len(load_concepts(split="test")), "instances_total": sum(counts.values()),
            "total_min": round(max((r["estimate_min"] for r in rows), default=0), 1)}


def format_final_plan(p: dict) -> str:
    lines = [f"final sweep: dev {p['instances']['dev']} and test {p['instances']['test']} instances, {p['methods']} methods, arms {', '.join(p['arms'])}"]
    for r in p["models"]:
        lines.append(f"  {r['model']:6} {', '.join(r['runs'])}: {r['answers']} answers x {r['seconds_per_answer']} s = about {r['estimate_min']} min ({r['source']})")
    lines.append(f"  models run side by side: about {p['total_min']} min wall time")
    return "\n".join(lines)


def _session_cost(sessions: list[str]) -> float:
    from varag import logbook

    path = logbook.logs_dir() / "costs.jsonl"
    if not path.exists():
        return 0.0
    total = 0.0
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rec = json.loads(line)
            if rec.get("session") in sessions:
                total += float(rec.get("cost_usd") or 0)
    return total


def _write_state(record: dict) -> None:
    from varag.eval.run import runs_dir

    with _state_lock:
        path = runs_dir() / f"sweep-final-{record['stamp']}.json"
        path.write_text(json.dumps(record, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")


_state_lock = threading.RLock()     # the model threads update the record; writes see a consistent copy


def _run_matches(run_dir: Path, item: dict, session: str, method_ids: list[str]) -> bool:
    try:
        meta = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return (meta.get("session") == session and meta.get("split") == item["split"] and meta.get("user_arm") == item["arm"]
            and meta.get("repeats") == item["repeats"] and (meta.get("instance_ids") or None) == (item.get("instance_ids") or None)
            and meta.get("methods") == method_ids and not meta.get("stopped"))


def final_sweep(models: list[str] | None = None, arms: list[str] | None = None, methods: str = "all", max_usd: float | None = None,
                resume: bool = False, dry_run: bool = False, log: Callable[[str], None] = print) -> dict:
    from varag import logbook
    from varag.eval.budget import price
    from varag.eval.report import write_report
    from varag.eval.run import git_commit, planned_requests, run, runs_dir
    from varag.eval.serve import endpoint_check, format_endpoint_report
    from varag.llm.client import Budget, ResponseCache, cache_dir, make_backend
    from varag.methods.registry import get_methods
    from varag.preflight import format_checks, preflight

    models = list(models or default_models())
    arms = list(arms or ARMS)
    method_ids = [m.id for m in get_methods(methods)]
    previous = None
    if resume:
        states = sorted(runs_dir().glob("sweep-final-*.json"))
        previous = json.loads(states[-1].read_text(encoding="utf-8")) if states else None
        if previous and previous.get("git_commit") != git_commit():
            log(f"not resuming {states[-1].name}: it ran on commit {str(previous.get('git_commit'))[:12]}, this is {str(git_commit())[:12]}")
            previous = None
    stamp = previous["stamp"] if previous else datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    p = final_plan(models, arms, methods)
    log(format_final_plan(p))
    record: dict = {"stage": "final", "stamp": stamp, "plan": p, "max_usd": max_usd, "methods": method_ids, "arms": arms,
                    "started_at": (previous or {}).get("started_at") or datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "resumed_at": datetime.now(timezone.utc).isoformat(timespec="seconds") if previous else None,
                    "git_commit": git_commit(), "config_hash": config_hash(), "models": {}, "ok": True, "failures": []}
    refused = final_refusals()
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
    for model in models:
        spec = load_models()["backends"][model]
        old = ((previous or {}).get("models") or {}).get(model) or {}
        session = old.get("session") or f"{spec.get('provider', model)}@{stamp}"
        cache = old.get("cache") or str((cache_dir() / "sessions" / f"{model}-{stamp}").relative_to(project_root()))
        record["models"][model] = {"session": session, "cache": cache, "items": final_items(model, arms), "runs": dict(old.get("runs") or {}),
                                   "endpoint_check": None, "error": None}
        report = endpoint_check(model)
        log(format_endpoint_report(report))
        record["models"][model]["endpoint_check"] = {k: v for k, v in report.items() if k not in ("response",)}
        if report["problems"]:
            record.update(ok=False, error=f"endpoint check failed for {model}: {'; '.join(report['problems'])}")
            return _finish(record, log)
    sessions = [m["session"] for m in record["models"].values()]
    spent_before = _session_cost(sessions) if previous else 0.0
    endpoint_cost = sum(float((m["endpoint_check"] or {}).get("cost_usd") or 0) for m in record["models"].values())
    budget = Budget(None if max_usd is None else max(0.0, max_usd - spent_before - endpoint_cost))
    record["spent_before_usd"] = round(spent_before + endpoint_cost, 6)
    from varag.eval.smoke import smoke

    smoked = smoke(offline=True, log=log, validate_concepts=False)
    record["smoke_offline"] = smoked["ok"]
    if not smoked["ok"]:
        record.update(ok=False, error="the offline smoke failed")
        return _finish(record, log)

    # Price every remaining run of every model before the first paid call: the distinct
    # first-turn requests per model, against that model's session cache.
    total = 0.0
    for model, entry in record["models"].items():
        backend = make_backend(model)
        backend.cache = ResponseCache(project_root() / entry["cache"])
        todo = [i for i in entry["items"] if not (i["name"] in entry["runs"] and _run_matches(runs_dir() / entry["runs"][i["name"]], i, entry["session"], method_ids))]
        requests = []
        for item in todo:
            requests += planned_requests(backend, methods, item["split"], item["arm"], item["repeats"], item.get("instance_ids"))
        entry["estimate"] = price(backend, requests) if requests else {"usd": 0.0, "uncached": 0}
        total += entry["estimate"]["usd"]
        log(f"[{model}] {len(todo)} runs to do; estimate ${entry['estimate']['usd']:.4f} for {entry['estimate']['uncached']} uncached distinct first-turn requests "
            f"(x{entry['estimate'].get('turn_factor', 1)} for extra turns)")
    record["estimate_usd"] = round(total, 4)
    left = budget.remaining()
    log(f"final sweep estimate ${total:.4f}" + (f" against ${left:.2f} left of the ${max_usd:.2f} cap" if left is not None else "; no cap"))
    logbook.event("final_sweep_estimate", stamp=stamp, estimate_usd=total, remaining_usd=left, models={m: e["estimate"].get("usd") for m, e in record["models"].items()})
    if left is not None and total > left:
        record.update(ok=False, error=f"estimate ${total:.4f} exceeds the ${left:.2f} left of the cap")
        return _finish(record, log)
    _write_state(record)

    def worker(model: str) -> None:
        entry = record["models"][model]
        model_log_path = logbook.logs_dir() / "sweep" / f"final-{stamp}-{model}.log"
        model_log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(model_log_path, "a", encoding="utf-8", newline="\n") as fh:
            def mlog(line: str) -> None:
                fh.write(logbook.redact(line) + "\n")
                fh.flush()
                if not line.startswith("  "):          # per-answer lines go to the model's log only
                    log(f"[{model}] {line}")

            for item in entry["items"]:
                done = entry["runs"].get(item["name"])
                if done and _run_matches(runs_dir() / done, item, entry["session"], method_ids):
                    mlog(f"{item['name']}: done in {done}")
                    continue
                try:
                    run_dir = run(methods, model, item["split"], item["arm"], log=mlog, repeats=item["repeats"], instance_ids=item.get("instance_ids"),
                                  session=entry["session"], cache=project_root() / entry["cache"], budget=budget)
                    write_report(run_dir)
                except (Exception, SystemExit) as exc:  # noqa: BLE001
                    with _state_lock:
                        entry["error"] = f"{item['name']}: {type(exc).__name__}: {exc}"[:800]
                    mlog(f"FAILED {entry['error']}")
                    break
                meta = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
                with _state_lock:
                    entry["runs"][item["name"]] = run_dir.name
                    if meta.get("stopped"):
                        entry["error"] = f"{item['name']} stopped: {meta['stopped']}"
                mlog(f"{item['name']}: {run_dir.name}, ${meta.get('cost_usd', 0):.4f}, {meta.get('wall_seconds')} s; sweep spent ${budget.spent:.4f}")
                _write_state(record)
                if meta.get("stopped"):
                    break

    threads = [threading.Thread(target=worker, args=(m,), name=f"final-{m}") for m in record["models"]]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    record["spent_usd"] = round(record["spent_before_usd"] + budget.spent, 6)
    record["session_cost_usd"] = round(_session_cost(sessions), 6)
    for model, entry in record["models"].items():
        if entry.get("error"):
            record["failures"].append(f"{model}: {entry['error']}")
    record["ok"] = not record["failures"]
    _write_state(record)
    try:
        from varag.eval.summary import write_final

        out = write_final(record, log=log)
        record["summary"] = str(out.relative_to(project_root()))
    except Exception as exc:  # noqa: BLE001
        record["failures"].append(f"summary: {type(exc).__name__}: {exc}"[:800])
        record["ok"] = False
        log(f"FAILED summary: {exc}")
    return _finish(record, log)
