import copy

import pytest

from varag.envs.verify import Mismatch, compare

ENTRY = {
    "library": "numpy",
    "side": "old",
    "expected_version": "1.26.4",
    "library_version": "1.26.4",
    "python_version": "3.11.17",
    "interpreter": "X:/envs/numpy_old/.venv/Scripts/python.exe",
    "distributions": {"numpy": "1.26.4", "pytest": "9.1.1"},
    "lock_sha256": "a" * 64,
}
PROBE = {
    "library_version": "1.26.4",
    "python_version": "3.11.17",
    "interpreter": "X:/envs/numpy_old/.venv/Scripts/python.exe",
    "distributions": {"numpy": "1.26.4", "pytest": "9.1.1"},
    "canaries": {
        "numpy.trapz": {"present": True, "detail": "function"},
        "numpy.trapezoid": {"present": False, "detail": "AttributeError"},
    },
}
CANARIES = {"numpy.trapz": True, "numpy.trapezoid": False}


def fields(mismatches: list[Mismatch]) -> set[str]:
    return {m.field for m in mismatches}


def test_clean_probe_has_no_mismatch():
    assert compare("numpy_old", ENTRY, PROBE, "a" * 64, CANARIES) == []


def test_tampered_version_and_lock_are_reported():
    probed = copy.deepcopy(PROBE)
    probed["library_version"] = "1.26.3"
    found = compare("numpy_old", ENTRY, probed, "b" * 64, CANARIES)
    assert "library_version" in fields(found)
    assert "lock_sha256" in fields(found)


def test_extra_distribution_is_reported():
    probed = copy.deepcopy(PROBE)
    probed["distributions"]["pyarrow"] = "20.0.0"
    found = compare("numpy_old", ENTRY, probed, "a" * 64, CANARIES)
    assert fields(found) == {"distributions"}
    assert found[0].actual == [("pyarrow", "20.0.0")]


def test_wildcard_pin_accepts_patch_release():
    entry = dict(ENTRY, expected_version="2.4.*", library_version="2.4.6")
    probed = dict(PROBE, library_version="2.4.6", canaries={})
    assert compare("numpy_new", entry, probed, "a" * 64, {}) == []
    probed["library_version"] = "2.5.0"
    entry["library_version"] = "2.5.0"
    assert "library_version (vs configs/libraries.yaml)" in fields(compare("numpy_new", entry, probed, "a" * 64, {}))


def test_canary_disagreement_is_reported():
    probed = copy.deepcopy(PROBE)
    probed["canaries"]["numpy.trapezoid"]["present"] = True
    found = compare("numpy_old", ENTRY, probed, "a" * 64, CANARIES)
    assert fields(found) == {"canary numpy.trapezoid"}


@pytest.mark.envs
def test_all_environments_verify_green():
    from varag.envs.verify import verify_all

    problems = {name: [str(m) for m in found] for name, found in verify_all().items() if found}
    assert problems == {}
