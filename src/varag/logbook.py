"""The logbook: everything a session does, kept under ``logs/`` so it can be read later.

  logs/README.md                    what each file holds
  logs/commands/<stamp>-<cmd>.log   stdout and stderr of every ``varag`` invocation
  logs/openrouter/<date>.jsonl      every OpenRouter request (body without credentials), response,
                                    status, attempt, backoff, latency; cache hits as one-line records
  logs/costs.jsonl                  one line per paid call: backend, provider, tokens, cost, session
  logs/events.jsonl                 milestones: runs started and finished, budget stops, checks
  logs/checks/<kind>-<stamp>.json   endpoint checks, noise checks, sweeps

Nothing here holds the API key: request headers are never logged, and ``redact`` removes anything
that looks like an OpenRouter key from free text before it is written.
"""

from __future__ import annotations

import json
import re
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

from varag.config import project_root

KEY_PATTERN = re.compile(r"sk-or-[A-Za-z0-9_-]{8,}")
_lock = threading.Lock()


def logs_dir() -> Path:
    path = project_root() / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def redact(text: str) -> str:
    return KEY_PATTERN.sub("sk-or-[REDACTED]", text)


def append(relative: str, record: dict) -> None:
    path = logs_dir() / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    line = redact(json.dumps({"ts": now(), **record}, ensure_ascii=False, default=str))
    with _lock, open(path, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(line + "\n")


def event(kind: str, **data) -> None:
    append("events.jsonl", {"event": kind, **data})


def openrouter(record: dict) -> None:
    append(f"openrouter/{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.jsonl", record)


def cost(record: dict) -> None:
    append("costs.jsonl", record)


def write_check(kind: str, record: dict) -> Path:
    path = logs_dir() / "checks" / f"{kind}-{stamp()}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(redact(json.dumps(record, indent=1, ensure_ascii=False, default=str)) + "\n", encoding="utf-8", newline="\n")
    return path


def total_cost() -> float:
    path = logs_dir() / "costs.jsonl"
    if not path.exists():
        return 0.0
    return sum(float(json.loads(line).get("cost_usd") or 0) for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


class _Tee:
    def __init__(self, stream, fh):
        self.stream, self.fh = stream, fh

    def write(self, data):
        self.stream.write(data)
        try:
            self.fh.write(redact(data))
            self.fh.flush()
        except ValueError:
            pass
        return len(data)

    def flush(self):
        self.stream.flush()

    def __getattr__(self, name):
        return getattr(self.stream, name)


def tee_command(argv: list[str]) -> Path | None:
    """Copy this process's stdout and stderr into logs/commands/. Called once by the CLI."""
    if not argv or argv[0] in ("--help", "-h", "--version"):
        return None
    name = "-".join(a for a in argv[:2] if not a.startswith("-")).replace("/", "_") or "varag"
    path = logs_dir() / "commands" / f"{stamp()}-{name}.log"
    path.parent.mkdir(parents=True, exist_ok=True)
    fh = open(path, "a", encoding="utf-8", newline="\n")
    fh.write(f"$ varag {redact(' '.join(argv))}\n# started {now()}\n")
    sys.stdout = _Tee(sys.stdout, fh)
    sys.stderr = _Tee(sys.stderr, fh)
    return path
