"""conftest.py injected by the harness into every execution directory. Stdlib + pytest hooks.

Environment:
  VARAG_LIBRARY         module to import for the version stamp (pandas, numpy, pydantic)
  VARAG_EXPECT_VERSION  the version the harness believes is installed
  VARAG_RESULT_PATH     where to write the JSON result record

Check 4 of the handoff's verification table: the stamp asserts the library version equals
VARAG_EXPECT_VERSION and writes it into the result; a mismatch is infra_error, never fail.
Also counts DeprecationWarning and FutureWarning attributed to solution.py (handoff L9) and
records the first failures' exception types.
"""

import importlib
import json
import os

import pytest

STATE = {
    "status": None,
    "infra_reason": None,
    "stamp_version": None,
    "collected": 0,
    "exit_status": None,
    "warning_counts": {"DeprecationWarning": 0, "FutureWarning": 0, "other": 0},
    "warnings": [],
    "failures": [],
}


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


def pytest_collection_finish(session):
    STATE["collected"] = len(session.items)


def pytest_warning_recorded(warning_message, when, nodeid, location):
    filename = str(getattr(warning_message, "filename", "") or "").replace("\\", "/")
    if not filename.endswith("/solution.py") and filename != "solution.py":
        return
    category = warning_message.category.__name__ if warning_message.category else "other"
    key = category if category in STATE["warning_counts"] else None
    if key is None:
        try:
            if issubclass(warning_message.category, DeprecationWarning):
                key = "DeprecationWarning"
            elif issubclass(warning_message.category, FutureWarning):
                key = "FutureWarning"
        except TypeError:
            key = None
    STATE["warning_counts"][key or "other"] += 1
    if len(STATE["warnings"]) < 20:
        STATE["warnings"].append(f"{category}: {warning_message.message}"[:300])


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
