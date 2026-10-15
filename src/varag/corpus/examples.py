"""Chunk examples: extraction from docstrings and docs markdown, and the check by execution.

Execution check (the user's M4 rule, docs/DECISIONS.md):
- each example runs in its tagged environment with pd/np preloaded and printed output ignored,
  in its own temp directory; it is kept only if it runs without error;
- soft warnings it raises are recorded on the chunk;
- it also runs in the other environment of the library; ``discriminative`` when it fails there;
- a failed run is re-run in a fresh worker before it counts as failed;
- examples that time out are dropped; examples that name a URL are dropped unrun (D7).
"""

from __future__ import annotations

import hashlib
import json
import queue
import re
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from varag.envs.runner import env_dir, env_python, scripts_dir, stripped_env
from varag.eval.execute import warning_patterns

PRELOAD = {"pandas": "pandas", "numpy": "numpy", "pydantic": "none"}
URL = re.compile(r"https?://")
SKIP = re.compile(r"doctest:\s*\+SKIP", re.I)
FENCE = re.compile(r"^([ \t]*)```[ \t]*(py|python)\b[^\n]*\n(.*?)^\1```", re.S | re.M)


def example_sha(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


# --- extraction ---------------------------------------------------------------------------


def doctest_statements(examples_text: str) -> list[str]:
    """Statements from a doctest block: `>>>` lines with their `...` continuations, prompts removed.
    Output lines are dropped."""
    statements: list[list[str]] = []
    for raw in examples_text.splitlines():
        line = raw.strip("\r")
        stripped = line.lstrip()
        if stripped.startswith(">>>"):
            statements.append([stripped[4:] if stripped.startswith(">>> ") else stripped[3:]])
        elif stripped.startswith("...") and statements:
            statements[-1].append(stripped[4:] if stripped.startswith("... ") else stripped[3:])
    return ["\n".join(s).rstrip() for s in statements if "\n".join(s).strip()]


def call_arguments(code: str, name: str) -> list[str]:
    """The argument text of every call ``name(...)`` in ``code``, matched by balanced parentheses."""
    out = []
    for m in re.finditer(r"\b" + re.escape(name) + r"\s*\(", code):
        depth, start = 1, m.end()
        for i in range(start, len(code)):
            if code[i] == "(":
                depth += 1
            elif code[i] == ")":
                depth -= 1
                if depth == 0:
                    out.append(code[start:i])
                    break
    return out


def passes_keyword(code: str, name: str, keyword: str) -> bool:
    """True when some call to ``name`` passes ``keyword=`` directly (not a nested call's keyword)."""
    for args in call_arguments(code, name):
        flat, depth = [], 0
        for ch in args:                       # blank out nested call arguments
            depth += ch in "([{"
            flat.append(ch if depth == 0 else " ")
            depth -= ch in ")]}"
        if re.search(r"(?:^|,)\s*" + re.escape(keyword) + r"\s*=(?!=)", "".join(flat)):
            return True
    return False


def uses_symbol(statement: str, name: str, keyword: str | None) -> bool:
    if keyword:
        return passes_keyword(statement, name, keyword)
    return bool(re.search(r"\b" + re.escape(name) + r"\b", statement))


def _is_bare_display(statement: str) -> bool:
    """A statement that only displays a name (``>>> df``): dropped, its output is ignored anyway."""
    return bool(re.fullmatch(r"[A-Za-z_][\w.]*", statement.strip()))


def extract_doctest_example(examples_text: str, name: str, keyword: str | None = None, max_statements: int = 12) -> tuple[str | None, bool]:
    """The doctest prefix up to and including the first statement that uses ``name``.

    With ``keyword`` (decision D5), a statement that calls ``name`` passing ``keyword=`` is
    preferred; the second return value says whether that preference was met. SKIP-marked
    statements and bare display statements are dropped. Returns (None, False) when no statement
    uses the name within ``max_statements``."""
    statements = [s for s in doctest_statements(examples_text) if not SKIP.search(s) and not _is_bare_display(s)]
    for want_keyword in ([keyword, None] if keyword else [None]):
        for i, statement in enumerate(statements[:max_statements]):
            if uses_symbol(statement, name, want_keyword):
                return "\n".join(statements[: i + 1]), want_keyword is not None
    return None, False


def fenced_blocks(markdown: str) -> list[str]:
    """Python code blocks from markdown, dedented."""
    import textwrap

    return [textwrap.dedent(m.group(3)).strip("\n") for m in FENCE.finditer(markdown)]


def pick_block(blocks: list[str], name: str, keyword: str | None = None) -> tuple[str | None, bool]:
    for want_keyword in ([keyword, None] if keyword else [None]):
        for block in blocks:
            if uses_symbol(block, name, want_keyword):
                return block, want_keyword is not None
    return None, False


# --- execution ------------------------------------------------------------------------------


@dataclass
class CheckResult:
    status: str                 # ok | error | timeout | network
    error: str | None = None
    soft_warnings: list = field(default_factory=list)
    retried: bool = False

    def to_dict(self) -> dict:
        return {"status": self.status, "error": self.error, "soft_warnings": self.soft_warnings, "retried": self.retried}


class _Worker:
    def __init__(self, env: str, preload: str, library: str):
        python = env_python(env)
        self.proc = subprocess.Popen(
            [str(python), "-I", str(scripts_dir() / "run_examples.py"), preload],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, encoding="utf-8", errors="replace", cwd=str(env_dir(env)),
            env=stripped_env(python, {"VARAG_WARNING_PATTERNS": json.dumps(warning_patterns(library))}),
        )
        self.lines: queue.Queue = queue.Queue()
        threading.Thread(target=self._pump, daemon=True).start()
        ready = self._next(120)
        if not ready or not ready.get("ready"):
            self.kill()
            raise RuntimeError(f"example worker in {env} did not start: {ready}")

    def _pump(self):
        for line in self.proc.stdout:
            self.lines.put(line)
        self.lines.put(None)

    def _next(self, timeout: float) -> dict | None:
        try:
            line = self.lines.get(timeout=timeout)
        except queue.Empty:
            return {"timeout": True}
        if line is None:
            return None
        return json.loads(line)

    def run(self, item_id: str, code: str, timeout: float) -> CheckResult:
        """A timeout or a dead worker means the caller must replace the worker."""
        try:
            self.proc.stdin.write(json.dumps({"id": item_id, "code": code}) + "\n")
            self.proc.stdin.flush()
        except OSError:
            return CheckResult("error", "worker died")
        out = self._next(timeout)
        if out is None:
            return CheckResult("error", "worker died")
        if out.get("timeout"):
            return CheckResult("timeout")
        return CheckResult(out["status"], out.get("error"), out.get("soft_warnings", []))

    def kill(self):
        try:
            self.proc.kill()
        except OSError:
            pass


def _run_sequence(env: str, library: str, items: list[tuple[str, str]], timeout: float) -> dict[str, CheckResult]:
    preload = PRELOAD[library]
    results: dict[str, CheckResult] = {}
    worker = None
    for item_id, code in items:
        if worker is None:
            worker = _Worker(env, preload, library)
        result = worker.run(item_id, code, timeout)
        results[item_id] = result
        if result.status == "timeout" or result.error == "worker died":
            worker.kill()
            worker = None
    if worker is not None:
        worker.kill()
    return results


def run_checks(env: str, library: str, items: list[tuple[str, str]], timeout: float = 10.0,
               parallel: int = 6, log: Callable[[str], None] = print) -> dict[str, CheckResult]:
    """Execute (id, code) items in ``env``. Failed items are re-run, each in a fresh worker."""
    results: dict[str, CheckResult] = {}
    runnable = []
    for item_id, code in items:
        if URL.search(code):
            results[item_id] = CheckResult("network", "example names a URL; not run (D7)")
        else:
            runnable.append((item_id, code))
    chunks = [runnable[i::parallel] for i in range(parallel)]
    with ThreadPoolExecutor(max_workers=parallel) as pool:
        for part in pool.map(lambda c: _run_sequence(env, library, c, timeout) if c else {}, chunks):
            results.update(part)
    failed = [(i, c) for i, c in runnable if results[i].status == "error"]
    if failed:
        log(f"  [{env}] re-running {len(failed)} failed example(s), each in a fresh worker")
        with ThreadPoolExecutor(max_workers=parallel) as pool:
            for (item_id, _), retry in zip(failed, pool.map(lambda ic: _run_sequence(env, library, [ic], timeout)[ic[0]], failed)):
                retry.retried = True
                results[item_id] = retry
    return results


class CheckCache:
    """data/corpus/{library}/example_checks.jsonl, keyed by (environment lock sha256, example sha256)."""

    def __init__(self, path: Path):
        self.path = path
        self.entries: dict[tuple[str, str], dict] = {}
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    row = json.loads(line)
                    self.entries[(row["lock_sha256"], row["example_sha256"])] = row

    def get(self, lock: str, sha: str) -> CheckResult | None:
        row = self.entries.get((lock, sha))
        if row is None:
            return None
        return CheckResult(row["status"], row.get("error"), row.get("soft_warnings", []), row.get("retried", False))

    def put(self, lock: str, sha: str, env: str, result: CheckResult) -> None:
        self.entries[(lock, sha)] = {"lock_sha256": lock, "example_sha256": sha, "env": env, **result.to_dict()}

    def save(self, keep: set[tuple[str, str]] | None = None) -> None:
        rows = [r for k, r in sorted(self.entries.items()) if keep is None or k in keep]
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8", newline="\n") as fh:
            for row in rows:
                fh.write(json.dumps(row, sort_keys=True) + "\n")
