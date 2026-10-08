"""Example worker: execute documentation examples one by one. Stdlib only; runs inside envs/<name>/.venv.

usage: python run_examples.py <preload>      (preload: "pandas", "numpy" or "none")

stdin: one JSON object per line, {"id": ..., "code": ...}
stdout: one JSON object per line as each example finishes,
        {"id", "status": ok|error, "error", "soft_warnings": [...]}

Each example runs in a fresh namespace (np, and pd for pandas, preloaded) inside its own
temporary directory, with stdout and stderr discarded and an empty stdin. The orchestrator
enforces the per-example timeout and restarts the worker after one.

Soft warnings follow the harness rule: a DeprecationWarning, a FutureWarning (or subclass), or a
migration-message match (VARAG_WARNING_PATTERNS), raised while a frame of the example is on the
stack.
"""

import contextlib
import io
import json
import os
import re
import shutil
import sys
import tempfile
import traceback
import warnings

EXAMPLE_FILE = "<varag-example>"
ADDRESS = re.compile(r" at 0x[0-9A-Fa-f]+")
try:
    _PATTERNS = json.loads(os.environ.get("VARAG_WARNING_PATTERNS") or "[]")
except json.JSONDecodeError:
    _PATTERNS = []
_REGEXES = [re.compile(p["regex"]) for p in _PATTERNS if p.get("regex")]
_SUBSTRINGS = [p["pattern"] for p in _PATTERNS if p.get("pattern")]
CURRENT = {"records": None}


def soft_kind(category, text):
    try:
        if issubclass(category, DeprecationWarning):
            return "DeprecationWarning"
        if issubclass(category, FutureWarning):
            return "FutureWarning"
    except TypeError:
        pass
    if any(s in text for s in _SUBSTRINGS) or any(r.search(text) for r in _REGEXES):
        return "MigrationMessage"
    return None


def _example_on_stack():
    frame = sys._getframe(2)
    while frame is not None:
        if frame.f_code.co_filename == EXAMPLE_FILE:
            return True
        frame = frame.f_back
    return False


def _showwarning(message, category, filename, lineno, file=None, line=None):
    records = CURRENT["records"]
    if records is None or not _example_on_stack():
        return
    text = str(message)
    kind = soft_kind(category, text)
    if kind and len(records) < 20:
        records.append({"kind": kind, "category": category.__name__, "message": text[:300],
                        "signature": f"{category.__name__}: {' '.join(ADDRESS.sub(' at 0x...', text).split())}"[:400]})


def preload_namespace(preload):
    ns = {"__name__": "__main__"}
    if preload in ("pandas", "numpy"):
        import numpy as np
        ns["np"] = np
    if preload == "pandas":
        import pandas as pd
        ns["pd"] = pd
    return ns


def run_one(code, preload, home):
    records = []
    workdir = tempfile.mkdtemp(prefix="ex-", dir=home)
    CURRENT["records"] = records
    status, error = "ok", None
    try:
        ns = preload_namespace(preload)
        os.chdir(workdir)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            exec(compile(code, EXAMPLE_FILE, "exec"), ns)
    except BaseException as exc:  # noqa: BLE001 - SystemExit and KeyboardInterrupt count as errors too
        status = "error"
        lines = traceback.format_exception_only(type(exc), exc)
        error = (lines[-1].strip() if lines else type(exc).__name__)[:300]
    finally:
        CURRENT["records"] = None
        os.chdir(home)
        shutil.rmtree(workdir, ignore_errors=True)
    return {"status": status, "error": error, "soft_warnings": records}


def main():
    preload = sys.argv[1]
    home = tempfile.mkdtemp(prefix="varag-examples-")
    os.chdir(home)
    warnings.simplefilter("always")
    warnings.showwarning = _showwarning
    stdin, stdout = sys.stdin, sys.stdout
    sys.stdin = io.StringIO("")          # examples must not read the worker's input
    try:
        preload_namespace(preload)        # import once up front so import time is not charged to example 1
    except Exception as exc:  # noqa: BLE001
        stdout.write(json.dumps({"fatal": f"preload failed: {type(exc).__name__}: {exc}"}) + "\n")
        stdout.flush()
        return
    stdout.write(json.dumps({"ready": True}) + "\n")
    stdout.flush()
    for line in stdin:
        if not line.strip():
            continue
        item = json.loads(line)
        result = run_one(item["code"], preload, home)
        result["id"] = item["id"]
        stdout.write(json.dumps(result) + "\n")
        stdout.flush()
    shutil.rmtree(home, ignore_errors=True)


if __name__ == "__main__":
    main()
