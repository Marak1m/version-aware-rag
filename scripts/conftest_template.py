"""conftest.py injected by the harness into every execution directory. Stdlib + pytest hooks.

Run with ``-p no:warnings``: pytest's warnings plugin replaces ``warnings.showwarning`` around
every test and collection step, which would bypass the hook installed here.

Environment:
  VARAG_LIBRARY             module to import for the version stamp (pandas, numpy, pydantic)
  VARAG_EXPECT_VERSION      the version the harness believes is installed
  VARAG_RESULT_PATH         where to write the JSON result record
  VARAG_WARNING_PATTERNS    JSON list of {"pattern": substring} or {"regex": expr} migration messages
  VARAG_WARNINGS_AS_ERRORS  "1" to raise attributed soft warnings as exceptions

Check 4 of the handoff's verification table: the stamp asserts the library version equals
VARAG_EXPECT_VERSION and writes it into the result; a mismatch is infra_error, never fail.

Warning attribution (docs/DECISIONS.md): a warning is the solution's when any frame from
solution.py is on the stack when it fires. That covers warnings raised while solution.py is
imported (module-level class definitions, decorators) as well as during test calls, and it does
not depend on the module the warning reports, which libraries often set to their own internals.
A soft warning is a DeprecationWarning, a FutureWarning (or a subclass of either), or any warning
whose message matches a library-authored migration message.
"""

import importlib
import json
import os
import re
import sys
import warnings

import pytest

STATE = {
    "status": None,
    "infra_reason": None,
    "stamp_version": None,
    "collected": 0,
    "exit_status": None,
    "warning_counts": {"DeprecationWarning": 0, "FutureWarning": 0, "MigrationMessage": 0},
    "soft_warnings": [],
    "unattributed_warnings": 0,
    "failures": [],
}
MAX_RECORDS = 200
ADDRESS = re.compile(r" at 0x[0-9A-Fa-f]+")

try:
    _PATTERNS = json.loads(os.environ.get("VARAG_WARNING_PATTERNS") or "[]")
except json.JSONDecodeError:
    _PATTERNS = []
_REGEXES = [re.compile(p["regex"]) for p in _PATTERNS if p.get("regex")]
_SUBSTRINGS = [p["pattern"] for p in _PATTERNS if p.get("pattern")]
_AS_ERRORS = os.environ.get("VARAG_WARNINGS_AS_ERRORS") == "1"


def _write():
    path = os.environ.get("VARAG_RESULT_PATH")
    if path:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(STATE, fh)


def _infra(reason):
    STATE["status"] = "infra_error"
    STATE["infra_reason"] = reason
    _write()
    pytest.exit("varag: " + reason, returncode=3)


def _solution_on_stack():
    frame = sys._getframe(2)
    while frame is not None:
        if os.path.basename(frame.f_code.co_filename) == "solution.py":
            return True
        frame = frame.f_back
    return False


def _matches_migration_message(text):
    return any(s in text for s in _SUBSTRINGS) or any(r.search(text) for r in _REGEXES)


def soft_kind(category, text):
    """The soft-warning kind of a warning, or None when it is not a soft warning."""
    try:
        if issubclass(category, DeprecationWarning):
            return "DeprecationWarning"
        if issubclass(category, FutureWarning):
            return "FutureWarning"
    except TypeError:
        pass
    if _matches_migration_message(text):
        return "MigrationMessage"
    return None


def signature(category_name, text):
    """Category plus normalised message: what reference subtraction compares."""
    return f"{category_name}: {' '.join(ADDRESS.sub(' at 0x...', text).split())}"[:400]


def _showwarning(message, category, filename, lineno, file=None, line=None):
    if not _solution_on_stack():
        STATE["unattributed_warnings"] += 1
        return
    text = str(message)
    kind = soft_kind(category, text)
    if kind is None:
        return
    STATE["warning_counts"][kind] += 1
    if len(STATE["soft_warnings"]) < MAX_RECORDS:
        STATE["soft_warnings"].append({
            "kind": kind,
            "category": category.__name__,
            "message": text[:400],
            "signature": signature(category.__name__, text),
        })
    if _AS_ERRORS:
        raise message if isinstance(message, Warning) else category(text)


# Installed at conftest import, before pytest imports test_solution.py and through it solution.py.
warnings.simplefilter("always")
warnings.showwarning = _showwarning


def pytest_configure(config):
    module = os.environ.get("VARAG_LIBRARY")
    expect = os.environ.get("VARAG_EXPECT_VERSION")
    if not module or not expect:
        return
    try:
        lib = importlib.import_module(module)
    except Exception as exc:  # noqa: BLE001
        _infra(f"import {module} failed: {type(exc).__name__}: {exc}"[:300])
        return
    actual = str(getattr(lib, "__version__", ""))
    STATE["stamp_version"] = actual
    if actual != expect:
        _infra(f"version stamp {actual} != expected {expect}")
    if warnings.showwarning is not _showwarning:
        _infra("warning hook was replaced; run pytest with -p no:warnings")


def pytest_collection_finish(session):
    STATE["collected"] = len(session.items)


def pytest_exception_interact(node, call, report):
    """Called for test failures and collection errors alike."""
    if call.excinfo is None or len(STATE["failures"]) >= 10:
        return
    exc = call.excinfo
    message = str(exc.value).strip().splitlines()
    STATE["failures"].append({
        "nodeid": getattr(node, "nodeid", ""),
        "when": call.when,
        "exc_type": exc.type.__name__,
        "message": (message[0] if message else "")[:500],
    })


def pytest_sessionfinish(session, exitstatus):
    STATE["exit_status"] = int(exitstatus)
    _write()
