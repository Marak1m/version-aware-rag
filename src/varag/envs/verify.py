"""``varag env verify``: re-probe every environment and diff it against the manifest.

Checks 2 and 3 of the handoff's verification table. Later commands call
``require_verified`` before they start, so no artifact is ever derived from an
environment whose version was not checked by execution.
"""

from __future__ import annotations

from dataclasses import dataclass

from packaging.specifiers import SpecifierSet
from packaging.version import Version

from varag.config import env_names, env_spec, load_canaries, load_libraries, sha256_file
from varag.envs.build import probe, read_manifest
from varag.envs.runner import env_dir, env_python


@dataclass(frozen=True)
class Mismatch:
    env: str
    field: str
    expected: object
    actual: object

    def __str__(self) -> str:
        return f"{self.env}: {self.field} expected {self.expected!r}, got {self.actual!r}"


def expected_canaries(library: str, side: str) -> dict[str, bool]:
    entry = load_canaries().get(library, {}).get(side, {})
    expected = {path: True for path in entry.get("present", [])}
    expected.update({path: False for path in entry.get("absent", [])})
    return expected


def compare(name: str, entry: dict, probed: dict, lock_sha256: str, canaries: dict[str, bool],
            expected_python: str | None = None) -> list[Mismatch]:
    """Pure comparison of a manifest entry with a fresh probe. Unit-tested without environments."""
    out: list[Mismatch] = []
    if expected_python and not probed["python_version"].startswith(f"{expected_python}."):
        out.append(Mismatch(name, "python_version (vs configs/libraries.yaml)", f"{expected_python}.x", probed["python_version"]))
    spec_version = entry["expected_version"]
    specifier = SpecifierSet(f"=={spec_version}")
    if not specifier.contains(Version(probed["library_version"]), prereleases=True):
        out.append(Mismatch(name, "library_version (vs configs/libraries.yaml)", spec_version, probed["library_version"]))
    for field in ("library_version", "python_version", "interpreter"):
        if probed[field] != entry[field]:
            out.append(Mismatch(name, field, entry[field], probed[field]))
    if probed["distributions"] != entry["distributions"]:
        expected_set, actual_set = set(entry["distributions"].items()), set(probed["distributions"].items())
        out.append(Mismatch(name, "distributions", sorted(expected_set - actual_set), sorted(actual_set - expected_set)))
    if lock_sha256 != entry["lock_sha256"]:
        out.append(Mismatch(name, "lock_sha256", entry["lock_sha256"], lock_sha256))
    for path, want in canaries.items():
        got = probed["canaries"].get(path)
        if got is None:
            out.append(Mismatch(name, f"canary {path}", want, "not probed"))
        elif got["present"] != want:
            out.append(Mismatch(name, f"canary {path}", "present" if want else "absent", got["detail"]))
    return out


def verify_env(name: str) -> list[Mismatch]:
    manifest = read_manifest()
    if name not in manifest:
        return [Mismatch(name, "manifest entry", "present", "missing")]
    if not env_python(name).exists():
        return [Mismatch(name, "interpreter", str(env_python(name)), "missing")]
    lock = env_dir(name) / "requirements.lock"
    if not lock.exists():
        return [Mismatch(name, "requirements.lock", "present", "missing")]
    spec = env_spec(name)
    probed = probe(name)
    return compare(name, manifest[name], probed, sha256_file(lock), expected_canaries(spec["library"], spec["side"]),
                   expected_python=str(load_libraries()["python"]))


def verify_all(names: list[str] | None = None) -> dict[str, list[Mismatch]]:
    return {name: verify_env(name) for name in (names or env_names())}


def require_verified(names: list[str] | None = None) -> None:
    """Refuse to start when any named environment disagrees with its manifest."""
    problems = [str(m) for found in verify_all(names).values() for m in found]
    if problems:
        raise SystemExit("environment verification failed:\n  " + "\n  ".join(problems))
