"""Preflight pieces that need no GPU: the manifest comparison and the report format."""

import copy

from varag.preflight import Check, format_checks, manifest_drift

ENTRY = {"lock_sha256": "abc", "library": "numpy", "side": "old", "library_version": "1.26.4", "expected_version": "1.26.4",
         "distributions": {"numpy": "1.26.4"}, "python_version": "3.11.15", "interpreter": "/home/a/envs/numpy_old/.venv/bin/python",
         "platform": "Linux-6.6", "created_at": "2026-10-15"}


def test_machine_specific_fields_do_not_count_as_drift():
    here = {**ENTRY, "python_version": "3.11.17", "interpreter": "/home/b/x/python", "platform": "Linux-6.18", "created_at": "2026-10-19"}
    assert manifest_drift({"numpy_old": here}, {"numpy_old": ENTRY}) == []


def test_lock_versions_and_minor_python_count_as_drift():
    changed = copy.deepcopy(ENTRY)
    changed["lock_sha256"] = "def"
    changed["distributions"]["numpy"] = "1.26.3"
    changed["python_version"] = "3.12.1"
    drift = manifest_drift({"numpy_old": changed}, {"numpy_old": ENTRY})
    assert any("lock_sha256" in d for d in drift) and any("distributions" in d for d in drift) and any("minor" in d for d in drift)
    assert manifest_drift({}, {"numpy_old": ENTRY}) == ["numpy_old: missing here"]


def test_format_lists_fixes_for_failures_only():
    text = format_checks([Check("gpu", "ok", "fine", "never shown"), Check("disk", "fail", "3 GB free", "free space")])
    assert "never shown" not in text and "fix: free space" in text and "FAILED: disk" in text
