"""Concept schema (handoff, "Benchmark"): one programming need with two version-exclusive
reference solutions, or a no-conflict control with one portable reference.

Layout of one concept directory:
  concept.yaml  ref_old.py  ref_new.py  [ref_portable.py]  test_solution.py  clues/  [validation.json]

A ``one_directional`` concept (user decision 2026-10-15) has no ref_new: its new-side form also
exists in the old version, so ref_portable (passes both, no deprecation warning) is the new
target's reference, and only ref_old is version-specific (passes old, fails new). Its instances
target the new version only. Class caps (configs/experiment.yaml, `composition.caps`) limit
one_directional to a third of the whole benchmark and behavior to 15% of each library except
pandas and NumPy.
"""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path

import yaml

from varag.config import SIDES, load_experiment, project_root

EXCLUSIVITY = ("removal", "deprecation", "behavior", "one_directional")
CHANGE_TYPES = ("symbol_rename", "symbol_removed", "moved_import", "param_rename", "param_removed", "default_change", "behavior")
PORTABLE = ("none", "guard_only", "plain")
SPLITS = ("dev", "test")
CLUE_TYPES = ("pin", "code", "error")
OVERLAPS = ("on_target", "off_target")
KINDS = ("concept", "no_conflict")

# A version number named in prose: "pandas 1.5", "numpy>=2", "version 2", "v2", "1.5.3".
VERSION_MENTION = re.compile(
    r"(?i)\b(?:pandas|numpy|pydantic|version)\s*(?:==|>=|<=|~=|<|>)?\s*v?\d+(?:\.\d+)*"
    r"|\b\d+\.\d+\.\d+\b"
    r"|\b[vV]\d+(?:\.\d+)*\b"
)


class ConceptError(ValueError):
    pass


@dataclass
class Clue:
    side: str
    type: str
    file: str
    overlap: str
    text: str


@dataclass
class Concept:
    id: str
    library: str
    kind: str
    split: str
    query: str
    entry_point: str
    directory: Path
    exclusivity: str | None = None
    change_type: str | None = None
    warnings_as_errors: bool = False
    portable_alternative: str = "none"
    gold: dict = field(default_factory=dict)
    clues: dict[str, list[Clue]] = field(default_factory=dict)
    control_eligible: bool = False

    @property
    def is_control(self) -> bool:
        return self.kind == "no_conflict"

    @property
    def test_path(self) -> Path:
        return self.directory / "test_solution.py"

    @property
    def one_directional(self) -> bool:
        return self.exclusivity == "one_directional"

    @property
    def target_sides(self) -> tuple[str, ...]:
        """The versions instances target: none for a control, new only for a one_directional concept."""
        if self.is_control:
            return ()
        return ("new",) if self.one_directional else SIDES

    def native_ref(self, side: str) -> str:
        """The reference written for one environment: ``old``, ``new`` or ``portable``."""
        if self.is_control or (self.one_directional and side == "new"):
            return "portable"
        return side

    def ref_path(self, side: str) -> Path:
        return self.directory / f"ref_{side}.py"

    def reference(self, side: str) -> str:
        return self.ref_path(side).read_text(encoding="utf-8")

    @property
    def has_portable(self) -> bool:
        return self.is_control or self.portable_alternative != "none"

    def clue(self, side: str, clue_type: str) -> Clue | None:
        for c in self.clues.get(side, []):
            if c.type == clue_type:
                return c
        return None


def tasks_dir() -> Path:
    return project_root() / "data" / "tasks"


def manifest_path() -> Path:
    return tasks_dir() / "MANIFEST.json"


def find_concept_dirs(library: str | None = None) -> list[Path]:
    root = tasks_dir()
    if not root.exists():
        return []
    dirs = []
    for lib_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        if library and lib_dir.name != library:
            continue
        dirs += sorted(p for p in lib_dir.iterdir() if (p / "concept.yaml").exists())
    return dirs


def find_concept_dir(concept_id: str) -> Path:
    for d in find_concept_dirs():
        if d.name == concept_id:
            return d
    raise ConceptError(f"no concept directory named {concept_id!r} under {tasks_dir()}")


def lint_version_mentions(text: str) -> list[str]:
    return [m.group(0) for m in VERSION_MENTION.finditer(text)]


def error_clue_snippet(text: str) -> str:
    """The user-written part of an error clue: everything before the captured traceback."""
    idx = text.find("Traceback (most recent call last)")
    return text if idx < 0 else text[:idx]


def concept_sha256(directory: Path) -> str:
    """sha256 over every file except validation.json, by relative path, with LF line endings."""
    h = hashlib.sha256()
    for path in sorted(p for p in directory.rglob("*") if p.is_file() and p.name != "validation.json"):
        h.update(path.relative_to(directory).as_posix().encode())
        h.update(b"\0")
        h.update(path.read_bytes().replace(b"\r\n", b"\n"))
        h.update(b"\0")
    return h.hexdigest()


def _check(cond: bool, problems: list[str], message: str) -> None:
    if not cond:
        problems.append(message)


def load_concept(directory: Path) -> Concept:
    directory = Path(directory)
    raw = yaml.safe_load((directory / "concept.yaml").read_text(encoding="utf-8")) or {}
    problems: list[str] = []
    kind = raw.get("kind", "concept")
    _check(kind in KINDS, problems, f"kind must be one of {KINDS}")
    for key in ("id", "library", "split", "query", "entry_point"):
        _check(bool(raw.get(key)), problems, f"missing field {key}")
    _check(raw.get("id") == directory.name, problems, f"id {raw.get('id')!r} must equal the directory name {directory.name!r}")
    _check(raw.get("split") in SPLITS, problems, f"split must be one of {SPLITS}")
    query = str(raw.get("query", "")).strip()
    entry = str(raw.get("entry_point", ""))
    _check(entry in query, problems, f"query must name the entry point {entry!r}")
    mentions = lint_version_mentions(query)
    _check(not mentions, problems, f"query names a version: {mentions}")
    _check((directory / "test_solution.py").exists(), problems, "test_solution.py missing")

    clues: dict[str, list[Clue]] = {}
    if kind == "no_conflict":
        _check((directory / "ref_portable.py").exists(), problems, "control needs ref_portable.py")
        _check(bool(raw.get("gold", {}).get("shared")), problems, "control needs gold.shared symbols")
    else:
        _check(raw.get("exclusivity") in EXCLUSIVITY, problems, f"exclusivity must be one of {EXCLUSIVITY}")
        _check(raw.get("change_type") in CHANGE_TYPES, problems, f"change_type must be one of {CHANGE_TYPES}")
        _check(raw.get("portable_alternative", "none") in PORTABLE, problems, f"portable_alternative must be one of {PORTABLE}")
        wae = bool(raw.get("warnings_as_errors", False))
        _check(not wae or raw.get("exclusivity") == "deprecation", problems, "warnings_as_errors is true only for exclusivity: deprecation")
        one_directional = raw.get("exclusivity") == "one_directional"
        for side in SIDES:
            if side == "new" and one_directional:
                _check(not (directory / "ref_new.py").exists(), problems, "one_directional concepts have no ref_new.py")
                _check(raw.get("portable_alternative") == "plain", problems, "one_directional needs portable_alternative: plain")
            else:
                _check((directory / f"ref_{side}.py").exists(), problems, f"ref_{side}.py missing")
            _check(bool(raw.get("gold", {}).get(side)), problems, f"gold.{side} missing")
        if raw.get("portable_alternative", "none") != "none":
            _check((directory / "ref_portable.py").exists(), problems, "portable_alternative set but ref_portable.py missing")
        for side in SIDES:
            for c in raw.get("clues", {}).get(side, []) or []:
                _check(c.get("type") in CLUE_TYPES, problems, f"clue type must be one of {CLUE_TYPES}: {c}")
                _check(c.get("overlap") in OVERLAPS, problems, f"clue overlap must be one of {OVERLAPS}: {c}")
                path = directory / str(c.get("file", ""))
                if not path.exists():
                    problems.append(f"clue file missing: {c.get('file')}")
                    continue
                text = path.read_text(encoding="utf-8")
                if c.get("type") == "code":
                    hits = lint_version_mentions(text)
                    _check(not hits, problems, f"code clue {c.get('file')} names a version: {hits}")
                elif c.get("type") == "error":
                    hits = lint_version_mentions(error_clue_snippet(text))
                    _check(not hits, problems, f"error clue snippet {c.get('file')} names a version: {hits}")
                clues.setdefault(side, []).append(Clue(side, c["type"], c["file"], c["overlap"], text))
    if problems:
        raise ConceptError(f"{directory.name}: " + "; ".join(problems))

    return Concept(
        id=raw["id"],
        library=raw["library"],
        kind=kind,
        split=raw["split"],
        query=query,
        entry_point=entry,
        directory=directory,
        exclusivity=raw.get("exclusivity"),
        change_type=raw.get("change_type"),
        warnings_as_errors=bool(raw.get("warnings_as_errors", False)),
        portable_alternative=raw.get("portable_alternative", "none") if kind == "concept" else "plain",
        gold=raw.get("gold", {}),
        clues=clues,
        control_eligible=bool(raw.get("control_eligible", False)),
    )


def class_counts(concepts: list[Concept]) -> dict[str, dict[str, int]]:
    """library -> exclusivity class -> number of concepts (controls excluded)."""
    out: dict[str, dict[str, int]] = {}
    for c in concepts:
        if not c.is_control:
            slot = out.setdefault(c.library, {})
            slot[c.exclusivity] = slot.get(c.exclusivity, 0) + 1
    return {lib: dict(sorted(v.items())) for lib, v in sorted(out.items())}


def class_caps() -> dict[str, dict]:
    caps = load_experiment().get("composition", {}).get("caps", {})
    return {cls: {**cap, "share": Fraction(str(cap["share"]))} for cls, cap in caps.items()}


def class_cap_problems(concepts: list[Concept], caps: dict[str, dict] | None = None) -> list[str]:
    """Classes over their share of the concepts in scope: the whole benchmark, or each library not
    exempted (controls excluded)."""
    caps = class_caps() if caps is None else caps
    counts = class_counts(concepts)
    problems = []
    for cls, cap in caps.items():
        if cap.get("scope") == "benchmark":
            scopes = {"benchmark": sum((Counter(c) for c in counts.values()), Counter())}
        else:
            scopes = {lib: c for lib, c in counts.items() if lib not in cap.get("exempt", [])}
        for scope, counted in scopes.items():
            total = sum(counted.values())
            if counted.get(cls, 0) > total * cap["share"]:
                problems.append(f"{scope}: {counted[cls]} of {total} concepts are {cls}; the cap is {cap['share']}")
    return problems


def load_concepts(library: str | None = None, split: str | None = None) -> list[Concept]:
    out = []
    for d in find_concept_dirs(library):
        c = load_concept(d)
        if split in (None, "all") or c.split == split:
            out.append(c)
    return out
