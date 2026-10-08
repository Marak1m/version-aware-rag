"""``varag bench validate``: the validation matrix a concept must pass before it enters
data/tasks/MANIFEST.json (handoff, "Validation", steps 1 to 9).

Steps 6 and 7 need the M5 extractor and the M4 corpus; until then they are recorded as
``skipped`` (docs/DECISIONS.md). A concept passes when no step failed.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from varag.bench.schema import Concept, concept_sha256, find_concept_dir, load_concept, load_concepts, manifest_path
from varag.config import SIDES, env_name, load_experiment, other_side, sha256_file
from varag.envs.verify import require_verified
from varag.eval.execute import ExecResult, execute
from varag.inventory.build import load_diff
from varag.inventory.diff import bucket_of
from varag.pipeline.signals import static_usages

STEP_NAMES = {
    1: "references pass in their own environment",
    2: "references fail in the other environment by test failure or exception",
    3: "all runs repeat with identical results",
    4: "references use the right exclusive symbols (static), gold symbols sit in the right buckets",
    5: "portable reference passes both environments with no deprecation warning",
    6: "each clue alone infers its version; error tracebacks reproduce",
    7: "gold chunks exist in the corpus for both versions",
    8: "query names the entry point and passes the version-number lint",
    9: "deprecation warnings from the references are recorded per environment",
}


@dataclass
class Step:
    status: str   # pass | fail | skipped
    detail: str = ""

    def to_dict(self) -> dict:
        return {"status": self.status, "detail": self.detail}


def _run(concept: Concept, ref: str, side: str) -> ExecResult:
    return execute(env_name(concept.library, side), concept.reference(ref), concept.test_path, concept.warnings_as_errors)


def _describe(r: ExecResult) -> str:
    return f"{r.status}" + (f" ({r.last_line})" if r.last_line else "") + (f" [{r.infra_reason}]" if r.infra_reason else "")


def _static_step(concept: Concept, diff: dict) -> Step:
    problems: list[str] = []
    if concept.is_control:
        usages = static_usages(concept.reference("portable"), diff)
        if usages.old or usages.new:
            problems.append(f"ref_portable uses exclusive symbols: old={sorted(usages.old)} new={sorted(usages.new)}")
        for symbol in concept.gold.get("shared", []):
            if bucket_of(diff, symbol) != "shared_same":
                problems.append(f"gold.shared {symbol} is in {bucket_of(diff, symbol)}, not shared_same")
        return Step("fail" if problems else "pass", "; ".join(problems))

    if concept.exclusivity == "behavior":
        return Step("skipped", "static check does not apply to behavior concepts")
    old_use = static_usages(concept.reference("old"), diff)
    new_use = static_usages(concept.reference("new"), diff)
    if not old_use.parsed or not new_use.parsed:
        problems.append("reference does not parse")
    if not (old_use.old or old_use.deprecated_in_new):
        problems.append("ref_old uses no old_only or deprecated_in_new symbol")
    if old_use.new:
        problems.append(f"ref_old uses new_only symbols {sorted(old_use.new)}")
    if not new_use.new:
        problems.append("ref_new uses no new_only symbol")
    if new_use.old or new_use.deprecated_in_new:
        problems.append(f"ref_new uses old-side symbols {sorted(new_use.old | new_use.deprecated_in_new)}")
    for symbol in concept.gold.get("old", []):
        if bucket_of(diff, symbol) not in ("old_only", "deprecated_in_new"):
            problems.append(f"gold.old {symbol} is in {bucket_of(diff, symbol)}")
    for symbol in concept.gold.get("new", []):
        if bucket_of(diff, symbol) != "new_only":
            problems.append(f"gold.new {symbol} is in {bucket_of(diff, symbol)}")
    detail = "; ".join(problems) if problems else f"ref_old uses {sorted(old_use.old | old_use.deprecated_in_new)}; ref_new uses {sorted(new_use.new)}"
    return Step("fail" if problems else "pass", detail)


def validate_concept(concept: Concept, repeats: int | None = None, log: Callable[[str], None] = print) -> dict:
    repeats = repeats or int(load_experiment().get("execution", {}).get("repeats", 3))
    diff = load_diff(concept.library)
    steps: dict[int, Step] = {}
    runs: dict[str, ExecResult] = {}
    warnings_by_ref: dict[str, dict[str, int]] = {}

    if concept.is_control:
        for side in SIDES:
            runs[f"ref_portable/{side}"] = _run(concept, "portable", side)
        failures = [k for k, r in runs.items() if not r.passed]
        steps[1] = Step("pass" if not failures else "fail", "; ".join(f"{k}: {_describe(runs[k])}" for k in failures))
        steps[2] = Step("skipped", "no-conflict control has no other version")
        warned = [k for k, r in runs.items() if r.deprecation_warnings]
        steps[5] = Step("pass" if not warned else "fail", "; ".join(f"{k}: {runs[k].warnings[:2]}" for k in warned))
    else:
        for ref, side in (("old", "old"), ("new", "new"), ("old", "new"), ("new", "old")):
            runs[f"ref_{ref}/{side}"] = _run(concept, ref, side)
        own = {k: runs[k] for k in ("ref_old/old", "ref_new/new")}
        other = {k: runs[k] for k in ("ref_old/new", "ref_new/old")}
        bad = [k for k, r in own.items() if not r.passed]
        steps[1] = Step("pass" if not bad else "fail", "; ".join(f"{k}: {_describe(runs[k])}" for k in bad))
        bad = [k for k, r in other.items() if not r.failed_by_code]
        steps[2] = Step("pass" if not bad else "fail",
                        "; ".join(f"{k}: {_describe(runs[k])}" for k in bad) or "; ".join(f"{k}: {_describe(r)}" for k, r in other.items()))
        if concept.has_portable:
            for side in SIDES:
                runs[f"ref_portable/{side}"] = _run(concept, "portable", side)
            portable = {k: r for k, r in runs.items() if k.startswith("ref_portable/")}
            problems = [f"{k}: {_describe(r)}" for k, r in portable.items() if not r.passed]
            problems += [f"{k}: deprecation warnings {r.warnings[:2]}" for k, r in portable.items() if r.deprecation_warnings]
            steps[5] = Step("pass" if not problems else "fail", "; ".join(problems))
        else:
            steps[5] = Step("skipped", "portable_alternative: none")

    # Step 3: repeat every run and require identical statuses.
    unstable: list[str] = []
    for key, first in runs.items():
        ref, side = key.split("/")
        for _ in range(max(repeats - 1, 0)):
            again = _run(concept, ref.removeprefix("ref_"), side)
            if again.status != first.status:
                unstable.append(f"{key}: {first.status} then {again.status}")
                break
    steps[3] = Step("pass" if not unstable else "fail", "; ".join(unstable) or f"{repeats} identical repeats per run")

    steps[4] = _static_step(concept, diff)
    steps[6] = Step("skipped", "needs the M5 signal extractor and make-error-clue")
    steps[7] = Step("skipped", "needs the M4 corpus")
    steps[8] = Step("pass", "checked by the concept loader")
    for key, r in runs.items():
        ref, side = key.split("/")
        warnings_by_ref.setdefault(ref, {})[side] = r.deprecation_warnings
    steps[9] = Step("pass", json.dumps(warnings_by_ref, sort_keys=True))

    passed = all(s.status != "fail" for s in steps.values())
    record = {
        "concept_id": concept.id,
        "library": concept.library,
        "kind": concept.kind,
        "split": concept.split,
        "concept_sha256": concept_sha256(concept.directory),
        "validated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "passed": passed,
        "steps": {str(n): {"name": STEP_NAMES[n], **steps[n].to_dict()} for n in sorted(steps)},
        "runs": {k: r.to_dict() for k, r in runs.items()},
        "reference_warnings": warnings_by_ref,
    }
    for n in sorted(steps):
        mark = {"pass": "ok", "fail": "FAIL", "skipped": "skip"}[steps[n].status]
        log(f"  [{mark:4}] step {n}: {STEP_NAMES[n]}" + (f" -- {steps[n].detail}" if steps[n].detail and steps[n].status != "pass" else ""))
    return record


def read_task_manifest() -> dict:
    path = manifest_path()
    if not path.exists():
        return {"concepts": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def write_task_manifest(manifest: dict) -> None:
    manifest["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    manifest_path().parent.mkdir(parents=True, exist_ok=True)
    manifest_path().write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate(concept_ids: tuple[str, ...] | list[str] = (), log: Callable[[str], None] = print) -> dict[str, dict]:
    concepts = [load_concept(find_concept_dir(c)) for c in concept_ids] if concept_ids else load_concepts()
    require_verified(sorted({env_name(c.library, side) for c in concepts for side in SIDES}))
    manifest = read_task_manifest()
    records: dict[str, dict] = {}
    for concept in concepts:
        log(f"{concept.id} ({concept.library}, {concept.kind})")
        record = validate_concept(concept, log=log)
        records[concept.id] = record
        validation_path = concept.directory / "validation.json"
        validation_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if record["passed"]:
            manifest["concepts"][concept.id] = {
                "library": concept.library,
                "kind": concept.kind,
                "split": concept.split,
                "path": concept.directory.relative_to(manifest_path().parent).as_posix(),
                "concept_sha256": record["concept_sha256"],
                "validation_sha256": sha256_file(validation_path),
                "validated_at": record["validated_at"],
            }
            log(f"  -> validated, added to manifest")
        else:
            manifest["concepts"].pop(concept.id, None)
            log(f"  -> FAILED, not in manifest")
    write_task_manifest(manifest)
    return records


def manifest_entries_for(concepts: list[Concept]) -> dict[str, dict]:
    """The manifest entries for ``concepts``; raises when a concept is unvalidated or changed."""
    manifest = read_task_manifest()["concepts"]
    out = {}
    for concept in concepts:
        entry = manifest.get(concept.id)
        if entry is None:
            raise RuntimeError(f"{concept.id} is not validated; run `varag bench validate {concept.id}`")
        if entry["concept_sha256"] != concept_sha256(concept.directory):
            raise RuntimeError(f"{concept.id} changed since validation; re-run `varag bench validate {concept.id}`")
        out[concept.id] = entry
    return out
