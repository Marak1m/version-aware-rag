"""``varag bench probe``: run a minimal old-form and new-form snippet for every candidate in both
environments of its library, and classify it two_directional, one_directional or
not_discriminative (user decision 2026-10-15).

Candidates, and where their snippets come from:
- symbol pairs (the rule-set replacements `bench candidates` lists): an attribute access of each
  symbol through its inventory root, unless data/candidates/snippets.json has a hand-written pair
  (needed where the change shows only when the symbol is called);
- keyword pairs: hand-written snippets in snippets.json, or ``unprobed``;
- value rules (data/rules/<library>/value_rules.json): the call template for (callable, parameter)
  in snippets.json with the value substituted. Each record is ``confirmed`` when the value works
  on its side and not on the other; a record with a replacement is also probed as a pair;
- behaviour and value candidates from the release notes (data/candidates/release_notes.json):
  their own snippets.

A form breaks on the other side when it errors, times out, or raises a soft warning there (a
deprecation, future or migration-message warning attributed to the snippet). A pair whose old
form breaks on the new side only by a warning is a ``deprecation``-class concept, which runs
with warnings_as_errors. A warning on a form's own side is recorded, not counted as a break.

Probes are snippets, not concepts. A concept built on a probed candidate still has to pass the
validation matrix.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from varag.bench.candidates import keyword_pairs, symbol_pairs
from varag.config import SIDES, env_name, load_libraries, project_root
from varag.corpus.examples import CheckResult, run_checks
from varag.envs.build import read_manifest
from varag.inventory.rules import rules_dir

VERDICTS = ("two_directional", "one_directional", "not_discriminative")


def candidates_dir() -> Path:
    return project_root() / "data" / "candidates"


def _load(name: str) -> dict:
    path = candidates_dir() / name
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


# --- snippets -------------------------------------------------------------------------------


def access_snippet(library: str, symbol: str) -> str | None:
    """Import the symbol's inventory root and access the rest of the path: the minimal probe for a
    symbol that is absent (AttributeError) or warns on access on one side."""
    spec = load_libraries()["libraries"][library]
    config_public = (spec.get("config_keys") or {}).get("public")
    if config_public and symbol.startswith(config_public + "."):
        return None                                   # config keys are not attributes of the package
    roots = spec["inventory_roots"]
    matching = [r for r in roots if symbol == r["public"] or symbol.startswith(r["public"] + ".")]
    if not matching:
        return None
    root = max(matching, key=lambda r: len(r["public"]))
    module, _, attr = root["import"].partition(":")
    if attr:                                          # a class root: pandas:DataFrame, ...accessors:DatetimeProperties
        rest = symbol[len(root["public"]):].lstrip(".")
        return f"from {module} import {attr} as _root\n_ = _root" + (f".{rest}" if rest else "")
    # A module root: import the package and walk attributes, as user code does (np.char.add). In
    # NumPy 1.26 `numpy.char` is an attribute, not an importable submodule.
    package = spec["module"]
    rest = symbol[len(package):].lstrip(".")
    return f"import {package} as _root\n_ = _root" + (f".{rest}" if rest else "")


def value_call(templates: dict[str, str], rule: dict) -> str | None:
    template = templates.get(f"{rule['callable']}|{rule['parameter']}")
    return template.replace("VALUE", repr(rule["value"])) if template else None


# --- classification ---------------------------------------------------------------------------


def cell(result: CheckResult) -> tuple[str, str]:
    """(status, detail): ok | warns | error | timeout | network."""
    if result.status != "ok":
        detail = (result.error or "").strip().splitlines()[-1][:160] if result.error else ""
        return result.status, detail
    if result.soft_warnings:
        return "warns", str(result.soft_warnings[0].get("signature", ""))[:160]
    return "ok", ""


def verdict(outcome: dict[str, str]) -> tuple[str, str]:
    """``outcome`` maps old@old, old@new, new@new, new@old to a status. Returns (verdict, reason)."""
    if outcome["old@old"] not in ("ok", "warns") or outcome["new@new"] not in ("ok", "warns"):
        return "not_discriminative", "a form fails on its own side"
    old_breaks, new_breaks = outcome["old@new"] != "ok", outcome["new@old"] != "ok"
    if old_breaks and new_breaks:
        return "two_directional", f"old form breaks on new by {outcome['old@new']}; new form breaks on old by {outcome['new@old']}"
    if old_breaks:
        return "one_directional", f"old form breaks on new by {outcome['old@new']}; new form runs on both"
    if new_breaks:
        return "not_discriminative", "reverse: only the new form is exclusive"
    return "not_discriminative", "both forms run on both sides"


def concept_class(kind: str, found: str, outcome: dict[str, str]) -> str | None:
    """The exclusivity class a concept on this candidate would take."""
    if found == "one_directional":
        return "one_directional"
    if found != "two_directional":
        return None
    if kind == "behaviour":
        return "behavior"
    return "deprecation" if outcome["old@new"] == "warns" else "removal"


# --- candidate collection -----------------------------------------------------------------------


def collect(library: str) -> tuple[list[dict], list[dict]]:
    """(pair candidates, value-rule records) for one library."""
    snippets = _load("snippets.json")
    hand, templates = snippets.get("pairs", {}), snippets.get("value_templates", {})
    out: list[dict] = []

    rows, _ = keyword_pairs(library)
    for level, row in [("symbol", r) for r in symbol_pairs(library)] + [("keyword", r) for r in rows if r["old"] and r["new"]]:
        key = f"{row['old']} -> {row['new']}"
        entry = {"id": key, "library": library, "kind": level, "source": row["source"], "old_symbol": row["old"], "new_symbol": row["new"]}
        spec = hand.get(key)
        if spec and "skip" in spec:
            entry.update(status="unprobed", reason=spec["skip"])
        elif spec:
            entry.update(status="probed", old=spec["old"], new=spec["new"], snippets="hand")
        elif level == "symbol" and access_snippet(library, row["old"]) and access_snippet(library, row["new"]):
            entry.update(status="probed", old=access_snippet(library, row["old"]), new=access_snippet(library, row["new"]), snippets="access")
        else:
            entry.update(status="unprobed", reason="no snippet")
        out.append(entry)

    for c in _load("release_notes.json").get("candidates", []):
        if c["library"] == library:
            kind = "value" if c["category"] == "value_change" else "behaviour"
            out.append({"id": c["id"], "library": library, "kind": kind, "source": "release notes", "status": "probed",
                        "old": c["old"], "new": c["new"], "snippets": "release_notes", "concept_grade": c.get("concept_grade")})

    rules_path = rules_dir(library) / "value_rules.json"
    rules = json.loads(rules_path.read_text(encoding="utf-8"))["rules"] if rules_path.exists() else []
    seen_pairs: set[tuple] = set()
    for i, rule in enumerate(rules):
        rule["_call"] = value_call(templates, rule)
        if rule["_call"] is None or not rule.get("replacement"):
            continue
        old_value, new_value = (rule["value"], rule["replacement"]) if rule["side"] == "old" else (rule["replacement"], rule["value"])
        key = (rule["callable"], rule["parameter"], old_value, new_value)
        if key in seen_pairs:
            continue
        seen_pairs.add(key)
        out.append({"id": f"{rule['callable']}({rule['parameter']}={old_value!r} -> {new_value!r})", "library": library, "kind": "value",
                    "source": "value_rules", "status": "probed", "snippets": "template",
                    "old": value_call(templates, {**rule, "value": old_value}), "new": value_call(templates, {**rule, "value": new_value})})
    return out, rules


# --- execution ----------------------------------------------------------------------------------


def probe_library(library: str, log=print) -> tuple[list[dict], list[dict]]:
    pairs, rules = collect(library)
    items: list[tuple[str, str]] = []
    for c in pairs:
        if c["status"] == "probed":
            items += [(f"{c['id']}|old", c["old"]), (f"{c['id']}|new", c["new"])]
    for i, rule in enumerate(rules):
        if rule["_call"]:
            items.append((f"rule:{i}", rule["_call"]))
    log(f"[{library}] probing {len(items)} snippet(s) in both environments")
    results = {side: run_checks(env_name(library, side), library, items, timeout=30, log=log) for side in SIDES}

    for c in pairs:
        if c["status"] != "probed":
            continue
        cells = {f"{form}@{side}": cell(results[side][f"{c['id']}|{form}"]) for form in SIDES for side in SIDES}
        outcome = {k: v[0] for k, v in cells.items()}
        found, reason = verdict(outcome)
        c.update(outcome=outcome, details={k: v[1] for k, v in cells.items() if v[1]}, verdict=found, reason=reason,
                 concept_class=concept_class(c["kind"], found, outcome),
                 warns_on_own_side=[f for f in SIDES if outcome[f"{f}@{f}"] == "warns"])
    manifest = read_manifest()
    stamp = {"lock_sha256": {side: manifest[env_name(library, side)]["lock_sha256"] for side in SIDES},
             "probed_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    for i, rule in enumerate(rules):
        call = rule.pop("_call")
        if not call:
            rule["probe"] = {"status": "unprobed", "reason": "no call template"}
            continue
        cells = {side: cell(results[side][f"rule:{i}"]) for side in SIDES}
        own, other = rule["side"], "new" if rule["side"] == "old" else "old"
        confirmed = cells[own][0] in ("ok", "warns") and cells[other][0] != "ok"
        rule["probe"] = {"status": "probed", "confirmed": confirmed, "outcome": {s: v[0] for s, v in cells.items()},
                         "details": {s: v[1] for s, v in cells.items() if v[1]}, **stamp}
    return pairs, rules


def probe(libraries: list[str] | None = None, log=print) -> dict:
    manifest = read_manifest()
    libraries = libraries or list(load_libraries()["libraries"])
    report = {"about": ("Every candidate's old and new form run in both environments; see varag.bench.probe. "
                        "Probes are snippets, not concepts."),
              "probed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "lock_sha256": {lib: {side: manifest[env_name(lib, side)]["lock_sha256"] for side in SIDES} for lib in libraries},
              "candidates": [], "value_rules": {}, "counts": {}}
    for library in libraries:
        pairs, rules = probe_library(library, log=log)
        report["candidates"] += pairs
        rules_path = rules_dir(library) / "value_rules.json"
        if rules_path.exists():
            data = json.loads(rules_path.read_text(encoding="utf-8"))
            data["rules"] = rules
            rules_path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
            report["value_rules"][library] = {"records": len(rules), "confirmed": sum(1 for r in rules if r["probe"].get("confirmed")),
                                              "unprobed": sum(1 for r in rules if r["probe"].get("status") == "unprobed")}
        report["counts"][library] = counts(pairs)
    (candidates_dir() / "probes.json").write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return report


def counts(pairs: list[dict]) -> dict:
    out: dict = {"unprobed": sum(1 for c in pairs if c["status"] == "unprobed")}
    for kind in ("symbol", "keyword", "value", "behaviour"):
        mine = [c for c in pairs if c["kind"] == kind and c["status"] == "probed"]
        if mine:
            out[kind] = {v: sum(1 for c in mine if c["verdict"] == v) for v in VERDICTS}
    out["by_class"] = {}
    for c in pairs:
        if c.get("concept_class"):
            out["by_class"][c["concept_class"]] = out["by_class"].get(c["concept_class"], 0) + 1
    return out


def format_report(report: dict) -> str:
    lines = []
    for library, c in report["counts"].items():
        lines.append(f"{library}: " + "; ".join(f"{kind} " + ", ".join(f"{v} {n}" for v, n in vs.items())
                                             for kind, vs in c.items() if kind not in ("unprobed", "by_class"))
                     + f"; unprobed {c['unprobed']}; classes {c['by_class']}")
        if library in report["value_rules"]:
            vr = report["value_rules"][library]
            lines.append(f"  value rules: {vr['confirmed']} of {vr['records']} confirmed, {vr['unprobed']} unprobed")
    total = sum(1 for c in report["candidates"] if c.get("verdict") == "two_directional")
    lines.append(f"two_directional across libraries: {total}" + ("" if total >= 35 else "  (below the 35 checkpoint)"))
    return "\n".join(lines)
