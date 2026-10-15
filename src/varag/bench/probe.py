"""``varag bench probe``: execute release-note candidates in both environments of their library.

A candidate (data/candidates/*.json) is a change the inventory cannot see (an argument value or a
behaviour), with an ``old`` snippet asserting the old version's behaviour and a ``new`` snippet
asserting the new one. Each snippet runs in both environments through the corpus example runner
(pd/np preloaded, own temp directory, fresh-worker retry). The verdict is form-level:
two_directional when old passes only in old and new passes only in new; one_directional when
the new form also passes in old. A concept built on a candidate still has to pass the validation
matrix: the probe is a pre-screen, not a substitute.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from varag.config import SIDES, env_name
from varag.corpus.examples import run_checks
from varag.envs.build import read_manifest


def verdict(outcome: dict[str, str]) -> str:
    old_only = outcome["old@old"] == "ok" and outcome["old@new"] != "ok"
    if old_only and outcome["new@new"] == "ok":
        return "two_directional" if outcome["new@old"] != "ok" else "one_directional"
    return "none"


def probe(candidates: list[dict]) -> list[dict]:
    manifest = read_manifest()
    for library in sorted({c["library"] for c in candidates}):
        mine = [c for c in candidates if c["library"] == library]
        items = [(f"{c['id']}|{form}", c[form]) for c in mine for form in SIDES]
        results = {side: run_checks(env_name(library, side), library, items, timeout=30, log=lambda _: None) for side in SIDES}
        for c in mine:
            outcome = {}
            for form in SIDES:
                for side in SIDES:
                    r = results[side][f"{c['id']}|{form}"]
                    outcome[f"{form}@{side}"] = "ok" if r.status == "ok" else f"{r.status}: {(r.error or '').strip().splitlines()[-1][:160] if r.error else ''}"
            c["probe"] = {
                "outcome": outcome,
                "verdict": verdict(outcome),
                "lock_sha256": {side: manifest[env_name(library, side)]["lock_sha256"] for side in SIDES},
                "probed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
    return candidates


def probe_file(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    data["candidates"] = probe(data["candidates"])
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return data["candidates"]
