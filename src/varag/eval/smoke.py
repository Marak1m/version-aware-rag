"""``varag smoke``: the end-to-end check (handoff M7 acceptance).

``--offline`` runs what needs no model: environments verified, the dev concepts validated, every
method on the mock backends with the anchors checked (mock_ref 100%, mock_wrong 0% and all
wrong_version, the guard triggering on mock_blend, plain_rag answering through mock_ask), and a
report for each run (``cpu_tiny`` is skipped while inactive). Without the flag it also checks each
active OpenRouter model's endpoint and runs ten dev instances through every method on it.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from varag.config import load_models
from varag.eval.metrics import compute
from varag.eval.report import write_report
from varag.eval.serve import format_report
from varag.eval.run import run, runs_dir
from varag.envs.verify import require_verified


class SmokeFailure(RuntimeError):
    pass


def _step(results: list[dict], name: str, fn: Callable, log: Callable[[str], None]) -> object:
    log(f"[smoke] {name}")
    try:
        value = fn()
        results.append({"step": name, "ok": True})
        return value
    except Exception as exc:  # noqa: BLE001
        results.append({"step": name, "ok": False, "error": f"{type(exc).__name__}: {exc}"[:400]})
        log(f"[smoke] FAILED {name}: {exc}")
        return None


def _pass_rates(run_dir: Path) -> dict[str, dict]:
    return compute(run_dir)["methods"]


def check_anchors(ref_dir: Path, wrong_dir: Path, blend_dir: Path, ask_dir: Path) -> None:
    ref = _pass_rates(ref_dir)
    bad = [m for m, v in ref.items() if (v["intended_pass_rate"]["estimate"] or 0) < 1.0]
    if bad:
        raise SmokeFailure(f"mock_ref below 100% for {bad}")
    wrong = _pass_rates(wrong_dir)
    bad = [m for m, v in wrong.items() if (v["intended_pass_rate"]["estimate"] or 0) > 0 or (v["outcomes"]["wrong_version"] or 0) < 1.0]
    if bad:
        raise SmokeFailure(f"mock_wrong not all wrong_version for {bad}")
    blend = _pass_rates(blend_dir)
    if not blend["va_rag"]["guard"]["flagged"]:
        raise SmokeFailure("the guard did not trigger on mock_blend")
    if (blend["va_rag"]["intended_pass_rate"]["estimate"] or 0) <= (blend["va_rag_no_guard"]["intended_pass_rate"]["estimate"] or 0):
        raise SmokeFailure("va_rag does not beat va_rag_no_guard on mock_blend")
    ask = _pass_rates(ask_dir)
    if (ask["plain_rag"]["ask_recall"] or 0) < 1.0 or (ask["plain_rag"]["intended_pass_rate"]["estimate"] or 0) < 1.0:
        raise SmokeFailure("plain_rag on mock_ask did not ask and then pass")


def cpu_tiny_reachable() -> bool:
    import urllib.request

    spec = load_models()["backends"].get("cpu_tiny")
    if not spec:
        return False
    try:
        with urllib.request.urlopen(spec["base_url"].rstrip("/") + "/models", timeout=5) as resp:
            return resp.status == 200
    except Exception:  # noqa: BLE001
        return False


def smoke(offline: bool, log: Callable[[str], None] = print, validate_concepts: bool = True) -> dict:
    """``validate_concepts=False`` (the final sweep): skip re-validation, which rewrites every
    validation.json with fresh timings; each run still refuses unvalidated or changed concepts."""
    results: list[dict] = []
    log_quiet = lambda _: None  # noqa: E731
    _step(results, "environments verify", require_verified, log)
    from varag.bench.validate import validate

    if validate_concepts:
        _step(results, "validate dev concepts", lambda: validate(log=log_quiet), log)
    else:
        from varag.bench.schema import load_concepts
        from varag.bench.validate import manifest_entries_for

        _step(results, "concepts validated and unchanged since (no re-validation)", lambda: manifest_entries_for(load_concepts()), log)
    dirs: dict[str, Path] = {}
    for key, methods, model, arm in (("ref", "all", "mock_ref", "knows"), ("wrong", "all", "mock_wrong", "knows"),
                                     ("blend", "plain_rag,va_rag,va_rag_no_guard", "mock_blend", "knows"),
                                     ("ask", "plain_rag,assume_state", "mock_ask", "knows"), ("unsure", "va_rag,two_branch,always_ask", "mock_ref", "unsure")):
        path = _step(results, f"run {methods} on {model} ({arm})", lambda m=methods, b=model, a=arm: run(m, b, "dev", a, log=log_quiet), log)
        if path:
            dirs[key] = path
            _step(results, f"report {path.name}", lambda p=path: write_report(p), log)
    if len(dirs) >= 4:
        _step(results, "anchors", lambda: check_anchors(dirs["ref"], dirs["wrong"], dirs["blend"], dirs["ask"]), log)
    tiny = load_models()["backends"].get("cpu_tiny", {})
    if tiny.get("active", True) is False:
        log("[smoke] cpu_tiny is inactive (inference runs on OpenRouter); its parsing check is skipped")
    elif cpu_tiny_reachable():
        path = _step(results, "cpu_tiny: 10 dev instances through every method (never reported)",
                     lambda: run("all", "cpu_tiny", "dev", "knows", log=log_quiet, limit=10), log)
        if path:
            _step(results, f"report {path.name}", lambda p=path: write_report(p), log)
            summary = _pass_rates(path)
            log("[smoke] cpu_tiny response kinds: " + json.dumps({m: v["outcomes"] for m, v in summary.items()}))
    else:
        results.append({"step": "cpu_tiny", "ok": offline is False, "error": "cpu_tiny server not reachable" if offline else None})
        log("[smoke] cpu_tiny server not reachable" + ("" if not offline else ": the offline smoke needs it"))
    if not offline:
        from varag.eval.serve import endpoint_check, format_endpoint_report

        # OpenRouter (2026-10-19): an endpoint check per active model, then ten dev instances
        # through every method. The full dev runs belong to `varag sweep`.
        models = [k for k, v in load_models()["backends"].items() if v.get("type") == "openrouter" and v.get("active", True) and v.get("role") != "judge"]
        for model in models:
            report = _step(results, f"endpoint check {model}", lambda m=model: endpoint_check(m), log)
            if report:
                log(format_endpoint_report(report))
            if report and not report["problems"]:
                path = _step(results, f"run all on {model}: 10 dev instances", lambda m=model: run("all", m, "dev", "knows", log=log_quiet, limit=10), log)
                if path:
                    dirs[f"{model}:smoke"] = path
                    _step(results, f"report {path.name}", lambda p=path: write_report(p), log)
            elif report:
                results.append({"step": f"endpoint check {model} problems", "ok": False, "error": "; ".join(report["problems"])[:400]})
    ok = all(r["ok"] for r in results)
    record = {"offline": offline, "ok": ok, "steps": results, "runs": {k: str(v) for k, v in dirs.items()},
              "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    runs_dir().mkdir(exist_ok=True)
    (runs_dir() / f"smoke-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json").write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8", newline="\n")
    log(f"[smoke] {'PASS' if ok else 'FAIL'}: {sum(r['ok'] for r in results)}/{len(results)} steps")
    return record
