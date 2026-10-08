"""Inventory files: one JSON object per symbol, with a provenance record on the first line.

Check 5 of the handoff's verification table: every derived file carries library, version,
lock_sha256, source, content_sha256 and created_at, and is rejected on read when its
lock_sha256 no longer matches the environment manifest.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from varag.config import project_root

KINDS = ("module", "function", "class", "method", "attribute", "param", "config_key")


class StaleArtifact(RuntimeError):
    """A derived file came from an environment that no longer matches the manifest."""


def inventories_dir() -> Path:
    return project_root() / "data" / "inventories"


def inventory_path(library: str, version: str) -> Path:
    return inventories_dir() / library / f"{version}.jsonl"


def diff_path(library: str) -> Path:
    return inventories_dir() / library / "diff.json"


def content_sha256(lines: list[str]) -> str:
    h = hashlib.sha256()
    for line in lines:
        h.update(line.encode("utf-8"))
        h.update(b"\n")
    return h.hexdigest()


def make_provenance(library: str, version: str, lock_sha256: str, source: str, lines: list[str]) -> dict:
    return {
        "kind": "provenance",
        "library": library,
        "version": version,
        "lock_sha256": lock_sha256,
        "source": source,
        "content_sha256": content_sha256(lines),
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def write_inventory(path: Path, entries: list[dict], library: str, version: str, lock_sha256: str, source: str) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(e, sort_keys=True) for e in entries]
    provenance = make_provenance(library, version, lock_sha256, source, lines)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(provenance, sort_keys=True) + "\n")
        for line in lines:
            fh.write(line + "\n")
    return provenance


def read_inventory(path: Path, expected_lock_sha256: str | None = None) -> tuple[dict, list[dict]]:
    """Returns (provenance, entries). Raises StaleArtifact on a lock or content mismatch."""
    with open(path, encoding="utf-8") as fh:
        first = fh.readline()
        body = [line.rstrip("\n") for line in fh if line.strip()]
    provenance = json.loads(first)
    if provenance.get("kind") != "provenance":
        raise StaleArtifact(f"{path}: first line is not a provenance record")
    if expected_lock_sha256 is not None and provenance["lock_sha256"] != expected_lock_sha256:
        raise StaleArtifact(
            f"{path}: built from lock {provenance['lock_sha256'][:12]}, manifest has {expected_lock_sha256[:12]}; regenerate"
        )
    if content_sha256(body) != provenance["content_sha256"]:
        raise StaleArtifact(f"{path}: content hash mismatch; regenerate")
    return provenance, [json.loads(line) for line in body]
