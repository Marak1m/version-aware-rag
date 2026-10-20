"""Published migration rule sets under data/rules/, and the audit rules derived from them.

- numpy:    ruff's NPY201 table (fetched from GitHub at a pinned commit) and
            numpy/_expired_attrs_2_0.py (dumped from the installed new-side package).
- pydantic: pydantic/_migration.py (dumped from the installed new-side package) and the
            bump-pydantic BP001 to BP010 rules, hand-transcribed with their source URL.
- pandas:   removals hand-mined from the 2.0, 2.x and 3.0 release notes. No machine-readable
            set exists, so the audit reports pandas recall without gating on it.

Every rule names the inventory symbol it expects to find, the buckets it may land in, and the
replacement (old symbol to new symbol) the blend guard's repair message will use.
"""

from __future__ import annotations

import json
import re
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from varag.config import load_libraries, project_root

RUFF_FILE = "crates/ruff_linter/src/rules/numpy/rules/numpy_2_0_deprecation.rs"
GONE = ("old_only",)
GONE_OR_DEPRECATED = ("old_only", "deprecated_in_new")
KEPT = ("shared_same", "shared_changed", "shared_unknown", "deprecated_in_new")


@dataclass(frozen=True)
class Rule:
    library: str
    symbol: str
    expected: tuple[str, ...]
    source: str
    replacement: str | None = None
    note: str = ""
    extra: dict = field(default_factory=dict, compare=False, hash=False)


def rules_dir(library: str) -> Path:
    return project_root() / "data" / "rules" / library


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


# --- ruff NPY201 -------------------------------------------------------------

_ARM = re.compile(
    r"\[((?:\"[^\"]+\"\s*,?\s*)+)\]\s*=>\s*Replacement\s*\{\s*existing:\s*\"([^\"]+)\"\s*,\s*details:\s*Details::(\w+)\s*\{(.*?)\}\s*,?\s*\}",
    re.S,
)
_STR = r"\"((?:[^\"\\]|\\.)*)\""


def parse_npy201(rust_source: str) -> list[dict]:
    entries = []
    for segments, existing, kind, body in _ARM.findall(rust_source):
        path = ".".join(re.findall(r"\"([^\"]+)\"", segments))
        entry = {"path": path, "existing": existing, "kind": kind, "replacement": None, "backwards_compatible": None, "guideline": None}
        if kind == "AutoImport":
            mod = re.search(r"path:\s*" + _STR, body)
            name = re.search(r"name:\s*" + _STR, body)
            compat = re.search(r"Compatibility::(\w+)", body)
            entry["replacement"] = f"{mod.group(1)}.{name.group(1)}" if mod and name else None
            entry["backwards_compatible"] = bool(compat and compat.group(1) == "BackwardsCompatible")
        elif kind == "AutoPurePython":
            expr = re.search(r"python_expr:\s*" + _STR, body)
            entry["replacement"] = expr.group(1) if expr else None
            entry["backwards_compatible"] = True
        else:
            guide = re.search(r"guideline:\s*Some\(\s*" + _STR, body, re.S)
            entry["guideline"] = guide.group(1) if guide else None
        entries.append(entry)
    return entries


def fetch_ruff_npy201(commit: str | None = None) -> dict:
    """One-off dev step: download ruff's NPY201 source at a pinned commit and store raw + parsed."""
    if commit is None:
        api = json.load(urllib.request.urlopen("https://api.github.com/repos/astral-sh/ruff/commits/main"))
        commit = api["sha"]
    url = f"https://raw.githubusercontent.com/astral-sh/ruff/{commit}/{RUFF_FILE}"
    source = urllib.request.urlopen(url).read().decode("utf-8")
    directory = rules_dir("numpy")
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "numpy_2_0_deprecation.rs").write_text(source, encoding="utf-8", newline="\n")
    parsed = {
        "source": "ruff NPY201",
        "commit": commit,
        "url": url,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "entries": parse_npy201(source),
    }
    _write_json(directory / "npy201.json", parsed)
    return parsed


# --- rule loading --------------------------------------------------------------


def _inventory_roots(library: str) -> set[str]:
    cfg = load_libraries()["libraries"][library]
    roots = {r["public"] for r in cfg["inventory_roots"]}
    if cfg.get("config_keys"):
        roots.add(cfg["config_keys"]["public"])
    return roots


def owner_of(symbol: str) -> str:
    base = symbol.split("(")[0]
    return base.rpartition(".")[0]


def applies(library: str, symbol: str) -> bool:
    """A rule is auditable only when its symbol sits under an inventory root."""
    return owner_of(symbol) in _inventory_roots(library)


def _numpy_rules() -> list[Rule]:
    rules: list[Rule] = []
    expired = _read_json(rules_dir("numpy") / "expired_attrs_2_0.json").get("expired_attributes", {})
    for name, message in sorted(expired.items()):
        hint = re.search(r"`(?:np\.|numpy\.)?([A-Za-z_][\w.]*)`", message)
        replacement = f"numpy.{hint.group(1)}" if hint else None
        rules.append(Rule("numpy", f"numpy.{name}", GONE, "numpy._expired_attrs_2_0", replacement, message))
    for e in _read_json(rules_dir("numpy") / "npy201.json").get("entries", []):
        rules.append(Rule("numpy", e["path"], GONE_OR_DEPRECATED, "ruff NPY201", e.get("replacement"), e.get("guideline") or "", extra=e))
        if e.get("backwards_compatible") and e.get("replacement") and e["kind"] == "AutoImport":
            rules.append(Rule("numpy", e["replacement"], KEPT, "ruff NPY201 (backwards-compatible replacement)", None, f"replacement for {e['path']}"))
    for e in _read_json(rules_dir("numpy") / "release_notes.json").get("rules", []):
        rules.append(Rule("numpy", e["symbol"], tuple(e["expected"]), f"numpy release notes {e['note']}", e.get("replacement"), e.get("url", "")))
    return rules


MIGRATION_TABLE_DEFAULTS = {
    "REMOVED_IN_V2": GONE,
    "MOVED_IN_V2": GONE_OR_DEPRECATED,
    "DEPRECATED_MOVED_IN_V2": ("deprecated_in_new",),
}


def _migration_expectation(table: str, behaviour: dict | None) -> tuple[str, ...]:
    """A migration-served name that raises PydanticImportError on V2 is gone (old_only); one that
    resolves with a deprecation warning is deprecated_in_new. Without probe data, the table decides."""
    if behaviour:
        if behaviour.get("outcome") == "raises" and behaviour.get("type") == "PydanticImportError":
            return GONE
        if behaviour.get("outcome") == "resolves" and behaviour.get("warnings"):
            return ("deprecated_in_new",)
    return MIGRATION_TABLE_DEFAULTS[table]


def _field_kwarg_rules(data: dict) -> list[Rule]:
    """Rules mined from pydantic's own Field() handling of V1 keywords, classified by execution:
    removed keywords raise PydanticUserError (old_only); deprecated ones are accepted through
    **extra with a PydanticDeprecatedSince20 warning (deprecated_in_new)."""
    rules: list[Rule] = []
    params = set(data.get("field_params", []))
    for keyword, info in sorted(data.get("keywords", {}).items()):
        symbol = f"pydantic.Field({keyword})"
        hint = re.search(r"use `(\w+)` instead", info.get("message", ""))
        replacement = f"pydantic.Field({hint.group(1)})" if hint and hint.group(1) in params else None
        if info.get("handling") == "removed":
            rules.append(Rule("pydantic", symbol, GONE, "pydantic Field removed-kwargs", replacement, info.get("message", ""), extra=dict(info)))
        else:
            rules.append(Rule("pydantic", symbol, ("deprecated_in_new",), "pydantic Field deprecated kwargs", replacement, info.get("message", ""), extra=dict(info)))
    return rules


def _pydantic_rules() -> list[Rule]:
    rules: list[Rule] = []
    migration = _read_json(rules_dir("pydantic") / "migration.json")
    served = migration.get("served_behaviour", {})
    for table in MIGRATION_TABLE_DEFAULTS:
        value = migration.get(table, {})
        items = value.items() if isinstance(value, dict) else [(v, None) for v in value]
        for key, target in sorted(items):
            symbol = key.replace(":", ".")
            replacement = target.replace(":", ".") if isinstance(target, str) else None
            behaviour = served.get(key)
            extra = {"behaviour": {**behaviour, "table": table}} if behaviour else {}
            rules.append(Rule("pydantic", symbol, _migration_expectation(table, behaviour), f"pydantic._migration.{table}", replacement, extra=extra))
    rules += _field_kwarg_rules(_read_json(rules_dir("pydantic") / "field_v1_kwargs.json"))
    for e in _read_json(rules_dir("pydantic") / "bump_pydantic.json").get("rules", []):
        rules.append(Rule("pydantic", e["symbol"], tuple(e["expected"]), f"bump-pydantic {e['id']}", e.get("replacement"), e.get("note", "")))
    return rules


def _pandas_rules() -> list[Rule]:
    rules: list[Rule] = []
    for e in _read_json(rules_dir("pandas") / "removals.json").get("rules", []):
        rules.append(Rule("pandas", e["symbol"], tuple(e["expected"]), f"pandas release notes {e['note']}", e.get("replacement"), e.get("url", "")))
    return rules


def load_rules(library: str) -> list[Rule]:
    loader = {"numpy": _numpy_rules, "pydantic": _pydantic_rules, "pandas": _pandas_rules}[library]
    seen: dict[tuple[str, str], Rule] = {}
    for rule in loader():
        seen.setdefault((rule.symbol, rule.source), rule)
    return list(seen.values())


def deprecated_symbols(library: str) -> set[str]:
    """Symbols a rule set lists as deprecated (or gone) on the new side. The diff applies
    this only to symbols present on both sides, so removed names are unaffected."""
    return {r.symbol for r in load_rules(library) if "deprecated_in_new" in r.expected and "shared_same" not in r.expected}


def deprecated_kept_symbols(library: str) -> set[str]:
    """Symbols a rule set says still work on the new side with a deprecation warning. For a
    keyword the new signature no longer declares but absorbs through **kwargs, this is what
    moves it from old_only to deprecated_in_new."""
    return {r.symbol for r in load_rules(library) if r.expected == ("deprecated_in_new",)}


def rule_listed_symbols(library: str) -> dict[str, str]:
    """Every symbol a rule set names, as the old symbol or as a replacement: the corroboration
    source for an `uncertain` keyword usage."""
    out: dict[str, str] = {}
    for r in load_rules(library):
        out.setdefault(r.symbol, r.source)
        if r.replacement:
            out.setdefault(r.replacement, f"{r.source} (replacement)")
    return dict(sorted(out.items()))


def replacements(library: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for r in load_rules(library):
        # A "replacement" under a ``.deprecated.`` module is where the old API was moved to keep it
        # running (pydantic's migration table sends validate_arguments to
        # pydantic.deprecated.decorator), not what replaces it (2026-10-20).
        if r.replacement and ".deprecated." in r.replacement:
            continue
        if r.replacement and r.symbol != r.replacement and "old_only" in r.expected or (r.replacement and r.expected == ("deprecated_in_new",)):
            out.setdefault(r.symbol, {"new": r.replacement, "source": r.source})
    return dict(sorted(out.items()))


def value_rules(library: str, confirmed_only: bool = True) -> list[dict]:
    """Argument values valid on one side only, as (callable, parameter, value, side) records mined
    from the release notes (data/rules/<library>/value_rules.json). By default only the records
    `varag bench probe` confirmed in the environments; the signal extractor reads those."""
    rules = _read_json(rules_dir(library) / "value_rules.json").get("rules", [])
    return [r for r in rules if not confirmed_only or (r.get("probe") or {}).get("confirmed")]


def behaviour_rules(library: str, confirmed_only: bool = True) -> list[dict]:
    """Behaviour changes from the release notes (data/rules/<library>/behaviour.json): the old and
    new gold symbols of a change the inventory cannot see. They link gold pairs in validation step 7
    and the doc-conflict test only, never signals (user decision 2026-10-18). Confirmed means the
    candidate's probe (data/candidates/probes.json) found a direction."""
    rules = _read_json(rules_dir(library) / "behaviour.json").get("rules", [])
    if not confirmed_only:
        return rules
    probes = _read_json(rules_dir(library).parent.parent / "candidates" / "probes.json")
    verdicts = {c["id"]: c.get("verdict") for c in probes.get("candidates", [])}
    return [r for r in rules if verdicts.get(r["probe_id"]) in ("two_directional", "one_directional")]


def write_replacements(library: str) -> Path:
    path = rules_dir(library) / "replacements.json"
    _write_json(path, {"library": library, "replacements": replacements(library)})
    return path


if __name__ == "__main__":  # python -m varag.inventory.rules  -> refetch ruff's table
    parsed = fetch_ruff_npy201()
    print(f"fetched {len(parsed['entries'])} NPY201 entries at {parsed['commit'][:12]}")
